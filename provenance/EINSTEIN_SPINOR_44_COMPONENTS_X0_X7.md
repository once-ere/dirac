# Signature `(4,4)` Einstein-Spinor Field Equations in Component Form on Coordinates `{x0,...,x7}`

## Complete coordinate-explicit provenance report

### Abstract

This report audits and rewrites the curved `Spin(4,4)` Einstein-spinor model in
the coordinate ordering

```text
coordinates = {x0, x1, x2, x3, x4, x5, x6, x7}
```

The expression occurs verbatim in the external `gpt-5.6_bridge.nb` reference
notebook. Its full path and audited SHA-256 are frozen in the machine-readable
evidence file.
Only the coordinate names and ordering are adopted. The reference notebook's
different frame, metric, and bridge connection are not imported into this
model.

The matter field is one commuting real 16-component spinor field
`psi=(psi1,...,psi16)^T`. There is no separate quintessence scalar and no
cosmological constant. All dark-sector-like behavior comes from the nonlinear
spinor potential. This report first states the covariant field theory and then
lists every independent Einstein equation and all 16 spinor equations after
the homogeneous ansatz used by the numerical study. It does not claim that the
homogeneous list is the unrestricted eight-coordinate PDE system.

## 1. Scope, coordinates, and signature

The authoritative machine-readable audit is
`refinement/phase7-x0-x7/evidence.json`. It independently checks seven exact
component identities, four action-and-Einstein identities, seven solver-source
claims, and 22 numerical-output claims.

Coordinate and tangent indices are

$$
\mu,\nu,\rho,\sigma,a,b\in\{0,1,2,3,4,5,6,7\}.
$$

The proper evolution coordinate is `x4`; a dot means `d/dx4`. The transverse
index set is

$$
I,J\in\{0,1,2,3,5,6,7\}.
$$

Tangent-signature matrix:

$$
\eta_{ab}=\operatorname{diag}(1,1,1,1,-1,-1,-1,-1).
$$

The homogeneous coframe, inverse frame, and metric are

$$
e_\mu{}^a=\operatorname{diag}(a,a,a,a,1,a,a,a),
$$

$$
e_a{}^\mu=\operatorname{diag}(a^{-1},a^{-1},a^{-1},a^{-1},1,
a^{-1},a^{-1},a^{-1}),
$$

$$
g_{\mu\nu}=\operatorname{diag}\bigl(a(x4)^2,a(x4)^2,a(x4)^2,a(x4)^2,-1,
-a(x4)^2,-a(x4)^2,-a(x4)^2\bigr).
$$

$$
H=\frac{\dot a}{a}.
$$

Thus a constant-`x4` slice has signature `(4,3)`, not a positive-definite
seven-space. This is a split-signature mathematical cosmology, not an ordinary
Lorentzian one-time cosmology.

## 2. Covariant field theory before symmetry reduction

The real commuting spinor is a section of the rank-16 real bundle associated
to `Spin(4,4)`. With

$$
D_\mu\psi=\partial_\mu\psi+
\frac18\omega_{\mu ab}[\gamma^a,\gamma^b]\psi,
\qquad \bar\psi=\psi^{\mathsf T}C,
$$

the action is

$$
I[g,\psi]=\int d^8x\sqrt{|g|}\left[
\frac{R}{2\kappa_8}
+\frac12\left(\bar\psi\gamma^\mu D_\mu\psi
-(D_\mu\bar\psi)\gamma^\mu\psi\right)-V(S)\right],
$$

where `S=bar(psi) psi`. There is no scalar field and no cosmological-constant
term. Variation gives the covariant equations

$$
G_{\mu\nu}=\kappa_8T_{\mu\nu},
\qquad
(\gamma^\mu D_\mu-V_S)\psi=0,
$$

with

$$
\begin{aligned}
T_{\mu\nu}={}&-\frac14\bigl[
\bar\psi\gamma_\mu D_\nu\psi+
\bar\psi\gamma_\nu D_\mu\psi\\
&-(D_\mu\bar\psi)\gamma_\nu\psi
-(D_\nu\bar\psi)\gamma_\mu\psi\bigr]
+g_{\mu\nu}\mathcal L_\psi.
\end{aligned}
$$

These are the unrestricted PDEs. Sections 4 through 7 impose
`psi=psi(x4)` and the metric of Section 1; only that reduction is integrated.

## 3. Exact spinor components, bilinear, and potential

Write the mathematical components one-based as

$$
\psi=(\psi_1,\ldots,\psi_{16})^{\mathsf T}.
$$

The implementation and CSV are zero-based:

$$
\boxed{\psi_A\ \text{in this report}=\texttt{psi}(A-1)
\ \text{in code and CSV}.}
$$

The canonical time generator from `cl44-seed.json` is exactly

$$
\gamma^4=\begin{pmatrix}0&I_8\\-I_8&0\end{pmatrix},
\qquad (\gamma^4)^2=-I_{16}.
$$

The symmetric bilinear matrix obeys

$$
C^{\mathsf T}=C,
\qquad C^2=I_{16},
\qquad (\gamma^4)^{\mathsf T}C+C\gamma^4=0,
$$

