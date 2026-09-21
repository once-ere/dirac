# Curved Spin(4,4) Bundle, Vielbein, and Canonical Spin Connection

## A standalone exact construction on a curved split-signature eight-manifold

### Abstract

This document defines one real rank-16 spinor bundle over an explicit curved
8-dimensional pseudo-Riemannian base of signature `(4,4)`. It distinguishes
coordinate indices from orthonormal tangent-space indices, distinguishes the
curved metric `g` from the constant tangent metric `eta`, constructs a diagonal
vielbein, derives the Levi-Civita Christoffel symbols and spin connection from
the vielbein postulate, defines eight exact real 16 by 16 gamma matrices, and
constructs the spinor covariant derivative. Every formula is evaluated for the
chosen curved metric. Independent Wolfram and Python implementations verify
the complete vielbein postulate, connection antisymmetry, the spinor bilinear,
chirality preservation, and the contracted homogeneous Dirac operator.

The construction is mathematical. A metric with four positive and four
negative directions is not standard one-time physical spacetime. The chosen
coordinate `t` is one timelike evolution coordinate, while each constant-`t`
slice still has signature `(4,3)`. No claim of observational viability,
causal stability, or uniqueness is made.

## 1. Geometric data and index conventions

Let `M` be an oriented, time-oriented, smooth 8-manifold equipped with a
pseudo-Riemannian metric `g` of signature `(4,4)`. Assume that `M` admits a
spin structure. Equivalently for the present purpose, the oriented
pseudo-orthonormal frame bundle has a lift through the double covering

$$
\operatorname{Spin}(4,4)\longrightarrow SO_0(4,4).
$$

Greek indices `mu,nu,rho,...` label coordinate components on `M`. Latin
indices `a,b,c,...` label components in a local pseudo-orthonormal tangent
frame. Both range from 0 through 7. The ordered coordinates and tangent labels
are

```text
(x0,x1,x2,x3,t,y1,y2,y3).
```

The zero-based index of `t` is 4. The remaining seven indices are

```text
I = {0,1,2,3,5,6,7}.
```

The constant tangent-space metric is

$$
\eta_{ab}=\operatorname{diag}(1,1,1,1,-1,-1,-1,-1).
$$

It is flat and independent of position. Calling it a `(4,4)` Minkowski metric
is common in this project, although "split pseudo-Euclidean metric" is less
likely to be confused with the usual `(3,1)` Minkowski metric.

The curved coordinate metric is a field

$$
g=g_{\mu\nu}(x)\,dx^\mu\otimes dx^\nu.
$$

Its entries can vary from point to point and its Levi-Civita curvature need
not vanish. The two metrics do not live on competing spaces: `eta` gives the
matrix of `g` in an orthonormal tangent frame, while `g_mu_nu` gives the same
bilinear form in a coordinate basis.

## 2. The spinor fiber bundle

Let

$$
\pi_{SO}:P_{SO_0(4,4)}(M)\longrightarrow M
$$

be the principal bundle of oriented pseudo-orthonormal frames. A spin structure
is a principal bundle

$$
\pi_{\mathrm{Spin}}:P_{\mathrm{Spin}(4,4)}(M)\longrightarrow M
$$

together with a fiberwise two-to-one map to the frame bundle that intertwines
the right group actions.

Let `Delta_R` be the real 16-dimensional irreducible module of the full
Clifford algebra `Cl(4,4)`. Restriction to the even Clifford algebra and to
`Spin(4,4)` decomposes it as

$$
\Delta_{\mathbb R}=\Delta_+\oplus\Delta_-,
\qquad \dim_{\mathbb R}\Delta_+=\dim_{\mathbb R}\Delta_-=8.
$$

The requested fiber bundle is the associated real spinor bundle

$$
\boxed{
\mathcal S=P_{\mathrm{Spin}(4,4)}(M)
\mathbin{\times}_{\rho}\Delta_{\mathbb R}
\longrightarrow M.}
$$

A spinor field is a smooth section

$$
\psi\in\Gamma(\mathcal S).
$$

The chirality operator splits the bundle into two rank-8 subbundles,

