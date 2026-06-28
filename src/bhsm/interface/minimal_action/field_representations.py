"""Field representations exposed by existing local action artifacts."""

from __future__ import annotations

from .common import FieldRepresentation


CP_SOURCES = (
    "artifacts/BHSM_cp_o_int_field_action_report_v0_6.json",
    "artifacts/BHSM_effective_lagrangian_candidate_v0_3.json",
)
X_SOURCES = (
    "artifacts/BHSM_x_ch_charged_boundary_response_theorem_v1_1.json",
    "artifacts/BHSM_vertex_source_target_map_v0_5.json",
)
NU_SOURCES = (
    "artifacts/neutral_operator_no_fit_output_v1.json",
    "artifacts/BHSM_neutrino_dirac_majorana_basis_scale_theorem_v1_1.json",
)


def cp_field_representation() -> FieldRepresentation:
    return FieldRepresentation(
        "Psi_CP_interface",
        "CP boundary/interface channel",
        "CP boundary/interface channel",
        "abstract bilinear field candidate",
        "gauge representation not action-derived",
        "not action-derived",
        "not action-derived",
        "Hermitian conjugate requested by symbolic ledger",
        "CANDIDATE",
        CP_SOURCES,
        "physical field representation and boundary-to-4D identification",
    )


def x_ch_field_representation() -> FieldRepresentation:
    return FieldRepresentation(
        "X_ch^mu",
        "charged boundary-response channel",
        "four-dimensional production field space",
        "vector index is suggested but spin representation is not derived",
        "not derived",
        "not applicable until field content is fixed",
        "charged-sector ledger only",
        "not derived",
        "OPEN_MISSING_FIELD_REPRESENTATION",
        X_SOURCES,
        "action-derived X_ch field representation",
    )


def neutrino_boundary_representation() -> FieldRepresentation:
    return FieldRepresentation(
        "Psi_nu",
        "three-dimensional neutral boundary channel basis",
        "three-dimensional neutral boundary channel basis",
        "boundary-operator bilinear seed",
        "neutral boundary channel representation",
        "not fixed physically",
        "three neutral boundary channels",
        "Dirac/Majorana rule not fixed",
        "ARTIFACT_BACKED",
        NU_SOURCES,
        "map from neutral boundary channels to physical neutrino states",
    )
