"""Regenerate fork settings and retain the optional themes' presentation.

The base revision supplies the last generated screens (default HEAD).
New screens share the theme's palette and existing header placement.
"""
from pathlib import Path
import json
import subprocess
import sys
import xml.etree.ElementTree as ET
import port_settings

ROOT = Path(__file__).resolve().parents[1]
BASE = sys.argv[1] if len(sys.argv) > 1 else "HEAD"
MENUS = ROOT / "port/assets/menus"

def previous(path):
    result = subprocess.run(["git", "show", f"{BASE}:{path.relative_to(ROOT)}"],
                            cwd=ROOT, capture_output=True, text=True)
    return ET.fromstring(result.stdout) if result.returncode == 0 else None

def widgets(tree):
    return {element.get("name"): element for element in tree.findall("widget")} if tree is not None else {}

def generate():
    files = {**port_settings.settings_files(), **port_settings.multiplayer_files()}
    for name, lines in files.items():
        path = MENUS / "ce" / name
        base = widgets(previous(path))
        text = "\n".join(lines)
        for folder in sorted((MENUS / "skin").glob("*/ce")):
            if folder.parent.name == "vanilla":
                continue
            target = folder / name
            old = widgets(previous(target))
            # Existing themes overlay the default menu files; include new settings too.
            if not old and "player_profile_edit" not in name:
                continue
            tree = ET.fromstring(text)
            new = widgets(tree)
            template = widgets(previous(folder / ("main_menu.settings_select.player_setup."
                                                "player_profile_edit.video_settings.xml")))
            palette = {}
            for key, element in old.items():
                if key in base and element.get("color") != base[key].get("color"):
                    palette[base[key].get("color")] = element.get("color")
            if not palette:
                palette = {"#FF2896FF": "#FFC8D6EA" if folder.parent.name == "cairo" else "#FF80BFFF"}
            for element in new.values():
                if element.get("color") in palette:
                    element.set("color", palette[element.get("color")])
                if not old and element.get("bitmap"):
                    for model in template.values():
                        if model.get("bitmap") == element.get("bitmap") and "header" in model.get("name", ""):
                            for attr in ("left", "top", "width", "height"):
                                if attr in model.attrib:
                                    element.set(attr, model.get(attr))
            for key, element in old.items():
                if key in base and key in new:
                    for attr, value in element.attrib.items():
                        if value != base[key].get(attr):
                            new[key].set(attr, value)
            ET.indent(tree, space="\t")
            target.write_text("<?xml version='1.0' encoding='UTF-8'?>\n" +
                              ET.tostring(tree, encoding="unicode") + "\n")
        path.write_text(text)
    manifest = MENUS / "menus.json"
    data = json.loads(manifest.read_text())
    paths = set(data["files"])
    paths.update("ce/" + name for name in files)
    paths = {path for path in paths if not path.startswith("skin/")}
    data["files"] = sorted(paths)
    manifest.write_text(json.dumps(data, indent=1) + "\n")

if __name__ == "__main__":
    generate()
