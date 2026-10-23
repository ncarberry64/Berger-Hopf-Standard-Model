"""Full-covariance nonlinear primary-pair inference with honest local errors."""
import platform
import copy
import json
import time
import numpy as np
import scipy
from scipy.optimize import least_squares
from scipy.stats import chi2 as chi2_distribution
from .data import load_dataset
from .forward import LensEngine,GM_SUN,C

def initial_parameters(data):
    """Inherited point-lens identities supply an initial state, not a prior."""
    o=data.observations;g=data.geometry
    logR=np.maximum(o[:,4],.01)
    u=2*np.sinh(logR/4);s=np.sqrt(u*u+4)
    h=.5*u*s+2*np.arcsinh(u/2)
    masses=np.maximum(o[:,5],1e-12)*C**3/(4*GM_SUN*(1+g['z_l'])*h)
    mass=float(np.median(masses))
    q2=np.exp(np.clip(logR/2,-20,20))
    centers=(o[:,:2]+q2[:,None]*o[:,2:4])/(1+q2[:,None])
    parallax=np.asarray(data.analysis.get('lens_parallax_factors',np.zeros((data.n,2))))*(1000/g['D_l_pc'])
    centers-=parallax
    dt=data.epochs-data.t0
    X=np.column_stack([np.ones(data.n),dt])
    fit=np.linalg.lstsq(X,centers,rcond=1e-12)[0]
    # Invert either primary using the independently fixed distance convention.
    theta2=4*GM_SUN*mass/(C*C*3.085677581491367e16)*g['D_ls_pc']/(g['D_l_pc']*g['D_s_pc'])*206264806.24709636**2
    cfit=X@fit+parallax;delta=o[:,:2]-cfit
    sources=o[:,:2]-theta2*delta/np.maximum(np.sum(delta*delta,axis=1)[:,None],1e-30)
    return {'mass_msun':mass,'center_mas':fit[0].tolist(),
            'proper_motion_mas_yr':fit[1].tolist(),'source_mas':sources.tolist(),
            'shear':[0.,0.],'compact_quad':[0.,0.],'convergence':0.,
            'flux_ratio':float(data.analysis.get('flux_ratio',1.))}

class ParameterMap:
    def __init__(self,engine,nuisance):
        if nuisance not in ['none','shear','full']:raise ValueError('nuisance must be none, shear or full')
        self.e=engine;self.nuisance=nuisance
        self.names=['log_mass','center_x','center_y','motion_x','motion_y']
        mb=engine.data.analysis.get('mass_bounds_msun',[1e-3,1e12])
        self.lower=[np.log(mb[0]/engine.ref_mass),-20.,-20.,-10.,-10.]
        self.upper=[np.log(mb[1]/engine.ref_mass),20.,20.,10.,10.]
        # Explicit conservative square inside the declared slow-motion disk.
        # This is a modeling-domain bound, never an observational precision.
        speed_cap=float(engine.data.analysis.get('quasistatic_speed_ratio_cap',.01))
        if engine.family=='r1':
            from .physics_admission import _sound_speed_lower_squared
            speed_cap*=np.sqrt(_sound_speed_lower_squared(engine._r1.ref.D/engine._r1.ref.C))
        mu_cap=speed_cap*C*31557600/(engine.data.geometry['D_l_pc']*3.085677581491367e16*(1+engine.data.geometry['z_l']))*206264806.24709636/np.sqrt(2)
        motion_bound=mu_cap*engine.tscale/engine.theta
        self.lower[3:5]=[-motion_bound,-motion_bound];self.upper[3:5]=[motion_bound,motion_bound]
        if nuisance in ['shear','full']:
            self.names+=['shear_plus','shear_cross'];self.lower +=[-.08,-.08];self.upper +=[.08,.08]
        if nuisance=='full':
            self.names+=['compact_plus','compact_cross','convergence']
            self.lower +=[-.01,-.01,-.15];self.upper +=[.01,.01,.15]
        self.fit_flux=engine.family=='r1' and engine.data.analysis.get('flux_provenance')!='regular_body_proxy'
        if self.fit_flux:
            self.names+=['log_flux'];self.lower +=[np.log(.05)];self.upper +=[np.log(20.)]
        self.nglobal=len(self.names)
        for i in range(engine.data.n):
            self.names +=[f'source_{i}_x',f'source_{i}_y'];self.lower +=[-30.,-30.];self.upper +=[30.,30.]
        self.lower=np.array(self.lower);self.upper=np.array(self.upper)

    def encode(self,p):
        e=self.e
        vals=[np.log(p['mass_msun']/e.ref_mass),*((np.array(p['center_mas'])-e.origin)/e.theta),
              *(np.array(p['proper_motion_mas_yr'])*e.tscale/e.theta)]
        if self.nuisance in ['shear','full']:vals+=list(p.get('shear',[0.,0.]))
        if self.nuisance=='full':vals+=list(p.get('compact_quad',[0.,0.]))+[p.get('convergence',0.)]
        if self.fit_flux:vals+=[np.log(max(p.get('flux_ratio',1.),.05))]
        vals+=list(((np.array(p['source_mas'])-e.origin)/e.theta).ravel())
        return np.clip(vals,self.lower+1e-7,self.upper-1e-7)

    def decode(self,x):
        e=self.e;j=5
        p={'mass_msun':float(e.ref_mass*np.exp(x[0])),
           'center_mas':(e.origin+e.theta*x[1:3]).tolist(),
           'proper_motion_mas_yr':(e.theta*x[3:5]/e.tscale).tolist(),
           'shear':[0.,0.],'compact_quad':[0.,0.],'convergence':0.,'flux_ratio':float(e.data.analysis.get('flux_ratio',1.))}
        if self.nuisance in ['shear','full']:p['shear']=x[j:j+2].tolist();j+=2
        if self.nuisance=='full':p['compact_quad']=x[j:j+2].tolist();p['convergence']=float(x[j+2]);j+=3
        if self.fit_flux:p['flux_ratio']=float(np.exp(x[j]));j+=1
        p['source_mas']=(e.origin+x[j:].reshape(-1,2)*e.theta).tolist()
        return p

