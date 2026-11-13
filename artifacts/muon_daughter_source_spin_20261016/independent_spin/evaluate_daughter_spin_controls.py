"""Independent local decay controls.  No fitted mass/coupling or physical gate."""
from pathlib import Path
import argparse,json,hashlib,importlib.util
import numpy as np
import mpmath as mp
from numpy.polynomial.legendre import leggauss
from daughter_spin_math import *

HERE=Path(__file__).resolve().parent
REPO=Path(r'C:/Users/carbe/Downloads/BHSM_muon_parent_maxwell_worktree_20261001')

def mx(a):return float(np.max(abs(a)))
def rel(a,b):return mx(a-b)/max(mx(a),mx(b),np.finfo(float).tiny)

def literal_gamma_joint(M,m,E,n):
    """Six-point degree-two exact angular rule and literal gamma currents."""
    p=np.sqrt(E*E-m*m);U=charged_spinor(M,np.zeros(3));V=charged_spinor(m,p*n)
    out=np.zeros((2,2,2,2),complex)
    for u in np.vstack((np.eye(3),-np.eye(3))):
        pn,pa=pair_momenta(M=M,m=m,E=E,n=n,u=u)
        def spinor(v):
            R=v[0]*I2-np.einsum('i,ijk->jk',v[1:],PAULI)
            j=int(np.argmax(R.diagonal().real));w=R[:,j]/np.sqrt(R[j,j].real)
            return np.r_[w,0.,0.]
        nu=spinor(pn);anti=spinor(pa)
        A=np.zeros((2,2),complex)
        for mu in range(4):
            left=nu.conj()@GAMMA[0]@GAMMA[mu]@PL@U
            right=V.conj().T@GAMMA[0]@GAMMA[mu]@PL@anti
            A+=METRIC[mu]*np.outer(right,left)
        out+=np.einsum('rs,lt->rlst',A,A.conj())/6
    return out

def mp_direct_joint(C,M,m,E,n,*,return_mp=False):
    """Independent 65-dps amplitude sum, no analytic pair moment/einsum."""
    if not return_mp:mp.mp.dps=65
    conv=lambda v:mp.mpc(v)if isinstance(v,(mp.mpf,mp.mpc))else mp.mpc(float(np.real(v)),float(np.imag(v)))
    M=mp.mpf(M);m=mp.mpf(m);E=mp.mpf(E);n=list(map(mp.mpf,n))
    p=mp.sqrt(E*E-m*m);s=M*M+m*m-2*M*E;root=mp.sqrt(s);q0=M-E;b=[-v for v in n]
    sig=[mp.matrix([[0,1],[1,0]]),mp.matrix([[0,-1j],[1j,0]]),mp.matrix([[1,0],[0,-1]])]
    mat=lambda a:sum((a[i]*sig[i]for i in range(3)),mp.zeros(2))
    t=mp.sqrt(E+m);sp=mat([p*v for v in n]);ve=mp.matrix(4,2)
    for r in range(2):
        for z in range(2):
            ve[z,r]=(t*(z==r)-sp[z,r]/t)/mp.sqrt(2)
            ve[z+2,r]=(t*(z==r)+sp[z,r]/t)/mp.sqrt(2)
    um=mp.matrix([[mp.sqrt(M),0],[0,mp.sqrt(M)],[mp.sqrt(M),0],[0,mp.sqrt(M)]])
    out=np.empty((2,2,2,2),object);out.fill(mp.mpc(0))
    for axis in range(3):
        for sign in (-1,1):
            u=[mp.mpf(sign if i==axis else 0)for i in range(3)];d=sum(b[i]*u[i]for i in range(3))
            nv=[root*u[i]/2+((q0-root)*d+p)*b[i]/2 for i in range(3)]
            ne=q0/2+p*d/2;av=[-p*n[i]-nv[i]for i in range(3)];ae=q0-ne
            def w(Ev,pv):
                R=Ev*mp.eye(2)-mat(pv);j=0 if R[0,0].real>=R[1,1].real else 1
                return [R[i,j]/mp.sqrt(R[j,j].real)for i in range(2)]
            wn=w(ne,nv);wa=w(ae,av);A=mp.matrix(2,2)
            for r in range(2):
                for z in range(2):
                    A[r,z]=sum(conv(C[a,b_,c,d_])*mp.conj(wn[a])*um[b_,z]*mp.conj(ve[c,r])*wa[d_]
                        for a in range(2)for b_ in range(4)for c in range(4)for d_ in range(2))
            for r in range(2):
                for l in range(2):
                    for z in range(2):
                        for t_ in range(2):out[r,l,z,t_]+=A[r,z]*mp.conj(A[l,t_])/6
    return out if return_mp else np.array([complex(v)for v in out.flat]).reshape(out.shape)

