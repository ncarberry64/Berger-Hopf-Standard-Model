"""Build portable artifacts and test an installed wheel outside the checkout.

Run with the product's development interpreter, for example:
  python scripts/package_product.py --output /path/to/release --base-python /path/to/python
After final documentation/receipt changes, use --source-only to regenerate the
portable source ZIP without repeating the scientific fits or wheel build.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile


PRODUCT = Path(__file__).resolve().parents[1]
RECEIPT = PRODUCT / "validation" / "package_install_receipt.json"
ARCHIVE_NAME = "Blackhole_Tracker_Product_Source.zip"
EXCLUDED = {".venv", "build", "dist", "__pycache__", ".pytest_cache", "user_runs",
            ".git", ".mypy_cache", ".ruff_cache", ".ipynb_checkpoints", "node_modules"}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def package_hashes():
    return {p.relative_to(PRODUCT).as_posix(): sha256(p)
            for p in sorted((PRODUCT / "bhtracker").rglob("*"))
            if p.is_file() and "__pycache__" not in p.parts}


def portable_files():
    for path in sorted(PRODUCT.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(PRODUCT)
        if any(part.lower() in EXCLUDED or part.lower().endswith(".egg-info")
               for part in relative.parts):
            continue
        if path.is_symlink():
            raise ValueError(f"source archive does not follow symlinks: {relative}")
        yield path, relative


def source_archive(output):
    archive = output / ARCHIVE_NAME
    included = []
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as target:
        for path, relative in portable_files():
            target.write(path, (Path("product") / relative).as_posix())
            included.append(relative.as_posix())
    for required in ["README.md", "pyproject.toml", "Start_Blackhole_Tracker.cmd",
                     "scripts/package_product.py", "validation/package_install_receipt.json"]:
        if required not in included:
            raise ValueError(f"portable source is missing {required}")
    for directory in ["notebooks/", "tests/", "scripts/", "validation/"]:
        if not any(name.startswith(directory) for name in included):
            raise ValueError(f"portable source is missing {directory}")
    return archive, included


def wheel_contents(wheel):
    with zipfile.ZipFile(wheel) as artifact:
        names = set(artifact.namelist())
        required = ["bhtracker/web/index.html", "bhtracker/web/app.js", "bhtracker/web/style.css",
                    "bhtracker/theory/ADAPTATION.json", "bhtracker/theory/provider/SOURCE_MANIFEST.json"]
        for name in required:
            if name not in names:
                raise ValueError(f"wheel is missing {name}")
        manifest = json.loads(artifact.read("bhtracker/theory/provider/SOURCE_MANIFEST.json"))
        if len(manifest["files"]) != 6:
            raise ValueError("expected six pinned provider files")
        checked = {}
        for item in manifest["files"]:
            name = "bhtracker/theory/provider/" + item["path"]
            payload = artifact.read(name)
            actual = hashlib.sha256(payload).hexdigest()
            if actual != item["sha256"]:
                raise ValueError(f"wheel provider hash mismatch: {name}")
            checked[item["path"]] = actual
        return {"file_count": len(names), "provider_files": checked,
                "web_files": {name: hashlib.sha256(artifact.read(name)).hexdigest()
                              for name in required[:3]}}


PROBE = r'''
import hashlib
from importlib import metadata, resources
import json
from pathlib import Path
import sys
import threading
from urllib.request import urlopen

import numpy as np
import scipy
import bhtracker
from bhtracker import fit, load_dataset, predict
from bhtracker.examples import make_example
from bhtracker.server import make_server

prefix = Path(sys.prefix).resolve()
package = Path(bhtracker.__file__).resolve()
if not package.is_relative_to(prefix):
    raise RuntimeError('bhtracker imported outside clean environment: ' + str(package))
direct = metadata.distribution('bhsm-blackhole-tracker').read_text('direct_url.json')
if direct and json.loads(direct).get('dir_info', {}).get('editable'):
    raise RuntimeError('installation is editable')

root = resources.files('bhtracker')
manifest = json.loads(root.joinpath('theory/provider/SOURCE_MANIFEST.json').read_text())
if len(manifest['files']) != 6:
    raise RuntimeError('expected six provider inputs')
provider = {}
for item in manifest['files']:
    actual = hashlib.sha256(root.joinpath('theory/provider/' + item['path']).read_bytes()).hexdigest()
    if actual != item['sha256']:
        raise RuntimeError('installed provider mismatch: ' + item['path'])
    provider[item['path']] = actual
web = {name: hashlib.sha256(root.joinpath('web/' + name).read_bytes()).hexdigest()
       for name in ['index.html', 'app.js', 'style.css']}
raw, truth = make_example('nearby_motion', noise=False)
data = load_dataset(raw)
prediction = predict(data, truth)
error = float(np.max(abs(prediction - data.observations)))
if error > 1e-10:
    raise RuntimeError('public prediction round-trip failed')
results = {}
for family in ['gr', 'r1']:
    result = fit(data, family=family, nuisance='shear', starts=1)
    if result['status'] != 'TRACKED':
        raise RuntimeError(family + ' clean-install fit was not TRACKED')
    if abs(result['estimates']['mass_msun'] / truth['mass_msun'] - 1) > 1e-5:
        raise RuntimeError(family + ' mass recovery failed')
    results[family] = {key: result[key] for key in
                      ['status', 'estimates', 'uncertainty', 'chi2', 'dof', 'model', 'conditional_envelope']}
    Path('api_' + family + '_result.json').write_text(json.dumps(result, indent=2, allow_nan=False), encoding='utf-8')
server = make_server(0)
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
http_checks = {}
try:
    for path in ['/', '/app.js', '/style.css', '/api/health', '/api/examples']:
        with urlopen('http://127.0.0.1:' + str(server.server_port) + path, timeout=10) as response:
            body = response.read()
            if response.status != 200 or not body:
                raise RuntimeError('installed app resource failed: ' + path)
            http_checks[path] = {'status': response.status, 'bytes': len(body)}
finally:
    server.shutdown()
    server.server_close()
    server.executor.shutdown(wait=True, cancel_futures=True)
    thread.join(timeout=10)
receipt = {'passed': True, 'python': sys.version, 'prefix': str(prefix),
           'bhtracker_file': str(package), 'editable': False,
           'dependency_versions': {'numpy': np.__version__, 'scipy': scipy.__version__},
           'public_predict_max_absolute_error': error, 'fits': results,
           'provider_files': provider, 'web_files': web, 'loopback_resource_checks': http_checks}
Path('installed_api_probe.json').write_text(json.dumps(receipt, indent=2, allow_nan=False), encoding='utf-8')
print(json.dumps({'passed': True, 'bhtracker_file': str(package),
                  'gr_status': results['gr']['status'], 'r1_status': results['r1']['status']}))
'''


def run_logged(command, cwd, log, environment):
    result = subprocess.run([str(x) for x in command], cwd=cwd, env=environment,
                            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=900)
    log.write_text(result.stdout + result.stderr, encoding="utf-8")
    if result.returncode:
        raise RuntimeError(f"command failed ({result.returncode}); see {log}")
    return {"command": [str(x) for x in command], "returncode": result.returncode,
            "log": str(log), "log_sha256": sha256(log)}


def release_manifest(output, archive, included, wheel=None):
    files = [archive] + ([wheel] if wheel else [])
    manifest = {"created_utc": datetime.now(timezone.utc).isoformat(),
                "files": {path.name: {"bytes": path.stat().st_size, "sha256": sha256(path)} for path in files},
                "source_archive_root": "product/", "source_file_count": len(included),
                "source_files": included,
                "source_receipt_sha256": sha256(RECEIPT),
                "note": "Archive hash is external to avoid a self-referential included receipt."}
    (output / "release_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--base-python", type=Path,
                        default=Path(sys.base_prefix) / ("python.exe" if os.name == "nt" else "bin/python"))
    parser.add_argument("--source-only", action="store_true")
    args = parser.parse_args(argv)
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    if output == PRODUCT or output.is_relative_to(PRODUCT):
        raise ValueError("release output must be outside the source product folder")
    if args.source_only:
        archive, included = source_archive(output)
        wheels = sorted(output.glob("bhsm_blackhole_tracker-*.whl"), key=lambda path: path.stat().st_mtime)
        manifest = release_manifest(output, archive, included, wheels[-1] if wheels else None)
        print(json.dumps({"source_archive": str(archive), "sha256": manifest["files"][archive.name]["sha256"]}))
        return
    work = Path(tempfile.mkdtemp(prefix="package_install_", dir=output))
    environment = dict(os.environ)
    environment.pop("PYTHONPATH", None)
    environment.pop("PYTHONHOME", None)
    environment["PYTHONUTF8"] = "1"
    steps = []
    receipt = {"status": "RUNNING", "created_utc": datetime.now(timezone.utc).isoformat(),
               "dependency_scope": "Fresh noneditable venv; runtime dependencies installed from the configured package index, no system-site-packages.",
               "outside_checkout_working_directory": str(work), "commands": steps}
    try:
        print("Building wheel with the invoking development interpreter...", flush=True)
        steps.append(run_logged([sys.executable, "-m", "build", "--wheel", "--outdir", output],
                                PRODUCT, work / "build.log", environment))
        wheels = sorted(output.glob("bhsm_blackhole_tracker-*.whl"), key=lambda path: path.stat().st_mtime)
        if not wheels:
            raise ValueError("build produced no wheel")
        wheel = wheels[-1]
        receipt["wheel"] = {"filename": wheel.name, "sha256": sha256(wheel),
                            "bytes": wheel.stat().st_size, "contents": wheel_contents(wheel)}
        clean = work / "clean_venv"
        print("Creating a clean environment and installing the wheel...", flush=True)
        steps.append(run_logged([args.base_python.resolve(), "-m", "venv", clean],
                                work, work / "venv.log", environment))
        python = clean / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        steps.append(run_logged([python, "-m", "pip", "install", "--force-reinstall", wheel],
                                work, work / "install.log", environment))
        (work / "probe_install.py").write_text(PROBE, encoding="utf-8")
        print("Checking public prediction, GR/R1 fits, provider hashes and installed app resources...", flush=True)
        steps.append(run_logged([python, "-I", work / "probe_install.py"], work,
                                work / "api_probe.log", environment))
        receipt["installed_api"] = json.loads((work / "installed_api_probe.json").read_text(encoding="utf-8"))
        cli = clean / ("Scripts/blackhole-tracker.exe" if os.name == "nt" else "bin/blackhole-tracker")
        dataset = work / "cli_nearby.json"
        print("Checking installed command-line example, validation and fit/export...", flush=True)
        for label, arguments in [
            ("example", ["example", "nearby_motion", "--output", dataset]),
            ("validate", ["validate", dataset]),
            ("fit", ["fit", dataset, "--family", "gr", "--starts", "1", "--output", work / "cli_fit"]),
        ]:
            steps.append(run_logged([cli, *arguments], work, work / ("cli_" + label + ".log"), environment))
        cli_result = json.loads((work / "cli_fit/result.json").read_text(encoding="utf-8"))
        if cli_result["status"] != "TRACKED":
            raise ValueError("installed CLI fit did not return TRACKED")
        for name in ["result.json", "report.html", "predictions.csv", "track_and_residuals.png", "manifest.json"]:
            if not (work / "cli_fit" / name).is_file():
                raise ValueError("CLI export is missing " + name)
        receipt["cli"] = {"status": cli_result["status"], "mass_msun": cli_result["estimates"]["mass_msun"],
                          "exports": {path.name: sha256(path) for path in sorted((work / "cli_fit").iterdir()) if path.is_file()}}
        receipt["package_source_sha256"] = package_hashes()
        receipt["status"] = "CLEAN_WHEEL_INSTALL_PASSED"
        receipt["source_archive"] = {"filename": ARCHIVE_NAME,
                                     "hash_location": "external release_manifest.json; regenerate with --source-only after final edits"}
    except Exception as error:
        receipt["status"] = "FAILED"
        receipt["error"] = str(error)
        RECEIPT.parent.mkdir(exist_ok=True)
        RECEIPT.write_text(json.dumps(receipt, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        raise
    RECEIPT.parent.mkdir(exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    archive, included = source_archive(output)
    manifest = release_manifest(output, archive, included, wheel)
    print(json.dumps({"status": receipt["status"], "output": str(output), "files": manifest["files"]}, indent=2))


if __name__ == "__main__":
    main()
