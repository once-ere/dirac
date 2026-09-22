# Phase 7 `{x0,...,x7}` refinement workspace

This tracked working directory audits and refines the Phase 7 component and
numerical provenance reports introduced at commit
`89408fef07a7b0a55237dc606074d58ef39a8892`.

## Scope

1. Expand the canonical `gamma^4` action and `C`-bilinear into actual scalar
   component formulas.
2. Distinguish the full covariant field equations from the homogeneous
   18-state reduction that was numerically integrated.
3. Verify every numerical claim against canonical artifacts, independent
   checkers, and tighter replay.
4. Classify dark-energy-like and dark-matter-like statements by what is
   proved, what is only analogous, and what remains untested.
5. Regenerate deterministic Markdown, LaTeX, and PDF outputs and verify them
   in a clean public clone.

## Audit status

- Initial finding: the previous report labels 16 equations “component form”
  while retaining unevaluated sums over the matrix entries of `gamma^4`.
- Local hypothesis: canonical `gamma^4` and `C` are signed permutation
  matrices, so all such sums and the condensate can be expanded without loss.
- Discriminating check: `verify_component_claims.py` requires exactly one
  nonzero entry in every row and checks the exact adjoint identities.
- Result: all six discriminating checks pass. The refined component report now
   expands the condensate and all 16 spinor equations without matrix sums.
- Corrected defect: the earlier report incorrectly gave positive metric entries
   for `x5`, `x6`, and `x7`; the refined metric has `-a^2` in all three slots.
- Evidence: `evidence.json` passes 7 exact-component, 4 exact-model, 7
   solver-source, and 22 numerical-output checks.
- Convergence: `convergence.json` passes all 24 canonical, replay, and refined
   numerical checks; the canonical replay is byte-identical.
- Semantic verification: `scripts/check_phase7_x0_x7_reports.py` passes 31
   report checks, including 16 spinor, 8 diagonal Einstein, and 28 independent
   off-diagonal Einstein component inventories.
- Publication verification: both eight-page PDFs build warning-free and are
   byte-identical across two isolated three-pass builds. Six focused regression
   tests pass, including deliberate matrix-sum and PDF-byte mutations.

All generated evidence belongs under this directory. The external
`Pre-Universe_opus-fable-main` reference remains untracked and read-only.