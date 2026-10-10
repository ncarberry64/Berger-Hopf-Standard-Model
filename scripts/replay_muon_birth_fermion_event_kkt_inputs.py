"""Materialize the six physical inputs to the existing fermion E1 callback.

The retained KKT/Noether routines are called only if every physical entry is
supplied. A null input is reported by argument and derivative order. This
script runs no synthetic event assembly or covariance-selection calculation.
"""
from __future__ import annotations

import argparse
import ast
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.muon_birth_fermion_event_kkt_inputs import (
    ARGUMENT_OPERANDS, ARTIFACT_DIRECTORY, STARTING_HEAD,
    call_retained_solver_and_noether, physical_input_packet,
)


def canonical_bytes(value):
    def numerical_json(item):
        if hasattr(item, "tolist"):
            return item.tolist()
        if isinstance(item, complex):
            return dict(real=item.real, imaginary=item.imag)
        raise TypeError("Unsupported callback output: " + type(item).__name__)
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False,
                       allow_nan=False, default=numerical_json) + "\n").encode("utf8")


def reference(path, symbols=()):
    raw = (ROOT / path).read_bytes()
    record = dict(path=path, bytes=len(raw), raw_sha256=sha256(raw).hexdigest())
    if symbols:
        nodes = list(ast.walk(ast.parse(raw.decode("utf8"))))
        spans = {}
        for symbol in symbols:
            candidates = [n for n in nodes if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name == symbol]
            if len(candidates) != 1:
                raise ValueError("Source symbol absent/ambiguous: " + path + ":" + symbol)
            spans[symbol] = [candidates[0].lineno, candidates[0].end_lineno]
        record["symbols"] = spans
    return record


