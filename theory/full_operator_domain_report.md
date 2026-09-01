# BHSM Full Operator and Domain Theorem Attempt

Status: `SELF_ADJOINT_DOMAIN_OPEN`
Theorem complete: `False`

## Hilbert Space and Kernel

Hilbert space: H = l2-completion of sector-labeled Berger-Hopf twisted spinor modes
Mode basis: `|sector,k,j,q,chi> with q=k-2j and sector in {ell,u,d}`

Formal kernel:

- `|ell,0,0,q=0,chi=-1>`
- `|u,0,0,q=0,chi=-1>`
- `|d,0,0,q=0,chi=-1>`

Complement: `H_perp = K_formal^perp`
Operator: `D_FK^2 = D_diag^2 + V_Hopf + V_boundary + V_chi + K_sector + P_perp_lift`

## Operator Terms

| Term | Expression | Domain status | Can lower gap | Limitations |
| --- | --- | --- | --- | --- |
| `D_diag_squared` | `D_diag^2` | `CANDIDATE_DOMAIN` | `False` | none |
| `V_Hopf` | `V_Hopf` | `DOMAIN_PRESERVATION_OPEN` | `True` | complete relative-bound proof needed |
| `V_boundary` | `V_boundary` | `DOMAIN_PRESERVATION_OPEN` | `True` | derive complete boundary functional domain action |
| `V_chi` | `V_chi` | `DOMAIN_PRESERVATION_OPEN` | `True` | prove projector compatibility in complete operator |
| `K_sector` | `K_sector` | `RELATIVE_BOUND_CANDIDATE` | `True` | upgrade finite/uniform scans to complete operator bound |
| `P_perp_lift` | `P_perp_lift` | `PROJECTOR_DOMAIN_OPEN` | `False` | prove formal projector for complete Hilbert space |

## Open Obligations

- prove density and core stability in the complete Hilbert space
- derive the complete Berger twisted Dirac spectral domain
- prove self-adjointness via Kato-Rellich or equivalent relative-bound conditions in the complete operator
- prove the formal kernel/complement split for the complete Hilbert-space operator

## Forbidden Claims

- Do not promote finite-matrix Hermiticity to full self-adjointness.
- Do not claim FULL_HT_THEOREM_PROVEN while SELF_ADJOINT_DOMAIN_OPEN remains.
