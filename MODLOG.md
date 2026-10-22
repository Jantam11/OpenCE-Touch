# OpenCE-Touch maintenance — 2026-10-09

## 2026-10-22 — 0.6.3 release request

User explicitly requested publishing a 0.6.3 APK, a short experimental
Xash-style controls changelog and minor Xash3D-FWGS team credit. Bump version
to 0.6.3-touch / Android code 14; tag v0.6.3-touch. Publish only after this exact
revision passes Android debug/release and regressions. Use Build's direct
publisher, never the legacy artifact-based Touch release workflow: account
Actions artifact storage remains full. Include APK, licensed ZIP and checksums.
Phone gameplay remains unverified; original pads remain default. Prior feature
code d1782a5a passed Android CI 39786139012; release CI is a separate gate.

## 2026-10-22 — optional Xash-style screen regions

User requested inspection and an alternative movement/look system; keep the
existing controls. Started from remote touch-controls c2e23836 (0.6.2).
Examined FWGS/xash3d-fwgs d6b54aaf6c1d8518e08404a842f3f6ee02cef3cc,
engine/client/input/in_touch.c. Chosen route: implement its floating _move and
relative _look behaviour in Java, preserving this fork's SDL virtual pad,
relative mouse, gyro, editable buttons, menu/profile/chat input and classic pads.

Original pads remain default. OPTIONS → Control system enables screen regions;
divider/handedness/axis travel are configurable and persist/export with layouts.
The new TouchRegions class and actual TouchControls event router pass synthetic
multi-finger/ownership/crossing/cancel/menu/chat/editor regression checks.
Java layout/gyro/HUD, old/foreign/new layout import, native mobile/JNI, existing
touch/controller/profile-coordinate, camera, chat, renderer/Quit/themes,
display-option and per-tick input checks passed locally. Local JRE compiler
and official OpenJDK JNI headers were used without installing an SDK.

Android CI 39786139012 passed on d1782a5a: debug/release APK compilation,
touch/mobile/JNI, 32-bit chat/filter/mixer and final layout/gyro/HUD/region checks.
Both artifact upload steps and release publication were skipped. Local keyboard
ASan/UBSan checks also passed with leak detection disabled for this host's /proc
restriction; six menu/config pytest checks passed. No phone or game data is
connected, so gameplay remains unverified. This is an unreleased source feature;
0.6.2 remains the published APK. Keep future validation Android-only and skip
Actions artifact storage. See docs/android_touch_regions.md for source
attribution, scope, compatibility and exact phone acceptance checks.

Work starts at 5a9c7892 on touch-controls. Chosen route: merge validated upstream f479e349 with both parents, adapt narrowly selected credited-fork fixes, validate on an isolated CI branch, then advance touch-controls and publish its Android artifacts. Existing release v0.5.1-touch is the rollback point. No game files or signing keys are accessed.

See INTEGRATION_NOTES.md for revisions, conflict decisions and local checks. GitHub CI is required for full builds and 32-bit regression execution. Compilation is separate from phone gameplay verification.

Initial integration run 37933045092: Linux debug/release passed; 224 tests passed, 16 profile fixture compile failures. Fixture repaired; native lifetime/negative-control tests pass. Final validation includes version 0.5.2-touch/code 7 and package checks for Opus/Lucide notices.

## 2026-10-12 update

Started at c2c1705a / v0.5.4-touch. Merged upstream build-190 and DamnationCE touchscreen selection fix. Protocol 27; version code 10. Preserve v0.5.4-touch as rollback. Android CI gates publication; no phone gameplay claimed. Git HTTPS push has no credentials, so publish Git objects and refs through the authorized GitHub connector.


## 2026-10-17 — uncommitted Android update review

Maintainer explicitly requires feature review before any commits or release. HEAD remains 650d18a8 (v0.5.5-touch). Prepared an uncommitted merge of validated upstream 01797c04 (82 new commits; upstream run 39004295351 passed all platform jobs). Resolved audio config/documentation and theme/font conflicts; themed Graphics menus retain styling and expose the new HUD button style.

Reproduced the current release resetting high_res_hud=false to true after a fresh process because duplicated config sections invalidate the entire TOML file. Upstream 1e794665 repairs it; expanded its production Android-config test for mixed ON/OFF, resampling/theme and unrelated writes, and included it in Android CI. Detailed evidence, candidate forks, exact validation limits, and a draft changelog are in docs/android-update-review-2026-10-17.md. No optional fork candidates imported. No commit, push, tag, CI dispatch or release. SDK/NDK and full JDK absent; integrated APK and phone checks remain pending, not passed. Continue from the existing merge working tree after maintainer choices; do not run another merge blindly.


## 2026-10-17 — selected 0.6.0 integrations

User approved upstream plus A/B/C/D/E/F/G and conditional J, commits and release with brief donor credits. Implemented selected features, optional display defaults and supported privacy controls; see INTEGRATION_NOTES for revisions and MCC deferral evidence. Local Java/JNI/HUD/settings/touch/camera/render/map checks pass after acquiring only official OpenJDK JNI headers and using the runtime compiler. Full Android CI debug/release is still mandatory. Prepare version 0.6.0-touch / Android code 11, publish only after CI. Existing workflow already gates publication on Android success.

## 2026-10-22 update

Prepared upstream fc22e846 merge (273 commits, upstream all-platform Build 39766822484 green), ChupathingyCE 4d0f50c8 rapid-tap adaptation and 0.6.2 release candidate. See INTEGRATION_NOTES.md for source review and validation. GitHub Actions artifact storage is full: direct upload from the checked Android job replaces artifact transfer on touch-controls. Never use the legacy artifact-based publisher for this candidate. Final release is conditional on Android CI; local JNI/toolchain and phone gameplay unavailable. GitHub connector saved the workflow successfully; no browser sign-in was needed.


Final Android CI run 39779955644 on 9f80176bc615d3e228215bc40b6927d03551516a passed touch/mobile/JNI, 32-bit chat/filter/mixer, debug/release APK builds and Java layout/gyro/HUD checks. Direct publication of v0.6.2-touch succeeded with OpenCE-Touch.apk, halo-android-release.zip (licenses/FFmpeg relinking) and SHA256SUMS.txt. Both Actions artifact uploads were skipped. Synthetic publisher checks also validated packaging/checksums/notes and rejection of missing licenses. Physical-phone gameplay remains unverified. Roll back by installing v0.6.1-touch after backing up saves/layouts; protocol 29 peers differ from this release's protocol 32. Temporary CI signing keys may require uninstalling before installation.
