"""Independent whole complex field/frame difference of the source readout."""
import numpy as np
from scipy.linalg import expm
from bhsm.interface.muon_d5_fixed_radial_source_consumption import fixed_field_source_and_frame,response_raw_slots


def test_common_gamma_channel_has_no_second_direct_shape():
    a=np.arange(268,dtype=complex)[:,None];data={}
    for half,scale in (('high',1),('low',1e-18)):
        data['direct_raw_'+half]=scale*a
        data['induced_raw_'+half]=scale*(2*a+1j)
        data['total_raw_'+half]=data['induced_raw_'+half].copy()
    area,_=response_raw_slots(data,'area')
    assert np.max(abs(area[:,:2]))==0
    np.testing.assert_array_equal(area[:,2:4],area[:,4:6])
    base,_=response_raw_slots(data,'base')
    np.testing.assert_array_equal(base[:,0],a[:,0])


def test_complete_complex_frame_field_and_energy_placements():
    rng = np.random.default_rng(10041)
    def a(n):
        return rng.normal(size=(n, n)) + .17j * rng.normal(size=(n, n))
    d, nw = 8, 3; ni = d - nw
    K = a(d) + 12 * np.eye(d); KE, S, SE = [a(d) for _ in range(3)]
    A0, R0 = a(nw), a(nw); AL, RR, G, GS = [a(nw) for _ in range(4)]
    out = fixed_field_source_and_frame(K, KE, S[None], SE[None], A0, R0,
        (AL @ A0)[None], (R0 @ RR)[None], G, GS[None])
    def direct(e, s):
        B = K + e * KE + s * S + e * s * SE
        C = B[ni:, ni:] - B[ni:, :ni] @ np.linalg.solve(B[:ni, :ni], B[:ni, ni:])
        return expm(s * AL) @ A0 @ C @ R0 @ expm(s * RR)
    h = 1e-4
    mixed = (direct(h,h)-direct(h,-h)-direct(-h,h)+direct(-h,-h))/(4*h*h)
    assert np.max(abs(mixed-out['adapted_complete_source_energy'][0])) < 2e-6
    first = (direct(0,h)-direct(0,-h))/(2*h)
    assert np.max(abs(first-out['adapted_complete_source'][0])) < 3e-6
    def wall(s):
        return expm(s*AL) @ A0 @ (G+s*GS) @ R0 @ expm(s*RR)
    assert np.max(abs((wall(h)-wall(-h))/(2*h)-out['adapted_complete_Green_source'][0])) < 1e-6
    assert np.linalg.norm(out['adapted_source_energy_left_frame']) > 0
    assert np.linalg.norm(out['adapted_source_energy_right_frame']) > 0
    for key in ('original_right_source_field_rows','original_left_source_field_rows',
                'original_right_source_energy_field_rows','original_left_source_energy_field_rows'):
        assert np.max(abs(out[key])) < 5e-14
    def poisson(e,s):
        B=K+e*KE+s*S+e*s*SE
        return np.r_[-np.linalg.solve(B[:ni,:ni],B[:ni,ni:]),np.eye(nw)]
    mixed_P=(poisson(h,h)-poisson(h,-h)-poisson(-h,h)+poisson(-h,-h))/(4*h*h)
    assert np.max(abs(mixed_P-out['original_raw_field_Poisson_source_energy'][0]))<3e-8
