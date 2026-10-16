"""Bind reviewed action/domain derivations; do not claim numerical physics gates."""
from pathlib import Path
from hashlib import sha256
import argparse
import json

from bind_muon_real_coupled_open_operator_20261016 import staged_blobs


def digest(raw):
    return sha256(raw).hexdigest()


def bind(repository, output):
    root, out = Path(repository).resolve(), Path(output).resolve()
    if out.exists():
        raise FileExistsError(out)
    base = root / 'artifacts/muon_native_domain_variational_derivation_20261016'
    index = json.loads((base / 'derivation_index.json').read_bytes())
    assert index['numerical_campaigns'] == 0
    assert not index['physical_outgoing_solution_evaluated']
    assert index['original_coupled_corrections_applied'] == 0
    assert len(index['proofs']) == 3 and len(index['owner_sources']) == 34
    review = json.loads((base / 'review_receipt.json').read_bytes())
    assert review['scientific_review_passed']
    assert not review['review_is_physical_derivative_test']
    for stem, item in index['proofs'].items():
        assert digest((base / item['note']).read_bytes()) == item['note_sha256']
        assert digest((base / item['source_pins']).read_bytes()) == item['source_pins_sha256']
        assert review['proof_sha256'][stem] == item['note_sha256']
    source_blobs = staged_blobs(root, sorted(index['owner_sources']))
    for rel, item in sorted(index['owner_sources'].items()):
        snapshot = root / item['snapshot']
        consumed, blob = snapshot.read_bytes(), source_blobs[rel]
        assert digest(consumed) == item['sha256'], rel
        assert digest(blob) == item['index_sha256'], rel
        if item['reconstruction'] == 'identity':
            assert consumed == blob, rel
        elif item['reconstruction'] == 'replace_every_index_LF_with_CRLF':
            assert b'\r\n' not in blob and consumed == blob.replace(b'\n', b'\r\n'), rel
        else:
            raise ValueError('Unknown exact source reconstruction: ' + rel)
    for name, expected in index['archival_pin_generators'].items():
        assert digest((base / 'archival_generators' / name).read_bytes()) == expected
    audit_dir = base / 'publication_audits'
    audits = json.loads((audit_dir / 'results.json').read_bytes())
    assert len(audits) == 5
    for name, item in audits.items():
        assert item['exit_code'] == 0, name
        assert digest((audit_dir / (name + '.log')).read_bytes()) == item['log_sha256']
        raw = (audit_dir / (name + '.log')).read_bytes()
        if name == 'precision':
            assert b'PASS' in raw and b'FAIL' not in raw
        else:
            assert json.loads(raw)['passed'], name
    cut = ('artifacts/muon_baton_zoo_maximal_current_realization_20261013/'
           'actual_linear_cut_compatible368_MP_full_operator_blocked_run_2/'
           'actual_precise_direct_CHILD620_and_full368_canonical_source_operands.npz')
    target_sha = 'ea02ed6aee45310c5651fef5c8f103e868007d4f125582ab2b64ff7651f76b2b'
    assert digest((root / cut).read_bytes()) == target_sha
    assert digest(staged_blobs(root, [cut])[cut]) == target_sha
    pins = {}
    for path in sorted(base.rglob('*')):
        if path.is_file() and not path.name.startswith('publication_manifest_run_'):
            pins[path.relative_to(root).as_posix()] = digest(path.read_bytes())
    for path in (Path(__file__).resolve(), root / 'audits/bind_muon_real_coupled_open_operator_20261016.py'):
        pins[path.relative_to(root).as_posix()] = digest(path.read_bytes())
    result = dict(
        classification='DERIVED_GREEN_DOMAIN_AND_ADMISSIBLE_STATIONARITY_WITH_OPEN_COMMON_GRADED_REALIZATION',
        source_algebra_derivations=3, owner_source_files=34,
        exact_source_snapshots_and_index_reconstruction_verified=True,
        conditional_closed_factor_square_construction_derived=True,
        allowed_nonfermion_domain_relation_stationarity_derived=True,
        existing_M4_seed_operator_and_statistics_dictionary_retained=True,
        spin_connection_full_D5_and_complement_not_truncated=True,
        scalar_cutoff_support_domain_and_relative_contacts_retained=True,
        independent_older_Wilson_or_cutoff_freedom_reopened=False,
        classical_Hessian_identified_with_native_operator=False,
        physical_BHSM_nonuniqueness_or_nonexistence_proved=False,
        repeated_binder_is_new_physical_solve=False,
        numerical_campaigns_executed=0, completed_campaigns_replayed=0,
        complete_physical_common_graded_operator_domain_evaluated=False,
        full_outgoing_solution_or_energy_field_derivatives_evaluated=False,
        physical_radial_convergence_established=False,
        full_physical_derivative_passed_at_2e_minus_10=False,
        original_coupled_corrections_applied=0,
        Maxwell_and_all_original_226_after_correction_validated=False,
        physical_two_spin_normalization=None, physical_muon_magnetic_moment=None,
        required_original_residual_tolerance=2e-10,
        unchanged_original_reference=dict(artifact=cut, sha256=target_sha,
            Maxwell_magnitude=2.4777309846820184,
            original_226_maximum=9.602842247524184e-7,
            residuals_recomputed_in_this_packet=False),
        publication_process_audits_passed=5,
        exact_packet_and_binder_sha256=pins,
    )
    out.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + '\n',
                   encoding='utf8', newline='\n')
    print(json.dumps(dict(file=out.name, sha256=digest(out.read_bytes()),
        source_algebra_derivations=3, physical_full_derivative_pass=False,
        coupled_corrections=0)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    bind(args.repository, args.output)
