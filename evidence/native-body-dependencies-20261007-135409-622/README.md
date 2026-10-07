# Native body-dependency acceptance and conditional Git archive

Run with the installed central compiler containing the body-dependency increment. No generator source is patched by this package and no fixture driver is appended to generated JS. All output is produced by the central CLI from fixture-openapi.json.

Three independent local cases: control (200), error (500 unchanged), changed (500 with unit state changed). Each creates and verifies a resource, food and unit. Parent lifecycles can be interleaved in any order. The process waits for all three verified revisions, submits the compiled body, and collects identity-bound GETs for all three. Nineteen wire requests per case, 57 total when complete. The fixture validates actual food/unit identities and names in the request and returns 422 on a wrong binding.

The native qualifier independently checks wire receipts, lifecycle subsequences, complete readbacks, callback payloads, expected-state diagnostic flags, native outcome and deferred-failure ordering. Six synthetic qualification regressions are explicitly mocks; they are not native acceptance. Node checks serialization of the actual generated interface expression with identity variables and mocked transport.

The two 500 cases must have intentional native FAIL only after all GET callbacks. They are accepted evidence cases, not successful HTTP operations. Native ERROR, timeout, incomplete evidence, fabricated IDs or wrong final states stop the campaign. No automatic retry, Mealie requests, cleanup or reset.

After all cases pass, archive verification regenerates exact JS/report/config from the captured OpenAPI and generator-source.zip. Only then Run-And-Save-Body-Dependencies.ps1 creates a sparse archive worktree, commits the original review.zip (which contains exact generated projects and compiler source), the verifier and fixture tools. With -Push it pushes without force and verifies remote equality. Original checkout and Docker are preserved. The new compiler is archived inside review.zip, not installed into the repository's canonical generator folder by the save step.

Native Provengo is unavailable in the assistant's environment. This package's native acceptance is pending on the user's machine. No claim is made of completing F04/F05 or inferring business semantics from OpenAPI.
