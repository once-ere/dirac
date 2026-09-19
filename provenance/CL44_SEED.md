# Exact-real Cl(4,4) seed provenance

## Scope

This gate constructs eight exact integer 16-by-16 matrices for signature
`(4,4)`. It verifies the Clifford relations, all 256 ordered monomials, the
rank-128 even algebra, the two rank-eight volume-element projectors, the spin
action, irreducibility of each half-spin action, and inequivalence of the two
half-spin modules. No historical notebook output is imported or evaluated.

The generated fixture is `artifacts/exact/cl44-seed.json`. It records the
SHA-256 of `wolfram/Cl44.wl`, so a fixture cannot silently survive a package
change.

## Windows verification

Open PowerShell and run the complete gate:

```powershell
Set-Location C:\Users\nsh\Developer\code\vscode\dirac
.\scripts\verify_phase1_seed.ps1
```

The script performs these operations in order:

```powershell
python scripts/backup_files.py artifacts/exact/cl44-seed.json
wolframscript -file scripts/verify_cl44.wls -- artifacts/exact/cl44-seed.json
wolframscript -file scripts/verify_cl44.wls -- build/phase1/cl44-seed-repeat.json
python scripts/check_cl44_fixture.py
python -m unittest discover -s tests -v
```

It then compares the two generated JSON files byte-for-byte by SHA-256. The
final line must be:

```text
phase1_seed_verification=OK
```

## Git Bash or WSL verification

```bash
cd /c/Users/nsh/Developer/code/vscode/dirac
./scripts/verify_phase1_seed.sh
```

This runs the same Wolfram generation twice, the independent Python verifier,
the complete Python test suite, and the final SHA-256 comparison.

## Individual checks

To regenerate only the exact fixture:

```powershell
wolframscript -file scripts/verify_cl44.wls -- artifacts/exact/cl44-seed.json
```

To verify the fixture without using Wolfram's algebra routines:

```powershell
python scripts/check_cl44_fixture.py
```

The independent checker uses standard-library integer matrix arithmetic. A
rank of 256 modulo the prime 1,000,003 proves that the 256 integer monomials
are linearly independent over the real numbers because a nonzero modular minor
comes from a nonzero integer minor. The same argument verifies ranks 128 and
64 for the even algebra and its two half-spin actions.

## Expected measurements

```text
generatorCount=8
matrixDimension=16
monomialCount=256
fullAlgebraRank=256
evenAlgebraRank=128
plusProjectorRank=8
minusProjectorRank=8
plusEvenActionRank=64
minusEvenActionRank=64
plusSpinCommutantDimension=1
minusSpinCommutantDimension=1
halfSpinIntertwinerDimension=0
```

The one-dimensional commutants establish irreducibility of the two real
half-spin actions, and the zero-dimensional intertwiner space establishes
their inequivalence for the fixed spin-generator labeling.