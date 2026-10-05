"""New node3 checks only; no earlier point producer or tail replay."""
from pathlib import Path
import json
import numpy as np
import pytest

ROOT=Path(__file__).resolve().parents[1]
REF=ROOT/'artifacts/muon_wall_input_attachment_20261005/run_1'


def read(p):
    with np.load(p,allow_pickle=False) as z:return {k:np.array(z[k]) for k in z.files}


@pytest.fixture(scope='module')
def actual():
    return read(REF/'node3_projected_intrinsic_kinetic.npz')


def test_actual_projection_cannot_factor_through_material_trace(actual):
    contact=read(ROOT/'artifacts/muon_parent_source_contact_20261003/replay_reference/parent_source_contact.npz')
    assert contact['spinor_probe_hat_nodes'][-1]==0
    a=actual;xi=a['Xi_full'];source=a['source_coordinates']
    material=a['material_trace'][1]*xi@source
    projection=a['B_volume'][1]*xi@source
    np.testing.assert_array_equal(material,a['material_source_trace'])
    assert np.linalg.norm(projection)>0.02
    assert a['B_volume'][1]>0 and a['B_Cauchy'][1]!=a['B_volume'][1]
    # A linear map of the zero material trace must be zero. This actual
    # nonzero projection therefore rules out B_rad=T Gamma_material here.


def test_actual_geometric_adjoint_and_time_maps_are_distinct(actual):
    a=actual
    assert abs(a['volume_adjoint_residual'])<1e-14
    assert abs(a['volume_isometry_quadrature_residual'])<1e-13
    assert abs(a['Cauchy_adjoint_residual'])<1e-14
    assert a['B_volume_tau'][1]!=a['B_Cauchy_tau'][1]
    assert a['material_trace_tau'][0]!=0
    assert a['B_volume_tau'][0]==0 and a['B_Cauchy_tau'][0]==0


def test_intrinsic_kinetic_source_jet_against_direct_covariant_action(actual):
    a=actual;d=len(a['source_coordinates']);rad=read(ROOT/'artifacts/muon_radial_inclusion_action_20261004/replay_reference/radial_source_action_and_interface.npz')
    G=rad['common_parent_Gamma'];H=float(a['H']);R=float(a['radius']);bg=float(a['wall_bg_reference'])
    zero=1.5*H*1j*G[0]+rad['angular_spin']/R+bg*rad['commonA_gauge_unit']
    for n in (1,3):
        xi=a[f'normalized_wall_W_input_n{n}'];b,bd=a['B_volume'][1],a['B_volume_tau'][1]
        # Differentiate the actual normalized source input first. Apply
        # the retained wall differential symbol to that full input and jet.
        field=b*xi;field_tau=bd*xi
        action=np.einsum('oi,imkj->omkj',zero,field)+np.einsum('oi,imkj->omkj',1j*G[0],field_tau)
        for k in range(3):
            action+=np.einsum('oi,imkj,vm->ovkj',1j*G[k+1],field,rad[f'angular_E_n{n}'][k])/R
        np.testing.assert_allclose(action,a[f'kinetic_reference_p_0_n{n}'],rtol=3e-15,atol=2e-17)
        assert a[f'kinetic_reference_p_0_n{n}'].shape==(64,n+1,n+1,d)
    # Dropping the B_tau term changes the actual source action appreciably.
    omission=a['F0'][:,d:]-a['B_volume'][1]*a['F0'][:,:d]
    assert np.linalg.norm(omission)>0.2*np.linalg.norm(a['F0'][:,d:])


def test_reference_gram_combines_the_same_output_before_squaring(actual):
    a=actual;d=len(a['source_coordinates']);c=a['source_coordinates']
    # Two actual supplied column combinations check W/p and temporal cross.
    x=np.r_[c,c];xt=np.r_[c,-c]
    output=a['F0']@x+a['F1']@xt
    direct=float(a['M4'])*np.vdot(output,output)
    A,B,C=(a['kinetic_reference_'+k] for k in ('A','B','C'))
    gram=np.vdot(x,A@x)+np.vdot(x,B@xt)+np.vdot(xt,B.conj().T@x)+np.vdot(xt,C@xt)
    assert abs(direct-gram)/abs(direct)<3e-15
    assert np.linalg.norm(A[:d,d:])>0 and np.linalg.norm(B)>0


def test_actual_bounded_graph_has_a_nonzero_geometric_orthogonal_vector(actual):
    a=actual;x=a['graph_orthogonal_bulk'];z=a['graph_orthogonal_wall']
    B,M5,M4=a['source_input_projection'],a['trial_M5'],a['wall_M4']
    pairing=x.conj().T@M5+z.conj().T@M4@B
    assert np.linalg.norm(pairing)<4e-14
    np.testing.assert_allclose(M5@a['B_sharp'],B.conj().T@M4,rtol=1e-14,atol=1e-13)
    assert np.vdot(x,M5@x).real+np.vdot(z,M4@z).real>25


def test_native_row_and_updated_response_are_not_promoted(actual):
    result=json.loads((REF/'result.json').read_text())
    assert all(v is None for v in result['native'].values())
    assert result['operator_update_applied'] is False
    assert result['new_stationary_solve'] is False
    # The recovered chiral block is kept in its inherited units and source
    # provenance, not inserted as a scalar mass into the64-carrier row.
    inherited=json.loads((ROOT/'artifacts/action_extension/BHSM_AE31_C2_CHIRAL_GREEN_DOMAIN.json').read_text())
    np.testing.assert_array_equal(actual['inherited_LR_mass_block_GeV'],inherited['chiral_operator_assembly']['LR_zero_order_mass_block_GeV'])


def test_actual_intrinsic_principal_time_input_cotangent(actual):
    a=actual;d=len(a['source_coordinates']);c=a['source_coordinates'];mu=float(a['M4'])
    saved=read(REF.parent/'principal_run_1/principal_time_input_cotangent.npz')
    T=a['F1'][:,:d];P=a['F1'][:,d:]
    # The known intrinsic time symbol is linear in its input. Its Gram is
    # exactly quadratic, so this polynomial identity has no soft-limit claim.
    exact_identity=2*float(a['B_volume'][1])*mu*(T.conj().T@T)
    # Use the matrix's actual scale; entrywise relative tests on zeros
    # cannot resolve BLAS roundoff from distinct contraction orders.
    assert np.linalg.norm(saved['derivative_Cpp_under_delta_Theta_Xi']-exact_identity)<3e-15*np.linalg.norm(exact_identity)
    delta=.125
    plus=mu*((P+delta*T).conj().T@(P+delta*T))
    minus=mu*((P-delta*T).conj().T@(P-delta*T))
    assert np.linalg.norm((plus-minus)/(2*delta)-saved['derivative_Cpp_under_delta_Theta_Xi'])<3e-15*np.linalg.norm(exact_identity)
    contraction=np.vdot(c,saved['derivative_Cpp_under_delta_Theta_Xi']@c)
    assert abs(contraction.real-.6470708143732534)<2e-15
    receipt=json.loads((REF.parent/'principal_run_1/result.json').read_text())
    assert receipt['native_wall_variation_justified'] is False
    assert receipt['new_stationary_solve'] is False
