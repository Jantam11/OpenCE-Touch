# Changelog

## 0.5.0-touch — 2026-10-08

Changes since [v0.4.0-touch](https://github.com/Jantam11/OpenCE-Touch/releases/tag/v0.4.0-touch): 103 commits, including 91 upstream commits.

- Updated OpenCE through `73dc01d0`: Custom Edition map/script/HUD fixes, safer co-op cameras, improved rendering/culling and OpenGL ES visibility queries, larger object/widget pools, Android relative-mouse input, multiplayer hosting/countdown fixes and positional stereo audio improvements.
- Added persistent shader caching/warm-up, sound lifetime and stream-underrun fixes, reduced menu profile/map I/O, profile keyboard Enter handoff, reusable deleted profile names, paused multiplayer input/crouch fixes and finer mouse sensitivity.
- Added independent Sinc/Linear audio resampling. Sinc remains the default.
- Added optional desktop playlist-server tools for unattended hosting, map/game-type rotation and idle/empty-game recovery.
- Added a map browser with stock/custom categories, pictures, list/grid views, co-op difficulty, native split-screen and next-map selection. It lists installed maps; it does not download maps. Set `display.map_browser=false` to use the original list.
- Added optional Glassed, Cairo (Halo 2 inspired) and Vanilla menu themes. Default remains selected. Change Settings → Video Setup → Menu Theme, save and restart.
- Added the optional **fqlx compact** Android touchscreen preset under OPTIONS → Layout presets. It remains editable and compatible with existing `.halolayout` import/export. Upgrading preserves your current layout; export it before choosing a replacement preset.
- Preserved existing touch/menu/profile-keyboard controls, gyro/rumble, single-player options, disc movies and relay features; expanded sound, keyboard, map-browser, playlist and mobile regressions.

**Compatibility:** multiplayer uses protocol **24**; older protocol-22 builds must update to join. Upstream game-state pool changes mean older campaign checkpoints may not load. Phone gameplay, theme appearance, shader warm-up on real drivers and live-server joins/rotation remain unverified. No community map pack, pfista downloader or Delta account/statistics service is included.

**Credits**
- [OpenCommunityEdition/OpenCE](https://github.com/OpenCommunityEdition/OpenCE) and this range's upstream contributors: [eltanschauung](https://github.com/eltanschauung), [MrMilenko](https://github.com/MrMilenko), [startupfoundry](https://github.com/startupfoundry), [innerhat-dev](https://github.com/innerhat-dev), [addisonbair](https://github.com/addisonbair), [xshxdex98](https://github.com/xshxdex98), [FernandolDev](https://github.com/FernandolDev), [cybersecurity](https://github.com/cybersecurity), [TwistedFlog](https://github.com/TwistedFlog), [DaftHacker](https://github.com/DaftHacker), [meowsandstuff](https://github.com/meowsandstuff) and [codex](https://github.com/codex).
- [ChupathingyCE/chupathingyce](https://github.com/ChupathingyCE/chupathingyce) and its contributors, including MrMilenko and eltanschauung: shader caching, sound/menu/profile/input fixes, audio options and playlist-server work.
- [xshxdex98/DamnationCE](https://github.com/xshxdex98/DamnationCE): map-browser and optional menu-theme work.
- [fqlx/OpenCE](https://github.com/fqlx/OpenCE): compact browser-touch layout adapted into an Android preset.
- Retained code: [theLlamaNet / FulGer](https://github.com/theLlamaNet/halo-ce-android) for mobile input/settings, cheats/camera and relay features; [JoshRob297/halo-ce-touch](https://github.com/JoshRob297/halo-ce-touch) for Bink playback and dedicated-server work; [FFmpeg](https://ffmpeg.org/) for video/audio decoding.
- Font licenses and notices are included in packaged builds. Integration and additional fixes were coded with AI (OpenAI Codex), maintained in this fork by Jantam11. See [integration notes](https://github.com/Jantam11/OpenCE-Touch/blob/touch-controls/INTEGRATION_NOTES.md) for source revisions and validation limits.

[Full commit comparison](https://github.com/Jantam11/OpenCE-Touch/compare/v0.4.0-touch...v0.5.0-touch)

## 0.4.0-touch — 2026-10-07

- Added gyro aiming, rumble, drag-to-aim fire buttons, Halo icons and portable layouts.
- Added Porting options, FOV/FPS settings, single-player cheats and free camera.
- Added disc intro, credits and attract-demo videos with audio and tap-to-skip; existing players can import movies separately.
- Added encrypted relay fallback and dedicated-server rotation/restart improvements.
- Retained the upstream revision from 0.3.0-touch and the existing menu/profile touch fixes; expanded regression checks.

Credits: [theLlamaNet / FulGer](https://github.com/theLlamaNet/halo-ce-android) for the mobile settings/input, cheats/camera and relay features; [JoshRob297](https://github.com/JoshRob297/halo-ce-touch) for Bink playback and dedicated-server changes; [FFmpeg](https://ffmpeg.org/) for the movie decoder. Integration and additional fixes were coded with AI (OpenAI Codex).

## 0.3.0-touch — 2026-10-07

- Updated to the latest passing OpenCE revision, `4e8ed2f`.
- Includes upstream Android rendering/stability improvements, co-op/network fixes and Custom Edition map support.
- Keeps the customizable touch controls and direct menu/profile-keyboard taps; adds controller-port regression checks to Android CI.
