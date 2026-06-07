# BHSM v1.3E Infinite Sector-Coupling Bound Scaffold

Status: `THEOREM_SCAFFOLD`
Theorem complete: `False`

BHSM v1.3E defines the Hilbert-space/domain assumptions under which the structured sector-coupling relative bound would extend beyond finite truncations. It does not prove the full H_T theorem until those assumptions and the zero-mode/complement split are derived from the complete operator.

## Finite Evidence Bridge

| Quantity | Value |
| --- | --- |
| `source` | `theory/uniform_relative_bound_report.json` |
| `classification` | `UNIFORM_BOUND_CANDIDATE` |
| `rows_scanned` | `108` |
| `k_max_max` | `32` |
| `all_rows_pass` | `True` |
| `all_b_k_zero` | `True` |
| `observed_max_a_k` | `0.03095889839310559` |
| `observed_min_structured_lower_bound` | `1.418773076862654` |
| `observed_min_finite_basis_lower_bound` | `1.4599918132873242` |
| `max_mode_block_band_width` | `2` |
| `theorem_complete` | `False` |

## Conservative Candidate

| Quantity | Value |
| --- | --- |
| `a_k_max` | `0.04` |
| `b_k` | `0.0` |
| `d0_candidate` | `1.4641` |
| `required_dirac_lower_bound` | `0.8038064161349437` |
| `candidate_structured_lower_bound` | `1.405536` |
| `margin` | `0.6017295838650562` |
| `passes` | `True` |

## Assumptions A1-A6

| ID | Status | Statement | Limitations |
| --- | --- | --- | --- |
| `A1` | `SUPPORTED_BY_FINITE_EVIDENCE` | K_sector preserves (k,j,q,chi) and only mixes charged-sector labels. | This structure is read from DIRAC_PROXY_LEVEL_2 and has not been derived for the full operator. |
| `A2` | `SUPPORTED_BY_FINITE_EVIDENCE` | K_sector has uniformly bounded mode-block bandwidth in the (k,j,chi,sector) ordering. | A finite ladder does not prove an infinite-basis bandwidth theorem. |
| `A3` | `ASSUMED_FOR_THEOREM_SCAFFOLD` | K_sector is D0^2-relative bounded on H_perp with a_K <= 0.04 and b_K = 0. | The uniform infinite-basis relative bound is not proven here. |
| `A4` | `SUPPORTED_BY_FINITE_EVIDENCE` | K_sector vanishes on the protected zero-mode subspace. | The protected zero-mode subspace itself remains a scaffold until the full kernel is proven. |
| `A5` | `OPEN` | The complement projection P_perp is well-defined and commutes with the relevant mode-block decomposition. | The infinite-dimensional complement projector compatibility is an open domain assumption. |
| `A6` | `ASSUMED_FOR_THEOREM_SCAFFOLD` | The diagonal complement lower bound d0 satisfies d0 >= d_required/(1-a_K^max), equivalently (1-a_K^max)d0 = 1.405536 >= d_required = 0.8038064161349437. | The infinite-basis diagonal complement lower bound is not proven here. |

## Conditional Implication

If A1-A6 hold on the full Hilbert-space domain, then K_sector is D0^2-relative bounded on H_perp and cannot close the required complement gap.

## Proof Obligations

- Derive A1-A2 from the full Berger-Hopf twisted Dirac/bundle action.
- Prove the A3 relative-bound inequality uniformly on the infinite basis.
- Prove the protected zero-mode subspace and complement projector in the full action.
- Prove the diagonal complement lower bound A6 on H_perp.

## v1.3G Zero-Mode/Complement Update

v1.3G adds:

- `theory/zero_mode_index_scaffold.md`
- `theory/complement_projector_report.md`
- `theory/index_theorem_scaffold_report.md`

The finite projector identities pass and exactly three protected zero-mode
candidates are recorded. The assumptions `I1`, `I3`, and `I5` remain open:
the topological index calculation, mirror zero-mode exclusion, and
trace-`U(1)` condition still need full-operator derivations. The infinite
sector-bound theorem therefore remains `THEOREM_SCAFFOLD`.

## Limitations

- This report defines assumptions under which the finite relative-bound evidence would extend beyond truncations.
- It does not prove those assumptions or complete the full H_T theorem.
