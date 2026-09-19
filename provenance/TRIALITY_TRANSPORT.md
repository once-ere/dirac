# 24-state triality transport provenance

## Mathematical definition

The state is three real eight-vectors `(v, s_plus, s_minus)`. The blocks carry
the vector, first half-spin, and second half-spin representations exported by
the verified exact triality fixture. They evolve under the same noncommuting,
time-dependent Lie-algebra path:

```text
X(t) = (1/5) E(0,1)
     + (3/20 + t/40) E(1,4)
     + (-1/10 + t/50) E(4,5)
     + (t (4 - t)/80) E(2,6).
```

The initial value of every block is `(1,0,0,0,0,0,0,0)`, and integration is
from zero through four with output spacing `0.1`. The three split norms and
the invariant trilinear form all start at one and must remain constant within
`1e-8`.

## Solver provenance

The solver is a Git submodule at `vendor/sundials_rs`, pinned to:

```text
d1836e6a279d63a90fe2839a0020123245487e76
```

That commit was compared against all 1,713 tracked files in the audited local
solver copy before it was added; no file was missing or different. Application
code is under `studies/triality_transport`. No file inside the solver submodule
is modified.

CVODE configuration:

```text
method             BDF
nonlinear method   Newton
linear solver      dense
state dimension    24
relative tolerance 1e-11
absolute tolerance 1e-13 for every component
maximum step       0.02
```

## Complete Windows verification

From PowerShell:

```powershell
Set-Location C:\Users\nsh\Developer\code\vscode\dirac
git submodule update --init --recursive
.\scripts\verify_phase1.ps1
.\scripts\verify_phase2_transport.ps1
```

The Phase 2 script performs, in order:

```powershell
python scripts/backup_files.py studies/triality_transport/src/generated.rs artifacts/triality-transport/trajectory.csv artifacts/triality-transport/summary.json
python scripts/generate_triality_transport_constants.py
python scripts/generate_triality_transport_constants.py --output build/phase2/generated-repeat.rs
cargo fmt -p triality_transport -- --check
cargo clippy -p triality_transport --all-targets -- -D warnings
cargo test -p triality_transport
python -m unittest discover -s tests -v
cargo run --release -p triality_transport -- --output artifacts/triality-transport
cargo run --release -p triality_transport -- --output build/phase2/triality-transport-repeat
python scripts/check_triality_transport.py --repeat build/phase2/triality-transport-repeat
```

The final line must be:

```text
phase2_triality_transport_verification=OK
```

## Complete Git Bash or WSL verification

```bash
cd /c/Users/nsh/Developer/code/vscode/dirac
git submodule update --init --recursive
./scripts/verify_phase1.sh
./scripts/verify_phase2_transport.sh
```

The Bash gate resolves the installed Windows WolframScript executable when it
runs under WSL.

## Verified output contract

The canonical run writes:

```text
artifacts/triality-transport/trajectory.csv
artifacts/triality-transport/summary.json
```

Expected measurements:

```text
sampleCount=41
solverSteps=237
rhsEvaluations=251
maximum vector-norm drift <= 1e-8
maximum plus-norm drift <= 1e-8
maximum minus-norm drift <= 1e-8
maximum trilinear drift <= 1e-8
```

The output checker reloads the CSV, recomputes all four invariants from the
24 state columns and the exact para-product tensor, reconciles the summary,
and requires byte-identical CSV and JSON from the repeated release run.