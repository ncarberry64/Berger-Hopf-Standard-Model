from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


PUBLIC_STATUS = "structural architecture integrated conditional; numerical closure open"

ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN_DERIVATION_INPUTS: Tuple[str, ...] = (
    "observed charged-lepton masses",
    "observed quark masses",
    "observed CKM values",
    "observed PMNS values",
    "observed neutrino mass splittings",
    "measured fine-structure alpha",
    "empirical target ratios",
    "post-comparison branch selection",
)


@dataclass(frozen=True)
class BoundaryActionSourceAuditRow:
    claim_id: str
    object: str
    claimed_role: str
    source_files_or_symbols_found: Tuple[str, ...]
    evidence_summary: str
    status: str
    blocking_missing_source: str
    forbidden_upgrade_notes: str


def _found_references(paths: Iterable[str], symbols: Iterable[str]) -> Tuple[str, ...]:
    found: List[str] = []
    for rel_path in paths:
        path = ROOT / rel_path
        if path.exists():
            found.append(rel_path)
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                text = path.read_text(encoding="utf-8", errors="ignore")
            for symbol in symbols:
                if symbol and symbol in text:
                    found.append(f"{rel_path}:{symbol}")
    return tuple(dict.fromkeys(found))


def _row(
    claim_id: str,
    object_name: str,
    claimed_role: str,
    paths: Iterable[str],
    symbols: Iterable[str],
    evidence_summary: str,
    status: str,
    blocking_missing_source: str,
    forbidden_upgrade_notes: str,
) -> BoundaryActionSourceAuditRow:
    return BoundaryActionSourceAuditRow(
        claim_id=claim_id,
        object=object_name,
        claimed_role=claimed_role,
        source_files_or_symbols_found=_found_references(paths, symbols),
        evidence_summary=evidence_summary,
        status=status,
        blocking_missing_source=blocking_missing_source,
        forbidden_upgrade_notes=forbidden_upgrade_notes,
    )


