# Mealie generator delta 1.7

Extract into the existing mealie_sbt_study project. Requires accepted increment 1.6.1 fixture and the reviewed v3.28.0 contract.

Run scripts/Prepare-Mealie-Provengo-Model.ps1 -Sample. This creates a new offline project with separate 00_interfaces.js and 10_stories.js, operation/schema/scenario IR, the accepted fixture bindings, and a review ZIP in Downloads.

The generator uses OpenAPI operations and reusable templates selected by profiles/mealie-pilot.json. Business identity bindings and oracle intent are explicit policy. The symbolic backend sends no server requests. The included provengo/generated-review directory is a source preview, without user fixture bindings. Use the preparation script to generate the actual project.

See docs/GENERATOR_ARCHITECTURE.md for source provenance, boundaries and remaining live execution gates. The previous uploaded model passed exact 70-schedule coverage. The separated generated JavaScript passed syntax and stub wiring checks; run installed Provengo to accept the new layout.
