# Coupled Einstein-Spinor Dynamics in Curved Signature `(4,4)`

## A standalone numerical and analytic provenance report for one real rank-16 spinor bundle

### Abstract

This document defines and approximately solves a coupled Einstein-spinor model
on an explicit curved 8-dimensional pseudo-Riemannian manifold of signature
`(4,4)`. The matter field is one commuting classical real 16-component
`Spin(4,4)` spinor, locally decomposed into the two inequivalent real
8-component half-spin modules. There is no quintessence scalar and no
cosmological-constant term. A nonlinear spinor potential supplies both a
rapidly diluting dust-like component and a slowly diluting negative-pressure
component.

The metric, vielbein, Christoffel symbols, and canonical Levi-Civita spin
connection are derived explicitly. A symmetric nondegenerate split bilinear
`C` defines the local Spin-invariant condensate `S=psi^T C psi`. The action,
Dirac equation, stress tensor, and 8-dimensional Einstein equations are stated
with all conventions. The homogeneous system is integrated with the pinned
pure-Rust SUNDIALS CVODE implementation. Independent checks recompute every
emitted thermodynamic quantity, both Einstein equations, all 18 differential
equations by five-point finite differences, the analytic condensate and
density laws, the acceleration transition, source hashes, and byte-identical
replay.

This is a split-signature mathematical model, not standard one-time
cosmology. Its constant-time slices have signature `(4,3)`. Terms are called
"dust-like" and "negative-pressure" rather than dark matter and dark energy
unless a comparison is explicitly qualified. The calculation does not prove
causal stability, quantum consistency, compactification, observational
viability, or a microscopic particle interpretation.

## 1. Base geometry and the spinor bundle

Let `(M,g)` be an oriented, time-oriented, spin 8-manifold with metric
signature `(4,4)`. Use coordinates

```text
(x0,x1,x2,x3,t,y1,y2,y3)
```

and constant tangent metric

$$
\eta_{ab}=\operatorname{diag}(1,1,1,1,-1,-1,-1,-1).
$$

The selected curved metric is

$$
 ds^2=a(t)^2\left[(dx^0)^2+(dx^1)^2+(dx^2)^2+(dx^3)^2
 -(dy^1)^2-(dy^2)^2-(dy^3)^2\right]-dt^2.
$$

The diagonal vielbein and inverse are

$$
e_\mu{}^a=\operatorname{diag}(a,a,a,a,1,a,a,a),
$$

$$
e_a{}^\mu=\operatorname{diag}(a^{-1},a^{-1},a^{-1},a^{-1},1,
 a^{-1},a^{-1},a^{-1}),
$$

and satisfy

$$
g_{\mu\nu}=e_\mu{}^a\eta_{ab}e_\nu{}^b.
$$

The principal pseudo-orthonormal frame bundle is lifted to a principal
`Spin(4,4)` bundle. The associated real rank-16 spinor bundle is

$$
\mathcal S=P_{\mathrm{Spin}(4,4)}(M)
\mathbin{\times}_\rho\Delta_{\mathbb R},
$$

with

$$
\Delta_{\mathbb R}=\Delta_+\oplus\Delta_-,
\qquad \dim\Delta_+=\dim\Delta_-=8.
$$

A field is

$$
\psi(t,x)\in\Gamma(\mathcal S),
\qquad
\psi=\psi_+\oplus\psi_-.
$$

The spin connection is even and preserves the two half-spin subbundles. The
Dirac operator includes odd Clifford multiplication and can couple the two
chiral components.

## 2. Canonical spin connection used by the model

The Levi-Civita Christoffel symbols are

$$
\Gamma^\rho{}_{\mu\nu}
=\frac12g^{\rho\sigma}
\left(\partial_\mu g_{\nu\sigma}
+\partial_\nu g_{\mu\sigma}
-\partial_\sigma g_{\mu\nu}\right).
$$

The vielbein postulate

$$
\partial_\mu e_\nu{}^a
-\Gamma^\rho{}_{\mu\nu}e_\rho{}^a
+\omega_\mu{}^a{}_b e_\nu{}^b=0
$$

has the explicit solution

$$
\omega_\mu{}^a{}_b
=e_b{}^\nu\left(
\Gamma^\rho{}_{\mu\nu}e_\rho{}^a
-\partial_\mu e_\nu{}^a\right).
$$

With `H=adot/a` and transverse indices
`I={0,1,2,3,5,6,7}`, the nonzero components are

$$
\Gamma^4{}_{ii}=\eta_{ii}a\dot a,
\qquad
\Gamma^i{}_{4i}=\Gamma^i{}_{i4}=H,
$$

