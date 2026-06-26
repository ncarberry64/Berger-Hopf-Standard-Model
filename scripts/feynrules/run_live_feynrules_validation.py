from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUN_DIR = ROOT / "runs" / "feynrules_validation"
LOG = RUN_DIR / "live_feynrules_validation.log"
CHECK_SCRIPT = ROOT / "scripts" / "feynrules" / "check_bhsm_minimal_model.m"
DISABLED = ROOT / "models" / "feynrules" / "BHSM_Minimal_Collider_Interface.fr.disabled"
CANDIDATE = RUN_DIR / "BHSM_Minimal_Collider_Interface.candidate.unvalidated.fr"


def main() -> int:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(DISABLED, CANDIDATE)
    wolframscript = shutil.which("wolframscript")
    if wolframscript is None:
        LOG.write_text("wolframscript not found; live validation not run.\n", encoding="utf-8")
        return 2
    result = subprocess.run(
        [wolframscript, "-file", str(CHECK_SCRIPT)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    LOG.write_text(
        "COMMAND: " + " ".join([wolframscript, "-file", str(CHECK_SCRIPT)]) + "\n\n"
        + "STDOUT:\n"
        + result.stdout
        + "\nSTDERR:\n"
        + result.stderr,
        encoding="utf-8",
    )
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())

