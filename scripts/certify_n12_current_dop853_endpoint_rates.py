"""Outward point rates on the current native DOP853 center.

This computes two point statements, not a flow tube or a first-hit theorem.
The imported rate action is unchanged. Its eigenline gap is supplied locally
by an Arb residual and polar-orthogonality certificate for the full spectrum.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
import time

import numpy as np
from flint import arb, arb_mat, ctx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts import certify_n12_gate7_accepted_replay_center_outward_74d as owner
from bhsm.interface.current_action_response_capture import evaluate_shared_rate

DEFAULT_CENTER = ROOT / "artifacts/flagship_integration/BHSM_N12_C2_STOP_HIGH_ORDER_QUARTER_STEP_RETAINED_RECONNAISSANCE.npz"
DEFAULT_OUTPUT = ROOT / "artifacts/current_runtime/current_dop853_endpoint_rates"
SELECTED = 24


def exact(value: float | int | arb) -> arb:
    if isinstance(value, arb):
        return value
    if isinstance(value, (int, np.integer)):
        return arb(int(value))
    numerator, denominator = float(value).as_integer_ratio()
    return arb(numerator) / arb(denominator)


def matrix(values: np.ndarray) -> arb_mat:
    array = np.asarray(values, dtype=object)
    if array.ndim == 1:
        array = array[:, None]
    return arb_mat([[exact(v) for v in row] for row in array])


def frobenius_bound(value: arb_mat) -> arb:
    total = arb(0)
    for i in range(value.nrows()):
        for j in range(value.ncols()):
            total += abs(value[i, j]).upper() ** 2
    return total.sqrt().upper()


def lower_float(value: arb) -> float:
    return math.nextafter(float(value.lower()), -math.inf)


def upper_float(value: arb) -> float:
    return math.nextafter(float(value.upper()), math.inf)


def scalar_packet(value: arb) -> dict[str, object]:
    if not value.is_finite():
        raise ArithmeticError("nonfinite endpoint ball")
    return {"ball": value.str(140), "lower": lower_float(value),
            "upper": upper_float(value)}


def spectrum_gap(hessian: np.ndarray, midpoint: np.ndarray) -> tuple[dict, np.ndarray, np.ndarray]:
    """Weyl intervals using the polar factor of a numerical full basis.

    For eta=||Q^TQ-I||_F<1, the orthogonal polar factor Z obeys
    ||Q-Z||_2 <= eta/(1+sqrt(1-eta)). Therefore
    ||H-Z Lambda Z^T||_2 <= ||H-Q Lambda Q^T||_F
      + ||Lambda||_2*||Q-Z||_2*(sqrt(1+eta)+1).
    Every sorted true eigenvalue lies in the corresponding Lambda_j +/- eps.
    All operands and displayed inequalities are evaluated outward in Arb.
    """
    values, vectors = np.linalg.eigh(np.asarray(midpoint, dtype=float))
    n = len(values)
    H = matrix(hessian)
    Q = matrix(vectors)
    identity = arb_mat(np.eye(n, dtype=int).tolist())
    diagonal = arb_mat(n, n)
    for i, value in enumerate(values):
        diagonal[i, i] = exact(value)
    eta = frobenius_bound(Q.transpose() * Q - identity)
    if not eta < 1:
        raise ArithmeticError("full eigenbasis polar bound does not close")
    residual = frobenius_bound(H - Q * diagonal * Q.transpose())
    distance = eta / (1 + (1 - eta).sqrt())
    lam_norm = max(abs(exact(v)) for v in values)
    epsilon = (residual + lam_norm * distance * ((1 + eta).sqrt() + 1)).upper()
    left = exact(values[SELECTED]) - exact(values[SELECTED - 1]) - 2 * epsilon
    right = exact(values[SELECTED + 1]) - exact(values[SELECTED]) - 2 * epsilon
    gap = min(left.lower(), right.lower())
    if not gap > 0:
        raise ArithmeticError("full-spectrum selected point gap does not close")
    packet = {"full_basis_orthogonality_norm_upper": scalar_packet(eta),
              "full_basis_residual_norm_upper": scalar_packet(residual),
              "polar_basis_distance_upper": scalar_packet(distance.upper()),
              "all_eigenvalue_error_upper": scalar_packet(epsilon),
              "selected_gap_lower": scalar_packet(gap),
              "negative_side_gap_lower": scalar_packet(left.lower()),
              "positive_side_gap_lower": scalar_packet(right.lower()),
              "full_approximate_eigenvalues": [exact(v).str(140) for v in values]}
    return packet, values, vectors


class VerifiedPointEigenline:
    def __init__(self):
        self.packet: dict[str, object] | None = None
        self.reduced_hessian: np.ndarray | None = None
        self.approximate_basis: np.ndarray | None = None
        self.normalized_point: np.ndarray | None = None

    def __call__(self, hessian, midpoint, reference):
        reduced = np.asarray(hessian[owner.QDIM:, owner.QDIM:], dtype=object)
        point_mid = np.asarray(midpoint[owner.QDIM:, owner.QDIM:], dtype=float)
        packet, values, vectors = spectrum_gap(reduced, point_mid)
        self.reduced_hessian = reduced
        self.approximate_basis = np.asarray([[exact(v) for v in row] for row in vectors], dtype=object)
        H = matrix(reduced)
        n = owner.REDUCED
        identity = arb_mat(np.eye(n, dtype=int).tolist())
        psi0 = vectors[:, SELECTED]
        if float(psi0 @ reference) < 0:
            psi0 = -psi0
        psi = matrix(psi0)
        lam = exact(values[SELECTED])
        # Newton only supplies a high precision point approximation. The
        # proof below uses its normalized point residual and verified gap.
        for _ in range(4):
            residual = H * psi - lam * psi
            defect = (psi.transpose() * psi)[0, 0] / 2 - arb(1) / 2
            K = arb_mat(n + 1, n + 1)
            for i in range(n):
                for j in range(n):
                    K[i, j] = H[i, j] - (lam if i == j else 0)
                K[i, n] = -psi[i, 0]
                K[n, i] = psi[i, 0]
            rhs = arb_mat(n + 1, 1)
            for i in range(n):
                rhs[i, 0] = -residual[i, 0]
            rhs[n, 0] = -defect
            correction = K.solve(rhs, algorithm="precond")
            for i in range(n):
                psi[i, 0] = arb((psi[i, 0] + correction[i, 0]).mid())
            lam = arb((lam + correction[n, 0]).mid())
        normalization = (psi.transpose() * psi)[0, 0].sqrt()
        unit = arb_mat([[psi[i, 0] / normalization] for i in range(n)])
        self.normalized_point = np.asarray([unit[i, 0] for i in range(n)], dtype=object)
        residual_upper = frobenius_bound(H * unit - lam * unit)
        epsilon = arb(packet["all_eigenvalue_error_upper"]["ball"])
        other_separation = min((abs(lam - exact(value)) - epsilon).lower()
                               for i, value in enumerate(values) if i != SELECTED)
        if not other_separation > residual_upper:
            raise ArithmeticError(f"normalized selected eigenline isolation failed: residual={residual_upper}, other_separation={other_separation}, lambda={lam}, spectral_error={epsilon}")
        # sin(theta)<=r/d. For matching orientation, Euclidean distance is
        # at most 2*sin(theta); use d-r as a further conservative margin.
        angle = (2 * residual_upper / (other_separation - residual_upper)).upper()
        overlap = sum(unit[i, 0] * exact(reference[i]) for i in range(n))
        refnorm = sum(exact(v) ** 2 for v in reference).sqrt()
        if not overlap - angle * refnorm > 0:
            raise ArithmeticError("selected eigenline reference orientation failed")
        enclosed = np.asarray([unit[i, 0] + arb(0, angle) for i in range(n)], dtype=object)
        p = matrix(enclosed)
        rayleigh = (p.transpose() * H * p)[0, 0] / (p.transpose() * p)[0, 0]
        packet.update(normalized_eigenline_residual_upper=scalar_packet(residual_upper),
                      eigenvector_euclidean_distance_upper=scalar_packet(angle),
                      other_spectrum_separation_lower=scalar_packet(other_separation),
                      refined_eigenvalue=scalar_packet(rayleigh),
                      reference_overlap_lower=scalar_packet((overlap - angle * refnorm).lower()))
        self.packet = packet
        return enclosed, rayleigh, lower_float(arb(packet["selected_gap_lower"]["ball"])), upper_float(residual_upper)


def dense_native(left: np.ndarray, coefficients: np.ndarray, fraction: float) -> np.ndarray:
    f = exact(fraction)
    out = np.asarray([arb(0) for _ in left], dtype=object)
    for i, coefficient in enumerate(reversed(coefficients)):
        for j, value in enumerate(coefficient):
            out[j] = (out[j] + exact(value)) * (f if i % 2 == 0 else 1 - f)
    return np.asarray([v + exact(a) for v, a in zip(out, left, strict=True)], dtype=object)


def run(center: Path, output: Path, points: tuple[str, ...], precision: int) -> dict:
    ctx.prec = precision
    output.mkdir(parents=True, exist_ok=True)
    with np.load(center) as source:
        weights = np.asarray(source["state_weights"], dtype=float)
        reference = np.asarray(source["branch_reference"], dtype=float)
        first = np.asarray([exact(v) for v in source["centers"][0]], dtype=object)
        first_s = exact(source["signed_descriptors"][0])
        bracket = int(source["stop_bracket_fine_grid_index"][0])
        fraction = float(source["stop_dense_fraction"][0])
        endpoint = dense_native(source["fine_grid_augmented_action_values"][bracket],
                                source["fine_grid_DOP853_dense_coefficients"][bracket], fraction)
        terminal = np.asarray([endpoint[i] / exact(weights[i]) for i in range(owner.STATE)], dtype=object)
        stored_terminal = np.asarray(source["centers"][-1], dtype=float)
    payload = {"center_npz": str(center.resolve()),
               "center_SHA256": hashlib.sha256(center.read_bytes()).hexdigest().upper(),
               "source_SHA256": {
                   str(path.resolve()): hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest().upper()
                   for path in (Path(__file__), Path(owner.__file__), ROOT / "src/bhsm/interface/current_action_response_capture.py")
               },
               "precision_bits": precision, "selected_branch": SELECTED,
               "requested_points": list(points),
               "scope": "OUTWARD_POINT_RATES_ON_STORED_CENTER_ONLY_NO_FLOW_TUBE_OR_FIRST_HIT",
               "rate_owner": str(Path(owner.__file__).resolve()),
               "point_definitions": {
                   "first_stored": "Exact dyadic import of stored raw98 first center and signed descriptor.",
                   "native_terminal": "Exact dyadic native degree7 polynomial at saved terminal fraction; raw state is action polynomial divided by exact imported weights; descriptor is not clamped.",
               },
               "terminal_interval": bracket, "terminal_fraction": fraction,
               "terminal_native_descriptor": scalar_packet(endpoint[-1]),
               "terminal_native_to_stored_raw_difference_norm_upper": scalar_packet(sum(abs(terminal[i] - exact(stored_terminal[i])) ** 2 for i in range(owner.STATE)).sqrt().upper()),
               "points": {}}
    arrays = {"state_weights_balls": np.asarray([exact(v).str(140) for v in weights]),
              "branch_reference_balls": np.asarray([exact(v).str(140) for v in reference])}
    for name in points:
        state, descriptor = (first, first_s) if name == "first_stored" else (terminal, endpoint[-1])
        verified = VerifiedPointEigenline()
        previous = owner._eigenline
        owner._eigenline = verified
        start = time.perf_counter()
        try:
            rate, internal = evaluate_shared_rate(owner, state, descriptor, weights, reference, None)
        finally:
            owner._eigenline = previous
        elapsed = time.perf_counter() - start
        norm = internal["norm_G"]
        if not norm.is_finite() or not norm > 0:
            raise ArithmeticError("cancelled field norm is not verified positive")
        if not all(v.is_finite() for v in rate.value):
            raise ArithmeticError("nonfinite normalized point rate")
        scalars = {key: scalar_packet(internal[key]) for key in
                   ("descriptor", "eigenvalue", "bpsi", "cpsi", "remainder", "delta", "norm_G")}
        scalars["descriptor_arc_rate"] = scalar_packet(rate.value[-1])
        row = {"elapsed_seconds": elapsed, "spectral_enclosure": verified.packet,
               "scalars": scalars, "cancelled_field_norm_verified_positive": True,
               "descriptor_arc_rate_verified_negative": bool(rate.value[-1] < 0),
               "Delta_verified_negative": bool(internal["delta"] < 0),
               "normalized_rate_finite": True,
               "rate_component_balls": [v.str(140) for v in rate.value]}
        payload["points"][name] = row
        arrays[name + "_raw_state_balls"] = np.asarray([v.str(140) for v in state])
        arrays[name + "_normalized_rate_balls"] = np.asarray([v.str(140) for v in rate.value])
        arrays[name + "_eigenvector_balls"] = np.asarray([v.str(140) for v in internal["psi"]])
        arrays[name + "_hard_response_balls"] = np.asarray([v.str(140) for v in internal["hard"]])
        arrays[name + "_reduced_hessian_balls"] = np.asarray([[v.str(140) for v in row] for row in verified.reduced_hessian])
        arrays[name + "_full_approximate_basis_balls"] = np.asarray([[v.str(140) for v in row] for row in verified.approximate_basis])
        arrays[name + "_normalized_point_eigenvector_balls"] = np.asarray([v.str(140) for v in verified.normalized_point])
        payload["all_requested_point_rates_finite"] = set(payload["points"]) == set(points)
        (output / "report.json").write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n")
        np.savez_compressed(output / "point_balls.npz", **arrays)
        print(json.dumps({"point": name, "elapsed_seconds": elapsed,
                          "descriptor_arc_rate": scalars["descriptor_arc_rate"],
                          "Delta": scalars["delta"],
                          "verified_gap_lower": verified.packet["selected_gap_lower"]["lower"]}), flush=True)
    return payload


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--center", type=Path, default=DEFAULT_CENTER)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--points", nargs="+", choices=("first_stored", "native_terminal"), default=["first_stored", "native_terminal"])
    parser.add_argument("--precision", type=int, default=384)
    args = parser.parse_args()
    run(args.center, args.output, tuple(args.points), args.precision)


if __name__ == "__main__":
    main()
