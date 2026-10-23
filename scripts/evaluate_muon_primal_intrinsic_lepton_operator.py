"""Apply the all-family lepton operator to corrected actual primal fields."""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.muon_parent_gauge_geometry_correction import correction_representation
from bhsm.interface.muon_primal_intrinsic_lepton_operator import primal_intrinsic_lepton_operator
from evaluate_muon_reached_trace_action import deterministic_archive


def materialize(output):
    out=Path(output)
    if out.exists():raise FileExistsError('preserve earlier evidence; choose a new output directory')
    base='artifacts/muon_parent_gauge_geometry_correction_20261010'
    refs=['src/bhsm/interface/muon_primal_intrinsic_lepton_operator.py',
        'src/bhsm/interface/muon_native_dirac_hamiltonian.py',
        'src/bhsm/interface/muon_native_product_factor_graph.py',
        'src/bhsm/interface/muon_intrinsic_m4_normal_pullback.py',
        'src/bhsm/interface/muon_parent_gauge_geometry_correction.py',
        'scripts/evaluate_muon_primal_intrinsic_lepton_operator.py',
        'scripts/evaluate_muon_reached_trace_action.py']
    for side in ('incoming','outgoing'):
        refs += [f'{base}/full_midpoint_{side}_run_1/{name}' for name in ('result.json','application.npz')]
    hashes={p:sha256((ROOT/p).read_bytes()).hexdigest() for p in refs}
    rep=correction_representation(radial_points=48,cap_points=48,radial_order=2,include_wall_lift=True,include_scalar_mean=True)
    arrays={};rows=[];values=[]
    for side in ('incoming','outgoing'):
        folder=ROOT/base/f'full_midpoint_{side}_run_1'
        receipt=json.loads((folder/'result.json').read_text(encoding='utf8'))
        if receipt['numerical_sha256']!=sha256((folder/'application.npz').read_bytes()).hexdigest():raise ValueError('actual primal field archive mismatch')
        with np.load(folder/'application.npz',allow_pickle=False) as f:
            fields=(f['initial_raw_coefficients'],f['updated_midpoint_raw'])
        for position,raw in zip(('birth','midpoint'),fields):
            a=primal_intrinsic_lepton_operator(raw,rep);label=f'{side}_{position}'
            for key,value in a.items():
                if isinstance(value,np.ndarray):arrays[label+'_'+key]=value
            eig=np.linalg.eigvalsh(a['W']);arrays[label+'_W_eigenvalues']=eig
            family_spectra={}
            for j,name in enumerate(('heavy','middle','light')):
                ids=np.array([2*j,2*j+1,6+2*j,7+2*j,12+2*j,13+2*j])
                family_spectra[name]=np.linalg.eigvalsh(a['W'][np.ix_(ids,ids)]).tolist()
            rows.append(dict(side=side,position=position,coordinate_time=0. if position=='birth' else receipt['step']/2,
                R4=a['R4'],N=a['N'],H_real=np.r_[a['H'].real,a['H'].imag].tolist(),
                proper_time_Haar_measure=a['proper_time_Haar_measure'],
                W_Hermiticity_residual=float(np.linalg.norm(a['W']-a['W'].conj().T)),
                Omega_tau_antiHermiticity_residual=float(np.linalg.norm(a['Omega_tau']+a['Omega_tau'].conj().T)),
                W_norm=float(np.linalg.norm(a['W'])),Omega_tau_norm=float(np.linalg.norm(a['Omega_tau'])),
                W_raw_first_jet_norm=float(np.linalg.norm(a['W_raw_first_jet'])),
                first_normal_W_norm=float(np.linalg.norm(a['W_raw_first_jet'][98])),
                family_W_spectra=family_spectra,action_parameters=receipt['action_parameters'],
                raw_array_key=label+'_raw_fields',stationary_physical_birth_claim=False,
                angular_scope=a['angular_scope'],zero_application_provenance=a['zero_application_provenance']))
            if position=='birth':values.append(a)
    if hashes!={p:sha256((ROOT/p).read_bytes()).hexdigest() for p in refs}:raise RuntimeError('consumed primal owner changed during the action application')
    out.mkdir(parents=True);deterministic_archive(out/'application.npz',arrays)
    result=dict(classification='EVALUATED_ALL_FAMILY_DIRAC_OPERATOR_AND_FIRST_JETS_ON_ACTUAL_PRIMAL_FIELDS',
        input_hashes=hashes,applications=rows,
        common_birth_comparison=dict(
            W_difference_norm=float(np.linalg.norm(values[0]['W']-values[1]['W'])),
            Omega_tau_difference_norm=float(np.linalg.norm(values[0]['Omega_tau']-values[1]['Omega_tau'])),
            proper_time_Haar_measure_difference=values[0]['proper_time_Haar_measure']-values[1]['proper_time_Haar_measure'],
            instantaneous_W_agreement_is_relative_heat_cancellation=False,
            birth_is_no_finite_temporal_offset=True),
        temporal_policy='birth values at exact common t0; midpoint operators separately labeled actual Euler continuation at step/2',
        pairing='chi=R4^(3/2)psi; current Gram I18, N_induced dt*2pi² heat measure returned with its variation',
        normalization='fixed Y operator and unitTr16 gauge generators; family eigenbasis is computational, no state/covariance/carrier selection',
        producer_scope='actual corrected assigned-parameter endpoint and nonlinear full-action midpoint fields; physical unit/area/formation and complementary graph remain further consumed solves',
        array_sha256=sha256((out/'application.npz').read_bytes()).hexdigest(),
        error_scope='binary64 exact analytic field/geometry first applications; spectra and differences numerical, not continuum, rounding or Pauli bounds',
        complete_native_domain_or_LSZ_selected=False,physical_Pauli_value=False,
        action_selected=False,Gate7_closed=False)
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    print(json.dumps(materialize(a.output),sort_keys=True))
