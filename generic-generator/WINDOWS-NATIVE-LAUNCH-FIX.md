# Windows native launch fix

Fixes the Python runner passing a cmd.exe command string inside an argument
list, causing a second list2cmdline conversion and literal backslash quotes.
The BAT launch now passes a raw, double-wrapped cmd command string, with each
argument quoted. Native failures also expose a sanitized error excerpt.

Four launch regression checks and eight compiler tests passed locally.
Actual Windows cmd.exe/Provengo execution remains to be verified on Windows.
No generator source, generated project, resource profile or schedule is changed.
Resume Sample-Generic-Relationship-Model.ps1 on the existing compiled project;
after successful sampling invoke Invoke-Generic-Relationship-Scenario.ps1.
Do not rerun the combined pilot wrapper just to apply this launch correction.
