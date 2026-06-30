"""Optional PyROOT adapter for the BHSM-inspired boundary coordinate utility."""

from __future__ import annotations

from pathlib import Path
from typing import Any


INTEGRATION_STATUS = "OPTIONAL_ROOT_ADAPTER_NOT_RUNTIME_VALIDATED_IN_REPOSITORY_CI"


def header_path() -> Path:
    return Path(__file__).resolve().parents[1] / "include" / "BHSMCoordinate.hxx"


def install(ROOT: Any) -> None:
    """Declare the header in an already imported PyROOT runtime."""

    header = header_path().as_posix()
    if not ROOT.gInterpreter.Declare(f'#include "{header}"'):
        raise RuntimeError("ROOT failed to declare BHSMCoordinate.hxx")


def add_boundary_columns(
    dataframe: Any,
    *,
    t: str = "t",
    x: str = "x",
    y: str = "y",
    z: str = "z",
    prefix: str = "bhsm",
) -> Any:
    """Return an RDataFrame with one state object and five derived columns."""

    state = f"{prefix}_state"
    expression = f"bhsm::root::MapBoundaryState({t}, {x}, {y}, {z})"
    result = dataframe.Define(state, expression)
    for suffix in ("radius", "ux", "uy", "uz", "minkowski_interval"):
        result = result.Define(f"{prefix}_{suffix}", f"{state}.{suffix}")
    return result
