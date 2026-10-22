"""Full-covariance nonlinear primary-pair inference with honest local errors."""
import platform
import copy
import json
import time
import numpy as np
import scipy
from scipy.optimize import least_squares, minimize
from scipy.stats import chi2 as chi2_distribution
from .data import load_dataset
from .forward import LensEngine,GM_SUN,C

_FIT_OBJECTIVE_RTOL=1e-10


def _projected_stationarity(solution):
    """Unit-normalized first-order KKT residual, not a parameter-size prior."""
    jac=np.asarray(solution.jac);residual=np.asarray(solution.fun)
    active=np.asarray(solution.active_mask)
    if (jac.ndim!=2 or not jac.shape[1] or residual.ndim!=1 or active.shape!=(jac.shape[1],)
            or jac.shape[0]!=residual.size or not residual.size
            or not all(np.all(np.isfinite(value)) for value in
                       (jac,residual,active,np.asarray(getattr(solution,'x',[]))))):
        return float('inf')
    # Outward descent at a bound satisfies the one-sided KKT condition.
    with np.errstate(over='ignore',invalid='ignore',divide='ignore'):
        gradient=jac.T@residual
        if not np.all(np.isfinite(gradient)):return float('inf')
        gradient=np.where(((active<0)&(gradient>=0))|((active>0)&(gradient<=0)),0.,gradient)
        norms=np.linalg.norm(jac,axis=0)
        normalized=gradient/np.maximum(norms,1e-300)
        score=float(np.linalg.norm(normalized,ord=np.inf))
    return score if np.isfinite(score) and np.all(np.isfinite(norms)) else float('inf')


def _select_multistart(solutions):
    """Resolve objective ties at the already requested solver precision.

    Material objective improvements retain precedence. Inside the declared
    ftol band, prefer a converged state with the smaller first-order residual.
    Column normalization removes dependence on parameter units; the canonical
    data-derived optimization basis is independent of engine reference choices.
    Stable seed order resolves an exact remaining tie.
    """
    with np.errstate(over='ignore',invalid='ignore'):
        costs=[float(item.fun@item.fun) for item in solutions]
    finite_costs=[value for value in costs if np.isfinite(value)]
    if not finite_costs:raise ValueError('No multistart candidate has a finite objective.')
    minimum=min(finite_costs);width=_FIT_OBJECTIVE_RTOL*max(1.,abs(minimum))
    scores=[_projected_stationarity(item) for item in solutions]
    near=[i for i,value in enumerate(costs) if np.isfinite(value) and
          np.isfinite(scores[i]) and value<=minimum+width]
    if not near:
        raise ValueError('The minimum-objective multistart candidate is numerically invalid; no valid tied solution establishes the fit.')
    converged=[i for i in near if solutions[i].success]
    eligible=converged or near
    index=min(eligible,key=lambda i:(scores[i],i))
    return solutions[index],{'rule':'objective_ftol_tie_then_column_normalized_projected_KKT_gradient',
        'relative_objective_tolerance':_FIT_OBJECTIVE_RTOL,'absolute_objective_tie_width':width,
        'minimum_candidate_chi2':minimum,'selected_candidate_chi2':costs[index],
        'selected_start':index,'eligible_starts':eligible,
        'candidate_chi2':[value if np.isfinite(value) else None for value in costs],
        'candidate_stationarity':[value if np.isfinite(value) else None for value in scores],
        'numerically_invalid_starts':[i for i,value in enumerate(scores) if not np.isfinite(value) or not np.isfinite(costs[i])],
        'stationarity_units':'whitened residual; column-normalized and projected at active bounds',
        'qualification':'Numerical tie resolution within existing objective stopping precision; no statistical threshold or physical prior.'}

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
    # Solve at an epoch near the observations, independently of the reporting
    # epoch. A distant user epoch must not make this linear seed ill-conditioned.
    epoch=float(np.mean(data.epochs));dt=data.epochs-epoch
    X=np.column_stack([np.ones(data.n),dt])
    fit=np.linalg.lstsq(X,centers,rcond=1e-12)[0]
    # Invert either primary using the independently fixed distance convention.
    theta2=4*GM_SUN*mass/(C*C*3.085677581491367e16)*g['D_ls_pc']/(g['D_l_pc']*g['D_s_pc'])*206264806.24709636**2
    cfit=X@fit+parallax;delta=o[:,:2]-cfit
    sources=o[:,:2]-theta2*delta/np.maximum(np.sum(delta*delta,axis=1)[:,None],1e-30)
    return {'mass_msun':mass,'center_mas':(fit[0]+(data.t0-epoch)*fit[1]).tolist(),
            'proper_motion_mas_yr':fit[1].tolist(),'source_mas':sources.tolist(),
            'shear':[0.,0.],'compact_quad':[0.,0.],'convergence':0.,
            'flux_ratio':float(data.analysis.get('flux_ratio',1.))}

