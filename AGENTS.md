# OpenCE-Touch maintenance

- Develop Android touch changes on `touch-controls`. Preserve the SDL virtual gamepad, direct menu/profile-keyboard taps, automatic mode switching and editable layout.
- Before merging upstream, select a revision whose Linux, Windows and Android build jobs passed. Keep the upstream history in a merge commit.
- Run `python tools/test_android_touch.py` and the CI build/test jobs before releasing. Compilation and regression checks do not establish phone gameplay verification.
- Each release must include the Android release APK and the packaged build with its dependency licenses. Increment the Android version for each release.
- Include a very short, plain-language changelog on every release: describe the upstream update and any fork changes in a few bullets. Keep the AI disclosure and upstream credits in the README.
- If CI uses its temporary debug signing key, say that installing over a previous APK can fail and saves should be backed up before uninstalling. Never commit signing keys or passwords.
