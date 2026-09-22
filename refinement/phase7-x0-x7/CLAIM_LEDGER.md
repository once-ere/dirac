# Phase 7 claim ledger

This ledger separates exact derivations, numerical measurements, modeling
interpretations, and open questions. The machine-readable companion is
`evidence.json`.

| ID | Claim | Evidence | Audit disposition |
|---|---|---|---|
| C01 | The adopted coordinate order is `{x0,...,x7}`. | External bridge notebook input expression, hash-pinned in `evidence.json`. | Verified as a naming/order adoption only. |
| C02 | The homogeneous metric uses `x4` as proper evolution coordinate. | `geometry.json`, time index 4, `g44=-1`. | Verified; this does not import the bridge notebook's metric or connection. |
| C03 | `gamma^4` is a signed permutation matrix. | `verify_component_claims.py`; `evidence.json`. | Verified exactly; all 16 sums must be expanded in the refined report. |
| C04 | `C` is symmetric, involutory, split `(8,8)`, and makes `gamma^4` skew-adjoint. | Exact integral matrix identities in both verifiers. | Verified exactly. |
| C05 | The homogeneous Einstein tensor has one `44`, seven diagonal transverse, and 28 independent vanishing off-diagonal equations. | Independent rational derivation in `check_einstein_spinor_model.py`. | Verified for the homogeneous ansatz only. |
| C06 | The report gives the full covariant field theory. | Action and covariant equations in the Phase 5 report. | Must be distinguished from the solved homogeneous reduction. |
| N01 | The application integrates 18 ODE states. | `STATE_DIMENSION=18`; independent CSV/checker validation. | Verified. |
| N02 | Initial data are imposed at `x4=0` and integrated as two branches to `-0.2` and `1.5`. | `initial_state()` and `integrate()` in `lib.rs`. | Verified; prior reports need this detail. |
| N03 | The three quoted approximately `1e-9` errors are condensate, density, and Friedmann relative errors. | `derived_values()` and canonical CSV. | Verified; they are not ODE residual norms. |
| N04 | The five-point ODE residual check has maximum component RMS below `1e-3`. | Independent checker measurement in `evidence.json`. | Verified; exact value must be reported separately. |
| N05 | BDF is globally the “best” method. | No comparative solver benchmark exists. | Not established; replace with “selected robust method”. |
| N06 | CVODE uses variable-order BDF, default Newton iteration, an internal difference-quotient Jacobian, and a dense 18-by-18 direct solve. | Application and pinned SUNDIALS 7.8.0 sources, hash-recorded in `evidence.json`. | Verified; orders 1--5 and at most three nonlinear correctors per attempt. |
| N07 | Canonical replay is byte-identical and the tighter run converges toward the analytic constraints. | `convergence.json`; 24 independent checks. | Verified; maximum normalized canonical/refined state difference is `6.310776406656671e-10`. |
| D01 | The linear potential term is dust-like. | `p=S V_S-V=0`, `S proportional to a^-7`. | Verified as a homogeneous background analogy. |
| D02 | The fractional term is dark-energy-like. | `w=-4/5`, while 7-space acceleration requires `w<-5/7`. | Verified as a homogeneous background analogy. |
| D03 | The model establishes observed dark matter or dark energy. | No perturbation, clustering, compactification, stability, or observational analysis. | Not established and must not be claimed. |

## Implemented refinements

1. Expanded `S` and all 16 spinor ODEs with no matrix sums.
2. Wrote the eight diagonal Einstein equations separately and enumerated all 28
   independent off-diagonal equations as ansatz-specific identities.
3. Added the one-based mathematical to zero-based implementation mapping.
4. Stated the positive-condensate domain and its singular boundary.
5. Recorded reference-state data and two-branch integration.
6. Defined every error metric and reported finite-difference residuals
   separately from invariant errors.
7. Bounded the dark-sector classification and explicitly recorded untested
   physical claims.
8. Added exact quadrature, spinor-rotation reconstruction, and early/late
   asymptotic solutions.