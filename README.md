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

The Phase 1 exact gate is also complete. It independently constructs the real
16-dimensional Clifford module, its two inequivalent real half-spin modules,
split-octonion multiplication, the invariant triality trilinear form, and the
outer six-element permutation action. All public fixtures contain only exact
real data.

The first numerical study transports the vector and two half-spin states as a
24-component real system through one noncommuting triality path. The
application uses the pinned pure-Rust CVODE engine, preserves three split
norms and the invariant trilinear form, and emits deterministic CSV and JSON.

The second numerical study evolves an 18-state real homogeneous spinor
background in e-fold time. It reconstructs a CPL density with a nonlinear
potential, checks the 16-component condensate dilution directly, and emits a
deterministic 1,201-row background history.

## Current verification

From PowerShell:

```powershell
Set-Location C:\Users\nsh\Developer\code\vscode\dirac
.\scripts\run_logged.ps1 -LogPath logs\phase0-tests.log `
  -Command "python -m unittest discover -s tests -v"
.\scripts\verify_phase0.ps1
.\scripts\verify_phase1.ps1
.\scripts\verify_phase2_transport.ps1
.\scripts\verify_phase3_cosmology.ps1
.\scripts\status.ps1
```

From Git Bash:

```bash
cd /c/Users/nsh/Developer/code/vscode/dirac
./scripts/run_logged.sh logs/phase0-tests-bash.log -- \
  python -m unittest discover -s tests -v
./scripts/verify_phase0.sh
./scripts/verify_phase1.sh
./scripts/verify_phase2_transport.sh
./scripts/verify_phase3_cosmology.sh
./scripts/status.sh
```

The generated source inventory and seven human-review reports are under
`audit/`. Local command logs and backup payloads are ignored;
hash-verification manifests remain trackable.

Exact machine-readable fixtures are under `artifacts/exact/`. Their complete
commands and expected measurements are in `provenance/CL44_SEED.md` and
`provenance/SPLIT_OCTONION_TRIALITY.md`.

The transport study is under `studies/triality_transport`, its canonical
outputs are under `artifacts/triality-transport`, and all commands are in
`provenance/TRIALITY_TRANSPORT.md`.

The cosmology study is under `studies/spinor_cosmology`, its canonical outputs
are under `artifacts/spinor-cosmology`, and all commands are in
`provenance/SPINOR_COSMOLOGY.md`.

## Scientific boundary

The real 16-dimensional irreducible module of the full Clifford algebra is
reducible after restriction to `Spin(4,4)`: it is the direct sum of two
inequivalent real 8-dimensional half-spin modules. The project will preserve
that distinction throughout its code and dissertation.