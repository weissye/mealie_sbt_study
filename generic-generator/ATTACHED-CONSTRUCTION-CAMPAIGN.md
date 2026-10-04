# Attached deletion during relationship construction

This additive generator revision keeps all HTTP operations and response callbacks
in interfaces. Stories schedule complete tasks sequentially; HTTP requests do not
overlap. Previous profiles and their generated outputs are preserved.

## New opt-in settings

- `attached_target_deletions`: selected resource type, documented DELETE operation,
  explicit absence codes (404/410), and `success_policy: remove_references`.
- `mutate_during_construction: true`: update/delete tasks wait for their own known
  incoming links and resource creations instead of the complete scenario prefix.
  Later qualified construction actions wait for mutations. Dependency cycles are
  rejected by the existing compiler.

The supplied Mealie profile selects five tags and five categories. Each is linked
to two recipes before DELETE. No preliminary PUT/PATCH detaches these links.
After successful DELETE, GET must confirm target absence; all five selected
recipes are read again. The two referring recipes must lose only the deleted
membership. Three non-referring controls and all other selected relationship
identity arrays must remain unchanged. The explicit policy is configuration,
not a deletion policy inferred from OpenAPI or independently confirmed source.
A rejection such as 400/409 stops the campaign for policy/precondition review;
it is not automatically a confirmed application bug.

The model also updates ten shared food/unit names and checks fresh embedded names
in thirty selected recipe/shopping-item views. Existing legal recipe graph and
negative cycle probes remain enabled.

## Run on Windows

Extract the delta into the existing study root, then run:

```powershell
& .\scripts\Run-Generic-Attached-Construction-Campaign.ps1 -Username 'changeme@example.com'
```

The runner checks compatibility, generates seed 208, samples three schedules once,
and replays each schedule with new owned resources. It asks for the API password
once, uses a 1 GiB Java heap, and requires 2 GiB free RAM and 1 GiB free disk.
It does not close Chrome. Resource use depends on other applications. Samples over
128 MiB prevent replay. No automatic retry or server reset is performed.

Upload `campaign.zip` from the printed timestamped Downloads folder. If failure
occurs earlier, upload the available generation/sampling/live ZIPs there.

## Evidence and limits

Each schedule has 129 tasks and 598 HTTP calls. The campaign collector independently
checks model hashes, actual completed task order, HTTP counts, callback receipts,
attached-delete GET/DELETE/GET sequences with no detach writes, and construction
remaining after the first mutation. It reports distinct mutation orders and the
observed number of initial links after the first mutation.

Protected invariants cover selected relationship identifiers, not every scalar
property or every resource in the server. The delete receipt key remains
`detached_deletions` for compatibility; entries for new tasks additionally require
`attached_at_delete: true`, and the plan uses `kind: attached_delete`.

Local injected-fault and native Provengo fixture regressions are not evidence
that the real Mealie server passed. Real campaign execution is still required.
