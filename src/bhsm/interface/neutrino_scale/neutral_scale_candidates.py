"""Candidate classification for the missing BHSM neutral energy scale."""

from __future__ import annotations

import json
from pathlib import Path

from .common import NeutralScaleCandidate, repository_path


BOUNDARY_PACKAGE = "artifacts/BHSM_boundary_no_fit_prediction_package_v1.json"


def build_neutral_scale_candidates(
    repository: str | Path | None = None,
) -> tuple[NeutralScaleCandidate, ...]:
    root = repository_path(repository)
    payload = json.loads((root / BOUNDARY_PACKAGE).read_text(encoding="utf-8"))
    profile = payload["profile_scale"]

    def dimensionless(key: str, value: float, source: str = BOUNDARY_PACKAGE) -> NeutralScaleCandidate:
        return NeutralScaleCandidate(
            candidate_key=key,
            value=float(value),
            unit=None,
            dimension="dimensionless",
            source=source,
            status="DIMENSIONLESS_ARTIFACT",
            can_map_to_eV=False,
            requires_external_calibration=True,
            forbidden_reason=None,
            neutral_kernel_link="internal normalization only; no physical unit map",
            claim_boundary=f"{key} cannot alone map a dimensionless neutral response to eV/GeV.",
        )

    rows = [
        dimensionless("tau", profile["tau"]),
        dimensionless("sigma", profile["sigma"]),
        dimensionless("kappa_H", profile["kappa_H"]),
        dimensionless("mu_H", profile["kappa_H"], "artifacts/canonical_profile_hessian_theorem_v1.json"),
        dimensionless("universal_overlap_width_S", profile["r_squared"]),
        dimensionless("berger_anisotropy", 1.157054135733433, "src/bhsm/interface/constants.py"),
        NeutralScaleCandidate(
            candidate_key="boundary_measure_dmu",
            value="dmu_boundary dt",
            unit=None,
            dimension="unspecified",
            source="artifacts/BHSM_author_ontology_v0_8.json",
            status="AUTHOR_ONTOLOGY_CONDITIONAL",
            can_map_to_eV=False,
            requires_external_calibration=True,
            forbidden_reason=None,
            neutral_kernel_link="symbolic neutral action measure",
            claim_boundary="A named measure is not a dimensionful normalization.",
        ),
        NeutralScaleCandidate(
            candidate_key="w_mass_calibration",
            value=None,
            unit="GeV",
            dimension="energy",
            source="artifacts/BHSM_prediction_report_example_v0_1.json",
            status="EMPIRICAL_FORBIDDEN",
            can_map_to_eV=False,
            requires_external_calibration=True,
            forbidden_reason="W calibration is forbidden as a neutral-scale theorem input.",
            neutral_kernel_link="none",
            claim_boundary="The W mass is comparison/calibration data, not a neutral theorem input.",
        ),
        NeutralScaleCandidate(
            candidate_key="electron_neutrino_upper_limit",
            value=None,
            unit="eV",
            dimension="energy",
            source="reference layer only",
            status="EMPIRICAL_FORBIDDEN",
            can_map_to_eV=False,
            requires_external_calibration=True,
            forbidden_reason="An upper limit cannot set the BHSM neutral scale.",
            neutral_kernel_link="none",
            claim_boundary="The electron-neutrino upper limit is comparison-only.",
        ),
        NeutralScaleCandidate(
            candidate_key="background_energy_density",
            value=None,
            unit=None,
            dimension="missing",
            source="not found in local neutral artifacts",
            status="MISSING",
            can_map_to_eV=False,
            requires_external_calibration=False,
            forbidden_reason=None,
            neutral_kernel_link="required by a curvature-response energy map",
            claim_boundary="No artifact-backed neutral background stiffness or energy density was found.",
        ),
        NeutralScaleCandidate(
            candidate_key="legacy_curvature_mass_functional",
            value="m = (c^2/(2G)) r_prop^2 k_neutral,eff",
            unit=None,
            dimension="mass if r_prop is in m and k_neutral,eff is in m^-2",
            source="theory/legacy_sources/v1_1/mass_from_local_curvature_thresholds_scalar_topographic_eft.pdf",
            status="ARTIFACT_BACKED_CURVATURE_MASS_FUNCTIONAL",
            can_map_to_eV=False,
            requires_external_calibration=False,
            forbidden_reason=None,
            neutral_kernel_link="conditional bridge; r_prop and physical curvature map remain missing",
            claim_boundary="The functional supplies dimensional structure but not the missing neutral radius or physical curvature value.",
        ),
    ]
    return tuple(rows)
