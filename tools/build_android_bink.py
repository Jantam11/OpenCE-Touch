"""Build JoshRob297's Bink player from pinned LGPL FFmpeg source, never a checked-in binary."""
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parent.parent
VERSION = "8.1.3"
SHA256 = "7138d28c96d9d3e3af4ee3d8cad72741f8ffb40da90c1112235dea3ecd3178a3"
SOURCE_URL = f"https://ffmpeg.org/releases/ffmpeg-{VERSION}.tar.xz"

def run(args, cwd):
    print("+", " ".join(map(str,args)),flush=True)
    subprocess.run(list(map(str,args)),cwd=cwd,check=True)

def main():
    ndk = None
    for key in ("ANDROID_NDK_HOME","ANDROID_NDK_ROOT","ANDROID_NDK"):
        if os.environ.get(key) and Path(os.environ[key]).is_dir(): ndk=Path(os.environ[key]);break
    if ndk is None:
        for key in ("ANDROID_HOME","ANDROID_SDK_ROOT"):
            parent=Path(os.environ.get(key,"/nonexistent"))/"ndk"
            if parent.is_dir(): ndk=sorted(parent.iterdir())[-1];break
    if ndk is None: raise RuntimeError("An Android NDK is required for movie playback")
    tool=next((ndk/"toolchains/llvm/prebuilt").glob("linux-*"))/"bin"
    cc=tool/"aarch64-linux-android28-clang"
    cache=ROOT/"build/android/third_party";cache.mkdir(parents=True,exist_ok=True)
    archive=cache/f"ffmpeg-{VERSION}.tar.xz"
    if not archive.exists(): urllib.request.urlretrieve(SOURCE_URL,archive)
    if hashlib.sha256(archive.read_bytes()).hexdigest()!=SHA256: raise RuntimeError("FFmpeg archive checksum mismatch")
    source=cache/f"ffmpeg-{VERSION}"
    if not source.is_dir():
        with tarfile.open(archive) as t: t.extractall(cache,filter="data")
    args=["./configure","--target-os=android","--arch=aarch64","--cpu=armv8-a",
        "--enable-cross-compile","--enable-pic","--disable-asm",f"--cc={cc}",
        f"--ar={tool/'llvm-ar'}",f"--nm={tool/'llvm-nm'}",f"--ranlib={tool/'llvm-ranlib'}",f"--strip={tool/'llvm-strip'}",
        f"--sysroot={tool.parent/'sysroot'}","--enable-small","--disable-everything",
        "--disable-programs","--disable-doc","--disable-avdevice","--disable-avfilter",
        "--disable-network","--enable-avformat","--enable-avcodec","--enable-avutil",
        "--enable-swscale","--enable-swresample","--enable-demuxer=bink,binka",
        "--enable-decoder=binkvideo,binkaudio_dct,binkaudio_rdft","--enable-protocol=file",
        "--enable-static","--disable-shared","--disable-autodetect","--disable-gpl","--disable-nonfree",
        "--extra-cflags=-O2","--extra-ldflags=-Wl,-z,max-page-size=16384"]
    fingerprint=hashlib.sha256("\n".join(args).encode()).hexdigest()
    stamp=source/"opence-configure.stamp"
    if not stamp.exists() or stamp.read_text()!=fingerprint:
        run(args,source);stamp.write_text(fingerprint)
    run(["make","-j",str(min(4,os.cpu_count() or 2))],source)
    stage=ROOT/"build/android/jniLibs/arm64-v8a";stage.mkdir(parents=True,exist_ok=True)
    player=ROOT/"port/android/binkplayer/binkplayer.c"
    obj=cache/"binkplayer.o"
    run([cc,"-fPIC","-O2","-c",player,f"-I{source}","-o",obj],ROOT)
    libs=[source/f"{name}/{name}.a" for name in ["libavformat","libavcodec","libswscale","libswresample","libavutil"]]
    output=stage/"libbinkplayer.so"
    run([cc,"-shared",obj,"-Wl,--start-group",*libs,"-Wl,--end-group","-laaudio","-llog","-landroid","-lm",
        "-Wl,-z,max-page-size=16384","-Wl,--no-undefined","-o",output],ROOT)
    run([tool/"llvm-strip",output],ROOT)
    # Provide exact dependency source and relinking materials alongside every release.
    bundle=ROOT/"build/android/bink-relink.zip"
    with zipfile.ZipFile(bundle,"w",zipfile.ZIP_DEFLATED) as z:
        z.write(archive,archive.name);z.write(obj,obj.name);z.write(player,"binkplayer.c")
        for lib in libs:z.write(lib,lib.name)
        z.write(source/"COPYING.LGPLv2.1","COPYING.LGPLv2.1")
        z.writestr("README.txt",f"FFmpeg {VERSION}, LGPL 2.1 or later; no GPL or nonfree components.\nSource SHA256: {SHA256}\nBuild recipe: tools/build_android_bink.py in the matching OpenCE-Touch tag.\nRelink with your NDK aarch64-linux-android28-clang:\nclang -shared -fPIC binkplayer.o -Wl,--start-group libavformat.a libavcodec.a libswscale.a libswresample.a libavutil.a -Wl,--end-group -laaudio -llog -landroid -lm -Wl,-z,max-page-size=16384 -o libbinkplayer.so\nAll game videos come from your own disc and are not bundled.\n")
    shutil.copyfile(source/"COPYING.LGPLv2.1",ROOT/"build/android/FFmpeg-LGPL.txt")
    print("Bink decoder built and relinking bundle prepared",flush=True)

if __name__=="__main__":main()
