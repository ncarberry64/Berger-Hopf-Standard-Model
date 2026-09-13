# Centered uniform physical derivative progress

Gate 7 and FULL_BHSM_COMPLETE remain false. The completed diagnostic results
below concern weighted augmented basis column 0 at endpoint 13 and its actual
HS midpoint. They are not full-basis certificates or physical observables.

| Method | Endpoint 13 maximum derivative radius | Actual midpoint 13 radius |
| --- | ---: | ---: |
| Previously paired coupled normalization, zero-center variations | 76989.0653 | 52103.0248 |
| Signed residual around fresh verified point variations | 178.234831 | 15.695650 |
| Affine state integration of that residual | 152.365345 | Canceled; partial results retained |
| Centered residual with component error bound | 3.693916 | 6.412255 |
| Iterated paired defect decomposition | 3.693884 | 6.382528 |

Every completed diagnostic contains the independently verified derivative at
the exact same domain anchor. The diagnostic artifacts themselves have not
been independently reproduced. Their records, data hashes and status are in
`artifacts/flagship_integration/BHSM_N12_GATE7_CENTERED_VARIATION_DIAGNOSTIC_20260912.json`.

The selected method uses exact point variation centers, signed preconditioned
action residuals and a componentwise consequence of the already proved
weighted Neumann bound. It retains all original D3/D4 descriptor terms and
both original physical variations, with common border-scale cancellation in
the final normalization. The action, selected index, original reference,
physical domain radii and frozen integration maps remain the same.

The affine alternative used all 75 endpoint or 249 midpoint domain columns.
At the endpoint its selected-line state contribution was 3.43e-5 versus
anchor residual magnitude 0.386. At the midpoint the corresponding partial
results were 1.67e-4 versus 1.925. The expensive midpoint response stage was
canceled to prioritize the simpler component method and curvature campaign.
Its cancellation record and partial log are retained; it is not a numerical
failure or a completed derivative enclosure. Iterating the stored defect
decomposition also offered little improvement over the simple component step.

New isolated producers apply the selected method to all 99 input directions
in one call, avoiding repeated point solves across small column batches.
They use the original producer's first/recompute publication protocol and
the immutable input hash cache. A local integration consumer requires paired
full endpoint, actual-midpoint and next-endpoint derivatives before using
the unchanged frozen HS local operator.

The full-basis integration pilot is now independently reproduced: endpoints
13 and 14, actual midpoint 13, and local interval 13 each have byte-identical
first/repeat records and data. The complete numerical evidence is in
`artifacts/flagship_integration/BHSM_N12_GATE7_COMPONENT_CENTERED_INTEGRATION_20260912.json`.

| Paired array | Shape | Maximum radius |
| --- | --- | ---: |
| Endpoint 13 DF | 99 by 99 | 620.281251 |
| Endpoint 14 DF | 99 by 99 | 580.585938 |
| Actual midpoint 13 DF | 99 by 99 | 1965.742189 |
| Local interval 13 C | 74 by 74 | 4.208756e-153 |
| Local interval 13 DL | 74 by 74 | 486.432636 |
| Local interval 13 DR | 74 by 74 | 485.949672 |

The descriptor column, rather than the diagnostic's column 0, dominates the
full DF radii. The unchanged local integration rescales and combines the
complete matrices through its frozen frames and preconditioner; its bounds
cannot be inferred from a single largest raw derivative entry.

The previously paired normalization-only local DL/DR radii were
62715518.8125 and 73728779.875. The new local radii are over 100,000 times
narrower, but remain far too broad to establish contraction. C retains its
previous sharp enclosure. This is a measured local numerical improvement,
not a physical quotient or full-path Z1 certificate.

Validation at this cutoff: 24 focused tests passed, including direct
polynomial residual identities, exact polynomial state differences,
independently constructed perturbed bordered systems, the original
normalization/local integration helpers and immutable-cache behavior.

Completion of this pilot leaves full-domain coverage, acceptable uniform
integration bounds, physical quotient identification,
higher remainders and the remaining action-to-prediction dependencies open.
The results therefore do not supply new data for a Museum observable or
establish manuscript completion.
