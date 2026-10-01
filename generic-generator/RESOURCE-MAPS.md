# Resource maps increment

Revision: `resource-maps.1`. Apply after `http-interface-separation.1`.

The existing generator now supports two additive CLI options:

- `--resource-maps`: emit resource_catalog.json, operation_map.json and relationship_map.json.
- `--relationship-profile PROFILE.json`: also emit relationship_scenario_plan.json.

The old flags, generated JavaScript and existing reports keep their behavior.
The new analysis is opt-in and does not silently replace legacy execution
dependencies. Its operation map covers the whole input contract, not just the
selected relationship profile.

## Evidence rules

Endpoint resources and schema components are separate kinds. Input/output
schema views may share a type when explicit title and base-name evidence agrees.
Alternate endpoint lookups share a canonical type only when their identity
schema and path family agree. Distinct endpoint families do not merge solely
because they return the same generic schema or UUID shape. Scope-bearing path
views remain recorded; equal runtime values are not instance-equality evidence.

The catalog records identity slots with business type, wire type/format, schema
location and evidence. UUID and slug views remain distinct representations.
Unknown foreign identifiers retain candidate types. Name matching alone never
creates an execution prerequisite or a runtime relationship.

Nested objects, arrays and explicit component references become relationship
templates, with their exact source pointers. Schema recursion is detected as
strongly connected components and preserved. Optional links can be established
after instance creation; required creation cycles need a validated bootstrap
and cannot be made executable by simply removing a graph edge.

## Current pilot plan

The scope is external configuration, not application-specific generator code.
The included profile selects seven endpoint resource types, with three symbolic
instances per type: 21 creation tasks. The planner discovers 27 proposed link
tasks from explicit references inside documented PUT/PATCH bodies. Eligible array
links use overlapping target pairs between source instances. Contained children
keep their creation parent; an array alone does not prove many-to-many sharing.
Recursive recipe links exclude direct self-links and
depend on instance creation, not recursive schema expansion.

Path-based relationship actions appear separately as action candidates.
Their relationship effects are not inferred from POST alone: POST can attach,
detach or have another effect. Runtime observation is required before selecting
them as link/unlink steps. Read-only response references do not become writes.

## Acceptance and limits

The test suite includes the original 28 contract/profile regression comparisons,
the 466-site optional Node check, and eight new resource-map/planning tests.
Tests cover nested relationships, view aliases, wire types, recursive schemas,
unrelated families using the same schema, deterministic maps, foreign path
identities, repeated shared targets, and opt-in analysis preserving old output.

The relationship plan is an intermediate review artifact. It is explicitly
REVIEW_PLAN_ONLY and every task has executable=false. It does not yet compile
those new link tasks into Provengo stories. Generated interfaces/stories still
contain the original schedule. Do not treat creation of the plan as successful
live execution of the new relationships.

Next implementation: validate response projection into each request schema,
operation-specific identity capture (including scalar responses), authentication
and fixture bootstrap; qualify action candidates; compile the accepted task
graph through the existing story/interface renderer; then sample and execute
bounded composed schedules with one HTTP request at a time and reset/replay.
Windows wrappers and live Provengo execution require acceptance on the user's PC.

## Files in this delta

The ZIP contains only changed/new files: pipeline.py, cli.py, two new inference/
planning modules, the new regression tests, scope profile, updated PowerShell
generation wrapper, this document and acceptance evidence. Expand it into the
existing study directory. It does not modify server data or old evidence.
