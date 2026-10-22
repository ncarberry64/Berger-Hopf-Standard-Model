"""Conditional Blackhole Tracker: calibrated primary-pair response experiment.

No observations or selected black-hole hair are used. The experiment compares
the same-action worldtube response against a predeclared nuisance family.
Source positions are free at every epoch; lens-center motion is also fitted.
It evaluates local identifiability, not an instrument/detection forecast.
"""
from pathlib import Path
import importlib
import json
import sys

import numpy as np
import mpmath as mp
from scipy.integrate import quad
from scipy.optimize import brentq, root
from radial_response import ScreenedExterior, C_KM_S

ROOT=Path(__file__).resolve().parents[1]


def distances(exterior,z_s=1.):
    # Same frozen closed R1 background as the archived cosmological paper.
    an=importlib.import_module('action_native_matter_n2')
    bg=importlib.import_module('background')
    sol=an.frozen_background()
    chi=lambda z: quad(lambda zz: 1/float(sol.sol(-np.log1p(zz))[2]),0,z,
                       epsabs=2e-12,epsrel=2e-12)[0]
    sk=lambda x: np.sin(np.sqrt(bg.KCURV)*x)/np.sqrt(bg.KCURV)
    cl,cs=chi(exterior.z_l),chi(z_s)
    L=exterior.L0_pc
    dl,ds,dls=L*sk(cl)/(1+exterior.z_l),L*sk(cs)/(1+z_s),L*sk(cs-cl)/(1+z_s)
    re=np.sqrt(4*exterior.m_pc*dl*dls/ds)
    return {'D_l_pc':dl,'D_s_pc':ds,'D_ls_pc':dls,'rE_pc':re,
            'thetaE_mas':re/dl*206264806.24709636,
            'time_unit_seconds':4*exterior.m_pc*(1+exterior.z_l)*3.085677581491367e13/C_KM_S}


def radial_tensor(x,a,ap,app):
    r=np.linalg.norm(x); e=x/r; ee=np.outer(e,e)
    H=(a/r)*np.eye(2)+(ap-a/r)*ee
    def dH(v):
        vr=float(e@v); vt=v-vr*e
        return ((ap/r-a/r**2)*vr*np.eye(2)+(app-ap/r+a/r**2)*vr*ee
                +(ap-a/r)/r*(np.outer(vt,e)+np.outer(e,vt)))
    return H,dH


def quadrupole(x,q,qp,qpp,sine=False):
    r=np.linalg.norm(x); e=x/r; t=np.array([-e[1],e[0]])
    c=e[0]**2-e[1]**2; s=2*e[0]*e[1]
    if sine: c,s=s,-c
    grad=qp*c*e-2*q*s/r*t
    H=(qpp*c*np.outer(e,e)+(qp/r-4*q/r**2)*c*np.outer(t,t)
       -2*(qp/r-q/r**2)*s*(np.outer(e,t)+np.outer(t,e)))
    return float(q*c),grad,H


