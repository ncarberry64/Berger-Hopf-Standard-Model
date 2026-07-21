# BHSM Scalar/Topographic Profile Boundary Closure v5.7

Status: `SCALAR_TOPOGRAPHIC_PROFILE_BOUNDARY_CLOSED_CONDITIONALLY`.

BHSM v5.7 solves the minimal scalar/topographic profile and boundary problem needed to evaluate the v5.6 vacuum functionals in a normalized, homogeneous Berger-boundary reduction. It does not introduce measured masses, electroweak calibration, rare-B phenomenology, or a physical eV/GeV unit anchor.

## Geometry And Mode Selection

The reduced manifold is a normalized homogeneous Berger boundary `Sigma_B` with collar `[0,rho_star]`, `rho_star=1`, and homogeneous collar Jacobian `J=1`. The selected scalar/topographic mode is the lowest admissible self-adjoint homogeneous mode satisfying finite action, Robin zero-flux boundary data, and sector compatibility.

The normalized mode is

```text
f = (f_T, f_Phi) = (1/sqrt(2), 1/sqrt(2))
integral(f_T^2 + f_Phi^2) dmu_normalized = 1
```

The scale amplitude `sigma_scale` is the dynamical vacuum-mode coefficient. It is not the profile width `sigma_profile`; for the homogeneous lowest mode, `sigma_profile=infinity` is only a shape label.

## Reduced Field Equations

The normalized reduced scalar/topographic action is

```text
S_red(T,Phi)
  = 1/2 m_diag (T^2 + Phi^2)
    - m_mix T Phi
    + 1/4 lambda_ST (T^2 + Phi^2)^2
```

with the v5.7 conditional coefficients

```text
Z_T = 1
Z_Phi = 1
m_diag = 1
m_mix = 3
lambda_ST = 8
c_K = c_K2 = c_S = 0
c_J = 0
rho_star = 1
```

`Z_T`, `Z_Phi`, and `rho_star` are conventional normalized choices in the reduced problem. The fixed homogeneous geometry gives no independent scalar variation for `c_K`, `c_K2`, or `c_S`. The collar Jacobian is already in the measure, so `c_J=0` prevents double-counting.

The reduced Euler-Lagrange equations are

```text
E_T = -Z_T partial_rho^2 T
      + m_diag T
      - m_mix Phi
      + lambda_ST (T^2+Phi^2) T
      = 0

E_Phi = -Z_Phi Delta_B Phi
        + m_diag Phi
        - m_mix T
        + lambda_ST (T^2+Phi^2) Phi
        = 0
```

For the homogeneous lowest mode, the differential terms vanish on the normalized cell and the stationary branch is

```text
sigma_scale = sqrt(alpha_scale / beta_scale) = 1/2
T_0 = Phi_0 = sigma_scale / sqrt(2)
y_0 = 0
```

The level-set residuals, Robin residuals, critical-point residual, normalization residual, and field-equation residuals are zero in the reduced model.

## Vacuum Functional

Projecting along the normalized mode gives

```text
V_eff(sigma_scale)
  = 1/2 A_ST sigma_scale^2
    + 1/4 G_ST sigma_scale^4
```

where

```text
A_ST = m_diag - m_mix = -2
C_ST = 0
G_ST = lambda_ST = 8
alpha_scale = -A_ST = 2
beta_scale = G_ST = 8
```

The cubic term vanishes by the simultaneous orientation-pair symmetry `(T,Phi)->-(T,Phi)` of the declared reduced action. The vacuum equation is

```text
A_ST sigma_scale + G_ST sigma_scale^3 = 0
```

with branches `0`, `+1/2`, and `-1/2`. The selected positive orientation branch has

```text
vacuum_energy = -1/8
radial Hessian = 4
M_BH/M_star = 1/2
R_BH/ell_star = 2
```

The old curvature-threshold mass-gap shortcut remains invalidated: expanding the old threshold action about `-laplacian phi_0=k_loc` produces a massless higher-derivative fluctuation operator, not a `k=0` mass term.

## Hessian And Response

At the selected branch, the reduced `(T,Phi)` Hessian is

```text
[[5, -1],
 [-1, 5]]
```

Its eigenvalues are `4` and `6`, so the reduced physical subspace has no zero or negative mode. The Green/response eigenvalues are `1/4` and `1/6`, defined only on this reduced self-adjoint Robin domain.

## Claim Boundary

Conditionally established:

- explicit homogeneous scalar/topographic background profiles
- explicit level-set data `T_0`, `Phi_0`, and `y_0`
- normalized scale mode `f=(1/sqrt(2),1/sqrt(2))`
- evaluated `alpha_scale=2` and `beta_scale=8` in normalized reduced units
- verified reduced vacuum solution and Hessian response

Still requiring new mathematics:

- `OPEN_MISSING_ABSOLUTE_UNIT_ANCHOR`
- `OPEN_MISSING_NONLINEAR_FULL_GEOMETRIC_BACKREACTION`
- `OPEN_MISSING_NONHOMOGENEOUS_BERGER_PROFILE_SOLUTION`
- `OPEN_MISSING_GAUGE_COUPLING_ACTION_ATTACHMENT`
- `OPEN_MISSING_ALPHA_I_ACTION_DERIVATION`
- `OPEN_MISSING_G2_BH_ACTION_SOURCE`
- `OPEN_MISSING_CKM_COEFFICIENT_VALUE_SOURCE`
- `CKM_EXPONENT_NOT_DERIVED`
- `OPEN_MISSING_NEUTRAL_SCALE`
- `OPEN_MISSING_NEUTRAL_ACTION_NORMALIZATION`
- `FULL_BHSM_NOT_COMPLETE`

BHSM v5.7 does not derive an absolute eV/GeV mass scale, particle masses, gauge couplings, CKM coefficient values, CKM exponents, rare-B observables, or full BHSM completion.

Command:

```bash
python -m bhsm.interface scalar-topographic-profile-boundary-status --format markdown
```
