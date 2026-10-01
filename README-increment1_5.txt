Increment 1.5 - bounded serial functional fixture. Requires increments 1.0 through 1.4.
Extract into C:\work\temp\mealie_sbt_study. Run scripts\Create-Mealie-Pilot-Fixture.ps1 once.
Creates resources with a unique mealie-sbt prefix: foods F1-F3, units Q1-Q2, categories C1-C2, tags T1-T2, recipes R1-R3, lists L1-L2.
Six ingredient occurrences: F1/Q1 and F3/Q2 in R1; F1/Q1 and F2/Q1 in R2; F2/Q1 and F3/Q2 in R3.
L1 links R1/R2; L2 links R2/R3. Independent reads verify typed identities, food/unit/category/tag links, list links and item recipe provenance. Item aggregation is not assumed to have a fixed item count.
The fixture uses operation-specific adapters for the reviewed contract; a general payload generator is not implemented here.
One serial run. No concurrency, cycle links, reset, retry or deletion. Existing resources are not selected for modification. Failure leaves partial fixture data and saves the trace for review. Upload the ZIP before retrying.
Passwords and access tokens are not saved. Output: Downloads\mealie_fixture_review.zip.
25 Python tests passed, including simulated fixture and mismatched readbacks. This fixture has not yet been run against the live server.
