# Direct primal refinement and midpoint integration

The independently repeated endpoint-14 calculation sharpens the complete
99-column physical derivative enclosure using mean-value bounds for the
primal eigenvector and bordered response. All numerical arrays from the
new direct signed-residual method are byte-identical to the independently
paired original rate-graph method. Both request only action orders two
and three, without computing a physical Hessian.

| Endpoint 14 radius | Previous | Refined |
| --- | ---: | ---: |
| Maximum over all 99 columns | 580.5859375 | 60.78125 |
| Maximum over state columns | 3.381874301 | 2.016408376 |
| Physical input column zero | 3.381874301 | 1.320666313 |

Values in the table are numerical enclosure radii, not measured observables.
Exact rational radii, record hashes and independent-reproduction receipts
are recorded in `BHSM_N12_GATE7_DIRECT_PRIMAL_REFINEMENT_20260913.json`.
The paired primal eigenvector radius is approximately 4.748608906e-8 and
the bordered response radius approximately 0.007611651781. Lambda is retained;
the projected eigenline border is not used as an eigenvalue derivative.

The direct method avoids constructing unused unpreconditioned uniform
variation tensors before evaluating the complete signed residual equations.
Its point anchors still come from all three original verified bordered
solves. The matching numerical arrays establish equivalence for this
endpoint; they do not establish a timing guarantee or full-path closure.

The midpoint implementation uses the actual paired Hermite-Simpson domain:
two longitudinal intervals, two 74-dimensional Euclidean balls, and the
99-dimensional box of field and rounding uncertainty. It scales all 249
directions by their own group radii once, integrates with unit-radius group
support, and uses the exact midpoint anchor and descriptor. A dedicated
validator requires the actual midpoint eigenpair and field certificates,
strict contraction on all 62 rows, positive inertia, reference orientation
and a strictly positive physical norm. Endpoint scope cannot substitute.

Eleven focused tests passed for the midpoint analytic prerequisites,
actual-domain inclusion and complete signed derivative residuals. Source
preflight also accepted the paired midpoint domain and both refined endpoint
matrices. Numerical midpoint values, its full derivative matrix and the
resulting local integration remain pending until their independent pairs
finish; this document makes no claim that these pending results passed.

The local consumer combines the refined endpoints 13 and 14 and actual
midpoint 13 in the existing preconditioned local operator. It retains the
frozen frames, maps, trial radii and operator, and verifies each complete
99-column input against the original physical-domain dependencies.

No empirical data is fitted. These are retained finite-action numerical
enclosures. Full-path contraction, physical quotient identification,
Gate 7 closure and full BHSM completion remain open. Existing Museum data
and the flagship manuscript must retain those claim boundaries.
