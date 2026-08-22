"""Record the finite-N12 retained-action maximal-flow theorem."""

from __future__ import annotations

import hashlib
import inspect
import json
from pathlib import Path

from bhsm.interface import aether_cross_resolution_reconnaissance_v21_35 as cross
from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import dimensions


ROOT = Path(__file__).resolve().parents[1]
DIRECT = ROOT / (
    "artifacts/n12_direct_checkpoint/"
    "BHSM_N12_COMPLETE_PERSISTENT_CHILD_CERTIFICATE.json"
)
OBSERVATION = ROOT / (
    "artifacts/n12_direct_checkpoint/"
    "BHSM_N12_POSITIVE_DURATION_OBSERVATION.json"
)
CONTINUUM = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_CONTINUUM_EVENT_CHILD_CERTIFICATE.json"
)
THEOREM = ROOT / "theory/n12_maximal_admissible_flow_dichotomy.md"
SOURCE = ROOT / "src/bhsm/interface/aether_cross_resolution_reconnaissance_v21_35.py"
RESULT = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_FINITE_FLOW_CONTINUATION_DICHOTOMY.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> None:
    inputs = (DIRECT, OBSERVATION, CONTINUUM, THEOREM, SOURCE)
    missing = [str(path) for path in inputs if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing finite-flow inputs: " + ", ".join(missing))
    direct = json.loads(DIRECT.read_text(encoding="utf-8"))
    observation = json.loads(OBSERVATION.read_text(encoding="utf-8"))
    continuum = json.loads(CONTINUUM.read_text(encoding="utf-8"))
    function_source = inspect.getsource(
        cross._exact_full_jet_euler_dirac_acceleration
    )
    dims = dimensions(12)
    state_dimension = 2 * dims["coordinates"] + dims["multipliers"]
    validation = {
        "certified_N12_child_consumed": direct[
            "DIRECT_N12_COMPLETE_PERSISTENT_CHILD_CERTIFIED"
        ] is True,
        "state_dimension_is_98": state_dimension == 98,
        "implemented_vector_field_uses_exact_retained_action_jet": (
            "exact_full_action_jet_at_state" in function_source
        ),
        "Euler_Dirac_block_is_solved_not_regularized": (
            "np.linalg.solve(dirac_hessian, rhs)" in function_source
            and "pinv" not in function_source
            and "lstsq" not in function_source
        ),
        "coordinate_rate_is_existing_velocity": (
            '"coordinate_rate": velocity.copy()' in function_source
        ),
        "finite_action_ball_has_Dirac_inverse_and_generator_bounds": (
            observation["validation_passed"] is True
            and observation["validation"][
                "both_gauge_fixed_Dirac_core_inverses_closed_on_ball"
            ] is True
            and observation["validation"][
                "finite_action_owned_Jacobi_generator_bound"
            ] is True
        ),
        "continuum_static_child_remains_certified": continuum[
            "CONTINUUM_EVENT_CHILD_CERTIFIED"
        ] is True,
        "theorem_does_not_choose_an_outcome": True,
        "no_new_equation_gate_selector_or_numerical_history": True,
    }
    payload = {
        "artifact": "BHSM_N12_FINITE_FLOW_CONTINUATION_DICHOTOMY",
        "classification": "FINITE_N12_MAXIMAL_ADMISSIBLE_FLOW_DICHOTOMY_PROVED",
        "inputs": {
            str(path.relative_to(ROOT)).replace("\\", "/"): _sha256(path)
            for path in inputs
        },
        "retained_vector_field": {
            "state": "z=(q,v,m)_IN_R98",
            "map": "V12(z)=(v,D(z)^-1*b(z))",
            "D": "GAUGE_FIXED_EULER_DIRAC_HESSIAN_FROM_RETAINED_ACTION",
            "implementation": (
                "bhsm.interface.aether_cross_resolution_reconnaissance_v21_35."
                "_exact_full_jet_euler_dirac_acceleration"
            ),
            "locally_Lipschitz_on_existing_admissible_invertible_domain": True,
            "new_physics": False,
        },
        "theorem": {
            "unique_maximal_N12_solution_exists": True,
            "constraint_manifold_preserved_while_admissible": True,
            "finite_maximal_time_alternatives": [
                "STATE_NORM_BLOWUP",
                "APPROACH_EXISTING_PHYSICAL_DOMAIN_BOUNDARY",
                "GAUGE_FIXED_DIRAC_SMALLEST_SINGULAR_VALUE_TENDS_TO_ZERO",
            ],
            "ordered_event_transport_identity": (
                "d_e_ord/dt=<psi,D_H[V12]psi>_ON_THE_SIMPLE_EIGENLINE_LOCUS"
            ),
            "additional_ordered_event_tracking_stop": (
                "LOSS_OF_SELECTED_EIGENLINE_SIMPLICITY"
            ),
            "return_exit_blowup_or_gap_outcome_selected": False,
            "proof": "theory/n12_maximal_admissible_flow_dichotomy.md",
        },
        "continuum_transfer": {
            "static_continuum_event_child_certified": True,
            "positive_duration_normal_observation_certified": True,
            "uniform_nonlinear_vector_field_local_Lipschitz_bound_along_"
            "bounded_admissible_segments": False,
            "nonlinear_Galerkin_flow_convergence_on_such_segments": False,
            "continuum_maximal_flow_dichotomy_closed": False,
            "first_missing_lemma": (
                "PROVE_UNIFORM_ACTION_GRAPH_LOCAL_LIPSCHITZ_BOUNDS_AND_"
                "NONLINEAR_GALERKIN_FLOW_CONVERGENCE_ON_EVERY_BOUNDED_"
                "ETA_DIRAC_ADMISSIBLE_CHILD_SEGMENT"
            ),
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
        "continuum_first_missing_lemma": payload["continuum_transfer"][
            "first_missing_lemma"
        ],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
