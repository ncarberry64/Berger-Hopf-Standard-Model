"""Explicitly gated optional parallax and unresolved-centroid conventions.

No ephemeris or HST epoch origin is guessed. The supplied 2022 HST tables can
be ingested here; their precision inference remains blocked by the unresolved
time origin and calibration/frame provenance. Forward functions support
separately verified contexts and are tested against summed image positions.

Conventions: NE=(north,east); u points from lens to unlensed source. The dark
centroid shift is +thetaE*u/(u^2+2), away from the lens. Gould's geocentric Sun
displacement gives d_tau=piN*d_sN+piE*d_sE and
d_beta=piN*d_sE-piE*d_sN (Gould 2004, DOI 10.1086/382782).
Centroid conventions: Dominik & Sahu 2000, DOI 10.1086/308716.
"""
from copy import deepcopy
import hashlib
import json
import numbers
from pathlib import Path

import numpy as np

from .photometry import MAG_FACTOR, pspl_magnification

ASTROMETRY_SCHEMA = "bhsm_unresolved_astrometry/1"


class PrecisionMetadataError(ValueError):
    """Precision inference needs the listed verified metadata, not a guess."""


def load_hst_astrometry(paths, metadata=None):
    """Read native 2022 Zenodo seven-column tables without assigning MJD.

    paths maps filter name to filename. Each source row is retained. Shared
    native times are labelled as the same visit, with no independence claim.
    """
    rows, sources = [], []
    for name, filename in paths.items():
        path = Path(filename); raw = path.read_bytes(); digest = hashlib.sha256(raw).hexdigest()
        count = 0; annotations = []
        for line_number, text in enumerate(raw.decode("utf8").splitlines(), 1):
            if not text.strip() or text.lstrip().startswith("#"):
                continue
            fields = text.split()
            if count == 0 and fields == ["t", "x", "x_err", "y", "y_err", "mag", "mag_err"]:
                if annotations:
                    raise ValueError(f"{path.name}:{line_number}: repeated HST column header")
                annotations.append({"line": line_number, "text": text, "kind": "column_header"})
                continue
            if len(fields) != 7:
                raise ValueError(f"{path.name}:{line_number}: expected seven native HST columns")
            try:
                t, x, sx, y, sy, mag, smag = map(float, fields)
            except ValueError as error:
                raise ValueError(f"{path.name}:{line_number}: malformed native HST measurement") from error
            if not np.all(np.isfinite([t, x, sx, y, sy, mag, smag])) or min(sx, sy, smag) <= 0:
                raise ValueError(f"{path.name}:{line_number}: finite native values and positive errors required")
            rows.append({"native_time": t, "x_mas": x, "x_error_mas": sx, "y_mas": y, "y_error_mas": sy,
                "magnitude_vega": mag, "magnitude_error": smag, "instrument": "HST", "filter": name,
                "source_file": path.name, "source_sha256": digest, "source_line": line_number,
                "source_row_id": f"{digest}:{line_number}", "quality_flags": [],
                "shared_native_epoch_id": f"HST-native-{t:.14g}"})
            count += 1
        sources.append({"filename": path.name, "sha256": digest, "byte_count": len(raw), "numeric_rows": count,
                        "annotations": annotations})
    defaults = {"time_scale": "UTC", "time_numeric_origin_jd": None,
        "native_axes": "relative RA, Dec in milliarcseconds; RA*cos(Dec) convention not established by supplied README",
        "ra_cosdec_convention_verified": False, "frame_and_filter_alignment_verified": False,
        "already_applied_cross_filter_corrections": "UNRESOLVED",
        "covariance_status": "per-point marginal errors only; no supplied full covariance",
        "shared_filter_dependence": "UNRESOLVED", "source": "Zenodo 6607578 version 1.0.0, 2022 reduction"}
    defaults.update(deepcopy(metadata or {}))
    document = {"schema": ASTROMETRY_SCHEMA, "observable": "unresolved_relative_centroid_and_magnitude",
        "rows": rows, "sources": sources, "metadata": defaults,
        "unique_native_visits": len({r["shared_native_epoch_id"] for r in rows}),
        "transformations": [], "precision_inference": precision_metadata_status(defaults)}
    json.dumps(document, allow_nan=False)
    return document


