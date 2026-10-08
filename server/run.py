#!/usr/bin/env python3
"""Launch an ordinary OpenCE Linux/Windows build as a playlist server."""
import argparse
import os
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--executable', type=Path, required=True)
    parser.add_argument('--data', type=Path, required=True, help='Folder containing your own maps/')
    parser.add_argument('--saves', type=Path, required=True, help='Persistent server saves/cache folder')
    parser.add_argument('--playlist', default='playlists/slayer.txt', help='Path relative to the data folder')
    parser.add_argument('--name', default='OpenCE-Touch', help='Browser name, at most 15 characters')
    parser.add_argument('--minimum', type=int, default=1)
    parser.add_argument('--maximum', type=int, default=12)
    parser.add_argument('--idle-limit', type=int, default=5, help='Minutes without a score; 0 disables')
    parser.add_argument('--private', action='store_true', help='Do not publish to the public lobby brokers')
    parser.add_argument('--dry-run', action='store_true', help='Validate setup without launching')
    args = parser.parse_args()
    executable, data, saves = args.executable.resolve(), args.data.resolve(), args.saves.resolve()
    if not executable.is_file(): parser.error('Executable does not exist')
    if not (data / 'maps').is_dir(): parser.error('Data folder must contain maps/')
    playlist = (data / args.playlist).resolve()
    if not playlist.is_relative_to(data) or not playlist.is_file():
        parser.error('Playlist must be an existing file inside the data folder')
    if not any(len(line.split('#', 1)[0].split()) == 2 for line in playlist.read_text().splitlines()):
        parser.error('Playlist must contain a map and game type')
    if not 1 <= args.minimum <= args.maximum <= 128: parser.error('Require 1 <= minimum <= maximum <= 128')
    if not 0 <= args.idle_limit <= 1440: parser.error('Idle limit must be 0..1440 minutes')
    if not args.name or len(args.name) > 15 or not args.name.isascii():
        parser.error('Name must contain 1..15 ASCII characters')
    environment = os.environ.copy()
    environment.update(HALO_DATA_ROOT=str(data), HALO_SAVE_ROOT=str(saves),
                       HALO_DEDICATED=playlist.relative_to(data).as_posix(),
                       HALO_DEDICATED_NAME=args.name,
                       HALO_DEDICATED_MINIMUM_PLAYERS=str(args.minimum),
                       HALO_DEDICATED_MAXIMUM_PLAYERS=str(args.maximum),
                       HALO_DEDICATED_IDLE_LIMIT=str(args.idle_limit),
                       HALO_DEDICATED_PUBLIC='false' if args.private else 'true')
    if args.dry_run:
        print(f'Valid setup: {executable.name}, {playlist}, {args.minimum}..{args.maximum} players')
        return
    saves.mkdir(parents=True, exist_ok=True)
    # Replacing the launcher lets service/container stop signals reach the game.
    os.chdir(data)
    os.execve(str(executable), [str(executable)], environment)


if __name__ == '__main__': main()
