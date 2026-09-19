# Standalone WolframScript provenance

## Artifact

```text
wolfram/dirac_triality.wls
```

The script loads the three exact packages, reruns their verification reports,
loads both numerical summaries, fails on any false check, and writes a compact
machine-readable report.

## Complete Windows commands

```powershell
Set-Location C:\Users\nsh\Developer\code\vscode\dirac
git submodule update --init --recursive
.\scripts\verify_phase1.ps1
.\scripts\verify_phase2_transport.ps1
.\scripts\verify_phase3_cosmology.ps1
.\scripts\run_logged.ps1 `
  -LogPath logs\phase4-standalone-wolfram.log `
  -Command "wolframscript -file wolfram/dirac_triality.wls -- artifacts/wolfram/dirac-triality-report.json"
Get-FileHash artifacts\wolfram\dirac-triality-report.json -Algorithm SHA256
```

The command must exit zero and print `failed_check_count=0`.

## Complete Git Bash or WSL commands

```bash
cd /c/Users/nsh/Developer/code/vscode/dirac
git submodule update --init --recursive
./scripts/verify_phase1.sh
./scripts/verify_phase2_transport.sh
./scripts/verify_phase3_cosmology.sh
source ./scripts/resolve_wolframscript.sh
wolframscript_command="$(resolve_wolframscript)"
./scripts/run_logged.sh logs/phase4-standalone-wolfram-bash.log -- \
  "$wolframscript_command" -file wolfram/dirac_triality.wls -- \
  artifacts/wolfram/dirac-triality-report.json
sha256sum artifacts/wolfram/dirac-triality-report.json
```

The report contains 69 checks: 23 Clifford checks, 17 split-octonion checks,
25 triality checks, and four numerical-summary checks.