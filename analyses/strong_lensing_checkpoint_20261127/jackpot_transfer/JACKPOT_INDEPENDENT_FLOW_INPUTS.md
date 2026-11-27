# Independence gate: light twist, inferred stellar velocities, and the proposed flow

Paper remains paused. This is a source and geometry audit with no third-source fit or new forecast.

## Observational foothold

[Gavazzi et al., §II.2 and Fig. 2](https://arxiv.org/html/0801.1555#S2.SS2) report a change in the direction and ellipticity of the lens galaxy's stellar light between about 1 and 2 arcsec, on the scale of the proposed annulus. Their HST treatment explicitly masks the lensed arcs. Their two differently oriented stellar-light components already provide a conventional way to get a changing projected axis, so this observation is a control to include in the ordinary baseline, not a BHSM detection. The cited inner stellar-light axis is approximately -36 degrees north through east near/below 1 arcsec; this is not a constant annular axis.

[Turner et al., §§3.3 and 5.2](https://arxiv.org/html/2401.08771#S5.SS2) report only order-ten-degree misalignment between the measured kinematic and photometric axes, with radius dependence, and a reversal of relative stellar velocity dispersion by axis from smaller to larger radii. The dispersion result is a second moment, not a signed radial velocity. The lens stars are dispersion-dominated. Their preferred model excludes nine outer bins around or beyond 2 arcsec, where the proposed band ends. [The observing program](https://doi.org/10.1093/mnras/stae263) is ESO 0102.A-0950; the relevant HST program is 10886. I confirmed archive availability stated by the authors, not availability of a particular source-subtracted cube, aperture/bin mask or full covariance. An automated ESO catalog probe did not return readable data; no fresh MUSE reduction was performed.

## Local sanity check

The available unmasked HST F814W/F160W cutouts were meant for neighboring-object photometry. I read their FITS coordinates and tried a first-pass inner angular-harmonic measurement around the WCS lens coordinate, then perturbed and re-centered it. The two bands' nominal angles disagreed by 84 degrees and their smoothed brightness maxima lay roughly 0.4 arcsec away in different directions. Centering on those peaks changes the answer substantially. These are failed registration/decomposition suitability checks, not measurements of different physical galaxy axes in the two bands. Do not use raw cutout results as an orientation prior. No adopted flow phase. Reproducible diagnostic: OPENBLAS_NUM_THREADS=1 python jackpot_independent_axis.py.

## What would make the test independent

1. Register the arc-masked lens light (same celestial WCS and center), recover the radial light ellipticity/twist and use it in the **ordinary comparator** first. Fix stellar-mass calibration, PSF, masks and a conventional tide/shear on the same inputs.
2. Use spatially resolved first stellar velocity moments and second moments jointly. In a simple inclined axisymmetric disk, the first moment is proportional to sin(i)[v_phi cos(phi)+v_R sin(phi)] in deprojected coordinates. That alone can be confused with a change in projected rotation geometry when the major axis is uncertain. The dispersion-axis contrast cannot supply a signed flow phase. For this dispersion-dominated galaxy, require explicit tracer geometry and an ordinary orbital-anisotropy control; a BHSM surface flow need not be a stellar drift at all.
3. Derive how the regular-side flow and stress alter the optical metric and, if appropriate, the modeled stellar motions. The observations above can constrain the host and test that model, but cannot fix the flow-to-light coefficient by themselves. Freeze model, orientation, amplitude-selection rule and uncertainty model upstream of a fresh holdout. Source 3 is a development benchmark after these repeated test cycles, even though B was never fitted. Do not advertise it as blind; use an unexamined observable or a different lens if claiming predictive advantage. Require performance against the matched ordinary twisting-light/kinematic model, not merely improvement over the earlier spherical trial.

No paper, contact or publication.
