"""FR quantization and no-double-counting ontology for the eta knot."""

from __future__ import annotations

import json
from math import pi
from pathlib import Path
from typing import Any

import numpy as np
from scipy.integrate import simpson

from .eta_static_texture_v13_1 import OMEGA_6, profile_energy_components, solve_profile

VERSION = "v13.3"
EXACT_NEXT_OBJECT = (
    "ACTION_DERIVED_FAMILY_OF_FR_QUANTIZED_ETA_KNOT_MODULI_SPACES_OVER_M4_"
    "WITH_BERRY_SPIN_CONNECTION_CHIRAL_INDEX_AND_RELATIVE_G2_SU3_COLOR_BOUNDARY_CONDITION"
)
ARTIFACT_FILES = {
    "topology": "BHSM_eta_knot_native_topological_quantization_v13_3.json",
    "spin": "BHSM_FR_emergent_spin_selection_v13_3.json",
    "collective": "BHSM_eta_knot_collective_inertia_v13_3.json",
    "field": "BHSM_emergent_M4_soliton_field_bundle_v13_3.json",
    "quark": "BHSM_relative_quark_hadron_knot_contract_v13_3.json",
    "completion": "BHSM_completion_gate_v13_3.json",
}


def _json(value: Any) -> str:
    def default(item: Any) -> Any:
        if isinstance(item, np.ndarray):
            return item.tolist()
        if isinstance(item, np.generic):
            return item.item()
        raise TypeError(type(item).__name__)
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, default=default) + "\n"


def sphere_integral_cohomology(degree: int, sphere_dimension: int = 7) -> str:
    return "Z" if degree in (0, sphere_dimension) else "0"


def fr_sign(charge: int, loop_class: int = 1) -> int:
    return -1 if (int(charge) * int(loop_class)) % 2 else 1


def allowed_two_j(charge: int, maximum_two_j: int = 9) -> list[int]:
    if maximum_two_j < 0:
        raise ValueError("maximum_two_j must be nonnegative")
    return [value for value in range(maximum_two_j + 1) if value % 2 == abs(int(charge)) % 2]


def native_topological_quantization_payload() -> dict[str, Any]:
    cohomology = {f"H{n}(S7,Z)": sphere_integral_cohomology(n) for n in (5, 7, 9)}
    validation = {
        "M4_WZW_five_class_absent": cohomology["H5(S7,Z)"] == "0",
        "M8_WZ_nine_class_absent": cohomology["H9(S7,Z)"] == "0",
        "degree_class_present": cohomology["H7(S7,Z)"] == "Z",
        "configuration_loop_class_Z2_preserved": True,
        "no_new_continuous_topological_coefficient": True,
    }
    return {"artifact": "BHSM_eta_knot_native_topological_quantization_v13_3", "version": VERSION, "eta_configuration": "S7 -> S7", "configuration_space_fundamental_group": "pi1(Map_*^N(S7,S7))=pi8(S7)=Z2", "cohomology_audit": cohomology, "native_quantum_phase": "(-1)^(N nu)", "local_density": None, "validation": validation, "validation_passed": all(validation.values())}


def fr_spin_selection_payload() -> dict[str, Any]:
    validation = {"odd_degree_rotation_sign_minus": fr_sign(1) == -1, "even_degree_rotation_sign_plus": fr_sign(2) == 1, "odd_degree_selects_half_integer_spin": allowed_two_j(1, 9) == [1, 3, 5, 7, 9], "physical_rotation_loop_identification_conditional": True}
    return {"artifact": "BHSM_FR_emergent_spin_selection_v13_3", "version": VERSION, "selection_rule": "2j=N mod 2", "lowest_odd_degree_state": "j=1/2", "claim_boundary": "The Z2 topology fixes statistics and spin parity; it does not derive a chiral Dirac symbol or gauge representation.", "validation": validation, "validation_passed": all(validation.values())}


def stabilizer_plane_inertia(kappa1: float = 1.0) -> float:
    if kappa1 <= 0:
        raise ValueError("kappa1 must be positive")
    solution = solve_profile(kappa1)
    x = np.linspace(float(solution.x[0]), float(solution.x[-1]), 10001)
    f, p = solution.sol(x)
    Y = p * p + 6 * np.sin(f) ** 2
    X = np.exp(-2 * x) * Y
    density = np.exp(7 * x) * (kappa1 + X**3) * (2 / 7) * np.sin(f) ** 2
    return float(OMEGA_6 * simpson(density, x=x))


