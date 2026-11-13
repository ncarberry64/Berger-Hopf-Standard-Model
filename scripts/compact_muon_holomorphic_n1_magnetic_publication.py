"""Additive compact publication selection for the frozen causal D3S pair.

The original full member manifest remains the immutable replay/hash list.
This script changes publication membership only; no action is recomputed.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "artifacts/muon_holomorphic_n1_magnetic_operands_20261012"
FULL_MANIFEST = BASE + "/pair_verification_outgoing_normal_basis_area_source/publication_manifest.json"
FULL_SHA256 = "333b110fbe7e13108d870054972275e74d68c67225a150e507c7feabcea19054"
CASES = ("normal_basis", "area_source")
COMPACT_OUTPUTS = (
    "result.json", "same_action_maps_and_trials.npz",
    "classical_mixed_action_and_source.npz",
    "same_prefix_existing_unsquared_current_terms.npz",
)

# Explicit dependency closure of the reviewed selection snapshot. The other
# input pins are unchanged tracked checkout inputs, rather than newly selected
# scientific outputs. This fixed list does not depend on later Git staging.
INPUT_CLOSURE = (
    "artifacts/muon_changing_canonical_source_20261012/run_3/outgoing_0000_area_source_source_response.npz",
    "artifacts/muon_changing_canonical_source_20261012/run_3/outgoing_0000_normal_basis_source_response.npz",
    "artifacts/muon_changing_canonical_source_20261012/run_3/outgoing_0001_area_source_source_response.npz",
    "artifacts/muon_changing_canonical_source_20261012/run_3/outgoing_0001_normal_basis_source_response.npz",
    "artifacts/muon_changing_canonical_source_20261012/run_3/result.json",
    "artifacts/muon_holomorphic_n1_magnetic_action_20261012/outgoing_area_source_run_1/actual_zero_Cauchy_magnetic_prefix.npz",
    "artifacts/muon_holomorphic_n1_magnetic_action_20261012/outgoing_area_source_run_1/actual_zero_Cauchy_magnetic_source_points.npz",
    "artifacts/muon_holomorphic_n1_magnetic_action_20261012/outgoing_area_source_run_1/actual_zero_Cauchy_magnetic_unit_EM_current.npz",
    "artifacts/muon_holomorphic_n1_magnetic_action_20261012/outgoing_area_source_run_1/result.json",
    "artifacts/muon_holomorphic_n1_magnetic_action_20261012/outgoing_area_source_run_1/stage_0_actual_magnetic_trace.npz",
    "artifacts/muon_holomorphic_n1_magnetic_action_20261012/outgoing_area_source_run_1/stage_1_actual_magnetic_trace.npz",
    "artifacts/muon_holomorphic_n1_magnetic_action_20261012/outgoing_normal_basis_run_1/actual_zero_Cauchy_magnetic_prefix.npz",
    "artifacts/muon_holomorphic_n1_magnetic_action_20261012/outgoing_normal_basis_run_1/actual_zero_Cauchy_magnetic_source_points.npz",
    "artifacts/muon_holomorphic_n1_magnetic_action_20261012/outgoing_normal_basis_run_1/actual_zero_Cauchy_magnetic_unit_EM_current.npz",
    "artifacts/muon_holomorphic_n1_magnetic_action_20261012/outgoing_normal_basis_run_1/result.json",
    "artifacts/muon_holomorphic_n1_magnetic_action_20261012/outgoing_normal_basis_run_1/stage_0_actual_magnetic_trace.npz",
    "artifacts/muon_holomorphic_n1_magnetic_action_20261012/outgoing_normal_basis_run_1/stage_1_actual_magnetic_trace.npz",
    "scripts/evaluate_muon_holomorphic_n1_magnetic_action.py",
    "scripts/evaluate_muon_holomorphic_n1_magnetic_operands.py",
    "src/bhsm/interface/muon_holomorphic_current_source.py",
    "src/bhsm/interface/muon_holomorphic_em_current.py",
    "src/bhsm/interface/muon_holomorphic_n1_magnetic_action.py",
    "src/bhsm/interface/muon_holomorphic_n1_magnetic_cauchy.py",
    "src/bhsm/interface/muon_holomorphic_n1_magnetic_operand_application.py",
    "src/bhsm/interface/muon_holomorphic_n1_magnetic_operands.py",
    "src/bhsm/interface/muon_literal_wall_magnetic_action.py",
    "tests/test_muon_complex_n1_literal_action.py",
    "tests/test_muon_complex_n1_row_polynomial.py",
    "tests/test_muon_holomorphic_n1_magnetic_action.py",
    "tests/test_muon_holomorphic_n1_magnetic_cauchy.py",
    "tests/test_muon_holomorphic_n1_magnetic_current_first.py",
    "tests/test_muon_holomorphic_n1_magnetic_operand_application.py",
    "tests/test_muon_holomorphic_n1_magnetic_operands.py",
    "tests/test_muon_n1_magnetic_current_independent.py",
)
CAP = 10 * 1024**2


def digest(relative):
    path = (ROOT / relative).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError("publication member escapes the intended checkout")
    data = path.read_bytes()
    return dict(bytes=len(data), sha256=sha256(data).hexdigest())


def write_new(output, name, record):
    folder = (ROOT / output).resolve()
    if not folder.is_relative_to(ROOT) or folder.exists():
        raise ValueError("new additive output folder within the checkout required")
    folder.mkdir(parents=True)
    target = folder / name
    target.write_text(json.dumps(record, sort_keys=True, indent=2, allow_nan=False)
                      + "\n", encoding="utf8", newline="\n")
    return target


def materialize(output):
    full_row = digest(FULL_MANIFEST)
    if full_row["sha256"] != FULL_SHA256:
        raise ValueError("immutable full D3S replay membership changed")
    full = json.loads((ROOT / FULL_MANIFEST).read_bytes())
    if (not full["all_output_bytes_equal"] or len(full["files"]) != 887
            or len(full["input_hashes"]) != 360
            or tuple(full["compact_outputs"]) != COMPACT_OUTPUTS):
        raise ValueError("the reviewed full causal D3S pair is required")

    files = {}

    def add(relative, expected=None):
        row = digest(relative)
        if expected is not None and row["sha256"] != expected:
            raise ValueError("selected frozen member changed: " + relative)
        if row["bytes"] >= CAP:
            raise ValueError("selected file exceeds the individual publication cap")
        files[relative] = row

    # Keep every current input pin, including baseline inputs not restaged.
    for relative, expected in full["input_hashes"].items():
        if digest(relative)["sha256"] != expected:
            raise ValueError("original action/source input pin changed: " + relative)
    pairs = {}
    for case in CASES:
        first_folder = f"{BASE}/outgoing_{case}_run_1"
        second_folder = f"{BASE}/outgoing_{case}_run_2"
        md = json.loads((ROOT / first_folder / "result.json").read_bytes())
        if len(md["archives"]) != 219 or md["source_points"] != 15:
            raise ValueError("complete original dense operator receipt required")
        for name in COMPACT_OUTPUTS:
            first, second = first_folder + "/" + name, second_folder + "/" + name
            add(first, full["files"][first])
            add(second, full["files"][second])
            if (ROOT / first).read_bytes() != (ROOT / second).read_bytes():
                raise ValueError("compact scientific pair bytes differ")
        pairs[case] = dict(compact_outputs_byte_identical=True,
                          result_sha256=files[first_folder + "/result.json"]["sha256"],
                          full_archives_per_execution=219,
                          dense_archives_per_execution_not_selected=216)
    logs = sorted(relative for relative in full["files"]
                  if relative.endswith(".stdout.txt"))
    if len(logs) != 6:
        raise ValueError("all four executed action logs and both control/failure logs required")
    for relative in logs:
        add(relative, full["files"][relative])
    original_verifier = "scripts/verify_muon_holomorphic_n1_magnetic_operands_pair.py"
    add(original_verifier, full["files"][original_verifier])
    for relative in INPUT_CLOSURE:
        if relative not in full["input_hashes"]:
            raise ValueError("explicit closure path lacks an original producer pin")
        add(relative, full["input_hashes"][relative])
    add(FULL_MANIFEST, FULL_SHA256)
    add(Path(__file__).relative_to(ROOT).as_posix())

    retained_original = set(files) & set(full["files"])
    excluded = set(full["files"]) - retained_original
    if len(excluded) != 864 or any(not relative.endswith(".npz") for relative in excluded):
        raise ValueError("only the expected dense local operator archives may be omitted")
    record = dict(
        classification="COMPACT_VERIFIED_CAUSAL_D3S_PUBLICATION_MEMBERSHIP",
        files=files, input_hashes=full["input_hashes"],
        selected_files=len(files), selected_bytes=sum(row["bytes"] for row in files.values()),
        maximum_selected_file_bytes=max(row["bytes"] for row in files.values()),
        original_full_manifest=dict(path=FULL_MANIFEST, **full_row, member_files=887,
            selected_as_hashlist_file_only=True, recursively_expand_membership=False),
        compact_scientific_pairs=pairs, compact_outputs=list(COMPACT_OUTPUTS),
        explicit_dependency_closure_paths=list(INPUT_CLOSURE),
        verified_input_pins=len(full["input_hashes"]),
        remaining_pinned_inputs="unchanged tracked checkout inputs; aggregate publication verifies all pins and closes any untracked inputs",
        scientific_regeneration_commands=full["commands"], environment=full["environment"],
        executed_scientific_logs=logs, applications=full["applications"],
        dense_local_operator_archives_not_selected=864,
        original_raw_scientific_files_modified_or_deleted=False,
        all15_point_and_directed_FE_operator_arrays_remain_local=True,
        each_result_retains_complete_219_archive_hashlist_and_point_records=True,
        all_four_K_BF_BR_M_placements_and_high_low_slots_retained=True,
        classical_mixed_action_free_and_initial_face_sources_retained=True,
        same_prefix_current_source_order_and_contacts_retained=True,
        full_supplied_stage_delta_forms_and_geometry_profile_coframe_complement_owned_by_separate_selected_quadratic_manifest=True,
        numerical_time_measure_held_in_classical_mixed_action=True,
        physical_time_domain_stop_or_exterior_jets_completed=False,
        new_action_evaluation_test_or_precision_refinement_performed=False,
        complete_clean_ancestor_regeneration_proved=False,
        physical_native_loop_pole_or_Pauli_completion_inferred=False,
        immutable_full_verification_not_a_claim_all_members_committed=True,
        scope="publication membership only; frozen causal D3S field-direction application, compact action/source/current and complete pins/hashlists; all scientific limitations and nonconvergent diagnostics unchanged",
    )
    target = write_new(output, "publication_manifest.json", record)
    print(json.dumps(dict(selected_files=len(files), selected_bytes=record["selected_bytes"],
        maximum_file_bytes=record["maximum_selected_file_bytes"], input_pins=360,
        excluded_dense_archives=864, manifest_sha256=sha256(target.read_bytes()).hexdigest())), flush=True)


def verify_pair(first, second, output):
    first = first / "publication_manifest.json"
    second = second / "publication_manifest.json"
    data = (ROOT / first).read_bytes()
    if data != (ROOT / second).read_bytes():
        raise ValueError("independent compact materializations differ")
    record = json.loads(data)
    for relative, expected in record["files"].items():
        if digest(relative) != expected:
            raise ValueError("compact member changed before pair verification")
    for relative, expected in record["input_hashes"].items():
        if digest(relative)["sha256"] != expected:
            raise ValueError("full input pin changed before pair verification")
    logs = [BASE + "/compact_publication_run_" + str(n) + ".stdout.txt" for n in (1, 2)]
    evidence = {path: digest(path) for path in logs}
    if (ROOT / logs[0]).read_bytes() != (ROOT / logs[1]).read_bytes():
        raise ValueError("independent compact command stdout differs")
    evidence[first.as_posix()] = digest(first)
    evidence[second.as_posix()] = digest(second)
    verification = dict(classification="VERIFIED_METADATA_ONLY_COMPACT_D3S_PAIR",
        files=evidence, compact_manifest_sha256=sha256(data).hexdigest(),
        compact_outputs_byte_identical=True, selected_files=record["selected_files"],
        selected_bytes=record["selected_bytes"], verified_input_pins=360,
        commands=[f"C:/Python314/python.exe scripts/compact_muon_holomorphic_n1_magnetic_publication.py --output {p.parent.as_posix()}" for p in (first, second)],
        command_environment="metadata-only Python; no scientific producer or test re-executed",
        original_full_887_member_manifest_sha256=FULL_SHA256,
        raw_scientific_artifacts_preserved=True,
        complete_clean_ancestor_regeneration_proved=False,
        physical_observable_completed=False,
        verification_scope="same metadata membership bytes, compact scientific pair bytes and unchanged all360 producer pins; original full verifier owns dense array replay")
    target = write_new(output, "verification.json", verification)
    print(json.dumps(dict(verification_sha256=sha256(target.read_bytes()).hexdigest(),
        selected_files=record["selected_files"], selected_bytes=record["selected_bytes"],
        manifest_sha256=sha256(data).hexdigest())), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--verify-pair", nargs=2, type=Path)
    args = parser.parse_args()
    if args.verify_pair:
        verify_pair(*args.verify_pair, args.output)
    else:
        materialize(args.output)
