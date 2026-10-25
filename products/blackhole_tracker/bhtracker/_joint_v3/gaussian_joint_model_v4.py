"""Audited Gaussian GP candidate, explicit native-diagonal + Matern/SHO law.

Composition uses the authenticated immutable native-data adapter from the
separately tested centered model. This class does not import observations,
launch searches, admit a benchmark or infer an absolute source distance.
Baselines and angular-frame coefficients are profiled, never fixed at truth.
"""
import math
import hashlib
import json
from pathlib import Path
from . import published_gp_leaf_v2 as gp_source
from . import centered_geometry_v1 as geometry_source
import numpy as np
from .published_gp_leaf_v2 import Hyperparameters, GaussianCovariance
from .centered_geometry_v1 import centered_geometry
from . import gaussian_mean_profile_v1 as linear_profile

MAG = 2.5/math.log(10.)
YEAR = 365.25
KAPPA = 4*1.3271244e20/(299792458.**2*149597870700.)*(180/math.pi)*3600000


class GaussianJointModel:
    """Working Gaussian candidate; all instrumental errors stay source-owned.

    State: 5 centered lens-geometry parameters; one source fraction per
    instrument; log sigma_M, log rho_days, log sigma_SHO, log omega0_per_day.
    This initial declared candidate keeps the source diagonal fixed; it may
    fail an adequacy test if that diagonal is unsuitable. A successful solver
    will not silently rescale it or certify the covariance.
    """
    def __init__(self, data_adapter, *, hyper_bounds=None):
        data_adapter.verify_snapshot()
        self.data = data_adapter
        d = self.data
        self.names = d.names
        self.fraction_start = 5
        self.hyper_start = 5+len(self.names)
        self.parameter_names = tuple(d.parameter_names[:5]) + tuple(
            name+'_source_fraction' for name in self.names) + (
            'log_matern_sigma_mag','log_matern_rho_days',
            'log_sho_sigma_mag','log_sho_omega_rad_per_day')
        # These are prospectively declared ANALYSIS caps, not measured limits.
        # A cap contact prevents a finite physical confidence endpoint.
        hbounds = hyper_bounds or ((1e-6,.3),(.02,5000.),(1e-6,.3),(2*math.pi/10000.,2*math.pi/.02))
        linear_profile._reject_booleans(hbounds)
        if len(hbounds)!=4 or any(len(pair)!=2 or not np.isfinite(pair).all()
                or pair[0]<=0 or pair[0]>=pair[1] for pair in hbounds):
            raise ValueError('Four finite ordered positive hyperparameter analysis bounds required')
        self.hyper_bounds = tuple(tuple(map(float,p)) for p in hbounds)
        self.lower = np.r_[d.lower[:5],np.full(len(self.names),1e-5),np.log([p[0] for p in hbounds])]
        self.upper = np.r_[d.upper[:5],np.ones(len(self.names)),np.log([p[1] for p in hbounds])]
        self.scales = np.r_[d.scales[:5],np.full(len(self.names),.1),np.ones(4)]
        self.baseline_bounds = tuple((float(np.median(d.yp[g]))-5.,float(np.median(d.yp[g]))+5.) for g in d.groups)
        for array in (self.lower,self.upper,self.scales): array.setflags(write=False)
        paths=[Path(__file__).resolve(),Path(gp_source.__file__).resolve(),Path(geometry_source.__file__).resolve(),Path(linear_profile.__file__).resolve()]
        self._source_pins = {str(path):hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
        self._array_pins={name:hashlib.sha256(getattr(self,name).tobytes()).hexdigest() for name in ('lower','upper','scales')}
        self._meta_pin=self._metadata_hash()

    def _metadata_hash(self):
        value={'input_sha256':self.data.input_sha256,'names':self.names,'hyper_start':self.hyper_start,'parameter_names':self.parameter_names,'hyper_bounds':self.hyper_bounds,'baseline_bounds':self.baseline_bounds}
        return hashlib.sha256(json.dumps(value,sort_keys=True,allow_nan=False).encode()).hexdigest()

    def verify_snapshot(self):
        result=self.data.verify_snapshot()
        for path,expected in self._source_pins.items():
            if hashlib.sha256(Path(path).read_bytes()).hexdigest()!=expected:raise ValueError('Gaussian candidate source changed: '+path)
        for name,expected in self._array_pins.items():
            arr=getattr(self,name)
            if arr.flags.writeable or hashlib.sha256(arr.tobytes()).hexdigest()!=expected:raise ValueError('Gaussian candidate analysis domain changed: '+name)
        if self._metadata_hash()!=self._meta_pin:raise ValueError('Gaussian candidate metadata changed')
        return {**result,'gaussian_candidate_source_pins':dict(self._source_pins)}

    def active_optimizer_indices(self,zero_components=()):
        if set(zero_components)-{'matern','sho'}:raise ValueError('Unknown zero component')
        inactive=set()
        if 'matern' in zero_components:inactive.update((self.hyper_start,self.hyper_start+1))
        if 'sho' in zero_components:inactive.update((self.hyper_start+2,self.hyper_start+3))
        return tuple(j for j in range(len(self.parameter_names)) if j not in inactive)

    def decode(self,x):
        p = self.data.decode(x)
        p['t0_evaluated_pair'] = {'origin_jd':self.data.time_origin,'offset_days':float(x[0])}
        return p

    def seeds(self):
        for native_seed in self.data.seeds():
            yield np.r_[native_seed[:5], [.05 if n=='OGLE' else .95 for n in self.names],
                        np.log([.005,30.,.005,.3])]

    def _photo(self,x,amplitude,da,*,zero_components=()):
        d = self.data
        values = np.exp(x[self.hyper_start:])
        if 'matern' in zero_components: values[0]=0.
        if 'sho' in zero_components: values[2]=0.
        hyper=Hyperparameters(*map(float,values))
        derivative=np.zeros((len(d.tp),len(x)))
        prediction=np.empty(len(d.tp)); inverse_residual=np.empty(len(d.tp))
        baselines=[]; active=[]; value=0.; quadratic=0.
        for k,(name,group) in enumerate(zip(self.names,d.groups)):
            fraction=x[5+k]
            blend=1+fraction*(amplitude[group]-1)
            curve=-MAG*np.log1p(fraction*(amplitude[group]-1))
            target=d.yp[group]-curve
            if name=='OGLE':
                covariance=GaussianCovariance(d.tp[group]-d.time_origin,d.sp[group],hyper)
                solved=covariance.inverse(np.column_stack([target,np.ones(len(group))]))
                b=float(np.sum(solved[:,0])/np.sum(solved[:,1]))
            else:
                weights=d.sp[group]**-2
                b=float(np.sum(weights*target)/np.sum(weights))
            lo,hi=self.baseline_bounds[k]
            b=float(np.clip(b,lo,hi)); baselines.append(b)
            if b in (lo,hi): active.append({'instrument':name,'baseline_analysis_cap':b})
            prediction[group]=b+curve
            residual=d.yp[group]-prediction[group]
            if name=='OGLE':
                value+=covariance.deviance(residual)
                quadratic+=covariance.quadratic(residual)
                inverse_residual[group]=covariance.inverse(residual)
            else:
                inverse_residual[group]=residual/d.sp[group]**2
                q=float(residual@inverse_residual[group]); quadratic+=q
                value+=q+float(np.sum(np.log(2*math.pi*d.sp[group]**2)))
            derivative[group,:5]=-MAG*fraction*da[group]/blend[:,None]
            derivative[group,5+k]=-MAG*(amplitude[group]-1)/blend
        gradient=-2*inverse_residual@derivative
        return {'value':float(value),'quadratic':float(quadratic),'gradient':gradient,
                'predictions':prediction,'baselines':baselines,'active':active,
                'hyper':hyper,'zero_components':tuple(zero_components)}

    def _angular(self,x,*,fixed_mass=None):
        d=self.data
        _,_,unit,du=centered_geometry(d.ta,numerical_time_origin=d.time_origin,
            t0_offset_days=x[0],tE_days=float(np.exp(x[1])),u0_heliocentric=x[2],
            angle_source_minus_lens_rad=x[3],pi_E=x[4],earth=d.ea)
        unit,du=d.average(unit),d.average(du)
        epoch=d.average(d.ta[:,None])[:,0]
        parallax=-d.average(d.ea-d.eref)
        columns=[unit.ravel()]
        for axis in range(2):
            col=np.zeros((len(d.ar),2));col[:,axis]=1.;columns.append(col.ravel())
        for axis in range(2):
            col=np.zeros((len(d.ar),2));col[:,axis]=(epoch-d.reference)/YEAR;columns.append(col.ravel())
        columns.append(parallax.ravel())
        for name in d.filters[1:]:
            mask=np.array([r['filter']==name for r in d.ar])
            for axis in range(2):
                col=np.zeros((len(d.ar),2));col[mask,axis]=1.;columns.append(col.ravel())
        design=np.column_stack(columns)
        fixed={0:KAPPA*fixed_mass*x[4]} if fixed_mass is not None else None
        profile=linear_profile.profile_mean(design/d.sa[:,None],d.ya/d.sa,d.linear_bounds,fixed=fixed)
        beta=profile['coefficients'];residual=d.ya-design@beta
        score=-2*residual/d.sa**2
        gradient=np.zeros(len(x))
        gradient[:5]=np.einsum('ni,nij->j',score.reshape(-1,2),beta[0]*du)
        if fixed_mass is not None: gradient[4]+=score@(KAPPA*fixed_mass*unit.ravel())
        value=profile['quadratic']+float(np.sum(np.log(2*math.pi*d.sa**2)))
        return {'value':float(value),'gradient':gradient,'profile':profile,
                'prediction':(design@beta).reshape(-1,2),'residual':residual,
                'design':design}

    def evaluate(self,state,*,fixed_mass=None,details=False,zero_components=(),hyper_step=2e-5,objective_audit=None):
        linear_profile._reject_booleans(state)
        if np.asarray(state).dtype.kind not in 'iuf':
            raise ValueError('Real numeric state required')
        x=np.asarray(state,dtype=float)
        if x.shape!=self.lower.shape or not np.isfinite(x).all() or np.any(x<self.lower) or np.any(x>self.upper):
            raise ValueError('Finite state within declared Gaussian candidate domain required')
        if fixed_mass is not None and (isinstance(fixed_mass,bool) or not np.isfinite(fixed_mass) or fixed_mass<=0):
            raise ValueError('Positive finite profiled mass required')
        if set(zero_components)-{'matern','sho'} or len(set(zero_components))!=len(zero_components):
            raise ValueError('Only explicit distinct zero-amplitude component faces are admitted')
        if not np.isfinite(hyper_step) or hyper_step<=0:raise ValueError('Positive finite derivative step required')
        if objective_audit is not None and not callable(objective_audit):
            raise ValueError('Objective audit must be callable or None')
        d=self.data
        amplitude,da,_,_=centered_geometry(d.tp,numerical_time_origin=d.time_origin,
            t0_offset_days=x[0],tE_days=float(np.exp(x[1])),u0_heliocentric=x[2],
            angle_source_minus_lens_rad=x[3],pi_E=x[4],earth=d.ep)
        # The angular profile depends only on geometry (and fixed_mass), never
        # on a covariance coordinate. Its same value therefore completes every
        # finite-difference photometric trial into an actual full joint value.
        angular=self._angular(x,fixed_mass=fixed_mass)
        photometric_evaluations=0
        def scored_photo(state,kind):
            nonlocal photometric_evaluations
            event={'kind':kind,'state':state.tolist(),
                'zero_components':list(zero_components),'fixed_mass':fixed_mass,
                'has_full_gradient':False}
            if objective_audit is not None:
                objective_audit({**event,'stage':'PLANNED'})
            photometric_evaluations+=1
            try:
                result=self._photo(state,amplitude,da,zero_components=zero_components)
                full_value=float(result['value']+angular['value'])
                if not np.isfinite(full_value):
                    raise FloatingPointError('Unrepresentable internal full objective')
            except Exception as exc:
                if objective_audit is not None:
                    objective_audit({**event,'stage':'FAILED','error_type':type(exc).__name__,'error':str(exc)})
                raise
            if objective_audit is not None:
                # The callback must commit or throw. Nothing after a failed
                # commit is computed by this evaluator. Caller latches failure.
                objective_audit({**event,'stage':'RETURNED',
                    'negative_two_log_likelihood':full_value,
                    'photometric_deviance':float(result['value']),
                    'same_geometry_angular_deviance':float(angular['value'])})
            return result
        photo=scored_photo(x,'CENTRAL')
        gradient=photo['gradient']+angular['gradient']
        # Only four covariance derivatives use finite differences; the profiled
        # mean and physical geometry use exact envelope first derivatives.
        for j in range(self.hyper_start,len(x)):
            if (j in (self.hyper_start,self.hyper_start+1) and 'matern' in zero_components) or (j in (self.hyper_start+2,self.hyper_start+3) and 'sho' in zero_components):
                # Both amplitude and coherence disappear on this exact face.
                gradient[j]=0.;continue
            a=max(self.lower[j],x[j]-hyper_step);b=min(self.upper[j],x[j]+hyper_step)
            xa=x.copy();xb=x.copy();xa[j]=a;xb[j]=b
            upper_photo=scored_photo(xb,'HYPER_PLUS_'+str(j))
            lower_photo=scored_photo(xa,'HYPER_MINUS_'+str(j))
            gradient[j]=(upper_photo['value']-lower_photo['value'])/(b-a)
        value=photo['value']+angular['value']
        if not np.isfinite(value) or not np.isfinite(gradient).all():raise FloatingPointError('Unrepresentable full Gaussian score')
        profile=angular['profile']
        result={'negative_two_log_likelihood':float(value),'gradient':gradient,
                'linear_profile_identified':profile['linear_parameters_identified'],
                'linear_profile_rank':profile['full_column_rank'],
                'linear_profile_projected_score':profile['column_normalized_projected_score'],
                'input_purpose':d.purpose,'law':'native diagonal plus variance-normalized F10-type Matern3/2 and Q=1/sqrt2 SHO; Gaussian',
                'accepted_mass_interval':None,'known_black_hole_recovery_accepted':False,
                'photometric_objective_evaluations':photometric_evaluations}
        if details:
            beta=profile['coefficients'];p=self.decode(x)
            p.update(dict(zip(d.linear_names,map(float,beta))))
            p['conditional_mass_msun']=float(beta[0]/(KAPPA*x[4])) if beta[0]>0 and x[4]>0 else None
            p['instruments']={name:{'baseline_magnitude':float(photo['baselines'][j]),'source_fraction':float(x[5+j])} for j,name in enumerate(self.names)}
            hp=photo['hyper']
            p['GP']={'matern_sigma_mag':hp.matern_sigma_mag,'matern_rho_days':None if 'matern' in zero_components else hp.matern_rho_days,'sho_sigma_mag':hp.sho_sigma_mag,'sho_omega_rad_per_day':None if 'sho' in zero_components else hp.sho_omega_rad_per_day,'zero_amplitude_components':list(zero_components),'zero_component_coherence_status':'UNIDENTIFIED_NOT_MEASURED'}
            result['complete_evaluated_state']={'parameter_names':list(self.parameter_names),'state':x.tolist(),'zero_components':list(zero_components),'active_optimizer_indices':list(self.active_optimizer_indices(zero_components)),'numerical_time_origin_jd':d.time_origin,'t0_offset_days':float(x[0]),'angular_reference_jd':d.reference,'input_sha256':d.input_sha256}
            result.update(parameters=p,baseline_magnitudes=dict(zip(self.names,photo['baselines'])),
                baseline_cap_contacts=photo['active'],photometric_quadratic=photo['quadratic'],
                photometric_predictions_magnitude=photo['predictions'].tolist(),
                astrometric_residuals_NE_mas=angular['residual'].reshape(-1,2).tolist(),
                astrometric_quadratic=profile['quadratic'],
                angular_profile={k:v for k,v in profile.items() if k not in ('coefficients','residual')},
                working_covariance='Supplied positive native marginal errors plus an explicitly fitted Gaussian covariance hypothesis; angular independence assumed, no complete matrix claimed supplied.',
                BHSM='One optical exterior interpreted as BHSM hypersurface topography, counted once; no core, horizon or BH-only envelope state measured.')
        return result