def integrate_va(M,m,order):
    z,w=leggauss(order);v=(z+1)/2;w=w/2;a=(M-m)**2/(2*M)
    out=0.
    for vi,wi in zip(v,w):
        E=m+a*vi*vi;p=np.sqrt(max(0.,E*E-m*m))
        D=va_parent_analyzer(M=M,m=m,E=E,direction=np.array([0.,0.,1.]))
        out+=wi*(2*a*vi)*p/(64*np.pi**3*M)*np.trace(D).real/2
    return out

def gamma_neutral_marginal(y,m,n,species):
    """Unequal-mass two-body phase space + independent 4x4 gamma trace."""
    M=1.;En=y/2;s=1-y;root=np.sqrt(s);q0=1-En;beta=-n;pn0=np.r_[En,En*n]
    out=np.zeros((2,2),complex)
    for u in np.vstack((np.eye(3),-np.eye(3))):
        e=(s-m*m)/(2*root);d=beta@u
        pv=e*u+((q0/root-1)*e*d+En*e/root)*beta
        v=np.r_[q0/root*e+En/root*e*d,pv]
        q=np.r_[q0,-En*n];k=q-v
        pn,pa=(pn0,v)if species=='nu_mu'else(v,pn0)
        out+=literal_gamma_analyzer(np.array([1.,0.,0.,0.]),k,pn,pa,M=1.,m=m)/6
    # dE/dy=1/2 and pair velocity 1-m^2/s.
    return out*(En/(64*np.pi**3))*(1-m*m/s)/2/(1/(1536*np.pi**3))

