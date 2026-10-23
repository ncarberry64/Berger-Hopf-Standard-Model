"""Check finite pole normalization under energy-dependent boundary rows.

Only stored six-row boundary data and independently computed simple modes
are used. No exterior, radiation subspace or magnetic insertion is chosen.
"""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import sys
import numpy as np


def encode(x):
    if isinstance(x,dict):return {k:encode(v)for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [encode(v)for v in x]
    if isinstance(x,np.ndarray):return encode(x.tolist())
    if isinstance(x,(complex,np.complexfloating)):return [float(x.real),float(x.imag)]
    if isinstance(x,np.generic):return x.item()
    return x


def run(repository,split_poles,output):
    root,split,out=map(lambda p:Path(p).resolve(),(repository,split_poles,output))
    sys.path[:0]=[str(root/'src'),str(root)]
    from bhsm.interface.muon_outgoing_trace_energy_jet import boundary_row_energy_change
    pins={};records=[]
    def read(p):
        pins[str(p)]=sha256(p.read_bytes()).hexdigest()
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    for p in (Path(__file__).resolve(),root/'src/bhsm/interface/muon_outgoing_trace_energy_jet.py'):
        pins[str(p)]=sha256(p.read_bytes()).hexdigest()
    S=np.eye(6)+.07*np.triu(np.ones((6,6)),1)+.03j*np.diag(np.arange(1,7))
    SE=np.eye(6,dtype=complex)
    def check(a,R,L,scope,stage,branch):
        d=boundary_row_energy_change(gamma=a['gamma6'],gamma_energy=a['gamma_energy6'],
            right_mode=R,left_mode=L,row_change=S,row_change_energy=SE)
        base_norm=np.linalg.norm(d['original_pairing'])
        records.append(dict(scope=scope,stage=stage,branch=branch,
            right_null_max=float(np.max(abs(d['right_null_rows']))),
            left_null_max=float(np.max(abs(d['left_null_rows']))),
            original_energy_pairing=d['original_pairing'],
            changed_energy_pairing=d['changed_pairing'],
            off_pole_row_contact=d['off_pole_row_contact'],
            relative_pairing_contact=float(np.linalg.norm(d['off_pole_row_contact'])/base_norm),
            exact_row_change_chain_rule_max=float(np.max(abs(d['exact_chain_rule_rows']))),
            physical_outgoing_mode_admitted=False))
    for stage in range(2):
        p=root/f'artifacts/muon_d5_finite_trace_pole_match_20261012/trial_0000_stage_pair_run_3/stage_{stage:04d}_finite_trace_pole_and_clock_rows.npz'
        a=read(p)
        check(dict(gamma6=a['full_gamma'],gamma_energy6=a['full_gamma_energy']),
              a['literal_right_trace_lift'],a['literal_left_trace_lift'],
              'old_shared_energy_trace_center',stage,None)
        for branch in range(2):
            a=read(split/f'stage_{stage:04d}_branch_{branch}_actual_finite_simple_pole.npz')
            check(a,a['normalized_right6'],a['normalized_literal_left6'],
                  'new_separately_normalized_finite_simple_pole',stage,branch)
    old=[r for r in records if r['branch'] is None]
    new=[r for r in records if r['branch'] is not None]
    if max(r['relative_pairing_contact']for r in new)>2e-10:
        raise ArithmeticError('simple-pole pairing is not insensitive to the analytic row basis within the guard')
    if min(r['relative_pairing_contact']for r in old)<1e-7:
        raise ArithmeticError('retained trace-center defect was not independently reproduced')
    if max(r['exact_row_change_chain_rule_max']for r in records)>5e-15:
        raise ArithmeticError('boundary row energy chain rule is unresolved')
    result=dict(classification='EVALUATED_FINITE_SPLIT_POLE_ENERGY_PAIRING_ROW_BASIS_CHECK',
        records=records,
        row_change_scope='S(E)=S0+(E-E_reference)*I is an invertible local coordinate change of boundary EQUATIONS, not a new field, energy correction, radiation condition or outgoing selector.',
        exact_identity='L_new Gamma_new,E R=L Gamma_E R+L S0^-1 S_E Gamma R. The extra term vanishes at a full pole, not merely a scalar trace-center root.',
        smaller_physical_exterior_requirement='For independently produced C(E)V(E)=0, Gamma=C T and T R=V a, Z=L C(T_E R-V_E a). Only normal motion of the actual allowed outgoing trace subspace is required. Its value and transverse E jet are still physically unbound; no arbitrary basis derivative or principal sector substitutes for them.',
        physical_boundary_energy_pairing=None,physical_magnetic_moment=None,
        coupled_matching_corrections_applied=0,
        original_source_D5_profile_canonical_pairing_campaigns_restarted=False,
        input_sha256=pins)
    for p,h in pins.items():
        if sha256(Path(p).read_bytes()).hexdigest()!=h:raise RuntimeError('consumed input changed')
    out.mkdir(parents=True,exist_ok=False)
    content=json.dumps(encode(result),sort_keys=True,indent=2,allow_nan=False)+'\n'
    (out/'result.json').write_text(content,encoding='utf8',newline='\n')
    print(json.dumps(dict(path=str(out/'result.json'),sha256=sha256(content.encode()).hexdigest(),
        new_maximum_relative_pairing_contact=max(r['relative_pairing_contact']for r in new),
        old_minimum_relative_pairing_contact=min(r['relative_pairing_contact']for r in old))),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repository',required=True);p.add_argument('--split-poles',required=True)
    p.add_argument('--output',required=True)
    a=p.parse_args();run(a.repository,a.split_poles,a.output)
