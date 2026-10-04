# Microsecond timestamp: oracle runtime incompatibility

Food-control sample 1, seed 596904, stopped at invalid_update_timestamp. The server returned 2026-10-04T19:04:27.431790Z. The nested live ZIP checksum matches the result record. Expected and observed responses differ only in updatedAt; the requested name persisted. This is a test oracle false positive. Transfer probes did not execute. No new Mealie defect is confirmed.

The correction validates ISO timestamp syntax and converts fractional seconds to three digits solely for the native JavaScript Date.parse check. The original response value is preserved in comparisons, baselines and receipts. The independent Python validator continues checking the unmodified value. Timestamp changes on other targets remain errors. The native mock now returns six fractional digits to cover the actual server response format.

The console confirms the preceding code and evidence were pushed as 427cab9516d07f77c46fe575131255e19b246641. This new campaign and correction need a subsequent push.
