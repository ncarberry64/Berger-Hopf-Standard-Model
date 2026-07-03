# Gauge Attachment Update V4 4 v4.4

Status: `OPEN_MISSING_GAUGE_TRACE_FRAME_AVERAGE_ATTACHMENT`

Candidate: `[3 Vol(S^3)]^-1 sum_a int Tr(F_a wedge *F_a)`

Orthonormal map: `*(e1 wedge e2)=e3; *(e2 wedge e3)=e1; *(e3 wedge e1)=e2`

Raw Berger map: `*(sigma1 wedge sigma2)=(r_fiber/r_base^2)sigma3; *(sigma2 wedge sigma3)=(1/r_fiber)sigma1; *(sigma3 wedge sigma1)=(1/r_fiber)sigma2`

## Claim boundary

The expansion does not attach an average or unit-volume normalization to gauge couplings.

- An explicit Berger Hodge-star component map is distinct from selecting the gauge-action coframe basis.
- The orthonormal coframe e^a absorbs Berger metric scale factors, while raw sigma_a components retain anisotropic Hodge factors.
- A component Hodge map does not by itself imply equal gauge-frame coefficients.
- Equal coefficients do not by themselves imply average normalization by 1/3.
- Gauge trace Hodge expansion does not by itself derive gauge couplings.
- The denominator 1/[3 Vol(S^3)] remains open unless frame averaging, unit volume normalization, and gauge-action attachment are all supported.
- alpha_i, g2_BH, CKM coefficient value, CKM exponent, and full BHSM completion remain open unless downstream gates close.

Run `python -m bhsm.interface gauge-attachment-update-v4-4 --format json`.
