"""Materialize normalized incoming carrier entries without filling physical P_F.

Reuses published carrier inequalities, form/contact proofs and source checks.
No old producer, KKT solve, covariance selector or physical branch is run.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
BASELINE = "a51a2026c7080f98d64c8566ac193b3792ac0427"
PRE_CAR = "a6e3ceebb0a9b8322be333c7be116a01ca6b837d"
ARTIFACT = "artifacts/muon_birth_incoming_parent_trace_response_20261008"

spec = importlib.util.spec_from_file_location(
    "published_c1_lr_replay", ROOT / "scripts/replay_muon_birth_c1_lr_response.py")
PUBLISHED = importlib.util.module_from_spec(spec)
spec.loader.exec_module(PUBLISHED)


def preserved_milestones(root=ROOT):
    """Verify all 72 CAR, guard, carrier and a51 milestone paths unchanged."""
    git = ["git", "-c", "gc.auto=0", "-c", "maintenance.auto=false"]
    paths = subprocess.check_output(
        git + ["diff", "--name-only", PRE_CAR, BASELINE], cwd=root, text=True).splitlines()
    records = []
    for path in paths:
        expected = subprocess.check_output(git + ["show", BASELINE + ":" + path], cwd=root)
        raw = (Path(root) / path).read_bytes()
        lf = raw.replace(b"\r\n", b"\n")
        if expected not in (raw, lf, lf.replace(b"\n", b"\r\n")):
            raise ValueError("Published milestone changed: " + path)
        records.append(PUBLISHED.reference(Path(root), path))
    if len(records) != 72:
        raise ValueError("Unexpected published milestone preservation scope")
    return records


def materialize(output, root=ROOT):
    from bhsm.interface.muon_birth_fermion_event_kkt_inputs import physical_input_packet
    from bhsm.interface.muon_birth_incoming_parent_trace_response import incoming_parent_trace_packet

    root = Path(root)
    imported = PUBLISHED.validated_companion_result(root)
    point = physical_input_packet(root)
    primal = json.loads((root / ARTIFACT / "incoming_lr_primal_receipt.json").read_text(encoding="utf8"))
    packet = incoming_parent_trace_packet(root)
    packet["incoming_lr_primal_receipt"] = primal
    packet["preserved_point_inputs"] = dict(
        solver_inputs=point["solver_inputs"], first_unavailable=point["first_unavailable"],
        point_guard_modified=False, point_KKT_callback_called=False,
        point_noether_callback_called=False)
    packet["reused_verification"] = dict(
        imported_exact_checks=imported["exact_control_groups_passed"],
        imported_source_checks=imported["source_verification"]["pinned_source_files_verified"],
        original_companion_result_sha256=PUBLISHED.EXPECTED_COMPANION_SHA,
        old_producers_recomputed=False,
        positive_square_form_and_constrained_adjoint_milestone=BASELINE)
    packet["classifications"] = dict(
        DERIVED="Inherited trace normalization, shell multiplicity, carrier operator action and entire-KKT reduction contract",
        EVALUATED="160 shared-family scaled carrier diagonal enclosures; 25440 ordered exact carrier off-diagonal zeros; source identities",
        CONTROL_ONLY="Clifford frame checks and non-Hermitian omitted-constraint-reaction counterexample",
        UNEVALUATED="Actual incoming LR base RHS/paired form and full P_F order0; all six physical solver tuples and complete E1/CAR result",
        OWNER_DEFINITION_GAP=[])
    sources = PUBLISHED.verify_receipt_sources(root, [primal, packet["source_records"]])
    paths = [
        "scripts/replay_muon_birth_incoming_parent_trace_response.py",
        "src/bhsm/interface/muon_birth_incoming_parent_trace_response.py",
        "tests/test_muon_birth_incoming_parent_trace_response.py",
        "tests/test_muon_birth_incoming_parent_trace_replay.py",
        "theory/muon_birth_incoming_parent_trace_response_20261008.md",
        ARTIFACT + "/incoming_lr_primal_receipt.json",
        ARTIFACT + "/.gitattributes",
    ]
    manifest = dict(
        baseline=BASELINE, source_records=[PUBLISHED.reference(root, p) for p in paths],
        retained_primal_claim_sources=sources,
        published_milestone_records=preserved_milestones(root), preserved_count=72)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    hashes = {}
    for name, value in (("incoming_parent_trace_response.json", packet),
                        ("source_manifest.json", manifest)):
        raw = PUBLISHED.canonical_bytes(value)
        (output / name).write_bytes(raw)
        hashes[name] = dict(bytes=len(raw), sha256=sha256(raw).hexdigest())
    (output / "output_hashes.json").write_bytes(PUBLISHED.canonical_bytes(hashes))
    return dict(audit_passed=True, products=hashes, preserved_milestone_files=72,
                reused_exact_controls=43, reused_pinned_sources=43,
                first_unavailable=point["first_unavailable"],
                physical_parent_point_value=None, physical_LR_enclosure=None,
                complete_E1_CAR_verdict=None)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    print(json.dumps(materialize(parser.parse_args().out), sort_keys=True))