class Tracker:
    def __init__(self,mass=1e9,flux=1.,r0=10.,z_s=1.,table_nodes=241):
        self.ext=ScreenedExterior(M_msun=mass,flux_ratio=flux,r0_pc=r0)
        self.geometry=distances(self.ext,z_s)
        self.re=self.geometry['rE_pc'];self.m=self.ext.m_pc
        self.table_report=self.ext.prepare_tables(r0,self.re*12,n=table_nodes)
        self.qref=float(self.ext.projected_quad(self.re)[0])
        self.axialref=float(self.ext.projected_axial(self.re)[0])
        self._mass_exteriors=[]
        self._flux_exteriors=[]
        self.mass_step=2e-4
        for sign in [-1,1]:
            ex=ScreenedExterior(M_msun=mass*np.exp(sign*self.mass_step),flux_ratio=flux,r0_pc=r0)
            ex.prepare_tables(r0,self.re*12,n=table_nodes)
            self._mass_exteriors.append(ex)
        if flux>0:
            for sign in [-1,1]:
                ex=ScreenedExterior(M_msun=mass,flux_ratio=flux*np.exp(sign*self.mass_step),r0_pc=r0)
                ex.prepare_tables(r0,self.re*12,n=table_nodes)
                self._flux_exteriors.append(ex)

    def alpha(self,r):
        vals=self.ext.monopole_deflection(self.re*r)
        factor=self.re/(4*self.m)
        return np.array([1/r,-1/r**2,2/r**3])+factor*np.array(vals)*np.array([1,self.re,self.re**2])

    def psi(self,r):
        return np.log(r)+quad(lambda t:self.alpha(t)[0]-1/t,1,r,epsabs=1e-15)[0]

    def parameter_radial(self,r,kind):
        exteriors=self._mass_exteriors if kind=='mass' else self._flux_exteriors
        if not exteriors:return 0.,0.,0.
        vs=[np.array(ex.monopole_deflection(self.re*r)) for ex in exteriors]
        dalpha=(vs[1]-vs[0])/(2*self.mass_step)*self.re/(4*self.m)*np.array([1,self.re,self.re**2])
        pv=quad(lambda t:(float(exteriors[1].monopole_deflection(self.re*t)[0])
             -float(exteriors[0].monopole_deflection(self.re*t)[0]))
             /(2*self.mass_step)*self.re/(4*self.m),1,r,epsabs=1e-15)[0]
        return np.array([pv,dalpha[0],dalpha[1]])+(np.array([np.log(r),1/r,-1/r**2]) if kind=='mass' else 0.)

    def pair(self,y):
        u=np.linalg.norm(y); e=y/u; rmin=self.ext.r0_pc/self.re*1.000001
        rp=brentq(lambda r:r-self.alpha(r)[0]-u,rmin,10,xtol=1e-14)
        rm=brentq(lambda r:r-self.alpha(r)[0]+u,rmin,10,xtol=1e-14)
        xs=[rp*e,-rm*e]; records=[]
        for x in xs:
            r=np.linalg.norm(x); a,ap,app=self.alpha(r)
            H,dH=radial_tensor(x,a,ap,app); A=np.eye(2)-H
            tau=.5*np.sum((x-y)**2)-self.psi(r)
            records.append(dict(x=x,r=r,A=A,dH=dH,H=H,tau=tau,
                                logmu=-np.log(abs(np.linalg.det(A)))))
        obs=np.r_[xs[0],xs[1],records[0]['logmu']-records[1]['logmu'],records[1]['tau']-records[0]['tau']]
        return records,obs

    def potential(self,x,kind):
        r=np.linalg.norm(x);e=x/r
        if kind in ['mass','scalar_flux']:
            p,qp,qpp=self.parameter_radial(r,kind)
            return p,qp*e,(qp/r)*np.eye(2)+(qpp-qp/r)*np.outer(e,e)
        if kind=='convergence': return .5*r*r,x,np.eye(2)
        if kind=='axial':
            if self.ext.flux_ratio==0:return 0.,np.zeros(2),np.zeros((2,2))
            q,qp,qpp=self.ext.projected_axial(self.re*r)
            q,qp,qpp=np.array([q,qp*self.re,qpp*self.re**2])/self.axialref
            return q,qp*e,(qp/r)*np.eye(2)+(qpp-qp/r)*np.outer(e,e)
        if kind.startswith('center'):
            v=np.eye(2)[int(kind[-1])];a,ap,app=self.alpha(r)
            H,dH=radial_tensor(x,a,ap,app)
            return -a*(e@v),-H@v,-dH(v)
        sine=kind.endswith('x')
        if kind.startswith('envelope'):
            q,qp,qpp=self.ext.projected_quad(r*self.re)
            q,qp,qpp=np.array([q,qp*self.re,qpp*self.re**2])/self.qref
        elif kind.startswith('deep'): q,qp,qpp=1.,0.,0.
        elif kind.startswith('shear'): q,qp,qpp=r*r,2*r,2.
        elif kind.startswith('compact'): q,qp,qpp=r**-2,-2*r**-3,6*r**-4
        else: raise ValueError(kind)
        return quadrupole(x,q,qp,qpp,sine)

    def response(self,pair,kind=None,dy=None):
        dy=np.zeros(2) if dy is None else np.asarray(dy)
        dxs=[];logs=[];taus=[]
        for rec in pair:
            x=rec['x']
            p,g,H=(0.,np.zeros(2),np.zeros((2,2))) if kind is None else self.potential(x,kind)
            dx=np.linalg.solve(rec['A'],g+dy)
            logs.append(np.trace(np.linalg.solve(rec['A'],H+rec['dH'](dx))))
            taus.append(-p-x@dy) # common y.dy drops from the delay
            dxs.append(dx)
        return np.r_[dxs[0],dxs[1],logs[0]-logs[1],taus[1]-taus[0]]

    def finite_pair(self,y,epsilon,kind):
        pair,obs=self.pair(y); xs=[];logs=[];taus=[];res=[]
        for rec in pair:
            def stationary(x):
                r=np.linalg.norm(x);p,g,H=self.potential(x,kind)
                return x-y-self.alpha(r)[0]*x/r-epsilon*g
            solved=root(stationary,rec['x'],tol=1e-11)
            x=solved.x;r=np.linalg.norm(x)
            p,g,Hp=self.potential(x,kind)
            a,ap,app=self.alpha(r);H,dH=radial_tensor(x,a,ap,app)
            A=np.eye(2)-H-epsilon*Hp
            det=np.linalg.det(A)
            if max(abs(stationary(x)))>1e-10 or r*self.re<self.ext.r0_pc:
                raise ValueError('primary branch fails exterior/stationarity admission')
            if np.sign(det)!=np.sign(np.linalg.det(rec['A'])):
                raise ValueError('continued image changed parity')
            xs.append(x);logs.append(-np.log(abs(np.linalg.det(A))))
            taus.append(.5*np.sum((x-y)**2)-self.psi(r)-epsilon*p)
            res.append(np.max(abs(stationary(x))))
        if logs[0]<=logs[1] or taus[1]<=taus[0]:
            raise ValueError('primary image flux/time ordering reversed')
        return np.r_[xs[0],xs[1],logs[0]-logs[1],taus[1]-taus[0]],max(res)