def precision_metadata_status(metadata):
    missing = []
    origin = metadata.get("time_numeric_origin_jd")
    if isinstance(origin, bool) or not isinstance(origin, numbers.Real) or not np.isfinite(origin):
        missing.append("native HST numeric epoch origin is not defined as a finite number; UTC alone is not an epoch origin")
    if not metadata.get("verified_time_transform_provenance"):
        missing.append("verified native-to-ephemeris time transformation and underlying photometric HJD clock scale")
    if metadata.get("ra_cosdec_convention_verified") is not True:
        missing.append("whether relative RA is the tangent-plane alpha*cos(delta) coordinate")
    if metadata.get("frame_and_filter_alignment_verified") is not True:
        missing.append("reference frame, existing cross-filter corrections and shared-epoch dependence")
    if not metadata.get("noise_and_frame_model"):
        missing.append("explicit angular noise, reference-frame and cross-filter dependence model")
    if not metadata.get("verified_observer_ephemeris_provenance"):
        missing.append("verified observer ephemeris and sky-position convention")
    return {"status": "BLOCKED_MISSING_VERIFIED_METADATA" if missing else "METADATA_DECLARED_FOR_VALIDATED_ROUTE",
            "missing": missing, "joint_mass_inference": "UNRESOLVED" if missing else "NOT_AUTOMATICALLY_IDENTIFIED"}


def require_precision_metadata(document):
    status = precision_metadata_status(document.get("metadata", {}))
    if status["missing"]:
        raise PrecisionMetadataError("; ".join(status["missing"]))
    return status


def _finite_array(value, shape_tail, name):
    array = np.asarray(value, dtype=float)
    if tuple(array.shape[-len(shape_tail):]) != tuple(shape_tail) or np.any(~np.isfinite(array)):
        raise ValueError(f"{name}: finite array ending in shape {shape_tail} required")
    return array


def project_icrs_ne(vectors, ra_deg, dec_deg):
    """Project ICRS Cartesian AU vectors on the declared north/east tangent plane."""
    vectors = _finite_array(vectors, (3,), "ICRS vectors")
    ra, dec = np.deg2rad([float(ra_deg), float(dec_deg)])
    if not np.all(np.isfinite([ra, dec])) or abs(dec) > np.pi / 2:
        raise ValueError("finite ICRS RA/Dec and -90<=Dec<=90 required")
    east = np.asarray([-np.sin(ra), np.cos(ra), 0])
    north = np.asarray([-np.cos(ra) * np.sin(dec), -np.sin(ra) * np.sin(dec), np.cos(dec)])
    return np.stack([vectors @ north, vectors @ east], axis=-1)


def geocentric_sun_displacement(times_jd_tdb, earth_position_au, reference_jd_tdb,
                                earth_reference_position_au, earth_reference_velocity_au_day,
                                ra_deg, dec_deg):
    """Gould geocentric Sun displacement, from supplied verified ephemeris values.

    Positions are observer barycentric ICRS; the apparent-Sun displacement is
    minus the observer displacement after removing reference position/velocity.
    This function performs geometry, not UTC/HJD conversion or ephemeris lookup.
    """
    times = np.asarray(times_jd_tdb, dtype=float)
    earth = _finite_array(earth_position_au, (3,), "observer positions")
    origin = _finite_array(earth_reference_position_au, (3,), "reference position")
    velocity = _finite_array(earth_reference_velocity_au_day, (3,), "reference velocity")
    if times.ndim != 1 or earth.shape != (len(times), 3) or origin.shape != (3,) or velocity.shape != (3,):
        raise ValueError("one observer position per TDB JD and one reference position/velocity required")
    if not np.all(np.isfinite(times)) or not np.isfinite(reference_jd_tdb):
        raise ValueError("finite verified JD TDB times required")
    sun = -earth + origin + (times - float(reference_jd_tdb))[:, None] * velocity
    return project_icrs_ne(sun, ra_deg, dec_deg)


def parallax_trajectory(times, *, t0, tE_days, u0, pi_E_north, pi_E_east, sun_displacement_ne):
    """Return (tau,beta) with the explicitly signed Gould cross-product convention."""
    times = np.asarray(times, dtype=float)
    ds = _finite_array(sun_displacement_ne, (2,), "projected Sun displacement")
    if times.ndim != 1 or ds.shape != (len(times), 2):
        raise ValueError("one NE ephemeris displacement per time required")
    values = [t0, tE_days, u0, pi_E_north, pi_E_east]
    if not np.all(np.isfinite(values)) or tE_days <= 0:
        raise ValueError("finite trajectory parameters and positive tE required")
    tau = (times - t0) / tE_days + pi_E_north * ds[:, 0] + pi_E_east * ds[:, 1]
    beta = u0 + pi_E_north * ds[:, 1] - pi_E_east * ds[:, 0]
    return np.column_stack([tau, beta])


