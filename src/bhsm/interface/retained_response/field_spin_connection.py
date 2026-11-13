"""Evaluated open-wall Higgs/gauge-to-lepton response on retained histories.

Fixed-geometry, prescribed original wall-coordinate variations only. No wall-law
closure, collider state, quantum sea, two-spin pole, or muon anomaly is selected.
The stored Higgs collocation responses and lepton coefficient samples are reused.
"""
from __future__ import annotations
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('OMP_NUM_THREADS','1')
import json, math, hashlib
from pathlib import Path
from functools import lru_cache
import sys
import numpy as np
from numpy.polynomial import Polynomial
from scipy.linalg import solve
from scipy.integrate import solve_ivp

ROOT=Path(__file__).resolve().parents[4]/'artifacts/muon_retained_response_20261018'
from .finite_time_response import (YUKAWA, PAULI, derivatives, interpolate, dagger,
                                 mx, comm, sample_operators, evolve, write_npz)
from .compatible_source import scalar_labels, cg, retained_representation, haar_rule, scalar_values
from .retained_magnetic_application import wall_data

LABELS=('lo','q000','q001','q002','q003','hi')
NINPUT=166
INPUT_ORDER='initial Higgs canonical32; original wall64*(1,tau); magnetic3*(1,tau)'


def verify_inputs():
    meta=json.loads((ROOT/'inputs/PROVENANCE.json').read_text())
    for name,record in meta['files'].items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=record['sha256']:
            raise ValueError('input changed: '+name)
    for name,expected in meta['maintained_source_sha256'].items():
        if hashlib.sha256((Path(__file__).parent/name).read_bytes()).hexdigest()!=expected:
            raise ValueError('maintained source changed: '+name)
    repo=Path(__file__).resolve().parents[4]
    for name,expected in meta['live_owner_lf_sha256'].items():
        payload=(repo/name).read_bytes().replace(b'\r\n',b'\n')
        if hashlib.sha256(payload).hexdigest()!=expected:
            raise ValueError('live owner changed; review affected cached applications: '+name)
    return meta


def gaussian_table():
    c,b=np.polynomial.legendre.leggauss(4);c=(c+1)/2;b=b/2
    polys=[];integrals=[]
    for j in range(4):
        p=Polynomial.fromroots(np.delete(c,j));p=p/p(c[j]);ip=p.integ();ip=ip-ip(0)
        polys.append(p);integrals.append(ip)
    return c,b,polys,integrals


@lru_cache(None)
def real_n1_multiplication(nmax=2):
    """Exact CG products for Y=(2x0,2x1,2x2,2x3), then a declared finite cutoff.

    For n<=1 initial fields, one insertion reaches n<=2. All n<=2 inputs
    instead need n<=3 outputs, which the nmax=2 square compression omits.
    """
    labels=scalar_labels(nmax);gs=scalar_labels(1);ix={v:i for i,v in enumerate(gs)}
    cf=np.zeros((4,len(gs)),complex);s=1/np.sqrt(2)
    cf[0,ix[1,1,1]]=s;cf[0,ix[1,-1,-1]]=s
    cf[1,ix[1,1,1]]=1j*s;cf[1,ix[1,-1,-1]]=-1j*s
    cf[2,ix[1,1,-1]]=s;cf[2,ix[1,-1,1]]=-s
    cf[3,ix[1,1,-1]]=1j*s;cf[3,ix[1,-1,1]]=1j*s
    out=np.zeros((4,len(labels),len(labels)),complex)
    for gi,(ng,mg,kg) in enumerate(gs):
        if ng!=1:continue
        for si,(ns,ms,ks) in enumerate(labels):
            for ti,(nt,mt,kt) in enumerate(labels):
                if mt!=ms+mg or kt!=ks+kg or not abs(ns-ng)<=nt<=ns+ng or (ns+ng-nt)%2:continue
                coeff=math.sqrt((ns+1)*(ng+1)/(nt+1))*float(cg(ns,ms,ng,mg,nt,mt)*cg(ns,ks,ng,kg,nt,kt))
                out[:,ti,si]+=cf[:,gi]*coeff
    return out


