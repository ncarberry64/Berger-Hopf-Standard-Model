# BHSM v1.9 Diagonal-Core Self-Adjointness Note

Branch: `bhsm-v1.9-diagonal-core-self-adjointness`

## Purpose

BHSM v1.9 closes the diagonal reference-operator foundation needed by the Kato-Rellich route toward the full `H_T` theorem. It focuses only on:

- the infinite sector-labeled basis;
- the dense finite-mode core `C_fin`;
- the diagonal reference operator `A0 = D_diag^2`;
- essential self-adjointness of `A0|C_fin`;
- the graph-norm domain;
- Kato-Rellich preconditions.

It does not change frozen predictions, constants, mode ledgers, scaffold outputs, or the virtual dressing rule.

## Formal Kernel

The corrected formal kernel remains:

```text
K_formal = span{
  |ell,0,0,q=0,chi=-1>,
  |u,0,0,q=0,chi=-1>,
  |d,0,0,q=0,chi=-1>
}
```

The old coordinate-first kernel `(0,1,2)` is not used.

## Diagonal Operator

The diagonal reference operator is:

```text
A0 e_(sector,k,j,q,chi) = lambda_diag(k,j,a) e_(sector,k,j,q,chi)
```

with:

```text
lambda_diag(k,j,a) = a^2 (k-2j)^2 + 2((2j+1)k - 2j^2)
```

The eigenvalues are real and lower bounded. The finite-mode core is dense in the abstract `l2` sector-labeled basis.

## Essential Self-Adjointness Result

Status:

```text
DIAGONAL_CORE_ESSENTIALLY_SELF_ADJOINT_PROVEN
```

Proof route:

1. `A0` is a real diagonal multiplication operator on `l2`.
2. The finite sequences `C_fin` form a dense core.
3. The closure is the maximal diagonal multiplication operator with domain:

```text
D(A0) = {x in l2 : sum lambda_n^2 |x_n|^2 < infinity}
```

4. The deficiency equations `(A0^* - z)x = 0` for non-real `z` have only the zero `l2` solution because all `lambda_n` are real.
5. The deficiency indices are `(0,0)`.

This proves essential self-adjointness for the diagonal reference operator only.

## Graph-Norm Domain

Status:

```text
GRAPH_NORM_DOMAIN_PROVEN
```

The graph norm is:

```text
||x||_A0^2 = ||x||^2 + ||A0 x||^2
```

Finite truncations are dense in this graph norm for the maximal diagonal domain.

## Kato-Rellich Preconditions

Status:

```text
KATO_RELLICH_PRECONDITIONS_CONDITIONAL
```

The reference operator and graph-norm domain are now closed, but perturbation symmetry, perturbation domain inclusion, and full infinite-basis relative-bound proofs remain open.

## H_T Consequence

The H_T bridge status improves to:

```text
HT_THEOREM_REFERENCE_OPERATOR_CLOSED
```

This is not `FULL_HT_THEOREM_PROVEN`. It closes the reference-operator foundation while leaving the perturbed operator and full theorem obligations open.

