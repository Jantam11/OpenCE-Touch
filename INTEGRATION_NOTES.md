# 0.5.4-touch upstream update

Merged only OpenCE's 12 new commits since bd98c8fb, through 9da2a45ffa364b720ae9faab6a1dee876926fe42. Upstream run 38042641991 passed all platform builds. Changes cover Android ART overlap recovery and early reservation in a separate game process, memory diagnostics, controller icons and reticles. Only the Android README conflicted; retained this fork's controls and Bink documentation. No additional fork commits selected. Integrated release checks are Android only.

# 2026-10-10 Android upstream and credited-fork review

Baseline: v0.5.2-touch / `0457f232`. Merge OpenCE `bd98c8fb20c1638bb66e22c94f61b739dcb45033`, preserving both histories. Its code parent `5e8ab023` passed the Linux, Windows and Android jobs in upstream run 38025177205; the final commit changes documentation only. Integrated testing on touch-controls is Android only.

Upstream includes protocol 25, co-op integrated lights/respawn fixes, frame-throttle sleeping, gamepad/profile-save fixes, rendering/audio/memory repairs, wider menu setting targets, in-game campaign Settings and FOV/viewmodel settings. Preserve the SDL virtual gamepad, editable/importable layouts, mouse-based swipe/gyro input, flying camera, native profile taps, main-menu confirmed Quit, Bink movies, map browser, menu themes, shader cache, Sinc/Linear audio and relay. `HALO_TOUCH_SDL_GAMEPAD` selects the fork overlay and excludes upstream's second overlay consumer. Both guest ABI and GLES macros are set after upstream's Android macro split. Settings/theme XML is regenerated from the settings generator.

Forks checked after upstream:
- DamnationCE `e8d806dd`: imported `ff654a77` by xshxdex98, guarding release of an absent progress-capture depth buffer. Its Windows PGO refresh and uncapped frame-limit policy are not Android additions selected for this release.
- ChupathingyCE `eccc6ec4`: new BC7 support `44a03b5b` relies on that fork's `ce_repairs` and `ce_resources` conversion pipeline, absent here. It was reviewed but not imported as an isolated patch. Its broad converter/hardening series remains a separate integration.
- FulGerNet/halo-ce-android `28e0e27f`: unchanged; camera ownership fix retained.
- JoshRob297/halo-ce-touch main `8a6fe36c`: unchanged. Movie branch bink-on-main `79847b0e` and all advertised branch heads checked; no newer movie code selected.
- fqlx/OpenCE: GitHub API still returns 404; existing compact preset and credits retained.

Local checks cover production touch taps/cancellation, controller routing, menu coordinates/profile keyboard, flying-camera delta ownership, renderer-upload race and Quit negative controls, optional depth-buffer release with a negative control, and no second overlay consumer. Four menu themes and upstream touch gesture tests pass. Keyboard address/undefined-sanitizer cases pass with leak checking disabled locally because this execution host cannot inspect /proc task entries; Android CI runs the normal sanitizer check. The complete Java/native mobile tests and Android debug/release compilation must pass in CI before publication. Initial Android CI 38032638611 compiled the guest/host sources but caught an unused upstream host_touch_read import at host link; removed that import because this branch uses the SDL virtual gamepad. The release remains gated on a clean rerun. No phone or owned game data is connected; no gameplay, microphone, gyro/rumble, physical GPU, movie playback or live multiplayer verification is claimed.

# 2026-10-09 upstream and credited-fork review

Baseline: `5a9c7892` / v0.5.1-touch. Merge OpenCE `f479e34914604df5a22a2bdb0b38f180a1f702d8`, preserving both histories. Its Linux, Windows and Android jobs passed in upstream run 37922923202. This advances 136 upstream commits (including side-branch history) from `73dc01d0`.