$$
\omega_{ii4}=\eta_{ii}\dot a,
\qquad
\omega_{i4i}=-\eta_{ii}\dot a.
$$

There are 21 nonzero Christoffel entries and 14 nonzero lowered spin-connection
entries.

The spinor derivative is

$$
D_\mu\psi
=\partial_\mu\psi
+\frac18\omega_{\mu ab}[\gamma^a,\gamma^b]\psi,
$$

where all ordered values of `a,b` are summed. If only `a<b` is summed, the
equivalent coefficient is `1/4`.

For a homogeneous spinor,

$$
\gamma^\mu D_\mu\psi
=\gamma^4\left(\partial_t+\frac72H\right)\psi.
$$

This `7H/2` term is computed exactly in independent Python and Wolfram
implementations.

## 3. Exact real gamma matrices and invariant adjoint

Use

$$
P=\begin{pmatrix}0&1\\1&0\end{pmatrix},
\quad
N=\begin{pmatrix}0&1\\-1&0\end{pmatrix},
\quad
G=\begin{pmatrix}1&0\\0&-1\end{pmatrix}.
$$

For `k=1,2,3,4`, define

$$
\gamma_k^+=G^{\otimes(k-1)}\otimes P\otimes I_2^{\otimes(4-k)},
$$

$$
\gamma_k^-=G^{\otimes(k-1)}\otimes N\otimes I_2^{\otimes(4-k)}.
$$

They are real integral 16 by 16 matrices satisfying

$$
\{\gamma^a,\gamma^b\}=2\eta^{ab}I_{16}.
$$

The evolution-time matrix is the first negative generator,

$$
\gamma^4=\gamma_1^-,
\qquad (\gamma^4)^2=-I_{16}.
$$

Define

$$
C=\gamma_1^+\gamma_2^+\gamma_3^+\gamma_4^+.
$$

Then

$$
C^{\mathsf T}=C,
\qquad C^2=I,
\qquad
(\gamma^a)^{\mathsf T}C=-C\gamma^a.
$$

The eigenvalue signature of `C` is `(8,8)`. The real adjoint and condensate
are

$$
\bar\psi=\psi^{\mathsf T}C,
\qquad
S=\bar\psi\psi.
$$

This bilinear is locally `Spin(4,4)` invariant and indefinite.

## 4. Classical-field assumption

The field in this numerical model is a commuting classical real spinor. This
assumption is essential. For a single Grassmann-odd spinor, anticommuting
components contracted with the symmetric matrix `C` would give

$$
\psi^{\mathsf T}C\psi=0.
$$

A nonzero nonlinear potential `V(S)` would then require independent dual
fields, multiple fermionic species, or another bilinear. This study instead
uses a commuting effective classical order parameter, analogous in modeling
role to a classical condensate but transforming in the real spin bundle.
Nothing here quantizes the field or identifies a fundamental fermion.

## 5. Action without a scalar quintessence field or cosmological constant

Choose the total action

$$
I[g,\psi]
=\int_M d^8x\sqrt{|g|}
\left[\frac{1}{2\kappa_8}R+\mathcal L_\psi\right],
$$

with

$$
\mathcal L_\psi
=\frac12\left(
\bar\psi\gamma^\mu D_\mu\psi
-(D_\mu\bar\psi)\gamma^\mu\psi
\right)-V(S).
$$

No cosmological constant and no scalar field occur. The potential depends only
on the invariant spinor condensate.

Varying the independent classical spinor variables gives

$$
\boxed{(\gamma^\mu D_\mu-V_S)\psi=0,}
$$

where

$$
V_S=\frac{dV}{dS}.
$$

For the homogeneous frame,

$$
\gamma^4\left(\dot\psi+\frac72H\psi\right)-V_S\psi=0.
$$

Multiplying by `-(gamma^4)` gives the implemented real first-order equation

$$
\boxed{
\dot\psi=-\frac72H\psi-V_S\gamma^4\psi.}
$$

The sign is fixed by `(gamma^4)^2=-I`.

## 6. Stress tensor and homogeneous reduction

The symmetric spinor stress tensor is

$$
T_{\mu\nu}
=-\frac14\left[
\bar\psi\gamma_\mu D_\nu\psi
+\bar\psi\gamma_\nu D_\mu\psi
-(D_\mu\bar\psi)\gamma_\nu\psi
-(D_\nu\bar\psi)\gamma_\mu\psi
\right]+g_{\mu\nu}\mathcal L_\psi.
$$