$$
\mathcal S=\mathcal S_+\oplus\mathcal S_-,
$$

so locally

$$
\psi=\psi_+\oplus\psi_-.
$$

These are the two inequivalent real half-spin fields called type 1 and type 2
in the task statement. They are not two unrelated bundles in this
construction; they are the two chiral summands of one rank-16 real spinor
bundle. The spin connection is even and therefore preserves each summand.
Odd Clifford multiplication exchanges them.

A global spinor bundle requires the spin-structure assumption. A local
vielbein always exists on a sufficiently small coordinate neighborhood, but a
single global vielbein need not exist on an arbitrary spin manifold.

## 3. Vielbein terminology and the metric relation

A vielbein is a local pseudo-orthonormal frame field. The word "vierbein"
literally refers to four dimensions. In eight dimensions the specific word is
"achtbein"; "vielbein" is the standard dimension-independent term. It is
therefore imprecise to call an 8-dimensional frame an "8-dimensional
vierbein."

Write the coframe as

$$
e^a=e_\mu{}^a dx^\mu
$$

and its inverse as

$$
e_a=e_a{}^\mu\partial_\mu.
$$

They obey

$$
e_a{}^\mu e_\mu{}^b=\delta_a{}^b,
\qquad
e_\mu{}^a e_a{}^\nu=\delta_\mu{}^\nu.
$$

The defining metric relation is

$$
\boxed{g_{\mu\nu}=e_\mu{}^a\eta_{ab}e_\nu{}^b.}
$$

In matrix notation this is

$$
g=e\eta e^{\mathsf T}.
$$

The vielbein is not unique. If `Lambda(x)` is a local `SO(4,4)` transformation,
then

$$
e'_\mu{}^a=e_\mu{}^b\Lambda_b{}^a
$$

gives the same metric. Thus a "canonical frame" means a frame selected by an
explicit gauge convention for a specified metric, not a frame uniquely
forced by `g` on every manifold.

## 4. The explicit curved `(4,4)` metric

To make every requested component computable, choose a positive smooth scale
factor `a(t)` and the cohomogeneity-one metric

$$
\boxed{
 ds^2=a(t)^2\left[(dx^0)^2+(dx^1)^2+(dx^2)^2+(dx^3)^2
 -(dy^1)^2-(dy^2)^2-(dy^3)^2\right]-dt^2.}
$$

In the ordered coordinates,

$$
g_{\mu\nu}=\operatorname{diag}
\left(a^2,a^2,a^2,a^2,-1,-a^2,-a^2,-a^2\right).
$$

There are four positive and four negative entries. If `a` is nonconstant, the
metric is curved. Constant-`t` hypersurfaces have signature `(4,3)`, so they
are not ordinary Riemannian spatial slices.

Define

$$
H(t)=\frac{\dot a(t)}{a(t)}.
$$

This resembles the Hubble parameter of a flat FLRW ansatz, but here it is the
expansion rate of a seven-dimensional split-signature transverse metric.

## 5. Step 1: the selected canonical frame field

Choose the diagonal coframe gauge

$$
e_\mu{}^a=
\operatorname{diag}(a,a,a,a,1,a,a,a).
$$

Its inverse is

$$
e_a{}^\mu=
\operatorname{diag}(a^{-1},a^{-1},a^{-1},a^{-1},1,
 a^{-1},a^{-1},a^{-1}).
$$

Direct multiplication gives

$$
e\eta e^{\mathsf T}
=\operatorname{diag}(a^2,a^2,a^2,a^2,-1,-a^2,-a^2,-a^2)
=g.
$$

In differential-form notation,

$$
e^4=dt,
\qquad e^i=a(t)dx^i\quad(i\in I),
$$

where the three `y` coordinates are included in the symbol `dx^i` according
to the fixed ordered index set.

This frame is selected because it is diagonal, orientation-compatible, and
reduces to the identity frame when `a=1`. Local `SO(4,4)` transforms produce
gauge-equivalent frames and transformed spin-connection components.

## 6. Levi-Civita Christoffel symbols

The torsion-free metric-compatible coordinate connection is

