# Runtime identity initialization fix

The first successful shopping-list creation reached identity capture, but the
callback parsed an uninitialized record returned by native RTV. The old
Node stub returned undefined and therefore missed the truthy missing-record
case. A stub returning an opaque object reproduces the JSON parse failure.

The authentication callback now initializes each selected instance identity
record to an empty JSON object. Identity capture only reads initialized
records. IDs remain unbound until observed in successful server responses;
this does not invent instance identities. Existing default generator behavior,
HTTP separation, relationship dependencies and operation scope are unchanged.

Also:
- Review ZIPs omit serialized relationship-samples.json and selected-sample.json;
  these stay in the project for replay. Model source, task orders, hashes and
  acceptance/log evidence remain in the review ZIP.
- Bare JWTs and token RTV log entries are redacted. Whole output is redacted
  before extracting an error excerpt.
- Completion evidence can be parsed from the native receipt RTV log as well
  as a success message. Exit code zero alone still cannot pass acceptance.
- The combined pilot wrapper accepts -SampleSize; its previous default is 3.

32 local tests and 466 transport comparisons passed. The old generated
callback failed with the opaque missing-record stub; regenerated callbacks
completed all 54 tasks and 167 stub responses. Native acceptance of this fix
is pending. Existing native evidence shows the first shopping-list POST
succeeded before capture failed; that partial resource is retained.

Generate a NEW project and sample again because old samples serialize old
callbacks. Run Run-Generic-Relationship-Pilot.ps1 with -SampleSize 1 for the
next native acceptance attempt. No automatic deletion/reset/retry is added.
