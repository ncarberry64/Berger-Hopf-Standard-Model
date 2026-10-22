# Final scope and primary-literature check

Checked the main manuscript and its exterior, projection, estimator and numerical-table inputs on 2026-10-21. No manuscript input was edited by this review. PDF visual review of pages 7-12 is recorded separately after the final render.

## Findings requiring attention

1. **P1: stale numerical table.** At review time `numerical_table.tex` still reports nuisance rank 29, projected singular values (3.13473, 1.58561), and norm fractions (0.08328, 0.14512). The main text and abstract describe the final axial-inclusive 30-nuisance experiment, with singular values about (3.135, 0.802). Regenerate the table and any associated plot from the final receipt. The new second direction is materially smaller, so the inconsistency is scientifically relevant rather than typographic. Parent notified immediately.

2. **P2: action attribution should be nearer the action.** `Deffayet2010` is present in the bibliography but uncited. Cite it where the cubic/KGB action is introduced; place `Kimura2012` near the quasi-static cosmological screening reduction. The existing `Chu2013`, `Brito2014` and `Kobayashi2026` citations at the start of the projection section and in the final scope section adequately disavow novelty of the known modes and powers; citing `Chu2013` directly after the hypergeometric formula would make the attribution easier to audit.

## Scope assessment

The draft explicitly credits static cubic screening, multipole exponents and exact radial modes, ordinary STF/TT projection, point-lens delay/flux inversion, internal/external lens multipoles and profiled inference. It avoids a first-ever claim and does not present a prescribed worldtube amplitude as a black-hole horizon prediction. The source, distance, frame, flux, symmetry, outer-matching and weak-field restrictions are visible in both the abstract and technical sections.

The exact scalar-statistic/shear null, potential-rank versus observable-rank distinction, two odd projection nulls, and screened axial mass degeneracy remain correctly qualified. The code uses a scalar monopole and fits its flux and the visible axial scalar mode; the narrative no longer silently fixes those modes. The 54-component broad scan is explicitly an information experiment, its million-year motion timescale is disclosed, and the picosecond model value is explicitly denied physical forecast status. The acknowledged absence of a source-selected horizon flux, causal deformation law and microscopic BHSM-to-R1 map is appropriate.

The contribution is a conditional composition and information-loss calculation. Its strength is reproducibility and explicit failure modes, not a demonstrated astrophysical breakthrough or detection method. It can support a theoretical methods submission after the numerical artifacts agree, but this internal check cannot determine journal acceptance or establish exhaustive novelty.

## Direct primary attribution controls

- Cubic/KGB action: [Deffayet et al. (2010)](https://arxiv.org/abs/1008.0048); cosmological nonlinear screening: [Kimura et al. (2012)](https://arxiv.org/abs/1111.6749).
- Exact cubic static multipoles: [Chu and Trodden (2013)](https://arxiv.org/abs/1210.6651); screened multipole powers: [Brito et al. (2014)](https://arxiv.org/abs/1409.0886); 2026 EFT comparison, with cubic limit in Appendix B: [Kobayashi and Takadera](https://arxiv.org/abs/2607.09098). The latter is labeled a preprint, and its beyond-Horndeski conclusions are not imported into R1.
- Harmonic STF/TT projection: [Turyshev and Toth (2022)](https://doi.org/10.1103/PhysRevD.105.024022). Internal/external quadrupole reconstruction: [Trotter et al. (2000)](https://arxiv.org/abs/astro-ph/0001022), [Bernstein and Nakajima (2009)](https://arxiv.org/abs/0807.1931).
- Standard compact point-lens delay and flux law: [Muñoz et al. (2016)](https://arxiv.org/abs/1605.00008). Existing astrometric tracking and delay drift: [Sahu et al. (2022)](https://arxiv.org/abs/2201.13296), [Van Tilburg et al. (2018)](https://arxiv.org/abs/1804.01991), [Dai and Lu (2017)](https://arxiv.org/abs/1706.06103).
- Equivalence/source and multi-plane freedoms: [Schneider (1997)](https://arxiv.org/abs/astro-ph/9706185), [Schneider and Sluse (2014)](https://arxiv.org/abs/1306.4675), [Schneider (2019)](https://arxiv.org/abs/1409.0015), [Fleury et al. (2021)](https://arxiv.org/abs/2011.04440). The 2019 journal date despite its 2014 preprint is correctly recorded.
- Time-dependent black-hole lensing is acknowledged using [Pantig (2026), version 3](https://arxiv.org/abs/2510.19849). It is not treated as solving the R1 horizon-matching problem.

This was a directed primary-literature and manuscript-consistency check, not an exhaustive citation or priority search.

## Resolution and late primary-literature addendum

Rechecked the saved sources after the parent fixes. The numerical table now reports nuisance rank 30, singular values (3.13473, 0.80220) and retained norm fractions (0.04213, 0.14512), consistent with the final experiment. The exterior section now cites Deffayet2010 and Kimura2012 beside the common action. Both numbered findings above are resolved.

The late discovery of Babichev et al. (2025) and Smulders--Noller (2026) requires, and now receives, explicit credit for cosmological charge selection and stable quasi-stationary black-hole constructions in related theories. See `cosmological_hair_applicability.md` for the bounded comparison. Neither paper directly selects the present canonical-plus-linear-potential R1 flux. The scope statement should identify an unevaluated action/background-specific matching map rather than imply that charge-selection or stable cosmological-hair methods do not exist. The new main-text paragraph addresses this distinction; avoid implying that Babichev et al.'s entire broader theory study is limited to its explicit self-accelerating cubic de Sitter example.

The actual-pixel PDF review of pages 7-12 passed for the hash recorded in `pdf_visual_review_pages7_12.md`. That visual receipt is version-specific.
