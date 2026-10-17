"""Replay the E1 fermion representation audit; choose no physical covariance."""
from __future__ import annotations
import argparse
import ast
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"src"))
sys.path.insert(0, str(ROOT))

from bhsm.interface.muon_birth_fermion_state_representation import (
    ARTIFACT_DIRECTORY, representation_report,
)
from scripts.audit_ae4_support_loss_classical_realization import canonical_bytes
from scripts.audit_ae4_branch_relative_support_transition import (
    referenced_paths, referenced_records, verify_retained_hashes,
    verify_source_references,
)
from scripts.replay_muon_birth_transfer_value import expanded_citations


def normalized_sources(value):
    """Normalize the independent audit receipts without changing their bytes."""
    refs = []
    if isinstance(value, dict):
        path = value.get("source_path", value.get("path"))
        digest = value.get("raw_sha256", value.get("sha256"))
        if path and digest:
            base = dict(path=path, sha256=digest)
            refs.append(base)
            for row in value.get("symbol_references", []):
                refs.append(dict(**base, symbol=row["symbol"],
                                 lines=[row["start_line"], row["end_line"]]))
            if str(path).endswith(".py"):
                for symbol, bounds in value.get("spans", {}).items():
                    refs.append(dict(**base, symbol=symbol, lines=bounds))
            elif str(path).endswith(".md"):
                spans = list(value.get("spans", {}).values())
                spans.extend([r["start_line"], r["end_line"]]
                             for r in value.get("line_references", []))
                count = len((ROOT/path).read_text(encoding="utf8").splitlines())
                if any(not 1 <= start <= end <= count for start, end in spans):
                    raise ValueError("Markdown citation span changed: "+path)
        for item in value.values():
            refs.extend(normalized_sources(item))
    elif isinstance(value, list):
        for item in value:
            refs.extend(normalized_sources(item))
    return refs


def smooth_response_sources():
    """Bind the retained nonzero charged-lepton vertices and finite-C consumers."""
    definitions = {
        "src/bhsm/interface/ae31_c2_lepton_composite_mixing_structure.py":
            ["shared_charged_lepton_vertex_jet", "one_loop_mixing_factorization"],
        "src/bhsm/interface/ae31_c2_lr_susceptibility_factorization.py":
            ["composite_hessian_decomposition", "exact_remaining_owner"],
        "src/bhsm/interface/ae31_c2_fixed_history_state_nonuniqueness.py":
            ["finite_rank_hadamard_nonuniqueness_theorem", "retained_selector_status"],
        "src/bhsm/interface/ae31_c2_local_em_ward_identity.py":
            ["charged_lepton_qem_ledger"],
        "src/bhsm/interface/arb_heat_pencil_contractions.py":
            ["HeatPencil"],
    }
    refs = []
    for path, symbols in definitions.items():
        raw = (ROOT/path).read_bytes()
        tree = ast.parse(raw.decode("utf8"))
        for symbol in symbols:
            nodes = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.ClassDef))
                     and n.name == symbol]
            if len(nodes) != 1:
                raise ValueError("Missing retained smooth-response source: "+symbol)
            node = nodes[0]
            refs.append(dict(path=path, sha256=sha256(raw).hexdigest(),
                             symbol=symbol, lines=[node.lineno, node.end_lineno]))
    return refs


def materialize(output):
    report = representation_report(ROOT)
    report["normalized_source_references"] = normalized_sources(report)+smooth_response_sources()
    checked, external = verify_retained_hashes(report)
    citations = verify_source_references([report, expanded_citations(report)])
    paths = referenced_paths(report)
    paths.update((
        "src/bhsm/interface/muon_birth_fermion_state_representation.py",
        "scripts/replay_muon_birth_fermion_state_representation.py",
        "tests/test_muon_birth_fermion_state_representation.py",
        "theory/muon_birth_fermion_state_representation_20261008.md",
        ARTIFACT_DIRECTORY+"/owner_state_receipt.json",
        ARTIFACT_DIRECTORY+"/interface_cancellation_receipt.json",
        "artifacts/muon_birth_transfer_value_20261008/run_1/transfer_value.json",
        "artifacts/muon_birth_transfer_value_20261008/run_1/source_manifest.json",
        "artifacts/muon_birth_transfer_value_20261008/verification.json",
    ))
    for module in tuple(sys.modules.values()):
        path = getattr(module, "__file__", None)
        if path:
            file = Path(path).resolve()
            try:
                relative = file.relative_to(ROOT).as_posix()
            except ValueError:
                continue
            if relative.startswith("src/bhsm/") and file.suffix == ".py":
                paths.add(relative)
    identities = []
    for path in sorted(paths):
        file = Path(path)
        if not file.is_absolute():
            file = ROOT/path
        data = file.read_bytes()
        convention = "raw_binary"
        if file.suffix in {".py", ".json", ".md", ".txt"}:
            data = data.replace(b"\r\n", b"\n")
            convention = "canonical_LF_text"
        identities.append(dict(path=path, bytes=len(data),
                               sha256=sha256(data).hexdigest(),
                               hash_convention=convention))
    checked_external = []
    for ref in referenced_records(report):
        file = Path(ref["path"])
        if file.is_absolute() and ref.get("sha256") and file.is_file():
            raw = file.read_bytes()
            canonical = raw.replace(b"\r\n", b"\n")
            if ref["sha256"] not in {sha256(raw).hexdigest(), sha256(canonical).hexdigest()}:
                raise ValueError("External retained source changed: "+str(file))
            checked_external.append(dict(path=str(file), bytes=len(raw),
                                         sha256=ref["sha256"],
                                         scope="Retained convention/source only; no state selected"))
    manifest = dict(
        classification="MUON_BIRTH_FERMION_STATE_REPRESENTATION_SOURCE_MANIFEST",
        source_input_identities=identities,
        checked_retained_identities=checked,
        verified_citations=citations,
        checked_external_input_identities=checked_external,
        contextual_external_references=external,
        numerical_covariances_selected=0, geometric_reset_recomputed=False,
        old_controls_run=0, new_root_solves=0, trajectories=0,
        symbolic_operator_identity_proved=report["exact_symbolic_matched_balance"]["identically_zero"],
    )
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    hashes = {}
    for name, value in (("fermion_state_representation", report), ("source_manifest", manifest)):
        data = canonical_bytes(value)
        filename = name+".json"
        (output/filename).write_bytes(data)
        hashes[filename] = dict(bytes=len(data), sha256=sha256(data).hexdigest())
    (output/"output_hashes.json").write_bytes(canonical_bytes(hashes))
    return dict(
        products=hashes, representation=report["representation"],
        previous_vector_stop_superseded=True,
        exact_matched_operator_balance=report["exact_symbolic_matched_balance"]["identically_zero"],
        selected_physical_covariance=None,
        next_operand=report["unified_state_operand"]["value_name"],
        source_input_files=len(identities), checked_retained_identities=len(checked),
        verified_Python_citations=len(citations),
        full_physical_birth_identified=False,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(materialize(args.out), sort_keys=True))


if __name__ == "__main__":
    main()
