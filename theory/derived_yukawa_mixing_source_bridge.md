# Derived Yukawa Mixing Source Bridge

Off-diagonal overlap entries feed future left diagonalization matrices.

```text
V_cyclic=U_cyclic_upper_L^dagger U_cyclic_lower_L
V_reference=U_reference_charged_L^dagger U_reference_neutral_L
```

Guardrails:

- no CKM values;
- no PMNS values.

Status: `YUKAWA_MIXING_SOURCE_BRIDGE_DERIVED_CONDITIONAL`.

Follow-up: [Theorem discharge: Yukawa distance-to-overlap law](theorem_discharge_yukawa_distance_overlap_law.md) keeps off-diagonal numerical overlap values open, so CKM and PMNS values remain open.

Follow-up: [Theorem discharge: legacy geometric-overlap bridge](theorem_discharge_legacy_geometric_overlap_bridge.md) identifies off-diagonal sources with geometric overlap/transport/moment structure, but does not derive numerical CKM or PMNS values.
