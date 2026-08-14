from bhsm.interface.aether_n3_zero_background_calderon_closure_v17_97 import (
    completion_payload,
)


def test_zero_background_calderon_closure_is_exact_but_scoped():
    payload = completion_payload()
    assert payload["validation_passed"]
    result = payload["zero_background_calderon_closure"]
    assert result["F_child_zero_background_norm"] == 0.0
    assert result["provenance"]["same_bundle_isomorphism_class"]
    assert not result["scope"][
        "full_nonzero_fluctuation_Calderon_matrices_derived"
    ]
    assert not result["scope"]["quantum_determinant_backreaction_zero"]
    assert not payload["direct_N3_solve_authorized_next"]
