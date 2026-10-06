# Native live functional acceptance

Use scripts/Test-Mealie-Generator-Live.ps1 from the existing study root.
It prompts for the password; authentication and all application HTTP operations
are native Provengo REST calls in generated interfaces. Python generates the
model and starts native sample/run; it sends no application HTTP requests.

The installed generator_v56 infers the Plan from a bounded OpenAPI projection.
The explicit scope selects one family (tags) with POST, GET and PUT. A new generic
bounded renderer uses that Plan's methods, paths, statuses, writable field and
inferred response identity. It contains no system-specific paths or fields.
It rejects unsupported family shapes. This is an added rendering module, not
a claim that the original full parallel CRUD profile has been repaired.

Two independent lifecycle bthreads create two uniquely named fixture tags.
Separate verifier bthreads perform owner-correlated GET checks after creation
and update. They assert persisted writable value and stable identity. Workers
wait for verifier events. Authentication has an explicit waitFor dependency.
Both fixtures are retained; no delete, merge, copy, permission-boundary probe,
automatic retry, cleanup or rollback is performed.

The authentication overlay uses the contract's OAuth password token URL and
standard bearer-token response. Credentials remain in the child environment,
and saved log text redacts credentials and observed bearer token values.
Only generated source, symbolic sample and redacted logs enter the review ZIP.

Local validation: real Provengo sampling and execution against a synthetic
HTTP fixture passed. A fixture that accepted PUT without persisting the value
was rejected by the native independent readback verifier. These are tool tests,
not results from the user's Mealie server. Windows wrappers were not executed
in this Linux workspace.

This is a live infrastructure acceptance check, not a reproducer for any of
the five earlier finding groups. Complex dependency families and application
invariants remain acceptance gaps. Preserve review.zip on failure and inspect
it before another run. No Git commit or push is performed.
