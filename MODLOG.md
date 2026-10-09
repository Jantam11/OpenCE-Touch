# OpenCE-Touch maintenance — 2026-10-09

Work starts at 5a9c7892 on touch-controls. Chosen route: merge validated upstream f479e349 with both parents, adapt narrowly selected credited-fork fixes, validate on an isolated CI branch, then advance touch-controls and publish its Android artifacts. Existing release v0.5.1-touch is the rollback point. No game files or signing keys are accessed.

See INTEGRATION_NOTES.md for revisions, conflict decisions and local checks. GitHub CI is required for full builds and 32-bit regression execution. Compilation is separate from phone gameplay verification.

Initial integration run 37933045092: Linux debug/release passed; 224 tests passed, 16 profile fixture compile failures. Fixture repaired; native lifetime/negative-control tests pass. Final validation includes version 0.5.2-touch/code 7 and package checks for Opus/Lucide notices.
