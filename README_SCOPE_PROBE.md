# Native callback scope probe

The uploaded native sample prefix shows a Java-serialized Rhino InterpretedFunction with parentScopeObject containing unrelated model globals (sbtRelSchemas, sbtRelRuntime, hundreds of sbtRelHttp helpers and legacy API functions). Node function text size was not a sufficient measure of native serialization size.

This additive diagnostic does not change the generator or existing models/samples. It creates a small separate diagnostic project and compiles callbacks into a fresh Rhino standard scope using Context.compileFunction. An unrelated global sentinel is deliberately included in the model. The sample must not contain that sentinel in either serialized callback. Sampling acceptance is bounded at 4 MiB; two GET /openapi.json calls are then executed and must prove pvg availability and RTV continuity with an explicit native receipt. Java heap is bounded to 1 GiB.

No authentication, resource creation, update, deletion, retry, reset or rollback is performed. The launcher also makes one GET readiness check before the two native GET calls.

Extract this ZIP into the existing study root, then run scripts/Test-Provengo-Callback-Scope.ps1. Upload the resulting timestamped provengo_callback_scope_review_*.zip from Downloads. Do not run the full relationship pilot again yet.

Three local unit tests passed, covering read-only boundaries, complete schedules, scope-leak detection and generated probe behavior. The native Rhino/Provengo compatibility check is still pending. Successful native evidence is required before changing production generated callbacks.
