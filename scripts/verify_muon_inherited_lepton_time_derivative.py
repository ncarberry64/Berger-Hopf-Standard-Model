"""Independent same-cell finite differences of the full inherited Dirac value."""
from pathlib import Path
from hashlib import sha256
import json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.muon_birth_finite_normal_phase import load_finite_normal_endpoint
from bhsm.interface.muon_inherited_intrinsic_lepton_operator import inherited_intrinsic_lepton_operator
from bhsm.interface.muon_inherited_lepton_temporal_weak_action import inherited_cell_raw_at_time


def main():
    phase=ROOT/'artifacts/muon_inherited_finite_normal_phase_20261011/run_1/application.npz'
    contact=ROOT/'artifacts/muon_inherited_lepton_time_contact_20261011/run_1/application.npz'
    base=load_finite_normal_endpoint('artifacts/muon_parent_gauge_geometry_correction_20261010/finite_moving_trace_run_1',side='outgoing')
    with np.load(phase,allow_pickle=False) as f:p={k:f[k].copy() for k in f.files}
    with np.load(contact,allow_pickle=False) as f:expected=f['stage_0_n0_spatial_proper_time_derivative'].copy()
    t=float(p['stage_coordinate_time'][0]);raw=p['stage_independent_raw'][0]
    op=inherited_intrinsic_lepton_operator(raw,t,p['initial_pair'],p['reference_pair'],base['representation'])
    results=[]
    for h in (1e-6,5e-7,2e-7):
        values=[]
        for z in (t-h,t+h):
            r=inherited_cell_raw_at_time(raw,t,z,base['representation'])
            values.append(inherited_intrinsic_lepton_operator(r,z,p['initial_pair'],p['reference_pair'],base['representation'])['W'])
        fd=(values[1]-values[0])/(2*h*op['N'])
        results.append(dict(coordinate_step=h,proper_time_derivative_difference_norm=float(np.linalg.norm(fd-expected))))
    if min(z['proper_time_derivative_difference_norm'] for z in results)>1e-7:
        raise AssertionError('full same-cell time derivative failed independent comparison')
    print(json.dumps(dict(classification='INDEPENDENT_SAME_CELL_FULL_INHERITED_VALUE_TIME_DERIVATIVE_CHECK',
        inputs={q.relative_to(ROOT).as_posix():sha256(q.read_bytes()).hexdigest() for q in (phase,contact)},
        results=results,expected_derivative_norm=float(np.linalg.norm(expected)),
        full_x_rates_and_parent_reference_explicit_time_used=True,
        samples_inside_represented_cell=True,
        numerical_error_enclosure=False,physical_history_or_anomaly_bound=False),sort_keys=True))

if __name__=='__main__':main()
