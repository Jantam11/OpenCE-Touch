# OpenCE Touch input repair

Repository: Jantam11/OpenCE-Touch, touch-controls, base e422bfa1e8bbb82d4c47e80e4967016b27a7d402.

User phone test: gameplay key buttons type letters in profile entry; backing out leaves controls ineffective; MENU only hides controls and taps do nothing.

Source evidence: xinput_sdl.c diverts keyboard keys to text entry. Android excludes menu mouse event routing in sdl_platform.c and returns zero from halo_ui_pointer_update in d3d8_gl.c. The original overlay sends only keyboard/mouse events.

Route: SDL virtual gamepad for touch buttons/movement; keep relative mouse swipe aim; enable the existing menu pointer coordinate conversion on Android, with absolute mouse button coordinates. Do not alter saves or game data. Test native input sequences, compile Android, verify APK contents; game execution unavailable in this workspace.

Completed source changes: SDL virtual gamepad; automatic menu mode hints; SDL mouse routing on Android; profile keyboard hit testing using real rectangles; absolute pointer down/up coordinates; v2 layout mapping migration; version touch 2.

Local regression checks passed for short taps, multiple held buttons, release/reset, scaled and letterboxed menu coordinates, letters/backspace/DONE/cancel and inactive keyboard. Build and phone validation pending. No phone/emulator is connected.

## 2026-10-07 upstream update / 0.3.0-touch

Baseline: touch-controls d540c323, user reports the touch 2 APK works great.
Upstream selected: 4e8ed2f196e0edd1f2830a4de9841686aabbf466, with successful Linux, Windows and Android build jobs in run 37610960226. It includes rendering/stability, co-op/network and Custom Edition map changes since the fork's merge base 7ea6107.

Prepared the upstream merge locally in two ordinary merge commits, without conflicts. GitHub synced both parents in merge 13d619b4, whose complete tree exactly matches the locally tested merged tree 4ff10f75. The renderer's Android pointer path and ui_widget profile-keyboard handling survive the merge. The Java touch overlay, native virtual pad, SDL routing, guest imports and keyboard hit map are unchanged from the phone-tested baseline.

Added production-function regression coverage for touch pad priority and player 1 ownership across split-screen/profile transitions, preserving physical-controller behaviour. All local touch tests pass after both merges. Android CI now runs them before compilation. Local broader port checks lack pytest/clang; the repository's CI provides those dependencies and will run its build/test jobs. No phone/emulator is connected for a new gameplay test.

Prepared version 0.3.0-touch (Android version code 3), short changelog and release instructions. Release APK/build validation pending CI; packaging must include dependency licenses. The fork has no persistent signing secret, so a new runner key can prevent installation over older builds.


## 2026-10-07 mobile fork integration / 0.4.0-touch

User approved the recommendations from theLlamaNet/halo-ce-android and JoshRob297/halo-ce-touch, especially video, and authorized commits/push/release with credits. Baseline touch-controls 93ec01b (0.3.0-touch). Feature references: Llama 2f469d2; Josh main 8a6fe36; clean Bink branch 79847b0. Selected/adapted patches rather than merging either older full fork: retain upstream network protocol 22, desktop builds, latest co-op, SDL virtual input, editable layouts and direct profile-keyboard taps.

Added mobile settings/input/cheats/camera bridge beside existing host_touch.c; layouts import both forks' Properties format; movie-only disc import leaves maps/profiles intact. Compile FFmpeg 8.1.3 Bink decoder from checksum-pinned official source; package LGPL notice/source/relink materials. Fixed held-input handoff to movie playback, playback pause/error recovery, case-sensitive filenames and language lookup, repeated asset registration and decoder clock waiting. Server rotation keeps co-op setup and requires normal readiness/precache conditions before forced start. MQTT relay retains current MQTT5 broker/listing/backpressure behavior.

Local actual-production regressions pass for fast taps/cancel/controller ports/menu coordinates/profile keyboard, portable layouts/malformed files, gyro rotation/time gaps/noise, startup init.txt preservation, synthetic disc import, native movie progress/skip/timeout/reopen/languages and mobile JNI bridge. No phone/emulator or game assets connected. Full debug/release Linux/Windows/Android CI and final release packaging still pending.

