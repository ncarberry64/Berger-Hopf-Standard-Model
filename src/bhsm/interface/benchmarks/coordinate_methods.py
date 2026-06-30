"""Controlled coordinate-mapping kernels for a synthetic performance audit.

This module does not model detector propagation, magnetic fields, material
interactions, fitting, or production HEP reconstruction. It compares three
implementations of the same Cartesian-state normalization task.
"""

from __future__ import annotations

import ctypes
import hashlib
import math
import platform
import statistics
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable

import numpy as np


KERNEL_STATUS = "SYNTHETIC_MICROBENCHMARK_NOT_PRODUCTION_HEP_VALIDATION"
BHSM_KERNEL_STATUS = "BHSM_INSPIRED_BOUNDARY_MAP_NOT_OFFICIAL_TRACKING_ENGINE"
BOUNDARY_GENERIC = 0
BOUNDARY_POLE = 1
BOUNDARY_AZIMUTH_SEAM = 2
BOUNDARY_NEAR_ORIGIN = 3


@dataclass(frozen=True)
class DatasetSummary:
    event_count: int
    boundary_fraction_requested: float
    boundary_event_count: int
    pole_count: int
    azimuth_seam_count: int
    near_origin_count: int
    bytes: int
    sha256: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class KernelBenchmark:
    kernel: str
    implementation_status: str
    timings_seconds: tuple[float, ...]
    median_seconds: float
    minimum_seconds: float
    maximum_seconds: float
    events_per_second: float
    peak_rss_bytes: int | None
    output_sha256: str
    output_checksum: float
    hardware_branch_count: int | None
    hardware_branch_misses: int | None
    branch_miss_rate: float | None
    branch_counter_status: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


Kernel = Callable[[np.ndarray], np.ndarray]


def generate_kinematic_dataset(
    event_count: int,
    boundary_fraction: float = 0.30,
    seed: int = 1729,
) -> tuple[np.ndarray, np.ndarray, DatasetSummary]:
    """Return deterministic `(t,x,y,z)` states with explicit edge populations."""

    if event_count <= 0:
        raise ValueError("event_count must be positive")
    if not 0.0 <= boundary_fraction <= 1.0:
        raise ValueError("boundary_fraction must be between 0 and 1")
    rng = np.random.default_rng(seed)
    xyz = rng.normal(size=(event_count, 3))
    radii = rng.lognormal(mean=0.0, sigma=0.5, size=event_count)
    xyz *= (radii / np.linalg.norm(xyz, axis=1))[:, None]
    labels = np.full(event_count, BOUNDARY_GENERIC, dtype=np.uint8)

    boundary_count = int(round(event_count * boundary_fraction))
    pole_count = boundary_count // 2
    seam_count = boundary_count // 3
    origin_count = boundary_count - pole_count - seam_count

    if pole_count:
        signs = rng.choice(np.array([-1.0, 1.0]), size=pole_count)
        tiny = np.finfo(np.float64).eps * radii[:pole_count]
        xyz[:pole_count, 0] = tiny * rng.normal(size=pole_count)
        xyz[:pole_count, 1] = tiny * rng.normal(size=pole_count)
        xyz[:pole_count, 2] = signs * radii[:pole_count]
        labels[:pole_count] = BOUNDARY_POLE

    seam_start = pole_count
    seam_stop = seam_start + seam_count
    if seam_count:
        seam_radii = radii[seam_start:seam_stop]
        xyz[seam_start:seam_stop, 0] = -seam_radii
        xyz[seam_start:seam_stop, 1] = np.finfo(np.float64).eps * seam_radii
        xyz[seam_start:seam_stop, 2] = 0.1 * seam_radii * rng.normal(size=seam_count)
        labels[seam_start:seam_stop] = BOUNDARY_AZIMUTH_SEAM

    origin_start = seam_stop
    origin_stop = origin_start + origin_count
    if origin_count:
        xyz[origin_start:origin_stop] *= 1.0e-12
        labels[origin_start:origin_stop] = BOUNDARY_NEAR_ORIGIN

    spatial_sq = np.einsum("ij,ij->i", xyz, xyz)
    t = np.sqrt(spatial_sq + 1.0)
    states = np.column_stack((t, xyz)).astype(np.float64, copy=False)
    digest = hashlib.sha256(memoryview(np.ascontiguousarray(states))).hexdigest()
    summary = DatasetSummary(
        event_count=event_count,
        boundary_fraction_requested=boundary_fraction,
        boundary_event_count=int(np.count_nonzero(labels)),
        pole_count=int(np.count_nonzero(labels == BOUNDARY_POLE)),
        azimuth_seam_count=int(np.count_nonzero(labels == BOUNDARY_AZIMUTH_SEAM)),
        near_origin_count=int(np.count_nonzero(labels == BOUNDARY_NEAR_ORIGIN)),
        bytes=states.nbytes + labels.nbytes,
        sha256=digest,
    )
    return states, labels, summary


def branchy_cylindrical_scalar(states: np.ndarray) -> np.ndarray:
    """Map states through scalar cylindrical/spherical coordinates with pole branches."""

    output = np.empty((len(states), 5), dtype=np.float64)
    pole_tolerance = 32.0 * np.finfo(np.float64).eps
    for index, (t, x, y, z) in enumerate(states):
        rho = math.hypot(x, y)
        radius = math.hypot(rho, z)
        if radius == 0.0:
            ux = uy = uz = 0.0
        elif rho <= pole_tolerance * radius:
            ux, uy, uz = x / radius, y / radius, z / radius
        else:
            phi = math.atan2(y, x)
            if phi > math.pi:
                phi -= 2.0 * math.pi
            elif phi <= -math.pi:
                phi += 2.0 * math.pi
            theta = math.atan2(rho, z)
            sin_theta = math.sin(theta)
            ux = sin_theta * math.cos(phi)
            uy = sin_theta * math.sin(phi)
            uz = math.cos(theta)
        output[index] = radius, ux, uy, uz, t * t - radius * radius
    return output