def _local_covariance(J,relative_cut=1e-9):
    U,s,Vt=np.linalg.svd(J,full_matrices=True)
    rank=int(np.sum(s>s[0]*relative_cut)) if len(s) and s[0]>0 else 0
    V=Vt.T
    cov=(V[:,:rank]/s[:rank]**2)@V[:,:rank].T
    null=V[:,rank:]
    return cov,null,s,rank

def fit(dataset,family='gr',starts=2,nuisance='shear',initial=None,max_nfev=160):
    beginning=time.perf_counter();d=load_dataset(dataset)
    if isinstance(starts,bool) or not isinstance(starts,int) or not 1<=starts<=8:raise ValueError('starts must be an integer from 1 to 8')
    if isinstance(max_nfev,bool) or not isinstance(max_nfev,int) or not 1<=max_nfev<=2000:
        raise ValueError('max_nfev must be an integer from 1 to 2000')
    seed_parameters=initial or initial_parameters(d)
    reference_mass=d.analysis.get('reference_mass_msun',seed_parameters['mass_msun'])
    e=LensEngine(d,family,reference_mass=reference_mass)
    mapping=ParameterMap(e,nuisance)
    guess=mapping.encode(seed_parameters)
    physics=None
    if family=='r1':
        from .physics_admission import assess_physics
        initial_physics=assess_physics(e.physics_config,mapping.decode(guess))
        if not initial_physics['eligible_physics_models']['r1_spherical_conditional']:
            raise ValueError('conditional R1 family is not admitted: supply valid flux provenance and physical domain')
    def residual(x):
        try:pred,_=e.calculate(mapping.decode(x),admit=False);return d.whiten((pred-d.observations).ravel())
        except (ValueError,FloatingPointError,np.linalg.LinAlgError):return np.full(6*d.n,1e8)
    solutions=[];rng=np.random.default_rng(49312)
    for k in range(starts):
        x=guess.copy()
        if k:
            x[:5]+=rng.normal(size=5)*np.array([.03,.015,.015,.008,.008])
            if nuisance in ['shear','full']:x[5:7]+=rng.normal(size=2)*.002
        x=np.clip(x,mapping.lower+1e-7,mapping.upper-1e-7)
        solved=least_squares(residual,x,bounds=(mapping.lower,mapping.upper),jac='3-point',
                 x_scale='jac',ftol=1e-10,xtol=1e-10,gtol=1e-8,max_nfev=max_nfev)
        solutions.append(solved)
    solved=min(solutions,key=lambda item:np.sum(item.fun**2))
    pars=mapping.decode(solved.x)
    pars['reference_mass_msun']=e.ref_mass
    pred,branch=e.calculate(pars,admit=False)
    white=d.whiten((pred-d.observations).ravel());chi=float(white@white)
    cov,null,s,rank=_local_covariance(solved.jac)
    sig=np.sqrt(np.maximum(np.diag(cov),0.))
    unidentified=np.linalg.norm(null,axis=1)>1e-4 if null.size else np.zeros(len(sig),dtype=bool)
    dof=6*d.n-rank;pvalue=float(chi2_distribution.sf(chi,dof)) if dof>0 else None
    errors=[None if unidentified[i] else float(sig[i]) for i in range(len(sig))]
    def scaled_error(i,factor):return None if errors[i] is None else errors[i]*factor
    unc={'mass_msun':scaled_error(0,pars['mass_msun']),
         'center_mas':[scaled_error(i,e.theta) for i in [1,2]],
         'proper_motion_mas_yr':[scaled_error(i,e.theta/e.tscale) for i in [3,4]],
         'method':'local Gaussian, known supplied covariance; no chi2 rescaling; null directions return null'}
    low=pars['mass_msun']*np.exp(-sig[0]) if errors[0] is not None and sig[0]<20 else None
    high=pars['mass_msun']*np.exp(sig[0]) if errors[0] is not None and sig[0]<20 else None
    unc['mass_68pct_interval_msun']=[low,high]
    motion_snr=None
    if not any(unidentified[3:5]):
        cm=cov[3:5,3:5];motion_snr=float(np.sqrt(max(solved.x[3:5]@np.linalg.pinv(cm)@solved.x[3:5],0.)))
    success=bool(solved.success and chi<1e14)
    if not success or pvalue is not None and pvalue<.001:status='FIT_REJECTED'
    elif errors[0] is None or sig[0]>.5:status='INSUFFICIENT_INFORMATION'
    elif motion_snr is None or motion_snr<5:status='PARTIALLY_IDENTIFIED'
    else:status='TRACKED'
    diagnostics=[]
    def note(level,code,message):diagnostics.append({'level':level,'code':code,'message':message})
    note('info','COMPACT_EXTERIOR_ONLY','The fit tracks a compact-lens exterior. It does not establish a black-hole horizon.')
    if d.raw['provenance']['kind']=='synthetic':note('info','SYNTHETIC_DATA','Recovery uses declared synthetic measurements, not an empirical detection.')
    if status=='FIT_REJECTED':note('error','FIT_REJECTED','Convergence or the predeclared p < 0.001 goodness-of-fit criterion failed; do not interpret fitted parameters as a valid track.')
    if motion_snr is None or motion_snr<5:note('warning','MOTION_UNRESOLVED','Motion does not satisfy the declared five-sigma two-component tracking criterion.')
    if rank<len(mapping.names):note('warning','PARAMETER_NULLS','Some parameter combinations are not identified by these data; null errors are not zero uncertainty.')
    bound=np.minimum(solved.x-mapping.lower,mapping.upper-solved.x)
    if np.any(bound[:mapping.nglobal]<1e-5):
        note('warning','BOUND_ACTIVE','A lens parameter is at a declared modeling bound; local errors are conditional and a profile is required.')
        if status=='TRACKED':status='PARTIALLY_IDENTIFIED'
    full_error=np.array([np.nan if err is None else err for err in errors])
    motion_cov=(cov[3:5,3:5]*(e.theta/e.tscale)**2).tolist()
    track=[];track_sigma=[]
    for i,t in enumerate(e.tau):
        track.append((e.origin+e.theta*(solved.x[1:3]+t*solved.x[3:5])+e.parallax[i]).tolist())
        jac=np.zeros((2,len(sig)));jac[0,1]=jac[1,2]=e.theta;jac[0,3]=jac[1,4]=e.theta*t
        cc=jac@cov@jac.T
        bad=np.any(abs(jac@null)>1e-4) if null.size else False
        track_sigma.append([None,None] if bad else np.sqrt(np.maximum(np.diag(cc),0)).tolist())
    from .physics_admission import assess_physics
    physics=assess_physics(e.physics_config,pars,branch['impact_pc'])
    if not physics['allowed_physics_models']['baseline_point_mass']:
        note('error','PHYSICAL_DOMAIN','The fitted track fails the declared weak-field or quasistatic domain. Results are outside the admitted physical model.')
        status='FIT_REJECTED'
    if family=='r1':
        message=('The scalar flux is a fitted conditional matching nuisance; it is not a selected black-hole charge.' if mapping.fit_flux else
                 'The scalar flux is fixed to the declared regular-body proxy. It is not a black-hole horizon selection.')
        note('info','CONDITIONAL_FLUX',message)
        if not physics['allowed_physics_models']['r1_spherical_conditional']:
            note('error','R1_DOMAIN','The fitted state is outside the declared conditional R1 exterior domain.')
            status='FIT_REJECTED'
    from .provenance import VERSION,software_provenance
    result={'schema_version':1,'product_version':VERSION,'status':status,'model':{'family':family,'nuisance':nuisance,
            'source_policy':'free_per_epoch','distance_and_frame':'supplied and fixed','fitted_parameters':mapping.names,
            'reference_mass_msun':e.ref_mass,'theta_reference_mas':e.theta,'time_reference_seconds':e.time,
            'r0_pc':e.r0,'worldtube_policy':'supplied' if 'r0_pc' in d.analysis else '0.001 times the computational reference Einstein radius; supply r0_pc for a fixed physical worldtube',
            'flux_policy':'fitted_conditional_flux' if mapping.fit_flux else 'fixed_regular_body_proxy' if family=='r1' else 'not_used',
            'bounds_internal':{'lower':mapping.lower.tolist(),'upper':mapping.upper.tolist()}},
            'estimates':{k:pars[k] for k in ['mass_msun','center_mas','proper_motion_mas_yr','shear','compact_quad','convergence','flux_ratio']},
            'uncertainty':unc,'motion_snr':motion_snr,'proper_motion_covariance':motion_cov,
            'chi2':chi,'dof':dof,'goodness_of_fit_p':pvalue,'optimizer_converged':success,
            'diagnostics':diagnostics,'rank':rank,'singular_values':s.tolist(),'branch_admission':branch,
            'source_mas':pars['source_mas'],'reference_epoch_yr':d.t0,'epochs_yr':d.epochs.tolist(),
            'center_track_mas':track,'center_track_sigma_mas':track_sigma,
            'observations':d.observations.tolist(),'predictions':pred.tolist(),'whitened_residuals':white.tolist(),
            'covariance':d.covariance.tolist(),'data_summary':d.summary(),'geometry':d.geometry,'physics_admission':physics,
            'dataset_input':copy.deepcopy(d.raw),
            'analysis_configuration':{'family':family,'nuisance':nuisance,'starts':starts,
                'max_nfev':max_nfev,'initial':None if initial is None else json.loads(json.dumps(initial,default=lambda v:v.tolist()))},
            'software_provenance':copy.deepcopy(software_provenance()),
            'multistart_chi2':[float(sol.fun@sol.fun) for sol in solutions],
            'runtime_seconds':time.perf_counter()-beginning,
            'runtime':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__},
            'conditional_envelope':{'status':'NOT_REQUESTED'},
            '_internal':{'parameters':pars,'x':solved.x.tolist(),'covariance':cov.tolist(),
                         'jacobian':solved.jac.tolist(),'unidentified':unidentified.tolist()}}
    if family=='r1' and status=='FIT_REJECTED':
        result['conditional_envelope']={'status':'NOT_EVALUATED','reasons':['Baseline fit rejected; conditional information must not be interpreted on an unacceptable fit.']}
    elif family=='r1':
        from .envelope import assess_envelope
        result['conditional_envelope']=assess_envelope(d,e,pars,solved.jac,pred,physics)
    from .interpretation import bhsm_interpretation
    result['bhsm_interpretation']=bhsm_interpretation(family,result['estimates'],unc,result['model'],status)
    return result

