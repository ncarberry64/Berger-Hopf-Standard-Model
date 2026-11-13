from pathlib import Path
import numpy as np
import pytest
from bhsm.interface.muon_saved_wall_complex_coefficients import (
    saved_original_wall_coefficient_family,forms_at_complex_offset,
)
from bhsm.interface.muon_literal_euclidean_higgs_green import literal_proper_euclidean_forms

ROOT=Path(__file__).resolve().parents[1]


@pytest.fixture(scope='module')
def family():return saved_original_wall_coefficient_family(repository=ROOT)


def test_actual_saved_nodes_and_chronological_anchor_binding(family):
    for side in ('incoming','outgoing'):
        arm=family['arms'][side];a=arm['arrays'];L=abs(arm['span'])
        for q,u in enumerate(a['times']):
            r=forms_at_complex_offset(side,u-L if side=='incoming' else u,family=family)
            for k,v in zip(('M','B','K'),r['Lorentz_forms']):
                np.testing.assert_allclose(v,a[k][q],atol=2e-12,rtol=8e-16)
            assert r['At_count']==64
            assert np.array_equal(r['value_permutation'],a['value_permutation'])
            assert len(r['central_radial_frame_indices'])==16
            assert not r['restored_connector_or_physical_relative_domain_identified']
        with pytest.raises(ValueError):forms_at_complex_offset(side,2*L,family=family)


def test_actual_complex_polynomial_and_literal_At_conversion_once(family):
    for side in ('incoming','outgoing'):
        arm=family['arms'][side];L=abs(arm['span']);u=.375*L
        t=u-L if side=='incoming' else u;z=(.013-.021j)*L
        r=forms_at_complex_offset(side,t,z,family=family)
        j=1;dz=u+z-arm['arrays']['times'][j]
        independent=tuple(sum(p.c[k,j]*dz**(3-k) for k in range(4))for p in arm['polynomials'])
        for got,want in zip(r['Lorentz_forms'],independent):np.testing.assert_array_equal(got,want)
        expected=literal_proper_euclidean_forms(independent,r['N'],64)
        for got,want in zip(r['forms'],expected['forms']):np.testing.assert_array_equal(got,want)
        # Proper At_E -> original At_L is i*N, not its adjoint or a
        # second vertex rotation. All original algebraic rows survive.
        np.testing.assert_allclose(r['inverse_coordinate_rotation'][:64],1j*r['N'],atol=0,rtol=3e-16)
        np.testing.assert_array_equal(r['inverse_coordinate_rotation'][64:],np.ones(272))
        x=np.arange(336)+.1j*np.arange(336)[::-1]
        np.testing.assert_allclose(r['proper_Euclidean_wall_trace_map']@x,
            r['wall_trace_map']@(r['inverse_coordinate_rotation']*x),atol=2e-13,rtol=3e-15)
        assert r['fresh_original_action_interpolation_checks']
        assert not r['complex_coefficient_parameters_conjugated']
