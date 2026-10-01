# Native authentication wire diagnostic

This additive diagnostic makes one direct authentication request using the
previously accepted form and one native Provengo authentication request through
an ephemeral loopback relay. The token URL is inferred from the supplied
OpenAPI password flow. Only local HTTP origins are supported.

The relay compares decoded username/password values with the process inputs,
records content types and native response status, and forwards the native
request body without modifying it. Report fields contain comparisons, not
credential values. Neither response tokens nor raw incoming bodies are saved.

Three local tests passed, including an actual local HTTP relay and absence of
secrets in the review ZIP. Native Provengo/Windows execution of this diagnostic
remains to be verified on the user computer. This diagnoses the cause rather
than presuming a generator fix. Existing generator, stories, interfaces,
profiles and sampled schedules remain unchanged. No resources are created.

Run scripts/Diagnose-Generic-Provengo-Auth.ps1 -Username changeme@example.com.
Upload Downloads/generic_auth_diagnostic_review.zip afterward. The
AUTH_DIAGNOSTIC_WIRE_CAPTURED result indicates diagnostic capture, not successful
authentication; inspect the recorded direct and native HTTP statuses.