class ParameterMap:
    def __init__(self,engine,nuisance):
        if nuisance not in ['none','shear','full']:raise ValueError('nuisance must be none, shear or full')
        self.e=engine;self.nuisance=nuisance
        self.epoch=float(np.mean(engine.data.epochs))
        # These scales precondition the numerical solve only. They are derived
        # from the unchanged observations, never from the computational Einstein
        # radius. No implicit positional prior is imposed.
        self.scale=max(float(np.median(np.linalg.norm(engine.data.observations[:,:2]-engine.data.observations[:,2:4],axis=1)))/2,1e-12)
        self.mass_scale=initial_parameters(engine.data)['mass_msun']
        self.compact_mass_scale=float(engine.data.analysis.get('compact_quad_reference_mass_msun',self.mass_scale))
        self.compact_factor=(self.compact_mass_scale/engine.ref_mass)**2
        self.names=['log_mass','center_x','center_y','motion_x','motion_y']
        mb=engine.data.analysis.get('mass_bounds_msun',[1e-3,1e12])
        self.lower=[np.log(mb[0]/self.mass_scale),-np.inf,-np.inf,-10.,-10.]
        self.upper=[np.log(mb[1]/self.mass_scale),np.inf,np.inf,10.,10.]
        # Explicit conservative square inside the declared slow-motion disk.
        # This is a modeling-domain bound, never an observational precision.
        speed_cap=float(engine.data.analysis.get('quasistatic_speed_ratio_cap',.01))
        if engine.family=='r1':
            from .physics_admission import _sound_speed_lower_squared
            speed_cap*=np.sqrt(_sound_speed_lower_squared(engine._r1.ref.D/engine._r1.ref.C))
        mu_cap=speed_cap*C*31557600/(engine.data.geometry['D_l_pc']*3.085677581491367e16*(1+engine.data.geometry['z_l']))*206264806.24709636/np.sqrt(2)
        motion_bound=mu_cap*engine.tscale/self.scale
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
            self.names +=[f'source_{i}_x',f'source_{i}_y'];self.lower +=[-np.inf,-np.inf];self.upper +=[np.inf,np.inf]
        self.lower=np.array(self.lower);self.upper=np.array(self.upper)

    def metadata(self):
        return {'schema':'bhtracker.resolved_parameter_basis.v2','optimization_epoch_yr':self.epoch,
                'reporting_epoch_yr':self.e.data.t0,'angular_scale_mas':self.scale,
                'time_scale_yr':self.e.tscale,'mass_scale_msun':self.mass_scale,
                'origin_mas':self.e.origin.tolist(),
                'compact_quad_convention':'public coefficients retain the computational reference Einstein-radius convention; internal coefficients/bounds use the separately fixed physical compact basis',
                'compact_quad_reference_mass_msun':self.compact_mass_scale,
                'compact_quad_internal_to_public_factor':self.compact_factor,
                'compact_quad_physical_bound_rule':'internal plus/cross each in [-0.01,0.01]; physical angular coefficients are public compact_quad * theta_reference_mas**4',
                'unbounded_positions':'center and free sources have no numerical positional prior'}

    def reporting_jacobian(self,x):
        """Full differential from internal coordinates to physical reporting basis."""
        J=np.eye(len(x));J[0,0]=self.mass_scale*np.exp(x[0])
        J[1:5,1:5]=0
        for j in range(2):
            J[1+j,1+j]=self.scale
            J[1+j,3+j]=self.scale*(self.e.data.t0-self.epoch)/self.e.tscale
            J[3+j,3+j]=self.scale/self.e.tscale
        if self.nuisance=='full':J[7,7]=J[8,8]=self.compact_factor
        if self.fit_flux:J[self.nglobal-1,self.nglobal-1]=np.exp(x[self.nglobal-1])
        J[self.nglobal:,self.nglobal:]*=self.scale
        return J

    def encode(self,p):
        e=self.e
        center=np.array(p['center_mas'])+(self.epoch-e.data.t0)*np.array(p['proper_motion_mas_yr'])
        vals=[np.log(p['mass_msun']/self.mass_scale),*((center-e.origin)/self.scale),
              *(np.array(p['proper_motion_mas_yr'])*e.tscale/self.scale)]
        if self.nuisance in ['shear','full']:vals+=list(p.get('shear',[0.,0.]))
        if self.nuisance=='full':vals+=list(np.asarray(p.get('compact_quad',[0.,0.]))/self.compact_factor)+[p.get('convergence',0.)]
        if self.fit_flux:vals+=[np.log(max(p.get('flux_ratio',1.),.05))]
        vals+=list(((np.array(p['source_mas'])-e.origin)/self.scale).ravel())
        return np.clip(vals,self.lower+1e-7,self.upper-1e-7)

    def decode(self,x):
        e=self.e;j=5
        p={'mass_msun':float(self.mass_scale*np.exp(x[0])),
           'reference_mass_msun':e.ref_mass,
           'center_mas':(e.origin+self.scale*(x[1:3]+(e.data.t0-self.epoch)*x[3:5]/e.tscale)).tolist(),
           'proper_motion_mas_yr':(self.scale*x[3:5]/e.tscale).tolist(),
           'shear':[0.,0.],'compact_quad':[0.,0.],'convergence':0.,'flux_ratio':float(e.data.analysis.get('flux_ratio',1.))}
        if self.nuisance in ['shear','full']:p['shear']=x[j:j+2].tolist();j+=2
        if self.nuisance=='full':p['compact_quad']=(x[j:j+2]*self.compact_factor).tolist();p['convergence']=float(x[j+2]);j+=3
        if self.fit_flux:p['flux_ratio']=float(np.exp(x[j]));j+=1
        p['source_mas']=(e.origin+x[j:].reshape(-1,2)*self.scale).tolist()
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
                 x_scale='jac',ftol=_FIT_OBJECTIVE_RTOL,xtol=1e-10,gtol=1e-8,max_nfev=max_nfev)
        solutions.append(solved)
    solved,selection=_select_multistart(solutions)
    pars=mapping.decode(solved.x)
    pars['reference_mass_msun']=e.ref_mass
    pred,branch=e.calculate(pars,admit=False)
    white=d.whiten((pred-d.observations).ravel());chi=float(white@white)
    cov,null,s,rank=_local_covariance(solved.jac)
    sig=np.sqrt(np.maximum(np.diag(cov),0.))
    unidentified=np.linalg.norm(null,axis=1)>1e-4 if null.size else np.zeros(len(sig),dtype=bool)
    report_jac=mapping.reporting_jacobian(solved.x)
    report_cov=report_jac@cov@report_jac.T
    report_null=report_jac@null
    report_unidentified=(np.linalg.norm(report_null,axis=1)/np.maximum(np.linalg.norm(report_jac,axis=1),1e-300)>1e-10
                         if null.size else np.zeros(len(sig),dtype=bool))
    dof=6*d.n-rank;pvalue=float(chi2_distribution.sf(chi,dof)) if dof>0 else None
    errors=[None if unidentified[i] else float(sig[i]) for i in range(len(sig))]
    def physical_error(i):return None if report_unidentified[i] else float(np.sqrt(max(report_cov[i,i],0.)))
    unc={'mass_msun':physical_error(0),
         'center_mas':[physical_error(i) for i in [1,2]],
         'proper_motion_mas_yr':[physical_error(i) for i in [3,4]],
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
    motion_cov=None if np.any(report_unidentified[3:5]) else report_cov[3:5,3:5].tolist()
    public_cov=[[None if report_unidentified[i] or report_unidentified[j] else float(report_cov[i,j])
                 for j in range(len(sig))] for i in range(len(sig))]
    track=[];track_sigma=[]
    for i,epoch in enumerate(d.epochs):
        t=(epoch-mapping.epoch)/e.tscale
        track.append((e.origin+mapping.scale*(solved.x[1:3]+t*solved.x[3:5])+e.parallax[i]).tolist())
        jac=np.zeros((2,len(sig)));jac[0,1]=jac[1,2]=mapping.scale;jac[0,3]=jac[1,4]=mapping.scale*t
        cc=jac@cov@jac.T
        bad=np.any(np.linalg.norm(jac@null,axis=1)/np.maximum(np.linalg.norm(jac,axis=1),1e-300)>1e-4) if null.size else False
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
            'r0_pc':e.r0,'worldtube_policy':'supplied' if 'r0_pc' in d.analysis else 'v2: 0.001 times the median observed primary-pair half-separation converted to pc; reference-mass independent data-scale convention, not a measured surface',
            'flux_policy':'fitted_conditional_flux' if mapping.fit_flux else 'fixed_regular_body_proxy' if family=='r1' else 'not_used',
            'parameter_basis':mapping.metadata(),
            'bounds_internal':{'lower':[float(v) if np.isfinite(v) else None for v in mapping.lower],
                               'upper':[float(v) if np.isfinite(v) else None for v in mapping.upper]}},
            'estimates':{k:pars[k] for k in ['mass_msun','center_mas','proper_motion_mas_yr','shear','compact_quad','convergence','flux_ratio']},
            'uncertainty':unc,'motion_snr':motion_snr,'proper_motion_covariance':motion_cov,
            'physical_parameter_uncertainty':{'schema':'bhtracker.reporting_covariance.v2',
                'names':['mass_msun',*['flux_ratio' if name=='log_flux' else name for name in mapping.names[1:]]],'covariance':public_cov,
                'unidentified':report_unidentified.tolist(),'null_basis_columns':report_null.tolist(),
                'null_projection_relative_tolerance':1e-10,
                'internal_to_reporting_jacobian':report_jac.tolist(),
                'contract':'Covariance entries involving an unidentified quantity are null. Null columns are transformed tangent directions in the stated physical reporting coordinates; the internal generalized inverse is not an ordinary covariance for unidentified directions.'},
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
            'multistart_chi2':selection['candidate_chi2'],
            'optimizer_selection':selection,
            'runtime_seconds':time.perf_counter()-beginning,
            'runtime':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__},
            'conditional_envelope':{'status':'NOT_REQUESTED'},
            '_internal':{'parameters':pars,'x':solved.x.tolist(),'covariance':cov.tolist(),
                         'basis':mapping.metadata(),'covariance_semantics':'generalized inverse restricted to the identified internal subspace',
                         'null_basis_columns':null.tolist(),
                         'jacobian':solved.jac.tolist(),'unidentified':unidentified.tolist()}}
    if family=='r1' and status=='FIT_REJECTED':
        result['conditional_envelope']={'status':'NOT_EVALUATED','reasons':['Baseline fit rejected; conditional information must not be interpreted on an unacceptable fit.']}
    elif family=='r1':
        from .envelope import assess_envelope
        result['conditional_envelope']=assess_envelope(d,e,pars,solved.jac,pred,physics)
    from .interpretation import bhsm_interpretation
    result['bhsm_interpretation']=bhsm_interpretation(family,result['estimates'],unc,result['model'],status)
    return result

