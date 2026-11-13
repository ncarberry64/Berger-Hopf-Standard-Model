from pathlib import Path
import numpy as np
from bhsm.interface.muon_coupled_lorentz_radial_green import coupled_radial_trace_application
from bhsm.interface.muon_static_coupled_charged_current import static_coupled_charged_current
ROOT=Path(__file__).resolve().parents[1]


def actual(side='incoming'):
    with np.load(ROOT/'artifacts/muon_coupled_lorentz_field_symbol_20261011/run_1/application.npz',allow_pickle=False)as a:
        data=[a[side+'_'+k].copy()for k in('proper_frequency_coefficients','field_quotient_lift','joint_trace_map','scalar_radial_source','central_radial_frame_rows')]
        raw=a[side+'_raw_fields'].copy()
    N=1.108427234091954 if side=='incoming'else .6981395735679908
    G=coupled_radial_trace_application(*data,frequency=0)['joint_wall_Green']
    h=raw[-8:-4];H=h[:2]+1j*h[2:]
    return G,static_coupled_charged_current(G,H,radius=.9633777962755172,lapse=N,family=1)


def test_full_static_source_tensor_matches_literal_all24_original_vertex_contractions():
    G,a=actual();literal=np.zeros((2,4,4,2),complex)
    for j in range(24):
        for k in range(24):
            literal+=G[j,k]*np.multiply.outer(a['charged_current_right_vertices'][j],a['charged_current_left_vertices'][k])
    assert np.linalg.norm(literal-a['full_charged_current_tensor'])<2e-14
    assert np.linalg.norm(a['exact_sector_sum_difference'])<2e-14
    assert np.linalg.norm(a['scalar_scalar_tensor'])>9e-5
    assert np.linalg.norm(a['gauge_scalar_tensor'])>1e-4
    assert np.array_equal(a['family_indices'],[2,3,8,9,14,15])
    assert abs(a['constant_angular_current_integral']-1)<3e-16


def test_both_actual_arms_keep_the_non_VA_remainder_and_analytic_vertex_dual():
    for side in('incoming','outgoing'):
        G,a=actual(side)
        assert np.linalg.norm(a['literal_left_minus_vertex_adjoint'])<1e-14
        assert abs(np.vdot(a['VA_template'],a['VA_tensor_remainder']))<2e-14
        assert a['VA_relative_remainder']>.75
        assert not a['physical_GF_or_unit_selected']
