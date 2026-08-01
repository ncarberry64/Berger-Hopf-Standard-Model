from bhsm.interface.envelopment import common_envelopment_mode_v10_3 as common


def test_exact_historical_variables_and_seam_fold_constraint_are_imported():
    payload = common.common_mode_payload()
    assert [row["exact_repository_variable"] for row in payload["provenance"]] == [
        "S_Sigma endpoint threading trace",
        "q_fold",
        "delta beta=delta ln(a_F/a_F0)",
    ]
    assert payload["constraints"]["equation"] == "psi+alpha_Sigma*zeta=0"
    assert payload["constraints"]["rank"] == 1
    assert {row["module"] for row in payload["historical_operator_imports"]} == {
        "bhsm.interface.full_shift_variation_support_closure",
        "bhsm.interface.fold_schur_kinetic",
        "bhsm.interface.envelopment.local_radion_v10_3",
    }


def test_gauge_quotient_and_cross_blocks_fail_closed():
    payload = common.common_mode_payload()
    assert payload["gauge"]["rank"] == 0
    assert payload["gauge"]["quotient_dimension_before_constraints"] == 3
    assert payload["blocks"]["K_env"][1][2]["status"] == "UNDEFINED_CROSS_DOMAIN"
    assert payload["blocks"]["H_env"][2][1]["status"] == "UNDEFINED_CROSS_DOMAIN"
    assert payload["equivalence_status"] == "EQUIVALENCE_UNRESOLVED"
    assert payload["physically_inequivalent"] is False
    assert payload["one_mode_equivalence_hypothesis"] == "INVALIDATED_BY_AUTHOR_ONTOLOGY"


def test_known_blocks_are_symmetric_and_typed():
    blocks = common.block_ledger()
    for name in ("K_env", "H_env"):
        matrix = blocks[name]
        for i in range(3):
            for j in range(3):
                assert matrix[i][j]["status"] == matrix[j][i]["status"]
                assert matrix[i][j]["value"] == matrix[j][i]["value"]
