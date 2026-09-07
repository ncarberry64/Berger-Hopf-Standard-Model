"""Build deterministic figure and numeric TeX inputs from the Museum evidence."""
import hashlib
import json
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from export_n12_gate7_scalar_response_for_museum import build_payload

OUT = Path(__file__).resolve().parent / "generated"
OUT.mkdir(exist_ok=True)
data = build_payload()
stored = json.loads((ROOT / "data/museum/bhsm_gate7_scalar_response.json").read_text())
if data != stored:
    raise RuntimeError("Manuscript evidence differs from the frozen Museum dataset")
values = {
    "ScalarIntervals": data["interval_count"],
    "ScalarNodes": data["node_count"],
    "ScalarMaximum": data["maximum_response_upper"],
    "ScalarOwner": data["maximum_response_node"],
    "ScalarLocalMaximum": max(data["local_residual_norm_upper"]),
}
(OUT / "scalar_values.tex").write_text("".join(
    f"\\newcommand{{\\{key}}}{{{value}}}\n" for key, value in values.items()
), encoding="utf-8")
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                     "pdf.fonttype": 42, "axes.spines.top": False,
                     "axes.spines.right": False})
fig, ax = plt.subplots(figsize=(6.35, 3.1), layout="constrained")
ax.plot(np.arange(data["node_count"]), data["response_norm_upper"], color="#126681", lw=1.6)
ax.set(xlabel="Computational node", ylabel="Response norm upper bound", xlim=(0, 370))
ax.grid(axis="y", alpha=.2)
fig.savefig(OUT / "scalar_response.pdf", metadata={"CreationDate": None, "ModDate": None})
plt.close(fig)
print(json.dumps({"nodes": data["node_count"], "maximum": data["maximum_response_upper"],
                  "figure_sha256": hashlib.sha256((OUT / "scalar_response.pdf").read_bytes()).hexdigest()}))
