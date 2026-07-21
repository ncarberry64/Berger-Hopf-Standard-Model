# BHSM v5.12 Primordial Boundary-Tension Action Source Closure

Primary result: `BHSM_PRIMORDIAL_BOUNDARY_SOURCE_NOT_CLOSED`.

## Central result

The stored BHSM action does not yet provide enough physically localized, dimensionally normalized boundary/collar structure to evaluate a finite release radius `L_c`. It also does not support the stronger minimal-one-scale classification because the dimensionless shape ratios, pressure balance, embedding, and normal-mode domain remain unresolved.

This sprint derives the strongest source-qualified normal-stress and surface-stability architecture. It does not derive an absolute unit, a historical primordial rupture, or plasma production.

## Boundary domain and dimensions

The v5.4 candidate explicitly uses

```text
dmu_Sigma,rho = sqrt(det h_rho) d^3x.
```

Thus its normalized boundary has three coordinates. This does not determine whether the physical action domain is spatial, spacetime, Euclidean, Lorentzian, or canonical; it does not identify which coordinate is time; and it does not establish a foundational bulk dimension. The collar has four coordinate integrations when `rho` is counted, but `rho_star=1` is a normalized dimensionless endpoint.

Physical dimensions therefore remain expressed using symbolic `d_Sigma` and explicit action dimension `[A]=[hbar]`:

```text
[U_boundary] = [A] L^(-d_Sigma)
[c_K]        = [A] L^(1-d_Sigma)
[c_K2]       = [A] L^(2-d_Sigma)
[c_S]        = [A] L^(2-d_Sigma)
[B_collar]   = [A] L^(-(d_Sigma+1))  if rho is physical.
```

For the candidate coordinate count `d_Sigma=3`, these become `[A]L^-3`, `[A]L^-2`, `[A]L^-1`, `[A]L^-1`, and `[A]L^-4`. The v5.4 dimension table instead uses powers of an unresolved `ell_BH`; it does not derive that length.

## Boundary and collar action

The strongest stored architecture is

```text
S_boundary = integral_Sigma dmu_h [
    U_boundary(T,Phi)
  + c_K K
  + c_K2 K^2
  + c_S Tr(S^2)
  + c_J log J
  + L_boundary,other]

S_collar = integral_Sigma integral_0^rho_star
  B_collar[T,Phi,g,K,S,rho] J(Y,rho) d rho dmu_h.
```

These are symbolic candidates. `kappa_geom L_geom` in v5.4 is already a quadratic fluctuation slot and is not a foundational bulk Einstein-Hilbert action. No theorem maps `kappa_geom` to `c_K`, `c_K2`, or `c_S`, and no Gibbons-Hawking-York coefficient can be imported without a normalized bulk source.

The v5.7 assignments `c_K=c_K2=c_S=0` only removed scalar variations on fixed normalized geometry. They are not geometric vanishing theorems. `c_J=0` prevents a duplicate standalone `log J` term; it does not remove `J` from the collar measure.

## Scalar vacuum localization

The reduced functional is

```text
V_red(sigma) = -sigma^2 + 2 sigma^4,
V_red(1/2) = -1/8.
```

This is a coordinate-normalized mode-space functional value. Its v5.7 component ledger combines mixing `-3`, threshold quadratic `-2`, and a quartic boundary/collar kernel `8`, while explicit boundary, collar, and geometry-measure contributions were recorded as zero in that fixed reduction. The repository supplies no inverse projection that determines which local boundary or collar density produced `-1/8`.

Consequently:

```text
V_red -> U_boundary       is open
V_red -> B_collar         is open
T_boundary physical value is null.
```

The normalized sign is not promoted to a physical tension sign.

## Stress, geometry, and pressure

The boundary stress convention is

```text
delta S_boundary
  = 1/2 integral_Sigma dmu_h tau_boundary^AB delta h_AB
    + field variations,

tau_boundary^AB
  = (2/sqrt|h|) delta S_boundary/delta h_AB.
```

For a metric-independent localized density, the pure area contribution would be `U_boundary h^AB`. The actual `U_boundary` response, curvature stresses, collar stress, and scalar stress remain unevaluated because their local sources are open.

For the reference convention `K_AB=(1/2)L_n h_AB` and outward normal,

```text
delta h_AB       = 2 xi_perp K_AB
delta dmu_h      = K xi_perp dmu_h
delta K          = -Delta_Sigma xi_perp
                   -(Tr(S^2)+Ric(n,n))xi_perp
delta log J      = Tr[(I+rho S)^(-1)rho delta S]
delta(J dmu_h)   = J(K xi_perp+delta log J)dmu_h.
```

BHSM stores `J=det(I +/- rho S)`, so the actual orientation sign remains open and must flip orientation-odd quantities consistently.

Pressure is defined by the normal variation coefficient `Delta p=p_inside-p_outside`. The repository does not set exterior pressure to zero. Scalar, collar, geometric, excitation, and local quantum pressures remain open; gauge and fermion pressures vanish only conditionally on the declared zero backgrounds. No hot-plasma equation of state is inserted.

## Shape equation and Hessian

