from __future__ import annotations
import hashlib
import json
from pathlib import Path

REPO = Path(r'C:\Users\carbe\Downloads\BHSM_muon_parent_maxwell_worktree_20261001')
WORK = Path(__file__).resolve().parent
SOURCES = {
    'ae4_selected_owner': ('src/bhsm/interface/ae4_stratified_dirac_zeta_induced_owner.py', [[178, 192], [272, 302], [305, 344]]),
    'ae4_future_domain_and_recovered_chain': ('src/bhsm/interface/ae4_future_collapse_relative_boundary_domain.py', [[93, 186]]),
    'ae2_regular_birth': ('src/bhsm/interface/action_extension_global_spin_reset_ae2.py', [[51, 137], [156, 194]]),
    'full_d5_weak_seam': ('src/bhsm/interface/muon_holomorphic_d5_trace_action.py', [[272, 337], [419, 517]]),
    'full_d5_normalized_source_trace': ('src/bhsm/interface/muon_full_d5_localized_lepton_trace.py', [[156, 237]]),
    'local_isotropic_graph': ('src/bhsm/interface/muon_isotropic_seam_transfer.py', [[1, 150]]),
    'master_compatibility': ('src/bhsm/interface/master_action/reduction.py', [[148, 225], [230, 281], [334, 392]]),
    'retained_attachment_incidence': ('src/bhsm/interface/completion/global_attachment_incidence_curvature_v14_68.py', [[1, 47], [265, 380]]),
    'retained_wentzell_theorem_class': ('src/bhsm/interface/completion/operator_valued_calderon_wentzell_v14_66.py', [[1, 48], [297, 369]]),
    'retained_dynamic_child': ('src/bhsm/interface/aether_n3_dynamic_child_wentzell_cauchy_v17_90.py', [[1, 230]]),
    'actual_fp_regular_graph': ('src/bhsm/interface/muon_regular_reset_brst_domain.py', [[1, 151]]),
    'intrinsic_chiral_domain': ('src/bhsm/interface/ae31_c2_chiral_green_domain.py', [[25, 86], [118, 169]]),
    'encapsulation_variation_class': ('src/bhsm/interface/owner_authorized_encapsulation_interface_action.py', [[71, 142], [341, 415]]),
    'ae4_current_event_assembly': ('src/bhsm/interface/ae4_c2_stratified_event_flux_assembly.py', [[1, 10], [66, 103], [115, 215], [246, 278]]),
    'native_d5_covector_component': ('src/bhsm/interface/muon_real_positive_d5_covector_binding.py', [[1, 80]]),
    'foundational_spatial_hard_collar_and_SH': ('src/bhsm/interface/completion/foundational_dirac_spin_glue_v14_45.py', [[92, 142], [248, 287]]),
}

def pin(path: Path) -> dict:
    b = path.read_bytes()
    return dict(path=str(path), bytes=len(b), sha256=hashlib.sha256(b).hexdigest(),
                crlf_count=b.count(b'\r\n'), lf_count=b.count(b'\n'))

rows = {}
for label, (relative, spans) in SOURCES.items():
    p = REPO / relative
    lines = p.read_text(encoding='utf-8').splitlines()
    if any(first < 1 or first > len(lines) or last < first or last > len(lines) for first, last in spans):
        raise ValueError(f'invalid source anchor: {relative}')
    rows[label] = dict(pin(p), repository_relative_path=relative,
                       line_anchors=spans, actual_line_count=len(lines))

proof = WORK / 'muon_global_stratified_domain_from_green_variation_20261016.txt'
payload = dict(
    classification='BHSM_GLOBAL_STRATIFIED_DOMAIN_GREEN_VARIATION_DERIVATION',
    date='2026-10-16', repository=str(REPO), proof=pin(proof),
    pin_generator=pin(Path(__file__).resolve()), sources=rows,
    mathematical_references=[
        {'title': 'Baer and Ballmann, Guide to Elliptic Boundary Value Problems for Dirac-Type Operators',
         'url': 'https://arxiv.org/pdf/1307.3021', 'version': 'v2, 2024-10-01',
         'scope': 'Green traces, graph closure, additional elliptic boundary/core hypotheses'},
        {'title': 'Arendt and ter Elst, Sectorial forms and degenerate differential operators',
         'url': 'https://www.uni-ulm.de/fileadmin/website_uni_ulm/mawi.inst.020/arendt/downloads/pubbib/short/2012-AreTerEls-SctFrmDgnDffOpr.pdf',
         'section': '4.5', 'scope': 'conditional Wentzell form/Hilbert embedding closure'}],
    numerical_campaigns_executed=0, original_coupled_corrections_applied=0,
    conditional_global_closed_factor_construction=True,
    complete_AE4_native_factor_domain_identified=False,
    physical_outgoing_derivative_passed=False,
    Maxwell_and_all_226_after_correction_passed=False,
    two_spin_states_normalized=False, muon_magnetic_moment_computed=False,
)
out = WORK / 'muon_global_stratified_domain_from_green_variation_20261016_source_pins.json'
out.write_bytes((json.dumps(payload, sort_keys=True, indent=2) + '\n').encode('utf-8'))
print(json.dumps({'proof': pin(proof), 'pins': pin(out), 'source_count': len(rows)}, sort_keys=True))
