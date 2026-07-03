# Gauge Trace Attachment Update V4 3 v4.3

Status: `OPEN_MISSING_GAUGE_TRACE_FRAME_AVERAGE_ATTACHMENT`

Candidate: `[3 Vol(S^3)]^-1 sum_a int Tr(F_a wedge *F_a)`

## Claim boundary

Neither conditional Hodge dependence nor a candidate average attaches the normalization to gauge trace densities.

- Equal frame coefficients in an orthonormal coframe are distinct from equal coefficients in the raw Berger coframe.
- Hodge-star metric factors may absorb Berger anisotropy, but this does not by itself imply frame averaging by 1/3.
- Equal orthonormal coefficients do not imply average normalization.
- Average normalization does not imply gauge trace attachment.
- Gauge couplings, CKM coefficient value, and full BHSM completion remain open unless downstream gates close.

Run `python -m bhsm.interface gauge-trace-attachment-update-v4-3 --format json`.

<!-- BHSM_BERGER_HODGE_COMPONENT_V4_4 -->
## v4.4 Berger Hodge update

Raw Berger and orthonormal Hodge components are now explicit conditionally. This does not select the gauge-action basis or promote any normalization or coupling status.
