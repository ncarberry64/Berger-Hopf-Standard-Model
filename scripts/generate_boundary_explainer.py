"""Generate the data-driven near-pole coordinate explainer GIF."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="docs/assets/bhsm_boundary_mapping_explainer.gif")
    parser.add_argument("--frames", type=int, default=28)
    args = parser.parse_args()

    rng = np.random.default_rng(1729)
    count = 600
    base_phi = rng.uniform(-np.pi, np.pi, count)
    theta = rng.uniform(0.2e-8, 1.0e-8, count)
    colors = theta * 1.0e8

    fig, (angle_ax, direct_ax) = plt.subplots(1, 2, figsize=(9.6, 4.2))
    fig.patch.set_facecolor("#f7f9fa")
    fig.suptitle("Same near-pole states, two coordinate views", fontsize=15, fontweight="bold")

    def draw(frame: int) -> None:
        phase = 2.0 * np.pi * frame / args.frames
        raw_phi = base_phi + phase
        wrapped_phi = (raw_phi + np.pi) % (2.0 * np.pi) - np.pi
        ux = np.sin(theta) * np.cos(raw_phi)
        uy = np.sin(theta) * np.sin(raw_phi)

        angle_ax.clear()
        direct_ax.clear()
        angle_ax.scatter(wrapped_phi, theta * 1.0e8, c=colors, s=9, cmap="viridis", alpha=0.75)
        angle_ax.axvline(-np.pi, color="#c74242", linewidth=1.2, linestyle="--")
        angle_ax.axvline(np.pi, color="#c74242", linewidth=1.2, linestyle="--")
        angle_ax.set_xlim(-np.pi, np.pi)
        angle_ax.set_ylim(0.0, 1.15)
        angle_ax.set_xlabel("wrapped azimuth phi")
        angle_ax.set_ylabel("polar distance (1e-8 rad)")
        angle_ax.set_title("Angle chart: seam at +/- pi")
        angle_ax.grid(alpha=0.2)

        direct_ax.scatter(ux * 1.0e8, uy * 1.0e8, c=colors, s=9, cmap="viridis", alpha=0.75)
        direct_ax.set_xlim(-1.15, 1.15)
        direct_ax.set_ylim(-1.15, 1.15)
        direct_ax.set_aspect("equal", adjustable="box")
        direct_ax.set_xlabel("u_x (1e-8)")
        direct_ax.set_ylabel("u_y (1e-8)")
        direct_ax.set_title("Direct unit-vector map: continuous")
        direct_ax.grid(alpha=0.2)
        fig.text(
            0.5,
            0.02,
            "Coordinate singularity visualization only - not detector tracking or physics validation.",
            ha="center",
            fontsize=9,
        )
        fig.tight_layout(rect=(0, 0.07, 1, 0.91))

    movie = animation.FuncAnimation(fig, draw, frames=args.frames, interval=90)
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    movie.save(destination, writer=animation.PillowWriter(fps=11), dpi=110)
    plt.close(fig)
    print(destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