def profile(dataset,result,parameter='mass_msun',points=17):
    """Reoptimized one-parameter likelihood curve within declared bounds.

    Delta-chi2=1/3.841 are reference levels, not a boundary-corrected coverage
    theorem. Returned crossings expose intervals truncated by domain bounds.
    """
    d=load_dataset(dataset);model=result['model']
    if d.sha256!=result['data_summary']['sha256']:
        raise ValueError('profile dataset differs from the fitted input; use dataset.json from this analysis export')
    e=LensEngine(d,model['family'],reference_mass=model['reference_mass_msun'])
    mapping=ParameterMap(e,model['nuisance']);x0=np.asarray(result['_internal']['x'])
    indices={'mass_msun':0,'motion_x':3,'motion_y':4}
    if parameter not in indices:raise ValueError('profile parameter must be mass_msun, motion_x or motion_y')
    if not 7<=points<=81:raise ValueError('profile points must be 7 to 81')
    index=indices[parameter];cov=np.asarray(result['_internal']['covariance'])
    width=max(3*np.sqrt(max(cov[index,index],0)),.001)
    grid=np.linspace(max(mapping.lower[index],x0[index]-width),min(mapping.upper[index],x0[index]+width),points)
    grid=np.unique(np.r_[grid,x0[index]])
    mask=np.arange(len(x0))!=index;rows=[]
    for value in grid:
        def residual(free):
            x=x0.copy();x[index]=value;x[mask]=free
            try:pred,_=e.calculate(mapping.decode(x),admit=False);return d.whiten((pred-d.observations).ravel())
            except ValueError:return np.full(6*d.n,1e8)
        solved=least_squares(residual,x0[mask],bounds=(mapping.lower[mask],mapping.upper[mask]),
                   jac='3-point',x_scale='jac',max_nfev=100,ftol=1e-9,xtol=1e-9,gtol=1e-7)
        physical=e.ref_mass*np.exp(value) if index==0 else value*e.theta/e.tscale
        rows.append({'value':float(physical),'chi2':float(solved.fun@solved.fun),'converged':bool(solved.success)})
    minimum=min(r['chi2'] for r in rows)
    for row in rows:row['delta_chi2']=row['chi2']-minimum
    return {'parameter':parameter,'points':rows,'reference_levels':[1.,3.841458820694124],
            'interpretation':'Reoptimized likelihood. Endpoints at bounds are truncated; reference levels need separate calibration for nonregular/boundary cases.'}
