# Derived Yukawa Mixing Scaffold

Symbolic diagonalization:

```text
U_f_L^dagger Y_f U_f_R = D_f
```

Cyclic scaffold:

```text
V_cyclic=U_cyclic_upper_L^dagger U_cyclic_lower_L
```

Reference scaffold:

```text
V_reference=U_reference_charged_L^dagger U_reference_neutral_L
```

Guardrails:

- CKM values are not derived.
- PMNS values are not derived.
- measured mixing angles are not derived.
- this branch only defines the scaffold that future overlap values feed into.

Status: `YUKAWA_MIXING_SCAFFOLD_DERIVED_CONDITIONAL`.

Follow-up: [Theorem discharge: Yukawa overlap-kernel selection](theorem_discharge_yukawa_overlap_kernel_selection.md) records off-diagonal overlap entries as conditional symbolic mixing sources. It does not derive CKM or PMNS values.
