import sympy as sp

from bhsm.interface.envelopment import coupled_mode_rank_v10_3 as rank


def test_unknown_cross_kinetic_block_leaves_rank_one_or_two():
    bounds = rank.rank_bounds_two_mode(sp.Integer(2), sp.Integer(3))
    assert bounds["possible_ranks"] == [1, 2]
    assert "K_zetaF**2" in bounds["determinant"]


def test_missing_cross_domain_block_is_unresolved_not_inequivalent():
    payload = rank.coupled_rank_payload()
    assert payload["physical_kinetic_rank"] is None
    assert payload["lowest_common_eigenmode"] is None
    assert payload["equivalence_status"] == "EQUIVALENCE_UNRESOLVED"
    assert payload["physically_inequivalent"] is False
    assert payload["nonlinear_continuation"]["status"] == "EQUIVALENCE_UNRESOLVED"
