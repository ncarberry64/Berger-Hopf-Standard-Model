# Derived Yukawa Allowed Operator Classes

| operator_class | active_field | scalar_field | singlet_field | hypercharge_sum | orientation_closes | cyclic_reference_closes | status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| cyclic_upper_closure | A_cyc | H | S_cyc_upper | 0 | True | True | ALLOWED_BOUNDARY_YUKAWA_OPERATOR |
| cyclic_lower_closure | A_cyc | H_tilde | S_cyc_lower | 0 | True | True | ALLOWED_BOUNDARY_YUKAWA_OPERATOR |
| reference_charged_closure | A_ref | H_tilde | S_ref_charged | 0 | True | True | ALLOWED_BOUNDARY_YUKAWA_OPERATOR |
| reference_neutral_closure | A_ref | H | S_ref_neutral | 0 | True | True | ALLOWED_BOUNDARY_YUKAWA_OPERATOR |

Status: `YUKAWA_ALLOWED_OPERATOR_CLASSES_DERIVED_CONDITIONAL`.

Follow-up: [Theorem discharge: Yukawa overlap texture source](theorem_discharge_yukawa_overlap_texture_source.md) uses these four allowed classes as parent operator classes for symbolic 3x3 boundary-overlap Yukawa matrix scaffolds. This does not derive numerical Yukawa values, mass ratios, or mixing matrices.