@lru_cache(None)
def field_vertices(nmax=2):
    """80 Hermitian matrices; numerical N/R, 1/T, N are in coefficient maps.

    Gauge field order is (At,A1,A2,A3), internal4, real harmonic4. Scalar
    order is (ReH1,ReH2,ImH1,ImH2), real harmonic4. Fixed Y_middle retained.
    """
    G18,a18,_=retained_representation();ids=np.array([2,3,8,9,14,15])
    G=G18[:,ids][:,:,ids];alpha=a18[:,ids][:,:,ids]
    Y=real_n1_multiplication(nmax);n=6*len(Y[0]);V=np.zeros((80,n,n),complex)
    for f,c,h in np.ndindex(4,4,4):
        fiber=-1j*G[c] if f==0 else -1j*alpha[f-1]@G[c]
        V[(f*4+c)*4+h]=np.kron(Y[h],fiber)
    Mass=[]
    for r in range(4):
        H=np.eye(4)[r];hc=H[:2]+1j*H[2:]
        m=np.zeros((6,6),complex);x=YUKAWA[1]*np.kron(hc[:,None],np.eye(2))
        m[:4,4:]=x;m[4:,:4]=x.conj().T;Mass.append(m)
        for h in range(4):V[64+r*4+h]=np.kron(Y[h],m)
    return dict(V=V,G=G,alpha=alpha,mass=np.array(Mass),family_ids=ids,Y=Y)


class OpenFieldPath:
    """One arm's saved scalar dynamics and explicit wall inputs.

    Constructing this object performs no new Higgs or Maxwell solve. It only
    reconstructs the collocation polynomial from the saved canonical stages.
    No interpolation of these data is promoted to the physical history.
    """
    def __init__(self,side):
        if side not in ('incoming','outgoing'):raise ValueError('incoming or outgoing required')
        self.side=side
        def load(name):
            with np.load(ROOT/'inputs'/name,allow_pickle=False) as z:return {k:z[k].copy() for k in z.files}
        self.ops=load(side+'_spin_operators.npz')
        self.hs=load(side+'_higgs_response.npz');self.hc=load(side+'_higgs_coefficients.npz')
        self.t=self.ops['sample_time'];self.T=float(self.t[-1]-self.t[0]);self.s=(self.t-self.t[0])/self.T
        self.samples=[load(side+'_'+k+'.npz') for k in LABELS]
        self.raw=np.array([r['raw'] for r in self.samples]);self.wall=[wall_data(r) for r in self.raw]
        self.N=np.array([d['lapse'] for d in self.wall]);self.R4=np.array([d['R4'] for d in self.wall])
        self.W=np.array([r['Wg'] for r in self.samples]);self.Wd=np.array([r['Wgdot'] for r in self.samples])
        self.J=self.hs['coordinate_frame']
        self.initial=np.c_[np.eye(32),np.zeros((32,134))]
        self.c,self.b,self.lagrange,self.integrals=gaussian_table()
        if mx(self.c-self.s[1:5])>2e-14:raise ValueError('stored chronological nodes mismatch')
        self.stage_rates=[];self.F=[];self.forces=[];self.initial_rates={}
        for i,lab in enumerate(LABELS):
            G,Gd=self.wall_input_at_sample(i)
            M,B,K=[self.hc[lab+'_'+k] for k in ('M','B','K')]
            F,g=self.scalar_system(M,B,K,G,Gd)
            if lab.startswith('q'):
                j=i-1;self.stage_rates.append(F@self.hs['stages'][j]+np.c_[np.zeros((32,32)),g]);self.F.append(F);self.forces.append(g)
            else:
                z=self.initial if lab=='lo' else self.hs['final']
                self.initial_rates[lab]=F@z+np.c_[np.zeros((32,32)),g]
        self.stage_rates=np.array(self.stage_rates);self.F=np.array(self.F);self.forces=np.array(self.forces)
        checks=[mx(self.scalar_state(s)-self.hs['stages'][j]) for j,s in enumerate(self.c)]
        checks+=[mx(self.scalar_state(0)-self.initial),mx(self.scalar_state(1)-self.hs['final'])]
        self.saved_reconstruction_error=max(checks)
        if self.saved_reconstruction_error>1e-12:raise ValueError('Higgs polynomial no longer matches saved stages/endpoints')
        self.history=dict(s=self.s,H=self.ops['H_coordinate_time'],V=self.ops['direct_magnetic_insertions_per_e'],
                          T=self.T,S=self.ops['spin_generators'],N=self.N)

    @staticmethod
    def scalar_system(M,B,K,G,Gd):
        mass=M[:16,:16];Bxx=B[:16,:16];Kxx=K[:16,:16]
        hh=B[16:,:16].T@G+M[:16,16:]@Gd;ff=K[:16,16:]@G+B[:16,16:]@Gd
        v=solve(mass,np.c_[Bxx.T,np.eye(16),hh],assume_a='pos')
        nx=-v[:,:16];ip=v[:,16:32];src=-v[:,32:]
        F=np.block([[nx,ip],[Kxx+Bxx@nx,Bxx@ip]])
        return F,np.vstack((src,ff+Bxx@src))

    def wall_input_at_sample(self,i):
        tau=self.s[i];G=np.zeros((64,134));Gd=np.zeros_like(G)
        G[:,:64]=np.eye(64);G[:,64:128]=tau*np.eye(64);Gd[:,64:128]=np.eye(64)
        W=self.W[i];Wd=self.T*self.Wd[i]
        G[:,128:131]=W;G[:,131:]=tau*W;Gd[:,128:131]=Wd;Gd[:,131:]=W+tau*Wd
        return G,Gd

    def wall_values(self,s):
        G=np.zeros((64,166));G[:,32:96]=np.eye(64);G[:,96:160]=s*np.eye(64)
        W=interpolate(self.s,self.W,s);G[:,160:163]=W;G[:,163:]=s*W
        return G

    def scalar_state(self,s):
        w=np.array([p(s) for p in self.integrals])
        return self.initial+np.einsum('j,jab->ab',w,self.stage_rates)

    def scalar_rate(self,s):
        return np.einsum('j,jab->ab',np.array([p(s) for p in self.lagrange]),self.stage_rates)

    def original_fields(self,s):
        """A_t material and spatial A, and real Higgs n1 coefficients, before N factors."""
        g=self.wall_values(s).copy();g[:16]/=self.T
        h=self.J[:16,:16]@self.scalar_state(s)[:16]
        return g,h

    def coefficients(self,s):
        """80x166 map into the fixed quantum field-variation vertices."""
        g,h=self.original_fields(s);N=float(interpolate(self.s,self.N,s));R=float(interpolate(self.s,self.R4,s))
        g[16:]*=N/R
        return np.vstack((g,N*h))

    def insertion(self,s,direction):
        d=np.asarray(direction,float)
        if d.shape!=(166,) or not np.isfinite(d).all():raise ValueError('finite declared166-coordinate source direction required')
        return np.einsum('b,bij->ij',self.coefficients(s)@d,field_vertices()['V'])