def run(outdir):
    outdir.mkdir(parents=True,exist_ok=False)
    C=va_tensor();n=np.array([2/3,1/3,2/3]);records={};arrays={}
    foundation=REPO/'src/bhsm/interface/completion/foundational_dirac_spin_glue_v14_45.py'
    sourceframe=REPO/'src/bhsm/interface/muon_local_source_jet.py'
    def load(path,name):
        spec=importlib.util.spec_from_file_location(name,path);owner=importlib.util.module_from_spec(spec);spec.loader.exec_module(owner);return owner
    gamma_owner=load(foundation,'actual_foundational_gamma')
    frame_owner=load(sourceframe,'actual_source_spin_frame')
    gamma_actual=frame_owner.source_spin_frame(gamma_owner.dirac_gamma_matrices())['gamma_LR']
    records['actual_owned_gamma_LR_absolute_difference']=mx(gamma_actual-GAMMA)
    gamma_errors=[];pair_errors=[];plus_errors=[];inv_errors=[]
    for m in (0.,.07,.23,.63):
        for f in (.17,.51,.89):
            E=m+f*((1+m*m)/2-m);p=np.sqrt(E*E-m*m)
            K=joint_spin_kernel(C,M=1.,m=m,E=E,direction=n)
            literal=literal_gamma_joint(1.,m,E,n)
            gamma_errors.append(rel(K,literal))
            pair_errors.append(rel(parent_analyzer(K),va_parent_analyzer(M=1.,m=m,E=E,direction=n)))
            plus=parent_analyzer(positive_muon_joint_spin_kernel(C,M=1.,m=m,E=E,direction=n))
            plus_errors.append(rel(plus,va_parent_analyzer(M=1.,m=m,E=E,direction=n,charge=1)))
            pn,pa=pair_momenta(M=1.,m=m,E=E,n=n,u=np.array([1.,0.,0.]))
            g=literal_gamma_analyzer(np.r_[1.,0.,0.,0.],np.r_[E,p*n],pn,pa,M=1.,m=m)
            inv=literal_invariant_analyzer(np.r_[1.,0.,0.,0.],np.r_[E,p*n],pn,pa,M=1.)
            inv_errors.append(rel(g,inv))
    records['literal_gamma_joint_vs_exact_neutral_moment_max_relative']=max(gamma_errors)
    records['mu_minus_finite_mass_analyzer_max_relative']=max(pair_errors)
    records['explicit_hc_mu_plus_finite_mass_sign_max_relative']=max(plus_errors)
    records['literal_gamma_vs_polarized_invariant_max_relative']=max(inv_errors)
    rng=np.random.default_rng(20261016)
    T=(rng.normal(size=C.shape)+1j*rng.normal(size=C.shape))/7
    dT=(rng.normal(size=C.shape)+1j*rng.normal(size=C.shape))/9
    kw=dict(M=1.,m=.23,E=.37,direction=n)
    K=joint_spin_kernel(T,**kw);mK=mp_direct_joint(T,**dict(M=1.,m=.23,E=.37,n=n))
    records['arbitrary_complete_tensor_65dps_direct_amplitude_relative']=rel(K,mK)
    dK=joint_spin_kernel_first(T,dT,**kw);h=1/16
    fd=(joint_spin_kernel(T+h*dT,**kw)-joint_spin_kernel(T-h*dT,**kw))/(2*h)
    records['physical_coefficient_functional_first_relative']=rel(dK,fd)
    L=(rng.normal(size=C.shape)+1j*rng.normal(size=C.shape))/8
    dl=(rng.normal(size=C.shape)+1j*rng.normal(size=C.shape))/10
    analytic=joint_spin_kernel_first(T,dT,left_tensor=L,left_first=dl,**kw)
    afd=(joint_spin_kernel(T+h*dT,left_tensor=L+h*dl,**kw)-joint_spin_kernel(T-h*dT,left_tensor=L-h*dl,**kw))/(2*h)
    records['independent_analytic_left_right_first_relative']=rel(analytic,afd)
    # All matrix-valued product contacts, including density from phase space,
    # compared against 65-dps differentiation of the literal six-direction amplitude.
    dM,dm,dE=.17,-.035,.041;dn=np.cross(np.array([.07,-.11,.13]),n)
    kfirst,pfirst=joint_spin_kernel_kinematic_first(T,dT,**kw,M_first=dM,m_first=dm,E_first=dE,direction_first=dn)
    conv=lambda v:mp.mpc(float(np.real(v)),float(np.imag(v)))
    Tmp=np.empty(T.shape,object);dTmp=np.empty(T.shape,object)
    for ix in np.ndindex(T.shape):Tmp[ix]=conv(T[ix]);dTmp[ix]=conv(dT[ix])
    def mpath(t):
        nv=[mp.mpf(float(n[i]))+t*mp.mpf(float(dn[i]))for i in range(3)]
        norm=mp.sqrt(sum(v*v for v in nv));nv=[v/norm for v in nv]
        return mp_direct_joint(Tmp+t*dTmp,mp.mpf(1)+t*mp.mpf(dM),mp.mpf(.23)+t*mp.mpf(dm),
            mp.mpf(.37)+t*mp.mpf(dE),nv,return_mp=True)
    mpfirst=np.array([complex(mp.diff(lambda t:mpath(t)[ix],0))for ix in np.ndindex(K.shape)]).reshape(K.shape)
    records['full_real_kinematic_coefficient_first_65dps_relative']=rel(kfirst,mpfirst)
    phase_mp=lambda t:mp.sqrt((mp.mpf(.37)+t*dE)**2-(mp.mpf(.23)+t*dm)**2)/(64*mp.pi**3*(1+t*dM))
    records['phase_space_first_65dps_relative']=abs(pfirst-float(mp.diff(phase_mp,0)))/abs(pfirst)
    phase=joint_spin_kernel_first(T,1j*T,**kw)
    records['global_vertex_phase_first_absolute']=mx(phase)
    records['global_vertex_scale_first_relative']=rel(joint_spin_kernel_first(T,T,**kw),2*K)
    choi=K.transpose(0,2,1,3).reshape(4,4)
    records['choi_hermiticity_absolute']=mx(choi-choi.conj().T)
    records['choi_smallest_eigenvalue']=float(np.linalg.eigvalsh(choi)[0])
    rho=(I2+.21*PAULI[0]-.37*PAULI[1]+.24*PAULI[2])/2
    spin,weight,dspin,dweight=normalized_electron_state(K,rho,kernel_first=dK)
    sp=normalized_electron_state(joint_spin_kernel(T+h*dT,**kw),rho)[0]
    sm=normalized_electron_state(joint_spin_kernel(T-h*dT,**kw),rho)[0]
    # Rational quotient has higher powers: a small h sweep is retained.
    quotient=[]
    for qh in (1e-2,1e-3,1e-4,1e-5):
        qp=normalized_electron_state(joint_spin_kernel(T+qh*dT,**kw),rho)[0]
        qm=normalized_electron_state(joint_spin_kernel(T-qh*dT,**kw),rho)[0]
        quotient.append(dict(step=qh,relative=rel(dspin,(qp-qm)/(2*qh))))
    records['conditional_spin_quotient_fd_sweep']=quotient
    records['conditional_spin_first_trace_absolute']=float(abs(np.trace(dspin)))
    for charge in (-1,1):
        vK=joint_spin_kernel(C,M=1.,m=0.,E=.4,direction=n)if charge==-1 else positive_muon_joint_spin_kernel(C,M=1.,m=0.,E=.4,direction=n)
        vrho=normalized_electron_state(vK,rho)[0]
        records[f'charge{charge}_massless_daughter_longitudinal_polarization']=float(np.trace(vrho@np.einsum('i,ijk->jk',n,PAULI)).real)
    totals=[]
    for m in (0.,.01,.07,.23,.63):
        r=mp.mpf(float(m))**2
        phase=float(1-8*r+8*r**3-r**4-12*r*r*mp.log(r))if r else 1.
        expected=phase/(1536*np.pi**3)
        row=dict(m=m,phase_factor=phase,exact_rate=expected)
        for order in (32,64):row[f'gauss{order}_rate']=integrate_va(1.,m,order)
        row['relative64']=abs(row['gauss64_rate']-expected)/expected
        totals.append(row)
    records['finite_mass_phase_space']=totals
    neutral=[]
    for m in (0.,.07,.23,.63):
        for species in ('nu_mu','anti_nu_e'):
            for f in (.19,.57,.83):
                y=f*(1-m*m)
                a=va_neutrino_analyzer(y,n,mass_squared_ratio=m*m,species=species)
                b=gamma_neutral_marginal(y,m,n,species)
                neutral.append(dict(m=m,species=species,y=y,relative=rel(a,b)))
    records['neutrino_marginals_literal_gamma_max_relative']=max(a['relative']for a in neutral)
    records['neutrino_marginal_controls']=neutral
    integrals=[]
    z,w=leggauss(96)
    for m in (0.,.07,.23,.63):
        phase=next(a['phase_factor']for a in totals if a['m']==m)
        for species in ('nu_mu','anti_nu_e'):
            y=(z+1)*(1-m*m)/2;ww=w*(1-m*m)/2
            val=sum(wwi*np.trace(va_neutrino_analyzer(yi,n,mass_squared_ratio=m*m,species=species)).real/2 for yi,wwi in zip(y,ww))
            integrals.append(dict(m=m,species=species,integral=float(val),relative=abs(val-phase)/phase))
    records['neutrino_marginal_integrated_phase_factor']=integrals
    # Independent existing spin-summed producer, with no measured-mass or fit.
    decay=REPO/'src/bhsm/interface/muon_coupled_tensor_decay_rate.py'
    spec=importlib.util.spec_from_file_location('retained_decay',decay);owner=importlib.util.module_from_spec(spec);spec.loader.exec_module(owner)
    legacy=[]
    for m in (0.,.07,.23):
        r=owner.tensor_tree_decay_rate(C,muon_mass_GeV=1.,electron_mass_GeV=m,radial_order=48,angular_order=3,muon_charge=-1)
        expected=next(a['exact_rate']for a in totals if a['m']==m)
        legacy.append(dict(m=m,rate=r['tree_rate_GeV_for_tensor_GeV_minus2'],relative=abs(r['tree_rate_GeV_for_tensor_GeV_minus2']-expected)/expected))
    records['existing_spin_sum_phase_space_control']=legacy
    scalars=[max(gamma_errors),max(pair_errors),max(plus_errors),max(inv_errors),rel(K,mK),rel(dK,fd),rel(analytic,afd),
        rel(kfirst,mpfirst),records['phase_space_first_65dps_relative'],quotient[-1]['relative'],
        max(a['relative64']for a in totals),max(a['relative']for a in neutral),max(a['relative']for a in integrals),max(a['relative']for a in legacy)]
    records['local_numerical_controls_threshold']=2e-10
    records['largest_stated_local_control_relative']=max(scalars)
    records['local_controls_pass']=bool(max(scalars)<2e-10)
    records['physical_outgoing_derivative_pass']=False
    records['physical_muon_decay_prediction']=False
    records['local_vertex_low_energy_projection_identified']=False
    records['neutrino_mass_scope']='neutrino masses zero; daughter charged mass retained exactly'
    records['input_scope']='dimensionless declared kinematics and deterministic full-tensor controls; no calibrated mass/coupling/lifetime input'
    records['pdg_control']='https://pdg.lbl.gov/2025/reviews/rpp2025-rev-muon-decay-params.pdf Eqs57.3,57.9; VA template control only'
    pins=[Path(__file__),HERE/'daughter_spin_math.py',decay,foundation,
        REPO/'src/bhsm/interface/muon_charged_current_fermi_reduction.py',
        REPO/'src/bhsm/interface/muon_primal_charged_current_response.py',
        REPO/'src/bhsm/interface/muon_local_source_jet.py']
    records['source_pins']={str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in pins}
    arrays.update(arbitrary_tensor=T,coefficient_direction=dT,joint_kernel=K,joint_kernel_first=dK,independent_mp_joint_kernel=mK,
        parent_density=rho,conditional_electron_density=spin,conditional_electron_density_first=dspin)
    np.savez_compressed(outdir/'application.npz',**arrays)
    records['numerical_sha256']=hashlib.sha256((outdir/'application.npz').read_bytes()).hexdigest()
    (outdir/'result.json').write_text(json.dumps(records,indent=2,sort_keys=True)+'\n')
    (outdir/'executed_producer.py').write_bytes(Path(__file__).read_bytes())
    (outdir/'executed_math.py').write_bytes((HERE/'daughter_spin_math.py').read_bytes())
    print(json.dumps({k:records[k]for k in ('local_controls_pass','largest_stated_local_control_relative','neutrino_marginals_literal_gamma_max_relative','explicit_hc_mu_plus_finite_mass_sign_max_relative','arbitrary_complete_tensor_65dps_direct_amplitude_relative')}))
    if not records['local_controls_pass']:raise ArithmeticError('declared local numerical controls did not pass')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);run(p.parse_args().out)
