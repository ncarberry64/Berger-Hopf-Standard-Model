# Charged-Lepton Dressing Formula Integrity Audit

## Summary

Classification: `FORMULA_CONSISTENT`
Candidate status: `CANDIDATE_NOT_OFFICIAL`
Documentation/code match: `True`
Prior candidate remains valid: `True`
Lepton precision blocker closed: `False`

## Formula Check

Originally reported formula: `Z_l(k,j)=exp[-eta_l*(q^2+j^2)]`
Actual implemented formula: `Z_l(k,j)=exp[-eta_l*((k-2j)^2+j^2)]`
Definition: `q = k - 2j`

The earlier ambiguity is that `q` is the Hopf charge `k-2j`, not the coordinate `k`.

## Implemented Exponents

| Rank | Ratio | Mode | k | j | q=k-2j | Implemented exponent | Tau exponent |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `middle` | `mu/tau` | `(5, 2)` | `5` | `2` | `1` | `5.0` | `0.0` |
| `light` | `e/tau` | `(9, 3)` | `9` | `3` | `3` | `18.0` | `0.0` |

## Candidate Norm Scan

| Norm | Mu exponent | Electron exponent | eta_l | Held-out e/tau | e/tau relative error | Improves e/tau | Note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `q` | `1.0` | `3.0` | `0.010221719572118334` | `0.0002883129481062665` | `0.0025299366507519337` | `True` | Hopf-fiber-only diagnostic; numerically strong but ignores base index. |
| `j` | `2.0` | `3.0` | `0.005110859786059167` | `0.00029276759258900855` | `0.018019752423573097` | `True` | Base-index-only diagnostic; ignores Hopf charge. |
| `q+j` | `3.0` | `6.0` | `0.003407239857372778` | `0.00029127511564232207` | `0.012830069377278494` | `True` | Simple additive Hopf/base diagnostic. |
| `q^2+j^2` | `5.0` | `18.0` | `0.0020443439144236667` | `0.0002865501268883495` | `0.0035997951408065676` | `True` | Current predeclared Hopf/base norm candidate using q=k-2j. |
| `sqrt(q^2+j^2)` | `2.23606797749979` | `4.242640687119285` | `0.004571291962039332` | `0.0002915808497597548` | `0.013893176696582217` | `True` | Euclidean Hopf/base amplitude diagnostic. |
| `2q` | `2.0` | `6.0` | `0.005110859786059167` | `0.0002883129481062665` | `0.0025299366507519337` | `True` | Fiber-weight diagnostic; numerically degenerate with q for held-out ratio ordering. |
| `q+3j` | `7.0` | `12.0` | `0.001460245653159762` | `0.0002921270254774223` | `0.015792354347915302` | `True` | Diagnostic only; a three-base-weight variant motivated by generation/coframe bookkeeping, not adopted. |

## Best Candidates

Best numerical held-out candidate: `q`
Best structurally motivated current candidate: `q^2+j^2`

The best numerical row is not official. The current `q^2+j^2` row remains the scoped candidate from the precision sprint because it uses both Hopf charge and base index.

## Frozen Output Check

Official outputs changed: `False`
Official lepton ratios changed: `False`
Dressed branch changes only c/t: `True`

## Limitations

- All candidate norms fit eta_l from mu/tau, so none is independently derived.
- The q^2+j^2 candidate uses Hopf charge q=k-2j, not the coordinate k.
- The best numerical held-out candidate is still exploratory and non-official.
- Frozen BHSM_BARE_V1 and BHSM_DRESSED_V1_CANDIDATE outputs are unchanged.
- The lepton precision blocker remains open.
- Official branch comparison changes only ['c/t'].
