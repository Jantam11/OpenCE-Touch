# Halo: Combat Evolved for Linux, Windows and Android

> **About this fork:** OpenCE-Touch adds customizable Android touchscreen controls,
> swipe aiming, and direct touch navigation for menus and the profile keyboard.
> The fork-specific changes were coded with AI (OpenAI Codex); the original OpenCE
> project and its contributors provide the underlying game port.
> Touch builds are on the [`touch-controls`](https://github.com/Jantam11/OpenCE-Touch/tree/touch-controls) branch;
> the download links below point to upstream OpenCE releases.

Get the Android touch version from this fork's [Releases](https://github.com/Jantam11/OpenCE-Touch/releases)
([latest APK](https://github.com/Jantam11/OpenCE-Touch/releases/latest/download/OpenCE-Touch.apk)).

## Mobile feature credits

- [theLlamaNet / FulGer — halo-ce-android](https://github.com/theLlamaNet/halo-ce-android): gyroscope aiming, rumble, fire-button drag aiming, Halo-style vector icons, portable layouts, Porting options, FOV/FPS settings, single-player cheats, free camera and encrypted relay fallback. Adapted to retain this fork's SDL virtual gamepad and working menu/profile-keyboard taps.
- [JoshRob297 — halo-ce-touch](https://github.com/JoshRob297/halo-ce-touch): Bink movie playback from [his clean Bink branch](https://github.com/JoshRob297/halo-ce-touch/tree/bink-on-main), plus dedicated-server map/variant rotation, time limits and restart/join fixes. His touch work also builds on theLlamaNet's controls.
- [FFmpeg](https://ffmpeg.org/): open-source Bink video/audio decoding, built from pinned LGPL source. Every Android release includes its license, exact source and relinking materials in the packaged build.

Open **OPTIONS** or the native **Porting options** menu to change settings. Layouts can be exported/imported as `.halolayout`; imports from the two credited forks are supported. Gyroscope and vibration require suitable phone hardware. Cheats apply to single-player; startup choices take effect when a campaign starts after restarting the app.

**Disc videos:** new installations extract `bink/` alongside `maps/`. Existing players can select **OPTIONS → Import disc movies** and choose their own Halo `.iso`/`.xiso`; this copies movies without replacing maps or profiles. Intro, credits and idle attract-demo videos play with audio, and a tap skips playback. No game videos are bundled in the APK. Other in-engine cutscenes still use the game's renderer.

## Update in 0.5.2-touch

Merged validated OpenCE `f479e349`: voice chat, vote kick, co-op settings, rendering/audio/camera fixes and the new Android icon. Fixed free-camera swipe/gyro ownership and repeated Zoom toggles with [FulGerNet/theLlamaNet's code](https://github.com/FulGerNet/halo-ce-android/commit/f1c3c4d425427779b05a764d10dafdadd753f2e1); added [ChupathingyCE/MrMilenko](https://github.com/ChupathingyCE/chupathingyce) map-header/profile/script checks. Existing layouts, direct menu taps, movies, shader caching, audio resampling, map browser and themes are retained. Voice chat requires microphone permission; phone gameplay/voice testing is still needed. See [changelog](CHANGELOG.md) and [integration notes](INTEGRATION_NOTES.md).

## Android fixes in 0.5.1-touch

- Main-screen Quit asks for confirmation and closes the app when confirmed; Back cancels. Porting options is a separate row below Quit. The native pause menu keeps its normal Save and Quit behavior.
- Targeted renderer fix adapted from [kirklandsig's OpenCE PR #165](https://github.com/OpenCommunityEdition/OpenCE/pull/165), avoiding an Android/Mali buffer-copy race that produces stretched geometry or missing world surfaces. Android exit handling adapted from [FernandolDev's PR #183](https://github.com/OpenCommunityEdition/OpenCE/pull/183).
- The `touch-controls` branch builds/tests and packages Android only. Phone gameplay still needs confirmation using your own game data.

## Fork features added on 2026-10-08

- [ChupathingyCE](https://github.com/ChupathingyCE/chupathingyce): persistent shader warm-up/cache, sound lifetime and stream-underrun fixes, less profile/map I/O in menus, profile keyboard Enter handoff, profile-name reuse, paused multiplayer input/crouch fixes, finer mouse sensitivity and independent Sinc/Linear audio resampling. Desktop [playlist server tools](server/README.md) add unattended hosting, map/game-type rotation and idle/empty-game recovery using OpenCE networking.
- [DamnationCE](https://github.com/xshxdex98/DamnationCE): a map picker with stock/custom categories, pictures, list/grid views, co-op selection and difficulty. Optional **Glassed**, **Cairo** (Halo 2 inspired) and **Vanilla** menu themes. **Default remains selected**; choose another in **Settings → Video Setup → Menu Theme**, save, then restart. Themes also have a Menus selector. `display.map_browser=false` restores the original map list.
- [fqlx/OpenCE](https://github.com/fqlx/OpenCE): an optional compact touchscreen preset adapted from its browser controls to our Android virtual gamepad. Choose **OPTIONS → Layout presets → fqlx compact**. Export your current layout first if you want to keep it. Preset controls remain editable and use the existing `.halolayout` export/import format; your current layout is not changed by upgrading.

The original touch/gyro/rumble, single-player options, layout import/export and disc-movie features remain in place. The shader cache is stored with saves (up to 48 MiB); deleting `shader_cache.bin` clears it. Audio defaults to Sinc; Linear is an optional lower-cost resampler. The server tools do not add Delta online accounts/statistics. No community map pack or downloader is bundled.

See [integration notes](INTEGRATION_NOTES.md) for source revisions, validation and the community-map proposal. Font notices ship in the packaged builds and Android assets. These changes need phone gameplay and live-server checks with your own game files before a release is considered verified on hardware.

[![Join our Discord](https://invidget.switchblade.xyz/9gqcHyr5km)](https://discord.gg/9gqcHyr5km)

This project is a port of the Halo: Combat Evolved decompilation to Linux,
Windows and Android. The decompilation is of the Xbox build 2342
(`cachebeta.exe`, SHA-256
`4cc87b45f721270392a96f1674ed2b5cd4a7bb4355faeab4531d1cf1884d9520`).

<img width="1289" height="995" alt="The game on Linux" src="https://github.com/user-attachments/assets/0d3ad50f-f8b8-46cf-aef8-e3661da2a7d7" />

The port starts from the decompilation of [bnunu/halo-1](https://github.com/bnunu/halo-1).
That project is a fork of [punpckhdq/halo](https://github.com/punpckhdq/halo).

## Download

GitHub Actions builds the game for each commit. These links download the
builds of the latest release:

| Platform | Release | Debug |
| --- | --- | --- |
| Linux | [halo-linux-release.zip](https://github.com/OpenCommunityEdition/OpenCE/releases/latest/download/halo-linux-release.zip) | [halo-linux-debug.zip](https://github.com/OpenCommunityEdition/OpenCE/releases/latest/download/halo-linux-debug.zip) |
| Windows | [halo-windows-release.zip](https://github.com/OpenCommunityEdition/OpenCE/releases/latest/download/halo-windows-release.zip) | [halo-windows-debug.zip](https://github.com/OpenCommunityEdition/OpenCE/releases/latest/download/halo-windows-debug.zip) |
| Android | [halo-android-release.zip](https://github.com/OpenCommunityEdition/OpenCE/releases/latest/download/halo-android-release.zip) | [halo-android-debug.zip](https://github.com/OpenCommunityEdition/OpenCE/releases/latest/download/halo-android-debug.zip) |

Use the release build to play. The debug build stops at the first failed
assertion and writes it to the log. Use the debug build to find and report
problems.

The game updates itself. At start-up it looks for a newer release, and asks
if you want to install it. Refer to "Updates" in
[port/linux/README.md](port/linux/README.md#updates).

Each build of the `main` branch that passes on all three platforms is a new
release. The [Releases](https://github.com/OpenCommunityEdition/OpenCE/releases)
page keeps the last five releases. If the latest build has a problem, get
an older build from that page.

## Game data

The port does not include the game data. Download an Xbox disc image
(`.xiso` or `.iso`) of Halo: Combat Evolved. All versions of the game
operate. The maps of the European (PAL) version were made for a slower
console. The port changes them to play as the North American (NTSC) maps do,
so players of the two versions can play together.

1. Start the game.
2. At the first start, the game asks for the disc image. Select it.
3. The game extracts the `maps/` folder. Then the game starts.

On Linux and Windows, the game puts `maps/` next to the executable. On
Android, copy the disc image to the phone first. The app puts `maps/` in its
data folder. Refer to [port/android/README.md](port/android/README.md).

## Platforms

Each platform has its own instructions:

| Platform | Instructions |
| --- | --- |
| Linux (32-bit x86 executable, OpenGL 4.5, SDL3) | [port/linux/README.md](port/linux/README.md) |
| Windows (32-bit x86 executable, OpenGL 4.5, SDL3) | [port/windows/README.md](port/windows/README.md) |
| Android (arm64 app, OpenGL ES 3, SDL3) | [port/android/README.md](port/android/README.md) |

The Linux README also gives the controls, the settings and the multiplayer
functions. These are almost the same on all platforms.

## Multiplayer

The game can play system link games on a local network and on the internet:

- A system link game can have up to 128 players on up to 128 machines.
- Linux, Windows and Android machines can play in the same game.
- An invite link lets a machine join a game on the internet. No server of
  this project is necessary.
- The netcode is new. Each machine moves its own player at once,
  and the host makes the decisions for the game. Refer to
  [port/linux/NETCODE.md](port/linux/NETCODE.md).

## Build the game

You do not need the Xbox SDK. The port supplies the SDK declarations that
the game uses. Refer to [port/include/xdk](port/include/xdk/README.md).

To build the game:

1. Install Python and [ninja](https://ninja-build.org/).
2. Install the tools for your platform. Refer to the README for the
   platform.
3. In the root folder of the repository, enter `python configure.py`.
4. Enter `ninja` with the target for the platform:

| Target | Result |
| --- | --- |
| `ninja linux` | `build/linux/halo` |
| `ninja windows` (on Windows) | `build/windows/halo.exe` and `SDL3.dll` |
| `ninja android_apk` | `port/android/app/build/outputs/apk/debug/app-debug.apk` |

If you enter `ninja` without a target, ninja builds the game for the
computer that you use.

`tools/ci_build.py` makes the same builds as GitHub Actions. For example,
enter `python tools/ci_build.py linux release`.

### Build options

Give these options to `configure.py`:

| Option | Result |
| --- | --- |
| (none) | A debug build. A failed assertion stops the game. |
| `--release` | A release build. The game does not examine assertions, as in the retail game. |
| `--portable` | The Linux and Windows builds operate on all x86-64 processors. The Linux build also operates on older distributions and on SteamOS: refer to "Portable build" in [port/linux/README.md](port/linux/README.md#portable-build). Use this option for builds that you give to other persons. |
| `--lto=thin`, `--lto=off` | Less link-time optimization. The link is faster. |
| `--pgo=off` | No profile-guided optimization. |
| `--pgo=train` | Records a new optimization profile. Refer to "Optimization profiles". |

Without `--portable`, the Linux and Windows builds use all the instructions
of the processor that builds them (`-march=native`). Such a build does not
always start on a different computer.

### Optimization profiles

The builds use profiles of the game to optimize the code:

- `pgo/halo_linux.profdata` for Linux and Android.
- `pgo/halo_windows.profdata` for Windows.

The profiles need clang 22 or later. With an older clang, the builds do not
use the profiles.

To record a new profile:

1. Delete the profile.
2. Enter `python configure.py --pgo=train`.
3. Enter `ninja linux` or `ninja windows`.

The build then plays the main menu and the first minute of each campaign
level. This procedure continues for approximately 15 minutes. The game
data must be in `assets/`.
