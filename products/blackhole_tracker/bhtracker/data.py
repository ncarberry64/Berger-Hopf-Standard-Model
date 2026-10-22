"""Versioned measurements and full covariance, always in stated physical units."""
from dataclasses import dataclass
from pathlib import Path
import copy
import hashlib
import json
import numpy as np
from scipy.linalg import cholesky, solve_triangular

FIELDS=['x_plus_mas','y_plus_mas','x_minus_mas','y_minus_mas','ln_flux_ratio','delay_seconds']

def _unique_object(pairs):
    result={}
    for key,value in pairs:
        if key in result:raise ValueError(f'JSON contains duplicate field {key!r}; supply each field once')
        result[key]=value
    return result

def read_json(text):
    """The same strict JSON parser for files, HTTP and replay inputs."""
    def invalid(value):raise ValueError(f'JSON contains {value}; replace nonfinite values with calibrated finite numbers')
    try:return json.loads(text,object_pairs_hook=_unique_object,parse_constant=invalid)
    except json.JSONDecodeError as error:
        raise ValueError(f'JSON line {error.lineno}, column {error.colno}: {error.msg}') from error

def _finite_number(value,label,positive=False):
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not np.isfinite(value):
        raise ValueError(f'{label} must be a finite number in the documented units')
    if positive and value<=0:raise ValueError(f'{label} must be positive and finite')
    return value

def _array(value,label):
    # Inspect supplied cells before NumPy can coerce True or "1.0" into data.
    # Object conversion preserves those distinctions for mixed JSON lists and
    # still accepts real integer/float NumPy arrays through the Python API.
    try:supplied=np.asarray(value,dtype=object)
    except (TypeError,ValueError,OverflowError) as error:
        raise ValueError(f'{label} must be a rectangular numeric array') from error
    for index,cell in np.ndenumerate(supplied):
        if isinstance(cell,(list,tuple,np.ndarray)):
            raise ValueError(f'{label} must be a rectangular numeric array')
        if isinstance(cell,(bool,np.bool_)) or not isinstance(cell,(int,float,np.integer,np.floating)):
            location=', '.join(f'{name} {int(v)+1}' for name,v in zip(('row','column'),index))
            raise ValueError(f'{label} {location} must be numeric; supply a real number, not a boolean or string')
    try:array=np.asarray(supplied,dtype=float)
    except (TypeError,ValueError,OverflowError) as error:
        raise ValueError(f'{label} must contain representable real numeric values') from error
    bad=np.argwhere(~np.isfinite(array))
    if len(bad):
        index=bad[0]
        location=', '.join(f'{name} {int(v)+1}' for name,v in zip(('row','column'),index))
        raise ValueError(f'{label} {location} must be finite; replace the invalid value using your calibration')
    return array

@dataclass
class Dataset:
    raw: dict
    epochs: np.ndarray
    observations: np.ndarray
    covariance: np.ndarray
    chol: np.ndarray
    sha256: str

    @property
    def n(self): return len(self.epochs)
    @property
    def geometry(self): return self.raw['geometry']
    @property
    def analysis(self): return self.raw.get('analysis',{})
    @property
    def t0(self): return self.raw['reference_epoch_yr']
    def whiten(self,values): return solve_triangular(self.chol,np.asarray(values),lower=True)
    def summary(self):
        return {'rows':self.n,'fields':FIELDS,'reference_epoch_yr':self.t0,
                'span_observer_years':float(np.ptp(self.epochs)),
                'provenance':self.raw['provenance'],'sha256':self.sha256,
                'covariance':'full supplied positive-definite covariance; row order preserved',
                'input_contract':{'positions':'mas in one supplied absolute tangent-plane frame',
                    'epochs':'observer-frame Julian years (365.25 days); repeated and unsorted rows retained',
                    'image_labels':'+ is positive parity; - is negative parity, not bright/faint labels',
                    'ln_flux_ratio':'natural log of positive-parity / absolute negative-parity magnification, after supplied corrections for non-lensing flux effects',
                    'delay_seconds':'negative-parity arrival minus positive-parity arrival, observer seconds; Gaussian measurement noise may cross zero',
                    'distances':'supplied angular-diameter distances in pc; local z_l=z_s=0 also supported; no cosmology inferred',
                    'source':'free position per row; frame, time, image association and calibrations supplied',
                    'provenance':'a declaration, not authentication of an observation'}}