def build_audit_table() -> Tuple[BoundaryActionSourceAuditRow, ...]:
    freeze_paths = (
        "src/charged_kf_generator.py",
        "docs/bhsm_freeze_protocol.md",
        "data/bhsm_full_freeze_protocol_charged_kf_v1.json",
    )
    projector_paths = (
        "src/sector_projector_hessian_fork.py",
        "docs/bhsm_sector_projector_ledger_theorem.md",
        *freeze_paths,
    )
    zvirt_paths = (
        "src/weak_double_projection_zvirt_bridge.py",
        "src/virtual_environment.py",
        "docs/bhsm_weak_double_projection_zvirt_bridge.md",
        "data/bhsm_weak_double_projection_zvirt_bridge.json",
        *freeze_paths,
    )
    hessian_paths = (
        "src/charged_hessian_source_audit.py",
        "docs/bhsm_charged_hessian_source_audit.md",
        "docs/bhsm_charged_hessian_fork_audit.md",
        *freeze_paths,
    )

    rows = [
        _row(
            "D_C_colored_contact_defect",
            "D_C",
            "colored-channel contact defect; rank readout 1+P_C and orientation readout 2P_C-1",
            projector_paths,
            ("P_C", "2 * P_C", "2P_C-1", "1+P_C"),
            "The C projector and readout factors are implemented in the sector/projector scaffold and freeze protocol.",
            "DERIVED_CONDITIONAL_ON_EXISTING_PROJECTOR_SCAFFOLD",
            "An action-level colored contact defect operator D_C is not derived.",
            "Do not upgrade to action-derived from projector algebra alone.",
        ),
        _row(
            "D_d_color_lower_overlap_contact_defect",
            "D_d",
            "color-lower overlap contact defect; rank readout 1+P_d and Hopf/base multiplier 1+P_d",
            projector_paths,
            ("P_d", "1 + P_d", "1+P_d", "down-sector"),
            "The down/lower projector and extra incidence factor are implemented and tested as sector-engine structures.",
            "DERIVED_CONDITIONAL_ON_EXISTING_PROJECTOR_SCAFFOLD",
            "An action-level color-lower overlap contact defect D_d is not derived.",
            "Do not claim the down multiplier is action-derived until D_d is produced by the boundary action.",
        ),
        _row(
            "Gamma_sigma_weak_orientation_grading",
            "Gamma_sigma",
            "weak-orientation grading; Hopf sign -sigma and leptonic target sign -(1-C)sigma",
            projector_paths,
            ("sigma", "-sigma", "orientation_tau", "Gamma_sigma"),
            "The sigma orientation label drives the Omega and target-orientation formulas in the generator.",
            "DERIVED_CONDITIONAL_ON_EXISTING_PROJECTOR_SCAFFOLD",
            "A boundary-action grading operator Gamma_sigma is not derived.",
            "Do not call this a chirality/action theorem without the operator source.",
        ),
        _row(
            "Gamma_T_target_orientation_trace",
            "Gamma_T",
            "target-orientation trace tau(C,sigma)=C-(1-C)sigma and T=tau A",
            freeze_paths,
            ("orientation_tau", "target_T", "Gamma_T", "T(C,sigma)"),
            "The target orientation trace is encoded as a deterministic freeze-protocol formula.",
            "STRONGLY_SUPPORTED_CANDIDATE",
            "The trace operator Gamma_T and its action trace over E_A are not derived.",
            "Do not upgrade from candidate status until Gamma_T is sourced by the action.",
        ),
        _row(
            "E3_universal_rank_three_closure",
            "E_3",
            "universal rank-three closure module; reference slot plus two excitation slots",
            projector_paths,
            ("KAPPA_3", "rank-three", "three-state", "reference slot"),
            "The three-slot ledger structure is repeatedly represented in projector and freeze-protocol scaffolds.",
            "STRONGLY_SUPPORTED_CANDIDATE",
            "The universal rank-three module E_3 is not derived as a boundary-action module.",
            "Do not claim generation closure is fully action-derived from the ledger alone.",
        ),
        _row(
            "EA_incidence_module_factorization",
            "E_A",
            "incidence module E_A=E_3 tensor E_C tensor E_d with rank kappa_3(1+P_C)(1+P_d)",
            freeze_paths,
            ("incidence_A", "E_A", "kappa_3", "1+P_C", "1+P_d"),
            "The incidence product A(C,sigma) is implemented and matches sector targets.",
            "STRONGLY_SUPPORTED_CANDIDATE",
            "The tensor factorization E_A=E_3 tensor E_C tensor E_d is not action-derived.",
            "Do not infer full module factorization from rank arithmetic alone.",
        ),
        _row(
            "Delta_IT_index_trace_defect",
            "Delta_IT",
            "index-trace defect Delta_IT=Omega-Tr(Gamma_T|E_A) with admissibility Delta_IT=0",
            freeze_paths,
            ("delta_IT", "Delta_IT", "Omega - T", "zero-defect"),
            "The zero-defect condition is implemented and tested against non-reference ledger modes.",
            "STRONGLY_SUPPORTED_CANDIDATE",
            "The zero-defect constraint is not derived by varying the boundary action.",
            "Do not claim the boundary graded defect theorem is proven from tests alone.",
        ),
        _row(
            "B_supp_universal_suppression_operator",
            "B_supp",
            "universal charged boundary suppression operator",
            freeze_paths,
            ("B_supp", "charged_suppression", "eta"),
            "Suppression fractions are encoded, but no direct B_supp action operator is found.",
            "OPEN_LOCALIZABLE",
            "The boundary action source for B_supp remains missing.",
            "Do not claim B_supp is action-derived unless a direct source is found.",
        ),
        _row(
            "g_ch_phase_normalized_coupling",
            "g_ch",
            "candidate phase-normalized charged coupling g_ch=alpha_geom/pi=1/21",
            freeze_paths,
            ("g_ch", "1/21", "R_ch"),
            "The value 1/21 is implemented as an incidence-rank candidate, not as measured alpha or an action-normalized phase response.",
            "STRONGLY_SUPPORTED_CANDIDATE",
            "Phase-response normalization and alpha_geom action source remain missing.",
            "Do not use measured fine-structure alpha or residuals to derive g_ch.",
        ),
        _row(
            "R_ch_total_incidence_rank",
            "R_ch",
            "total charged incidence rank R_ch=A_l+A_u+A_d=21 as candidate source of g_ch",
            freeze_paths,
            ("A_l", "A_u", "A_d", "21", "g_ch"),
            "The charged incidence arithmetic 3+6+12=21 is present through A(C,sigma) and g_ch=1/21.",
            "STRONGLY_SUPPORTED_CANDIDATE",
            "The action has not derived that the inverse total incidence rank is the coupling.",
            "Do not promote incidence arithmetic to phase-normalized coupling without action normalization.",
        ),
        _row(
            "Pi_f_incidence_projection_fractions",
            "Pi_f",
            "charged incidence projection fractions Pi_l=1/7, Pi_u=2/7, Pi_d=4/7",
            freeze_paths,
            ("Pi_l", "Pi_u", "Pi_d", "projection_fraction"),
            "Projection fractions are exact in the candidate suppression package.",
            "STRONGLY_SUPPORTED_CANDIDATE",
            "The projection fractions are not yet derived from B_supp or a boundary response functional.",
            "Do not fit Pi_f to charged-sector residuals.",
        ),
        _row(
            "chi_f_incidence_self_screening_counts",
            "chi_f",
            "incidence self-screening counts chi_l=1, chi_u=2, chi_d=4",
            freeze_paths,
            ("CHI", "chi_l", "chi_u", "chi_d", "self_screening"),
            "Self-screening counts are implemented as exact candidate integers in the suppression package.",
            "STRONGLY_SUPPORTED_CANDIDATE",
            "The self-screening counts are not derived from the charged boundary action.",
            "Do not tune chi_f to numerical residuals.",
        ),
        _row(
            "S_f_self_screening_factors",
            "S_f",
            "self-screening factors S_l=20/21, S_u=19/21, S_d=17/21",
            freeze_paths,
            ("S_l", "S_u", "S_d", "self_screening"),
            "S_f follows algebraically inside the candidate package from chi_f and g_ch.",
            "DERIVED_CONDITIONAL_ON_SUPPRESSION_CANDIDATE",
            "The underlying B_supp and g_ch derivations remain missing.",
            "Do not treat conditional algebra as numerical closure.",
        ),
        _row(
            "eta_f_charged_suppression_constants",
            "eta_f",
            "eta_l=20/3087, eta_u=38/3087, eta_d=68/3087",
            freeze_paths,
            ("eta_l", "eta_u", "eta_d", "eta("),
            "Eta constants follow algebraically inside the candidate package from Pi_f, g_ch, and S_f.",
            "DERIVED_CONDITIONAL_ON_SUPPRESSION_CANDIDATE",
            "The underlying B_supp, g_ch, and phase-response normalization remain missing.",
            "Do not call eta_f action-derived or numerically closed.",
        ),
        _row(
            "N_ch_charged_cost_form",
            "N_ch(q,j;rho_ch)",
            "charged cost q^2 + rho_ch j^2",
            hessian_paths,
            ("N_ch", "q^2+rho_ch", "charged_norm_N", "diagonal_charged_hessian"),
            "The charged cost form is implemented in the Hessian fork and freeze generator.",
            "STRONGLY_SUPPORTED_CANDIDATE",
            "The charged action has not selected the exact stiffness rho_ch.",
            "Do not use mass fits to choose the charged stiffness.",
        ),
        _row(
            "rho_ch_branch_candidates",
            "rho_ch branches",
            "rho_ch=1 isotropic, rho_ch=2 weak-involution weighted, rho_ch=3 rank-three closure weighted",
            hessian_paths,
            ("RHO_CH_BRANCHES", "rho_ch=1", "rho_ch=3", "rho_ch"),
            "Branch candidates are documented and emitted by the generator.",
            "STRUCTURAL_CANDIDATES",
            "No charged action/Hessian source chooses among the branches.",
            "Do not select rho_ch from mass near-degeneracy or residuals.",
        ),
        _row(
            "rho_ch_exact_value",
            "rho_ch exact value",
            "exact charged stiffness selection",
            hessian_paths,
            ("rho_ch_exact_value", "rho_ch_action_value", "OPEN_LOCALIZABLE"),
            "The exact value remains explicitly open in charged Hessian audits and freeze protocol.",
            "OPEN_LOCALIZABLE",
            "The charged-sector action/Hessian source that fixes rho_ch remains missing.",
            "Do not promote rho_ch=1,2,3 from candidate to selected by comparison.",
        ),
        _row(
            "down_sector_admissibility_windows",
            "down-sector rho_ch windows",
            "membership 0<rho_ch<8 and old ordering 0<rho_ch<16/5",
            hessian_paths,
            ("0 < rho_ch < 8", "0 < rho_ch < 16/5", "membership_constraint"),
            "The windows follow from preserving the down-sector ledger/order under the charged cost scaffold.",
            "DERIVED_CONDITIONAL_ON_DOWN_LEDGER_SELECTION",
            "The windows do not select an exact rho_ch value.",
            "Do not use the down window or near-degeneracy as a fit criterion.",
        ),
        _row(
            "Kf_tridiagonal_structure",
            "K_f tridiagonal structure",
            "real symmetric 3x3 tridiagonal charged operator template",
            freeze_paths,
            ("minimal_K_f", "tridiagonal", "K_f"),
            "The template is deterministic, real, symmetric, and tridiagonal in the generator.",
            "STRONGLY_SUPPORTED_CANDIDATE",
            "The action source for excluding non-tridiagonal entries is not derived.",
            "Do not treat candidate spectra as charged mass predictions.",
        ),
        _row(
            "beta_f_reference_bridge",
            "beta_f",
            "reference bridge beta_f=g_ch Pi_f",
            freeze_paths,
            ("beta", "beta_f", "g_ch() * projection_fraction"),
            "The bridge is implemented exactly as a minimal candidate ansatz.",
            "STRONGLY_SUPPORTED_CANDIDATE",
            "No action derivation of beta_f=g_ch Pi_f is found.",
            "Do not mark beta_f derived conditional unless the action source is explicit.",
        ),
        _row(
            "kappa_f_tangent_bridge",
            "kappa_f",
            "tangent bridge kappa_f=g_ch/||v_f||_ch^2",
            freeze_paths,
            ("kappa", "tangent_norm_sq", "g_ch() / tangent_norm_sq"),
            "The tangent bridge is implemented exactly as a minimal candidate ansatz.",
            "STRONGLY_SUPPORTED_CANDIDATE",
            "No action derivation of kappa_f=g_ch/||v_f||^2 is found.",
            "Do not mark kappa_f derived conditional unless the action source is explicit.",
        ),
        _row(
            "tangent_generators",
            "v_f tangents",
            "v_l=(2,1), v_u=(2,1), v_d=(4,-1), v_nu=(-2,1)",
            freeze_paths,
            ("EXPECTED_TANGENTS", "tangent_difference", "zero_defect_tangent_adjacency"),
            "Tangents are generated from non-reference zero-defect ledger adjacency.",
            "DERIVED_CONDITIONAL_ON_SECTOR_ENGINE",
            "The sector engine/action derivation of the ledgers remains a dependency.",
            "Do not treat tangent adjacency as an empirical mass fit.",
        ),
        _row(
            "tangent_norms",
            "||v_f||_ch^2",
            "charged tangent norms 4+rho_ch, 4+rho_ch, and 16+rho_ch",
            freeze_paths,
            ("tangent_norm_sq", "4+rho", "16+rho"),
            "Norms follow algebraically from N_ch and the tangent generators.",
            "DERIVED_CONDITIONAL_ON_RHO_CH_BRANCH",
            "Exact norms remain branch-conditional because rho_ch remains open.",
            "Do not choose the branch by post-comparison spectra.",
        ),
        _row(
            "operator_level_threshold_insertion",
            "operator threshold insertion",
            "K_u -> K_u + (ln 2)|1_u><1_u|",
            zvirt_paths,
            ("threshold_insertions", "ln 2", "operator_level", "WEAK_DOUBLE_PROJECTION"),
            "The insertion is localized to the up-sector (6,0) construction-basis slot and uses the PO-BH-68 bridge.",
            "STRONGLY_SUPPORTED_CANDIDATE",
            "A full threshold operator is not derived.",
            "Do not add post-diagonal or additional threshold factors without derivation.",
        ),
        _row(
            "Z_virt_u1",
            "Z_virt up threshold slot",
            "derived conditional Z_virt factor applied to the middle-up operator slot",
            zvirt_paths,
            ("Z_virt_u1", "Z_virt_u2_applicability", "DERIVED_CONDITIONAL"),
            "The weak-double projection bridge derives the local 1/2 factor conditionally for the actual source path.",
            "DERIVED_CONDITIONAL",
            "The full virtual loop/threshold operator source remains open.",
            "Do not use observed charm/top or CKM agreement as a derivation.",
        ),
        _row(
            "mode_identity_branch_tracking",
            "mode identity / spectral branch tracking",
            "construction-basis ledgers become physical branches only after frozen operator diagonalization",
            freeze_paths,
            ("Mode_Identity_Threshold_Readout_Theorem", "branch tracking", "maximal overlap"),
            "The freeze protocol states the continuous branch-tracking rule.",
            "STRONGLY_SUPPORTED_CANDIDATE",
            "The branch-tracking/readout theorem is not proven from the full operator.",
            "Do not relabel branches after comparison.",
        ),
        _row(
            "post_diagonal_multiplicative_dressing_prohibition",
            "post-diagonal dressing prohibition",
            "thresholds must be inserted at operator level unless another theorem exists",
            freeze_paths,
            ("post-diagonal", "operator-level", "No post-diagonal"),
            "The protocol forbids arbitrary multiplicative dressings after diagonalization.",
            "DERIVED_CONDITIONAL_ON_FREEZE_PROTOCOL",
            "A complete theorem for all possible threshold mechanisms remains open.",
            "Do not introduce post-diagonal dressing as a repair knob.",
        ),
        _row(
            "full_threshold_operator",
            "full threshold operator",
            "complete threshold operator beyond the single derived-conditional up insertion",
            zvirt_paths,
            ("full_threshold_operator", "full virtual loop/threshold source", "OPEN"),
            "Docs and data keep the full threshold operator open.",
            "OPEN",
            "The full virtual loop/threshold source is not derived.",
            "Do not claim full threshold closure from a single local insertion.",
        ),
        _row(
            "RG_transport",
            "RG transport",
            "scheme/RG transport after frozen structural readout",
            freeze_paths,
            ("RG_transport", "RG/scheme", "OPEN"),
            "The freeze protocol leaves RG/scheme transport outside this sprint.",
            "OPEN",
            "Precision RG transport is not implemented or derived here.",
            "Do not treat structural operator output as transported comparison data.",
        ),
        _row(
            "numerical_closure",
            "numerical closure",
            "full numerical charged-sector closure",
            freeze_paths,
            ("numerical_closure", "numerical closure", "OPEN"),
            "The global public status and freeze protocol keep numerical closure open.",
            "OPEN",
            "Multiple symbolic/action sources remain open before comparison.",
            "Do not claim charged masses, CKM, PMNS, or Full BHSM are numerically closed.",
        ),
    ]
    return tuple(rows)