def nuisance_projection(nuisance,signal):
    norms=np.linalg.norm(nuisance,axis=0)
    floor=max(float(np.max(norms)),1.)*1e-11
    keep=norms>floor
    matrix=nuisance[:,keep]/norms[keep]
    U,s,V=np.linalg.svd(matrix,full_matrices=False)
    # Report spectrum; use a specified numerical rank threshold, not a claim
    # that mathematical nulls are determined at arbitrary finite precision.
    rank=int(np.sum(s>s[0]*1e-9)) if len(s) else 0
    residual=signal-U[:,:rank]@(U[:,:rank].T@signal)
    refinement='double SVD'
    if rank==matrix.shape[1] and s[-1]<s[0]*1e-6:
        # The axial mode is nearly masslike. Avoid subtracting a double
        # precision least-squares solution with large cancelling coefficients.
        # Rank selection stays exactly the stated SVD rule. These are the
        # same double-input columns, projected with 70-digit arithmetic.
        with mp.workdps(70):
            nm=mp.matrix(matrix.tolist());sm=mp.matrix(signal.tolist())
            gram=nm.T*nm;rhs=nm.T*sm
            fitted=[]
            for j in range(sm.cols):
                sol=mp.lu_solve(gram,rhs[:,j])
                fitted.append(nm*sol)
            residual=np.array([[float(sm[i,j]-fitted[j][i]) for j in range(sm.cols)] for i in range(sm.rows)])
        refinement='70-digit normal equations after unchanged SVD rank selection'
    ss=np.linalg.svd(residual,compute_uv=False)
    full=np.column_stack([matrix,signal/np.linalg.norm(signal,axis=0)])
    sf=np.linalg.svd(full,compute_uv=False)
    return {'nuisance_rank':rank,'nuisance_columns':nuisance.shape[1],
        'absolute_column_norm_floor':floor,'columns_above_floor':int(sum(keep)),
        'projection_arithmetic':refinement,
        'nuisance_singular_values':s.tolist(),'projected_signal_singular_values':ss.tolist(),
        'signal_column_norms':np.linalg.norm(signal,axis=0).tolist(),
        'retained_signal_norm_fractions':(np.linalg.norm(residual,axis=0)/np.linalg.norm(signal,axis=0)).tolist(),
        'full_column_normalized_singular_values':sf.tolist(),
        'common_dimensionless_precision_for_unit_amplitude_sigma':ss[-1] if len(ss) else 0.},residual


