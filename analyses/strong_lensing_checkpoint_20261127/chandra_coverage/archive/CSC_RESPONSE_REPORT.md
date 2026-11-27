# HE 0435−1223 | Chandra exposure-response check

**Result: the Wilson excess survives exposure weighting, but it is weak and depends on the detector-direction mask. It does not establish an X-ray centroid or an outer gravity constraint.**

Used all 33 full-field per-observation exposure maps from the [Chandra Source Catalog 2.2](https://cxc.harvard.edu/csc2/data_products/full-field/expmap3.html), revision N028, matched by observation and interval to 11 archival Level 2 event lists. The three [CSC bands](https://cxc.harvard.edu/csc2.2/columns/ebands.html) are 0.5–1.2, 1.2–2.0, and 2–7 keV, with maps at 0.92, 1.56, and 3.8 keV. The soft and medium counts were combined only after exposure weighting in their separate bands. CCD7 regions below 80% of the positive local map's 90th percentile and near the swept FOV boundary were excluded. The 25″ quasar mask and 6″ CSC source masks give the conservative results below. Test bands and both candidate radii are in the machine-readable record. The radial control conditions on counts in 2″ annuli about the quasar in each observation; a mixture weights either constant local particle background, local sky exposure, or their midpoint. This differs from fitting or subtracting a calibrated particle background.

| Wilson, 42.052″ aperture | Recorded 0.5–2 keV counts | Conditional expected counts | Illustrative conditional residual |
| --- | ---: | ---: | ---: |
| 10 later observations, flat geometry weighting | 720 | 687.24 | 1.50 |
| 10 later observations, full sky exposure weighting | 720 | 686.08 | 1.55 |
| 10 later observations, sky exposure weighting and ±5″ detector readout-direction strip mask | 631 | 610.97 | 0.97 |
| 2 full frames, sky exposure weighting | 103 | 85.03 | 2.33 |
| 9 partial frames, sky exposure weighting | 647 | 627.35 | 0.94 |

The two later subsets give conditional residuals 0.63 and 1.56 without the strip, 0.56 and 0.81 with it. The small Wilson aperture is less repeatable across splits. Hard-band controls do not establish a source. A separate 9.5–12 keV detector particle-rate stability check within each CCD7 good-time interval found no strong deviations from a steady Poisson rate at ~2 ks timescales. Across observations, mean rates differ and are not comparable without matching readout configuration and active area. Absence of obvious high-energy flares does not exclude all soft-background changes.

The numbers in the last column are **not discovery significances or flux limits**. Tests share pixels, and the model does not explicitly fit residual quasar wings, all backgrounds, or overlapping physical groups. An azimuthally symmetric lens-centered component can be absorbed by the control. The historical HE 0435 field-level diffuse claim remains unconfirmed/unlocalized, not ruled out. No gas asymmetry or mass estimate should be imported into BHSM from this result. No quasar image/time-delay fit was used.

## Replay
The initial counts-screen ZIP contains the primary archive/FOV/source-mask acquisition. Here `csc_calibrated/siap.xml` and `csc_calibrated/SHA256SUMS` identify the CXC calibration files. Run `bash fetch_csc_maps.sh`, then `python counts_csc_response.py` and `STREAK_MASK_ARCSEC=5 python counts_csc_response.py` with NumPy, SciPy, Astropy and Matplotlib. Run `python high_energy.py` for the detector stability table. This bundle contains derived results and retrieval instructions, not the raw public event lists or exposure maps.
