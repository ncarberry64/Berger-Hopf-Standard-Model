"""Compose all15 existing finite positive-reference forms from saved MP blocks.

Matched radial64:time8, radial128:time8, radial128:time12 rules are compared.
Common kinetic/Gram sums are formed before comparison, retaining cancellation.
This does not construct the physical native operator or outgoing domain.
"""
from __future__ import annotations
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import mpmath as mp
import numpy as np
from scipy import sparse
from flint import arb,arb_mat,ctx

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'audits')]
import bhsm_changing_lorenz_tensor_precision_20261016 as tensor
import bhsm_changing_yang_mills_mp_values_20261016 as ym
import bhsm_scalar_wall_mp_complete_forms_20261016 as wall
from bhsm_finite_lorenz_projector_ball_20261016 import decode,dyadic
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz

GUARDS={
    'audits/bhsm_changing_lorenz_tensor_precision_20261016.py':'a0fafae124d00be5954e0284fb2ed5891f645b4955af211a53a2e7494b39238a',
    'audits/bhsm_changing_yang_mills_mp_values_20261016.py':'a70200780782da13fbdbe4700c939c93b3e2487fd9edf14f81bbe14601d184b3',
    'audits/bhsm_scalar_wall_mp_complete_forms_20261016.py':'771f1129ff19d57484e9950adc3fbc288d7144b92baefff53dd69f7a3df612d9',
    'audits/bhsm_finite_lorenz_projector_ball_20261016.py':'c409d5247ed17ce3c2279aeea294eb2a0baa45f47b857b6083ecd3e95ca054da',
}
NAMES=('one_form_Hessian_per_kappa','one_form_Gram_per_kappa','curvature_contact_per_kappa',
    'FP_Hessian_per_kappa','ghost_Gram_per_kappa','weak_Lorenz','weak_gradient_pairing',
    'finite_Lorenz_slice_projector',*wall.FORM_NAMES,'common_kinetic_Hessian','common_Gram','finite_Lorenz_fixing')


def exact(z,key):
    a=z[key]
    return np.array([decode(x) for x in a.flat],dtype=object).reshape(a.shape)


def entries(a):
    return {(i,j):dyadic(a[i,j]) for i,j in zip(*np.nonzero(a))}


def from_ball_matrix(a):
    return {(i,j):a[i,j] for i in range(a.nrows()) for j in range(a.ncols()) if not a[i,j].is_zero()}


def ball_matrix(a):
    return arb_mat(*a.shape,[dyadic(x) for x in a.flat])


def add(a,b,scale=arb(1)):
    out=dict(a)
    for k,v in b.items():out[k]=out.get(k,arb(0))+scale*v
    return {k:v for k,v in out.items() if not v.is_zero()}


def compare(a,b):
    maximum=arb(0);scaled=arb(0);chosen=(0,0)
    for k in sorted(a.keys()|b.keys()):
        x,y=a.get(k,arb(0)),b.get(k,arb(0));d=abs(y-x)
        den=max(arb(1),abs(x).lower(),abs(y).lower());ratio=d/den
        if d.upper()>maximum.upper():maximum=d
        if ratio.upper()>scaled.upper():scaled,chosen=ratio,k
    return dict(max_absolute_upper=float(np.nextafter(float(maximum.upper()),np.inf)),
        max_entry_scaled_upper=float(np.nextafter(float(scaled.upper()),np.inf)),index=list(map(int,chosen)),
        old_entry=str(a.get(chosen,arb(0))),new_entry=str(b.get(chosen,arb(0))),
        checked_union_support_entries=len(a.keys()|b.keys()),
        denominator_lower_bound='max(1,abs(old).lower,abs(new).lower) on each entry; complement exactly zero',
        scope='ARB384 composition of finite saved MP80 operands and explicit serialization intervals; excludes upstream coefficient/quadrature error')