def _admission_constraints(engine, parameters, branch, admission):
    """Continuous, dimensionless sufficient-domain margins (nonnegative is feasible).

    The public forward calculation remains the final admission certificate.
    Discrete provenance/geometry checks are recorded separately; solver success
    never substitutes for that certificate.
    """
    a=engine.data.analysis;g=engine.data.geometry
    impact=np.asarray(branch['impact_pc']);mass_pc=GM_SUN*parameters['mass_msun']/(C*C*3.085677581491367e16)
    speed=np.linalg.norm(parameters['proper_motion_mas_yr'])/206264806.24709636*g['D_l_pc']*3.085677581491367e16*(1+g['z_l'])/(31557600*C)
    margins={'weak_at_impacts':1-mass_pc/(float(np.min(impact))*float(a.get('weak_metric_cap',.01))),
             'quasistatic_motion_baseline':1-speed/float(a.get('quasistatic_speed_ratio_cap',.01)),
             'impact_outside_worldtube':1-engine.r0/float(np.min(impact))}
    if engine.family=='r1':
        scales=admission.get('scales',{});budgets=admission.get('approximation_budgets',{})
        state=admission.get('boundary_state',{})
        ratios=[('worldtube_weak_metric','weak_metric_bound_at_worldtube','weak_metric_cap'),
                ('quasistatic_motion','quasistatic_advection_ratio','quasistatic_speed_ratio_cap'),
                ('quasistatic_intrinsic_evolution','intrinsic_evolution_ratio','quasistatic_speed_ratio_cap'),
                ('frozen_background','background_drift_ratio','background_drift_cap'),
                ('small_spatial_background_gradient','uniform_total_spatial_to_temporal_gradient_ratio_bound','spatial_gradient_ratio_cap')]
        for name,value,budget in ratios:
            v=scales.get(value);b=budgets.get(budget)
            margins[name]=1-float(v)/float(b) if v is not None and b else -1.
        cap=state.get('amplitude_norm_max')
        margins['state_within_sufficient_cap']=1-float(state.get('amplitude_norm',0))/cap if cap else -1.
        for key in ['spatial','time']:
            margins['retained_'+key+'_principal_positive']=1-float(state.get('uniform_'+key+'_principal_fraction_bound',2.))
    return margins


