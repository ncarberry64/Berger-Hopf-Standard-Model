"""Audit the complete E1 operator dependency before claiming state sensitivity.

The replay evaluates exact algebra and retained identities. It does not assign
an absent physical kernel zero, nor select a covariance to repair that absence.
"""
from __future__ import annotations

import argparse
import ast
from hashlib import sha256
import json
from pathlib import Path
import sys

import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
DIRECTORY = "artifacts/muon_birth_covariance_sensitivity_20261008"
STARTING_HEAD = "a6e3ceebb0a9b8322be333c7be116a01ca6b837d"


def canonical_bytes(value):
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf8")


def density_variation_identity():
    """Differentiate the owner's literal overline convention without changing it.

    P=iD and beta are the retained operator and Dirac-adjoint matrix. Symbols
    for P acting on each test spinor keep the two ordered actions independent.
    The compact-test strong kernel uses the BASE-measure formal adjoint.
    """
    w, dw = sp.symbols("w delta_w", real=True)
    beta, dbeta, fdag, g, pg, dpg, pfdag, dpfdag = sp.symbols(
        "beta delta_beta f_dagger g P_g deltaP_g Pf_dagger deltaPf_dagger", commutative=False)
    eps = sp.Symbol("eps", real=True)
    original = w / 2 * (fdag * beta * pg - pfdag * beta * g)
    perturbed = (w + eps * dw) / 2 * (
        fdag * (beta + eps * dbeta) * (pg + eps * dpg)
        - (pfdag + eps * dpfdag) * (beta + eps * dbeta) * g)
    derivative = sp.expand(perturbed).coeff(eps, 1)
    separated = dw * original / w + w / 2 * (
        fdag * dbeta * pg + fdag * beta * dpg
        - dpfdag * beta * g - pfdag * dbeta * g)
    residual = sp.expand(derivative - separated)
    if residual != 0:
        raise ValueError("Symmetric Dirac density product rule failed")
    return dict(
        classification="DERIVED_FORMAL_FIXED_FIELD_DENSITY_IDENTITY",
        residual=str(residual), includes_measure=True, includes_symbol=True,
        includes_spin_and_gauge_connection=True, includes_mass_Higgs_variation=True,
        delta_density=str(sp.expand(separated)),
        normalized_formula="delta S_D=1/2 integral mu [f^dagger((b beta+delta_beta)P+beta delta_P)g-(Pf)^dagger(b beta+delta_beta)g-(delta_P f)^dagger beta g]",
        compact_test_strong_kernel="K_v=1/2[(b beta+delta_beta)P+beta delta_P-P^dagger_mu(b beta+delta_beta)-delta_P^dagger_mu beta]",
        measure_ordering="b=delta(mu)/mu; multiplication b remains inside P^dagger_mu, including its derivatives",
        kinetic_operator_variation="delta_P=i delta_gamma^M nabla_M+i gamma^M delta_Omega_M; delta_Omega includes spin and the adopted gauge connection",
        separate_Yukawa_variation="K_v,Y=-(b beta M_H+delta_beta M_H+beta delta_M_H), from the separate additive AE3.1 Yukawa owner. Absorption into P requires a proved action-to-operator equivalence; it is not inferred from the Hermitian chiral mass template",
        spin_connection_jet="d delta_e^A+delta_omega^A_B wedge e^B+omega^A_B wedge delta_e^B=0, with antisymmetry",
        boundary_and_domain_terms_dropped=False,
        boundary_terms_in_bulk_formula=False,
        required_domain_variation="Gamma0_child delta_Psi_child=U_R Gamma0_event delta_Psi_event+(delta_U_R) Gamma0_event Psi_event+U_R(delta_Gamma0_event)Psi_event-(delta_Gamma0_child)Psi_child",
        moving_interface="Reynolds surface term or equivalent pulled-back Lie derivatives, booked once",
        actual_E1_coefficients_evaluated=False,
    )


