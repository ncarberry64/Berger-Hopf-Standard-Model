# BHSM v1.8 Infinite-Basis Domain and Relative-Bound Note

Branch: `bhsm-v1.8-infinite-basis-domain-proof`

## Purpose

BHSM v1.8 attacks the v1.7 operator-domain blocker by formalizing an infinite-basis Hilbert/domain scaffold, a uniform relative-bound theorem attempt, a Kato-Rellich-style self-adjointness closure attempt, and formal-complement projector stability.

This branch does not change frozen predictions, canonical constants, mode ledgers, prior scaffold outputs, or the virtual dressing rule.

## Formal Kernel

The corrected formal kernel is:

```text
K_formal = span{
  |ell,0,0,q=0,chi=-1>,
  |u,0,0,q=0,chi=-1>,
  |d,0,0,q=0,chi=-1>
}
```

The old coordinate-first kernel `(0,1,2)` is not used.

## v1.8 Status

| Chain Element | Status |
| --- | --- |
| Infinite-basis domain | `INFINITE_DOMAIN_CONDITIONAL` |
| Uniform relative bound | `UNIFORM_RELATIVE_BOUND_CONDITIONAL` |
| Self-adjointness closure | `SELF_ADJOINT_DOMAIN_CONDITIONAL` |
| Formal complement stability | `FORMAL_COMPLEMENT_CONDITIONAL` |
| H_T domain bridge | `HT_THEOREM_CANDIDATE_STRENGTHENED` |

## Relative-Bound Result

The v1.8 audit records a favorable aggregate relative-a estimate:

```text
total a <= 0.015621013485509948 < 1
```

The sector-coupling term inherits:

```text
a_K = 0.015621013485509948, b_K = 0
```

This supports a strengthened theorem candidate, but it does not prove the complete infinite-basis theorem because the Hopf, boundary, and sector-coupling infinite-basis comparison bounds remain conditional.

## Self-Adjointness Result

The Kato-Rellich-style closure remains conditional. Essential self-adjointness does not follow until the uniform relative-bound proof, diagonal reference operator core theorem, domain equality, and perturbation domain preservation are proven in the complete operator.

## Formal Complement Result

Projection algebra is clean for:

```text
P_perp = I - P_K_formal
```

However, full operator invariance and finite-projector convergence to the coordinate-free formal projector remain conditional. Therefore the formal complement status is `FORMAL_COMPLEMENT_CONDITIONAL`, not `FORMAL_COMPLEMENT_STABLE`.

## H_T Consequence

The H_T dependency status improves from the v1.7 domain blocker to:

```text
HT_THEOREM_CANDIDATE_STRENGTHENED
```

This is not `FULL_HT_THEOREM_PROVEN`. The full theorem still requires proof of the infinite-basis relative bounds, self-adjoint domain, formal-complement stability, topological index, and mirror exclusion.

## Limitation

BHSM v1.8 strengthens the mathematical bridge toward the full H_T theorem, but it does not prove the final theorem or permit final paper/Zenodo release.

