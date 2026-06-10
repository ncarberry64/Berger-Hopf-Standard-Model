# BHSM Full Theorem Package Completion Attempt

Status: `BHSM_THEOREM_PACKAGE_INCOMPLETE`
Theorem complete: `False`
Frozen outputs changed: `False`
Final paper allowed: `False`

## Theorem Nodes

| Node | Status | Gate status | Complete | Open obligations |
| --- | --- | --- | --- | --- |
| `canonical_constants` | `ACTION_DERIVED` | `FROZEN` | `True` | none |
| `operator_domain` | `OPEN` | `SELF_ADJOINT_DOMAIN_OPEN` | `False` | prove density and core stability in the complete Hilbert space<br>derive the complete Berger twisted Dirac spectral domain<br>prove self-adjointness via Kato-Rellich or equivalent relative-bound conditions in the complete operator<br>prove the formal kernel/complement split for the complete Hilbert-space operator |
| `ht_gap` | `STRONG_SCAFFOLD` | `FORMAL_KERNEL_SCAFFOLD_STRONG` | `False` | Prove an infinite-basis uniform complement lower bound independent of k_max.<br>Prove compactness/relative-bound hypotheses for the complete operator.<br>Specify the full Hilbert-space domain.<br>Prove self-adjointness and domain stability under twist/profile terms.<br>Prove the topological index theorem for the complete twisted Dirac operator.<br>Exclude mirror zero modes from the full chiral operator, not only the scaffold channels. |
| `index` | `OPEN` | `INDEX_THEOREM_OPEN` | `False` | derive the topological index of the complete twisted Dirac operator<br>prove absence of additional protected kernel states in the complete operator<br>prove the formal-kernel/complement split independently of finite truncation |
| `mirror_exclusion` | `OPEN` | `MIRROR_EXCLUSION_OPEN` | `False` | close the Higgs-selected U(1) mirror channel in the complete operator<br>close the boundary-functional mirror channel in the complete operator<br>connect mirror exclusion to the full topological index theorem |
| `scalar_topographic` | `STRONG_SCAFFOLD` | `SCALAR_FULL_ACTION_PROOF_OPEN` | `False` | derive all scalar/topographic screening channels from the complete action<br>prove global absence of unscreened direct light scalar matter couplings<br>connect scalar complement lifting to the full H_T theorem |
| `virtual_dressing` | `THEOREM_CANDIDATE` | `VIRTUAL_DRESSING_ADOPTION_CANDIDATE` | `False` | Derive the virtual-environment dressing factor from the full loop/threshold action.<br>Prove that weak-doublet projection uniquely yields Z_virt^{u,2}=1/2 in the complete theory.<br>Keep BHSM_DRESSED_V1_CANDIDATE noncanonical until the loop derivation is complete. |
| `qcd_rg` | `OPEN` | `PRECISION_INPUTS_REQUIRED` | `False` | Supply validated precision-QCD common-scheme quark mass inputs.<br>Implement validated two-/three-loop threshold matching if precision closure is required.<br>Propagate uncertainties from supplied precision inputs. |
| `unified_action` | `STRONG_SCAFFOLD` | `ACTION_SCAFFOLD_WITH_OPEN_NODES` | `False` | omega_f<br>ckm_cp<br>formal_kernel<br>ht_gap<br>scalar_topographic<br>virtual_dressing<br>qcd_rg<br>state_ontology |
| `forbidden_claims` | `FORBIDDEN` | `ACTIVE` | `True` | none |

## Open Obligations

- prove density and core stability in the complete Hilbert space
- derive the complete Berger twisted Dirac spectral domain
- prove self-adjointness via Kato-Rellich or equivalent relative-bound conditions in the complete operator
- prove the formal kernel/complement split for the complete Hilbert-space operator
- Prove an infinite-basis uniform complement lower bound independent of k_max.
- Prove compactness/relative-bound hypotheses for the complete operator.
- Specify the full Hilbert-space domain.
- Prove self-adjointness and domain stability under twist/profile terms.
- Prove the topological index theorem for the complete twisted Dirac operator.
- Exclude mirror zero modes from the full chiral operator, not only the scaffold channels.
- derive the topological index of the complete twisted Dirac operator
- prove absence of additional protected kernel states in the complete operator
- prove the formal-kernel/complement split independently of finite truncation
- close the Higgs-selected U(1) mirror channel in the complete operator
- close the boundary-functional mirror channel in the complete operator
- connect mirror exclusion to the full topological index theorem
- derive all scalar/topographic screening channels from the complete action
- prove global absence of unscreened direct light scalar matter couplings
- connect scalar complement lifting to the full H_T theorem
- Derive the virtual-environment dressing factor from the full loop/threshold action.
- Prove that weak-doublet projection uniquely yields Z_virt^{u,2}=1/2 in the complete theory.
- Keep BHSM_DRESSED_V1_CANDIDATE noncanonical until the loop derivation is complete.
- Supply validated precision-QCD common-scheme quark mass inputs.
- Implement validated two-/three-loop threshold matching if precision closure is required.
- Propagate uncertainties from supplied precision inputs.
- omega_f
- ckm_cp
- formal_kernel
- ht_gap
- scalar_topographic
- virtual_dressing
- qcd_rg
- state_ontology

## Forbidden Claims

- Do not claim the full BHSM theorem package is complete while any node remains open.
- Do not prepare final paper/Zenodo release unless status is FULL_BHSM_THEOREM_PACKAGE_COMPLETE.
