import json
from pathlib import Path

from bhsm.interface.sector_boundary_operator import INVALIDATIONS, OPEN_GATES, build_artifact_payloads

ROOT = Path(__file__).resolve().parents[1]
MARKER = "<!-- BHSM_SECTOR_BOUNDARY_OPERATOR_V4_6 -->"
DOCTRINE = "BHSM v4.6 treats the sector boundary kinetic operator L_i(ρ) as a conditional Laplace-type candidate on active adjoint-valued boundary one-form fluctuations over the relative Berger boundary Σ_ρ. The operator is used only to define a whitened boundary fluctuation B_i=L_i(ρ)^{1/2}A_i and a candidate inverse-covariance quadratic action S_i=(1/2λ_i)<A_i,L_i(ρ)A_i>. The three boundary coframe channels are evaluated through the normalized primitive frame state τ_frame=1/3, so the raw one-form factor of three does not overcount the active residue. The v4.5 residue λ_i=w_i/(6π²) remains a conditional whitened fluctuation covariance density, not yet a derived physical gauge coupling. The action source for L_i(ρ), the gauge-fixed boundary domain, lower-order curvature/collar terms, Z_i(μ,ρ), ρ_i(μ), α_i identification, g2_BH, CKM value/exponent, and full BHSM completion remain open."

ARTIFACT_NAMES = {
    "sector_boundary_operator": "BHSM_sector_boundary_operator_v4_6.json",
    "whitened_gauge_action": "BHSM_whitened_gauge_action_v4_6.json",
    "boundary_operator_principal_symbol": "BHSM_boundary_operator_principal_symbol_v4_6.json",
    "frame_normalized_principal_residue": "BHSM_frame_normalized_principal_residue_v4_6.json",
    "gauge_fixed_domain_gate": "BHSM_gauge_fixed_domain_gate_v4_6.json",
    "lower_order_operator_terms_gate": "BHSM_lower_order_operator_terms_gate_v4_6.json",
    "open_gates": "BHSM_v4_6_open_gates.json",
}

DOCS = {
    "bhsm_sector_boundary_operator_v4_6.md": ("Sector Boundary Operator v4.6", "The conditional operator family is the adjoint-valued one-form Hodge-de Rham Laplacian Delta_1^ad=d_i^dagger d_i+d_i d_i^dagger, or d_i^dagger d_i on a controlled coexact/transverse domain. Its codifferential uses the Berger boundary metric and Hodge star."),
    "bhsm_whitened_gauge_action_v4_6.md": ("Whitened Gauge Action v4.6", "The candidate quadratic identity is S_i=[1/(2 lambda_i)]<A_i,L_i(rho)A_i>=[1/(2 lambda_i)]<B_i,B_i>, with B_i=L_i(rho)^(1/2)A_i and lambda_i=[w_i/(6pi^2)]Z_i."),
    "bhsm_boundary_operator_gauge_domain_v4_6.md": ("Boundary Operator Gauge Domain v4.6", "A_i is defined modulo exact/gauge directions. A gauge-fixed, transverse/coexact, quotient, or otherwise admissible boundary fluctuation domain is required and remains open."),
    "bhsm_operator_lower_order_terms_v4_6.md": ("Boundary Operator Lower-Order Terms v4.6", "The Laplace-type principal symbol leaves Berger/Ricci curvature, adjoint connection curvature, shape/collar, extrinsic-curvature, sector/projector, and scalar/topographic response terms open."),
    "bhsm_v4_6_status_and_open_gates.md": ("BHSM v4.6 Status and Open Gates", "The operator class, principal symbol, frame-normalized residue, and whitened quadratic form are conditional. Their action source, physical running, coupling identification, CKM consequences, and full completion remain open."),
}


def upsert_tail_block(path, block):
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
        content = f"# {title}\n\nStatus: conditional candidate; physical action attachment remains open.\n\n## Doctrine\n\n{DOCTRINE}\n\n## Candidate\n\n{body}\n\n## Invalidations\n\n{invalidations}\n\n## Open gates\n\n{gates}\n"
        (ROOT / "docs" / filename).write_text(content, encoding="utf-8")
    artifacts = "\n".join(f"- `artifacts/{filename}`" for filename in ARTIFACT_NAMES.values())
    block = MARKER + "\n## Sector boundary operator / whitened gauge action v4.6\n\n" + DOCTRINE + "\n\nStatuses: `SECTOR_BOUNDARY_OPERATOR_CONDITIONAL_CANDIDATE`, `LAPLACE_TYPE_PRINCIPAL_SYMBOL_CONDITIONAL`, `FRAME_NORMALIZED_PRINCIPAL_RESIDUE_CONDITIONAL`, and `WHITENED_GAUGE_ACTION_CONDITIONAL`.\n\n### Artifacts\n\n" + artifacts + "\n\n### Invalidations\n\n" + invalidations + "\n\n### Open gates\n\n" + gates
    for name in ("STATUS.md", "CLAIMS.md", "ROADMAP.md", "ARTIFACT_INDEX.md"):
        upsert_tail_block(ROOT / name, block)
    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    old = "The v4.5 audit retains the artifact-backed `alpha_i=w_i/(6*pi^2)` registry pattern and classifies `w=(1,2,7)` as a strong Casimir-shell residue candidate, never gauge-boson counts; spectral density, whitening, inverse-covariance placement, action attachment, coupling values, CKM coefficient value, and CKM exponent remain conditional or open."
    new = "The stacked v4.6 audit extends the v4.5 Casimir-shell residue candidate with a conditional Laplace-type sector boundary operator, principal symbol, frame-normalized residue, and whitened quadratic action; gauge domain, lower-order terms, running, action attachment, coupling values, CKM coefficient/exponent, and full completion remain open."
    if old in text:
        readme.write_text(text.replace(old, new), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
