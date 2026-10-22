import numpy as np
from bhtracker.examples import make_example
from bhtracker import fit,predict
from bhtracker.forward import LensEngine

def test_exported_full_nuisance_preserves_its_reference_basis():
    raw,_=make_example('nearby_motion')
    raw['analysis'].pop('reference_mass_msun',None)
    result=fit(raw,nuisance='full',starts=1)
    pars=result['_internal']['parameters']
    assert pars['reference_mass_msun']==result['model']['reference_mass_msun']
    np.testing.assert_allclose(predict(raw,pars),result['predictions'],rtol=1e-12,atol=1e-12)

def test_implicit_worldtube_matches_propagation_configuration():
    raw,_=make_example('nearby_motion')
    raw['analysis'].pop('r0_pc',None)
    engine=LensEngine(raw,'r1')
    assert engine.physics_config['analysis']['r0_pc']==engine.r0
    assert 'r0_pc' not in raw['analysis']
