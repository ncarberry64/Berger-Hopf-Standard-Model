"""Materialize a provenance audit, not a physical solve or observational fit.

Run: python scripts/audit_global_action_x2_selection_v1.py
Repeat generation must be byte-identical while the audited inputs are fixed.
The searches are local; existing research and scientific input files are read only.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
R1 = Path(r'C:\Users\carbe\Manuscript-Generation')
HANDOFF = Path(r'C:\Users\carbe\Downloads\BHSM_GLOBAL_ACTION_X2_SELECTION_HANDOFF.json')
STEM = 'BHSM_GLOBAL_ACTION_X2_SELECTION_V1'
BHSM_INPUTS = [
    'AGENTS.md', 'STATUS.md',
    'docs/BHSM_COSMOLOGICAL_PARENT_DYNAMIC_ENVELOPMENT_V14_54.md',
    'docs/BHSM_GLOBAL_ENVELOPMENT_CAP_SELECTION_V14_60.md',
    'docs/BHSM_INTRINSIC_FULL_PREIMAGE_DYNAMICAL_MOMENTUM_GATE_V14_90.md',
    'docs/BHSM_DEGREE_ONE_LORENTZIAN_FULL_PREIMAGE_PHASE_SPACE_V14_91.md',
    'docs/BHSM_NONLINEAR_ENCAPSULATED_STATE_SPECTRAL_BAND_GATE_V14_93.md',
    'docs/BHSM_NORMAN_BHSM_FULL_RECALL_HINDSIGHT_V16_22.md',
    'artifacts/BHSM_CURRENT_FULL_FIELD_ACTION_ATTACHMENT_AUDIT.json',
    'artifacts/action_extension/BHSM_ACTION_AE2_GLOBAL_SPIN_RESET_ACTION.json',
    'artifacts/action_extension/BHSM_AE4_EXISTING_ASSET_SYSTEM_INTEGRATION.json',
    'artifacts/action_extension/BHSM_AE4_CURRENT_C2_PHYSICAL_ENCLOSURE_STATE_INTEGRATION.json',
    'artifacts/action_extension/BHSM_AE4_C2_STRATIFIED_EVENT_FLUX_ASSEMBLY.json',
    'artifacts/action_extension/BHSM_AE4_CURRENT_C2_CANONICAL_STOP_DOMAIN_BRIDGE.json',
    'artifacts/current_semantics/BHSM_CURRENT_MATHEMATICAL_BASIS.json',
    'artifacts/mission_state/BHSM_COSMOLOGY_MISSION_STATE_V1.json',
    'src/bhsm/interface/universal_brst_quotient.py',
    'src/bhsm/interface/retained_n12_action_expansion_adapter.py',
    'theory/ae4_c2_stratified_event_flux_assembly.md',
    'museum/ASSET_PROVENANCE.md', 'docs/museum/norman_cosmic_enclosure_cycle.md',
]
R1_INPUTS = [
    'preregistration/prediction_manifest.json',
    'manuscript/main.pdf', 'manuscript/sections/04_scalar_metric_bridge.tex',
    'manuscript/sections/04aa_bhsm_native_n2_transport.tex',
    'docs/bhsm_native_cosmology_bridge.md',
    'docs/r1_effective_representation_gate.json',
    'docs/R1_COSMOLOGY_MANUSCRIPT_CLOSURE_V15.md',
    'code/closed_horndeski_n2.py', 'code/action_native_matter_n2.py',
]
FIRST_MISSING = 'ACTION_OWNED_NORMALIZED_COSMOLOGICAL_N2_PROJECTOR_AND_MODE_ON_THE_CURRENT_PHYSICAL_COMMON_DOMAIN'
STATUSES = dict(
    BHSM_GLOBAL_BRANCH='NOT_DERIVED',
    ELL2_PHYSICAL_PROJECTOR='PARTIAL',
    CANONICAL_NORMALIZATION_BRIDGE='MISSING',
    NONZERO_CAP_RELATIVE_MOMENTUM='NOT_EVALUATED',
    ORBIT_PHASE_LOCK='UNDECIDABLE',
    X2_ACTION_SELECTED='NO', X2_VALUE=None, RETUNING=False,
)


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], text=True).strip()


def evidence(root, name, needles):
    path = root/name
    lines = path.read_text(encoding='utf8').splitlines()
    matches = []
    for needle in needles:
        found = [(i+1, line.strip()) for i, line in enumerate(lines) if needle.lower() in line.lower()]
        if not found:
            raise AssertionError(f'Evidence changed: {name}: {needle}')
        matches.extend(dict(line=i, text=t) for i, t in found[:3])
    return dict(root=str(root), path=name, sha256=sha(path), excerpts=matches)


def materialize():
    before = {str(root/p): sha(root/p) for root, paths in [(ROOT, BHSM_INPUTS), (R1, R1_INPUTS)] for p in paths}
    excerpts = [
        evidence(ROOT, BHSM_INPUTS[2], ['does_not_select', 'not yet been solved as one system']),
        evidence(ROOT, BHSM_INPUTS[3], ['synthetic theorem-witness values']),
        evidence(ROOT, BHSM_INPUTS[4], ['DeltaPi=0', 'homogeneous round and Jensen']),
        evidence(ROOT, BHSM_INPUTS[5], ['Gauge-reduced physical projector: undefined']),
        evidence(ROOT, BHSM_INPUTS[7], ['Horndeski/Galileon', 'independently solved']),
        evidence(ROOT, 'theory/ae4_c2_stratified_event_flux_assembly.md',
                 ['H_eff^R =', 'not physical', 'event flux, or']),
        evidence(ROOT, 'src/bhsm/interface/universal_brst_quotient.py', ['supplied', 'tangent_constraints:']),
        evidence(R1, 'manuscript/sections/04aa_bhsm_native_n2_transport.tex',
                 ['If $P_2$', 'Let $e_2', 'declared operator domain', 'a^3\\mathcal G_2 D_tq_2']),
        evidence(R1, 'docs/bhsm_native_cosmology_bridge.md', ['still-open numerical transfer']),
        evidence(R1, 'code/action_native_matter_n2.py', ['This selects two columns', 'a**3*(M@xd+L@x)']),
    ]
    integration = json.loads((ROOT/'artifacts/action_extension/BHSM_AE4_EXISTING_ASSET_SYSTEM_INTEGRATION.json').read_text(encoding='utf8'))
    flux = json.loads((ROOT/'artifacts/action_extension/BHSM_AE4_C2_STRATIFIED_EVENT_FLUX_ASSEMBLY.json').read_text(encoding='utf8'))
    frontier = integration['authoritative_frontier_reconciliation']
    assert frontier['local_enclosure_and_state_transport_already_closed']
    assert frontier['six_sector_assembly_already_derived']
    assert not flux['claim_boundary']['AE4_CURRENT_C2_PHYSICAL_EVENT_FLUX_NUMERICALLY_EVALUATED']
    assert not flux['claim_boundary']['AE4_CURRENT_C2_NONZERO_SECTOR_CALDERON_BLOCKS_EVALUATED']
    pattern = r'Horndeski|Pi2_R1|G_S2|cosmolog.{0,80}(projector|intertwiner|normalization)|physical.{0,30}ell.?2'
    search = subprocess.run(['rg', '-l', '-i', pattern, 'docs', 'artifacts', 'src', 'theory', 'museum',
        '--glob', '*.md', '--glob', '*.json', '--glob', '*.py', '--glob', '*.tsx',
        '--glob', '!BHSM_GLOBAL_ACTION_X2_SELECTION*', '--glob', '!audit_global_action_x2_selection_v1.py',
        '--glob', '!BHSM_COSMOLOGY_MISSION_STATE_V1.json'], cwd=ROOT, capture_output=True, text=True)
    assert search.returncode in [0, 1], search.stderr
    # A preceding read-only scan of all 19 registered worktrees, using this
    # pattern, found no additional matching paths. Record byte variants of the
    # matched inputs as well: identical filenames are not assumed identical data.
    wt_listing = git(ROOT, 'worktree', 'list', '--porcelain').splitlines()
    cross_worktree = []
    for line in wt_listing:
        if not line.startswith('worktree '):
            continue
        other = Path(line[9:])
        records = {}
        for name in search.stdout.splitlines():
            p = other/name
            if p.is_file():
                same_text = p.read_text(encoding='utf8') == (ROOT/name).read_text(encoding='utf8')
                assert same_text, f'New substantive worktree variant requires review: {p}'
                records[name] = dict(sha256=sha(p), identical_to_primary=sha(p)==sha(ROOT/name),
                                     identical_after_newline_normalization=same_text)
        cross_worktree.append(dict(path=str(other), matched_path_snapshots=records))
    report = dict(
        schema='BHSM-global-action-X2-selection-audit-v1', statuses=STATUSES,
        stop=dict(step=2, first_missing_object=FIRST_MISSING,
                  detail='No evaluated full-preimage-to-cosmological-n2 projector P2 and normalized physical profile e2 on a declared current background/domain were located. The conditional operator contract exists; its physical cosmological instantiation is missing.',
                  consequence='Do not compute q2, Pi2, source/inertia/mixed block, branch uniqueness or a data comparison from a surrogate.'),
        provenance=dict(handoff_path=str(HANDOFF), handoff_sha256=sha(HANDOFF),
            bhsm_branch=git(ROOT, 'branch', '--show-current'), bhsm_commit=git(ROOT, 'rev-parse', 'HEAD'),
            r1_branch=git(R1, 'branch', '--show-current'), r1_commit=git(R1, 'rev-parse', 'HEAD'),
            input_sha256=before, evidence=excerpts,
            local_refs=git(ROOT, 'for-each-ref', '--format=%(refname) %(objectname)', 'refs/heads').splitlines(),
            worktrees=wt_listing, matching_file_variants_across_worktrees=cross_worktree,
            relevant_all_branch_history=git(ROOT, 'log', '--all', '--oneline', '--regexp-ignore-case',
                '--extended-regexp', '--grep=cosmolog|full.preimage|global.envelopment|ell.?2.*project|canonical.*normaliz', '-35').splitlines(),
            search_pattern=pattern, primary_checkout_search_matches=sorted(search.stdout.splitlines()),
            scope_limit='Local working files, docs, artifacts, source, museum, current worktrees and relevant all-branch history. No assertion about inaccessible external archives or unexamined deleted historical blobs.',
            script_sha256=sha(Path(__file__))),
        supersession=dict(
            v14_54='Moving-seam/relative-periodic architecture and kinematic capability; no selected orbit/phase.',
            v14_60='Synthetic convex global-envelopment witness, not a physical q2/Pi2 solution.',
            v14_90_91='Conditional P1/eta full-preimage results and cap-common momentum; not a blanket no-dynamics theorem.',
            v16_22='Explicitly acknowledges an independently solved constrained orbit and keeps the separate Horndeski cosmology out of microscopic action input.',
            AE3_AE4='Local same-spacetime enclosure, state transport, six-sector assembly and event-flux identities exist. Their presence supersedes a blanket claim that no domain, localization or dynamics exist.',
            remaining_specific_gap='None of those recovered objects supplies the evaluated cosmological P2/e2 and a symplectic intertwiner to frozen R1.'),
        retained_current_positive_results={k:frontier[k] for k in [
            'local_enclosure_and_state_transport_already_closed','six_sector_assembly_already_derived',
            'current_identification_rows','physical_nonzero_sector_values_evaluated']},
        normalization=dict(status='MISSING', conditional_necessary_relations=[
            'If q_B=s*zeta with constant nonzero s, identical time/volume conventions and no cross-term or boundary momentum shift, symplectic matching requires Pi_R=s*Pi_B.',
            'Matching the quadratic kinetic actions then requires s^2*G2=2*G_S2.',
            'Only if action ownership establishes s=1 under those assumptions does G2=2*G_S2 follow.',
            'Time-dependent s, D_t connections, moving-domain terms and mixed fluid momenta require the complete pulled-back symplectic form, not a comparison of two printed kinetic coefficients.'
        ], assumptions_verified=False, normalization_value=None,
            r1_boundary='R1 canonical X2 is already closed. Its six-state momentum is a^3(M xdot+L x); X2 labels two seed columns and is not a new microscopic BHSM normalization derivation.'),
        phase=dict(status='UNDECIDABLE', findings=[
            'A relative-periodic orbit modulo translations does not specify its phase relative to cosmological a(t).',
            'Current canonical-stop and sigma-zero events have action-owned roles, but no owned map to the R1 z=2.1 event was located.',
            'No evaluated projected J2(t), parent clock intertwiner, or boundary rule fixing the cosmological momentum sign was located.',
            'Do not label the unresolved phase as gauge-only or assert it is physically free on an unconstructed cosmological branch.'
        ]),
        numeric_outputs={k:None for k in ['q2_anchor','Pi2_anchor','Pi2_over_q2_anchor',
            'canonical_unit_direction','source_J2_projection','ell2_inertia','ell2_restoring_coefficient',
            'cap_relative_momentum_difference','common_domain_Green_leakage','constraint_residuals',
            'kinetic_eigenvalues','branch_phase_uniqueness','posthoc_chi2','posthoc_p']},
        interpretation='Requested cosmological global branch NOT_DERIVED in audited records; not a proof of nonexistence or denial of retained BHSM dynamical/local enclosure solutions.',
        next_object_contract=['action/background/domain identity for the cosmological parent',
            'constraint and gauge quotient with declared inner product',
            'explicit P2, normalized e2 and their physical-domain and spectral identification',
            'reduced symplectic pullback into R1 with no duplicate scalar',
            'then evaluate source/relative momentum/branch and phase ownership before any observational comparison'],
        controls=dict(observational_inputs_used_for_selection=False, fits_performed=0,
            frozen_parameters_changed=False, Option1_reopened=False, synthetic_witness_promoted=False,
            new_worktree_created=False, reason_no_worktree='Prerequisite normalization map was not identified; stayed in inventory mode and added only audit files.',
            manuscript_changed=False, remote_main_changed=False, unrelated_work_overwritten=False),
    )
    assert before == {str(root/p): sha(root/p) for root, paths in [(ROOT, BHSM_INPUTS), (R1, R1_INPUTS)] for p in paths}
    report['verification'] = dict(input_hashes_unchanged=True, evidence_assertions_passed=True,
                                  numerical_solver_run=False, data_test_run=False,
                                  cross_worktree_matched_file_differences_only_newlines=True)
    body = (ROOT/'docs'/f'{STEM}.md').read_text(encoding='utf8')
    report['report_sha256'] = hashlib.sha256(body.encode('utf8')).hexdigest()
    target = ROOT/'artifacts'/f'{STEM}.json'
    target.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False)+'\n', encoding='utf8')
    print(json.dumps(STATUSES, indent=2))
    print('Artifact SHA256:', sha(target))


if __name__ == '__main__':
    materialize()
