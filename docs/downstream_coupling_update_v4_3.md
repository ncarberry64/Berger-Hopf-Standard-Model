# Downstream Coupling Update V4 3 v4.3

Status: `OPEN_DOWNSTREAM_GAUGE_AND_CKM_COUPLING_GATES`

Candidate: `alpha_i=w_i/(6*pi^2); g2_BH=2/sqrt(3*pi); C_CKM=g2_BH/sqrt(2), all conditional only`

## Claim boundary

No downstream coupling value promotes while the gauge normalization chain remains open.

- Equal frame coefficients in an orthonormal coframe are distinct from equal coefficients in the raw Berger coframe.
- Hodge-star metric factors may absorb Berger anisotropy, but this does not by itself imply frame averaging by 1/3.
- Equal orthonormal coefficients do not imply average normalization.
- Average normalization does not imply gauge trace attachment.
- Gauge couplings, CKM coefficient value, and full BHSM completion remain open unless downstream gates close.

Run `python -m bhsm.interface downstream-coupling-update-v4-3 --format json`.
