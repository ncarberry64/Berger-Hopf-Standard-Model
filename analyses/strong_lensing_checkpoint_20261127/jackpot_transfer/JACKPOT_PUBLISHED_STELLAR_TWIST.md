# Ordinary lens control with the published stellar-light twist

[Sonnenfeld et al., Table 3](https://pure.rug.nl/ws/portalfiles/portal/56877757/Evidence_for_dark_matter_contraction.pdf) provide the arc-masked photometric geometry needed for this test: two components with axis ratios 0.66 and 0.71, and position angles 63.0 and -24.3 degrees east of north. Their core/cut radii are the same as the circularized profiles in the existing lens. Restore the geometrically measured ellipticities and orientations without adjusting them to any lensing position. Keep stellar inventory, compact mass, neighbor deflections, distance ratios, source-plane conventions, and the five conventional fit parameters identical. No surface flow is added.

Compute deflections for homogeneous elliptical contours from the standard one-dimensional homoeoid integral using the area-preserving elliptical radius. Check the q→1 limit against the original circular profile and the matched angular-average deflection against zero. The full arm restores the published projected ellipses at fixed component total masses. A second arm removes the change of circularly averaged deflection only, isolating the angular effect with exact circular monopole equality. A third aligns both components to the outer component's measured axis as an artificial single-axis comparison. Fit only the original first two sources' knots (the conventional excess power and amplitude, shear and S1 strength); using the same branch seeded in advance, trace the counterimage from A and score B. B remains a repeatedly evaluated development benchmark, not a fresh blind prediction.

| Stellar normalization | Shape | Early knot RMS (mas) | B error (mas) |
|---|---|---:|---:|
| Chabrier | Circular | 14.95 | 37.57 |
| Chabrier | Artificial aligned stars, matched monopole | 16.36 | 230.17 |
| Chabrier | Published twist, matched monopole | 15.59 | 28.63 |
| Chabrier | Published twist, full | 15.57 | 30.25 |
| Salpeter | Circular | 16.99 | 96.55 |
| Salpeter | Artificial aligned stars, matched monopole | 20.94 | 570.03 |
| Salpeter | Published twist, matched monopole | 18.49 | 103.97 |
| Salpeter | Published twist, full | 18.38 | 100.45 |

The 9 mas Chabrier improvement is nominal and does not hold for both stellar inventories. The early knot RMS worsens slightly even for Chabrier. No new covariance calculation, detection, statistical superiority or generic conclusion about spin/flow follows. But ignoring the measured change of orientation, or folding it into a single arbitrary common axis, can materially change the conventional reference. Use the same light-driven stellar correction in both arms of any future matched test. No paper or external contact.

Replay: OPENBLAS_NUM_THREADS=1 python jackpot_published_stellar_twist.py.