def source_records():
    """Bind symbols used in the dependency proof to exact current source bytes."""
    definitions = {
        "src/bhsm/interface/action_extension_global_spin_reset_ae2.py": ["action_definition"],
        "src/bhsm/interface/ae31_c2_intrinsic_m4_lepton_action.py": ["action_composition_contract", "first_variation_and_pole_gate"],
        "src/bhsm/interface/ae31_c2_chiral_green_domain.py": ["chiral_operator_assembly"],
        "src/bhsm/interface/ae3_reciprocal_join_localization.py": ["interface_variation_ledger"],
        "src/bhsm/interface/ae4_c2_stratified_event_flux_assembly.py": ["solve_retarded_event_kkt", "canonical_noether_flux_balance"],
        "src/bhsm/interface/ae4_event_response_jet_integration.py": ["solve_retarded_event_kkt_jet", "canonical_noether_flux_balance_jet"],
        "src/bhsm/interface/muon_parent_source_contact.py": ["cut_metric_dirac_actions"],
        "src/bhsm/interface/ae31_c2_fermion_hadamard_state_class.py": ["cauchy_covariance_selection_contract"],
        "src/bhsm/interface/arb_heat_pencil_contractions.py": ["HeatPencil"],
        "src/bhsm/interface/completion/foundational_dirac_spin_glue_v14_45.py": ["foundational_action_payload"],
        "src/bhsm/interface/ae4_stratified_dirac_zeta_induced_owner.py": ["microscopic_owner_contract"],
        "src/bhsm/interface/ae32_c2_einstein_cartan_lr_action.py": ["action_completion_contract", "claim_boundary"],
        "src/bhsm/interface/ae31_c2_gauge_composite_hs_action.py": ["action_owned_gauge_hs_contract", "current_c2_domain_and_trace_transport"],
    }
    records = []
    for path, symbols in definitions.items():
        raw = (ROOT / path).read_bytes()
        nodes = list(ast.walk(ast.parse(raw.decode("utf8"))))
        for symbol in symbols:
            found = [node for node in nodes if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name == symbol]
            if len(found) != 1:
                raise ValueError("Source citation missing or ambiguous: " + path + ":" + symbol)
            node = found[0]
            records.append(dict(path=path, raw_sha256=sha256(raw).hexdigest(),
                symbol=symbol, lines=[node.lineno, node.end_lineno]))
    return records


