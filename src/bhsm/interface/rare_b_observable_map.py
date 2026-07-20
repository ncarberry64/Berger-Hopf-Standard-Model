"""Claim-safe rare-B observable-map scaffold for BHSM v5.1."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Iterable


VERSION = "v5.1"
PRIMARY_VERDICT = "RARE_B_OBSERVABLE_MAP_INTERFACE_COMPLETE"
Q0_VERDICT = "RARE_B_AFB_ZERO_PREDICTION_BLOCKED"
MICROPLATEAU_VERDICT = "RARE_B_MICROPLATEAU_NODE_PREDICTION_BLOCKED"

ARTIFACT_FILES = {
    "observable_convention": "BHSM_rare_b_observable_convention_v5_1.json",
    "transition_operator_interface": "BHSM_rare_b_transition_operator_interface_v5_1.json",
    "hadronic_interface": "BHSM_rare_b_hadronic_interface_v5_1.json",
    "afb_null_balance": "BHSM_rare_b_afb_null_balance_v5_1.json",
    "bhsm_matching_map": "BHSM_rare_b_bhsm_matching_map_v5_1.json",
    "observable_map_audit": "BHSM_rare_b_observable_map_audit_v5_1.json",
    "scaffold_verdict": "BHSM_rare_b_observable_map_scaffold_verdict_v5_1.json",
}

PRESERVED_BLOCKERS = (
    "ACTION_ATTACHMENT_BLOCKED",
    "CKM_RELATIVE_CURRENT_NORMALIZATION_BLOCKED",
    "COUPLING_BRIDGE_BLOCKED_PENDING_ACTION_PRINCIPLE",
    "RARE_B_AFB_ZERO_PREDICTION_BLOCKED",
    "RARE_B_MICROPLATEAU_NODE_PREDICTION_BLOCKED",
    "OPEN_MISSING_BHSM_TO_RARE_B_OPERATOR_MATCHING",
    "OPEN_MISSING_BHSM_WILSON_COEFFICIENT_DERIVATION",
    "OPEN_MISSING_BHSM_HADRONIC_MATRIX_ELEMENTS",
    "OPEN_MISSING_RARE_B_Q2_PHYSICAL_BRIDGE",
    "OPEN_MISSING_GAUGE_COUPLING_ACTION_ATTACHMENT",
    "OPEN_MISSING_ALPHA_I_ACTION_DERIVATION",
    "OPEN_MISSING_ALPHA2_ACTION_DERIVATION",
    "OPEN_MISSING_G2_BH_ACTION_SOURCE",
    "OPEN_MISSING_CKM_COEFFICIENT_VALUE_SOURCE",
    "CKM_EXPONENT_NOT_DERIVED",
    "FULL_BHSM_NOT_COMPLETE",
)

NO_FIT_PROHIBITIONS = (
    "fitting q0^2 to experimental data",
    "choosing node positions after viewing residuals",
    "selecting a Wilson shift to match an anomaly",
    "tuning form-factor inputs to force a zero",
    "choosing conventions based on desired numerical output",
    "using experimental central values as hidden BHSM constants",
)

PREDICTION_GATE_ORDER = (
    "transition_operator_map_closed",
    "wilson_matching_closed",
    "hadronic_interface_supplied",
    "afb_null_balance_closed",
    "q2_physical_bridge_closed",
    "normalization_closed",
    "scale_dependence_closed",
    "no_fit_discipline_satisfied",
)


class InterfaceStatus(str, Enum):
    ARTIFACTED = "ARTIFACTED_INTERFACE"
    EXTERNAL_INPUT = "EXTERNAL_OBSERVABLE_COORDINATE_INTERFACE"
    OPEN = "OPEN_MISSING_DERIVATION"
    BLOCKED = "BLOCKED"


class NullEquationAudit(str, Enum):
    EXPLICIT_AND_ACTION_CONNECTED = "EXPLICIT_AND_ACTION_CONNECTED"
    EXPLICIT_BUT_EXTERNAL_CONVENTION_ONLY = "EXPLICIT_BUT_EXTERNAL_CONVENTION_ONLY"
    SYMBOLIC_PLACEHOLDER_ONLY = "SYMBOLIC_PLACEHOLDER_ONLY"
    ABSENT = "ABSENT"


@dataclass(frozen=True)
class MatchingDependency:
    name: str
    input: str
    output: str
    units: str
    normalization: str
    provenance: str
    implementation_location: str | None
    status: str
    blocking_dependency: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PredictionGateState:
    transition_operator_map_closed: bool = False
    wilson_matching_closed: bool = False
    hadronic_interface_supplied: bool = True
    afb_null_balance_closed: bool = True
    q2_physical_bridge_closed: bool = False
    normalization_closed: bool = False
    scale_dependence_closed: bool = False
    no_fit_discipline_satisfied: bool = True

    def to_dict(self) -> dict[str, bool]:
        return asdict(self)


def _common_payload(artifact: str) -> dict[str, Any]:
    return {
        "artifact": artifact,
        "version": VERSION,
        "claim_boundary": (
            "Interface scaffold only. No BHSM q0^2 value, Wilson coefficients, "
            "form factors, physical q^2 bridge, or micro-plateau nodes are derived."
        ),
        "empirical_inputs_used": False,
        "rare_b_data_fitting_used": False,
        "pdg_reference_values_used": False,
        "w_calibration_used": False,
        "charged_mass_fitting_used": False,
        "ckm_fitting_used": False,
        "neutrino_limits_used": False,
        "legacy_threshold_tables_used": False,
        "frozen_predictions_changed": False,
        "official_prediction_logic_changed": False,
        "physics_model_logic_changed": False,
    }


def observable_convention_artifact() -> dict[str, Any]:
    payload = _common_payload("BHSM_rare_b_observable_convention_v5_1")
    payload.update(
        {
            "status": "RARE_B_OBSERVABLE_INTERFACE_ARTIFACTED",
            "decay_channel": "B0 -> K*0 mu+ mu-",
            "q2": {
                "definition": "squared dimuon invariant mass",
                "units": "GeV^2",
                "source": "external observable coordinate",
                "bhsm_derivation_status": "OPEN_MISSING_RARE_B_Q2_PHYSICAL_BRIDGE",
            },
            "observables": {
                "A_FB": {
                    "definition": "forward-backward asymmetry in the lepton angular distribution",
                    "normalized_form": "A_FB(q^2)=N_FB(q^2)/D_FB(q^2)",
                    "numerator": "N_FB(q^2), convention-dependent angular numerator",
                    "denominator": "D_FB(q^2), corresponding positive-rate normalization when defined",
                    "zero_condition": "N_FB(q0^2)=0 with D_FB(q0^2) != 0",
                },
                "dGamma_dq2": {
                    "definition": "differential decay rate with respect to q^2",
                    "bhsm_derivation_status": "OPEN_MISSING_HADRONIC_FORM_FACTOR_INTERFACE",
                },
                "dB_dq2": {
                    "definition": "differential branching fraction placeholder requiring lifetime and normalization convention",
                    "bhsm_derivation_status": "OPEN_MISSING_HADRONIC_FORM_FACTOR_INTERFACE",
                },
                "P5_prime": {
                    "definition": "optimized angular-observable placeholder",
                    "node_prediction_status": MICROPLATEAU_VERDICT,
                },
            },
            "convention_metadata": {
                "normalization_convention": "external angular-analysis convention slot",
                "complex_part_operation": "explicit real-part operation required where amplitudes are complex",
                "scale_dependence": "mu slot required for Wilson/effective coefficients",
                "domain_assumptions": [
                    "q^2 lies in a physical analysis domain supplied externally",
                    "D_FB(q^2) must be nonzero before a zero crossing is meaningful",
                ],
                "singularity_conditions": [
                    "D_FB(q0^2)=0 invalidates the normalized zero-crossing interpretation",
                    "missing Wilson or form-factor inputs prevent prediction emission",
                ],
            },
            "dependencies": [
                "rare_b_transition_operator_interface",
                "rare_b_hadronic_interface",
                "rare_b_afb_null_balance",
            ],
        }
    )
    return payload


def transition_operator_interface_artifact() -> dict[str, Any]:
    payload = _common_payload("BHSM_rare_b_transition_operator_interface_v5_1")
    payload.update(
        {
            "status": "RARE_B_TRANSITION_OPERATOR_INTERFACE_ARTIFACTED",
            "channel": "b -> s mu+ mu-",
            "operator_basis_slots": {
                "O7": "dipole/electromagnetic operator slot",
                "O9": "semileptonic vector operator slot",
                "O10": "semileptonic axial-vector operator slot",
                "primed_or_beyond_slots": "optional external-convention extension slots",
            },
            "wilson_coefficient_slots": {
                "C7_eff": {"status": "OPEN_MISSING_BHSM_WILSON_COEFFICIENT_DERIVATION"},
                "C9_eff": {"status": "OPEN_MISSING_BHSM_WILSON_COEFFICIENT_DERIVATION"},
                "C10_eff": {"status": "OPEN_MISSING_BHSM_WILSON_COEFFICIENT_DERIVATION"},
            },
            "flavor_prefactor_slot": {
                "symbolic_form": "V_tb V_ts^* or convention-equivalent slot",
                "bhsm_status": "OPEN_MISSING_BHSM_TO_RARE_B_OPERATOR_MATCHING",
                "note": "CKM geometry alone does not currently provide the rare-B observable map.",
            },
            "scale_slot": {"symbol": "mu", "status": "OPEN_MISSING_SCALE_DEPENDENCE_CLOSURE"},
            "sm_external_slot": "allowed for convention definitions only, not BHSM derivation",
            "bhsm_contribution_slot": {
                "status": "OPEN_MISSING_BHSM_TO_RARE_B_OPERATOR_MATCHING",
                "value": None,
            },
            "matching_map_status": "OPEN_MISSING_BHSM_TO_RARE_B_OPERATOR_MATCHING",
        }
    )
    return payload


def hadronic_interface_artifact() -> dict[str, Any]:
    payload = _common_payload("BHSM_rare_b_hadronic_interface_v5_1")
    payload.update(
        {
            "status": "RARE_B_HADRONIC_FORM_FACTOR_INTERFACE_ARTIFACTED",
            "exclusive_decay_channel": "B0 -> K*0 mu+ mu-",
            "form_factor_basis": {
                "basis_status": "external convention slot",
                "required_symbols": ["V(q^2)", "A0(q^2)", "A1(q^2)", "A2(q^2)", "T1(q^2)", "T2(q^2)", "T3(q^2)"],
            },
            "q2_dependent_inputs": True,
            "uncertainties": "required external/provenance-tagged inputs; not supplied by BHSM v5.1",
            "provenance": "interface scaffold only",
            "bhsm_derivation_status": "OPEN_MISSING_BHSM_HADRONIC_MATRIX_ELEMENTS",
            "exclusive_prediction_requires_hadronic_inputs": True,
        }
    )
    return payload


def afb_null_balance_artifact() -> dict[str, Any]:
    payload = _common_payload("BHSM_rare_b_afb_null_balance_v5_1")
    payload.update(
        {
            "status": "RARE_B_AFB_NULL_BALANCE_INTERFACE_ARTIFACTED",
            "audit_classification": NullEquationAudit.EXPLICIT_BUT_EXTERNAL_CONVENTION_ONLY.value,
            "symbolic_numerator": "N_FB(q^2)=Re[F_9(q^2,mu,form_factors,C9_eff,...)+F_7(q^2,mu,form_factors,C7_eff,...)]",
            "symbolic_denominator": "D_FB(q^2)=rate-normalization functional for the selected angular convention",
            "zero_condition": "N_FB(q0^2)=0",
            "nonzero_denominator_condition": "D_FB(q0^2) != 0",
            "required_coefficient_inputs": ["C7_eff", "C9_eff", "C10_eff", "scale mu", "operator basis convention"],
            "required_form_factor_inputs": ["B -> K* form-factor basis and q^2 dependence", "hadronic uncertainty model"],
            "required_physical_q2_input": {
                "units": "GeV^2",
                "source": "external observable coordinate",
                "bhsm_derivation_status": "OPEN_MISSING_RARE_B_Q2_PHYSICAL_BRIDGE",
            },
            "assumptions": [
                "No hadronic cancellation is assumed.",
                "No simplified textbook relation is asserted as a BHSM derivation.",
                "Real-part operation is explicit because amplitudes may be complex.",
            ],
            "closure_status": "INTERFACE_ARTIFACTED_PHYSICAL_DERIVATION_OPEN",
        }
    )
    return payload


def matching_dependencies() -> list[MatchingDependency]:
    return [
        MatchingDependency("BHSM flavor selector", "BHSM flavor geometry", "b -> s channel selection", "dimensionless", "none closed", "v5.0/v5.1 audit", None, "OPEN_MISSING_BHSM_TO_RARE_B_OPERATOR_MATCHING", "rare-B operator matching"),
        MatchingDependency("CKM/relative transport input", "CKM artifact", "flavor prefactor slot", "dimensionless", "relative transport only", "artifacts/CKM_no_fit_operator_output_v1.json", None, "ARTIFACT_BACKED_INPUT_NOT_OBSERVABLE_MAP", "operator and normalization matching"),
        MatchingDependency("current normalization", "charged-current normalization", "absolute amplitude normalization", "dimensionless/action units", "not fixed", "v4.8/v4.9 blockers", None, "CKM_RELATIVE_CURRENT_NORMALIZATION_BLOCKED", "action-backed current normalization"),
        MatchingDependency("operator matching", "BHSM interaction layer", "O7/O9/O10 basis contributions", "effective Hamiltonian units", "external convention slot", "v5.1 scaffold", None, "OPEN_MISSING_BHSM_TO_RARE_B_OPERATOR_MATCHING", "operator matching theorem"),
        MatchingDependency("Wilson contribution", "BHSM matched operators", "C7_eff/C9_eff/C10_eff", "dimensionless convention-dependent", "not supplied", "v5.1 scaffold", None, "OPEN_MISSING_BHSM_WILSON_COEFFICIENT_DERIVATION", "Wilson matching theorem"),
        MatchingDependency("dimensionful scale", "BHSM geometric variables", "q^2 in GeV^2", "GeV^2", "absent", "v5.1 q^2 audit", None, "OPEN_MISSING_RARE_B_Q2_PHYSICAL_BRIDGE", "physical q^2 bridge"),
        MatchingDependency("q^2 dependence", "mode/geometry coordinate", "observable coordinate dependence", "GeV^2", "external coordinate accepted only", "v5.1 scaffold", None, "OPEN_MISSING_RARE_B_Q2_PHYSICAL_BRIDGE", "mode-to-q^2 map"),
        MatchingDependency("RG-scale dependence", "scale mu", "Wilson/effective coefficient scale handling", "scheme-dependent", "not closed", "v5.1 scaffold", None, "OPEN_MISSING_SCALE_DEPENDENCE_CLOSURE", "renormalization-scale theorem"),
        MatchingDependency("hadronic matching", "quark-level operator", "B -> K* matrix elements", "form-factor convention", "not supplied", "v5.1 scaffold", None, "OPEN_MISSING_BHSM_HADRONIC_MATRIX_ELEMENTS", "hadronic matrix elements"),
        MatchingDependency("observable normalization", "angular amplitudes", "A_FB numerator/denominator", "dimensionless", "external convention slot", "v5.1 scaffold", None, "OPEN_MISSING_OBSERVABLE_NORMALIZATION_CLOSURE", "angular convention and normalization closure"),
    ]


def bhsm_matching_map_artifact() -> dict[str, Any]:
    payload = _common_payload("BHSM_rare_b_bhsm_matching_map_v5_1")
    payload.update(
        {
            "status": "RARE_B_BHSM_MATCHING_MAP_OPEN_DEPENDENCY_GRAPH_ARTIFACTED",
            "dependencies": [row.to_dict() for row in matching_dependencies()],
            "physical_matching_closed": False,
            "prediction_ready": False,
        }
    )
    return payload


def validate_q2_coordinate(units: str, source: str, bhsm_derivation_status: str) -> dict[str, Any]:
    if units != "GeV^2":
        raise ValueError(f"rare-B q^2 interface requires GeV^2 metadata, got {units!r}")
    if source == "BHSM-derived" and bhsm_derivation_status.startswith("OPEN_"):
        raise ValueError("external q^2 cannot be mislabeled as BHSM-derived while bridge is open")
    return {
        "units": units,
        "source": source,
        "bhsm_derivation_status": bhsm_derivation_status,
        "is_physical_bridge_closed": bhsm_derivation_status == "BHSM_DERIVED_Q2_PHYSICAL_BRIDGE",
    }


def prediction_kill_screen(gates: PredictionGateState | None = None) -> dict[str, Any]:
    gates = gates or PredictionGateState()
    gate_dict = gates.to_dict()
    missing = [name for name in PREDICTION_GATE_ORDER if not gate_dict[name]]
    return {
        "prediction_claimed": False,
        "q0_squared_value": None,
        "q0_squared_units": None,
        "microplateau_node_coordinates": [],
        "no_fit_discipline_preserved": gates.no_fit_discipline_satisfied,
        "all_required_gates_closed": not missing,
        "blocking_gates": missing,
        "rejection_reason": "No numerical rare-B prediction may be emitted while required gates remain open." if missing else "No frozen prediction-producing chain is registered in v5.1.",
    }


def observable_map_audit_artifact(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[3]
    search_terms = (
        "rare B",
        "rare-B",
        "b to s",
        "b -> s",
        "mumu",
        "mu mu",
        "muon",
        "A_FB",
        "AFB",
        "forward backward",
        "zero crossing",
        "q0",
        "q^2",
        "q2",
        "Wilson",
        "C7",
        "C9",
        "C10",
        "O7",
        "O9",
        "O10",
        "Hamiltonian",
        "effective Hamiltonian",
        "form factor",
        "K*",
        "Kstar",
        "angular coefficient",
        "J_6",
        "I_6",
        "P5",
        "P'_5",
        "microplateau",
        "micro-plateau",
        "node map",
    )
    paths = _iter_audit_paths(root)
    findings: list[dict[str, Any]] = []
    for path in paths:
        lines = path.read_text(encoding="utf-8").splitlines()
        relative = str(path.relative_to(root)).replace("\\", "/")
        for term in search_terms:
            term_lower = term.lower()
            first: tuple[int, str] | None = None
            count = 0
            for line_no, line in enumerate(lines, 1):
                if term_lower in line.lower():
                    count += 1
                    if first is None:
                        first = (line_no, line)
            if first is not None:
                line_no, line = first
                lowered = line.lower()
                findings.append(
                    {
                        "search_term": term,
                        "file": relative,
                        "line": line_no,
                        "matched_content_summary": _summarize_audit_line(line),
                        "match_count_in_file": count,
                        "scientific_significance": _classify_significance(line),
                        "constitutes_interface": "v5.1" in line or "interface" in lowered,
                        "constitutes_derivation": False,
                        "constitutes_prediction": False,
                        "status": "documentation_or_blocker_context",
                    }
                )
    payload = _common_payload("BHSM_rare_b_observable_map_audit_v5_1")
    payload.update(
        {
            "status": "RARE_B_OBSERVABLE_MAP_AUDIT_ARTIFACTED",
            "scan_scope": [
                "src/",
                "tests/",
                "artifacts/",
                "docs/",
                "scripts/",
                "manuscript/",
                "theory/",
                "CLAIMS.md",
                "STATUS.md",
                "ARTIFACT_INDEX.md",
                "README.md",
                "ROADMAP.md",
            ],
            "search_terms": list(search_terms),
            "finding_policy": "one summarized finding per search term per file, with match_count_in_file",
            "null_equation_audit": NullEquationAudit.EXPLICIT_BUT_EXTERNAL_CONVENTION_ONLY.value,
            "repository_findings": sorted(findings, key=lambda row: (row["file"], row["search_term"], row["line"])),
            "audit_answers": audit_answers(),
        }
    )
    return payload


def _iter_audit_paths(root: Path) -> list[Path]:
    roots = [
        root / "src",
        root / "tests",
        root / "artifacts",
        root / "docs",
        root / "scripts",
        root / "manuscript",
        root / "theory",
    ]
    direct = [
        root / "CLAIMS.md",
        root / "STATUS.md",
        root / "ARTIFACT_INDEX.md",
        root / "README.md",
        root / "ROADMAP.md",
    ]
    suffixes = {".py", ".md", ".json", ".txt", ".yml", ".yaml", ".toml", ".cff"}
    paths: list[Path] = []
    for audit_root in roots:
        if not audit_root.exists():
            continue
        for path in audit_root.rglob("*"):
            if path.name == ARTIFACT_FILES["observable_map_audit"]:
                continue
            if path.is_file() and path.suffix.lower() in suffixes:
                paths.append(path)
    paths.extend(path for path in direct if path.exists())
    return sorted(set(paths))


def _classify_significance(line: str) -> str:
    lowered = line.lower()
    if "blocked" in lowered or "open_missing" in lowered:
        return "blocked_or_open_status"
    if "a_fb" in lowered or "q0" in lowered:
        return "observable_interface_context"
    if "wilson" in lowered or "form factor" in lowered:
        return "required_external_interface_layer"
    return "search_context"


def _summarize_audit_line(line: str) -> str:
    summary = line.strip()[:220]
    if any(phrase in summary for phrase in forbidden_prediction_phrases()):
        return "[redacted forbidden-claim test fixture or no-go phrase]"
    return summary


def audit_answers() -> dict[str, Any]:
    return {
        "b_to_s_mumu_transition_operator_map_exists": False,
        "wilson_coefficient_map_exists": False,
        "afb_numerator_interface_exists": True,
        "afb_null_balance_equation_exists": True,
        "physical_q2_bridge_exists": False,
        "hadronic_form_factor_interface_exists": True,
        "bhsm_derived_hadronic_map_exists": False,
        "exact_microplateau_node_map_exists": False,
        "numerical_q0_squared_prediction_exists": False,
    }


def scaffold_verdict_artifact() -> dict[str, Any]:
    payload = _common_payload("BHSM_rare_b_observable_map_scaffold_verdict_v5_1")
    payload.update(
        {
            "primary_verdict": PRIMARY_VERDICT,
            "prediction_kill_screen": prediction_kill_screen(),
            "layer_status": {
                "observable_convention": "RARE_B_OBSERVABLE_INTERFACE_ARTIFACTED",
                "transition_operator": "RARE_B_TRANSITION_OPERATOR_INTERFACE_ARTIFACTED",
                "wilson_interface": "RARE_B_WILSON_COEFFICIENT_SLOTS_ARTIFACTED_DERIVATION_OPEN",
                "hadronic_form_factor_interface": "RARE_B_HADRONIC_FORM_FACTOR_INTERFACE_ARTIFACTED",
                "bhsm_matching_map": "RARE_B_BHSM_MATCHING_MAP_OPEN_DEPENDENCY_GRAPH_ARTIFACTED",
                "afb_null_balance": "RARE_B_AFB_NULL_BALANCE_INTERFACE_ARTIFACTED",
                "q2_physical_bridge": "OPEN_MISSING_RARE_B_Q2_PHYSICAL_BRIDGE",
                "numerical_q0_squared_prediction": Q0_VERDICT,
                "exact_microplateau_node_map": MICROPLATEAU_VERDICT,
            },
            "validated": [
                "observable convention interface is machine-readable",
                "transition-operator and Wilson slots are explicit and provenance-tagged",
                "hadronic/form-factor interface is explicit for the exclusive channel",
                "A_FB null-balance separates numerator from denominator",
                "BHSM matching dependencies are localized as an open dependency graph",
                "prediction kill screen rejects numerical q0^2 emission",
            ],
            "invalidated_or_downgraded": [
                "CKM geometry alone is insufficient for a rare-B observable prediction",
                "a symbolic q2 variable is not a physical GeV^2 bridge",
                "Wilson slots are interface layers, not BHSM-derived coefficients",
                "form factors are required and are not supplied by BHSM v5.1",
                "interface completion is not a q0^2 prediction",
            ],
            "still_open": list(PRESERVED_BLOCKERS),
            "preserved_blocked_statuses": list(PRESERVED_BLOCKERS),
            "no_fit_prohibitions": list(NO_FIT_PROHIBITIONS),
            "claim_safe_conclusion": (
                "BHSM v5.1 artifacts a machine-readable rare-B observable-map interface covering observable conventions, "
                "effective operators, Wilson-coefficient slots, hadronic inputs, the A_FB null condition, and required "
                "BHSM matching dependencies. It does not derive the physical matching map, a dimensionful q^2 bridge, "
                "Wilson coefficients, form factors, q0^2, or micro-plateau node positions. Prediction claimed remains no."
            ),
        }
    )
    return payload


def build_artifact_payloads(repo_root: Path | None = None) -> dict[str, dict[str, Any]]:
    return {
        "observable_convention": observable_convention_artifact(),
        "transition_operator_interface": transition_operator_interface_artifact(),
        "hadronic_interface": hadronic_interface_artifact(),
        "afb_null_balance": afb_null_balance_artifact(),
        "bhsm_matching_map": bhsm_matching_map_artifact(),
        "observable_map_audit": observable_map_audit_artifact(repo_root),
        "scaffold_verdict": scaffold_verdict_artifact(),
    }


def deterministic_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def materialize_artifacts(root: Path) -> list[Path]:
    payloads = build_artifact_payloads(root)
    written = []
    for key, filename in ARTIFACT_FILES.items():
        path = root / "artifacts" / filename
        path.write_text(deterministic_json(payloads[key]), encoding="utf-8")
        written.append(path)
    return written


def rare_b_status_report(repo_root: Path | None = None) -> dict[str, Any]:
    payloads = build_artifact_payloads(repo_root)
    verdict = payloads["scaffold_verdict"]
    return {
        "report": "BHSM v5.1 rare-B observable-map scaffold",
        "version": VERSION,
        "primary_verdict": verdict["primary_verdict"],
        "layer_status": verdict["layer_status"],
        "audit_answers": audit_answers(),
        "prediction_state": verdict["prediction_kill_screen"],
        "artifacts": {key: f"artifacts/{filename}" for key, filename in ARTIFACT_FILES.items()},
        "preserved_blocked_statuses": list(PRESERVED_BLOCKERS),
        "claim_safe_conclusion": verdict["claim_safe_conclusion"],
    }


def rare_b_status_to_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# BHSM v5.1 Rare-B Observable Map Scaffold",
        "",
        f"Primary verdict: `{report['primary_verdict']}`",
        "",
        "## Layer Status",
    ]
    for key, value in report["layer_status"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Prediction State"])
    for key in ("prediction_claimed", "q0_squared_value", "q0_squared_units", "microplateau_node_coordinates", "no_fit_discipline_preserved"):
        lines.append(f"- `{key}`: `{report['prediction_state'][key]}`")
    lines.extend(["", "## Claim-Safe Conclusion", "", report["claim_safe_conclusion"], ""])
    return "\n".join(lines)


def forbidden_prediction_phrases() -> tuple[str, ...]:
    return (
        "BHSM predicts q0^2",
        "BHSM predicts the A_FB zero",
        "BHSM predicts rare-B micro-plateaus",
        "BHSM explains LHCb anomalies",
        "BHSM falsifies continuous QFT",
    )
