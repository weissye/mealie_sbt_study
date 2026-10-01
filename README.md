# Mealie SBT study - Increment 1

This project is an isolated subtree intended for `C:\work\temp\mealie_sbt_study`.
It does not modify or execute the previous Vikunja/Gitea/Keycloak generator.

## Delivered

- Three separate machine-readable maps: data structure, operation input binding candidates, and relationship templates.
- An explicit schema-view/resource catalog and typed identifier slots.
- Schema strongly connected components with contract-permitted ways to stop recursive expansion.
- A typed run-local RTV prototype: observed aliases, instance values, relationship observations and deletion state.
- A many-to-many pilot topology with three recipes, shared foods/categories/tags and two shopping lists.
- Windows preparation and localhost-only server/contract acceptance scripts.
- A read-only disk and Docker storage audit. No deletion or prune operation is included.
- Standard-library Python acceptance tests.

## Stage boundaries

`M2_STATIC_READY` means maps have been compiled from the uploaded reference contract.
It does NOT mean that the local server, auth, fixture creation, reset/replay, generic payload generation or Provengo execution have been accepted.
The uploaded contract is `nightly`. Keep it as a reference. Obtain and recompile the contract from the pinned local server before generating live tests.

## Windows commands

Extract this package under `C:\work\temp`; the ZIP contains the `mealie_sbt_study` root directory.

```powershell
Set-Location 'C:\work\temp\mealie_sbt_study'
& .\scripts\Initialize-Mealie-Study.ps1
& .\scripts\Audit-Study-Storage.ps1 -ScanRoot 'C:\work\temp'
```

After Docker Desktop is installed and running, prepare a separate local server:

```powershell
& .\scripts\Start-Mealie-Local.ps1
```

The default pinned image is `ghcr.io/mealie-recipes/mealie:v3.28.0`, based on the official SQLite installation example checked on 2026-10-01.
The server binds to `127.0.0.1:9925`, uses its own Compose project and stores data only under this project.
The script records image digests and application information, downloads the local OpenAPI contract, and compiles separate local maps.
It does not create accounts, log in, wipe data, or reset the server.
If an existing compose file differs, startup stops instead of changing version/port/data automatically.

If a local Mealie server already exists on that port, do not start another server. Read its contract using:

```powershell
& .\scripts\Accept-Mealie-Local.ps1 -BaseUrl 'http://127.0.0.1:9925'
```

## Outputs

- `maps/reference/01_data_map.json`: all schemas and explicit reference edges.
- `maps/reference/02_operation_map.json`: all operations; path/body identity slots and unresolved candidates.
- `maps/reference/03_relationship_map.json`: reviewed static relation hints; runtime instances/edges initially empty.
- `maps/reference/resource_catalog.json`: schema aliases and identifier business types.
- `maps/reference/cycle_report.json`: schema cycles, nullable/optional/empty-array alternatives.
- `maps/local-<timestamp>/`: maps compiled from a particular preserved local contract.
- `runs/acceptance-<timestamp>.json`: reachability and contract access result only.
- `storage-audit/`: CSV folder sizes, candidate list and JSON summary.

## Provenance and uncertainty

Schema families and field target roles come from the explicit reviewed `profiles/mealie.json` profile. They are not all derivable from OpenAPI alone.
Changing a schema alias never proves that two runtime instances are the same. Runtime co-reference requires observed identifiers with the same entity type, run and scope.
Every operation dependency is a binding candidate until a successful live acceptance establishes its applicability.
The runtime registry does not merge different scopes automatically or infer that equal strings of different business types are equal entities.
Moves between scopes and automatic endpoint response extraction are not implemented in this increment.
Optional recursive properties can be omitted or explicitly null where permitted. A required, unsatisfied creation cycle stays blocked for review.

## Sources

- https://mealie.io/documentation/getting-started/installation/sqlite/
- Uploaded `mealie-openapi(1).json`, copied as `model/mealie-openapi.reference.json`.

## Next increment

M1: authenticate the intended local test accounts; prove repeatable fixture setup and reset/replay without touching previous projects.
M3: generate bounded payloads, populate RTV from actual responses, and execute each pilot story individually.
M4: compose two accepted stories in Provengo with one HTTP request in flight; retain actual response observations.
M5: accept a small set of documented requirements before issuing semantic verdicts.
