# Unified Dynamical Action Construction v5.4

Sprint: `bhsm-unified-dynamical-action-construction-v5-4`

Primary result: `UNIFIED_BHSM_ACTION_CONSTRUCTED_CONDITIONALLY`

BHSM v5.4 constructs the strongest explicit unified symbolic action currently supported by the repository. It upgrades the older sector-sum skeleton into a configuration-space definition, term-by-term action candidate, coefficient/dimension ledger, variational system, boundary-condition statement, quadratic operator extraction, interaction-source map, dimensionful-scale analysis, and deterministic reduced model.

The construction remains conditional because physical scale generation, coefficient derivation, gauge/current normalization, lower-order operator completion, and nonlinear solution theory remain open.

## Unified Action

```text
S_BHSM^cand
  =
  integral_Sigma [
      L_geom
    + sum_i L_gauge,i
    + L_fermion
    + L_topographic
    + L_charged
    + L_neutral
    + L_scale
  ] dmu_Sigma,rho
```

The measure is the relative Berger/collar boundary measure:

```text
dmu_Sigma,rho = sqrt(det h_rho) d^3x
```

The construction uses `h_rho`, `rho`, `A_i`, `Psi`, `Phi`, `J_ch`, `N`, sector projectors `P_i`, and generation/mode projectors `P_gen`. The projectors and geometric labels are fixed data in this sprint; `rho`, `A_i`, `Psi`, `Phi`, `J_ch`, and `N` are the active symbolic variables.

## Action Terms

```text
L_geom:
  1/2 kappa_geom <delta h, L_geom(rho) delta h>

L_gauge,i:
  1/(2 lambda_i) <A_i, L_i(rho) A_i>

L_fermion:
  zeta_psi Re <Psi, D_BH(h,A,P) Psi>

L_topographic:
  1/2 kappa_phi <Phi, L_phi(rho) Phi> + V_topo(Phi; rho)

L_charged:
  g_ch Re <J_ch(P_gen Psi,A_SU2), X_ch(P_ch Psi)>

L_neutral:
  g_neu <N, R_neu(Phi,h,rho)> + 1/2 <N, K_neu N>

L_scale:
  1/2 kappa_scale (rho-rho_*)^2 + C_Lambda(Phi,h,rho; Lambda_BH)
```

Every coefficient remains explicitly named and dimensioned. Unknown coefficients are symbolic, not fitted.

## Variation

The constructed action produces symbolic operator equations for:

```text
delta h
A_i
Psi
Phi
N
rho
```

Representative equations:

```text
(1/lambda_i) L_i(rho) A_i + J_i^matter + J_i^charged = 0

zeta_psi D_BH Psi + g_ch delta J_ch/delta Psibar
  + neutral/scalar source terms = 0

K_neu N + g_neu R_neu(Phi,h,rho) = 0
```

Boundary terms vanish only under the declared boundary conditions: fixed induced metric or natural geometric flux cancellation, gauge-fixed/coexact boundary domain, Hermitian spinor boundary pairing, scalar/topographic Dirichlet or natural Neumann condition, neutral admissible cone/domain, and fixed or stationary collar scale.

## Quadratic Dynamics

The v5.4 Hessian is a block symbolic operator. It contains:

```text
kappa_geom L_geom
(1/lambda_i) L_i(rho)
zeta_psi D_BH
kappa_phi L_phi + Hess(V_topo)
K_neu
kappa_scale + Hess_rho(C_Lambda)
```

Inverse/Green/resolvent operators remain conditional. No inverse is invented where gauge redundancy, zero modes, boundary domain, neutral scale, or physical normalization remain open.

## Interaction Structure

The action structurally supports:

```text
charged-current source terms
neutral-response source terms
sector/projector-conditioned couplings
generation/mode-labeled charged transport
conditional mode-mediated effective interactions by Schur complement
```

It does not close rare-B FCNC generation, Wilson coefficients, or rare-B observables. Those remain downstream.

## Dimensional Structure

All terms are dimensionless in powers of a geometric length unit `ell_BH`. A physical conversion scale remains explicit:

```text
Lambda_BH
```

Status:

```text
OPEN_MISSING_PHYSICAL_SCALE_GENERATION
```

## Reduced Computable Model

The reduced model is:

```text
S_red = 1/2 kappa_g a^2 + 1/2 kappa_phi phi^2 + epsilon a phi
```

with deterministic parameters:

```text
kappa_g = 2
kappa_phi = 3
epsilon = 0.5
```

Equations:

```text
kappa_g a + epsilon phi = 0
epsilon a + kappa_phi phi = 0
```

The stationary solution is `(a,phi)=(0,0)`, the residual is exactly zero in the deterministic model, the Hessian determinant is positive, and the mode spectrum is positive. This demonstrates coupled equations, a mode spectrum, and a stability condition. It is not a physical fit.

## Preserved Claim Boundary

BHSM v5.4 does not derive physical gauge couplings, `g2_BH`, `alpha_i`, CKM coefficient value, CKM exponent, rare-B Wilson coefficients, `q0^2`, exact rare-B node coordinates, physical mass scales, or full BHSM completion.

Run:

```bash
python -m bhsm.interface unified-dynamical-action-status --format markdown
```
