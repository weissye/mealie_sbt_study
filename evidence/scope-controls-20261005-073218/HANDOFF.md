# Scope controls findings handoff

This follows evidence/multi-identity-20261005-065704/HANDOFF.md. Original foreign-reference HTTP 500 repeats with fresh identities/resources under seed 264758 after seed 844524. Missing-reference controls also return 500 without changing inspected list content. Same-group recipe sharing passes. Foreign-household list operations return 500 and owner readback shows an added item in four observations across two fresh samples.

Keep server-error robustness and household isolation/state deviation separate until mechanism is qualified. The captured household traceback is not evidence for every reference error. No concurrency claim. Prior copy and quantity findings remain separate.

Next closure work: independent fresh-seed household confirmation, minimal-prefix qualification, pinned environment capture, and source-level diagnostic review. Do not silently replace the deprecated endpoint while confirming the original finding. Testing its bulk successor is later coverage.

Run verify_campaign.py before commit. It is offline and sends no API calls. Credentials remain local; do not archive DPAPI secrets, tokens, passwords, or raw Docker environment values.
