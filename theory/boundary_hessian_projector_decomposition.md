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

## Related Candidate Term Realization

The companion [Boundary Action Term Realization Audit](boundary_action_term_realization_audit.md) realizes the action-term labels as finite diagnostics that support this projector decomposition while leaving the full Hessian proof open.