This overall sign follows from
`T_{mu nu}=-(2/sqrt(|g|)) delta I_m/delta g^{mu nu}` together with the action
and Einstein-equation convention used here. With the opposite definition of
the metric variation, both the definition of `T` and the Einstein equation
would have to change together.

For the homogeneous on-shell ansatz it takes the isotropic transverse form

$$
T_{tt}=\rho,
\qquad
T_{AB}=p\,g_{AB},
$$

with

$$
\boxed{\rho=V(S),}
$$

$$
\boxed{p=S V_S-V.}
$$

The gamma-four term is skew-adjoint for `C`, so it drops out of the condensate
derivative:

$$
\dot S
=\dot\psi^{\mathsf T}C\psi+\psi^{\mathsf T}C\dot\psi
=-7HS.
$$

Consequently

$$
\boxed{S=S_0a^{-7}.}
$$

This is also the continuity equation consequence

$$
\dot\rho+7H(\rho+p)=0.
$$

## 7. Signature `(4,4)` Einstein equations

Use

$$
G_{\mu\nu}=\kappa_8 T_{\mu\nu}.
$$

For the flat transverse metric with seven scaled directions, direct curvature
calculation gives

$$
\boxed{G_{tt}=21H^2,}
$$

$$
\boxed{G_{AB}=-(6\dot H+21H^2)g_{AB}.}
$$

Therefore the two independent homogeneous Einstein equations are

$$
21H^2=\kappa_8\rho,
$$

$$
6\dot H+21H^2=-\kappa_8p.
$$

Choose dimensionless normalization

$$
\kappa_8=21.
$$

Then

$$
\boxed{H^2=\rho,}
$$

$$
\boxed{\dot H=-\frac72(\rho+p).}
$$

The acceleration equation follows:

$$
\frac{\ddot a}{a}=H^2+\dot H
=-\frac52\rho-\frac72p.
$$

For a single component with `p=w rho`, expansion accelerates when

$$
\boxed{w<-\frac57.}
$$

The threshold differs from the familiar four-dimensional value `-1/3`
because seven directions share the scale factor.

## 8. Chosen nonlinear spinor potential

Select

$$
\boxed{
V(S)=\frac1{20}S+\frac{19}{20}S^{1/5}.}
$$

The first term is mass-like. The second is a nonlinear self-interaction. They
are both generated by the same rank-16 spinor field; no extra matter fluid is
added. Because `C` has split signature while the fractional power is evaluated
as a real principal power, this model is defined on the positive-condensate
cone `S>0`. The selected initial data have `S=1`, and the exact identity
`S=a^-7` preserves that domain for every positive scale factor.

The derivative is

$$
V_S=\frac1{20}+\frac{19}{100}S^{-4/5}.
$$

Energy density and pressure are

$$
\rho=\frac1{20}S+\frac{19}{20}S^{1/5},
$$

$$
p=-\frac{19}{25}S^{1/5}.
$$

Since `S=a^-7` for the selected normalization,

$$
\boxed{
\rho(a)=\frac1{20}a^{-7}+\frac{19}{20}a^{-7/5},}
$$

$$
\boxed{
p(a)=-\frac{19}{25}a^{-7/5}.}
$$

The first contribution has `w=0` and scales as `a^-7`, the dust law in seven
scaled dimensions. The second has

$$
w=\frac15-1=-\frac45
$$

and scales as `a^-7/5`. Since `-4/5<-5/7`, it can drive acceleration in this
model.

## 9. Complete monomial connection map

For a general positive monomial spinor interaction

$$
V_q(S)=\lambda_q S^q,
$$

the homogeneous formulas give

$$
\rho_q=\lambda_qS^q,
\qquad
p_q=(q-1)\rho_q,
\qquad
w_q=q-1,
$$

and

$$
\rho_q\propto a^{-7q}.
$$

This classifies every component in the monomial family:

- `q=1` gives `w=0` and `rho proportional to a^-7`: a pressureless
  dust-like component.
- `q=8/7` gives `w=1/7` and `rho proportional to a^-8`: a radiation-like
  component in seven scaled dimensions.
- `q=2/7` gives `w=-5/7` and `rho proportional to a^-2`: the acceleration
  boundary.
- `0<q<2/7` gives `-1<w<-5/7` and dilution slower than `a^-2`: a
  nonphantom accelerating component.
- `q=0` gives `w=-1` and constant density: a cosmological-constant-like
  limiting term.
- `q<0` gives `w<-1` and density that grows during expansion: phantom-like
  behavior singular as `S` approaches zero.

