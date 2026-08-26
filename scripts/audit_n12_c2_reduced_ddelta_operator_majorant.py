"""Reconnoiter a cancellation-reduced full C2 D2Delta majorant.

This is deliberately diagnostic.  It consumes the retained mixed action
majorant engine but does not promote its output to a certificate.  The point
is to test whether the fully reduced hard-adjoint identities leave enough of
the 29-ish full-covector transport budget to justify a dedicated outward-
rounded implementation.
"""

from __future__ import annotations

import importlib.util
import argparse
import json
import math
import os
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from bhsm.interface.aether_retained_action_one_axis_interval import (  # noqa: E402
    retained_action_one_axis_interval,
)
from bhsm.interface.aether_retained_action_tensor_interval import (  # noqa: E402
    DirectedInterval,
)
BASE = ROOT / "artifacts" / "flagship_integration"
MAJORANT_SOURCE = ROOT / "scripts" / "derive_n12_action_ball_majorants.py"
RADIUS = 5.5104723095444935e-11
QDIM = 37
TOTAL = 98


def _load_majorant_module():
    spec = importlib.util.spec_from_file_location("bhsm_action_majorants", MAJORANT_SOURCE)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load retained action majorant engine")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    module.BALL_RADIUS = RADIUS
    return module


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--signed-row", type=int)
    parser.add_argument("--exact-first", action="store_true")
    parser.add_argument("--cb-only", action="store_true")
    args = parser.parse_args()
    majorants = _load_majorant_module()
    bordered_path = BASE / "BHSM_N12_C2_BORDERED_HARD_RESPONSE_MATRIX.npz"
    recon_path = BASE / "BHSM_N12_C2_DIRECT_DDELTA_ROW_RECONNAISSANCE.npz"
    field_path = BASE / "BHSM_N12_C2_EXACT_CENTER_FIXED_S_FIELD_MATRIX.json"
    field_data_path = field_path.with_suffix(".npz")
    response_path = BASE / "BHSM_N12_C2_CANCELLED_FIELD_LOHNER_STEP.json"
    first_path = BASE / "BHSM_N12_C2_SIGNED_FIRST_COEFFICIENT_VECTORS.npz"

    with np.load(bordered_path) as data:
        state = np.asarray(data["center_state"], dtype=float)
        weights = np.asarray(data["state_weights"], dtype=float)
        psi = np.asarray(data["selected_vector"], dtype=float)
        psi_first = np.asarray(
            data["selected_vector_derivative_action"], dtype=float
        )
        hard = np.asarray(data["bordered_response"], dtype=float)[:-1]
        hard_first = np.asarray(
            data["bordered_response_derivative_action"], dtype=float
        )[:-1]
        lambda_gradient = np.asarray(data["lambda_gradient_action"], dtype=float)
    with np.load(recon_path) as data:
        z = np.asarray(data["third_variation_hard_adjoint"], dtype=float)
    with np.load(field_data_path) as data:
        delta_partial = np.asarray(data["Delta_first_partial_action"], dtype=float)
        seed_remainder = float(data["Delta_first_total_remainder_action_norm_upper"])
    with np.load(first_path) as data:
        b_center_lo = np.asarray(data["b_first_action_lower"], dtype=float)
        b_center_hi = np.asarray(data["b_first_action_upper"], dtype=float)
        c_center_lo = np.asarray(data["c_first_action_lower"], dtype=float)
        c_center_hi = np.asarray(data["c_first_action_upper"], dtype=float)
        l_center_lo = np.asarray(data["lambda_first_action_lower"], dtype=float)
        l_center_hi = np.asarray(data["lambda_first_action_upper"], dtype=float)

    field = json.loads(field_path.read_text(encoding="utf-8"))
    response = json.loads(response_path.read_text(encoding="utf-8"))
    b = float(field["center_field"]["b_psi"])
    c = float(field["center_field"]["moving_cubic_from_Dlambda_Psi"])
    s = float(field["center_field"]["signed_descriptor_decimal"])
    p2 = float(
        json.loads(
            (BASE / "BHSM_N12_C2_FRESH_CHART_FIXED_S_GROWTH.json")
            .read_text(encoding="utf-8")
        )["fresh_line_bounds"]["selected_line_second_variation_coefficient_upper"]
    )
    v2 = float(response["second_variation"]["response_second_variation_upper"])

    eye = np.eye(TOTAL)
    reduced_weights = weights[QDIM:]
    embed = np.zeros((TOTAL, reduced_weights.size))
    embed[QDIM:] = np.diag(reduced_weights)
    p = embed @ psi
    z_action = embed @ z
    p1 = embed @ psi_first
    v = embed @ hard
    v1 = embed @ hard_first
    qdot = np.zeros(TOTAL)
    qdot[:QDIM] = weights[:QDIM] * state[QDIM:2 * QDIM]
    qdot_first = np.zeros((TOTAL, TOTAL))
    qdot_first[:QDIM, QDIM:2 * QDIM] = np.diag(
        weights[:QDIM] / weights[QDIM:2 * QDIM]
    )
    whole_v = qdot + v
    whole_v1 = qdot_first + v1
    j_p = np.zeros(TOTAL)
    j_p[:QDIM] = weights[:QDIM] * psi[:QDIM]
    j_p1 = np.zeros((TOTAL, TOTAL))
    j_p1[:QDIM] = weights[:QDIM, None] * psi_first[:QDIM]

    def mixed(*directions: np.ndarray) -> float:
        value = majorants.action_bound(
            state, mixed_directions=list(directions)
        )
        return float(value.d[-1])

    if args.exact_first:
        def exact(output_index: int, *directions: np.ndarray) -> np.ndarray:
            return np.asarray(majorants.action_bound(
                state,
                mixed_directions=list(directions),
                exact_signed_output_index=output_index,
            ).d[-1], dtype=float)

        c1_exact = exact(0, eye, p, p, p) + 3.0 * exact(
            0, eye, p, z_action
        )
        source_exact = (
            exact(0, eye, j_p)
            - exact(0, eye, p, qdot)
            - exact(1, p, qdot_first)
        )
        b1_exact = source_exact - exact(0, eye, p, v)
        lambda_exact = exact(0, eye, p, p)
        row_payload = {
            "authority": "DIAGNOSTIC_BINARY64_EXACT_SIGNED_CENTER",
            "b_first_norm": float(np.linalg.norm(b1_exact)),
            "b_first_86": float(b1_exact[86]),
            "c_first_norm": float(np.linalg.norm(c1_exact)),
            "c_first_86": float(c1_exact[86]),
            "lambda_gradient_norm": float(np.linalg.norm(lambda_exact)),
            "lambda_gradient_86": float(lambda_exact[86]),
            "stored_lambda_gradient_residual": float(np.linalg.norm(
                lambda_exact - lambda_gradient
            )),
        }
        diagnostic_result = os.environ.get("BHSM_C2_DIAGNOSTIC_ROW_RESULT")
        if diagnostic_result:
            Path(diagnostic_result).write_text(
                json.dumps(row_payload, indent=2, sort_keys=True) + "\n",
                encoding="utf-8", newline="\n",
            )
        print(json.dumps(row_payload, indent=2, sort_keys=True))
        return

    if args.signed_row is not None:
        row_index = args.signed_row
        if not 0 <= row_index < TOTAL:
            raise ValueError("signed row index is outside the state dimension")
        IV = DirectedInterval
        basis = eye[row_index]
        state_lo = np.nextafter(state - RADIUS / weights, -np.inf)
        state_hi = np.nextafter(state + RADIUS / weights, np.inf)
        raw_spread = np.abs(embed @ np.ones(psi.size))

        def box(center: np.ndarray, radius: float) -> tuple[np.ndarray, np.ndarray]:
            center = np.asarray(center, dtype=float)
            return (
                np.nextafter(center - raw_spread * radius, -np.inf),
                np.nextafter(center + raw_spread * radius, np.inf),
            )

        p_box = box(p, 6.0e-9)
        z_box = box(z_action, 2.0e-3)
        v_box = box(v, 40.0)
        pi = p1[:, row_index]
        pi_box = box(pi, 1.0e-2)
        j_p_box = (
            np.r_[
                weights[:QDIM] * (p_box[0][QDIM:] / reduced_weights)[:QDIM],
                np.zeros(TOTAL - QDIM),
            ],
            np.r_[
                weights[:QDIM] * (p_box[1][QDIM:] / reduced_weights)[:QDIM],
                np.zeros(TOTAL - QDIM),
            ],
        )

        def iv(
            output_index: int,
            directions: list[np.ndarray],
            bounds: list[tuple[np.ndarray, np.ndarray] | None],
        ):
            return retained_action_one_axis_interval(
                12,
                state_lo,
                state_hi,
                directions,
                bounds,
                output_index=output_index,
                points=96,
            )

        def ivnorm(value) -> float:
            magnitude = np.maximum(
                np.abs(np.asarray(value.lo)), np.abs(np.asarray(value.hi))
            ).ravel()
            return math.nextafter(
                math.sqrt(math.fsum(float(x) * float(x) for x in magnitude)),
                math.inf,
            )

        def transpose_row(value):
            return value

        lambda_all = iv(0, [eye, p], [None, p_box])
        c_first_iv = (
            iv(0, [eye, p, p, p], [None, p_box, p_box, p_box])
            + 3.0 * iv(0, [eye, p, z_action], [None, p_box, z_box])
        )
        source_first_iv = (
            iv(0, [eye, j_p], [None, j_p_box])
            - iv(0, [eye, p, qdot], [None, p_box, None])
            - iv(1, [p, qdot_first], [p_box, None])
        )
        b_first_iv = source_first_iv - iv(
            0, [eye, p, v], [None, p_box, v_box]
        )

        b_domain = response["domain"]["b_psi_interval"]
        c_domain = response["domain"]["c_interval"]
        b_iv = IV(float(b_domain[0]), float(b_domain[1]))
        c_iv = IV(float(c_domain[0]), float(c_domain[1]))
        bi_iv = IV(
            math.nextafter(float(b_center_lo[row_index]) - 0.08, -math.inf),
            math.nextafter(float(b_center_hi[row_index]) + 0.08, math.inf),
        )
        ci_iv = IV(
            math.nextafter(float(c_center_lo[row_index]) - 2.0e-6, -math.inf),
            math.nextafter(float(c_center_hi[row_index]) + 2.0e-6, math.inf),
        )
        li_iv = IV(
            math.nextafter(float(l_center_lo[row_index]) - 1.0e-5, -math.inf),
            math.nextafter(float(l_center_hi[row_index]) + 1.0e-5, math.inf),
        )

        p_t_z = IV.constant(psi_first.T @ z)
        p_t_v = IV.constant(psi_first.T @ hard)
        p_t_pi = IV.constant(psi_first.T @ psi_first[:, row_index])
        z_t_pi = IV.constant(float(z @ psi_first[:, row_index]))
        v_t_pi = IV.constant(float(hard @ psi_first[:, row_index]))
        g_first = iv(0, [eye, p, p], [None, p_box, p_box])

        c2 = (
            iv(1, [basis, eye, p, p, p], [None, None, p_box, p_box, p_box])
            + 3.0 * iv(0, [eye, pi, p, p], [None, pi_box, p_box, p_box])
            + 3.0 * iv(1, [basis, p1, p, p], [None, None, p_box, p_box])
            + 3.0 * iv(1, [basis, eye, p, z_action], [None, None, p_box, z_box])
            + 3.0 * (
                iv(1, [basis, p1, z_action], [None, None, z_box])
                - li_iv * p_t_z
            )
            + 3.0 * iv(0, [eye, z_action, pi], [None, z_box, pi_box])
            - 3.0 * z_t_pi * g_first
            - 3.0 * c_iv * p_t_pi
            + 6.0 * iv(0, [p1, pi, p], [None, pi_box, p_box])
        )
        j_pi = np.zeros(TOTAL)
        j_pi[:QDIM] = weights[:QDIM] * (
            pi[QDIM:] / reduced_weights
        )[:QDIM]
        j_pi_box = (
            np.r_[
                weights[:QDIM] * (pi_box[0][QDIM:] / reduced_weights)[:QDIM],
                np.zeros(TOTAL - QDIM),
            ],
            np.r_[
                weights[:QDIM] * (pi_box[1][QDIM:] / reduced_weights)[:QDIM],
                np.zeros(TOTAL - QDIM),
            ],
        )
        source_pifh = (
            iv(0, [eye, j_pi], [None, j_pi_box])
            - iv(0, [eye, pi, qdot], [None, pi_box, None])
            - iv(1, [pi, qdot_first], [pi_box, None])
        )
        source_phfi = (
            iv(1, [basis, j_p1], [None, None])
            - iv(1, [basis, p1, qdot], [None, None, None])
        )
        source_pfih = (
            iv(1, [basis, eye, j_p], [None, None, j_p_box])
            - iv(1, [basis, eye, p, qdot], [None, None, p_box, None])
            - iv(2, [basis, p, qdot_first], [None, p_box, None])
        )
        b2 = (
            -b_iv * p_t_pi
            - iv(1, [basis, eye, p, v], [None, None, p_box, v_box])
            - iv(1, [basis, p1, v], [None, None, v_box])
            + li_iv * p_t_v
            - iv(0, [eye, v, pi], [None, v_box, pi_box])
            + v_t_pi * g_first
            + source_pifh
            + source_phfi
            + source_pfih
        )
        cb_iv = b_iv * c2 + bi_iv * c_first_iv + ci_iv * b_first_iv + c_iv * b2
        c2_fixed_bound = ivnorm(c2)
        b2_fixed_bound = ivnorm(b2)
        cb_center_bound = ivnorm(cb_iv)
        b_abs = max(abs(float(b_domain[0])), abs(float(b_domain[1])))
        c_abs = max(abs(float(c_domain[0])), abs(float(c_domain[1])))
        l_abs = max(abs(float(li_iv.lo)), abs(float(li_iv.hi)))
        pi_norm = float(np.linalg.norm(psi_first[:, row_index])) + 1.0e-2
        z_norm = float(np.linalg.norm(z)) + 2.0e-3
        v_norm = float(np.linalg.norm(hard)) + 40.0
        p_matrix_motion = 8.0
        c2_motion = p_matrix_motion * (
            3.0 * ivnorm(iv(1, [basis, embed, p, p], [None, None, p_box, p_box]))
            + 3.0 * ivnorm(iv(1, [basis, embed, z_action], [None, None, z_box]))
            + 3.0 * l_abs * z_norm
            + 3.0 * c_abs * pi_norm
            + 6.0 * ivnorm(iv(0, [embed, pi, p], [None, pi_box, p_box]))
        )
        j_embed = np.zeros((TOTAL, psi.size))
        j_embed[:QDIM, :QDIM] = np.diag(weights[:QDIM])
        fi_motion = (
            ivnorm(iv(1, [basis, j_embed], [None, None]))
            + ivnorm(iv(1, [basis, embed, qdot], [None, None, None]))
        )
        b2_motion = p_matrix_motion * (
            b_abs * pi_norm
            + ivnorm(iv(1, [basis, embed, v], [None, None, v_box]))
            + l_abs * v_norm
            + fi_motion
        )
        cb_motion = b_abs * c2_motion + c_abs * b2_motion
        cb_total = math.nextafter(cb_center_bound + cb_motion, math.inf)
        c2_total = math.nextafter(c2_fixed_bound + c2_motion, math.inf)
        b2_total = math.nextafter(b2_fixed_bound + b2_motion, math.inf)
        b_radius_needed = math.nextafter(b2_total * RADIUS, math.inf)
        c_radius_needed = math.nextafter(c2_total * RADIUS, math.inf)
        lambda_radius_needed = math.nextafter(986.016684739049 * RADIUS, math.inf)
        if args.cb_only:
            row_payload = {
                "authority": "DIAGNOSTIC_SIGNED_ONE_AXIS_INTERVAL",
                "row": row_index,
                "b_i_interval": [float(bi_iv.lo), float(bi_iv.hi)],
                "c_i_interval": [float(ci_iv.lo), float(ci_iv.hi)],
                "lambda_i_interval": [float(li_iv.lo), float(li_iv.hi)],
                "fixed_cb_row_upper_before_P_matrix_motion": cb_center_bound,
                "fixed_c_second_row_upper": c2_fixed_bound,
                "fixed_b_second_row_upper": b2_fixed_bound,
                "c_second_row_P_matrix_motion_upper": c2_motion,
                "b_second_row_P_matrix_motion_upper": b2_motion,
                "cb_row_P_matrix_motion_upper": cb_motion,
                "complete_cb_row_upper": cb_total,
                "complete_c_second_row_upper": c2_total,
                "complete_b_second_row_upper": b2_total,
                "b_i_radius_needed": b_radius_needed,
                "c_i_radius_needed": c_radius_needed,
                "lambda_i_radius_needed_global": lambda_radius_needed,
                "validation": {
                    "b_i_radius_self_consistent": b_radius_needed < 0.08,
                    "c_i_radius_self_consistent": c_radius_needed < 2.0e-6,
                    "lambda_i_radius_self_consistent": lambda_radius_needed < 1.0e-5,
                },
            }
            diagnostic_result = os.environ.get("BHSM_C2_DIAGNOSTIC_ROW_RESULT")
            if diagnostic_result:
                Path(diagnostic_result).write_text(
                    json.dumps(row_payload, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8", newline="\n",
                )
            print(json.dumps(row_payload, indent=2, sort_keys=True))
            return
        whole_v_box_spread = (
            np.linalg.norm(qdot_first, axis=1) * RADIUS
            + raw_spread * 40.0
        )
        whole_v_box = (
            np.nextafter(whole_v - whole_v_box_spread, -np.inf),
            np.nextafter(whole_v + whole_v_box_spread, np.inf),
        )
        whole_v1 = qdot_first + v1
        whole_vi = whole_v1[:, row_index]
        hard_first_motion = math.nextafter(v2 * RADIUS, math.inf)
        psi_first_motion = math.nextafter(p2 * RADIUS, math.inf)
        r_terms = {
            "D5_i_h_W_p_p": ivnorm(iv(
                1, [basis, eye, whole_v, p, p],
                [None, None, whole_v_box, p_box, p_box],
            )),
            "D4_i_W_h_center_p_p": ivnorm(iv(
                1, [basis, whole_v1, p, p],
                [None, None, p_box, p_box],
            )),
            "D4_i_W_h_motion_p_p": hard_first_motion * mixed(
                basis, embed, p, p
            ),
            "D4_h_W_i_center_p_p": ivnorm(iv(
                0, [eye, whole_vi, p, p],
                [None, None, p_box, p_box],
            )),
            "D4_h_W_i_motion_p_p": hard_first_motion * mixed(
                eye, embed, p, p
            ),
            "2D4_i_W_p_h_center_p": 2.0 * ivnorm(iv(
                2, [basis, whole_v, p1, p],
                [None, whole_v_box, None, p_box],
            )),
            "2D4_i_W_p_h_motion_p": 2.0 * psi_first_motion * mixed(
                basis, whole_v, embed, p
            ),
            "2D4_h_W_p_i_p": 2.0 * ivnorm(iv(
                0, [eye, whole_v, pi, p],
                [None, whole_v_box, pi_box, p_box],
            )),
            "D3_W_ih_p_p": v2 * mixed(embed, p, p),
            "2D3_W_i_center_p_h_center_p": 2.0 * ivnorm(iv(
                1, [whole_vi, p1, p], [None, None, p_box]
            )),
            "2D3_W_i_motion_p_h_center_p": (
                2.0 * hard_first_motion * mixed(embed, p1, p)
            ),
            "2D3_W_i_center_p_h_motion_p": (
                2.0 * psi_first_motion * mixed(whole_vi, embed, p)
            ),
            "2D3_W_i_motion_p_h_motion_p": (
                2.0 * hard_first_motion * psi_first_motion
                * mixed(embed, embed, p)
            ),
            "2D3_W_h_center_p_i_p": 2.0 * ivnorm(iv(
                0, [whole_v1, pi, p], [None, pi_box, p_box]
            )),
            "2D3_W_h_motion_p_i_p": (
                2.0 * hard_first_motion * mixed(embed, pi, p)
            ),
            "2D3_W_p_ih_p": 2.0 * p2 * mixed(whole_v, embed, p),
            "2D3_W_p_i_p_h_center": 2.0 * ivnorm(iv(
                2, [whole_v, pi, p1], [whole_v_box, pi_box, None]
            )),
            "2D3_W_p_i_p_h_motion": (
                2.0 * psi_first_motion * mixed(whole_v, pi, embed)
            ),
        }
        raw_r = math.fsum(r_terms.values())
        s_r = math.nextafter(abs(s) * raw_r, math.inf)
        complete_row = math.nextafter(cb_total + s_r, math.inf)
        print(json.dumps({
            "authority": "DIAGNOSTIC_SIGNED_ONE_AXIS_INTERVAL",
            "row": row_index,
            "b_i_interval": [float(bi_iv.lo), float(bi_iv.hi)],
            "c_i_interval": [float(ci_iv.lo), float(ci_iv.hi)],
            "lambda_i_interval": [float(li_iv.lo), float(li_iv.hi)],
            "fixed_cb_row_upper_before_P_matrix_motion": cb_center_bound,
            "c_second_row_P_matrix_motion_upper": c2_motion,
            "b_second_row_P_matrix_motion_upper": b2_motion,
            "cb_row_P_matrix_motion_upper": cb_motion,
            "complete_cb_row_upper": cb_total,
            "raw_R_second_row_term_uppers": r_terms,
            "raw_R_second_row_upper": raw_r,
            "s_R_second_row_upper": s_r,
            "complete_D2Delta_row_upper": complete_row,
        }, indent=2, sort_keys=True))
        return

    p1n = float(np.linalg.norm(p1, 2))
    lin = float(np.linalg.norm(lambda_gradient))
    p1tz = float(np.linalg.norm(psi_first.T @ z))
    p1tv = float(np.linalg.norm(psi_first.T @ hard))
    p1tp1 = p1n * p1n

    c1 = mixed(eye, p, p, p) + 3.0 * mixed(eye, p, z_action)
    f1 = mixed(eye, j_p) + mixed(eye, p, qdot) + mixed(p, qdot_first)
    b1 = f1 + mixed(eye, p, v)

    c2_parts = {
        "D5_IIppp": mixed(eye, eye, p, p, p),
        "six_D4_IPpp": 6.0 * mixed(eye, p1, p, p),
        "three_D4_IIpz": 3.0 * mixed(eye, eye, p, z_action),
        "six_D3_IPz": 6.0 * mixed(eye, p1, z_action),
        "lambda_outer": 3.0 * lin * p1tz,
        "z_outer_g": 3.0 * p1tz * mixed(eye, p, p),
        "c_PtP": 3.0 * abs(c) * p1tp1,
        "six_D3_PPp": 6.0 * mixed(p1, p1, p),
    }
    c2 = math.fsum(c2_parts.values())

    source_pair = (
        mixed(eye, j_p1)
        + mixed(eye, p1, qdot)
        + mixed(p1, qdot_first)
    )
    source_second = (
        mixed(eye, eye, j_p)
        + mixed(eye, eye, p, qdot)
        + mixed(eye, p, qdot_first)
    )
    b2_parts = {
        "b_PtP": abs(b) * p1tp1,
        "D4_IIpV": mixed(eye, eye, p, v),
        "two_D3_IPV": 2.0 * mixed(eye, p1, v),
        "lambda_outer": lin * p1tv,
        "V_outer_g": p1tv * mixed(eye, p, p),
        "two_source_pairs": 2.0 * source_pair,
        "source_second": source_second,
    }
    b2 = math.fsum(b2_parts.values())
    cb = abs(b) * c2 + 2.0 * b1 * c1 + abs(c) * b2

    r_parts = {
        "D5_IIWpp": mixed(eye, eye, whole_v, p, p),
        "two_D4_IW1pp": 2.0 * mixed(eye, whole_v1, p, p),
        "four_D4_IWPp": 4.0 * mixed(eye, whole_v, p1, p),
        "W_second": v2 * mixed(embed, p, p),
        "four_D3_W1Pp": 4.0 * mixed(whole_v1, p1, p),
        "Psi_second": 2.0 * p2 * mixed(whole_v, embed, p),
        "two_D3_WPP": 2.0 * mixed(whole_v, p1, p1),
    }
    r2 = math.fsum(r_parts.values())
    complete = cb + abs(s) * r2
    ceiling = (float(np.linalg.norm(delta_partial)) - seed_remainder) / RADIUS
    print(json.dumps({
        "authority": "DIAGNOSTIC_NORM_MAJORANT_ONLY",
        "c_first_upper": c1,
        "b_first_upper": b1,
        "c_second_parts": c2_parts,
        "c_second_upper": c2,
        "b_second_parts": b2_parts,
        "b_second_upper": b2,
        "cb_operator_upper": cb,
        "R_second_parts": r_parts,
        "R_second_upper": r2,
        "s_R_second_upper": abs(s) * r2,
        "complete_D2Delta_operator_upper": complete,
        "transport_ceiling": ceiling,
        "diagnostic_pass": complete < ceiling,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
