# A quantitative obstruction for the current Cartesian column enclosure

The independently replayed saved-data calculation proves a limitation of the
current independent-coordinate enclosure. Its relaxed derivative set has
radius-weighted gain at least **54.843547458166**. Any contraction upper bound
covering that entire set therefore has margin at most **-53.843547458166**.
The exact rational lower bound and its squared-norm proof are in the paired
record. No new physical derivatives were evaluated.

This is **not** a lower bound for the physical derivative. The Cartesian box
contains corners that the coupled physical equations may exclude. Physical
noncontraction, nonexistence, instability and failure of BHSM are not proved.

## Proof and scope

Use interval 13's paired right local Newton-defect column, trial index j=14,
at its first affected output node 14. Let a be the unchanged stored axis at
that node, and Q=I-aa^T the retained transverse output map. All binary64 axis
entries are treated as exact rationals; no exact-unit-axis assumption is made.
The reconstructed complete axes array matches the source binding's SHA256.

Let u_j be the jth coordinate vector and set x=r_T u_j. With s=a^T a,

    ell = r_T a_j / s,
    t = r_T (u_j - a a_j / s),
    x = a ell + t,   a^T t = 0.

Exact rational checks give |ell|<r_L and ||t||^2<=r_T^2. Thus x lies in the
same two-radius trial domain. At node 14, earlier residual rows cannot depend
on input node 14; a later interval's left injection cannot cancel this first
causal output. This argument uses the right block only. Applying it to the
left block alone would neglect the preceding interval's possible cancellation.

For the saved column box with center c, coordinate k=73 has radius
54.90988665819168. The box admits both c+rho_k u_k and c-rho_k u_k.
By the triangle inequality, at least one has projected norm at least
rho_k ||Q u_k||. Acting on x and dividing by output radius r_T cancels r_T.
Consequently every upper bound covering this Cartesian relaxation must obey

    q_box >= rho_k ||Q u_k|| >= 54.843547458166 > 1.

The squared norm is calculated exactly. An integer-square-root construction
rounds its square root downward to twelve decimal places; its defining lower
and upper square inequalities are checked exactly. Two fresh processes produce
identical record bytes. This is arithmetic replay of existing evidence, not a
new pair of physical derivative evaluations.

## Consequence for the next calculation

The existing Cartesian column enclosure cannot certify contraction, even if
all remaining point-Hessian shards succeed. With the same independent-coordinate
representation, this one projected coordinate uncertainty needs more than a
54.84-fold reduction merely to remove this necessary obstruction. That alone
would not prove the complete contraction. Changing the box center cannot remove
the argument because it uses the box diameter.

The positive stored-polynomial headroom remains valid for its own coefficients.
It does not absorb or supersede this uniform-column enclosure failure. The actual
physical global margin remains unknown.

The highest-value next calculation is a joint enclosure of this right-column
response on the unchanged tube, retaining the implicit eigenline/response and
normalization correlations before coordinate ranges are taken. Its target is
projected support compatible with contraction, not a modest reduction of an
unweighted maximum radius. Reuse saved point jets as anchors and retain the full
neighborhood remainder. Such a method can exclude the nonphysical corners used
above; whether it yields the required improvement remains unproved. Another
expensive seed bootstrap is not justified until that bound is designed.

Gate 7 still requires the full joint operator oracle, projected force, KKT root
and constrained physical Hessian. Continuum closure, physical observables, Museum
integration and the flagship submission requirements remain separate. No gate is
promoted by this negative enclosure result.

## Portable manuscript supplement

All arithmetic operands, retained source hashes, and the paired result are in
`generated/column_box_obstruction.json`. Run
`python manuscript/flagship/replay_column_box_obstruction.py` from the repository
root to replay the exact inequalities using only the Python standard library.
The full local derivative construction still requires its retained raw evidence;
this portable replay proves the box obstruction for the supplied input snapshot.
