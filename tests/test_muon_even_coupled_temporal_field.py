"""CONTROL_ONLY exact complete angular image/reduction checks."""
import numpy as np
from bhsm.interface.muon_even_coupled_temporal_field import complete_even_angular_blocks


def test_complete_even_source_image_not_scalar_subblock():
    a=complete_even_angular_blocks()
    assert [len(b['harmonic_indices'])for b in a['blocks']]==[1,3,6,5,10,10]
    assert sorted(np.concatenate([b['harmonic_indices']for b in a['blocks']]).tolist())==list(range(35))
    assert sorted(np.concatenate([b['field_indices']for b in a['blocks']]).tolist())==list(range(2100))
    assert a['off_block_derivative_max']==0


def test_entire_angular_laplacian_is_recovered_from_all_blocks():
    a=complete_even_angular_blocks();full=-sum(E@E for E in a['derivatives']);assembled=np.zeros_like(full)
    for b in a['blocks']:
        hi=b['harmonic_indices'];part=-sum(E@E for E in b['derivatives']);assembled[np.ix_(hi,hi)]=part
        np.testing.assert_allclose(part,b['level']*(b['level']+2)*np.eye(len(hi)),atol=3e-14,rtol=0)
    np.testing.assert_array_equal(assembled,full)
