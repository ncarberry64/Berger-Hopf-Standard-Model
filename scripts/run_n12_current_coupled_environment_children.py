"""Join current N12 modes, child form jets and the known parent action load.

One execution uses the cached current48-node history, reconstructs its moving
first-hit clock and child coefficient jets, evaluates both mixed Dirac form
blocks on that same47-element mesh, and returns the known minus-zeta parent
gradient component. Individual heat channels retain their separate scaled
cotangents and logarithmic factors. They are not graded into a full action.

The reusable result exposes ``parent_gradient_component()`` and
``deliver_to_parent(receiver)``. The default callback passes the98-component
action-dual gradient on the72-dimensional fixed-birth-descriptor slice, plus
the actual operator jets and their action/raw coordinate maps. Full73 jets
and their fixed-birth72 contractions are both available. The covector is
owned by the first stored C2 frontier, not the incoming E1 formation state.
This is a partial frontier-action derivative; it does
not solve a nonlinear backreacted trajectory or select a future-child state.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Callable

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from scripts.run_n12_current_child_parent_backreaction import run as run_backreaction
from bhsm.interface.ae31_c2_lepton_composite_mixing_structure import shared_charged_lepton_vertex_jet
from bhsm.interface.n12_current_mixed_child_forms import normalized_source_mixed_form_jets

DEFAULT_CENTER = ROOT / "artifacts/flagship_integration/BHSM_N12_C2_STOP_HIGH_ORDER_QUARTER_STEP_RETAINED_RECONNAISSANCE.npz"
DEFAULT_MODES = ROOT / "artifacts/current_runtime/current_physical_mode_response"
DEFAULT_OUTPUT = ROOT / "artifacts/current_runtime/current_coupled_environment_children"


@dataclass
class CurrentCoupledChildEvaluation:
    """Numerical arrays and a callable partial C2-frontier gradient receiver."""

    report: dict[str, Any]
    parent_loads: dict[str, np.ndarray]
    operator_jets: dict[str, dict[str, np.ndarray]]

    def parent_gradient_component(
        self, *, representation: str = "action_dual", fixed_birth_slice: bool = True,
    ) -> np.ndarray:
        """Return the known -D Gamma_zeta component, without a heat sum.

        ``action_dual`` and ``raw_dual`` are98-component covectors.
        ``mode_covector`` is72-dimensional on the fixed birth slice and
        73-dimensional on the full tangent with its outgoing one-sided axis.
        No unknown component is supplied as a zero placeholder.
        """
        fields = {
            "action_dual": "known_replacement_minus_zeta_parent_action_dual",
            "raw_dual": "known_replacement_minus_zeta_parent_raw_dual",
            "mode_covector": "known_replacement_minus_zeta_parent_covector",
        }
        if representation not in fields:
            raise ValueError("representation must be action_dual, raw_dual or mode_covector")
        key = fields[representation] + ("_birth72" if fixed_birth_slice else "")
        if key not in self.parent_loads:
            raise ValueError(f"the supplied child calculation did not produce {key}")
        return self.parent_loads[key].copy()

    def deliver_to_parent(
        self, receiver: Callable[[np.ndarray, dict[str, dict[str, np.ndarray]]], Any],
        *, representation: str = "action_dual", fixed_birth_slice: bool = True,
    ) -> Any:
        """Pass the C2-frontier action derivative and mixed operator maps.

        ``parent_coordinates`` identifies every jet-column direction.
        ``*_first_jet*_birth72`` arrays use the fixed-birth slice; unsuffixed
        first jets retain all73 columns, including the outgoing one-sided
        descriptor direction. The maps apply also when a raw covector is
        requested, without equating raw and weighted action coordinates.
        Incoming E1 formation coordinates require their owned reset and
        seed-to-frontier pullbacks. Equal vector dimensions do not provide
        those maps; this suffix derivative is not a direct E1 Gamma_y term.
        """
        return receiver(self.parent_gradient_component(
            representation=representation, fixed_birth_slice=fixed_birth_slice,
        ), self.operator_jets)


def _current_mode_binding(center: Path, mode_dir: Path) -> tuple[str, dict[str, Any]]:
    mode_report = json.loads((mode_dir / "report.json").read_text(encoding="utf-8"))
    sha = hashlib.sha256(center.read_bytes()).hexdigest().upper()
    reported = mode_report.get("center_SHA256")
    if not isinstance(reported, str) or reported.upper() != sha:
        raise ValueError("current mode response center SHA256 does not match the requested N12 center")
    with np.load(mode_dir / "arrays.npz", allow_pickle=False) as source:
        if (source["initial_mode_action"].shape != (98, 73)
                or not np.array_equal(source["node_indices"], np.arange(48))):
            raise ValueError("actual current48-node/73-tangent mode arrays required")
    return sha, mode_report


def evaluate_current_coupled_environment_children(
    *, mode_dir: Path = DEFAULT_MODES, output: Path = DEFAULT_OUTPUT,
    center: Path = DEFAULT_CENTER,
) -> CurrentCoupledChildEvaluation:
    """Compute the connected current mode-to-child-to-parent derivative path."""
    sha, mode_report = _current_mode_binding(center, mode_dir)
    output = output.resolve()
    bridge_dir = output / "backreaction"
    bridge = run_backreaction(mode_dir, bridge_dir)
    if bridge["center_SHA256"].upper() != sha:
        raise ValueError("child coefficient bridge changed center binding")
    with np.load(bridge_dir / "arrays.npz", allow_pickle=False) as source:
        arrays = {key: np.array(source[key]) for key in source.files}
    x, h, dx, dh = (arrays[key] for key in (
        "log_radius", "proper_durations", "log_radius_first_jet", "proper_durations_first_jet",
    ))
    if (x.shape != (48,) or h.shape != (47,) or dx.shape != (48, 73) or dh.shape != (47, 73)):
        raise ValueError("one shared actual48/47 coefficient mesh with73 jets required")
    mixed_saved = {
        "action_lengths": arrays["action_lengths"], "log_radius": x,
        "proper_durations": h, "proper_times": arrays["proper_times"],
        "normalized_proper_times": arrays["normalized_proper_times"],
        "log_radius_first_jet": dx, "proper_durations_first_jet": dh,
        "proper_duration_first_jet": arrays["proper_duration_first_jet"],
        "birth_slice_Q72": arrays["birth_slice_Q72"], "center_SHA256": np.asarray(sha),
    }
    operator_jets: dict[str, dict[str, np.ndarray]] = {}
    Q72 = arrays["birth_slice_Q72"]
    U0 = arrays["initial_mode_action"]
    weights = arrays["state_weights"]
    coordinate_maps = {
        "full73_state_action_basis": U0,
        "fixed_birth72_state_action_basis": U0 @ Q72,
        "full73_state_raw_basis": U0 / weights[:, None],
        "fixed_birth72_state_raw_basis": (U0 @ Q72) / weights[:, None],
        "fixed_birth72_to_full73": Q72,
        "full73_covector_to_fixed_birth72": Q72.T,
        "outgoing_normal_full73": arrays["birth_outgoing_normal_mode"],
        "outgoing_normal_state_action": U0 @ arrays["birth_outgoing_normal_mode"],
        "birth_descriptor_full73_covector": arrays["birth_descriptor_mode_covector"],
        "state_weights": weights,
        "frontier_action_length": arrays["action_lengths"][0],
        "frontier_state_raw": arrays["states"][0],
    }
    operator_jets["parent_coordinates"] = coordinate_maps
    mixed_saved.update({f"parent_coordinates_{key}": value for key, value in coordinate_maps.items()})
    mixed_summaries = {}
    for chi, name in ((1, "plus"), (-1, "minus")):
        values = normalized_source_mixed_form_jets(
            log_radii=x, proper_durations=h, chirality=chi,
            log_radius_first_jet=dx, proper_durations_first_jet=dh,
        )
        form_arrays = values["arrays"]
        slice_jets = {
            f"{key}_birth72": value @ Q72
            for key, value in form_arrays.items()
            if "_first_jet" in key and value.shape[-1] == 73
        }
        form_arrays.update(slice_jets)
        operator_jets[name] = form_arrays
        mixed_summaries[name] = values["summary"]
        mixed_saved.update({f"{name}_{key}": value for key, value in values["arrays"].items()})
    lepton = shared_charged_lepton_vertex_jet()
    lepton_keys = ("intrinsic_vertex_matrix", "auxiliary_vertex_matrix", "squared_pencil_mixed_contact")
    operator_jets["lepton_vertices"] = {key: np.asarray(lepton[key], dtype=float) for key in lepton_keys}
    mixed_saved.update({f"lepton_{key}": value for key, value in operator_jets["lepton_vertices"].items()})
    np.savez_compressed(output / "mixed_operator_jets.npz", **mixed_saved)

    prefixes = ("known_replacement_minus_zeta_", "heat_scaled_parent_", "heat_cotangent_common_log_factors")
    parent_loads = {key: value for key, value in arrays.items() if key.startswith(prefixes)}
    for key in ("initial_mode_action", "state_weights", "birth_slice_Q72", "birth_slice_initial_action",
                "birth_descriptor_mode_covector", "birth_outgoing_normal_mode", "birth_signed_descriptor",
                "child_boundary_first_jet", "child_boundary_first_jet_birth72", "child_boundary_channel_names"):
        parent_loads[key] = arrays[key]
    parent_loads["center_SHA256"] = np.asarray(sha)
    required_loads = ("known_replacement_minus_zeta_parent_covector",
                      "known_replacement_minus_zeta_parent_action_dual",
                      "known_replacement_minus_zeta_parent_raw_dual",
                      "known_replacement_minus_zeta_parent_covector_birth72",
                      "known_replacement_minus_zeta_parent_action_dual_birth72",
                      "known_replacement_minus_zeta_parent_raw_dual_birth72")
    missing = [key for key in required_loads if key not in parent_loads]
    if missing:
        raise ValueError("computed bridge is missing actual parent load arrays: " + ", ".join(missing))
    np.savez_compressed(output / "parent_loads.npz", **parent_loads)

    boundary = []
    channel_names = arrays["child_boundary_channel_names"].tolist()
    responses = [bridge["boundary_responses"]["gauge"]["coexact"],
                 bridge["boundary_responses"]["gauge"]["BRST_scalar"],
                 bridge["boundary_responses"]["dirac_plus"], bridge["boundary_responses"]["dirac_minus"]]
    for index, name in enumerate(channel_names):
        boundary.append({"channel": name, "spectral_parameter": responses[index]["spectral_parameter"],
                         "Weyl_birth_value": responses[index]["Weyl_birth_value"],
                         "first_jet_full73_norm": float(np.linalg.norm(arrays["child_boundary_first_jet"][index])),
                         "first_jet_fixed_birth72_norm": float(np.linalg.norm(arrays["child_boundary_first_jet_birth72"][index])),
                         **bridge["boundary_responses"]["forward_reverse_duality"][index]})
    heat = []
    for row in bridge.get("individual_finite_core_heat_channels", []):
        coefficient = row["coefficient_cotangent"]
        heat.append({
            "channel": row["channel"], "heat_length": coefficient["heat_length"],
            "minimum_generalized_eigenvalue": coefficient["minimum_generalized_eigenvalue"],
            "Gamma_heat": coefficient["Gamma_heat"],
            "log_absolute_Gamma_heat": coefficient["log_absolute_Gamma_heat"],
            "cotangent_common_log_factor": coefficient["cotangent_common_log_factor"],
            "binary64_cotangent_underflow": coefficient["binary64_cotangent_underflow"],
            "scaled_parent_covector_norm": row["scaled_parent_covector_norm"],
            "parent_covector_log_norm": row["parent_covector_log_norm"],
            "scaled_parent_covector_birth72_norm": row["scaled_parent_covector_birth72_norm"],
            "forward_reverse_duality_relative_residual": row["scaled_forward_reverse_duality_relative_residual"],
            "graded_weight_or_sum_inserted": False,
        })
    report = {
        "status": "CURRENT_N12_COUPLED_CHILD_OPERATORS_AND_KNOWN_PARENT_ACTION_LOAD_EVALUATED",
        "center": str(center.resolve()), "center_SHA256": sha,
        "mode_response": str(mode_dir.resolve()),
        "physical_mode_scope": mode_report["scientific_scope"],
        "coefficient_mesh": {"node_count": 48, "element_count": 47,
                             "proper_duration": float(arrays["proper_duration"]),
                             "coefficient_jet_count": 73, "fixed_birth_slice_dimension": 72,
                             "mode_transport_substeps_per_macro_interval": 4,
                             "terminal_arc_motion_and_zero_hit_density_included": True},
        "admissible_birth_directions": bridge["birth_slice"],
        "child_boundary_responses": boundary,
        "mixed_geometry_source_forms": mixed_summaries,
        "lepton_vertices": {"dimensions": [6, 6], "cross_contact_residual": lepton["squared_pencil_cross_contact_residual"],
                            "inserted_into_current_carrier": False},
        "known_parent_action_component": {
            "component": "MINUS_D_GAMMA_SM_ZETA",
            "coordinate_owner": "FIRST_STORED_CURRENT_C2_FRONTIER_RAW98_AND_WEIGHTED_ACTION98",
            "incoming_E1_formation_Gamma_y_directly_available": False,
            "incoming_formation_role": "LAUNCH_COMPONENT_AFTER_OWNED_SEED_TO_FRONTIER_PULLBACK; NOT_DIRECT_E1_GRADIENT",
            "receiver_default": "98_COMPONENT_ACTION_DUAL_ON_CURRENT72_FIXED_BIRTH_DESCRIPTOR_SLICE",
            **bridge["known_zeta_component"],
            "full73_covector_norm": float(np.linalg.norm(parent_loads["known_replacement_minus_zeta_parent_covector"])),
            "fixed_birth72_covector_norm": float(np.linalg.norm(parent_loads["known_replacement_minus_zeta_parent_covector_birth72"])),
            "fixed_birth72_action_dual_norm": float(np.linalg.norm(parent_loads["known_replacement_minus_zeta_parent_action_dual_birth72"])),
        },
        "individual_finite_core_heat_channels": heat,
        "callable": {
            "function": "evaluate_current_coupled_environment_children",
            "gradient": "result.parent_gradient_component(representation='action_dual',fixed_birth_slice=True)",
            "receiver": "result.deliver_to_parent(receiver);receiver(known_partial_frontier_gradient,operator_jets)",
            "gradient_addition_to_parent_owned_by_caller": True,
            "heat_channels_kept_scaled_and_separate": True,
            "jet_coordinates": "operator_jets['parent_coordinates']; full73 and explicit fixed_birth72 jets",
        },
        "scope": "KNOWN_MINUS_ZETA_PARENT_ACTION_COMPONENT_AND_INDIVIDUAL_FINITE_CORE_HEAT_COTANGENTS;_NOT_FULL_GAMMA_OR_A_NONLINEAR_BACKREACTED_TRAJECTORY",
        "execution": {"new_exact_action_evaluations": 0, "trajectory_reintegrated": False,
                      "retarded_Hpc_packet_invented": False, "full73_two_sided_admissibility_assumed": False,
                      "mixed_forms_use_actual48_node_coefficient_jets": True},
        "outputs": {"backreaction_report": str(bridge_dir / "report.json"),
                    "mixed_operator_jets": str(output / "mixed_operator_jets.npz"),
                    "parent_loads": str(output / "parent_loads.npz")},
    }
    (output / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    return CurrentCoupledChildEvaluation(report=report, parent_loads=parent_loads, operator_jets=operator_jets)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode-response", type=Path, default=DEFAULT_MODES)
    parser.add_argument("--center", type=Path, default=DEFAULT_CENTER)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = evaluate_current_coupled_environment_children(mode_dir=args.mode_response, center=args.center, output=args.output)
    print(json.dumps({
        "status": result.report["status"], "report": str(args.output.resolve() / "report.json"),
        "coefficient_nodes": 48, "coefficient_jets": 73, "fixed_birth_slice": 72,
        "known_minus_zeta_parent_gradient_birth72_norm": float(np.linalg.norm(result.parent_gradient_component())),
        "individual_heat_channels": len(result.report["individual_finite_core_heat_channels"]),
        "new_exact_action_evaluations": 0,
    }, indent=2), flush=True)


if __name__ == "__main__":
    main()
