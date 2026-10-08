# 2026-10-08 integration

The baseline was OpenCE-Touch `062566ac` (v0.4.0-touch). Upstream
`OpenCommunityEdition/OpenCE` was initially advanced to `2d2348cd` in merge
[`f6c912ff`](https://github.com/Jantam11/OpenCE-Touch/commit/f6c912ffa30bb55969edd8b4f232fbae861b14ee).
Both parents are preserved; 88 upstream commits bring the native rendering,
co-op, networking and menu changes forward. Network protocol is now 24 as in
upstream. Previous protocol-22 builds need updating to join protocol-24 games.

[Upstream-merge CI](https://github.com/Jantam11/OpenCE-Touch/actions/runs/37762090042)
passed Linux, Windows and Android debug/release builds and the existing tests
before the merge was published to touch-controls.

A final upstream check also merged `73dc01d0` in
[`d3b86268`](https://github.com/Jantam11/OpenCE-Touch/commit/d3b86268f4ff555dc54558a9723c3889e501b705),
preserving the ChupathingyCE sound changes and both upstream histories.
These three additional commits repair positional stereo distance attenuation
and reverb; all upstream platform jobs passed in run 37764567816. The complete
update contains 91 new upstream commits.

## Selected fork ports

The ports adapt selected source changes to the current upstream and existing
Android touch stack. They do not import each fork's entire divergent history.

| Source | References | Changes |
| --- | --- | --- |
| [ChupathingyCE](https://github.com/ChupathingyCE/chupathingyce) | `acd2087a`, `45677e54`, `fc525201`, `fb47309a` | Looping-sound ownership/stop lifetime, underrun resume, avoid repeated profile/map I/O during menu frames; tests adapted to current upstream functions. |
| ChupathingyCE | `916cf2fe`, `4575f6e6`, `771a257f`, `37951253` | Return/keypad Enter restored after virtual keyboard exit, allow deleted profile names to be reused, paused multiplayer input inhibition and keyboard crouch. Android native keyboard hints are preserved. |
| ChupathingyCE | `51093bf3`, `21c90775`, `a551abf5`, `63ea522f`, `edfd2cda` | Finer mouse sensitivities, persistent GLSL source/pair cache and bulk warm-up, Windows replacement fix, Sinc/Linear audio choice independent of reverb. Existing upstream sinc optimization and reverb remain. Cache reads/writes are capped at 48 MiB. |
| ChupathingyCE | `dc4518a6` playlist director; `40e8bc8d` score helper | Optional no-window/no-audio desktop hosting, player limits, map/type playlists, automatic countdown with existing readiness/precache checks, post-match rotation, score-idle/empty-game recovery. Launcher, example playlist, optional systemd/Docker templates. Uses this fork's brokers/protocol; no Delta online identity/statistics service. |
| [DamnationCE](https://github.com/xshxdex98/DamnationCE) | Map picker/overlay from `91493038`; Cairo/theme generators from `add42e6e` | Stock/custom map categories, list/grid pictures, co-op campaign and difficulty; pointer/pad input reuses our existing routing. Optional Glassed/Cairo/Vanilla themes are regenerated over our current menu definitions, preserving visible native lobby/settings behavior. Default is selected initially. |
| [fqlx/OpenCE](https://github.com/fqlx/OpenCE) | `8102b91f`, browser `port/web/site/input.js` / CSS compact controls | Compact 14-control native Android preset. It reuses normal button/action geometry and `.halolayout` version 1; users can edit/export/import it. Preset selection replaces buttons only and retains general gyro/rumble/input preferences. No automatic switch on upgrade. |

Source credits and AI disclosure are in README. Theme/overlay fonts carry SIL
OFL/CC0 notices, copied into packaged builds and Android license assets. Theme
art is generated; no Xbox/PC map assets were added to the repository.

## Use

- Themes: Settings → Video Setup → Menu Theme → save → restart. Default restores
  OpenCE's previous menus. Optional themed main menus also include a Menus
  selector. Theme changes are intentionally applied on restart.
- Map browser: enabled independently of themes. `display.map_browser=false`
  (`HALO_MAP_BROWSER=false` on desktop) keeps the original map list. Installed
  compatible maps are shown; the browser does not download a community pack.
- Compact controls: Android OPTIONS → Layout presets → fqlx compact. Export
  your current layout first if you want to retain it. Default remains available.
- Audio: Settings → Audio Setup → Resampling. Sinc is default; Linear costs less
  CPU and is an optional quality tradeoff.
- Servers: [server/README.md](server/README.md), ordinary Linux/Windows binaries,
  your own map data, and a separate persistent save/cache folder.

## Regression and validation limits

The original mobile checks still cover touch taps/coordinate mapping, virtual
pad ownership, portable import/export, gyro/startup-cheat settings, multiplayer
cheat isolation, disc/movie import, movie/JNI lifecycle, relay bounds and network
rotation/countdown/precache. The new compact layout round-trips all 14 controls.

Added checks exercise real sound and keyboard production functions, stock/CE
map filtering and co-op/PvP selection/back navigation/empty-list cleanup,
playlist parsing and rotation/idle/empty recovery, and the restriction that only
the local dedicated host may lack a player. Menu XML references, handlers,
settings and artwork are checked separately for all four themes. Changed native
sources and the generated embedded assets compile locally as 32-bit objects.

[Final integration CI](https://github.com/Jantam11/OpenCE-Touch/actions/runs/37769789258)
passed for code commit `3897fc42`: Linux, Windows and Android debug/release
builds and the available regression checks. The resulting source also includes
native split-screen/next-map browser entry points and desktop-only SDL/GL guards
for the Android guest. This environment has no connected Android phone/emulator, owned game
assets, or live second client. Compilation and deterministic regression checks
cannot prove visual layout, gameplay, gyro hardware, driver shader warm-up or
live-server joins/rotation. Docker/systemd templates are supplied, not deployed.

## Pfista community-map management: proposal only

[pfista/halo-og](https://github.com/pfista/halo-og)'s
[community-map guide](https://github.com/pfista/halo-og/blob/main/docs/community-maps.md)
describes a curated multiplayer-map collection, compatible **Xbox v5** maps
rather than a generic arbitrary-map downloader. Its manifest records names,
file sizes and SHA-256 hashes so known compatible files can be recognized;
different maps with the same filename can remain distinct. Changed map files
refresh their decompressed cache, maps remain usable offline, and the desktop
layout preserves map/profile/save data across app updates.

Desktop setup can fetch roughly 40 maps (about 863 MiB). Android's documented
path is manual installation, so adding this to our app would also require a
mobile download/storage flow. This is separate from DamnationCE's map picker,
which lists installed maps.

Recommendation: if approved later, add explicit per-map opt-in downloads,
progress/cancel/retry, compatibility/hash checks, available-storage checks and
persistent offline storage. Avoid automatically downloading the whole pack.
No pfista downloader/map-management code or map files are included in this
integration; it was requested for explanation only.
