"""Versioned native unresolved observations, independent of resolved-image data.

Native values and source line identities are never replaced by invented lens
observables. Time-origin arithmetic below is deliberately not a clock or
heliocentric/barycentric conversion.
"""
from copy import deepcopy
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re

import numpy as np

OBSERVATION_SCHEMA = "bhsm_unresolved_observations/1"
SOURCE_WARNING = "ERROR: data not sorted in HJD!"


def _canonical_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                    allow_nan=False).encode("utf8")).hexdigest()


@dataclass
class UnresolvedPhotometry:
    """One or more instruments on a declared compatible relative-time system."""
    document: dict

    def __post_init__(self):
        self.document = deepcopy(self.document)
        if self.document.get("schema") != OBSERVATION_SCHEMA:
            raise ValueError("unsupported unresolved observation schema")
        if self.document.get("observable") != "apparent_magnitude":
            raise ValueError("this route requires native apparent magnitudes; difference flux needs a reference-subtraction model")
        common_origin = self.document.get("common_numeric_origin_jd", 2450000.0)
        if isinstance(common_origin, bool) or not isinstance(common_origin, (int, float)) or not np.isfinite(common_origin):
            raise ValueError("common numeric time origin must be finite")
        rows = self.document.get("rows", [])
        if not rows:
            raise ValueError("no unresolved photometric measurements")
        instruments = self.document.get("instruments", {})
        identities = set()
        for row in rows:
            identity = row.get("source_row_id")
            if not isinstance(identity, str) or not identity or identity in identities:
                raise ValueError("missing or duplicate source row identity")
            identities.add(identity)
            if row.get("instrument") not in instruments:
                raise ValueError("row instrument has no calibration/time metadata")
            for key in ("native_time", "magnitude", "magnitude_error"):
                if isinstance(row.get(key), bool) or not isinstance(row.get(key), (int, float)) or not np.isfinite(row[key]):
                    raise ValueError(f"{identity}: {key} must be finite")
            if row["magnitude_error"] <= 0:
                raise ValueError(f"{identity}: magnitude_error must be positive")
        for instrument, metadata in instruments.items():
            timing = metadata.get("time", {})
            if timing.get("reference") != "HJD" or timing.get("unit") != "day":
                raise ValueError(f"{instrument}: rectilinear native route requires explicit HJD/day convention")
            if isinstance(timing.get("numeric_origin_jd"), bool) or not isinstance(timing.get("numeric_origin_jd"), (int, float)) or not np.isfinite(timing["numeric_origin_jd"]):
                raise ValueError(f"{instrument}: numeric time origin must be declared, never guessed")
            if not timing.get("clock_scale"):
                raise ValueError(f"{instrument}: clock scale must be declared or explicitly UNSPECIFIED")
            if not metadata.get("filter") or not metadata.get("calibration"):
                raise ValueError(f"{instrument}: filter and calibration provenance required")
        scales = {x["time"]["clock_scale"] for x in instruments.values()}
        if len(scales) != 1:
            raise ValueError("incompatible clock scales; supply a verified conversion before combining instruments")
        self.document.setdefault("metadata", {})
        self.document.setdefault("transformations", [])
        if len(instruments) > 1 and scales == {"UNSPECIFIED"}:
            assumption = self.document["metadata"].get("relative_time_combination_assumption")
            if not assumption:
                raise ValueError("joint unknown-clock fit requires an explicit limited relative-time combination assumption")

    @property
    def rows(self):
        return self.document["rows"]

    @property
    def instruments(self):
        return tuple(self.document["instruments"])

    @property
    def common_origin_jd(self):
        return float(self.document.get("common_numeric_origin_jd", 2450000.0))

    @property
    def times(self):
        origin = self.common_origin_jd
        return np.asarray([r["native_time"] +
                           (self.document["instruments"][r["instrument"]]["time"]["numeric_origin_jd"] - origin)
                           for r in self.rows], dtype=float)

    @property
    def magnitudes(self):
        return np.asarray([r["magnitude"] for r in self.rows], dtype=float)

    @property
    def errors(self):
        return np.asarray([r["magnitude_error"] for r in self.rows], dtype=float)

    @property
    def instrument_indices(self):
        mapping = {key: i for i, key in enumerate(self.instruments)}
        return np.asarray([mapping[r["instrument"]] for r in self.rows], dtype=int)

    @property
    def sha256(self):
        return _canonical_hash(self.document)

    def to_dict(self):
        return deepcopy(self.document)

    @classmethod
    def from_dict(cls, document):
        return cls(document)


