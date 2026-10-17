# Android update review — 2026-10-17

Prepared locally on `touch-controls`, based on `650d18a8` / v0.5.5-touch. Initial review was uncommitted. The maintainer subsequently approved upstream plus A/B/C/D/E/F/G and conditional J. Selected integration is in progress for 0.6.0; see INTEGRATION_NOTES for the implemented state and validation gate. J is deferred because the combined Android integration/runtime is unverified.

## Upstream

82 commits are new from the fork's HEAD to OpenCE `01797c043430570c389d75b7e5bb236744ab0f9b` (build-217). [Upstream run 39004295351](https://github.com/OpenCommunityEdition/OpenCE/actions/runs/39004295351) completed successfully, including Linux, Windows and Android jobs. This is upstream evidence; the combined fork has not passed an APK build yet.

The local merge retains both histories, the Android-only fork CI policy, SDL virtual controller, touch/profile taps, gyro/camera controls, confirmed Quit, movies, map browser, themes, relay, shader cache and Sinc/Linear audio settings. Resolved source conflicts combine themed font selection with upstream font metrics and preserve fork audio settings. Regenerated themed Graphics settings retain their colors and header positions.

Notable upstream changes: client-side texture/sound/text resource packs with enable/disable and load order; live high-resolution HUD/text changes and button styles; pause/postgame menu repairs; co-op respawn/teleport and remote vehicle/body corrections; map-sharing/input validation and voice-frame hardening; GLES base-vertex extension support. Network protocol increases from 27 to 29.

## Settings reset: reproduced and repaired in the working tree

The old defaults writer repeated `[display]` when settings for that section occurred later in its definition table. TOML rejects duplicate tables and the application falls back to defaults at the next launch. Compiling the current release's `port_config.c` with Android/guest defines reproduced it: write `display.high_res_hud=false`, read in a fresh process, receive `true` and `table defined more than once; using the defaults`.

