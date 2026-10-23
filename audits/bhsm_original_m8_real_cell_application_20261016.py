"""Original-frame geometric M8 expression on actual REAL saved cell samples.

No SM twisting/statistics, global native domain or physical state is
selected. This evaluates the source geometric block before a Hopf frame
change, with all eight directions and supplied independent source jets.
"""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.muon_original_m8_geometric_expression import (
    JETS, SCALARS, original_m8_geometric_expression_jets,
    original_left_maurer_coefficient_maps, apply_original_m8_expression_jets,
    original_m8_ordered_weak_jets)
from bhsm.interface.muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace
from bhsm.interface.muon_intrinsic_scalar_discretization import scalar_s3_discretization
from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase,profile_preserving_raw_sample
from bhsm.interface.muon_holomorphic_normal_geometry import _geometry_variables,_fields
from bhsm.interface.muon_parent_retarded_hypercharge import WALL
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz

PHASES=dict(incoming='artifacts/muon_finite_normal_phase_20261011/incoming_run_1',
            outgoing='artifacts/muon_inherited_finite_normal_phase_20261011/run_1')


def compare(a,b):
    absolute=float(np.max(abs(a-b)))
    return dict(absolute=absolute,scaled=absolute/max(1.,float(np.max(abs(a))),float(np.max(abs(b)))))


def geometry(raw,rawtime,rho):
    if raw.dtype.kind!='f' or rawtime.dtype.kind!='f':
        raise ValueError('actual real state/time arrays required; no projection')
    q,v,m,delta,wall_rate,wall,Cstar=_geometry_variables(raw[:100])
    jac=wall/WALL;chi=rho*jac
    f=_fields(12,q,v,m,chi)
    N,C,A,B,beta=(f[k] for k in ('N','C','A','B','beta'))
    h0=(f['lc']+3*f['la']+3*f['lb']-beta*(f['cp']+3*f['ap']+3*f['bp'])-f['betap'])/(2*N)
    hr=(f['np']+3*f['ap']+3*f['bp'])/(2*C)
    values=dict(zip(SCALARS,(N,C*jac,A,B,(beta+rho*wall_rate/WALL)/jac,h0,hr,N*C*jac*A**3*B**3)))
    c={}
    for name,a in values.items():
        c[name]=dict(value=np.array([a.value]),x=np.array([a.gradient@rawtime[:100]]),
            y=np.array([a.gradient[25]]),xy=np.array([rawtime[:100]@a.hessian[:,25]]))
        if any(np.any(a.imag!=0) for a in c[name].values()):
            raise ValueError('real geometric/source chart left the real branch: '+name)
    for name in ('lapse','radial_coframe','orbit_A','orbit_B','volume_density'):
        if c[name]['value'][0].real<=0:raise ValueError('positive real coframe required')
    return c


def trial(rho,t,lo,hi,d):
    h=hi-lo;theta=(t-(hi+lo)/2)/h;r=rho/WALL
    F=np.array([1.,theta,1+.2*theta*theta]);Ft=np.array([0.,1/h,.4*theta/h]);Ftt=np.array([0.,0.,.4/h**2])
    R=np.array([1+.2*r,.7-.1*r+.04*r*r,.2+r*(1-r)])
    Rr=np.array([.2,-.1+.08*r,1-2*r])/WALL
    rows=np.arange(1,d+1)[:,None];cols=np.arange(2,5)[None,:]
    B=(np.cos(.127*rows*cols)+1j*np.sin(.193*rows*(cols+.17)))/np.sqrt(d)
    def j(value,x):return dict(value=value[None],x=x[None],y=np.zeros((1,)+value.shape,complex),xy=np.zeros((1,)+value.shape,complex))
    V=j(B*(F*R),B*(Ft*R));Vr=j(B*(F*Rr),B*(Ft*Rr));Vt=j(B*(Ft*R),B*(Ftt*R))
    lrow=np.arange(2,8)[:,None];fib=np.arange(1,d+1)[None,:]
    L=(np.cos(.151*lrow*fib)+1j*np.sin(.103*(lrow+.27)*fib))/np.sqrt(d)
    return V,Vr,Vt,j((1+.13*r+.1*theta)*L,.1/h*L)


def literal(c,U,V,G,trial_maps):
    """Direct original eight-direction action, not an assembled coefficient."""
    hu,hv=U.shape[1],V.shape[1]
    u,ur,ut=[a['value'][0].reshape(16,hu,hv,3) for a in trial_maps[:3]]
    N,C,A,B,z,h0,hr,mu=(c[k]['value'][0] for k in SCALARS)
    apply=lambda g,a:np.einsum('ij,juvk->iuvk',g,a)
    dt=(ut-z*ur)/N+h0*u
    spatial=1j*apply(G[1],ur/C+hr*u)
    for a in range(3):
        spatial+=1j*apply(G[a+2],np.einsum('ab,ibvk->iavk',U[a],u))/A
        spatial+=1j*apply(G[a+5],np.einsum('ab,iubk->iuak',V[a],u))/B
    spatial+=1.5j*apply(G[2]@G[3]@G[4],u)/A+1.5j*apply(G[5]@G[6]@G[7],u)/B
    return ((1j*apply(G[0],dt)+spatial).reshape(1,-1,3),
            (dt-apply(G[0],spatial)).reshape(1,-1,3))