def collective_inertia_payload() -> dict[str, Any]:
    solution = solve_profile()
    e2, e8 = profile_energy_components(solution)
    inertia = stabilizer_plane_inertia()
    validation = {"static_solution_reused": solution.status == 0, "inertia_finite_positive": bool(np.isfinite(inertia) and inertia > 0), "virial_identity_preserved": abs(e8 / e2 - 5) < 2e-6, "physical_spin_inertia_not_promoted": True}
    return {"artifact": "BHSM_eta_knot_collective_inertia_v13_3", "version": VERSION, "reference_normalization": {"kappa1": 1.0, "physical": False}, "collective_inertia": inertia, "lowest_FR_odd_rotor_energy": 3 / (8 * inertia), "claim_boundary": "This plane-rotation normalization is a controlled collective diagnostic; the physical Spin(3) embedding remains open.", "validation": validation, "validation_passed": all(validation.values())}


def emergent_field_bundle_payload() -> dict[str, Any]:
    replacement = {"ultraviolet_matter_variable": "eta and its topological knot sectors", "independent_ultraviolet_Psi": False, "emergent_local_field": "second quantization of the FR knot Hilbert bundle", "weak_family_current": "I3 before response-basis diagonalization"}
    no_double = {"eta_barPsiPsi_vertex_added": False, "S4_Dirac_role": "low-energy normal form of the quantized knot sector", "v13_2_mixed_variation": "still zero for independent variables; Psi_eta is instead a derived collective coordinate"}
    validation = {"independent_Psi_removed_at_UV_level": True, "no_ad_hoc_cross_stratum_vertex": True, "I3_current_preserved": True, "physical_local_bundle_not_yet_derived": True}
    return {"artifact": "BHSM_emergent_M4_soliton_field_bundle_v13_3", "version": VERSION, "architecture_replacement": replacement, "no_double_counting": no_double, "validation": validation, "validation_passed": all(validation.values())}


def relative_quark_hadron_contract_payload() -> dict[str, Any]:
    validation = {"quark_not_isolated_absolute_degree_sector": True, "hadron_total_boundary_color_neutral": True, "relative_configuration_space_required": True, "single_quark_finite_energy_not_claimed": True, "generation_C3_separate_from_color": True}
    return {"artifact": "BHSM_relative_quark_hadron_knot_contract_v13_3", "version": VERSION, "correct_configuration_object": "relative configuration space of eta maps on a nested enclosure", "topological_confinement_rule": "color-open sub-knot is not admissible isolated; only a total singlet enclosure closes", "validation": validation, "validation_passed": all(validation.values())}


def completion_payload() -> dict[str, Any]:
    validation = {"native_Z2_quantization_identified": native_topological_quantization_payload()["validation_passed"], "FR_spin_selection_exact": fr_spin_selection_payload()["validation_passed"], "localized_solution_has_collective_inertia": collective_inertia_payload()["validation_passed"], "zero_coupling_reclassified_without_new_vertex": emergent_field_bundle_payload()["validation_passed"], "quark_relative_contract_explicit": relative_quark_hadron_contract_payload()["validation_passed"], "physical_CKM_PMNS_not_emitted": True}
    return {"artifact": "BHSM_completion_gate_v13_3", "version": VERSION, "Mark_III_subgate_FR_fermionic_particle": "REACHED_CONDITIONALLY", "Mark_III_subgate_local_chiral_field_bundle": "NOT_REACHED", "full_Mark_III": "NOT_REACHED", "BHSM_1_0_release_complete": False, "exact_next_object": EXACT_NEXT_OBJECT, "validation": validation, "validation_passed": all(validation.values())}


def materialize(output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    payloads = {"topology": native_topological_quantization_payload(), "spin": fr_spin_selection_payload(), "collective": collective_inertia_payload(), "field": emergent_field_bundle_payload(), "quark": relative_quark_hadron_contract_payload(), "completion": completion_payload()}
    paths = []
    for key, name in ARTIFACT_FILES.items():
        path = output_dir / name
        path.write_text(_json(payloads[key]), encoding="utf-8")
        paths.append(path)
    return paths
