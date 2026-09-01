from __future__ import annotations
import numpy as np
from bhsm.interface.ae3_c2_coexact_su2l_neutral import lowest_weyl_coexact_su2l_neutral_source_jet, neutral_source_pair_ledger, weak_neutral_representation_ledger
from scripts.materialize_ae3_c2_coexact_su2l_neutral import build_payload

def test_rank16_weak_neutral_trace_ledger() -> None:
    r=weak_neutral_representation_ledger(); assert r["one_family_T3_trace"] == 0.0; assert r["one_family_T3_square_trace"] == 2.0; assert r["three_family_T3_square_trace"] == 6.0; assert r["one_family_Y_T3_trace"] == 0.0

def test_j3_jet_is_hermitian_on_both_chiral_pencils() -> None:
    for s in (-1,1):
        j=lowest_weyl_coexact_su2l_neutral_source_jet(proper_durations=np.array([.2,.3]),inverse_radii=np.array([1.,1.1]),source_profile=np.ones(2),chirality=s)
        assert np.allclose(j["vertex_elements"],j["vertex_elements"].conj().transpose(0,2,1)); assert j["source_kind"] == "SPATIAL_COEXACT_SU2L_NEUTRAL_T3"

def test_pair_stops_before_neutral_mixing() -> None:
    p=neutral_source_pair_ledger(); assert p["current_C2_JY_source_attached"] and p["current_C2_J3_source_attached"]; assert not p["neutral_Hessian_null_direction_derived"]; assert not p["physical_photon_vertex_derived"]

def test_actual_artifact_is_fail_closed() -> None:
    p=build_payload(); assert p["validation_passed"]; assert p["claim_boundary"]["CURRENT_C2_COEXACT_SU2L_J3_SOURCE_JET_DERIVED"]; assert not p["claim_boundary"]["CURRENT_C2_PHYSICAL_PHOTON_VERTEX_DERIVED"]