def save(arrays,name,values,shape):
    keys=sorted(values);centers=[float(values[k].mid()) for k in keys]
    a=sparse.coo_matrix((centers,([k[0] for k in keys],[k[1] for k in keys])),shape=shape).tocsr()
    a.eliminate_zeros()
    arrays[name+'_data'],arrays[name+'_indices'],arrays[name+'_indptr'],arrays[name+'_shape']=a.data,a.indices,a.indptr,np.array(shape)


def execute(moment64,time_forms,value_forms,ordinary8,ordinary12,wall_file,ym_forms,projectors,output):
    out=Path(output)
    if out.exists():raise FileExistsError('Preserve each independent composition')
    for rel,h in GUARDS.items():
        if sha256((ROOT/rel).read_bytes()).hexdigest()!=h:raise ValueError('Frozen owner changed: '+rel)
    out.mkdir(parents=True);pins={};records=[]
    (out/'executed_producer.py').write_bytes(Path(__file__).read_bytes())
    def pin(path):
        path=Path(path);raw=path.read_bytes();pins[str(path.resolve())]=sha256(raw).hexdigest();return path
    ordinary={t:json.loads(pin(p).read_bytes()) for t,p in ((8,ordinary8),(12,ordinary12))}
    wall_file=pin(wall_file);moment64=pin(moment64)
    with mp.workdps(80):
        oldprec=ctx.prec;ctx.prec=384
        try:
            for side in ('incoming','outgoing'):
                previous=None
                with np.load(pin(Path(value_forms)/f'{side}_radial128/forms.npz'),allow_pickle=False) as ez:
                    E=ez['EW4_real_angular_derivatives'].copy()
                angular=ym.products(E);wall_angular=wall.angular_factors(E)
                scalar={}
                with np.load(wall_file,allow_pickle=False) as wz:
                    if not np.array_equal(E,wz['EW4_real_harmonic_derivatives']):raise ValueError('Same held harmonic basis required')
                    for t in (8,12):
                        scalar[t]={}
                        for name in wall.FORM_NAMES:
                            s=wall.assemble(exact(wz,f'{side}_time{t}_{name}_coefficient_exact_MP_tuple'),wall_angular)
                            # Reproduce every saved rounded scalar entry; no shadow replacement.
                            observed=tensor.load_matrix(wz,f'{side}_time{t}_{name}')
                            check=np.zeros((1200,1200))
                            for k,v in s.items():check[k]=float(v)
                            if not np.array_equal(check,observed):raise ValueError('Scalar tuple lift disagrees with saved full form')
                            scalar[t][name]={k:dyadic(v) for k,v in s.items()}
                for radial,t in ((64,8),(128,8),(128,12)):
                    print(json.dumps(dict(stage='compose_actual_all15',side=side,radial=radial,time=t)),flush=True)
                    p=moment64 if radial==64 else pin(Path(time_forms)/f'{side}_time{t}/forms.npz')
                    prefix=side+'_' if radial==64 else ''
                    with np.load(p,allow_pickle=False) as mz:
                        moments={name:exact(mz,prefix+'moment_'+name+'_exact_MP_tuple') for name in tensor.tensors()}
                        B=tensor.assemble(moments,E)
                        if not np.array_equal(tensor.as_float(B),tensor.load_matrix(mz,prefix+'B')):raise ValueError('Complete B tuple lift changed')
                        if radial==64:
                            goo=exact(mz,prefix+'moment_ordinary_Gram10_exact_MP_tuple')
                            Goo={(i,j):dyadic(goo[i,j]) for i in range(10) for j in range(10) if goo[i,j]}
                        else:
                            r=next(r for r in ordinary[t]['records'] if r['side']==side and r['radial_order']==128)
                            if r['temporal_order_per_half']!=t or r['anchored_response_order']!=96:
                                raise ValueError('Matched ordinary Gram time and response rule required')
                            Goo={}
                            for i,row in enumerate(r['all100_unrounded_MP_entries']):
                                for j,value in enumerate(row):
                                    v=arb(value)
                                    if not v.is_zero():Goo[i,j]=v+arb(0,abs(v).upper()*arb('1e-62'))
                    ymfile=pin(Path(ym_forms)/f'{side}_radial{radial}_time{t}/forms.npz')
                    with np.load(ymfile,allow_pickle=False) as yz:
                        if not np.array_equal(E,yz['EW4_real_angular_derivatives']):raise ValueError('Yang--Mills harmonic epoch mismatch')
                        sq=ym.lift(exact(yz,'square_coefficient_upper_exact_MP_tuple'),angular)
                        cc=ym.lift(exact(yz,'contact_coefficient_upper_exact_MP_tuple'),angular);kin=sq+cc
                        if not np.array_equal(tensor.as_float(kin),tensor.load_matrix(yz,'one_form_Hessian')):raise ValueError('Full YM Hessian tuple lift changed')
                        if not np.array_equal(tensor.as_float(cc),tensor.load_matrix(yz,'curvature_contact')):raise ValueError('Full contact tuple lift changed')
                        K,C=entries(kin),entries(cc)
                    G={}
                    for (i,j),v in Goo.items():
                        for h in range(80):G[80*i+h,80*j+h]=v
                    for i,j in zip(*np.nonzero(B[:,:1120])):
                        v=dyadic(B[i,j]);G[800+i,j]=v
                        if j<800:G[j,800+i]=v
                    FP={(i,j):v for (ii,jj),v in G.items() if ii>=800 and jj>=800 for i,j in [(ii-800,jj-800)]}
                    gg={}
                    for i in range(4):
                        for j in range(4):
                            for h in range(80):
                                v=moments['ghost_G4'][i,j]
                                if v:gg[i*80+h,j*80+h]=dyadic(v)
                    # Pure ghost norm inverse, distinct from the FP kinetic inverse.
                    F=tensor.apply_inverse(tensor.inverse4(moments['ghost_G4']),B)
                    Bb,Fb=ball_matrix(B),ball_matrix(F)
                    fixing=from_ball_matrix(dyadic(tensor.number(tensor.MAXWELL_TO_CAP))*(Bb.transpose()*Fb))
                    folder=Path(projectors)/f'{side}_radial{radial}_time{t}'
                    pr=json.loads(pin(folder/'result.json').read_bytes())
                    if pr['input_moment_sha256']!=sha256(p.read_bytes()).hexdigest():raise ValueError('Projector moment epoch mismatch')
                    if pr['input_E_sha256']!=sha256((Path(value_forms)/f'{side}_radial128/forms.npz').read_bytes()).hexdigest():raise ValueError('Projector E epoch mismatch')
                    pf=pin(folder/'finite_projector_action.npz')
                    if sha256(pf.read_bytes()).hexdigest()!=pr['numerical_sha256']:raise ValueError('Projector bytes changed')
                    Pi={(i,i):arb(1) for i in range(1200)}
                    with np.load(pf,allow_pickle=False) as pz:
                        hi,lo=pz['X_high'],pz['X_low'];radius=arb(pr['X_high_low_max_entry_conversion_error_upper'])
                        if hi.shape!=(320,1200) or lo.shape!=hi.shape:raise ValueError('Full projector action required')
                        for i in range(320):
                            for j in range(1200):
                                v=arb(float(hi[i,j]))+arb(float(lo[i,j]))+arb(0,radius)
                                key=(800+i,j);Pi[key]=Pi.get(key,arb(0))-v
                    kappa=dyadic(tensor.number(tensor.MAXWELL_TO_CAP))
                    family=dict(one_form_Hessian_per_kappa=(K,(1120,1120)),one_form_Gram_per_kappa=(G,(1120,1120)),
                        curvature_contact_per_kappa=(C,(1120,1120)),FP_Hessian_per_kappa=(FP,(320,320)),
                        ghost_Gram_per_kappa=(gg,(320,320)),weak_Lorenz=(entries(F),(320,1200)),
                        weak_gradient_pairing=(entries(B),(320,1200)),finite_Lorenz_slice_projector=(Pi,(1200,1200)))
                    family.update({name:(a,(1200,1200)) for name,a in scalar[t].items()})
                    family.update(common_kinetic_Hessian=(add(scalar[t]['scalar_kinetic_Hessian'],K,kappa),(1200,1200)),
                        common_Gram=(add(scalar[t]['scalar_Gram'],G,kappa),(1200,1200)),finite_Lorenz_fixing=(fixing,(1200,1200)))
                    if set(family)!=set(NAMES) or len(family)!=15:raise ValueError('All original15 forms required')
                    comparison=None if previous is None else {name:compare(previous[name][0],family[name][0]) for name in NAMES}
                    arrays={}
                    for name,(values,shape) in family.items():save(arrays,name,values,shape)
                    target=out/f'{side}_radial{radial}_time{t}';target.mkdir()
                    _compressed_npz(target/'all15_forms.npz',arrays)
                    record=dict(side=side,radial_order=radial,time_order_per_half=t,
                        comparison_axis=None if previous is None else ('radial_at_fixed_time8' if radial==128 and t==8 else 'time8_to12_at_fixed_radial128'),
                        comparisons=comparison,all15_scaled_rule_pass=None if comparison is None else all(v['max_entry_scaled_upper']<=2e-10 for v in comparison.values()),
                        numerical_sha256=sha256((target/'all15_forms.npz').read_bytes()).hexdigest(),
                        numerical_archive_scope='Floating centers/readouts only; exact input tuples and explicit serialization intervals own reported comparison bounds',
                        dimensions={name:list(shape) for name,(_,shape) in family.items()},
                        scalar_potential_coefficients_assigned=False)
                    (target/'result.json').write_text(json.dumps(record,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
                    print(json.dumps(dict(stage='all15_case_complete',side=side,radial=radial,time=t,all15_scaled_rule_pass=record['all15_scaled_rule_pass'])),flush=True)
                    records.append(record);previous=family
        finally:ctx.prec=oldprec
    sources=dict(GUARDS)
    for name,module in list(sys.modules.items()):
        p=getattr(module,'__file__',None)
        if p and (name.startswith('bhsm.') or name.startswith('bhsm_')) and Path(p).is_relative_to(ROOT):sources[Path(p).relative_to(ROOT).as_posix()]=sha256(Path(p).read_bytes()).hexdigest()
    sources[Path(__file__).relative_to(ROOT).as_posix()]=sha256(Path(__file__).read_bytes()).hexdigest()
    for name,h in GUARDS.items():
        if sha256((ROOT/name).read_bytes()).hexdigest()!=h:raise ValueError('Consumed owner changed')
    result=dict(classification='MATCHED_FINITE_POSITIVE_REFERENCE_ALL15_MP_BLOCK_COMPOSITION',records=records,
        input_sha256=dict(sorted(pins.items())),source_and_owner_sha256=dict(sorted(sources.items())),
        component_lifts_arithmetic='MP80 on exact saved MP tuples; original rounded component arrays reproduced bitwise',
        composite_sums_comparisons_arithmetic='ARB384; ordinary65-digit decimal margin and saved projector high-low conversion intervals retained',
        ordinary_Gram_decimal_relative_serialization_radius='1e-62',
        common_kinetic_and_Gram_sum_before_comparison=True,common_YM_prefactor_applied_once_binary_hex=float(tensor.MAXWELL_TO_CAP).hex(),
        scalar_wall_has_no_radial_integration=True,no_field_history_recomputed=True,
        finite_all15_scaled_matched_rule_pass=all(r['all15_scaled_rule_pass'] for r in records if r['comparisons'] is not None),
        physical_radial_solution_convergence=False,physical_native_operator_or_outgoing_domain_selected=False,
        physical_energy_field_source_domain_derivative_pass=False,original_coupled_corrections=0,
        physical_normalized_muon_spins=None,physical_muon_magnetic_moment=None)
    (out/'result.json').write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(result_sha256=sha256((out/'result.json').read_bytes()).hexdigest())),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('moment64','time-forms','value-forms','ordinary8','ordinary12','wall-file','ym-forms','projectors','output'):p.add_argument('--'+name,required=True)
    a=p.parse_args();execute(a.moment64,a.time_forms,a.value_forms,a.ordinary8,a.ordinary12,a.wall_file,a.ym_forms,a.projectors,a.output)
