from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from phase_three_l_common import component, guardrails, load_phase_three_l_inputs, which, write_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_software_environment_preflight_v1_4.json"


def manual_component(name: str, detected: bool, required_for: list[str], blocks: bool, notes: str) -> dict[str, object]:
    return {
        "component": name,
        "detected": detected,
        "version": "unknown" if detected else "not_detected",
        "detection_method": "manual/path heuristic",
        "required_for": required_for,
        "blocks_if_missing": blocks,
        "notes": notes,
    }


def build_payload() -> dict[str, object]:
    load_phase_three_l_inputs()
    wolframscript_path = which("wolframscript")
    math_path = which("math") or which("MathKernel") or which("WolframKernel")
    madgraph_path = which("mg5_aMC") or which("mg5")
    return {
        "artifact": "BHSM_software_environment_preflight_v1_4",
        "release_basis": "v1.0.1",
        "phase": "PHASE_THREE_L_FEYNRULES_SYNTAX_RUNNER",
        "entries": [
            {
                "component": "python",
                "detected": True,
                "version": sys.version.split()[0],
                "detection_method": "current Python interpreter",
                "required_for": ["repository exporters", "static checks"],
                "blocks_if_missing": True,
                "notes": "Python is available for repository tooling.",
            },
            component(
                "mathematica_kernel",
                "WolframKernel" if which("WolframKernel") else ("MathKernel" if which("MathKernel") else ("math" if which("math") else None)),
                ["FeynRules syntax validation", "UFO export"],
                True,
                "Required for real FeynRules execution.",
            ),
            component(
                "wolframscript",
                "wolframscript" if wolframscript_path else None,
                ["scripted Mathematica/FeynRules execution"],
                True,
                "Convenient command-line path for local execution.",
            ),
            manual_component(
                "feynrules",
                False,
                ["model loading", "Feynman rule generation", "UFO export"],
                True,
                "FeynRules is a Mathematica package; PATH detection is insufficient, so this remains not detected.",
            ),
            manual_component(
                "feynarts",
                False,
                ["optional diagram/form-factor workflows"],
                False,
                "Optional FeynArts package not detected by repository preflight.",
            ),
            component(
                "madgraph",
                "mg5_aMC" if which("mg5_aMC") else ("mg5" if madgraph_path else None),
                ["MadGraph import", "MadGraph smoke process"],
                True,
                "Required for actual MadGraph smoke tests.",
            ),
            component(
                "hepmc",
                "hepmc3-config" if which("hepmc3-config") else ("hepmc-config" if which("hepmc-config") else None),
                ["HepMC event-output validation"],
                True,
                "Required only after event generation path exists.",
            ),
            component(
                "root_optional",
                "root-config" if which("root-config") else None,
                ["optional analysis and plotting checks"],
                False,
                "ROOT is optional for this runner package.",
            ),
        ],
        **guardrails(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Phase Three-L software environment preflight.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    write_json(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

