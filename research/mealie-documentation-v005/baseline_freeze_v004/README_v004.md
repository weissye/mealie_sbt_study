# Mealie research freeze v004

Read FREEZE_REPORT_v004.md. BASELINE_v004.json pins the user's immutable v016 ZIP. SOURCE_INVENTORY_v004.json covers all 416 source files. INPUTS_AND_SEMANTICS_v004.json separates declared semantic input, structural contract and package templates. VALIDATION_v004.json records the read-only checks.

Keep the original source ZIP alongside this audit sidecar. The sidecar contains metadata and a read-only verifier, not an additional live replay runner or a replacement source package.

After extracting this freeze package, verify it from PowerShell:

```powershell
python .\Verify-Freeze-v004.py --source "$env:USERPROFILE\Downloads\Mealie_F04_F05_Evidence_Package (1).zip"
```

Use the actual original ZIP path if its download name differs. Successful verification prints MEALIE_FREEZE_V004_ACCEPTED. No credentials, server, Java or Provengo are required. The verifier reads existing evidence and parses Python syntax without executing archived source.

ADAPTER_INPUT_SCHEMA_v004.json is a proposed provenance contract for the next research phase. It is not yet implemented as the input schema of the frozen compiler.
