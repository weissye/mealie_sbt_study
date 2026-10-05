# Linked recipe copy isolation

This opt-in generic compiler extension derives operations and request/response
schemas from OpenAPI. HTTP remains exclusively in generated interfaces; generated
stories schedule resource construction and the appended copy task. Existing
profiles do not enable this extension.

## Campaign

Four profiles, two native sampled schedules per profile, fresh owned resources
per replay:

1. Control: copy a linked recipe, then change source/copy descriptions separately.
2. Source-first: change source instructions, copy ingredient notes, source
   ingredient notes, and copy instructions.
3. Copy-first: perform the nested changes in the opposite order.
4. Internal-reference: seed a valid instruction-to-ingredient reference before
   copying; verify its target is a copied ingredient, then perform nested changes.

The source points to a third recipe; another recipe points to the source;
shopping lists also refer to source recipes. Copies intentionally retain external
food/unit/recipe identities. They must receive independent recipe and child
identities. Incoming links must retain their original targets and quantities.

## Evidence and classification

All duplicate/mutation response bodies and both recipe plus referrer GET bodies
are retained before semantic qualification. The independent Python validator
checks those bodies, declared mutations, child-ID remapping, and counterpart
isolation. No response exit code alone constitutes acceptance. A discrepancy is
COPY_CANDIDATE; two fresh-resource reproductions require analysis before a new bug
claim. Repeated manifestations of one cause count as one defect.

The generic policy explicitly declares the fields under protection, child UUID
paths, incoming reference paths, writable mutations, and derived display paths.
Only ingredient display strings are excluded from copied/changed content
comparisons; they are retained raw. Counterpart content, child identities,
quantities, external identities, ordering and incoming links remain protected.
Instruction IDs may be regenerated on an intentional PUT, as observed in prior
live campaigns. Other child identities cannot change on that PUT.

This is a sequential scenario campaign. It does not claim exhaustive graph
coverage, assets/image isolation, concurrent HTTP, full reset/replay or live
Mealie acceptance before the user runs it.

## Run on either computer

Extract into the existing study root. Run Save-Generic-Copy-Isolation.ps1 -Push,
then Run-Generic-Copy-Isolation.ps1 -Username changeme@example.com. The root is
inferred from the scripts directory. The runner checks compatibility, pinned
server metadata, 1 GiB free RAM/disk, and compact samples, then uses a 512 MiB Java
heap. It never closes Chrome. Password is prompted once and restored environment
variables are cleared afterward. Partial campaign evidence is archived in a
finally block. Upload the printed Downloads campaign.zip for independent review.

The release also archives the six successful name-driven route runs supplied on
2026-10-05, with a findings document and offline verifier. Source/evidence are
not considered remotely saved until the source-save script verifies the remote
commit. The separate older home direct-slug finding remains unqualified.
