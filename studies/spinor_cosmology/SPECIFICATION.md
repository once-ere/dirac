# Real homogeneous nonlinear-spinor cosmology specification

## Scientific scope

This is a homogeneous background reconstruction, not a perturbation theory or
an observational fit. It uses the central CPL parameters documented in the
audited source corpus and tests whether a 16-component real field can carry the
required dilution while its nonlinear potential reproduces the same background
density history.

## State and independent variable

The independent variable is e-fold time `N = ln(a)`. The 18 real state
variables are

```text
y = (tau, rho, psi_0, ..., psi_15),
```

where `tau = H0 (t - t0)`, `rho` is measured in present critical-density
units, and `psi` is a real 16-vector. Define

```text
S = psi^T psi.
```

The internal rotation matrix `J` is the fifth generator in the verified
`Cl(4,4)` ordering. It is real, satisfies `J^2 = -I`, and is skew under the
ordinary transpose, so it changes the spinor direction without changing `S`.

## Parameters

```text
Omega_m0   = 0.305
Omega_r0   = 0.00009
Omega_psi0 = 0.69491
w0         = -0.861
wa         = -0.60
```

These values obey flatness at `a = 1`.

## Potential and equations

```text
w(a) = w0 + wa (1 - a),

U(S) = Omega_psi0 S^(1+w0+wa)
       exp[-3 wa (1 - S^(-1/3))],

E^2 = Omega_r0 exp(-4N) + Omega_m0 exp(-3N) + rho,

dtau/dN = 1/E,
drho/dN = -3 (1 + w(exp(N))) rho,
dpsi/dN = -(3/2) psi + (U_S/E) J psi.
```

The rotation term is a real representation of the homogeneous first-order
internal evolution. Since `J` is skew, it drops out of `dS/dN`, giving the
exact identity `S = exp(-3N)` for the selected initial data. Consequently
`rho = U(S)` follows from the continuity equation.

## Initial data and interval

At `N = 0`:

```text
tau = 0
rho = Omega_psi0
psi = (1,0,...,0)
```

CVODE integrates two branches from this same initial state: backward to
`N = -4` and forward to `N = 1`. The joined output contains 1,201 points at
spacing `1/240`, with the present epoch included once.

## Acceptance criteria

- All public states and outputs are real.
- CVODE BDF, Newton iteration, and the dense solver return no negative flag.
- Relative tolerance is `1e-11`; every absolute tolerance is `1e-13`.
- Maximum step magnitude is `0.02` in e-fold time.
- The maximum relative errors in `S = exp(-3N)`, analytic CPL density, and
  `rho = U(S)` are each at most `1e-8`.
- Repeated release runs produce byte-identical CSV and JSON.

The reconstruction proves background consistency only. It does not establish
perturbative stability, microscopic uniqueness, or observational preference
for this field model.