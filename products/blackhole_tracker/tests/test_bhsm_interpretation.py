from copy import deepcopy
from decimal import Decimal, localcontext
import json
import hashlib
from pathlib import Path
import numpy as np
import pytest
from bhtracker import fit
from bhtracker.examples import make_example
from bhtracker.forward import C,GM_SUN,PC
from bhtracker.interpretation import spherical_boundary,bhsm_interpretation
from bhtracker.report import report_html


def _input_value_sha256(value):
    # GUI JSON writes integral floats as integers. Compare supplied values
    # without confusing that serialization difference with a data change.
    def canonical(item):
        if isinstance(item,bool) or item is None or isinstance(item,str):return item
        if isinstance(item,(int,float)):return ['number',str(Decimal(str(item)).normalize())]
        if isinstance(item,list):return ['array',[canonical(v) for v in item]]
        return ['object',[[k,canonical(v)] for k,v in sorted(item.items())]]
    return hashlib.sha256(json.dumps(canonical(value),separators=(',',':')).encode()).hexdigest()


def test_boundary_map_has_the_same_mass_at_different_enclosing_radii():
    mass=1e5
    radii=[1e-5,.01,100.]
    energies=[]
    for radius in radii:
        actual=spherical_boundary(mass,radius,2.)
        with localcontext() as ctx:
            ctx.prec=65
            m=Decimal(str(GM_SUN))*Decimal(str(mass))/(Decimal(str(C))**2*Decimal(str(PC)))
            r=Decimal(str(radius))
            expected=(1-(1-2*m/r).sqrt())/r
        assert actual['curvature_deficit_pc_inverse']==pytest.approx(float(expected),rel=2e-15)
        assert actual['reconstructed_monopole_msun']==pytest.approx(mass,rel=2e-15)
        energies.append(actual['boundary_energy_over_Msun_c2'])
    assert energies[0]>energies[1]>energies[2]


def test_boundary_errors_are_fixed_radius_pushforwards():
    mass=1e5;radius=1e-5;step=.1
    actual=spherical_boundary(mass,radius,3.)
    plus=spherical_boundary(mass+step,radius);minus=spherical_boundary(mass-step,radius)
    for value,error in [('boundary_energy_over_Msun_c2','boundary_energy_sigma_over_Msun_c2'),
                        ('curvature_deficit_pc_inverse','curvature_deficit_sigma_pc_inverse')]:
        derivative=(plus[value]-minus[value])/(2*step)
        assert actual[error]==pytest.approx(3*derivative,rel=2e-8)


@pytest.mark.parametrize('mass,radius',[(0,1),(1,0),(float('nan'),1),(1,float('inf')),(1e12,1e-10)])
def test_boundary_rejects_invalid_static_geometry(mass,radius):
    with pytest.raises(ValueError):spherical_boundary(mass,radius)


def test_gr_fit_is_preserved_and_has_its_bhsm_interpretation():
    raw,_=make_example('nearby_motion');original=deepcopy(raw)
    result=fit(raw,starts=2)
    stored=json.loads((Path(__file__).resolve().parent/'fixtures/pre_interpretation_fit.json').read_text())
    np.testing.assert_allclose(result['predictions'],stored['predictions'],rtol=2e-11,atol=1e-12)
    assert result['estimates']['mass_msun']==pytest.approx(stored['estimates']['mass_msun'],rel=2e-11)
    assert result['chi2']==pytest.approx(stored['chi2'],rel=2e-11,abs=1e-12)
    for parameter,value in stored['estimates'].items():
        np.testing.assert_allclose(result['estimates'][parameter],value,rtol=2e-11,atol=1e-12)
    assert result['status']==stored['status']=='TRACKED'
    scientific=json.loads((Path(__file__).resolve().parent/'fixtures/pre_core_surface_scientific_summary.json').read_text())
    assert _input_value_sha256(raw)==scientific['input_value_sha256']
    assert result['analysis_configuration']==scientific['configuration']
    assert result['dof']==scientific['dof'] and result['rank']==scientific['rank']
    assert result['goodness_of_fit_p']==pytest.approx(scientific['goodness_of_fit_p'],rel=2e-11,abs=1e-12)
    for parameter,value in scientific['uncertainty'].items():
        # v2 changes only the numerical derivative basis. Independent symmetric
        # steps 1e-6..8e-6 give a 6.7e-11 mass-sigma spread and 5.4e-10 motion
        # covariance spread; 2e-11 was below that finite-difference resolution.
        # Physical predictions, mass, admission and fixture bytes retain their
        # original checks above; only this historical local-covariance check
        # uses the separately justified numerical tolerance.
        np.testing.assert_allclose(result['uncertainty'][parameter],value,rtol=1e-9,atol=1e-12)
    np.testing.assert_allclose(result['proper_motion_covariance'],scientific['proper_motion_covariance'],rtol=1e-9,atol=1e-12)
    assert raw==original
    meaning=result['bhsm_interpretation']
    repository='https://github.com/ncarberry64/Berger-Hopf-Standard-Model'
    assert meaning['project_citation']==result['software_provenance']['project_citation']
    assert meaning['project_citation']['repository_url']==repository
    assert meaning['source_provenance']['formal_repository_url']==repository
    assert f'href="{repository}"' in report_html(result)
    assert meaning['framework']=='BHSM' and meaning['spherical_boundary']['status']=='AVAILABLE'
    assert meaning['spherical_boundary']['reconstructed_monopole_msun']==pytest.approx(result['estimates']['mass_msun'])
    assert meaning['interpretation_schema_version']==2
    assert meaning['core_surface']['status']=='PROPOSED_NOT_INFERRED'
    assert meaning['core_surface']['core_parameters_fitted'] is False
    assert meaning['core_surface']['new_optical_term_added'] is False
    for quantity in meaning['core_surface']['unavailable_quantities'].values():
        assert quantity['status']=='NOT_INFERRED' and quantity['value'] is None
    assert 'BHSM interpretation' in report_html(result)


def test_r1_mass_is_not_silently_given_schwarzschild_boundary_energy():
    meaning=bhsm_interpretation('r1',{'mass_msun':1e5},{'mass_msun':3.},{'r0_pc':.01},'TRACKED')
    assert meaning['spherical_boundary']['status']=='NOT_ASSUMED_FOR_R1_METRIC'
    assert 'Action metric/source' in meaning['parameter_meanings'][0]['interpretation']


def test_failed_mass_fit_does_not_export_an_interpreted_boundary_measurement():
    for status in ['FIT_REJECTED','INSUFFICIENT_INFORMATION']:
        meaning=bhsm_interpretation('gr',{'mass_msun':1e5},{'mass_msun':3.},{'r0_pc':.01},status)
        assert meaning['spherical_boundary']['status']!='AVAILABLE'


def test_interpretation_contract_is_hash_pinned_and_returned_without_shared_state():
    import hashlib
    first=bhsm_interpretation('gr')
    manifest=first['source_provenance']
    entry=next(item for item in manifest['sources'] if item['path']==manifest['interpretation_contract_path'])
    base=Path(__file__).resolve().parents[1]/'bhtracker/theory'
    assert hashlib.sha256((base/entry['path']).read_bytes()).hexdigest()==entry['sha256']
    contract=json.loads((base/entry['path']).read_text(encoding='utf8'))
    assert first['core_surface']==contract
    first['core_surface']['unavailable_quantities']['core_mode_data']['value']='mutated copy'
    first['source_provenance']['sources'].clear()
    second=bhsm_interpretation('r1')
    assert second['core_surface']==contract and second['source_provenance']['sources']
