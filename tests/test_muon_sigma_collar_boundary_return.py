"""Independent signed interval endpoint sum before projection."""
import numpy as np
from bhsm.interface.muon_sigma_collar_boundary_return import collar_surface_work_projection
from bhsm.interface.muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace


def test_broken_interval_surface_work_sign_and_literal_energy_response():
    full=full_d5_localized_lepton_trace();rng=np.random.default_rng(67)
    endpoint=rng.normal(size=(6,2,2,64,64))+1j*rng.normal(size=(6,2,2,64,64))
    # Three intervals: [endpoint0,1], [2,3], [4,5].
    jumps=np.array([endpoint[2]-endpoint[1],endpoint[4]-endpoint[3]])
    P=rng.normal(size=(768,18))+1j*rng.normal(size=(768,18));PE=.17j*P+.03*P[::-1]
    z=collar_surface_work_projection(endpoint[0],endpoint[5],jumps,P,PE,full=full)
    independent=(endpoint[1]-endpoint[0])+(endpoint[3]-endpoint[2])+(endpoint[5]-endpoint[4])
    branch=lambda a:np.block([[a[0],np.zeros((64,64))],[np.zeros((64,64)),a[1]]])
    A=[np.kron(np.eye(3),branch(a))for a in independent]
    whole=np.block([[A[0],np.zeros((384,384))],[np.zeros((384,384)),A[1]]])
    assert np.max(abs(z['signed_full_field_surface_matrix']-whole))<4e-15
    assert np.max(abs(z['total_broken_trial_surface_work']-z['analytic_left_test']@whole@P))<2e-13
    assert np.max(abs(z['total_broken_trial_surface_work_energy']-z['analytic_left_test']@whole@PE))<5e-14
