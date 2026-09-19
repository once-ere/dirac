# Audit: Eternal-DEFLATION-Inflation-main

Review status: complete for all nine required artifacts: one Markdown file,
two Wolfram sources, and six notebooks. No source was modified or executed.
Notebook code was imported only as held structure; stored outputs and messages
are historical evidence rather than verification.

## Artifact Findings

| Path | Finding | Disposition |
|---|---|---|
| `README.md` | Clearly labels the model as a hypothesis and acknowledges that the wave-function stress tensor and coupled self-consistency were not demonstrated. Claims about paired universes, mass signs, dark sectors, and superluminal behavior therefore remain conjectural. | Historical evidence |
| `ConvertMapleToMathematicaV2.wl` | SHA-256-identical to the reviewed copies in two other roots. It is a disclaimed, incomplete text parser that may skip input before evaluating the result. | Historical evidence |
| `Dirac-Lord-Nash_4+4.wl` | SHA-256-identical to the reviewed copies in two other roots. It conflates chiral blocks with full Clifford generators and lacks faithfulness, half-spin, and full-triality proofs. | Independently reconstruct |
| `Dirac_Nash_Identity.nb` | Historical scratch derivation with useful low-dimensional identity patterns, but it depends on front-end notation state, retains 167 cached outputs and rasterized derivations, and does not supply an isolated exact-real test suite. | Independently reconstruct |
| `Einstein-Lovelock-4+4-Nash.nb` | xAct-dependent diagonal-ansatz calculation with opaque binary cache writes and 227 cached result cells. It may supply candidate reduced equations, but no clean-kernel reproduction or independent substitution proof is present. | Historical evidence |
| `Einstein-Lovelock-7+1-Nash.nb` | Near-duplicate of the 4+4 notebook with 66 of 79 distinct input bodies shared. It retains one message cell and the same stateful xAct/cache workflow, so it is not independent confirmation. | Historical evidence |
| `Pair-Crtn-Univ-same_E-L-eqs-alt-approach.nb` | Large copied scratch notebook with 908 input cells, four stored messages, an incomplete Maple parser, binary-state dependencies, failed symbolic-solver paths, and an explicit warning that the source backreaction is omitted. Mass-sign solutions do not by themselves prove physical pair creation. | Independently reconstruct |
| `WaveFunctionUniverse-4+4-Einstein-Lovelock.nb` | Shares 442 distinct input bodies with the paired-universe notebook and retains six messages plus several binary cache writes. The metric and field equations are treated in stages rather than as a verified coupled system. | Independently reconstruct |
| `xact-Vacuum.nb` | Useful xAct setup pattern, but 16 stored messages are explicitly ignored, kernel-dependent binary caches are written, and 69 of its 110 distinct inputs recur in the 4+4 notebook. | Reuse pattern |

## Structural And Lineage Evidence

- All nine files have complete byte and text-stream coverage; all eight
  Wolfram files parse without evaluation, parser messages, hash drift, or size
  drift.
- The source duplicates were matched by SHA-256 before findings were reused.
- The six notebooks contain 2,545 authored cells and 1,680 cached
  result/message cells in total. Every authored cell has an ordered digest.
- The two Einstein-Lovelock variants share 66 of 79 distinct input-cell bodies.
- The 4+4 variant shares 69 input bodies with `xact-Vacuum`; the two large
  wave-function notebooks share 442 input bodies.
- The notebooks depend on xAct, front-end notation state, local path context,
  and kernel-version-sensitive binary caches. None is a standalone rerun.

## Corrections Carried Forward

- Solving a reduced diagonal ansatz can establish a candidate special
  solution only after complete substitution into every independently derived
  field equation; it does not classify the full solution space.
- Coordinate scale-factor growth does not by itself establish a causal
  superluminal observable.
- Opposite signs of a mass parameter in field solutions do not establish a
  creation process, conserved energy assignment, or a pair-production rate.
- Omitting the field stress tensor prevents a self-consistent coupled
  cosmological solution.
- All target numerical claims must be reconstructed with the required CVODE
  implementation and checked against exact constraints; cached Wolfram or
  Maple output is not accepted.

Reviewed: 9 of 9 required artifacts.