$$
\Gamma^\rho{}_{\mu\nu}
=\frac12 g^{\rho\sigma}
\left(\partial_\mu g_{\nu\sigma}
+\partial_\nu g_{\mu\sigma}
-\partial_\sigma g_{\mu\nu}\right).
$$

Only time derivatives are nonzero. For each transverse index `i in I`, the
complete nonzero inventory is

$$
\boxed{
\Gamma^4{}_{ii}=\eta_{ii}a\dot a,
\qquad
\Gamma^i{}_{4i}=\Gamma^i{}_{i4}=H.}
$$

There are `7*3=21` nonzero coordinate components. The sign in
`Gamma^4_ii` follows the tangent signature:

- for `i=0,1,2,3`, `Gamma^4_ii=+a adot`;
- for `i=5,6,7`, `Gamma^4_ii=-a adot`.

No summation over `i` is intended in these displayed component formulas.

## 7. Step 2: canonical Levi-Civita spin connection

The vielbein postulate is

$$
\partial_\mu e_\nu{}^a
-\Gamma^\rho{}_{\mu\nu}e_\rho{}^a
+\omega_\mu{}^a{}_b e_\nu{}^b=0.
$$

Multiplying by the inverse frame solves it directly:

$$
\boxed{
\omega_\mu{}^a{}_b
=e_b{}^\nu\left(
\Gamma^\rho{}_{\mu\nu}e_\rho{}^a
-\partial_\mu e_\nu{}^a
\right).}
$$

Lower the first tangent index with `eta`:

$$
\omega_{\mu ab}=\eta_{ac}\omega_\mu{}^c{}_b.
$$

Metric compatibility gives

$$
\omega_{\mu ab}=-\omega_{\mu ba}.
$$

For the chosen frame, all components with `mu=4` vanish. For every
transverse `i`, the complete nonzero lowered components are

$$
\boxed{
\omega_{i i4}=\eta_{ii}\dot a,
\qquad
\omega_{i4i}=-\eta_{ii}\dot a.}
$$

There are `7*2=14` nonzero lowered components. Explicitly,

```text
omega_0,04 = +adot    omega_0,40 = -adot
omega_1,14 = +adot    omega_1,41 = -adot
omega_2,24 = +adot    omega_2,42 = -adot
omega_3,34 = +adot    omega_3,43 = -adot
omega_5,54 = -adot    omega_5,45 = +adot
omega_6,64 = -adot    omega_6,46 = +adot
omega_7,74 = -adot    omega_7,47 = +adot
```

Here a comma separates the coordinate index from the two tangent indices.
Substitution into every one of the `8*8*8=512` vielbein-postulate components
returns zero exactly.

The task's Step 4 repeats the Step 2 equation. No new connection is required:
the Levi-Civita construction is dimension-independent, and the formula above
is already its direct 8-dimensional generalization. Introducing a second
"canonical" connection without extra torsion or nonmetricity data would be
mathematically unjustified.

## 8. Exact real 16 by 16 gamma matrices

Define

$$
P=\begin{pmatrix}0&1\\1&0\end{pmatrix},
\qquad
N=\begin{pmatrix}0&1\\-1&0\end{pmatrix},
\qquad
G=\begin{pmatrix}1&0\\0&-1\end{pmatrix}.
$$

They satisfy

$$
P^2=I_2,
\qquad N^2=-I_2,
\qquad G^2=I_2,
$$

and anticommute pairwise. On the fourth tensor power of `R^2`, define

$$
\gamma_k^+=G^{\otimes(k-1)}\otimes P\otimes I_2^{\otimes(4-k)},
$$

$$
\gamma_k^-=G^{\otimes(k-1)}\otimes N\otimes I_2^{\otimes(4-k)},
\qquad k=1,2,3,4.
$$

The ordered list is

$$
(\gamma_1^+,\gamma_2^+,\gamma_3^+,\gamma_4^+,
 \gamma_1^-,\gamma_2^-,\gamma_3^-,\gamma_4^-).
$$

In zero-based indexing, the evolution-time generator is `gamma^4`, the first
negative generator and fifth matrix in this list. The matrices obey

$$
\gamma^a\gamma^b+\gamma^b\gamma^a=2\eta^{ab}I_{16}.
$$