The source-separated architecture is

```text
F_boundary = T_boundary+c_K K+c_K2 K^2+c_S Tr(S^2)

E_perp = epsilon_n K F_boundary
       + D_K^dagger(c_K+2c_K2 K)
       + D_Q^dagger(c_S)
       + E_J+E_collar+p_ST+E_quantum-Delta p.
```

Every term has either a stored candidate source or an explicit open status. `E_quantum` is open as a local term: v5.10 supplies only a global scale derivative.

The surface Hessian and eigenproblem are

```text
H_surface = delta E_perp/delta xi_perp,
H_surface xi_n = lambda_n xi_n,
lambda_surface = min spec'(H_surface).
```

Its formal principal symbol is

```text
B_eff |k|^4 + T_eff |k|^2.
```

The candidate scaling architecture remains

```text
lambda_surface =
    T_boundary q_tau/L^2
  + c_K q_K/L^3
  + (c_K2 q_K2+c_S q_S)/L^4
  + lambda_collar+lambda_ST+lambda_quantum.
```

The powers follow from the area-Jacobi, single-curvature, and bending variations. Collar, scalar, and quantum powers cannot be fixed before localization. No uniform-only spectrum assumption is made. On a closed Berger surface the formal integration boundary form vanishes, but collar endpoint/matching data and the physical self-adjoint domain remain open.

## Competing-scaling and release theorem

The candidate release condition is `lambda_surface(L_c)=0`. A single nonzero homogeneous contribution `A L^-p` cannot have an isolated positive finite zero: `L^-p` is nonzero for every finite `L>0`, so the equation requires `A=0`, which gives an identically flat direction rather than a threshold.

A physical crossing therefore requires at least two sourced contributions, different scaling or non-polynomial dependence, opposing signs on the physical branch, and a valid self-adjoint physical mode. The deterministic model

```text
lambda_red=A2/L^2+A3/L^3+A4/L^4
```

reduces the root equation to `A2 L^2+A3 L+A4=0` and exactly distinguishes stable-to-unstable, reverse, tangential, multiple, and absent crossings. Its representative coefficients are algebra tests, not BHSM values.

The physical result remains:

```text
L_c = null
number of roots = unresolved
crossing direction = unresolved
absolute unit = not derived.
```

## One-scale, quantum, pilot-wave, and energy boundaries

A dimensionful primitive is necessary for physical localization, but current data do not prove it is sufficient. Because the dimensionless ratios and shape data remain open, v5.12 cannot claim `BHSM_MINIMAL_ONE_SCALE_BOUNDARY_PRINCIPLE_REQUIRED`. A future candidate could have a dimensionally derived form such as `L_c=C_L([hbar]/T_primitive)^(1/d_Sigma)`, but neither `C_L` nor that BHSM law is currently derived.

The v5.10 relations `dGamma/dL=-1/L` and `d^2Gamma/dL^2=1/L^2` remain global and `mu`-dependent. They are stored separately and are not used as local pressure or Casimir stress.

The v5.9 guidance equation is outward only on an outgoing `k>0` branch. That branch is not selected by the current boundary action, and the threshold is absent from the v5.9 Hamiltonian. Keeping the layers separate prevents double counting.

Primordial conversion remains the formal ledger

```text
E_initial = E_expansion+E_plasma+E_residual.
```

No time split, Hamiltonian boundary energy, conversion mechanism, temperature, abundance, baryogenesis, or reheating result is derived.

## Open gates

Principal blockers are `OPEN_MISSING_PHYSICAL_BOUNDARY_DOMAIN_SIGNATURE`, `OPEN_MISSING_SCALAR_TOPOGRAPHIC_PHYSICAL_LOCALIZATION_MAP`, `OPEN_MISSING_ABSOLUTE_BOUNDARY_TENSION_DENSITY_SOURCE`, `OPEN_MISSING_COMPLETE_SCALAR_TOPOGRAPHIC_COLLAR_ACTION`, `OPEN_MISSING_BOUNDARY_EMBEDDING_AND_SHAPE_VALUES`, `OPEN_MISSING_BOUNDARY_SHAPE_COEFFICIENT_VALUES`, `OPEN_MISSING_BULK_GEOMETRIC_ACTION_NORMALIZATION`, `OPEN_MISSING_STATIC_INSIDE_OUTSIDE_PRESSURE_SOURCE`, `OPEN_MISSING_NORMAL_DISPLACEMENT_DOMAIN_AND_SPECTRUM`, `OPEN_MISSING_LOCAL_QUANTUM_SURFACE_STRESS`, `OPEN_MISSING_PRIMORDIAL_RELEASE_ENERGY_CONVERSION`, `OPEN_MISSING_ABSOLUTE_UNIT_ANCHOR`, and `FULL_BHSM_NOT_COMPLETE`.

No measured input, physical Casimir energy, absolute unit, primordial rupture history, hot plasma production, particle mass, gauge coupling, fine-structure constant, CKM result, rare-B prediction, or full BHSM completion is claimed.

Command: `python -m bhsm.interface primordial-boundary-tension-status --format markdown`.
