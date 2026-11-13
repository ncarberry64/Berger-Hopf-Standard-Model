"""Independent MP80/100 full-fibre weak/positive first-source control.

This applies sparse fixed Kronecker factors in the literal original D5
expression, then differentiates complete contracted forms in high precision.
It consumes the frozen supplied-germ application; it solves no field/domain.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
import mpmath as mp
import numpy as np
from scipy import sparse

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'audits'))
from bhsm.interface.muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace
from bhsm.interface.muon_intrinsic_scalar_discretization import scalar_s3_discretization
from bhsm.interface.muon_parent_retarded_hypercharge import WALL
from bhsm_real_full_d5_source_first_application_20261016 import declared_trials

REPORT_SHA='d15def102e329c38f35b62c137d8398aa72eeda626924498a426246d66c88df1'
ARCHIVE_SHA='7da8ddd5fa4bda397aa6a2d50e845338a3ef92fb3f0e837a5a6d0d166915e177'
PRODUCER_SHA='c96814490c43faa21b35a4b2f14926d48929fa60cc6f2af774a148225dd65aa9'


def number(x):
    z=complex(x);return mp.mpc(mp.mpf(float(z.real)),mp.mpf(float(z.imag)))


def matrix(a):
    return mp.matrix([[number(x) for x in row] for row in np.asarray(a)])


def encode(a,digits):
    return dict(real=[[mp.nstr(mp.re(a[i,j]),digits) for j in range(a.cols)] for i in range(a.rows)],
        imag=[[mp.nstr(mp.im(a[i,j]),digits) for j in range(a.cols)] for i in range(a.rows)])


def maxabs(a):
    return max(abs(x) for x in a)


def compare(a,b):
    e=maxabs(a-b);den=maxabs(b)
    return dict(absolute=float(e),scaled_by_max_one=float(e/max(1,den)),
        relative_to_nonzero_derivative=float(e/den) if den else None,
        nonzero_reference_maximum=float(den))


def fixed_operator(a):
    co=sparse.coo_matrix(a);return [(int(i),int(j),number(v)) for i,j,v in zip(co.row,co.col,co.data) if v!=0]


def apply_fixed(op,a):
    out=mp.zeros(a.rows,a.cols)
    for i,j,z in op:
        for k in range(a.cols):out[i,k]+=z*a[j,k]
    return out


def fixed_maps(full,branch,E):
    h=E.shape[-1];gamma=full['gamma5D_'+branch];gen=full['unitTr16_gauge_particle']
    if branch=='conjugate':gen=gen.conj()  # Fixed charge-conjugate module only.
    I=sparse.eye(16*h,format='csr')
    g=[fixed_operator(sparse.kron(a,I,format='csr')) for a in gamma]
    gauge=[fixed_operator(sparse.kron(sparse.eye(4),sparse.kron(a,sparse.eye(h)),format='csr')) for a in gen]
    spin=fixed_operator(sparse.kron(-1.5j*gamma[1]@gamma[2]@gamma[3],I,format='csr'))
    angular=fixed_operator(sum((sparse.kron(sparse.kron(1j*gamma[a+1],sparse.eye(16)),E[a],format='csr')
        for a in range(3)),sparse.csr_matrix((64*h,64*h),dtype=complex)))
    return dict(gamma=g,gauge=gauge,spin=spin,angular=angular)


def prepare(c,E,full,trials):
    v,vr,vt,vx,vrx,vtx,left,leftx=trials;q,D,n=v.shape;d=D//6;blocks=[]
    for b,branch in enumerate(('particle','conjugate')):
        ops=fixed_maps(full,branch,E)
        for family in range(3):
            sl=slice((2*family+b)*d,(2*family+b+1)*d)
            for r in range(q):
                vv=[matrix(a[r,sl]) for a in (v,vx,vtx)]
                block=dict(point=r,gamma0=ops['gamma'][0],gamma4=ops['gamma'][4],
                    v=vv,vr=[matrix(a[r,sl]) for a in (vr,vrx)],vt=[matrix(a[r,sl]) for a in (vt,vtx)],
                    left=[matrix(a[r,:,sl]) for a in (left,leftx)])
                block['gauge']=[[apply_fixed(op,a) for a in vv] for op in ops['gauge']]
                block['spin']=[apply_fixed(ops['spin'],a) for a in vv]
                block['angular']=[apply_fixed(ops['angular'],a) for a in vv]
                block['spatial_gamma']=ops['gamma'][1:4]
                blocks.append(block)
    return blocks


def linear(a,x):return a[0]+x*a[1]


def polynomial(a,x):return a[0]+x*a[1]+x*x*a[2]/2


def literal_form_function(c,blocks,weights,eps,energy):
    names=('lapse','radial_coframe','radius','coordinate_shift','geometric_time_contact',
        'geometric_radial_contact','surface_proper_clock_rate','volume_density',
        'eta_profile','eta_profile_coordinate_time','eta_profile_radial')
    coef=[{k:(number(c[k][r]),number(c[k+'_first'][0,r])) for k in names} for r in range(len(weights))]
    gauge=[[[[number(c['gauge_connection_material'][r,mu,k]),number(c['gauge_connection_material_first'][0,r,mu,k])]
        for k in range(4)] for mu in range(5)] for r in range(len(weights))]
    ww=[number(w) for w in weights];ee=number(energy);radial_quadratic=number(.031-.019j)
    def evaluate(x):
        weak,positive,phase=mp.zeros(4,3),mp.zeros(3,3),mp.zeros(4,3)
        for b in blocks:
            r=b['point'];cc={k:a[0]+x*a[1] for k,a in coef[r].items()}
            N,C,R,z,h0,h4,ell,mu,ff,ft,fr=(cc[k] for k in names)
            A=[[a[0]+x*a[1] for a in row] for row in gauge[r]]
            v=polynomial(b['v'],x);vr=linear(b['vr'],x)+x*x*radial_quadratic*b['vr'][0]
            vt=linear(b['vt'],x);L=linear(b['left'],x)
            gv=[polynomial(a,x) for a in b['gauge']]
            cov=(vt-z*vr)/N+h0*v+sum(((A[0][k]-z*A[1][k])*gv[k]/N for k in range(4)),mp.zeros(v.rows,3))
            f0,f4=(ft-z*fr)/N,fr/C
            g0v=apply_fixed(b['gamma0'],v);g4v=apply_fixed(b['gamma4'],v)
            spatial=mp.j*eps*(apply_fixed(b['gamma4'],vr)/C+h4*g4v)
            spatial-=mp.j*mp.cot(ff)*(f0*g0v+eps*f4*g4v)
            spatial+=(polynomial(b['spin'],x)+polynomial(b['angular'],x))/R
            gauge_r=sum((A[1][k]*gv[k] for k in range(4)),mp.zeros(v.rows,3))
            spatial+=mp.j*eps*apply_fixed(b['gamma4'],gauge_r)/C
            for a in range(3):
                gauge_a=sum((A[a+2][k]*gv[k] for k in range(4)),mp.zeros(v.rows,3))
                spatial+=mp.j*apply_fixed(b['spatial_gamma'][a],gauge_a)/R
            lorentz=mp.j*apply_fixed(b['gamma0'],cov)+spatial+ee*ell*g0v/N
            product=cov-apply_fixed(b['gamma0'],spatial)-mp.j*ee*ell*v/N
            weight=ww[r]*mu
            weak+=weight*(L*lorentz)
            positive+=weight*(product.transpose_conj()*product)
            phase+=weight*(L*(ell*g0v/N))
        return mp.matrix([[a[i,j] for j in range(3)] for a in (weak,positive,phase) for i in range(a.rows)])
    return evaluate


def select(a,name):
    start,end=dict(weak=(0,4),positive=(4,7),phase=(7,11))[name]
    return a[start:end,:]


def frozen_targets(archive,side,level,eps,trials,weights,c):
    name=f'{side}_n{level}_eta{eps}';L,Lx=trials[-2:]
    p,px=(archive[name+'_point_'+k] for k in ('phase_frequency_partial','phase_frequency_partial_first'))
    mu,mux=c['volume_density'],c['volume_density_first'][0]
    con=lambda m,l,r:np.einsum('q,qij,qjk->ik',m,l,r)
    phase=con(weights*mu,L,p)
    phasex=con(weights*mux,L,p)+con(weights*mu,Lx,p)+con(weights*mu,L,px)
    return dict(weak=(archive[name+'_weak_value'],archive[name+'_weak_first']),
        positive=(archive[name+'_positive_value'],archive[name+'_positive_first']),phase=(phase,phasex))


def execute(application,output):
    application,out=Path(application).resolve(),Path(output).resolve()
    if out.exists():raise FileExistsError('preserve independent control outputs')
    pins={}
    def pin(p,expected=None):
        p=Path(p);digest=sha256(p.read_bytes()).hexdigest()
        if expected and digest!=expected:raise ValueError('frozen bytes changed: '+str(p))
        label=p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else 'retained_inputs/'+p.name
        pins[label]=digest
    pin(application/'result.json',REPORT_SHA);pin(application/'application.npz',ARCHIVE_SHA)
    pin(ROOT/'audits/bhsm_real_full_d5_source_first_application_20261016.py',PRODUCER_SHA)
    report=json.loads((application/'result.json').read_bytes())
    with np.load(application/'application.npz',allow_pickle=False) as z:archive={k:z[k] for k in z.files}
    if report['source_axis']!='sole saved c[*_first][0]: coordinate-time direction frozen inside the original represented cell':
        raise ValueError('same sole represented-cell source axis required')
    qx,qw=np.polynomial.legendre.leggauss(4);rho=(qx+1)*WALL/2;weights=qw*WALL/2*(2*np.pi**2)
    full=full_d5_localized_lepton_trace();records=[]
    for side in ('incoming','outgoing'):
        prefix=side+'_input_';c={k[len(prefix):]:a for k,a in archive.items() if k.startswith(prefix) and k not in (prefix+'raw',prefix+'rawtime')}
        for k,a in list(c.items()):
            if k.endswith('_first') and a.ndim>=2 and a.shape[1]==5:c[k]=a[:,:4]
            elif not k.endswith('_first') and a.ndim>=1 and a.shape[0]==5:c[k]=a[:4]
        for level in (0,1):
            E=scalar_s3_discretization(level)['angular_derivative_matrices'];D=384*E.shape[-1]
            trials=declared_trials(rho,D)
            for eps in (-1,1):
                targets=frozen_targets(archive,side,level,eps,trials,weights,c)
                precisions=[];stored={}
                for digits in (80,100):
                    with mp.workdps(digits):
                        blocks=prepare(c,E,full,trials);fun=literal_form_function(c,blocks,weights,eps,report['off_shell_phase_frequency'])
                        value=fun(mp.mpf(0));first=mp.diff(fun,mp.mpf(0));components={};fd=[]
                        for name,(value64,first64) in targets.items():
                            vv,ff=select(value,name),select(first,name)
                            components[name]=dict(value=encode(vv,digits-8),first=encode(ff,digits-8),
                                binary64_value=compare(matrix(value64),vv),binary64_first=compare(matrix(first64),ff),
                                nonzero_value_maximum=float(maxabs(vv)),nonzero_first_maximum=float(maxabs(ff)))
                        if digits==80:
                            original=next(r for r in report['records'] if r['side']==side and r['angular_level']==level and r['eta_orientation']==eps)
                            for old in original['affine_germ_FD_sweep']:
                                hh=mp.mpf(old['step']);detail={}
                                for name in ('weak','positive','phase'):
                                    vv,ff=select(value,name),select(first,name);den=maxabs(ff)
                                    detail[name]=dict(baseline_value_over_step_derivative=float(maxabs(vv)/(hh*den)),
                                        binary64_unit_roundoff_stencil_scale_estimate=float(mp.mpf(2)**-53*mp.mpf('1.5')*maxabs(vv)/(hh*den)),
                                        original_binary64_FD_error=old.get('weak_first' if name=='weak' else 'positive_form_first') if name!='phase' else None)
                                fd.append(dict(step=old['step'],components=detail))
                        if digits==100:
                            agreement={name:compare(select(first,name),stored[name]) for name in ('weak','positive','phase')}
                        else:
                            stored={name:select(first,name).copy() for name in ('weak','positive','phase')};agreement=None
                        precisions.append(dict(decimal_digits=digits,components=components,
                            all_original_step_cancellation_diagnostics=fd,precision_80_to_100_first_agreement=agreement))
                        del blocks,fun
                    print(json.dumps(dict(progress_side=side,angular_level=level,eta=eps,decimal_digits=digits)),flush=True)
                records.append(dict(side=side,angular_level=level,eta_orientation=eps,full_fibre_rows=D,
                    source_axis='same saved real coefficient first, independent analytic left, fixed Eulerian/Haar frame',precisions=precisions))
    for name,module in list(sys.modules.items()):
        p=getattr(module,'__file__',None)
        if name.startswith('bhsm.') and p and Path(p).is_relative_to(ROOT):pin(p)
    pin(__file__)
    worst=max(p['components'][name]['binary64_first']['relative_to_nonzero_derivative']
        for r in records for p in r['precisions'] for name in ('weak','positive','phase'))
    worst_precision=max(p['precision_80_to_100_first_agreement'][name]['relative_to_nonzero_derivative']
        for r in records for p in r['precisions'] if p['precision_80_to_100_first_agreement'] for name in ('weak','positive','phase'))
    result=dict(classification='INDEPENDENT_MP80_100_FULL384_SUPPLIED_GERM_FORM_FIRST_CONTROL',records=records,
        worst_binary64_first_relative_to_nonzero_derivative=worst,
        worst_MP80_MP100_first_relative=worst_precision,
        full_supplied_germ_contracted_form_first_at_2e_minus10=(worst<2e-10 and worst_precision<2e-10),
        tested_forms='complete weak4x3, positive3x3 and exact phase-partial4x3; all384h rows and original4 core nodes',
        independent_method='literal Dtau/spatial Kronecker application, MP form contraction and mp.diff; no source-first derivative code',
        tiny_phase_contacts='direct ell Gamma0 V/N and its derivative, never frequency-value subtraction',
        binary64_failed_sweep_preserved_unchanged=True,selected_favorable_step=False,
        cancellation_estimates_are_not_roundoff_bounds_or_truncation_proofs=True,
        field_source_and_trial_scope='frozen supplied first germ only; no solved field acceleration or new history evaluation',
        physical_E_B_outgoing_or_domain_derivative_at_2e_minus10=False,full_operator_norm_derivative_certificate=False,
        radial_angular_exterior_or_polar_domain_convergence=False,physical_two_spin_state_or_muon_moment=None,
        coupled_corrections=0,new_history_profile_or_source_integrations=0,input_and_source_sha256=dict(sorted(pins.items())))
    out.mkdir(parents=True);(out/'result.json').write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(worst_binary64_first_relative=worst,
        worst_MP80_MP100_first_relative=worst_precision,supplied_germ_form_control_pass=result['full_supplied_germ_contracted_form_first_at_2e_minus10'],
        physical_domain_derivative_pass=False)),flush=True)
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--application',default=str(ROOT/'artifacts/muon_real_coupled_open_operator_20261016/source_first_run_1'))
    p.add_argument('--output',required=True);a=p.parse_args();execute(a.application,a.output)
