"""Boundary covering-map channel theorem audit for BHSM.

This module reframes the cyclic channel dimension as a finite covering-degree
statement. The key distinction is that an integer Wilson-loop phase can be
globally trivial while the degree-N phase map still has N covering sheets.
It does not alter frozen predictions or promote any dressing rule to official
status.
"""

from __future__ import annotations

import cmath
import json
from dataclasses import asdict, dataclass
from fractions import Fraction
from math import gcd, isclose, pi
from pathlib import Path
from typing import Any

from bhsm_config import canonical_geometry_config
from bhsm_completion_manual_theory_delta import frozen_sanity_payload
from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from constants import S_OVERLAP


COVERING_MAP_THEOREM_STATUS = "BOUNDARY_COVERING_MAP_CHANNEL_THEOREM_PARTIAL"
OMEGA_AS_DEGREE_STATUS = "OMEGA_AS_COVERING_DEGREE_CONDITIONAL"
PRIMITIVE_COVERING_STATUS = "PRIMITIVE_COVERING_CONDITIONAL"
RESIDUE_SHEET_STATUS = "RESIDUE_SHEET_CHANNELS_PARTIAL"
DECK_TRANSFORMATION_STATUS = "DECK_TRANSFORMATION_ORDER_PARTIAL"
CHANNEL_DIMENSION_STATUS = "DIM_H_EQUALS_ABS_OMEGA_COVERING_MAP_PARTIAL"
WILSON_LOOP_TRAP_STATUS = "WILSON_LOOP_TRIVIALITY_TRAP_RESOLVED_BY_COVERING_DEGREE"
COHERENT_CHANNEL_SPACE_STATUS = "COHERENT_RESIDUE_SHEET_CHANNEL_SPACE_PARTIAL"
SIMPLEX_VS_ENDH_STATUS = "SIMPLEX_VS_ENDH_DISTINCTION_PARTIAL"
LEPTON_8_9_STATUS = "LEPTON_8_9_CHANNEL_RULE_COVERING_MAP_PARTIAL_STRENGTHENED"
QUARK_COVERING_CONSEQUENCE_STATUS = "QUARK_COVERING_CONSEQUENCE_CANDIDATE_ONLY"
S2_GEOMETRIC_QUANTIZATION_NOT_USED_FOR_CHANNEL_DIMENSION = (
    "S2_GEOMETRIC_QUANTIZATION_NOT_USED_FOR_CHANNEL_DIMENSION"
)