Upstream adds voice chat, vote kick, categorized co-op options, camera interpolation and cyborg animation improvements, renderer transparency/overshield ordering fixes, faster audio mixing/resampling, safer map strings and network input, an Android icon, Steam Deck support and desktop screenshots. Network version remains 24. Android screenshot action remains upstream's no-op. Voice chat needs microphone permission and a network game; hardware/Internet voice behavior has not been tested here.

Conflicts were resolved by retaining Android direct menu/profile pointer routing, SDL virtual gamepad and host hint bridges, shader caching, Bink movies, relay helpers, editable layouts, independent Sinc/Linear audio, themes/map browser, and playlist server support. Regenerated settings and theme XML so upstream voice/co-op controls are available. The mirror-upload fix and Android Quit now also have upstream history. New Opus/ISC notices are packaged alongside existing FFmpeg and font notices.

Credited sources checked after upstream:
- ChupathingyCE main `b78e6cfa`: most relevant fixes are already merged upstream. Additionally adapted `d4ff4cc2` (bounded cache-header name), `d009a4bf` (custom campaign completion cannot write outside profile flags), and `4c6e68a6` (script speed must be finite and in 0–100). Its Delta service, large CE conversion/hardening series and changed server protocol are not imported.
- FulGerNet/halo-ce-android (renamed from theLlamaNet), main `28e0e27f`: adapted free-camera input ownership from `f1c3c4d4`, including the earlier rising-edge Zoom toggle needed when a 30 Hz snapshot spans several frames. Kept our movement speed and menu geometry. Production camera regression verifies player-before-director delta ownership, sensitivity, normal cameras and repeated input snapshots.
- JoshRob297/halo-ce-touch: main `8a6fe36c`, movie source bink-on-main `79847b0e`, and all advertised branches reviewed; no newer movie commits since the prior integration.
- DamnationCE main `37fcd24e`: upstream voice/co-op additions already arrive through this merge. Recent broad source/type cleanup and the Battle Creek hotfix address its divergent 64-bit/type cleanup; our 32-bit transparent BSP buffer code has not undergone that change. Do not import that cleanup into Android. No additional theme/browser feature selected.
- fqlx/OpenCE: HTTPS fetch and GitHub API both fail (404/unavailable); current commits cannot be verified. Existing credited compact preset is preserved.

Local checks: touch/coordinate/profile pointer, camera ownership, Java layouts/gyro/startup cheats/disc import, native movie/mobile bridge, renderer/Quit negative controls, keyboard lifecycle with address/undefined sanitizers (leak checking unavailable on this host), sound lifecycle/transition, map browser and dedicated-server checks passed. XML/settings tests passed. Initial integrated CI run 37933045092 built Linux debug/release, then reported a profile-keyboard fixture missing our retained text_typing_enter_blocked state. Updated the fixture to include that state and release held Done before simulating a fresh Enter; all 16 cases/negative controls pass natively. The 224 other upstream checks passed. Full platform builds and the 32-bit upstream harness run again in GitHub CI before release; this host cannot execute 32-bit binaries. No phone, owned game data or second network client is connected, so no gameplay/voice/gyro/rumble testing is claimed.

# 0.5.1 Android visual/exit repair

Baseline: `e4c22f8f` / v0.5.0-touch. User gameplay screenshots show stretched red wall polygons and missing floor/ceiling geometry in a10, plus a30 lifepod geometry artifacts. Diagnosis: the inherited Android renderer has the still-unmerged upstream #165 Mali buffer-copy race. The symptoms are consistent; no device logs or controlled upstream-versus-fork phone run are available to establish this as the only cause.

Adapted kirklandsig's `343eef15ccc10e211059ebd1f9a26995b0904317` PR #165 change: track synchronized mirror uploads per 4 MiB segment and defer first-use unsynchronized writes until the three-frame fence ring passes the copy. The new regression compiles production mirror_refresh and models delayed GPU copies, including same-frame loads, adjacent pages, segment independence and unsigned frame rollover. Restoring the old condition must fail. Known upstream limits remain: host mapping failure silently falls back to subdata, and a timed-out fence can still proceed. No physical GPU behavior or performance is established by this model.

