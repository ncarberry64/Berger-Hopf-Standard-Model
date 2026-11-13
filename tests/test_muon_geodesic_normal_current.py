from pathlib import Path
import numpy as np
from scipy.linalg import expm

from test_muon_normal_current_contraction_maps import actual_arguments
from bhsm.interface.muon_normal_current_contraction_maps import normal_current_contraction_maps
from bhsm.interface.muon_geodesic_normal_current import represented_geodesic_current, local_radial_higgs_charge_vertices

ROOT=Path(__file__).resolve().parents[1]


def test_actual_complete_loop_block_geodesic_jet_and_literal_reverse():
    args=actual_arguments();m=normal_current_contraction_maps(**args)
    folder=ROOT/'artifacts/muon_paired_changing_magnetic_columns_20261011/constant_run_1'
    with np.load(folder/'incoming_family_1_forward.npz',allow_pickle=False) as a:C=a['total']
    with np.load(folder/'incoming_family_1_reverse.npz',allow_pickle=False) as a:B=a['total']
    opts=dict(radius=args['radius'], connection=m['full_C6_spatial_connection'], direction=np.array([0.,1.,0.]))
    expected=represented_geodesic_current(C,B,separation=0.,**opts)['exact_represented_relative_first_jet']
    errors=[]
    for s in (1e-3,5e-4):
        p=represented_geodesic_current(C,B,separation=s,**opts)['Wilson_bilocal_kernel']
        q=represented_geodesic_current(C,B,separation=-s,**opts)['Wilson_bilocal_kernel']
        errors.append(np.linalg.norm((p-q)/(2*s)-expected))
    assert errors[1] < .26*errors[0]
    assert errors[1] < 2e-7*np.linalg.norm(expected)
    assert np.linalg.norm(B-C.conj().transpose(0,2,1)) > 1e-13


def test_geodesic_transport_constant_frame_covariance_keeps_neutral_fibers():
    args=actual_arguments();m=normal_current_contraction_maps(**args)
    rng=np.random.default_rng(660)
    C=rng.normal(size=(3,6,4,6))+1j*rng.normal(size=(3,6,4,6))
    B=rng.normal(size=(3,6,6,4))+1j*rng.normal(size=(3,6,6,4))
    K=rng.normal(size=(6,6))+1j*rng.normal(size=(6,6));U=expm(K-K.conj().T)
    Cp=np.einsum('ia,Aahb,bj->Aihj',U,C,U.conj().T).reshape(3,24,6)
    Bp=np.einsum('ia,Aabh,bj->Aijh',U,B,U.conj().T).reshape(3,6,24)
    opts=dict(radius=args['radius'],direction=np.array([1.,0.,0.]),separation=.001)
    a=represented_geodesic_current(C.reshape(3,24,6),B.reshape(3,6,24),connection=m['full_C6_spatial_connection'],**opts)
    b=represented_geodesic_current(Cp,Bp,connection=U[None]@m['full_C6_spatial_connection']@U.conj().T[None],**opts)
    np.testing.assert_allclose(b['Wilson_bilocal_kernel'],U[None]@a['Wilson_bilocal_kernel']@U.conj().T[None],rtol=2e-14,atol=3e-14)


def test_same_action_radial_overlap_couplings_do_not_refit_mass_or_double_lr():
    args=actual_arguments()
    for H in (args['H'],np.array([.3+.4j,.7-.2j])):
        a=local_radial_higgs_charge_vertices(H,family=1)
        np.testing.assert_allclose(a['charged_vertex_identity_residual'],0.,atol=3e-19)
        np.testing.assert_allclose(a['charged_charge_identity_residual'],0.,atol=1e-15)
        np.testing.assert_allclose(a['full_radial_fixed_Y_vertex'],a['full_LR_forward_vertex']+a['full_LR_reverse_vertex'],atol=0.)
        assert not a['finite_core_or_continuum_overlap_subtracted']
        assert not a['same_scalar_pole_and_Lorentz_domain_evaluated']