def _parse_native(raw, source_name, instrument, *, allow_ogle_annotation, benchmark_header=False):
    path = Path(source_name)
    digest = hashlib.sha256(raw).hexdigest()
    rows, annotations = [], []
    for number, line in enumerate(raw.decode("utf8").splitlines(), 1):
        text = line.strip()
        if not text or text.startswith("#"):
            if text:
                annotations.append({"line": number, "text": line, "kind": "comment"})
            continue
        if allow_ogle_annotation and text == SOURCE_WARNING:
            annotations.append({"line": number, "text": line, "kind": "publisher_chronology_warning"})
            continue
        if benchmark_header and not rows and text.split() == ["hjd", "mag", "mag_err"]:
            if any(a["kind"] == "column_header" for a in annotations):
                raise ValueError(f"{path.name}:{number}: repeated benchmark column header")
            annotations.append({"line": number, "text": line, "kind": "column_header"})
            continue
        fields = text.split()
        if len(fields) != 3:
            raise ValueError(f"{path.name}:{number}: expected exactly 3 numeric columns, got {len(fields)}; only the documented exact OGLE warning is recognized")
        try:
            values = [float(v) for v in fields]
        except ValueError as error:
            raise ValueError(f"{path.name}:{number}: malformed numeric measurement") from error
        if not all(np.isfinite(values)) or values[2] <= 0:
            raise ValueError(f"{path.name}:{number}: finite values and positive magnitude uncertainty required")
        rows.append({"source_file": path.name, "source_sha256": digest, "source_line": number,
                     "source_row_id": f"{digest}:{number}", "instrument": instrument,
                     "native_time": values[0], "magnitude": values[1], "magnitude_error": values[2],
                     "quality_flags": []})
    times = np.asarray([r["native_time"] for r in rows])
    unique_times, counts = np.unique(times, return_counts=True)
    duplicates = unique_times[counts > 1].tolist()
    summary = {"filename": path.name, "sha256": digest, "byte_count": len(raw),
               "numeric_rows": len(rows), "annotations": annotations,
               "native_order_strictly_increasing": bool(np.all(np.diff(times) > 0)),
               "duplicate_times": duplicates,
               "duplicate_policy": "retained with distinct source row identities; no averaging or thinning",
               "rows_sorted": False}
    return rows, summary


def load_ogle_photometry(path, metadata=None):
    """Load the actual optimized OGLE-III 3-column format without rescaling errors.

    Optional metadata is analysis context (event id, aliases, coordinates, URL),
    not independent fitted measurements. Its `instrument`/`filter` keys override
    the explicit defaults for a differently documented OGLE-like table.
    """
    path = Path(path)
    return parse_ogle_photometry(path.read_bytes(), source_name=path.name, metadata=metadata)


def parse_ogle_photometry(content, *, source_name="uploaded_ogle.dat", metadata=None):
    """Byte-preserving upload counterpart of load_ogle_photometry."""
    if not isinstance(content, bytes):
        raise TypeError("native observation content must be bytes")
    metadata = deepcopy(metadata or {})
    instrument = metadata.pop("instrument", "OGLE-III")
    filter_name = metadata.pop("filter", "I")
    rows, source = _parse_native(content, source_name, instrument, allow_ogle_annotation=True)
    document = {
        "schema": OBSERVATION_SCHEMA, "observable": "apparent_magnitude",
        "common_numeric_origin_jd": 2450000.0,
        "instruments": {instrument: {"filter": filter_name,
            "time": {"reference": "HJD", "numeric_origin_jd": 2450000.0,
                     "clock_scale": "UNSPECIFIED", "unit": "day"},
            "magnitude_convention": "published OGLE I apparent magnitude",
            "calibration": "OGLE-III class-A optimized reduction; published error corrections already applied",
            "error_treatment": "native positive magnitude errors unchanged; diagonal independence is an analysis assumption"}},
        "sources": [source], "rows": rows, "metadata": metadata,
        "transformations": [{"operation": "numeric_origin_arithmetic_only", "common_origin_jd": 2450000.0,
                             "qualification": "No clock-scale or heliocentric/barycentric conversion performed."}]}
    return UnresolvedPhotometry(document)


def load_benchmark_photometry(paths, metadata=None):
    """Load 2022 Zenodo OGLE/MOA native HJD magnitudes, separate instrument fits.

    `paths` is {"OGLE": path, "MOA": path}; any other instrument requires its
    own declared metadata and is refused rather than assigned a guessed filter.
    """
    return parse_benchmark_photometry({name: {"content": Path(path).read_bytes(),
        "source_name": Path(path).name} for name, path in paths.items()}, metadata=metadata)


