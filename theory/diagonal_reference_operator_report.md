# BHSM v1.9 Diagonal Reference Operator Report

Status: `DIAGONAL_REFERENCE_OPERATOR_PROVEN`
Theorem complete: `True`

## Operator

- Symbol: `A0 = D_diag^2`
- Action: `A0 e_(sector,k,j,q,chi) = lambda_diag(k,j,a) e_(sector,k,j,q,chi)`
- Eigenvalue formula: `lambda_diag(k,j,a) = a^2 (k-2j)^2 + 2((2j+1)k - 2j^2)`
- Lower bound: `0.0`
- Eigenvalues real: `True`
- Tends to infinity: `True`

## Closure

- Closure candidate: maximal real diagonal multiplication operator on l2 with domain sum lambda_n^2 |x_n|^2 < infinity
- Self-adjoint extension candidate: closure of A0|C_fin

## Limitations

- This proves the diagonal multiplication-operator foundation in the abstract l2 scaffold.
- It does not prove relative boundedness of all BHSM perturbations.
