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
