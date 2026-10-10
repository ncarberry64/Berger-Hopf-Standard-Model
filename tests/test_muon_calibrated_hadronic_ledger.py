import json
import math
from pathlib import Path

import numpy as np
import pytest

from bhsm.interface.muon_calibrated_hadronic_ledger import (
    PINNED, _pinned, central_log_derivative, coherent_spectral_sum, primitive_gradient,
)

ROOT=Path(__file__).resolve().parents[1]


def test_shared_signed_rows_cancel_before_norm():
    rows=[dict(value=3.,statistical_error_vector=[1.,2.],systematic_error_vector=[4.]),
          dict(value=-1.,statistical_error_vector=[-.5,-2.],systematic_error_vector=[-3.])]
    result=coherent_spectral_sum(rows)
    assert result['value']==2
    assert result['statistical_vector']==[.5,0.]
    assert result['systematic_vector']==[1.]
    assert result['standard_uncertainty']==pytest.approx(math.sqrt(1.25))


@pytest.mark.parametrize('bad',[
    [],[dict(value=math.nan,statistical_error_vector=[0.],systematic_error_vector=[0.])],
    [dict(value=0.,statistical_error_vector=[math.inf],systematic_error_vector=[0.])],
    [dict(value=0.,statistical_error_vector=[0.],systematic_error_vector=[0.]),
     dict(value=0.,statistical_error_vector=[0.,0.],systematic_error_vector=[0.])],
])
def test_no_misaligned_or_nonfinite_error_rows(bad):
    with pytest.raises(ValueError):
        coherent_spectral_sum(bad)


def test_log_derivative_refines_true_mass_dependence():
    result=central_log_derivative(lambda m: m**3+.3*math.log(m),.11)
    exact=3*.11**2+.3/.11
    assert result['value']==pytest.approx(exact,rel=1e-9)
    assert result['absolute_refinement_difference']>0
    with pytest.raises(ValueError):
        central_log_derivative(lambda m:float('nan'),.11)


def test_mass_and_alpha_dependencies_share_the_retained_primitive():
    config,_=_pinned(ROOT,'config')
    result=np.array(primitive_gradient(config,derivative_alpha=7.,derivative_muon=3.,
                                       derivative_electron=-2.,derivative_tau=5.))
    jac=np.asarray(config['uncertainty_and_correlations']['consumer_vs_primitive_jacobian'])
    inverse=config['primary_measurements']['alpha_inverse_0']['value']
    expected=3*jac[3]-2*jac[4]+5*jac[2]
    expected[0]-=7/inverse**2
    np.testing.assert_allclose(result,expected,rtol=0,atol=0)
    assert result[3]==0 and result[4]==0
    assert result[5]==5


def test_frozen_physical_centers_and_shared_rows_are_retained():
    lo,_=_pinned(ROOT,'LO'); nlo,_=_pinned(ROOT,'NLO'); nnlo,_=_pinned(ROOT,'NNLO')
    result=coherent_spectral_sum([lo['LO_HVP'],nlo['application']['NLO_HVP'],
                                  nnlo['application']['NNLO_HVP']])
    assert result['value']==6.883273877717739e-8
    assert result['standard_uncertainty']==pytest.approx(3.9322964803041445e-10,rel=1e-14)
    for name in ['LO','NLO','NNLO']:
        path=PINNED[name][0]
        assert (ROOT/path).read_bytes()==(ROOT/path.replace('/run_3/','/run_4/')).read_bytes()


def test_pinned_receipt_rejects_a_changed_input(tmp_path):
    target=tmp_path/PINNED['HLbL'][0]
    target.parent.mkdir(parents=True)
    target.write_text(json.dumps({'projected_value':0}))
    with pytest.raises(ValueError,match='identity mismatch'):
        _pinned(tmp_path,'HLbL')
