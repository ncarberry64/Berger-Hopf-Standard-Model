import jax
import jax.numpy as jnp
import numpy as np

from bhsm.interface.universal_physical_action_expansion import (
    JaxDirectionalActionOracle,
    PhysicalActionExpansion,
    PhysicalBackground,
)
from bhsm.interface.universal_quadratic_spectrum import QuadraticDescriptorPencil
from bhsm.interface.universal_vertex_amplitude import (
    BareVertexGenerator,
    TreeAmplitudeAssembler,
)


jax.config.update("jax_enable_x64", True)


def action(x):
    return 0.5 * (2.0 * x[0] ** 2 + 3.0 * x[1] ** 2) + x[0] ** 2 * x[1] + 0.5 * x[0] ** 2 * x[1] ** 2


def assembler() -> TreeAmplitudeAssembler:
    background = PhysicalBackground(
        state=np.asarray([0.0, 0.0]),
        physical_frame=np.eye(2),
        action_version="TEST-ACTION",
        background_id="test-background",
        gate7_closed=False,
    )
    expansion = PhysicalActionExpansion(JaxDirectionalActionOracle(action), background)
    pencil = QuadraticDescriptorPencil(
        constant=np.diag([2.0, 3.0]),
        linear=np.eye(2),
        action_version="TEST-ACTION",
        background_id="test-background",
        domain_id="test-domain",
        gate7_closed=False,
        quotient_applied=True,
        brst_cancellation_accounted=False,
    )
    return TreeAmplitudeAssembler(pencil, BareVertexGenerator(expansion))


def test_tree_channel_uses_action_cubic_quartic_and_linear_solve() -> None:
    result = assembler()
    e0 = np.asarray([1.0, 0.0])
    e1 = np.asarray([0.0, 1.0])
    amplitude = result.four_point_channel((e0, e1, e0, e1), 1.0, channel="s")
    # S3(e0,e1,e0)=2 and S4(e0,e1,e0,e1)=2.  The internal
    # symbol at z=1 is diag(3,4), so exchange=2*(1/3)*2=4/3.
    assert abs(amplitude.contact - 2.0) < 1.0e-12
    assert abs(amplitude.exchange - 4.0 / 3.0) < 1.0e-12
    assert abs(amplitude.total - 10.0 / 3.0) < 1.0e-12
    assert amplitude.linear_solve_relative_residual < 1.0e-14
    assert result.metadata()["explicit_matrix_inverse_formed"] is False


def test_crossed_ordering_is_supplied_explicitly() -> None:
    result = assembler()
    e0 = np.asarray([1.0, 0.0])
    e1 = np.asarray([0.0, 1.0])
    direct = result.four_point_channel((e0, e0, e1, e1), 1.0, channel="s")
    crossed = result.four_point_channel((e0, e1, e0, e1), 1.0, channel="t")
    assert direct.channel == "s"
    assert crossed.channel == "t"
    assert np.isfinite(crossed.total)
