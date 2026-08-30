import numpy as np
import pytest

from bhsm.interface.bhsm_standard_model_gauge_vertices import (
    ActionGaugeCoupling,
    GaugeKineticResidue,
    derive_action_gauge_coupling,
    fermion_gauge_vertex,
    multiplet_generators,
    structure_constants,
    su2_fundamental_generators,
    su3_fundamental_generators,
    three_gauge_vertex_color_tensor,
)


def coupling(group: str) -> ActionGaugeCoupling:
    return ActionGaugeCoupling(
        group=group,
        value=2.0,
        action_version="BHSM-TEST",
        background_id="background",
        local_form_factor_id="same-action-local-limit",
        provenance=("retained gauge quadratic response",),
        derived_from_retained_local_form_factor=True,
    )


def test_fundamental_generators_have_canonical_trace_and_lie_brackets() -> None:
    for generators in (su2_fundamental_generators(), su3_fundamental_generators()):
        gram = np.asarray([[np.trace(a @ b) for b in generators] for a in generators])
        np.testing.assert_allclose(gram, 0.5 * np.eye(len(generators)), atol=3.0e-16)
        constants = structure_constants(generators)
        for a, first in enumerate(generators):
            for b, second in enumerate(generators):
                reconstructed = 1j * sum(
                    constants[a, b, c] * generators[c] for c in range(len(generators))
                )
                np.testing.assert_allclose(first @ second - second @ first, reconstructed, atol=5e-16)


def test_bhsm_multiplets_supply_exact_tensor_product_representations() -> None:
    assert multiplet_generators("Q_L", "SU3")[0].shape == (6, 6)
    assert multiplet_generators("Q_L", "SU2")[0].shape == (6, 6)
    np.testing.assert_allclose(multiplet_generators("Q_L", "U1")[0], np.eye(6) / 6.0)
    np.testing.assert_allclose(multiplet_generators("nu_c", "U1")[0], [[0.0]])
    assert len(fermion_gauge_vertex("u_c", coupling("SU3"))) == 8


def test_nonabelian_and_abelian_three_gauge_tensors_are_distinguished() -> None:
    assert np.max(np.abs(three_gauge_vertex_color_tensor(coupling("SU3")))) > 0.0
    assert np.max(np.abs(three_gauge_vertex_color_tensor(coupling("U1")))) == 0.0


def test_non_action_owned_coupling_is_rejected() -> None:
    with pytest.raises(ValueError, match="retained local form factor"):
        ActionGaugeCoupling(
            group="SU2",
            value=0.65,
            action_version="BHSM-TEST",
            background_id="background",
            local_form_factor_id="measured",
            provenance=("external fit",),
            derived_from_retained_local_form_factor=False,
        )


def test_local_lorentzian_kinetic_residue_sets_coupling_without_fit() -> None:
    result = derive_action_gauge_coupling(GaugeKineticResidue(
        group="SU2",
        electric=4.0,
        magnetic=4.0,
        action_version="BHSM-TEST",
        background_id="background",
        local_form_factor_id="local-limit",
        provenance=("same-action quadratic response",),
        local_zero_momentum_limit_derived=True,
    ))
    assert result.value == 0.5


def test_nonlocal_or_non_lorentzian_response_cannot_be_called_a_coupling() -> None:
    residue = GaugeKineticResidue(
        group="SU3",
        electric=2514.17,
        magnetic=813.03,
        action_version="BHSM-TEST",
        background_id="historical-cycle",
        local_form_factor_id="nonlocal-DtN",
        provenance=("retained response seed",),
        local_zero_momentum_limit_derived=False,
    )
    with pytest.raises(RuntimeError, match="nonlocal DtN"):
        derive_action_gauge_coupling(residue)
