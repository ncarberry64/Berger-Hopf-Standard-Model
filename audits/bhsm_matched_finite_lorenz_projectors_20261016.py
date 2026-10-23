"""Matched finite Lorenz projectors; no resampling of saved coefficient fields."""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'audits')]
import bhsm_finite_lorenz_projector_ball_20261016 as owner

OWNER_SHA='c409d5247ed17ce3c2279aeea294eb2a0baa45f47b857b6083ecd3e95ca054da'


def execute(moment64,time_forms,value_forms,output):
    out=Path(output)
    if out.exists():raise FileExistsError('Preserve every independent matched solve')
    if sha256(Path(owner.__file__).read_bytes()).hexdigest()!=OWNER_SHA:
        raise ValueError('Reviewed finite projector owner required')
    out.mkdir(parents=True);records=[]
    for side in ('incoming','outgoing'):
        E=Path(value_forms)/f'{side}_radial128/forms.npz'
        for radial,time in ((64,8),(128,8),(128,12)):
            moment=Path(moment64) if radial==64 else Path(time_forms)/f'{side}_time{time}/forms.npz'
            prefix=side+'_' if radial==64 else ''
            folder=out/f'{side}_radial{radial}_time{time}'
            owner.execute(moment,prefix,E,folder,384)
            r=json.loads((folder/'result.json').read_bytes())
            records.append(dict(side=side,radial_order=radial,time_order_per_half=time,
                input_moment_sha256=r['input_moment_sha256'],input_E_sha256=r['input_E_sha256'],
                result_sha256=sha256((folder/'result.json').read_bytes()).hexdigest(),
                numerical_sha256=r['numerical_sha256'],
                exact_finite_B_times_Pi_residual=r['exact_finite_B_times_Pi_residual'],
                exact_finite_Pi_idempotence_residual=r['exact_finite_Pi_idempotence_residual'],
                X_high_low_max_entry_conversion_error_upper=r['X_high_low_max_entry_conversion_error_upper']))
    result=dict(classification='MATCHED_SAVED_MOMENT_FINITE_LORENZ_PROJECTORS',
        records=records,source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        finite_projector_source_sha256=OWNER_SHA,coefficient_history_recomputed=False,
        arithmetic_ball_scope='Exact saved finite MP80 tensor B only; excludes upstream field/quadrature error',
        physical_outgoing_domain_selected=False,physical_derivative_passed=False,
        original_coupled_corrections=0,physical_normalized_spins=None,muon_magnetic_moment=None)
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(matched_result_sha256=sha256((out/'result.json').read_bytes()).hexdigest())),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('moment64','time-forms','value-forms','output'):p.add_argument('--'+name,required=True)
    a=p.parse_args();execute(a.moment64,a.time_forms,a.value_forms,a.output)
