"""Native joint likelihood v2: stable time coordinates and native-marginal OU.

NE is north/east on the tangent plane. q points LENS -> unlensed SOURCE.
The heliocentric straight-line source-minus-lens motion is n=(cos a,sin a),
q=u0*(-sin a,cos a)+(t-t0)/tE*n+piE*rEarth_NE/AU. t0/u0 describe the
rectilinear HELIOCENTRIC trajectory, not the apparent peak including parallax.
No absolute frame motion, source distance, horizon or nongeometric core is
inferred by assigning a literature mass to the data.
"""
from copy import deepcopy
from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from scipy.linalg import cholesky, solve_triangular, cholesky_banded, solve_banded, cho_solve_banded
from scipy.optimize import least_squares, lsq_linear
from scipy.stats import chi2

JOINT_SCHEMA='bhtracker.native_joint_mass.v1'
JOINT_RESULT_SCHEMA='bhtracker.native_joint_mass_result.v2'
YEAR=365.25
# IAU 2015 nominal solar GM, exact c/AU, radians converted to mas.
KAPPA_MAS_MSUN=4*1.3271244e20/(299792458.**2*149597870700.)*(180/math.pi)*3600000
MAG=2.5/math.log(10.)


def project_ne(vector,ra_deg,dec_deg):
    a,d=np.deg2rad([ra_deg,dec_deg]);v=np.asarray(vector)
    return np.stack([v@np.array([-np.cos(a)*np.sin(d),-np.sin(a)*np.sin(d),np.cos(d)]),
                     v@np.array([-np.sin(a),np.cos(a),0.])],axis=-1)


def earth_heliocentric_ne(jd_tdb,ra_deg,dec_deg,ephemeris='builtin'):
    """Astropy ICRS-oriented observer-Sun vectors; times explicitly JD TDB."""
    from astropy.time import Time
    from astropy.coordinates import get_body_barycentric
    times=Time(np.asarray(jd_tdb),format='jd',scale='tdb')
    earth=get_body_barycentric('earth',times,ephemeris=ephemeris)
    sun=get_body_barycentric('sun',times,ephemeris=ephemeris)
    return project_ne((earth-sun).xyz.to_value('au').T,ra_deg,dec_deg)


def hjd_utc_to_tdb(hjd,ra_deg,dec_deg,location,clock_offset_seconds=0.):
    """Explicit HJD_UTC assumption -> observer JD UTC -> JD TDB.

    Invert heliocentric light-time iteratively at the actual observatory. The
    caller must record the assumed underlying clock and bound its sensitivity;
    this function does not turn an unspecified source clock into verified UTC.
    """
    from astropy.time import Time,TimeDelta
    from astropy.coordinates import SkyCoord
    from astropy import units as u
    from astropy.utils import iers
    # Use bundled IERS data: network refresh must not change this import.
    iers.conf.auto_download=False
    target=SkyCoord(ra_deg*u.deg,dec_deg*u.deg,frame='icrs')
    supplied=Time(np.asarray(hjd),format='jd',scale='utc',location=location)
    estimate=supplied
    for _ in range(4):
        correction=estimate.light_travel_time(target,kind='heliocentric')
        estimate=supplied-correction
    return (estimate+TimeDelta(clock_offset_seconds,format='sec')).tdb.jd


def trajectory(times,p,earth):
    times=np.asarray(times,dtype=float);earth=np.asarray(earth,dtype=float)
    if times.ndim!=1 or earth.shape!=(len(times),2) or not np.isfinite(times).all() or not np.isfinite(earth).all():raise ValueError('finite one-dimensional times and matching NE Earth vectors required')
    if not np.isfinite([p[k] for k in ['angle_source_minus_lens_rad','u0_heliocentric','t0_jd_tdb','tE_days','pi_E']]).all() or p['tE_days']<=0 or p['pi_E']<0:raise ValueError('finite physical trajectory parameters required')
    angle=p['angle_source_minus_lens_rad'];n=np.array([np.cos(angle),np.sin(angle)])
    b=np.array([-n[1],n[0]])
    return p['u0_heliocentric']*b+((np.asarray(times)-p['t0_jd_tdb'])/p['tE_days'])[:,None]*n+p['pi_E']*np.asarray(earth)


def amplification(q):
    q=np.asarray(q,dtype=float)
    if q.ndim<1 or q.shape[-1]!=2 or not np.isfinite(q).all():raise ValueError('finite NE separation vectors required')
    squared=np.sum(q**2,axis=-1)
    if np.any(squared<=1e-16):raise ValueError('exact critical alignment outside numerical domain')
    return (squared+2)/np.sqrt(squared*(squared+4))


def centroid_unit(q,blend_to_source=0.):
    """Centroid minus unlensed source per thetaE, including optional lens light.

    Fs*A and Fl weight the unresolved image centroid and lens location. Other
    unresolved stellar blend locations require a separately declared model.
    """
    q=np.asarray(q);a=amplification(q);g=np.asarray(blend_to_source)
    if not np.isfinite(g).all() or np.any(g<0):raise ValueError('luminous lens blend ratio must be nonnegative')
    return q*((a/(np.sum(q*q,axis=-1)+2)-g)/(a+g))[...,None]


