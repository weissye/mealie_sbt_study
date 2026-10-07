# Native Context F02 and F03 confirmations

F02, seed 869772553: addition total 11; food merge total 11; recipe removal expected manual baseline 7, observed 0. Two list GETs confirmed empty state. Both original item identities returned 404. Earlier no-merge control seed 726666326 preserved baseline 7 and remains in its prior archive.

F03, seed 717883341: duplicate returned HTTP 201 and new recipe and ingredient identities. All three instruction reference occurrences retained source ingredient identities. Two copy GETs confirmed persistence. The source response was identical before and after duplication.

These reproduce the existing finding families. Server source-code root causes and novelty are not established. Original archives and generated JS are preserved byte-for-byte. Compiler snapshots preserve the local source at archival time. Raw native logs are excluded; their hashes remain in the qualification files. No SUT requests were sent by this archiving procedure.
