# Optional Android movement/look regions

## Source and scope

Requested as an alternative to the current editable controls. Implementation
starts from OpenCE-Touch `c2e238362540843132e3fadda900b3a776193011` on
`touch-controls`, after the 0.6.2 release.

Examined [FWGS/xash3d-fwgs in_touch.c at
d6b54aaf6c1d8518e08404a842f3f6ee02cef3cc](https://github.com/FWGS/xash3d-fwgs/blob/d6b54aaf6c1d8518e08404a842f3f6ee02cef3cc/engine/client/input/in_touch.c):
`Touch_Init`, `Touch_Motion`, and `Touch_ButtonPress`. Credit to mittorn
and FWGS contributors. That source carries GPL-3.0-or-later notices. This is a
new Java implementation of the region behaviour, rather than vendored Xash
engine code. No Xash textures, console commands or game assets are included.

Xash's default regions divide the full screen at x=0.5. Its `_move` captures
the first contact as the movement origin, divides horizontal/vertical
displacements by `touch_sidezone`/`touch_forwardzone` (both initially 0.06), and
clamps each axis. `_look` accumulates finger deltas. Each region has one finger
owner; release clears movement. These are the behaviours adapted here.

`TouchRegions.java` owns the two pointers and computes displacement/deltas.
`TouchControls.java` gives editable action buttons and the toolbar priority,
then offers empty gameplay space to the regions. Movement uses `TouchInput.move`
and the existing SDL virtual gamepad. Looking uses the same relative SDL mouse
path and sensitivity as the existing aim pad, including fire-button drag and
gyro support. It does not import Xash's sensitivity units or nonlinear curves.

This is the requested movement/look alternative, not the entire Xash control
editor. Arbitrary overlapping rectangular zones, Xash config files, wheel
commands, latching and nonlinear aim are outside this change. Existing circular
pad/button layout storage and native menu handling remain in place. No native
ABI, protocol, game simulation or controller bindings change.

## Use and compatibility

Open **OPTIONS → Control system → Xash-style screen regions**. **Region
settings** adjusts the divider, movement side and travel distances. Lower travel
values reach full speed with a shorter drag. Choose **OpenCE-Touch pads
(original)** to switch back; the saved pad positions and action buttons remain.
**EDIT** displays the original editable layout in either mode. Layout presets
change buttons/pads while retaining the selected control system and tuning.

The default remains original pads. New preferences use the existing
`touch_controls_v3` store. The existing version-1 `.halolayout` format gains
optional `screen-regions`, `region-move-right`, `region-split`,
`region-side-zone` and `region-forward-zone` properties. Old files omit them and
default to pads. Foreign halo-touch-layout imports also use pads. Invalid
divider/travel values are rejected before an imported layout is applied.

## Verification

- `python tools/test_touch_regions.py` compiles the production touch-event
  handler, hit testing, mode transitions and release methods with platform
  stubs. It checks classic pads, region/button priority, simultaneous movement,
  look and fire, pointer index reordering, crossing the divider, extra fingers,
  cancellation, menus/profile/chat, the editor and disabled/movie modes.
- `python tools/test_touch_layout.py` includes production region geometry and
  ownership tests across resolution/handedness/divider changes and invalid
  events, alongside existing layout/gyro/HUD checks.
- `python tools/test_android_mobile.py` checks mode/tuning round trips,
  compatibility with old/foreign files and invalid-value rejection, alongside
  the existing Java and native mobile checks.
- Android CI runs these before debug/release APK compilation. On
  `touch-controls`, it skips Actions artifact storage. Release commits publish
  the checked APK and licensed package directly from the runner.

Local deterministic tests and Android compilation do not establish phone
gameplay. No phone or owned Halo game data is connected in this session.

[Android CI 39786139012](https://github.com/Jantam11/OpenCE-Touch/actions/runs/39786139012)
passed on source commit `d1782a5a01af95faddde7d41fad9838f5454cf5e`:
debug and release APK compilation, full touch/mobile/JNI regressions, 32-bit
chat/filter/mixer checks, and the final layout/gyro/HUD/region tests. Desktop
and web jobs, both artifact uploads and release publication were skipped.
The feature is included as an experimental option in
[0.6.3-touch](https://github.com/Jantam11/OpenCE-Touch/releases/tag/v0.6.3-touch).
[Release CI 39789651866](https://github.com/Jantam11/OpenCE-Touch/actions/runs/39789651866)
passed the Android debug/release build/test gate and direct publication on
`e4b244b1d1ded24fcf6a0b53f3bfe7d198893a10`. The APK, licensed ZIP and checksums
were uploaded without Actions artifact storage. The original 0.6.2 APK does
not contain this feature. Phone gameplay remains unverified.

## Phone acceptance checks

1. Keep original pads selected after upgrading; confirm movement, aiming,
   profile naming and menu taps still work.
2. Select screen regions in a campaign. Start movement at several empty
   locations on the left; hold a displacement and confirm movement continues.
   Move the right finger and confirm the view stops when it stops.
3. Move, look and hold fire together. Lift fingers in different orders, cross
   the divider, and try a second finger in an occupied region. Confirm no
   ownership stealing or stuck movement/fire.
4. Open pause, chat/profile keyboard, change app focus and resume. Confirm
   gameplay input clears and menu taps remain accurate.
5. Change the divider, movement side and travel; save, restart, and round-trip
   a `.halolayout`. Check the settings and buttons survive.
6. Switch to original pads. Confirm their saved locations, actions and fqlx
   preset/editor still behave as before. Gyro/fire drag need hardware checks.
