# Numerical and Approximate Solution Methods for the Signature `(4,4)` Einstein-Spinor Components on `{x0,...,x7}`

## Complete solver-method provenance and dark-sector interpretation report

### Abstract

This report verifies the numerical and approximate methods for the 18-equation
homogeneous reduction of the Einstein-spinor model written in

```text
coordinates = {x0, x1, x2, x3, x4, x5, x6, x7}
```

with evolution variable `x4`. The external bridge notebook supplies only these
coordinate names and their ordering; its metric and connection are not used.
The selected production method is the pinned safe-Rust SUNDIALS 7.8.0 CVODE
BDF implementation. A separate exact reduction to one background quadrature
and eight spinor rotations supplies analytic structure and asymptotic
approximations. No comparison study establishes BDF as globally optimal.

## 1. Exact initial-value problem solved

State vector:

$$
y(x4)=(a,H,\psi_1,\ldots,\psi_{16})\in\mathbb R^{18}.
$$

The report uses one-based spinor labels. They map to zero-based code and CSV
columns by `psi_A = psi(A-1)`. Define

$$
U=\frac1{20}+\frac{19}{100}S^{-4/5}.
$$

The geometry equations are

$$
\dot a=aH,
\qquad
\dot H=-\frac{21}{6}(\rho+p).
$$

For each `j=1,...,8`, the two spinor equations are exactly

$$
\dot\psi_j=-\frac72H\psi_j-U\psi_{j+8},
\qquad
\dot\psi_{j+8}=-\frac72H\psi_{j+8}+U\psi_j.
$$

This represents all 16 scalar equations; they are listed individually in the
companion component report. The closures are

$$
S=\psi^{\mathsf T}C\psi,
\qquad
\rho=\frac{1}{20}S+\frac{19}{20}S^{1/5},
$$

$$
p=-\frac{19}{25}S^{1/5},
\qquad H^2=\rho.
$$

The reference state is imposed at `x4=0`:

$$
a=1,
\quad H=1,
\quad \psi_1=1,
\quad \psi_{16}=\frac12,
\quad \psi_A=0\ \text{otherwise}.
$$

CVODE integrates independently from this state backward to `-0.2` and forward
to `1.5`; the backward branch is reversed before both branches are joined.

## 2. Selected production method and exact solver configuration

The implemented production method is variable-step, variable-order BDF in the
safe-Rust port of SUNDIALS CVODE 7.8.0. The solver submodule commit is frozen
in the machine-readable evidence file.

Source inspection and executable evidence establish this configuration:

1. `CVodeCreate(CV_BDF)` selects BDF.
2. CVODE starts at order one and permits orders one through five.
3. `CVodeInit` installs the default Newton nonlinear solver, with at most three
   nonlinear corrector iterations per attempt in the pinned implementation.
4. The application attaches an 18-by-18 dense matrix and dense direct linear
   solver.
5. No user Jacobian is supplied, so the internal dense difference-quotient
   Jacobian is used.
6. A direct dense solve needs no iterative preconditioner; none is configured.

Canonical solver settings:

- Interval: `x4 in [-0.2, 1.5]`.
- Output step: `0.01`.
- Relative tolerance: `1e-11`.
- Absolute tolerance: `1e-13`.
- Maximum internal step: `0.002`.
- Maximum allowed steps per branch: `1,000,000`.

Canonical run summary:

- Samples: `171`.
- Internal solver steps: `1372`.
- RHS evaluations: `1486`.
- Acceleration transition at `x4=-0.138005293303244986`.

BDF is a defensible robust choice for the nonlinear, potentially rapidly
rotating spinor system, but this repository has not benchmarked Rosenbrock,
DIRK, Adams, or symplectic alternatives. Therefore “selected method” is the
verified claim; “globally best method” is not.

## 3. Exact reduction and approximate analytic solution

Skew-adjointness of `gamma4` with respect to `C` gives

$$
\dot S=-7HS,
\qquad S(0)=1,
\qquad \boxed{S=a^{-7}}.
$$

The expanding background therefore reduces exactly to

$$
\rho(a)=\frac1{20}a^{-7}+\frac{19}{20}a^{-7/5},
\qquad H(a)=+\sqrt{\rho(a)},
$$

and one scalar quadrature:

$$
x4-x4_0=\int_{a_0}^{a}
\frac{d\tilde a}{\tilde a\sqrt{
(1/20)\tilde a^{-7}+(19/20)\tilde a^{-7/5}}}.
$$

For the spinor, define `chi=a^(7/2) psi` and

$$
	heta(x4)=\int_0^{x4}U(S(s))\,ds.
$$

Then

$$
\dot\chi=-U\gamma^4\chi,
\qquad
\chi(x4)=\left(\cos\theta\,I_{16}
-\sin\theta\,\gamma^4\right)\chi(0).
$$

Thus every pair `j,j+8` has the explicit reconstruction

