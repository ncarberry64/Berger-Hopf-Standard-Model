"""Fail-closed audit for the BHSM museum presentation boundary."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MUSEUM_URL = "https://ncarberry64.github.io/Berger-Hopf-Standard-Model/"
ASSETS = ROOT / "docs" / "assets"
SIMULATION_BASES = (
    "bhsm_geometry_to_prediction",
    "bhsm_simulated_particle_spectrum",
    "bhsm_spectral_forecast",
    "bhsm_muon_g2_pipeline",
    "bhsm_collision_predictor",
    "bhsm_decay_stability_engine",
    "bhsm_no_fit_firewall",
    "bhsm_physical_identification_bridge",
)
OTHER_WORK_BASE = "cosmology_hyperspherical_scalar_topography"
CMS_REQUIRED = (
    "coordinate-engine validation",
    "detector reconstruction",
    "BHSM empirical validation",
    "CERN/CMS endorsement",
    "https://opendata.cern.ch/record/303",
    "pr98_cms_sample_manifest.json",
    "artifacts/cern_open_data_benchmark/results.json",
    "tests/test_cern_open_data_benchmark.py",
    "100,000",
    "200,000",
)
GENERATED_PATH = re.compile(
    r"(^|/)(node_modules|dist|\.next|__pycache__|coverage|\.cache)(/|$)|\.pyc$"
)


def _text(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def audit() -> dict:
    status = json.loads(_text("docs/current_bhsm_status.json"))
    exhibits = _text("museum/app/exhibits.ts")
    page = _text("museum/app/page.tsx")
    layout = _text("museum/app/layout.tsx")
    combined = " ".join((exhibits + "\n" + page).split())

    cms_checks = {
        phrase: phrase.casefold() in combined.casefold() for phrase in CMS_REQUIRED
    }
    exhibit_checks = {
        "ten_animated_visuals": exhibits.count("animated: '") == 10,
        "ten_static_visuals": exhibits.count("still: '") == 10,
        "lay_copy_for_every_exhibit": exhibits.count("lay: '") == 10,
        "lay_placard_rendered": "<dt>Lay description</dt>" in page,
        "real_data_engine_label": "Real-data engine" in page,
        "simulation_engine_label": "Simulation / audit engine" in page,
        "motion_fallback": "onError={() => setFailedSource(desired)}" in page,
        "cosmology_other_work_boundary": all(
            phrase.casefold() in combined.casefold()
            for phrase in (
                "not peer reviewed",
                "not observational data",
                "full likelihood analysis",
                "10.20944/preprints202601.1427.v1",
            )
        ),
    }
    asset_checks = {
        f"{base}{suffix}": (ASSETS / f"{base}{suffix}").is_file()
        for base in SIMULATION_BASES
        for suffix in (".svg", ".png", "_animated.gif")
    }
    asset_checks.update(
        {
            f"{OTHER_WORK_BASE}{suffix}": (
                ASSETS / f"{OTHER_WORK_BASE}{suffix}"
            ).is_file()
            for suffix in (".svg", ".png", "_animated.gif")
        }
    )
    asset_checks.update(
        {
            "cms_png": (
                ASSETS
                / "pr98_cms_open_data_animation"
                / "pr98_cms_engine_validation.png"
            ).is_file(),
            "cms_gif": (
                ASSETS
                / "pr98_cms_open_data_animation"
                / "pr98_cms_engine_validation_continuous.gif"
            ).is_file(),
            "simulation_generator": (
                ASSETS / "generate_bhsm_museum_engines.py"
            ).is_file(),
            "cosmology_generator": (
                ASSETS / "generate_cosmology_other_work_exhibit.py"
            ).is_file(),
        }
    )

    tracked = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    ).stdout.splitlines()
    generated_tracked = [path for path in tracked if GENERATED_PATH.search(path)]

    checks = {
        "current_science_remains_open": status.get("FULL_BHSM_COMPLETE") is False,
        "current_science_version_present": bool(status.get("current_version")),
        "museum_exhibits_are_visual_and_lay_accessible": all(
            exhibit_checks.values()
        ),
        "museum_assets_resolve": all(asset_checks.values()),
        "cms_boundary_complete": all(cms_checks.values()),
        "canonical_museum_url": MUSEUM_URL in _text("README.md")
        and MUSEUM_URL in layout,
        "no_tracked_generated_output": not generated_tracked,
        "no_full_completion_promotion": not re.search(
            r"FULL_BHSM_COMPLETE\s*[=:]\s*TRUE", page, re.IGNORECASE
        ),
        "no_cms_physics_promotion": "CMS Open Data validates BHSM physics"
        not in combined,
    }
    return {
        "audit": "bhsm_public_surfaces",
        "passed": all(checks.values()),
        "checks": checks,
        "cms_checks": cms_checks,
        "exhibit_checks": exhibit_checks,
        "asset_checks": asset_checks,
        "generated_tracked": generated_tracked,
    }


if __name__ == "__main__":
    result = audit()
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["passed"] else 1)