def parse_benchmark_photometry(contents, metadata=None):
    """`contents` maps OGLE/MOA to {content: bytes, source_name: str}."""
    instruments, rows, sources = {}, [], []
    for instrument, item in contents.items():
        name = instrument.upper()
        if name not in {"OGLE", "MOA"}:
            raise ValueError("benchmark instrument must be OGLE or MOA")
        new_rows, source = _parse_native(item["content"], item["source_name"], instrument,
                                         allow_ogle_annotation=False, benchmark_header=True)
        rows.extend(new_rows)
        sources.append(source)
        instruments[instrument] = {
            "filter": "I" if name == "OGLE" else "MOA broad optical calibrated to OGLE-III",
            "time": {"reference": "HJD", "numeric_origin_jd": 0.0,
                     "clock_scale": "UNSPECIFIED", "unit": "day"},
            "magnitude_convention": "published native apparent magnitude",
            "calibration": "Zenodo 6607578 v1.0.0 (2022); OGLE-IV I" if name == "OGLE" else
                           "Zenodo 6607578 v1.0.0 (2022); MOA calibrated to OGLE-III",
            "error_treatment": "published positive magnitude errors unchanged; no additional historical correction"}
    combined_metadata = deepcopy(metadata or {})
    combined_metadata.setdefault("relative_time_combination_assumption",
        "Rectilinear photometric screen assumes published OGLE/MOA HJD days share an adequate relative-day axis. This is not verified clock equivalence and cannot support precision annual parallax.")
    return UnresolvedPhotometry({"schema": OBSERVATION_SCHEMA, "observable": "apparent_magnitude",
        "common_numeric_origin_jd": 2450000.0, "instruments": instruments, "sources": sources,
        "rows": rows, "metadata": combined_metadata, "transformations": [{
            "operation": "numeric_origin_arithmetic_only", "formula": "native HJD - 2450000",
            "qualification": "Relative-time rectilinear screen only; HJD clock scale remains unspecified."}]})


def _aliases(text):
    return [] if text == "-" else [x for x in re.split(r"[,;]", text) if x]


def load_ogle_catalog(path):
    """Parse all 26 physical columns; no catalog fit enters the likelihood."""
    path = Path(path)
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    result = {}
    for number, line in enumerate(raw.decode("utf8").splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        f = line.split()
        if len(f) != 26:
            raise ValueError(f"{path.name}:{number}: full OGLE catalog requires 26 physical fields, got {len(f)}")
        try:
            n = int(f[0]); values = [float(x) for x in f[5:24]]
        except ValueError as error:
            raise ValueError(f"{path.name}:{number}: malformed catalog value") from error
        if not np.all(np.isfinite(values)):
            raise ValueError(f"{path.name}:{number}: nonfinite catalog value")
        event = f"OGLE3-ULENS-{n:04d}"
        if event in result:
            raise ValueError(f"duplicate primary catalog identity {event}")
        v, verr = float(f[22]), float(f[23])
        result[event] = {"event_id": event, "catalog_id": f"{n:04d}", "ra_j2000": f[1], "dec_j2000": f[2],
            "field_chip": f[3], "star_number": f[4], "published_t0_hjd_minus_2450000": float(f[5]),
            "published_tE_days": float(f[8]), "published_u0": float(f[11]),
            "published_source_flux_fraction": float(f[14]), "published_baseline_I_magnitude": float(f[17]),
            "published_chi_square": float(f[20]), "published_dof": int(f[21]),
            "V_magnitude": None if v == 99.999 else v, "V_error": None if verr == 9.999 else verr,
            "ews_alias": None if f[24] == "-" else f[24], "ews_aliases": _aliases(f[24]),
            "overlap_alias": None if f[25] == "-" else f[25], "overlap_aliases": _aliases(f[25]),
            "source_sha256": digest, "source_line": number, "source_row_id": f"{digest}:{number}",
            "native_fields": f, "role": "published fit metadata; selection/initialization only, not likelihood observations"}
    return result


def reproduce_pilot_selection(catalog, manifest):
    """Recompute the declared pre-fit 100-event selection and its canonical hash."""
    if isinstance(manifest, (str, Path)):
        manifest = json.loads(Path(manifest).read_text(encoding="utf8"))
    salt = manifest["rule"]["salt"]
    long = [key for key, row in catalog.items() if row["published_tE_days"] >= 150]
    controls = [key for key, row in catalog.items() if 10 <= row["published_tE_days"] < 50]
    controls.sort(key=lambda key: (hashlib.sha256((salt + key).encode("ascii")).hexdigest(), int(key.rsplit("-", 1)[1])))
    selected = sorted(long + controls[:25], key=lambda key: int(key.rsplit("-", 1)[1]))
    expected = sorted([row["event_id"] for row in manifest["selected"]], key=lambda key: int(key.rsplit("-", 1)[1]))
    if len(long) != 75 or len(controls) != 2272 or len(selected) != 100 or selected != expected:
        raise ValueError("frozen pilot membership/count does not reproduce")
    digest = hashlib.sha256(("\n".join(selected) + "\n").encode("ascii")).hexdigest()
    expected_hash = "0cf5dbf714a99567ccfc8448f53560333ed4597115a2801138ac707926a8a4a7"
    if digest != expected_hash:
        raise ValueError("frozen pilot canonical-ID hash does not match")
    source_hashes = {row["source_sha256"] for row in catalog.values()}
    if source_hashes != {manifest["parent_catalog_sha256"]}:
        raise ValueError("pilot parent catalog hash does not match")
    return {"cohort_id": manifest["cohort_id"], "selected_ids": selected,
            "selected_ids_sha256": digest, "long_duration_count": len(long), "control_count": 25,
            "eligible_control_count": len(controls), "status": "EXACT_SELECTION_REPRODUCED"}
