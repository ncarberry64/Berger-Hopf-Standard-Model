# Current-Green longitudinal/transverse linear defect

The accepted same-center outward contraction already certifies the frozen
preconditioner's full 74-dimensional linear defect.  Its retained Arb shards
provide the interval matrices `C_i`, `DL_i`, and `DR_i` in the causal
recurrence.  No action evaluation is repeated here.

At each post-reset node let `a_i` be the fixed normalized binary axis used by
the current Green central and mixed campaigns, and let

```text
P_i = a_i a_i^T,    Q_i = I - P_i.
```

For every causal source block `B_ij`, the four resolved operators are

```text
P_i B_ij P_j,  P_i B_ij Q_j,
Q_i B_ij P_j,  Q_i B_ij Q_j.
```

The two longitudinal-input blocks are evaluated by propagating only
`B_ij a_j` in Arb and are summed in the same causal block-sup convention as
the parent certificate.  Both transverse-input entries reuse the certified
full row bound directly, because orthogonal projection and restriction cannot
increase the Euclidean operator norm.  This reduces exact recurrence width by
a factor of 74.  It is deliberately conservative but preserves interval
authority.

This unit certifies only the linear `Z1` block.  It does not supply the
outward transverse quadratic neighborhood, the two-radius self-map and
contraction, Gate 7, or BHSM completion.