Curved gamma matrices are

$$
\gamma^\mu(x)=e_a{}^\mu(x)\gamma^a,
$$

and satisfy

$$
\gamma^\mu\gamma^\nu+\gamma^\nu\gamma^\mu
=2g^{\mu\nu}I_{16}.
$$

## 9. Step 3: spinor covariant derivative

Define

$$
\Omega_\mu
=\frac18\omega_{\mu ab}[\gamma^a,\gamma^b]
$$

and

$$
\boxed{D_\mu\psi=\partial_\mu\psi+\Omega_\mu\psi.}
$$

The factor `1/8` is correct when the repeated indices `a,b` are summed over
all ordered pairs. Since `omega_muab` and the commutator are both
antisymmetric, the `(a,b)` and `(b,a)` terms are equal. If one instead writes
only a sum over `a<b`, the equivalent coefficient is `1/4`:

$$
\frac18\sum_{a,b}\omega_{\mu ab}[\gamma^a,\gamma^b]
=\frac14\sum_{a<b}\omega_{\mu ab}[\gamma^a,\gamma^b].
$$

For this frame,

$$
\Omega_4=0,
$$

and for each transverse index,

$$
\boxed{
\Omega_i=\frac12\eta_{ii}\dot a\,\gamma^i\gamma^4.}
$$

The chirality operator is

$$
\omega_{\mathrm{chir}}
=\gamma^0\gamma^1\cdots\gamma^7.
$$

Every `Omega_mu` is an even Clifford element, so

$$
[\Omega_\mu,\omega_{\mathrm{chir}}]=0.
$$

The connection therefore preserves the two half-spin subbundles even though
odd Clifford multiplication exchanges them.

## 10. Homogeneous Dirac operator

For a homogeneous spinor `psi(t)`, transverse partial derivatives vanish but
transverse spin-connection terms do not. Contracting with the curved gamma
matrices gives

$$
\gamma^\mu\Omega_\mu
=\sum_{i\in I}\frac1a\gamma^i
\left(\frac12\eta_{ii}\dot a\gamma^i\gamma^4\right).
$$

Since `(gamma^i)^2=eta_ii I`, each summand equals `H gamma^4/2`. There are
seven transverse directions, hence

$$
\boxed{
\gamma^\mu D_\mu\psi
=\gamma^4\left(\partial_t+\frac72H\right)\psi.}
$$

The factor `7/2` is the 8-dimensional analogue of the familiar `3H/2` term
in a four-dimensional spatially flat homogeneous spinor equation.

## 11. Real invariant spinor bilinear

The exact gamma representation admits the symmetric matrix

$$
C=\gamma_1^+\gamma_2^+\gamma_3^+\gamma_4^+.
$$

It obeys

$$
C^{\mathsf T}=C,
\qquad C^2=I_{16},
\qquad
(\gamma^a)^{\mathsf T}C=-C\gamma^a.
$$

Its eigenvalue signature is `(8,8)`, so it is nondegenerate but not positive
definite. Define

$$
\bar\psi=\psi^{\mathsf T}C,
\qquad
S=\bar\psi\psi=\psi^{\mathsf T}C\psi.
$$

For a local spin transformation `R` generated by bivectors,

$$
R^{\mathsf T}CR=C,
$$

so `S` is locally `Spin(4,4)` invariant. This is the covariant bilinear used
by the coupled gravitational model. It must not be confused with the positive
Euclidean quantity `psi^T psi` used in a previous background-only numerical
reconstruction.

Because `C` is symmetric, a single Grassmann-odd spinor would satisfy
`psi^T C psi=0`. The nonlinear model that uses nonzero `S` therefore treats
`psi` as a commuting classical real spinor field, an effective classical
order parameter, rather than a quantized fermionic field.

## 12. Exact verification strategy

Two implementations derive the geometry independently.

The Python generator differentiates the metric and frame using exact rational
arithmetic at the nontrivial sample

$$
a=\frac32,
\qquad \dot a=\frac25,
\qquad H=\frac4{15}.
$$

It checks all 512 vielbein-postulate components, all connection antisymmetry
components, the exact invariant bilinear, the chirality commutators, and the
full 16 by 16 slash-connection identity.