def design(tracker,n=9,free_center_each_epoch=False,span=1.8,offset=.6,origin=0.):
    times=np.linspace(-1,1,n)
    ys=np.column_stack([origin+span*times,np.full(n,offset)])
    pairs=[];observables=[]
    for y in ys:
        p,o=tracker.pair(y);pairs.append(p);observables.append(o)
    obs=np.array(observables)
    columns={}
    for kind in ['mass','scalar_flux','axial','convergence','center0','center1','shear+','shearx','compact+','compactx','envelope+','envelopex','deep+','deepx']:
        columns[kind]=np.concatenate([tracker.response(p,kind) for p in pairs])
    columns['velocity0']=np.concatenate([t*tracker.response(p,'center0') for t,p in zip(times,pairs)])
    columns['velocity1']=np.concatenate([t*tracker.response(p,'center1') for t,p in zip(times,pairs)])
    for i,p in enumerate(pairs):
        for j in range(2):
            c=np.zeros((n,6));c[i]=tracker.response(p,dy=np.eye(2)[j]);columns[f'source{i}_{j}']=c.ravel()
            if free_center_each_epoch:
                c=np.zeros((n,6));c[i]=tracker.response(p,f'center{j}');columns[f'freecenter{i}_{j}']=c.ravel()
    nuisance_names=[k for k in columns if not k.startswith(('envelope','deep'))]
    nuisance=np.column_stack([columns[k] for k in nuisance_names])
    signal=np.column_stack([columns['envelope+'],columns['envelopex']])
    deep=np.column_stack([columns['deep+'],columns['deepx']])
    full,res=nuisance_projection(nuisance,signal)
    deep_report,_=nuisance_projection(nuisance,deep)
    # The apparent-mass statistic is deliberately assessed separately. Its
    # baseline contains the small screened monopole; report that distinction.
    projector=np.zeros((n,n*6))
    for i,o in enumerate(obs):
        u=2*np.sinh(o[4]/4);s=np.sqrt(u*u+4)
        h=.5*u*s+2*np.arcsinh(u/2)
        projector[i,i*6+4]=-s*s/(4*h);projector[i,i*6+5]=1/o[5]
    massonly,_=nuisance_projection(projector@nuisance,projector@signal)
    astrometry,_=nuisance_projection(nuisance.reshape(n,6,-1)[:,:4].reshape(n*4,-1),signal.reshape(n,6,2)[:,:4].reshape(n*4,2))
    return {'epochs':n,'sources':ys.tolist(),'dimensionless_times':times.tolist(),
            'source_position_policy':'independent free 2-vector at each epoch',
            'center_policy':'free each epoch' if free_center_each_epoch else 'unknown constant center and constant velocity',
            'observables_per_epoch':['x_plus','y_plus','x_minus','y_minus','ln_abs_flux_ratio','delay_over_time_unit'],
            'normalization':'Euclidean in thetaE, lnR and tM; illustrative equal dimensionless errors',
            'nuisance_names':nuisance_names,'full_pair':full,'deep_limit_full_pair':deep_report,
            'mass_statistic_only':massonly,'astrometry_only':astrometry,
            'baseline_observables':obs.tolist()},res,signal,columns