The selected model uses `q=1` and `q=1/5`. It intentionally contains no
`q=0` constant term, so it does not hide a cosmological constant inside the
potential.

For a sum

$$
V(S)=\sum_q\lambda_qS^q,
$$

the total equation of state is the density-weighted mean

$$
w(S)=\frac{\sum_q(q-1)\lambda_qS^q}
{\sum_q\lambda_qS^q}.
$$

This is the complete relation between condensate monomials and homogeneous
fluid analogies within the stated potential family. It is not a classification
of every possible nonlocal, derivative, anisotropic, quantum, or multi-spinor
model; that unrestricted set is infinite.

## 10. Acceleration transition

For the selected two-term potential,

$$
\frac{\ddot a}{a}
=-\frac18S+\frac{57}{200}S^{1/5}.
$$

The exact transition condition is

$$
S_*^{4/5}=\frac{57}{25}.
$$

Since `S=a^-7`,

$$
\boxed{
a_*=\left(\frac{25}{57}\right)^{5/28}
=0.8631436165767085\ldots.}
$$

The reported transition time is obtained by linear interpolation in `a`
between neighboring output samples separated by `Delta t=0.01`:

$$
t_*=-0.138005293303245\ldots.
$$

The scale factor is analytic; the time carries output-grid interpolation
error and should not be interpreted as having 17 digits of physical accuracy.

## 11. Numerical initial-value problem

The real state has 18 components:

$$
y=(a,H,\psi_0,\ldots,\psi_{15}).
$$

The ODE system is

$$
\dot a=aH,
$$

$$
\dot H=-\frac72(\rho+p),
$$

$$
\dot\psi=-\frac72H\psi-V_S\gamma^4\psi.
$$

Initial data at `t=0` are

$$
a(0)=1,
\qquad H(0)=1,
$$

$$
\psi_0(0)=1,
\qquad \psi_{15}(0)=\frac12,
$$

with all other spinor components zero. The exact matrix `C` pairs components
0 and 15 symmetrically, so

$$
S(0)=1.
$$

Then

$$
\rho(0)=1,
\qquad H(0)^2=\rho(0),
$$

and the Friedmann constraint is satisfied initially.

CVODE integrates two branches from the same initial state:

```text
backward interval = [0,-0.2]
forward interval  = [0, 1.5]
output step        = 0.01
relative tolerance = 1e-11
absolute tolerance = 1e-13 for every component
maximum step       = 0.002
method             = BDF
nonlinear method   = Newton
linear solver      = dense
```

The branches are joined with the initial sample included once, producing 171
ordered rows.

## 12. Canonical numerical results

The canonical release run reports

```text
sample_count=171
solver_steps=1372
rhs_evaluations=1486
acceleration_transition_time=-0.138005293303245
acceleration_transition_scale_factor=0.8631436165767085
maximum_condensate_relative_error=7.441921424927986e-9
maximum_density_relative_error=1.4894832079072834e-9
maximum_friedmann_relative_error=1.203543250505252e-9
maximum_component_ODE_RMS=4.705850657056059e-4
maximum_spatial_Einstein_finite_difference_error=5.702272371471661e-7
```

The finite-difference ODE residual is computed from the 0.01 output grid, not
from CVODE's internal smaller steps. A five-point stencil differentiates all
18 emitted state columns. Its truncation error is therefore much larger than
the analytic-identity errors, but it distinguishes the implemented spinor
rotation sign from the opposite sign by orders of magnitude.

A separate convergence run uses relative tolerance `1e-12`, absolute
tolerance `1e-14`, and maximum internal step `0.001`. It takes 2,294 steps and
2,422 right-hand-side evaluations. Across all 171 output times and all 18
state components, its maximum scaled difference from the canonical run is
`6.310776406656671e-10`. Its maximum condensate, density, and Friedmann errors
are respectively `1.6415774988196702e-9`, `3.2855796418252515e-10`, and
`3.31034411227924e-10`, each smaller than in the canonical run.

Canonical hashes are

```text
geometry.json=6b5eab6b001d69c5face7b179af8a27e3cfe254cf80bc740cdcb7a2855fcdf67
wolfram-report.json=f81a902f7efc2a36bef1bacdbc4682a278f4907383970a8383f565efd602dc38
generated.rs=fa3aba370c1039f17b83fe86a65d75e45be6448aa7bd025dc0db6d0e79e61f60
history.csv=9553b36f201ef43a92c7de3fe2f46457a592e55285e6220d8aa7af6e36a26f9c
summary.json=6b15d084178d01aaed37b84b4bcf8f5246a6941bbe8366ad9c0c3db099eea0f1
```