def integrated_response(path,U,order=12):
    """Endpoint operator derivative, n<=1 initial subspace and all reached n<=2 output.

    Returns separate prescribed-gauge and induced/initial-scalar parts. The gauge
    part already contains the direct magnetic boundary-lift columns. Adding the
    old direct magnetic answer to their total would count that insertion twice.
    """
    xx,ww=np.polynomial.legendre.leggauss(order);nodes=(xx+1)/2;ww=ww/2
    n=84;nin=30;vg=field_vertices()['V'];JG=np.zeros((166,n,nin),complex);JH=np.zeros_like(JG)
    for s,w in zip(nodes,ww):
        u=U(s);bi=dagger(u)@vg@u[:,:nin];coef=path.coefficients(s)
        JG+=path.T*w*np.tensordot(coef[:64].T,bi[:64],axes=(1,0))
        JH+=path.T*w*np.tensordot(coef[64:].T,bi[64:],axes=(1,0))
    J=JG+JH;uf=U(1.);OI=dagger(uf)@path.history['S']@uf
    def spin_response(j):
        # OI preserves the initial n<=1 subspace for this homogeneous base.
        jj=j[:,:nin];out=np.empty((166,3,nin,nin),complex)
        for a in range(3):out[:,a]=1j*(jj@OI[a,:nin,:nin]-OI[a,:nin,:nin]@jj)
        return out
    return dict(J_gauge=JG,J_Higgs=JH,J_total=J,
                propagator_first=-1j*uf@J,
                spin_first=spin_response(J),spin_gauge=spin_response(JG),spin_Higgs=spin_response(JH),
                initial_isometry=np.eye(n)[:,:nin],final_unperturbed=uf,
                spin_readout_leakage=max(mx(oi[nin:,:nin]) for oi in OI))


def independently_projected_insertion(path,s,direction,*,degree=7):
    """Original local six-component Hamiltonian, evaluated at Haar points.

    This does not call the CG matrices or the coefficient-to-operator contraction.
    Complete metric is fixed for this partial. Normal geometry jets are not zeroed
    in a claim of a total response; they are outside the present input set.
    """
    d=np.asarray(direction,float);g,h=path.original_fields(s);g=g@d;h=h@d
    sg,w,points=haar_rule(degree);phi=scalar_values(sg,2);Y=2*points
    gg=np.einsum('ph,fch->pfc',Y,g.reshape(4,4,4));hh=Y@h.reshape(4,4).T
    N=float(interpolate(path.s,path.N,s));R=float(interpolate(path.s,path.R4,s))
    # Recreate the point-fiber coefficients independently rather than reading V80.
    pauli=np.array([[[0,1],[1,0]],[[0,-1j],[1j,0]],[[1,0],[0,-1]]],complex)
    generators=np.zeros((4,6,6),complex);alpha=np.zeros((3,6,6),complex)
    for a in range(3):
        generators[a,:4,:4]=-1j*np.kron(pauli[a]/2,np.eye(2))/np.sqrt(2)
        alpha[a,:4,:4]=-np.kron(np.eye(2),pauli[a]);alpha[a,4:,4:]=pauli[a]
    generators[3]=-1j*np.diag([-.5,-.5,-.5,-.5,-1.,-1.])/np.sqrt(10/3)
    omega=np.einsum('pfc,cij->pfij',gg,generators)
    local=-1j*omega[:,0]-1j*N/R*np.einsum('aij,pajk->pik',alpha,omega[:,1:])
    hc=hh[:,:2]+1j*hh[:,2:];bridge=YUKAWA[1]*np.einsum('pa,st->past',hc,np.eye(2)).reshape(len(points),4,2)
    local[:,:4,4:]+=N*bridge;local[:,4:,:4]+=N*dagger(bridge)
    return np.einsum('p,pt,pij,ps->tisj',w,phi.conj(),local,phi).reshape(84,84)


