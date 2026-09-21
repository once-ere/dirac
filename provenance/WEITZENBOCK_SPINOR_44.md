# Weitzenböck Spin Connection and Spinor Dark-Sector Dynamics in Signature `(4,4)`

## A standalone exact, numerical, and interpretive provenance report

### Abstract

This report defines a metric-compatible, curvature-free, torsionful
Weitzenböck connection on an explicit curved eight-dimensional manifold of
signature `(4,4)`, lifts its inertial tangent connection to the real
16-component `Spin(4,4)` spinor bundle, substitutes that lift for the
Levi-Civita spin connection, derives the resulting homogeneous field
equations, and solves them numerically with the pinned pure-Rust SUNDIALS
CVODE implementation.

The selected diagonal frame is a Weitzenböck gauge in which the inertial spin
connection is zero. This statement is gauge-dependent; the report gives the
full local-Lorentz gauge family and never identifies zero connection
coefficients with an invariant absence of gravity. Gravity is represented by
torsion. The Hermitian spinor action produces a torsion-trace term, so the
homogeneous Weitzenböck Dirac equation has exactly the same `7 H/2` dilution
term as the previously derived Levi-Civita equation. The teleparallel
gravitational action differs from the Einstein-Hilbert action by an explicit
boundary divergence, and the reduced TEGR equations agree with the reduced
Einstein equations.

The numerical solution contains no scalar quintessence field and no
cosmological constant. A linear spinor-condensate term behaves as a
dust-like homogeneous effective fluid, while a fractional-power
self-interaction behaves as a negative-pressure homogeneous effective fluid.
The calculation establishes those model-internal analogies. It does not
establish that either term is observed dark matter or dark energy, and the
TEGR torsion scalar is not counted as an additional dark component.

The base has split signature, and a constant-time slice has signature
`(4,3)`. This is a mathematical model, not standard one-time cosmology.

## 1. Scope and terminology

The phrase "all possible connections" cannot literally mean every possible
spinor, torsion, dark-matter, or dark-energy theory: infinitely many
nonminimal couplings and potentials can be written. This report instead gives
an exhaustive classification of the connections supported by the implemented
action and ansatz, then separately lists nearby extensions that are not part
of the calculation. This distinction prevents an implemented result from
being confused with speculation.

The connection constructed here is named the **Dirac-Weitzenböck inertial
spin connection**. The name labels this project's explicit specialization of
standard covariant teleparallel geometry; it is not a claim to have invented
the general theory of Weitzenböck connections.

All fields are classical. The spinor components commute. No claim about
Grassmann quantization, a quantum vacuum, particle production, or a Standard
Model identification is made.

## 2. Base geometry, frame, and spinor bundle

Let `M` be an oriented, time-oriented, spin eight-manifold. Use the ordered
coordinates

```text
(x0,x1,x2,x3,t,y1,y2,y3)
```

and tangent metric

$$
\eta_{ab}=\operatorname{diag}(1,1,1,1,-1,-1,-1,-1).
$$

The evolution coordinate is `t`, at zero-based index 4. The seven transverse
indices are

$$
I\in\{0,1,2,3,5,6,7\}.
$$

Choose the cohomogeneity-one metric

$$
ds^2=a(t)^2\left[(dx^0)^2+(dx^1)^2+(dx^2)^2+(dx^3)^2
-(dy^1)^2-(dy^2)^2-(dy^3)^2\right]-dt^2
$$

and the diagonal coframe

$$
e_\mu{}^a=\operatorname{diag}(a,a,a,a,1,a,a,a).
$$

Its inverse is

$$
e_a{}^\mu=\operatorname{diag}
(a^{-1},a^{-1},a^{-1},a^{-1},1,a^{-1},a^{-1},a^{-1}),
$$

and direct multiplication gives

$$
g_{\mu\nu}=e_\mu{}^a\eta_{ab}e_\nu{}^b.
$$

Write

$$
H=\frac{\dot a}{a}.
$$

The real spinor bundle is

$$
\mathcal S=P_{\operatorname{Spin}(4,4)}(M)
\mathbin{\times}_\rho\Delta_{\mathbb R},
$$

where

$$
\Delta_{\mathbb R}=\Delta_+\oplus\Delta_-,
\qquad \dim_{\mathbb R}\Delta_+=\dim_{\mathbb R}\Delta_-=8.
$$

