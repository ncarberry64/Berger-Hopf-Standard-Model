"""Exact algebra controls for the native heat/source reconstruction note.

These finite algebra witnesses are not alternative BHSM operators or fields.
They check the note's restricted non-inference, not physical nonuniqueness.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path


def execute(note: Path, output: Path) -> None:
    if output.exists():
        raise FileExistsError(output)
    eigenvalues = (1, 2, 3, 4)
    weights = (tuple(Q(x, 32) for x in (7, 11, 5, 9)),
               tuple(Q(x, 32) for x in (9, 5, 11, 7)))
    records = []
    for w in weights:
        first = sum(a * d for a, d in zip(w, eigenvalues))
        second = sum(a * d**2 for a, d in zip(w, eigenvalues))
        inverse = sum(a / d**2 for a, d in zip(w, eigenvalues))
        assert sum(w) == 1 and min(w) > 0
        assert first == Q(5, 2) and second == Q(15, 2)
        assert second - first**2 == Q(5, 4)
        records.append(dict(weights=list(map(str, w)), compression_D=str(first),
                            compression_P=str(second),
                            complement_first_order_norm_squared=str(second-first**2),
                            fixed_source_inverse=str(inverse)))
    difference = Q(records[0]['fixed_source_inverse']) - Q(records[1]['fixed_source_inverse'])
    assert difference == -Q(25, 768)
    assert [r['fixed_source_inverse'] for r in records] == ['1565/4608', '1715/4608']
    groups = [[], []]
    for k in range(32):
        groups[k.bit_count() % 2].append(k + 1)
    moments = [sum(x**j for x in groups[0]) - sum(x**j for x in groups[1])
               for j in range(6)]
    assert moments == [0, 0, 0, 0, 0, -122880]
    # With V=R/4, the Laplace-type coefficient is R/6 - V = -R/12.
    a2_per_scalar_curvature = Q(1, 6) - Q(1, 4)
    F6_per_F8_without_length = Q(8, 6)
    assert a2_per_scalar_curvature == -Q(1, 12)
    assert a2_per_scalar_curvature * F6_per_F8_without_length == -Q(1, 9)
    result = dict(
        classification='EXACT_FINITE_ALGEBRA_CONTROLS_FOR_SOURCE_RESOLVED_NATIVE_MATCHING_CONSTRAINTS',
        note_sha256=sha256(note.read_bytes()).hexdigest(),
        producer_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        source_resolved_inverse_witness=records,
        fixed_source_inverse_difference=str(difference),
        full_D_and_P_spectra_in_witness_are_identical=True,
        fixed_inclusion_in_witness='J=e1; full unitary conjugation need not preserve J',
        Prouhet_groups=groups,
        exact_moment_differences_orders_0_through_5=moments,
        untwisted_positive_LC_reference_a2_per_R=str(a2_per_scalar_curvature),
        positive_LC_reference_EH_to_volume_ratio='-ell^2/9, conditional on the same nonzero graded rank',
        actual_BHSM_native_module_or_domain_selected=False,
        BHSM_continuum_nonuniqueness_proved=False,
        new_physical_parameter_or_completion_introduced=False,
        full_physical_outgoing_derivative_pass=False,
        coupled_matching_corrections_applied=0,
        normalized_physical_muon_spins=None,
        muon_magnetic_moment=None,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False)+'\n',
                      encoding='utf8', newline='\n')
    print(json.dumps(dict(output=str(output), sha256=sha256(output.read_bytes()).hexdigest())))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--note', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    execute(args.note, args.output)
