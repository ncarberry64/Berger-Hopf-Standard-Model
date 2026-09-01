# BHSM v1.9 Diagonal-Core Essential Self-Adjointness Report

Status: `DIAGONAL_CORE_ESSENTIALLY_SELF_ADJOINT_PROVEN`
Theorem complete: `True`
Deficiency indices: `(0, 0)`

## Proof Routes

| Route | Passes | Statement |
| --- | --- | --- |
| `diagonal_multiplication_operator` | `True` | A real diagonal multiplication operator on l2 with finite sequences as a core is essentially self-adjoint; its closure is the maximal diagonal operator. |
| `deficiency_index_check` | `True` | For non-real z, (A0^* - z)x=0 has only the zero l2 solution because (lambda_n - z)x_n=0 and lambda_n is real. |
| `graph_norm_core` | `True` | Finite truncations converge in graph norm for every vector in the maximal diagonal domain. |

## Limitations

- Essential self-adjointness is proven only for the diagonal reference operator.
- Full BHSM self-adjointness still requires Kato-Rellich preconditions for perturbations.
