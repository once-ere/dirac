# Real Spin(4,4), split octonions, and triality

This repository is being built as a reproducible, exact-real treatment of
`Cl(4,4)`, `Spin(4,4)`, its two real half-spin modules, split-octonion
multiplication, and split-real triality. It will also contain two numerical
studies driven by the pure-Rust SUNDIALS 7.8.0 CVODE implementation and publish
standalone WolframScript, Mathematica, Jupyter, Markdown, LaTeX, PDF, and
provenance artifacts.

Phase 0 is complete. The seven-root source corpus is frozen in a byte-complete
SHA-256 manifest, all 209 required Markdown and Wolfram-family artifacts have
human review evidence, and all 66 parseable Wolfram artifacts import without
evaluation or drift. Embedded outputs in historical notebooks are not treated
as verified results.

## Current verification

From PowerShell:

```powershell
Set-Location C:\Users\nsh\Developer\code\vscode\dirac
.\scripts\run_logged.ps1 -LogPath logs\phase0-tests.log `
  -Command "python -m unittest discover -s tests -v"
.\scripts\verify_phase0.ps1
.\scripts\status.ps1
```

From Git Bash:

```bash
cd /c/Users/nsh/Developer/code/vscode/dirac
./scripts/run_logged.sh logs/phase0-tests-bash.log -- \
  python -m unittest discover -s tests -v
./scripts/verify_phase0.sh
./scripts/status.sh
```

The generated source inventory and seven human-review reports are under
`audit/`. Local command logs and backup payloads are ignored;
hash-verification manifests remain trackable.

## Scientific boundary

The real 16-dimensional irreducible module of the full Clifford algebra is
reducible after restriction to `Spin(4,4)`: it is the direct sum of two
inequivalent real 8-dimensional half-spin modules. The project will preserve
that distinction throughout its code and dissertation.