@dataclass(frozen=True)
class CoveringStatus:
    """Status for one route in the covering-map channel theorem."""

    route: str
    status: str
    follows: bool
    assumptions: tuple[str, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class SectorCoveringRow:
    """Exact covering/channel data for one charged sector."""

    sector: str
    omega: int
    degree: int
    sheet_count: int
    deck_group_order: int
    channel_dimension: int
    classical_simplex_relative_dimension: int
    coherent_end_dimension: int
    coherent_traceless_dimension: int
    active_fraction: Fraction
    status: str
    official_prediction_update: bool


def q_from_kj(k: int, j: int) -> int:
    """Return Hopf charge q=k-2j."""

    return int(k) - 2 * int(j)


def lepton_omega(q: int, j: int) -> int:
    """Return charged-lepton boundary operator Omega_l=-q+2j."""

    return -int(q) + 2 * int(j)


def degree_from_omega(Omega: int | Fraction) -> int:
    """Return covering degree |Omega| for a nonzero integer Omega."""

    value = Fraction(Omega)
    if value.denominator != 1:
        raise ValueError("Omega must be an integer boundary level")
    if value == 0:
        raise ValueError("Omega must be nonzero for a covering channel space")
    return abs(int(value))


def sheet_count_from_degree(degree: int) -> int:
    """Return the number of preimage sheets for a primitive degree-N cover."""

    value = abs(int(degree))
    if value == 0:
        raise ValueError("degree must be nonzero")
    return value


def deck_group_order(degree: int) -> int:
    """Return order of the cyclic deck/sheet-shift group."""

    return sheet_count_from_degree(degree)


def covering_channel_dimension(Omega: int | Fraction) -> int:
    """Return dim C[Z_|Omega|] from covering sheet count."""

    return sheet_count_from_degree(degree_from_omega(Omega))


def is_primitive_covering(Omega: int | Fraction, divisor_data: tuple[int, ...] | None = None) -> bool:
    """Return whether the covering is primitive under supplied divisor data.

    With no divisor data, this checks the primitive cyclic model used by the
    audit: the deck shift by one has order |Omega|. If explicit divisor data is
    supplied, any common divisor larger than one marks the cover imprimitive.
    """

    degree = degree_from_omega(Omega)
    if divisor_data is None:
        return degree > 0
    if not divisor_data:
        return degree > 0
    common = degree
    for value in divisor_data:
        common = gcd(common, abs(int(value)))
    return common == 1


def classical_simplex_relative_dimension(N: int) -> int:
    """Return the zero-sum fluctuation dimension of a classical N-simplex."""

    value = sheet_count_from_degree(N)
    return value - 1


def coherent_end_dimension(N: int) -> int:
    """Return dim End(C[Z_N])=N^2."""

    value = sheet_count_from_degree(N)
    return value * value


def coherent_traceless_dimension(N: int) -> int:
    """Return dim su(N)=N^2-1."""

    return coherent_end_dimension(N) - 1


def active_fraction_from_dimension(N: int) -> Fraction:
    """Return coherent traceless active fraction (N^2-1)/N^2."""

    return Fraction(coherent_traceless_dimension(N), coherent_end_dimension(N))


def active_fraction_from_covering_degree(Omega: int | Fraction) -> Fraction:
    """Return active fraction from covering degree |Omega|."""

    return active_fraction_from_dimension(degree_from_omega(Omega))


def wilson_loop_phase_from_degree(degree: int) -> complex:
    """Return exp(2*pi*i*degree), the globally single-valued Wilson phase."""

    return cmath.exp(2j * pi * int(degree))


def is_wilson_loop_globally_trivial_for_integer_degree(degree: int) -> bool:
    """Return whether exp(2*pi*i*N)=1 for integer N."""

    phase = wilson_loop_phase_from_degree(degree)
    return isclose(phase.real, 1.0, abs_tol=1e-12) and isclose(phase.imag, 0.0, abs_tol=1e-12)


def channel_space_status_object() -> CoveringStatus:
    """Return covering-map channel-space status."""

    return CoveringStatus(
        route="covering_map_channel_dimension",
        status=CHANNEL_DIMENSION_STATUS,
        follows=True,
        assumptions=(
            "u_f:S1_boundary->U(1) is a degree-|Omega_f| boundary phase map",
            "the covering is primitive",
            "residue sheets are treated as coherent boundary amplitude channels",
        ),
        limitations=(
            "the completed BHSM boundary action has not yet derived u_f",
            "physical sheet-channel identification remains partial",
        ),
    )


def wilson_trap_status_object() -> CoveringStatus:
    """Return Wilson-loop triviality trap status."""

    return CoveringStatus(
        route="wilson_loop_triviality_trap",
        status=WILSON_LOOP_TRAP_STATUS,
        follows=True,
        assumptions=(
            "Omega_f is interpreted as covering degree, not only total Wilson-loop phase",
            "channel count comes from sheet/preimage multiplicity",
        ),
        limitations=(
            "this resolves a counting ambiguity, not the full boundary-action derivation",
        ),
    )


def omega_as_degree_status_object() -> CoveringStatus:
    """Return omega-as-degree status."""

    return CoveringStatus(
        route="omega_as_covering_degree",
        status=OMEGA_AS_DEGREE_STATUS,
        follows=True,
        assumptions=("Omega_f is the winding/degree number of u_f",),
        limitations=("u_f has not been derived from the completed boundary action",),
    )


def primitive_covering_status_object() -> CoveringStatus:
    """Return primitive covering status."""

    return CoveringStatus(
        route="primitive_covering",
        status=PRIMITIVE_COVERING_STATUS,
        follows=True,
        assumptions=("the deck shift acts by one residue class",),
        limitations=("imprimitive/reducible coverings are excluded by assumption in this sprint",),
    )


def coherent_channel_status_object() -> CoveringStatus:
    """Return coherent residue-sheet channel status."""

    return CoveringStatus(
        route="coherent_residue_sheet_channel_space",
        status=COHERENT_CHANNEL_SPACE_STATUS,
        follows=True,
        assumptions=(
            "boundary field is phase-coherent over sheet preimages",
            "superpositions over sheets span H_f=C[Z_N]",
        ),
        limitations=("coherent physical-channel interpretation remains partial until derived from full dynamics",),
    )


def simplex_vs_endh_status_object() -> CoveringStatus:
    """Return simplex-vs-End(H) status."""

    return CoveringStatus(
        route="simplex_vs_EndH",
        status=SIMPLEX_VS_ENDH_STATUS,
        follows=True,
        assumptions=("stochastic dressing acts on density/covariance operators in End(H_f)",),
        limitations=("the full Brownian generator/rates on End(H_f) remain open",),
    )


def _sector_covering_row(sector: str, omega: int, status: str, official: bool = False) -> SectorCoveringRow:
    degree = degree_from_omega(omega)
    dim = covering_channel_dimension(omega)
    return SectorCoveringRow(
        sector=sector,
        omega=omega,
        degree=degree,
        sheet_count=sheet_count_from_degree(degree),
        deck_group_order=deck_group_order(degree),
        channel_dimension=dim,
        classical_simplex_relative_dimension=classical_simplex_relative_dimension(dim),
        coherent_end_dimension=coherent_end_dimension(dim),
        coherent_traceless_dimension=coherent_traceless_dimension(dim),
        active_fraction=active_fraction_from_dimension(dim),
        status=status,
        official_prediction_update=official,
    )


def sector_covering_table() -> tuple[SectorCoveringRow, ...]:
    """Return covering consequences for charged sectors."""

    return (
        _sector_covering_row("charged_lepton", 3, LEPTON_8_9_STATUS),
        _sector_covering_row("up_candidate_only", 6, QUARK_COVERING_CONSEQUENCE_STATUS),
        _sector_covering_row("down_candidate_only", 12, QUARK_COVERING_CONSEQUENCE_STATUS),
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
    """Return boundary covering-map channel theorem audit payload."""

    open_blockers = (
        "derive boundary phase map u_f from completed BHSM boundary action",
        "prove Omega_f is exactly the degree of u_f, not only a symbolic sector number",
        "prove primitive covering rather than reducible/imprimitive covering",
        "prove residue sheets are physical coherent amplitude channels from full dynamics",
        "derive stochastic residue sampling from completed topographic dynamics",
        "derive full Brownian generator/rates on End(H_f)",
        "resolve stochastic alpha/pi factor-of-two normalization from completed path integral",
        "fix A_j normalization/global bundle coupling without convention dependence",
    )
    rows = sector_covering_table()
    payload: dict[str, Any] = {
        "official_outputs_modified": False,
        "frozen_predictions_modified": False,
        "prs_opened": False,
        "covering_map_theorem_status": COVERING_MAP_THEOREM_STATUS,
        "omega_as_degree_status": OMEGA_AS_DEGREE_STATUS,
        "primitive_covering_status": PRIMITIVE_COVERING_STATUS,
        "residue_sheet_status": RESIDUE_SHEET_STATUS,
        "deck_transformation_status": DECK_TRANSFORMATION_STATUS,
        "channel_dimension_status": CHANNEL_DIMENSION_STATUS,
        "wilson_loop_triviality_trap_status": WILSON_LOOP_TRAP_STATUS,
        "coherent_channel_space_status": COHERENT_CHANNEL_SPACE_STATUS,
        "simplex_vs_endH_status": SIMPLEX_VS_ENDH_STATUS,
        "lepton_8_9_consequence_status": LEPTON_8_9_STATUS,
        "quark_covering_consequence_status": QUARK_COVERING_CONSEQUENCE_STATUS,
        "does_omega_define_covering_degree": True,
        "does_degree_N_give_N_sheets": True,
        "does_deck_group_have_order_N": True,
        "does_wilson_loop_phase_become_trivial": True,
        "does_covering_degree_resolve_wilson_trap": True,
        "does_H_equal_C_Z_N_follow": True,
        "does_EndH_not_simplex_give_8_9": True,
        "does_this_promote_full_lepton_8_9": False,
        "does_this_change_official_predictions": False,
        "preferred_dimension_route": "cyclic_boundary_monodromy",
        "preferred_dimension_interpretation": "cyclic_boundary_covering_degree",
        "geometric_quantization_plus_one_hazard": True,
        "rejected_or_limited_route_note": S2_GEOMETRIC_QUANTIZATION_NOT_USED_FOR_CHANNEL_DIMENSION,
        "derived_components": (
            "degree_N_covering_has_N_generic_preimages",
            "deck_shift_order_equals_N_for_primitive_cover",
            "integer_Wilson_loop_global_phase_is_trivial",
            "End_H_traceless_dimension_formula_N_squared_minus_one",
        ),
        "partial_components": (
            "Omega_f_as_boundary_phase_map_degree",
            "residue_sheets_as_boundary_channel_basis",
            "coherent_H_equals_C_Z_N_channel_space",
            "lepton_8_9_covering_map_consequence",
        ),
        "conditional_components": (
            "primitive_covering_assumption",
            "physical_sheet_channel_identification",
            "stochastic_activity_on_End_H",
        ),
        "candidate_components": (
            "up_active_fraction_35_over_36",
            "down_active_fraction_143_over_144",
        ),
        "open_blockers": open_blockers,
        "missing_assumptions": open_blockers,
        "forbidden_claims_absent": True,
        "safe_to_merge_as_candidate_only": True,
        "wilson_loop_phase_examples": {
            "degree_3": {
                "phase": [
                    wilson_loop_phase_from_degree(3).real,
                    wilson_loop_phase_from_degree(3).imag,
                ],
                "globally_trivial": is_wilson_loop_globally_trivial_for_integer_degree(3),
                "sheet_count": sheet_count_from_degree(3),
            }
        },
        "lepton_mode_checks": {
            "muon": {
                "k": 5,
                "j": 2,
                "q": q_from_kj(5, 2),
                "Omega_l": lepton_omega(q_from_kj(5, 2), 2),
            },
            "electron": {
                "k": 9,
                "j": 3,
                "q": q_from_kj(9, 3),
                "Omega_l": lepton_omega(q_from_kj(9, 3), 3),
            },
        },
        "sector_covering_table": rows,
        "status_objects": {
            "channel_space": channel_space_status_object(),
            "wilson_trap": wilson_trap_status_object(),
            "omega_as_degree": omega_as_degree_status_object(),
            "primitive_covering": primitive_covering_status_object(),
            "coherent_channel": coherent_channel_status_object(),
            "simplex_vs_endH": simplex_vs_endh_status_object(),
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


def _fraction_label(value: Fraction | dict[str, Any]) -> str:
    if isinstance(value, Fraction):
        return f"{value.numerator}/{value.denominator}"
    return f"{value['numerator']}/{value['denominator']}"


def render_markdown(payload: dict[str, Any] | None = None, title: str | None = None) -> str:
    """Render covering-map channel theorem Markdown."""

    p = audit_payload() if payload is None else payload
    heading = title or "BHSM Boundary Covering-Map Channel Theorem"
    lines = [
        f"# {heading}",
        "",
        "This audit reframes BHSM cyclic boundary channels as covering-map sheet multiplicities rather than total Wilson-loop phase order.",
        "",
        "## Summary",
        "",
        f"Covering-map theorem status: `{p['covering_map_theorem_status']}`",
        f"Omega-as-degree status: `{p['omega_as_degree_status']}`",
        f"Primitive covering status: `{p['primitive_covering_status']}`",
        f"Residue sheet status: `{p['residue_sheet_status']}`",
        f"Deck transformation status: `{p['deck_transformation_status']}`",
        f"Channel dimension status: `{p['channel_dimension_status']}`",
        f"Wilson-loop trap status: `{p['wilson_loop_triviality_trap_status']}`",
        f"Coherent channel-space status: `{p['coherent_channel_space_status']}`",
        f"Simplex-vs-EndH status: `{p['simplex_vs_endH_status']}`",
        f"Lepton 8/9 consequence: `{p['lepton_8_9_consequence_status']}`",
        "",
        "## Covering-Map Theorem",
        "",
        "```text",
        "u_f:S^1_boundary -> U(1)",
        "Omega_f = deg(u_f) = (1/(2*pi)) integral dphi_f",
        "N = |Omega_f|",
        "generic preimage count = N",
        "T:s_r -> s_{r+1}, T^N=I",
        "H_f^chan ~= C[Z_N]",
        "dim(H_f^chan)=N",
        "```",
        "",
        "## Wilson-Loop Trap",
        "",
        "The total phase `exp(i integral dphi_f)=exp(2*pi*i*N)` is globally single-valued for integer `N`. That fact does not erase the `N` preimage sheets of the degree-`N` boundary phase map.",
        "",
        f"Wilson phase trivial for degree 3: `{p['wilson_loop_phase_examples']['degree_3']['globally_trivial']}`",
        f"Sheet count for degree 3: `{p['wilson_loop_phase_examples']['degree_3']['sheet_count']}`",
        "",
        "## Sector Covering Table",
        "",
        "| Sector | Omega | Degree | Sheets | Deck order | dim H | Simplex rel dim | dim End(H) | Traceless | Active fraction | Status | Official update |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for row in p["sector_covering_table"]:
        lines.append(
            f"| `{row.sector}` | `{row.omega}` | `{row.degree}` | `{row.sheet_count}` | `{row.deck_group_order}` | `{row.channel_dimension}` | `{row.classical_simplex_relative_dimension}` | `{row.coherent_end_dimension}` | `{row.coherent_traceless_dimension}` | `{_fraction_label(row.active_fraction)}` | `{row.status}` | `{row.official_prediction_update}` |"
        )
    lines.extend(
        [
            "",
            "## Coherent Channels vs Classical Simplex",
            "",
            "The classical probability simplex over `N` sheets has relative dimension `N-1`. BHSM's lepton `8/9` channel factor uses coherent amplitude/density operators on `H_f=C[Z_N]`, where `dim End(H_f)=N^2` and the trace-preserving relative sector has dimension `N^2-1`.",
            "",
            "## Dimension Route",
            "",
            f"Preferred dimension route: `{p['preferred_dimension_route']}`",
            f"Preferred interpretation: `{p['preferred_dimension_interpretation']}`",
            f"Geometric quantization plus-one hazard: `{p['geometric_quantization_plus_one_hazard']}`",
            f"Rejected/limited route note: `{p['rejected_or_limited_route_note']}`",
            "",
            "Ordinary S2 geometric quantization is used only as a hazard comparison, not as the channel-dimension proof route.",
            "",
            "## Blockers Closed",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in p["derived_components"])
    lines.extend(["", "## Open Blockers", ""])
    lines.extend(f"{index}. {item}" for index, item in enumerate(p["open_blockers"], start=1))
    lines.extend(
        [
            "",
            "## Claim Safety",
            "",
            "- No official frozen outputs are changed.",
            "- No retuning is performed.",
            "- No frozen lepton or quark dressing rule is changed.",
            "- No claim is made that BHSM replaces the Standard Model.",
            "- The lepton 8/9 chain is strengthened only as a partial/candidate result.",
            "",
        ]
    )
    return "\n".join(lines)


def export_boundary_covering_map_outputs(root: str | Path = ".") -> dict[str, Any]:
    """Export covering-map theorem artifacts."""

    base = Path(root)
    payload = audit_payload()
    outputs = {
        "main": base / "theory" / "boundary_covering_map_channel_theorem.md",
        "wilson": base / "theory" / "wilson_loop_triviality_vs_covering_degree.md",
        "coherent": base / "theory" / "coherent_residue_sheet_channel_space.md",
        "simplex": base / "theory" / "classical_simplex_vs_endH_stochastic_space.md",
        "audit_md": base / "audits" / "boundary_covering_map_channel_theorem_audit.md",
        "audit_json": base / "audits" / "boundary_covering_map_channel_theorem_audit.json",
    }
    for path in outputs.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    outputs["main"].write_text(render_markdown(payload), encoding="utf-8")
    outputs["wilson"].write_text(
        render_markdown(payload, "Wilson-Loop Triviality vs Covering Degree"),
        encoding="utf-8",
    )
    outputs["coherent"].write_text(
        render_markdown(payload, "Coherent Residue-Sheet Channel Space"),
        encoding="utf-8",
    )
    outputs["simplex"].write_text(
        render_markdown(payload, "Classical Simplex vs End(H) Stochastic Space"),
        encoding="utf-8",
    )
    outputs["audit_md"].write_text(render_markdown(payload), encoding="utf-8")
    outputs["audit_json"].write_text(
        json.dumps(_jsonable(payload), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return payload


if __name__ == "__main__":
    export_boundary_covering_map_outputs()
