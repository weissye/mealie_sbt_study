# Real Mealie native interleaving acceptance

Run: generator-interleaved-dependencies-20261006-051538-638348. Native exit: 0. Seed: 871186583. Four symbolic candidates, selected candidate 2; 68 symbolic events. Twenty-five live HTTP calls, 24 business responses and four update request bodies. Eighteen bthreads, four lifecycle workers.

Two children shared parent2. Child2 was created and updated before parent2's rename; child1 was created before that rename and updated afterwards. Parent PUT included both existing children. Its response and subsequent readbacks preserved both identities. Final child reads preserved notes, quantities, binding and ownership fields.

This validates the protected snapshot-update acceptance. No new application bug is confirmed. One native action reservation excludes other modeled mutations between refresh GET, PUT and verification. It does not protect against external clients or prove arbitrary interleaving coverage. Full generator acceptance and five historical finding reproductions remain pending.

Next release completes create/read/update/delete for child1 and checks absence, parent integrity and surviving child2. Deletion occurs after final reads for all updates. Only newly created child1 is deleted; parent lists, sibling and prior evidence remain.
