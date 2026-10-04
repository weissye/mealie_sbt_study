# Continue the Mealie investigation at home

1. On the work computer, extract this delivery into the existing Mealie study and run scripts/Save-Mealie-Research-Day.ps1 -Push. Wait for RESEARCH_PUSH_VERIFIED and retain the commit hash and printed branch name.
2. At home, use the same repository and branch. Run git pull --ff-only in D:\Yeshayahu\Temp\mealie_sbt_study. If Git reports local edits or divergent branches, preserve the files and inspect the message; do not reset or overwrite them.
3. Run py -3 -B .\evidence\mealie-quantity-family-20261004\verify_freeze.py. Expected result: ARCHIVE_AND_SEMANTIC_EVIDENCE_VERIFIED, 24 runs, 18 discrepancies, 6 successes, zero server requests.
4. Open docs/research/20261004/Mealie_Quantity_Consistency_Engineering_and_Research.docx. The combined engineering and research record is eight pages.
5. Continue with linked-resource deletion and dependent-resource integrity. Quantity permutations are frozen. Live deletion scenarios have not yet been implemented or qualified in this delivery.

Git carries source code, generated evidence, analysis and documentation. It does not carry current running Docker state through this research commit. The earlier partial home restore remains unresolved. Preserve its backup and restore status; do not blindly repeat Import.

The Vikunja repository is not modified by this Mealie freeze. Its prior transfer and restoration state remains separate.
