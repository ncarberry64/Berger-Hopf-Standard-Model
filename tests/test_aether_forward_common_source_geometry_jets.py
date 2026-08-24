import numpy as np

from bhsm.interface.aether_forward_common_source_incidence import (
    forward_hs_scalar_log_radius_jets,
    forward_hs_scalar_operator_and_gauge_vertices,
    forward_oneform_ghost_log_radius_jets,
    forward_oneform_ghost_matrices,
    forward_weyl_log_radius_jets,
    forward_weyl_squared_operator_and_vertices,
)


RADII = np.array([0.9, 1.1, 1.3])
PROFILE = np.array([0.4, -0.2, 0.7])
H = np.array([0.3, -0.4, 0.2])
K = np.array([-0.1, 0.25, 0.5])
D = np.array(
    [[0.0, 0.5, -0.5], [-0.5, 0.0, 0.5], [0.5, -0.5, 0.0]],
    dtype=complex,
)
L = D.conj().T @ D + 0.2 * np.eye(3)


def _first_difference(builder, eps: float = 1.0e-5):
    plus = builder(RADII * np.exp(eps * H))
    minus = builder(RADII * np.exp(-eps * H))
    return tuple((left - right) / (2.0 * eps) for left, right in zip(plus, minus))


def _mixed_difference(builder, eps: float = 2.0e-4):
    pp = builder(RADII * np.exp(eps * H + eps * K))
    pm = builder(RADII * np.exp(eps * H - eps * K))
    mp = builder(RADII * np.exp(-eps * H + eps * K))
    mm = builder(RADII * np.exp(-eps * H - eps * K))
    return tuple(
        (a - b - c + d) / (4.0 * eps**2)
        for a, b, c, d in zip(pp, pm, mp, mm)
    )


def _assert_tuple_close(actual, expected, atol: float) -> None:
    for left, right in zip(actual, expected):
        assert np.allclose(left, right, rtol=2.0e-6, atol=atol)


def test_weyl_log_radius_jets_match_mixed_finite_differences() -> None:
    for source in ("coexact_gauge", "HS"):
        builder = lambda radii: forward_weyl_squared_operator_and_vertices(
            1, radii, D, PROFILE, source=source
        )
        jets = forward_weyl_log_radius_jets(
            1, RADII, D, PROFILE, H, K, source=source
        )
        _assert_tuple_close(jets["base"], builder(RADII), 1.0e-12)
        _assert_tuple_close(jets["first"], _first_difference(builder), 2.0e-9)
        _assert_tuple_close(
            jets["mixed_second"], _mixed_difference(builder), 3.0e-7
        )


def test_hs_scalar_log_radius_jets_match_mixed_finite_differences() -> None:
    builder = lambda radii: forward_hs_scalar_operator_and_gauge_vertices(
        2, radii, L, PROFILE
    )
    jets = forward_hs_scalar_log_radius_jets(
        2, RADII, L, PROFILE, H, K
    )
    _assert_tuple_close(jets["base"], builder(RADII), 1.0e-12)
    _assert_tuple_close(jets["first"], _first_difference(builder), 2.0e-9)
    _assert_tuple_close(
        jets["mixed_second"], _mixed_difference(builder), 3.0e-7
    )


def test_oneform_ghost_log_radius_jets_match_mixed_finite_differences() -> None:
    builder_dict = lambda radii: forward_oneform_ghost_matrices(
        1, radii, D, L, PROFILE
    )
    keys = tuple(builder_dict(RADII))
    builder = lambda radii: tuple(builder_dict(radii)[key] for key in keys)
    jets = forward_oneform_ghost_log_radius_jets(
        1, RADII, D, L, PROFILE, H, K
    )
    _assert_tuple_close(
        tuple(jets["base"][key] for key in keys), builder(RADII), 1.0e-12
    )
    _assert_tuple_close(
        tuple(jets["first"][key] for key in keys),
        _first_difference(builder),
        2.0e-9,
    )
    _assert_tuple_close(
        tuple(jets["mixed_second"][key] for key in keys),
        _mixed_difference(builder),
        8.0e-7,
    )


def test_oneform_global_scalar_zero_quotient_is_preserved_by_jets() -> None:
    jets = forward_oneform_ghost_log_radius_jets(
        0, RADII, D, L, PROFILE, H, K
    )
    assert jets["base"]["ghost_operator"].shape == (2, 2)
    assert jets["first"]["ghost_operator"].shape == (2, 2)
    assert jets["mixed_second"]["ghost_operator"].shape == (2, 2)
