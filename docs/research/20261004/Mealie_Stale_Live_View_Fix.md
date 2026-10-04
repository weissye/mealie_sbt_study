# Stale snapshot live-view oracle correction

The first home run (campaign 9, seed 791130) stopped in the no-deletion control. The recipe update was reflected in a shopping-list embedded recipe view. The old oracle incorrectly required this embedded view to remain byte-identical. This is an oracle false positive, not a confirmed server defect. No deletion probes ran.

The opt-in generic control configuration now declares live_views through OpenAPI-validated paths. On an accepted write, only the embedded view matching the observed, owned source identity may adopt the submitted description and vary its declared update timestamps. Association IDs, recipe IDs, quantities, other fields, and views of other recipes remain protected. Rejected writes receive no relaxation. Receipt validation independently derives the same expectation. Legacy profiles have no live_views mapping. HTTP stays in interfaces.

Install the delta over the existing stale-snapshot release and run scripts/Run-Generic-Stale-Snapshot.ps1. The runner generates fresh projects and resources. Preserve the previous campaign ZIP as a false-positive regression example; do not edit or replay the old generated project.

Validation: native Provengo with a 512 MiB heap passed eight healthy schedules; eight injected state faults were detected, and two accepted writes after deletion remained policy observations. The uploaded evidence reproduces the corrected comparison while changed association IDs, recipe IDs and quantities still fail. The transport comparison covers 466 request sites. Full static suite results are in stale_live_view_validation.json. Live Mealie rerun remains pending.
