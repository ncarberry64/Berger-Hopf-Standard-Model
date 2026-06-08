# BHSM Infinite-Basis H_T Bound Closure Attempt

Status: `FORMAL_KERNEL_SCAFFOLD_STRONG`
Theorem complete: `False`

## Corrected Bounds

| Quantity | Value |
| --- | --- |
| required Dirac lower bound | `0.8038064161349437` |
| structured relative lower bound | `6.729508865520464` |
| exact finite lower bound | `6.8171156827281205` |
| heat-lift lower bound | `19591.98933512353` |

## Proof Nodes

| Node | Status | Open obligations |
| --- | --- | --- |
| `finite_formal_kernel_bound` | `FORMAL_KERNEL_SCAFFOLD_STRONG` | none |
| `infinite_basis_complement` | `INFINITE_BASIS_OPEN` | Prove an infinite-basis uniform complement lower bound independent of k_max.<br>Prove compactness/relative-bound hypotheses for the complete operator. |
| `operator_domain` | `INFINITE_BASIS_OPEN` | Specify the full Hilbert-space domain.<br>Prove self-adjointness and domain stability under twist/profile terms. |

## Limitations

- Finite/semi-analytic evidence is strong but is not an infinite-basis theorem.
- The full operator domain and topological index theorem remain open.
