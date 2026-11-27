# Jackpot: fixed distributed stellar load on the settled quadratic surface

This test answers whether distributing the normal force over the already fixed stellar map, and retaining its interaction with a persistent pin, rescues the graph calculation. It is a spherical, fixed-ambient reduction, not the full BHSM collar or backreacted metric.

## Model and what is fitted

Use the same positive static operator A=-Delta+ell² Delta² as the point control. Let d_P be the positive radial slope magnitude from a unit point Green source, and d_S from convolution with the two fixed spherical stellar deprojections and compact mass proxy, normalized by 10^11 solar masses for units. Under the declared hypothesis the ordinary density sets the **shape** of the distributed normal load, not its unknown coupling. The two smooth mass components have radial mass measure
dM_i/ds = 2 M_i (a_i+b_i) s² / [pi(s²+a_i²)(s²+b_i²)].
Evaluate the exact Green field by spherical shell averaging, not a fitted Gaussian. Keep the ordinary gravitational field of stars and compact mass in the lens baseline once. Their auxiliary shape forcing is not a second ordinary gravitational deflector.

Write the settled slope field as p d_P + s d_S, with positive p,s. Project the three products d_P², d_P d_S, and d_S² using the previous squared-gradient Born kernel. The mixed comparison is obtained by subtraction before identifying the optical increment:
- Pin difference about the loaded surface: p² P + 2ps X; only the mathematical reference lacks the pin.
- Distributed change on the pinned surface: 2ps X + s² S.
- Total shape contribution beyond ordinary gravity: p² P + 2ps X + s² S. This accounting is the relevant case if no shape-induced bending is implicitly included in the ordinary baseline.

Thus changes in both directions retain the reference-gradient cross term. Each run uses exactly the same stellar geometry, ordinary deflectors, weighting and ray geometry. The proportionality of normal loading to ordinary deprojected mass, positive co-directed forcing and zero non-shape bulk response are test hypotheses, not independently established. A strictly local flat hypersurface's minimal linear matter-normal source would vanish when its background extrinsic curvature vanishes; here the prescribed mass-shaped force probes the regular shape operator, not a derivation of nonzero force from that flat background.

On the predetermined log grid ell=0.1–1000 kpc with seven fixed interior sensitivities, calibrate positive p,s using only the two nominal aperture excesses. The point, cross, and distributed-square ratios appear in that order on the sampled grid, making the full mixed ratio monotone in the stellar fraction there. Select at most one solution per arm by nearest published lensing-equivalent slope 0.96, only within its quoted nominal ±.02 band, before evaluating B. Do not assign independent meaning to a fitted ell or p,s. Fit three nuisance coefficients to the early 14 knots and then predict the other image of the third source from A. No third-source position is used to choose ell or strength. The aperture summaries and slope are not treated as independent observations with a full joint error model.

## Results

| Stellar normalization | Shape accounting | Sampled positive aperture solutions | Equivalent inner slope | Held-out B error |
|---|---|---:|---|---:|
| Salpeter | Pin increment about loaded stars | 0 | none | not evaluated |
| Salpeter | Distributed increment about pin | 28 | 1.158–1.200 | not evaluated |
| Salpeter | Total shape response | 28 | 1.158–1.205 | not evaluated |
| Chabrier | Pin increment about loaded stars | 35 | 0.965 in selected case | 328 mas |
| Chabrier | Distributed increment about pin | 15 | 0.960 in selected case | 334 mas |
| Chabrier | Total shape response | 50 | 0.959 in selected case | 346 mas |

On the scanned ell range the Salpeter aperture ratio needs 1.750. The point and cross ratios are at most 1.466 and 1.655, so no positive mixture of only the point and cross terms can reach it. This is a grid conclusion, not a continuum bound for all extended matter or signs. Including the square of the distributed displacement restores that ratio on the grid, but the full well remains too steep against the [Turner et al. modeled 0.96 ± 0.02 slope](https://arxiv.org/abs/2401.08771). The Chabrier assumption allows a jointly calibrated inner well and is the fair case for the out-of-fit test. The full graph result is 346 mas versus about 38 mas for the matched Chabrier conventional control. The change is not evidence for an extra visible component or a new dark-matter measurement.

Verified shell-force convolution against direct adaptive integration and projected products against a higher-order quadrature, two-aperture closure after coefficient recovery, and independent replay. Replay: OPENBLAS_NUM_THREADS=1 python jackpot_settled_distributed_graph.py. The response is not ready to transfer. Broader progress requires nonconformal collar/bulk metric variation computed on the same settled state, or an independently specified asymmetric load, not another spherical width tuned against the third image.
