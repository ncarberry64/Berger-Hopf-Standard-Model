"""Build the standalone author-review manuscript without altering sources."""
from pathlib import Path
import subprocess
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    if shutil.which("latexmk") is None:
        raise SystemExit("latexmk is required; install a standard TeX distribution.")
    result = subprocess.run(
        ["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error", "main.tex"],
        cwd=ROOT / "manuscript", text=True, capture_output=True,
    )
    logdir = ROOT / "artifacts/build"
    logdir.mkdir(parents=True, exist_ok=True)
    (logdir / "latexmk.log").write_text(result.stdout + result.stderr)
    if result.returncode:
        print((result.stdout + result.stderr)[-7000:])
        return result.returncode
    log = (ROOT / "manuscript/main.log").read_text(errors="replace")
    problems = [x for x in log.splitlines() if
                "Overfull" in x or "LaTeX Warning" in x or "undefined" in x]
    print("Built manuscript/main.pdf")
    for line in problems:
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