At the earliest sample `t=-0.2`:

```text
a=0.8018695
H=1.2364004
w=-0.6772517
dust_like_fraction=0.1534354
negative_pressure_fraction=0.8465646
acceleration=-0.1981471
```

At the normalized present sample `t=0`:

```text
a=1
H=1
w=-0.76
dust_like_fraction=0.05
negative_pressure_fraction=0.95
acceleration=0.16
```

At the latest sample `t=1.5`:

```text
H=0.4808740
w=-0.7998523
dust_like_fraction=0.0001846
negative_pressure_fraction=0.9998154
acceleration=0.0692524
```

The two fractions sum to one by construction. They describe contributions to
the effective homogeneous spinor energy density, not independently detected
particle populations.

## 13. Independent verification

The release does not accept the reduced equations or the solver's stored
summary as proof. The exact Python model checker performs four rational checks:

- reconstruction of the initial positive condensate from the actual `C` and
  spinor components;
- direct evaluation of the on-shell Lagrangian and every component of the
  corrected action stress tensor using the exact 16 by 16 gamma matrices;
- reconstruction of the full Einstein tensor from second-order metric jets at
  two independent rational choices of `a`, `H`, and `Hdot`; and
- all 64 components of `G_mu nu=21 T_mu nu` at the normalized initial state,
  including vanishing off-diagonal components.

The trajectory checker reloads `history.csv` and performs 22 base checks:

- file, schema, signature, state-dimension, source-hash, and parameter checks;
- exact output headers, sample count, time grid, finite values, and initial data;
- recomputation of `S`, `rho`, `p`, `w`, both component fractions, and
  acceleration from all 16 spinor columns;
- positivity of `a` and `S` throughout the implemented fractional-power domain;
- analytic comparisons with `S=a^-7` and the corresponding density;
- direct Friedmann residual `H^2-rho`;
- five-point finite differences for `a`, `H`, and all 16 spinor components;
- an independently differentiated spatial Einstein residual
  `6 Hdot+21 H^2+21 p`;
- exact acceleration-transition scale and interpolated transition time;
- canonical SHA-256 values, solver statistics, and verdict.

The release command supplies both optional evidence sets, increasing that
total to 24: byte-identical replay of the canonical run and componentwise
comparison with the tighter convergence run. If either path is omitted, its
check is reported as not performed rather than vacuously true.

The Rust crate also contains four tests for exact matrix adjoint properties,
the present Einstein constraints, condensate derivative, rejection of
nonpositive scale factors or condensates, CVODE smoke integration, analytic
errors, and acceleration.

## 14. What may be connected to dark matter

The mass-like term

$$
\rho_{\mathrm{dust}}=\frac1{20}S
$$

has zero pressure and dilutes as `a^-7`, exactly like homogeneous pressureless
matter in seven scaled dimensions. This is a precise background-level
connection to a dark-matter-like fluid.

It is not enough to call the component dark matter physically. No galactic
clustering, perturbation growth, sound speed, lensing, halo structure,
standard-model coupling, relic abundance, or compactification to four
dimensions is calculated. The label "dust-like" is therefore used in emitted
artifacts.

## 15. What may be connected to dark energy

The nonlinear term

$$
\rho_{\mathrm{neg}}=\frac{19}{20}S^{1/5}
$$

has `w=-4/5`, satisfies the 8D acceleration condition, and eventually
dominates because it dilutes more slowly than the mass term. This is a precise
background-level connection to a nonphantom dark-energy-like component.

It is not a cosmological constant: its density changes with `a`, and the
selected action contains no constant term. It is not scalar quintessence:
the dynamical section is a rank-16 real spinor, and its covariant derivative
contains the Spin connection.

It is also not an observational dark-energy result. The base has split
signature, there is no compactification map to observed `(3,1)` spacetime,
and no likelihood analysis is performed.

## 16. Other possible connections and excluded claims

Within local polynomial or monomial potentials, changing powers and
coefficients can produce mixtures analogous to dust, radiation, accelerating
nonphantom energy, a constant term, or phantom behavior. Derivative couplings,
curvature couplings such as `R S`, torsion, nonmetricity, multiple spinors,
and anisotropic condensates would produce additional possibilities, but none
is silently added here.

The present result does not establish:

