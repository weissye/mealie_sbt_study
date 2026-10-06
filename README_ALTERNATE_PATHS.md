# Generic alternate-path extension and compact callbacks

Extract the delta into the existing mealie_sbt_study root. Existing profiles and generated projects are preserved. All new behavior is opt-in.

## New scenario

The previous legal lifecycle remains. Then all five owned recipe link sets are cleared and read back. A diamond is built: A references B and C; B and C each reference D.

1. D -> A must be rejected because both paths close a cycle.
2. Remove B -> D and verify the removal.
3. D -> A must still be rejected through A -> C -> D.
4. Remove C -> D and verify the removal.
5. D -> A must now be accepted, with source and target readbacks.

The full generated schedule contains 109 tasks, 378 HTTP operations, 35 owned instances, 17 legal transition receipts and seven rejection receipts. Full cycle-member checks are performed for the selected observed path of each rejection. These checks do not assert that every unrelated recipe or unused branch is unchanged.

Shared-target deletion and full reset/replay are not implemented in this increment.

## Memory changes

The optional compact_callbacks runtime setting places the runtime function source and schema registry in RTV once during authentication. Every subsequent callback remains self-contained after function serialization and reads its runtime and schemas from RTV. No callback depends on a JavaScript closure surviving serialization. All HTTP remains in interfaces.

Node callback serialization fell from 8,839,849 to 495,685 bytes with identical task order, HTTP count and passing receipts. This is a Node serialization measurement, not a measured native Provengo sample size. Native sampling and execution must be accepted separately on Windows.

File hashing now streams 1 MiB chunks. Audited Python sample objects are released before Java starts. A single native sample reuses the original file instead of writing a selected-sample copy.

## Run

Run scripts/Run-Generic-Alternate-Path-Pilot.ps1 -Username changeme@example.com.

The script requires 1 GiB free disk, creates one new model with seed 205, samples once, and rejects a sample larger than 128 MiB before live replay. Live Java is limited to 2 GiB heap and requires 3 GiB free RAM. JAVA_TOOL_OPTIONS is restored afterward. Chrome does not need to be closed by the script. If memory is insufficient, samples are preserved; do not regenerate or resample. Record the generated project path for a later replay.

Successful runs create generation.zip, sampling.zip and live.zip under a timestamped Downloads/mealie-alternate-paths-* directory. Upload live.zip and sampling.zip for independent review.

No automatic resource deletion, reset, rollback or retry is performed. A live run creates new owned resources.

## Verification

The full regression suite passed 55 tests before the additional streaming-hash unit test. The extension's tests cover three scheduler seeds, reconstructed serialized callbacks, accepted alternate-path transitions, rejected remaining-path cycles and injected faults. 466 original transport comparison cases preserved HTTP arguments and callback effects. The additional checksum test verifies unchanged SHA256 output with streaming hashing.
