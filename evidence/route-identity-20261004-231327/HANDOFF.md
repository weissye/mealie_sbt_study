# Work handoff: 2026-10-04

Source push verified: dbcd9a7c84d1ca9338b5f22ad46261e377aaa452.
Campaign seed: 686781.

Two control runs passed independent receipt validation.
Four rename/reuse runs stopped at new_route_resolution with HTTP 404.
All six nested live archive checksums were verified.

Actual request bodies retained the original recipe name and supplied a new slug.
Pinned Mealie v3.28.0 repository code retains the existing slug when the name is unchanged.
This explains the failure hypothesis, but final classification remains OPEN:
PUT response bodies and post-write reads of the original routes were not captured.

Next:
1. Read the existing resources without mutation: original route, requested route,
   stable recipe UUID, recipe references and shopping-list references.
2. Preserve observations before classifying the candidates.
3. Generate name-driven route changes using an explicit generic route-driver policy.
4. Test rename and old-alias reuse while protecting UUIDs, quantities and references.

A name-driven compiler change passed local native mock tests but has NOT been
delivered, installed or pushed. Do not assume it exists in this repository.
No new route defect is confirmed. Full reset/replay remains pending.
