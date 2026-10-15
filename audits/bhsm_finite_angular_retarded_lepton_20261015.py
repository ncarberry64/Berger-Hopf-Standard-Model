"""Finite first-order angular lepton response on supplied retarded field cells.

All18 fibers and both gauge/H source channels are retained. This consumes a
declared finite field/time discretization; it does not construct the physical
formed-muon exterior or identify its temporal energy jet with Gamma_E.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
from io import BytesIO
import json
import math
import os
from pathlib import Path
import sys
import zipfile
os.environ['OPENBLAS_NUM_THREADS']='2'
os.environ['OMP_NUM_THREADS']='2'
import numpy as np
from scipy.linalg import expm


def encode(a):
    if isinstance(a,dict): return {k:encode(v) for k,v in a.items()}
    if isinstance(a,(list,tuple)): return [encode(x) for x in a]
    if isinstance(a,np.ndarray): return encode(a.tolist())
    if isinstance(a,(complex,np.complexfloating)): return [float(a.real),float(a.imag)]
    if isinstance(a,np.generic): return a.item()
    return a


def maximum(a): return float(np.max(abs(a)))


def relative(a,b): return float(np.linalg.norm(a)/np.linalg.norm(b))


def save(path,data):
    with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for key,value in sorted(data.items()):
            b=BytesIO();np.lib.format.write_array(b,np.asarray(value),allow_pickle=False)
            info=zipfile.ZipInfo(key+'.npy',(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(info,b.getvalue())


def exponential(a,order=12):
    result=np.eye(len(a),dtype=complex);term=result.copy()
    for k in range(1,order+1):
        term=term@a/k;result+=term
    return result


def duhamel(a,b,forcing,order=6):
    """Exact exponential moment through total degree6; scaled a,b <<1."""
    value=forcing.copy();s=forcing.copy();power=np.eye(len(b),dtype=complex)
    for n in range(1,order+1):
        power=power@b;s=a@s+forcing@power
        value+=s/math.factorial(n+1)
    return value


def run(root,angular,field,out):
    root,angular,field,out=map(lambda p:Path(p).resolve(),(root,angular,field,out))
    if out.exists():raise FileExistsError('preserve every actual finite response')
    sys.path.insert(0,str(root/'src'))
    from bhsm.interface.muon_native_dirac_hamiltonian import lepton_current_hilbert_representation
    from bhsm.interface.muon_native_product_factor_graph import lepton_unit_trace_gauge_representation
    from bhsm.interface.muon_continued_action_reality import _higgs_mass_realified
    pins={}
    def read(path):
        path=Path(path);pins[str(path)]=sha256(path.read_bytes()).hexdigest()
        if path.suffix=='.json':return json.loads(path.read_bytes())
        with np.load(path,allow_pickle=False)as z:return {k:z[k].copy()for k in z.files}
    md=read(field/'result.json');core=read(angular/'exact_angular_core.npz')
    for source in ('muon_native_dirac_hamiltonian','muon_native_product_factor_graph','muon_continued_action_reality'):
        path=root/f'src/bhsm/interface/{source}.py';pins[str(path)]=sha256(path.read_bytes()).hexdigest()
    current=lepton_current_hilbert_representation();alpha=current['alpha'];gens=lepton_unit_trace_gauge_representation()['generators']
    eout=core['right_body_derivatives_out_n012'];ein=core['right_body_derivatives_input_n01']
    gaunt=core['gaunt_out_n012_source_n1_input_n01']
    cap=np.zeros((14,4,14));cap[:,:,:5]=gaunt;cap[:5]=gaunt.transpose(2,1,0)
    assert maximum(cap[:,:,:5]-gaunt)<1e-14
    stages=[]
    source_root=root/'artifacts/muon_formed_weak_field_20261015/same_epoch_probe/run_2'
    for j in range(2):
        s=read(source_root/f'stage_{j:04d}_actual_unit_magnetic_source_and_direct_insertion.npz')
        R,N=s['wall_radius'].item(),s['wall_induced_lapse'].item();x=s['raw268'];connection=s['actual_background_wall_connection']
        omega=np.einsum('ac,cij->aij',connection[2:],gens)
        H18=(-1j*np.einsum('aij,ajk->ik',alpha,omega)+1.5*current['gamma5'])/R
        H18+=_higgs_mass_realified(x[260:264])-1j*np.einsum('c,cij->ij',connection[0],gens)/N
        Hout=np.kron(np.eye(14),H18)-1j*sum(np.kron(e,al)for e,al in zip(eout,alpha))/R
        Hin=np.kron(np.eye(5),H18)-1j*sum(np.kron(e,al)for e,al in zip(ein,alpha))/R
        vertices=np.zeros((24,18,18),complex);vertices[:4]=-1j*gens/N
        for a in range(3):vertices[8+4*a:12+4*a]=-1j*np.einsum('ij,cjk->cik',alpha[a],gens)/R
        vertices[20:]=np.array([_higgs_mass_realified(e)for e in np.eye(4)])
        stages.append(dict(N=N,Hout=Hout,Hin=Hin,vertices=vertices))
    # This is an exact sparsity property of the supplied fixed-Y operators,
    # checked on all original rows rather than imposed on small entries.
    intrinsic=[np.array([2*f,2*f+1,6+2*f,7+2*f,12+2*f,13+2*f])for f in range(3)]
    outs=[np.concatenate([18*h+i for h in range(14)])for i in intrinsic]
    ins=[np.concatenate([18*h+i for h in range(5)])for i in intrinsic]
    mask=np.zeros((252,252),bool)
    for ids in outs:mask[np.ix_(ids,ids)]=True
    assert all(not np.any(s['Hout'][~mask])for s in stages)
    paths=sorted(field.glob('cell_*_same_stage_retarded_n1_midpoint.npz'))
    if len(paths)!=md['steps']:raise ValueError('one actual field midpoint per cell required')
    original_steps=[]
    for j in range(2):
        original=read(root/f'artifacts/muon_fixed_parent_finite_shooting_20261012/run_1/trial_0000/stage_{j:04d}.npz')
        original_steps.append(original['coordinate_step'].item())
    duration=sum(original_steps)
    if duration.imag!=0 or duration.real<=0:raise ValueError('original finite real coordinate interval required')
    cells=[];dt=duration.real/len(paths)
    for k,path in enumerate(paths):
        z=read(path);j=int(z['stage']);s=stages[j]
        if abs(z['coordinate_time'].item()-(k+.5)*dt)>1e-21:raise ValueError('original20ns cell clocks differ')
        wall=z['wall_gauge80_and_natural_H16_high']+z['wall_gauge80_and_natural_H16_low']
        q=wall.reshape(24,4,3)
        local_g=np.einsum('chA,cij->Ahij',q[:20],s['vertices'][:20])
        local_h=np.einsum('chA,cij->Ahij',q[20:],s['vertices'][20:])
        rect=np.stack([np.einsum('ohx,Ahij->Aoixj',gaunt,v).reshape(3,252,90)for v in(local_g,local_h)])
        square=np.stack([np.einsum('ohx,Ahij->Aoixj',cap,v).reshape(3,252,252)for v in(local_g,local_h)])
        assert not np.any(square[:,:,~mask])
        cells.append(dict(stage=j,rect=rect,square=square,dt=dt))
    out.mkdir(parents=True)
    total=np.zeros((2,3,252,90),complex);energy=np.zeros_like(total);uout=np.zeros((252,252),complex);uin=np.zeros((90,90),complex)
    checks=[];responses=[];family_data=[]
    for fi,(oi,ii)in enumerate(zip(outs,ins)):
        x=np.eye(30,dtype=complex);y=np.eye(84,dtype=complex);response=np.zeros((2,3,84,30),complex);de=np.zeros_like(response)
        family_cells=[]
        for cell in cells:
            s=stages[cell['stage']];a=-1j*s['N']*dt*s['Hout'][np.ix_(oi,oi)];b=-1j*s['N']*dt*s['Hin'][np.ix_(ii,ii)]
            f=-1j*s['N']*dt*cell['rect'][:,:,oi][:,:,:,ii]
            v=exponential(a);w=exponential(b);j=duhamel(a,b,f)
            step_energy=1j*s['N']*dt
            de=step_energy*v@response+v@de+step_energy*j@x+j@(1j*sum(stages[c['stage']]['N']*dt for c in cells[:len(family_cells)])*x)
            response=v@response+j@x;x=w@x;y=v@y
            beta=max(np.sqrt(np.linalg.norm(a,1)*np.linalg.norm(a,np.inf)),
                     np.sqrt(np.linalg.norm(b,1)*np.linalg.norm(b,np.inf)))
            if beta>1e-2:raise ValueError('small finite-stage exponential bound failed')
            checks.append(dict(family=fi,cell=len(family_cells),scaled_generator_norm=beta,
                endpoint_exponential_relative=relative(v-expm(a),v),
                absolute_Duhamel_series_tail_bound=float(np.linalg.norm(f)*np.exp(2*beta)*(2*beta)**7/math.factorial(8))))
            family_cells.append(dict(a=a,square=-1j*s['N']*dt*cell['square'][:,:,oi][:,:,:,oi]))
        for ch in range(2):
            for ax in range(3):total[ch,ax][np.ix_(oi,ii)]=response[ch,ax];energy[ch,ax][np.ix_(oi,ii)]=de[ch,ax]
        uout[np.ix_(oi,oi)]=y;uin[np.ix_(ii,ii)]=x
        family_data.append(family_cells)
    proper=sum(stages[c['stage']]['N']*dt for c in cells)
    energy_identity=relative(energy-1j*proper*total,total*proper)
    # Fresh B differences on the finite square cap check its derivative at0.
    # At first order from n<=1 the complete n<=2 image is exact; cap errors at
    # higher B orders are not claimed to be physical finite-field solutions.
    fd_records=[]
    for channel in range(2):
        for axis in range(3):
            scale=sum(max(np.linalg.norm(f['square'][channel,axis],np.inf)for f in data)for data in family_data)
            if scale==0:raise ValueError('a supplied source channel unexpectedly vanished')
            h=.001/scale;fresh=np.zeros((252,90),complex)
            for fi,(oi,ii)in enumerate(zip(outs,ins)):
                embed=np.zeros((84,30),complex);embed[:30]=np.eye(30)
                values=[]
                for sign in(-2,-1,1,2):
                    state=embed.copy()
                    for f in family_data[fi]:state=exponential(f['a']+sign*h*f['square'][channel,axis])@state
                    values.append(state)
                derivative=(values[0]-8*values[1]+8*values[2]-values[3])/(12*h)
                fresh[np.ix_(oi,ii)]=derivative
            error=relative(fresh-total[channel,axis],total[channel,axis]);fd_records.append(dict(channel=['gauge','induced_H'][channel],axis=axis,
                numerical_coefficient_probe_step=h,relative_derivative_difference=error,
                numerical_scaled_exponent_target=.001,physical_field_strength_selected=False))
    if energy_identity>2e-10 or max(r['relative_derivative_difference']for r in fd_records)>2e-10:
        raise ArithmeticError('finite temporal lepton derivative control failed')
    save(out/'finite_angular_response.npz',dict(retarded_B_response_gauge=total[0],retarded_B_response_induced_H=total[1],
        retarded_B_response_energy_gauge=energy[0],retarded_B_response_energy_induced_H=energy[1],
        unperturbed_input_transfer=uin,unperturbed_output_transfer=uout,finite_complex_proper_duration=np.array(proper)))
    result=dict(classification='EVALUATED_FULL_ONE_INSERTION_ANGULAR_FINITE_HISTORY_LEPTON_RESPONSE_ON_SUPPLIED_GAUGE_H_FIELD_CELLS',
        field_discretization_steps=len(paths),field_original_row_bounds=md['original_row_upper_bounds'],
        gauge_response_norm=float(np.linalg.norm(total[0])),nonzero_induced_H_response_norm=float(np.linalg.norm(total[1])),
        finite_temporal_E_product_rule_relative=energy_identity,finite_B_derivative_checks=fd_records,
        finite_small_exponential_checks=checks,all_finite_temporal_derivatives_meet_2e_minus_10=True,
        input_dim=90,output_dim=252,all18_fibers_retained=True,exact_family_sparsity_verified_before_using_blocks=True,
        gauge_and_natural_H_channels_kept_separate=True,induced_H_rounding_into_gauge_not_used=True,
        physical_outgoing_derivative_admitted=False,physical_two_spin_muon_state=None,physical_magnetic_moment=None,
        physical_g_mu=None,physical_a_mu=None,matching_corrections_applied=0,
        derivative_scope='Finite piecewise-stage intrinsic S4 operator only, with supplied field operands held on their declared time discretization. Its common temporal E phase is not the physical outgoing Gamma_E. Finite B differences test the same frozen linearized field-response operator, not a fresh nonlinear field solve or its exterior-domain contacts.',
        angular_scope='Exactly complete one-n1-insertion image of n0+n1 inputs under harmonic-preserving local homogeneous H0; a physical tail preserving those shells is not supplied. Higher B orders and n2 input need additional shells.',
        time_scope='Actual midpoint gauge/H field values consumed as constant insertion per finite cell; no continuum time error enclosure. Initial B perturbation zero; final nonzero remainder retained.',
        radial_source_scope='Intrinsic S4 current has no direct Ar vertex; full supplied Ar fields remain in archived field operands and are not declared zero in the D5/outgoing response.',
        input_hashes=pins,producer_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        packet_sha256=sha256((out/'finite_angular_response.npz').read_bytes()).hexdigest())
    for p,h in pins.items():assert sha256(Path(p).read_bytes()).hexdigest()==h
    (out/'result.json').write_text(json.dumps(encode(result),sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(path=str(out/'result.json'),sha256=sha256((out/'result.json').read_bytes()).hexdigest(),
        gauge_response_norm=result['gauge_response_norm'],induced_H_response_norm=result['nonzero_induced_H_response_norm'],
        finite_B_derivative_max=max(r['relative_derivative_difference']for r in fd_records))))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repository',required=True);p.add_argument('--angular',required=True)
    p.add_argument('--field',required=True);p.add_argument('--output',required=True);a=p.parse_args()
    run(a.repository,a.angular,a.field,a.output)
