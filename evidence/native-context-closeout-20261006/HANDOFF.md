# Mealie native Context checkpoint — 2026-10-06

## Result
Two live runs with fresh recipe/list/item/food/unit identities reproduced the quantity discrepancy. Seeds: 803164486 and 47653690. Both first contributions stored 6. Both subsequent half contributions stored 11, while the DAL computed 9 and the server recipe reference reported quantity 6 times scale 1.5 = 9. Each archive contains two operation receipts and eight independent readbacks. The original recipe quantities 2 and 4 were preserved. Item-reference row identity changes are observations, not separately established defects.

The first observation was pushed in 21f753a8f2003d6f0d8a96217b39d063fcab1aff. This checkpoint adds both original archives and a runnable current source snapshot. Confirmation of a fresh-resource rerun is complete; full server reset/replay and comparison with historical F01 evidence remain pending.

## Implementation
Native Provengo Context; entity lifecycle bthreads, a dependency-linking process and a separate recipe contribution process; all HTTP including authentication lives in shared interfaces. Every run generates new JS from the pinned OpenAPI before native execution. All three JS files in each submitted run regenerated identically with the corresponding seed. The current generator excludes unrelated nullable rating from contribution setup. Failure collection handles UTF-16 and UTF-8 logs.

Important methodological limit: OpenAPI supplies operation and schema mapping; contribution/merge arithmetic remains an explicit generic test hypothesis in the compiler/DAL, not a law established by OpenAPI alone. Expected quantities are calculated from model state, not copied from server responses.

## Resume on the work computer
1. Obtain origin/main containing this checkpoint; the push script uses a separate worktree and does not update your original checkout.
2. Extract evidence/native-context-closeout-20261006/runnable-source.zip into a new package directory, e.g. C:/work/temp/mealie-context-20261006. Do not extract over the original generator.
3. Start the existing local Mealie service on port 9925. Use the valid account email changeme@example.com and your existing password; no credentials are stored here.
4. For offline generation: scripts/Run-Mealie-Context-F01.ps1 -Root <package> -GenerateOnly. The baseline generated/ directory required by callback tests is included in the snapshot.
5. No third identical live confirmation is needed now. Continue with exact historical evidence mapping for the next defect, using the same compiler and native Context structure. Do not assume that all five historical findings are already mapped or recreated.

## Preservation limits
Raw native logs remain on the home machine because they may contain credentials. Review archives preserve callback response bodies, generated code and raw-log hashes. They do not contain a complete wire transcript, database backup or Docker volumes. This closeout covers Mealie work in this session; it does not assert synchronization of Vikunja or Paperless.

The extracted runnable snapshot passed 15 Python tests and 56 callback/DAL unit checks locally. Native fixture tests of this compiler passed a normal run and detected injected quantity corruption. These are distinct from the two user-supplied live Mealie runs. PowerShell wrappers have not been executed in the local Linux environment.