def status_by_claim_id() -> Dict[str, str]:
    return {row.claim_id: row.status for row in build_audit_table()}


def audit_as_dict() -> Dict[str, object]:
    rows = build_audit_table()
    return {
        "id": "PO-BH-boundary-action-source-audit-kf-v1",
        "title": "Boundary Action Source Audit for Full Freeze / Charged Kf Generator",
        "public_status": PUBLIC_STATUS,
        "frozen_predictions_changed": False,
        "official_predictions_changed": False,
        "uses_empirical_derivation_inputs": False,
        "forbidden_derivation_inputs": list(FORBIDDEN_DERIVATION_INPUTS),
        "rows": [asdict(row) for row in rows],
        "statuses": status_by_claim_id(),
        "summary": {
            "sector_ledger_architecture": "strong candidate / conditional on existing projector scaffold",
            "Z_virt_u1": "DERIVED_CONDITIONAL",
            "tangent_adjacency": "DERIVED_CONDITIONAL_ON_SECTOR_ENGINE",
            "minimal_charged_Kf_generator": "STRONGLY_SUPPORTED_CANDIDATE",
            "charged_suppression_package": "STRONGLY_SUPPORTED_CANDIDATE",
            "B_supp": "OPEN_LOCALIZABLE",
            "g_ch": "STRONGLY_SUPPORTED_CANDIDATE",
            "beta_f": "STRONGLY_SUPPORTED_CANDIDATE",
            "kappa_f": "STRONGLY_SUPPORTED_CANDIDATE",
            "rho_ch_exact_value": "OPEN_LOCALIZABLE",
            "full_threshold_operator": "OPEN",
            "RG_transport": "OPEN",
            "numerical_closure": "OPEN",
        },
        "claim_boundary": (
            "Action/source support audit only; no new predictions, no frozen output changes, "
            "and no numerical closure."
        ),
    }