Upstream [1e794665](https://github.com/OpenCommunityEdition/OpenCE/commit/1e7946659c5497c0448712bd1c3c60d1facc1da9) writes each section once and repairs existing duplicated sections. Its production-code regression passes on the merged fork. Extended coverage verifies mixed ON/OFF choices, audio resampling and theme choices across fresh processes and unrelated subsequent writes. Added this regression to the Android CI selection.

This proves a configuration reset mechanism, not every possible device-specific loss. Java touch preferences already save on changes through SharedPreferences; Android lifecycle and immediate process termination still need device checks. Profile choices also need their normal OK/save action. No phone logs were supplied for this incident.

## Fork candidates (not integrated)

Reviewed newest/popular fork listings covering 126 distinct repositories, then inspected selected source trees and recent commits. Listing a fork is not equivalent to auditing all its code. Priority suggestions:

| Option | Source and revision | Candidate | Assessment |
| --- | --- | --- | --- |
| A | [ChupathingyCE](https://github.com/ChupathingyCE/chupathingyce/commit/dba13a105f9b2b204071a6ea0d13b52685003c15), follow-up `415f8ea5` | Keep system bars hidden after dialogs/resume; selectable CPU/GPU texture decoding with Adreno workaround | Recommended Android fixes; retain the fork's activity, touch and movie lifecycle. Device GPU testing needed. |
| B | [FulGerNet](https://github.com/FulGerNet/halo-ce-android/commit/db04b1d4) | Drag weapon, health and radar HUD panels; native-looking Porting options | Best mobile feature. Adapt HUD editing separately to preserve this fork's Quit and virtual gamepad. Main unchanged at `3bf59027`. |
| C | [DamnationCE](https://github.com/xshxdex98/DamnationCE/commit/3bd966cf4) | Click/tap setting arrows | Recommended touch improvement; source/input regressions required. |
| D | [DamnationCE](https://github.com/xshxdex98/DamnationCE/commit/98889fc72), `335c6522e`, `472d23224` | Measured server pings, ping colors and clearer selected rows | Useful for Android multiplayer. Ping code touches relay/signalling; adapt carefully rather than merging the entire fork. |
| E | [ChupathingyCE](https://github.com/ChupathingyCE/chupathingyce/commit/2b752f7d38c3370e6114285442c0fe5a8bf2fe82), follow-up `7b30ce62` | Optional powerup timers and restored classic loading screen | Good optional visuals; timers off, added load delay zero by default. |
| F | [ChupathingyCE](https://github.com/ChupathingyCE/chupathingyce/commit/f930d22cc16ae593793c35ca2b4b2077f5deb032) | Configurable far draw distance | Useful on large maps; keep stock default because phones may lose performance. |
| G | [ChupathingyCE](https://github.com/ChupathingyCE/chupathingyce/commit/36e6fc86e2b1924b9985c400a0df66e953bf8844) | In-game reporting/privacy controls | Useful independent addition; fork lacks some Chupathingy reporting services, so expose only controls actually supported. |
| H | [Quake Edition](https://github.com/XplosivBolts/OpenCE-Quake-Edition), main `510a73a7` | Optional Quake movement/projectile presets and speedometer | Large gameplay change. Separate opt-in project, with explicit multiplayer compatibility work. |
| I | [OpenCE-Conquest](https://github.com/SutlabSol/OpenCE-Conquest), main `ac68c31f` | Territories/base capture with tickets and HUD markers | Interesting separate game mode; published playtest is Windows focused. Android/network validation needed. |
| J | [GulchCE](https://github.com/chestahh/GulchCE), main `3e0498d5` | MCC map support | Large format/rendering integration requiring owned MCC assets. Its MCC maps require matching clients; defer from the maintenance release. |
| K | [FractumSeraph](https://github.com/FractumSeraph/OpenCE), main `1d3501f5` | Match recording, live/replay viewer, persistent invites and custom-map distribution | Substantial networking/storage/service integration; defer. Replays have configurable disk budgets, material on phones. |
| L | [Halo OG](https://github.com/pfista/halo-og), main `a930bdc9` | Optional practice/competitive settings and map catalog workflow | Divergent older networking and extensive native Mac work; assess individual ideas separately. |

Other credited sources: JoshRob297 main remains `8a6fe36c`, Bink-on-main `79847b0e`; other Bink branch heads were checked, with no replacement selected for the current working movie integration. fqlx/OpenCE still returns 404, but the repository is available under [fqlx/halo-ce-universal](https://github.com/fqlx/halo-ce-universal), main `8102b91f`: compact controls are already represented here, other advertised branches are browser/iPhone focused. [thelinkin3000](https://github.com/thelinkin3000/halo-ce-universal) recent work is Switch focused. [innerhat-dev](https://github.com/innerhat-dev/OpenCE) has newer light/interpolation/client-stability work beyond the selected upstream build, worth a later focused review rather than importing its platform branch wholesale. Chupathingy team switching and menu replacements are additional candidates with broader network/menu impact. Its BC7/converter work remains a larger dependency chain.

Recommendation: upstream + settings repair, A/C/D, and B if wanted now. E/F/G are optional. Keep H–L for separately scoped updates.

## Validation and remaining gate

Passed: production Android-config restart/recovery regression; 7 selected pytest settings/menu/touch checks; touch tap/cancel/controller/menu-coordinate/profile keyboard checks; renderer/Quit/theme checks; camera ownership; single touch-consumer/depth guard; map-browser checks; eight keyboard tests with ASan active and leak detection disabled (the host cannot inspect `/proc` for LeakSanitizer). Mobile script's non-JNI checks passed.

Not completed: Java layout compilation and native JNI mobile checks (JDK compiler/headers absent), integrated Android debug/release APK builds (SDK/NDK absent), actual phone gameplay/lifecycle/GPU/multiplayer tests. Five optional mod integration checks skipped because their Linux executable/game maps were absent; those do not constitute Android testing. No Linux/Windows game build was run for this review.

After feature selection and authorization: integrate selected commits/adaptations with author/source credits, run the complete Android CI gate, increment app/release version, then release APK plus dependency-license package only if checks pass. Test on phone: save mixed ON/OFF settings using OK, Quit/relaunch; Home/resume and close/relaunch; repeat with legacy duplicate-section config, theme, layout and profile choices. Verify films, menu taps, camera and map browser after integration.

## Draft next changelog (not published)

- Fixed settings returning to defaults after restarting; existing duplicated configuration sections are repaired.
- Updated OpenCE with resource-pack controls, live HUD/text settings, co-op/menu repairs and map-sharing improvements. Multiplayer now uses protocol 29.
- Additional selected Android/fork features and credits will be added after review.

Use the short v0.5.5-touch release style, retain contributor credits and dependency notices, and state the existing temporary-signing-key upgrade limitation unless signing has actually changed.