Thus a section `psi` has 16 real components. The two eight-dimensional
summands are the two inequivalent real half-spin representations. An even
spin connection preserves the summands; odd Clifford multiplication
exchanges them.

## 3. Definition of the Weitzenböck connection

For a coframe `e` and a flat inertial tangent connection
`omegaW_mu^a_b`, define

$$
\boxed{
\Gamma^{\rho}_{W\,\mu\nu}
=e_a{}^\rho\left(
\partial_\mu e_\nu{}^a
+\omega^a{}_{W\,\mu b}e_\nu{}^b
\right).}
$$

This ordering follows the vielbein postulate

$$
\partial_\mu e_\nu{}^a
-\Gamma^\rho{}_{W\,\mu\nu}e_\rho{}^a
+\omega^a{}_{W\,\mu b}e_\nu{}^b=0.
$$

The selected diagonal frame is declared to be a proper frame, and the
Weitzenböck gauge is

$$
\boxed{\omega^a{}_{W\,\mu b}=0.}
$$

Therefore

$$
\boxed{
\Gamma^{\rho}_{W\,\mu\nu}
=e_a{}^\rho\partial_\mu e_\nu{}^a.}
$$

The only nonzero coefficients are

$$
\Gamma^I{}_{W\,4I}=H.
$$

There are seven nonzero affine-connection components.

### 3.1 Local-Lorentz gauge family

The zero spin connection is not a gauge-invariant statement. Under

$$
e'^a=\Lambda^a{}_b(x)e^b,
$$

the same geometric connection is represented by

$$
\omega'_W
=\Lambda\omega_W\Lambda^{-1}
-(d\Lambda)\Lambda^{-1}.
$$

Starting from the selected gauge gives

$$
\omega'_W=-(d\Lambda)\Lambda^{-1}.
$$

If `U(x)` is a spin lift of `Lambda(x)`, the spinor connection transforms as

$$
\Omega'_W
=U\Omega_WU^{-1}-(dU)U^{-1}.
$$

The zero representative and every transformed pure-gauge representative are
members of one flat inertial connection family. Calculations that set
`omegaW=0` without also fixing the frame would not be locally Lorentz
covariant; this implementation always records the selected frame.

## 4. Torsion, curvature, and metric compatibility

Use the torsion convention

$$
T^\rho{}_{\mu\nu}
=\Gamma^\rho{}_{W\,\mu\nu}
-\Gamma^\rho{}_{W\,\nu\mu}.
$$

The nonzero components are

$$
T^I{}_{4I}=H,
\qquad
T^I{}_{I4}=-H.
$$

There are 14 nonzero torsion components. Define the trace used below by

$$
\tau_\mu=T^\nu{}_{\mu\nu}.
$$

Then

$$
\boxed{\tau_4=7H,\qquad \tau_I=0.}
$$

Direct substitution verifies

$$
\nabla^W_\mu g_{\nu\rho}=0
$$

for all 512 component choices. The full curvature tensor

$$
R^\rho{}_{W\,\sigma\mu\nu}
=\partial_\mu\Gamma^\rho{}_{W\,\nu\sigma}
-\partial_\nu\Gamma^\rho{}_{W\,\mu\sigma}
+\Gamma^\rho{}_{W\,\mu\lambda}
 \Gamma^\lambda{}_{W\,\nu\sigma}
-\Gamma^\rho{}_{W\,\nu\lambda}
 \Gamma^\lambda{}_{W\,\mu\sigma}
$$

vanishes identically. The connection is therefore flat and torsionful, not
the torsion-free Levi-Civita connection.

## 5. Contortion and relation to Levi-Civita geometry

Define contortion by the unambiguous difference

$$
\boxed{
K^\rho{}_{\mu\nu}
=\Gamma^\rho{}_{W\,\mu\nu}
-\Gamma^\rho{}_{LC\,\mu\nu}.}
$$

Thus

$$
\Gamma_W=\Gamma_{LC}+K.
$$

For every transverse index `I`, the nonzero components are

$$
K^4{}_{II}=-\eta_{II}a\dot a,
\qquad
K^I{}_{I4}=-H.
$$

There are 14 nonzero contortion components. Converting the coordinate
contortion to tangent indices and lifting it to the spin representation gives

$$
\boxed{\Omega_W=\Omega_{LC}+K_{\rm spin}=0}
$$

