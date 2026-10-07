# Integrated central Context native acceptance — 7 October 2026

The original review archive records three native Provengo 0.7.5-SNAPSHOT runs against an isolated loopback fixture, with seven HTTP requests per run. The central CLI generated each resource lifecycle and the shared observation support. The fixture test compiler added the bounded action process. This fixture binding is not automatic inference of arbitrary complex application actions.

The control completed successfully. An injected HTTP 500 without state change and an injected HTTP 500 with a stored state change each completed identity-bound readback before intentional failure. Captured status, actual state, and expected DAL state are separate. No Mealie requests occurred.

The exact generator source snapshot is included in generator-source.zip and in the unmodified review-original.zip. Generated JS, configuration and provenance are copied under executed/. The verifier checks checksums, requalifies all three native results and generates all three projects again from the captured source, fixture contract and compiler. Fifteen generated JS/report files and three configuration files must match after LF/CRLF normalization. Original archive bytes are preserved unchanged.

## Corrections included in the captured source

- The dedicated Context verifier calls synchronizing interfaces through a direct for loop rather than a forEach callback, avoiding the native continuation error seen in the preceding run.
- The qualifier expects the central lifecycle's GET before PATCH: seven requests, not six.
- The verified pre-action state is taken from the post-update GET.

## Scope still pending

F01–F03 evidence and source archives remain separate. This acceptance does not reproduce F04/F05 against Mealie. Complex action selection, binding and semantic effects must not be presented as OpenAPI-derived capabilities until implemented and evaluated. Observation expectedMatches currently records a diagnostic difference; it alone does not imply that a complex action's state change is forbidden.

The archive script only adds this evidence directory to a branch based on origin/main and pushes without force. It neither edits the original checkout nor installs the captured generator into another working project. No tests are rerun against Mealie. The next increment is automatic generation and isolated regression of action bindings, with explicit provenance and unsupported cases.
