"""Evaluate higher-even-Y finite target/contact bounds on the changing action."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_changing_closed_fermion_tail import changing_heat_tail_application
from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase
from evaluate_muon_reached_trace_action import deterministic_archive


def materialize(output,precision_bits=192):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve previous tail application')
    refs={};data={}
    for key,stem in (('mean','muon_corrected_profile_mean_load'),('heat','muon_changing_closed_fermion_mean')):
        folder=ROOT/'artifacts'/(stem+'_20261011')/'run_1'
        r=json.loads((folder/'result.json').read_bytes());refs.update(r['input_hashes'])
        for name in ('application.npz','result.json'):
            p=folder/name;h=sha256(p.read_bytes()).hexdigest();refs[p.relative_to(ROOT).as_posix()]=h
            if name=='application.npz'and h!=r['archive']['sha256']:raise ValueError('consumed archive changed')
        with np.load(folder/'application.npz',allow_pickle=False)as a:data[key]={k:a[k].copy()for k in a.files}
    arrays={};rows=[]
    for side in ('incoming','outgoing'):
        phase=load_profile_preserving_phase('artifacts/muon_finite_normal_phase_20261011/incoming_run_1'if side=='incoming'else'artifacts/muon_inherited_finite_normal_phase_20261011/run_1')
        refs.update(phase['input_hashes']);a=data['heat'];prefix=side+'_quadrature_16_'
        print(json.dumps(dict(stage='changing_even_tail_certificate',side=side)),flush=True)
        r=changing_heat_tail_application(phase,*[a[prefix+k]for k in ('weak_P0','weak_P1','weak_P2','temporal_Gram')],
            data['mean'][side+'_raw_mean_cotangent'],cutoff=1e-11,quadrature_order=16,precision_bits=precision_bits)
        for k,v in r.items():
            if isinstance(v,np.ndarray):arrays[side+'_'+k]=v
        for k,v in r['primitive_norms'].items():arrays[side+'_primitive_'+k]=v
        contacts=[]
        for c in r['contacts']:
            for k,v in c.items():
                if isinstance(v,np.ndarray):arrays[side+'_'+c['frame']+'_'+k]=v
            contacts.append(dict(frame=c['frame'],maximum_contact_Y4_majorant=float(np.max(c['contact_tail_majorant'])),
                original_response_residual_norm=float(np.linalg.norm(c['original_response_residual'])),
                stored_response_amplification_only=True))
        row=dict(side=side,pencil_certificate=r['pencil_certificate'],tail_certificate=r['tail_certificate'],
            phase_gradient_Y4_majorant_norm=float(np.linalg.norm(r['phase_gradient_tail_upper'])),contacts=contacts)
        rows.append(row);print(json.dumps(dict(stage='changing_even_tail_evaluated',**row),sort_keys=True),flush=True)
    for p in ('src/bhsm/interface/muon_changing_closed_fermion_tail.py','src/bhsm/interface/muon_native_even_y_remainder_certificate.py',
        'src/bhsm/interface/muon_native_mean_core_heat_target.py','tests/test_muon_changing_closed_fermion_tail.py',Path(__file__).relative_to(ROOT).as_posix()):
        refs[p]=sha256((ROOT/p).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('consumed action changed')
    out.mkdir(parents=True);deterministic_archive(out/'application.npz',arrays)
    receipt=dict(classification='EVALUATED_CHANGING_CHRONOLOGICAL_HIGHER_EVEN_Y_BOUNDS',input_hashes=refs,records=rows,
        archive=dict(path='application.npz',bytes=(out/'application.npz').stat().st_size,sha256=sha256((out/'application.npz').read_bytes()).hexdigest()),
        precision_bits=precision_bits,cutoff_probe=1e-11,quadrature_order=16,higher_even_Y_filled_zero=False,
        stored_pencil_tail_certified=True,primitive_production_and_adjoint_response_certified=False,
        domain='actual changing n0/C6 temporal8 generalized pencil and original chronological finite adjoint',
        complete_observable=False,physical_a_mu=None,physical_g_mu=None,
        error_scope='Arb outward exact-stored finite-pencil even-Y tails; primitive arithmetic bounds and binary64 response amplification. Field/entry production, quadrature, solve, starting-loop/domain/completion and Pauli errors remain separate.')
    (out/'result.json').write_text(json.dumps(receipt,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(classification=receipt['classification'],archive=receipt['archive']),sort_keys=True))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--precision-bits',type=int,default=192)
    a=p.parse_args();materialize(a.output,a.precision_bits)