in the selected gauge. This identity is checked as a full array of eight
real `16 x 16` matrices. It is the precise sense in which the new spin
connection is substituted for the canonical one.

## 6. Torsion scalar and the TEGR boundary identity

Define

$$
\mathbb T=
\frac14 T^\rho{}_{\mu\nu}T_\rho{}^{\mu\nu}
+\frac12 T^\rho{}_{\mu\nu}T^{\nu\mu}{}_\rho
-\tau_\mu\tau^\mu.
$$

For the explicit frame,

$$
\boxed{\mathbb T=42H^2.}
$$

Let

$$
v_\mu=T^\nu{}_{\nu\mu}=-\tau_\mu
$$

and let `e=abs(det(e_mu^a))=a^7` on the positive-scale branch. Define

$$
B=\frac{2}{e}\partial_\mu(ev^\mu).
$$

Independent symbolic contraction gives

$$
R_{LC}=14\dot H+56H^2,
$$

$$
B=14\dot H+98H^2,
$$

and hence

$$
\boxed{R_{LC}=-\mathbb T+B.}
$$

With these sign conventions, the teleparallel gravitational action is

$$
I_g=-\frac{1}{2\kappa_8}\int_M d^8x\,e\,\mathbb T.
$$

It differs from the Einstein-Hilbert action by the integral of `B`, a
boundary term. Under boundary conditions for which that variation vanishes,
the tetrad equation is equivalent to

$$
G^{LC}_{\mu\nu}=\kappa_8\Theta_{\mu\nu}.
$$

This is the teleparallel equivalent of general relativity, or TEGR. The
torsion scalar is the gravitational Lagrangian in a different connection
description. It is not an extra matter density in this model.

## 7. Real gamma matrices and the inertial spin connection

The eight exact real `16 x 16` gamma matrices satisfy

$$
\{\gamma^a,\gamma^b\}=2\eta^{ab}I_{16}.
$$

The curved matrices are

$$
\gamma^\mu=e_a{}^\mu\gamma^a.
$$

For tangent connection coefficients `omegaW_muab`, define

$$
\boxed{
\Omega^W_\mu
=\frac18\omega^W_{\mu ab}[\gamma^a,\gamma^b],
\qquad
D^W_\mu=\partial_\mu+\Omega^W_\mu.}
$$

All ordered pairs `a,b` are summed. The coefficient would be `1/4` if only
`a<b` were summed. In the selected Weitzenböck gauge,

$$
\Omega^W_\mu=0,
\qquad
D^W_\mu=\partial_\mu.
$$

Although its coefficients vanish in this gauge, the connection is not absent:
its transformed representatives are nonzero pure-gauge matrices, and the
affine connection still has nonzero torsion.

## 8. Hermitian Weitzenböck-Dirac equation

Let

$$
C=\gamma_1^+\gamma_2^+\gamma_3^+\gamma_4^+,
\qquad
\bar\psi=\psi^{\mathsf T}C,
\qquad
S=\bar\psi\psi.
$$

The symmetric real classical spinor action is

$$
I_\psi=\int_Md^8x\,e\left[
\frac12\left(
\bar\psi\gamma^\mu D^W_\mu\psi
-(D^W_\mu\bar\psi)\gamma^\mu\psi
\right)-V(S)\right].
$$

Integration by parts in a torsionful geometry produces the trace term

$$
\frac1eD^W_\mu(e\gamma^\mu)=\tau_\mu\gamma^\mu.
$$

The spinor Euler-Lagrange equation is therefore

