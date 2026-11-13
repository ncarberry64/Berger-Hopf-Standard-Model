"""Replay the additive C1 LR reduction without selecting physical operands.

The immutable imported companion is checked, not regenerated. New exact
contractions use explicitly marked controls. The point-valued E1 guard stays
in its original module, and all physical missing entries remain null.
"""
from __future__ import annotations

import argparse
import ast
from fractions import Fraction
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
BASELINE = "ad750077f1a3138418a2dc4ee65f7c50236b5608"
PRE_CAR = "a6e3ceebb0a9b8322be333c7be116a01ca6b837d"
ARTIFACT = "artifacts/muon_birth_c1_lr_response_20261008"
EXPECTED_COMPANION_SHA = "269452297e37de4d19450413d8422e281ae2402cef52acd4a4d811083ddffcf0"


def canonical_bytes(value):
    def exact(item):
        if isinstance(item, (sp.MatrixBase, sp.Basic, Fraction)):
            return str(item)
        raise TypeError(type(item).__name__)
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False,
                       allow_nan=False, default=exact) + "\n").encode("utf8")


def reference(root, path):
    raw = (root / path).read_bytes()
    return dict(path=path, bytes=len(raw), raw_sha256=sha256(raw).hexdigest())


def verify_receipt_sources(root, receipt):
    """Bind each retained claim to its source bytes and exact symbol spans."""
    verified = {}
    def walk(item):
        if isinstance(item, dict):
            path, digest = item.get("path"), item.get("raw_sha256")
            if path and digest:
                raw = (root / path).read_bytes()
                lf = raw.replace(b"\r\n", b"\n")
                variants = (raw, lf, lf.replace(b"\n", b"\r\n"))
                if not any(sha256(candidate).hexdigest() == digest for candidate in variants):
                    raise ValueError("Retained claim source changed: " + path)
                if item.get("symbols"):
                    nodes = list(ast.walk(ast.parse(raw.decode("utf8"))))
                    symbols = item["symbols"]
                    pairs = (symbols.items() if isinstance(symbols, dict) else
                             [(row["symbol"], [row["start_line"], row["end_line"]]) for row in symbols])
                    for name, span in pairs:
                        choices = [node for node in nodes if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name == name]
                        if len(choices) != 1 or [choices[0].lineno, choices[0].end_lineno] != span:
                            raise ValueError("Retained claim symbol changed: " + path + ":" + name)
                verified[path] = reference(root, path)
            for child in item.values():
                walk(child)
        elif isinstance(item, list):
            for child in item:
                walk(child)
    walk(receipt)
    return [verified[path] for path in sorted(verified)]


def verify_package_bytes(package):
    manifest = json.loads((package / "artifact_manifest.json").read_text())
    for row in manifest["files"]:
        raw = (package / row["path"]).read_bytes()
        if len(raw) != row["bytes"] or sha256(raw).hexdigest() != row["sha256"]:
            raise ValueError("Imported companion changed: " + row["path"])
    if (package / "run_1/results.json").read_bytes() != (package / "run_2/results.json").read_bytes():
        raise ValueError("Inherited companion replays differ")
    raw = (package / "run_1/results.json").read_bytes()
    if sha256(raw).hexdigest() != EXPECTED_COMPANION_SHA:
        raise ValueError("Inherited companion result hash differs")
    return json.loads(raw)


