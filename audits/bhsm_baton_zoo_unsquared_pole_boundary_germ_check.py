"""Small algebraic checks on retained unsquared pole/energy operands.

No roots, actions, source responses, D5 inverses or histories are recomputed.
The only solves are the stored 6x6 candidate's original four-complement and
2x2 residue pairing.  Physical exterior maps are never fabricated.
"""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import numpy as np

REPO = Path(r"C:/Users/carbe/Downloads/BHSM_muon_parent_maxwell_worktree_20261001")
WORK = Path(r"C:/Users/carbe/OneDrive/Documents/CODEX")
BASE = WORK / "outputs/bhsm_unsquared_pole_boundary_germ_check_20261014"
GUARD = 2e-10


def encode(value):
    if isinstance(value, dict):
        return {k: encode(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [encode(v) for v in value]
    if isinstance(value, np.ndarray):
        return encode(value.tolist())
    if isinstance(value, (complex, np.complexfloating)):
        return [float(value.real), float(value.imag)]
    if isinstance(value, np.generic):
        return value.item()
    return value


def maximum(value):
    return float(np.max(np.abs(value)))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run", type=int, required=True)
    args = p.parse_args()
    output = BASE / f"run_{args.run}"
    output.mkdir(parents=True, exist_ok=False)
    pins = {}

    def read(relative):
        path = REPO / relative
        payload = path.read_bytes()
        pins[relative] = {"sha256": sha256(payload).hexdigest(), "bytes": len(payload)}
        if path.suffix == ".npz":
            with np.load(path, allow_pickle=False) as a:
                return {k: a[k].copy() for k in a.files}
        text = payload.decode("utf-8-sig")
        return json.loads(text) if path.suffix == ".json" else text

    for rel in ["AGENTS.md", "src/bhsm/interface/muon_unsquared_physical_boundary_pole.py",
                "src/bhsm/interface/muon_unsquared_forced_boundary_attachment.py",
                "src/bhsm/interface/muon_birth_external_trace_chart.py",
                "src/bhsm/interface/muon_d5_finite_trace_pole_match.py",
                "scripts/evaluate_muon_d5_finite_trace_pole_match.py",
                "scripts/evaluate_muon_chronological_current_amputation.py"]:
        read(rel)

    d5_path = "artifacts/muon_d5_finite_trace_pole_match_20261012/trial_0000_stage_pair_run_3"
    md = read(d5_path + "/result.json")
    assert md["actual_retarded_domain_sigma_flow_mode_or_physical_pole_admitted"] is False
    d5 = []
    for stage in range(2):
        a = read(d5_path + f"/stage_{stage:04d}_finite_trace_pole_and_clock_rows.npz")
        G, GE = a["full_gamma"], a["full_gamma_energy"]
        # Reconstruct independently from G; do not reuse the exported lifts.
        A, B, C, D = G[:4, :4], G[:4, 4:], G[4:, :4], G[4:, 4:]
        X = np.linalg.solve(A, B)
        Y = np.linalg.solve(A.T, C.T).T
        R, L = np.r_[-X, np.eye(2)], np.c_[-Y, np.eye(2)]
        K, Z = D-C@X, L@GE@R
        residue = R@np.linalg.solve(Z, L)
        null_right, null_left = G@R, L@G
        residue_right, residue_left = G@residue, residue@G
        spin = K-np.trace(K)*np.eye(2)/2
        stored_difference = max(maximum(R-a["literal_right_trace_lift"]),
                                maximum(L-a["literal_left_trace_lift"]),
                                maximum(K-a["charged_two_spin_equation"]),
                                maximum(Z-a["candidate_rank2_kinetic"]),
                                maximum(residue-a["candidate_rank2_residue"]))
        assert stored_difference <= GUARD
        assert max(maximum(null_right), maximum(null_left)) > GUARD
        d5.append({
            "stage": stage, "stored_candidate_energy": a["energy_candidate"].item(),
            "gamma_shape": G.shape, "gamma_energy_shape": GE.shape,
            "trace_center_abs": float(abs(np.trace(K)/2)),
            "full_right_null_rows_max": maximum(null_right),
            "full_left_null_rows_max": maximum(null_left),
            "traceless_spin_matrix": spin, "traceless_spin_Frobenius": float(np.linalg.norm(spin)),
            "candidate_residue_right_null_rows_max": maximum(residue_right),
            "candidate_residue_left_null_rows_max": maximum(residue_left),
            "gamma_singular_values_diagnostic_only": np.linalg.svd(G, compute_uv=False),
            "kinetic_pairing_condition_number": float(np.linalg.cond(Z)),
            "independent_vs_stored_check_max": stored_difference,
            "full_two_spin_null_guard_pass": False,
            "physical_residue_admitted": False,
            "interpretation": "Trace centering cancels one scalar, not the traceless two-spin equation. Nonzero spin dependence can be a physical background/probe response; it is not proved to be arithmetic and is not forced to zero.",
        })

    birth = read("artifacts/muon_birth_external_trace_chart_20261011/run_1/application.npz")
    tp, tc = (birth[k].item() for k in ("parent_birth_source_clock", "child_birth_source_clock"))
    T, TL = birth["envelope_value_reset"], birth["envelope_literal_left_reset"]
    # Product rule for chi=e^-E tau phi, at the actual E0=0 anchor.
    assert birth["continued_external_energy_anchor"].item() == 0
    right = -tc*T+birth["envelope_value_reset_energy_first"]+tp*T
    left = tc*TL+birth["envelope_literal_left_reset_energy_first"]-tp*TL
    birth_check = {
        "actual_source_clock_jump": birth["source_clock_jump"].item(),
        "envelope_right_energy_first_max": maximum(birth["envelope_value_reset_energy_first"]),
        "envelope_left_energy_first_max": maximum(birth["envelope_literal_left_reset_energy_first"]),
        "product_rule_physical_right_energy_first_max": maximum(right),
        "product_rule_physical_left_energy_first_max": maximum(left),
        "vs_stored_physical_right_first_max": maximum(right-birth["physical_value_reset_energy_first"]),
        "vs_stored_physical_left_first_max": maximum(left-birth["physical_literal_left_reset_energy_first"]),
        "interpretation": "These energy contacts are arm-origin envelope coordinates. They cancel in the represented physical Cauchy trace and are not a spectral pole residue.",
    }
    assert max(maximum(right), maximum(left)) <= GUARD

    amp_path = "artifacts/muon_chronological_current_amputation_20261011/run_1"
    amp_md = read(amp_path + "/result.json")
    finite = []
    for degree in range(2):
        a = read(amp_path + f"/fullbody_degree_{degree}_amputation.npz")
        G, GE = a["exterior_pole_matrix"], a["exterior_pole_matrix_energy_first"]
        identity_error = maximum(G-np.eye(len(G)))
        finite.append({
            "degree": degree, "dimension": len(G),
            "finite_IVP_gamma_minus_I_max": identity_error,
            "finite_IVP_gamma_energy_max": maximum(GE),
            "continued_source_energy_response_norm": float(np.linalg.norm(a["continued_source_energy_first"])),
            "envelope_transfer_energy_first_norm": float(np.linalg.norm(a["energy_shifted_core_trace_first"])),
            "envelope_derivative_minus_span_times_transfer_max": maximum(a["energy_shifted_core_trace_first"]-a["proper_clock_span"]*a["energy_shifted_core_trace"]),
            "physical_exterior_selected": False,
            "interpretation": "The retained initial-zero/free-final finite IVP has Gamma=I and no mass poles, although its source and energy-envelope responses are nonzero. No alternative boundary was installed.",
        })
        assert identity_error == 0 and maximum(GE) == 0
    cauchy = {}
    for side in ("incoming", "outgoing"):
        a = read(f"artifacts/muon_chronological_cauchy_trace_current_20261011/{side}_run_1/result.json")
        cauchy[side] = {
            "point_individual_energy_contact_max": max(v["point_individual_energy_contact_max"] for v in a["records"]),
            "point_canceled_energy_contact_max": max(v["point_energy_phase_trace_cancellation_max"] for v in a["records"]),
            "complete_continued_energy_first_norm": a["complete_continued_energy_first_norm"],
            "internal_operator_energy_action_explicitly_held_zero": a["internal_operator_energy_action_explicitly_held_zero"],
            "external_trace_kind": "Complete initial-data Cauchy columns, not selected physical frequency bands",
        }

    forced = read("artifacts/muon_unsquared_forced_boundary_attachment_20261012/run_1/result.json")
    mag = read("artifacts/muon_inherited_magnetic_pure_trace_20261012/run_1/result.json")
    result = {
        "classification": "EVALUATED_SMALL_RETAINED_UNSQUARED_POLE_NULL_RESIDUE_AND_ENERGY_OWNER_CHECK",
        "guard": GUARD, "d5_candidate_checks": d5,
        "d5_background_scope": {
            "source": md["source"],
            "scope": "Two actual current-candidate geometry/normal/material stages; fixed-Y intrinsic seam once; homogeneous n0 trace, full four C6 complement retained. No stationary/vacuum/retarded exterior or physical rest-frame spin degeneracy has been selected.",
            "energy_ownership": "Full finite original radial K0+E KE is Schur reduced at the stored E; Gamma_E includes differentiated inverses. This is genuine declared finite-action spectral dependence, distinct from the source-only envelope energy used below.",
            "no_new_root_or_trace_center_polishing": True,
            "no_conclusion_that_spin_splitting_is_arithmetic": True,
        },
        "birth_envelope_owner_check": birth_check,
        "finite_IVP_pole_countercheck": finite,
        "saved_complete_Cauchy_energy_cancellation": cauchy,
        "forced_unsquared_source_scope": {
            "energy_contact": forced["energy_contact"],
            "full_internal_operator_energy_or_magnetic_derivative_evaluated": forced["full_internal_operator_energy_or_magnetic_derivative_evaluated"],
            "physical_exterior_maps_selected": False,
        },
        "smallest_missing_exterior_germ": {
            "owner": "Action-tail/stop allowed-trace frame and its annihilator on the same full canonical trace, including current-candidate sigma-flow/normal-density and actual retarded field tail/relative transmission",
            "uncomputed_numeric_maps": ["Bi(E), Bf(E)", "Bi_E(E), Bf_E(E)", "actual full-domain U_E(E), if not exhausted by the declared envelope clock", "compatible right/left null traces R,L and nonzero Z=L Gamma_E R"],
            "pole_equation": "Gamma(E)=Bi(E)+Bf(E)U(E); Gamma R=0; L Gamma=0",
            "minimal_reached_right_application": "Bi R + Bf(UR), and Bi_E R+Bf_E(UR)+Bf(U_E R)",
            "minimal_residue_pairing": "Z=L[Bi_E R+Bf_E(UR)+Bf(U_E R)]",
            "source_extension_if_source_amplitude_is_requested": "f=b-Bf r and f_E=b_E-Bf_E r-Bf r_E, retaining the separately evaluated forced unsquared return once",
            "magnetic_extension": mag["physical_Gamma_B_relation"],
            "reduction_limit": "Evaluating the exterior operator only on reached right/dual trace columns can avoid a dense exterior inverse. Null-space selection and a range-complement certificate are still required; an arbitrary pair of Cauchy columns cannot replace physical R,L.",
            "finite_six_row_reduction_limit": "At the stored candidate the original four-complement solve yields exact K=D-C A^-1 B and Z=L Gamma_E R. For a future small exterior variation deltaGamma its directional contribution is deltaK=L deltaGamma R, not a guessed scalar load. A finite exterior change must be composed and the complement resolved, not added as this linearization.",
            "no_physical_boundary_or_missing_jet_defaulted_to_zero": True,
        },
        "physical_status": {"physical_Gamma_with_selected_exterior_available": False,
                            "physical_muon_pole_or_residue": None, "physical_a_mu": None,
                            "physical_corrections_applied": 0,
                            "why_pole_inference_fails": ["Retained IVP boundary is invertible I and has no pole", "D5 trace-center candidate fails full null and residue rows", "Source-only envelope jets cancel from the physical Cauchy trace", "Actual exterior annihilator and energy jets remain uncomputed"]},
        "repeat_scope": "New small algebraic checks on stored arrays twice; no D5/root/source/history campaign repeated. Binary64 point checks do not enclose upstream coefficient/domain errors.",
        "input_hashes": pins,
        "producer_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    for relative, pin in pins.items():
        assert sha256((REPO/relative).read_bytes()).hexdigest() == pin["sha256"]
    text = json.dumps(encode(result), indent=2, sort_keys=True, allow_nan=False)+"\n"
    (output/"result.json").write_text(text, encoding="utf-8", newline="\n")
    print(json.dumps({"output": str(output), "result_sha256": sha256(text.encode()).hexdigest(),
                      "full_null_max": max(v["full_right_null_rows_max"] for v in d5),
                      "candidate_residue_null_max": max(v["candidate_residue_right_null_rows_max"] for v in d5),
                      "physical_pole": None}))


if __name__ == "__main__":
    main()
