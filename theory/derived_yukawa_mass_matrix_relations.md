# Derived Yukawa Mass Matrix Relations

For each allowed boundary closure class:

```text
M_f = v/sqrt(2) * Y_f
```

- `M_cyclic_upper=v/sqrt(2)*Y_cyclic_upper`
- `M_cyclic_lower=v/sqrt(2)*Y_cyclic_lower`
- `M_reference_charged=v/sqrt(2)*Y_reference_charged`
- `M_reference_neutral=v/sqrt(2)*Y_reference_neutral`

Guardrails:

- `v` remains symbolic in this theorem layer.
- numerical masses are not predicted in this branch.
- frozen mass-ratio outputs are not changed.

Status: `YUKAWA_MASS_MATRIX_RELATIONS_DERIVED_CONDITIONAL`.

Follow-up: [Theorem discharge: Yukawa overlap-kernel selection](theorem_discharge_yukawa_overlap_kernel_selection.md) refines the symbolic mass hierarchy bridge by identifying leading diagonal kernel sources. It does not derive numerical masses or mass ratios.