def evolve_perturbed(path,direction,epsilon,*,rtol=2e-12,atol=2e-14):
    """Independent full propagator rerun on H0+epsilon*computed first-order field path.

    This validates the linearized-field composition. It is not a nonlinear
    self-consistent Maxwell/Higgs/collider re-solve at nonzero magnetic field.
    """
    direction=np.asarray(direction,float);V=field_vertices()['V'];T=path.T
    def rhs(s,y):
        H=interpolate(path.s,path.history['H'],s)
        coeff=path.coefficients(s)@direction
        H=H+epsilon*np.einsum('b,bij->ij',coeff,V)
        return (-1j*T*H@y.reshape(84,84)).ravel()
    sol=solve_ivp(rhs,(0.,1.),np.eye(84,dtype=complex).ravel(),method='DOP853',rtol=rtol,atol=atol,max_step=.125)
    if not sol.success:raise ArithmeticError(sol.message)
    return sol.y[:,-1].reshape(84,84)


def apply_open_result(result_directory,side,source_coefficients,*,initial_density=None):
    """Apply the evaluated linear maps to EXPLICIT supplied variation coefficients.

    This does not solve the wall equation. The optional finite30 density supplies
    an expectation in the mathematical initial subspace; its validation is not
    physical muon/state admission. Keep this distinct from the classical initial
    field variations among the 574 input coordinates.
    """
    if side not in ('incoming','outgoing'):raise ValueError('incoming or outgoing required')
    c=np.asarray(source_coefficients)
    if c.shape!=(574,) or not np.isrealobj(c) or not np.isfinite(c).all():
        raise ValueError('finite real574 linear input coefficients are required')
    root=Path(result_directory)
    verify_application_result(root)
    with np.load(root/f'{side}_joint_open_response.npz',allow_pickle=False) as f:
        final=f['classical_final_map']@c
        wall=f['classical_wall_map']@c
        endpoint=f['wall_temporal_endpoint']@c
        selected=f['field_to_spin_input_indices']
    with np.load(root/f'{side}_spin_response.npz',allow_pickle=False) as f:
        j=np.einsum('c,cij->ij',c[selected],f['J_gauge']+f['J_Higgs'])
        du=-1j*f['final_unperturbed']@j
        spin=np.einsum('c,cbij->bij',c[selected],f['spin_first'])
    result=dict(classical_final_variation=final,known_wall_weak_variation=wall,
                known_wall_temporal_endpoint_variation=endpoint,lepton_propagator_first=du,
                initial_space_spin_operator_first=spin,physical_wall_closed=False,
                physical_muon_admitted=False)
    if initial_density is not None:
        rho=np.asarray(initial_density,complex)
        if rho.shape!=(30,30) or not np.isfinite(rho).all():raise ValueError('finite30x30 initial density required')
        if mx(rho-dagger(rho))>1e-12 or abs(np.trace(rho)-1)>1e-12 or np.linalg.eigvalsh(rho)[0]<-1e-12:
            raise ValueError('Hermitian positive unit-trace finite density required')
        result['finite_density_spin_expectation_first']=np.einsum('ij,bji->b',rho,spin).real
    return result


def verify_application_result(result_directory):
    """Reject stale owners, source, inputs or modified evaluated output arrays."""
    verify_inputs()
    root=Path(result_directory)
    binding=json.loads((root/'BINDING.json').read_text())
    if binding['input_manifest_sha256']!=hashlib.sha256((ROOT/'inputs/PROVENANCE.json').read_bytes()).hexdigest():
        raise ValueError('application input binding changed; review affected result')
    for name,expected in binding['files'].items():
        if hashlib.sha256((root/name).read_bytes()).hexdigest()!=expected:
            raise ValueError('evaluated result changed: '+name)
    return binding
