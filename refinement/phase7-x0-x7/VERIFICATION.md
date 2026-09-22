# Phase 7 refinement verification record

Date: 2026-09-22

## Audited lineage

- Original Phase 7 report commit: `89408fef07a7b0a55237dc606074d58ef39a8892`.
- Refinement workspace commit: `2935c07f88af399116663a79146ae15e3804a968`.
- Claim-evidence commit: `898a0cf45ff8fc14c75bb9c8b394e3aa949f9421`.
- Refined report commit: `0f2944d9057a1e42f5b13044edf8cf3351696229`.
- Convergence-verification commit: `4622b04719191469b742d37767cf4e1a84a9ccbc`.
- Fresh-clone line-ending fix: `c1e6c9dbda7c16d459ad92fb62b022ffa5a23b98`.
- Solver submodule: `d1836e6a279d63a90fe2839a0020123245487e76`.

## Corrections made

1. Corrected the homogeneous metric entries at coordinate indices 5, 6, and
   7 from `+a^2` to `-a^2`, restoring signature `(4,4)`.
2. Clarified that only the names/order `{x0,...,x7}` are adopted from the
   external bridge notebook; its metric and connection are not imported.
3. Distinguished the unrestricted covariant Einstein-spinor PDEs from the
   homogeneous system actually solved.
4. Expanded the invariant condensate and all 16 spinor equations using the
   exact signed-permutation matrices `C` and `gamma^4`.
5. Listed all 8 diagonal and all 28 independent off-diagonal homogeneous
   Einstein equations.
6. Documented the one-based mathematical to zero-based implementation mapping,
   the `x4=0` reference state, and independent backward/forward integrations.
7. Replaced the unsupported globally "best" solver claim by the source-verified
   selected method and its limitations.
8. Defined invariant errors separately from five-point ODE and spatial-Einstein
   residuals.
9. Added exact background quadrature, spinor-rotation reconstruction, early
   dust-like and late negative-pressure asymptotics, and bounded physical
   interpretation.
10. Added checkout-independent evidence generation and pinned the hashed Rust
    source to LF after the first fresh clone exposed line-ending drift.

## Verification counts

- Exact matrix/component verifier: 6 checks passed.
- Machine-readable evidence: 7 exact-component, 4 exact-model, 7 solver-source,
  and 22 canonical numerical checks passed.
- Replay/refinement evidence: 24 checks passed.
- Semantic report checker: 32 checks passed, including recomputation of every
   artifact hash quoted by this record.
- Focused Python regressions: 6 tests passed, including deliberate mutation
  rejection.
- Complete Python suite: 42 tests passed.
- Einstein-spinor Rust suite: 4 tests passed; formatting and clippy passed with
  warnings denied.
- Components PDF: 6 structural/hash/replay checks passed.
- Numerics PDF: 6 structural/hash/replay checks passed.
- Both PDF pairs were produced by isolated three-pass builds with no errors,
  warnings, overfull boxes, underfull boxes, or undefined controls.

## Numerical results

- Canonical samples: 171.
- Canonical solver steps / RHS evaluations: 1,372 / 1,486.
- Canonical maximum independently recomputed relative errors:
  - condensate: `7.441921424927986e-09`;
  - density: `1.4894832079072834e-09`;
  - Friedmann constraint: `1.203543250505252e-09`.
- Maximum five-point component ODE RMS residual:
  `4.705850657056059e-04`.
- Maximum normalized spatial-Einstein finite-difference residual:
  `5.702272371471661e-07`.
- Transition `(x4,a)`: `(-0.13800529330324499, 0.8631436165767085)`.
- Refined solver steps / RHS evaluations: 2,294 / 2,422.
- Maximum canonical/refined normalized state difference:
  `6.310776406656671e-10`.
- Refined maximum independently recomputed relative errors:
  `1.6415774988196702e-09`, `3.2855796418252515e-10`, and
  `3.31034411227924e-10`.

## Canonical hashes

| Artifact | SHA-256 |
|---|---|
| Components Markdown | `aba76aabc2fce453aa1214b4b580555aa04045649279df2c9f796a27d3994502` |
| Components LaTeX | `4249ed227b8b4ed1c6ad7b8ec9f4b122fc296f7f17e729c274f49b7914d802ee` |
| Components PDF | `f64e3f8420c18c3886e201c64ee41d8e0564d7222038f5a8b83f45a46b7113f4` |
| Numerics Markdown | `1ea9958088af5044f8ceea67e44c1b3b634e581e0902c26c1f364f9efa9e8f49` |
| Numerics LaTeX | `8465df163fb255c8b091365d543c604e6692d8b114921241e6cac5b39eb3a054` |
| Numerics PDF | `8501d992709282039b5a69d1de045660018505f1048f09fecfedc40795484af9` |
| Exact/canonical evidence | `58373d6aeea90807a3f064f395b8367502ff3a280050a5c8823c9e0cc0b2eb0b` |
| Replay/refinement evidence | `9cf9e89a2326786e2573eafbf1ad1cdcb1528eeb540bfb102cbf5c6988a1ef76` |

Both PDFs have 8 pages and one letter-sized `612 x 792` point media box.

## Independent public-clone verification

A recursive clone from `https://github.com/once-ere/dirac.git` at
`C:\Users\nsh\Developer\code\vscode\dirac-phase7-verify-c1e6c9d` resolved
`HEAD`, `origin/main`, and live `refs/heads/main` to
`c1e6c9dbda7c16d459ad92fb62b022ffa5a23b98`.

The fresh clone passed the complete strengthened PowerShell Phase 7 gate, all
42 Python tests, strict `git fsck --full --strict` in the main repository and
solver submodule, and zero tracked or staged drift after regeneration. The
six publication artifact hashes and both evidence hashes matched the source
checkout exactly.

## Scientific boundary

The verified results establish exact algebraic consistency and reproducible
homogeneous background dynamics for this specified split-signature classical
spinor model. They do not establish a realistic dark-matter clustering model,
perturbative or quantum stability, compactification to observed spacetime, or
agreement with cosmological data.