def execute(output,radial_order=4):
    out=Path(output).resolve()
    if out.exists():raise FileExistsError('preserve independently executed applications')
    arrays={};records=[];pins={}
    gamma=full_d5_localized_lepton_trace()['gamma5D_particle'][[0,4,1,2,3]]
    bands={n:scalar_s3_discretization(n) for n in (0,1)}
    maps={n:original_left_maurer_coefficient_maps(a['angular_derivative_matrices'],a['scalar_labels']) for n,a in bands.items()}
    qr,wr=np.polynomial.legendre.leggauss(radial_order);rho=np.r_[(qr+1)*WALL/2,WALL];rw=wr*WALL/2
    qt,wt=np.polynomial.legendre.leggauss(2)
    for side,path in PHASES.items():
        phase=load_profile_preserving_phase(path,repository=ROOT);pins.update(phase['input_hashes'])
        span=float(phase['receipt']['span']);lo,hi=min(0.,span),max(0.,span)
        times=lo+(qt+1)*(hi-lo)/2;tw=wt*(hi-lo)/2
        for ti,t in enumerate(times):
            sample=profile_preserving_raw_sample(phase,float(t));raw=sample['raw_fields'];rawtime=sample['raw_coordinate_time_derivative']
            arrays[f'{side}_t{ti}_raw']=raw;arrays[f'{side}_t{ti}_rawtime']=rawtime
            for ri,r in enumerate(rho):
                c=geometry(raw,rawtime,float(r))
                base=f'{side}_t{ti}_r{ri}'
                for name,j in c.items():
                    for key,a in j.items():arrays[f'{base}_{name}_{key}']=a
                for nu,nv in ((0,0),(0,1),(1,0),(1,1)):
                    U,V=maps[nu],maps[nv]
                    op=original_m8_geometric_expression_jets(c,U,V,gamma5_base=gamma)
                    probes=trial(float(r),float(t),lo,hi,op['width']);G=op['gamma8_original']
                    name=f'{base}_u{nu}_v{nv}';wanted=literal(c,U,V,G,probes)
                    errors={}
                    for placement,reference in zip(('lorentz','plus_product'),wanted):
                        acted=apply_original_m8_expression_jets(op,*probes[:3],placement=placement)
                        errors[placement]=compare(acted['value'],reference)
                        for key,a in acted.items():arrays[f'{name}_{placement}_{key}']=a
                    weight=(tw[ti]*rw[ri]*(2*np.pi**2)**2 if ri<radial_order else 1.)
                    weights={key:np.array([weight if key=='value' else 0.]) for key in JETS}
                    weak=original_m8_ordered_weak_jets(op,*probes[:3],independent_left=probes[3],coordinate_weights=weights,placement='lorentz')
                    for key,a in weak.items():arrays[f'{name}_ordered_weak_{key}']=a
                    records.append(dict(side=side,coordinate_time=float(t),rho=float(r),actual_wall=(ri==radial_order),
                        u_level=nu,v_level=nv,full_geometric_spin_rows=op['width'],source_value_errors=errors,
                        Haar_weighted_spacetime_node=(ri<radial_order),
                        wall_record_is_diagnostic_not_an_extra_volume_node=(ri==radial_order),
                        source_jet_axes=('inside_saved_cell_time','declared_qb0_raw25_partial'),
                        mean_time_spin_contact=float(abs(c['geometric_time_contact']['value'][0])),
                        radial_spin_contact=float(abs(c['geometric_radial_contact']['value'][0])),
                        u_round_spin_norm=float(np.linalg.norm(op['original_u_spin_triple'])),
                        v_round_spin_norm=float(np.linalg.norm(op['original_v_spin_triple']))))
                    del op
    arrays.update(radial_points=rho,radial_weights=rw,gamma5_base=gamma)
    for n,a in maps.items():arrays[f'original_left_Maurer_n{n}']=a
    for name,module in list(sys.modules.items()):
        p=getattr(module,'__file__',None)
        if name.startswith('bhsm.') and p and Path(p).is_relative_to(ROOT):pins[Path(p).relative_to(ROOT).as_posix()]=sha256(Path(p).read_bytes()).hexdigest()
    pins[Path(__file__).relative_to(ROOT).as_posix()]=sha256(Path(__file__).read_bytes()).hexdigest()
    worst=max(e['scaled'] for r in records for e in r['source_value_errors'].values())
    if worst>3e-12:raise ArithmeticError('literal original M8 expression mismatch')
    out.mkdir(parents=True);_compressed_npz(out/'application.npz',arrays)
    if (out/'application.npz').stat().st_size>=10*1024*1024:raise ValueError('archive exceeds10MiB')
    result=dict(classification='ACTUAL_REAL_ORIGINAL_FRAME_M8_GEOMETRIC_EXPRESSION_FOURJET_APPLICATION',
        records=records,radial_order=radial_order,time_order=2,worst_literal_value_scaled=worst,
        original_angular_coframe='left Maurer u/v, positive commutators and plus spin triples',
        complete_spin16_retained=True, all_eight_coordinate_directions_retained=True,
        no_adapted_KK_spin_frame_body_mixed=True,
        internal_twist_or_finite_native_endomorphism_evaluated=False,
        native_statistics_or_SM_multiplicity_selected=False,
        native_full_graded_operator_and_domain_completed=False,
        spectral_eigenmode_or_physical_spin_selected=False,
        source_xy_is_physical_E_B_or_outgoing_response=False,
        moving_domain_endpoint_contacts_evaluated=False,
        parent_background_is_provisional_saved_real_iterate=True,
        radial_or_angular_or_physical_convergence=False,full_physical_derivative_at_2e_minus10=False,
        coupled_corrections=0,physical_muon_magnetic_moment=None,
        input_and_source_sha256=dict(sorted(pins.items())),
        numerical_sha256=sha256((out/'application.npz').read_bytes()).hexdigest())
    (out/'result.json').write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(records=len(records),worst_literal_value_scaled=worst,numerical_sha256=result['numerical_sha256'])))
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True);p.add_argument('--radial-order',type=int,default=4)
    a=p.parse_args();execute(a.output,a.radial_order)