1. a physical theory with four observed time directions;
2. a ghost-free or hyperbolic perturbation system;
3. stability against inhomogeneous spinor or metric perturbations;
4. dimensional reduction to `(3,1)` spacetime;
5. a quantum theory of a Grassmann-odd fermion;
6. dark-matter clustering or a dark-energy observational fit;
7. uniqueness of the potential or initial data;
8. a particle-generation mechanism;
9. compatibility with standard energy conditions;
10. microscopic derivation from split octonions.

These are separate research questions. The numerical solution establishes a
well-specified classical homogeneous background and nothing broader.

## 17. Complete Windows commands

Open PowerShell and run every command below:

```powershell
Set-Location C:\Users\nsh\Developer\code\vscode\dirac
git submodule update --init --recursive

python scripts\backup_files.py `
  studies\einstein_spinor_44\src\generated.rs `
  artifacts\einstein-spinor-44\history.csv `
  artifacts\einstein-spinor-44\summary.json `
  provenance\EINSTEIN_SPINOR_44.tex `
  provenance\EINSTEIN_SPINOR_44.pdf

New-Item -ItemType Directory -Force -Path `
  build\phase5, `
  build\phase5\einstein-spinor-repeat, `
  build\phase5\einstein-spinor-refined, `
  build\phase5\gravity-pdf-a, `
  build\phase5\gravity-pdf-b | Out-Null

python scripts\build_curved_spin_geometry.py
wolframscript -file scripts\verify_curved_spin_geometry.wls -- `
  artifacts\curved-spin-geometry\wolfram-report.json
python scripts\check_curved_spin_geometry.py
python scripts\check_einstein_spinor_model.py

python scripts\generate_einstein_spinor_constants.py
python scripts\generate_einstein_spinor_constants.py `
  --output build\phase5\einstein-spinor-generated-repeat.rs

cargo fmt -p einstein_spinor_44 -- --check
cargo clippy -p einstein_spinor_44 --all-targets -- -D warnings
cargo test -p einstein_spinor_44
python -m unittest discover -s tests -v

cargo run --release -p einstein_spinor_44 -- `
  --output artifacts\einstein-spinor-44
cargo run --release -p einstein_spinor_44 -- `
  --output build\phase5\einstein-spinor-repeat
cargo run --release -p einstein_spinor_44 -- `
  --output build\phase5\einstein-spinor-refined `
  --relative-tolerance 1e-12 `
  --absolute-tolerance 1e-14 `
  --maximum-step 0.001

python scripts\check_einstein_spinor_44.py `
  --repeat build\phase5\einstein-spinor-repeat `
  --refined build\phase5\einstein-spinor-refined

python scripts\build_dissertation_tex.py --strip-heading-numbers `
  --input provenance\EINSTEIN_SPINOR_44.md `
  --output provenance\EINSTEIN_SPINOR_44.tex
python scripts\build_dissertation_tex.py --strip-heading-numbers `
  --input provenance\EINSTEIN_SPINOR_44.md `
  --output build\phase5\EINSTEIN_SPINOR_44-repeat.tex

pdflatex -interaction=nonstopmode -halt-on-error `
  -jobname=EINSTEIN_SPINOR_44 `
  -output-directory=build\phase5\gravity-pdf-a `
  provenance\EINSTEIN_SPINOR_44.tex
pdflatex -interaction=nonstopmode -halt-on-error `
  -jobname=EINSTEIN_SPINOR_44 `
  -output-directory=build\phase5\gravity-pdf-a `
  provenance\EINSTEIN_SPINOR_44.tex
pdflatex -interaction=nonstopmode -halt-on-error `
  -jobname=EINSTEIN_SPINOR_44 `
  -output-directory=build\phase5\gravity-pdf-a `
  provenance\EINSTEIN_SPINOR_44.tex

pdflatex -interaction=nonstopmode -halt-on-error `
  -jobname=EINSTEIN_SPINOR_44 `
  -output-directory=build\phase5\gravity-pdf-b `
  build\phase5\EINSTEIN_SPINOR_44-repeat.tex
pdflatex -interaction=nonstopmode -halt-on-error `
  -jobname=EINSTEIN_SPINOR_44 `
  -output-directory=build\phase5\gravity-pdf-b `
  build\phase5\EINSTEIN_SPINOR_44-repeat.tex
