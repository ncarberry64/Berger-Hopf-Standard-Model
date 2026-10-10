"""Only the new proposed-law controls, never old production replays."""
from pathlib import Path
import sys
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from bhsm.interface.muon_proposed_dynamic_seam import (
    actual_source_readout, actual_green_controls, charged_left_projector,
    source_total_jet, sharp, sharp_jet, readout_jet)

ROOT=Path(__file__).resolve().parents[1]


def data():
    refs=(ROOT/'artifacts/muon_wall_input_attachment_20261005/run_1/node3_projected_intrinsic_kinetic.npz',
          ROOT/'artifacts/muon_joint_variational_attachment_20261005/run_2/node3_joint_known_variations.npz')
    out=[]
    for p in refs:
        with np.load(p,allow_pickle=False) as z:
            out.append({k:np.array(z[k]) for k in z.files})
    return out


def test_action_green_average_jump_on_actual_sources():
    wall,green=data()
    controls=actual_green_controls(wall,green)
    assert controls['action_Green_skew']<2e-14
    assert controls['action_Green_square']<2e-14
    assert controls['average_jump_identity']<2e-12
    # The bare L2 Green density is a different adjoint convention.
    assert np.linalg.norm(green['Dirac_bar_Green_density']-green['geometric_L2_Green_density'])>1


def test_proposed_material_domain_force_uses_actual_pairing():
    controls=actual_green_controls(*data())
    assert controls['proposed_material_Green_balance']<2e-12
    assert controls['proposed_matched_average_constraint']<2e-14


def test_actual_readout_retains_unmatched_spin_and_carrier():
    wall,green=data()
    arrays,numeric=actual_source_readout(wall,green)
    assert numeric['J_left_column_Frobenius_norm']>0
    assert numeric['unmatched_average_column_Frobenius_norm']>0
    for n in (1,3):
        left=arrays[f'J_chi_left_n{n}'].reshape(4,16,n+1,n+1,12)
        unmatched=arrays[f'unmatched_average_trace_n{n}'].reshape(left.shape)
        assert not np.any(left[2:])
        assert np.linalg.norm(unmatched[2:,6:8])>0
        assert not np.any(arrays[f'J_chi_right_singlet_n{n}'])
        average=arrays[f'average_trace_chi_n{n}']
        assert np.linalg.norm(average-float(green['kappa'])*arrays[f'J_chi_left_n{n}']
                              -arrays[f'unmatched_average_trace_n{n}'])<1e-16
        # Along the material relation, total kappa motion cancels the
        # fixed-trace partial kernel; this is not a physical photon jet.
        P=charged_left_projector(); kappa=float(green['kappa'])
        trace=average.reshape(64,-1); rate=.3
        _,total=readout_jet(kappa,rate*kappa,P,np.zeros_like(P),
                           np.eye(64),np.zeros_like(P),trace,rate*trace)
        assert np.linalg.norm(total)<2e-17
        assert np.array_equal(arrays[f'partial_dJ_d_log_kappa_at_fixed_trace_n{n}'],
                              -arrays[f'J_chi_left_n{n}'])


def test_ordered_total_jet_and_moving_geometric_dual():
    # One algebra control with every jet nonzero. This is explicitly not a
    # physical photon jet. Polynomial differentiation checks missing terms.
    F=np.array([[1.,2.],[-1.,3.]])
    FA=np.array([[.3,-.4],[.2,.1]])
    p=np.array([[2.],[-3.]]);pA=np.array([[.1],[.7]])
    W=np.array([[1.],[.4]]);WA=np.array([[.2],[-.1]])
    B=np.array([[.6,-.2]]);BA=np.array([[.05,.03]])
    J,JA=source_total_jet(F,FA,p,pA,W,WA,B,BA)
    curves=lambda t:(F+t*FA)@(p+t*pA-(W+t*WA)@(B+t*BA)@(p+t*pA))
    h=1e-5
    assert np.linalg.norm((curves(h)-curves(-h))/(2*h)-JA)<1e-9
    assert np.linalg.norm(J-curves(0))<1e-14
    Ms=np.diag([2.,3.]);MsA=np.diag([.2,-.3])
    Mt=np.diag([4.,5.]);MtA=np.array([[.1,.03],[.03,.2]])
    X=F.astype(complex)+.2j*np.eye(2);XA=FA+.1j*np.eye(2)
    Xs=sharp(X,Ms,Mt);XsA=sharp_jet(X,XA,Ms,MsA,Mt,MtA)
    # Differentiate the duality identity Ms Xsharp=Xdag Mt.
    assert np.linalg.norm(MsA@Xs+Ms@XsA-XA.conj().T@Mt-X.conj().T@MtA)<2e-15