The Wolfram implementation performs symbolic differentiation with an
unspecified function `a(t)`. It independently derives the metric,
Christoffels, spin connection, and spin matrices and checks the same symbolic
identities without reading the Python result.

The independent Python checker reads both reports, reconstructs the
Christoffels and spin connection again from metric/frame derivatives, verifies
source hashes, and compares exact half-spin indices to volume-element
eigenspaces.

Expected exact totals are

```text
base_dimension=8
signature=(4,4)
spinor_fiber_dimension=16
half_spin_dimensions=(8,8)
nonzero_Christoffel_components=21
nonzero_lowered_spin_connection_components=14
spinor_bilinear_signature=(8,8)
Python_generator_checks=12
Wolfram_symbolic_checks=11
independent_checker_checks=16
```

## 13. Complete Windows commands

Open PowerShell and run every command below from a clean checkout:

```powershell
Set-Location C:\Users\nsh\Developer\code\vscode\dirac
git submodule update --init --recursive

python scripts\backup_files.py `
  artifacts\curved-spin-geometry\geometry.json `
  artifacts\curved-spin-geometry\wolfram-report.json `
  provenance\CURVED_SPIN_BUNDLE.tex `
  provenance\CURVED_SPIN_BUNDLE.pdf

New-Item -ItemType Directory -Force -Path `
  build\curved-spin-geometry\pdf-a, `
  build\curved-spin-geometry\pdf-b | Out-Null

python scripts\build_curved_spin_geometry.py
python scripts\build_curved_spin_geometry.py `
  --output build\curved-spin-geometry\geometry-repeat.json

wolframscript -file scripts\verify_curved_spin_geometry.wls -- `
  artifacts\curved-spin-geometry\wolfram-report.json
wolframscript -file scripts\verify_curved_spin_geometry.wls -- `
  build\curved-spin-geometry\wolfram-report-repeat.json

python scripts\check_curved_spin_geometry.py
python -m unittest discover -s tests -p test_curved_spin_geometry.py -v
python -m unittest discover -s tests -v

python scripts\build_dissertation_tex.py --strip-heading-numbers `
  --input provenance\CURVED_SPIN_BUNDLE.md `
  --output provenance\CURVED_SPIN_BUNDLE.tex
python scripts\build_dissertation_tex.py --strip-heading-numbers `
  --input provenance\CURVED_SPIN_BUNDLE.md `
  --output build\curved-spin-geometry\CURVED_SPIN_BUNDLE-repeat.tex

pdflatex -interaction=nonstopmode -halt-on-error `
  -jobname=CURVED_SPIN_BUNDLE `
  -output-directory=build\curved-spin-geometry\pdf-a `
  provenance\CURVED_SPIN_BUNDLE.tex
pdflatex -interaction=nonstopmode -halt-on-error `
  -jobname=CURVED_SPIN_BUNDLE `
  -output-directory=build\curved-spin-geometry\pdf-a `
  provenance\CURVED_SPIN_BUNDLE.tex
pdflatex -interaction=nonstopmode -halt-on-error `
  -jobname=CURVED_SPIN_BUNDLE `
  -output-directory=build\curved-spin-geometry\pdf-a `
  provenance\CURVED_SPIN_BUNDLE.tex

pdflatex -interaction=nonstopmode -halt-on-error `
  -jobname=CURVED_SPIN_BUNDLE `
  -output-directory=build\curved-spin-geometry\pdf-b `
  build\curved-spin-geometry\CURVED_SPIN_BUNDLE-repeat.tex
pdflatex -interaction=nonstopmode -halt-on-error `
  -jobname=CURVED_SPIN_BUNDLE `
  -output-directory=build\curved-spin-geometry\pdf-b `
  build\curved-spin-geometry\CURVED_SPIN_BUNDLE-repeat.tex
pdflatex -interaction=nonstopmode -halt-on-error `
  -jobname=CURVED_SPIN_BUNDLE `
  -output-directory=build\curved-spin-geometry\pdf-b `
  build\curved-spin-geometry\CURVED_SPIN_BUNDLE-repeat.tex

