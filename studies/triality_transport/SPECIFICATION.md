# Triality transport specification

## State

The 24 real state variables are three ordered eight-vectors:

```text
y = (v, s_plus, s_minus)
```

`v` carries the vector representation, `s_plus` carries the first verified
half-spin representation, and `s_minus` carries the second. Their matrices are
generated from `artifacts/exact/triality44.json`; they are not transcribed from
a historical notebook.

## Evolution equation

Let `rho_v`, `rho_plus`, and `rho_minus` denote the three representations of
the same 28-dimensional triality Lie algebra. Define the time-dependent element

```text
X(t) = c0(t) E(0,1) + c1(t) E(1,4)
     + c2(t) E(4,5) + c3(t) E(2,6),

c0(t) = 1/5,
c1(t) = 3/20 + t/40,
c2(t) = -1/10 + t/50,
c3(t) = t (4 - t) / 80.
```

The ODE is

```text
dv/dt       = rho_v(X(t)) v,
ds_plus/dt  = rho_plus(X(t)) s_plus,
ds_minus/dt = rho_minus(X(t)) s_minus.
```

The selected generators include compact and split directions and do not all
commute. The problem therefore tests synchronized transport in all three
representations rather than three independent constant exponentials.

## Initial data and interval

```text
t0 = 0
t_final = 4
v(0) = s_plus(0) = s_minus(0) = (1,0,0,0,0,0,0,0)
```

CVODE uses BDF, Newton iteration, a dense linear solver, relative tolerance
`1e-11`, componentwise absolute tolerance `1e-13`, maximum step `0.02`, and
output spacing `0.1`.

## Invariants

With the common metric `eta = diag(1,1,1,1,-1,-1,-1,-1)`, the following
quantities are constant:

```text
Nv = v^T eta v,
Np = s_plus^T eta s_plus,
Nm = s_minus^T eta s_minus,
T  = <s_plus star s_minus, v>,
```

where `star` is the verified para-product. All four initial values equal one.

## Acceptance criteria

- CVODE returns no negative flag.
- Exactly 41 samples are written, including both endpoints.
- Each maximum absolute invariant drift is at most `1e-8`.
- A repeated release run produces byte-identical CSV and JSON outputs.
- The application and workspace build with zero warnings and contain no unsafe
  code or external package dependency beyond the pinned solver submodule.