# BHSM Charm/Top Tension Audit

This diagnostic does not tune BHSM parameters, geometry, S, or the mode ledger.

## c/t Running Comparison

- Fixed-nf c/t reference: `0.004266868071316746`
- Fixed-nf relative error: `0.9476816285776762`
- Piecewise-nf c/t reference: `0.004251569034944846`
- Piecewise-nf relative error: `0.9546902533539826`

## Charm Mode Diagnostic

- Current charm mode: `(6, 0)`
- Current lambda: `60.1958738286423`
- Next admissible mode: `(10, 1)`
- Next-mode assessment: `overcorrects`

## Simple Normalization Factor Diagnostic

| Candidate | Value | Distance to threshold factor | Adopted |
| --- | --- | --- | --- |
| `1/2` | `0.5` | `0.01159000679731026` | `False` |
| `1/sqrt(3)` | `0.5773502691896258` | `0.06576026239231558` | `False` |
| `1/3` | `0.3333333333333333` | `0.17825667346397694` | `False` |
| `1/sqrt(2)` | `0.7071067811865475` | `0.1955167743892372` | `False` |
| `2*sqrt(alpha)` | `0.17084908626368245` | `0.3407409205336278` | `False` |
| `sqrt(alpha)` | `0.08542454313184122` | `0.42616546366546904` | `False` |

## Likely Root Cause Classification

The c/t tension is not removed by the approximate threshold-aware scaffold. It remains localized to the charm/up-sector comparison and may reflect top/charm reference ambiguity, missing precision threshold matching, a missing representation normalization, or a genuine BHSM charm-mode tension.

## Limitations

- Diagnostic only; no BHSM parameter, geometry, S, mode ledger, or normalization factor is changed.
- Top running-mass-like variant is a label-only placeholder reusing current values.
- Piecewise running remains approximate and is not precision QCD.