def report():
    receipt_path = DIRECTORY + "/operator_owner_receipt.json"
    owner = json.loads((ROOT / receipt_path).read_text(encoding="utf8"))
    prior_path = "artifacts/muon_birth_fermion_state_representation_20261008/run_1/fermion_state_representation.json"
    prior = json.loads((ROOT / prior_path).read_text(encoding="utf8"))
    return dict(
        classification="EXACT_CAR_SENSITIVITY_QUOTIENT_DERIVED__COMPLETE_E1_OPERATOR_UNEVALUATED",
        starting_head=STARTING_HEAD,
        scientific_reference="524ed90689bd5923c249bba2e699abf627e703cd",
        branch="codex/muon-parent-maxwell-density-review",
        common_event="C1_branch23_E1_minus_to_C2_branch24_E1_plus",
        convention=prior["convention"],
        complete_operator_owner_receipt=owner,
        excluded_quartic_candidate=dict(
            AE4_predecessor="BHSM-AE-3.1.0",
            AE32_EC_globally_promoted=False,
            EC_quartic_silently_added_to_retained_birth=False,
            retained_gauge_HS_interactions_erased=False,
            affine_scope="Uneliminated fixed supplied auxiliary background; eliminating fields or self-consistent induced response is not automatically affine in C",
        ),
        density_derivation=density_variation_identity(),
        canonical_row=dict(
            G="(H_cc^R)^(-1)", H_eff="H_pp-H_pc G H_cp",
            E="H_eff q+J+C_response^dagger lambda",
            D_H_eff="D H_pp-(D H_pc)G H_cp-H_pc G(D H_cp)+H_pc G(D H_cc^R)G H_cp",
            D_E="(D H_eff)q+H_eff Dq+DJ+(D C_response)^dagger lambda+C_response^dagger Dlambda",
            Noether="2 Re <Tq,E>",
            D_Noether="2 Re <D(Tq),E>+2 Re <Tq,D E>",
            Noether_is_contraction_not_additional_action=True,
            contacts_booked_once_in_canonical_row=True,
            on_shell_solution_is_not_uniform_CAR_kernel_identity=True,
        ),
        covariance_sensitivity=dict(
            ordered_particle_row="B_alpha[C]-B_alpha[C_ref]=-Tr((C_plus-C_plus_ref) K_alpha)",
            derivative="D_C B_alpha[X]=-Tr(X K_alpha)",
            scope="Relative smooth/smeared differences at one supplied fixed sourced background/domain; no absolute Wick subtraction",
            pulled_back_K="K_event+U_R^dagger K_child_oriented U_R+K_return_source_constraint_domain",
            Delta_C="-K for the ordinary occupation convention; no quantum doubling factor inferred",
            gamma="Gamma=G conjugation; Gamma X Gamma=-X",
            reset="X_child=U_R X_event U_R^dagger; [X_event,U_R]=0 is NOT required",
            projection="S_B=Q_mu E_charge((Herm(Delta_B)-G conjugate(Herm(Delta_B)) G^dagger)/2) Q_mu",
            charged_blocks="In canonical Gamma-swap coordinates and H=Herm(Delta): X=diag(A,-conjugate(A)); K_mu=Pi_mu(H_pp-conjugate(H_hh))Pi_mu",
            paired_projection="In canonical Gamma-swap coordinates: S_B=diag(K_mu/2,-conjugate(K_mu)/2); Re Tr(X Delta)=Tr(A K_mu)",
            general_Gamma="G=[[0,V],[V^T,0]]: lower X=-V^T conjugate(A) conjugate(V); K_mu=Pi_mu(H_pp-V conjugate(H_hh)V^dagger)Pi_mu",
            iff_scope="All admissible finite affine mixed-interior tangents in normalized CAR coordinates, with commuting symmetry projections",
            minimal_moment_count="dim_R span{projected particle kernels of independent consumed rows}",
            minimal_moment_count_is_operator_rank=False,
            no_fixed_charge_expectation_or_pure_state_assumed=True,
            pure_state_caveat="Local pure projection C S(I-C)+(I-C)S C can vanish at one C without global state independence",
            continuum_caveat="Relative smoothing contractions need an owned domain; finite zero alone does not certify continuum tails",
        ),
        physical_values=dict(
            physical_operator_status="UNDETERMINED_OPERATOR",
            Delta_Green=0, Delta_internal_EM_normal_flux=0,
            independent_fermion_reset_density=0,
            Delta_stress=None, Delta_Noether=None, Delta_contacts=None,
            total_Delta_B=None, S_B=None, physical_operator_rank=None,
            consumed_moment_span_dimension=None, minimal_state_moments=None,
            outcome_A_state_independent=None, outcome_B_state_sensitive=None,
            complete_physical_birth_identified=False,
        ),
        dependency_result=dict(
            actual_question_answered=False,
            exact_first_unpopulated_operand="K_E1,alpha^complete: the one-sided full action-variation kernel on the reset-pulled common CAR domain, with returned-child/source/constraint/domain contacts for each independent consumed PEI06/PEI07 row",
            selected_covariance_is_proven_birth_blocker=False,
            covariance_selection_can_replace_missing_operator=False,
            reason="Projection is linear in the COMPLETE kernel. Exact zeros of two summands and a conditional solved KKT residual fix neither that kernel nor its projection.",
            unknown_kernel_assigned_zero=False,
            nonzero_old_probe_promoted_to_physical_sensitivity=False,
            new_independent_seam_or_action_added=False,
        ),
        heat_and_downstream=dict(
            fixed_complete_sourced_HeatPencil_has_independent_C_operand=False,
            covariance_uncertainty_automatically_propagated_to_heat=False,
            physical_birth_promoted=False,
            mechanical_mode=None, full_inertia=None, xi_psi=None,
            seven_port=None, physical_KKT=None, six_derivatives=None,
            h_psi=None, z_psi=None, r_i_jets=None, physical_cutoff=None,
            AE4_heat=None, relative_zeta_eta=None, R_ind=None,
            native_photon=None, paired_heat=None, Pauli=None,
        ),
        claim_statuses=dict(
            DERIVED="Full affine CAR dual projection, minimal independent moment span, symmetric Dirac density product rule and complete canonical-row derivative; conditional on supplied kernels",
            EVALUATED="Exact symbolic density residual and source/hash/line scope audit; frozen zero identities read without recomputation",
            CONTROL_ONLY="Exact finite matrices in focused tests verify the entire supplied tangent space; none is an E1 physical kernel or selected state",
            UNEVALUATED="Actual complete E1 row kernels, their projected sensitivity/rank/moments, full physical birth and downstream quantities",
            OWNER_DEFINITION_GAP="None asserted by this audit; existing theory/action/composition owners are defined",
            UNDETERMINED_OPERATOR="Complete same-E1 physical directional row-kernel values remain unpopulated in the inspected producers; no impossibility of deriving them is claimed",
        ),
        source_references=source_records(),
        frozen_calculations_recomputed=0,
        selected_covariances=0,
    )


