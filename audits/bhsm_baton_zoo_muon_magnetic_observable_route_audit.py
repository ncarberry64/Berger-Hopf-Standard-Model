"""Bind retained muon magnetic-observable operands without replaying campaigns.

This is a dependency and existing-ledger audit.  It never constructs a vertex,
substitutes a missing native contribution, or calls a physical readout on a test
coefficient.  Run twice into separate directories and compare output bytes.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
from pathlib import Path


REPO = Path(r"C:/Users/carbe/Downloads/BHSM_muon_parent_maxwell_worktree_20261001")
WORK = Path(r"C:/Users/carbe/OneDrive/Documents/CODEX")
OUT = WORK / "outputs/bhsm_muon_magnetic_observable_route_audit_20261014"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=int, required=True)
    args = parser.parse_args()
    output = OUT / f"run_{args.run}"
    output.mkdir(parents=True, exist_ok=False)
    pins: dict[str, dict] = {}

    def read(relative: str, *, workspace: bool = False):
        path = (WORK if workspace else REPO) / relative
        payload = path.read_bytes()
        key = ("workspace/" if workspace else "repository/") + relative
        pins[key] = {"path": str(path), "sha256": hashlib.sha256(payload).hexdigest(),
                     "bytes": len(payload)}
        text = payload.decode("utf-8-sig")
        return json.loads(text) if path.suffix == ".json" else text

    read("AGENTS.md")
    source_names = [
        "universal_precision_form_factor", "universal_lsz",
        "universal_loop_renormalization", "universal_quadratic_spectrum",
        "universal_dressed_pole", "ae31_c2_local_em_ward_identity",
        "muon_intrinsic_fermion_wick_application", "muon_continued_current_factor",
        "muon_native_kkt_downstream", "muon_calibrated_local_pauli",
        "muon_paired_local_vp_pauli",
    ]
    sources = {name: read(f"src/bhsm/interface/{name}.py") for name in source_names}
    pauli_doc = read("theory/muon_minimum_pauli_readout_20260930.md")
    read("theory/muon_active_action_combination_20261011.md")
    read("audits/muon_pauli_sufficient_readout.py")
    read("tests/test_muon_pauli_sufficient_readout.py")
    read("scripts/verify_muon_active_action_combination.py")
    required_history_sentence = "No full incoming-history reconstruction is required by this algebra alone."
    assert required_history_sentence in pauli_doc

    paths = {
        "active_combination": "artifacts/muon_observable_combination_20261011/contribution_error_table.json",
        "combination_verification": "artifacts/muon_observable_combination_20261011/verification.json",
        "calibration_inputs": "artifacts/muon_calibrated_pauli_20261009/inputs.json",
        "calibrated_pauli": "artifacts/muon_calibrated_pauli_20261009/run_1/calibrated_pauli.json",
        "paired_local_overlap": "artifacts/muon_paired_local_vp_pauli_20261011/run_1/result.json",
        "continued_current": "artifacts/muon_continued_current_factor_20261011/run_1/result.json",
        "unsquared_domain": "artifacts/muon_native_unsquared_domain_matching_20261011/run_1/result.json",
        "magnetic_source_returns": "artifacts/muon_inherited_magnetic_weak_combination_20261012/run_3/result.json",
    }
    data = {key: read(path) for key, path in paths.items()}
    remote = read("outputs/bhsm_full_realization_search_20261013/remote_search.json", workspace=True)
    pr = remote["pr468"]

    # Verify arithmetic only on already evaluated, explicitly included rows.
    ledger = data["active_combination"]
    rows = []
    included = []
    for row in ledger["contribution_and_error_table"]:
        rows.append({k: row[k] for k in ("component", "status", "a_mu", "owner", "overlap_rule")})
        if row.get("already_in_local_subtotal") is True:
            assert isinstance(row["a_mu"], (int, float)) and math.isfinite(row["a_mu"])
            included.append(row["a_mu"])
    subtotal = math.fsum(included)
    assert abs(subtotal - ledger["completed_local_subtotal"]) <= 2e-18
    assert abs(2 * (1 + subtotal) - ledger["completed_local_subtotal_g"]) <= 1e-15
    for name in ("complete_a_mu", "complete_g_mu", "complete_magnetic_moment"):
        assert ledger[name] is None
    assert ledger["complete_observable"] is False
    config = data["calibration_inputs"]
    for key in ("measured_muon_anomaly_used", "equivalent_measured_muon_g_used",
                "discrepancy_inferred_native_correction_used"):
        assert config["claims"][key] is False
    assert data["calibrated_pauli"]["muon_anomaly_used"] is False
    assert data["calibrated_pauli"]["native_Pauli_evaluated"] is False
    assert data["continued_current"]["physical_external_shell_or_LSZ_or_Pauli_completed"] is False
    assert data["unsquared_domain"]["physical_external_pole_LSZ_or_Pauli_assignment"] is False

    targets = {"muon_gminus2_from_renormalized_vertex", "assemble_renormalized_vertex"}
    calls = {key: [] for key in sorted(targets)}
    for folder in (REPO / "src", REPO / "scripts"):
        for path in sorted(folder.rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            text = path.read_text(encoding="utf-8-sig")
            if not any(name in text for name in targets):
                continue
            tree = ast.parse(text, filename=str(path))
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                name = node.func.id if isinstance(node.func, ast.Name) else (
                    node.func.attr if isinstance(node.func, ast.Attribute) else None)
                if name in calls:
                    calls[name].append({"path": str(path.relative_to(REPO)), "line": node.lineno})
    assert all(not value for value in calls.values()), calls

    def function_lines(module: str):
        return {node.name: node.lineno for node in ast.parse(sources[module]).body
                if isinstance(node, (ast.FunctionDef, ast.ClassDef))}

    interfaces = {
        name: {"source": f"src/bhsm/interface/{name}.py", "definitions": function_lines(name)}
        for name in source_names
    }
    compact = {}
    for name in ("continued_current", "unsquared_domain", "paired_local_overlap", "magnetic_source_returns"):
        compact[name] = {key: value for key, value in data[name].items()
                         if isinstance(value, (str, int, float, bool)) or value is None}

    primary = {name: {key: value[key] for key in ("value_decimal", "unit", "source")}
               for name, value in config["primary_measurements"].items()}
    local = data["calibrated_pauli"]
    audit = {
        "classification": "EVALUATED_RETAINED_MUON_MAGNETIC_OBSERVABLE_ROUTE_AND_DEPENDENCY_AUDIT",
        "scope": "Read-only retained-source/artifact audit and existing local-ledger arithmetic; no physical campaign rerun.",
        "equations": {
            "vertex": "Gamma_R^mu = D^mu F1(q^2) + i sigma^{mu nu} q_nu F2(q^2)/(2 m_mu), after factoring signed charge",
            "intrinsic": "a_mu=F2(0); g_mu=2(1+a_mu); mu_vector=g_mu Q e S/(2 m_mu)",
            "normalization": "F1(0)=1 in charge-factored convention; charge-inside F1=-1 must not be mixed with it",
            "soft_readout": "a_mu=lim_{t->0}<L_u,Gamma_R(tu)-Gamma_R(0)>/t; exact q=0 Pauli basis vanishes",
            "Ward_scope": "q_mu P^mu=0: Ward fixes longitudinal/charge consistency, not transverse F2",
        },
        "intrinsic_vs_preparation": {
            "repository_statement": required_history_sentence,
            "full_collider_formation_proved_necessary_for_intrinsic_F2": False,
            "state_independence_proved": False,
            "physical_scope": "Need a selected physical muon external-state/pole and matched electromagnetic vertex. Any history dependence of these operands needs its action-sufficient projection or a bound; a new blanket collider-history prerequisite is not justified.",
            "measurement": "A collider/ring preparation predicts state populations and measurement response. Timelike e+e- to mu+mu- formation is not itself the elastic soft-transfer F2(0) readout.",
            "primary_definition_reference": "https://pdg.lbl.gov/2025/reviews/rpp2025-rev-g-2-muon-anom-mag-moment.pdf",
        },
        "first_missing_physical_map": {
            "from": "Actual retained unsquared finite muon/current coefficient germ and its owned domain",
            "to": "Same-owner physical inverse two-point symbol Gamma2_mu(z), its spectral derivative, action-selected pole and normalized external injections",
            "available_state_can_supply_directly": False,
            "reason": "Retained finite first-order current/range applications have no physical external pole/LSZ assignment. The active action record says the Cauchy envelope source-energy cancels in the transported physical field, so it supplies no physical Gamma2,E residue.",
            "spectral_convention_guard": "Universal dressed-pole z=m_p^2-i m_p Gamma_p is squared; no unproved identification with unsquared temporal energy E, or E^2, is admitted.",
        },
        "smallest_new_native_application_after_external_match": {
            "source": "J_gamma=bar_gamma B_tilde r_in on the owned physical quotient",
            "response": "(K0_Q+zeta M0_Q)u_zeta=J_gamma",
            "scalar_target": local["native_reduction"]["minimal_scalar"],
            "minimal_response": local["native_reduction"]["minimal_response_application"],
            "adjoint_identity": local["native_reduction"]["resolvent_remainder_identity"],
            "required_motion_once": ["external pole/injection and residue", "current/source", "soft momentum", "physical cutoff if reached", "quotient/domain and boundary", "relative completion/counterterm", "owned local-overlap subtraction", "charge normalization"],
            "existing_physical_state_sufficiency": "The retained coefficient state supplies action/current inputs and finite source solves, not the missing normalized shell, positive completed quotient or soft-limit vertex. A full R_ind matrix is unnecessary if the reached current and adjoint contractions are sufficient.",
            "cutoff_cancellation_established": local["native_reduction"]["full_completion_cutoff_cancellation_established"],
            "no_missing_default_coefficient": True,
        },
        "reusable_computations": [
            {"component": "Charge and local Ward/Pauli algebra", "use": "Reuse Q=-1/tree Ward, charge-factored F1 and transverse dual. Tree F2=0 does not determine quantum F2."},
            {"component": "Continued C6 current and magnetic Y coefficients", "use": "Reuse actual -Q source, canonical -iG/N magnetic insertion and both finite inverse/dual domain placements; no second electric-charge factor."},
            {"component": "Unsquared/squared range and dual match", "use": "Reuse actual 48 source applications and all free final/corner rows on their declared finite domain; no physical exterior pole inferred."},
            {"component": "Inherited magnetic action/source/temporal returns", "use": "Reuse wall/frame/source work and initial-corner outer returns as finite action operands, not a normalized a_mu error."},
            {"component": "Calibrated local QED/EW/hadronic ledger", "use": "Reuse frozen evaluated rows with their declared inputs and shared errors; count their same-background native overlap once."},
            {"component": "Paired local VP and soft readout", "use": "Reuse same-external-muon-shell local overlap; physical native subtraction still needs common photon/current/domain and shell matching."},
            {"component": "Universal readout/LSZ/renormalization interfaces", "use": "Reuse validators and supplied-tensor contractions; they do not generate the missing physical vertex or mode."},
        ],
        "available_evidence": compact,
        "calibrated_dependency_audit": {
            "classification": "Explicitly calibrated local-sector result, not input-independent BHSM magnetic prediction",
            "historical_authorization_record": config["authorization"],
            "primary_measurements": primary,
            "selected_consumers": config["selected_consumer_values"],
            "target_leakage_flags": {key: config["claims"][key] for key in ("measured_muon_anomaly_used", "equivalent_measured_muon_g_used", "discrepancy_inferred_native_correction_used")},
            "excluded_magnetic_mass_ratio": config["reference_and_rejected_inputs"]["CODATA2022_muon_electron_ratio"],
            "remaining_dependencies": ["Rb recoil alpha and spectroscopy/mass extraction include bound-state QED and metrology dependencies", "Optical muonium mass ratio uses its bound-state extraction and equal-charge assumption", "Lifetime-to-G_F matching carries weak/radiative assumptions", "Hadronic rows use empirical spectral/published connected input", "Physical cross-source covariance and omitted/native sectors remain unclosed"],
            "fixed_Y_replaced_or_independently_fitted": local["independent_Yukawas_fitted"],
            "common_scale_matches_all_selected_central_mass_ratios": local["matching"]["common_scale_matches_all_supplied_central_mass_ratios"],
        },
        "existing_local_ledger_check": {
            "included_row_count": len(included), "evaluated_rows": rows,
            "sum": subtotal, "recorded_sum": ledger["completed_local_subtotal"],
            "absolute_sum_difference": abs(subtotal-ledger["completed_local_subtotal"]),
            "g_of_local_subtotal_only": 2*(1+subtotal),
            "complete_a_mu": None, "complete_g_mu": None, "complete_magnetic_moment": None,
            "unknown_rows_retained_as_null": True,
            "complete_uncertainty": None,
        },
        "PR468_reference_only": {
            "url": pr["url"], "head_sha": pr["head_sha"], "commit_date_utc": pr["commit_date_utc"],
            "search_observed_at": remote["searched_at_utc"],
            "scope": "Cached observed reference, not a claim about present live head",
            "mixed_HS": "Composes supplied Hu,Hv,Huv and Lu,Lv,Luv into same-scalar-H/profile terminal mixed jets; no physical HS/terminal graph selection and no zero fill.",
            "event_KKT": "Composes supplied 0,u,v,uv leaves with actual retarded child domain; does not produce the physical collision/event inputs.",
            "pole_consumer": "Charged-lepton squared-pole mass/flavor invariant of supplied admitted poles and covariance, not a Pauli/F2/g calculation.",
            "reusable_for_missing_magnetic_map": "Conditional jet/covariance machinery only after common physical owners and spectral conversion are supplied.",
        },
        "source_interfaces": interfaces,
        "production_callsite_audit": {"scope": "Direct AST calls under repository src and scripts; tests excluded", "calls": calls,
                                     "conclusion": "No production caller for the physical muon vertex-to-gminus2 factory or renormalized-vertex assembly was found in this local checkout."},
        "physical_status": {"a_mu": None, "g_mu": None, "magnetic_moment": None,
                            "physical_vertex_or_external_modes_completed": False,
                            "physical_promotion": False, "new_coupled_physical_corrections": 0,
                            "gate_order": "Whole physical derivative, exactly one coupled correction, then fresh original Maxwell and all226 <=2e-10; audit performs none of these."},
        "verification": {"no_action_or_history_replay": True, "no_default_or_synthetic_physical_readout": True,
                         "no_target_anomaly_fitting": True, "historical_inputs_unchanged": True,
                         "repeat_scope": "Run this audit twice; byte identity verifies deterministic source/dependency and existing-ledger audit, not a physical campaign scientific rerun."},
        "input_hashes": pins,
        "producer": {"path": str(Path(__file__).resolve()), "sha256": sha(Path(__file__))},
    }
    for pin in pins.values():
        assert sha(Path(pin["path"])) == pin["sha256"], pin["path"]
    text = json.dumps(audit, indent=2, sort_keys=True, allow_nan=False) + "\n"
    (output / "audit.json").write_text(text, encoding="utf-8", newline="\n")
    report = "\n".join([
        "Retained muon magnetic observable route audit",
        "",
        "Intrinsic a_mu=F2(0) needs a physical normalized elastic muon-photon vertex. The Pauli algebra does not itself require a complete collider history; any state/vertex history dependence needs an action-sufficient projection or bound.",
        "",
        "First missing map: retained unsquared finite coefficient/current state -> same-owner physical Gamma2_mu(z), derivative/residue, pole selection and external injections. Existing finite current applications do not assign that shell or normalize physical photons.",
        "",
        "Smallest subsequent native compute: source-directed positive quotient photon response on matched J_gamma, paired with the downstream adjoint, then its soft derivative with external/source/domain/completion/counterterm/owned-overlap motion once. A full native response matrix or complete incoming history has not been proved necessary.",
        "",
        f"Existing calibrated local subtotal: {subtotal:.17g}; its g-only conversion: {2*(1+subtotal):.17g}. Eight explicitly included rows reproduce the retained subtotal. These are calibrated local-sector components; complete a_mu, g, moment and error remain unevaluated. Unknown native and local complements were not assigned zero.",
        "",
        "Selected alpha, masses, lifetime and hadronic inputs are measured/extracted calibrations. The selected configuration excludes measured muon anomaly, equivalent muon g and discrepancy-inferred native corrections, and rejects the magnetic-moment-correlated CODATA mu/e ratio. Bound-state QED, weak matching and empirical hadronic dependencies remain explicit.",
        "",
        "PR468 cached head b51ed0e318e162dc9919698fb9ed6d8aeafb13d3 supplies conditional mixed-event/HS and squared-pole consumers. It does not create physical terminal jets or the muon Pauli vertex. Unsquared E is not silently equated with squared pole z.",
        "",
        "All retained inputs are SHA256 pinned and unchanged. No physical readout, action campaign, history integration or coupled correction was run. Two audit materializations must agree byte for byte; this is an audit repeat, not a scientific rerun of the retained campaigns.",
        "",
        "Primary definition/measurement reference: https://pdg.lbl.gov/2025/reviews/rpp2025-rev-g-2-muon-anom-mag-moment.pdf",
        "",
    ])
    (output / "report.txt").write_text(report, encoding="utf-8", newline="\n")
    print(json.dumps({"output": str(output), "audit_sha256": sha(output/"audit.json"),
                      "report_sha256": sha(output/"report.txt"), "input_count": len(pins),
                      "physical_a_mu": None, "physical_promotion": False}))


if __name__ == "__main__":
    main()
