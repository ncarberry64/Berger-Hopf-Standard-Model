"""Full original/Hopf Spin16 incidence on exact saved REAL geometry germs.

No vertical mode, graded bundle, physical state, or exterior is selected.
The independent eight-dimensional metric/Christoffel calculation retains
both complete S3 coframes and all time/shift/radial rotation contacts.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import sys
import numpy as np


ROOT=Path(__file__).resolve().parents[1]
KEYS=('value','x','y','xy')
NAMES=('N','C','A','B','beta','np','cp','ap','bp','betap','la','lb','lc')
EXPECTED='9a132366d729c85ea1d83815a5482fbf6352b117507e9f447abb4c3b7534739d'


def maximum(a):return float(np.max(abs(a)))


def epsilon():
    e=np.zeros((3,3,3))
    for i in range(3):e[i,(i+1)%3,(i+2)%3]=1;e[i,(i+2)%3,(i+1)%3]=-1
    return e


def independent_adapted_tetrad(f,theta_t,theta_r):
    """Literal rotated coframe/metric Christoffels, no KK/spin formula."""
    N,C,A,B,z=(float(f[n]['value'].real)for n in('N','C','A','B','beta'))
    v={n:float(f[n]['value'].real)for n in NAMES}
    e=epsilon();eta=np.diag([1]+[-1]*7)
    original=np.diag([N,C,A,A,A,B,B,B]);original[1,0]=C*z
    dt=np.diag([0,C*v['lc'],A*v['la'],A*v['la'],A*v['la'],B*v['lb'],B*v['lb'],B*v['lb']]);dt[1,0]=C*v['lc']*z
    dr=np.diag([N*v['np'],C*v['cp'],A*v['ap'],A*v['ap'],A*v['ap'],B*v['bp'],B*v['bp'],B*v['bp']]);dr[1,0]=C*(v['cp']*z+v['betap'])
    dc=np.zeros((8,8,8));dc[0]=dt;dc[1]=dr
    for offset,radius in((2,A),(5,B)):
        for i in range(3):
            for j in range(3):
                for k in range(3):dc[offset+j,offset+i,offset+k]=-radius*e[i,j,k]
    L=np.hypot(A,B);c,s=B/L,A/L;rot=np.eye(8);Rt=np.zeros((8,8));Rr=np.zeros((8,8))
    for a in range(3):
        h,i=a+2,a+5;rot[h,h]=rot[i,i]=c;rot[h,i]=-s;rot[i,h]=s
        derivative=np.array([[-s,-c],[c,-s]])
        for D,rate in((Rt,theta_t),(Rr,theta_r)):D[np.ix_([h,i],[h,i])]=float(np.real(rate))*derivative
    cof=rot@original;derivative=np.einsum('ab,mbc->mac',rot,dc)
    derivative[0]+=Rt@original;derivative[1]+=Rr@original
    metric=cof.T@eta@cof;dg=np.array([d.T@eta@cof+cof.T@eta@d for d in derivative])
    christoffel=np.zeros((8,8,8))
    for mu in range(8):
        for nu in range(8):christoffel[:,mu,nu]=np.linalg.solve(metric,.5*np.array([dg[mu,j,nu]+dg[nu,j,mu]-dg[j,mu,nu]for j in range(8)]))
    inv=np.linalg.inv(cof);upper=np.array([(cof@christoffel[:,mu,:]-derivative[mu])@inv for mu in range(8)])
    lower=np.einsum('ab,mbc->acm',eta,upper)
    tetrad=np.array([derivative[mu]-cof@christoffel[:,mu,:]+upper[mu]@cof for mu in range(8)])
    return dict(coframe=cof,inverse=inv,lower_coordinate=lower,tetrad=tetrad,metric=metric)


def _real_exact(a,name):
    a=np.asarray(a)
    if not np.isfinite(a).all()or(np.iscomplexobj(a)and np.any(a.imag!=0)):
        raise ValueError(name+': exact saved REAL values required, no complex projection')
    return a.real if np.iscomplexobj(a)else a


def execute(repository,output):
    root,out=Path(repository).resolve(),Path(output)
    if out.exists():raise FileExistsError('Keep previous runs and source receipts')
    sys.path.insert(0,str(root/'src'));sys.path.insert(0,str(root/'audits'))
    from bind_muon_real_changing_gauge_transport_20261016 import archive_bytes
    from bhsm.interface.muon_m8_original_hopf_spin_lift import m8_original_hopf_spin_lift_jets
    from bhsm.interface.muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace
    from bhsm.interface.muon_holomorphic_normal_geometry import _geometry_variables,_fields
    from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
    base=root/'artifacts/muon_real_changing_gauge_transport_20261016'
    raw=archive_bytes(base,'stable_time6_run_1/changing_forms.npz')
    if sha256(raw).hexdigest()!=EXPECTED:raise ValueError('Preserved real snapshot bytes changed')
    with np.load(BytesIO(raw),allow_pickle=False)as z:
        saved={side:tuple(_real_exact(z[side+'_radial32_'+name].copy(),side+name)for name in('raw','rawtime','temporal_coordinate_time'))for side in('incoming','outgoing')}
    gamma5=full_d5_localized_lepton_trace()['gamma5D_particle'][[0,4,1,2,3]]
    arrays={};records=[]
    for side,(states,rates,times)in saved.items():
        for ti in(0,6,11):
            state,rate=states[ti],rates[ti]
            if not np.array_equal(rate[:37],state[37:74])or np.any(rate[74:98]!=0):raise ValueError('Actual affine q/v and held lapse/shift multiplier germ required')
            q,v,m,*_=_geometry_variables(state[:100],differentiate=True)
            x=rate[:100];y=np.eye(100)[25]
            for chi in(.13,.37,.69):
                fields=_fields(12,q,v,m,type(q[0]).constant(chi,100))
                f={}
                for name in NAMES:
                    a=fields[name]
                    # Source derivatives are analytic derivatives at the
                    # fixed ORIGINAL chi point; no material point motion.
                    f[name]=dict(value=np.asarray(_real_exact(a.value,name),complex),
                        x=np.asarray(a.gradient@x,complex),y=np.asarray(a.gradient@y,complex),xy=np.asarray(x@a.hessian@y,complex))
                o=m8_original_hopf_spin_lift_jets(f,gamma5_base=gamma5)
                independent=independent_adapted_tetrad(f,o['angle_coordinate_time']['value'],o['angle_coordinate_chi']['value'])
                G=o['gamma_original_and_fixed_adapted_slots'];pairs=np.einsum('aij,bjk->abik',G,G)
                spin=.25*np.einsum('abm,abij->mij',independent['lower_coordinate'],pairs)
                body=1j*sum(np.einsum('A,Aij->ij',independent['inverse'][mu],G)@spin[mu]for mu in range(8))
                prefix=f'{side}_time{ti}_chi{chi:.2f}'
                arrays[prefix+'_raw100']=state[:100];arrays[prefix+'_raw100_x']=x;arrays[prefix+'_raw100_y']=y
                arrays[prefix+'_independent_adapted_coframe']=independent['coframe']
                arrays[prefix+'_independent_adapted_spin_connection_coordinate']=spin
                arrays[prefix+'_independent_adapted_body']=body
                for name,a in f.items():arrays[prefix+'_field_'+name]=np.array([a[k]for k in KEYS])
                for name in('angle','angle_coordinate_time','angle_coordinate_chi','S','analytic_inverse','coframe_rotation','spin_connection_time','spin_connection_chi',
                    'time_coordinate_principal','chi_coordinate_principal','original_body','transformed_original_body','adapted_Cartan_KK_body','horizontal_spin_body','vertical_spin_body',
                    'vertical_horizontal_spin_connection_body','KK','normalized_full_body','unit_U_principal','unit_V_principal'):
                    arrays[prefix+'_'+name]=np.array([o[name][k]for k in KEYS])
                for name in('gamma_original_and_fixed_adapted_slots','boost_free_spatial_generators','vertical_horizontal_spin_generators'):arrays[name]=o[name]
                record=dict(side=side,time_index=ti,coordinate_time=float(times[ti]),original_chi=chi,
                    independent_full8D_Lorentz_metric_Cartan_body_absolute=maximum(body-o['transformed_original_body']['value']),
                    independent_full8D_tetrad_absolute=maximum(independent['tetrad']),
                    independent_full8D_spin_metric_antisymmetry=maximum(independent['lower_coordinate']+independent['lower_coordinate'].swapaxes(0,1)),
                    all_supplied_source_body_contacts={k:maximum(o['transformed_body_minus_adapted_body'][k])for k in KEYS},
                    all_original_u_v_principal_contacts={k:maximum(o['transformed_principal_minus_adapted'][k])for k in KEYS},
                    analytic_inverse_contacts={k:maximum(o['spin_inverse_rows'][k])for k in KEYS},
                    ordered_commuting_spin_product_absolute=maximum(o['finite_gamma_ordered_product_difference']),
                    real_base_spin_unitarity_absolute=maximum(o['value_unitarity_rows']),
                    angle=float(o['angle']['value'].real),angle_time=float(o['angle_coordinate_time']['value'].real),angle_chi=float(o['angle_coordinate_chi']['value'].real),
                    KK_norm=float(np.linalg.norm(o['KK']['value'])),vertical_horizontal_spin_connection_norm=float(np.linalg.norm(o['vertical_horizontal_spin_connection_body']['value'])),
                    time_shift_chi_principal_norm=float(np.linalg.norm(o['chi_coordinate_principal']['value']-1j*G[1]/f['C']['value'])))
                records.append(record)
    pins={Path(__file__).resolve().relative_to(root).as_posix():sha256(Path(__file__).read_bytes()).hexdigest()}
    for name,module in list(sys.modules.items()):
        p=getattr(module,'__file__',None)
        if p and(name.startswith('bhsm')or name.startswith('bind_muon_'))and Path(p).is_relative_to(root):pins[Path(p).relative_to(root).as_posix()]=sha256(Path(p).read_bytes()).hexdigest()
    inputs={};original=base/'stable_time6_run_1/changing_forms.npz'
    if original.exists():inputs[original.relative_to(root).as_posix()]=sha256(original.read_bytes()).hexdigest()
    else:
        recipe=base/'exact_archive_reconstruction.json';inputs[recipe.relative_to(root).as_posix()]=sha256(recipe.read_bytes()).hexdigest()
        for part in json.loads(recipe.read_bytes())['stable_time6_run_1/changing_forms.npz']['chunks']:
            p=base/part['path'];b=p.read_bytes()
            if len(b)!=part['bytes']or sha256(b).hexdigest()!=part['sha256']:raise ValueError('Exact raw chunk changed')
            inputs[p.relative_to(root).as_posix()]=part['sha256']
    result=dict(classification='REAL_ORIGINAL_TO_HOPF_FULL_GEOMETRIC_SPIN16_DIFFERENTIAL_INCIDENCE',records=records,
        jet_order=KEYS,field_order=NAMES,source_pins=dict(sorted(pins.items())),raw_input_pins=dict(sorted(inputs.items())),actual_input_archive_sha256=EXPECTED,
        incidence='psi_ad=S psi_original; S=exp(theta sum Gamma_u,a Gamma_v,a/2); theta=atan2(A,B)',
        source_axes='x=stored affine raw100 coordinate-time tangent, y=e25, xy_raw=0; fixed original chi',
        coefficient_background='Historical REAL one-cell numerical seeds, not a solved physical mean',
        complete_decomposition='density + horizontal spin + vertical spin + vertical horizontal-spin connection + full ordered KK',
        full_original_u_v_operator_directions_retained=True,associated_mode_projection_selected=False,complement_set_zero=False,
        mode_or_fibre_resolvent_complement_evaluated=False,native_grading_or_SM_carrier_identified=False,
        microscopic_stratified_operator_or_physical_exterior_solved=False,physical_energy_or_field_derivative_pass=False,
        coupled_corrections=0,spin_state_normalized=False,physical_muon_moment=None)
    out.mkdir(parents=True);_compressed_npz(out/'spin_lift.npz',arrays)
    result['numerical_sha256']=sha256((out/'spin_lift.npz').read_bytes()).hexdigest()
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(records=len(records),numerical_sha256=result['numerical_sha256'],max_independent_body=max(r['independent_full8D_Lorentz_metric_Cartan_body_absolute']for r in records))))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repository',default=str(ROOT));p.add_argument('--output',required=True);a=p.parse_args();execute(a.repository,a.output)
