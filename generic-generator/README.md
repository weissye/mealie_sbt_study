# Generic generator: HTTP interface separation

Revision: `http-interface-separation.1`. Base generator: `generator_v56`, version
`0.26.19-parallel-crud.3`. The original package name and version remain unchanged.

This is the existing generator, not the earlier two-story demonstration. The
OpenAPI parser, entity inference, dependency graph, planning, request rules,
RTV bindings and story scheduling come from the original generator.

The production pipeline now moves HTTP from parallel CRUD stories and prefix
observations into generated functions in `interfaces.<name>.js`. Stories call
those interfaces. Verification requests follow the same boundary. Request
paths, bodies, headers, callbacks, expected responses and event names are
preserved. No application-specific inference or new overlap mechanism was added.

Changed existing files:

- `generator_v56/pipeline.py`
- `generator_v56/render/parallel_crud_v3.py`
- `generator_v56/render/stories_js.py`

New module: `generator_v56/render/http_interfaces.py`. Its registry is local to
one generation. The pipeline rejects direct `svc` HTTP calls in generated
stories. Original low-level story renderer calls keep their old behavior when
the optional transport registry is omitted, preserving that Python helper API.
Use the pipeline or CLI to generate the complete separated file pair.

## Compatibility evidence

The included tests reconstruct the pre-change package by overlaying preserved
original sources. They compare before/after generation on the included Keycloak
and Mealie contracts across all 14 existing CLI profiles (28 combinations).
Plans, dependency reports, generation reports and unsupported references must
match. Replacing generated interface calls with their original transport source
must reproduce the old stories byte for byte. Outputs with no lifted requests
must match byte for byte without replacement.

Additional cases cover multiple logical workers and instances, configured
request rules, authentication environment names, prefix observations and
deterministic generation. An optional Node VM check compares 466 lifted request
sites, including HTTP arguments, callback effects, RTV writes and caller flags.
It uses stubs and sends no requests. It does not validate Provengo internals.

Validated here: Python regression suite, Node comparison, JavaScript syntax and
the original CLI generating Mealie files. Windows PowerShell wrappers and live
Provengo/server execution have not been validated here. These checks establish
compatibility on these inputs, not on every possible OpenAPI contract.
The prior four-system archive could not be downloaded; those contracts were
not included in this acceptance run.

## Run

From this directory:

```text
python -m unittest discover -s tests -v
python tests/export_transport_cases.py transport-cases.json
node tests/check_transport_equivalence.js transport-cases.json
python -m generator_v56 generate --openapi compatibility/contracts/mealie.json --output generated --name mealie --base-url http://127.0.0.1:9925 --seed 2 --story-profile parallel-crud
```

`transport-cases.json` is a temporary test input and can be removed afterwards.
JSON inputs use the standard library; YAML inputs require PyYAML as before.
Generation itself sends no HTTP requests. Existing CLI options remain available.

## Installation and next acceptance

The delta adds `generic-generator/` and two new scripts to the study directory.
It leaves the previous demonstration and original source tree in place. The
new subtree contains the original generator with the scoped refactor, regression
inputs, baseline sources, and a generated Mealie preview under `preview/`.

`Prepare-Generic-Provengo-Model.ps1` takes an OpenAPI path, application name and
base URL as configuration. It generates a separate Provengo project and review
ZIP. It never runs that project or changes the server.

Next acceptance must inspect the original generator's inferred resource types,
parent bindings, bootstrap and response extraction against observed fixture
facts. The previous demonstration's successful live run does not prove these
generated stories execute successfully. Then sample the actual generated model
and run a bounded composed schedule with reset/replay checks. Target complex
interleavings with one HTTP request at a time. Existing explicitly configured
overlap profiles were preserved for compatibility, not selected for this work.
