# OpenCE Touch input repair

Repository: Jantam11/OpenCE-Touch, touch-controls, base e422bfa1e8bbb82d4c47e80e4967016b27a7d402.

User phone test: gameplay key buttons type letters in profile entry; backing out leaves controls ineffective; MENU only hides controls and taps do nothing.

Source evidence: xinput_sdl.c diverts keyboard keys to text entry. Android excludes menu mouse event routing in sdl_platform.c and returns zero from halo_ui_pointer_update in d3d8_gl.c. The original overlay sends only keyboard/mouse events.

Route: SDL virtual gamepad for touch buttons/movement; keep relative mouse swipe aim; enable the existing menu pointer coordinate conversion on Android, with absolute mouse button coordinates. Do not alter saves or game data. Test native input sequences, compile Android, verify APK contents; game execution unavailable in this workspace.

Completed source changes: SDL virtual gamepad; automatic menu mode hints; SDL mouse routing on Android; profile keyboard hit testing using real rectangles; absolute pointer down/up coordinates; v2 layout mapping migration; version touch 2.

Local regression checks passed for short taps, multiple held buttons, release/reset, scaled and letterboxed menu coordinates, letters/backspace/DONE/cancel and inactive keyboard. Build and phone validation pending. No phone/emulator is connected.
