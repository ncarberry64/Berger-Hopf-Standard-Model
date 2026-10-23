"""Independent collar diagnostics; no discontinuous-cell physical sewing claim.

The moving-history fixture gave a 5.7249461737965286e-5 density/leaf
determinant disagreement before explicit face handling, while its internally
constructed normal-mode residual was 2.220513810852149e-16.  The synthetic
smooth fixture separately exposes the sign reversal from sqrt(exp(logJ)).
"""

import numpy as np

from bhsm.interface import muon_sigma_normal_collar_transport as transport
from bhsm.interface.muon_birth_trace_enriched_action import generic_coordinate_lift
from bhsm.interface.muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace
from bhsm.interface.muon_holomorphic_d5_trace_action import d5_sigma_foliation_eta
from bhsm.interface.muon_parent_retarded_hypercharge import WALL


def _coordinates():
    labels = [
        dict(field=field, internal=internal, radial=radial)
        for radial in range(4)
        for field in ("A_tau", "A_rho", "A_1", "A_2", "A_3")
        for internal in range(4)
    ]
    return generic_coordinate_lift(labels)


def _zero_gauge_representation():
    return dict(
        affine_profile_reference_states=np.zeros((2, 98)),
        affine_interior_projection=np.zeros(2),
        affine_wall_coefficient=0.0,
        affine_complement_norm=1.0,
    )


def _sample_cells(arrays, corners, history):
    """The retained face samples are ordered before-side, then after-side."""
    face_by_s = {corner["s"]: corner for corner in corners}
    cells = []
    for index, (s, time) in enumerate(zip(arrays["s"], arrays["coordinate_time"])):
        if s in face_by_s:
            corner = face_by_s[s]
            after = index > 0 and arrays["s"][index - 1] == s
            cells.append(corner["to_cell"] if after else corner["from_cell"])
        else:
            cells.append(history.cell(time))
    return cells


def test_complex_c1_face_density_matches_returned_leaf_only_as_scoped_diagnostic():
    """Keep the executed old failure; a real-linear return is not physical sewing."""
    times = np.array([0.0, 1e-4, 2e-4])
    raw = np.zeros((3, 268), complex)
    raw[:, 0] = [0.0, 0.001, 0.004]
    raw[:, 86] = -0.1 + 0.02j
    raw[:, 98] = 1e-6
    history = transport.CanonicalC1History(times, raw, np.zeros_like(raw), _coordinates())
    full = full_d5_localized_lepton_trace()
    arrays, summary = transport.transport_sigma_normal(
        history, _zero_gauge_representation(), full,
        start_time=8e-5, wall_amplitude=0.8 + 0.02j,
        literal_left_wall_amplitude=0.8 + 0.02j, normal_length=0.015,
    )

    corners = summary["interpolation_corners"]
    assert len(corners) == 1
    corner = corners[0]
    face_time = corner["located_complex_time"]
    np.testing.assert_allclose(face_time.real, times[1], rtol=0, atol=1e-13)
    assert abs(face_time.imag) > 1e-6
    left, _ = history.value(face_time, corner["from_cell"])
    right, _ = history.value(face_time, corner["to_cell"])
    assert np.linalg.norm(right - left) > 1.0
    assert corner["real_linear_face_source_derivative_not_a_holomorphic_physical_sewing"]
    assert summary["partial_integral_not_full_mode_normalization"]
    assert summary["physical_retarded_tail_pole_or_Pauli_selected"] is False
    assert summary["status"] == "BOUNDED_NORMAL_LENGTH"

    start_raw, start_rate = history.value(8e-5)
    wall_geometry = transport.sigma_geometry_point(start_raw, start_rate, WALL)
    wall_radius = wall_geometry["radius"][0]
    determinant_density = []
    independently_evaluated_f = []
    cells = _sample_cells(arrays, corners, history)
    for time, rho, leaf, cell in zip(
        arrays["coordinate_time"], arrays["material_rho"],
        arrays["normal_leaf_transverse"], cells,
    ):
        state, rate = history.value(time, cell)
        c = transport.sigma_geometry_point(state, rate, rho)
        n = d5_sigma_foliation_eta(
            c, gamma=full["gamma5D_particle"], carrier_count=1,
            angular_count=1, sheet_orientation=1,
        )
        lapse, coframe, radius, shift = (
            c[key][0] for key in ("lapse", "radial_coframe", "radius", "coordinate_shift")
        )
        time_velocity = -n["sigma_normal_timelike_component"][0] / lapse
        radial_velocity = -n["sigma_normal_radial_component"][0] / coframe - shift * time_velocity
        determinant = leaf[0] * radial_velocity - leaf[1] * time_velocity
        determinant_density.append(-lapse * coframe * radius**3 * determinant / wall_radius**3)
        independently_evaluated_f.append(c["eta_profile"][0])

    # Independent geometric pullback, not the producer's residual array.
    # The old max error was 5.72e-5; the corrected interpolation diagnostic
    # must agree within accumulated integration error on both retained sides.
    np.testing.assert_allclose(arrays["normal_density"], determinant_density, rtol=0, atol=2e-8)
    sine_ratio = np.sin(independently_evaluated_f) / np.sin(wall_geometry["eta_profile"][0])
    # This squared bilinear identity checks the returned values but does not
    # claim physical normalization or resolve the half-density sign chart.
    np.testing.assert_allclose(
        arrays["normal_mode"]**2 * determinant_density,
        (0.8 + 0.02j)**2 * sine_ratio**2, rtol=0, atol=2e-8,
    )


