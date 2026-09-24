from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path

import numpy as np
from fractions import Fraction


def qfloat(x):
    """Convert Gate-7 exact JSON scalars, including 'p/q', to float."""
    if isinstance(x, str):
        x = x.strip()
        try:
            return float(Fraction(x))
        except (ValueError, ZeroDivisionError):
            return float(x)
    return float(x)


def qarray(x):
    """Recursively parse an exact-rational JSON array into float64."""
    arr = np.asarray(x, dtype=object)
    out = np.empty(arr.shape, dtype=float)
    it = np.nditer(
        arr,
        flags=["multi_index", "refs_ok", "zerosize_ok"],
        op_flags=["readonly"],
    )
    for v in it:
        out[it.multi_index] = qfloat(v.item())
    return out



ROOT = Path.cwd()

AXES_PATH = (
    ROOT
    / "artifacts"
    / "action_extension"
    / "BHSM_AE4_CURRENT_C2_GREEN_IMAGE_PARTITION_RECONCILIATION.npz"
)

OUT = (
    Path(r"C:\Users\carbe\Manuscript-Generation")
    / "artifacts"
    / "GATE7_LOCAL_COSMOLOGY_RESPONSE_V1.json"
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest().upper()


def is_adjoint_object(obj) -> bool:
    required = {
        "input_map",
        "point_line_map",
        "point_response_map",
        "fixed_axis_covectors",
    }
    return (
        isinstance(obj, dict)
        and required.issubset(obj.keys())
        and isinstance(obj.get("fixed_axis_covectors"), dict)
        and "axis_line" in obj["fixed_axis_covectors"]
        and "axis_response" in obj["fixed_axis_covectors"]
    )


def find_adjoint_records():
    """
    Prefer files with 'adjoint' in the filename.  Fall back to a bounded
    scan of Gate-7 JSON artifacts.  Nothing is modified.
    """
    search_roots = [
        ROOT / "artifacts" / "flagship_integration",
        ROOT / "artifacts" / "gate7",
        ROOT / "tmp",
    ]

    seen = set()
    found = []

    preferred = []

    for base in search_roots:
        if not base.exists():
            continue
        for p in base.rglob("*.json"):
            if "adjoint" in p.name.lower():
                preferred.append(p)

    def inspect(paths):
        for p in paths:
            rp = str(p.resolve())
            if rp in seen:
                continue
            seen.add(rp)

            try:
                if p.stat().st_size > 50_000_000:
                    continue
                obj = json.loads(p.read_text(encoding="utf-8-sig"))
            except Exception:
                continue

            if is_adjoint_object(obj):
                found.append((p, obj))

    inspect(preferred)

    if not found:
        # Bounded fallback: likely Gate-7 areas only.
        candidates = []
        for base in search_roots[:2]:
            if not base.exists():
                continue
            for p in base.rglob("*.json"):
                candidates.append(p)
                if len(candidates) >= 6000:
                    break
            if len(candidates) >= 6000:
                break
        inspect(candidates)

    return found


if not AXES_PATH.exists():
    raise FileNotFoundError(
        f"Missing Gate-7 axis file:\n{AXES_PATH}"
    )

records = find_adjoint_records()

if not records:
    raise RuntimeError(
        "Could not locate a Gate-7 adjoint JSON containing "
        "input_map, point_line_map, point_response_map and "
        "fixed_axis_covectors."
    )


# ---------------------------------------------------------------------
# Gate-7 local topographic axis
# ---------------------------------------------------------------------

with np.load(AXES_PATH, allow_pickle=False) as z:
    if "current_center_green_image_unit_mid" not in z:
        raise KeyError(
            "current_center_green_image_unit_mid absent from axis artifact"
        )

    axes = np.asarray(
        z["current_center_green_image_unit_mid"],
        dtype=float,
    )

if axes.ndim != 2 or axes.shape[1] != 74:
    raise ValueError(
        f"Expected Gate-7 axes (*,74), got {axes.shape}"
    )

# This is the exact direction used by the Gate-7 full-input/output
# calculation shown in certify_n12_gate7_full_input_output.py.
phi = np.asarray(axes[14], dtype=float)

phi_norm = float(np.linalg.norm(phi))

if not np.isfinite(phi_norm) or phi_norm == 0.0:
    raise ValueError("Gate-7 axis 14 has invalid norm")

phi = phi / phi_norm


def unit(v):
    v = np.asarray(v, dtype=float)
    n = float(np.linalg.norm(v))
    if n == 0.0:
        return v, n
    return v / n, n


results = []

print("=" * 96)
print("GATE-7 -> LOCAL COSMOLOGY DIRECT RESPONSE EXTRACTION")
print("=" * 96)
print("NO SUPERNOVA AMPLITUDE USED")
print("Gate-7 physical input dimension = 74")
print("local topographic direction      = normalized Gate-7 axis 14")
print("axis original norm               =", phi_norm)
print("adjoint records found            =", len(records))


for path, adj in records:

    U = qarray(
        adj["input_map"],
    )

    Lmap = qarray(
        adj["point_line_map"],
    )

    Rmap = qarray(
        adj["point_response_map"],
    )

    v_line = qarray(
        adj["fixed_axis_covectors"]["axis_line"],
    )

    v_resp = qarray(
        adj["fixed_axis_covectors"]["axis_response"],
    )

    if U.ndim != 2 or U.shape[1] != 74:
        continue

    if Lmap.ndim != 2 or Lmap.shape[1] != 74:
        continue

    if Rmap.ndim != 2 or Rmap.shape[1] != 74:
        continue

    if len(v_line) != Lmap.shape[0]:
        continue

    if len(v_resp) != Rmap.shape[0]:
        continue

    # --------------------------------------------------------------
    # Compose the Gate-7 fixed metric covectors with the 74D physical
    # input maps.
    #
    # These are the two scalar response covectors on the common
    # physical input space.
    # --------------------------------------------------------------

    g_A = v_line @ Lmap
    g_psi = v_resp @ Rmap

    g_A = np.asarray(g_A, dtype=float)
    g_psi = np.asarray(g_psi, dtype=float)

    # Direct local metric response to the normalized topographic axis.
    R_A = float(g_A @ phi)
    R_psi = float(g_psi @ phi)

    Rgphi = np.array(
        [R_A, R_psi],
        dtype=float,
    )

    # Conventional scalar combinations.
    R_W = float(0.5 * (R_A + R_psi))
    R_slip = float(0.5 * (R_A - R_psi))

    # --------------------------------------------------------------
    # Diagnose independence/conditioning of the two metric channels.
    # --------------------------------------------------------------

    C = np.vstack([
        g_A,
        g_psi,
    ])

    svals = np.linalg.svd(
        C,
        compute_uv=False,
    )

    rank = int(
        np.linalg.matrix_rank(
            C,
            tol=max(C.shape) * np.finfo(float).eps * svals[0]
            if svals.size and svals[0] > 0
            else 0.0,
        )
    )

    gram = C @ C.T

    if rank == 2:
        gram_inv = np.linalg.inv(gram)

        # Minimum-Euclidean-norm primal basis dual to the two response
        # covectors:
        #
        #     C @ P_g = I_2
        #
        P_g = C.T @ gram_inv

        duality_residual = float(
            np.linalg.norm(
                C @ P_g - np.eye(2)
            )
        )

        phi_metric_projection = (
            P_g @ (C @ phi)
        )

        metric_projection_fraction = float(
            np.linalg.norm(
                phi_metric_projection
            )
        )

        phi_orth = (
            phi - phi_metric_projection
        )

        orthogonal_fraction = float(
            np.linalg.norm(phi_orth)
        )

        condition = float(
            svals[0] / svals[-1]
        )

    else:
        P_g = None
        duality_residual = None
        metric_projection_fraction = None
        orthogonal_fraction = None
        condition = math.inf

    uA, nA = unit(g_A)
    uP, nP = unit(g_psi)

    if nA > 0 and nP > 0:
        channel_cosine = float(
            np.clip(
                uA @ uP,
                -1.0,
                1.0,
            )
        )
        channel_angle_deg = float(
            np.degrees(
                np.arccos(channel_cosine)
            )
        )
    else:
        channel_cosine = None
        channel_angle_deg = None

    family = adj.get(
        "family",
        "unknown",
    )

    result = {
        "family":
            family,

        "adjoint_path":
            str(path),

        "adjoint_SHA256":
            sha256(path),

        "input_map_shape":
            list(U.shape),

        "point_line_map_shape":
            list(Lmap.shape),

        "point_response_map_shape":
            list(Rmap.shape),

        "metric_covector_norms": {
            "A_line":
                nA,
            "psi_response":
                nP,
        },

        "metric_channel_singular_values":
            svals.tolist(),

        "metric_channel_rank":
            rank,

        "metric_channel_condition_number":
            condition,

        "metric_channel_cosine":
            channel_cosine,

        "metric_channel_angle_deg":
            channel_angle_deg,

        "local_topographic_axis_response": {
            "R_A":
                R_A,

            "R_psi":
                R_psi,

            "R_gphi":
                Rgphi.tolist(),

            "R_W_half_sum":
                R_W,

            "R_slip_half_difference":
                R_slip,

            "response_norm":
                float(
                    np.linalg.norm(Rgphi)
                ),
        },

        "dual_basis_diagnostics": {
            "C_P_minus_I_norm":
                duality_residual,

            "axis_metric_projection_fraction":
                metric_projection_fraction,

            "axis_orthogonal_fraction":
                orthogonal_fraction,
        },
    }

    results.append(result)

    print()
    print("-" * 96)
    print("family       =", family)
    print("adjoint      =", path)
    print("U shape      =", U.shape)
    print("line map     =", Lmap.shape)
    print("response map =", Rmap.shape)

    print()
    print("metric-channel singular values =", svals)
    print("metric-channel rank            =", rank)
    print("metric-channel condition       =", condition)
    print("metric-channel angle [deg]     =", channel_angle_deg)

    print()
    print("R_A          =", f"{R_A:+.16e}")
    print("R_psi        =", f"{R_psi:+.16e}")
    print("R_W          =", f"{R_W:+.16e}")
    print("R_slip       =", f"{R_slip:+.16e}")
    print(
        "|R_gphi|     =",
        f"{np.linalg.norm(Rgphi):.16e}",
    )

    if duality_residual is not None:
        print(
            "dual residual =",
            f"{duality_residual:.3e}",
        )
        print(
            "axis metric-projection norm =",
            f"{metric_projection_fraction:.16e}",
        )
        print(
            "axis orthogonal norm        =",
            f"{orthogonal_fraction:.16e}",
        )


if not results:
    raise RuntimeError(
        "Adjoint records were found but none had compatible "
        "74D Gate-7 map dimensions."
    )


# ---------------------------------------------------------------------
# Cross-family consistency
# ---------------------------------------------------------------------

cross = None

if len(results) >= 2:

    vectors = np.asarray([
        r["local_topographic_axis_response"]["R_gphi"]
        for r in results
    ])

    mean = vectors.mean(axis=0)

    deviations = np.linalg.norm(
        vectors - mean,
        axis=1,
    )

    scale = max(
        float(np.linalg.norm(mean)),
        1.0e-300,
    )

    cross = {
        "mean_R_gphi":
            mean.tolist(),

        "max_absolute_vector_deviation":
            float(
                deviations.max()
            ),

        "max_relative_vector_deviation":
            float(
                deviations.max() / scale
            ),
    }

    print()
    print("=" * 96)
    print("CROSS-RECORD CONSISTENCY")
    print("=" * 96)
    print("mean R_gphi =", mean)
    print(
        "max vector deviation =",
        cross["max_absolute_vector_deviation"],
    )
    print(
        "max relative deviation =",
        cross["max_relative_vector_deviation"],
    )


payload = {
    "schema":
        "BHSM-Gate7-local-cosmology-response-v1",

    "status":
        "DIRECT_GATE7_LOCAL_RESPONSE_EXTRACTED",

    "bridge_identification": {
        "Gate7_74D_physical_input":
            "cosmological local physical tangent",

        "Gate7_axis_14":
            "normalized local topographic direction phi_loc",

        "fixed_axis_axis_line":
            "first scalar metric-response coordinate A",

        "fixed_axis_axis_response":
            "second scalar metric-response coordinate psi",

        "classification":
            "EXPLICIT_CROSS_PROGRAM_BRIDGE_IDENTIFICATION",

        "not_claimed":
            [
                "new Gate7 closure",
                "independent proof of the semantic identification",
                "supernova calibration",
                "absolute local source-population normalization",
            ],
    },

    "no_SN_amplitude_used":
        True,

    "axes_path":
        str(AXES_PATH),

    "axes_SHA256":
        sha256(AXES_PATH),

    "axis_index":
        14,

    "axis_original_norm":
        phi_norm,

    "records":
        results,

    "cross_record_consistency":
        cross,

    "next_step":
        (
            "compose extracted R_gphi with the existing closed-S3 "
            "optical observation functional and independently supplied "
            "local source profile; compare only afterward with the "
            "held-out low-z residual"
        ),
}

OUT.parent.mkdir(
    parents=True,
    exist_ok=True,
)

OUT.write_text(
    json.dumps(
        payload,
        indent=2,
        allow_nan=False,
    ) + "\n",
    encoding="utf-8",
)

print()
print("=" * 96)
print("WROTE")
print("=" * 96)
print(OUT)
print("DONE")