def profile(dataset,result,parameter='mass_msun',points=17):
    """Physically constrained nuisance profile, with explicit unresolved points.

    A local constrained solve is attempted when an unconstrained optimum fails
    admission. No failed search proves physical infeasibility. Only admitted,
    adequately solved points enter the physical likelihood and its reference.
    Reference delta-chi2 levels do not establish nonregular/boundary coverage.
    """
    from .physics_admission import assess_physics
    d=load_dataset(dataset);model=result['model']
    if d.sha256!=result['data_summary']['sha256']:
        raise ValueError('profile dataset differs from the fitted input; use dataset.json from this analysis export')
    e=LensEngine(d,model['family'],reference_mass=model['reference_mass_msun'])
    mapping=ParameterMap(e,model['nuisance'])
    if model.get('parameter_basis')!=mapping.metadata() or result.get('_internal',{}).get('basis')!=mapping.metadata():
        raise ValueError('saved result has a legacy or incompatible internal parameter basis; refit the preserved dataset before profiling (no silent coordinate migration)')
    x0=np.asarray(result['_internal']['x'])
    try:
        reference_prediction,_=e.calculate(mapping.decode(x0),admit=True)
    except ValueError as exc:
        raise ValueError('profile requires an admitted reference minimum; refit within the physical domain') from exc
    if not result.get('optimizer_converged'):
        raise ValueError('profile requires an adequately solved reference minimum')
    indices={'mass_msun':0,'motion_x':3,'motion_y':4}
    if parameter not in indices:raise ValueError('profile parameter must be mass_msun, motion_x or motion_y')
    if isinstance(points,bool) or not isinstance(points,int) or not 7<=points<=81:raise ValueError('profile points must be 7 to 81')
    index=indices[parameter];cov=np.asarray(result['_internal']['covariance'])
    width=max(3*np.sqrt(max(cov[index,index],0)),.001)
    grid=np.linspace(max(mapping.lower[index],x0[index]-width),min(mapping.upper[index],x0[index]+width),points)
    grid=np.sort(np.r_[grid[~np.isclose(grid,x0[index],rtol=0,atol=1e-14)],x0[index]])
    mask=np.arange(len(x0))!=index;rows=[]
    for value in grid:
        cache={}
        def evaluate(free):
            key=np.asarray(free,dtype=float).tobytes()
            if key in cache:return cache[key]
            x=x0.copy();x[index]=value;x[mask]=free
            pars=mapping.decode(x)
            try:
                pred,branch=e.calculate(pars,admit=False)
                white=d.whiten((pred-d.observations).ravel())
                admission=assess_physics(e.physics_config,pars,branch['impact_pc'])
                margins=_admission_constraints(e,pars,branch,admission)
                baseline=admission['allowed_physics_models'].get('baseline_point_mass',False)
                conditional=e.family!='r1' or admission['allowed_physics_models'].get('r1_boundary_conditional',False)
                admitted=bool(baseline and conditional)
                # Branch continuation, parity and all public physical conditions
                # are assessed again for candidate solutions below.
                out=(white,pars,margins,admitted,admission)
            except (ValueError,FloatingPointError,np.linalg.LinAlgError):
                out=(np.full(6*d.n,1e8),pars,{},False,None)
            cache[key]=out
            return out
        def residual(free):return evaluate(free)[0]
        unconstrained=least_squares(residual,x0[mask],bounds=(mapping.lower[mask],mapping.upper[mask]),
                   jac='3-point',x_scale='jac',max_nfev=160,ftol=1e-10,xtol=1e-10,gtol=1e-8)
        candidate=unconstrained.x;details=evaluate(candidate)
        searched=False;search_method='not_required';solver_success=bool(unconstrained.success);message=str(unconstrained.message)
        if not details[3]:
            searched=True
            # SLSQP varies nuisance parameters at the fixed physical value;
            # this is a constrained optimization, not post-hoc filtering.
            margin_names=list(_admission_constraints(e,mapping.decode(x0),
                    e.calculate(mapping.decode(x0),admit=False)[1],
                    assess_physics(e.physics_config,mapping.decode(x0),e.calculate(mapping.decode(x0),admit=False)[1]['impact_pc'])))
            def constraint(free):
                margins=evaluate(free)[2]
                return np.array([margins.get(name,-1.) for name in margin_names])-1e-9
            scale=max(1.,min(float(details[0]@details[0]),1e6))
            def objective(free):
                r=evaluate(free)[0];return float(r@r)/scale
            def objective_jacobian(free):
                # Differentiate residuals before squaring: this avoids finite
                # differences of a very steep chi-square near its minimum.
                from scipy.optimize._numdiff import approx_derivative
                r=residual(free)
                J=approx_derivative(residual,free,method='3-point')
                return 2*J.T@r/scale
            candidates=[]
            invariant_wall=(e.family=='r1' and index==0 and not mapping.fit_flux
                            and details[2].get('worldtube_weak_metric',1.)<0)
            # For fixed mass and fixed flux, this sufficient R1 worldtube
            # condition contains no free fitted nuisance. Do not burn hundreds
            # of likelihood iterations against a nuisance-invariant wall. Keep
            # the public point unresolved rather than claiming a general
            # impossibility result about physics outside the declared family.
            search_method='nuisance_invariant_R1_worldtube_check' if invariant_wall else 'SLSQP_constrained_nuisance_multistart'
            for start in ([] if invariant_wall else [candidate,x0[mask]]):
                constrained=minimize(objective,start,jac=objective_jacobian,method='SLSQP',
                    bounds=list(zip(mapping.lower[mask],mapping.upper[mask])),
                    constraints=[{'type':'ineq','fun':constraint}],
                    options={'maxiter':350,'ftol':1e-10,'eps':2e-7})
                state=evaluate(constrained.x)
                if state[3] and constrained.success:
                    candidates.append((float(state[0]@state[0]),constrained,state))
            if candidates:
                _,chosen,details=min(candidates,key=lambda item:item[0]);candidate=chosen.x
                solver_success=True;message=str(chosen.message)
            else:
                solver_success=False;message='Constrained local searches did not establish an admitted optimum; physical feasibility remains unresolved.'
        admitted=bool(details[3] and solver_success)
        if admitted:
            try:e.calculate(details[1],admit=True)
            except ValueError:admitted=False;solver_success=False
        physical=mapping.mass_scale*np.exp(value) if index==0 else value*mapping.scale/e.tscale
        boundary=admitted and (min(details[2].values())<1e-6 or np.any(np.minimum(candidate-mapping.lower[mask],mapping.upper[mask]-candidate)<1e-5))
        state=('ADMITTED_BOUNDARY' if boundary else 'ADMITTED_INTERIOR') if admitted else ('PHYSICAL_DOMAIN_UNRESOLVED' if searched else 'NUMERICAL_FAILURE')
        rows.append({'value':float(physical),'chi2':float(details[0]@details[0]) if admitted else None,
            'converged':bool(solver_success),'admitted':admitted,'solution_status':state,
            'constrained_nuisance_search':searched,'physical_interval_eligible':admitted,
            'constrained_search_method':search_method,
            'physical_truncation':bool(boundary or not admitted),'physical_feasibility_proven_impossible':False,
            'admission_margins':details[2] if admitted else None,
            'parameters':details[1] if admitted else None,
            'unconstrained_chi2':float(unconstrained.fun@unconstrained.fun),
            'unconstrained_admitted':bool(evaluate(unconstrained.x)[3]),'optimizer_message':message})
    reference_white=d.whiten((reference_prediction-d.observations).ravel())
    minimum=min([float(reference_white@reference_white)]+[r['chi2'] for r in rows if r['physical_interval_eligible']])
    for row in rows:row['delta_chi2']=row['chi2']-minimum if row['physical_interval_eligible'] else None
    return {'schema':'bhtracker.physical_profile.v2','parameter':parameter,'points':rows,
            'reference_chi2':minimum,'reference_admitted':True,'boundary_margin_tolerance':1e-6,
            'reference_levels':[1.,3.841458820694124],
            'interval_construction':'Only physical_interval_eligible points may enter crossings; unresolved points break a crossing bracket. Boundary points indicate physical truncation, not calibrated coverage.',
            'interpretation':'Locally reoptimized nuisance likelihood constrained by the public physical domain. Failed searches are unresolved, not infeasibility proofs. Reference levels need separate calibration for nonregular/boundary cases.'}
