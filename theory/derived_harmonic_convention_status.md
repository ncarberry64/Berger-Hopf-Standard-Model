# Derived Harmonic Convention Status

| convention | ell | n | status | reason |
| --- | --- | --- | --- | --- |
| A: ell=k/2, n=j | `ell=k/2` | `n=j` | `FAILED_GUARDRAIL` | admissibility must hold for all modes; failures recorded |
| B: ell=k, n=j | `ell=k` | `n=j` | `STRUCTURALLY_MOTIVATED_NOT_DERIVED` | may avoid parity issue but must be derived from BHSM harmonic normalization |
| C: ell=k/2, n=j/2 | `ell=k/2` | `n=j/2` | `FAILED_GUARDRAIL` | requires derivation of fiber-weight normalization |
| D: ell=k/2, n=q/2 | `ell=k/2` | `n=q/2` | `STRUCTURALLY_MOTIVATED_NOT_DERIVED` | requires derivation tying q to the Wigner fiber/base weight |

Update: `theory/theorem_discharge_harmonic_highest_weight_normalization.md` conditionally derives Convention D for the `n` label. This page records the earlier PO-BH-26 status before the highest-weight normalization layer.

Status: `SELECTED_HARMONIC_CONVENTION_REMAINS_OPEN`.
