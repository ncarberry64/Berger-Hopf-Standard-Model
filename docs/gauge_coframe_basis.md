# Gauge Coframe Basis v4.3

Status: `OPEN_MISSING_GAUGE_COFRAME_BASIS`

Candidate: `raw: sigma_a; orthonormal candidate: e^1=r_base sigma_1, e^2=r_base sigma_2, e^3=r_fiber sigma_3`

## Claim boundary

The repository does not state whether gauge-field components use the raw Berger coframe or its orthonormal rescaling.

- Equal frame coefficients in an orthonormal coframe are distinct from equal coefficients in the raw Berger coframe.
- Hodge-star metric factors may absorb Berger anisotropy, but this does not by itself imply frame averaging by 1/3.
- Equal orthonormal coefficients do not imply average normalization.
- Average normalization does not imply gauge trace attachment.
- Gauge couplings, CKM coefficient value, and full BHSM completion remain open unless downstream gates close.

Run `python -m bhsm.interface gauge-coframe-basis --format json`.
