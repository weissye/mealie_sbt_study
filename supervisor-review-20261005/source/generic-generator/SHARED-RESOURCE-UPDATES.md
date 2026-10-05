# Shared resource update expansion

This is an additive generic generator option. HTTP operations remain in interfaces;
actors and scheduling remain in stories. Without shared_target_updates, generated
model sources, maps and reports remain identical to the previous compiler.

The new runtime configuration is a list of rules with resource_type, operation,
field and value. Operations and fields must belong to the selected OpenAPI resource.
Only documented writable/readable string fields are supported. Route identities,
id and slug cannot be updated. A rule must have at least one owned target referenced
by two distinct selected source instances; otherwise generation fails.

The compiler discovers every inbound source/path binding in the generated link
plan for each qualifying target. After existing relationships and graph lifecycle
tasks finish, it reads all those bindings, reads and updates the target using its
contract-derived request schema, reads the target again, and reads all referrers
again. Assertions require the changed target value, stable target/referrer route
identities, and identical referenced identity multisets. Update names include an
instance suffix to avoid collisions among resources created by one schedule.

This checks referenced identities, not propagation of display labels into every
embedded response view. Unselected resources are outside this bounded pilot.
Shared update receipts include the actual target identity and before/after bindings;
live acceptance independently validates completeness and rejects duplicate receipts
and missing or incorrect referrers.

The Mealie profile adds 10 update tasks and 30 before/after referrer checks to the
existing alternate-path campaign: 119 tasks, 468 HTTP calls, 35 created resources,
17 legal relationship receipts and 7 qualified rejection receipts. Sample length
is derived from the compiled schedule rather than a fixed 600-event limit.

## Windows execution

Download generic_generator_shared_resource_updates_delta.zip into Downloads and
extract it into the existing C:\work\temp\mealie_sbt_study tree. Run
scripts\Run-Generic-Shared-Resource-Pilot.ps1 -Username changeme@example.com.
The runner generates a fresh seed-206 project, samples one native schedule and
replays it against the owned local server. It creates and updates new test resources.
It uses a 1 GiB JVM heap and guards at 2 GiB free RAM and 1 GiB free disk. The native
regression also passed with a 512 MiB heap. Existing projects remain available.

Review ZIPs are written into a timestamped Downloads\mealie-shared-resources-*
folder. Upload live.zip; generation.zip and sampling.zip can support diagnostics.

Deletion and reset/replay are not part of this increment. OpenAPI references alone
do not specify whether deletion restricts, detaches or cascades; those expectations
must be qualified before assertions for shared target deletion are generated.

## Validation

Run python -m unittest discover -s tests -v from generic-generator.
Set PROVENGO_TEST_JAR to the installed Provengo.uber.jar to enable native tests.
The native tests execute generated samples against a local HTTP fixture, not Mealie.
The healthy shared model completes; ignored updates and corrupted referrer identities
both prevent runtime acceptance. The runner performs live Mealie acceptance separately.
