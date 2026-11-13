"""Full384 D5 first-source application on two preserved REAL cell midpoints.

Only saved coefficient values/firsts are consumed. No history, profile,
field equation, exterior or normal-mode problem is solved by this audit.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
import mpmath as mp
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.muon_combined_f_eta_contact import combined_f_eta_contact
from bhsm.interface.muon_full_d5_source_first import (
    full_d5_differential_source_first,full_d5_weak_source_first,full_d5_positive_source_first)
from bhsm.interface.muon_full_d5_differential_form import full_d5_differential_coefficients,apply_full_d5_expression
from bhsm.interface.muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace
from bhsm.interface.muon_holomorphic_d5_trace_action import d5_unsquared_weak_trace
from bhsm.interface.muon_intrinsic_scalar_discretization import scalar_s3_discretization
from bhsm.interface.muon_parent_retarded_hypercharge import WALL
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz

REPORT_SHA='7c3c1ac4e98d48b65adc842439675b2c0c6c163afaa4334e588b03504e943514'
ARCHIVE_SHA='3237d90c3cba1234a115ed3b47eb7fb67ff7c56b5d14b266e6cd23728062f6ca'
COEFFICIENT_KEYS=('time','radial','body','energy','Dtau_time','Dtau_radial','Dtau_body',
    'W_radial','W_body','A_time','A_radial','A_body','A_energy','sigma_eta_contact')


def encode(a):
    a=np.asarray(a,complex);return dict(real=a.real.tolist(),imag=a.imag.tolist())


def compare(a,b):
    a,b=np.asarray(a),np.asarray(b);error=float(np.max(abs(a-b)))
    return dict(absolute=error,scaled=error/max(1.,float(np.max(abs(a))),float(np.max(abs(b)))))


def slice_points(c,indices):
    q=len(c['lapse']);out={}
    for k,a in c.items():
        if k.endswith('_first') and a.ndim>=2 and a.shape[1]==q:out[k]=a[:,indices].copy()
        elif not k.endswith('_first') and a.ndim>=1 and a.shape[0]==q:out[k]=a[indices].copy()
        else:out[k]=a.copy()
    return out


def affine_coefficients(c,x):
    out={k:a.copy() for k,a in c.items()}
    for k,a in c.items():
        if not k.endswith('_first') and k+'_first' in c:
            if c[k+'_first'].shape==(1,)+a.shape:out[k]=a+x*c[k+'_first'][0]
    return out


def eta_literal(c,gamma,h,eps):
    # Original combined f-contact, independently evaluated WITHOUT a normal
    # square root, source derivative routine, sigma projection or conjugation.
    f0=(c['eta_profile_coordinate_time']-c['coordinate_shift']*c['eta_profile_radial'])/c['lapse']
    f4=c['eta_profile_radial']/c['radial_coframe']
    g0,g4=(np.kron(gamma[k],np.eye(16*h)) for k in (0,4))
    return -1j/np.tan(c['eta_profile'])[:,None,None]*(f0[:,None,None]*g0+eps*f4[:,None,None]*g4)


def declared_trials(rho,D):
    """Dense bounded algebraic test functions, not normal-mode/state data.

    x is coordinate-time offset from the saved midpoint. V_x=V_t,
    V_rho,x=partial_rho V_t and V_t,x=V_tt are exact polynomial identities.
    These test functions are external probes, never a solved spin state.
    """
    r=rho/WALL;rows=np.arange(1,D+1)[:,None];cols=np.arange(2,5)[None,:]
    B=(np.cos(rows*cols*.173)+1j*np.sin(rows*(cols+.37)*.119))/np.sqrt(D)
    leftrows=np.arange(2,6)[:,None];fib=np.arange(1,D+1)[None,:]
    LB=(np.cos(leftrows*fib*.131)+1j*np.sin((leftrows+.23)*fib*.157))/np.sqrt(D)
    a=1+(.17+.03j)*r+.07*r*r;ar=((.17+.03j)+.14*r)/WALL
    k=.13-.04j;z=.021+.017j;eta=.031-.019j
    v=a[:,None,None]*B;vr=ar[:,None,None]*B
    vt=(k*a+z*r)[:,None,None]*B
    vrx=(k*ar+z/WALL)[:,None,None]*B;vtx=(2*eta*a)[:,None,None]*B
    left=(1+(.07+.03j)*r)[:,None,None]*LB
    leftx=(.11-.023j)*(1+.1*r)[:,None,None]*LB
    return v,vr,vt,vt.copy(),vrx,vtx,left,leftx


def move_trials(t,x):
    v,vr,vt,vx,vrx,vtx,left,leftx=t
    return v+x*vx+.5*x*x*vtx,vr+x*vrx+x*x*(.031-.019j)*vr,vt+x*vtx,left+x*leftx


def literal_full(c,E,trial,w,energy,eps,full):
    v,vr,vt,left=trial;q,D,n=v.shape;d=D//6;out=np.empty_like(v);form=np.zeros((left.shape[1],n),complex)
    # Identical family coefficient blocks are applied once to a concatenated
    # family trial map, while diagonal family contractions are all retained.
    for b,branch in enumerate(('particle','conjugate')):
        slices=[slice((2*f+b)*d,(2*f+b+1)*d) for f in range(3)]
        vv=np.concatenate([v[:,sl] for sl in slices],axis=2)
        rr=np.concatenate([vr[:,sl] for sl in slices],axis=2)
        tt=np.concatenate([vt[:,sl] for sl in slices],axis=2)
        ll=np.concatenate([left[:,:,sl] for sl in slices],axis=1)
        gamma=full['gamma5D_'+branch];gen=full['unitTr16_gauge_particle']
        if branch=='conjugate':gen=gen.conj()  # Fixed representation only.
        r=d5_unsquared_weak_trace(c,w,gamma=gamma,carrier_generators=gen,angular_derivatives=E,
            right_values=vv,right_radial=rr,right_coordinate_time=tt,literal_left_values=ll,
            energy=energy,sheet_orientation=eps,eta_clifford_contact=eta_literal(c,gamma,E.shape[-1],eps))
        for f,sl in enumerate(slices):
            out[:,sl]=r['original_D5_on_trial'][:,:,f*n:(f+1)*n]
            form+=r['unsquared_trace_action'][f*left.shape[1]:(f+1)*left.shape[1],f*n:(f+1)*n]
    return out,form


def fd4(fun,h):
    return (fun(-2*h)-8*fun(-h)+8*fun(h)-fun(2*h))/(12*h)


def mpc(z):
    z=complex(z);return mp.mpc(str(z.real),str(z.imag))


def mp_literal(c,E,full,branch,r,eps,pair,x):
    """Original ordered 4x4 spin coefficient entries at MP64.

    MP differentiation acts on supplied affine coefficients, not any saved
    or newly solved second field derivative. All source slots stay analytic.
    """
    ci,cj,ai,aj=pair;val=lambda k:mpc(c[k][r])+x*mpc(c[k+'_first'][0,r])
    N,C,R,z,h0,h4,ell=(val(k) for k in ('lapse','radial_coframe','radius','coordinate_shift',
        'geometric_time_contact','geometric_radial_contact','surface_proper_clock_rate'))
    g=[mp.matrix([[mpc(t) for t in row] for row in a]) for a in full['gamma5D_'+branch]]
    I=mp.eye(4);ident=int(ci==cj and ai==aj)
    gen=full['unitTr16_gauge_particle']
    if branch=='conjugate':gen=gen.conj()
    A=[sum((mpc(c['gauge_connection_material'][r,mu,k])+x*mpc(c['gauge_connection_material_first'][0,r,mu,k]))
        *mpc(gen[k,ci,cj])*int(ai==aj) for k in range(4)) for mu in range(5)]
    ff,ft,fr=val('eta_profile'),val('eta_profile_coordinate_time'),val('eta_profile_radial')
    f0,f4=(ft-z*fr)/N,fr/C
    eta=-mp.j*mp.cot(ff)*(f0*g[0]+eps*f4*g[4])*ident
    angular=sum((mp.j*g[a+1]*mpc(E[a,ai,aj])*int(ci==cj) for a in range(3)),mp.zeros(4))
    spin=-mp.mpf('1.5')*mp.j*g[1]*g[2]*g[3]*ident
    # Literal original Lorentz body is assembled before its Dtau/W split.
    inside=mp.j*eps*g[4]*h4*ident+eta+(spin+angular)/R+mp.j*eps*g[4]*A[1]/C
    inside+=sum((mp.j*g[a+1]*A[a+2]/R for a in range(3)),mp.zeros(4))
    dt=I*ident/N;dr=-z*I*ident/N;db=I*(h0*ident+(A[0]-z*A[1])/N)
    wr=-mp.j*eps*g[0]*g[4]*ident/C;wb=-g[0]*inside
    blocks=dict(time=mp.j*g[0]*dt,radial=g[0]*(mp.j*dr-wr),body=g[0]*(mp.j*db-wb),
        energy=g[0]*ell*ident/N,Dtau_time=dt,Dtau_radial=dr,Dtau_body=db,W_radial=wr,W_body=wb,
        A_time=dt,A_radial=dr+wr,A_body=db+wb,A_energy=-mp.j*ell*I*ident/N,sigma_eta_contact=eta)
    return mp.matrix([[blocks[COEFFICIENT_KEYS[j//4]][i,j%4]
        for j in range(4*len(COEFFICIENT_KEYS))] for i in range(4)])


def mp_controls(c,E,germ,full,eps):
    h=E.shape[-1];pairs=[(0,0,0,0),(6,7,0,0),(14,14,0,0)]
    if h>1:pairs.append((0,0,1,2))
    maximum=dict(absolute=0.,scaled=0.);by_key={k:0. for k in COEFFICIENT_KEYS}
    with mp.workdps(64):
        for branch in ('particle','conjugate'):
            for r in range(len(c['lapse'])):
                for pair in pairs:
                    ref=np.array(mp.diff(lambda x:mp_literal(c,E,full,branch,r,eps,pair,x),mp.mpf(0)).tolist(),complex)
                    ci,cj,ai,aj=pair;ri=np.arange(4)*16*h+ci*h+ai;co=np.arange(4)*16*h+cj*h+aj
                    for j,k in enumerate(COEFFICIENT_KEYS):
                        got=germ['first']['blocks'][branch][k][r][np.ix_(ri,co)]
                        e=compare(got,ref[:,4*j:4*j+4]);maximum={a:max(maximum[a],e[a]) for a in maximum}
                        by_key[k]=max(by_key[k],e['scaled'])
    return dict(maximum=maximum,scaled_by_coefficient=by_key,precision_decimal_digits=64,
        source_affine_germ_only=True,full_fibre_operator_or_domain_not_inferred=True)


def execute(inputs,output):
    inputs,out=Path(inputs).resolve(),Path(output).resolve()
    if out.exists():raise FileExistsError('preserve independent output runs')
    pins={};arrays={};records=[]
    def pin(p,expected=None,label=None):
        p=Path(p);digest=sha256(p.read_bytes()).hexdigest()
        if expected and digest!=expected:raise ValueError('pinned bytes changed: '+str(p))
        pins[label or p.relative_to(ROOT).as_posix()]=digest
    rp=inputs/'result.json';ap=inputs/'actual_real_coefficients_and_normal_squares.npz'
    pin(rp,REPORT_SHA);pin(ap,ARCHIVE_SHA)
    report=json.loads(rp.read_bytes())
    if report['classification']!='PRESERVED_ACTUAL_REAL_FULL_CAP_SIGMA_NORMAL_REJECTION' or report['numerical_sha256']!=ARCHIVE_SHA:
        raise ValueError('the original preserved real coefficient packet is required')
    with np.load(ap,allow_pickle=False) as z:archive={k:z[k] for k in z.files}
    full=full_d5_localized_lepton_trace();qx,qw=np.polynomial.legendre.leggauss(4)
    expected_rho=np.r_[(qx+1)*WALL/2,WALL];weights=qw*WALL/2*(2*np.pi**2)
    energy=.23;energy_first=0.  # A disclosed off-shell probe; no pole choice.
    for side in ('incoming','outgoing'):
        prefix=side+'_sample2_';c={k[len(prefix+'c_'):]:a.copy() for k,a in archive.items() if k.startswith(prefix+'c_')}
        rho=archive[prefix+'rho'];raw=archive[prefix+'raw'];rawtime=archive[prefix+'raw_future_time']
        if not np.array_equal(rho,expected_rho) or raw.dtype.kind!='f' or rawtime.dtype.kind!='f':
            raise ValueError('original real midpoint and original separate wall required')
        rec=[r for r in report['records'] if r['side']==side and r['sample_kind']=='actualsavedcellmidpoint']
        if len(rec)!=1 or c['lapse_first'].shape!=(1,5):raise ValueError('one frozen inside-cell source slot required')
        core=slice_points(c,np.arange(4));wall=slice_points(c,np.array([4]))
        for k,a in c.items():arrays[side+'_input_'+k]=a
        arrays[side+'_input_raw']=raw;arrays[side+'_input_rawtime']=rawtime
        for level in (0,1):
            E=scalar_s3_discretization(level)['angular_derivative_matrices'];h=E.shape[-1];d=64*h;D=6*d
            trials=declared_trials(rho[:4],D);v,vr,vt,vx,vrx,vtx,left,leftx=trials
            for eps in (-1,1):
                name=f'{side}_n{level}_eta{eps}';eta={};etax={};wall_eta={};wall_etax={}
                for branch in ('particle','conjugate'):
                    a=combined_f_eta_contact(core,gamma=full['gamma5D_'+branch],carrier_count=16,angular_count=h,sheet_orientation=eps)
                    b=combined_f_eta_contact(wall,gamma=full['gamma5D_'+branch],carrier_count=16,angular_count=h,sheet_orientation=eps)
                    eta[branch]=a['combined_f_eta_contact'];etax[branch]=a['combined_f_eta_contact_first'][0]
                    wall_eta[branch]=b['combined_f_eta_contact'];wall_etax[branch]=b['combined_f_eta_contact_first'][0]
                germ=full_d5_differential_source_first(core,E,source_slot=0,sheet_orientation=eps,full_representation=full,
                    eta_contacts=eta,eta_contacts_first=etax)
                wallg=full_d5_differential_source_first(wall,E,source_slot=0,sheet_orientation=eps,full_representation=full,
                    eta_contacts=wall_eta,eta_contacts_first=wall_etax)
                shared=dict(value_first=vx,radial_derivative_first=vrx,time_derivative_first=vtx,
                    energy=energy,energy_first=energy_first)
                weak=full_d5_weak_source_first(germ,v,vr,vt,independent_left=left,independent_left_first=leftx,
                    coordinate_weights=weights,coordinate_weights_first=np.zeros(4),placement='lorentz',**shared)
                mu,mux=core['volume_density'],core['volume_density_first'][0]
                if np.any(mu.imag!=0) or np.any(mux.imag!=0):raise ValueError('actual real density source required')
                G=np.broadcast_to(np.eye(d),(4,2,d,d));Gx=np.zeros_like(G)
                positive=full_d5_positive_source_first(germ,v,vr,vt,positive_coordinate_weights=weights*mu.real,
                    coordinate_weights_first=weights*mux.real,output_block_grams=G,output_block_grams_first=Gx,
                    real_source_axis=True,**shared)
                point,form=literal_full(core,E,move_trials(trials,0),weights,energy,eps,full)
                fd=[]
                def direct(x):return literal_full(affine_coefficients(core,x),E,move_trials(trials,x),weights,energy,eps,full)
                def direct_positive(x):
                    cx=affine_coefficients(core,x);xx=move_trials(trials,x)
                    aa=full_d5_differential_coefficients(cx,E,sheet_orientation=eps,full_representation=full,
                        sigma_eta_contacts={b:eta_literal(cx,full['gamma5D_'+b],h,eps) for b in eta})
                    acted=apply_full_d5_expression(aa,*xx[:3],energy=energy,placement='formal_product')
                    return np.einsum('q,qji,qjk->ik',weights*cx['volume_density'].real,acted.conj(),acted)
                for step in (.000002,.000001,.0000005):
                    fd.append(dict(step=step,weak_first=compare(weak['first'],fd4(lambda x:direct(x)[1],step)),
                        positive_form_first=compare(positive['first'],fd4(direct_positive,step))))
                controls=mp_controls(core,E,germ,full,eps);wall_controls=mp_controls(wall,E,wallg,full,eps)
                action=weak['point_application']
                for k in ('value','first','coefficient_contact','moving_trial_contact','phase_frequency_contact',
                    'phase_frequency_partial','phase_frequency_partial_first'):arrays[name+'_point_'+k]=action[k]
                for k in ('value','first','density_contact','independent_left_contact','operator_and_trial_contact'):
                    arrays[name+'_weak_'+k]=weak[k]
                arrays[name+'_positive_value']=positive['value'];arrays[name+'_positive_first']=positive['first']
                nonzero={}
                for branch in eta:
                    b=germ['value']['blocks'][branch];bx=germ['first']['blocks'][branch]
                    nonzero[branch]=dict(eta=float(np.linalg.norm(eta[branch])),eta_first=float(np.linalg.norm(etax[branch])),
                        gauge=float(np.linalg.norm(core['gauge_connection_material'])),round_spin=float(np.linalg.norm(b['round_spin_Dirac_matrix'])),
                        time=float(np.linalg.norm(b['time'])),shift=float(np.linalg.norm(b['Dtau_radial'])),
                        angular=float(np.linalg.norm(b['angular_Dirac_matrix'])),body_first=float(np.linalg.norm(bx['body'])),
                        wall_eta=float(np.linalg.norm(wall_eta[branch])),wall_eta_first=float(np.linalg.norm(wall_etax[branch])))
                records.append(dict(side=side,coordinate_time=rec[0]['coordinate_time'],angular_level=level,angular_count=h,
                    eta_orientation=eps,full_fibre_count=D,core_radial_count=4,separate_actual_wall_count=1,
                    minimum_actual_core_Q_f=float(np.min(archive[prefix+'Q_f'][:4].real)),
                    minimum_actual_core_Q_sigma=float(np.min(archive[prefix+'Q_sigma'][:4].real)),
                    nonzero_terms=nonzero,literal_value_point=compare(action['value'],point),literal_value_weak=compare(weak['value'],form),
                    MP64_core_coefficient_first=controls,MP64_wall_coefficient_first=wall_controls,affine_germ_FD_sweep=fd,
                    weak_value=encode(weak['value']),weak_first=encode(weak['first']),
                    density_contact=encode(weak['density_contact']),independent_left_contact=encode(weak['independent_left_contact']),
                    coefficient_contact_norm=float(np.linalg.norm(action['coefficient_contact'])),
                    moving_trial_contact_norm=float(np.linalg.norm(action['moving_trial_contact'])),
                    exact_phase_partial_norm=float(np.linalg.norm(action['phase_frequency_partial'])),
                    exact_time_phase_mixed_norm=float(np.linalg.norm(action['phase_frequency_partial_first'])),
                    positive_value=encode(positive['value']),positive_first=encode(positive['first']),
                    positive_value_minimum_eigenvalue=float(np.min(np.linalg.eigvalsh(positive['value'])))))
                del germ,wallg,positive,G,Gx
    for name,module in list(sys.modules.items()):
        p=getattr(module,'__file__',None)
        if name.startswith('bhsm.') and p and Path(p).is_relative_to(ROOT):pin(p)
    pin(__file__)
    worst_mp=max(r[k]['maximum']['scaled'] for r in records for k in ('MP64_core_coefficient_first','MP64_wall_coefficient_first'))
    worst_literal=max(r[k]['scaled'] for r in records for k in ('literal_value_point','literal_value_weak'))
    if worst_mp>2e-12 or worst_literal>2e-12:raise ArithmeticError('independent local coefficient/value control failed')
    out.mkdir(parents=True);_compressed_npz(out/'application.npz',arrays)
    result=dict(classification='ACTUAL_REAL_FULL384_D5_FROZEN_CELL_SOURCE_FIRST_APPLICATION',records=records,
        source_axis='sole saved c[*_first][0]: coordinate-time direction frozen inside the original represented cell',
        solved_field_acceleration_or_second_source_jet_fabricated=False,
        supplied_test_maps='declared dense algebraic polynomial probes; exact V_x=V_t and V_rho,x/V_t,x contacts',
        independent_left_conjugated=False,source_coefficients_conjugated=False,
        off_shell_phase_frequency=energy,phase_frequency_source_first=energy_first,
        physical_E_B_or_outgoing_domain_derivative=False,exact_phase_partial_and_time_phase_mixed_retained=True,
        core_measure='original Gauss4 coordinate weights times 2pi² and actual NCR³ density ONCE',
        positive_current_Gram='owned real fixed-Eulerian I384; Gram source first zero in this fixed representation',
        eta_owner='combined original f-gradient collar coefficient continued analytically; not a global unit normal',
        sigma_normal_failure_preserved=True,abs_Q_or_Wick_or_eta_deletion=False,
        midpoint_fields_are_saved_real_trial_backgrounds=True,physical_stationary_background_solved=False,
        physical_normal_mode_normalization_or_spin_state=False,physical_exterior_load=None,
        full_native_or_stratified_domain_selected=False,physical_radial_or_angular_convergence=False,
        full_physical_derivative_at_2e_minus10=False,Maxwell_or_226_after_correction_validated=False,
        coupled_corrections=0,new_history_profile_source_or_D5_integrations=0,physical_muon_magnetic_moment=None,
        finite_difference_scope='affine extension of supplied first germ for numerical verification only; NOT reevaluated physical histories',
        inherited_background_parameter_scope='historical provisional real finite iterate; no new physical preparation or matching imposed',
        inherited_failure_input_lineage=report['input_and_source_sha256'],input_and_source_sha256=dict(sorted(pins.items())),
        worst_MP64_scaled=worst_mp,worst_literal_value_scaled=worst_literal,
        numerical_sha256=sha256((out/'application.npz').read_bytes()).hexdigest())
    (out/'result.json').write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(records=len(records),worst_MP64_scaled=worst_mp,worst_literal_value_scaled=worst_literal,
        numerical_sha256=result['numerical_sha256'],full_physical_derivative_pass=False)))
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inputs',default=str(ROOT/'artifacts/muon_real_coupled_open_operator_20261016/normal_chart_failure_run_1'))
    parser.add_argument('--output',required=True)
    args=parser.parse_args();execute(args.inputs,args.output)
