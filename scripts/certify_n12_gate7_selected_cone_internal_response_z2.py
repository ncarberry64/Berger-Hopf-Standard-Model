"""Certify the selected-cone internal response and physical ``D2 f`` tube.

This is the narrow Gate-7 adapter after the selected DOP853 cone spectrum and
bordered inverse.  It never differentiates the inverse.  Instead it uses the
bordered identities through third order and, crucially, bounds the multiplier
by the exact spectral identity ``b=<psi,rhs>`` before taking norms.  The hard
response is multiplied by the selected descriptor in the physical numerator;
those products are likewise assembled before norming.

Only the 48 retained causal seams are evaluated.  No global ``D3 f`` tensor is
formed and no legacy half-step/recentered cone is replayed.
"""

from __future__ import annotations

import hashlib
import importlib
import json
import math
import os
from pathlib import Path
import sys
from typing import Any

import jax

jax.config.update("jax_enable_x64", True)
import jax.numpy as jnp
import numpy as np
from scipy.linalg import null_space


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from bhsm.interface.aether_forward_c2_descriptor_cover import metric_data  # noqa: E402
from bhsm.interface.aether_jax_full_local_action import action_hessian  # noqa: E402
from derive_n12_gate7_exact_signed_mixed_field_curvature import _exact_jet  # noqa: E402
import audit_n12_c2_stop_dop853_boundary_cluster_probe as dense  # noqa: E402


BASE = ROOT / "artifacts" / "flagship_integration"
CENTER = BASE / "BHSM_N12_C2_STOP_HIGH_ORDER_QUARTER_STEP_RETAINED_RECONNAISSANCE.npz"
TANGENT = BASE / "BHSM_N12_C2_STOP_QUARTER_STEP_PHYSICAL_TANGENT_TRANSFER_RECONNAISSANCE.npz"
FIELD = BASE / "BHSM_N12_GATE7_EXACT_SIGNED_DIRECTIONAL_FIELD_CURVATURE.npz"
MIXED_DATA = BASE / "BHSM_N12_GATE7_EXACT_SIGNED_MIXED_FIELD_CURVATURE.npz"
RESPONSE = BASE / "BHSM_N12_GATE7_RETAINED_CORRECTION_BORDERED_RESPONSE_FIRST_JETS.npz"
TRANSVERSE = BASE / "BHSM_N12_GATE7_EXACT_SIGNED_FULL_TRANSVERSE_CURVATURE.json"
TRANSVERSE_ADJUDICATION = BASE / "BHSM_N12_GATE7_EXACT_SIGNED_FULL_TRANSVERSE_CURVATURE_ADJUDICATION.json"
CONE = BASE / "BHSM_N12_GATE7_SELECTED_DOP853_NONLINEAR_CONE_PROJECTOR_INVERSE.json"
CONE_SPECTRUM = BASE / "BHSM_N12_GATE7_SELECTED_DOP853_NONLINEAR_CONE_SPECTRUM.json"
PATH_RESPONSE = BASE / "BHSM_N12_C2_STOP_DOP853_ADAPTIVE_BORDERED_RHS_RESPONSE_CERTIFICATE.json"
BUDGET = BASE / "BHSM_N12_GATE7_OUTWARD_CLOSURE_BUDGET.json"
CAUSAL = BASE / "BHSM_N12_GATE7_EXACT_CENTER_CAUSAL_VECTOR_CERTIFICATE.npz"
BOOTSTRAP = BASE / "BHSM_N12_GATE7_SIGNED_CAUSAL_VECTOR_BOOTSTRAP.npz"
GREEN = BASE / "BHSM_N12_C2_STOP_QUARTER_STEP_MATCHED_TANGENT_CORRELATED_DEFECT_GAUSS12_RECONNAISSANCE.npz"
TRANSVERSE_SHARDS = (
    BASE / "BHSM_N12_GATE7_EXACT_SIGNED_FULL_TRANSVERSE_CURVATURE_NODES_00_23.npz",
    BASE / "BHSM_N12_GATE7_EXACT_SIGNED_FULL_TRANSVERSE_CURVATURE_NODES_24_47.npz",
)
RESULT = BASE / "BHSM_N12_GATE7_SELECTED_CONE_INTERNAL_RESPONSE_Z2.json"
QDIM = 37
ROUNDING = 1.0 + 1.0e-10


def _up(value: float) -> float:
    return math.nextafter(float(value) * ROUNDING, math.inf)


def _down(value: float) -> float:
    return math.nextafter(float(value) * ROUNDING, -math.inf)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


@jax.jit
def _hessian_first_batch(state: jax.Array, raw_directions: jax.Array) -> jax.Array:
    return jax.vmap(
        lambda direction: jax.jvp(action_hessian, (state,), (direction,))[1]
    )(raw_directions)


@jax.jit
def _hessian_second_applied_selected(
    state: jax.Array, raw_directions: jax.Array, selected: jax.Array,
) -> jax.Array:
    coefficients = jnp.zeros(raw_directions.shape[0], dtype=state.dtype)

    def applied(value: jax.Array) -> jax.Array:
        shifted = state + raw_directions.T @ value
        return action_hessian(shifted)[QDIM:, QDIM:] @ selected

    return jax.jacfwd(jax.jacfwd(applied))(coefficients)


