# Changelog

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
