from bhsm.interface.aether_n3_physical_residual_role_audit_v16_45 import physical_residual_role_audit


def test_every_q_coordinate_group_has_a_physical_role():
    assert len(physical_residual_role_audit()["coordinate_group_ranking"]) == 10
