"""Independent angle/VA/total-three-marginal checks of complete local C."""
from pathlib import Path
import argparse,hashlib,json
import numpy as np
from numpy.polynomial.legendre import leggauss
from daughter_spin_math import (I2,PAULI,charged_spinor,va_tensor,va_neutrino_analyzer,
    joint_spin_kernel,parent_analyzer,sphere_rule)
from generic_neutrino_spectrum import (neutrino_parent_analyzer,neutrino_parent_analyzer_first,
    neutrino_phase_prefactor)

HERE=Path(__file__).resolve().parent
def mx(a):return float(np.max(abs(a)))
def rel(a,b):return mx(a-b)/max(mx(a),mx(b),np.finfo(float).tiny)

def direct_pair_angles(C,*,M,m,E,direction,species):
    """Literal two-body boost + charged4/neutral2 densities, no pair moments."""
    n=np.asarray(direction);q0=M-E;s=M*M-2*M*E;root=np.sqrt(s);beta=-n
    U=charged_spinor(M,np.zeros(3));out=np.zeros((2,2),complex)
    tagged=E*I2-E*np.einsum('i,ijk->jk',n,PAULI)
    for u in np.vstack((np.eye(3),-np.eye(3))):
        En=(s-m*m)/(2*root);Ee=(s+m*m)/(2*root);d=beta@u
        pv=En*u+((q0/root-1)*En*d+E*En/root)*beta
        ep=q0/root*En+E/root*En*d
        kp=np.r_[q0-ep,-E*n-pv]
        re=np.block([[kp[0]*I2-np.einsum('i,ijk->jk',kp[1:],PAULI),m*I2],
                     [m*I2,kp[0]*I2+np.einsum('i,ijk->jk',kp[1:],PAULI)]])
        rn=ep*I2-np.einsum('i,ijk->jk',pv,PAULI)
        nu,anti=(tagged,rn)if species=='nu_mu'else(rn,tagged)
        out+=np.einsum('abcd,efgh,bs,ft,ea,gc,dh->ts',C,C.conj(),U,U.conj(),nu,re,anti,optimize=True)/6
    return out

def integrated_all_three(C,*,M,m,order):
    z,w=leggauss(order);normals,aw=sphere_rule(3)
    v=(z+1)/2;vw=w/2;alpha=(M-m)**2/(2*M)
    e=np.zeros((2,2),complex);nn={s:np.zeros((2,2),complex)for s in('nu_mu','anti_nu_e')}
    for vi,wi in zip(v,vw):
        E=m+alpha*vi*vi;p=np.sqrt(E*E-m*m)
        for n,weight in zip(normals,aw):
            D=parent_analyzer(joint_spin_kernel(C,M=M,m=m,E=E,direction=n))
            e+=wi*2*alpha*vi*weight*p/(64*np.pi**3*M)*D
    Emax=(M*M-m*m)/(2*M);en=(z+1)*Emax/2;ew=w*Emax/2
    for E,wi in zip(en,ew):
        for n,weight in zip(normals,aw):
            for species in nn:
                D=neutrino_parent_analyzer(C,M=M,m=m,E=E,direction=n,species=species)
                nn[species]+=wi*weight*neutrino_phase_prefactor(M=M,m=m,E=E)*D
    return e,nn

def run(out):
    out.mkdir(parents=True,exist_ok=False)
    baseline=HERE/'run_1/application.npz'
    with np.load(baseline,allow_pickle=False)as a:
        T=a['arbitrary_tensor'];dT=a['coefficient_direction']
    C=va_tensor();n=np.array([2/3,1/3,2/3]);G0=1/(1536*np.pi**3)
    va=[];generic=[];first=[];data={}
    for m in (0.,.07,.23,.63):
        for species in ('nu_mu','anti_nu_e'):
            for f in (.19,.57,.83):
                E=f*(1-m*m)/2;kw=dict(M=1.,m=m,E=E,direction=n,species=species)
                D=neutrino_parent_analyzer(C,**kw);phase=neutrino_phase_prefactor(M=1.,m=m,E=E)
                exact=G0*va_neutrino_analyzer(2*E,n,mass_squared_ratio=m*m,species=species)
                va.append(dict(m=m,species=species,E=E,relative=rel(phase*D/2,exact)))
                A=neutrino_parent_analyzer(T,**kw);literal=direct_pair_angles(T,**kw)
                generic.append(dict(m=m,species=species,E=E,relative=rel(A,literal)))
                dA=neutrino_parent_analyzer_first(T,dT,**kw);h=1/16
                fd=(neutrino_parent_analyzer(T+h*dT,**kw)-neutrino_parent_analyzer(T-h*dT,**kw))/(2*h)
                first.append(dict(m=m,species=species,E=E,relative=rel(dA,fd)))
                if m==.23 and f==.57:data[species+'_analyzer']=A;data[species+'_first']=dA
    # Preserve complex spin coherences in a FULL 2x2 integrated identity,
    # not just a scalar unpolarized rate.
    ee,nn=integrated_all_three(T,M=1.,m=.23,order=64)
    totals={s:rel(ee,v)for s,v in nn.items()}
    data['integrated_electron_parent_analyzer']=ee
    for s,v in nn.items():data['integrated_'+s+'_parent_analyzer']=v
    # Analytic-left directional check without imposing conjugation on that axis.
    L=.7*T.conj()+.13j*dT;dL=-.11*T+.29j*dT.conj()
    kw=dict(M=1.,m=.23,E=.27,direction=n,species='nu_mu');h=1/16
    aj=neutrino_parent_analyzer_first(T,dT,left_tensor=L,left_first=dL,**kw)
    af=(neutrino_parent_analyzer(T+h*dT,left_tensor=L+h*dL,**kw)-neutrino_parent_analyzer(T-h*dT,left_tensor=L-h*dL,**kw))/(2*h)
    result=dict(va_finite_mass_analyzers=va,arbitrary_complete_tensor_pair_angles=generic,
        coefficient_functional_first=first,independent_analytic_left_first_relative=rel(aj,af),
        arbitrary_complete_tensor_integrated_all_three_parent_spin_relative=totals,
        phase_convention='dGamma/dE/dOmega_over_4pi = E(1-m^2/s)/(64pi^3 M) Tr(rho D)',
        neutrino_masses_zero=True,charged_mass_exact=True,physical_local_operator_identified=False,
        physical_outgoing_derivative_pass=False,physical_muon_decay_prediction=False,
        six_cartesian_pair_angle_rule='degree2 spherical rule exact for this STATIC local squared amplitude',
        no_observed_mass_coupling_or_lifetime_fit=True)
    maximum=max([a['relative']for a in va+generic+first]+list(totals.values())+[rel(aj,af)])
    result['largest_local_control_relative']=maximum;result['local_controls_pass']=bool(maximum<2e-10)
    pins=[Path(__file__),HERE/'generic_neutrino_spectrum.py',HERE/'daughter_spin_math.py',baseline,HERE/'run_1/result.json']
    result['source_and_input_sha256']={str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in pins}
    np.savez_compressed(out/'application.npz',**data)
    result['numerical_sha256']=hashlib.sha256((out/'application.npz').read_bytes()).hexdigest()
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    (out/'executed_producer.py').write_bytes(Path(__file__).read_bytes())
    (out/'executed_math.py').write_bytes((HERE/'generic_neutrino_spectrum.py').read_bytes())
    print(json.dumps(dict(largest_local_control_relative=maximum,integrated_three_parent_spin=totals)))
    if not result['local_controls_pass']:raise ArithmeticError('local neutrino controls did not pass')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);run(p.parse_args().out)