def validated_companion_result(root):
    package = root / ARTIFACT / "companion"
    packet = verify_package_bytes(package)
    spec = importlib.util.spec_from_file_location("bhsm_frozen_lr_source_check", package / "verify_all.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    checked = module.source_crosscheck(packet["new_carrier_bounds"], root)
    if checked != packet["source_verification"]:
        raise ValueError("Inherited source check differs")
    return packet


def preserved_milestones(root):
    command = ["git", "-c", "gc.auto=0", "-c", "maintenance.auto=false"]
    paths = subprocess.check_output(command + ["diff", "--name-only", PRE_CAR, BASELINE], cwd=root, text=True).splitlines()
    records = []
    for path in paths:
        expected = subprocess.check_output(command + ["show", BASELINE + ":" + path], cwd=root)
        raw = (root / path).read_bytes()
        normalized = raw.replace(b"\r\n", b"\n")
        if expected not in (raw, normalized, normalized.replace(b"\n", b"\r\n")):
            raise ValueError("Preserved milestone changed: " + path)
        records.append(reference(root, path))
    if len(records) != 38:
        raise ValueError("Unexpected preservation scope")
    return records


def exact_contraction_controls():
    from bhsm.interface.muon_birth_c1_lr_scalar_contraction import constrained_scalar_contraction
    a = sp.Matrix([[1, 1], [0, 0]])
    f = sp.Matrix([2, 0])
    unique = constrained_scalar_contraction(a, f, sp.Matrix([1, 1]))
    ambiguous = constrained_scalar_contraction(a, f, sp.Matrix([1, 0]))
    return dict(classification="CONTROL_ONLY", augmented_response_operator=a,
                compatible_forcing=f, consumed_unique=unique,
                supplied_nullspace_detects_ambiguity=ambiguous,
                physical_C1_nullspace_or_underdetermination_claimed=False)


def materialize(output, root=ROOT):
    from bhsm.interface.muon_birth_fermion_event_kkt_inputs import physical_input_packet
    from bhsm.interface.muon_birth_c1_lr_form_response import (
        exact_lr_symbol_identity, exact_squared_form_and_conormal_identity)
    from bhsm.interface.muon_birth_parametric_fermion_seam import fraction_record
    root = Path(root)
    imported = validated_companion_result(root)
    point = physical_input_packet(root)
    owner = json.loads((root / ARTIFACT / "incoming_source_domain_receipt.json").read_text())
    embedding = json.loads((root / ARTIFACT / "lr_embedding_receipt.json").read_text())
    retained_sources = verify_receipt_sources(root, [owner, embedding])
    values = imported["new_carrier_bounds"]["values"]
    t = Fraction(values["T_star"]["exact_fraction"])
    st = Fraction(values["S_T_star"]["exact_fraction"])
    coefficient = Fraction(values["effective_a_upper"]["exact_fraction"])
    lift_length = t / (Fraction(3, 2) - st)
    form_thresholds = dict(
        classification="EVALUATED_CONDITIONAL_SAME_FACTOR_FORM_CRITERION",
        one_end_form_L2_to_energy_length=fraction_record(lift_length),
        sufficient_insertion_norm_upper=fraction_record(Fraction(2, 5)/lift_length),
        sufficient_lambda_squared_insertion_norm_upper=fraction_record(Fraction(2, 5)*(Fraction(3, 2)-st)/coefficient),
        criterion="w=ell*||E||<=2/5 implies eta=2w+w^2<=24/25<1; use the full one-end trace domain and the verified factor insertion",
        inverse_seam_conclusion="||S_full^-1||<=25*b_star for the same nonnegative child load under this sufficient condition",
        physical_factor_insertion_norm=None, physical_norm_enclosure_evaluated=False)
    packet = dict(
        schema="BHSM_MUON_BIRTH_C1_LR_RESPONSE_CONTINUATION_V1",
        baseline=BASELINE,
        domain=point["domain"],
        carrier_bounds=imported["new_carrier_bounds"],
        imported_companion=dict(exact_checks=43, pinned_sources=43,
                                original_result_sha256=EXPECTED_COMPANION_SHA,
                                original_evidence_reused=True, old_producers_recomputed=False),
        incoming_source_domain=owner, lr_embedding=embedding,
        exact_mass_partner_and_positive_symbol=exact_lr_symbol_identity(),
        exact_squared_form_and_conormal=exact_squared_form_and_conormal_identity(),
        conditional_form_thresholds=form_thresholds,
        constrained_contraction_controls=exact_contraction_controls(),
        consumed_parent_LR_response=dict(
            definition="R_LR=E_0,L^dagger (L_full-L_car) E_1,R; in carrier coordinates W-V_bi(A_0+V_ii)^(-1)V_ib; include action-owned boundary contacts",
            value=None, enclosure=None, exact_zero_proved=False,
            required_base_contractions=["W=E_0,L^dagger V E_0,R", "V_bi=E_0,L^dagger V J_i", "V_ib=J_i^dagger V E_0,R", "V_ii=J_i^dagger V J_i"],
            contraction_guard="These are consumed pairings only after V is bound to the actual full-minus-carrier quadratic action/domain. The cancelling algebraic partner or raw local mass cannot fill these slots; whole matrices are not required if the readout pairings are enclosed directly.",
            derivative="D_alpha Lambda=E_L^dagger (D_alpha L) E_R, with all three moving-pullback terms and scalar adjoint/source/boundary forcing",
            scalar_consumed_response="ell_alpha(h_alpha)=Re <p_alpha,f_alpha>, A_H^*p_alpha=ell_alpha on the existing augmented real-linear retarded domain",
            scalar_mixed_kernel="L_xC-[L_xh,R_x^dagger] K_H^(-1) [L_hC;R_C] where K_H=[[L_hh,R_h^dagger],[R_h,0]]; only on justified inverse/quotient",
            no_constraint_or_source_contact_dropped=True),
        solver_inputs=point["solver_inputs"], first_unavailable=point["first_unavailable"],
        physical_status=dict(actual_incoming_LR_response_enclosed=False,
            scalar_contraction=None, complete_E1_kernel=None,
            complete_CAR_verdict=None, minimal_physical_moment_rank=None,
            physical_a_mu=None, physical_g_mu=None,
            physical_C1_underdetermination_proved=False,
            physical_member_selection_proved_necessary=False,
            physical_member_or_covariance_selected=False,
            point_KKT_callback_called=False, point_noether_callback_called=False),
        independent_E1_contacts=["oriented metric/interface action rows", "parent and returned-child canonical traction", "explicit source", "response multiplier and constraint domain", "moving trace/measure/frame/domain", "separately consumed integrated Hamiltonian"],
        claims=dict(DERIVED="Actual local Euler mass-partner/adjoint distinction; constrained consumed-response and mixed-KKT identities; conditional form enclosure",
            EVALUATED="Exact imported carrier constants and source/hash checks; exact local symbol identity",
            CONTROL_ONLY="Supplied finite constrained-response, nonlinear-constraint and omitted-contact checks",
            UNEVALUATED="Actual incoming LR response contractions; complete E1/CAR/moment span and normalized physical Pauli readout",
            OWNER_DEFINITION_GAP=[]))
    preserved = preserved_milestones(root)
    paths = [
        "scripts/replay_muon_birth_c1_lr_response.py",
        "src/bhsm/interface/muon_birth_c1_lr_form_response.py",
        "src/bhsm/interface/muon_birth_c1_lr_scalar_contraction.py",
        "tests/test_muon_birth_c1_lr_form_response.py",
        "tests/test_muon_birth_c1_lr_scalar_contraction.py",
        "tests/test_muon_birth_c1_lr_replay.py",
        "theory/muon_birth_c1_lr_response_20261008.md",
        ARTIFACT + "/incoming_source_domain_receipt.json",
        ARTIFACT + "/lr_embedding_receipt.json",
        ARTIFACT + "/companion/artifact_manifest.json",
        ARTIFACT + "/companion/.gitattributes",
        ARTIFACT + "/companion/pinned_source_manifest.json",
    ]
    manifest = dict(baseline=BASELINE, source_records=[reference(root, p) for p in paths],
                    retained_claim_sources=retained_sources,
                    preserved_milestones=preserved, preserved_count=len(preserved))
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    hashes = {}
    for name, value in (("c1_lr_response.json", packet), ("source_manifest.json", manifest)):
        raw = canonical_bytes(value)
        (output / name).write_bytes(raw)
        hashes[name] = dict(bytes=len(raw), sha256=sha256(raw).hexdigest())
    (output / "output_hashes.json").write_bytes(canonical_bytes(hashes))
    return dict(audit_passed=True, products=hashes, imported_exact_checks=43,
                imported_pinned_sources=43, preserved_milestone_files=len(preserved),
                first_unavailable=point["first_unavailable"],
                actual_LR_enclosure=False, complete_CAR_verdict=None,
                physical_underdetermination_proved=False, physical_member_selected=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    print(json.dumps(materialize(parser.parse_args().out), sort_keys=True))