and has eigenvalue signature `(8,8)`. Its condensate is fully expanded as

$$
\boxed{\begin{aligned}
S=2(&\psi_1\psi_{16}+\psi_2\psi_{15}
-\psi_3\psi_{14}-\psi_4\psi_{13}\\
&+\psi_5\psi_{12}+\psi_6\psi_{11}
-\psi_7\psi_{10}-\psi_8\psi_9).
\end{aligned}}
$$

The implemented real branch is the positive-condensate cone `S>0`. The
potential and its derivative are

$$
V(S)=\frac1{20}S+\frac{19}{20}S^{1/5},
\qquad
U(S):=V_S=\frac1{20}+\frac{19}{100}S^{-4/5}.
$$

The derivative `U(S)` diverges as `S` approaches zero from above. The solver
therefore rejects `S<=0`; the canonical finite interval remains strictly in
`S>0`.

## 4. Homogeneous connection, Einstein tensor, and stress tensor

The 21 nonzero Levi-Civita coefficients are

$$
\begin{aligned}
&\Gamma^4{}_{00}=\Gamma^4{}_{11}=\Gamma^4{}_{22}
=\Gamma^4{}_{33}=a\dot a,\\
&\Gamma^4{}_{55}=\Gamma^4{}_{66}=\Gamma^4{}_{77}=-a\dot a,\\
&\Gamma^I{}_{4I}=\Gamma^I{}_{I4}=H
\quad (I=0,1,2,3,5,6,7).
\end{aligned}
$$

Define

$$
Q=6\dot H+21H^2.
$$

The nonzero Einstein-tensor components are

$$
G_{00}=G_{11}=G_{22}=G_{33}=-a^2Q,
\qquad G_{44}=21H^2,
$$

$$
G_{55}=G_{66}=G_{77}=a^2Q.
$$

All off-diagonal `G_mu nu` vanish under this ansatz. On shell,

$$
\rho=V(S)=\frac1{20}S+\frac{19}{20}S^{1/5},
$$

$$
p=SV_S-V=-\frac{19}{25}S^{1/5}.
$$

Consequently,

$$
T_{00}=T_{11}=T_{22}=T_{33}=a^2p,
\qquad T_{44}=\rho,
$$

$$
T_{55}=T_{66}=T_{77}=-a^2p,
$$

and all off-diagonal stress components vanish. These formulas, including every
sign, are independently reconstructed with exact rational arithmetic by
`scripts/check_einstein_spinor_model.py`.

## 5. All 36 independent homogeneous Einstein equations

Use

$$
G_{\mu\nu}=\kappa_8 T_{\mu\nu},\qquad \kappa_8=21.
$$

The eight diagonal equations are

$$
\begin{aligned}
E_{00}:&\quad -a^2Q=21a^2p,\\
E_{11}:&\quad -a^2Q=21a^2p,\\
E_{22}:&\quad -a^2Q=21a^2p,\\
E_{33}:&\quad -a^2Q=21a^2p,\\
E_{44}:&\quad 21H^2=21\rho,\\
E_{55}:&\quad a^2Q=-21a^2p,\\
E_{66}:&\quad a^2Q=-21a^2p,\\
E_{77}:&\quad a^2Q=-21a^2p.
\end{aligned}
$$

For `a>0`, these reduce to the two scalar relations

$$
\boxed{H^2=\rho},
\qquad
\boxed{6\dot H+21H^2=-21p}.
$$

Define `E_mu nu=G_mu nu-21 T_mu nu`. The 28 independent off-diagonal
equations are each zero:

$$
\begin{aligned}
&E_{01}=E_{02}=E_{03}=E_{04}=0,\\
&E_{05}=E_{06}=E_{07}=0,\\
&E_{12}=E_{13}=E_{14}=E_{15}=0,\\
&E_{16}=E_{17}=0,\\
&E_{23}=E_{24}=E_{25}=E_{26}=E_{27}=0,\\
&E_{34}=E_{35}=E_{36}=E_{37}=0,\\
&E_{45}=E_{46}=E_{47}=0,\\
&E_{56}=E_{57}=E_{67}=0.
\end{aligned}
$$

The reflected equations `E_nu mu=0` follow from symmetry. This is the full
36-component symmetric Einstein system after the homogeneous ansatz, not the
general component form for an arbitrary eight-dimensional metric and spinor.

## 6. Spinor field equations in complete component form

Homogeneous Dirac equation:

$$
\dot\psi=-\frac72H\psi-U\gamma^4\psi.
$$

Using the exact `gamma^4` above, the first eight scalar equations are

$$
\begin{aligned}
\dot\psi_1&=-\frac72H\psi_1-U\psi_9,&
\dot\psi_2&=-\frac72H\psi_2-U\psi_{10},\\
\dot\psi_3&=-\frac72H\psi_3-U\psi_{11},&
\dot\psi_4&=-\frac72H\psi_4-U\psi_{12},\\
\dot\psi_5&=-\frac72H\psi_5-U\psi_{13},&
\dot\psi_6&=-\frac72H\psi_6-U\psi_{14},\\
\dot\psi_7&=-\frac72H\psi_7-U\psi_{15},&
\dot\psi_8&=-\frac72H\psi_8-U\psi_{16}.
\end{aligned}
$$

