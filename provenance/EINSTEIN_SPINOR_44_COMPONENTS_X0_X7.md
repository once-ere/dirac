# Signature `(4,4)` Einstein-Spinor Field Equations in Component Form on Coordinates `{x0,...,x7}`

## Complete coordinate-explicit provenance report

### Abstract

This report rewrites the curved `Spin(4,4)` Einstein-spinor model in the exact
coordinate ordering

```text
coordinates = {x0, x1, x2, x3, x4, x5, x6, x7}
```

matching the bridge notebook convention used in `gpt-5.6_bridge.nb`.
The evolution coordinate is `x4`.

The matter field is one commuting real 16-component spinor field
`psi=(psi1,...,psi16)^T`. The model includes neither a scalar quintessence
field nor a cosmological constant. Every Einstein and spinor equation is
presented in component form, including all vanishing off-diagonal components.

## 1. Geometry and index conventions

Tangent-signature matrix:

$$
\eta_{ab}=\operatorname{diag}(1,1,1,1,-1,-1,-1,-1).
$$

Coordinate indices:

$$
\mu,\nu,\rho,\sigma\in\{0,1,2,3,4,5,6,7\},
\qquad I,J\in\{0,1,2,3,5,6,7\}.
$$

Metric ansatz:

$$
g_{\mu\nu}=\operatorname{diag}\bigl(a(x4)^2,a(x4)^2,a(x4)^2,a(x4)^2,-1,
a(x4)^2,a(x4)^2,a(x4)^2\bigr),
$$

$$
H(x4)=\frac{d a/dx4}{a}.
$$

## 2. Nonzero connection and curvature components

Levi-Civita nonzero Christoffel components:

$$
\Gamma^4{}_{II}=\eta_{II}\,a\,\frac{da}{dx4},
\qquad
\Gamma^I{}_{4I}=\Gamma^I{}_{I4}=H.
$$

Einstein tensor components:

$$
G_{44}=21H^2,
$$

$$
G_{II}=-\eta_{II}\,a^2\left(6\frac{dH}{dx4}+21H^2\right),
$$

$$
G_{\mu\nu}=0\quad(\mu\neq\nu).
$$

## 3. Spinor sector and potential

Real 16-component commuting spinor field:

$$
\psi(x4)=\begin{pmatrix}
\psi_1(x4)\\\psi_2(x4)\\\vdots\\\psi_{16}(x4)
\end{pmatrix}.
$$

Invariant bilinear with symmetric split matrix `C`:

$$
S=\psi^{\mathsf T} C\,\psi.
$$

Potential and derivative:

$$
V(S)=\frac{1}{20}S+\frac{19}{20}S^{1/5},
\qquad
V_S=\frac{dV}{dS}=\frac{1}{20}+\frac{19}{100}S^{-4/5}.
$$

## 4. Stress-energy components (all components listed)

Energy density and pressure:

$$
\rho=\frac{1}{20}S+\frac{19}{20}S^{1/5},
\qquad
p=\left(\frac{1}{5}-1\right)\frac{19}{20}S^{1/5}=-\frac{19}{25}S^{1/5}.
$$

Component form:

$$
T_{44}=\rho,
$$

$$
T_{II}=\eta_{II}\,a^2\,p,
$$

$$
T_{\mu\nu}=0\quad(\mu\neq\nu).
$$

## 5. Einstein equations in complete component form

Use

$$
G_{\mu\nu}=\kappa_8 T_{\mu\nu},\qquad \kappa_8=21.
$$

### 5.1 The 36 independent symmetric components

Time-time component:

$$
\boxed{\,21H^2=21\rho\,}\quad\Longleftrightarrow\quad H^2=\rho.
$$

Seven diagonal transverse components (`I\in\{0,1,2,3,5,6,7\}`):

$$
\boxed{\,-\eta_{II}a^2\left(6\frac{dH}{dx4}+21H^2\right)
=21\eta_{II}a^2 p\,}
$$

which reduce to

$$
\boxed{\,6\frac{dH}{dx4}+21H^2=-21p\,}.
$$

Twenty-eight off-diagonal components:

$$
\boxed{\,G_{\mu\nu}=0=21\,T_{\mu\nu}\,\text{ for every }\mu<\nu.\,}
$$

Explicitly,

$$
(\mu,\nu)\in\{(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),(0,7)\},
$$

$$
(\mu,\nu)\in\{(1,2),(1,3),(1,4),(1,5),(1,6),(1,7)\},
$$

$$
(\mu,\nu)\in\{(2,3),(2,4),(2,5),(2,6),(2,7)\},
$$

$$
(\mu,\nu)\in\{(3,4),(3,5),(3,6),(3,7),(4,5),(4,6),(4,7)\},
$$

$$
(\mu,\nu)\in\{(5,6),(5,7),(6,7)\}.
$$

## 6. Spinor field equations in complete component form

