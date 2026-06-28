"""Minimal action terms and disabled author-axiom input."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from .common import ActionSourceTerm, MinimalActionTerm, VariationResult, repository_path


AXIOM_TEMPLATE = "data/theorem_inputs/minimal_action_axioms_template.json"
LEDGER = "artifacts/BHSM_symbolic_4d_lagrangian_assembly_ledger_v0_9.json"
BOUNDARY = "theory/boundary_action_to_rep_connection.md"
SECTORS = "artifacts/BHSM_boundary_source_matrices_v0_5.json"
CP_REPORT = "artifacts/BHSM_cp_o_int_field_action_report_v0_6.json"
X_REPORT = "artifacts/BHSM_x_ch_charged_boundary_response_theorem_v1_1.json"
NU_REPORT = "artifacts/BHSM_neutrino_dirac_majorana_basis_scale_theorem_v1_1.json"


def load_minimal_action_axioms(
    repository: str | Path | None = None,
    payload: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    if payload is not None:
        return dict(payload)
    path = repository_path(repository) / AXIOM_TEMPLATE
    if not path.is_file():
        return {"axioms": [], "source_status": "MISSING"}
    result = json.loads(path.read_text(encoding="utf-8"))
    result["source_status"] = "DISCOVERED"
    return result


REQUIRED_AXIOM_DEFINITIONS = {
    "cp_o_int": {
        "field_representation", "lorentz_structure", "gauge_representation",
        "coupling_normalization", "operator_mass_dimension", "coupling_mass_dimension",
        "action_source", "measure", "locality", "variation", "production_rule",
    },
    "X_ch": {
        "field_representation", "lorentz_structure", "gauge_representation",
        "coupling_normalization", "operator_mass_dimension", "coupling_mass_dimension",
        "action_source", "measure", "locality", "variation", "production_rule",
    },
    "neutrino_basis_scale": {
        "physical_basis_map", "dimensional_scale", "ordering_policy",
        "dirac_majorana_convention", "action_source", "measure", "observable_map",
    },
}


def enabled_complete_axiom(payload: Mapping[str, Any], theorem_key: str) -> dict[str, Any] | None:
    for row in payload.get("axioms", []):
        definitions = row.get("definitions", {})
        if (
            row.get("enabled") is True
            and row.get("complete_definition") is True
            and theorem_key in row.get("affected_theorems", [])
            and row.get("maximum_status") == "CONDITIONAL_ACTION_THEOREM"
            and REQUIRED_AXIOM_DEFINITIONS[theorem_key] <= set(definitions)
            and all(definitions[key] not in (None, "") for key in REQUIRED_AXIOM_DEFINITIONS[theorem_key])
        ):
            return dict(row)
    return None


def build_minimal_action_terms() -> tuple[MinimalActionTerm, ...]:
    return (
        MinimalActionTerm(
            "boundary",
            "S_boundary",
            "integral_boundary Psi^dagger (d + i A_rep) Psi",
            "topological and boundary base action",
            "CANDIDATE",
            (BOUNDARY,),
            "completed boundary action and boundary-to-4D projection",
        ),
        MinimalActionTerm(
            "sector",
            "S_sector",
            "sum_f Psi_f^dagger P_f Psi_f",
            "finite sector separation and admissibility",
            "CANDIDATE",
            (SECTORS,),
            "action derivation of the finite sector projectors",
        ),
        MinimalActionTerm(
            "phase",
            "S_phase",
            "Hol_CP = exp(i*pi/3) attached to admissible boundary structures",
            "CP/Z6 boundary holonomy constraint",
            "ARTIFACT_BACKED",
            (CP_REPORT, LEDGER),
            None,
        ),
        MinimalActionTerm(
            "charged",
            "S_charged",
            "integral_boundary <J_ch, X_ch(P_ch Psi_boundary)> + h.c.",
            "conditional charged boundary-response action",
            "CONDITIONAL_ACTION_THEOREM",
            (X_REPORT, LEDGER),
            None,
        ),
        MinimalActionTerm(
            "neutral",
            "S_neutral",
            "S_neutral_prop[Psi_nu, U_nu, R_curv]",
            "conditional propagation-locked curvature response",
            "CONDITIONAL_PROPAGATION_THEOREM",
            (NU_REPORT, LEDGER),
            None,
        ),
    )


def cp_action_source() -> ActionSourceTerm:
    return ActionSourceTerm(
        "L_CP_O_int",
        "G_raw exp(i delta_BH) O_int + h.c.",
        "undefined boundary/interface measure",
        "boundary/interface candidate",
        True,
        False,
        "OPEN_MISSING_ACTION_SOURCE",
        (CP_REPORT, LEDGER),
        "action-derived measure, normalized source, and variation",
    )


def x_ch_action_source() -> ActionSourceTerm:
    return ActionSourceTerm(
        "L_X_ch",
        "Psi_ch_bar C_ch_boundary Psi_ch X_ch",
        "undefined",
        "boundary-to-4D candidate",
        True,
        False,
        "OPEN_MISSING_FIELD_REPRESENTATION",
        (X_REPORT, LEDGER),
        "action-derived X_ch field representation",
    )


def neutrino_action_source() -> ActionSourceTerm:
    return ActionSourceTerm(
        "L_nu_boundary",
        "Psi_nu_bar K_nu Psi_nu",
        "boundary/interface measure",
        "neutral boundary seed",
        True,
        False,
        "OPEN_MISSING_PHYSICAL_BASIS",
        (NU_REPORT, LEDGER),
        "physical neutrino basis map",
    )


def missing_variation(field: str, status: str, source: tuple[str, ...], missing: str) -> VariationResult:
    return VariationResult(field, "not action-derived", "not defined", False, status, source, missing)