def ou_whiten(times,error,residual,amplitude,tau_days,return_mean=False):
    """Exact O(N) exponential-GP Gaussian likelihood by banded factorization.

    L0 has diagonal1 and subdiagonal -exp(-dt/tau). L0*(K+D)*L0.T is
    tridiagonal; det(L0)=1. No covariance is claimed supplied by observations.
    Numeric duplicates are retained with independent marginal measurement noise.
    """
    t=np.asarray(times);sigma=np.asarray(error);r=np.asarray(residual)
    if t.ndim!=1 or not len(t) or sigma.shape!=t.shape or r.shape!=t.shape or not np.isfinite(t).all() or not np.isfinite(sigma).all() or not np.isfinite(r).all() or np.any(sigma<=0) or not np.isfinite([amplitude,tau_days]).all():raise ValueError('finite matched OU arrays, positive errors/amplitude/tau required')
    if np.any(np.diff(t)<0) or min(amplitude,tau_days)<=0:raise ValueError('sorted times and positive OU amplitude/tau required')
    transition=np.exp(-np.diff(t)/tau_days)
    innovation=amplitude**2*(-np.expm1(-2*np.diff(t)/tau_days))
    diagonal=sigma*sigma;diagonal=diagonal.copy()
    diagonal[0]+=amplitude**2
    diagonal[1:]+=innovation+transition**2*sigma[:-1]**2
    band=np.zeros((2,len(t)));band[0]=diagonal;band[1,:-1]=-transition*sigma[:-1]**2
    factor=cholesky_banded(band,lower=True,check_finite=False)
    transformed=r.copy();transformed[1:]-=transition*r[:-1]
    white=solve_banded((1,0),factor,transformed,check_finite=False)
    log_ratio=float(2*np.log(factor[0]).sum()-2*np.log(sigma).sum())
    if log_ratio < -1e-6:raise ValueError('GP determinant smaller than native diagonal determinant')
    if return_mean:
        w=cho_solve_banded((factor,True),transformed,check_finite=False)
        precision_r=w.copy();precision_r[:-1]-=transition*w[1:]
        return white,max(log_ratio,0.),r-sigma*sigma*precision_r
    return white,max(log_ratio,0.)


def _canonical_numbers(value):
    if isinstance(value,bool):return value
    if isinstance(value,dict):return {key:_canonical_numbers(item) for key,item in value.items()}
    if isinstance(value,(list,tuple)):return [_canonical_numbers(item) for item in value]
    if isinstance(value,float) and np.isfinite(value) and value.is_integer():return int(value)
    return value