def cylindrical_vectorized_control(states: np.ndarray) -> np.ndarray:
    """Vectorized cylindrical/spherical control for implementation-fair comparison."""

    t = states[:, 0]
    x, y, z = states[:, 1], states[:, 2], states[:, 3]
    rho = np.hypot(x, y)
    radius = np.hypot(rho, z)
    safe_radius = np.where(radius == 0.0, 1.0, radius)
    phi = np.arctan2(y, x)
    theta = np.arctan2(rho, z)
    sin_theta = np.sin(theta)
    unit = np.column_stack((sin_theta * np.cos(phi), sin_theta * np.sin(phi), np.cos(theta)))
    pole = rho <= (32.0 * np.finfo(np.float64).eps) * safe_radius
    unit[pole] = states[pole, 1:4] / safe_radius[pole, None]
    unit[radius == 0.0] = 0.0
    return np.column_stack((radius, unit, t * t - radius * radius))


def bhsm_boundary_vectorized(states: np.ndarray) -> np.ndarray:
    """Apply a direct vectorized boundary normalization without angle branches."""

    t = states[:, 0]
    xyz = states[:, 1:4]
    radius = np.sqrt(np.einsum("ij,ij->i", xyz, xyz))
    safe_radius = np.where(radius == 0.0, 1.0, radius)
    unit = xyz / safe_radius[:, None]
    unit[radius == 0.0] = 0.0
    return np.column_stack((radius, unit, t * t - radius * radius))


KERNELS: dict[str, Kernel] = {
    "branchy_cylindrical_scalar": branchy_cylindrical_scalar,
    "cylindrical_vectorized_control": cylindrical_vectorized_control,
    "bhsm_boundary_vectorized": bhsm_boundary_vectorized,
}


def validate_kernel_equivalence(states: np.ndarray) -> dict[str, object]:
    """Compare both candidate kernels to the scalar coordinate baseline."""

    baseline = branchy_cylindrical_scalar(states)
    rows: dict[str, object] = {}
    for name in ("cylindrical_vectorized_control", "bhsm_boundary_vectorized"):
        candidate = KERNELS[name](states)
        delta = np.abs(candidate - baseline)
        rows[name] = {
            "max_absolute_difference": float(np.max(delta)),
            "mean_absolute_difference": float(np.mean(delta)),
            "allclose_rtol_1e_12_atol_1e_12": bool(
                np.allclose(candidate, baseline, rtol=1.0e-12, atol=1.0e-12)
            ),
        }
    return rows


def _peak_rss_bytes() -> int | None:
    if platform.system() == "Windows":
        class ProcessMemoryCounters(ctypes.Structure):
            _fields_ = [
                ("cb", ctypes.c_ulong),
                ("PageFaultCount", ctypes.c_ulong),
                ("PeakWorkingSetSize", ctypes.c_size_t),
                ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t),
                ("PeakPagefileUsage", ctypes.c_size_t),
            ]

        counters = ProcessMemoryCounters()
        counters.cb = ctypes.sizeof(counters)
        handle = ctypes.windll.kernel32.GetCurrentProcess()
        get_memory = ctypes.windll.kernel32.K32GetProcessMemoryInfo
        get_memory.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(ProcessMemoryCounters),
            ctypes.c_ulong,
        ]
        get_memory.restype = ctypes.c_int
        ok = get_memory(handle, ctypes.byref(counters), counters.cb)
        return int(counters.PeakWorkingSetSize) if ok else None
    import resource

    usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(usage if platform.system() == "Darwin" else usage * 1024)


def branch_counter_status() -> str:
    if platform.system() == "Linux":
        return "LINUX_PERF_REQUIRED_NOT_COLLECTED_BY_PYTHON_RUNNER"
    return f"HARDWARE_COUNTERS_UNAVAILABLE_ON_{platform.system().upper()}"


def benchmark_kernel(
    kernel_name: str,
    states: np.ndarray,
    repeats: int = 3,
    warmup_events: int = 10_000,
) -> KernelBenchmark:
    """Benchmark one kernel; dataset generation and output hashing are outside timing."""

    if kernel_name not in KERNELS:
        raise KeyError(kernel_name)
    if repeats <= 0:
        raise ValueError("repeats must be positive")
    kernel = KERNELS[kernel_name]
    warmup = states[: min(len(states), warmup_events)]
    kernel(warmup)
    timings = []
    output = None
    for _ in range(repeats):
        start = time.perf_counter_ns()
        output = kernel(states)
        timings.append((time.perf_counter_ns() - start) / 1.0e9)
    assert output is not None
    median = statistics.median(timings)
    digest = hashlib.sha256(memoryview(np.ascontiguousarray(output))).hexdigest()
    return KernelBenchmark(
        kernel=kernel_name,
        implementation_status=(
            BHSM_KERNEL_STATUS if kernel_name == "bhsm_boundary_vectorized" else KERNEL_STATUS
        ),
        timings_seconds=tuple(timings),
        median_seconds=median,
        minimum_seconds=min(timings),
        maximum_seconds=max(timings),
        events_per_second=len(states) / median,
        peak_rss_bytes=_peak_rss_bytes(),
        output_sha256=digest,
        output_checksum=float(np.sum(output, dtype=np.float64)),
        hardware_branch_count=None,
        hardware_branch_misses=None,
        branch_miss_rate=None,
        branch_counter_status=branch_counter_status(),
    )


def write_json(path: str | Path, payload: dict[str, object]) -> Path:
    import json

    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return destination
