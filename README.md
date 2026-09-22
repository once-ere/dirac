# Real Spin(4,4), split octonions, and triality

This repository provides a reproducible, exact-real treatment of
`Cl(4,4)`, `Spin(4,4)`, its two real half-spin modules, split-octonion
algebra, and split-real triality. It includes multiple numerical studies,
including Levi-Civita and teleparallel
Einstein-spinor reductions, driven by the pure-Rust SUNDIALS 7.8.0 CVODE
implementation. It publishes
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

The publication layer is complete. A standalone WolframScript combines all
69 exact and numerical checks; generated Mathematica and Jupyter notebooks
execute without failed checks; and the Phase 6-complete Markdown dissertation
builds to deterministic LaTeX and a warning-free 19-page PDF.

A parallel self-contained teaching edition is published as
[dissertation/Learn_dirac-triality.md](dissertation/Learn_dirac-triality.md),
[dissertation/Learn_dirac-triality.tex](dissertation/Learn_dirac-triality.tex),
and [dissertation/Learn_dirac-triality.pdf](dissertation/Learn_dirac-triality.pdf).
It develops the subject from calculus and basic matrices through Clifford
algebras, real half-spin representations, split octonions, triality, curved
spin geometry, Einstein-spinor dynamics, and teleparallel gravity. It includes
20 worked examples, 20 misconception checks, 22 exercises with complete
solutions, 53 glossary entries, a notation index, and reference capsules.
Both dissertation editions now include the verified Phase 5 and Phase 6 work.

Phase 5 defines the rank-16 real spinor bundle
`S = P_Spin x_rho (Delta_+ direct-sum Delta_-)` over an explicit curved
eight-manifold of signature `(4,4)`. The exact fixture records the tangent
metric, vielbein, curved metric, Christoffel symbols, canonical Levi-Civita
spin connection, and covariant derivative. Independent Python and Wolfram
derivations verify the Clifford relation, the full vielbein postulate, and the
ordered-pair convention behind
`D_mu = partial_mu + (1/8) omega_muab [gamma^a,gamma^b]`.

The third numerical study couples the same 16-component commuting classical
real spinor directly to the `(4,4)` Einstein equations. It contains neither a
scalar field nor a cosmological constant. Its two-term spinor potential has a
dust-like contribution and a negative-pressure contribution; an 18-state
CVODE integration checks condensate dilution, density evolution, Friedmann
closure, all state equations by finite differences, and deterministic replay.
The dark-matter and dark-energy identifications are homogeneous effective-fluid
analogies within this stated classical model, not observational detections.

Phase 6 replaces the canonical spin connection by a flat inertial
`Spin(4,4)` connection in an explicit diagonal Weitzenböck gauge. The exact
geometry has zero affine curvature, 14 nonzero torsion components,
`T=42 H^2`, and the boundary identity `R_LC=-T+B`. The Hermitian spinor
action contributes half the torsion trace, reproducing the canonical
homogeneous `7 H/2` Dirac term without treating the vanishing gauge
representative as an invariant absence of connection.

The fourth numerical study solves the resulting 18-state TEGR-spinor system.
It reproduces the canonical state history exactly, verifies the torsion and
boundary quantities independently at every sample, passes a tighter CVODE
convergence run, and classifies the linear and fractional-power condensate
terms as dust-like and negative-pressure homogeneous effective fluids. It
does not count the TEGR torsion scalar as a separate dark component and makes
no observational dark-matter or dark-energy claim.

Phase 6 content commit `369df0a80a9738b50880ea3f20846eebb6249a28`
was rebuilt from an anonymous recursive clone of public `main`. Every Phase 0
through Phase 6 PowerShell gate, the focused Learn gate, and the Phase 6 Bash
gate passed with zero tracked drift. Both the repository and recursive solver
submodule passed strict Git object checks.

Phase 6 release commit `acf02fe2f4f79fd4d41066aaddde06fb8bdcce97`
passed the same complete PowerShell and Bash verification from a second
anonymous recursive clone. The annotated `phase6-weitzenbock-spinor-green`
tag identifies that verified release commit.

Phase 5 content commit `88ce2220c144fa9487243f8d47e961f95f27461e`
and release commit `f9fef6a47b9cb5767c2f1150e9795798bfe8adef`
were rebuilt from anonymous recursive clones of public `main`. Every Phase 0
through Phase 5 PowerShell gate, the focused Learn gate, and the Phase 5 Bash
gate passed with zero tracked drift. The annotated
`phase5-curved-spin-gravity-green` tag identifies the verified release commit.