pdflatex -interaction=nonstopmode -halt-on-error `
  -jobname=EINSTEIN_SPINOR_44 `
  -output-directory=build\phase5\gravity-pdf-b `
  build\phase5\EINSTEIN_SPINOR_44-repeat.tex

python scripts\check_provenance_pdf.py --edition einstein-spinor-44 `
  build\phase5\gravity-pdf-a\EINSTEIN_SPINOR_44.pdf `
  --repeat build\phase5\gravity-pdf-b\EINSTEIN_SPINOR_44.pdf

$generatedA = (Get-FileHash `
  studies\einstein_spinor_44\src\generated.rs `
  -Algorithm SHA256).Hash
$generatedB = (Get-FileHash `
  build\phase5\einstein-spinor-generated-repeat.rs `
  -Algorithm SHA256).Hash
if ($generatedA -ne $generatedB) { throw "Generated constants changed bytes" }
$historyA = (Get-FileHash `
  artifacts\einstein-spinor-44\history.csv `
  -Algorithm SHA256).Hash
$historyB = (Get-FileHash `
  build\phase5\einstein-spinor-repeat\history.csv `
  -Algorithm SHA256).Hash
if ($historyA -ne $historyB) { throw "Einstein-spinor CSV changed bytes" }
$summaryA = (Get-FileHash `
  artifacts\einstein-spinor-44\summary.json `
  -Algorithm SHA256).Hash
$summaryB = (Get-FileHash `
  build\phase5\einstein-spinor-repeat\summary.json `
  -Algorithm SHA256).Hash
if ($summaryA -ne $summaryB) { throw "Einstein-spinor summary changed bytes" }

$warningPattern = '^!|LaTeX Warning|Package .* Warning|'
$warningPattern += 'Overfull|Underfull|Undefined control sequence'
$issues = Select-String `
  -Path build\phase5\gravity-pdf-a\EINSTEIN_SPINOR_44.log, `
        build\phase5\gravity-pdf-b\EINSTEIN_SPINOR_44.log `
  -Pattern $warningPattern
if ($issues) { throw "Einstein-spinor LaTeX warnings remain" }

Copy-Item build\phase5\gravity-pdf-a\EINSTEIN_SPINOR_44.pdf `
  provenance\EINSTEIN_SPINOR_44.pdf -Force

.\scripts\verify_phase5_curved_spin_gravity.ps1
```

The final line must be

```text
phase5_curved_spin_gravity_verification=OK
```

## 18. Complete Git Bash or WSL commands

Run every command below:

