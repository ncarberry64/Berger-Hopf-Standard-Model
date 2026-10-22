"""CSV ingestion without sorting rows or replacing a supplied covariance.

Measurements have one header containing ``epoch_yr`` and every ``data.FIELDS``
name exactly once. Column order is arbitrary; output fields have the canonical
``FIELDS`` order. The required, headerless covariance is already in canonical
field order within each measurement row, including every cross-row covariance.
Metadata is a JSON dataset skeleton, without measurement or covariance arrays.
Paths use UTF-8 with an optional BOM; caller-owned text streams stay open.
"""
from contextlib import contextmanager
from copy import deepcopy
import csv
import json
from math import isfinite
from os import PathLike
from pathlib import Path

from .data import FIELDS, load_dataset


@contextmanager
def _text_source(source, label):
    if isinstance(source, (str, PathLike)):
        with Path(source).open("r", encoding="utf-8-sig", newline="") as handle:
            yield handle
    elif callable(getattr(source, "read", None)):
        yield source
    else:
        raise ValueError(f"{label} must be a path or readable text stream")


def _number(value, label):
    try:
        parsed = float(value)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError(f"{label} must be numeric") from error
    if not isfinite(parsed):
        raise ValueError(f"{label} must be finite")
    return parsed


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"metadata contains duplicate key {key!r}")
        result[key] = value
    return result


def _invalid_constant(value):
    raise ValueError(f"metadata contains nonfinite JSON constant {value}")


def _metadata(source):
    if isinstance(source, dict):
        raw = deepcopy(source)
    else:
        with _text_source(source, "metadata") as handle:
            text = handle.read()
        if not isinstance(text, str):
            raise ValueError("metadata must be a readable text stream")
        try:
            raw = json.loads(text.removeprefix("\ufeff"),
                             object_pairs_hook=_unique_object,
                             parse_constant=_invalid_constant)
        except json.JSONDecodeError as error:
            raise ValueError(f"metadata is not valid JSON: {error.msg}") from error
    if not isinstance(raw, dict):
        raise ValueError("metadata must contain a JSON object")
    for key in ("epochs_yr", "observations", "covariance"):
        if key in raw:
            raise ValueError(f"metadata must not contain {key}; supply it through CSV")
    if not isinstance(raw.get("geometry"), dict):
        raise ValueError("metadata.geometry must be an object")
    if not isinstance(raw.get("provenance"), dict):
        raise ValueError("metadata.provenance must be an object")
    if "analysis" in raw and not isinstance(raw["analysis"], dict):
        raise ValueError("metadata.analysis must be an object")
    return raw


def _measurements(source):
    required = ["epoch_yr", *FIELDS]
    with _text_source(source, "measurements") as handle:
        reader = csv.reader(handle, strict=True)
        try:
            header = next(reader, None)
            if not header:
                raise ValueError("measurements CSV requires a header")
            header[0] = header[0].removeprefix("\ufeff")
            if len(header) != len(set(header)):
                raise ValueError("measurements CSV contains duplicate columns")
            missing = sorted(set(required) - set(header))
            extra = sorted(set(header) - set(required))
            if missing or extra:
                details = []
                if missing:
                    details.append("missing columns: " + ", ".join(missing))
                if extra:
                    details.append("extra columns: " + ", ".join(extra))
                raise ValueError("measurements CSV " + "; ".join(details))
            indices = [header.index(field) for field in required]
            epochs, observations = [], []
            for line, row in enumerate(reader, start=2):
                if len(epochs) >= 80:
                    raise ValueError("measurements CSV must contain 3 to 80 rows")
                if len(row) != len(header):
                    raise ValueError(f"measurements CSV row {line} must have {len(header)} columns")
                values = [_number(row[index], f"measurements CSV row {line}, {field}")
                          for field, index in zip(required, indices)]
                epochs.append(values[0])
                observations.append(values[1:])
        except csv.Error as error:
            raise ValueError(f"measurements CSV is malformed: {error}") from error
    if len(epochs) < 3:
        raise ValueError("measurements CSV must contain 3 to 80 rows")
    return epochs, observations


def _covariance(source, size):
    if source is None:
        raise ValueError("a full dense covariance CSV is required")
    values = []
    with _text_source(source, "covariance") as handle:
        reader = csv.reader(handle, strict=True)
        try:
            for line, row in enumerate(reader, start=1):
                if len(values) >= size:
                    raise ValueError(f"covariance CSV must have exactly {size} rows and columns")
                if len(row) != size:
                    raise ValueError(f"covariance CSV row {line} must have exactly {size} columns")
                if line == 1:
                    row[0] = row[0].removeprefix("\ufeff")
                values.append([_number(value, f"covariance CSV row {line}, column {column}")
                               for column, value in enumerate(row, start=1)])
        except csv.Error as error:
            raise ValueError(f"covariance CSV is malformed: {error}") from error
    if len(values) != size:
        raise ValueError(f"covariance CSV must have exactly {size} rows and columns")
    return values


def import_measurement_csv(measurements, metadata, covariance):
    """Return a validated raw dataset from measurements, metadata, and full C.

    Each argument may be a filesystem path or readable text stream; ``metadata``
    may also be a dict (copied, never mutated). The covariance has no header and
    is in row-major measurement order, with canonical ``FIELDS`` per row.
    No epochs are sorted, no errors are inferred, and no covariance terms are
    dropped. Physical units are given by the exact field names.
    """
    raw = _metadata(metadata)
    epochs, observations = _measurements(measurements)
    raw["epochs_yr"] = epochs
    raw["observations"] = observations
    raw["covariance"] = _covariance(covariance, 6 * len(epochs))
    raw.setdefault("fields", list(FIELDS))
    # Return the raw, unsymmetrized supplied matrix. load_dataset independently
    # checks dimensions, finite values, symmetry, and positive definiteness.
    return load_dataset(raw).raw
