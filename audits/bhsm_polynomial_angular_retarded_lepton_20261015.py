"""Complete one-insertion angular response of certified finite field polynomials.

The physical outgoing boundary, its jets and an interacting pole are not
created by this finite intrinsic S4 application. Gauge and natural-Higgs
terms remain separate even when their sizes differ by many orders.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import os
from pathlib import Path
import sys
import json
import math
os.environ['OPENBLAS_NUM_THREADS']='2'
os.environ['OMP_NUM_THREADS']='2'
import numpy as np
from scipy.integrate import solve_ivp
from numpy.polynomial.legendre import leggauss
from bhsm_finite_angular_retarded_lepton_20261015 import encode,save,exponential,maximum,relative


def polynomial(coeff,s):
    out=np.zeros_like(coeff[0])
    for c in coeff[::-1]:out=out*s+c
    return out


def norm2upper(a):return float(np.sqrt(np.linalg.norm(a,1)*np.linalg.norm(a,np.inf)))


def moment(a,b,coeff,count):
    points,weights=leggauss(count);answer=np.zeros_like(coeff[0])
    for s,w in zip((points+1)/2,weights/2):
        answer+=w*(exponential((1-s)*a)@polynomial(coeff,s)@exponential(s*b))
    return answer


def run(root,angular,field,out):
    root,angular,field,out=map(lambda p:Path(p).resolve(),(root,angular,field,out))
    if out.exists():raise FileExistsError('preserve each actual application')
    sys.path.insert(0,str(root/'src'))
    from bhsm.interface.muon_native_dirac_hamiltonian import lepton_current_hilbert_representation
    from bhsm.interface.muon_native_product_factor_graph import lepton_unit_trace_gauge_representation
    from bhsm.interface.muon_continued_action_reality import _higgs_mass_realified
    pins={}
    def read(p):
        p=Path(p);pins[str(p)]=sha256(p.read_bytes()).hexdigest()
        if p.suffix=='.json':return json.loads(p.read_bytes())
        with np.load(p,allow_pickle=False)as z:return {k:z[k].copy()for k in z.files}
    md=read(field/'result.json');c=read(angular/'exact_angular_core.npz')
    for p in [Path(__file__).with_name('bhsm_finite_angular_retarded_lepton_20261015.py'),
              *[root/f'src/bhsm/interface/{m}.py'for m in('muon_native_dirac_hamiltonian','muon_native_product_factor_graph','muon_continued_action_reality')]]:
        pins[str(p)]=sha256(p.read_bytes()).hexdigest()
    rep=lepton_current_hilbert_representation();alpha=rep['alpha'];gens=lepton_unit_trace_gauge_representation()['generators']
    gaunt=c['gaunt_out_n012_source_n1_input_n01'];gcap=np.zeros((14,4,14));gcap[:,:,:5]=gaunt;gcap[:5]=gaunt.transpose(2,1,0)
    assert maximum(gcap[:,:,:5]-gaunt)<1e-14
    stages=[]
    for j in range(2):
        p=root/f'artifacts/muon_formed_weak_field_20261015/same_epoch_probe/run_2/stage_{j:04d}_actual_unit_magnetic_source_and_direct_insertion.npz'
        source=read(p);R=source['wall_radius'].item();N=source['wall_induced_lapse'].item();con=source['actual_background_wall_connection']
        h18=(-1j*np.einsum('aij,ac,cjk->ik',alpha,con[2:],gens)+1.5*rep['gamma5'])/R
        h18+=_higgs_mass_realified(source['raw268'][260:264])-1j*np.einsum('c,cij->ij',con[0],gens)/N
        hout=np.kron(np.eye(14),h18)-1j*sum(np.kron(e,a)for e,a in zip(c['right_body_derivatives_out_n012'],alpha))/R
        hin=np.kron(np.eye(5),h18)-1j*sum(np.kron(e,a)for e,a in zip(c['right_body_derivatives_input_n01'],alpha))/R
        vertex=np.zeros((24,18,18),complex);vertex[:4]=-1j*gens/N
        for a in range(3):vertex[8+4*a:12+4*a]=-1j*np.einsum('ij,cjk->cik',alpha[a],gens)/R
        vertex[20:]=np.array([_higgs_mass_realified(e)for e in np.eye(4)])
        internal_mask=np.zeros((18,18),bool)
        for f in range(3):
            ids=np.array([2*f,2*f+1,6+2*f,7+2*f,12+2*f,13+2*f]);internal_mask[np.ix_(ids,ids)]=True
        if np.any(vertex[:,~internal_mask]):raise ValueError('Actual vertex does not preserve family; full solve required')
        stages.append(dict(N=N,hout=hout,hin=hin,vertex=vertex))
    family=[np.array([2*f,2*f+1,6+2*f,7+2*f,12+2*f,13+2*f])for f in range(3)]
    outs=[np.concatenate([18*h+i for h in range(14)])for i in family];ins=[np.concatenate([18*h+i for h in range(5)])for i in family]
    mask=np.zeros((252,252),bool)
    for ids in outs:mask[np.ix_(ids,ids)]=True
    assert all(not np.any(s['hout'][~mask])for s in stages)
    pieces=[]
    for p in sorted(field.glob('piece_*_certified_wall96_polynomial.npz')):
        data=read(p);bounds=data['coordinate_bounds'];dt=(bounds[1]-bounds[0]).item()
        if dt.imag!=0 or dt.real<=0:raise ValueError('original finite coordinate pieces required')
        pieces.append(dict(data=data,dt=dt.real,stage=int(data['stage']),
            coeff=(data['wall96_polynomial_coefficients_high']+data['wall96_polynomial_coefficients_low']).reshape(-1,24,4,3)))
    if len(pieces)!=3:raise ValueError('three declared exact source-polynomial pieces required')
    out.mkdir(parents=True)
    result_ops=np.zeros((2,3,252,90),complex);energy_ops=np.zeros_like(result_ops);quad_errors=[];kernel_bounds=[];fd=[]
    proper=sum(stages[p['stage']]['N']*p['dt']for p in pieces)
    for fi,(ids,oi,ii)in enumerate(zip(family,outs,ins)):
        x=np.eye(30,dtype=complex);response=np.zeros((2,3,84,30),complex);de=np.zeros_like(response);clock=0j;local=[]
        for ip,p in enumerate(pieces):
            st=stages[p['stage']];dt=p['dt'];a=-1j*st['N']*dt*st['hout'][np.ix_(oi,oi)];b=-1j*st['N']*dt*st['hin'][np.ix_(ii,ii)]
            vertices=st['vertex'][:,ids][:,:,ids];q=p['coeff']
            hg=np.einsum('kchA,cij->kAhij',q[:,:20],vertices[:20]);hh=np.einsum('kchA,cij->kAhij',q[:,20:],vertices[20:])
            hc=np.stack((hg,hh),axis=1)
            fr=-1j*st['N']*dt*np.einsum('ohx,kcAhij->kcAoixj',gaunt,hc).reshape(len(q),2,3,84,30)
            fs=-1j*st['N']*dt*np.einsum('ohx,kcAhij->kcAoixj',gcap,hc).reshape(len(q),2,3,84,84)
            count=max(24,(len(q)-1+24+2)//2)
            j=moment(a,b,fr,count);higher=moment(a,b,fr,count+8)
            quad_errors.append(dict(family=fi,piece=ip,points=count,
                gauge_relative=relative(j[0]-higher[0],higher[0]),H_relative=relative(j[1]-higher[1],higher[1])))
            v,w=exponential(a),exponential(b);tau=1j*st['N']*dt
            de=tau*v@response+v@de+tau*j@x+j@(1j*clock*x)
            response=v@response+j@x;x=w@x;clock+=st['N']*dt
            beta=max(norm2upper(a),norm2upper(b));sourcebound=sum(float(np.linalg.norm(z))for z in fr)
            kernel_bounds.append(dict(family=fi,piece=ip,induced_2_norm_upper=beta,
                absolute_kernel_Taylor_remainder=sourcebound*np.exp(2*beta)*2*beta**13/math.factorial(13)))
            if beta>1e-2:raise ValueError('kernel requires a new controlled exponential scheme')
            local.append(dict(a=a,coeff=fs))
        for ch in range(2):
            for ax in range(3):result_ops[ch,ax][np.ix_(oi,ii)]=response[ch,ax];energy_ops[ch,ax][np.ix_(oi,ii)]=de[ch,ax]
        # Independent finite-field differences integrate the square cap ODE.
        # First derivative on inputn<=1 has the exact n<=2 image. Higher orders
        # of this numerical check do not define a physical angular cutoff.
        for ch in range(2):
            for ax in range(3):
                bound=sum(sum(norm2upper(z[ch,ax])for z in p['coeff'])for p in local)
                if bound==0:raise ValueError('nonzero field channel disappeared')
                h=.003/bound;values=[]
                for shift in(-2,-1,1,2):
                    state=np.zeros((84,30),complex);state[:30]=np.eye(30)
                    for p in local:
                        def rhs(t,y):return ((p['a']+shift*h*polynomial(p['coeff'][:,ch,ax],t))@y.reshape(84,30)).ravel()
                        solution=solve_ivp(rhs,(0.,1.),state.ravel(),method='DOP853',rtol=5e-14,atol=5e-16,max_step=.125)
                        if not solution.success:raise ArithmeticError(solution.message)
                        state=solution.y[:,-1].reshape(84,30)
                    values.append(state)
                fresh=(values[0]-8*values[1]+8*values[2]-values[3])/(12*h)
                fd.append(dict(family=fi,channel=['gauge','natural_H'][ch],axis=ax,
                    relative_B_difference=relative(fresh-response[ch,ax],response[ch,ax]),
                    coefficient_probe_step=h,physical_field_strength_selected=False))
    energy_error=relative(energy_ops-1j*proper*result_ops,proper*result_ops)
    maximum_fd=max(r['relative_B_difference']for r in fd);maximum_quad=max(max(r['gauge_relative'],r['H_relative'])for r in quad_errors)
    status=maximum_fd<=2e-10 and maximum_quad<=2e-10 and energy_error<=2e-10
    save(out/'finite_polynomial_angular_response.npz',dict(retarded_B_response_gauge=result_ops[0],retarded_B_response_natural_H=result_ops[1],
        finite_temporal_energy_B_gauge=energy_ops[0],finite_temporal_energy_B_natural_H=energy_ops[1],proper_duration=np.array(proper)))
    result=dict(classification='CERTIFIED_FINITE_SOURCE_POLYNOMIAL_CONSUMED_IN_COMPLETE_ONE_INSERTION_ANGULAR_LEPTON_RESPONSE',
        gauge_response_norm=float(np.linalg.norm(result_ops[0])),nonzero_natural_H_response_norm=float(np.linalg.norm(result_ops[1])),
        temporal_E_product_rule_relative=energy_error,quadrature_checks=quad_errors,finite_B_difference_checks=fd,
        controlled_finite_kernel_bounds=kernel_bounds,finite_checks_meet_2e_minus_10=status,
        field_original_rows=md['original_row_upper_bounds'],source_piece_count=3,input_dim=90,output_dim=252,
        field_sample_hold_used=False,all18_fibers_and_all_three_axes_retained=True,gauge_H_channels_separate=True,
        exact_family_sparsity_verified=True,physical_outgoing_derivative_admitted=False,physical_magnetic_moment=None,
        physical_g_mu=None,physical_a_mu=None,physical_two_spin_muon_state=None,coupled_matching_corrections_applied=0,
        derivative_scope='E clock product rule and fresh B differences of this finite intrinsic S4 operator with the supplied classical field polynomials held as operands. Full outgoing boundary/domain/quantum jets and physical Lorentz pole are not supplied.',
        angular_scope='Complete one-n1-insertion image n0+n1 to n0+n1+n2 under homogeneous unperturbed field; full physical tail/angular cutoff closure is not asserted.',
        normalization_scope='A physical resonance readout would require its actual unsquared outgoing residue; this consumer supplies no pole or residue. No positive-L2 collar requirement is added. Physical outgoing symbol and its E/B jets remain absent.',
        source_enclosures='Certified MP wall96 source-polynomial bounds are retained in input archives. New lepton norm, quadrature and DOP853 checks use floating arithmetic and are not outward interval certificates. Kernel formulas concern the fixed complex background only; no continuum/physical error enclosure.',
        input_hashes=pins,producer_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        packet_sha256=sha256((out/'finite_polynomial_angular_response.npz').read_bytes()).hexdigest())
    for p,h in pins.items():assert sha256(Path(p).read_bytes()).hexdigest()==h
    (out/'result.json').write_text(json.dumps(encode(result),sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(output=str(out),result_sha256=sha256((out/'result.json').read_bytes()).hexdigest(),
        finite_B_difference_max=maximum_fd,quadrature_difference_max=maximum_quad,E_clock_relative=energy_error,
        gauge_norm=result['gauge_response_norm'],natural_H_norm=result['nonzero_natural_H_response_norm'],finite_checks_pass=status)),flush=True)
    if not status:raise ArithmeticError('Finite source-polynomial lepton derivative control did not pass')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repository',required=True);p.add_argument('--angular',required=True)
    p.add_argument('--field',required=True);p.add_argument('--output',required=True);a=p.parse_args();run(a.repository,a.angular,a.field,a.output)
