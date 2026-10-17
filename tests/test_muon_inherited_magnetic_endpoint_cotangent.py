import numpy as np
from bhsm.interface.muon_inherited_magnetic_endpoint_cotangent import inherited_magnetic_endpoint_cotangent


def test_complete_endpoint_first_keeps_both_cotangents_and_independent_source_motion():
    rng=np.random.default_rng(39216);draw=lambda shape:rng.normal(size=shape)+.3j*rng.normal(size=shape)
    qp,qc,pp,pc,sp,sc=[draw((8,3))for _ in range(6)]
    dqp,dqc,dpp,dpc,dsp,dsc=[draw((2,8,3))for _ in range(6)]
    direct=np.array([dsp[k].T@pp-dsc[k].T@pc for k in range(2)])
    data=dict(parent_total_field=qp,child_total_field=qc,parent_canonical_momentum=pp,child_canonical_momentum=pc,
        parent_total_field_first=dqp,child_total_field_first=dqc,parent_canonical_momentum_first=dpp,child_canonical_momentum_first=dpc,
        parent_known_wall_field=sp,child_known_wall_field=sc,direct_source_first_endpoint_cotangent=direct)
    a=inherited_magnetic_endpoint_cotangent(data)
    h=.17
    for k in range(2):
        full=lambda t:(qp+t*dqp[k]).T@(pp+t*dpp[k])-(qc+t*dqc[k]).T@(pc+t*dpc[k])
        source=lambda t:(sp+t*dsp[k]).T@(pp+t*dpp[k])-(sc+t*dsc[k]).T@(pc+t*dpc[k])
        np.testing.assert_allclose(a['full_interface_action_cotangent_first'][k],(full(h)-full(-h))/(2*h),rtol=8e-15,atol=2e-14)
        np.testing.assert_allclose(a['prescribed_source_action_cotangent_first'][k],(source(h)-source(-h))/(2*h),rtol=8e-15,atol=2e-14)
    assert np.linalg.norm(a['prescribed_source_momentum_motion'])>1
    assert np.linalg.norm(qp.conj().T@pp-a['full_interface_action_cotangent']-qc.T@pc)>1
    assert not a['physical_full_birth_event_exterior_Gamma2_pole_or_Pauli_selected']
