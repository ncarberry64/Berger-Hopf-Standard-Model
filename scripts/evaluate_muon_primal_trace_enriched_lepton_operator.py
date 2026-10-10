"""Apply the intrinsic operator to the corrected interacting paired endpoint."""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.muon_primal_trace_enriched_lepton_operator import primal_trace_enriched_lepton_operator
from evaluate_muon_reached_trace_action import deterministic_archive


def materialize(endpoint,output):
    folder=Path(endpoint);folder=folder if folder.is_absolute() else ROOT/folder
    out=Path(output);out=out if out.is_absolute() else ROOT/out
    if out.exists():raise FileExistsError('preserve previous applications; choose a new output directory')
    receipt_path=folder/'result.json';archive=folder/'application.npz'
    receipt=json.loads(receipt_path.read_text(encoding='utf8'))
    if receipt['status']!='REPRESENTED_TEMPORAL_FIELD_TOLERANCE':raise ValueError('paired endpoint equations not converged')
    if sha256(archive.read_bytes()).hexdigest()!=receipt['numerical_sha256']:raise ValueError('paired endpoint archive mismatch')
    refs=[receipt_path,archive,ROOT/'src/bhsm/interface/muon_primal_trace_enriched_lepton_operator.py',
        ROOT/'src/bhsm/interface/muon_primal_intrinsic_lepton_operator.py',
        ROOT/'src/bhsm/interface/muon_native_dirac_hamiltonian.py',
        ROOT/'src/bhsm/interface/muon_native_product_factor_graph.py',
        ROOT/'src/bhsm/interface/muon_birth_trace_enriched_action.py',
        ROOT/'src/bhsm/interface/muon_intrinsic_m4_normal_pullback.py',
        ROOT/'scripts/evaluate_muon_reached_trace_action.py',Path(__file__)]
    hashes={p.relative_to(ROOT).as_posix():sha256(p.read_bytes()).hexdigest() for p in refs}
    with np.load(archive,allow_pickle=False) as f:
        fields=f['updated_raw_pair'];wall_map=f['wall_trace_map']
    rep=dict(gauge_labels=receipt['gauge_labels'],wall_trace_map=wall_map)
    arrays={};rows=[];operators=[]
    for side,raw in zip(('incoming','outgoing'),fields):
        a=primal_trace_enriched_lepton_operator(raw,rep);operators.append(a)
        for key,value in a.items():
            if isinstance(value,np.ndarray):arrays[side+'_'+key]=value
        spectra={}
        for j,name in enumerate(('heavy','middle','light')):
            ids=np.array([2*j,2*j+1,6+2*j,7+2*j,12+2*j,13+2*j])
            eig=np.linalg.eigvalsh(a['W'][np.ix_(ids,ids)]);spectra[name]=eig.tolist()
            arrays[side+'_'+name+'_W_eigenvalues']=eig
        rows.append(dict(side=side,coordinate_time=0.,birth_side_no_finite_offset=True,
            R4=a['R4'],N=a['N'],H_real=np.r_[a['H'].real,a['H'].imag].tolist(),
            independent_gauge_norm=float(np.linalg.norm(raw[100:180])),
            W_norm=float(np.linalg.norm(a['W'])),Omega_tau_norm=float(np.linalg.norm(a['Omega_tau'])),
            W_Hermiticity_defect=float(np.linalg.norm(a['W']-a['W'].conj().T)),
            Omega_tau_antiHermiticity_defect=float(np.linalg.norm(a['Omega_tau']+a['Omega_tau'].conj().T)),
            proper_time_Haar_measure=a['proper_time_Haar_measure'],
            normal_W_first_jet_norm=float(np.linalg.norm(a['W_raw_first_jet'][98])),
            raw_first_jet_count=len(raw),wall_action_rank=a['wall_action_rank'],
            complete_wall_trace_reconstruction_defect=a['complete_trace_reconstruction_defect'],
            family_W_spectra=spectra))
    if hashes!={p.relative_to(ROOT).as_posix():sha256(p.read_bytes()).hexdigest() for p in refs}:
        raise RuntimeError('consumed action owner changed')
    out.mkdir(parents=True);deterministic_archive(out/'application.npz',arrays)
    result=dict(classification='EVALUATED_ACTUAL_INTERACTING_PAIRED_ENDPOINT_INTRINSIC_OPERATOR',
        input_hashes=hashes,applications=rows,action_parameters=receipt['action_parameters'],
        consumed_scaled_paired_residual=receipt['scaled_residual'],
        consumed_gauge_temporal_dual_jump=receipt['gauge_temporal_dual_jump_norm'],
        consumed_H_temporal_dual_jump=receipt['scalar_temporal_dual_jump_norm'],
        common_birth_comparison=dict(W_difference_norm=float(np.linalg.norm(operators[0]['W']-operators[1]['W'])),
            Omega_t_difference_norm=float(np.linalg.norm(operators[0]['Omega_t']-operators[1]['Omega_t'])),
            Omega_tau_difference_norm=float(np.linalg.norm(operators[0]['Omega_tau']-operators[1]['Omega_tau'])),
            proper_time_Haar_measure_difference=operators[0]['proper_time_Haar_measure']-operators[1]['proper_time_Haar_measure'],
            instantaneous_operator_agreement_is_relative_heat_cancellation=False),
        domain='exact common birth surface on represented corrected parent-final/child-initial action; constant-angular invariant C18 computational subspace',
        normalization='current Gram I18 after chi=R4^(3/2)psi; unitTr16 gauge generators and fixed action Y; proper-time measure and its first jets separate',
        representation='all80 actual radial gauge coordinates; exact intrinsic action reduction through all20 wall trace components, radial Maxwell action not reduced',
        first_jet_frame='saved affine source profile is a fixed numerical reference frame; no mode/covariance/state selected',
        error_scope='binary64 analytic first operator applications on saved finite Newton fields; no continuum, rounding, matching or Pauli enclosure',
        array_sha256=sha256((out/'application.npz').read_bytes()).hexdigest(),
        physical_fullfield_junction_closed=False,complete_relative_native_domain=False,
        physical_Pauli_value=False,action_selected=False,Gate7_closed=False,complete_observable=False)
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return dict(array_sha256=result['array_sha256'],receipt_sha256=sha256((out/'result.json').read_bytes()).hexdigest(),
        common_birth_comparison=result['common_birth_comparison'],applications=rows)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--endpoint',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();print(json.dumps(materialize(args.endpoint,args.output),sort_keys=True))
