Increment 1.4: reviewed local contract and identity acceptance.
Extract into C:\work\temp\mealie_sbt_study. Run scripts\Accept-Mealie-Identity.ps1 directly in an interactive terminal.
The default login identity is changeme@example.com. Enter the current password at the hidden prompt. No password or access token is stored in evidence.
One token request and three authenticated GET requests. No account creation, recipe creation, deletion or reset.
Output: Downloads\mealie_identity_review.zip with selected identity observations and a typed RTV.
Expected success: M1_IDENTITY_ACCEPTANCE_PASS. Fixtures and replay remain pending.
20 Python unit tests passed with simulated responses; the new script has not yet been run against the live server.