$$
\begin{aligned}
\psi_j&=a^{-7/2}\left(
\cos\theta\,\psi_j(0)-\sin\theta\,\psi_{j+8}(0)\right),\\
\psi_{j+8}&=a^{-7/2}\left(
\sin\theta\,\psi_j(0)+\cos\theta\,\psi_{j+8}(0)\right).
\end{aligned}
$$

This reduces the approximate solution problem to quadrature for `a` and
`theta`. It also supplies an independent structural check on all 16 numerical
components.

Two useful single-term asymptotics are:

1. Linear-term dominance, with `m=1/20`:

$$
a(x4)^{7/2}\simeq a_r^{7/2}
+\frac72\sqrt{m}\,(x4-x4_r).
$$

2. Fractional-term dominance, with `lambda=19/20`:

$$
a(x4)^{7/10}\simeq a_r^{7/10}
+\frac7{10}\sqrt{\lambda}\,(x4-x4_r).
$$

The late expression corresponds to `a proportional to x4^(10/7)` after an
appropriate origin shift and is accelerating. These are regime-specific
approximations; the canonical output integrates the full two-term system.

## 4. Numerical approximation and error control

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

For nonzero expected value `q_ref`, define

$$
\operatorname{rel}(q,q_{\rm ref})=
\frac{|q-q_{\rm ref}|}{\max(|q_{\rm ref}|,10^{-300})}.
$$

The three invariant metrics are explicitly

$$
\varepsilon_S=\max\operatorname{rel}(S,a^{-7}),
$$

$$
\varepsilon_\rho=\max\operatorname{rel}
\left(\rho,\frac1{20}a^{-7}+\frac{19}{20}a^{-7/5}\right),
$$

$$
\varepsilon_F=\max\operatorname{rel}(H^2,\rho).
$$

The canonical run records

$$
\varepsilon_S\le 7.44192091691309166\times 10^{-9},
$$

$$
\varepsilon_\rho\le 1.48948308787786630\times 10^{-9},
$$

$$
\varepsilon_{F}\le 1.20354325050525201\times 10^{-9}.
$$

Independent recomputation from the decimal CSV gives, respectively,

```text
7.441921424927986e-09
1.4894832079072834e-09
1.203543250505252e-09
```

The tiny difference in the first two values is output-decimal roundoff. These
are invariant and constraint errors, not residuals of all 18 ODEs.

For the ODE test, the checker differentiates the 171-point output with the
five-point centered stencil and compares it with an independently implemented
right-hand side. The largest component RMS residual is

$$
4.705850657056059\times10^{-4},
$$

below the declared `1e-3` acceptance bound. The largest normalized spatial
Einstein finite-difference residual is

$$
5.702272371471661\times10^{-7},
$$

below `1e-6`. Finite-difference truncation at output spacing `0.01` dominates
these residuals, so they must not be reported as `1e-9` equation accuracy.

## 5. Equation-by-equation numerical treatment

Each equation family is solved as part of the same implicit coupled system:

1. `a` equation:
   the nonlinear stage equation includes the product `a H`; it is advanced in
   the same Newton solve as every other component.
2. `H` equation:
   nonlinear scalar equation coupled through `rho(S)` and `p(S)`.
3. Eight spinor pairs `(psi_j,psi_(j+8))`:
   each has the exact two-component rotation/dilution form in Section 1, while
   all pairs remain nonlinearly coupled through the shared condensate `S`.

No equation is decoupled or solved by shortcut substitution; all 18 components
are advanced simultaneously in each implicit Newton solve. The canonical
initial state leaves six spinor pairs identically zero, but their equations are
still present and checked. Only the `(1,9)` and `(8,16)` pairs become nonzero.

## 6. Dark-energy-like and dark-matter-like provenance

Within the implemented potential there are exactly two homogeneous background
correspondences:

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
3. Dust-like background dilution does not establish dark-matter clustering.
4. Negative background pressure does not establish perturbative stability or
   an observational dark-energy fit.
5. No compactification, particle-physics identity, quantum theory, or
   precision-fit cosmology is supplied.

Other spinor potentials, nonminimal curvature terms, torsion couplings, and
inhomogeneous modes are mathematically possible but were not implemented.
Accordingly, this is exhaustive only for the selected two-term potential and
homogeneous ansatz.

## 7. Reproduction and machine-readable evidence

`refinement/phase7-x0-x7/evidence.json` records the exact component pairings,
source hashes, solver configuration, four exact model checks, 22 numerical
checks, and dark-sector scope. It is regenerated byte-identically by the Phase
7 gate.

### Windows PowerShell

```powershell
python refinement\phase7-x0-x7\build_evidence.py
.\scripts\verify_phase7_x0_x7_reports.ps1
```

### Git Bash or WSL

```bash
python.exe refinement/phase7-x0-x7/build_evidence.py
bash ./scripts/verify_phase7_x0_x7_reports.sh
```
