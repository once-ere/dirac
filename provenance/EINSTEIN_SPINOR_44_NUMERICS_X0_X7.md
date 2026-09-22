# Numerical and Approximate Solution Methods for the Signature `(4,4)` Einstein-Spinor Components on `{x0,...,x7}`

## Complete solver-method provenance and dark-sector interpretation report

### Abstract

This report gives the numerical strategy for solving the full 18-equation
homogeneous reduction of the coordinate-explicit Einstein-spinor model written
in

```text
coordinates = {x0, x1, x2, x3, x4, x5, x6, x7}
```

with evolution variable `x4`. The method is designed to solve each component
equation in one coupled stiff system, quantify approximation error, and expose
model-internal dark-energy-like and dark-matter-like behavior from the
16-component commuting spinor condensate.

## 1. System solved and solver target

State vector:

$$
y(x4)=(a,H,\psi_1,\ldots,\psi_{16})\in\mathbb R^{18}.
$$

The solved component equations are:

$$
\frac{da}{dx4}=aH,
\qquad
\frac{dH}{dx4}=-\frac{\kappa_8}{6}(\rho+p),
$$

$$
\frac{d\psi_A}{dx4}=-\frac{7}{2}H\psi_A-V_S\sum_{B=1}^{16}(\gamma^4)_{AB}\psi_B,
\quad A=1,\ldots,16.
$$

Auxiliary closures:

$$
S=\psi^{\mathsf T}C\psi,
\qquad
\rho=\frac{1}{20}S+\frac{19}{20}S^{1/5},
$$

$$
p=-\frac{19}{25}S^{1/5},
\qquad
V_S=\frac{1}{20}+\frac{19}{100}S^{-4/5}.
$$

## 2. Best numerical method used for all component equations

The best method for this system, as implemented and verified in this repository,
is variable-step variable-order BDF with Newton iterations via the pinned pure-
Rust SUNDIALS/CVODE engine.

Reasoning for this choice:

1. The coupled Einstein-spinor equations are mildly stiff near the transition
   where dilution and self-interaction contributions rebalance.
2. The spinor block is linear in `psi` for fixed `(H,S)` but nonlinear through
   `S(psi)`, which benefits from implicit stability.
3. BDF + Newton gives robust long-interval integration with deterministic
   tolerances and reproducible step histories under fixed binaries and inputs.

Canonical solver settings:

- Interval: `x4 in [-0.2, 1.5]`.
- Output step: `0.01`.
- Relative tolerance: `1e-11`.
- Absolute tolerance: `1e-13`.
- Maximum internal step: `0.002`.

Canonical run summary:

- Samples: `171`.
- Internal solver steps: `1372`.
- RHS evaluations: `1486`.
- Acceleration transition at `x4=-0.138005293303244986`.

## 3. Approximation and error-control method

The approximation strategy is fully controlled, not ad hoc:

1. Integrate the full coupled ODE once with canonical tolerances.
2. Repeat integration with identical settings to enforce byte-level replay.
3. Integrate a refined run with tighter controls (`rtol=1e-12`,
   `atol=1e-14`, `max_step=0.001`).
4. Compare canonical and refined states componentwise.
5. Recompute every derived quantity from raw state output independently.

Independent consistency checks applied to each equation family:

1. Friedmann closure check from the `44` Einstein component.
2. Pressure/acceleration consistency from the spatial Einstein components.
3. Five-point finite-difference residual checks on all 18 ODE components.
4. Condensate power-law consistency:

$$
S(x4)\sim a(x4)^{-7}.
$$

5. Deterministic replay byte-identity for history and summary artifacts.

Canonical maximum relative errors from independent checker:

$$
\varepsilon_S\le 7.44192091691309166\times 10^{-9},
$$

$$
\varepsilon_\rho\le 1.48948308787786630\times 10^{-9},
$$

$$
\varepsilon_{F}\le 1.20354325050525201\times 10^{-9}.
$$

These bounds demonstrate that the approximate numerical solution tracks the
component equations at high precision over the full interval.

## 4. Equation-by-equation numerical treatment

Each equation family is solved as part of the same implicit coupled system:

1. `a` equation:
   treated as a linear transport equation once `H` is known per implicit stage.
2. `H` equation:
   nonlinear scalar equation coupled through `rho(S)` and `p(S)`.
3. `psi_A` equations (`A=1,...,16`):
   linear matrix action in `psi` with nonlinear coefficient `V_S(S(psi))`.

No equation is decoupled or solved by shortcut substitution; all 18 components
are advanced simultaneously in each implicit Newton solve.

## 5. Dark-energy-like and dark-matter-like provenance from component output

The model's possible dark-sector correspondences are fully internal and
conditional:

1. Dust-like component (candidate dark-matter analog):

$$
\rho_{\mathrm{dust}}=\frac{1}{20}S,
\qquad p_{\mathrm{dust}}=0.
$$

2. Negative-pressure component (candidate dark-energy analog):

$$
\rho_{\mathrm{neg}}=\frac{19}{20}S^{1/5},
\qquad p_{\mathrm{neg}}=-\frac{4}{5}\rho_{\mathrm{neg}}.
$$

3. Total equation-of-state trajectory:

$$
w=\frac{p}{\rho},
$$

which evolves from less negative to more negative effective pressure dominance
as `S` dilutes.

4. Fraction diagnostics used by the solver output:

$$
f_{\mathrm{dust}}=\frac{(1/20)S}{\rho},
\qquad
f_{\mathrm{neg}}=\frac{(19/20)S^{1/5}}{\rho}.
$$

Interpretation guardrails:

1. These are model-internal effective-fluid analogies, not direct observational
   identifications.
2. Split signature `(4,4)` is mathematically consistent in this framework but
   is not a standard Lorentzian cosmology.
3. The report does not claim particle-physics identity, perturbation stability,
   or precision-fit cosmology.

## 6. Reproduction commands

### Windows PowerShell

```powershell
.\scripts\verify_phase7_x0_x7_reports.ps1
```

### Git Bash or WSL

```bash
bash ./scripts/verify_phase7_x0_x7_reports.sh
```
