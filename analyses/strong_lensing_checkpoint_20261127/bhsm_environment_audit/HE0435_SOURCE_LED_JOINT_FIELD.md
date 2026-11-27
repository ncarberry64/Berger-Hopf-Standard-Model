# HE 0435−1223: source-led two-plane field control

The galaxy and separately redshifted G1 are fixed by published stellar inputs and transported through the retained, fixed PR #23 background. There is no lens fit, arrival-time input, fitted halo, residual shear, or fitted source position. The result is a conditional stars-only part of the field, not an all-source prediction.

- Main galaxy: [Zahedy et al., §4.2 and Fig. 5](https://arxiv.org/pdf/1510.04307), photometric log10 stellar mass 11.1; Sérsic n=3.51, major-axis effective radius 4.4 kpc and q=.82. Spherical approximation uses the equal-area effective radius 3.984 kpc.
- Rear G1: [Wong et al., §3.4 and 4.2](https://doi.org/10.1093/mnras/stw3077) photometric Chabrier log10 stellar mass 10.9; [Kochanek et al., §2](https://arxiv.org/pdf/astro-ph/0508070) NICMOS de Vaucouleurs bulge Re~.37″, H~18.7 and exponential disk scale length .67″, H~18.8. Adopt projected circular shapes and common H-band stellar M/L, giving .5230 bulge mass fraction and circular effective radii 2.821 and 8.575 kpc at G1's spectroscopic z=.7821. No fitted angular Einstein radius is used. PR #23's independent angular offset is (−2.585,−3.637)″ relative to main light.
- Observed image locations: [Courbin et al., Table 2](https://doi.org/10.1051/0004-6361/201015709), copied from the pinned PR #23 provenance. Used exclusively to test if the four back-projected rays agree; common-source RMS is centered scatter, not a fitted forward lens model. We do not score time delays.
- Frozen [two-plane lens equation and ordered Jacobian](https://github.com/ncarberry64/Manuscript-Generation/blob/4f044a6af5757f6f1c4e99e6547b43d6c45e353c/manuscript/sections/he0435_geometry_20261021.tex): tracing G1's own observed direction through the main lens fixes rear-plane physical center. The two galaxies are far apart in depth and treated as separate local response regions. G1's bulge and disk enclosed masses enter one R1 source before nonlinear screening; two per-plane fields are not added as if centered in one spatial region. Cross-plane source evolution and non-spherical coupled R1 are not solved here.

| Conditional model | Four-ray common-source RMS |
| --- | ---: |
| Main stellar component alone | 0.910170879″ |
| Main + separate rear G1 stellar mass | 0.909292353″ |
| Same sources + baryon-sourced R1 metric | 0.909281803″ |

G1 moves recovered source positions relative to one another by up to 17.8056 mas. The additional retained R1 response changes a pair separation vector by only 0.0216267 mas. The final pair spread reaches 1.987758″. The ordered analytic Jacobian agrees with finite differences within 1.38e−9 over the nominal observed rays. It includes nonzero rotation from noncommuting plane Hessians. Effective convergence for A–D is .04285/.05608/.04473/.06720 in retained R1, a model diagnostic, not a measurement.

The inputs reproduce neither a common quasar coordinate nor the total gravitational field. This says only that the two specified stellar sources, under these circular approximations, are insufficient. It neither excludes a conventional total-mass model nor demonstrates a BHSM residual. A complete conventional prediction needs independent galaxy/environment mass and boundary data; a complete BHSM-specific prediction additionally needs the action-normalized environment/galaxy state-to-metric source.

Replay from this directory: `PYTHONDONTWRITEBYTECODE=1 python he0435_joint_field_control.py`. Machine-readable result: `he0435_joint_field_control.json`.
