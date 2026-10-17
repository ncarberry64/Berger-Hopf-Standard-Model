from pathlib import Path
import json
import numpy as np
import pytest
from bhsm.interface.muon_coupled_tensor_decay_rate import (tensor_tree_decay_rate,
    temporal_charged_current_series,conditional_decay_unit,tensor_rate_tail_estimate)
from bhsm.interface.muon_coupled_lorentz_radial_green import coupled_radial_trace_application
from bhsm.interface.muon_static_coupled_charged_current import static_coupled_charged_current
ROOT=Path(__file__).resolve().parents[1]


def actual(side):
    folder=ROOT/'artifacts/muon_coupled_lorentz_field_symbol_20261011/run_1'
    md=json.loads((folder/'result.json').read_bytes())
    r=next(r for r in md['records']if r['side']==side)
    with np.load(folder/'application.npz',allow_pickle=False)as a:
        data=[a[side+'_'+k].copy()for k in('proper_frequency_coefficients','field_quotient_lift','joint_trace_map','scalar_radial_source','central_radial_frame_rows')]
        raw=a[side+'_raw_fields'];h=raw[-8:-4];H=h[:2]+1j*h[2:]
    zero=coupled_radial_trace_application(*data,frequency=0)
    current=static_coupled_charged_current(zero['joint_wall_Green'],H,radius=r['radius'],lapse=r['lapse'],family=1,out_family=2)
    return data,current


def test_massive_VA_spin_sums_match_analytic_decay_with_both_muon_charges():
    _,a=actual('incoming')
    for charge in(-1,1):
        r=tensor_tree_decay_rate(a['VA_template'],muon_mass_GeV=.10565842526040435,
            electron_mass_GeV=.000510998950905377,radial_order=24,muon_charge=charge)
        assert abs(r['tree_rate_coefficient_GeV5']/r['VA_unit_coefficient_analytic_rate']-1)<3e-13
        assert r['maximum_spin_sum_imaginary_residual']<1e-18
    # The integrated massive phase is not the massless approximation.
    assert 0<1-r['exact_massive_VA_phase_factor']<.001


def test_actual_full_tensor_rate_retains_nonVA_terms_and_cross_family_Yukawas():
    _,a=actual('outgoing')
    kwargs=dict(muon_mass_GeV=.10565842526040435,electron_mass_GeV=.000510998950905377)
    full=tensor_tree_decay_rate(a['full_charged_current_tensor'],radial_order=24,**kwargs)
    refined=tensor_tree_decay_rate(a['full_charged_current_tensor'],radial_order=48,angular_order=4,**kwargs)
    va=tensor_tree_decay_rate(a['VA_projection_coefficient']*a['VA_template'],radial_order=24,**kwargs)
    assert abs(full['tree_rate_coefficient_GeV5']/refined['tree_rate_coefficient_GeV5']-1)<2e-12
    assert full['tree_rate_coefficient_GeV5']>100*va['tree_rate_coefficient_GeV5']
    assert np.linalg.norm(a['scalar_scalar_tensor'])>0
    assert np.linalg.norm(a['literal_left_minus_vertex_adjoint'])>0
    assert np.array_equal(a['out_family_indices'],[4,5,10,11,16,17])
    scale=conditional_decay_unit(full['tree_rate_coefficient_GeV5'],lifetime_seconds=2.1969803e-6,hbar_GeV_seconds=6.582119569509066e-25)
    assert abs(scale['reconstructed_rate_GeV']/scale['measured_rate_GeV']-1)<5e-15
    assert not scale['physical_unit_selected']


def test_nonnormal_temporal_source_series_uses_grouped_square_and_matches_direct_action():
    data,a=actual('outgoing');maximum=.0026
    s=temporal_charged_current_series(*data[:3],a['charged_current_right_vertices'],a['charged_current_left_vertices'],maximum_frequency=maximum)
    assert s['grouped_square_norm_estimate']<.01
    assert maximum*np.linalg.norm(s['temporal_operator_X_coefficients'][0],2)>1
    for z in(-maximum,.4*maximum,maximum):
        direct=coupled_radial_trace_application(*data,frequency=z)
        literal=np.einsum('aij,ab,bkl->ijkl',a['charged_current_right_vertices'],direct['joint_wall_Green'],a['charged_current_left_vertices'])
        polynomial=np.einsum('k,kabcd->abcd',z**np.arange(len(s['temporal_current_coefficients'])),s['temporal_current_coefficients'])
        assert np.linalg.norm(literal-polynomial)<s['uniform_tensor_series_tail_estimate']+3e-12
    changed=data[1].astype(complex)
    with pytest.raises(ValueError,match='must be real'):
        temporal_charged_current_series(data[0],changed,data[2],a['charged_current_right_vertices'],a['charged_current_left_vertices'],maximum_frequency=maximum)


def test_rate_tail_converts_uniform_source_error_and_rejects_unowned_operands():
    r=tensor_rate_tail_estimate(1e-12,1e-8,muon_mass_GeV=.1057)
    assert 0<r['tail_squared_rate_estimate']<r['absolute_rate_series_tail_estimate']
    with pytest.raises(ValueError):conditional_decay_unit(0,lifetime_seconds=1,hbar_GeV_seconds=1)
    with pytest.raises(ValueError):tensor_rate_tail_estimate(1,-1,muon_mass_GeV=1)
