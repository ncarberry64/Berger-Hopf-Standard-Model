# BHSM v10.4 support-action derivation

## Covariant audit class

On `M_regular`, the smallest local second-order class compatible with the
selected field is

```text
S_upsilon = integral sqrt(-G) [
  -1/2 Z(upsilon) |nabla upsilon|^2 - U(upsilon)
  + (F_C(upsilon)-1) X_C + (F_W(upsilon)-1) X_W
] + S_Sigma_core.
```

The subtraction makes reduction to the frozen action at `upsilon=1`
explicit when `F_C(1)=F_W(1)=1`. Regular background stationarity requires
`U'(1)=0` and `sum_a F_a'(1) X_a,*=0`. Stability requires the full constrained
`U_eff''(1)` to be nonnegative.

The Euler equation is

```text
nabla_A(Z nabla^A upsilon)
- 1/2 Z' |nabla upsilon|^2
- U' + F_C' X_C + F_W' X_W = 0.
```

The scalar stress before the coupling variations is

```text
T_AB = Z nabla_A upsilon nabla_B upsilon
       - G_AB [1/2 Z |nabla upsilon|^2 + U].
```

The two support couplings are required as an audit class so the new field is
not promoted as a spectator. Their common-domain invariant owners and Taylor
coefficients are not supplied by the frozen action.

## Non-uniqueness theorem

Covariance, dimensions, the endpoint range, and regular-background conditions
do not select the functions. Two inequivalent healthy examples are:

| family | positive kinetic function | canonical depth |
| --- | --- | --- |
| constant | `Z=zeta*kappa_1` | `sqrt(zeta*kappa_1)(1-upsilon)` |
| logarithmic | `Z=zeta*kappa_1/upsilon^2` | `-sqrt(zeta*kappa_1)log(upsilon)` |

Both have one positive local scalar polarization for `zeta*kappa_1>0`, but
the core lies at finite canonical distance in the first and infinite distance
in the second. The fixed range prevents this difference from being dismissed
as an arbitrary field rescaling. Potentials and support couplings add further
inequivalent choices.

No new particle data were used. A cosmic unit anchor could later convert a
selected coefficient to units, but cannot choose its dimensionless ratio.

Primary verdict:
`BHSM_MULTIPLE_INEQUIVALENT_SUPPORT_ACTIONS_REMAIN_AFTER_AUTHOR_EXTENSION_SELECTION`.

Exact next object:
`ACTION_PRINCIPLE_FIXING_Z_UPSILON_U_UPSILON_AND_SUPPORT_COUPLINGS`.
