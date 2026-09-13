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

The first full-basis integration pilot targets endpoints 13 and 14 plus
actual midpoint 13, each with a separate repeat, then local interval 13 with
its own repeat. It is in progress at this document's cutoff. No full-basis
or local improvement is asserted from the one-column diagnostic table.

Validation at this cutoff: 24 focused tests passed, including direct
polynomial residual identities, exact polynomial state differences,
independently constructed perturbed bordered systems, the original
normalization/local integration helpers and immutable-cache behavior.

Even successful completion of this pilot would leave full-domain coverage,
acceptable uniform integration bounds, physical quotient identification,
higher remainders and the remaining action-to-prediction dependencies open.
The results therefore do not supply new data for a Museum observable or
establish manuscript completion.
