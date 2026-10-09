# Changelog

## 0.5.2-touch — 2026-10-09

Changes since [v0.5.1-touch](https://github.com/Jantam11/OpenCE-Touch/releases/tag/v0.5.1-touch):

- Merged the newest validated [OpenCE revision `f479e349`](https://github.com/OpenCommunityEdition/OpenCE/commit/f479e34914604df5a22a2bdb0b38f180a1f702d8): voice chat, vote kick, co-op setup options, camera/animation improvements, transparency and overshield rendering fixes, faster audio mixing, map/network checks and the new Android icon. The previous Mali geometry and confirmed Quit fixes are retained.
- Fixed swipe/gyro input being consumed before the Android free camera could use it, and repeated Zoom toggles within one input tick. Adapted from [FulGerNet/theLlamaNet](https://github.com/FulGerNet/halo-ce-android/commit/f1c3c4d425427779b05a764d10dafdadd753f2e1). Added ChupathingyCE checks for map-header names, custom-map campaign completion and finite script speed.
- Preserved editable touch layouts/import/export, direct menu/profile taps, Bink movies, gyro/rumble, relay fallback, shader cache, Sinc/Linear audio, map browser and optional menu themes. Updated generated menus for upstream audio/co-op controls. Android version code increased to 7; dependency notices remain in the APK/package.

**Compatibility and validation:** network protocol remains **24**. Upstream Linux, Windows and Android builds passed; this release is published only after integrated Android debug/release builds and touch/mobile/renderer/camera checks pass. Voice chat requires microphone permission and a network game. Android's upstream Screenshot action does nothing. No phone or live second client is connected here; real-phone gameplay, microphone/voice chat, gyro/rumble and Internet multiplayer remain to be tested.

**Fork review:** checked ChupathingyCE, DamnationCE, FulGerNet and JoshRob297. Most useful new fixes arrived through upstream; no newer movie branch changes were available. fqlx/OpenCE currently returns 404, so new commits there could not be checked. Existing features and credits are retained.

**Credits:** [OpenCommunityEdition/OpenCE](https://github.com/OpenCommunityEdition/OpenCE) and its contributors; [ChupathingyCE / MrMilenko](https://github.com/ChupathingyCE/chupathingyce), [FulGerNet / theLlamaNet](https://github.com/FulGerNet/halo-ce-android), kirklandsig and FernandolDev; retained contributions from [DamnationCE](https://github.com/xshxdex98/DamnationCE), [fqlx/OpenCE](https://github.com/fqlx/OpenCE), [JoshRob297](https://github.com/JoshRob297/halo-ce-touch), [FFmpeg](https://ffmpeg.org/), Opus and Lucide. Integration and regression updates coded with AI (OpenAI Codex), maintained by Jantam11. Dependency licenses and FFmpeg relinking materials are included in the ZIP.

[Full comparison](https://github.com/Jantam11/OpenCE-Touch/compare/v0.5.1-touch...v0.5.2-touch)

## 0.5.1-touch — 2026-10-08

Changes since [v0.5.0-touch](https://github.com/Jantam11/OpenCE-Touch/releases/tag/v0.5.0-touch):

- Fixed an inherited Android/Mali upload race that can cause stretched geometry and missing floor/ceiling surfaces after changing maps. Adapted [kirklandsig's upstream PR #165](https://github.com/OpenCommunityEdition/OpenCE/pull/165); this is a targeted fix, not a full upstream update.
- Restored main-screen **Quit** with the existing **Are you sure?** confirmation. Confirming closes the Android app; Back cancels. **Porting options** stays available as a separate row. Android exit handling is adapted from [FernandolDev's PR #183](https://github.com/OpenCommunityEdition/OpenCE/pull/183). No app-exit button was added to the pause menu.
- Android-only validation and release packaging for `touch-controls`; Android version code increased to 6. Includes production-code upload-race and Quit checks with negative controls. Windows/Linux builds are skipped for this branch.

**Validation limits:** screenshots match the known Mali race, but its responsibility for this phone's artifacts remains a diagnosis to confirm by retesting. No phone is connected here; compilation and modeled upload checks do not prove in-game rendering or measure phone performance. Retest The Pillar of Autumn after the menu/map loads, restart/reload it, then enter Halo. Protocol 24 and the 0.5.0 features remain unchanged.

**Credits:** [OpenCommunityEdition/OpenCE](https://github.com/OpenCommunityEdition/OpenCE), kirklandsig (renderer fix), FernandolDev (Android exit fix), and retained work from [ChupathingyCE](https://github.com/ChupathingyCE/chupathingyce), [xshxdex98/DamnationCE](https://github.com/xshxdex98/DamnationCE), [fqlx/OpenCE](https://github.com/fqlx/OpenCE), [theLlamaNet / FulGer](https://github.com/theLlamaNet/halo-ce-android), [JoshRob297](https://github.com/JoshRob297/halo-ce-touch) and [FFmpeg](https://ffmpeg.org/). Integration and regression checks coded with AI (OpenAI Codex), maintained by Jantam11. Dependency licenses and relinking materials remain in the packaged ZIP.

[Full comparison](https://github.com/Jantam11/OpenCE-Touch/compare/v0.5.0-touch...v0.5.1-touch)

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
