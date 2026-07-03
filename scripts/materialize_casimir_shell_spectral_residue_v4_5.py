import json
from pathlib import Path

from bhsm.interface.gauge_coupling_spectral_residue import INVALIDATIONS, OPEN_GATES, build_artifact_payloads

ROOT = Path(__file__).resolve().parents[1]
MARKER = "<!-- BHSM_CASIMIR_SHELL_SPECTRAL_RESIDUE_V4_5 -->"
DOCTRINE = "BHSM should not interpret w=(1,2,7) as gauge-boson counts. Gauge algebra dimensions remain (1,3,8). The candidate interpretation is that w=(1,2,7) are active Casimir-shell spectral residues: U(1) retains its sole abelian amplitude channel, while SU(2) and SU(3) separate one radial quadratic Casimir coordinate into the relative-boundary scale layer, leaving tangent residues 2 and 7. The universal factor 1/(6π²) is a candidate 3D boundary Weyl-density coefficient. The resulting λ_i=w_i/(6π²) is a candidate whitened boundary fluctuation covariance density. The action must still derive inverse-covariance placement and coupling identification before α_i is claimed as derived."

ARTIFACT_NAMES = {
    "casimir_shell_residue": "BHSM_casimir_shell_residue_v4_5.json",
    "spectral_density_gauge_quantum": "BHSM_spectral_density_gauge_quantum_v4_5.json",
    "whitened_boundary_operator": "BHSM_whitened_boundary_operator_v4_5.json",
    "inverse_covariance_placement": "BHSM_inverse_covariance_placement_v4_5.json",
    "open_gates": "BHSM_open_gates_v4_5.json",
}

DOCS = {
    "bhsm_casimir_shell_spectral_residue_v4_5.md": ("Casimir-Shell Spectral Residue v4.5", "The candidate radial/angular split gives U(1): 1, SU(2): 3-1=2, and SU(3): 8-1=7. These are active tangent-shell residues, not gauge-boson counts. Direct classical Yang-Mills density sees the radial norm and does not derive this split."),
    "bhsm_whitened_boundary_fluctuation_v4_5.md": ("Whitened Boundary Fluctuation v4.5", "Use B_i=L_i(rho)^(1/2)A_i and S_i=[1/(2 lambda_i)]<B_i,B_i>. Weyl density belongs to whitened active modes; identifying it with raw Green covariance of A_i is invalid."),
    "bhsm_inverse_covariance_placement_v4_5.md": ("Inverse-Covariance Placement v4.5", "The candidate placement is K_i proportional to 1/lambda_i and alpha_i proportional to lambda_i. Both placement and physical coupling identification remain action-gated."),
    "bhsm_relative_boundary_spectral_running_v4_5.md": ("Relative-Boundary Spectral Running v4.5", "At Z_i(mu0,rho0)=1, lambda_i is conditionally w_i/(6pi^2). Physical running requires Z_i(mu,rho), lower spectral and collar corrections, and an action-selected rho_i(mu)."),
}


def append_once(path, block):
    text = path.read_text(encoding="utf-8")
    marker_index = text.find(MARKER)
    if marker_index >= 0:
        text = text[:marker_index].rstrip()
    path.write_text(text + "\n\n" + block + "\n", encoding="utf-8")


def main():
    payloads = build_artifact_payloads()
    for key, filename in ARTIFACT_NAMES.items():
        (ROOT / "artifacts" / filename).write_text(json.dumps(payloads[key], indent=2, sort_keys=True) + "\n", encoding="utf-8")
    invalidations = "\n".join(f"{index}. {item}" for index, item in enumerate(INVALIDATIONS, 1))
    gates = "\n".join(f"- `{gate}`" for gate in OPEN_GATES)
    for filename, (title, body) in DOCS.items():
        text = f"# {title}\n\nStatus: conditional candidate; action attachment remains open.\n\n## Doctrine\n\n{DOCTRINE}\n\n## Candidate\n\n{body}\n\nThe primitive frame trace candidate tau_frame=1/3 gives (1/3)*3=1, but does not close `OPEN_MISSING_FRAME_AVERAGE_NORMALIZATION`.\n\n## Invalidations\n\n{invalidations}\n\n## Open gates\n\n{gates}\n"
        (ROOT / "docs" / filename).write_text(text, encoding="utf-8")
    artifact_lines = "\n".join(f"- `artifacts/{filename}`" for filename in ARTIFACT_NAMES.values())
    block = MARKER + "\n## Casimir-shell spectral residue v4.5\n\n" + DOCTRINE + "\n\nStatuses: `CASIMIR_SHELL_RESIDUE_STRONG_CANDIDATE`, `SPECTRAL_DENSITY_GAUGE_QUANTUM_CONDITIONAL`, `WHITENED_BOUNDARY_FLUCTUATION_CONDITIONAL`, and `INVERSE_COVARIANCE_PLACEMENT_CONDITIONAL`. All action and downstream gates remain open.\n\n### Artifacts\n\n" + artifact_lines + "\n\n### Invalidations\n\n" + invalidations + "\n\n### Open gates\n\n" + gates
    for name in ("STATUS.md", "CLAIMS.md", "ROADMAP.md", "ARTIFACT_INDEX.md"):
        append_once(ROOT / name, block)
    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    old = "The v3.1 audit finds the `alpha_i=w_i/(6*pi^2)` registry pattern artifact-backed and the `1:2:7` sector-weight source conditional, but the volume denominator, universal quantum, action attachment, coupling values, CKM coefficient value, and CKM exponent remain open."
    new = "The v4.5 audit retains the artifact-backed `alpha_i=w_i/(6*pi^2)` registry pattern and classifies `w=(1,2,7)` as a strong Casimir-shell residue candidate, never gauge-boson counts; spectral density, whitening, inverse-covariance placement, action attachment, coupling values, CKM coefficient value, and CKM exponent remain conditional or open."
    if old in text:
        readme.write_text(text.replace(old, new), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