The annotated `learn-dissertation-green` tag was verified from an anonymous
recursive clone of the public repository. Every Phase 0 through Phase 4 gate
passed at the tagged commit, including both dissertation editions and all 27
Python tests, with zero tracked drift after regeneration. Both PowerShell and
Bash publication gates reproduce the same normalized Jupyter notebook bytes.

The `final-release-green` tag was verified from a fresh recursive clone. Every
phase gate passed, all 21 Python tests passed, 15 canonical artifacts were
byte-identical, and the rebuilt worktree had zero tracked drift. The local
`prompt.txt` is intentionally ignored and absent from the remote repository.

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
.\scripts\verify_learn_dissertation.ps1
.\scripts\verify_phase4_publication.ps1
.\scripts\verify_phase5_curved_spin_gravity.ps1
.\scripts\verify_phase6_weitzenbock_spinor.ps1
.\scripts\verify_phase7_x0_x7_reports.ps1
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
bash ./scripts/verify_learn_dissertation.sh
bash ./scripts/verify_phase4_publication.sh
bash ./scripts/verify_phase5_curved_spin_gravity.sh
bash ./scripts/verify_phase6_weitzenbock_spinor.sh
bash ./scripts/verify_phase7_x0_x7_reports.sh
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

The curved bundle geometry is under `wolfram/CurvedSpinGeometry.wl` and
`artifacts/curved-spin-geometry`; its standalone account is
[provenance/CURVED_SPIN_BUNDLE.md](provenance/CURVED_SPIN_BUNDLE.md), with
generated [LaTeX](provenance/CURVED_SPIN_BUNDLE.tex) and
[PDF](provenance/CURVED_SPIN_BUNDLE.pdf) editions.

The coupled Einstein-spinor study is under `studies/einstein_spinor_44`, with
canonical outputs under `artifacts/einstein-spinor-44`. Its equations,
numerical method, complete commands, limitations, and dark-sector analysis are
in [provenance/EINSTEIN_SPINOR_44.md](provenance/EINSTEIN_SPINOR_44.md), with
generated [LaTeX](provenance/EINSTEIN_SPINOR_44.tex) and
[PDF](provenance/EINSTEIN_SPINOR_44.pdf) editions.

The coordinate-fixed `{x0,...,x7}` component-by-component Einstein-spinor
equation inventory is in
[provenance/EINSTEIN_SPINOR_44_COMPONENTS_X0_X7.md](provenance/EINSTEIN_SPINOR_44_COMPONENTS_X0_X7.md),
with generated
[LaTeX](provenance/EINSTEIN_SPINOR_44_COMPONENTS_X0_X7.tex) and
[PDF](provenance/EINSTEIN_SPINOR_44_COMPONENTS_X0_X7.pdf).

The coordinate-fixed `{x0,...,x7}` numerical and approximate-method report,
including solver validation and dark-sector mapping, is in
[provenance/EINSTEIN_SPINOR_44_NUMERICS_X0_X7.md](provenance/EINSTEIN_SPINOR_44_NUMERICS_X0_X7.md),
with generated
[LaTeX](provenance/EINSTEIN_SPINOR_44_NUMERICS_X0_X7.tex) and
[PDF](provenance/EINSTEIN_SPINOR_44_NUMERICS_X0_X7.pdf).

The Weitzenböck geometry is under
`wolfram/WeitzenbockSpinGeometry.wl` and
`artifacts/weitzenbock-spin-geometry`. The teleparallel numerical study is
under `studies/weitzenbock_spinor_44`, with canonical outputs under
`artifacts/weitzenbock-spinor-44`. Its connection, action, field equations,
numerical method, complete commands, limitations, and dark-sector analysis
are in
[provenance/WEITZENBOCK_SPINOR_44.md](provenance/WEITZENBOCK_SPINOR_44.md),
with generated
[LaTeX](provenance/WEITZENBOCK_SPINOR_44.tex) and
[PDF](provenance/WEITZENBOCK_SPINOR_44.pdf) editions.

The publication artifacts are under `wolfram/`, `notebooks/`, and
`dissertation/`. Complete standalone rebuild commands are in
`provenance/WOLFRAMSCRIPT.md`, `provenance/MATHEMATICA_NOTEBOOK.md`,
`provenance/JUPYTER_NOTEBOOK.md`, `provenance/DISSERTATION.md`, and
`provenance/LEARN_DISSERTATION.md`.

## Scientific boundary

The real 16-dimensional irreducible module of the full Clifford algebra is
reducible after restriction to `Spin(4,4)`: it is the direct sum of two
inequivalent real 8-dimensional half-spin modules. The project will preserve
that distinction throughout its code and dissertation. A zero inertial spin
connection is used only together with its declared proper frame; local
Lorentz transforms generally produce nonzero pure-gauge representatives.