def load_dataset(source):
    if isinstance(source,Dataset): return source
    raw=read_json(Path(source).read_text(encoding='utf-8-sig')) if isinstance(source,(str,Path)) else copy.deepcopy(source)
    if not isinstance(raw,dict) or isinstance(raw.get('schema_version'),(bool,np.bool_)) or raw.get('schema_version')!=1:
        raise ValueError('schema_version must be 1')
    geometry=raw.get('geometry',{})
    if not isinstance(geometry,dict):raise ValueError('geometry must be an object containing distances in pc and redshifts')
    for key in ['D_l_pc','D_s_pc','D_ls_pc']:
        v=geometry.get(key)
        _finite_number(v,f'geometry.{key}',positive=True)
    for key in ['z_l','z_s']:
        v=geometry.get(key)
        _finite_number(v,f'geometry.{key}')
        if v<0:raise ValueError(f'geometry.{key} must be nonnegative and finite')
    if geometry['z_s']<=geometry['z_l'] and not geometry['z_l']==geometry['z_s']==0:
        raise ValueError('source redshift must exceed lens redshift, or both may be zero for supplied local distances')
    epochs=_array(raw.get('epochs_yr',[]),'epochs_yr')
    obs=_array(raw.get('observations',[]),'observations')
    if epochs.ndim!=1 or not 3<=len(epochs)<=80:raise ValueError('provide 3 to 80 epoch/source rows')
    if obs.shape!=(len(epochs),6):raise ValueError('observations must have six fields per row, in the documented order')
    coincident=np.flatnonzero(np.linalg.norm(obs[:,:2]-obs[:,2:4],axis=1)==0)
    if len(coincident):raise ValueError(f'observations row {coincident[0]+1}: primary images must be separated; check parity labels and image association')
    t0=raw.get('reference_epoch_yr')
    _finite_number(t0,'reference_epoch_yr')
    covariance=_array(raw.get('covariance',[]),'covariance')
    n=6*len(epochs)
    if covariance.shape!=(n,n):raise ValueError(f'covariance must be a finite 6N by 6N matrix: expected {n} rows and {n} columns, received {covariance.shape}; use the canonical six fields within each input row')
    # Compare symmetry in correlation units, avoiding mixed mas/second scales.
    bad=np.flatnonzero(np.diag(covariance)<=0)
    if len(bad):raise ValueError(f'covariance variances must be positive: diagonal row/column {bad[0]+1} is invalid; supply its calibrated variance')
    scale=np.sqrt(np.diag(covariance));corr=covariance/np.outer(scale,scale)
    asym=abs(corr-corr.T)
    if np.max(asym)>1e-9:
        i,j=np.unravel_index(np.argmax(asym),asym.shape)
        raise ValueError(f'covariance must be symmetric: row {i+1}, column {j+1} differs from its transpose by {asym[i,j]:.3g} in correlation units (tolerance 1e-9); correct the supplied covariance, retaining correlations')
    covariance=(covariance+covariance.T)/2
    try:chol=cholesky(covariance,lower=True)
    except np.linalg.LinAlgError as error:raise ValueError(f'covariance must be positive definite: {error}; check dependent/duplicated measurements and calibrated cross-covariances; no diagonal replacement is applied') from error
    provenance=raw.get('provenance',{})
    if not isinstance(provenance,dict):raise ValueError('provenance must be an object with kind synthetic or observed')
    if provenance.get('kind') not in ['synthetic','observed']:raise ValueError('provenance.kind must explicitly be synthetic or observed')
    if raw.get('fields',FIELDS)!=FIELDS:raise ValueError('field order differs from the six-field contract')
    analysis=raw.setdefault('analysis',{})
    if not isinstance(analysis,dict):raise ValueError('analysis must be an object containing supplied model assumptions')
    if 'lens_parallax_factors' in analysis:
        pf=_array(analysis['lens_parallax_factors'],'analysis.lens_parallax_factors')
        if pf.shape!=(len(epochs),2) or not np.all(np.isfinite(pf)):
            raise ValueError('lens_parallax_factors must contain N finite two-vectors')
    if analysis.get('source_policy','free_per_epoch')!='free_per_epoch':raise ValueError('this version supports source_policy=free_per_epoch')
    for key in ['r0_pc','reference_mass_msun','compact_quad_reference_mass_msun']:
        if key in analysis:_finite_number(analysis[key],f'analysis.{key}',positive=True)
    if 'mass_bounds_msun' in analysis:
        mb=_array(analysis['mass_bounds_msun'],'analysis.mass_bounds_msun')
        if mb.shape!=(2,) or not np.all(np.isfinite(mb)) or not 0<mb[0]<mb[1]:
            raise ValueError('mass_bounds_msun must be two increasing positive finite masses')
    digest=hashlib.sha256(json.dumps(raw,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
    return Dataset(raw,epochs,obs,covariance,chol,digest)
