# Interval-14 entry 73 <- 14: shared-parameter feasibility

The retained Hessians certify a small linear state dependence for this
entry. They do not yet certify its uniform higher-order remainder. Interval
13 remains a frozen lemma and was not recomputed.

## Shared representation

Let `P = R_frozen^-1 T`, `u = E_right e_14`, and let `h` be interval 14's
original step. Use the SAME state parameters in

```
A(theta) = DF(endpoint_15(theta)) u
w(theta) = u/2 - h A(theta)/8
B(theta) = DF(midpoint_14(theta)) w(theta)
a(theta) = e_73^T [-P u + h P A(theta)/6 + 2h P B(theta)/3].
```

Here `a` is DR[73,14]; its identity contribution is zero. These identities
are the repository's physical Hermite–Simpson chain rule. In particular,
`w` must not be independently boxed after calculating `A`.

The candidate enclosure is `a(theta) = a0 + J_a theta + e_a(theta)`.
Keep the selected eigenpair, bordered response, their directional
corrections, normalization, and endpoint/midpoint incidence in a common
Taylor parameter domain. Form the projected residual `Y - beta G` before
relaxing solve corrections, using the retained equations `G=0`. When
bounding the final vector, also keep cross-output coefficients through
the causal maps and transverse projection before taking support norms.
This is a representation route, not an already evaluated interval-14
nonlinear model.

## What the frozen Hessians supply

For source output row 73, let Q be the saved local half-Hessian, with
endpoint slots 0/1 and full transverse-coordinate input convention. The
first state variation of the right input column 14 is exactly represented
by the following retained coefficients:

```
da = 2 LT01[14] l_left + 2 LT11[14] l_right
   + (TT01[:,14] + TT10[14,:]) . t_left
   + (TT11[:,14] + TT11[14,:]) . t_right.
```

The signed shared coefficients are combined before their norms. On the
unchanged original radius product, conservative decimal upper bounds are:

| Part of the entry's linear state dependence | Upper bound |
| --- | ---: |
| LT | 2.067900821e-7 |
| TT | 9.368881458e-7 |
| LT + TT | 1.143678228e-6 |

LT is already included in the global selected LL/LT quadratic budget; it is
not charged again. TT is not yet included there. These bounds concern the
linear Taylor polynomial of the derivative entry, not its higher-order
error over the full domain.

## Full-history cost and sufficient nonlinear target

A unit error in this output coordinate is injected at node 15 and propagated
through all subsequent signed frozen maps. The certified transverse gain is
at most 131.433949143, including the existing frozen-map perturbation lemma.
The stored-map maximum occurs at node 301. The radius-domain support of
input coordinate 14 is at most 2.176630744562e-9, using the existing Euclidean
transverse input superset without splitting the input vector into boxes.

Consequently an isolated unaccounted derivative-entry error bounded by
`epsilon` costs at most `2.860831745829e-7 * epsilon` in the full-history
transverse value remainder. This uses the conservative mean-value bound;
no additional factor of one half is assumed.

The retained TT linear state contribution therefore costs at most
`2.680279350e-13`, or **0.023714%** of the available transverse remainder
budget `1.130278227669531e-9`.

After this TT contribution, sufficient targets for the uniform higher-order
derivative-entry remainder are:

| Budget share assigned to this isolated path | Sufficient upper bound on higher-order entry error |
| --- | ---: |
| Entire remaining transverse budget | strictly below 3.949935893e-3 |
| 10% of that budget | strictly below 3.941503899e-4 |

These are downward-rounded sufficient targets, not measured error bounds
or an allocation already committed to this entry. Other missing intervals,
operators, entries and remainders must share the total budget. Splitting an
isolated entry can also lose useful cross-output cancellation, so failure
of this scalar test would not prove failure of a joint vector enclosure.

## Evidence and limitation

Both new calculations reproduced byte-for-byte in separate processes:

- `scripts/derive_n12_gate7_interval14_entry_budget.py`, outputs
  `tmp/gate7_vector_20260919/interval14_entry_budget_{first,repeat}.json`;
- `scripts/derive_n12_gate7_interval14_entry_first_jet.py`, outputs
  `tmp/gate7_vector_20260919/interval14_entry_first_jet_{first,repeat}.json`.

The reproduction receipt is
`tmp/gate7_vector_20260919/interval14_entry_structure_reproduction.json`.
No action derivative was reevaluated. The next unresolved object is the
uniform bound on `e_a(theta)` over the original interval-14 physical domain.
No full nonlinear fit, global inequality PASS, or Gate-7 closure follows
from the present linear-part calculation alone.
