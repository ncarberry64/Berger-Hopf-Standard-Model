from __future__ import annotations
import hashlib
import json
from pathlib import Path

REPO=Path(r'C:\Users\carbe\Downloads\BHSM_muon_parent_maxwell_worktree_20261001')
WORK=Path(__file__).resolve().parent
SOURCES={
 'foundational_action_and_same_spatial_hard_glue':('src/bhsm/interface/completion/foundational_dirac_spin_glue_v14_45.py',[[92,135],[230,287]]),
 'actual_two_half_collar_topology':('src/bhsm/interface/master_action/reduction.py',[[63,117]]),
 'full_hopf_collar_cover':('src/bhsm/interface/completion/full_hopf_preimage_effective_action_v14_30.py',[[36,50]]),
 'full_384_normalized_point_trace':('src/bhsm/interface/muon_full_d5_localized_lepton_trace.py',[[1,101],[118,237]]),
 'unsquared_two_sheet_SH_and_Green_owner':('src/bhsm/interface/muon_holomorphic_d5_trace_action.py',[[272,337],[419,517]]),
 'exact_nilpotent_algebra':('src/bhsm/interface/muon_isotropic_seam_transfer.py',[[1,150]]),
 'distinct_AE2_regular_birth':('src/bhsm/interface/action_extension_global_spin_reset_ae2.py',[[156,194]]),
}

def pin(p):
 b=p.read_bytes()
 return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),crlf_count=b.count(b'\r\n'),lf_count=b.count(b'\n'))

rows={}
for key,(rel,spans) in SOURCES.items():
 p=REPO/rel
 n=len(p.read_text(encoding='utf-8').splitlines())
 if any(not(1<=a<=b<=n)for a,b in spans):raise ValueError((rel,n,spans))
 rows[key]=dict(pin(p),repository_relative_path=rel,line_anchors=spans,actual_line_count=n)
proof=WORK/'muon_eta_seam_geometric_transition_and_universal_weak_completion_20261016.txt'
out=WORK/'muon_eta_seam_geometric_transition_and_universal_weak_completion_20261016_source_pins.json'
payload=dict(classification='BHSM_ORIGINAL_TWO_TRACE_SH_UNIVERSAL_LOCAL_WEAK_COMPLETION',
 date='2026-10-16',repository=str(REPO),proof=pin(proof),pin_generator=pin(Path(__file__).resolve()),sources=rows,
 original_trace_fiber_dimension=384,original_two_trace_dimension=768,
 extra_trace_copies_introduced=0,local_thin_layer_theorem_requires_stated_bounds=True,
 physical_finite_layer_profile_selected=False,normalization_or_measured_value_selected=False,
 native_common_positive_operator_identified=False,global_operator_or_norm_resolvent_convergence_proved=False,
 physical_outgoing_derivative_passed=False,original_coupled_corrections_applied=0,
 Maxwell_and_all_226_after_correction_passed=False,two_spin_states_normalized=False,
 muon_magnetic_moment_computed=False,numerical_campaigns_executed=0)
out.write_bytes((json.dumps(payload,sort_keys=True,indent=2)+'\n').encode('utf-8'))
print(json.dumps(dict(proof=pin(proof),pins=pin(out),source_count=len(rows)),sort_keys=True))
