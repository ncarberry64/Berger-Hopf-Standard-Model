# BHSM v1.3A H_T Analytic-Bound Classification Report

Theorem complete: `False`
Weakest analytic block: `zero_complement_projector`
Weakest matrix term: `sector_coupling`
Sector-coupling bound status: v1.3B adds finite spectral, Frobenius, row-sum, Weyl, and relative-bound estimates. v1.3C adds structured block and generalized relative-bound diagnostics. v1.3D tests uniform-in-k_max stability through k_max=32. v1.3E defines the Hilbert-space/domain assumptions needed to upgrade the scan. The status remains THEOREM_SCAFFOLD, not proven.

BHSM v1.3A inventories and classifies the Level 2 H_T operator terms for analytic-bound development. It does not prove the full no-extra-light-state theorem.

## Classification Table

| Term | Classification | Analytic status | Upgrade requirement |
| --- | --- | --- | --- |
| `berger_dirac_kinetic` | `DIAGONAL_EXACT` | exact for the Level 2 finite-basis diagonal block | derive a closed Berger twisted-Dirac diagonal lower bound |
| `hopf_twist` | `SIGN_INDEFINITE_BOUNDED` | bounded in finite basis by explicit coefficient and mode ranges | prove global coefficient-weighted mode bounds on H_perp |
| `boundary_term` | `SIGN_INDEFINITE_BOUNDED` | bounded in finite basis by explicit coefficient and mode ranges | prove global coefficient-weighted mode bounds on H_perp |
| `chirality_term` | `SIGN_INDEFINITE_BOUNDED` | bounded in finite basis by explicit coefficient and mode ranges | prove global coefficient-weighted mode bounds on H_perp |
| `sector_coupling` | `OFF_DIAGONAL_BOUNDED` | bounded in finite basis by Gershgorin and restricted min-max estimates | prove an infinite-basis operator-norm or relative-bound estimate |
| `heat_lift` | `PSD_EXACT` | nonnegative contribution controlled exactly under the PSD assumption | derive the profile or heat-lift input from the complete action |
| `psd_profile` | `PSD_EXACT` | nonnegative contribution controlled exactly under the PSD assumption | derive the profile or heat-lift input from the complete action |
| `zero_complement_projector` | `FINITE_BASIS_ONLY` | finite-basis evidence only | prove the protected kernel and complement decomposition in the full action |

## Current Best Lower-Bound Chain

1. Restrict the finite Level 2 Dirac matrix to the complement of the three protected zero modes.
2. Use the exact finite-basis diagonal contribution and finite q/residual ranges for diagonal sign-indefinite terms.
3. Control sector off-diagonal blocks with Gershgorin and restricted min-max bounds.
4. Use the v1.3B sector-coupling operator-norm audit to distinguish norm-certified cases from finite-basis-only passes.
5. Square the symmetric Level 2 Dirac matrix and take the conservative complement lower bound.
6. Apply the monotone heat-lift inequality with Lambda^2 = 1/(4*pi).
7. Add only PSD curvature/profile contributions, so Weyl's lower bound cannot decrease.
8. Keep theorem_complete=False until the zero-mode/complement split and off-diagonal bounds are proven in the full action.

## Next Upgrade Target

Prove the full-action zero-mode/complement decomposition dim ker D_twist = 3 and prove assumptions A1-A6 from the complete operator.

## v1.3G Zero-Mode/Complement Update

v1.3G formalizes the weak `zero_complement_projector` block as a dedicated
zero-mode/index and complement-projector scaffold. The finite Level 2
projector identities pass, the heat lift preserves protected zero modes, and
the finite sector-coupling block vanishes on the protected coordinate block.

The classification of `zero_complement_projector` remains `FINITE_BASIS_ONLY`
because the full topological index calculation, mirror zero-mode exclusion,
and infinite-dimensional complement projector compatibility remain open.

## Limitations

- The report is an analytic-bound development scaffold over DIRAC_PROXY_LEVEL_2.
- It does not prove the full no-extra-light-state theorem.
- No frozen v1.0/v1.1 predictions or v1.2 action-origin outputs are changed.
