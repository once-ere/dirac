# Mathematica notebook provenance

## Artifact

```text
notebooks/DiracTriality.nb
```

The notebook is generated from held Wolfram expressions. It contains 22 cells,
including 14 executable input cells. The verifier imports the notebook without
evaluation, then evaluates every input cell in order in a fresh Wolfram kernel
with an explicit repository root. It fails on messages, failed evaluations, a
changed cell count, or any failed notebook check.

## Complete Windows commands

```powershell
Set-Location C:\Users\nsh\Developer\code\vscode\dirac
.\scripts\run_logged.ps1 `
  -LogPath logs\phase4-build-mathematica-notebook.log `
  -Command "wolframscript -file scripts/build_mathematica_notebook.wls -- notebooks/DiracTriality.nb"
.\scripts\run_logged.ps1 `
  -LogPath logs\phase4-build-mathematica-notebook-repeat.log `
  -Command "wolframscript -file scripts/build_mathematica_notebook.wls -- build/phase4/DiracTriality-repeat.nb"
$first = (Get-FileHash notebooks\DiracTriality.nb -Algorithm SHA256).Hash
$second = (Get-FileHash build\phase4\DiracTriality-repeat.nb -Algorithm SHA256).Hash
if ($first -ne $second) { throw "Mathematica notebook generation changed bytes" }
.\scripts\run_logged.ps1 `
  -LogPath logs\phase4-verify-mathematica-notebook.log `
  -Command "wolframscript -file scripts/verify_mathematica_notebook.wls -- notebooks/DiracTriality.nb"
```

Expected verifier totals:

```text
input_cell_count=14
failed_evaluation_count=0
message_count=0
notebook_check_count=5
failed_notebook_check_count=0
```

## Complete Git Bash or WSL commands

```bash
cd /c/Users/nsh/Developer/code/vscode/dirac
source ./scripts/resolve_wolframscript.sh
wolframscript_command="$(resolve_wolframscript)"
./scripts/run_logged.sh logs/phase4-build-mathematica-notebook-bash.log -- \
  "$wolframscript_command" -file scripts/build_mathematica_notebook.wls -- \
  notebooks/DiracTriality.nb
./scripts/run_logged.sh logs/phase4-build-mathematica-notebook-repeat-bash.log -- \
  "$wolframscript_command" -file scripts/build_mathematica_notebook.wls -- \
  build/phase4/DiracTriality-repeat.nb
test "$(sha256sum notebooks/DiracTriality.nb | cut -d' ' -f1)" = \
  "$(sha256sum build/phase4/DiracTriality-repeat.nb | cut -d' ' -f1)"
./scripts/run_logged.sh logs/phase4-verify-mathematica-notebook-bash.log -- \
  "$wolframscript_command" -file scripts/verify_mathematica_notebook.wls -- \
  notebooks/DiracTriality.nb
```