def main():
    tracker=Tracker()
    experiment,res,signal,columns=design(tracker)
    r0=tracker.ext.r0_pc;x0=tracker.ext.x0
    eta=1e-3
    boundary_a=eta*x0*abs(float(tracker.ext.p(x0)))/6
    eps=boundary_a*tracker.qref/(4*tracker.m)
    chosen_y=np.array([.9,.6]);pair,obs=tracker.pair(chosen_y)
    response=tracker.response(pair,'envelope+')
    phys=response*eps
    fd=[]
    for step in [1e-3,3e-4,1e-4,3e-5]:
        plus,rp=tracker.finite_pair(chosen_y,step,'envelope+')
        minus,rm=tracker.finite_pair(chosen_y,-step,'envelope+')
        measured=(plus-minus)/(2*step)
        fd.append({'epsilon':step,'max_stationary_residual':max(rp,rm),
                   'max_abs_derivative_error':float(np.max(abs(measured-response)))})
    scales=[]
    for ratio in [.001,.01,.1,1,10]:
        b=tracker.ext.rV_pc*ratio
        if b<r0: continue
        q,qp,qpp=tracker.ext.projected_quad(b)
        scales.append({'b_over_rV':ratio,'q_pc':float(q),'dln_abs_q_dln_b':float(b*qp/q),
                       'b2_qsecond_over_q':float(b*b*qpp/q)})
    # Size of motion over a 10 yr observer interval, a hypothetical transverse
    # speed only; not an actual inferred object/forecast.
    v=300.;years=10.;pc_per_yr_kms=31557600/3.085677581491367e13
    shift_pc=v*years*pc_per_yr_kms/(1+tracker.ext.z_l)
    sigma_eps=abs(eps)*experiment['full_pair']['projected_signal_singular_values'][-1]
    sweep=[]
    for mass,flux,r0s in [(1e9,0.,10.),(1e9,.1,10.),(1e9,3.,10.),
                          (1e6,1.,.1),(1e11,1.,100.)]:
        other=Tracker(mass=mass,flux=flux,r0=r0s,table_nodes=161)
        expt,*_=design(other)
        aa=eta*other.ext.x0*abs(float(other.ext.p(other.ext.x0)))/6
        ee=aa*other.qref/(4*other.m)
        sweep.append({'M_msun':mass,'flux_ratio':flux,'r0_pc':r0s,'rE_over_rV':
                 other.re/other.ext.rV_pc if flux else None,
                 'dimensionless_lens_amplitude':ee,
                 'projected_singular_values':expt['full_pair']['projected_signal_singular_values'],
                 'retained_norm_fractions':expt['full_pair']['retained_signal_norm_fractions']})
    short,*_=design(tracker,span=shift_pc/tracker.re/2,origin=.9)
    result={'status':'CONDITIONAL_COMPACT_SOURCE_TRACKER_RESPONSE_NO_DETECTION',
       'exterior':tracker.ext.summary(),'geometry':tracker.geometry,'tables':tracker.table_report,
       'physical_state':{'eta':eta,'boundary_amplitude':boundary_a,'dimensionless_lens_amplitude':eps,
          'normalization':'a=eta*x0*abs(p0)/6; epsilon=a*q(rE)/(4m)',
          'chosen_source':chosen_y.tolist(),'linear_shift':phys.tolist(),
          'max_position_shift_nanoarcsec':float(max(abs(phys[:4]))*tracker.geometry['thetaE_mas']*1e6),
          'delay_shift_seconds':float(phys[5]*tracker.geometry['time_unit_seconds']),
          'log_flux_ratio_shift':float(phys[4]),
          'illustrative_equal_dimensionless_sigma_for_marginalized_unit_snr_worst_orientation':sigma_eps},
       'experiment':experiment,'free_center_each_epoch_control':design(tracker,free_center_each_epoch=True)[0],
       'finite_difference_checks':fd,'radial_scales':scales,
       'physical_input_sweep':sweep,'ten_year_conditioning_control':short,
       'motion_example':{'speed_km_s':v,'observer_years':years,'lens_shift_pc':shift_pc,
          'lens_shift_over_rE':shift_pc/tracker.re,
          'years_for_full_synthetic_scan_at_same_speed':years*3.6*tracker.re/shift_pc,
          'warning':'large scan is an abstract information experiment, not an observing campaign'},
       'matching_tail_at_1Mpc':tracker.ext.matching_tail_bounds(tracker.re,1e6),
       'not_derived':['BH horizon scalar flux','physical deformation state','microscopic BHSM to R1 map','observational detection']}
    (ROOT/'results').mkdir(exist_ok=True)
    (ROOT/'results/tracker_response.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    np.savez(ROOT/'results/design_arrays.npz',projected_signal=res,signal=signal,
             times=experiment['dimensionless_times'],**columns)
    assert fd[-1]['max_abs_derivative_error']<2e-7
    assert experiment['full_pair']['projected_signal_singular_values'][-1]>1e-4
    print(json.dumps({'geometry':tracker.geometry,'physical_state':result['physical_state'],
                      'full_pair':experiment['full_pair'],'finite_difference_checks':fd},indent=2))


if __name__=='__main__':main()
