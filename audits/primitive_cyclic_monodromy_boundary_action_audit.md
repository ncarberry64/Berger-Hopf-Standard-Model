# BHSM Primitive Cyclic Monodromy from Boundary Action

This sprint tests whether the Berger-Hopf boundary-action scaffold defines a primitive finite cyclic monodromy whose order is `|Omega_f|`.
The result is partial: the symbolic Wilson-loop boundary action defines `U_f` and exact cyclic arithmetic works, but primitive closure is not forced by finite action alone.

## Summary

Primitive cyclic monodromy: `PRIMITIVE_CYCLIC_MONODROMY_PARTIAL`
Boundary action monodromy: `BOUNDARY_ACTION_MONODROMY_PARTIAL`
Wilson-loop monodromy: `WILSON_LOOP_MONODROMY_PARTIAL`
Boundary phase matching: `BOUNDARY_PHASE_MATCHING_STRUCTURAL_CANDIDATE`
Self-adjoint monodromy: `SELF_ADJOINT_MONODROMY_STRUCTURAL_CANDIDATE`
Hopf primitive orbit: `HOPF_PRIMITIVE_ORBIT_PARTIAL`
Topological boundary term: `TOPOLOGICAL_BOUNDARY_TERM_STRUCTURAL_CANDIDATE`
dim(H)=|Omega|: `DIM_H_EQUALS_ABS_OMEGA_PARTIAL`
Lepton 8/9 consequence: `LEPTON_8_9_CHANNEL_RULE_CONDITIONAL_STRENGTHENED`

## Boundary-Action Mechanism

```text
S_hol = integral_gamma <psi, i D_gamma psi>
D_gamma = d/ds + i A_rep(gamma_dot)
A_rep = A_q tensor O_q + A_j tensor O_j
Omega_f = O_q q + O_j j
psi(1) = U_f psi(0),  U_f = P exp(i integral_gamma A_rep)
```

Boundary action defines U_f: `True`
Variation forces parallel transport: `True`
Finite action forces primitive closure: `False`
U_f has order |Omega_f| in the primitive cyclic model: `True`

## Sector Monodromy

| Sector | Omega | Order | dim(H_f) | Orbit states | Primitive check |
| --- | ---: | ---: | ---: | --- | --- |
| `charged_lepton` | `3` | `3` | `3` | `[0, 1, 2]` | `True` |
| `up` | `6` | `6` | `6` | `[0, 1, 2, 3, 4, 5]` | `True` |
| `down` | `12` | `12` | `12` | `[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]` | `True` |

## Preferred Dimension Route

Preferred route: `cyclic_boundary_monodromy`
S2 geometric quantization used for channel dimension: `False`
Geometric quantization plus-one hazard: `True`
Rejected/limited route note: `S2_GEOMETRIC_QUANTIZATION_NOT_USED_FOR_CHANNEL_DIMENSION`

Ordinary S2 geometric quantization is not used for BHSM channel counting here; it remains a hazard route because line-bundle conventions can produce an `n+1` dimension.

## Blockers Closed

- boundary_action_defines_Wilson_loop_monodromy_operator
- variation_gives_parallel_transport_in_symbolic_boundary_action
- exact_integer_orbit_arithmetic_for_3_6_12

## Blockers Remaining

- derive primitive finite cyclic quotient from the completed boundary action
- fix A_j normalization and global bundle coupling without convention dependence
- prove orbit states C[Z_|Omega_f|] are the physical boundary channel states
- derive stochastic dressing action on End(H_f) from the full BHSM dynamics

## Normalization Ambiguities

- A_j may be a Berger/base curvature or coframe component rather than a line holonomy
- global A_j normalization is not uniquely fixed by the completed boundary action
- finite cyclic order requires the primitive boundary quotient rather than ordinary S2 quantization

## Claim Safety

- No official frozen outputs are changed.
- No retuning is performed.
- No frozen lepton or quark dressing rule is changed.
- No neutrino speed anomaly claim is made.
- No lab-scale environmental mass-drift claim is made.
- No Standard Model replacement claim is made.
