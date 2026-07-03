# Berger Anisotropy Compatibility v4.2

Status: `CONDITIONAL_BERGER_ANISOTROPY_COMPATIBILITY`

## Candidate

`e^1=r_base sigma_1, e^2=r_base sigma_2, e^3=r_fiber sigma_3; candidate c1=c2=c3 in e^a basis`

## Claim boundary

Equal gauge-frame coefficients are compatible with Berger anisotropy only if field strengths are expressed in an orthonormal coframe and metric factors are handled separately.

## Required boundaries

- Three artifact-backed Berger frame directions do not by themselves imply equal weighting.
- Equal weighting does not by itself imply average normalization by 1/3.
- Average normalization does not by itself attach to gauge trace densities.
- Berger anisotropy must be checked before equal frame averaging can be promoted.
- The denominator 1/[3 Vol(S³)] remains open unless equal frame averaging, unit-volume normalization, and gauge-trace attachment are supported.
- The gauge coupling quantum remains open unless the denominator is action-attached.
- α_i, g2_BH, CKM coefficient value, and CKM exponent remain open unless downstream action gates close.
- Full BHSM remains not complete.

Run `python -m bhsm.interface berger-anisotropy-compatibility --format json`.

<!-- BHSM_GAUGE_COFRAME_HODGE_V4_3 -->
## v4.3 coframe/Hodge update

The gauge basis is unspecified and Berger Hodge factors are not evaluated. No downstream status is promoted.
