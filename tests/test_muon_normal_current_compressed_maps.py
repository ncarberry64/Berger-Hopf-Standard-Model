import numpy as np

from test_muon_normal_current_contraction_maps import actual_arguments
from bhsm.interface.muon_normal_current_contraction_maps import (
    normal_current_contraction_maps, dyadic_two_green_contraction)
from bhsm.interface.muon_normal_current_compressed_maps import compress_normal_current_maps


def test_actual_covariant_neutral_return_requires_complete_right_basis():
    args = actual_arguments()
    maps = normal_current_contraction_maps(**args)
    c = compress_normal_current_maps(maps, radius=args['radius'])
    for name in ('right_mass_C', 'right_FW_C', 'Weyl_mass_C',
            'Weyl_mass_T', 'Weyl_FW_C', 'Weyl_FW_T'):
        size = 6 if name.endswith('_C') else 18
        for row in c[name]:
            assert row['right_tests'].shape[0] == size
            np.testing.assert_allclose(row['left_tests'].T @ row['right_tests'],
                row['tensor_weight'], rtol=3e-14, atol=3e-14)
    assert c['right_mass_C'][0]['charged_only_projection_relative_residual'] < 1e-14
    assert c['right_FW_C'][0]['charged_only_projection_relative_residual'] > .18
    assert c['Weyl_FW_T'][0]['charged_only_projection_relative_residual'] > .23


def test_structural_compression_preserves_literal_complex_current_contraction():
    args = actual_arguments()
    maps = normal_current_contraction_maps(**args)
    c = compress_normal_current_maps(maps, radius=args['radius'])
    rng = np.random.default_rng(707)
    for name in ('right_FW_C', 'Weyl_FW_T'):
        out, inp = c[name][0]['tensor_weight'].shape
        L = rng.normal(size=(3, out, 5, 7)) + 1j*rng.normal(size=(3, out, 5, 7))
        R = rng.normal(size=(5, inp, 7)) + 1j*rng.normal(size=(5, inp, 7))
        K = rng.normal(size=(5, 7))
        for i in range(3):
            np.testing.assert_allclose(
                dyadic_two_green_contraction(L, R, K, c[name][i]),
                dyadic_two_green_contraction(L, R, K, maps[name][i]),
                rtol=1e-13, atol=1e-10)
