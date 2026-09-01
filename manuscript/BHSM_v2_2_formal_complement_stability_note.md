# BHSM v2.2 Formal Complement Stability Note

Status: `HT_THEOREM_CONDITIONAL_ON_INDEX_MIRROR`
Theorem complete: `False`

BHSM v2.2 formalizes the corrected sector-labeled formal kernel projector and its orthogonal complement. It proves the finite-rank projector algebra and finite-projector convergence inside the labeled Hilbert-space scaffold, while keeping perturbed-domain stability conditional on complete-operator identification.

## Status Table

| Dependency | Status |
| --- | --- |
| Formal kernel projector | `FORMAL_KERNEL_PROJECTOR_PROVEN` |
| Formal complement projector | `FORMAL_COMPLEMENT_PROJECTOR_PROVEN` |
| Projector domain stability | `PROJECTOR_DOMAIN_STABILITY_CONDITIONAL` |
| Finite-projector convergence | `FINITE_PROJECTOR_CONVERGENCE_PROVEN` |
| Complement lower-bound bridge | `COMPLEMENT_LOWER_BOUND_CONDITIONAL` |
| H_T dependency | `HT_THEOREM_CONDITIONAL_ON_INDEX_MIRROR` |

## Correct Claim

BHSM v2.2 closes the formal complement projector bridge at the scaffold level: the sector-labeled kernel projector is well-defined, the complement projector is orthogonal/self-adjoint/idempotent, finite projectors converge to the coordinate-free formal projector in the nested labeled basis, and the v2.1 lower bound applies conditionally to H_perp. The full H_T theorem remains conditional on topological index and mirror-mode closure.

## Open Obligations

- prove topological index theorem for the complete twisted Dirac operator
- exclude mirror zero modes in the complete chiral operator
- upgrade conditional perturbation-domain stability to complete-operator proof

## Limitations

- v2.2 closes the formal projector algebra and finite-projector convergence bridge.
- The full H_T theorem still requires index and mirror closure.
