"""Independent MP root/quadrature checks at exact binary64 response deltas."""
from pathlib import Path
from hashlib import sha256
from io import BytesIO
import argparse
import json
import sys
import numpy as np
import mpmath as mp

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'audits'))
from bind_muon_real_changing_gauge_transport_20261016 import archive_bytes
from bhsm.interface.muon_holomorphic_normal_geometry import _geometry_variables,anchored_holomorphic_chart
from bhsm.interface.muon_exact_material_response import _rule


def evaluate(delta,order,precision):
    original=anchored_holomorphic_chart(delta,points=order)
    x,w=_rule(order)
    with mp.workdps(precision):
        d=mp.mpf(float(delta));pi=mp.mpf(float(np.pi));wall=pi/4+d
        x,w=[[mp.mpf(float(v))for v in a]for a in(x,w)]
        full=[pi*t/2 for t in x];cap=[wall*t for t in x]
        def integral(points,extent,a):
            return extent*sum(weight*mp.sin(2*(t+a[0]*mp.sin(2*t)+a[1]*mp.sin(6*t)))**2/4 for t,weight in zip(points,w))
        def equations(a,b):
            z=integral(full,pi/2,(a,b));n=integral(cap,wall,(a,b))
            return wall+a*mp.sin(2*wall)+b*mp.sin(6*wall)-pi/4,n/z-mp.mpf('.5')
        seed=tuple(mp.mpf(float(z.real))for z in original['coefficients'])
        root=mp.findroot(equations,seed,tol=mp.mpf(10)**(-precision+15),maxsteps=25)
        a=(root[0],root[1]);z=integral(full,pi/2,a)
        probabilities=[]
        for fraction in(1e-4,.5,1.):
            chi=mp.mpf(float(fraction))*wall
            numerator=integral([chi*t for t in x],chi,a)
            generic=numerator/z
            owned=numerator/(pi/16 if delta==0 else z)
            probabilities.append(dict(material_fraction=fraction,
                generic_chart_probability=mp.nstr(generic,68),owner_special_probability=mp.nstr(owned,68),
                stable_localization_weight=mp.nstr(4*owned*(1-owned),68)))
        residual=equations(*a)
        result=dict(order=order,precision_digits=precision,delta_binary_hex=float(delta).hex(),
            original_binary_coefficients=[[float(z.real),float(z.imag)]for z in original['coefficients']],
            original_implicit_residual=[[float(z.real),float(z.imag)]for z in original['implicit_residual']],
            original_implicit_jacobian_condition=float(np.linalg.cond(original['implicit_jacobian'])),
            MP_coefficients=[mp.nstr(v,68)for v in a],
            MP_minus_original_coefficients=[mp.nstr(v-s,68)for v,s in zip(a,seed)],
            MP_normalization=mp.nstr(z,68),MP_residual_maximum=mp.nstr(max(map(abs,residual)),20),
            probabilities=probabilities,original_delta_zero_normalization_override=(delta==0),
            quadrature_nodes_and_weights='Exact lifts of the original binary64 _rule(order), not regenerated MP roots',
            pi_constant='Exact binary64 numpy pi lifted to MP; not substituted with true MP pi')
        return result


def execute(output):
    out=Path(output)
    if out.exists():raise FileExistsError(out)
    base=ROOT/'artifacts/muon_real_changing_gauge_transport_20261016'
    raw=archive_bytes(base,'stable_time6_run_1/changing_forms.npz')
    cases=[]
    with np.load(BytesIO(raw),allow_pickle=False)as a:
        for side in('incoming','outgoing'):
            for index in(0,11):
                state=a[f'{side}_radial32_raw'][index]
                delta=_geometry_variables(state[:100],differentiate=False)[3].value
                if delta.imag!=0:raise ValueError('Actual exactly real delta required')
                cases.append((side,index,float(delta.real)))
    cases.append(('delta_zero_owner_control',None,0.))
    records=[]
    for side,index,d in cases:
        records.append(dict(side=side,time_index=index,delta=d,
            controls=[evaluate(d,n,p)for n in(96,192)for p in(80,100)]))
    pins={}
    for name,module in list(sys.modules.items()):
        p=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and p and Path(p).is_relative_to(ROOT):
            pins[Path(p).relative_to(ROOT).as_posix()]=sha256(Path(p).read_bytes()).hexdigest()
    pins[Path(__file__).relative_to(ROOT).as_posix()]=sha256(Path(__file__).read_bytes()).hexdigest()
    result=dict(classification='MP80_100_ANCHORED_RESPONSE_ROOT_AND_FIXED_BINARY_RULE_DIAGNOSIS',
        source_deltas='Exact binary64 outputs of original _geometry_variables on four saved snapshots; not a high precision reevaluation of that map',
        original_time6_archive_sha256=sha256(raw).hexdigest(),records=records,
        original_coefficient_and_derivative_owners_unmodified=True,
        higher_rule_is_physical_source_error_enclosure=False,
        full_physical_derivative_at_2e_minus10=False,coupled_corrections=0,
        source_byte_sha256=pins)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(result_sha256=sha256(out.read_bytes()).hexdigest(),case_count=len(cases))))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True);a=p.parse_args();execute(a.output)