```bash
if [[ -d /c/Users/nsh/Developer/code/vscode/dirac ]]; then
  cd /c/Users/nsh/Developer/code/vscode/dirac
else
  cd /mnt/c/Users/nsh/Developer/code/vscode/dirac
fi
git submodule update --init --recursive
source ./scripts/resolve_wolframscript.sh
python_command="$(resolve_windows_command python.exe)"
cargo_command="$(resolve_windows_command cargo.exe)"
pdflatex_command="$(resolve_miktex_pdflatex)"

"$python_command" scripts/backup_files.py \
  studies/einstein_spinor_44/src/generated.rs \
  artifacts/einstein-spinor-44/history.csv \
  artifacts/einstein-spinor-44/summary.json \
  provenance/EINSTEIN_SPINOR_44.tex \
  provenance/EINSTEIN_SPINOR_44.pdf

rm -rf build/phase5/einstein-spinor-repeat \
  build/phase5/einstein-spinor-refined \
  build/phase5/gravity-pdf-a build/phase5/gravity-pdf-b
mkdir -p build/phase5/einstein-spinor-repeat \
  build/phase5/einstein-spinor-refined \
  build/phase5/gravity-pdf-a build/phase5/gravity-pdf-b

"$python_command" scripts/build_curved_spin_geometry.py
wolframscript_command="$(resolve_wolframscript)"
"$wolframscript_command" -file scripts/verify_curved_spin_geometry.wls -- \
  artifacts/curved-spin-geometry/wolfram-report.json
"$python_command" scripts/check_curved_spin_geometry.py
"$python_command" scripts/check_einstein_spinor_model.py

"$python_command" scripts/generate_einstein_spinor_constants.py
"$python_command" scripts/generate_einstein_spinor_constants.py \
  --output build/phase5/einstein-spinor-generated-repeat.rs

"$cargo_command" fmt -p einstein_spinor_44 -- --check
"$cargo_command" clippy -p einstein_spinor_44 --all-targets -- -D warnings
"$cargo_command" test -p einstein_spinor_44
"$python_command" -m unittest discover -s tests -v

"$cargo_command" run --release -p einstein_spinor_44 -- \
  --output artifacts/einstein-spinor-44
"$cargo_command" run --release -p einstein_spinor_44 -- \
  --output build/phase5/einstein-spinor-repeat
"$cargo_command" run --release -p einstein_spinor_44 -- \
  --output build/phase5/einstein-spinor-refined \
  --relative-tolerance 1e-12 \
  --absolute-tolerance 1e-14 \
  --maximum-step 0.001
"$python_command" scripts/check_einstein_spinor_44.py \
  --repeat build/phase5/einstein-spinor-repeat \
  --refined build/phase5/einstein-spinor-refined

"$python_command" scripts/build_dissertation_tex.py \
  --strip-heading-numbers \
  --input provenance/EINSTEIN_SPINOR_44.md \
  --output provenance/EINSTEIN_SPINOR_44.tex
"$python_command" scripts/build_dissertation_tex.py \
  --strip-heading-numbers \
  --input provenance/EINSTEIN_SPINOR_44.md \
  --output build/phase5/EINSTEIN_SPINOR_44-repeat.tex

for pass in 1 2 3; do
  "$pdflatex_command" -interaction=nonstopmode -halt-on-error \
    -jobname=EINSTEIN_SPINOR_44 \
    -output-directory=build/phase5/gravity-pdf-a \
    provenance/EINSTEIN_SPINOR_44.tex
  "$pdflatex_command" -interaction=nonstopmode -halt-on-error \
    -jobname=EINSTEIN_SPINOR_44 \
    -output-directory=build/phase5/gravity-pdf-b \
    build/phase5/EINSTEIN_SPINOR_44-repeat.tex
done

"$python_command" scripts/check_provenance_pdf.py \
  --edition einstein-spinor-44 \
  build/phase5/gravity-pdf-a/EINSTEIN_SPINOR_44.pdf \
  --repeat build/phase5/gravity-pdf-b/EINSTEIN_SPINOR_44.pdf

generated_a="$(sha256sum \
  studies/einstein_spinor_44/src/generated.rs | cut -d' ' -f1)"
generated_b="$(sha256sum \
  build/phase5/einstein-spinor-generated-repeat.rs | cut -d' ' -f1)"
test "$generated_a" = "$generated_b"
history_a="$(sha256sum \
  artifacts/einstein-spinor-44/history.csv | cut -d' ' -f1)"
history_b="$(sha256sum \
  build/phase5/einstein-spinor-repeat/history.csv | cut -d' ' -f1)"
test "$history_a" = "$history_b"
summary_a="$(sha256sum \
  artifacts/einstein-spinor-44/summary.json | cut -d' ' -f1)"
summary_b="$(sha256sum \
  build/phase5/einstein-spinor-repeat/summary.json | cut -d' ' -f1)"
test "$summary_a" = "$summary_b"
warning_pattern='^!|LaTeX Warning|Package .* Warning|'
warning_pattern+='Overfull|Underfull|Undefined control sequence'
! grep -Ei "$warning_pattern" \
  build/phase5/gravity-pdf-a/EINSTEIN_SPINOR_44.log \
  build/phase5/gravity-pdf-b/EINSTEIN_SPINOR_44.log
cp build/phase5/gravity-pdf-a/EINSTEIN_SPINOR_44.pdf \
  provenance/EINSTEIN_SPINOR_44.pdf

bash ./scripts/verify_phase5_curved_spin_gravity.sh
```

## 19. Files and ownership boundaries

```text
studies/einstein_spinor_44/Cargo.toml
studies/einstein_spinor_44/src/lib.rs
studies/einstein_spinor_44/src/main.rs
studies/einstein_spinor_44/src/generated.rs
scripts/generate_einstein_spinor_constants.py
scripts/check_einstein_spinor_model.py
scripts/check_einstein_spinor_44.py
artifacts/einstein-spinor-44/history.csv
artifacts/einstein-spinor-44/summary.json
provenance/EINSTEIN_SPINOR_44.md
provenance/EINSTEIN_SPINOR_44.tex
provenance/EINSTEIN_SPINOR_44.pdf
```

The solver submodule is read-only. The new equations, generated matrices,
output format, checks, and documentation belong to the application repository.

## 20. Conclusion

A new signature `(4,4)` Einstein system has been defined without a scalar
quintessence field and without a cosmological constant. Its only source is a
commuting classical real rank-16 `Spin(4,4)` spinor with a two-term invariant
potential. The mass-like term is exactly dust-like at the homogeneous level;
the nonlinear term has `w=-4/5` and produces acceleration after the exact scale
`a_*=(25/57)^(5/28)`.

The solution is approximate numerically but tightly checked: analytic
condensate and density laws, both Einstein equations, all 18 ODE components,
source hashes, solver statistics, canonical output hashes, and deterministic
replay all pass. The result is a reproducible split-signature background model,
not an observational identification of dark matter or dark energy.
