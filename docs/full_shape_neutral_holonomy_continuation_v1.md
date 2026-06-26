# Full Shape / Neutral / Holonomy Continuation v1

Current public status: structural architecture integrated conditional; numerical closure open.

This sprint installs structural theorem-kernel diagnostics for charged shape
freeze, neutral minimal Hessian/bridge structure, CKM/PMNS structural sources,
and boundary relative-holonomy CP candidates. It does not change frozen or
official predictions and does not claim numerical closure.

## Charged Effective Bridge Balance

At candidate settings

```text
rho_ch=3
g_bridge=16/189=(1/21)(4/3)^2
```

the bridge records give:

```text
Pi_l=1/7, Pi_u=2/7, Pi_d=4/7
||v_l||^2=7, ||v_u||^2=7, ||v_d||^2=19
beta_l=kappa_l=16/1323
beta_u=32/1323, kappa_u=16/1323
beta_d=64/1323, kappa_d=16/3591
(beta_l/kappa_l, beta_u/kappa_u, beta_d/kappa_d)=(1,2,76/7)
```

With `D_u=1/2`, the up effective balance is `1`. The down sector remains a
bottleneck candidate.

Statuses:

```text
rho_ch_3_effective_bridge_balance=DERIVED_CONDITIONAL_ON_COLORLESS_LEPTON_BALANCE_AND_UP_THRESHOLD_PROJECTION
down_bridge_bottleneck_76_over_7=STRUCTURALLY_SUPPORTED_CANDIDATE
rho_ch_exact_value=OPEN_LOCALIZABLE
```

## Charged Shape-Freeze Candidate

Using full tridiagonal `K_f` operators with Rule-A suppression, `rho_ch=3`,
`g_bridge=16/189`, and the derived-only up `(6,0)` `ln 2` threshold, the
internal eigen-gap shape diagnostics are:

```text
S_l^K approx 2.769118200
S_u^K approx 1.732090337
S_d^K approx 1.037027926
S_l^K - S_d^K - S_u^K approx -6.3e-8
```

The symbolic shape vector

```text
S_d=28/27
S_u=sqrt(3)
S_l=sqrt(3)+28/27
```

is retained as a strongly supported candidate, not an exact theorem or frozen
prediction.

## Neutral Minimal Hessian and PMNS Source

Neutral candidate:

```text
H_nu=[[1,1],[1,2]]
det(H_nu)=1
N_nu(q,j)=q^2+2qj+2j^2
N_nu(3,0)=9
N_nu(1,1)=5
v_nu=(-2,1)
v_nu^T H_nu v_nu=2
```

Neutral bridge candidate:

```text
eta_nu=1/3
g_nu=1/3
beta_nu=1/3
kappa_nu=1/6
theta_01^nu=1/9
theta_12^nu=1/8
theta_02^nu=1/90
```

PMNS structural source remains candidate only:

```text
PMNS_structural_source=STRONGLY_SUPPORTED_CANDIDATE
PMNS_numerical_closure=OPEN
```

## CKM Structural Source

The CKM structural diagnostic records the contrast:

```text
down: N_d1=27, N_d2=28, gap=1
up: N_u1=36, N_u2=67, threshold gap=1178/147 - ln2
theta_12^d=28/2907
theta_12^u=(16/1323)/(1178/147 - ln2)
```

Status:

```text
CKM_structural_source=STRONGLY_SUPPORTED_CANDIDATE
CKM_real_mixing_source=DOWN_NEAR_DEGENERACY_VS_UP_THRESHOLD_GAP
CKM_numerical_closure=OPEN
```

## Boundary Relative-Holonomy CP Candidate

Complex tridiagonal edge phases preserve single-sector spectra by diagonal
rephasing on the tridiagonal tree, but relative cross-sector holonomy can remain
physical in sector comparisons.

```text
single_sector_spectrum_phase_invariance=DERIVED_CONDITIONAL_ON_TRIDIAGONAL_TREE_REPHASING
boundary_relative_holonomy_CP_source=STRUCTURALLY_MOTIVATED_CANDIDATE
Z6_boundary_phase_holonomy=STRUCTURALLY_MOTIVATED_CANDIDATE
CKM_CP_closure=OPEN
PMNS_CP_closure=OPEN
```

The candidate primitive phase is `exp(i*pi/3)`. CP smallness remains only a
structural candidate because no direct real `0<->2` bridge is present, so
CP-odd leakage is second order in `beta*kappa`.

## Remaining Open Blockers

- absolute same-sector mass ratios
- cross-sector transported mass ratios
- residual RG coefficients
- full scheme/common-scale alignment
- exact action derivation of `g_bridge=16/189`
- exact action derivation of boundary phase source
- neutral eta/beta/kappa final derivation
- neutral threshold rules
- PMNS numerical closure
- CKM numerical closure
- CP numerical closure
- final comparison-ready prediction package

No observed masses, CKM data, PMNS data, neutrino data, empirical target ratios,
or measured particle values are used as derivation inputs.

Frozen predictions changed: no.

Official predictions changed: no.
