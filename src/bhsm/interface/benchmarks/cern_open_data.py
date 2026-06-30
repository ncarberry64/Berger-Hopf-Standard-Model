"""Checksum-gated CMS Open Data loading for coordinate benchmarks."""

from __future__ import annotations

import hashlib
import json
import urllib.request
import zlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np


REAL_DATA_STATUS = "CERN_OPEN_DATA_FOUR_VECTOR_BENCHMARK_NOT_TRACK_RECONSTRUCTION"


@dataclass(frozen=True)
class OpenDataVectors:
    states: np.ndarray
    event_count: int
    source_sha256: str

    @property
    def vector_count(self) -> int:
        return int(self.states.shape[0])


def load_manifest(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    required = {"record_id", "doi", "record_url", "file", "license", "benchmark_scope"}
    missing = sorted(required - payload.keys())
    if missing:
        raise ValueError(f"open-data manifest missing keys: {', '.join(missing)}")
    return payload


def file_checksums(path: str | Path) -> tuple[str, str]:
    sha256 = hashlib.sha256()
    adler32 = 1
    with Path(path).open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            sha256.update(chunk)
            adler32 = zlib.adler32(chunk, adler32)
    return sha256.hexdigest(), f"{adler32 & 0xFFFFFFFF:08x}"


def verify_download(path: str | Path, manifest: dict[str, Any]) -> None:
    source = Path(path)
    expected = manifest["file"]
    if source.stat().st_size != int(expected["size_bytes"]):
        raise ValueError("CERN Open Data file size does not match manifest")
    sha256, adler32 = file_checksums(source)
    if sha256 != expected["sha256"]:
        raise ValueError("CERN Open Data SHA-256 does not match manifest")
    if f"adler32:{adler32}" != expected["portal_checksum"]:
        raise ValueError("CERN Open Data Adler-32 does not match portal checksum")


def download_open_data(
    manifest: dict[str, Any], destination: str | Path, *, timeout: float = 120.0
) -> Path:
    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(target.suffix + ".part")
    request = urllib.request.Request(
        manifest["file"]["url"], headers={"User-Agent": "BHSM-open-data-benchmark/1.0"}
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response, temporary.open("wb") as out:
            while chunk := response.read(1024 * 1024):
                out.write(chunk)
        verify_download(temporary, manifest)
        temporary.replace(target)
    finally:
        if temporary.exists():
            temporary.unlink()
    return target


def load_cms_dimuon_vectors(
    path: str | Path, manifest: dict[str, Any], *, verify: bool = True
) -> OpenDataVectors:
    source = Path(path)
    if verify:
        verify_download(source, manifest)
    values = np.loadtxt(
        source,
        delimiter=",",
        skiprows=1,
        usecols=(3, 4, 5, 6, 11, 12, 13, 14),
        dtype=np.float64,
    )
    if values.ndim == 1:
        values = values.reshape(1, 8)
    states = np.ascontiguousarray(values.reshape(-1, 4))
    if states.shape[1] != 4 or not np.all(np.isfinite(states)):
        raise ValueError("CMS dimuon four-vectors must be finite E,px,py,pz rows")
    source_sha256, _ = file_checksums(source)
    return OpenDataVectors(states=states, event_count=int(values.shape[0]), source_sha256=source_sha256)


def boundary_diagnostics(states: np.ndarray) -> dict[str, int]:
    xyz = states[:, 1:4]
    rho = np.hypot(xyz[:, 0], xyz[:, 1])
    radius = np.linalg.norm(xyz, axis=1)
    safe_radius = np.where(radius == 0.0, 1.0, radius)
    phi = np.arctan2(xyz[:, 1], xyz[:, 0])
    return {
        "near_polar_axis_1e_6": int(np.count_nonzero(rho <= 1.0e-6 * safe_radius)),
        "near_azimuth_seam_1e_4_rad": int(
            np.count_nonzero(np.abs(np.abs(phi) - np.pi) <= 1.0e-4)
        ),
        "near_zero_momentum_1e_6_gev": int(np.count_nonzero(radius <= 1.0e-6)),
    }
