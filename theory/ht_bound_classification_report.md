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

## v1.3H Diagonal Complement and Mirror-Mode Update

v1.3H audits two pieces of the `zero_complement_projector` blocker:

- the finite diagonal coordinate-complement lower bound before sector coupling
  is `1.4641`, clearing `d_required = 0.8038064161349437`;
- opposite-chirality candidates paired with the three protected zero-mode
  labels are generated and classified as `OPEN_MIRROR_RISK`.

The diagonal finite scaffold passes, but the mirror exclusion and
infinite-basis diagonal complement theorem remain open. The full `H_T` theorem
therefore remains incomplete.

## v1.3I Mirror-Exclusion Derivation Update

v1.3I closes the generated mirror-candidate risk at the scaffold channel level:
`mirror_lepton`, `mirror_up`, and `mirror_down` are excluded by the weak chiral
projector channel. The Higgs-`U(1)` and boundary-functional mirror channels are
still reported as `OPEN`.

The full `H_T` theorem remains incomplete because the topological index
theorem, formal/coordinate zero-mode alignment, and infinite-basis complement
bound remain open.

## v1.3J Zero-Mode Alignment Update

v1.3J audits the formal/coordinate alignment blocker directly. The result is
`PARTIALLY_ALIGNED`: the lepton formal zero-mode label aligns with coordinate
`0`, while the up/down formal labels are present at coordinates `18` and `36`
but are not in the finite coordinate-protected block.

The `zero_complement_projector` term therefore remains the weakest analytic
block and remains scaffolded.

## v1.3K Sector-Labeled Kernel Update

v1.3K tests whether the Level 2 protected block should be the formal
sector-labeled kernel. The formal projector uses coordinates `(0,18,36)`,
whereas the legacy Level 2 scaffold protected `(0,1,2)`.

Outcome: `FORMAL_KERNEL_NOT_PROTECTED`. The formal projector is well-defined
and idempotent, but the current Level 2 matrix does not protect formal up/down
coordinates. Recomputing the `H_T` gap with `P0_formal` collapses the finite
gap, so the previous Level 2 gap does not survive as a formal-kernel audit.

## v1.3L Corrected Formal-Kernel Operator Update

v1.3L introduces `DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL`, a corrected Level 2
variant whose protected block is the formal sector-labeled kernel
`(0,18,36)` at `k_max=4`.

Corrected finite-basis result:

| Quantity | Value |
| --- | --- |
| status | `FORMAL_KERNEL_GAP_RESTORED` |
| protected sectors | `('lepton', 'up', 'down')` |
| first complement eigenvalue | `6.8171156827281205` |
| required Dirac lower bound | `0.8038064161349437` |
| H_T gap | `19592.076941940737` |
| margin vs mu_H | `6.81711568272658` |
| sector coupling vanishes on formal kernel | `True` |

The immediate finite-basis kernel bookkeeping issue is corrected. The
`zero_complement_projector` term remains `FINITE_BASIS_ONLY` until the formal
kernel, complement projector, and infinite-basis lower bound are derived from
the complete twisted Dirac / bundle action.

## v1.3M Corrected Formal-Kernel Regression Update

v1.3M reruns the lower-bound, sector-coupling, structured relative-bound, and
basis-convergence audits using `DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL`.

Corrected result:

| Quantity | Value |
| --- | --- |
| regression status | `FORMAL_KERNEL_CONVERGENCE_SUPPORTED` |
| direct lower bound | `6.8171156827281205` |
| min-max lower bound | `6.8171156827281205` |
| Gershgorin lower bound | `6.721838618515489` |
| sector-coupling structured lower bound | `6.729508865520464` |
| convergence rows | `27` |
| all convergence rows pass | `True` |
| worst direct margin | `4.833981204821612` |

Coordinate-first Level 2 conclusions are superseded where they depended on
the old protected block `(0,1,2)`. The corrected formal-kernel baseline should
be used for future Level 2 `H_T` regression, convergence, and bound audits.
Theorem status remains `False`.

## Limitations

- The report is an analytic-bound development scaffold over DIRAC_PROXY_LEVEL_2.
- It does not prove the full no-extra-light-state theorem.
- No frozen v1.0/v1.1 predictions or v1.2 action-origin outputs are changed.
