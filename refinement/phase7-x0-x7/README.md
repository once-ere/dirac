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

All generated evidence belongs under this directory. The external
`Pre-Universe_opus-fable-main` reference remains untracked and read-only.