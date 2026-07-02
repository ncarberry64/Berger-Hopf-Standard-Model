# Boundary Collar Measure Source v4.1

Status: `CONDITIONAL_BOUNDARY_COLLAR_MEASURE_SOURCE`

## Candidate

`dV_collar = J(Y,rho) dA d rho; J=det(I +/- rho S)=sqrt(det h(Y,rho)/det h(Y,0))`

## Claim boundary

Standard smooth-collar geometry supplies the symbolic measure formula, but BHSM-specific metric, shape, and orientation data remain open.

## Required boundaries

- The mathematical identity Vol(S³_unit)=2π² is not by itself a gauge-coupling derivation.
- The candidate denominator 6π² = 3 Vol(S³_unit) is not action-derived unless BHSM supplies an action-selected three-frame boundary average.
- A three-frame decomposition does not by itself imply a frame average.
- A frame average does not derive gauge couplings unless attached to gauge trace densities in the normalized action.
- The gauge coupling quantum λ_gauge = 1/(6π²) remains open unless the denominator is action-attached.
- The α_i values remain open unless the gauge quantum, sector weights, and action coefficient are attached by the normalized action.
- g2_BH remains open unless α2_BH is action-derived and the weak convention applies.
- The CKM coefficient value remains open unless g2_BH is action-derived.
- The CKM exponent remains not derived.
- Full BHSM remains not complete unless all action-normalization and scale gates close.

Run `python -m bhsm.interface boundary-collar-measure-source --format json`.