def _hash(data):return hashlib.sha256(json.dumps(_canonical_numbers(data),sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


@dataclass
class JointData:
    document:dict
    def __post_init__(self):
        self.document=deepcopy(self.document)
        d=self.document
        if d.get('schema')!=JOINT_SCHEMA or d.get('time_coordinate')!='JD_TDB':raise ValueError('versioned joint schema with explicit JD_TDB required')
        if not d.get('metadata',{}).get('time_and_frame_provenance'):raise ValueError('joint time/frame provenance required')
        if d['metadata'].get('ra_axis')!='EAST_TANGENT_ALPHA_COS_DEC':raise ValueError('east tangent-plane RA convention must be explicit')
        for key in ['reference_jd_tdb','ra_deg','dec_deg']:
            if isinstance(d[key],bool) or not isinstance(d[key],(int,float)) or not np.isfinite(d[key]):raise ValueError('finite reference epoch/sky coordinates required')
        if not -90<=d['dec_deg']<=90 or not 0<=d['ra_deg']<360:raise ValueError('sky coordinates outside angular domain')
        if not d['photometry'] or not d['astrometry']:raise ValueError('actual photometry and astrometry both required')
        ids=[]
        for row in d['photometry']:
            for key in ['time_jd_tdb','magnitude','magnitude_error']:
                if isinstance(row[key],bool) or not isinstance(row[key],(int,float)) or not np.isfinite(row[key]):raise ValueError('finite native photometry required')
            if row['magnitude_error']<=0:raise ValueError('positive native photometric error required')
            ids.append(row['source_row_id'])
        for row in d['astrometry']:
            for key in ['north_mas','east_mas','north_error_mas','east_error_mas']:
                if isinstance(row[key],bool) or not isinstance(row[key],(int,float)) or not np.isfinite(row[key]):raise ValueError('finite native astrometry required')
            if min(row['north_error_mas'],row['east_error_mas'])<=0:raise ValueError('positive native astrometric errors required')
            times=row['exposure_midpoints_jd_tdb']
            if not times or any(isinstance(t,bool) or not isinstance(t,(int,float)) or not np.isfinite(t) for t in times):raise ValueError('actual exposure midpoint samples required; no guessed precise HST epoch')
            if 'exposure_window_jd_tdb' in row:
                window=row['exposure_window_jd_tdb']
                if len(window)!=2 or any(isinstance(t,bool) or not isinstance(t,(int,float)) or not np.isfinite(t) for t in window) or window[0]>min(times) or window[1]<max(times):raise ValueError('finite ordered exposure window must contain all actual midpoints')
            ids.append(row['source_row_id'])
        if len(ids)!=len(set(ids)):raise ValueError('distinct observation source row IDs required')
    @property
    def sha256(self):return _hash(self.document)


class JointModel:
    def __init__(self,dataset,*,gp=False,cross_filter_correlation=0.,astrometric_jitter_mas=0.,
                 source_parallax_prior=None,free_filter_offsets=True,astrometric_lens_light=False,
                 exposure_time_choice='all_midpoints_equal_weight',noise_model='native_marginal_ou'):
        self.data=dataset if isinstance(dataset,JointData) else JointData(dataset);d=self.data.document
        if noise_model not in ['native_marginal_ou','calibrated_marginal_ou','additive_ou']:raise ValueError('declared versioned noise model required')
        self.options={'noise_model':noise_model,'gp':bool(gp),'cross_filter_correlation':float(cross_filter_correlation),
            'astrometric_jitter_mas':float(astrometric_jitter_mas),'source_parallax_prior':source_parallax_prior,
            'free_filter_offsets':bool(free_filter_offsets),'astrometric_lens_light':bool(astrometric_lens_light),
            'exposure_time_choice':exposure_time_choice}
        if not np.isfinite([cross_filter_correlation,astrometric_jitter_mas]).all() or not 0<=cross_filter_correlation<1 or astrometric_jitter_mas<0:raise ValueError('invalid assumed astrometric noise sensitivity')
        self.ref=float(d['reference_jd_tdb']);self.ra=d['ra_deg'];self.dec=d['dec_deg']
        self.pr=d['photometry'];self.ar=d['astrometry'];self.names=list(dict.fromkeys(r['instrument'] for r in self.pr))
        self.tp=np.array([float(np.average(r['exposure_midpoints_jd_tdb'],weights=[e['duration_seconds'] for e in r['native_exposure_metadata']])) if exposure_time_choice=='duration_weighted' and r.get('native_exposure_metadata') else r.get('exposure_window_jd_tdb',[r['time_jd_tdb'],r['time_jd_tdb']])[0 if exposure_time_choice=='earliest' else 1] if exposure_time_choice in ['earliest','latest'] else r['time_jd_tdb'] for r in self.pr]);self.yp=np.array([r['magnitude'] for r in self.pr]);self.sp=np.array([r['magnitude_error'] for r in self.pr])
        self.group=np.array([self.names.index(r['instrument']) for r in self.pr]);self.gp_indices=np.flatnonzero(self.group==self.names.index('OGLE')) if 'OGLE' in self.names else np.array([],dtype=int)
        if gp and not len(self.gp_indices):raise ValueError('OGLE instrument required for optional OGLE OU noise model')
        if source_parallax_prior is not None and (len(source_parallax_prior)!=2 or not np.isfinite(source_parallax_prior).all() or source_parallax_prior[1]<=0):raise ValueError('finite source parallax prior with positive sigma required')
        self.gp_indices=self.gp_indices[np.argsort(self.tp[self.gp_indices],kind='stable')]
        self.ta=[];self.starts=[];self.counts=[];self.weights=[];self.weight_sums=[]
        for row in self.ar:
            times=np.asarray(row['exposure_midpoints_jd_tdb'])
            if exposure_time_choice=='earliest':times=np.array([row.get('exposure_window_jd_tdb',[min(times),max(times)])[0]])
            elif exposure_time_choice=='latest':times=np.array([row.get('exposure_window_jd_tdb',[min(times),max(times)])[1]])
            elif exposure_time_choice not in ['all_midpoints_equal_weight','duration_weighted']:raise ValueError('unsupported exposure time choice')
            weights=np.array([e['duration_seconds'] for e in row['native_exposure_metadata']]) if exposure_time_choice=='duration_weighted' else np.ones(len(times))
            if not np.isfinite(weights).all() or np.any(weights<=0) or len(weights)!=len(times):raise ValueError('positive matched declared exposure weights required')
            self.starts.append(len(self.ta));self.counts.append(len(times));self.ta.extend(times);self.weights.extend(weights);self.weight_sums.append(float(sum(weights)))
        self.ta=np.array(self.ta);self.counts=np.array(self.counts);self.weights=np.array(self.weights);self.weight_sums=np.array(self.weight_sums)
        self.ep=earth_heliocentric_ne(self.tp,self.ra,self.dec,d.get('ephemeris','builtin'))
        self.ea=earth_heliocentric_ne(self.ta,self.ra,self.dec,d.get('ephemeris','builtin'))
        self.eref=earth_heliocentric_ne([self.ref],self.ra,self.dec,d.get('ephemeris','builtin'))[0]
        self.ya=np.array([[r['north_mas'],r['east_mas']] for r in self.ar]).ravel()
        self.sa=np.sqrt(np.array([[r['north_error_mas'],r['east_error_mas']] for r in self.ar]).ravel()**2+astrometric_jitter_mas**2)
        covariance=np.diag(self.sa**2)
        for i,a in enumerate(self.ar):
            for j,b in enumerate(self.ar[:i]):
                if a['visit_id']==b['visit_id']:
                    for axis in [0,1]:covariance[2*i+axis,2*j+axis]=covariance[2*j+axis,2*i+axis]=cross_filter_correlation*self.sa[2*i+axis]*self.sa[2*j+axis]
        self.chol=cholesky(covariance,lower=True)
        self.filters=list(dict.fromkeys(r['filter'] for r in self.ar))
        analysis=d.get('analysis',{})
        if not str(d.get('data_version','')).startswith('OGLE-Mroz2022-corrected_LamLu2023v2'):
            required={'t0_jd_tdb','tE_days','u0_heliocentric','pi_E','theta_E_mas','relative_frame_source_parallax_mas'}
            if not required.issubset(analysis.get('bounds',{})) or not {'t0_jd_tdb','tE_days','u0_absolute','pi_E'}.issubset(analysis.get('initial_guess',{})):raise ValueError('future targets require explicit analysis bounds and initial guesses; benchmark defaults cannot be silently reused')
        self.analysis_bounds=analysis.get('bounds',{})
        self.parameter_names=['heliocentric_t0_offset_days','log_tE_days','u0_heliocentric','angle_source_minus_lens_rad','pi_E']
        self.lower=[float(d.get('bounds',{}).get('t0_relative_days',[5700,5830])[0]),np.log(20),-1.,-np.pi,0.]
        self.upper=[float(d.get('bounds',{}).get('t0_relative_days',[5700,5830])[1]),np.log(2000),1.,np.pi,1.]
        for name in self.names:
            median=float(np.median(self.yp[self.group==self.names.index(name)]))
            self.parameter_names +=[name+'_baseline_magnitude',name+'_source_fraction']
            self.lower +=[median-5,1e-5];self.upper +=[median+5,1.]
        if gp and noise_model=='calibrated_marginal_ou':
            self.parameter_names+=['log_OGLE_error_calibration_scale','OGLE_extra_noise_floor_mag']
            self.lower +=[np.log(.5),0.];self.upper +=[np.log(2.),.02]
        if gp:
            self.parameter_names+=['OGLE_correlation_fraction' if noise_model in ['native_marginal_ou','calibrated_marginal_ou'] else 'log_OGLE_GP_sigma_mag','log_OGLE_GP_tau_days']
            self.lower +=[0. if noise_model in ['native_marginal_ou','calibrated_marginal_ou'] else np.log(1e-5),np.log(.05)];self.upper +=[.95 if noise_model in ['native_marginal_ou','calibrated_marginal_ou'] else np.log(.3),np.log(100)]
        self.lower=np.array(self.lower);self.upper=np.array(self.upper)
        t0bounds=np.asarray(self.analysis_bounds.get('t0_jd_tdb',2450000.+np.array([self.lower[0],self.upper[0]])),dtype=float)
        if t0bounds.shape!=(2,) or not np.isfinite(t0bounds).all() or t0bounds[1]<=t0bounds[0]:raise ValueError('finite ordered physical t0 bounds required')
        self.time_origin_jd_tdb=float(analysis.get('numerical_time_center_jd_tdb',np.mean(t0bounds)))
        self.lower[0],self.upper[0]=t0bounds-self.time_origin_jd_tdb
        for index,name in [(1,'tE_days'),(2,'u0_heliocentric'),(4,'pi_E')]:
            if name in self.analysis_bounds:
                limits=np.asarray(self.analysis_bounds[name],dtype=float)
                if limits.shape!=(2,) or not np.isfinite(limits).all() or limits[1]<=limits[0] or (index==1 and limits[0]<=0) or (index==4 and limits[0]<0):raise ValueError('finite ordered admissible physical bounds required')
                self.lower[index],self.upper[index]=np.log(limits) if index==1 else limits
        if not np.isfinite(self.time_origin_jd_tdb):raise ValueError('finite computational time centre required')
        for name in ['theta_E_mas','relative_frame_source_parallax_mas']:
            limits=np.asarray(self.analysis_bounds.get(name,[.01,40.] if name=='theta_E_mas' else [-1.,1.]),dtype=float)
            if limits.shape!=(2,) or not np.isfinite(limits).all() or limits[1]<=limits[0] or (name=='theta_E_mas' and limits[0]<=0):raise ValueError('finite ordered angular nuisance bounds required')
        self.objective_offset=(-len(self.gp_indices)*(np.log1p(-.95)+(2*np.log(.5) if noise_model=='calibrated_marginal_ou' else 0.))) if gp and noise_model in ['native_marginal_ou','calibrated_marginal_ou'] else 0.

    def average(self,value):return np.add.reduceat(value*self.weights.reshape((-1,)+(1,)*(value.ndim-1)),self.starts,axis=0)/self.weight_sums.reshape((-1,)+(1,)*(value.ndim-1))
    def decode(self,x):
        p={'t0_jd_tdb':self.time_origin_jd_tdb+float(x[0]),'tE_days':float(np.exp(x[1])),'u0_heliocentric':float(x[2]),
           'angle_source_minus_lens_rad':float(x[3]),'pi_E':float(x[4]),'instruments':{}}
        for k,name in enumerate(self.names):p['instruments'][name]={'baseline_magnitude':float(x[5+2*k]),'source_fraction':float(x[6+2*k])}
        if self.options['gp']:
            if self.options['noise_model'] in ['native_marginal_ou','calibrated_marginal_ou']:p['gp_correlation_fraction']=float(x[-2])
            else:p['gp_sigma_mag']=float(np.exp(x[-2]))
            p['gp_tau_days']=float(np.exp(x[-1]))
            if self.options['noise_model']=='calibrated_marginal_ou':
                index=5+2*len(self.names);p['OGLE_error_calibration_scale']=float(np.exp(x[index]));p['OGLE_extra_noise_floor_mag']=float(x[index+1])
        return p

    def evaluate(self,x,*,fixed_mass=None,details=False):
        p=self.decode(x);qp=trajectory(self.tp,p,self.ep);ap=amplification(qp)
        phot=np.empty(len(self.tp))
        for k,name in enumerate(self.names):
            sub=self.group==k;v=p['instruments'][name]
            phot[sub]=v['baseline_magnitude']-MAG*np.log1p(v['source_fraction']*(ap[sub]-1))
        residual_p=self.yp-phot;white_p=residual_p/self.sp;extra=[];gp_mean=np.zeros(len(phot));gp_logdet=0.
        if self.options['gp']:
            take=self.gp_indices
            if self.options['noise_model'] in ['native_marginal_ou','calibrated_marginal_ou']:
                fraction=p['gp_correlation_fraction'];effective_sigma=self.sp[take]
                if self.options['noise_model']=='calibrated_marginal_ou':effective_sigma=np.sqrt((p['OGLE_error_calibration_scale']*self.sp[take])**2+p['OGLE_extra_noise_floor_mag']**2)
                variance_logdet=2*np.log(effective_sigma/self.sp[take]).sum()
                if fraction<=0:white=residual_p[take]/effective_sigma;logdet=variance_logdet;mean=np.zeros(len(take))
                else:
                    white,relative,normalized_mean=ou_whiten(self.tp[take],np.full(len(take),np.sqrt(1-fraction)),residual_p[take]/effective_sigma,np.sqrt(fraction),p['gp_tau_days'],True)
                    logdet=relative+len(take)*np.log1p(-fraction)+variance_logdet;mean=normalized_mean*effective_sigma
            else:white,logdet,mean=ou_whiten(self.tp[take],self.sp[take],residual_p[take],p['gp_sigma_mag'],p['gp_tau_days'],True)
            if logdet+self.objective_offset < -1e-6:raise ValueError('Gaussian determinant violates frozen optimizer-offset bound')
            white_p[take]=white;extra.append(np.sqrt(max(0.,logdet+self.objective_offset)));gp_mean[take]=mean;gp_logdet=logdet
        qa=trajectory(self.ta,p,self.ea);unit=centroid_unit(qa)
        if self.options['astrometric_lens_light']:
            ratios=[]
            for row,count in zip(self.ar,self.counts):
                instrument='HST_'+row['filter'];fraction=p['instruments'][instrument]['source_fraction']
                ratios.extend([(1-fraction)/fraction]*count)
            unit=centroid_unit(qa,np.array(ratios))
        unit=self.average(unit)
        at=self.average(self.ta[:,None])[:,0];parallax=-self.average(self.ea-self.eref)
        columns=[unit.ravel()];linear_names=['theta_E_mas']
        for axis,label in enumerate(['N','E']):
            col=np.zeros((len(self.ar),2));col[:,axis]=1;columns.append(col.ravel());linear_names.append('source_position_'+label+'_mas')
            col=np.zeros((len(self.ar),2));col[:,axis]=(at-self.ref)/YEAR;columns.append(col.ravel());linear_names.append('relative_frame_source_motion_'+label+'_mas_yr')
        columns.append(parallax.ravel());linear_names.append('relative_frame_source_parallax_mas')
        if self.options['free_filter_offsets']:
            for name in self.filters[1:]:
                mask=np.array([r['filter']==name for r in self.ar])
                for axis,label in enumerate(['N','E']):
                    col=np.zeros((len(self.ar),2));col[mask,axis]=1;columns.append(col.ravel());linear_names.append(name+'_constant_frame_offset_'+label+'_mas')
        design=np.column_stack(columns);white_design=solve_triangular(self.chol,design,lower=True,check_finite=False)
        target=solve_triangular(self.chol,self.ya,lower=True,check_finite=False)
        lower=np.full(len(columns),-np.inf);upper=np.full(len(columns),np.inf);lower[0],upper[0]=self.analysis_bounds.get('theta_E_mas',[.01,40.])
        par_index=linear_names.index('relative_frame_source_parallax_mas');lower[par_index],upper[par_index]=self.analysis_bounds.get('relative_frame_source_parallax_mas',[-1.,1.])
        if self.options['source_parallax_prior'] is not None:
            mean,sigma=self.options['source_parallax_prior']
            row=np.zeros(len(columns));row[par_index]=1/sigma
            white_design=np.vstack([white_design,row]);target=np.r_[target,mean/sigma]
        if fixed_mass is not None:
            theta=KAPPA_MAS_MSUN*fixed_mass*p['pi_E']
            if not lower[0]<=theta<=upper[0]:raise ValueError('fixed mass implies angular scale outside declared model bounds')
            target=target-white_design[:,0]*theta
            linear=np.linalg.lstsq(white_design[:,1:],target,rcond=1e-11)[0]
            if np.any(linear<lower[1:]) or np.any(linear>upper[1:]):linear=lsq_linear(white_design[:,1:],target,bounds=(lower[1:],upper[1:]),tol=1e-10).x
            linear=np.r_[theta,linear]
            target=target+white_design[:,0]*theta
        else:
            linear=np.linalg.lstsq(white_design,target,rcond=1e-11)[0]
            if np.any(linear<lower) or np.any(linear>upper):linear=lsq_linear(white_design,target,bounds=(lower,upper),tol=1e-10).x
        white_a=white_design@linear-target
        result=np.r_[white_p,white_a,extra]
        if not details:return result
        p.update(dict(zip(linear_names,map(float,linear))))
        p['mass_msun']=p['theta_E_mas']/(KAPPA_MAS_MSUN*p['pi_E']) if p['pi_E']>1e-8 else None
        p['heliocentric_relative_motion_mas_yr']=p['theta_E_mas']/p['tE_days']*YEAR
        return {'parameters':p,'photometric_predictions_magnitude':phot.tolist(),'photometric_GP_conditional_mean_mag':gp_mean.tolist(),
            'photometric_residuals_magnitude':residual_p.tolist(),'whitened_photometric_residuals':white_p.tolist(),
            'astrometric_predictions_NE_mas':(design@linear).reshape(-1,2).tolist(),
            'astrometric_residuals_NE_mas':(self.ya-design@linear).reshape(-1,2).tolist(),
            'whitened_astrometric_residuals':white_a[:len(self.ya)].tolist(),
            'objective_deviance':float(result@result-self.objective_offset),'optimization_constant_offset':float(self.objective_offset),'photometric_innovation_chi2':float(white_p@white_p),
            'astrometric_chi2':float(white_a[:len(self.ya)]@white_a[:len(self.ya)]),
            'GP_log_determinant_ratio_to_native_diagonal':gp_logdet,
            'linear_parameter_names':linear_names,'linear_active_bounds':[name for i,name in enumerate(linear_names) if min(linear[i]-lower[i],upper[i]-linear[i])<1e-6]}

    def seeds(self,starts=16):
        for k in range(starts):
            angle=-np.pi+2*np.pi*(k%8)/8;sign=1 if (k//8)%2 else -1
            guess=self.data.document.get('analysis',{}).get('initial_guess',{})
            values=[float(guess.get('t0_jd_tdb',self.time_origin_jd_tdb))-self.time_origin_jd_tdb,np.log(float(guess.get('tE_days',250.))),sign*float(guess.get('u0_absolute',.06)),angle,float(guess.get('pi_E',.1))]
            for index,name in enumerate(self.names):
                median=float(np.median(self.yp[self.group==index]));values +=[median,.05 if name=='OGLE' else .98]
            if self.options['gp'] and self.options['noise_model']=='calibrated_marginal_ou':values +=[np.log(1.),.003]
            if self.options['gp']:values +=[.1 if self.options['noise_model'] in ['native_marginal_ou','calibrated_marginal_ou'] else np.log(.01),np.log(2.)]
            yield np.clip(values,self.lower+1e-8,self.upper-1e-8)


def _safe(value):
    if isinstance(value,dict):return {k:_safe(v) for k,v in value.items()}
    if isinstance(value,(list,tuple,np.ndarray)):return [_safe(v) for v in value]
    if isinstance(value,(np.floating,float)):return float(value) if np.isfinite(value) else None
    if isinstance(value,np.integer):return int(value)
    if isinstance(value,np.bool_):return bool(value)
    return value


def residual_structure(model,detail,nfit):
    """Prospective structure screens; native data/error values are immutable.

    Bonferroni screens are approximate after estimation; parametric controls and
    blocked-night predictive checks remain separate from this diagnostic table.
    """
    ids=model.gp_indices;z=np.asarray(detail['whitened_photometric_residuals'])[ids];rows=[]
    def add(label,indices):
        sample=z[np.asarray(indices)];n=len(sample)
        if not n:return
        q=float(sample@sample);tail=None
        if n>=30:
            tail=max(min(1.,2*min(chi2.cdf(q,df),chi2.sf(q,df))) for df in [n,max(1,n-nfit)])
        rows.append({'bin':label,'count':n,'mean_whitened':float(sample.mean()),'innovation_chi2':q,'Q_per_row':q/n,'two_sided_probability_approximate_conservative':tail})
    def quartiles(label,values):
        values=np.asarray(values);edges=np.quantile(values,[.25,.5,.75]);membership=np.digitize(values,edges,right=True)
        for k in range(4):add(label+str(k+1),np.flatnonzero(membership==k))
    if len(ids):
        quartiles('native_sigma_quartile_',model.sp[ids]);quartiles('predicted_noise_free_magnitude_quartile_',np.asarray(detail['photometric_predictions_magnitude'])[ids])
        if all('seeing_pixels' in model.pr[i] for i in ids):quartiles('native_seeing_quartile_',[model.pr[i]['seeing_pixels'] for i in ids])
        years=np.floor((model.tp[ids]-2451545.)/365.25).astype(int)+2000
        for year in sorted(set(years)):add('Julian_year_'+str(year),np.flatnonzero(years==year))
        if str(model.data.document.get('data_version','')).startswith('OGLE-Mroz2022-corrected_LamLu2023v2'):
            native=np.array([model.pr[i]['native_HJD'] for i in ids]);event=(native>=2455400)&(native<=2456400)
            add('fixed_event_HJD2455400_2456400',np.flatnonzero(event));add('fixed_offevent_complement',np.flatnonzero(~event))
    eligible=[r for r in rows if r['two_sided_probability_approximate_conservative'] is not None];threshold=.01/max(1,len(eligible))
    failed=[r['bin'] for r in eligible if r['two_sided_probability_approximate_conservative']<threshold]
    lags=[float(np.corrcoef(z[:-k],z[k:])[0,1]) for k in range(1,11)] if len(z)>30 else []
    box=float(len(z)*(len(z)+2)*sum(v*v/(len(z)-k) for k,v in enumerate(lags,1))) if lags else None
    probability=float(chi2.sf(box,8 if model.options['gp'] else 10)) if box is not None else None
    return {'schema':'bhtracker.joint_residual_structure.v1','bins':rows,'familywise_screen_level':.01,'per_bin_Bonferroni_threshold':threshold,'failed_bins':failed,'screen_passed':not failed and (probability is None or probability>=.01),'OGLE_lags1_to10':lags,'Ljung_Box10_approximate':box,'Ljung_Box10_tail_probability_approximate':probability,'qualification':'Approximate postfit structure screen, not coverage calibration; blocked-night prediction and parametric controls required.'}


def fit_joint(dataset,*,starts=16,max_nfev=600,initial_states=None,**options):
    """All-row native joint likelihood with profiled linear angular nuisances."""
    model=JointModel(dataset,**options);solutions=[];reports=[]
    configuration={'requested_starts':int(starts),'max_nfev':int(max_nfev),'jacobian':'3-point','x_scale':'jac','ftol':1e-10,'xtol':1e-10,'gtol':1e-7,'initial_state_count':None if initial_states is None else len(initial_states)}
    seeds=list(model.seeds(starts)) if initial_states is None else [np.asarray(x) for x in initial_states]
    for k,seed in enumerate(seeds):
        try:
            solution=least_squares(model.evaluate,np.clip(seed,model.lower+1e-8,model.upper-1e-8),bounds=(model.lower,model.upper),
                jac='3-point',x_scale='jac',ftol=1e-10,xtol=1e-10,gtol=1e-7,max_nfev=max_nfev)
            value=float(solution.fun@solution.fun-model.objective_offset);detail=model.evaluate(solution.x,details=True)
            reports.append({'start':k,'converged':bool(solution.success),'objective_deviance':value,'nfev':int(solution.nfev),
                'optimality':float(solution.optimality),'internal_state':solution.x.tolist(),'parameters':detail['parameters']})
            if solution.success:solutions.append((value,solution,detail))
        except (ValueError,FloatingPointError,np.linalg.LinAlgError) as error:reports.append({'start':k,'converged':False,'error':str(error)})
    if not solutions:return {'schema':JOINT_RESULT_SCHEMA,'status':'JOINT_SEARCH_FAILED','experimental_validation_status':'SEARCH_FAILED','fit_configuration':configuration,'model_options':model.options,'dataset_input':model.data.document,'all_starts':reports,'input_sha256':model.data.sha256,'input_hash_algorithm':'bhtracker.canonical_numeric_json.v2','scientific_source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    solutions.sort(key=lambda row:row[0]);value,best,detail=solutions[0]
    singular=np.linalg.svd(best.jac/np.maximum(np.linalg.norm(best.jac,axis=0),1e-300),compute_uv=False)
    rank=int(np.sum(singular>singular[0]*1e-7));nlinear=len(detail['linear_parameter_names'])
    nphoto=len(model.pr);nastro=len(model.ya);nfit=len(best.x)+nlinear
    astro_dof=max(1,nastro-nlinear-5)
    diagnostics={'astrometry_chi2':detail['astrometric_chi2'],'astrometry_dof_conservative':astro_dof,
        'astrometry_chi2_tail_probability':float(chi2.sf(detail['astrometric_chi2'],astro_dof)),
        'photometry_innovation_chi2':detail['photometric_innovation_chi2'],
        'photometry_dof_approximate':max(1,nphoto-len(best.x)),
        'photometry_chi2_tail_probability_approximate':float(chi2.sf(detail['photometric_innovation_chi2'],max(1,nphoto-len(best.x)))),
        'GP_noise_inference_requires_simulation_calibration':bool(options.get('gp',False))}
    white=np.asarray(detail['whitened_photometric_residuals'])[model.gp_indices]
    diagnostics['OGLE_sorted_innovation_lag1']=float(np.corrcoef(white[:-1],white[1:])[0,1]) if len(white)>3 else None
    diagnostics['photometry_chi2_two_sided_probability_approximate']=float(min(1.,2*min(chi2.cdf(detail['photometric_innovation_chi2'],max(1,nphoto-len(best.x))),chi2.sf(detail['photometric_innovation_chi2'],max(1,nphoto-len(best.x))))))
    diagnostics['astrometry_chi2_two_sided_probability_approximate']=float(min(1.,2*min(chi2.cdf(detail['astrometric_chi2'],astro_dof),chi2.sf(detail['astrometric_chi2'],astro_dof))))
    structure=residual_structure(model,detail,nfit)
    good=diagnostics['astrometry_chi2_two_sided_probability_approximate']>=.01 and diagnostics['photometry_chi2_two_sided_probability_approximate']>=.01 and structure['screen_passed']
    return _safe({'schema':JOINT_RESULT_SCHEMA,'experimental_validation_status':'EXPERIMENTAL_RESEARCH_REQUIRES_PROFILE_AND_SYSTEMATIC_GATES','product_version':__import__('bhtracker.provenance',fromlist=['VERSION']).VERSION,'scientific_source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'status':'JOINT_MODEL_NOT_REJECTED' if good else 'JOINT_MODEL_OR_NOISE_INADEQUATE',
        'input_sha256':model.data.sha256,'input_hash_algorithm':'bhtracker.canonical_numeric_json.v2','dataset_input':model.data.document,'model_options':model.options,
        'numerical_convergence':{'converged_starts':len(solutions),'attempted_starts':len(seeds),'best_objective_deviance':value,
            'computational_time_origin_jd_tdb':model.time_origin_jd_tdb,'optimization_constant_offset':model.objective_offset,'profiled_nonlinear_rank':rank,'nonlinear_parameter_count':len(best.x),'linear_parameter_count':nlinear},
        **detail,'diagnostics':diagnostics,'residual_structure':structure,'all_starts':reports,'best_internal_state':best.x.tolist(),
        'parameter_order_internal':model.parameter_names,'fit_configuration':configuration,
        'analysis_contract':{'physical_t0_bounds_jd_tdb':(model.time_origin_jd_tdb+np.array([model.lower[0],model.upper[0]])).tolist(),'tE_bounds_days':np.exp([model.lower[1],model.upper[1]]).tolist(),'u0_heliocentric_bounds':[model.lower[2],model.upper[2]],'pi_E_bounds':[model.lower[4],model.upper[4]],'theta_E_bounds_mas':model.analysis_bounds.get('theta_E_mas',[.01,40.]),'relative_frame_source_parallax_bounds_mas':model.analysis_bounds.get('relative_frame_source_parallax_mas',[-1.,1.]),'computational_time_origin_jd_tdb':model.time_origin_jd_tdb},'mass_status':('MASS_UNIDENTIFIED_BOUNDARY' if best.x[4]<1e-6 or detail['linear_active_bounds'] else 'PROFILE_AND_SYSTEMATICS_REQUIRED'),
        'nonlinear_active_bounds':[name for i,name in enumerate(model.parameter_names) if name!='angle_source_minus_lens_rad' and min((best.x[i]-model.lower[i])/(model.upper[i]-model.lower[i]),(model.upper[i]-best.x[i])/(model.upper[i]-model.lower[i]))<1e-5],
        'unavailable':{'absolute_lens_proper_motion':None,'absolute_source_parallax':None,'lens_distance_pc':None,'horizon':None,'core_state':None},
        'bhsm_interpretation':{'framework':'BHSM','one_potential_rule':'One ordinary compact-lens optical potential counted once; no extra core or envelope term.',
            'luminous_lens_sensitivity':'If enabled, ALL non-source HST flux is assigned to lens as limiting assumption. Blend location is not supplied by photometry.',
            'scope':'Conditional mass from independently modeled thetaE and photometric parallax. No horizon, core state, membrane radius or new-discovery claim.'},
        'noise_contract':'Native reported magnitude errors remain immutable in input/export. Native_marginal_ou uses C=S[(1-f)I+fK]S with S=native sigma. Calibrated_marginal_ou explicitly estimates S_i=sqrt(k^2*sigma_native_i^2+s^2) as a separate calibration hypothesis with full determinant; it never labels effective errors supplied. Angular covariance/jitter sensitivities are assumptions. Additive_ou is archived diagnostic comparison only.',
        'constants':{'kappa_mas_per_msun':KAPPA_MAS_MSUN,'kappa_basis':'IAU2015 nominal solar GM; exact c and AU; angular units mas'},
        'source_frame_contract':'Source position, proper motion and apparent parallax are nuisance coordinates of the published relative frame. Absolute PM/distance require independently supplied calibration.'})


def profile_joint_mass(dataset,result,masses,*,max_nfev=600,mode_limit=8):
    """Retain competing admitted modes; unresolved searches never define limits."""
    if result['input_sha256']!=_hash(dataset.document if isinstance(dataset,JointData) else dataset):raise ValueError('joint profile input differs')
    model=JointModel(dataset,**result['model_options']);reference=result['objective_deviance']
    candidates=sorted([r for r in result['all_starts'] if r.get('converged')],key=lambda r:r['objective_deviance'])
    modes=[]
    for row in candidates:
        x=np.asarray(row['internal_state'])
        distances=[]
        for m in modes:
            difference=(x-m)/np.maximum(1,np.abs(m));difference[3]=np.arctan2(np.sin(x[3]-m[3]),np.cos(x[3]-m[3]))
            distances.append(np.linalg.norm(difference))
        if not any(distance<.03 for distance in distances):modes.append(x)
        if len(modes)>=mode_limit:break
    rows=[]
    for mass in masses:
        mass=float(mass)
        if not .05<=mass<=200:raise ValueError('profile mass outside separately declared .05..200 solar-mass range')
        lower=model.lower.copy();upper=model.upper.copy()
        theta_limits=model.analysis_bounds.get('theta_E_mas',[.01,40.])
        lower[4]=max(lower[4],(theta_limits[0]+1e-7)/(KAPPA_MAS_MSUN*mass));upper[4]=min(upper[4],(theta_limits[1]-1e-7)/(KAPPA_MAS_MSUN*mass))
        solutions=[]
        for seed in modes:
            try:
                solved=least_squares(lambda x:model.evaluate(x,fixed_mass=mass),np.clip(seed,lower+1e-8,upper-1e-8),
                    bounds=(lower,upper),jac='3-point',x_scale='jac',max_nfev=max_nfev,ftol=1e-9,xtol=1e-9,gtol=1e-7)
                if solved.success:solutions.append((float(solved.fun@solved.fun-model.objective_offset),solved))
            except (ValueError,FloatingPointError,np.linalg.LinAlgError):pass
        if not solutions:rows.append({'mass_msun':mass,'status':'SEARCH_UNRESOLVED','delta_deviance':None,'interval_eligible':False});continue
        score,solution=min(solutions,key=lambda row:row[0]);state=model.evaluate(solution.x,fixed_mass=mass,details=True)
        reference_valid=score>=reference-1e-3
        active=[name for i,name in enumerate(model.parameter_names) if name!='angle_source_minus_lens_rad' and min((solution.x[i]-lower[i])/(upper[i]-lower[i]),(upper[i]-solution.x[i])/(upper[i]-lower[i]))<1e-5]
        physical=[name for name in active if (name.endswith('_source_fraction') and solution.x[model.parameter_names.index(name)]>.99999) or (name in ['OGLE_correlation_fraction','OGLE_extra_noise_floor_mag'] and solution.x[model.parameter_names.index(name)]<1e-5)]
        numerical=[name for name in active if name not in physical]
        boundary=bool(numerical or state['linear_active_bounds'])
        valid=reference_valid and not boundary
        rows.append({'mass_msun':mass,'status':('REFERENCE_MINIMUM_UNRESOLVED' if not reference_valid else 'BOUNDARY_LIMITED' if boundary else 'ADMITTED_NONREGULAR_PHYSICAL_BOUNDARY' if physical else 'ADMITTED_LOCAL_PROFILE'),
            'objective_deviance':score,'delta_deviance':max(0.,score-reference) if reference_valid else None,
            'nonlinear_active_bounds':active,'linear_active_bounds':state['linear_active_bounds'],'physical_nuisance_boundaries':physical,'regular_asymptotic_interval':valid and not physical,
            'interval_eligible':valid,'parameters':state['parameters'],'internal_state':solution.x.tolist(),'converged_modes':len(solutions)})
    return {'schema':'bhtracker.joint_mass_profile.v2','reference_objective_deviance':reference,'rows':rows,
            'configuration':{'max_nfev':int(max_nfev),'mode_limit':int(mode_limit),'retained_modes':len(modes)},'coverage_claim':False,'qualification':'Local multistart profile including all retained modes. Finite endpoints are not limits. Unresolved rows interrupt crossing brackets; model/noise and systematic checks remain separate.'}
