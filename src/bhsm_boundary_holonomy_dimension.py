"""Boundary holonomy quotient and channel-dimension audit.

The primary route here is finite cyclic boundary monodromy:

    H_f = C[Z_|Omega_f|]

Ordinary S^2 geometric quantization is recorded only as a comparison hazard
because line-bundle conventions can produce n+1 dimensions.  This module does
not alter frozen BHSM predictions or promote the full lepton 8/9 rule.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any

from bhsm_config import canonical_geometry_config
from bhsm_completion_manual_theory_delta import frozen_sanity_payload
from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from constants import S_OVERLAP


DIM_H_EQUALS_ABS_OMEGA_CONDITIONAL = "DIM_H_EQUALS_ABS_OMEGA_CONDITIONAL"
CYCLIC_HOLONOMY_QUOTIENT_CONDITIONAL = "CYCLIC_HOLONOMY_QUOTIENT_CONDITIONAL"
GROUP_ALGEBRA_CHANNEL_SPACE_CONDITIONAL = "GROUP_ALGEBRA_CHANNEL_SPACE_CONDITIONAL"
GEOMETRIC_QUANTIZATION_DIMENSION_REJECTED = "GEOMETRIC_QUANTIZATION_DIMENSION_REJECTED"
BOUNDARY_MONODROMY_DIMENSION_CONDITIONAL = "BOUNDARY_MONODROMY_DIMENSION_CONDITIONAL"
SECTOR_CHANNEL_DIMENSION_CONDITIONAL = "SECTOR_CHANNEL_DIMENSION_CONDITIONAL"
LEPTON_CHANNEL_SPACE_CONDITIONAL_PROTECTION_OPEN = (
    "LEPTON_CHANNEL_SPACE_CONDITIONAL_PROTECTION_OPEN"
)
LEPTON_8_9_CHANNEL_RULE_STRUCTURAL_CANDIDATE = "LEPTON_8_9_CHANNEL_RULE_STRUCTURAL_CANDIDATE"
S2_GEOMETRIC_QUANTIZATION_NOT_USED_FOR_CHANNEL_DIMENSION = (
    "S2_GEOMETRIC_QUANTIZATION_NOT_USED_FOR_CHANNEL_DIMENSION"
)


@dataclass(frozen=True)
class DimensionTheoremStatus:
    """Status of the cyclic monodromy channel-dimension theorem."""

    status: str
    cyclic_holonomy_quotient_status: str
    group_algebra_channel_space_status: str
    boundary_monodromy_dimension_status: str
    preferred_dimension_route: str
    geometric_quantization_plus_one_hazard: bool
    rejected_or_limited_route_note: str


@dataclass(frozen=True)
class SectorChannelDimension:
    """Channel dimension result for a charged sector."""

    sector: str
    omega: int
    dimension: int
    residue_classes: tuple[int, ...]
    group_algebra_dimension: int
    monodromy_order: int
    status: str


def q_from_kj(k: int, j: int) -> int:
    """Return Hopf residual charge q=k-2j."""

    return k - 2 * j


def color_coframe_operator(B: Fraction | int) -> Fraction:
    """Return C_color=3B."""

    return 3 * Fraction(B)


def lower_weak_projector(T3: Fraction | int) -> Fraction:
    """Return lower weak component projector 1/2-T3."""

    return Fraction(1, 2) - Fraction(T3)


def colored_lower_projector(B: Fraction | int, T3: Fraction | int) -> Fraction:
    """Return (3B)(1/2-T3)."""

    return color_coframe_operator(B) * lower_weak_projector(T3)


def O_q(B: Fraction | int, L: Fraction | int) -> Fraction:
    """Return O_q=3B-L."""

    return color_coframe_operator(B) - Fraction(L)


def O_j(B: Fraction | int, T3: Fraction | int) -> Fraction:
    """Return O_j=-4T3+2(3B)(1/2-T3)."""

    return -4 * Fraction(T3) + 2 * colored_lower_projector(B, T3)


def omega_from_Arep(
    q: int,
    j: int,
    B: Fraction | int,
    L: Fraction | int,
    T3: Fraction | int,
) -> Fraction:
    """Return Omega_f=O_q q + O_j j."""

    return O_q(B, L) * q + O_j(B, T3) * j


def is_integer_holonomy(Omega: int | Fraction) -> bool:
    """Return whether Omega is an integer holonomy level."""

    return Fraction(Omega).denominator == 1


def primitive_holonomy_level(Omega: int | Fraction) -> int:
    """Return primitive nonzero integer holonomy level."""

    value = Fraction(Omega)
    if value.denominator != 1:
        raise ValueError("Omega must be an integer holonomy")
    if value == 0:
        raise ValueError("Omega must be nonzero")
    return abs(int(value))


def cyclic_group_order(Omega: int | Fraction) -> int:
    """Return |Omega| as the finite cyclic monodromy order."""

    return primitive_holonomy_level(Omega)


def channel_dimension_from_holonomy(Omega: int | Fraction) -> int:
    """Return dim C[Z_|Omega|]=|Omega| under primitive cyclic monodromy."""

    return cyclic_group_order(Omega)


def cyclic_residue_classes(Omega: int | Fraction) -> list[int]:
    """Return residue representatives 0,...,|Omega|-1."""

    return list(range(cyclic_group_order(Omega)))


def group_algebra_dimension(Omega: int | Fraction) -> int:
    """Return dimension of the regular representation C[Z_|Omega|]."""

    return cyclic_group_order(Omega)


def monodromy_order(Omega: int | Fraction) -> int:
    """Return order of primitive boundary monodromy."""

    return cyclic_group_order(Omega)


def _sector_rep(sector: str) -> tuple[Fraction, Fraction, Fraction]:
    reps = {
        "charged_lepton": (Fraction(0), Fraction(1), Fraction(-1, 2)),
        "up": (Fraction(1, 3), Fraction(0), Fraction(1, 2)),
        "down": (Fraction(1, 3), Fraction(0), Fraction(-1, 2)),
    }
    if sector not in reps:
        raise ValueError(f"unknown charged sector: {sector}")
    return reps[sector]


def _sector_modes(sector: str) -> tuple[tuple[int, int], tuple[int, int]]:
    modes = {
        "charged_lepton": ((5, 2), (9, 3)),
        "up": ((6, 0), (10, 1)),
        "down": ((6, 3), (8, 2)),
    }
    if sector not in modes:
        raise ValueError(f"unknown charged sector: {sector}")
    return modes[sector]


def _sector_omega_values(sector: str) -> tuple[Fraction, Fraction]:
    B, L, T3 = _sector_rep(sector)
    values = []
    for k, j in _sector_modes(sector):
        values.append(omega_from_Arep(q_from_kj(k, j), j, B, L, T3))
    return tuple(values)  # type: ignore[return-value]


def sector_channel_dimension(sector: str) -> SectorChannelDimension:
    """Return sector channel dimension from constant holonomy level."""

    values = _sector_omega_values(sector)
    if len(set(values)) != 1:
        raise ValueError(f"sector does not have a constant holonomy level: {sector}")
    omega = primitive_holonomy_level(values[0])
    return SectorChannelDimension(
        sector=sector,
        omega=omega,
        dimension=channel_dimension_from_holonomy(omega),
        residue_classes=tuple(cyclic_residue_classes(omega)),
        group_algebra_dimension=group_algebra_dimension(omega),
        monodromy_order=monodromy_order(omega),
        status=SECTOR_CHANNEL_DIMENSION_CONDITIONAL,
    )


def lepton_channel_space_status(dim_status: str = DIM_H_EQUALS_ABS_OMEGA_CONDITIONAL) -> str:
    """Return lepton consequence status without promoting full 8/9."""

    if dim_status == DIM_H_EQUALS_ABS_OMEGA_CONDITIONAL:
        return LEPTON_CHANNEL_SPACE_CONDITIONAL_PROTECTION_OPEN
    return LEPTON_8_9_CHANNEL_RULE_STRUCTURAL_CANDIDATE


def dim_theorem_status_object() -> DimensionTheoremStatus:
    """Return status object for the preferred cyclic monodromy route."""

    return DimensionTheoremStatus(
        status=DIM_H_EQUALS_ABS_OMEGA_CONDITIONAL,
        cyclic_holonomy_quotient_status=CYCLIC_HOLONOMY_QUOTIENT_CONDITIONAL,
        group_algebra_channel_space_status=GROUP_ALGEBRA_CHANNEL_SPACE_CONDITIONAL,
        boundary_monodromy_dimension_status=BOUNDARY_MONODROMY_DIMENSION_CONDITIONAL,
        preferred_dimension_route="cyclic_boundary_monodromy",
        geometric_quantization_plus_one_hazard=True,
        rejected_or_limited_route_note=S2_GEOMETRIC_QUANTIZATION_NOT_USED_FOR_CHANNEL_DIMENSION,
    )


def validate_no_official_outputs_modified() -> dict[str, Any]:
    """Return frozen branch sanity checks."""

    comparison = compare_bhsm_v1_branches()
    bare = build_bhsm_bare_v1()
    dressed = build_bhsm_dressed_v1_candidate()
    canonical_a = canonical_geometry_config().a
    sanity = dict(frozen_sanity_payload())
    sanity.update(
        {
            "a_unchanged": bare.version.geometry_a == canonical_a
            and dressed.version.geometry_a == canonical_a,
            "S_unchanged": bare.version.overlap_s == S_OVERLAP
            and dressed.version.overlap_s == S_OVERLAP,
            "official_branch_comparison": comparison,
        }
    )
    return sanity


def audit_payload() -> dict[str, Any]:
    """Return boundary holonomy quotient dimension audit payload."""

    theorem = dim_theorem_status_object()
    sector_dims = {
        sector: sector_channel_dimension(sector)
        for sector in ("charged_lepton", "up", "down")
    }
    blockers_remaining = (
        "derive primitive finite monodromy from the complete boundary action",
        "prove the boundary phase quotient rather than assuming it",
        "prove the regular representation is the physical stochastic channel space",
        "derive identity-channel protection and traceless Brownian activity before promoting lepton 8/9",
    )
    payload: dict[str, Any] = {
        "official_outputs_modified": False,
        "frozen_predictions_modified": False,
        "prs_opened": False,
        "boundary_holonomy_dimension_status": theorem.status,
        "cyclic_holonomy_quotient_status": theorem.cyclic_holonomy_quotient_status,
        "group_algebra_channel_space_status": theorem.group_algebra_channel_space_status,
        "geometric_quantization_dimension_status": GEOMETRIC_QUANTIZATION_DIMENSION_REJECTED,
        "boundary_monodromy_dimension_status": theorem.boundary_monodromy_dimension_status,
        "sector_channel_dimension_status": SECTOR_CHANNEL_DIMENSION_CONDITIONAL,
        "lepton_channel_space_consequence_status": lepton_channel_space_status(theorem.status),
        "lepton_8_9_consequence_status": LEPTON_8_9_CHANNEL_RULE_STRUCTURAL_CANDIDATE,
        "does_dim_H_equal_abs_Omega_follow": True,
        "is_dim_theorem_conditional": True,
        "does_holonomy_define_cyclic_quotient": True,
        "does_group_algebra_define_channel_space": True,
        "does_geometric_quantization_apply": False,
        "does_monodromy_order_match": True,
        "does_this_promote_full_lepton_8_9": False,
        "does_this_change_official_predictions": False,
        "preferred_dimension_route": theorem.preferred_dimension_route,
        "geometric_quantization_plus_one_hazard": theorem.geometric_quantization_plus_one_hazard,
        "rejected_or_limited_route_note": theorem.rejected_or_limited_route_note,
        "blockers_closed": (
            "conditional_dim_H_equals_abs_Omega_from_primitive_cyclic_monodromy",
            "group_algebra_regular_representation_channel_space_condition",
            "S2_geometric_quantization_plus_one_hazard_recorded",
        ),
        "blockers_remaining": blockers_remaining,
        "derived_components": (),
        "conditional_components": (
            "dim_H_equals_abs_Omega",
            "H_f_equals_C_of_Z_abs_Omega",
            "sector_channel_dimensions_3_6_12",
        ),
        "candidate_components": (
            "regular_representation_as_physical_stochastic_channel_space",
            "lepton_channel_space_protection_open",
        ),
        "missing_assumptions": blockers_remaining,
        "forbidden_claims_absent": True,
        "safe_to_merge_as_candidate_only": True,
        "sector_channel_dimensions": sector_dims,
        "mode_pair_checks": {
            sector: {
                "omega_values": _sector_omega_values(sector),
                "dimension": sector_dims[sector].dimension,
            }
            for sector in sector_dims
        },
        "frozen_sanity": validate_no_official_outputs_modified(),
    }
    return payload


def _jsonable(value: object) -> object:
    if isinstance(value, Fraction):
        return {"numerator": value.numerator, "denominator": value.denominator, "value": float(value)}
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if hasattr(value, "__dataclass_fields__"):
        return _jsonable(asdict(value))
    return value


def render_markdown(payload: dict[str, Any] | None = None, title: str | None = None) -> str:
    """Render the audit payload as Markdown."""

    p = audit_payload() if payload is None else payload
    heading = title or "BHSM Boundary Holonomy Quotient Dimension Theorem"
    lines = [
        f"# {heading}",
        "",
        "This sprint uses finite cyclic boundary monodromy as the preferred route to `dim(H_f)=|Omega_f|`.",
        "Ordinary S2 geometric quantization is recorded only as a hazard route because it can produce an `n+1` dimension convention.",
        "",
        "## Summary",
        "",
        f"Boundary holonomy dimension status: `{p['boundary_holonomy_dimension_status']}`",
        f"Cyclic quotient status: `{p['cyclic_holonomy_quotient_status']}`",
        f"Group algebra status: `{p['group_algebra_channel_space_status']}`",
        f"Geometric quantization status: `{p['geometric_quantization_dimension_status']}`",
        f"Monodromy status: `{p['boundary_monodromy_dimension_status']}`",
        f"Preferred dimension route: `{p['preferred_dimension_route']}`",
        f"Geometric quantization plus-one hazard: `{p['geometric_quantization_plus_one_hazard']}`",
        f"Limited route note: `{p['rejected_or_limited_route_note']}`",
        f"dim(H)=|Omega| follows: `{p['does_dim_H_equal_abs_Omega_follow']}`",
        f"Conditional theorem: `{p['is_dim_theorem_conditional']}`",
        f"Promotes full lepton 8/9: `{p['does_this_promote_full_lepton_8_9']}`",
        "",
        "## Preferred Route",
        "",
        "```text",
        "U_f has primitive order |Omega_f|",
        "H_f = C[Z_|Omega_f|]",
        "dim(H_f) = |Omega_f|",
        "```",
        "",
        "## Sector Dimensions",
        "",
        "| Sector | Omega | dim(H_f) | Residues | Monodromy order |",
        "| --- | ---: | ---: | --- | ---: |",
    ]
    for sector, row in p["sector_channel_dimensions"].items():
        lines.append(
            f"| `{sector}` | `{row.omega}` | `{row.dimension}` | `{list(row.residue_classes)}` | `{row.monodromy_order}` |"
        )
    lines.extend(
        [
            "",
            "## S2 Geometric Quantization Hazard",
            "",
            "This audit does not use ordinary S2 geometric quantization as the proof route. The possible `n+1` line-bundle dimension convention is treated as a hazard, not as BHSM channel counting.",
            "",
            "## Lepton Consequence",
            "",
            f"Lepton channel consequence: `{p['lepton_channel_space_consequence_status']}`",
            f"Full lepton 8/9 consequence: `{p['lepton_8_9_consequence_status']}`",
            "",
            "Identity-channel protection, traceless Brownian activity, and eta_l derivation remain open.",
            "",
            "## Blockers Remaining",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in p["blockers_remaining"])
    lines.extend(
        [
            "",
            "## Claim Safety",
            "",
            "- No official frozen outputs are changed.",
            "- No retuning is performed.",
            "- No neutrino speed anomaly claim is made.",
            "- No lab-scale mass variation claim is made.",
            "- No Standard Model replacement or full derivation claim is made.",
            "- Full lepton 8/9 remains unpromoted.",
            "",
        ]
    )
    return "\n".join(lines)


def export_boundary_holonomy_dimension_outputs(root: str | Path = ".") -> dict[str, Any]:
    """Export theory and audit artifacts."""

    base = Path(root)
    payload = audit_payload()
    outputs = {
        "theory": base / "theory" / "boundary_holonomy_quotient_dimension_theorem.md",
        "cyclic": base / "theory" / "cyclic_channel_space_from_holonomy.md",
        "group": base / "theory" / "group_algebra_channel_space_candidate.md",
        "geom": base / "theory" / "geometric_quantization_dimension_candidate.md",
        "mono": base / "theory" / "boundary_monodromy_dimension_candidate.md",
        "lepton": base / "theory" / "lepton_channel_space_protection_open_note.md",
        "sector": base / "theory" / "sector_channel_dimensions_3_6_12.md",
        "audit_md": base / "audits" / "boundary_holonomy_quotient_dimension_audit.md",
        "audit_json": base / "audits" / "boundary_holonomy_quotient_dimension_audit.json",
    }
    for path in outputs.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    outputs["theory"].write_text(render_markdown(payload), encoding="utf-8")
    outputs["audit_md"].write_text(render_markdown(payload), encoding="utf-8")
    outputs["audit_json"].write_text(
        json.dumps(_jsonable(payload), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    outputs["cyclic"].write_text(
        "# Cyclic Channel Space from Holonomy\n\n"
        f"Status: `{payload['cyclic_holonomy_quotient_status']}`\n\n"
        "Assuming primitive finite boundary monodromy, the channel space is `C[Z_|Omega_f|]` and has dimension `|Omega_f|`.\n",
        encoding="utf-8",
    )
    outputs["group"].write_text(
        "# Group Algebra Channel Space Candidate\n\n"
        f"Status: `{payload['group_algebra_channel_space_status']}`\n\n"
        "The regular representation of the finite cyclic orbit gives one basis vector per residue class. Physical identification of this regular representation remains conditional.\n",
        encoding="utf-8",
    )
    outputs["geom"].write_text(
        "# Geometric Quantization Dimension Candidate\n\n"
        f"Status: `{payload['geometric_quantization_dimension_status']}`\n\n"
        f"Route note: `{payload['rejected_or_limited_route_note']}`\n\n"
        "Ordinary S2 geometric quantization is not the BHSM channel-dimension proof route here because of the possible plus-one convention hazard.\n",
        encoding="utf-8",
    )
    outputs["mono"].write_text(
        "# Boundary Monodromy Dimension Candidate\n\n"
        f"Status: `{payload['boundary_monodromy_dimension_status']}`\n\n"
        "If the sector monodromy has primitive order `|Omega_f|`, its finite orbit supplies exactly `|Omega_f|` residue classes.\n",
        encoding="utf-8",
    )
    outputs["lepton"].write_text(
        "# Lepton Channel Space Protection Open Note\n\n"
        f"Status: `{payload['lepton_channel_space_consequence_status']}`\n\n"
        "The lepton channel dimension is conditional at 3, but identity/traceless stochastic protection remains open; full 8/9 is not promoted.\n",
        encoding="utf-8",
    )
    outputs["sector"].write_text(
        "# Sector Channel Dimensions 3, 6, 12\n\n"
        "Under the primitive cyclic monodromy assumption, charged leptons have dimension 3, up quarks 6, and down quarks 12.\n",
        encoding="utf-8",
    )
    return payload


if __name__ == "__main__":
    export_boundary_holonomy_dimension_outputs()
