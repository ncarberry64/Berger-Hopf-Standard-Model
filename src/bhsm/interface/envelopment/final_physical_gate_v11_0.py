"""Deterministic BHSM v11.0 physical-completion and obstruction gate."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .canonical_crystallization_v11_0 import (
    CANONICAL_DOCTRINE_VERDICT,
    buoyancy_payload,
    charge_payload,
    core_transfer_payload,
    dependency_payload,
    falsification_payload,
    higgs_payload,
    ontology_payload,
    quantum_measurement_payload,
)
from .core_stratum_action_v11_0 import CORE_VERDICT, core_action_payload
from .generation_monodromy_v10_4 import FROZEN_LEDGERS
from .relational_axioms import deterministic_json
from .support_composition_v11_0 import composition_payload
from .support_weight_derivation_v11_0 import (
    NEXT_EXACT_OBJECT,
    PRIMARY_VERDICT,
    supported_action_payload,
)


VERSION = "v11.0"
SPRINT = "bhsm-canonical-unification-completion-v11-0"
SOURCE_V10_4_SHA = "04a38d962e32613ff4486f6ef068a01d24a9e4ac"

ARTIFACT_FILES = {
    "canonical_ontology": "BHSM_canonical_ontology_v11_0.json",
    "canonical_dependency_graph": "BHSM_canonical_dependency_graph_v11_0.json",
    "canonical_falsification": "BHSM_canonical_falsification_v11_0.json",
    "support_composition": "BHSM_support_composition_v11_0.json",
    "supported_parent_action": "BHSM_supported_parent_action_v11_0.json",
    "support_action": "BHSM_support_action_v11_0.json",
    "core_stratum_action": "BHSM_core_stratum_action_v11_0.json",
    "core_transfer": "BHSM_core_transfer_v11_0.json",
    "three_mode_hessian": "BHSM_three_mode_hessian_v11_0.json",
    "topological_buoyancy": "BHSM_topological_buoyancy_v11_0.json",
    "higgs_buoyancy_mode": "BHSM_higgs_buoyancy_mode_v11_0.json",
    "nonlinear_orbits": "BHSM_nonlinear_orbits_v11_0.json",
    "global_equilibrium": "BHSM_global_equilibrium_v11_0.json",
    "global_scale": "BHSM_global_scale_v11_0.json",
    "sector_cycles": "BHSM_sector_cycles_v11_0.json",
    "particle_cycles": "BHSM_particle_cycles_v11_0.json",
    "generation_monodromy": "BHSM_generation_monodromy_v11_0.json",
    "mass_spectrum": "BHSM_mass_spectrum_v11_0.json",
    "ckm_pmns": "BHSM_ckm_pmns_v11_0.json",
    "m4_reduction": "BHSM_m4_reduction_v11_0.json",
    "geometric_charges": "BHSM_geometric_charges_v11_0.json",
    "core_transition": "BHSM_core_transition_v11_0.json",
    "quantum_measurement": "BHSM_quantum_measurement_v11_0.json",
    "completion": "BHSM_final_physical_gate_v11_0.json",
}


def support_constraint_payload() -> dict[str, Any]:
    return {
        "regular_canonical_pair": ["q_D", "pi_D"],
        "pi_D": "sqrt(h)/N (dot(q_D)-N^i partial_i q_D)",
        "primary_first_class": ["p_N=0", "p_Ni=0"],
        "secondary_first_class": ["C_H,total=0", "C_i,total=0"],
        "support_second_class_constraints": [],
        "support_internal_gauge_orbit": None,
        "physical_support_pairs": 1,
        "kinetic_norm": "integral sqrt(h) (delta q_D)^2>0",
        "gradient_speed_squared": 1.0,
        "no_duplicate_common_volume_pair": True,
        "no_duplicate_q_C_or_q_W": True,
        "long_range_scalar_control": "interaction/restoring Hessian open until support characters and equilibrium are action fixed",
        "status": "BHSM_HAAR_DEPTH_HAS_ONE_HEALTHY_REGULAR_CANONICAL_PAIR",
    }


def three_mode_payload() -> dict[str, Any]:
    open_weight = "support characters and lambda_D are not action fixed"
    cross_domain = "q_C and q_W remain owned on distinct S8/S5 strata without a derived common reduction functor"
    def block(status: str, value: Any, reason: str) -> dict[str, Any]:
        return {"status": status, "value": value, "reason": reason}
    k = [
        [block("DERIVED_CONDITIONAL", "6*kappa5", "historical M8 Einstein-frame block"), block("UNDEFINED_CROSS_DOMAIN", None, cross_domain), block("OPEN", None, open_weight)],
        [block("UNDEFINED_CROSS_DOMAIN", None, cross_domain), block("DERIVED_CONDITIONAL", 6.935084858283065, "historical M5 fold block"), block("OPEN", None, open_weight)],
        [block("OPEN", None, open_weight), block("OPEN", None, open_weight), block("DERIVED", 1.0, "canonical Haar depth")],
    ]
    h = [
        [block("OPEN_BACKGROUND", None, "no localized stationary q_C background"), block("UNDEFINED_CROSS_DOMAIN", None, cross_domain), block("OPEN", None, open_weight)],
        [block("UNDEFINED_CROSS_DOMAIN", None, cross_domain), block("OPEN_BACKGROUND", None, "fold Hessian lacks common stationary background"), block("OPEN", None, open_weight)],
        [block("OPEN", None, open_weight), block("OPEN", None, open_weight), block("OPEN", None, "emergent effective potential cannot be reduced before couplings")],
    ]
    return {
        "artifact": "BHSM_three_mode_hessian_v11_0",
        "state": ["q_C", "q_W", "q_D"],
        "K_0": k,
        "H_0": h,
        "J_D_requirement": "nonzero q_C and q_W contributions retained as a gate",
        "common_domain": None,
        "complete_source": None,
        "kinetic_matrix_complete": False,
        "hessian_complete": False,
        "mixed_blocks_complete": False,
        "stable_coupled_eigenmode": None,
        "seam_projection": "psi_seam=Pi_seam(q_C,q_W,q_D); no fourth mode",
        "status": "BHSM_THREE_MODE_ACTION_BLOCKED_BY_UNFIXED_SUPPORT_REPRESENTATION_AND_COMMON_DOMAIN",
        "validation_passed": True,
    }


def nonlinear_orbit_payload() -> dict[str, Any]:
    return {
        "artifact": "BHSM_nonlinear_orbits_v11_0",
        "relative_periodic_equation": "Phi(tau+T)=h.Phi(tau)",
        "equations_available": False,
        "reason": "the common three-mode action, core response, boundary data, and stationary background are incomplete",
        "solver_run": False,
        "orbit": None,
        "residual_norm": None,
        "constraint_residual": None,
        "monodromy": None,
        "physical_floquet_multipliers": None,
        "status": "BHSM_RELATIVE_PERIODIC_ORBIT_NOT_EVALUABLE_FROM_INCOMPLETE_ACTION",
        "validation_passed": True,
    }


def global_equilibrium_payload() -> dict[str, Any]:
    return {
        "artifact": "BHSM_global_equilibrium_v11_0",
        "closed_topology_postulate": "author binding structural postulate",
        "stationary_equations_complete": False,
        "unique_dimensionless_shape": False,
        "residual_moduli": ["lambda_D", "support weights", "existing parent theory inputs", "cross-stratum reduction data", "core response data"],
        "cosmic_anchor_used": False,
        "cosmic_anchor": None,
        "particle_inputs_used": [],
        "status": "BHSM_UNIQUE_CLOSED_GLOBAL_EQUILIBRIUM_NOT_TESTABLE_BEFORE_COMPLETE_ACTION",
        "validation_passed": True,
    }


def sector_cycles_payload() -> dict[str, Any]:
    sectors = {
        "charged_leptons": {"interpretation": "timelike self-envelopment", "cycle": None},
        "quarks_hadrons": {"interpretation": "color-open sub-envelope in color-neutral parent", "cycle": None},
        "neutrinos": {"interpretation": "near-null propagation-supported envelopment", "cycle": None},
        "antimatter": {"interpretation": "complementary orientation of same envelopment class", "involution": None},
    }
    return {
        "artifact": "BHSM_sector_cycles_v11_0",
        "sectors": sectors,
        "physical_cycle_count": 0,
        "reason": "no complete three-mode equations, global equilibrium, core transfer law, or normalized asymptotic state",
        "status": "BHSM_PHYSICAL_SECTOR_CYCLES_REMAIN_FAIL_CLOSED",
        "validation_passed": True,
    }


def generation_payload() -> dict[str, Any]:
    sectors = {
        key: {
            "frozen_slots": value,
            "cycle": None,
            "monodromy": None,
            "stable_eigenphases": [None, None, None],
            "slot_to_phase_intertwiner": None,
        }
        for key, value in FROZEN_LEDGERS.items()
    }
    sectors["neutrinos"] = {
        "frozen_slots": None,
        "cycle": None,
        "monodromy": None,
        "stable_eigenphases": [None, None, None],
        "slot_to_phase_intertwiner": None,
    }
    return {
        "artifact": "BHSM_generation_monodromy_v11_0",
        "sectors": sectors,
        "three_modes_are_generations": False,
        "derived_stable_phase_count": 0,
        "frozen_ledgers_changed": False,
        "status": "BHSM_GENERATION_PHASE_MONODROMY_BLOCKED_BY_ABSENT_SECTOR_CYCLES",
        "validation_passed": True,
    }


def mass_payload() -> dict[str, Any]:
    return {
        "artifact": "BHSM_mass_spectrum_v11_0",
        "functional": "m_fi=mu_global epsilon_f(q_f,theta_fi)",
        "global_scale": None,
        "dimensionless_outputs": None,
        "physical_masses": None,
        "hierarchy_operator": "Theta_f=exp[-Lambda_f/(4pi)] retained as frozen candidate",
        "hierarchy_operator_action_origin": None,
        "particle_calibration_used": False,
        "status": "BHSM_PHYSICAL_MASS_SPECTRUM_WITHHELD_BY_ACTION_AND_SCALE_GATES",
        "validation_passed": True,
    }


def mixing_payload() -> dict[str, Any]:
    return {
        "artifact": "BHSM_ckm_pmns_v11_0",
        "G_f": None,
        "Q_f": None,
        "K_ud": None,
        "Gram_positive": None,
        "current_pullback_rank": None,
        "CKM": None,
        "PMNS": None,
        "unitarity": None,
        "measured_mixing_inputs": [],
        "status": "BHSM_CKM_PMNS_WITHHELD_BECAUSE_CYCLE_FORMS_AND_CURRENTS_ARE_UNEVALUABLE",
        "validation_passed": True,
    }


def m4_payload() -> dict[str, Any]:
    fields = ["g_mu_nu", "A_mu", "W_mu", "B_mu", "G_mu", "psi_f", "H", "J_mu"]
    return {
        "artifact": "BHSM_m4_reduction_v11_0",
        "map": "R_M4:Phi_complete -> (g,A,W,B,G,psi,H,J)_effective",
        "effective_fields": fields,
        "intrinsic_fields_retained": True,
        "field_source_dictionary_complete": False,
        "normalized_action_complete": False,
        "gauge_couplings_action_derived": False,
        "scalar_sector_action_derived": False,
        "currents_complete": False,
        "anomaly_ledger_retained": True,
        "vertices": None,
        "collider_runtime": None,
        "established_physics_reproduction_complete": False,
        "status": "BHSM_EFFECTIVE_M4_REDUCTION_REMAINS_CONDITIONAL",
        "validation_passed": True,
    }


def core_transition_payload() -> dict[str, Any]:
    return {
        "artifact": "BHSM_core_transition_v11_0",
        "absorption_map": None,
        "core_evolution": None,
        "emission_map": None,
        "transition_operator": None,
        "norm_preservation": None,
        "probability_law": None,
        "CPTP_reduction": None,
        "no_signalling": None,
        "measurement_interpretation": "author doctrine only; not action-derived",
        "fundamental_dissipation": False,
        "status": "BHSM_QUANTUM_CORE_TRANSITION_NOT_DERIVED_WITHOUT_CORE_PHASE_SPACE",
        "validation_passed": True,
    }


def completion_marks() -> dict[str, str]:
    return {
        "Mark_I_Canonical_ontology": "REACHED",
        "Mark_II_Complete_conditional_architecture": "NOT_REACHED",
        "Mark_III_Physical_derivation": "NOT_REACHED",
        "Mark_IV_Empirical_replacement": "NOT_REACHED",
    }


def hindsight_payload() -> dict[str, list[str]]:
    return {
        "VALIDATED": [
            "multiplicative support and continuous additive depth uniquely give q_D=-lambda_D log(upsilon)",
            "the invariant support metric is lambda_D^2 dupsilon^2/upsilon^2",
            "canonical q_D contributes one healthy regular scalar pair",
            "the core endpoint upsilon=0 is at infinite Haar field distance",
            "continuous support characters have the form upsilon^w",
            "the frozen parent action is recovered at upsilon=1 for every normalized character",
        ],
        "INVALIDATED": [
            "constant support kinetic function as a physical realization of the multiplicative composition axiom",
            "lambda_D treated as a pure unit convention after nonzero support couplings are present",
            "tensor rank or density weight alone treated as a derivation of support character exponents",
            "minimal positive integer weights treated as action-derived merely because they are simple",
            "finite regular-domain core transfer inferred at an infinite field-space endpoint without core data",
            "downstream orbit, mass, mixing, M4, or quantum outputs inferred from unevaluable equations",
        ],
        "OPEN": [
            NEXT_EXACT_OBJECT,
            "CORE_BOUNDARY_PHASE_SPACE_AND_SELF_ADJOINT_TRANSFER_OPERATOR_AT_QD_INFINITY",
            "COMMON_S8_S5_S4_REDUCTION_FUNCTOR_AND_COMPLETE_THREE_MODE_HESSIAN",
            "STABLE_RELATIVE_PERIODIC_SECTOR_CYCLES_AND_PHYSICAL_MONODROMIES",
            "ACTION_SELECTED_GLOBAL_EQUILIBRIUM_AND_ELIGIBLE_COSMIC_ANCHOR",
            "FROZEN_SLOT_TO_CYCLE_PHASE_INTERTWINERS",
            "NORMALIZED_M4_REDUCTION_AND_COMPLETE_CURRENT_PULLBACKS",
        ],
    }


def completion_payload() -> dict[str, Any]:
    ontology = ontology_payload()
    dependencies = dependency_payload()
    falsification = falsification_payload()
    support = composition_payload()
    action = supported_action_payload()
    core = core_action_payload()
    transfer = core_transfer_payload()
    three_mode = three_mode_payload()
    buoyancy = buoyancy_payload()
    higgs = higgs_payload()
    orbit = nonlinear_orbit_payload()
    global_result = global_equilibrium_payload()
    cycles = sector_cycles_payload()
    generations = generation_payload()
    masses = mass_payload()
    mixing = mixing_payload()
    m4 = m4_payload()
    charges = charge_payload()
    transition = core_transition_payload()
    measurement = quantum_measurement_payload()
    validation = {
        "canonical_ontology_crystallized": ontology["validation_passed"],
        "dependency_graph_valid": dependencies["validation_passed"],
        "falsification_registry_valid": falsification["validation_passed"],
        "support_composition_exact": support["validation_passed"],
        "support_nonuniqueness_proved": action["validation_passed"] and not action["support_weights_fixed"],
        "one_healthy_support_pair": support_constraint_payload()["physical_support_pairs"] == 1,
        "core_fail_closed": core["validation_passed"] and not core["complete_flux_relation"],
        "core_transfer_fail_closed": transfer["transfer_operator"] is None,
        "three_mode_fail_closed": three_mode["stable_coupled_eigenmode"] is None,
        "orbit_not_fabricated": orbit["solver_run"] is False,
        "global_anchor_unused": global_result["cosmic_anchor_used"] is False,
        "cycles_not_fabricated": cycles["physical_cycle_count"] == 0,
        "frozen_ledgers_unchanged": generations["frozen_ledgers_changed"] is False,
        "masses_withheld": masses["physical_masses"] is None,
        "mixing_withheld": mixing["CKM"] is None and mixing["PMNS"] is None,
        "m4_fail_closed": m4["collider_runtime"] is None,
        "buoyancy_not_promoted": buoyancy["displaced_energy_functional"] is None,
        "higgs_not_promoted": higgs["normalized_scalar_mode"] is None,
        "charges_not_promoted": charges["geometric_assignments"] is None,
        "quantum_not_fabricated": transition["transition_operator"] is None,
        "measurement_not_fabricated": measurement["measurement_channel"] is None,
        "no_particle_inputs": True,
    }
    return {
        "artifact": "BHSM_final_physical_gate_v11_0",
        "version": VERSION,
        "sprint": SPRINT,
        "source_v10_4_sha": SOURCE_V10_4_SHA,
        "primary_verdict": PRIMARY_VERDICT,
        "canonical_doctrine_verdict": CANONICAL_DOCTRINE_VERDICT,
        "next_exact_object": NEXT_EXACT_OBJECT,
        "canonical_ontology": ontology,
        "canonical_dependency_graph": dependencies,
        "canonical_falsification": falsification,
        "support_composition": support,
        "supported_parent_action": action,
        "support_action": action,
        "support_constraint_analysis": support_constraint_payload(),
        "core_stratum_action": core,
        "core_transfer": transfer,
        "three_mode_hessian": three_mode,
        "topological_buoyancy": buoyancy,
        "higgs_buoyancy_mode": higgs,
        "nonlinear_orbits": orbit,
        "global_equilibrium": global_result,
        "global_scale": global_result,
        "sector_cycles": cycles,
        "particle_cycles": cycles,
        "generation_monodromy": generations,
        "mass_spectrum": masses,
        "ckm_pmns": mixing,
        "m4_reduction": m4,
        "geometric_charges": charges,
        "core_transition": transition,
        "quantum_measurement": measurement,
        "completion_marks": completion_marks(),
        "hindsight_20_20": hindsight_payload(),
        "physical_BHSM_complete": False,
        "empirical_replacement_complete": False,
        "frozen_predictions_changed": False,
        "official_prediction_logic_changed": False,
        "new_geometric_fields": [],
        "new_continuous_physical_parameters_adopted": [],
        "unfixed_continuous_action_data": ["lambda_D"],
        "measured_particle_inputs": [],
        "fundamental_dissipation": False,
        "new_gravity_mediator": False,
        "physical_outputs": {"masses": None, "CKM": None, "PMNS": None, "transition_amplitudes": None},
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def artifact_payloads() -> dict[str, dict[str, Any]]:
    data = completion_payload()
    return {key: data[key] for key in ARTIFACT_FILES if key != "completion"} | {"completion": data}


COMMAND_SECTIONS = {
    "canonical-ontology-status-v11": "canonical_ontology",
    "support-action-status-v11": "support_action",
    "core-transfer-status-v11": "core_transfer",
    "three-mode-status-v11": "three_mode_hessian",
    "topological-buoyancy-status-v11": "topological_buoyancy",
    "higgs-buoyancy-status-v11": "higgs_buoyancy_mode",
    "particle-cycle-status-v11": "particle_cycles",
    "generation-status-v11": "generation_monodromy",
    "global-scale-status-v11": "global_scale",
    "mass-spectrum-status-v11": "mass_spectrum",
    "mixing-status-v11": "ckm_pmns",
    "geometric-charge-status-v11": "geometric_charges",
    "quantum-measurement-status-v11": "quantum_measurement",
    "support-composition-status": "support_composition",
    "supported-action-status": "supported_parent_action",
    "core-stratum-action-status": "core_stratum_action",
    "three-mode-hessian-status": "three_mode_hessian",
    "nonlinear-orbit-status": "nonlinear_orbits",
    "global-equilibrium-status-v11": "global_equilibrium",
    "sector-cycle-status": "sector_cycles",
    "generation-monodromy-status-v11": "generation_monodromy",
    "mass-spectrum-status": "mass_spectrum",
    "ckm-pmns-status": "ckm_pmns",
    "m4-reduction-status": "m4_reduction",
    "core-transition-status": "core_transition",
    "physical-completion-status-v11": None,
}


def command_payload(command: str) -> dict[str, Any]:
    if command not in COMMAND_SECTIONS:
        raise ValueError(f"unknown v11.0 status command: {command}")
    completion = completion_payload()
    key = COMMAND_SECTIONS[command]
    return {
        "version": VERSION,
        "command": command,
        "primary_verdict": PRIMARY_VERDICT,
        "section": completion if key is None else completion[key],
        "physical_BHSM_complete": False,
        "frozen_predictions_changed": False,
        "next_exact_object": NEXT_EXACT_OBJECT,
    }


def command_to_markdown(command: str, payload: dict[str, Any] | None = None) -> str:
    data = command_payload(command) if payload is None else payload
    return "\n".join(
        [
            f"# BHSM v11.0 {command}",
            "",
            f"Primary verdict: `{data['primary_verdict']}`",
            "",
            "- Haar support kinematics derived: `true`",
            "- Complete supported parent action: `false`",
            "- Physical derivation complete: `false`",
            "- Frozen predictions changed: `false`",
            "- Particle calibration used: `false`",
            "",
            "## Exact next object",
            "",
            f"`{data['next_exact_object']}`",
        ]
    ) + "\n"


def canonical_completion_gate_payload() -> dict[str, Any]:
    from .final_completion_gate_v10_4 import canonical_completion_gate_payload as v10_4_gate

    data = completion_payload()
    gate = v10_4_gate()
    gate.update(
        {
            "version": VERSION,
            "sprint": SPRINT,
            "source_v10_4_sha": SOURCE_V10_4_SHA,
            "current_verdict": PRIMARY_VERDICT,
            "next_highest_upstream_blocker": NEXT_EXACT_OBJECT,
            "support_composition_derived": True,
            "support_weights_action_owned": False,
            "third_spacetime_removal_mode_action_owned": True,
            "three_mode_action_complete": False,
            "physical_particle_cycles_complete": False,
            "physical_mass_mixing_complete": False,
            "BHSM_1_0_release_complete": False,
            "completion_marks": data["completion_marks"],
            "new_fields_in_v11_0": [],
            "new_continuous_parameters_in_v11_0": [],
            "frozen_predictions_changed": False,
            "validation_passed": data["validation_passed"],
        }
    )
    gate["RB15"] = {
        "status": "BLOCKED_BY_UNFIXED_SUPPORT_REPRESENTATION_AND_HAAR_SCALE",
        "resolution": NEXT_EXACT_OBJECT,
    }
    gate["RB16"] = {
        "status": "DOWNSTREAM_BLOCKED",
        "resolution": "no physical mass, mixing, M4, or quantum artifact is licensed",
    }
    return gate


def materialize(root: Path | None = None) -> list[Path]:
    repository = Path(__file__).resolve().parents[4] if root is None else Path(root)
    target = repository / "artifacts"
    target.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for key, payload in artifact_payloads().items():
        path = target / ARTIFACT_FILES[key]
        path.write_text(deterministic_json(payload), encoding="utf-8", newline="\n")
        paths.append(path)
    canonical = target / "BHSM_1_0_completion_gate.json"
    canonical.write_text(deterministic_json(canonical_completion_gate_payload()), encoding="utf-8", newline="\n")
    paths.append(canonical)
    return paths