def materialize(output):
    value = report()
    paths = {ref["path"] for ref in value["source_references"]}
    def collect(item):
        if isinstance(item, dict):
            path = item.get("path", item.get("source_path"))
            if path and (item.get("raw_sha256") or item.get("sha256")):
                paths.add(path)
            for child in item.values():
                collect(child)
        elif isinstance(item, list):
            for child in item:
                collect(child)
    collect(value)
    paths.update((
        "src/bhsm/interface/muon_birth_covariance_sensitivity.py",
        "tests/test_muon_birth_covariance_sensitivity.py",
        "scripts/replay_muon_birth_covariance_sensitivity.py",
        "theory/muon_birth_covariance_sensitivity_20261008.md",
        DIRECTORY + "/operator_owner_receipt.json",
        "artifacts/muon_birth_fermion_state_representation_20261008/run_1/fermion_state_representation.json",
        "artifacts/muon_birth_transfer_value_20261008/run_1/transfer_value.json",
        "artifacts/flagship_integration/BHSM_N12_C2_REFINED_RESET_ROOT_CENTER.npz",
    ))
    sources = []
    for path in sorted(paths):
        raw = (ROOT / path).read_bytes()
        sources.append(dict(path=path, bytes=len(raw), raw_sha256=sha256(raw).hexdigest()))
    frozen = {
        "artifacts/muon_birth_transfer_value_20261008/run_1/transfer_value.json": "c351215d0218f1acfc74b0c6d818975e460d694fd1ca5234aad6f3c1f0b24a09",
        "artifacts/flagship_integration/BHSM_N12_C2_REFINED_RESET_ROOT_CENTER.npz": "59dd88661b15cbeec96bc19294f9d9c64f754cccbfbc385c32329fa9c864a8fe",
    }
    for path, expected in frozen.items():
        if sha256((ROOT / path).read_bytes()).hexdigest() != expected:
            raise ValueError("Frozen E1 input changed: " + path)
    # Verify independent receipt references as well; never trust stale line bounds.
    def verify(item):
        if isinstance(item, dict):
            path = item.get("path", item.get("source_path"))
            digest = item.get("raw_sha256", item.get("sha256"))
            if path and digest:
                if not (ROOT / path).is_file():
                    raise ValueError("Retained source missing: " + path)
                raw = (ROOT / path).read_bytes()
                if digest not in {sha256(raw).hexdigest(), sha256(raw.replace(b"\r\n", b"\n")).hexdigest()}:
                    raise ValueError("Retained identity changed: " + path)
                if item.get("symbol") and item.get("lines"):
                    nodes = ast.walk(ast.parse(raw.decode("utf8")))
                    spans = [(n.lineno, n.end_lineno) for n in nodes if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name == item["symbol"]]
                    if tuple(item["lines"]) not in spans:
                        raise ValueError("Retained citation changed: " + path + ":" + item["symbol"])
                if item.get("symbols"):
                    nodes = list(ast.walk(ast.parse(raw.decode("utf8"))))
                    for symbol, bounds in item["symbols"].items():
                        spans = [(n.lineno, n.end_lineno) for n in nodes if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name == symbol]
                        if tuple(bounds) not in spans:
                            raise ValueError("Retained receipt citation changed: " + path + ":" + symbol)
                for bounds in item.get("md_spans", {}).values():
                    if not 1 <= bounds[0] <= bounds[1] <= len(raw.decode("utf8").splitlines()):
                        raise ValueError("Retained Markdown citation out of bounds: " + path)
            for child in item.values():
                verify(child)
        elif isinstance(item, list):
            for child in item:
                verify(child)
    verify(value)
    manifest = dict(classification="COMPLETE_E1_OPERATOR_DEPENDENCY_AUDIT", sources=sources,
                    physical_kernel_supplied=False, physical_sensitivity_evaluated=False)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    products = {}
    for name, content in (("covariance_sensitivity.json", value), ("source_manifest.json", manifest)):
        data = canonical_bytes(content)
        (output / name).write_bytes(data)
        products[name] = dict(bytes=len(data), sha256=sha256(data).hexdigest())
    (output / "output_hashes.json").write_bytes(canonical_bytes(products))
    return dict(audit_passed=True, products=products, actual_question_answered=False,
                physical_S_B=None, selected_covariances=0, sources=len(sources))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    print(json.dumps(materialize(parser.parse_args().out), sort_keys=True))


if __name__ == "__main__":
    main()
