"""Reproducible synthetic examples; their truth is never passed to fit()."""
from pathlib import Path
import copy
import json
import numpy as np
from .data import load_dataset,FIELDS
from .forward import LensEngine

TITLES={'nearby_motion':('Nearby compact-mass track','Resolved synthetic primary pairs with measurable center motion.'),
        'cosmological_short_track':('Short cosmological track','A mass measurement with deliberately weak ten-year motion information.'),
        'ordinary_shear':('Ordinary-shear control','A conventional external shear; compare fits with and without shear.'),
        'stellar_benchmark':('Published-parameter stellar benchmark','Synthetic local point lens inspired by BAGLE Table 2; supplied observer factors, no observed claim.')}

def example_names():return [{'id':k,'title':v[0],'description':v[1]} for k,v in TITLES.items()]

def make_example(name='nearby_motion',seed=20261021,noise=True):
    if name not in TITLES:raise ValueError('unknown example')
    stellar=name=='stellar_benchmark';cosmic=name=='cosmological_short_track'
    if stellar:
        mass=7.4;geometry={'D_l_pc':1000/.275,'D_s_pc':8000.,'D_ls_pc':8000-1000/.275,'z_l':0.,'z_s':0.}
        epochs=2015.+np.linspace(-.13,.13,13);t0=2015.
        center=[.4,-.3];motion=[-26.52,0.]
        sig=[.015,.015,.015,.015,.01,1e-6]
    else:
        mass=1e9 if cosmic else 1e5
        geometry=({'D_l_pc':945162839.37304,'D_s_pc':1689312239.6872935,'D_ls_pc':1076994348.059601,'z_l':.3,'z_s':1.} if cosmic else
                  {'D_l_pc':1e6,'D_s_pc':1e9,'D_ls_pc':999e6,'z_l':.000225,'z_s':.3})
        epochs=np.repeat([2015.,2020.,2025.],3);t0=2020.
        center=[.8,-.6];motion=[.00005,-.00003] if cosmic else [.065,-.038]
        sig=[.2,.2,.2,.2,.01,60.] if cosmic else [.02,.02,.02,.02,.005,.0003]
    n=len(epochs)
    raw={'schema_version':1,'title':TITLES[name][0],'fields':FIELDS,'geometry':geometry,
       'reference_epoch_yr':t0,'epochs_yr':epochs.tolist(),'observations':np.tile([1.,.2,-1.,-.2,1.,1.],(n,1)).tolist(),
       'covariance':np.diag(np.tile(np.array(sig)**2,n)).tolist(),
       'analysis':{'reference_mass_msun':mass,'source_policy':'free_per_epoch','r0_pc':1e-4 if not cosmic else 10.,
                   'flux_ratio':1.,'flux_provenance':'regular_body_proxy'},
       'provenance':{'kind':'synthetic','seed':seed,'noise_added':noise,
          'description':'Declared measurement errors are experimental inputs, not an instrument forecast or detection.'}}
    if stellar:
        phase=2*np.pi*(epochs-t0)
        raw['analysis']['lens_parallax_factors']=np.column_stack([np.cos(phase)-1,.4*np.sin(phase)]).tolist()
        raw['analysis']['r0_pc']=1e-8
        raw['provenance']['parameter_reference']='Lu et al. arXiv:2512.03364 Table 2; Table-derived synthetic variation, not BAGLE output or observed data'
        raw['provenance']['observer_factors']='explicit synthetic ellipse; no Earth ephemeris or BAGLE parallax convention is claimed'
    engine=LensEngine(load_dataset(raw))
    if stellar:
        sources=np.column_stack([.4+10*(epochs-t0),-.3+np.full(n,.3*3.)])
    else:
        # Three distinct, stationary background source coordinates sampled at
        # each of three epochs. No million-year source/lens scan is implied.
        base=np.array([[.65,.55],[-.75,.6],[1.1,-.45]])*engine.theta
        sources=np.tile(base,(3,1))+np.array(center)
    truth={'mass_msun':mass,'center_mas':center,'proper_motion_mas_yr':motion,
           'source_mas':sources.tolist(),'shear':[.03,-.018] if name=='ordinary_shear' else [0.,0.],
           'compact_quad':[0.,0.],'convergence':0.,'flux_ratio':1.}
    exact,branch=engine.calculate(truth)
    # A declared correlated covariance, including cross-epoch timing and
    # astrometric reference errors. It is supplied in full, not diagonalized.
    sd=np.tile(np.array(sig),n);corr=np.eye(6*n)
    v=np.zeros(6*n);v[::6]=1.;v[2::6]=1.
    corr+=.08*np.outer(v,v)
    v=np.zeros(6*n);v[5::6]=1.;corr+=.04*np.outer(v,v)
    cov=corr*np.outer(sd,sd)
    rng=np.random.default_rng(seed)
    observed=exact+(np.linalg.cholesky(cov)@rng.normal(size=6*n)).reshape(n,6) if noise else exact
    raw['observations']=observed.tolist();raw['covariance']=cov.tolist()
    return raw,truth

def save_examples(directory):
    target=Path(directory);target.mkdir(parents=True,exist_ok=True)
    for name in TITLES:
        raw,truth=make_example(name)
        (target/f'{name}.json').write_text(json.dumps(raw,indent=2)+'\n',encoding='utf8')
        (target/f'{name}.truth.json').write_text(json.dumps(truth,indent=2)+'\n',encoding='utf8')
