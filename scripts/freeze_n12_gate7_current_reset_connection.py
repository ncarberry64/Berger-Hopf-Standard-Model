"""Bind numerical construction evidence without promoting it to a history proof."""
import argparse
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from checkpoint_n12_gate7_66d_tangent_binding import digest,encoded
BASE=ROOT/'artifacts/flagship_integration/gate7_current_reset_connection_20260927'


def calculate(out):
    paths=['arb_predictor/endpoint.npz','arb_predictor/path.npz','arb_predictor/report.json',
           'reset_match_complete/candidate.npz','reset_match_complete/report.json',
           'branches/arrays.npz','branches/report.json']
    reproduction={}
    for relative in paths:
        first,second=BASE/relative,BASE/'replay'/relative
        if first.read_bytes()!=second.read_bytes():raise ValueError('nonidentical reproduction: '+relative)
        reproduction[relative]=dict(SHA256=digest(first),bytes=first.stat().st_size)
    source_records={}
    for relative in ['arb_predictor/report.json','reset_match_complete/report.json','branches/report.json']:
        report=json.loads((BASE/relative).read_bytes())
        for name,expected in report['source_SHA256'].items():
            if digest(ROOT/name)!=expected:raise ValueError('source changed: '+name)
            source_records[name]=expected
    provenance=[
        'artifacts/flagship_integration/BHSM_N12_C2_FIXED_SEED_UPSTREAM_FORCE_OWNER.json',
        'artifacts/flagship_integration/BHSM_N12_C2_RESET_LAUNCH_ADJOINT_INTERFACE.json',
        'artifacts/flagship_integration/BHSM_N12_FINITE_TERMINAL_TWO_SIDED_FORWARD_INTERFACE.json',
        'scripts/certify_n12_gate7_compact_reset_quotient_domain.py',
        'src/bhsm/interface/aether_full_reset_action_jacobian.py',
        'src/bhsm/interface/material_momentum_rate.py',
        'src/bhsm/interface/formation_reset_first_jet.py',
        'tests/test_material_momentum_rate.py','tests/test_formation_reset_first_jet.py',
        'theory/n12_gate7_current_formation_reset_connection.md']
    source_records.update({p:digest(ROOT/p) for p in provenance})
    source_records[str(Path(__file__).relative_to(ROOT))]=digest(Path(__file__))
    report=dict(status='CURRENT_RESET_CONNECTION_AND_TWO_SIDED_INITIAL_GUESS_PRESERVED',
        numerical_outputs_reproduced_byte_identically=reproduction,
        source_SHA256=source_records,
        current_formation_history='NOT_YET_CONSTRUCTED_OR_CERTIFIED',
        current_first_73_jet='NOT_YET_CONSTRUCTED_OR_CERTIFIED',
        current_reset_member='NUMERICAL_PROOF_SECTION_GUESS_ONLY',
        first_mathematical_task='Jointly correct/certify the current reset connection and solve the owned upstream formation stationarity on the seed-invisible directions, then differentiate that solved system.',
        missing_object='CURRENT_CENTER_INCOMING_PARENT_FORMATION_HISTORY_AND_FIRST_JET',
        full_material_history_4x73_materialized=False,
        inherited_trace_proof_reopened=False,frozen_prefix_rebuilt=False,
        extra_environment_action_introduced=False,certificate_tolerances_changed=False,
        Gate7_closed=False,FULL_BHSM_COMPLETE=False)
    out=Path(out);out.mkdir(parents=True,exist_ok=False)
    (out/'report.json').write_bytes(encoded(report))
    print('Seven numerical output files reproduced; source hashes match. No history promotion.')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();calculate(a.out)
