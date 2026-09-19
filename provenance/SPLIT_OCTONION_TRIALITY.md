# Split-octonion multiplication and triality provenance

## Scope

`wolfram/SplitOctonion.wl` constructs a split composition algebra in an
orthogonal real basis with signature `(4,4)`. The unit is the first basis
vector. Multiplication is derived from a Zorn model rather than copied from a
historical notebook.

`wolfram/Triality44.wl` constructs the 28-dimensional related-triple Lie
algebra of the para-product. It solves the defining linear equations, proves
that all three eight-dimensional projections are irreducible and pairwise
inequivalent, and constructs exact outer generators satisfying the relations
of `S3`. It also builds the Clifford representation induced by multiplication
and finds an exact invertible intertwiner to `wolfram/Cl44.wl`.

## Complete Windows verification

```powershell
Set-Location C:\Users\nsh\Developer\code\vscode\dirac
.\scripts\verify_phase1.ps1
```

This command backs up all generated exact fixtures, runs each Wolfram verifier
twice, runs three independent Python verifiers, runs the full test suite, and
requires byte-identical repeated JSON output.

The final line must be:

```text
phase1_exact_verification=OK
```

## Complete Git Bash or WSL verification

```bash
cd /c/Users/nsh/Developer/code/vscode/dirac
./scripts/verify_phase1.sh
```

## Individual commands

```powershell
wolframscript -file scripts/verify_split_octonion.wls -- artifacts/exact/split-octonion.json
python scripts/check_split_octonion_fixture.py
wolframscript -file scripts/verify_triality44.wls -- artifacts/exact/triality44.json
python -u scripts/check_triality44_fixture.py
python -m unittest discover -s tests -v
```

## Required split-octonion results

- Basis dimension: 8.
- Metric inertia: four positive and four negative directions.
- Ordinary and para-product tensors: 64 nonzero integral entries each.
- Tensor mode ranks: `(8,8,8)` for both products.
- Exact unit, conjugation reversal, quadratic norm, norm composition,
  alternativity, and cyclic para-product trilinear form.

## Required triality results

- Related-triple constraint rank: 56 inside 84 parameters.
- Triality Lie algebra dimension: 28.
- Projection ranks: `(28,28,28)`.
- Representation commutant dimensions: `(1,1,1)`.
- Pairwise intertwiner dimensions: `(0,0,0)`.
- Outer-action element count: 6, with exact order-three, order-two, and braid
  relations.
- Multiplication-induced Clifford intertwiner: dimension 1 and rank 16.
- Canonical half-spin matching dimensions: `((1,0),(0,1))`.

The three scalar commutants establish real irreducibility. The zero pairwise
intertwiner dimensions establish inequivalence. Since the order-three outer
action permutes these inequivalent modules, it cannot be an inner action.