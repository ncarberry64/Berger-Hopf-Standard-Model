import numpy as np
import pytest

from bhsm.interface.universal_loop_renormalization import (
    ActionOwnedRenormalizationScheme,
    LaurentCoefficient,
    LinearWardConstraint,
    RegulatedDiagram,
    assemble_renormalized_vertex,
)


def scheme() -> ActionOwnedRenormalizationScheme:
    return ActionOwnedRenormalizationScheme(
        scheme_id="BHSM-action-scheme",
        action_version="BHSM-TEST",
        background_id="background",
        scale_value=2.0,
        scale_dimension="inverse_length",
        scale_provenance=("same-action saddle",),
        derived_from_action=True,
    )


def diagram(
    diagram_id: str,
    kind: str,
    pole: tuple[complex, complex],
    finite: tuple[complex, complex],
) -> RegulatedDiagram:
    return RegulatedDiagram(
        diagram_id=diagram_id,
        sector="fermion-photon",
        loop_order=1,
        contribution_kind=kind,
        coefficients=(
            LaurentCoefficient(-1, np.asarray(pole)),
            LaurentCoefficient(0, np.asarray(finite)),
        ),
        action_version="BHSM-TEST",
        background_id="background",
        provenance=("action expansion",),
    )


def test_complete_same_action_ledger_cancels_poles_and_closes_ward_identity() -> None:
    loop = diagram("loop", "loop", (3.0, -2.0), (0.25, 0.0))
    counterterm = diagram("counterterm", "counterterm", (-3.0, 2.0), (0.75, 0.0))
    ward = LinearWardConstraint(
        "charge-normalization",
        np.asarray([[1.0, 0.0]]),
        np.asarray([1.0]),
        ("BRST master identity",),
    )
    result = assemble_renormalized_vertex(
        [loop, counterterm],
        scheme(),
        [ward],
        complete_diagram_ledger=True,
        complete_counterterm_ledger=True,
        gate7_closed=True,
    )
    result.require_physical_promotion()
    np.testing.assert_allclose(result.finite_value, [1.0, 0.0])
    assert result.maximum_relative_pole_residual == 0.0
    assert result.metadata()["external_observable_target_used"] is False


def test_uncancelled_pole_blocks_physical_promotion() -> None:
    loop = diagram("loop", "loop", (3.0, -2.0), (1.0, 0.0))
    ward = LinearWardConstraint(
        "charge-normalization",
        np.asarray([[1.0, 0.0]]),
        np.asarray([1.0]),
        ("BRST master identity",),
    )
    result = assemble_renormalized_vertex(
        [loop],
        scheme(),
        [ward],
        complete_diagram_ledger=True,
        complete_counterterm_ledger=False,
        gate7_closed=True,
    )
    with pytest.raises(RuntimeError, match="counterterm.*Laurent"):
        result.require_physical_promotion()


def test_observable_fitted_scale_is_rejected() -> None:
    with pytest.raises(ValueError, match="observable-fitted"):
        ActionOwnedRenormalizationScheme(
            scheme_id="bad",
            action_version="BHSM-TEST",
            background_id="background",
            scale_value=1.0,
            scale_dimension="mass",
            scale_provenance=("fit to g-2",),
            derived_from_action=True,
            fitted_to_observable=True,
        )


def test_duplicate_diagram_id_is_rejected_as_double_counting() -> None:
    item = diagram("same", "loop", (0.0, 0.0), (1.0, 0.0))
    with pytest.raises(ValueError, match="double-count"):
        assemble_renormalized_vertex(
            [item, item],
            scheme(),
            [],
            complete_diagram_ledger=True,
            complete_counterterm_ledger=True,
            gate7_closed=True,
        )
