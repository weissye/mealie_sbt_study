# Native Context F01 handoff

Confirmation run, seed 47653690, reached both contributions. Whole contribution: expected and observed 6. After half contribution: expected 9, observed 11 in the operation response, item GET and both list GETs. Source ingredient quantities remained 2 and 4. Item recipe reference reports quantity 6 times scale 1.5 = 9, contradicting stored item quantity 11. Stable item identity and food/unit/list links were preserved. Internal item-reference row ID changed; do not classify that alone as a bug.

All three generated JS files were regenerated from the pinned OpenAPI and the seed with the frozen compiler and matched exactly after LF normalization. The run script generates a new project before native Provengo execution. The explicit contribution hypothesis and generation scope are inputs; schema alone does not specify the arithmetic.

Next: preserve this checkpoint in Git and compare with historical F01 evidence. First observation is archived at commit 21f753a8f2003d6f0d8a96217b39d063fcab1aff. No reset/replay has been completed. Do not change the expected quantity to 11.
