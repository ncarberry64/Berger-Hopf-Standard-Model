import numpy as np
from bhsm.interface.muon_sigma_normal_collar_transport import CanonicalC1History,transport_sigma_normal
from bhsm.interface.muon_birth_trace_enriched_action import generic_coordinate_lift
from bhsm.interface.muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace


def test_actual_sigma_flow_normal_density_jacobian_mode_and_independent_duals():
    labels=[dict(field=f,internal=i,radial=r)for r in range(4)for f in('A_tau','A_rho','A_1','A_2','A_3')for i in range(4)]
    coords=generic_coordinate_lift(labels)
    raw=np.zeros(268,complex);raw[0]=.01+.002j;raw[124+3]=.03+.004j
    rep=dict(affine_profile_reference_states=np.zeros((2,98)),affine_interior_projection=np.zeros(2),
        affine_wall_coefficient=0.,affine_complement_norm=1.)
    times=np.array([0.,.5,1.]);x=np.tile(raw,(3,1));rates=np.zeros_like(x)
    history=CanonicalC1History(times,x,rates,coords)
    a,b=transport_sigma_normal(history,rep,full_d5_localized_lepton_trace(),start_time=.5,
        wall_amplitude=.8+.02j,literal_left_wall_amplitude=.7-.01j,normal_length=.02)
    np.testing.assert_allclose(a['original_normal_mode_rows'],0,atol=2e-16)
    np.testing.assert_allclose(a['original_flow_volume_Jacobian_rows'],0,atol=2e-10)
    np.testing.assert_allclose(a['particle_analytic_dual_rows'],0,atol=2e-12)
    np.testing.assert_allclose(a['conjugate_analytic_dual_rows'],0,atol=2e-12)
    assert b['partial_integral_not_full_mode_normalization']
    assert np.linalg.norm(a['conjugate_gauge_transport']-a['particle_gauge_transport'].conj())>1e-6
