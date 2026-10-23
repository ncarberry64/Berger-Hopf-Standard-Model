"""Render the paper's scientific figures and tables from executed receipts."""
from pathlib import Path
import json
import os
import tempfile

os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "bhsm_angular_mpl"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "manuscript" / "figures"
OUT.mkdir(parents=True, exist_ok=True)
TABLES = ROOT / "manuscript" / "tables"
TABLES.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10,
    "axes.labelsize": 11, "axes.titlesize": 12,
    "axes.spines.top": False, "axes.spines.right": False,
    "figure.facecolor": "white", "savefig.facecolor": "white",
    "pdf.fonttype": 42, "ps.fonttype": 42,
})
COLORS = ["#18648A", "#24A39A", "#DA8733", "#8B4A87"]


def save(fig, stem):
    fig.savefig(OUT / (stem + ".pdf"), bbox_inches="tight")
    fig.savefig(OUT / (stem + ".png"), dpi=200, bbox_inches="tight")
    plt.close(fig)


def sci(x, digits=4):
    m, e = f"{x:.{digits-1}e}".split("e")
    return rf"${m}\times10^{{{int(e)}}}$"


def main():
    lens = json.loads((ROOT / "artifacts/lensing/nodal_sis_prediction.json").read_text())
    shared = json.loads((ROOT / "artifacts/lensing/shared_state_relations.json").read_text())
    optical = json.loads((ROOT / "artifacts/temporal/angular_response.json").read_text())
    configs = lens["configurations"]

    angle = np.linspace(0, 180, 721)
    fig, ax = plt.subplots(figsize=(7.1, 4.05), layout="constrained")
    ax.axhline(0, color="#7A8690", linewidth=.8)
    for x in (45, 135):
        ax.axvline(x, color="#AEB8C0", linestyle=":", linewidth=1)
    for item, color in zip(configs, COLORS):
        amp = item["illustrative_angular_response"][0]["linear_delta_delay_seconds"]
        ax.plot(angle, amp * np.cos(2 * np.deg2rad(angle)), color=color, linewidth=2,
                label=rf"$z_l={item['z_l']:g},\ z_s={item['z_s']:g}$")
    ax.set(xlim=(0, 180), xticks=np.arange(0, 181, 30),
           xlabel=r"Physical source azimuth $\varphi$ (degrees)",
           ylabel=r"First-order relative-delay shift $\delta\Delta t$ (s)")
    ax.legend(ncol=2, loc="lower center", bbox_to_anchor=(.5, 1.02),
              frameon=False, fontsize=9)
    ax.grid(axis="y", color="#E5E9EC", linewidth=.65)
    ax.set_axisbelow(True)
    save(fig, "nodal_delay_angular_response")

    scan = shared["redshift_scan"]
    z = np.array([x["z_s"] for x in scan])
    b = np.array([x["density_seed_B11_over_p"] for x in scan])
    ref = b[np.argmin(abs(z - 1.0))]
    fig, ax = plt.subplots(figsize=(7.1, 3.75), layout="constrained")
    ax.plot(z, b * 1e7, color=COLORS[0], linewidth=2.1,
            label="Computed distributed preparation")
    ax.axhline(ref * 1e7, color=COLORS[2], linestyle="--", linewidth=1.7,
               label=r"One physical lens-plane quadratic term, matched at $z_s=1$")
    for target in (.6, 1.):
        idx = np.argmin(abs(z - target))
        ax.plot(z[idx], b[idx] * 1e7, "o", color=COLORS[0], markersize=5)
    ax.set(xlim=(.4, 2.), xlabel=r"Source redshift $z_s$ at fixed $z_l=0.3$",
           ylabel=r"Reduced coefficient $10^7 B_{11,s}/p_s$")
    ax.set_title("A restricted cross-redshift consistency comparison", pad=12)
    ax.grid(color="#E5E9EC", linewidth=.65)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, fontsize=8.5, loc="lower left")
    save(fig, "shared_state_redshift_contrast")

    rows = [r"\begin{tabular}{lrrrr}", r"\toprule",
            r"Anchor & $g_{ol,j}$ & $g_{os,j}$ & $g_{ls,j}$ & $k_j=\sqrt2(g_{os,j}-g_{ol,j})$\\",
            r"\midrule"]
    names = [r"$\zeta$", r"$\Pi_{2,\mathrm{ref}}$", r"$\delta_m^{\rm ADM}$",
             r"$\delta_r^{\rm ADM}$", r"$v_m^{\rm ADM}$", r"$v_r^{\rm ADM}$"]
    item = optical["configurations"][0]
    for j, name in enumerate(names):
        values = [item["segments"][s]["g_per_physical_anchor"][j] for s in ("ol", "os", "ls")]
        values.append(configs[0]["fractional_delay_kernel"][j])
        rows.append(name + " & " + " & ".join(sci(v) for v in values) + r"\\")
    rows += [r"\bottomrule", r"\end{tabular}"]
    (TABLES / "response_coefficients.tex").write_text("\n".join(rows) + "\n")

    rows = [r"\begin{tabular}{rrrrrr}", r"\toprule",
            r"$z_l$ & $z_s$ & $\Delta t_0$ (days) & $\delta\Delta t(0^\circ)$ (s) & $\delta\Delta t(45^\circ)$ (s) & $\delta\Delta t(90^\circ)$ (s)\\",
            r"\midrule"]
    for item in configs:
        dt = item["illustrative_angular_response"][0]["linear_delta_delay_seconds"]
        rows.append(f"{item['z_l']:g} & {item['z_s']:g} & {item['baseline_delay_days']:.6f} & {dt:.6f} & 0 & {-dt:.6f}" + r"\\")
    rows += [r"\bottomrule", r"\end{tabular}"]
    (TABLES / "delay_predictions.tex").write_text("\n".join(rows) + "\n")
    print(json.dumps({"figures": 2, "formats": ["pdf", "png"], "tables": 2}))


if __name__ == "__main__":
    main()
