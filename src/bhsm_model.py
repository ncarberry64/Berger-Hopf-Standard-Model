"""Executable Berger-Hopf Standard Model reinterpretation object.

The model assembled here is a working low-energy reinterpretation ledger. It
uses the repository's existing audited modules and keeps proxy/open statuses
visible rather than upgrading them to completed proofs.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from anomalies import anomalies_cancel, anomaly_residuals
from berger_spectrum import berger_lambda
from bhsm_config import GeometryConfig, canonical_geometry_config
from boundary_derivation import DerivationStatus, default_boundaries
from constants import V_HIGGS_EMPIRICAL_GEV
from flavor_matrix import canonical_flavor_report
from gauge_couplings import coupling_screens, gauge_coupling_screen
from higgs_scale import higgs_scale_screen
from ht_operator import default_level2_config, level2_ht_gap_report
from hypercharge import derive_hypercharges
from lagrangian import full_symbolic_lagrangian
from mode_selection import HEAVY_MODE, EXPECTED_LEDGER, hopf_charge, mode_ledger
from pmns import pmns_effective_screen
from rg_matching import matching_report
from scalar_decoupling import build_scalar_proxy_spectrum, hopf_gap_mass, scalar_decoupling_report
from spectral_gap import natural_lambda2
from twisted_dirac import DIRAC_PROXY_LEVEL_2
from yukawa_overlap import hierarchy_screen, mass_ratio


@dataclass(frozen=True)
class GaugeGroup:
    """Gauge group ledger entry."""

    factors: tuple[str, ...]
    display: str


@dataclass(frozen=True)
class FieldRepresentation:
    """Gauge representation for a low-energy field."""

    su3: str
    su2: str
    hypercharge: Fraction


@dataclass(frozen=True)
class FermionField:
    """Fermion field entry in physical SM notation."""

    name: str
    chirality: str
    representation: FieldRepresentation
    generations: int


@dataclass(frozen=True)
class HiggsField:
    """Higgs doublet with internal topographic profile."""

    name: str
    representation: FieldRepresentation
    profile: str
    expression: str


@dataclass(frozen=True)
class GenerationMode:
    """Charged-sector internal mode assignment."""

    sector: str
    generation_rank: str
    k: int
    j: int
    q: int
    action: float


@dataclass(frozen=True)
class YukawaSector:
    """Yukawa overlap ledger for one charged sector."""

    sector: str
    modes: tuple[GenerationMode, ...]
    ratios: Mapping[str, float]
    status: str


@dataclass(frozen=True)
class BHSMModel:
    """Executable aggregate of the reinterpreted low-energy SM ledger."""

    gauge_group: GaugeGroup
    fermion_fields: tuple[FermionField, ...]
    higgs: HiggsField
    generation_modes: Mapping[str, tuple[GenerationMode, ...]]
    yukawa_sectors: Mapping[str, YukawaSector]
    include_effective_neutrino_sector: bool
    lagrangian_blocks: Mapping[str, str]
    boundary_derivation_status: Mapping[str, str]
    geometry_config: GeometryConfig
    model_level: str
    theorem_complete: bool


def _fraction_to_json(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}" if value.denominator != 1 else str(value.numerator)


def _jsonable(value: Any) -> Any:
    if isinstance(value, Fraction):
        return _fraction_to_json(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if hasattr(value, "__dataclass_fields__"):
        return _jsonable(asdict(value))
    return value


def standard_model_field_ledger() -> tuple[FermionField, ...]:
    """Return the physical SM fermion field ledger from derived hypercharges."""

    charges = derive_hypercharges()
    return (
        FermionField("Q_L", "left", FieldRepresentation("3", "2", charges["Q"]), 3),
        FermionField("u_R", "right", FieldRepresentation("3", "1", -charges["u_c"]), 3),
        FermionField("d_R", "right", FieldRepresentation("3", "1", -charges["d_c"]), 3),
        FermionField("L_L", "left", FieldRepresentation("1", "2", charges["L"]), 3),
        FermionField("e_R", "right", FieldRepresentation("1", "1", -charges["e_c"]), 3),
    )


def _make_generation_mode(sector: str, rank: str, pair: tuple[int, int], a: float) -> GenerationMode:
    k, j = pair
    return GenerationMode(
        sector=sector,
        generation_rank=rank,
        k=k,
        j=j,
        q=hopf_charge(k, j),
        action=berger_lambda(k, j, a=a),
    )


def generation_mode_ledger(geometry_config: GeometryConfig | None = None) -> dict[str, tuple[GenerationMode, ...]]:
    """Return the three-generation internal charged-sector mode ledger."""

    config = canonical_geometry_config() if geometry_config is None else geometry_config
    selected = mode_ledger(k_max=12)
    sector_map = {
        "lepton": "charged_leptons",
        "up": "up_quarks",
        "down": "down_quarks",
    }
    ranks = ("middle", "light")
    ledger: dict[str, tuple[GenerationMode, ...]] = {}
    for short_sector, model_sector in sector_map.items():
        nonzero = tuple(selected[short_sector]["selected"])
        ledger[model_sector] = (
            _make_generation_mode(model_sector, "heavy", HEAVY_MODE, config.a),
            *(
                _make_generation_mode(model_sector, rank, pair, config.a)
                for rank, pair in zip(ranks, nonzero, strict=True)
            ),
        )
    return ledger


def _build_yukawa_sectors(
    generation_modes: Mapping[str, tuple[GenerationMode, ...]],
    geometry_config: GeometryConfig,
) -> dict[str, YukawaSector]:
    sectors: dict[str, YukawaSector] = {}
    for sector, modes in generation_modes.items():
        ratios = {
            mode.generation_rank: mass_ratio(mode.k, mode.j, a=geometry_config.a)
            for mode in modes
        }
        sectors[sector] = YukawaSector(
            sector=sector,
            modes=modes,
            ratios=ratios,
            status="screened_overlap_ratios",
        )
    return sectors


def build_bhsm_model(geometry_config: GeometryConfig | None = None) -> BHSMModel:
    """Construct the working Berger-Hopf Standard Model reinterpretation."""

    config = canonical_geometry_config() if geometry_config is None else geometry_config
    gauge_group = GaugeGroup(
        factors=("SU(3)_c", "SU(2)_L", "U(1)_Y"),
        display="SU(3)_c x SU(2)_L x U(1)_Y",
    )
    higgs = HiggsField(
        name="H",
        representation=FieldRepresentation("1", "2", derive_hypercharges()["H"]),
        profile="Phi(y)",
        expression="H(x,y)=H(x)Phi(y)",
    )
    modes = generation_mode_ledger(config)
    boundaries = default_boundaries()
    return BHSMModel(
        gauge_group=gauge_group,
        fermion_fields=standard_model_field_ledger(),
        higgs=higgs,
        generation_modes=modes,
        yukawa_sectors=_build_yukawa_sectors(modes, config),
        include_effective_neutrino_sector=True,
        lagrangian_blocks=full_symbolic_lagrangian(include_neutrino_extension=True),
        boundary_derivation_status={
            sector: boundary.derivation_status.value for sector, boundary in boundaries.items()
        },
        geometry_config=config,
        model_level="BHSM_WORKING_LOW_ENERGY_REINTERPRETATION",
        theorem_complete=False,
    )


def compute_yukawa_ratios(model: BHSMModel) -> dict[str, dict[str, float]]:
    """Compute charged-sector overlap ratios from the mode ledger."""

    hierarchy_screen()
    return {
        sector: dict(yukawa.ratios)
        for sector, yukawa in model.yukawa_sectors.items()
    }


def compute_ckm_from_internal_rules(model: BHSMModel) -> dict[str, object]:
    """Return CKM output from supplied BHSM internal mass-ratio rules."""

    return canonical_flavor_report(model)


def compute_pmns_from_internal_rules(model: BHSMModel) -> dict[str, object]:
    """Return PMNS output for the effective neutrino extension."""

    return pmns_effective_screen()


def compute_geometric_couplings(model: BHSMModel) -> dict[str, object]:
    """Return supplied geometric coupling screens and RG matching scaffold."""

    screen = gauge_coupling_screen()
    return {
        "values": coupling_screens(),
        "screen_status": screen.status,
        "relative_error": dict(screen.relative_error),
        "rg_matching": matching_report(),
    }


def compute_higgs_sector(model: BHSMModel) -> dict[str, object]:
    """Return Higgs/electroweak-scale outputs."""

    screen = higgs_scale_screen()
    return {
        "higgs_expression": model.higgs.expression,
        "outputs": dict(screen.outputs),
        "empirical": dict(screen.empirical),
        "relative_error": dict(screen.relative_error),
        "status": screen.status,
    }


def compute_ht_gap_status(model: BHSMModel) -> dict[str, object]:
    """Return current Level 2 H_T proxy gap status."""

    report = level2_ht_gap_report(default_level2_config(), natural_lambda2())
    return {
        **report,
        "status": "PROXY_AUDIT",
        "lambda2": natural_lambda2(),
        "theorem_complete": False,
    }


def compute_scalar_decoupling_status(model: BHSMModel) -> dict[str, object]:
    """Return current scalar/topographic decoupling scaffold status."""

    higgs_outputs = compute_higgs_sector(model)["outputs"]
    gap = hopf_gap_mass(float(higgs_outputs["v_gev"]))
    modes = build_scalar_proxy_spectrum(6, gap_scale=gap)
    report = scalar_decoupling_report(modes, gap)
    return {
        **report,
        "status": "FINITE_BASIS_SCAFFOLD",
        "theorem_complete": False,
    }


def model_summary(model: BHSMModel) -> dict[str, object]:
    """Return a complete executable summary for model cards."""

    charges = derive_hypercharges()
    return {
        "model_level": model.model_level,
        "theorem_complete": model.theorem_complete,
        "geometry_config": model.geometry_config,
        "gauge_group": model.gauge_group.display,
        "field_ledger": model.fermion_fields,
        "higgs": model.higgs,
        "left_weyl_hypercharges": charges,
        "physical_hypercharges": {
            field.name: field.representation.hypercharge for field in model.fermion_fields
        },
        "anomaly_residuals": anomaly_residuals(charges),
        "anomalies_cancel": anomalies_cancel(charges),
        "generation_mode_ledger": model.generation_modes,
        "expected_mode_ledger": EXPECTED_LEDGER,
        "boundary_derivation_status": model.boundary_derivation_status,
        "yukawa_ratios": compute_yukawa_ratios(model),
        "ckm": compute_ckm_from_internal_rules(model),
        "pmns": compute_pmns_from_internal_rules(model),
        "couplings": compute_geometric_couplings(model),
        "higgs_sector": compute_higgs_sector(model),
        "ht_gap": compute_ht_gap_status(model),
        "scalar_decoupling": compute_scalar_decoupling_status(model),
        "lagrangian_blocks": model.lagrangian_blocks,
        "open_action_level_derivations": (
            "derive Omega_f from the full twisted Dirac/bundle action",
            "compute the full analytic twisted Dirac H_T spectrum",
            "prove assumptions A1-A7 in the full internal action",
            "complete two-/three-loop threshold RG matching",
            "prove scalar/topographic decoupling from the full action",
        ),
    }


def export_model_card_json(model: BHSMModel, path: str | Path) -> None:
    """Export the working model card as JSON."""

    data = _jsonable(model_summary(model))
    Path(path).write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def export_model_card_markdown(model: BHSMModel, path: str | Path) -> None:
    """Export the working model card as Markdown."""

    summary = model_summary(model)
    couplings = summary["couplings"]["values"]
    higgs = summary["higgs_sector"]["outputs"]
    ht = summary["ht_gap"]
    scalar = summary["scalar_decoupling"]
    lines = [
        "# Berger-Hopf Standard Model Working Model Card",
        "",
        "This card assembles the current executable low-energy reinterpretation. It is not a completed first-principles proof.",
        "",
        f"Model level: `{model.model_level}`",
        f"Theorem complete: `{model.theorem_complete}`",
        f"Geometry config: `{model.geometry_config.name}` (`a={model.geometry_config.a}`, status `{model.geometry_config.status}`)",
        f"Geometry source: {model.geometry_config.source}",
        "Geometry notes:",
        *[f"- {note}" for note in model.geometry_config.notes],
        "",
        "## Gauge Group",
        "",
        model.gauge_group.display,
        "",
        "## Field and Representation Ledger",
        "",
        "| Field | Chirality | SU(3) | SU(2) | Y | Generations |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for field in model.fermion_fields:
        rep = field.representation
        lines.append(
            f"| `{field.name}` | {field.chirality} | `{rep.su3}` | `{rep.su2}` | `{_fraction_to_json(rep.hypercharge)}` | {field.generations} |"
        )
    lines.extend(
        [
            f"| `{model.higgs.name}` | scalar | `{model.higgs.representation.su3}` | `{model.higgs.representation.su2}` | `{_fraction_to_json(model.higgs.representation.hypercharge)}` | profile `{model.higgs.profile}` |",
            "",
            "## Hypercharge and Anomalies",
            "",
            f"Anomalies cancel: `{summary['anomalies_cancel']}`",
            "",
            "## Generation and Mode Ledger",
            "",
            "| Sector | Rank | Mode (k,j) | Hopf q | Action |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for sector, modes in model.generation_modes.items():
        for mode in modes:
            lines.append(
                f"| {sector} | {mode.generation_rank} | `({mode.k},{mode.j})` | {mode.q} | {mode.action} |"
            )
    lines.extend(
        [
            "",
            "## Yukawa Hierarchy Outputs",
            "",
            "```json",
            json.dumps(_jsonable(summary["yukawa_ratios"]), indent=2, sort_keys=True),
            "```",
            "",
            "## CKM and PMNS Outputs",
            "",
            f"CKM status: `{summary['ckm']['status']}`, CP phase: `{summary['ckm']['cp_phase_status']}`",
            f"PMNS status: `{summary['pmns']['status']}`, alpha: `{summary['pmns']['alpha']}`",
            "",
            "## Coupling Outputs",
            "",
            f"alpha_1 = `{couplings['alpha_1']}`",
            f"alpha_2 = `{couplings['alpha_2']}`",
            f"alpha_3 = `{couplings['alpha_3']}`",
            "",
            "## Higgs/Electroweak Outputs",
            "",
            f"v_gev = `{higgs['v_gev']}`",
            f"m_lift_gev = `{higgs['m_lift_gev']}`",
            "",
            "## H_T Proxy Gap Output",
            "",
            f"Status: `{ht['status']}`",
            f"Model level: `{ht['model_level']}`",
            f"First complement eigenvalue: `{ht['first_complement_eigenvalue']}`",
            f"First H_T complement gap: `{ht['first_ht_complement_gap']}`",
            f"Passes proxy target: `{ht['passes']}`",
            "",
            "## Scalar Decoupling Output",
            "",
            f"Status: `{scalar['status']}`",
            f"Passes scaffold: `{scalar['passes']}`",
            f"Light Higgs projections: `{scalar['light_higgs_projection_count']}`",
            "",
            "## Symbolic Lagrangian Blocks",
            "",
            "```text",
            json.dumps(_jsonable(summary["lagrangian_blocks"]), indent=2, sort_keys=True),
            "```",
            "",
            "## Remaining Open Action-Level Derivations",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in summary["open_action_level_derivations"])
    lines.append("")
    Path(path).write_text("\n".join(lines))