python scripts\check_provenance_pdf.py --edition curved-spin-bundle `
  build\curved-spin-geometry\pdf-a\CURVED_SPIN_BUNDLE.pdf `
  --repeat build\curved-spin-geometry\pdf-b\CURVED_SPIN_BUNDLE.pdf

$texA = (Get-FileHash `
  provenance\CURVED_SPIN_BUNDLE.tex `
  -Algorithm SHA256).Hash
$texB = (Get-FileHash `
  build\curved-spin-geometry\CURVED_SPIN_BUNDLE-repeat.tex `
  -Algorithm SHA256).Hash
if ($texA -ne $texB) { throw "Curved-spin LaTeX changed bytes" }
$pdfA = (Get-FileHash `
  build\curved-spin-geometry\pdf-a\CURVED_SPIN_BUNDLE.pdf `
  -Algorithm SHA256).Hash
$pdfB = (Get-FileHash `
  build\curved-spin-geometry\pdf-b\CURVED_SPIN_BUNDLE.pdf `
  -Algorithm SHA256).Hash
if ($pdfA -ne $pdfB) { throw "Curved-spin PDF changed bytes" }

$warningPattern = '^!|LaTeX Warning|Package .* Warning|'
$warningPattern += 'Overfull|Underfull|Undefined control sequence'
$issues = Select-String `
  -Path build\curved-spin-geometry\pdf-a\CURVED_SPIN_BUNDLE.log, `
        build\curved-spin-geometry\pdf-b\CURVED_SPIN_BUNDLE.log `
  -Pattern $warningPattern
if ($issues) { throw "Curved-spin LaTeX warnings remain" }

Copy-Item build\curved-spin-geometry\pdf-a\CURVED_SPIN_BUNDLE.pdf `
  provenance\CURVED_SPIN_BUNDLE.pdf -Force

.\scripts\verify_phase5_curved_spin_gravity.ps1
```

The final command runs the complete exact geometry, coupled numerical study,
two provenance builds, all tests, all byte comparisons, and all warning scans.
Its final line must be

```text
phase5_curved_spin_gravity_verification=OK
```

## 14. Complete Git Bash or WSL commands

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
pdflatex_command="$(resolve_miktex_pdflatex)"

"$python_command" scripts/backup_files.py \
  artifacts/curved-spin-geometry/geometry.json \
  artifacts/curved-spin-geometry/wolfram-report.json \
  provenance/CURVED_SPIN_BUNDLE.tex \
  provenance/CURVED_SPIN_BUNDLE.pdf

rm -rf build/curved-spin-geometry/pdf-a build/curved-spin-geometry/pdf-b
mkdir -p build/curved-spin-geometry/pdf-a build/curved-spin-geometry/pdf-b

"$python_command" scripts/build_curved_spin_geometry.py
"$python_command" scripts/build_curved_spin_geometry.py \
  --output build/curved-spin-geometry/geometry-repeat.json

wolframscript_command="$(resolve_wolframscript)"
"$wolframscript_command" -file scripts/verify_curved_spin_geometry.wls -- \
  artifacts/curved-spin-geometry/wolfram-report.json
"$wolframscript_command" -file scripts/verify_curved_spin_geometry.wls -- \
  build/curved-spin-geometry/wolfram-report-repeat.json

"$python_command" scripts/check_curved_spin_geometry.py
"$python_command" -m unittest discover -s tests \
  -p test_curved_spin_geometry.py -v
"$python_command" -m unittest discover -s tests -v

"$python_command" scripts/build_dissertation_tex.py \
  --strip-heading-numbers \
  --input provenance/CURVED_SPIN_BUNDLE.md \
  --output provenance/CURVED_SPIN_BUNDLE.tex
"$python_command" scripts/build_dissertation_tex.py \
  --strip-heading-numbers \
  --input provenance/CURVED_SPIN_BUNDLE.md \
  --output build/curved-spin-geometry/CURVED_SPIN_BUNDLE-repeat.tex

for pass in 1 2 3; do
  "$pdflatex_command" -interaction=nonstopmode -halt-on-error \
    -jobname=CURVED_SPIN_BUNDLE \
    -output-directory=build/curved-spin-geometry/pdf-a \
    provenance/CURVED_SPIN_BUNDLE.tex
  "$pdflatex_command" -interaction=nonstopmode -halt-on-error \
    -jobname=CURVED_SPIN_BUNDLE \
    -output-directory=build/curved-spin-geometry/pdf-b \
    build/curved-spin-geometry/CURVED_SPIN_BUNDLE-repeat.tex
done

"$python_command" scripts/check_provenance_pdf.py \
  --edition curved-spin-bundle \
  build/curved-spin-geometry/pdf-a/CURVED_SPIN_BUNDLE.pdf \
  --repeat build/curved-spin-geometry/pdf-b/CURVED_SPIN_BUNDLE.pdf

tex_a="$(sha256sum provenance/CURVED_SPIN_BUNDLE.tex | cut -d' ' -f1)"
tex_b="$(sha256sum \
  build/curved-spin-geometry/CURVED_SPIN_BUNDLE-repeat.tex | \
  cut -d' ' -f1)"
test "$tex_a" = "$tex_b"
pdf_a="$(sha256sum \
  build/curved-spin-geometry/pdf-a/CURVED_SPIN_BUNDLE.pdf | \
  cut -d' ' -f1)"
pdf_b="$(sha256sum \
  build/curved-spin-geometry/pdf-b/CURVED_SPIN_BUNDLE.pdf | \
  cut -d' ' -f1)"
test "$pdf_a" = "$pdf_b"
warning_pattern='^!|LaTeX Warning|Package .* Warning|'
warning_pattern+='Overfull|Underfull|Undefined control sequence'
! grep -Ei "$warning_pattern" \
  build/curved-spin-geometry/pdf-a/CURVED_SPIN_BUNDLE.log \
  build/curved-spin-geometry/pdf-b/CURVED_SPIN_BUNDLE.log
cp build/curved-spin-geometry/pdf-a/CURVED_SPIN_BUNDLE.pdf \
  provenance/CURVED_SPIN_BUNDLE.pdf

bash ./scripts/verify_phase5_curved_spin_gravity.sh
```