def physical_inventory():
    """Populate only source-bound numerical operands for the actual domain.

    The current parent receipt identifies P_F order0 unavailable. The other
    sources below independently show why synthetic and later-C2 data cannot
    fill a physical tuple or prove a whole-row zero. No numerical entries are
    obtained by changing their event, source or pairing scope.
    """
    parent_path = ARTIFACT_DIRECTORY + "/parent_operand_receipt.json"
    parent = json.loads((ROOT / parent_path).read_text(encoding="utf8"))
    definitions = {
        "src/bhsm/interface/ae4_event_response_jet_integration.py": ["solve_retarded_event_kkt_jet", "canonical_noether_flux_balance_jet"],
        "src/bhsm/interface/ae4_c2_stratified_event_flux_assembly.py": ["assemble_stratified_direct_sum", "solve_retarded_event_kkt", "assembly_contract"],
        "scripts/materialize_ae4_c2_stratified_event_flux_assembly.py": ["theorem_witness", "build_payload"],
        "scripts/materialize_ae4_event_response_jet_integration.py": ["build_payload"],
        "src/bhsm/interface/ae4_current_c2_affine72_particle_fiber_calderon.py": ["product_dirac_friedrichs_weyl_first_jet", "attach_preserved_particle_fibers"],
        "src/bhsm/interface/ae3_c2_action_puzzle.py": ["reduced_product_dirac_hs_source_jet"],
        "src/bhsm/interface/ae3_c2_hs_mixed_variation.py": ["reduced_bilinear_variations"],
        "src/bhsm/interface/action_extension_global_spin_reset_ae2.py": ["action_definition"],
        "src/bhsm/interface/ae31_c2_intrinsic_m4_lepton_action.py": ["action_composition_contract"],
        "src/bhsm/interface/ae31_c2_fermion_hadamard_state_class.py": ["cauchy_covariance_selection_contract"],
        "src/bhsm/interface/aether_forward_channel_transfer.py": ["product_dirac_compact_history_weyl_jets", "restrict_two_boundary_weyl_to_dirichlet_birth_jets"],
    }
    refs = [reference(path, symbols) for path, symbols in definitions.items()]
    refs.extend(reference(path) for path in (
        "artifacts/action_extension/BHSM_AE4_C2_STRATIFIED_EVENT_FLUX_ASSEMBLY.json",
        "artifacts/action_extension/BHSM_AE4_EVENT_RESPONSE_JET_INTEGRATION.json",
        "artifacts/action_extension/BHSM_AE4_CURRENT_C2_AFFINE72_PARTICLE_FIBER_CALDERON.json",
        "artifacts/action_extension/BHSM_AE3_C2_FULL_FIELD_PUZZLE_ASSEMBLY.json",
        "artifacts/flagship_integration/BHSM_N12_C2_REFINED_RESET_ROOT_CENTER.npz",
        "artifacts/muon_birth_covariance_sensitivity_20261008/run_1/covariance_sensitivity.json",
        "theory/muon_birth_covariance_sensitivity_20261008.md",
        parent_path,
    ))
    descriptions = {
        "P_F": "H_pp fermion_family: same incoming E1 parent quadratic trace/traction block, including parent-interior elimination, inherited statistics/pairing and active LR/Higgs/gauge/HS composition",
        "B_F": "H_pc fermion_family: same-event parent-child mixed block before the existing child Schur elimination",
        "L_F": "H_cc^R fermion_family: same retarded child block on the oriented/reset-pulled trace space",
        "C_F": "Fermion-family restriction of the action response rows, including their metric/normal/profile/source/domain contacts",
        "J_F": "Actual explicit fermion source/current column on that common trace space; kept affine and separate from quadratic commutator",
        "d_F": "Actual response target column for the same constraints/source/domain",
    }
    rows = []
    for argument, operand in ARGUMENT_OPERANDS:
        rows.append(dict(
            argument=argument, operand=operand, mathematical_object=descriptions[operand],
            entries=[dict(derivative_order=order, value=None,
                status="UNAVAILABLE_NUMERICAL_PHYSICAL_OPERAND",
                zero_provenance=None) for order in (0, 1, 2)],
            unknown_is_zero=False,
        ))
    return dict(
        schema="BHSM_PHYSICAL_E1_FERMION_FAMILY_JET_INPUT_INVENTORY_V1",
        starting_head=STARTING_HEAD,
        incoming=dict(branch=23, event="E1_minus", source_state_slice=[98, 196]),
        outgoing=dict(branch=24, event="E1_plus", source_state_slice=[0, 98]),
        sector="fermion_family", same_common_event=True,
        source_parameter=dict(name="s", real=True, physical_direction_evaluated=False,
                              unknown_direction_replaced_by_zero=False),
        pairing="Inherited action-normalized fermion trace pairing; the callback adjoints assume its common normalized coordinates",
        orientation="Parent and child outward normals and the existing AE2 reset pullback; no sign changed to force zero",
        charge_family="Charge-conjugate doubling and inherited family projectors; no spatial Dirac level relabelled as muon (k,j)",
        input_rows=rows,
        solver_inputs={argument: [None, None, None] for argument, _ in ARGUMENT_OPERANDS},
        parent_operand_receipt=parent,
        binding_requirements=[
            "Differentiate the originating action, including metric/measure/spin and additive Yukawa terms, before boundary reduction.",
            "Pairing, reset, trace/domain and moving-boundary derivatives must be pulled to the same incoming domain before supplying jets.",
            "Use one real physical source direction for all six triples; order2 means second derivative, not a Taylor coefficient.",
            "Keep explicit-source, response-target and multiplier reactions; no missing numerical derivative defaults to zero.",
        ],
        scoped_zero_ledger=[dict(
            object="independent fermion reset surface density", value=0,
            source="action_extension_global_spin_reset_ae2.action_definition",
            exact=True, zeros_any_of_the_six_solver_arguments=False)],
        rejected_substitutions=[
            "The event and jet materializers explicitly construct synthetic finite matrices; their successful KKT solves are not physical operands.",
            "The actual C2 Friedrichs carrier supplies a value and affine72 first jet, before full internal composition; it is not the incoming E1 parent block or six complete jets.",
            "The finite-core reduced LR/HS V,Q source jet is a local quadratic/contact piece with a supplied nondynamical source profile; it is not the actual E1 source or response tuple.",
            "Zero-coefficient-background HS contractions do not set a sourced row or its higher vertices to zero.",
            "Closed Green/EM normal flux is not substituted for this sourced KKT input calculation.",
        ],
        source_references=refs,
        assembly_reimplemented=False, old_calculations_recomputed=False,
        selected_covariances=0,
    )


