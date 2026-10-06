# Native compact callback fix

Install this delta over the existing alternate-paths/memory delta in the study root.
Run scripts/Run-Generic-Alternate-Path-Pilot.ps1 -Username YOUR_USER.
The runner generates a fresh model, samples it, audits task completeness, and
replays one schedule. Existing large projects and samples are preserved.

## Change

Only the opt-in compact_callbacks compiler branch changes. The legacy compiler
branch stays identical. HTTP remains in generated interfaces, while stories
request and coordinate tasks. The sampled Rhino function has an empty parent
scope with an associated ClassCache. Standard JavaScript objects are created
only during execution. The arguments parameter prevents Rhino from constructing
its builtin Arguments object before the detached scope has been hydrated.
The shared runtime receives pvg explicitly; context and schemas are parsed in
its live scope. No model globals are captured in serialized callbacks.

## Validation

Used the supplied Provengo 0.7.5-SNAPSHOT jar (ef04cca/20250714-0453/master).
Native sampling and replay passed against a local HTTP fixture with -Xmx512m.
The complete scenario has 109 tasks, 378 HTTP requests, 35 owned instances,
17 legal relationship receipts and seven negative cycle receipts.
The native sample is approximately 2.74 MiB, compared with the previous
approximately 1470 MiB Windows sample. This is not a Mealie acceptance result.
The optional native regression also injects identity corruption and checks
that execution fails without a completed receipt.
Set PROVENGO_TEST_JAR to enable that regression locally; otherwise it is skipped.

## Windows execution

The runner limits both sampling and replay to -Xmx1g and checks for 2 GiB of
available RAM. Chrome can remain open when that memory is available. One GiB
of free disk space and a reachable local Mealie server are required.
No reset/replay, cleanup or automatic retry is performed. Upload live.zip
from the timestamped review directory printed by the runner.
