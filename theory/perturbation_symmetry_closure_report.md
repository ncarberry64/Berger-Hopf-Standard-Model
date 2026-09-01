# BHSM v2.1 Perturbation Symmetry Closure

Status: `PERTURBATION_SYMMETRY_TERMWISE_CONDITIONAL`
Theorem complete: `False`
All symmetric on finite core: `True`
All termwise symmetric on D(A0): `True`

| Term | Core symmetry | D(A0) symmetry | Status | Evidence |
| --- | --- | --- | --- | --- |
| `V_Hopf` | `True` | `True` | `SYMMETRIC_ON_DA0_CONDITIONAL` | relative diagonal domination by Berger action q^2 <= C lambda_diag<br>the q-growth comparison holds for the complete Berger twisted diagonal action |
| `V_boundary` | `True` | `True` | `SYMMETRIC_ON_DA0_CONDITIONAL` | linear boundary growth controlled by diagonal action<br>Omega_f growth remains at most linearly controlled by the complete diagonal action. |
| `V_chi` | `True` | `True` | `SYMMETRIC_ON_DA0_CONDITIONAL` | bounded projector<br>chirality remains a bounded involutive/projector label in the complete basis |
| `K_sector` | `True` | `True` | `SYMMETRIC_ON_DA0_CONDITIONAL` | sector-coupling matrix is symmetric by paired sector block rule<br>The complete sector-coupling rule has the same fixed-label sparse support as the formal-kernel scaffold.<br>The sector-coupling weights are uniformly bounded by the stated scaffold weight.<br>The diagonal reference action dominates the fixed-label sector-coupling quadratic form. |
| `P_perp_lift` | `True` | `True` | `SYMMETRIC_ON_DA0_CONDITIONAL` | bounded formal-complement heat-lift projector<br>the formal complement projector has a bounded infinite-basis limit preserving D(A0) |
| `PSD_profile` | `True` | `True` | `SYMMETRIC_ON_DA0_CONDITIONAL` | positive semidefinite topographic/profile contribution<br>the profile contribution is nonnegative on the formal complement |

## Open Obligations

- identify each symmetric scaffold term with the corresponding complete operator term on D(A0)
- prove the complete sector-coupling block remains symmetric under the infinite-basis pairing rule

## Limitations

- Termwise symmetry is explicit under v2.1 scaffold assumptions.
- It is not upgraded to PERTURBATION_SYMMETRY_PROVEN for the complete operator.
