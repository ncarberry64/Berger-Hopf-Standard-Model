# BHSM Explicit Hopf-Berger Boundary One-Forms

This sprint introduces symbolic Hopf/Berger boundary geometry components without changing frozen predictions.

## Summary

Explicit Hopf-Berger oneform status: `EXPLICIT_HOPF_BERGER_ONEFORMS_PARTIAL`
A_q status: `A_Q_EXPLICIT_HOPF_FIBER_ONEFORM_SUPPORTED`
A_j status: `A_J_EXPLICIT_BERGER_BASE_COMPONENT_SUPPORTED`
Hopf normalization status: `HOPF_NORMALIZATION_RESOLVED`
Berger/base normalization status: `BERGER_BASE_NORMALIZATION_CONVENTION_DEPENDENT`
q=k-2j status: `Q_EQUALS_K_MINUS_2J_REPRESENTATION_SUPPORTED`
Reproduces Omega_l,u,d: `True`
Closes boundary connection: `False`
Promotes lepton 8/9: `False`

## Symbolic One-Forms

```text
sigma_1 = cos(psi) dtheta + sin(psi) sin(theta) dphi
sigma_2 = -sin(psi) dtheta + cos(psi) sin(theta) dphi
sigma_3 = dpsi + cos(theta) dphi
A_Hopf = sigma_3
A_Hopf_norm = sigma_3/(2*pi)
F_Hopf = dA_Hopf = -sin(theta) dtheta wedge dphi
```

The Hopf/fiber component supports `A_q`. The Berger/base component is recorded as a curvature/coframe component because the full boundary-action coupling is not yet derived.

## Representation Operators

```text
O_q = 3B - L
O_j = -4T3 + 2(3B)(1/2 - T3)
Omega_f = O_q q + O_j j
```

| Sector | O_q | O_j | Candidate Only |
| --- | ---: | ---: | --- |
| `charged_lepton` | `-1` | `2` | `False` |
| `up` | `1` | `-2` | `False` |
| `down` | `1` | `4` | `False` |
| `neutrino` | `-1` | `-2` | `True` |

## Mode Pair Checks

| Sector | Constant | Level |
| --- | --- | ---: |
| `charged_lepton` | `True` | `3` |
| `up` | `True` | `6` |
| `down` | `True` | `12` |

## Normalization Ambiguities

- Euler-angle period and 2*pi normalization conventions must be fixed globally.
- The Berger/base j-channel may be a curvature or coframe flux component rather than a line holonomy.
- No full boundary-action coupling fixes the A_j normalization uniquely.

## Blockers Remaining

- derive A_j coupling from the full Berger-Hopf boundary action
- fix Berger/base normalization globally rather than by convention
- prove A_rep is a true connection on the boundary tensor-product bundle
- derive dim(H)=|Omega| separately
- derive identity/traceless stochastic protection before promoting lepton 8/9

## Claim Safety

- No official frozen outputs are changed.
- No retuning is performed.
- No neutrino speed anomaly claim is made.
- No lab-scale mass variation claim is made.
- No Standard Model replacement or full derivation claim is made.
- Lepton 8/9 remains unpromoted.
