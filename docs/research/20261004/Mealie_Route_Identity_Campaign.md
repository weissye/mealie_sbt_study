# Route identity migration: engineering and research plan

## Mechanism

The generic opt-in route_identity compiler separates a stable business identity from a mutable routing alias. OpenAPI validates the operation, writable field, response identity and protected field paths; an explicit profile supplies behavioral expectations. These expectations are hypotheses, not inferred promises that every writable alias must change in the same way. Failure is a candidate requiring qualification and fresh-resource reproduction, never automatic proof of a bug.

## Prefix and probes

Three owned recipes, foods, units and shopping lists are created by the existing generic compiler. The compiler establishes an acyclic recipe R2 to R1 reference after construction. Existing generated shopping actions link lists to recipe UUIDs. Baselines are read afresh. All three recipes and all three lists are protected, including ingredient quantities and list items.

1. Control: update a descriptive field twice while retaining the routing alias; check the original address and all protected referrers.
2. Rename: change R1 alias twice; verify UUID and protected target state, use the new route, require 404 on each superseded route, and verify all referrers.
3. Alias reuse: move R1 to a new alias, give its old alias to independently owned R3, require the old address to resolve to R3, and verify references still follow R1 UUID instead of migrating to R3.

The two samples in each case vary native prefix construction; probe phases are explicit and fixed. Requests are sequential. Each sample creates fresh owned resources. No deletion, merge, full reset or automatic retry is requested. New candidates are grouped by invariant and require independent reproduction before counting distinct defects.

## Architecture and resource budget

All HTTP requests and callbacks remain in generated interfaces. Stories orchestrate compiled tasks and contain no direct transport calls. Successful explicit alias change updates the runtime route binding only after the target UUID and protected fields match. Timestamp allowance is restricted to configured documented update fields on the changed target; original precise values are retained. Independent Python receipt checks reconstruct protected referrer expectations and alias resolutions from observed baselines and declared phases.

The runtime option is isolated; legacy profiles keep their existing callback source and schedules. The campaign runs with a 512 MiB Java heap, requires 1 GiB free RAM and 1 GiB free disk, and does not require closing Chrome when those checks pass. Controls run first; a failed control stops probes. Windows PowerShell execution and actual Mealie outcomes remain pending until the user runs the release.
