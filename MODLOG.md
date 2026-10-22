# OpenCE-Touch maintenance — 2026-10-09

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
