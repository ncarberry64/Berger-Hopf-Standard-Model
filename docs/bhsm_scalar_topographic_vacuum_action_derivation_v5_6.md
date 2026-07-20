# BHSM Scalar/Topographic Vacuum Action Derivation v5.6

Primary result: `SCALAR_TOPOGRAPHIC_VACUUM_ACTION_DERIVED_CONDITIONALLY`.

BHSM v5.6 replaces the v5.5 generic scale-potential ansatz with a controlled
scalar/topographic action reduction. The result is conditional because explicit
profiles, threshold values, boundary coefficients, collar measure values, and
the absolute unit anchor remain open.

## Scale Order Parameter

The v5.5 `sigma` is renamed:

```text
sigma_scale
```

It is the dimensionless coefficient of a normalized scalar/topographic scale
mode:

```text
T = T_bar + sigma_scale f_T + ...
Phi = Phi_bar + sigma_scale f_Phi + ...
Q_ST[f_T,f_Phi] = 1
```

`sigma_scale` is not the profile width. The profile-width or shape parameter is
tracked separately as:

```text
sigma_profile
```

The map is:

```text
(T, Phi, boundary geometry)
  -> normalized scale mode (f_T,f_Phi)
  -> sigma_scale = <(delta T,delta Phi),(f_T,f_Phi)>_Q_ST
```

## Scalar/Topographic Action

The scalar/topographic action source is assembled as:

```text
S_ST =
    S_T_bulk
  + S_Phi_internal
  + S_threshold
  + S_boundary
  + S_collar
```

with:

```text
S_T_bulk =
  integral_B [1/2 z_T |grad T|^2 + U_T(T; geometry)] dV

S_Phi_internal =
  integral_Bint [1/2 z_Phi |D_B Phi|^2 + U_Phi(Phi; g_B)] dmu_B

S_threshold =
  integral [1/2 m_TT(T-T_0)^2
          + 1/2 m_PP(Phi-Phi_0)^2
          + m_TP(T-T_0)(Phi-Phi_0)]

S_boundary =
  integral_boundary [
      U_boundary(T,Phi)
    + c_K K
    + c_K2 K^2
    + c_S Tr(S^2)
    + c_J log J
  ] dA

S_collar =
  integral_boundary integral_0^rho_star
    B_threshold[T,Phi,K,S,J;Y,rho] J(Y,rho) drho dA
```

This uses the PO-BH scalar/topographic source chain rather than importing the
Standard Model Higgs potential.

## Reduced Vacuum

Projecting `S_ST` onto the normalized scale mode gives:

```text
V_eff(sigma_scale)
  =
  V_0
  + 1/2 A_ST[f] sigma_scale^2
  + 1/4 G_ST[f] sigma_scale^4
  + O(sigma_scale^6)
```

When:

```text
A_ST[f] < 0
G_ST[f] > 0
```

define:

```text
alpha_scale = -A_ST[f]
beta_scale  =  G_ST[f]
```

so:

```text
V_eff =
  V_0
  - 1/2 alpha_scale sigma_scale^2
  + 1/4 beta_scale sigma_scale^4
  + O(sigma_scale^6)
```

Thus `alpha_scale` and `beta_scale` are conditional action functionals, not free
quartic placeholders.

## Vacuum

The truncated stationary equation is:

```text
-alpha_scale sigma_scale + beta_scale sigma_scale^3 = 0
```

Branches:

```text
sigma_scale = 0
sigma_scale = +sqrt(alpha_scale/beta_scale)
sigma_scale = -sqrt(alpha_scale/beta_scale)
```

The nonzero branch has:

```text
V_eff'' = 2 alpha_scale
V_min = V_0 - alpha_scale^2/(4 beta_scale)
```

It is locally stable under `alpha_scale>0` and `beta_scale>0`, with a unique
magnitude and sign degeneracy unless a later action term breaks the branch
symmetry.

## Curvature-Threshold Audit

The old candidate:

```text
L =
  1/2 phidot^2
  - 1/2 |grad phi|^2
  - lambda/2 (-laplacian phi - k_loc)^2
```

expanded about:

```text
-laplacian phi_0 = k_loc
phi = phi_0 + eta
```

gives:

```text
L_quad =
  1/2 etadot^2
  - 1/2 |grad eta|^2
  - lambda/2 (laplacian eta)^2
```

The fluctuation operator is:

```text
eta_tt - laplacian eta + lambda laplacian^2 eta = 0
```

and:

```text
omega^2 = |k|^2 + lambda |k|^4
```

There is no constant mass term. The prior mass-gap shortcut does not survive
the background substitution. A gap requires an action-derived nonlinear or
potential term.

## Unit Anchor

The vacuum updates v5.5 to:

```text
M_BH / M_star = sqrt(alpha_scale / beta_scale)
```

where `alpha_scale` and `beta_scale` are action functionals. The absolute unit
anchor remains open:

```text
OPEN_MISSING_ABSOLUTE_UNIT_ANCHOR
```

No numeric eV/GeV scale, particle mass, gauge coupling, CKM value, rare-B
observable, or full BHSM completion is claimed.

Command:

```bash
python -m bhsm.interface scalar-topographic-vacuum-status --format markdown
```
