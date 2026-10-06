# Callback scope diagnostic matrix

This diagnostic does not change the generic generator or existing projects.
It samples one ordinary callback baseline and two isolation variants: construction
inside a bthread and construction before the bthread. SCOPE_STAGE markers locate
model initialization, scope creation, compilation, and REST event construction.

A zero native exit code without a sample is rejected explicitly. Isolated samples
must be complete, contain exactly two public-contract GET requests, stay below
4 MiB, and omit the unrelated global sentinel. Only a passing isolated sample
is replayed. No credentials or resource mutation are used. All bounded diagnostic
logs and sources are included in the review ZIP. This is an investigation,
not a validated fix for the large relationship samples.

Local validation: six Python tests and Node syntax checks for all three models.
Native Provengo validation is pending on the Windows host.
