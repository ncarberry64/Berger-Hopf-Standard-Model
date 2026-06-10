# BHSM Full H_T Theorem Closure Attempt

Status: `FORMAL_KERNEL_SCAFFOLD_STRONG`
Theorem complete: `False`

## Corrected Formal Kernel

`K_formal = span{|ell,0,0,q=0,chi=-1>, |u,0,0,q=0,chi=-1>, |d,0,0,q=0,chi=-1>}`

k_max=4 coordinates: `(0, 18, 36)`

## Bound Summary

| Bound | Value |
| --- | --- |
| required Dirac lower bound | `0.8038064161349437` |
| structured relative lower bound | `6.729508865520464` |
| exact finite lower bound | `6.8171156827281205` |
| heat-lift lower bound | `19591.98933512353` |

## v1.7 Dependency Status

`HT_THEOREM_BLOCKED_BY_DOMAIN`

The corrected formal-kernel H_T scaffold remains strong, but v1.7 keeps the full theorem blocked by the complete operator-domain/self-adjointness chain before index and mirror closure can upgrade the theorem.

## v1.8 Domain Bridge Status

`HT_THEOREM_CANDIDATE_STRENGTHENED`

The v1.8 domain bridge records favorable conditional infinite-basis relative-bound structure, but it does not prove the full H_T theorem.

## Remaining Open Nodes

- Prove an infinite-basis uniform complement lower bound independent of k_max.
- Prove compactness/relative-bound hypotheses for the complete operator.
- Specify the full Hilbert-space domain.
- Prove self-adjointness and domain stability under twist/profile terms.
- Prove the topological index theorem for the complete twisted Dirac operator.
- Exclude mirror zero modes from the full chiral operator, not only the scaffold channels.

## Correct Claim

The corrected formal-kernel H_T scaffold is strong and clears current finite/semi-analytic thresholds; the full H_T theorem remains open pending infinite-basis, domain, and index proofs.

## Forbidden Claims

- Do not claim FULL_HT_THEOREM_PROVEN.
- Do not claim the no-extra-light-state theorem is proven.
- Do not use coordinate-first protected block (0,1,2) as the corrected formal kernel.