def test_returned_mode_keeps_analytic_half_density_when_density_winds(monkeypatch):
    """Synthetic smooth kernel: u'=-2*pi*i*u, so u(3/4)=+i*u(0).

    This is a transport-kernel regression, not an action-owned physical
    collar. Its analytic metric has N=C=1 and R(rho)^3=exp[-4*pi*i*(rho-WALL)].
    The exact normal flow is rho=WALL-s and its log density is 4*pi*i*s.
    The former principal sqrt(exp(logJ)) gives -i*u(0) at s=3/4.
    """
    def smooth_geometry(raw, raw_time, rho):
        radius = np.exp(-(4j * np.pi / 3) * (rho - WALL))
        values = dict(
            lapse=1.0, radial_coframe=1.0, radius=radius, coordinate_shift=0.0,
            volume_density=radius**3, lapse_log_radial=0.0,
            radial_coframe_log_radial=0.0, radius_log_radial=-4j * np.pi / 3,
            coordinate_shift_radial=0.0, sigma_radial=1.0,
            sigma_radial_second=0.0, sigma_coordinate_time=0.0,
            eta_profile=np.pi / 4, eta_profile_radial=0.0,
            eta_profile_coordinate_time=0.0,
        )
        c = {key: np.array([value], complex) for key, value in values.items()}
        c.update({key + "_first": np.zeros((1, 1), complex) for key in values})
        return c

    monkeypatch.setattr(transport, "sigma_geometry_point", smooth_geometry)
    monkeypatch.setattr(
        transport, "_fixed_radial_maps",
        lambda rep, rho: (np.zeros(4, complex), np.zeros(4, complex)),
    )
    raw = np.zeros((2, 268), complex)
    history = transport.CanonicalC1History([0.0, 1.0], raw, raw, _coordinates())
    wall_amplitude, left_amplitude = 0.8 + 0.02j, 0.6 - 0.3j
    arrays, summary = transport.transport_sigma_normal(
        history, {}, full_d5_localized_lepton_trace(), start_time=0.5,
        wall_amplitude=wall_amplitude, literal_left_wall_amplitude=left_amplitude,
        normal_length=0.75,
    )
    phase = np.cos(2 * np.pi * arrays["s"]) - 1j * np.sin(2 * np.pi * arrays["s"])
    # Exact solution of the independently specified ODE, evaluated on the
    # returned mesh; no internally constructed mode-residual is consulted.
    np.testing.assert_allclose(arrays["normal_mode"], wall_amplitude * phase, rtol=0, atol=2e-9)
    np.testing.assert_allclose(arrays["literal_left_normal_mode"], left_amplitude * phase, rtol=0, atol=2e-9)
    np.testing.assert_allclose(arrays["normal_mode"][-1], 1j * wall_amplitude, rtol=0, atol=2e-9)
    np.testing.assert_allclose(arrays["partial_mode_norm"], left_amplitude * wall_amplitude * 0.75, rtol=0, atol=2e-9)
    assert not summary["interpolation_corners"]
    assert summary["partial_integral_not_full_mode_normalization"]
    assert summary["physical_retarded_tail_pole_or_Pauli_selected"] is False
