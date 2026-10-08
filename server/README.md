# Playlist server

Adapted from [ChupathingyCE](https://github.com/ChupathingyCE/chupathingyce)'s
playlist director (`dc4518a6`), using this fork's existing network protocol and
public lobby brokers. Ordinary Linux and Windows binaries can host without a
window, audio device or local player. This is not Delta's account/statistics
service or a new wire protocol. Android retains its existing network-test tools.

The director rotates maps/game types after matches, waits for the configured
minimum players and every joined machine's readiness, recovers after everyone
leaves (30 seconds), and ends score-idle games (five minutes by default). After
a match it allows 20 seconds for the carnage report before returning to the
lobby. With one player, it chooses a non-team entry when the playlist has one.
Unavailable maps, campaign maps and unknown game types are skipped, with a
five-second retry delay. Missing/empty playlists exit unsuccessfully.

## Setup

Use the Linux or Windows build artifact from this branch. On Linux install the
32-bit SDL3/runtime libraries (the same ones as the ordinary game). Put your own
Halo Xbox maps in a persistent `data/maps/` folder. Required menu/shared maps
must be present too. Put compatible CE maps and their resource maps in the usual
map locations described by OpenCE. No game files are included in these tools.

Copy `server/playlists/slayer.txt` into `data/playlists/slayer.txt`, then launch:

```sh
python server/run.py --executable /opt/opence/halo-linux-release/halo \
  --data /var/lib/opence/data --saves /var/lib/opence/saves \
  --playlist playlists/slayer.txt --name MyServer --minimum 1 --maximum 12
```

Windows uses the same launcher with `halo.exe` and Windows paths. Add
`--dry-run` to validate paths/options, `--private` to suppress public listings,
or `--idle-limit 0` to disable score-idle recovery. Names accept up to 15 ASCII
characters. Save/cache data are kept separately from the executable for updates.
Configuration still lives next to the executable, as in the normal desktop
port; its folder must be writable. Network/firewall requirements match regular
OpenCE hosting. A public listing does not guarantee connectivity through every
NAT/firewall.

Playlist syntax is `map game_type`, with `#` comments; at most 64 entries:

```text
bloodgulch slayer
sidewinder ctf
timberland@ce slayer
```

Available game types include `slayer`, `team_slayer`, `ctf`, `king`, `oddball`
and `race` (the game's existing named variants). CE entries need compatible
installed maps; this tool does not download maps. Environment variables allow
launching the executable directly: `HALO_DEDICATED` (playlist relative to data),
`HALO_DEDICATED_NAME`, `HALO_DEDICATED_MINIMUM_PLAYERS`,
`HALO_DEDICATED_MAXIMUM_PLAYERS`, `HALO_DEDICATED_IDLE_LIMIT`,
`HALO_DEDICATED_PUBLIC`, `HALO_DATA_ROOT` and `HALO_SAVE_ROOT`.

## Service/container templates

`opence-touch.service` is an optional systemd template. Create a dedicated
`opence` OS user, give it access to its data/saves/executable configuration,
adjust paths, then install the unit yourself. No service is installed by a
build or launcher.

The optional Dockerfile expects the Linux release artifact unpacked into
`dist/halo-linux-release` in the repository:

```sh
docker build -f server/Dockerfile -t opence-touch-server .
docker run --rm --network host \
  -v /your/data:/data -v /your/saves:/saves \
  opence-touch-server --playlist playlists/slayer.txt --name MyServer
```

The mounted folders must be readable/writable as needed by UID 10001. Keep
maps and saves in these external folders when replacing the container. The
image includes dependency licenses from the build artifact. These templates
have not been deployed here; live joins and map rotation need a host with game
assets and a second compatible client.

## Checks

`python tools/test_dedicated_server.py` exercises the production director with
a deterministic clock and fake network: opt-in startup, playlist parsing,
limits, readiness gating, rotation, empty/idle recovery and invalid-entry
retries. It does not establish live server/gameplay verification.
