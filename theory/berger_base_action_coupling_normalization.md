# BHSM Berger-Base Action Coupling and Normalization

This sprint tests whether the Berger/base component `A_j` can be treated as an action-coupled boundary object.
The result is partial: a universal minimal-coupling scaffold is recorded, while full action variation and global normalization remain open.

## Summary

Berger/base action coupling status: `BERGER_BASE_ACTION_COUPLING_PARTIAL`
A_j action coupling status: `A_J_ACTION_COUPLING_PARTIAL`
A_j geometric object status: `A_J_GEOMETRIC_OBJECT_SUPPORTED`
A_rep true connection status: `A_REP_TRUE_CONNECTION_PARTIAL`
Base curvature normalization status: `BASE_CURVATURE_NORMALIZATION_CONVENTION_DEPENDENT`
Horizontal coframe coupling status: `HORIZONTAL_COFRAME_COUPLING_PARTIAL`
Does A_j have action coupling: `True`
Does A_j normalization become global: `False`
Does A_rep act on boundary tensor bundle: `True`
Does A_rep reproduce Omega_l,u,d: `True`
Closes boundary connection: `False`
Promotes lepton 8/9: `False`

## Candidate Boundary Coupling

```text
D_boundary_rep = d + i A_q tensor O_q + i A_j tensor O_j
S_boundary = integral_boundary sqrt(g_Berger) <D_boundary_rep psi, D_boundary_rep psi>
O_q = 3B - L
O_j = -4T3 + 2(3B)(1/2 - T3)
```

## Geometry

```text
sigma_1 = cos(psi) dtheta + sin(psi) sin(theta) dphi
sigma_2 = -sin(psi) dtheta + cos(psi) sin(theta) dphi
sigma_3 = dpsi + cos(theta) dphi
A_q = sigma_3/(2*pi)
F_Hopf = dA_Hopf = -sin(theta) dtheta wedge dphi
g_Berger = r_base^2 (sigma_1^2 + sigma_2^2) + r_fiber^2 sigma_3^2
```

## Mode Pair Checks

| Sector | Omega values |
| --- | --- |
| `charged_lepton` | `(Fraction(3, 1), Fraction(3, 1))` |
| `up` | `(Fraction(6, 1), Fraction(6, 1))` |
| `down` | `(Fraction(12, 1), Fraction(12, 1))` |

## Normalization Ambiguities

- Chern-unit and raw-sphere base flux conventions differ by a factor of 2.
- The boundary action has not fixed whether A_j is a spin connection, curvature channel, coframe channel, or Casimir term.
- The down-sector colored-lower bonus is supported by projectors but not yet derived from a full color/coframe boundary action.

## Blockers Remaining

- derive the minimal boundary coupling from the complete Berger-Hopf action variation
- globally fix A_j normalization without convention choice
- prove A_rep is a true connection on the completed boundary tensor bundle
- derive dim(H)=|Omega| separately
- derive identity/traceless stochastic protection before promoting lepton 8/9

## Claim Safety

- No official frozen outputs are changed.
- No retuning is performed.
- No neutrino speed anomaly claim is made.
- No lab-scale mass variation claim is made.
- No Standard Model replacement or full derivation claim is made.
- Lepton 8/9 remains unpromoted.
