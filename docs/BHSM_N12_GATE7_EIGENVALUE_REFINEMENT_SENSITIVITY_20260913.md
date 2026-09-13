# Eigenvalue refinement: correct derivative, negligible tested DF benefit

The selected normalized symmetric eigenpair obeys
D lambda[v] = psi^T DH[v] psi. The new producer evaluates this scalar
third-action contraction on all 249 scaled directions of the actual
midpoint-13 domain, then integrates its complete five-group support from
the verified point eigenvalue. It does not integrate the auxiliary border
of the projected eigenline solve.

The eigenvalue enclosure independently reproduced byte-for-byte. Its
radius fell from approximately 3.9990816243e-14 to 2.3428707307e-14,
a reduction of about 41 percent. The producer uses the independently
paired primal eigenvector box and unchanged analytic family certificate.

A fresh calculation of physical derivative column zero then used the
paired tighter eigenvalue, the same paired primal eigenvector and response
bounds, and the original complete first-variation graph. That calculation
also independently reproduced. The maximum restored comparison radius was
4.391752049326897; the candidate radius was 4.391751877963543. The relative
reduction is only about 3.9e-8 (0.0000039 percent). The comparison radius is
read through the producer's Arb restoration, which can enlarge the saved
radius by an outward rounding unit; exact reproduction hashes identify
both inputs and outputs.

This is not a material improvement in the tested physical column. The
full 99-column matrix and local integration are therefore not recomputed
for this eigenvalue-only change. The result does not rule out benefits in
every other column or domain, and does not establish a global lower bound
on achievable enclosure width. It identifies an ineffective next expansion
for the current tested case and preserves the negative result.

Nine focused tests passed, including an analytic two-by-two symmetric
family whose eigenvalue slope is nonzero while the projected auxiliary
border is zero, and the existing midpoint-family prerequisites. All
numerical records and data in the two pairs are byte-identical. Exact
source/data/receipt hashes and the decision are in
`BHSM_N12_GATE7_EIGENVALUE_REFINEMENT_SENSITIVITY_20260913.json`.

No empirical data is fitted. No full-path contraction, physical quotient,
Gate 7 closure, Museum-data replacement or manuscript completion is claimed.
