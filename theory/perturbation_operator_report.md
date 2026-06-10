# BHSM v2.0 Perturbation Operator Inventory

Status: `PERTURBATION_INVENTORIED`
Reference operator: `A0 = D_diag^2`
Perturbation: `V = V_Hopf + V_boundary + V_chi + K_sector`
Total relative a: `0.015621013485509948`

| Term | Symmetry | Domain | a | b | Infinite-basis status | Open obligations |
| --- | --- | --- | --- | --- | --- | --- |
| `V_Hopf` | `SYMMETRIC_CANDIDATE` | `DOMAIN_CONDITIONAL` | `0.0` | `0.0` | `CONDITIONAL` | prove q-growth is A0-relative bounded on D(A0) |
| `V_boundary` | `SYMMETRIC_CANDIDATE` | `DOMAIN_CONDITIONAL` | `0.0` | `0.0` | `CONDITIONAL` | prove Omega_f growth is A0-relative bounded on D(A0) |
| `V_chi` | `SYMMETRY_PROVEN` | `DOMAIN_INCLUDED` | `0.0` | `1.0` | `PROVEN_BOUNDED` | none |
| `K_sector` | `SYMMETRIC_CANDIDATE` | `DOMAIN_CONDITIONAL` | `0.015621013485509948` | `0.0` | `CONDITIONAL` | upgrade sparse/banded finite-scan evidence to a complete infinite-basis operator bound |
| `P_perp_lift` | `SYMMETRY_PROVEN` | `DOMAIN_CONDITIONAL` | `0.0` | `0.0` | `CONDITIONAL` | prove formal complement projector preserves D(A0) |
| `PSD_profile` | `SYMMETRY_PROVEN` | `DOMAIN_INCLUDED` | `0.0` | `0.0` | `PROVEN_PSD_SCAFFOLD` | none |

## Limitations

- This is an operator-theoretic inventory, not a full perturbation theorem.
- Finite-scan evidence is flagged explicitly where used.
