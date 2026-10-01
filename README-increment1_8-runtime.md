# Mealie standalone runtime delta 1.8

Prerequisite: accepted increment 1.7 generated project and the existing accepted fourteen-resource fixture. Extract into C:\work\temp\mealie_sbt_study. Keep the existing sampled project; do not recreate fixtures.

Run scripts/Accept-Mealie-Standalone-Stories.ps1 -Username 'changeme@example.com'. The password prompt is hidden. Expected result: M4_STANDALONE_RESTORATION_ACCEPTANCE_PASS. Review ZIP: Downloads/mealie_standalone_review.zip.

The backend consumes operation/scenario IR and the actual Provengo sampled events. It executes the two functional stories separately, with semantic restoration checks and fresh typed bindings. It is a standalone replay bridge, not 70 composed live schedules or an in-engine Provengo REST executor. See docs/RUNTIME_BACKEND_1_8.md.

Successful execution performs 51 fixture requests plus five contract/authentication requests. On any failure it stops and packages evidence without an automatic retry or failure rollback. Review the ZIP before repeating a failed run; the state may be partially changed.

Validation: 44 Python tests passed. Actual uploaded fixture/sample evidence passed read-only validation. The user's live server and PowerShell runtime have not been executed in the development workspace.
