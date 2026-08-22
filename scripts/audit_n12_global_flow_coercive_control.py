"""Audit whether an existing action-owned invariant globalizes child flow."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
LOCAL_FLOW = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_LOCAL_CONTINUUM_GALERKIN_FLOW.json"
)
JOIN = ROOT / "artifacts/BHSM_aether_degree_one_join_state_map_v15_23.json"
CROSS = ROOT / "artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
QXI = ROOT / (
    "artifacts/qxi_relative_energy_preparation/"
    "BHSM_N12_MATCHED_PARENT_QXI_OWNERSHIP.json"
)
PARENT = ROOT / (
    "artifacts/qxi_relative_energy_preparation/"
    "BHSM_N12_MATCHED_PARENT_STATIONARY_SECTION_GATE.json"
)
PERSISTENCE = ROOT / "artifacts/BHSM_aether_persistent_nonequilibrium_child_v17_87.json"
THEOREM = ROOT / "theory/n12_global_flow_coercive_control.md"
RESULT = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_GLOBAL_FLOW_COERCIVE_CONTROL_GATE.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    inputs = (LOCAL_FLOW, JOIN, CROSS, QXI, PARENT, PERSISTENCE, THEOREM)
    missing = [str(path) for path in inputs if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing coercive-control inputs: " + ", ".join(missing))
    local_flow = _load(LOCAL_FLOW)
    join = _load(JOIN)
    cross = _load(CROSS)["cross_resolution_reconnaissance"]
    qxi = _load(QXI)
    parent = _load(PARENT)
    persistence = _load(PERSISTENCE)

    form = join["gravitational_velocity_form"]
    matrix = np.asarray(form["matrix"], dtype=float)
    eigenvalues = np.linalg.eigvalsh(matrix)
    null_direction = np.asarray([-2.5, 1.0, 0.0])
    null_value = float(null_direction @ matrix @ null_direction)
    local_energy = cross["N6_reduced_local_energy_readout_reconnaissance"]
    first_missing = (
        "DERIVE_THE_CONSTRAINT_REDUCED_GAUGE_QUOTIENTED_RETAINED_CHILD_"
        "ENERGY_IDENTITY_AND_PROVE_A_COERCIVE_STRONG_S2_ESTIMATE_ON_THE_"
        "CONTINUUM_CHILD_COMPONENT_OR_LOCALIZE_ITS_ACTION_OWNED_FAILURE"
    )
    validation = {
        "local_continuum_flow_is_certified": local_flow[
            "validation_passed"
        ] is True,
        "ADM_velocity_form_has_both_signs": (
            float(np.min(eigenvalues)) < 0.0 < float(np.max(eigenvalues))
        ),
        "exact_unbounded_null_cone_direction_exists": abs(null_value) < 1.0e-14,
        "fixed_volume_is_not_substituted_for_constraints": (
            "not_a_substitute" in form["constraint_warning"]
        ),
        "local_Legendre_energy_is_not_Delta_H_or_mass": (
            local_energy["is_Delta_H6"] is False
            and local_energy["is_a_mass_measurement"] is False
        ),
        "complete_Q_xi_is_unavailable": (
            qxi["Q_xi_evaluated"] is False
            and qxi["required_boundary_improved_charge"][
                "complete_common_reference_Q_xi_assembler_available"
            ] is False
        ),
        "matched_parent_section_is_unavailable": parent[
            "R_P_executable"
        ] is False,
        "persistence_domain_requires_the_same_admissible_action_flow": (
            "same_action_owned_child_flow" in persistence[
                "persistence_and_decay_contract"
            ]["persistence_domain_B_child"]["dynamic_domain"]
        ),
        "no_local_energy_mass_or_parent_subtraction_promoted": True,
    }
    payload = {
        "artifact": "BHSM_N12_GLOBAL_FLOW_COERCIVE_CONTROL_GATE",
        "classification": (
            "UNREDUCED_AUTONOMOUS_ENERGY_IS_NOT_COERCIVE;_PHYSICAL_"
            "CONSTRAINT_REDUCED_STRONG_SPACE_ENERGY_ESTIMATE_IS_OPEN"
        ),
        "inputs": {
            str(path.relative_to(ROOT)).replace("\\", "/"): _sha256(path)
            for path in inputs
        },
        "exact_unreduced_countersequence": {
            "quadratic_form": form["quadratic_form"],
            "matrix": form["matrix"],
            "eigenvalues": [float(value) for value in eigenvalues],
            "base_null_direction": null_direction.tolist(),
            "base_quadratic_value": null_value,
            "sequence": "z_k=k*(-5/2,1,0)",
            "quadratic_value_for_every_k": 0.0,
            "norm_tends_to_infinity": True,
            "scope": (
                "UNREDUCED_ADM_METRIC_VELOCITY_BLOCK_ONLY;_NOT_A_"
                "COUNTEREXAMPLE_ON_THE_UNKNOWN_PHYSICAL_CONSTRAINT_QUOTIENT"
            ),
        },
        "owned_and_missing_energy_structure": {
            "autonomous_local_Legendre_energy_available": True,
            "local_energy_quadrature_converged": False,
            "local_energy_is_complete_Q_xi": False,
            "local_energy_is_Delta_H_or_mass": False,
            "matched_parent_relative_charge_available": False,
            "constraint_reduced_gauge_quotiented_positive_energy_theorem": False,
            "coercive_S2_bound_on_continuum_child_component": False,
        },
        "global_flow_consequence": {
            "local_continuum_flow_remains_certified": True,
            "globalization_by_unreduced_energy_conservation_allowed": False,
            "finite_analytic_action_ball_cover_is_an_alternative_proof_route": True,
            "numerical_sampling_alone_is_a_proof_route": False,
            "first_missing_action_owned_object": first_missing,
        },
        "prediction_frozen": False,
        "FULL_BHSM_COMPLETE": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({
        "classification": payload["classification"],
        "null_direction_quadratic_value": null_value,
        "first_missing_action_owned_object": first_missing,
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
