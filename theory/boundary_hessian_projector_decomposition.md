# Boundary Hessian Projector Decomposition

Candidate decomposition:

```text
H_boundary_candidate =
mu_ref P_ref
+ mu_orient P_orient
+ mu_cyclic P_cyclic
+ mu_excess P_excess
```

Projector meanings:

```text
P_ref: reference/single closure sector
P_orient: Z2 orientation-pair sector
P_cyclic: cyclic three-channel sector
P_excess: remaining higher/composite closure sector
```

Candidate orthogonality/completeness:

```text
P_i P_j = 0 for i != j
P_ref + P_orient + P_cyclic + P_excess = I
```

Candidate stability hierarchy:

```text
mu_ref = 0 or reference-normalized
0 < mu_orient < mu_excess
0 < mu_cyclic < mu_excess
mu_excess >= gap
```

| projector | closure dimension | interpretation | low-energy selected | eigenvalue | status | finite block |
| --- | --- | --- | --- | --- | --- | --- |
| P_ref | 1 | reference/single closure | true | 0 | reference-normalized | C |
| P_orient | 2 | orientation-pair closure | true | 1 | stable low-energy | M2(C) |
| P_cyclic | 3 | cyclic three-channel closure | true | 1 | stable low-energy | M3(C) |
| P_excess | >=4 | higher/composite/excess closure | false | 10 | gapped/excess | higher/composite |

Required guardrail: this is a candidate Hessian decomposition, not the full Hessian proof.

## Related Second-Variation Audit

The [Boundary Action Second-Variation Audit](boundary_action_second_variation_audit.md) computes the local candidate Hessian coefficients for the finite action-term diagnostics supporting this decomposition.

Related theorem scaffold: [Theorem-Level Boundary Action Derivation Scaffold](theorem_level_boundary_action_derivation.md).

Related discharge attempt: [Theorem Discharge: Phase, Orientation, And Cyclic Closure](theorem_discharge_phase_orientation_cyclic.md).