## 15. Files created and their roles

```text
wolfram/CurvedSpinGeometry.wl
scripts/verify_curved_spin_geometry.wls
scripts/build_curved_spin_geometry.py
scripts/check_curved_spin_geometry.py
artifacts/curved-spin-geometry/geometry.json
artifacts/curved-spin-geometry/wolfram-report.json
provenance/CURVED_SPIN_BUNDLE.md
provenance/CURVED_SPIN_BUNDLE.tex
provenance/CURVED_SPIN_BUNDLE.pdf
```

The Wolfram and Python definitions are independent implementations of the
same mathematical equations. The JSON files are machine-readable exact
evidence. The Markdown, LaTeX, and PDF contain the complete standalone human
explanation and commands.

## 16. Limitations

The frame is canonical only relative to the chosen diagonal gauge and metric
ansatz. It is not a unique frame for every `(4,4)` metric. The base is assumed
to possess the required orientation, time orientation, and spin structure.
The explicit chart and frame describe the chosen coordinate domain; global
topology is not classified.

The constant-`t` slices are split signature `(4,3)`. The construction is a
valid pseudo-Riemannian and spin-geometric model, but it is not ordinary
Lorentzian cosmology. Any physical interpretation requires separate analyses
of causality, hyperbolicity, ghosts, boundary conditions, compactification,
perturbations, and observations.

## 17. Conclusion

One precise fiber bundle has been defined:

$$
\mathcal S=P_{\mathrm{Spin}(4,4)}(M)
\mathbin{\times}_{\rho}(\Delta_+\oplus\Delta_-).
$$

The flat tangent metric `eta`, curved metric `g`, and selected vielbein `e`
are related by `g=e eta e^T`. The Levi-Civita spin connection follows uniquely
from the stated frame gauge and vielbein postulate. The requested covariant
derivative with coefficient `1/8` is correct under an all-ordered-pairs tangent
index sum. Exact Python and Wolfram calculations agree on every nonzero
connection component and on the homogeneous `7H/2` spin-connection term.
