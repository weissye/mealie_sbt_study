# Generic relationship consistency campaign

This delta extends the generic OpenAPI compiler, not a hand-written Mealie story.
All modeled HTTP operations and runtime checks stay in interfaces. Provengo actors
and dependencies stay in stories. Earlier runtime options remain unchanged unless
the new options are explicitly enabled.

## New opt-in options

- shared_target_updates[].verify_embedded_value: require the updated string value
  in every matched embedded object returned by known referrers. Each object must
  match the observed target identity; unrelated objects cannot satisfy the oracle.
  Non-null OpenAPI schema alternatives must all document the string view.
- detached_target_deletions: each rule selects resource_type, a documented DELETE
  operation belonging to that type, and explicit absence codes (404/410). This
  bounded implementation supports top-level many-to-many membership arrays and
  at least two known referrers. Other relationship forms fail generation.
- interleave_mutations: make independent update tasks and independent detach/delete
  tasks ready together. The coordinator still admits one whole task at a time.
  HTTP requests remain sequential. The existing graph prefix completes first;
  deletion tasks start after the update phase. Provengo chooses the ready actors.

## Oracles

Updates must persist at the target and in its embedded views while referenced
identity multisets and route identities remain stable. Receipts record actual
embedded values and the target identity; the acceptance tool independently checks
that every configured referrer was observed.

Before a tag/category deletion, every selected recipe is read. Two referring recipes
have only the selected membership removed. Other membership identities and all
other generated relationship fields are checked after each write. The target is
then deleted and must return the configured absence status. All five recipes are
read again, including the three non-referring controls. Removed target references
must remain absent, surviving membership identities must remain unchanged, and
other relationship bindings must remain unchanged. The deletion is an explicit
part of the generated test, not automatic cleanup or server reset.

No cascade policy for deleting an attached resource is assumed. This increment
first detaches the known memberships and only then deletes the owned target.
These assertions cover identities of protected relationship fields; they do not
assert equality of every scalar property or cover resources outside the pilot.

## Mealie configuration

mealie-relational-consistency-runtime.json retains the earlier food/unit, recipe,
shopping-list/item, tag/category and cycle prefix. Per complete schedule:

- 129 tasks and 658 HTTP calls;
- 35 registered owned instances;
- 10 shared food/unit updates with 30 embedded referrer checks;
- 20 tag/category membership detachments;
- 10 tag/category deletions with absence GETs;
- 50 post-deletion recipe checks (20 referrers, 30 non-referring controls);
- the existing 17 legal graph receipts and 7 qualified cycle rejection receipts.

The runner samples three schedules once and replays each without resetting the
server. Each replay creates its own owned instances. Credentials are entered once,
used only in process environment variables and cleared/restored in finally. The
campaign stops at its first failed replay; it never automatically retries.

The collector checks model hashes, source sample identity, exact live task order,
prerequisites, selected HTTP event counts and every runtime receipt. Duplicate
sample identities do not count as extra runs. Distinct mutation order counts are
measured rather than inferred from different sample IDs.

## Windows execution

Extract generic_generator_relationship_consistency_delta.zip into the existing
C:\work\temp\mealie_sbt_study tree. Run:

    .\scripts\Run-Generic-Consistency-Campaign.ps1 -Username changeme@example.com

The runner uses seed 207, a 1 GiB JVM heap, a 2 GiB free-RAM guard and a 1 GiB
free-disk guard. Sampling is bounded by the compiled event count and capped at
128 MiB. For one initial schedule, pass -SampleCount 1; default is 3.

Review ZIPs are placed in Downloads\mealie-consistency-<timestamp>. Upload
campaign.zip, which contains the individual live review ZIPs and a campaign
acceptance report. If execution stops before live replay, upload sampling.zip.
Existing projects and their evidence remain intact.

A failed assertion is a candidate for investigation, not automatically a confirmed
Mealie bug. Direct reproduction and expected-behavior qualification are still needed.
Full server reset/replay and deletion while references remain attached are not
implemented in this increment.

## Validation

Run python -m unittest discover -s tests -v from generic-generator. Set
PROVENGO_TEST_JAR to Provengo.uber.jar to enable native tests. Native tests use a
local HTTP fixture, not a Mealie server, with a 512 MiB JVM heap. They execute
three schedules with mutation-order variation and verify that stale embedded values, ignored
deletes, unrelated-link corruption and unintended source deletion prevent acceptance.
