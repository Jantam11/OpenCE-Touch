"""Package and publish the checked Android build directly, without Actions artifacts."""
import hashlib
import os
from pathlib import Path
import re
import subprocess
import zipfile


def main():
    tag = os.environ['TAG']
    if not re.fullmatch(r'v\d+\.\d+\.\d+-touch', tag):
        raise ValueError('Invalid touch release tag')
    package = Path('dist/halo-android-release')
    apk = package / 'app-release.apk'
    for name in ('FFmpeg-LGPL.txt', 'bink-relink.zip', 'opus-COPYING.txt', 'lucide-LICENSE.txt'):
        assert (package / name).is_file(), name
    with zipfile.ZipFile(apk) as archive:
        assert archive.testzip() is None
        for name in ('lib/arm64-v8a/libbinkplayer.so', 'lib/arm64-v8a/libmain.so',
                     'lib/arm64-v8a/libSDL3.so', 'assets/halo_guest.elf',
                     'assets/licenses/opus-COPYING.txt', 'assets/licenses/lucide-LICENSE.txt'):
            assert name in archive.namelist(), name
    output = Path('touch-release')
    output.mkdir(exist_ok=True)
    (output / 'OpenCE-Touch.apk').write_bytes(apk.read_bytes())
    zipped = output / 'halo-android-release.zip'
    with zipfile.ZipFile(zipped, 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(package.rglob('*')):
            if path.is_file():
                archive.write(path, path.relative_to(package))
    assets = [output / 'OpenCE-Touch.apk', zipped]
    checksums = output / 'SHA256SUMS.txt'
    checksums.write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest() + '  ' + p.name + '\n' for p in assets))
    entries = Path('CHANGELOG.md').read_text().split('## ')
    entry = next(e for e in entries if e.startswith(tag[1:] + ' '))
    notes = entry.split('\n', 1)[1].strip()
    notes += ('\n\nDownload **OpenCE-Touch.apk** to install. The ZIP also includes dependency licenses '
              'and FFmpeg source/relinking materials.\n\nInstallation over an older APK may fail because CI '
              'uses a temporary signing key. Back up saves before uninstalling.\n\nBuild: https://github.com/'
              + os.environ['GITHUB_REPOSITORY'] + '/actions/runs/' + os.environ['GITHUB_RUN_ID'] + '\n')
    notes_path = output / 'notes.md'
    notes_path.write_text(notes)
    subprocess.run(['gh', 'release', 'create', tag, *map(str, assets), str(checksums),
                    '--target', os.environ['GITHUB_SHA'], '--latest', '--title',
                    'OpenCE-Touch ' + tag[1:], '--notes-file', str(notes_path)], check=True)


if __name__ == '__main__':
    main()
