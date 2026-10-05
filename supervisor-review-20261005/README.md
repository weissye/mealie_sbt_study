# Mealie supervisory review package

Start with reports/Research_Report.docx and reports/Engineering_Report.docx.
Five finding groups are preserved; five independent root causes are not claimed.

1. Run scripts/Verify-Evidence.ps1. This is offline and verifies originals.
2. Review the classification and limitations in both reports.
3. For functional quantity/copy replay only, start the separate port 9928 fixture and use scripts/Run-Functional-Reproduction.ps1. Live Windows validation remains pending.
4. F04/F05 recorded stories do not reproduce scope sensitive behavior against a live service. Use the original archive verifier for those findings.
5. Run scripts/Save-Supervisor-Review.ps1 -Push on the authenticated repository machine to archive this new package. It has not been pushed by the packaging environment.

All live HTTP for the new functional stories is in reproductions/interfaces.shared.js.
The original archive bytes remain unchanged. No runtime reset, simultaneous requests or global novelty is claimed.
