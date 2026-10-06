# Installed-generator native acceptance delta

Extract into the existing Mealie study root. This package adds files only;
it does not contain or replace generator_v56, the OpenAPI or previous findings.
Python 3.10+, Java and Provengo are required. Docker and credentials are not.

It validates critical source files against normalized hashes of the supplied
generator_v56 source, records raw hashes of all installed Python modules,
validates the Mealie contract (CRLF tolerated without modifying it), generates
interfaces and stories, and invokes native Provengo sample once. No replay or
API actuation is performed. No business profile is passed to generation.

The sample audit checks action/verifier pairing and completion of each generated
CRUD worker. Symbolic verifier events do not prove that callbacks passed live.
Unfinished workers, missing output, oversized samples and timeouts retain a
review.zip and return nonzero. Never silently retry or call an incomplete
sample an accepted scenario. The default 600-event bound is diagnostic and may
be insufficient; first inspect the audit instead of raising it blindly.

Five Mealie finding groups still require separate semantic qualification.
Neither operation generation coverage nor symbolic completion reproduces them.
This milestone establishes real Provengo sampling of the agreed architecture.
The next milestone is isolated functional fixture validation of supported
runtime oracles. No new boundary-sensitive reproducer is included.

Default uses provengo on PATH. -ProvengoJar accepts an explicit installed JAR;
that path uses java -Xmx1g directly. Every run writes a unique runs directory.
No source changes, Git staging, commits or pushes are performed.
