# Gauge Denominator Source v4.0

Status: `OPEN_MISSING_GAUGE_COUPLING_VOLUME_DENOMINATOR`

## Claim boundary

The identity 6π² = 3 Vol(S³) is not enough; the action must use it as gauge trace-density normalization.

## Required repository boundaries

- BHSM is not complete until the full action-normalization and scale gates close.
- The 1:2:7 gauge-coupling registry pattern is artifact-backed but not action-derived.
- The candidate denominator 6π² = 3 Vol(S³) is not a coupling derivation unless attached to the normalized gauge action.
- Sector weights do not derive gauge couplings without action attachment.
- The overall gauge-action coefficient k remains open unless fixed by the action.
- The CKM coefficient form is artifact-backed, but the CKM coefficient value remains open unless g2_BH is action-derived.
- The CKM exponent remains not derived unless all CKM action, transport, identification, and log-averaging gates close.
- Dimensionless neutral/PMNS structure does not imply physical neutrino masses.
- Physical Delta m², matter effects, radiative corrections, stiffness length, curvature, and unit normalization remain open unless separately derived.
- Full BHSM completion is not claimed by this repository unless every completion gate passes.

## Machine-readable source

Run `python -m bhsm.interface gauge-denominator-source --format json`.

<!-- BHSM_BOUNDARY_COLLAR_MEASURE_V4_1 -->
## v4.1 measure/frame update

The collar measure formula is conditional and three Berger coframe directions are artifact-backed.
Unit-S3 normalization, action-selected averaging, and gauge trace-density attachment remain open;
this result does not promote the gauge denominator, couplings, CKM value, or completion status.
See [boundary/collar measure source](boundary_collar_measure_source.md).
