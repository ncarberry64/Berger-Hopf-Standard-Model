"""Materialize the current-C2 neutral SU(2)_L source jet."""

from __future__ import annotations

import hashlib, json, sys
from pathlib import Path
from typing import Any
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from bhsm.interface.ae3_c2_coexact_su2l_neutral import (
    ACTION_VERSION, CLASSIFICATION, lowest_weyl_coexact_su2l_neutral_source_jet,
    neutral_source_pair_ledger, weak_neutral_representation_ledger,
)

ARTIFACTS = ROOT / "artifacts"
JSON_DESC = ARTIFACTS / "flagship_integration/BHSM_N12_C2_1222_SEGMENT_FINITE_CORE_DESCRIPTOR.json"
NPZ_DESC = ARTIFACTS / "flagship_integration/BHSM_N12_C2_1222_SEGMENT_FINITE_CORE_DESCRIPTOR.npz"
TARGET = ARTIFACTS / "action_extension/BHSM_AE3_C2_COEXACT_SU2L_NEUTRAL_SOURCE_JET.json"
INPUTS = (
    JSON_DESC, NPZ_DESC,
    ARTIFACTS / "action_extension/BHSM_AE3_C2_COEXACT_HYPERCHARGE_SOURCE_JET.json",
    ARTIFACTS / "action_extension/BHSM_AE3_C2_LORENTZIAN_GAUGE_GHOST_FREQUENCY_HESSIAN.json",
    ARTIFACTS / "BHSM_aether_hybrid_standard_model_bundle_v15_53.json",
    ROOT / "src/bhsm/interface/ae3_c2_coexact_su2l_neutral.py",
)

def _load(path: Path) -> dict[str, Any]: return json.loads(path.read_text(encoding="utf-8"))
def _sha(path: Path) -> str: return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest().upper()
def _summary(a: np.ndarray) -> dict[str, float]:
    v=np.asarray(a); return {"minimum_real":float(v.real.min()),"maximum_real":float(v.real.max()),"maximum_absolute":float(np.abs(v).max())}

def build_payload() -> dict[str, Any]:
    if missing := [str(p) for p in INPUTS if not p.is_file()]: raise FileNotFoundError(", ".join(missing))
    descriptor, jy, hessian, bundle = map(_load, (JSON_DESC, INPUTS[2], INPUTS[3], INPUTS[4]))
    representation = weak_neutral_representation_ledger(); rows={}
    with np.load(NPZ_DESC) as data:
        x=np.asarray(data["node_log_R4_center"]); h=np.asarray(data["segment_proper_duration_proof_center"]); inv=np.exp(-0.5*(x[:-1]+x[1:]))
        for chirality, suffix in ((1,"plus"),(-1,"minus")):
            jet=lowest_weyl_coexact_su2l_neutral_source_jet(proper_durations=h,inverse_radii=inv,source_profile=np.ones_like(h),chirality=chirality)
            rows[suffix]={"chirality":chirality,"segments":jet["segments"],"vertex_summary":_summary(jet["vertex_elements"]),"contact_summary":_summary(jet["contact_elements"]),"Hermitian":bool(np.allclose(jet["vertex_elements"],jet["vertex_elements"].conj().transpose(0,2,1)))}
    pair=neutral_source_pair_ledger()
    validation={
        "current_C2_descriptor_valid":descriptor["validation_passed"] is True,
        "JY_predecessor_valid":jy["validation_passed"] is True,
        "dynamic_gauge_ghost_Hessian_valid":hessian["validation_passed"] is True,
        "global_SM_bundle_valid":bundle["validation_passed"] is True,
        "T3_traceless":representation["one_family_T3_trace"] == 0.0,
        "one_family_T3_square_trace_is_2":representation["one_family_T3_square_trace"] == 2.0,
        "three_family_T3_square_trace_is_6":representation["three_family_T3_square_trace"] == 6.0,
        "Y_T3_trace_zero":representation["one_family_Y_T3_trace"] == 0.0,
        "both_chiral_C2_jets_Hermitian":all(r["Hermitian"] for r in rows.values()),
        "same_domain_JY_J3_pair":pair["both_sources_share_lowest_Weyl_coexact_C2_domain"],
        "photon_not_promoted":not pair["physical_photon_vertex_derived"],
    }
    return {"artifact":"BHSM_AE3_C2_COEXACT_SU2L_NEUTRAL_SOURCE_JET","action_version":ACTION_VERSION,"classification":CLASSIFICATION,"domain":{"background":"ACTUAL_RESET_GENERATED_C2_FINITE_CORE_FAMILY","retained_boundary":"C2_BIRTH_TRACE_NODE_0","far_boundary":"FRIEDRICHS_FORM_CORE_TRUNCATION_ONLY"},"representation_attachment":representation,"chiral_rows":rows,"neutral_source_pair":pair,"claim_boundary":{"CURRENT_C2_COEXACT_SU2L_J3_SOURCE_JET_DERIVED":True,"CURRENT_C2_NEUTRAL_SOURCE_PAIR_JY_J3_ATTACHED":True,"CURRENT_C2_NEUTRAL_HESSIAN_NULL_DIRECTION_DERIVED":False,"CURRENT_C2_PHYSICAL_PHOTON_VERTEX_DERIVED":False},"inputs":{str(p.relative_to(ROOT)).replace("\\","/"):_sha(p) for p in INPUTS},"validation":validation,"validation_passed":all(validation.values()),"MUON_MAGNETIC_MOMENT_DERIVED":False,"FULL_BHSM_COMPLETE":False}

def main() -> None:
    payload=build_payload()
    if not payload["validation_passed"]: raise SystemExit("SU2L neutral source validation failed")
    TARGET.parent.mkdir(parents=True,exist_ok=True); TARGET.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8"); print(TARGET.relative_to(ROOT))
if __name__ == "__main__": main()