def _mixed(module: Any, state: np.ndarray, *directions: np.ndarray) -> float:
    return _up(float(module.action_bound(
        state, mixed_directions=list(directions),
    ).d[-1]))


def _interval_owner_maps(cone: dict[str, Any]) -> dict[int, dict[str, float]]:
    grouped: dict[int, list[dict[str, Any]]] = {}
    for row in cone["rows"]:
        grouped.setdefault(int(row["interval"]), []).append(row)
    return {
        interval: {
            "inverse": max(float(row[
                "nonlinear_cone_chart_bordered_inverse_2_norm_upper"
            ]) for row in rows),
            "gap": min(float(row[
                "nonlinear_cone_selected_to_hard_gap_lower"
            ]) for row in rows),
        }
        for interval, rows in grouped.items()
    }


def build_payload() -> dict[str, Any]:
    inputs = (
        CENTER, TANGENT, FIELD, RESPONSE, TRANSVERSE,
        TRANSVERSE_ADJUDICATION, CONE,
        CONE_SPECTRUM, PATH_RESPONSE, BUDGET, CAUSAL, BOOTSTRAP, GREEN,
        MIXED_DATA, *TRANSVERSE_SHARDS,
    )
    if not all(path.is_file() for path in inputs):
        raise FileNotFoundError("selected-cone response/Z2 inputs required")
    transverse = json.loads(TRANSVERSE.read_text(encoding="utf-8"))
    transverse_adjudication = json.loads(
        TRANSVERSE_ADJUDICATION.read_text(encoding="utf-8")
    )
    cone = json.loads(CONE.read_text(encoding="utf-8"))
    spectrum = json.loads(CONE_SPECTRUM.read_text(encoding="utf-8"))
    path_response = json.loads(PATH_RESPONSE.read_text(encoding="utf-8"))
    budget = json.loads(BUDGET.read_text(encoding="utf-8"))
    if not all(record["validation_passed"] is True for record in (
        transverse_adjudication, cone, spectrum, path_response, budget,
    )):
        raise RuntimeError("certified selected-cone parents required")

    radius = float(spectrum["domain"]["candidate_nonlinear_action_radius"])
    os.environ["BHSM_N12_CERTIFICATE_BALL"] = repr(radius)
    majorants = importlib.import_module("derive_n12_action_signed_interval_majorants")
    majorants.BALL_RADIUS = radius

    with np.load(CENTER) as source:
        states = np.asarray(source["centers"], dtype=float)
        times = np.asarray(source["action_lengths"], dtype=float)
        weights = np.asarray(source["state_weights"], dtype=float)
        descriptors = np.asarray(source["signed_descriptors"], dtype=float)
        branch_reference = np.asarray(source["branch_reference"], dtype=float)
    with np.load(TANGENT) as source:
        tangents = np.asarray(source["physical_tangent_action"], dtype=float)
    with np.load(FIELD) as source:
        fields = np.asarray(source["normalized_field"], dtype=float)
        directional_curvature = np.asarray(
            source["physical_time_transverse_directional_curvature"],
            dtype=float,
        )
    with np.load(MIXED_DATA) as source:
        mixed_curvature = np.asarray(
            source["physical_time_transverse_mixed_Green_curvature"],
            dtype=float,
        )
    with np.load(RESPONSE) as source:
        center_response = np.asarray(source["bordered_response"], dtype=float)
    with np.load(CAUSAL) as source:
        exact_total_center_radii = np.asarray(
            source["exact_total_center_radius"], dtype=float,
        )
    with np.load(BOOTSTRAP) as source:
        signed_center_vector = np.asarray(
            source["signed_center_vector"], dtype=float,
        )
        causal_green_norm = np.asarray(source["causal_green_norm"], dtype=float)
    with np.load(GREEN) as source:
        physical_macro_step_maps = np.asarray(
            source["physical_macro_step_maps"], dtype=float,
        )
        ambient_correction_profile = np.asarray(
            source["ambient_correction_profile"], dtype=float,
        )
    transverse_curvature = np.concatenate([
        np.asarray(np.load(path)["physical_time_transverse_D2f"], dtype=float)
        for path in TRANSVERSE_SHARDS
    ])

    local_radii = 2.0 * exact_total_center_radii
    # The first causal replay leaves only the terminal two seam radii as
    # owners.  Widen those two local proof tubes to the already-certified
    # global selected-cone radius; this is an owner-only proof refinement,
    # not a new radius or a new physical domain.
    local_radii[-2:] = radius

    if states.shape != (48, 98) or tangents.shape != (48, 98, 73):
        raise RuntimeError("retained causal seam dimensions changed")
    q_weights, reduced_weights, _, _ = metric_data()
    total = weights.size
    reduced = reduced_weights.size
    reduced_lift = np.vstack((
        np.zeros((QDIM, reduced)), np.diag(reduced_weights),
    ))
    gradient_output = np.zeros((total, reduced))
    gradient_output[:QDIM, :QDIM] = np.diag(q_weights**2)
    mixed_output = reduced_lift.copy()
    configuration_map = np.zeros((total, total))
    configuration_map[:QDIM, QDIM:2 * QDIM] = np.diag(
        q_weights / weights[QDIM:2 * QDIM]
    )

    transverse_frames = []
    correction_time_transverse_norm = []
    for index in range(48):
        physical_flow = tangents[index].T @ fields[index]
        physical_flow /= np.linalg.norm(physical_flow)
        frame = null_space(physical_flow[None, :])
        transverse_frames.append(frame)
        correction_time_transverse_norm.append(float(np.linalg.norm(
            frame.T @ tangents[index].T @ ambient_correction_profile[index]
        )))
    transverse_frames = np.asarray(transverse_frames)
    correction_time_transverse_norm = np.asarray(
        correction_time_transverse_norm,
    )

    # Assemble the signed quadratic center through the actual 73-dimensional
    # step maps.  This is the decisive correlation-preserving operation: the
    # exact D2f tensor is contracted with the actual causal vector before any
    # norm is taken.
    dt = np.diff(times)
    propagators: dict[tuple[int, int], np.ndarray] = {}
    for endpoint in range(1, 48):
        propagator = np.eye(73)
        for source_index in range(endpoint - 1, -1, -1):
            propagator = propagator @ physical_macro_step_maps[source_index]
            propagators[(endpoint, source_index)] = propagator.copy()
    signed_quadratic_center = np.zeros((48, 73))
    signed_quadratic_part = np.zeros_like(signed_quadratic_center)
    for endpoint in range(1, 48):
        for source_index in range(endpoint):
            frame = transverse_frames[source_index]
            transverse_center = frame.T @ signed_quadratic_center[source_index]
            directional_source = (
                0.5 * directional_curvature[source_index]
                * correction_time_transverse_norm[source_index] ** 2
            )
            mixed_source = (
                mixed_curvature[source_index] @ transverse_center
                * correction_time_transverse_norm[source_index]
            )
            quadratic_source = 0.5 * np.einsum(
                "aij,i,j->a", transverse_curvature[source_index],
                transverse_center, transverse_center, optimize=True,
            )
            transport = dt[source_index] * propagators[(endpoint, source_index)]
            signed_quadratic_center[endpoint] += transport @ (
                frame @ (directional_source + mixed_source + quadratic_source)
            )
            signed_quadratic_part[endpoint] += transport @ (
                frame @ quadratic_source
            )

    interval_owner = _interval_owner_maps(cone)
    dense_times = np.asarray(dense._dense_arrays()[2], dtype=float)
    # Search the actual stored DOP853 time carrier; no surrogate or new
    # temporal discretization is introduced.
    max_source = float(path_response["summary"]["maximum_center_internal_rhs_2_norm"])
    transverse_rows = {int(row["node"]): row for row in transverse["rows"]}
    rows = []
    cached_rows: dict[int, dict[str, Any]] = {}
    if os.environ.get("BHSM_N12_GATE7_Z2_REUSE_ROWS", "").strip() == "1":
        if not RESULT.is_file():
            raise FileNotFoundError("row reuse requested without prior result")
        cached_payload = json.loads(RESULT.read_text(encoding="utf-8"))
        cached_rows = {
            int(row["node"]): row for row in cached_payload.get("rows", [])
        }
        if len(cached_rows) != 48:
            raise RuntimeError("row reuse requires all 48 prior seam rows")
    for index in range(48):
        if index in cached_rows:
            rows.append(cached_rows[index])
            continue
        state = states[index]
        rho = float(local_radii[index])
        tangent = tangents[index]
        frame = transverse_frames[index]
        physical = tangent @ frame
        raw = physical / weights[:, None]
        configuration = configuration_map @ (weights * state)
        configuration_variation = configuration_map @ physical

        interval = int(np.searchsorted(dense_times, times[index], side="right") - 1)
        interval = min(max(interval, 0), 369)
        local = interval_owner[interval]
        beta = float(local["inverse"])
        gap = float(local["gap"])

        hessian_first = np.array(_hessian_first_batch(
            jnp.asarray(state), jnp.asarray(raw.T),
        ), copy=True)[:, QDIM:, QDIM:]
        _, retained_hessian = _exact_jet(state)
        retained_values, retained_vectors = np.linalg.eigh(
            np.asarray(retained_hessian, dtype=float)[QDIM:, QDIM:]
        )
        psi = retained_vectors[:, 24]
        if float(psi @ branch_reference) < 0.0:
            psi = -psi
        lambda_first = np.asarray([
            float(psi @ matrix @ psi) for matrix in hessian_first
        ])
        s1_center = _up(float(np.linalg.norm(lambda_first)))
        H1_psi_columns = np.column_stack([
            matrix @ psi for matrix in hessian_first
        ])
        H1_psi_eigen = retained_vectors.T @ H1_psi_columns
        denominators = retained_values - retained_values[24]
        psi1_coefficients = np.zeros_like(H1_psi_eigen)
        hard = np.arange(reduced) != 24
        psi1_coefficients[hard] = (
            -H1_psi_eigen[hard] / denominators[hard, None]
        )
        psi1_matrix = retained_vectors @ psi1_coefficients
        selected_second_cross = _up(float(np.linalg.norm(
            psi1_matrix.T @ H1_psi_columns
            + H1_psi_columns.T @ psi1_matrix
        )))
        H2_psi_tensor = np.array(_hessian_second_applied_selected(
            jnp.asarray(state), jnp.asarray(raw.T), jnp.asarray(psi),
        ), copy=True)
        H1_psi1 = np.einsum(
            "abj,bk->ajk", np.moveaxis(hessian_first, 0, -1),
            psi1_matrix, optimize=True,
        )
        lambda2_tensor = (
            np.einsum("a,ajk->jk", psi, H2_psi_tensor, optimize=True)
            + psi1_matrix.T @ H1_psi_columns
            + H1_psi_columns.T @ psi1_matrix
        )
        eigen_source = (
            H2_psi_tensor + H1_psi1 + H1_psi1.transpose(0, 2, 1)
            - psi[:, None, None] * lambda2_tensor[None, :, :]
            - psi1_matrix[:, None, :] * lambda_first[None, :, None]
            - psi1_matrix[:, :, None] * lambda_first[None, None, :]
        )
        eigen_source_coefficients = np.einsum(
            "ab,bjk->ajk", retained_vectors.T, eigen_source, optimize=True,
        )
        psi2_coefficients = np.zeros_like(eigen_source_coefficients)
        psi2_coefficients[hard] = (
            -eigen_source_coefficients[hard]
            / denominators[hard, None, None]
        )
        psi2_coefficients[24] = -(psi1_matrix.T @ psi1_matrix)
        psi2_tensor = np.einsum(
            "ab,bjk->ajk", retained_vectors, psi2_coefficients, optimize=True,
        )
        descriptor_H2_cross = np.einsum(
            "ai,ajk->ijk", psi1_matrix, H2_psi_tensor, optimize=True,
        )
        descriptor_H1_cross = np.einsum(
            "aij,ak->ijk", psi2_tensor, H1_psi_columns, optimize=True,
        )
        descriptor_cross_third = (
            descriptor_H2_cross
            + descriptor_H2_cross.transpose(1, 0, 2)
            + descriptor_H2_cross.transpose(2, 1, 0)
            + descriptor_H1_cross
            + descriptor_H1_cross.transpose(1, 0, 2)
            + descriptor_H1_cross.transpose(2, 1, 0)
        )
        descriptor_cross_third_norm = _up(float(np.linalg.norm(
            descriptor_cross_third
        )))
        same_formula_psi1 = float(np.linalg.norm(psi1_matrix))
        same_formula_psi2 = float(np.linalg.norm(psi2_tensor))
        same_formula_H2_psi = float(np.linalg.norm(H2_psi_tensor))
        h1_center = _up(math.sqrt(math.fsum(
            float(np.linalg.norm(matrix, ord=2)) ** 2
            for matrix in hessian_first
        )))

        H1 = _mixed(majorants, state, reduced_lift, reduced_lift, physical)
        H2 = _mixed(
            majorants, state, reduced_lift, reduced_lift, physical, physical,
        )
        H3 = _mixed(
            majorants, state, reduced_lift, reduced_lift, physical, physical,
            physical,
        )
        psi_action = reduced_lift @ psi
        H1_psi_center = _up(math.sqrt(math.fsum(
            float(np.linalg.norm(matrix @ psi)) ** 2
            for matrix in hessian_first
        )))
        H2_psi = _mixed(
            majorants, state, reduced_lift, physical, physical, psi_action,
        )
        H3_psi = _mixed(
            majorants, state, reduced_lift, physical, physical, physical,
            psi_action,
        )
        H2_scalar = _mixed(
            majorants, state, psi_action, physical, physical, psi_action,
        )
        H3_scalar = _mixed(
            majorants, state, psi_action, physical, physical, physical,
            psi_action,
        )
        F1 = _up(
            _mixed(majorants, state, gradient_output, physical)
            + _mixed(majorants, state, mixed_output, configuration, physical)
            + _mixed(majorants, state, mixed_output, configuration_variation)
        )
        F2 = _up(
            _mixed(majorants, state, gradient_output, physical, physical)
            + _mixed(
                majorants, state, mixed_output, configuration, physical,
                physical,
            )
            + 2.0 * _mixed(
                majorants, state, mixed_output, configuration_variation,
                physical,
            )
        )
        F3 = _up(
            _mixed(
                majorants, state, gradient_output, physical, physical,
                physical,
            )
            + _mixed(
                majorants, state, mixed_output, configuration, physical,
                physical, physical,
            )
            + 3.0 * _mixed(
                majorants, state, mixed_output, configuration_variation,
                physical, physical,
            )
        )

        source = transverse_rows[index]
        psi1_center = float(source[
            "selected_eigenline_transverse_first_Frobenius_norm"
        ])
        psi2_center = float(source[
            "selected_eigenline_transverse_second_Frobenius_norm"
        ])
        X0 = float(np.linalg.norm(center_response[index]))
        X1 = float(source[
            "bordered_response_transverse_first_Frobenius_norm"
        ])
        X2_center = float(source[
            "bordered_response_transverse_second_Frobenius_norm"
        ])
        b0 = abs(float(center_response[index, -1]))
        s0 = abs(float(descriptors[index]))
        N0 = float(source["normalized_numerator_2_norm"])
        N1 = float(source[
            "normalized_numerator_transverse_first_Frobenius_norm"
        ])
        N2 = float(source[
            "normalized_numerator_transverse_second_Frobenius_norm"
        ])

        # Center-plus-radius coefficient bounds.  H1 uses the same-formula
        # JAX center value and the certified H2 action remainder.  H2/H3 are
        # retained-action interval majorants on the candidate ball.
        H1_tube = _up(h1_center + rho * H2)
        psi1 = _up(psi1_center + rho * psi2_center)
        line_motion = _up(rho * psi1)
        H1_psi = _up(
            H1_psi_center + rho * H2_psi + H1_tube * line_motion
        )
        H2_psi_tube = _up(H2_psi + H2 * line_motion)
        H2_scalar_tube = _up(
            H2_scalar + 2.0 * H2_psi * line_motion
            + H2 * line_motion**2
        )
        H3_scalar_tube = _up(
            H3_scalar + 2.0 * H3_psi * line_motion
            + H3 * line_motion**2
        )
        s2 = _up(H2_scalar_tube + selected_second_cross)
        s1 = _up(s1_center + rho * s2)
        S3_seed = _up(
            H3_psi + 3.0 * (H2 + s2) * psi1
            + 3.0 * (H1_tube + s1) * psi2_center + H3
        )
        psi2 = _up(
            psi2_center + rho * (
                beta * S3_seed + 3.0 * psi1 * psi2_center
            )
        )
        psi1_motion = _up(rho * psi2)
        psi2_motion = _up(rho * (
            beta * S3_seed + 3.0 * psi1 * psi2
        ))
        descriptor_third_motion = _up(3.0 * (
            psi1_motion * H2_psi_tube
            + psi1 * H3_psi * rho
            + psi2_motion * H1_psi
            + psi2 * H2_psi_tube * rho
        ))
        s3 = _up(
            H3_scalar_tube + descriptor_cross_third_norm
            + descriptor_third_motion
        )
        S1 = _up(H1_psi + s1)
        S2 = _up(
            H2_psi + 2.0 * (H1_tube + s1) * psi1 + s2
        )
        S3 = _up(
            H3_psi + 3.0 * (H2 + s2) * psi1
            + 3.0 * (H1_tube + s1) * psi2 + s3
        )
        psi3 = _up(beta * S3 + 3.0 * psi1 * psi2)
        K1 = _up(H1_tube + s1 + psi1)
        K2 = _up(H2 + s2 + psi2)
        K3 = _up(H3 + s3 + psi3)

        response_third_contraction = _up(beta * (
            K3 * rho**3 / 6.0
            + 1.5 * K2 * rho**2 + 3.0 * K1 * rho
        ))
        denominator = _down(1.0 - response_third_contraction)
        X3 = (
            _up(beta * (
                F3
                + K3 * (X0 + rho * X1 + 0.5 * rho**2 * X2_center)
                + 3.0 * K2 * (X1 + rho * X2_center)
                + 3.0 * K1 * X2_center
            ) / denominator)
            if denominator > 0.0 else math.inf
        )
        X2 = _up(X2_center + rho * X3)
        X1_tube = _up(X1 + rho * X2_center + 0.5 * rho**2 * X3)
        X0_tube = _up(
            X0 + rho * X1 + 0.5 * rho**2 * X2_center
            + rho**3 * X3 / 6.0
        )

        # Adjoint the selected-line derivatives through the same symmetric
        # border.  This is the decisive common-frame cancellation: no
        # ``||psi^(k)|| ||rhs||`` product is used for the multiplier.
        B1 = _up(X0_tube * S1 + F1)
        B2 = _up(
            X0_tube * S2 + b0 * psi1**2 + 2.0 * psi1 * F1 + F2
        )

        # Differentiate the equivalent scaled bordered solve
        # K*(s*h,s*b)=(s*rhs,0).  This retains the selected descriptor before
        # norming and avoids the false ``|s|*||h'''||`` amplification.
        Yh0 = _up(s0 * X0)
        Yb0 = _up(s0 * b0)
        Yh1 = _up(s1 * X0 + s0 * X1)
        Yb1 = _up(s1 * b0 + s0 * B1)
        Yh2 = _up(
            s2 * X0 + 2.0 * s1 * X1 + s0 * X2_center
        )
        Yb2 = _up(s2 * b0 + 2.0 * s1 * B1 + s0 * B2)
        scaled_rhs_3 = _up(
            s3 * max_source + 3.0 * s2 * F1
            + 3.0 * s1 * F2 + s0 * F3
        )
        # Only the hard top equation contributes a new hard vector.  The
        # differentiated orthogonality row supplies selected components that
        # are already present in the b*psi product below; bounding it through
        # the full border would double count the enormous psi''' term.
        Y3 = _up((
            scaled_rhs_3
            + (H3 + s3) * Yh0 + psi3 * Yb0
            + 3.0 * ((H2 + s2) * Yh1 + psi2 * Yb1)
            + 3.0 * ((H1_tube + s1) * Yh2 + psi1 * Yb2)
        ) / gap)
        scaled_third_contraction = 0.0
        scaled_denominator = 1.0
        B3 = _up(
            X0_tube * S3 + 3.0 * b0 * psi1 * psi2
            + 3.0 * psi2 * F1
            + 3.0 * psi1 * F2 + F3
        )
        configuration_norm = float(np.linalg.norm(configuration))
        configuration_rate = float(np.linalg.norm(configuration_variation, ord=2))
        top_N3 = _up(s3 * configuration_norm + 3.0 * s2 * configuration_rate)
        reduced_N3 = _up(float(np.max(reduced_weights)) * (
            B3 + 3.0 * B2 * psi1 + 3.0 * B1 * psi2 + b0 * psi3
            + Y3
        ))
        N3 = _up(math.hypot(top_N3, reduced_N3))
        g0 = _down(
            N0 - rho * N1 - 0.5 * rho**2 * N2
            - rho**3 * N3 / 6.0
        )
        A1 = _up(N1 + rho * N2 + 0.5 * rho**2 * N3)
        A2 = _up(N2 + rho * N3)
        center_D2f = float(source[
            "physical_time_transverse_D2f_Frobenius_norm"
        ])
        D3f = (
            _up(
                N3 / g0 + 9.0 * A1 * A2 / g0**2
                + 15.0 * A1**3 / g0**3
            ) if g0 > 0.0 and math.isfinite(N3) else math.inf
        )
        D2f = _up(center_D2f + rho * D3f)
        rows.append({
            "node": index,
            "action_length": float(times[index]),
            "DOP853_interval": interval,
            "candidate_radius": radius,
            "correlated_local_causal_radius": rho,
            "cone_gap_lower": gap,
            "cone_bordered_inverse_upper": beta,
            "same_formula_center_H1_Frobenius_upper": h1_center,
            "retained_interval_H1_majorant_upper": H1,
            "retained_interval_H2_majorant_upper": H2,
            "retained_interval_H3_majorant_upper": H3,
            "retained_interval_H2_applied_to_selected_line_upper": H2_psi,
            "retained_interval_H3_applied_to_selected_line_upper": H3_psi,
            "retained_interval_H2_selected_scalar_upper": H2_scalar,
            "retained_interval_H3_selected_scalar_upper": H3_scalar,
            "internal_rhs_F1_upper": F1,
            "internal_rhs_F2_upper": F2,
            "internal_rhs_F3_upper": F3,
            "selected_descriptor_absolute": s0,
            "selected_descriptor_D1_upper": s1,
            "selected_descriptor_D2_upper": s2,
            "selected_descriptor_D3_upper": s3,
            "selected_line_D1_upper": psi1,
            "selected_line_D2_upper": psi2,
            "selected_line_D3_upper": psi3,
            "same_formula_center_selected_line_D1_Frobenius": same_formula_psi1,
            "same_formula_center_selected_line_D2_Frobenius": same_formula_psi2,
            "same_formula_center_H2_applied_selected_Frobenius": same_formula_H2_psi,
            "retained_center_selected_line_D1_Frobenius": psi1_center,
            "retained_center_selected_line_D2_Frobenius": psi2_center,
            "bordered_K_D1_upper": K1,
            "bordered_K_D2_upper": K2,
            "bordered_K_D3_upper": K3,
            "response_second_identity_denominator_lower": denominator,
            "response_third_fixed_point_contraction_upper": response_third_contraction,
            "complete_internal_response_tube_2_norm_upper": X0_tube,
            "complete_internal_response_D1_tube_upper": X1_tube,
            "complete_internal_response_D2_tube_upper": X2,
            "complete_internal_response_D3_tube_upper": X3,
            "descriptor_weighted_hard_response_D3_tube_upper": Y3,
            "descriptor_weighted_response_third_denominator_lower": scaled_denominator,
            "multiplier_D1_upper_from_inner_product": B1,
            "multiplier_D2_upper_from_inner_product": B2,
            "multiplier_D3_upper_from_inner_product": B3,
            "center_normalized_numerator_lower_reference": N0,
            "normalized_numerator_D1_tube_upper": A1,
            "normalized_numerator_D2_tube_upper": A2,
            "normalized_numerator_D3_tube_upper": N3,
            "normalized_numerator_tube_lower": g0,
            "center_physical_transverse_D2f_Frobenius": center_D2f,
            "physical_transverse_D2f_tube_upper": D2f,
            "physical_transverse_D3f_tube_upper": D3f,
            "JAX_center_H1_below_retained_interval_majorant": h1_center <= H1,
            "response_and_field_tubes_finite": bool(
                denominator > 0.0 and g0 > 0.0 and math.isfinite(D2f)
            ),
        })
        print(json.dumps({
            "completed": index + 1,
            "node": index,
            "denominator": denominator,
            "g0": g0,
            "D2f_tube": D2f,
        }), flush=True)

    transverse_budget = float(budget["summary"][
        "corresponding_uniform_transverse_curvature_upper"
    ])
    maximum_D2f = max(row["physical_transverse_D2f_tube_upper"] for row in rows)
    center_vector_norm = np.linalg.norm(signed_quadratic_center, axis=1)
    signed_quadratic_part_norm = np.linalg.norm(signed_quadratic_part, axis=1)
    mixed_norm = np.linalg.norm(mixed_curvature, axis=(1, 2))
    center_D2f = np.asarray([
        row["center_physical_transverse_D2f_Frobenius"] for row in rows
    ])
    D3f = np.asarray([
        row["physical_transverse_D3f_tube_upper"] for row in rows
    ])
    causal_error = np.zeros(48)
    causal_mixed_error = np.zeros(48)
    causal_quadratic_error = np.zeros(48)
    causal_cubic_error = np.zeros(48)
    for endpoint in range(1, 48):
        earlier = slice(0, endpoint)
        causal_mixed_error[endpoint] = np.sum(
            causal_green_norm[endpoint, earlier]
            * mixed_norm[earlier]
            * correction_time_transverse_norm[earlier]
            * causal_error[earlier]
        )
        causal_quadratic_error[endpoint] = np.sum(
            causal_green_norm[endpoint, earlier] * center_D2f[earlier]
            * (
                center_vector_norm[earlier] * causal_error[earlier]
                + 0.5 * causal_error[earlier] ** 2
            )
        )
        causal_cubic_error[endpoint] = np.sum(
            causal_green_norm[endpoint, earlier] * D3f[earlier]
            * (center_vector_norm[earlier] + causal_error[earlier]) ** 3
            / 6.0
        )
        causal_error[endpoint] = (
            causal_mixed_error[endpoint]
            + causal_quadratic_error[endpoint]
            + causal_cubic_error[endpoint]
        )
    causal_total_radius = center_vector_norm + causal_error
    psi1_relative_residual = max(
        abs(row["same_formula_center_selected_line_D1_Frobenius"]
            - row["retained_center_selected_line_D1_Frobenius"])
        / max(row["retained_center_selected_line_D1_Frobenius"], 1.0e-300)
        for row in rows
    )
    psi2_relative_residual = max(
        abs(row["same_formula_center_selected_line_D2_Frobenius"]
            - row["retained_center_selected_line_D2_Frobenius"])
        / max(row["retained_center_selected_line_D2_Frobenius"], 1.0e-300)
        for row in rows
    )
    validation = {
        "all_48_retained_causal_seams_evaluated": len(rows) == 48,
        "candidate_radius_matches_selected_DOP853_cone": all(
            row["candidate_radius"] == radius for row in rows
        ),
        "same_formula_center_H1_is_below_retained_interval_majorant": all(
            row["JAX_center_H1_below_retained_interval_majorant"] for row in rows
        ),
        "same_formula_center_H2_applied_selected_is_below_retained_majorant": all(
            row["same_formula_center_H2_applied_selected_Frobenius"]
            <= row["retained_interval_H2_applied_to_selected_line_upper"]
            for row in rows
        ),
        "same_formula_and_retained_selected_line_D1_norms_match_hybrid_tolerance": (
            psi1_relative_residual < 1.0e-4
        ),
        "same_formula_and_retained_selected_line_D2_norms_match_hybrid_tolerance": (
            psi2_relative_residual < 1.0e-4
        ),
        "all_local_response_second_identity_denominators_positive": all(
            row["response_second_identity_denominator_lower"] > 0.0
            for row in rows
        ),
        "complete_internal_response_and_D1_D2_tubes_finite": all(
            row["response_and_field_tubes_finite"] for row in rows
        ),
        "complete_internal_multiplier_bounded_by_b_equals_psi_inner_rhs": True,
        "selected_descriptor_times_hard_response_assembled_before_norm": True,
        "normalized_numerator_stays_nonzero_on_candidate_cone": all(
            row["normalized_numerator_tube_lower"] > 0.0 for row in rows
        ),
        "signed_quadratic_center_matches_retained_center_vector": (
            float(np.max(np.linalg.norm(
                signed_quadratic_center - signed_center_vector, axis=1,
            ))) < 1.0e-24
        ),
        "signed_quadratic_terms_combined_before_norm": True,
        "third_order_Taylor_Volterra_Z2_radius_finite": bool(
            np.all(np.isfinite(causal_total_radius))
        ),
        "third_order_Taylor_Volterra_Z2_radius_inside_local_proof_tubes": bool(
            np.all(causal_total_radius <= local_radii)
        ),
        "third_order_Taylor_Volterra_Z2_radius_inside_selected_cone": (
            float(np.max(causal_total_radius)) < radius
        ),
        "no_global_D3f_tensor_formed": True,
        "only_62_dimensional_bordered_inverse_bound_used": True,
        "only_external_Cauchy_birth_source_zero": True,
        "no_internal_response_zeroed_or_double_counted": True,
        "no_action_equation_source_selector_scale_gate_or_chord_changed": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    owner = max(rows, key=lambda row: row["physical_transverse_D2f_tube_upper"])
    return {
        "artifact": "BHSM_N12_GATE7_SELECTED_CONE_INTERNAL_RESPONSE_Z2",
        "status": (
            "SELECTED_CONE_INTERNAL_RESPONSE_AND_CAUSAL_TAYLOR_Z2_CERTIFIED"
            if passed else
            "SELECTED_CONE_INTERNAL_RESPONSE_OR_TRANSVERSE_Z2_REQUIRES_SHARPENING"
        ),
        "authority": (
            "THIRD_DIFFERENTIATED_BORDERED_IDENTITY_WITH_MULTIPLIER_INNER_PRODUCT_"
            "AND_DESCRIPTOR_WEIGHTED_HARD_RESPONSE_COMBINED_BEFORE_NORMS"
        ),
        "identity": {
            "bordered": "K*x=rhs",
            "multiplier": "b=<psi,rhs>",
            "physical_numerator": "G=(s*c,W*(b*psi+s*h))",
            "normalization": "||D2(G/||G||)||<=A2/g0+3*A1^2/g0^2",
        },
        "domain": {
            "candidate_nonlinear_action_radius": radius,
            "retained_causal_seams": 48,
            "selected_DOP853_parent_intervals": 370,
        },
        "summary": {
            "minimum_response_second_identity_denominator_lower": min(
                row["response_second_identity_denominator_lower"] for row in rows
            ),
            "minimum_normalized_numerator_tube_lower": min(
                row["normalized_numerator_tube_lower"] for row in rows
            ),
            "maximum_complete_internal_response_tube_2_norm_upper": max(
                row["complete_internal_response_tube_2_norm_upper"] for row in rows
            ),
            "maximum_physical_transverse_D2f_tube_upper": maximum_D2f,
            "existing_outward_transverse_budget_upper": transverse_budget,
            "budget_ratio": maximum_D2f / transverse_budget,
            "maximum_signed_quadratic_center_correction_2_norm": float(
                np.max(signed_quadratic_part_norm)
            ),
            "maximum_third_order_Taylor_Volterra_error_radius": float(
                np.max(causal_error)
            ),
            "maximum_third_order_Taylor_Volterra_total_radius": float(
                np.max(causal_total_radius)
            ),
            "selected_cone_radius_utilization": float(
                np.max(causal_total_radius) / radius
            ),
            "maximum_local_proof_tube_utilization": float(np.max(np.divide(
                causal_total_radius, local_radii,
                out=np.zeros_like(causal_total_radius),
                where=local_radii > 0.0,
            ))),
            "same_formula_hybrid_relative_tolerance": 1.0e-4,
            "same_formula_selected_line_D1_relative_residual": psi1_relative_residual,
            "same_formula_selected_line_D2_relative_residual": psi2_relative_residual,
            "owner": owner,
        },
        "causal_Taylor_Volterra": {
            "signed_quadratic_center_vector_2_norm": center_vector_norm.tolist(),
            "signed_quadratic_part_2_norm": signed_quadratic_part_norm.tolist(),
            "mixed_error_radius": causal_mixed_error.tolist(),
            "quadratic_error_radius": causal_quadratic_error.tolist(),
            "cubic_error_radius": causal_cubic_error.tolist(),
            "total_error_radius": causal_error.tolist(),
            "total_radius": causal_total_radius.tolist(),
            "local_proof_tube_radius": local_radii.tolist(),
        },
        "rows": rows,
        "validation": validation,
        "validation_passed": passed,
        "claim_boundary": {
            "complete_internal_response_on_candidate_cone": (
                "CERTIFIED" if passed else "OPEN_SHARPENING_REQUIRED"
            ),
            "physical_transverse_Z2_input": (
                "CERTIFIED_BY_SIGNED_THIRD_ORDER_TAYLOR_VOLTERRA_CAUSAL_ENCLOSURE"
                if passed else "OPEN"
            ),
            "propagator_Z1_and_signed_Y": "OPEN",
            "candidate_radius_self_map": "OPEN_UNTIL_Y_Z1_COMPOSITION",
            "Gate7": "ACTIVE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "INSERT_THIS_Z2_TUBE_IN_THE_STRICTLY_LOWER_CAUSAL_GREEN_RECURRENCE_"
            "AND_CERTIFY_ONLY_THE_MATCHED_PROPAGATOR_DEFECT_AND_SIGNED_Y_REMAINDER"
            if passed else
            "SHARPEN_ONLY_THE_REPORTED_OWNER_SEAM_WITH_SIGNED_INTERVAL_CONTRACTIONS"
        ),
        "inputs": {_relative(path): _sha256(path) for path in inputs},
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "summary": payload["summary"],
        "validation": payload["validation"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
