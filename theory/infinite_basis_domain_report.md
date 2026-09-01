# BHSM v1.8 Infinite-Basis Domain Report

Status: `INFINITE_DOMAIN_CONDITIONAL`
Theorem complete: `False`
Old coordinate-first kernel used: `False`

## Domain Definitions

- Hilbert space: `H = l2({sector,k,j,q,chi}) over sector in {ell,u,d}, q=k-2j`
- Infinite basis: `|sector,k,j,q,chi> with k>=0, 0<=j<=k, chi in {-1,+1}`
- Dense core: `C_fin = finite-support span of the infinite labeled basis`
- Graph norm: `||psi||_D0^2 = ||psi||^2 + ||D0 psi||^2`
- Formal complement: `H_perp = K_formal^perp`

## Formal Kernel

- `|ell,0,0,q=0,chi=-1>`
- `|u,0,0,q=0,chi=-1>`
- `|d,0,0,q=0,chi=-1>`

## Components

| ID | Status | Open obligations |
| --- | --- | --- |
| `hilbert_basis` | `INFINITE_DOMAIN_DEFINED` | none |
| `finite_core` | `INFINITE_DOMAIN_DEFINED` | none |
| `graph_norm_closure` | `INFINITE_DOMAIN_CONDITIONAL` | prove the complete diagonal Berger/twisted Dirac spectrum and graph-norm closure |
| `perturbation_domain` | `INFINITE_DOMAIN_CONDITIONAL` | upgrade every finite/scaffold bound to an infinite-basis operator bound |
| `formal_kernel_domain` | `INFINITE_DOMAIN_DEFINED` | none |
| `formal_complement_domain` | `INFINITE_DOMAIN_CONDITIONAL` | prove the full operator leaves K_formal and/or H_perp invariant or block-controlled |

## Limitations

- The infinite Hilbert/domain scaffold is explicit, but graph-norm closure and perturbation domains remain conditional.
- The old coordinate-first kernel (0,1,2) is not used.