def verify_references(value):
    """Verify every encountered source identity and Python symbol span."""
    identities = {}
    def walk(item):
        if isinstance(item, dict):
            path = item.get("path", item.get("source_path"))
            digest = item.get("raw_sha256", item.get("sha256"))
            if path and digest:
                file = ROOT / path
                if not file.is_file():
                    raise ValueError("Referenced input is absent: " + path)
                raw = file.read_bytes()
                if digest.lower() not in {sha256(raw).hexdigest(), sha256(raw.replace(b"\r\n", b"\n")).hexdigest()}:
                    raise ValueError("Referenced input identity changed: " + path)
                identities[path] = reference(path)
                if item.get("symbols"):
                    current = reference(path, item["symbols"])
                    if current["symbols"] != item["symbols"]:
                        raise ValueError("Referenced Python span changed: " + path)
            for child in item.values():
                walk(child)
        elif isinstance(item, list):
            for child in item:
                walk(child)
    walk(value)
    return identities


def materialize(output):
    inventory = physical_inventory()
    inventory_path = ROOT / ARTIFACT_DIRECTORY / "physical_input_inventory.json"
    data = canonical_bytes(inventory)
    if inventory_path.exists() and inventory_path.read_bytes() != data:
        raise ValueError("Physical input inventory changed; inspect rather than silently replace")
    inventory_path.parent.mkdir(parents=True, exist_ok=True)
    inventory_path.write_bytes(data)
    packet = physical_input_packet(ROOT)
    identities = verify_references(packet)
    # A genuine first-input stop; no synthetic tuple is passed to either callback.
    try:
        response, noether = call_retained_solver_and_noether(
            packet["solver_inputs"], packet["physical_generator"])
    except ValueError as exc:
        if packet["first_unavailable"] is None:
            raise
        packet["solver_invocation"] = dict(called=False, reason=str(exc))
        packet["Noether_invocation"] = dict(called=False, reason="No physical traction jets were produced")
    else:
        packet["solver_invoked"] = True
        packet["solver_invocation"] = dict(called=True)
        packet["retained_solver_output"] = response
        packet["effective_retarded_parent_jet"] = response["effective_retarded_parent_jet"]
        packet["event_traction_jets"] = response["event_traction_jets"]
        packet["noether_invoked"] = noether is not None
        packet["Noether_invocation"] = dict(called=noether is not None,
            reason=None if noether is not None else "Physical Noether generator is absent")
        packet["retained_Noether_output"] = noether
    for path in (
        "src/bhsm/interface/muon_birth_fermion_event_kkt_inputs.py",
        "scripts/replay_muon_birth_fermion_event_kkt_inputs.py",
        "tests/test_muon_birth_fermion_event_kkt_inputs.py",
        "theory/muon_birth_fermion_event_kkt_inputs_20261008.md",
        ARTIFACT_DIRECTORY + "/physical_input_inventory.json",
    ):
        identities[path] = reference(path)
    manifest = dict(source_input_identities=[identities[p] for p in sorted(identities)],
                    preserved_CAR_head=STARTING_HEAD,
                    physical_solver_called=packet["solver_invoked"], physical_covariance_selected=False)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    products = {}
    for name, value in (("fermion_event_kkt_inputs.json", packet), ("source_manifest.json", manifest)):
        raw = canonical_bytes(value)
        (output / name).write_bytes(raw)
        products[name] = dict(bytes=len(raw), sha256=sha256(raw).hexdigest())
    (output / "output_hashes.json").write_bytes(canonical_bytes(products))
    return dict(audit_passed=True, first_unavailable=packet["first_unavailable"],
                solver_called=packet["solver_invoked"], noether_called=packet["noether_invoked"],
                quadratic_identity_residual=packet["quadratic_identity"]["Hermitian_residual"],
                products=products, sources=len(identities))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    print(json.dumps(materialize(parser.parse_args().out), sort_keys=True))


if __name__ == "__main__":
    main()
