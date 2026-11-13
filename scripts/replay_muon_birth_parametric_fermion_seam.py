"""Replay the incoming parametric carrier/seam response companion.

No historical producer or point-valued KKT callback is executed. The recorded
positive family and its joint seam supply exact rational uniform majorants.
"""
from __future__ import annotations

import argparse
import ast
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"src"))

from bhsm.interface.muon_birth_parametric_fermion_seam import (
    ADJOINT_PATH, ARTIFACT_DIRECTORY, QUOTIENT_PATH, STARTING_HEAD,
    parametric_response_packet,
)


def canonical_bytes(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False,
                       allow_nan=False)+"\n").encode("utf8")


def reference(path, symbols=()):
    raw=(ROOT/path).read_bytes()
    result=dict(path=path, bytes=len(raw), raw_sha256=sha256(raw).hexdigest())
    if symbols:
        nodes=list(ast.walk(ast.parse(raw.decode("utf8"))))
        spans={}
        for name in symbols:
            choices=[node for node in nodes if isinstance(node,(ast.FunctionDef,ast.ClassDef)) and node.name==name]
            if len(choices)!=1:
                raise ValueError("Source symbol absent or ambiguous: "+path+":"+name)
            spans[name]=[choices[0].lineno, choices[0].end_lineno]
        result["symbols"]=spans
    return result


def verify_references(value):
    identities={}
    def walk(item):
        if isinstance(item,dict):
            path=item.get("path")
            digest=item.get("raw_sha256")
            if path and digest:
                current=reference(path, item.get("symbols",()))
                if current["raw_sha256"]!=digest:
                    raise ValueError("Retained source identity changed: "+path)
                if item.get("symbols") and current["symbols"]!=item["symbols"]:
                    raise ValueError("Retained source span changed: "+path)
                identities[path]=current
            for child in item.values():
                walk(child)
        elif isinstance(item,list):
            for child in item:
                walk(child)
    walk(value)
    return identities


def materialize(output):
    packet=parametric_response_packet(ROOT)
    if packet["lower_order_owner_receipt"]["starting_head"]!=STARTING_HEAD:
        raise ValueError("Wrong companion action/head binding")
    identities=verify_references(packet)
    references={
        ADJOINT_PATH: (), QUOTIENT_PATH: (),
        "src/bhsm/interface/ae2_covariant_seam_response.py": ("covariant_effective_event_load_jet","covariant_seam_response"),
        "src/bhsm/interface/aether_forward_product_dirac_weyl_enclosures.py": ("product_dirac_compact_radius_weyl_variation_bounds",),
        "scripts/derive_n12_force_adjoint_pullback.py": ("build_payload",),
        "scripts/derive_n12_intrinsic_time_quotient_force_root.py": ("build_payload",),
        "src/bhsm/interface/muon_birth_covariance_sensitivity.py": ("charged_nambu_tangent_projection","minimal_consumed_moments"),
        "src/bhsm/interface/muon_birth_fermion_event_kkt_inputs.py": ("first_unavailable","physical_input_packet","call_retained_solver_and_noether"),
        "src/bhsm/interface/ae4_event_response_jet_integration.py": ("solve_retarded_event_kkt_jet","canonical_noether_flux_balance_jet"),
        "src/bhsm/interface/muon_birth_parametric_carrier_bounds.py": ("uniform_carrier_majorants","retained_carrier_bound_inputs"),
        "src/bhsm/interface/muon_birth_parametric_fermion_seam.py": ("parametric_response_packet","exact_symbolic_seam_cotangent_identity"),
        "scripts/replay_muon_birth_parametric_fermion_seam.py": ("materialize",),
        "tests/test_muon_birth_parametric_fermion_seam.py": (),
        "theory/muon_birth_parametric_fermion_seam_20261008.md": (),
        ARTIFACT_DIRECTORY+"/lower_order_owner_receipt.json": (),
    }
    for path,symbols in references.items():
        identities[path]=reference(path,symbols)
    manifest=dict(source_records=[identities[path] for path in sorted(identities)],
                  starting_head=STARTING_HEAD, point_guard_modified=False,
                  point_KKT_callback_called=False, old_producers_recomputed=False)
    output=Path(output)
    output.mkdir(parents=True,exist_ok=True)
    products={}
    for name,value in (("parametric_fermion_seam.json",packet),("source_manifest.json",manifest)):
        raw=canonical_bytes(value)
        (output/name).write_bytes(raw)
        products[name]=dict(bytes=len(raw),sha256=sha256(raw).hexdigest())
    (output/"output_hashes.json").write_bytes(canonical_bytes(products))
    return dict(audit_passed=True, desired_milestone=3,
        first_blocker=packet["first_blocker"]["term"],
        uniform_carrier_bounds_evaluated=True, uniform_seam_cotangent_bounds_evaluated=True,
        complete_CAR_verdict=None, physical_member_selected=False,
        point_KKT_callback_called=False, symbolic_residual=packet["symbolic_seam_cotangent"]["residual"],
        source_records=len(identities), products=products)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out",required=True,type=Path)
    print(json.dumps(materialize(parser.parse_args().out),sort_keys=True))


if __name__=="__main__":
    main()