Completed validation: release source c40f59833f45d9cb130970d5f91f5cc1ad1dfd51 (tree 8cbfc4d12cf797c36f44191154b178d35f9b046f) passed Android, Linux and Windows debug/release builds in run 37638620788. Android ran the original touch/profile regressions and expanded mobile/server/relay tests; Linux port tests reported 11 passed and 4 skipped. Fixed remaining menu text-scaling calls for current upstream, provided an aim pad for imported layouts and tested removal of panel-owned campaign cheat flags before hosted or joined multiplayer.

Published v0.4.0-touch with OpenCE-Touch.apk, packaged Android build and SHA256SUMS.txt. Independently verified the artifact digest, APK ZIP integrity, arm64 native decoder/JNI entry points, guest ELF, absence of bundled maps/videos, dependency licenses and exact FFmpeg source/relink archive. APK SHA256: 10cfddd9b7e2f8cbaedece53ecf5802bfda5713a3cfc31a57e7ead9a9261fb9a. README and release credit theLlamaNet/FulGer, JoshRob297 and FFmpeg and retain AI disclosure. Real-phone gameplay, gyro/rumble, video/audio and Internet relay remain unverified; temporary CI signing can prevent updates over an older APK, so back up profiles/saves before uninstalling.


## 2026-10-08 upstream update

Baseline: touch-controls 062566acd90461f35687006ac55610e17f23d615 (0.4.0-touch).
Selected upstream: 2d2348cd7db935cd11024e160241fc8315e13447, 88 new commits; Linux, Windows and Android debug/release jobs all passed in upstream run 37756123632.

Resolved the Android third-party cache conflict by tracking both Bink build inputs and the SDL relative-mouse patch. Resolved server countdown conflict by keeping upstream's solo-host/team/minimum-player behavior together with fork countdown diagnostics, rotation and precache guards. Removed the superseded local-machine helper. Added production-code regressions for solo hosting, team readiness, minimum players, unowned machines, precache and dedicated-server state.

Existing Android Java controls/layout/gyro/settings/movie code, host touch/mobile/movie bridge, decoder, virtual-gamepad implementation, MQTT relay, profile-keyboard handling, cheats and rumble files remain unchanged from the 0.4.0 baseline. Upstream moves the network protocol from 22 to 24; multiplayer peers need a compatible build.

Local touch and expanded mobile regressions passed with the existing project JDK. Upstream asset-free harness and full merged-source Linux/Windows/Android CI validation pending. No connected phone, emulator or game data, so no new gameplay/audio/video/Internet/gyro/rumble validation is claimed.

Popular forks are being reviewed separately. No new third-party fork feature is part of this upstream merge. No release is requested by this task.


Completion checkpoint: local merged-source touch and mobile checks passed; Linux tooling pytest: 8 passed, 7 skipped (no clang/32-bit compiler environment). Native light-storage and upstream harness execution are blocked by the missing clang/lld/32-bit libc toolchain. These are environment failures, not established source failures.

Remote publication is blocked: git push has no authenticated credentials; GitHub create_blob returns 403 Resource not accessible by integration. The connected login is Jantam11, but list_installations, list_installed_accounts and owner-filtered list_repositories return empty. No branch, PR, remote commit or release was created; touch-controls remains 062566ac. GitHub plugin is installed. The account connection needs repository write access, or explicit permission for signed-in browser fallback, before publishing a staging branch, running full CI and updating touch-controls. Browser fallback has not been initialized.

Fork review: retrieved the top 100 direct forks ranked by stars, examined the top 12, plus JoshRob297/halo-ce-touch, RadlikesBurgs/halo-vulkan and astromaddie/HaloCE-VR. Leading candidates: ChupathingyCE shader warm-up/cache, plasma-pistol loop lifetime repair, menu/profile I/O reduction, profile-keyboard Enter handoff, audio quality option and dedicated-server tooling; DamnationCE map picker/themes and selected CE/co-op behavior; thelinkin3000 optional Android Vulkan/Turnip backend and relocatable memory window. Existing Llama and Josh features are already integrated. Platforms/VR/browser features are expansion projects. No new fork feature was imported. Evidence and comparative JSON are in /workspace/scratch/e518e782cfe5/fork-review; current branch update-touch-20261008 in /workspace/scratch/e518e782cfe5/OpenCE-Touch.