Homogeneous Dirac equation:

$$
\frac{d\psi}{dx4}=-\frac{7}{2}H\psi-V_S\gamma^4\psi.
$$

For each component `A=1,...,16`:

$$
\boxed{\,\frac{d\psi_A}{dx4}
=-\frac{7}{2}H\,\psi_A-V_S\sum_{B=1}^{16}(\gamma^4)_{AB}\,\psi_B\,}.
$$

Written one-by-one:

1. $\dfrac{d\psi_1}{dx4}=-\dfrac{7}{2}H\psi_1-V_S\sum_{B=1}^{16}(\gamma^4)_{1B}\psi_B$
2. $\dfrac{d\psi_2}{dx4}=-\dfrac{7}{2}H\psi_2-V_S\sum_{B=1}^{16}(\gamma^4)_{2B}\psi_B$
3. $\dfrac{d\psi_3}{dx4}=-\dfrac{7}{2}H\psi_3-V_S\sum_{B=1}^{16}(\gamma^4)_{3B}\psi_B$
4. $\dfrac{d\psi_4}{dx4}=-\dfrac{7}{2}H\psi_4-V_S\sum_{B=1}^{16}(\gamma^4)_{4B}\psi_B$
5. $\dfrac{d\psi_5}{dx4}=-\dfrac{7}{2}H\psi_5-V_S\sum_{B=1}^{16}(\gamma^4)_{5B}\psi_B$
6. $\dfrac{d\psi_6}{dx4}=-\dfrac{7}{2}H\psi_6-V_S\sum_{B=1}^{16}(\gamma^4)_{6B}\psi_B$
7. $\dfrac{d\psi_7}{dx4}=-\dfrac{7}{2}H\psi_7-V_S\sum_{B=1}^{16}(\gamma^4)_{7B}\psi_B$
8. $\dfrac{d\psi_8}{dx4}=-\dfrac{7}{2}H\psi_8-V_S\sum_{B=1}^{16}(\gamma^4)_{8B}\psi_B$
9. $\dfrac{d\psi_9}{dx4}=-\dfrac{7}{2}H\psi_9-V_S\sum_{B=1}^{16}(\gamma^4)_{9B}\psi_B$
10. $\dfrac{d\psi_{10}}{dx4}=-\dfrac{7}{2}H\psi_{10}-V_S\sum_{B=1}^{16}(\gamma^4)_{10B}\psi_B$
11. $\dfrac{d\psi_{11}}{dx4}=-\dfrac{7}{2}H\psi_{11}-V_S\sum_{B=1}^{16}(\gamma^4)_{11B}\psi_B$
12. $\dfrac{d\psi_{12}}{dx4}=-\dfrac{7}{2}H\psi_{12}-V_S\sum_{B=1}^{16}(\gamma^4)_{12B}\psi_B$
13. $\dfrac{d\psi_{13}}{dx4}=-\dfrac{7}{2}H\psi_{13}-V_S\sum_{B=1}^{16}(\gamma^4)_{13B}\psi_B$
14. $\dfrac{d\psi_{14}}{dx4}=-\dfrac{7}{2}H\psi_{14}-V_S\sum_{B=1}^{16}(\gamma^4)_{14B}\psi_B$
15. $\dfrac{d\psi_{15}}{dx4}=-\dfrac{7}{2}H\psi_{15}-V_S\sum_{B=1}^{16}(\gamma^4)_{15B}\psi_B$
16. $\dfrac{d\psi_{16}}{dx4}=-\dfrac{7}{2}H\psi_{16}-V_S\sum_{B=1}^{16}(\gamma^4)_{16B}\psi_B$

## 7. Reduced autonomous ODE system solved by the study

State vector:

$$
y=(a,H,\psi_1,\ldots,\psi_{16})\in\mathbb R^{18}.
$$

Equations:

$$
\frac{da}{dx4}=aH,
$$

$$
\frac{dH}{dx4}=-\frac{\kappa_8}{6}(\rho+p),
$$

$$
\frac{d\psi_A}{dx4}=-\frac{7}{2}H\psi_A-V_S\sum_{B=1}^{16}(\gamma^4)_{AB}\psi_B,
\quad A=1,\ldots,16.
$$

## 8. Model-internal dark-sector connections from the components

The component equations imply two distinguished effective pieces:

1. Dust-like term from $S/20$ with equation-of-state $w=0$ at the term level.
2. Negative-pressure term from $(19/20)S^{1/5}$ with term-level
   equation-of-state $w=\alpha-1=-4/5$.

Because the equations are exact in this coordinate basis, these statements
follow from component reduction rather than from coordinate relabeling.

## 9. Reproduction commands

### Windows PowerShell

```powershell
.\scripts\verify_phase7_x0_x7_reports.ps1
```

### Git Bash or WSL

```bash
bash ./scripts/verify_phase7_x0_x7_reports.sh
```
