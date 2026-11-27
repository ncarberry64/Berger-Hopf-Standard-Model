# CSWA 31: first held-out path replay

Frozen inputs: [Wang et al. 2022](https://doi.org/10.1051/0004-6361/202243600)
Table 1 angular positions/redshifts, fixed R1 background distances, spherical
Hernquist stand-in for the photometric BGG of 1.6e12 solar masses and
27.2 kpc effective radius. This is a positive-density group-potential
control, not the hypothetical BHSM collective environment law. Fit six
projected group parameters to centered source-plane pairs for S0–S3 only
(14 scalar contrasts, same 12 initializations for both models). No held-out
image positions were used in the optimization. This objective is an
unweighted reduced diagnostic, not a full covariance likelihood.

S0 acts as an intermediate deflector for the higher-redshift images; its
center is the average of the development S0 rays. Include a conditional
cored SIS based on equivalent infinite-source Einstein angle 0.20 arcsec
(83.28 km/s), from the median gas-kinematics interpretation of
[Wang et al. 2024](https://arxiv.org/abs/2404.13205), section 4.2.1.
The observation is a velocity field; its translated radius/normalization
depends partly on the assumed lens magnification and is not an unconditional
prior. Check additional 0, 130 and 220 km/s values, not tuned on the holdout.

At the gas-kinematics-motivated normalization:

- Development component RMS for the ordinary control is 0.3800 arcsec
  in source coordinates, not an observed image-position RMS.
- S5's four reported images back-project to points as much as 2.667 arcsec
  apart. With S5(a) as the only source anchor, the other three matched roots
  miss observed counterimage positions by 4.835, 3.328, and 4.684 arcsec.
- S4 fails the test independently. The two S4 counterimage misses are
  1.388 and 4.454 arcsec, conditional on its less clean family association.
- Adding the frozen isolated stellar R1 correction and refitting only
  the same development data moves the matched S5 distances by no more
  than 0.000006 arcsec in this configuration. This is not a test of a
  jointly solved BHSM group field.
- No shape or arrival-time prediction is warranted. A root match by
  distance is not claimed to reproduce parity/morphology; roots are
  searched over a 90 arcsec square, not proven exhaustive.

The conventional *reduced control* is inadequate, not conventional gravity
as a whole. The independently cataloged redshift-1.36 structures and
resolved arc shapes are next inputs; do not use an absorber position
chosen by fitting S4/S5. Wang et al. 2024 report seven galaxies at
z≈1.36 and two bright candidates within 15 arcsec; their effective fitted
centroid did not correspond to a visible HST galaxy. Include that
uncertainty and do not infer a shared primary-group field from an
intermediate-plane correction. Keep the cross-target rule test frozen.

Reproduce: `OPENBLAS_NUM_THREADS=1 python -W error cswa31_holdout.py`.