$$
\boxed{
\gamma^\mu\left(D^W_\mu+\frac12\tau_\mu\right)\psi
-V'(S)\psi=0.}
$$

It would be incorrect to replace the Levi-Civita spin connection by zero in
the already reduced equation and discard the integration-by-parts term. That
operation would not follow from the symmetric action.

For a homogeneous spinor in the selected gauge,

$$
\gamma^\mu\left(D^W_\mu+\frac12\tau_\mu\right)\psi
=\gamma^4\left(\partial_t+\frac72H\right)\psi.
$$

The exact matrix calculation also gives

$$
\gamma^\mu\Omega^{LC}_\mu
=\frac72H\gamma^4.
$$

Thus the homogeneous Hermitian Weitzenböck operator and the homogeneous
Levi-Civita operator agree for this frame and ansatz, even though their
connections, torsion, and curvature do not.

## 9. Matter potential and field equations

Choose

$$
V(S)=mS+\lambda S^q
$$

with

$$
\kappa_8=21,
\qquad
m=\frac1{20},
\qquad
\lambda=\frac{19}{20},
\qquad
q=\frac15.
$$

There is no scalar field and no cosmological constant. The homogeneous
energy density and pressure are

$$
\rho=V(S)=mS+\lambda S^q,
$$

$$
p=SV'(S)-V(S)=(q-1)\lambda S^q.
$$

The complete action used by the reduced model is

$$
\boxed{
I=\int_Md^8x\,e\left[
-\frac{\mathbb T}{2\kappa_8}
+\frac12\left(
\bar\psi\gamma^\mu D^W_\mu\psi
-(D^W_\mu\bar\psi)\gamma^\mu\psi
\right)-V(S)
\right].}
$$

The reduced TEGR equations are

$$
\boxed{21H^2=\kappa_8\rho,}
$$

$$
\boxed{6\dot H+21H^2=-\kappa_8 p.}
$$

Equivalently,

$$
\dot H=-\frac{\kappa_8}{6}(\rho+p).
$$

Multiplying the spinor equation by `-gamma^4` gives

$$
\boxed{
\dot\psi=-\frac72H\psi-V'(S)\gamma^4\psi.}
$$

Together with

$$
\dot a=aH,
$$

these are 18 first-order real equations: one for `a`, one for `H`, and 16
for `psi`.

## 10. Analytic identities used to audit the solution

Because `gamma^4` is skew-adjoint with respect to `C`, the potential-rotation
term cancels from the condensate derivative. Therefore

$$
\dot S=-7HS
$$

and

$$
\boxed{S(a)=a^{-7}}
$$

for the normalization `S(1)=1`.

It follows that

$$
\rho(a)=ma^{-7}+\lambda a^{-7q},
$$

and direct differentiation gives the continuity equation

$$
\dot\rho+7H(\rho+p)=0.
$$

The two effective fractions are

$$
f_{\rm dust}=\frac{mS}{\rho},
\qquad
f_{\rm neg}=\frac{\lambda S^q}{\rho},
\qquad
f_{\rm dust}+f_{\rm neg}=1.
$$

The total equation-of-state parameter is

$$
w=\frac{p}{\rho}.
$$

The acceleration is

$$
\frac{\ddot a}{a}=H^2+\dot H.
$$

Its zero occurs at

$$
a_{\rm tr}
=\left[
\frac{5m}{(2-7q)\lambda}
\right]^{1/[7(1-q)]}
=0.8631436165767085\ldots.
$$

## 11. Numerical method

The state is

$$
y=(a,H,\psi_0,\ldots,\psi_{15})\in\mathbb R^{18}.
$$

Initial data at `t=0` are

$$
a=1,
\qquad H=1,
\qquad \psi_0=1,
\qquad \psi_{15}=\frac12,
$$

with all other spinor components zero. These values give

$$
S=1,
\quad \rho=1,
\quad p=-\frac{19}{25},
\quad w=-\frac{19}{25},
$$

and satisfy both gravitational equations exactly.

The implementation uses CVODE BDF with a dense linear solver. The canonical
configuration is

```text
relative tolerance = 1e-11
absolute tolerance = 1e-13 for every state component
maximum internal step = 0.002
output interval = 0.01
integration interval = [-0.2, 1.5]
```

The solver integrates forward and backward from the same exact initial state.
The two branches are ordered and joined with the initial point included once.
The canonical result has 171 samples, 1,372 internal steps, and 1,486 right-hand
side evaluations.

The Phase 6 application owns this RHS, its state types, and its CVODE setup.
It generates `C` and `gamma^4` directly from the exact fixtures and depends
only on the pinned `cvode_rs` and `sundials_core` crates. It does not call the
Phase 5 Einstein-spinor application. Equality with the Levi-Civita history is
therefore an externally checked result rather than delegated behavior.

A refined run uses relative tolerance `1e-12`, absolute tolerance `1e-14`,
and maximum step `0.001`. It has 2,294 internal steps and 2,422 right-hand-side
evaluations. The maximum normalized state difference from the canonical run
is `6.310776406656671e-10`.

## 12. Numerical results

| Quantity | Earliest `t=-0.2` | Present `t=0` | Final `t=1.5` |
|---|---:|---:|---:|
| `a` | 0.801869547 | 1 | 2.744015737 |
| `H` | 1.236400448 | 1 | 0.480873971 |
| `S` | 4.691092064 | 1 | 0.000853677 |
| `rho` | 1.528686068 | 1 | 0.231239776 |
| `p` | -1.035305172 | -0.76 | -0.184957674 |
| `w` | -0.677251657 | -0.76 | -0.799852330 |
| dust-like fraction | 0.153435429 | 0.05 | 0.000184587 |
| negative-pressure fraction | 0.846564571 | 0.95 | 0.999815413 |
| `tau_4=7H` | 8.654803137 | 7 | 3.366117800 |
| `T=42H^2` | 64.20481486 | 42 | 9.711741913 |

The acceleration changes sign at

$$
t_{\rm tr}=-0.1380052933032450,
\qquad
a_{\rm tr}=0.8631436165767085.
$$

The canonical maximum relative errors are

| Check | Maximum error |
|---|---:|
| condensate dilution | `7.441921424927986e-09` |
| analytic density | `1.4894832079072834e-09` |
| TEGR/Friedmann constraint | `1.203543250505252e-09` |
| teleparallel boundary identity, absolute | `2.842170943040401e-14` |
| homogeneous Dirac equivalence, absolute | `0` |

Independent five-point differentiation gives maximum component ODE RMS
$4.705850657056059\times10^{-4}$ and maximum normalized spatial
gravitational-equation residual $5.702272371471661\times10^{-7}$. These
finite-difference values are looser
than the solver tolerances because they differentiate output sampled only
every `0.01`; they are independent checks, not CVODE's internal error estimate.

The Weitzenböck and Levi-Civita runs have exactly equal serialized values for
all 171 times and all 18 state components. This is an expected consequence of
the proved homogeneous operator and TEGR boundary identities, not evidence
that the two connections are geometrically identical.

## 13. Connections to dark matter

### 13.1 Established within the model: linear term

The linear contribution is

$$
\rho_m=mS=ma^{-7}.
$$

Its pressure is

$$
p_m=S\frac{d(mS)}{dS}-mS=0.
$$

It therefore has the homogeneous equation of state of pressureless matter in
seven expanding transverse dimensions. This is the precise reason for the
label **dust-like**.

### 13.2 What is not established

The calculation does not provide perturbation growth, clustering, halo
profiles, a particle mass spectrum, interactions with visible matter, or a
compactification to three spatial dimensions. Consequently it does not show
that the spinor is observed cold dark matter. The background scaling is a
necessary analogy, not a sufficient identification.

## 14. Connections to dark energy

### 14.1 Established within the model: fractional self-interaction

The nonlinear contribution is

$$
\rho_q=\lambda S^q=\lambda a^{-7q}
$$

with

$$
p_q=(q-1)\rho_q.
$$

For `q=1/5`,

$$
w_q=q-1=-\frac45.
$$

It dilutes more slowly than the linear term, acquires an increasing fractional
share during expansion, and drives positive acceleration after the computed
transition. This is the precise reason for the label **negative-pressure** or
**dark-energy-like**.

### 14.2 What is not established

The model has not been fitted to supernova, baryon-acoustic-oscillation,
cosmic-microwave-background, lensing, or structure-growth data. Its
split-signature base is not the observed `(3,1)` spacetime. It supplies no
proof of stability under inhomogeneous perturbations. It therefore does not
identify the self-interaction with observed dark energy.

## 15. Connections involving torsion

### 15.1 Established: geometric replacement

The torsion scalar replaces the Levi-Civita Ricci scalar in the gravitational
action up to `B`. This is a reformulation of the same gravitational dynamics
under the stated boundary conditions. It does not add an independently
conserved torsion fluid.

### 15.2 Established: spinor dilution through torsion trace

The selected inertial spin connection vanishes, but variation of the
Hermitian spinor action gives `tau_mu/2`. For this ansatz,

$$
\frac12\tau_4=\frac72H,
$$

which exactly replaces the contracted Levi-Civita spin connection in the
homogeneous equation. This is a direct spinor-torsion connection, but it is
kinematic and fixed by the frame rather than a new fitted dark-sector force.

### 15.3 Established: gauge covariance

The zero representative is tied to the diagonal proper frame. A local Lorentz
rotation creates a nonzero pure-gauge inertial spin connection while leaving
the curvature zero and the covariant physics unchanged. A calculation that
compared only connection coefficients across gauges would be physically
meaningless.

### 15.4 Not included: nonminimal torsion couplings

Terms such as

$$
F(S)\mathbb T,
\qquad
G(S)B,
\qquad
T_\mu\bar\psi\gamma^\mu\psi,
$$

or higher torsion invariants would define different theories. They can create
additional effective densities, pressures, energy exchange, or modified
gravity behavior. None is present here. No numerical conclusion in this
report can be transferred to those models without deriving and testing their
new field equations.

### 15.5 Not included: modified teleparallel gravity

Replacing the TEGR term by `f(T)`, `f(T,B)`, scalar-torsion, or
spinor-torsion functions changes the dynamics and can itself mimic dark
energy. Those possibilities are logically related but are not results of this
calculation.

## 16. Complete artifact inventory

The exact connection artifacts are

```text
wolfram/WeitzenbockSpinGeometry.wl
scripts/build_weitzenbock_spin_geometry.py
scripts/verify_weitzenbock_spin_geometry.wls
scripts/check_weitzenbock_spin_geometry.py
scripts/check_weitzenbock_spinor_model.py
artifacts/weitzenbock-spin-geometry/geometry.json
artifacts/weitzenbock-spin-geometry/wolfram-report.json
```

The numerical implementation and outputs are

```text
studies/weitzenbock_spinor_44/Cargo.toml
studies/weitzenbock_spinor_44/src/generated.rs
studies/weitzenbock_spinor_44/src/lib.rs
studies/weitzenbock_spinor_44/src/main.rs
scripts/generate_weitzenbock_spinor_constants.py
scripts/check_weitzenbock_spinor_44.py
artifacts/weitzenbock-spinor-44/history.csv
artifacts/weitzenbock-spinor-44/summary.json
```

The publication and regression artifacts are

```text
notebooks/DiracTriality.nb
provenance/WEITZENBOCK_SPINOR_44.md
provenance/WEITZENBOCK_SPINOR_44.tex
provenance/WEITZENBOCK_SPINOR_44.pdf
tests/test_weitzenbock_spin_geometry.py
tests/test_weitzenbock_spinor_model.py
tests/test_weitzenbock_spinor_44_output.py
```

The exact Weitzenböck geometry SHA-256 is

```text
804f00f31ffa4247fc1e30d8e89df3ea7ddbd7c8d9fe795317bd57155c93774c
```

The Wolfram geometry report SHA-256 is

```text
4faa10f831727e8142c9137f50ebec416eb2286f6adb74148ad318fa1a05b517
```

The numerical history SHA-256 is

```text
c88ed61cafa59ea0d7693da41527c7b4486ded7cc09ac680b4f20f893d42b62a
```

The numerical summary SHA-256 is

```text
d03a90539887702ad6bdbe0ee3a5d783094b052609fc0e4d2b761a12b97fa6c8
```

## 17. Complete reproduction and verification commands

Run these commands from the repository root in PowerShell 7.

```powershell
Set-Location C:\Users\nsh\Developer\code\vscode\dirac

python scripts/build_weitzenbock_spin_geometry.py
python scripts/build_weitzenbock_spin_geometry.py `
  --output build/phase6/geometry-repeat.json

wolframscript -file scripts/verify_weitzenbock_spin_geometry.wls -- `
  artifacts/weitzenbock-spin-geometry/wolfram-report.json
wolframscript -file scripts/verify_weitzenbock_spin_geometry.wls -- `
  build/phase6/wolfram-report-repeat.json

python scripts/check_weitzenbock_spin_geometry.py
python scripts/check_weitzenbock_spinor_model.py

python scripts/generate_weitzenbock_spinor_constants.py
python scripts/generate_weitzenbock_spinor_constants.py `
  --output build/phase6/generated-repeat.rs

cargo fmt -p weitzenbock_spinor_44 -- --check
cargo clippy -p weitzenbock_spinor_44 --all-targets -- -D warnings
cargo test -p weitzenbock_spinor_44

cargo run --release -p weitzenbock_spinor_44 -- `
  --output artifacts/weitzenbock-spinor-44
cargo run --release -p weitzenbock_spinor_44 -- `
  --output build/phase6/weitzenbock-repeat
cargo run --release -p weitzenbock_spinor_44 -- `
  --output build/phase6/weitzenbock-refined `
  --relative-tolerance 1e-12 `
  --absolute-tolerance 1e-14 `
  --maximum-step 0.001

python scripts/check_weitzenbock_spinor_44.py `
  --repeat build/phase6/weitzenbock-repeat `
  --refined build/phase6/weitzenbock-refined

wolframscript -file scripts/build_mathematica_notebook.wls -- `
  notebooks/DiracTriality.nb
wolframscript -file scripts/build_mathematica_notebook.wls -- `
  build/phase6/DiracTriality-repeat.nb
wolframscript -file scripts/verify_mathematica_notebook.wls -- `
  notebooks/DiracTriality.nb

python scripts/build_dissertation_tex.py `
  --strip-heading-numbers `
  --input provenance/WEITZENBOCK_SPINOR_44.md `
  --output provenance/WEITZENBOCK_SPINOR_44.tex
python scripts/build_dissertation_tex.py `
  --strip-heading-numbers `
  --input provenance/WEITZENBOCK_SPINOR_44.md `
  --output build/phase6/WEITZENBOCK_SPINOR_44-repeat.tex

1..3 | ForEach-Object {
  pdflatex -interaction=nonstopmode -halt-on-error `
    -jobname=WEITZENBOCK_SPINOR_44 `
    -output-directory=build/phase6/pdf-a `
    provenance/WEITZENBOCK_SPINOR_44.tex
  pdflatex -interaction=nonstopmode -halt-on-error `
    -jobname=WEITZENBOCK_SPINOR_44 `
    -output-directory=build/phase6/pdf-b `
    build/phase6/WEITZENBOCK_SPINOR_44-repeat.tex
}

python scripts/check_provenance_pdf.py `
  --edition weitzenbock-spinor-44 `
  build/phase6/pdf-a/WEITZENBOCK_SPINOR_44.pdf `
  --repeat build/phase6/pdf-b/WEITZENBOCK_SPINOR_44.pdf

Copy-Item build/phase6/pdf-a/WEITZENBOCK_SPINOR_44.pdf `
  provenance/WEITZENBOCK_SPINOR_44.pdf -Force

python -m unittest discover -s tests -v
.\scripts\verify_phase6_weitzenbock_spinor.ps1
.\scripts\status.ps1
git diff --exit-code
git diff --cached --exit-code
```

The one-command Git Bash gate is

```bash
cd /c/Users/nsh/Developer/code/vscode/dirac
bash ./scripts/verify_phase6_weitzenbock_spinor.sh
```

## 18. Verification coverage

The implemented checks cover all of the following:

- exact metric reconstruction from the frame;
- all nonzero Weitzenböck connection, torsion, and contortion components;
- the complete vielbein postulate and metric compatibility;
- zero Weitzenböck curvature and nonzero torsion;
- the exact torsion scalar and TEGR boundary identity;
- the tangent and spin contortion relations;
- chirality preservation by the inertial spin connection;
- equality of the homogeneous Hermitian Weitzenböck and Levi-Civita Dirac
  operators;
- exact condensate continuity and both reduced gravitational equations;
- exact lapse and scale-factor variations of the reduced action at three
  rational condensates;
- Rust formatting, linting, seven unit tests, and independent CVODE execution;
- every emitted matter, geometry, error, and dark-sector CSV field;
- all 18 ODEs by independent five-point finite differences;
- the spatial gravitational equation by independent finite differences;
- byte-identical canonical replay and tighter-tolerance convergence;
- exact equality of all serialized state values with the Levi-Civita baseline;
- Wolfram symbolic reconstruction;
- headless evaluation of the generated Mathematica notebook;
- deterministic Markdown-to-LaTeX generation and deterministic PDF replay.

## 19. Final scientific boundary

The calculation proves that this explicit flat inertial spin connection,
torsion tensor, contortion, and TEGR action reproduce the stated homogeneous
Levi-Civita Einstein-spinor dynamics. It also proves that the chosen spinor
potential decomposes into dust-like and negative-pressure homogeneous pieces.

It does not prove that nature uses a split-signature eight-manifold, that the
classical commuting spinor is a quantum fermion, that the two pieces are the
observed dark sectors, or that unimplemented nonminimal torsion couplings are
viable. Those are separate physical hypotheses requiring perturbation theory,
stability analysis, dimensional reduction, and confrontation with data.