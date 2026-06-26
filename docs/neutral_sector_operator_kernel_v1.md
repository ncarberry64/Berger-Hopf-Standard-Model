# Neutral Sector Operator Kernel v1

Current public status: structural architecture integrated conditional;
numerical closure open.

This sprint starts the neutral/neutrino operator scaffold. It does not compute
neutrino masses, PMNS angles, mass splittings, or cosmological neutrino
constraints.

## Sector Ledger

The neutrino sector ledger is kept as the sector-engine result:

```text
q + 2j = 3
L_nu = [(0,0), (3,0), (1,1)]
v_nu = (1,1) - (3,0) = (-2,1)
neutrino_mode_ledger=DERIVED_CONDITIONAL_ON_SECTOR_ENGINE
```

## Neutral Hessian

The charged stiffness form is not automatically reused. The neutral/topographic
sector keeps a symbolic Hessian:

```text
H_nu_raw = [[a,b],[b,c]]
N_nu(q,j)=a q^2 + 2b qj + c j^2
a>0, c>0, ac-b^2>=0
neutral_Hessian_symbolic_form=OPEN_LOCALIZABLE
```

## Candidate Branches

| branch | Hessian | status | role |
| --- | --- | --- | --- |
| N0 | `a=1,b=0,c=1` | `NEUTRAL_HESSIAN_BRANCH_CANDIDATE` | isotropic diagnostic |
| N1 | `a=1,b=0,c=rho_ch` | `STRUCTURALLY_POSSIBLE_NOT_DERIVED` | charged-like placeholder |
| N2 | `a=1,b=1,c=2` | `STRUCTURALLY_MOTIVATED_CANDIDATE` | topographic mixed diagnostic |
| N3 | tangent diagnostics for `v_nu=(-2,1)` | `OPEN_LOCALIZABLE` | tangent-adapted source remains open |

No branch is selected and no branch is numerically closed.

## Neutral Operator Template

The symbolic neutral operator has tridiagonal topology:

```text
K_nu =
[ 0        beta_nu       0
  beta_nu  lambda_1,nu   kappa_nu
  0        kappa_nu      lambda_2,nu ]

lambda_i,nu = eta_nu N_nu(q_i,j_i)
```

The sources remain open:

```text
neutral_eta_source=OPEN_LOCALIZABLE
neutral_beta_bridge_source=OPEN_LOCALIZABLE
neutral_kappa_bridge_source=OPEN_LOCALIZABLE
```

Diagnostic readout modes are available, but they are not physical predictions:

```text
NEUTRAL_OPERATOR_SYMBOLIC
NEUTRAL_OPERATOR_UNIT_DIAGNOSTIC
NEUTRAL_OPERATOR_TOPOGRAPHIC_MIXED_DIAGNOSTIC
```

## Thresholds

No neutral threshold dressing is currently derived.

| slot | mode | status |
| ---: | --- | --- |
| 0 | `(0,0)` | `REFERENCE_SLOT_NOT_THRESHOLD_TARGET` |
| 1 | `(3,0)` | `NO_THRESHOLD_SOURCE_FOUND` |
| 2 | `(1,1)` | `NO_THRESHOLD_SOURCE_FOUND` |

```text
neutral_threshold_operator=OPEN
```

## PMNS Preparation

The structural placeholder is:

```text
U_PMNS = U_l^dagger U_nu
PMNS_structural_source=STRUCTURALLY_MOTIVATED_CANDIDATE
PMNS_numerical_closure=OPEN
```

PMNS angles should not be computed until both charged and neutral operators are
fully derived and frozen.

## Verdict

```text
neutral_sector_operator_kernel_v1=STRUCTURALLY_MOTIVATED_CANDIDATE
neutral_numerical_closure=OPEN
numerical_closure=OPEN
```

No observed neutrino masses, neutrino mass splittings, PMNS data, observed
charged masses, measured alpha, cosmological neutrino bounds, or empirical
target ratios are used.

Frozen predictions changed: no.

Official predictions changed: no.