The remaining eight are

$$
\begin{aligned}
\dot\psi_9&=-\frac72H\psi_9+U\psi_1,&
\dot\psi_{10}&=-\frac72H\psi_{10}+U\psi_2,\\
\dot\psi_{11}&=-\frac72H\psi_{11}+U\psi_3,&
\dot\psi_{12}&=-\frac72H\psi_{12}+U\psi_4,\\
\dot\psi_{13}&=-\frac72H\psi_{13}+U\psi_5,&
\dot\psi_{14}&=-\frac72H\psi_{14}+U\psi_6,\\
\dot\psi_{15}&=-\frac72H\psi_{15}+U\psi_7,&
\dot\psi_{16}&=-\frac72H\psi_{16}+U\psi_8.
\end{aligned}
$$

There are no hidden matrix sums in these equations. Differentiating the exact
condensate and using
`(gamma4)^T C+C gamma4=0` cancels every `U` term:

$$
\dot S=-7HS.
$$

Together with `S(0)=1` and `a(0)=1`, this gives the exact background identity

$$
\boxed{S=a^{-7}}.
$$

## 7. Reduced autonomous ODE system solved by the study

The state vector and the remaining two equations are

$$
y=(a,H,\psi_1,\ldots,\psi_{16})\in\mathbb R^{18}.
$$

$$
\dot a=aH,
\qquad
\dot H=-\frac{21}{6}(\rho+p).
$$

Together with the 16 explicit equations in Section 6, these form the complete
implemented 18-state right-hand side. The Friedmann equation `H^2=rho` is an
initial constraint and an independently monitored numerical invariant, not a
nineteenth evolution equation.

The reference data are imposed at `x4=0`, not at the first CSV row:

$$
a(0)=1,
\qquad H(0)=1,
\qquad \psi_1(0)=1,
\qquad \psi_{16}(0)=\frac12,
$$

with every other spinor component zero. Therefore

$$
S(0)=1,
\qquad \rho(0)=1,
\qquad p(0)=-\frac{19}{25},
\qquad H(0)^2=\rho(0).
$$

CVODE integrates one branch backward from `x4=0` to `-0.2` and another
forward from `0` to `1.5`. The backward samples are reversed, the duplicate
reference sample is removed, and the resulting CSV has 171 ordered samples at
spacing `0.01`.

## 8. Exhaustive dark-sector classification within this action and ansatz

The word “all” is bounded here. The implemented potential contains exactly two
monomials, so there are exactly two homogeneous effective-fluid contributions
within this action and ansatz:

1. Linear term:

$$
\rho_{\rm d}=\frac1{20}S=\frac1{20}a^{-7},
\qquad p_{\rm d}=0,
\qquad w_{\rm d}=0.
$$

It is dust-like at homogeneous background level and is therefore a candidate
dark-matter analogy only.

2. Fractional self-interaction:

$$
\rho_{\rm n}=\frac{19}{20}S^{1/5}
=\frac{19}{20}a^{-7/5},
\qquad p_{\rm n}=-\frac45\rho_{\rm n},
\qquad w_{\rm n}=-\frac45.
$$

It is a negative-pressure, dark-energy-like homogeneous component. For seven
transverse dimensions,

$$
\frac{\ddot a}{a}=H^2+\dot H
=-\frac52\rho-\frac72p,
$$

so acceleration requires

$$
w< -\frac57.
$$

The fractional term satisfies this inequality. For the mixture, the analytic
transition scale is

$$
a_*=\left[
\frac{5(1/20)}{(2-7/5)(19/20)}
\right]^{1/(7(4/5))}
=0.8631436165767085\ldots,
$$

and the canonical interpolation gives
`x4=-0.13800529330324499...`.

These statements do not establish clustering, perturbative stability,
compactification to a one-time Lorentzian theory, particle identity, or an
observational fit. Infinitely many other potentials and nonminimal couplings
are possible and are outside this exhaustive classification of the implemented
two-term model.

## 9. Verification evidence and reproduction

The exact component verifier checks the signed-permutation structures of
`gamma4` and `C`, `(gamma4)^2=-I`, `C^T=C`, `C^2=I`, and skew-adjointness. The
evidence builder additionally runs the exact action/Einstein checker and all 22
canonical numerical checks. Its canonical SHA-256 is
`58373d6aeea90807a3f064f395b8367502ff3a280050a5c8823c9e0cc0b2eb0b`.

### Windows PowerShell

```powershell
python refinement\phase7-x0-x7\verify_component_claims.py
python refinement\phase7-x0-x7\build_evidence.py
.\scripts\verify_phase7_x0_x7_reports.ps1
```

### Git Bash or WSL

```bash
python.exe refinement/phase7-x0-x7/verify_component_claims.py
python.exe refinement/phase7-x0-x7/build_evidence.py
bash ./scripts/verify_phase7_x0_x7_reports.sh
```
