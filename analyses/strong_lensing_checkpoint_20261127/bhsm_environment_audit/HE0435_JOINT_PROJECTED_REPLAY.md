# HE 0435−1223: fixed-input full-field closure test

Run from the ZIP’s root (Python 3, NumPy 2.x and SciPy):
```sh
cd bhsm_environment_audit
OPENBLAS_NUM_THREADS=1 python he0435_joint_projected.py
python verify_joint_projected.py
```
This recreates the source-map JSON and updates the local stars-only prerequisite readout. The latter is not substituted for the cored, photometrically renormalized main profile in the joint calculation. The starting manuscript revision is 4f044a6af5757f6f1c4e99e6547b43d6c45e353c; the cumulative TeX patch also includes the prior checked clarity and provenance changes.

Numerical implementation: main profile from [Zahedy et al.](https://arxiv.org/abs/1510.04307), group position and velocity dispersion from [Sluse et al.](https://doi.org/10.1093/mnras/stx1484), G1 photometric profile from [Kochanek et al.](https://arxiv.org/abs/astro-ph/0508070), G1 stellar mass/redshift and two-plane formalism from [Wong et al.](https://doi.org/10.1093/mnras/stw3077), evaluated angles from [Courbin et al.](https://doi.org/10.1051/0004-6361/201015709). Separate profile names and redshifts prevent conflating the associated group and G1. Assumptions: spherical main and group proxies tilted neither forward nor back, group displacement in sky plane, smoothed stellar core, unmeasured group core and outer scales, common approximate far monopole, finite scalar integration and thin foreground lens, separated rear stellar G1 response. No quasar data used to adjust the physical inputs.

Primary comparison holds the ordinary foreground, matter, distance, G1 stellar+R1 response and finite scalar LOS path fixed. The single-domain nonlinear solution differs from the sum of the isolated scalar solutions only in foreground R1; the rear deflection changes because the incident coordinates and apparent G1 centroid change. The separately reported ordinary baseline turns off both R1 terms. The variation in scatter is a model diagnostic, not a fit metric with an observational likelihood. The four back-projected sources are not coincident. Do not report physical observed-lens delays. No independently inferred native BHSM matter/stress source or dark-matter exclusion is claimed. The positive conventional-density representation in the earlier manuscript refers to its specified spherical R1 family, not a positivity theorem for this anisotropic group run.