def predict_parallax_photometry(dataset, parameters, context):
    """Optional forward likelihood route, blocked unless context is documented.

    Context requires row_ids in the original order, times_relative_days already
    transformed to the declared ephemeris clock, sun_displacement_ne_au, and
    metadata accepted by require_precision_metadata. No ephemeris interpolation
    or inferred time origin is performed here.
    """
    from .observations import UnresolvedPhotometry
    dataset = dataset if isinstance(dataset, UnresolvedPhotometry) else UnresolvedPhotometry(dataset)
    require_precision_metadata(context)
    if context.get("row_ids") != [r["source_row_id"] for r in dataset.rows]:
        raise PrecisionMetadataError("ephemeris/source row identity mismatch")
    vector = parallax_trajectory(context["times_relative_days"], t0=parameters["t0"],
        tE_days=parameters["tE_days"], u0=parameters["u0"], pi_E_north=parameters["pi_E_north"],
        pi_E_east=parameters["pi_E_east"], sun_displacement_ne=context["sun_displacement_ne_au"])
    a = pspl_magnification(np.linalg.norm(vector, axis=1))
    output = np.empty(len(a)); indices = dataset.instrument_indices
    for k, name in enumerate(dataset.instruments):
        p = parameters["instruments"][name]; f = float(p["source_fraction"])
        baseline = float(p["baseline_magnitude"])
        if not np.isfinite(f) or not np.isfinite(baseline) or f <= 0 or (f > 1 and not parameters.get("allow_negative_blend", False)):
            raise ValueError("invalid parallax source/blend fraction")
        select = indices == k
        output[select] = baseline - MAG_FACTOR * np.log1p(f * (a[select] - 1))
    if np.any(~np.isfinite(output)):
        raise ValueError("parallax magnitude prediction must be finite")
    return output


def dark_centroid_shift(u_ne, theta_E_mas):
    """Absolute lensed-image centroid minus unlensed source, in NE mas."""
    u = _finite_array(u_ne, (2,), "source-minus-lens separation")
    theta = float(theta_E_mas)
    if not np.isfinite(theta) or theta <= 0:
        raise ValueError("positive finite angular Einstein radius required")
    return theta * u / (np.sum(u * u, axis=-1)[..., None] + 2)


def predict_astrometric_centroid(times_jd, *, reference_jd, source_position_ne_mas,
                                source_proper_motion_ne_mas_yr, source_parallax_mas,
                                parallax_factors_ne, u_ne, theta_E_mas,
                                blend_to_source_flux_ratio=0.0, blend_position_ne_mas=None,
                                frame_offset_ne_mas=(0.0, 0.0), precision_context=None):
    """Optional unresolved-centroid route with source motion/parallax and blending.

    Source parallax factors are -observer ICRS position projected in NE, in AU.
    Blend positions are absolute in the same frame at each epoch; for a luminous
    lens they equal source_position(t)-thetaE*u. Filter-specific ratios/offsets
    must be passed separately, with actual alignment provenance in context.
    All angular errors/frame covariances remain an external likelihood choice.
    """
    if precision_context is None:
        raise PrecisionMetadataError("a verified time/frame/calibration/ephemeris context is required")
    require_precision_metadata(precision_context)
    t = np.asarray(times_jd, dtype=float)
    position = _finite_array(source_position_ne_mas, (2,), "source position")
    motion = _finite_array(source_proper_motion_ne_mas_yr, (2,), "source proper motion")
    factors = _finite_array(parallax_factors_ne, (2,), "parallax factors")
    u = _finite_array(u_ne, (2,), "source-minus-lens separation")
    offset = _finite_array(frame_offset_ne_mas, (2,), "frame offset")
    if t.ndim != 1 or u.shape != (len(t), 2) or factors.shape != u.shape:
        raise ValueError("one NE trajectory and parallax factor per epoch required")
    if position.shape != (2,) or motion.shape != (2,) or offset.shape != (2,):
        raise ValueError("two-component source position, motion and frame offset required")
    if not np.all(np.isfinite(t)) or not np.all(np.isfinite([reference_jd, source_parallax_mas])) or source_parallax_mas < 0:
        raise ValueError("finite times and nonnegative source parallax required")
    source = position + (t - reference_jd)[:, None] * motion / 365.25 + float(source_parallax_mas) * factors
    images = source + dark_centroid_shift(u, theta_E_mas)
    ratio = float(blend_to_source_flux_ratio)
    if not np.isfinite(ratio) or ratio < 0:
        raise ValueError("luminous blend flux must be nonnegative")
    if ratio == 0:
        return images + offset
    if blend_position_ne_mas is None:
        raise ValueError("a luminous blend requires its position in the declared source frame")
    blend = _finite_array(blend_position_ne_mas, (2,), "blend positions")
    if blend.shape not in {(2,), images.shape}:
        raise ValueError("blend position must be one NE pair or one pair per epoch")
    amplification = pspl_magnification(np.linalg.norm(u, axis=1))
    return ((amplification[:, None] * images + ratio * blend) / (amplification + ratio)[:, None]) + offset
