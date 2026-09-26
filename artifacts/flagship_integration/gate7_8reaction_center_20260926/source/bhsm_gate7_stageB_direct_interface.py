#!/usr/bin/env python3
"""
BHSM Gate-7 direct Stage-B 73 -> 66+7 interface binder
======================================================

Read-only. No Git mutation. No Gate7 promotion.

Uses the frozen N12 Gate-7 endpoint candidate and the generic finite-N
complete-child row producer to evaluate the seven interface rows
(3 trace + 2 canonical momentum + 2 dynamic flux) on the persisted 73D
constraint tangent at nodes 13 and 14, then constructs the 66D child tangent.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

DEFAULT_REPO = Path(
    r"C:\Users\carbe\OneDrive\Documents\CODEX\Berger-Hopf-Standard-Model"
)

EXPECTED_ENDPOINT_SHA = (
    "3E52E013B473938B6959D5D63054FCC4D5057A13A71D10E2874ADB9A53E85B4E"
)

ORDER = 12
QDIM = 37
MDIM = 24
STATE_DIM = 98
CONSTRAINT_ROWS = 25
INTERFACE_ROWS = 7
CHILD_DIM = 66


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest().upper()


def git(root: Path, *args: str) -> str:
    p = subprocess.run(
        ["git", *args],
        cwd=str(root),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if p.returncode:
        return f"ERROR[{p.returncode}]: {p.stdout.strip()}"
    return p.stdout.strip()


def numerical_rank(a: np.ndarray, rel: float = 1e-9) -> tuple[int, np.ndarray, float]:
    s = np.linalg.svd(a, compute_uv=False)
    if not len(s):
        return 0, s, 0.0
    tol = max(
        max(a.shape) * np.finfo(float).eps * s[0],
        rel * s[0],
    )
    return int(np.sum(s > tol)), s, float(tol)


def nullspace(a: np.ndarray, rel: float = 1e-9) -> tuple[np.ndarray, np.ndarray, int]:
    u, s, vh = np.linalg.svd(a, full_matrices=True)
    tol = max(
        max(a.shape) * np.finfo(float).eps * (s[0] if len(s) else 1.0),
        rel * (s[0] if len(s) else 1.0),
    )
    rank = int(np.sum(s > tol))
    return vh[rank:].T, s, rank


def child_interface_values(
    child: np.ndarray,
    *,
    points: int,
    flux_relative_step: float,
) -> np.ndarray:
    from bhsm.interface.aether_cross_resolution_reconnaissance_v21_35 import (
        _child_rows_at_order,
    )

    event_q = np.zeros(QDIM)
    event_momentum = np.zeros(2)
    event_flux = np.zeros(2)

    rows = np.asarray(
        _child_rows_at_order(
            ORDER,
            np.asarray(child, dtype=float),
            event_q,
            event_momentum,
            event_flux,
            points=points,
            relative_flux_step=flux_relative_step,
            richardson_flux=True,
            flux_derivative_method="richardson",
        ),
        dtype=float,
    )

    if rows.shape != (32,):
        raise RuntimeError(f"unexpected complete-child row shape {rows.shape}")

    return np.concatenate(
        (
            rows[:3],
            rows[3 + CONSTRAINT_ROWS : 3 + CONSTRAINT_ROWS + 2],
            rows[-2:],
        )
    )


def directional_interface_jacobian(
    x: np.ndarray,
    weights: np.ndarray,
    tangent_action: np.ndarray,
    *,
    points: int,
    flux_relative_step: float,
    outer_step: float,
) -> np.ndarray:
    out = np.empty((INTERFACE_ROWS, tangent_action.shape[1]))
    ncols = tangent_action.shape[1]

    for j in range(ncols):
        d_raw = tangent_action[:, j] / weights
        max_raw = max(1.0, float(np.max(np.abs(d_raw))))
        h = outer_step / max_raw

        plus = child_interface_values(
            x + h * d_raw,
            points=points,
            flux_relative_step=flux_relative_step,
        )
        minus = child_interface_values(
            x - h * d_raw,
            points=points,
            flux_relative_step=flux_relative_step,
        )
        out[:, j] = (plus - minus) / (2.0 * h)

        if (j + 1) % 5 == 0 or j + 1 == ncols:
            print(
                f"      derivative columns {j+1}/{ncols} "
                f"(outer_step={outer_step:g})",
                flush=True,
            )

    return out


def full_action_hessian_action_coordinates(
    x: np.ndarray,
    weights: np.ndarray,
    *,
    points: int,
) -> np.ndarray:
    from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import (
        exact_full_action_jet_at_state,
    )

    q = x[:QDIM]
    v = x[QDIM : 2 * QDIM]
    m = x[2 * QDIM :]
    jet = exact_full_action_jet_at_state(
        ORDER, q, v, m, points=points
    )
    Hraw = np.asarray(jet.hessian, dtype=float)
    if Hraw.shape != (STATE_DIM, STATE_DIM):
        raise RuntimeError(f"unexpected full Hessian shape {Hraw.shape}")
    return Hraw / (weights[:, None] * weights[None, :])


def action_hessian_boundary_lift(
    H_action: np.ndarray,
    tangent_action: np.ndarray,
    betaQ: np.ndarray,
    condition_limit: float,
) -> tuple[np.ndarray | None, dict[str, Any]]:
    HT = tangent_action.T @ H_action @ tangent_action
    HTs = 0.5 * (HT + HT.T)
    eig = np.linalg.eigvalsh(HTs)
    sv = np.linalg.svd(HT, compute_uv=False)
    cond = float(sv[0] / sv[-1]) if sv[-1] > 0 else math.inf

    diag = {
        "restricted_Hessian_condition_number": cond,
        "restricted_Hessian_min_abs_eigenvalue": float(np.min(np.abs(eig))),
        "restricted_Hessian_max_abs_eigenvalue": float(np.max(np.abs(eig))),
    }

    if not np.isfinite(cond) or cond > condition_limit:
        diag["status"] = "BLOCKED_RESTRICTED_HESSIAN_CONDITION"
        return None, diag

    Z = np.linalg.solve(HT, betaQ.T)
    compliance = betaQ @ Z
    csv = np.linalg.svd(compliance, compute_uv=False)
    ccond = float(csv[0] / csv[-1]) if csv[-1] > 0 else math.inf
    diag.update(
        {
            "compliance_condition_number": ccond,
            "compliance_singular_values": csv.tolist(),
        }
    )

    if not np.isfinite(ccond) or ccond > condition_limit:
        diag["status"] = "BLOCKED_INTERFACE_COMPLIANCE_CONDITION"
        return None, diag

    coeff_lift = Z @ np.linalg.inv(compliance)
    L_action = tangent_action @ coeff_lift
    diag.update(
        {
            "status": "EVALUATED",
            "interface_identity_max_abs": float(
                np.max(np.abs(betaQ @ coeff_lift - np.eye(INTERFACE_ROWS)))
            ),
        }
    )
    return L_action, diag


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=str(DEFAULT_REPO))
    ap.add_argument("--nodes", default="13,14")
    ap.add_argument("--points", type=int, default=96)
    ap.add_argument("--flux-relative-step", type=float, default=1.0e-1)
    ap.add_argument("--outer-step-coarse", type=float, default=2.0e-5)
    ap.add_argument("--outer-step-fine", type=float, default=1.0e-5)
    ap.add_argument("--stability-limit", type=float, default=5.0e-3)
    ap.add_argument("--condition-limit", type=float, default=1.0e14)
    args = ap.parse_args()

    root = Path(args.repo).expanduser().resolve()
    sys.path.insert(0, str(root / "src"))

    endpoint = (
        root
        / "artifacts"
        / "flagship_integration"
        / "BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_NEWTON_ENDPOINT_CANDIDATE.npz"
    )
    if not endpoint.exists():
        raise SystemExit(f"missing frozen endpoint candidate: {endpoint}")

    endpoint_sha = sha256(endpoint)
    if endpoint_sha != EXPECTED_ENDPOINT_SHA:
        raise SystemExit(
            "endpoint candidate SHA mismatch:\n"
            f"  expected {EXPECTED_ENDPOINT_SHA}\n"
            f"  actual   {endpoint_sha}"
        )

    with np.load(endpoint, allow_pickle=False) as z:
        states = np.asarray(z["projected_states"], dtype=float)
        weights = np.asarray(z["state_weights"], dtype=float)
        tangents = np.asarray(
            z["endpoint_constraint_tangent_action"], dtype=float
        )

    if states.ndim != 2 or states.shape[1] != STATE_DIM:
        raise RuntimeError(f"unexpected state shape {states.shape}")
    if weights.shape != (STATE_DIM,):
        raise RuntimeError(f"unexpected weights shape {weights.shape}")
    if tangents.ndim != 3 or tangents.shape[1:] != (STATE_DIM, 73):
        raise RuntimeError(f"unexpected tangent shape {tangents.shape}")
    if np.any(weights <= 0.0):
        raise RuntimeError("state weights must be positive")

    wanted = [int(v) for v in args.nodes.split(",") if v.strip()]
    for node in wanted:
        if node < 0 or node >= states.shape[0]:
            raise RuntimeError(f"node {node} outside stored range")

    stamp = time.strftime("%Y%m%d_%H%M%S")
    out_json = Path.home() / "Downloads" / f"BHSM_GATE7_STAGEB_DIRECT_INTERFACE_{stamp}.json"
    out_npz = Path.home() / "Downloads" / f"BHSM_GATE7_STAGEB_DIRECT_INTERFACE_{stamp}.npz"

    report: dict[str, Any] = {
        "record_type": "BHSM_GATE7_STAGEB_DIRECT_73_TO_66_PLUS_7_BINDING",
        "timestamp_local": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "repo": str(root),
        "git": {
            "branch": git(root, "branch", "--show-current"),
            "head": git(root, "rev-parse", "HEAD"),
        },
        "source": {
            "endpoint_candidate": str(endpoint),
            "endpoint_candidate_SHA256": endpoint_sha,
            "projected_states_shape": list(states.shape),
            "state_weights_shape": list(weights.shape),
            "endpoint_constraint_tangent_action_shape": list(tangents.shape),
        },
        "configuration": {
            "order": ORDER,
            "points": args.points,
            "flux_relative_step": args.flux_relative_step,
            "outer_step_coarse": args.outer_step_coarse,
            "outer_step_fine": args.outer_step_fine,
            "stability_limit": args.stability_limit,
            "condition_limit": args.condition_limit,
        },
        "theorem_target": {
            "ambient_state": 98,
            "constraint_tangent": 73,
            "interface_rows": 7,
            "intrinsic_child_tangent": 66,
            "interface_order": [
                "trace_0",
                "trace_1",
                "trace_2",
                "canonical_momentum_0",
                "canonical_momentum_1",
                "dynamic_flux_0",
                "dynamic_flux_1",
            ],
            "descriptor_independent_input": False,
        },
        "rows": [],
        "Gate7_closed": False,
        "FULL_BHSM_COMPLETE": False,
    }

    arrays: dict[str, np.ndarray] = {
        "state_weights": weights,
    }

    overall_pass = True

    for node in wanted:
        print("=" * 88)
        print(f"NODE {node}")
        print("=" * 88, flush=True)

        x = states[node]
        T = tangents[node]

        print("  [1/4] coarse seven-row directional derivative", flush=True)
        beta_coarse = directional_interface_jacobian(
            x,
            weights,
            T,
            points=args.points,
            flux_relative_step=args.flux_relative_step,
            outer_step=args.outer_step_coarse,
        )

        print("  [2/4] fine seven-row directional derivative", flush=True)
        beta_fine = directional_interface_jacobian(
            x,
            weights,
            T,
            points=args.points,
            flux_relative_step=args.flux_relative_step,
            outer_step=args.outer_step_fine,
        )

        diff = beta_fine - beta_coarse
        stability = float(
            np.linalg.norm(diff)
            / max(np.linalg.norm(beta_fine), 1.0e-30)
        )
        max_abs_diff = float(np.max(np.abs(diff)))

        rank, s, tol = numerical_rank(beta_fine)
        Z, s2, rank2 = nullspace(beta_fine)
        if rank2 != rank:
            raise RuntimeError("rank implementations disagree")

        T_child = T @ Z
        tangent_rank = int(np.linalg.matrix_rank(T))
        child_rank = int(np.linalg.matrix_rank(T_child))
        interface_null_residual = float(np.linalg.norm(beta_fine @ Z, 2))

        print("  [3/4] same-action restricted Hessian", flush=True)
        H_action = full_action_hessian_action_coordinates(
            x, weights, points=args.points
        )

        print("  [4/4] seven-channel action-Hessian lift", flush=True)
        L, lift_diag = action_hessian_boundary_lift(
            H_action,
            T,
            beta_fine,
            args.condition_limit,
        )

        node_pass = bool(
            tangent_rank == 73
            and rank == 7
            and Z.shape == (73, 66)
            and child_rank == 66
            and interface_null_residual < 1.0e-8
            and stability <= args.stability_limit
            and L is not None
            and lift_diag.get("interface_identity_max_abs", math.inf) < 1.0e-8
        )
        overall_pass = overall_pass and node_pass

        row = {
            "node": node,
            "tangent_rank": tangent_rank,
            "interface_rank": rank,
            "interface_rank_tolerance": tol,
            "interface_singular_values": s.tolist(),
            "smallest_interface_singular_value": float(s[-1]),
            "intrinsic_child_dimension": int(Z.shape[1]),
            "intrinsic_child_rank": child_rank,
            "interface_null_residual_2": interface_null_residual,
            "two_scale_relative_Frobenius_change": stability,
            "two_scale_max_abs_change": max_abs_diff,
            "lift": lift_diag,
            "stageB_node_pass": node_pass,
        }
        report["rows"].append(row)

        arrays[f"node_{node:03d}_state"] = x
        arrays[f"node_{node:03d}_constraint_tangent_action"] = T
        arrays[f"node_{node:03d}_betaQ_coarse"] = beta_coarse
        arrays[f"node_{node:03d}_betaQ_fine"] = beta_fine
        arrays[f"node_{node:03d}_child_coeff_null_73x66"] = Z
        arrays[f"node_{node:03d}_T_child_action_98x66"] = T_child
        arrays[f"node_{node:03d}_H_action_98x98"] = H_action
        if L is not None:
            arrays[f"node_{node:03d}_L_boundary_action_98x7"] = L

        print(
            f"  rank(betaQ)={rank}, dim child={Z.shape[1]}, "
            f"stability={stability:.6e}, pass={node_pass}",
            flush=True,
        )

    report["stageB_pass"] = overall_pass
    if overall_pass:
        report["status"] = "STAGE_B_73_TO_66_PLUS_7_NUMERICALLY_CLOSED"
        report["next_required_stage"] = (
            "SHARED_BORDERED_RESOLVENT_ON_66D_CHILD_TANGENT"
        )
    else:
        report["status"] = "STAGE_B_NOT_CLOSED"
        failed = [r["node"] for r in report["rows"] if not r["stageB_node_pass"]]
        report["failed_nodes"] = failed
        report["next_required_stage"] = (
            "RESOLVE_FIRST_FAILED_RANK_STABILITY_OR_ACTION_LIFT_CONDITION"
        )

    np.savez_compressed(out_npz, **arrays)
    report["derived_npz"] = str(out_npz)
    report["derived_npz_SHA256"] = sha256(out_npz)

    out_json.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print("\n" + "=" * 88)
    print("RESULT")
    print("=" * 88)
    print("Status:", report["status"])
    for row in report["rows"]:
        print(
            f"Node {row['node']}: rank={row['interface_rank']} "
            f"child_dim={row['intrinsic_child_dimension']} "
            f"stability={row['two_scale_relative_Frobenius_change']:.6e} "
            f"lift={row['lift'].get('status')} "
            f"PASS={row['stageB_node_pass']}"
        )
    print("Stage-B pass:", report["stageB_pass"])
    print("Gate7_closed: False")
    print("FULL_BHSM_COMPLETE: False")
    print("Report:", out_json)
    print("Arrays:", out_npz)

    return 0 if overall_pass else 3


if __name__ == "__main__":
    raise SystemExit(main())
