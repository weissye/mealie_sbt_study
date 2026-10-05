# Generic multi-identity campaign

This opt-in extension compiles explicit identity programs from the pinned OpenAPI contract. The generator contains no Mealie paths or permission decisions: actor credentials, operations, writable templates, prerequisites and qualification checks are profile data. Existing relationship profiles retain the existing compilation path.

## Two configurations

| Configuration | Regular identities | Boundaries | Main probes |
|---|---|---|---|
| Shared | Two distinct user UUIDs | Same group and household UUIDs | Cross-user recipe link, collaborative edit, copy ownership, independent source/copy changes, shared shopping list, denied non-owner deletion |
| Separate | Two distinct user UUIDs | Different group and household UUIDs | Both directions: foreign recipe read/copy/update/delete, foreign list read, foreign recipe addition to own list; owner reads after each mutation |

A provisioning administrator creates new isolated groups, households and two regular users per replay. Resource probes use regular-user tokens only. Self reads verify all role flags are false and verify user/group/household IDs before resource mutations. No existing account is modified. The default username argument is your existing administrator login; the script prompts for its password once.

The program performs HTTP serially. Provengo chooses between ready actor tasks, including independent construction prefixes and independent source/copy changes. No HTTP request is intentionally overlapped. A separate group/household pair is created for every separate-scope replay; two samples therefore use fresh users and resources, not a reused fixture.

## Evidence and outcomes

Every modeled HTTP response is recorded with its actor and operation, including write bodies and rejection responses. Authentication response tokens and provisioning passwords are scrubbed. An independent Python verifier checks expected statuses, ownership, UUIDs, quantities and references. Failed permission probes continue to owner readbacks; a status rejection alone is insufficient.

- `PASS`: complete evidence satisfied the explicit profile policy.
- `IDENTITY_CANDIDATE`: complete evidence violated an expectation. Preserve and analyze; this is not automatically a confirmed new bug.
- `INCONCLUSIVE`: authentication, provisioning, native execution or complete receipt failed; stop the campaign.

The campaign retains the first candidate and executes its second sampled schedule with fresh resources. Repeated manifestations are not automatically counted as different bugs. Full reset/replay, same-user/two-login testing, and two households within the same group remain separate future coverage.

The runner writes `Downloads/mealie-multi-identity-<timestamp>/campaign.zip`, containing the four result records, scrubbed outputs, complete native samples, generated interfaces/stories, maps and model checksums. Windows fixture passwords are separately protected with DPAPI under `%LOCALAPPDATA%/MealieSbtStudy/IdentityCredentials/`; they are not placed in the ZIP or Git and are bound to the Windows account. This allows later qualification of original resources on this machine. No automatic deletion or reset is performed.

## Memory and prerequisites

Java heap: 512 MiB. Required free RAM: 1024 MiB. Required free disk: 512 MiB. Two compact samples must stay below 4 MiB per generated project. Chrome can remain open if the measured RAM threshold passes. Provengo, Java, Node for existing compatibility checks, and the existing project's Python resolution scripts must already be installed.

Run `Save-Generic-Multi-Identity.ps1 -Push` before the live campaign. It checks the added offline configuration tests, invokes the existing compatibility script, and commits only the release files. No live server calls are made by the save script.

## Qualification basis and limitations

Pinned v3.28.0 primary sources:

- `https://github.com/mealie-recipes/mealie/blob/v3.28.0/mealie/services/recipe/recipe_service.py`: group-scoped recipe lookup, collaborative editing, owner-only deletion, and copy creation assigned to the executing user.
- `https://github.com/mealie-recipes/mealie/blob/v3.28.0/mealie/routes/admin/admin_management_users.py`: administrator creates users with explicit role and scope fields.
- `https://github.com/mealie-recipes/mealie/blob/v3.28.0/docs/docs/documentation/getting-started/usage/permissions-and-public-access.md`: custom permissions and public access conditions.

The OpenAPI contract describes request/response structure, not the complete authorization policy. Permission expectations are explicit profile assumptions backed by these sources. Undocumented authorization rejections (403/404) are qualified by policy; they are not treated as missing success declarations. PUT response bodies are retained even though their response properties are not fully documented. Semantic write verification uses subsequent GETs against intended values, not the PUT body as its own oracle.

Local native tests use an independent mock server, not a real Mealie instance. Windows DPAPI and PowerShell execution need validation on the user's Windows machine. No new Mealie finding is claimed from those mock tests.