Quit: commit `a97cd967` in this fork had replaced native Quit artwork/taps/controller actions with Porting options and suppressed root Back. Removed that interception and moved Porting options to the next row. All four PC-style native menu themes already provide Quit → confirmation → exit and Back cancellation. Adapted only the Android exit change from FernandolDev's PR #183 (`dc71f682`); did not add its optional debug-package feature. The existing guest exit reaches host_exit, which ends the app process. Pause-menu functions are unchanged.

Checks: local Android touch and production mirror/exit regressions pass. The mobile suite's Java/configuration/gyro/import, single-player, relay and countdown checks passed locally; native JNI checks need headers absent on this host and will run in Android CI. Full Android debug/release builds and the complete mobile suite are required before automated publication. Desktop build jobs and Discord notifications are skipped on touch-controls. Version code 6, version name 0.5.1-touch; protocol remains 24.

# 2026-10-08 integration

The baseline was OpenCE-Touch `062566ac` (v0.4.0-touch). Upstream
`OpenCommunityEdition/OpenCE` was initially advanced to `2d2348cd` in merge
[`f6c912ff`](https://github.com/Jantam11/OpenCE-Touch/commit/f6c912ffa30bb55969edd8b4f232fbae861b14ee).
Both parents are preserved; 88 upstream commits bring the native rendering,
co-op, networking and menu changes forward. Network protocol is now 24 as in
upstream. Previous protocol-22 builds need updating to join protocol-24 games.

[Upstream-merge CI](https://github.com/Jantam11/OpenCE-Touch/actions/runs/37762090042)
passed Linux, Windows and Android debug/release builds and the existing tests
before the merge was published to touch-controls.

A final upstream check also merged `73dc01d0` in
[`d3b86268`](https://github.com/Jantam11/OpenCE-Touch/commit/d3b86268f4ff555dc54558a9723c3889e501b705),
preserving the ChupathingyCE sound changes and both upstream histories.
These three additional commits repair positional stereo distance attenuation
and reverb; all upstream platform jobs passed in run 37764567816. The complete
update contains 91 new upstream commits.

## Selected fork ports

The ports adapt selected source changes to the current upstream and existing
Android touch stack. They do not import each fork's entire divergent history.

| Source | References | Changes |
| --- | --- | --- |
| [ChupathingyCE](https://github.com/ChupathingyCE/chupathingyce) | `acd2087a`, `45677e54`, `fc525201`, `fb47309a` | Looping-sound ownership/stop lifetime, underrun resume, avoid repeated profile/map I/O during menu frames; tests adapted to current upstream functions. |
| ChupathingyCE | `916cf2fe`, `4575f6e6`, `771a257f`, `37951253` | Return/keypad Enter restored after virtual keyboard exit, allow deleted profile names to be reused, paused multiplayer input inhibition and keyboard crouch. Android native keyboard hints are preserved. |
| ChupathingyCE | `51093bf3`, `21c90775`, `a551abf5`, `63ea522f`, `edfd2cda` | Finer mouse sensitivities, persistent GLSL source/pair cache and bulk warm-up, Windows replacement fix, Sinc/Linear audio choice independent of reverb. Existing upstream sinc optimization and reverb remain. Cache reads/writes are capped at 48 MiB. |
| ChupathingyCE | `dc4518a6` playlist director; `40e8bc8d` score helper | Optional no-window/no-audio desktop hosting, player limits, map/type playlists, automatic countdown with existing readiness/precache checks, post-match rotation, score-idle/empty-game recovery. Launcher, example playlist, optional systemd/Docker templates. Uses this fork's brokers/protocol; no Delta online identity/statistics service. |
| [DamnationCE](https://github.com/xshxdex98/DamnationCE) | Map picker/overlay from `91493038`; Cairo/theme generators from `add42e6e` | Stock/custom map categories, list/grid pictures, co-op campaign and difficulty; pointer/pad input reuses our existing routing. Optional Glassed/Cairo/Vanilla themes are regenerated over our current menu definitions, preserving visible native lobby/settings behavior. Default is selected initially. |
| [fqlx/OpenCE](https://github.com/fqlx/OpenCE) | `8102b91f`, browser `port/web/site/input.js` / CSS compact controls | Compact 14-control native Android preset. It reuses normal button/action geometry and `.halolayout` version 1; users can edit/export/import it. Preset selection replaces buttons only and retains general gyro/rumble/input preferences. No automatic switch on upgrade. |

Source credits and AI disclosure are in README. Theme/overlay fonts carry SIL
OFL/CC0 notices, copied into packaged builds and Android license assets. Theme
art is generated; no Xbox/PC map assets were added to the repository.

## Use

- Themes: Settings → Video Setup → Menu Theme → save → restart. Default restores
  OpenCE's previous menus. Optional themed main menus also include a Menus
  selector. Theme changes are intentionally applied on restart.
- Map browser: enabled independently of themes. `display.map_browser=false`
  (`HALO_MAP_BROWSER=false` on desktop) keeps the original map list. Installed
  compatible maps are shown; the browser does not download a community pack.
- Compact controls: Android OPTIONS → Layout presets → fqlx compact. Export
  your current layout first if you want to retain it. Default remains available.
- Audio: Settings → Audio Setup → Resampling. Sinc is default; Linear costs less
  CPU and is an optional quality tradeoff.
- Servers: [server/README.md](server/README.md), ordinary Linux/Windows binaries,
  your own map data, and a separate persistent save/cache folder.

## Regression and validation limits

The original mobile checks still cover touch taps/coordinate mapping, virtual
pad ownership, portable import/export, gyro/startup-cheat settings, multiplayer
cheat isolation, disc/movie import, movie/JNI lifecycle, relay bounds and network
rotation/countdown/precache. The new compact layout round-trips all 14 controls.

Added checks exercise real sound and keyboard production functions, stock/CE
map filtering and co-op/PvP selection/back navigation/empty-list cleanup,
playlist parsing and rotation/idle/empty recovery, and the restriction that only
the local dedicated host may lack a player. Menu XML references, handlers,
settings and artwork are checked separately for all four themes. Changed native
sources and the generated embedded assets compile locally as 32-bit objects.

[Final integration CI](https://github.com/Jantam11/OpenCE-Touch/actions/runs/37769789258)
passed for code commit `3897fc42`: Linux, Windows and Android debug/release
builds and the available regression checks. The resulting source also includes
native split-screen/next-map browser entry points and desktop-only SDL/GL guards
for the Android guest. This environment has no connected Android phone/emulator, owned game
assets, or live second client. Compilation and deterministic regression checks
cannot prove visual layout, gameplay, gyro hardware, driver shader warm-up or
live-server joins/rotation. Docker/systemd templates are supplied, not deployed.

## Pfista community-map management: proposal only

[pfista/halo-og](https://github.com/pfista/halo-og)'s
[community-map guide](https://github.com/pfista/halo-og/blob/main/docs/community-maps.md)
describes a curated multiplayer-map collection, compatible **Xbox v5** maps
rather than a generic arbitrary-map downloader. Its manifest records names,
file sizes and SHA-256 hashes so known compatible files can be recognized;
different maps with the same filename can remain distinct. Changed map files
refresh their decompressed cache, maps remain usable offline, and the desktop
layout preserves map/profile/save data across app updates.

Desktop setup can fetch roughly 40 maps (about 863 MiB). Android's documented
path is manual installation, so adding this to our app would also require a
mobile download/storage flow. This is separate from DamnationCE's map picker,
which lists installed maps.

Recommendation: if approved later, add explicit per-map opt-in downloads,
progress/cancel/retry, compatibility/hash checks, available-storage checks and
persistent offline storage. Avoid automatically downloading the whole pack.
No pfista downloader/map-management code or map files are included in this
integration; it was requested for explanation only.
