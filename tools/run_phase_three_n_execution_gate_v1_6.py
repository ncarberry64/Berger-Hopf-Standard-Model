from __future__ import annotations

import argparse
from pathlib import Path

from phase_three_n_common import ROOT, phase_three_n_results, write_all, write_json


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=str(ROOT / "artifacts"))
    parser.add_argument("--no-execute", action="store_true")
    args = parser.parse_args()
    results = phase_three_n_results(execute=not args.no_execute)
    output_dir = Path(args.output_dir)
    if output_dir == ROOT / "artifacts":
        write_all(results)
    else:
        output_dir.mkdir(parents=True, exist_ok=True)
        mapping = {
            "runtime_provisioning": "BHSM_runtime_provisioning_report_v1_6.json",
            "command_log": "BHSM_live_validation_command_log_v1_6.json",
            "feynrules_validation": "BHSM_feynrules_validation_outcome_v1_6.json",
            "feynrules_enablement": "BHSM_feynrules_enablement_outcome_v1_6.json",
            "ufo_export": "BHSM_ufo_export_outcome_v1_6.json",
            "madgraph_smoke": "BHSM_madgraph_smoke_outcome_v1_6.json",
            "gate_status": "BHSM_phase_three_n_gate_status_v1_6.json",
        }
        for key, name in mapping.items():
            write_json(output_dir / name, results[key])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

