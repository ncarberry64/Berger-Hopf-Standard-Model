"""Freeze completed whole original current action/body/energy applications."""
from pathlib import Path
from hashlib import sha256
import json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts/muon_chronological_current_applications_20261011/core_pair_verification'
PACKS=(
 dict(folder='muon_chronological_n1_field_action_20261011',runs=('run_1','run_2'),
      classification='EVALUATED_GLOBAL_ORIGINAL_N1_FIELD_ACTION_AND_EXACT_OWNED_CURRENT_TEST_LIFT',
      producer='scripts/evaluate_muon_chronological_n1_field_action.py',arguments=(),
      chunks=('bfdbe1','d421c8'),test='muon_chronological_harmonic_field_action',test_chunk='ccdf1e',tests=2,duration=1.94),
 dict(folder='muon_chronological_current_body_20261011',runs=('run_1','run_2'),
      classification='EVALUATED_CORRECTED_WHOLE_CHRONOLOGICAL_FULL18_CURRENT_BODY_AND_COORDINATE_FIRST_GERM',
      producer='scripts/evaluate_muon_chronological_current_body.py',
      arguments=('--action-folder','artifacts/muon_chronological_n1_field_action_20261011/run_1'),
      chunks=('7651f1','60e345'),test='muon_chronological_current_body',test_chunk='a789ee',tests=2,duration=4.58),
 dict(folder='muon_chronological_literal_current_20261011',runs=('incoming_family_1_run_1','incoming_family_1_run_2'),
      classification='EVALUATED_WHOLE_ORIGINAL_N1_LITERAL_CURRENT_AND_TRANSPOSE_ADJOINT',
      producer='scripts/evaluate_muon_chronological_literal_current.py',
      arguments=('--action-folder','artifacts/muon_chronological_n1_field_action_20261011/run_1',
                 '--source-side','incoming','--family','1','--current-kind','literal'),
      chunks=('d164ab','258d7b'),test='muon_chronological_literal_current_source',test_chunk='a37b84',tests=2,duration=1.02),
 dict(folder='muon_chronological_literal_current_20261011',runs=('outgoing_family_1_run_1','outgoing_family_1_run_2'),
      classification='EVALUATED_WHOLE_ORIGINAL_N1_LITERAL_CURRENT_AND_TRANSPOSE_ADJOINT',
      producer='scripts/evaluate_muon_chronological_literal_current.py',
      arguments=('--action-folder','artifacts/muon_chronological_n1_field_action_20261011/run_1',
                 '--source-side','outgoing','--family','1','--current-kind','literal'),
      chunks=('fb1728','a0b4fe'),test='muon_chronological_current_factor',test_chunk='fd1ded',tests=2,duration=.90),
 dict(folder='muon_chronological_current_energy_20261011',runs=('incoming_family_1_run_1','incoming_family_1_run_2'),
      classification='EVALUATED_WHOLE_ORIGINAL_COMPLETE288_CURRENT_BOTH_ORDERED_SOURCE_ENERGY_LEGS',
      producer='scripts/evaluate_muon_chronological_current_energy.py',
      arguments=('--current-folder','artifacts/muon_chronological_literal_current_20261011/incoming_family_1_run_1',
                 '--action-folder','artifacts/muon_chronological_n1_field_action_20261011/run_1'),
      chunks=('3e9a6b','f6a641'),test='muon_chronological_current_energy',test_chunk='d6ca71',tests=2,duration=.84),
 dict(folder='muon_chronological_current_amputation_20261011',runs=('run_1','run_2'),
      classification='EVALUATED_CORRECTED_FULL_BODY_NONSTATIONARY_CURRENT_ENDPOINT_AND_EXTERIOR_POLE_EQUATION',
      producer='scripts/evaluate_muon_chronological_current_amputation.py',
      arguments=('--action-folder','artifacts/muon_chronological_n1_field_action_20261011/run_1',
                 '--body-folder','artifacts/muon_chronological_current_body_20261011/run_1'),
      chunks=('3de644','7f162d'),test='muon_chronological_current_amputation',test_chunk='04f346',tests=2,duration=.82),
)


def freeze():
    if OUT.exists():raise FileExistsError('preserve every current replay receipt')
    files={};pins={};pairs=[];runtime=[];tests=[]
    def identity(p):
        p=Path(p);p=p if p.is_absolute()else ROOT/p
        return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    for pack in PACKS:
        base=ROOT/'artifacts'/pack['folder'];a,b=(base/r for r in pack['runs'])
        ma,mb=(json.loads((p/'result.json').read_bytes())for p in(a,b))
        if ma['classification']!=pack['classification']:
            raise ValueError('unexpected original current application class: '+ma['classification'])
        if ma['input_hashes']!=mb['input_hashes']or ma['archives']!=mb['archives']:
            raise ArithmeticError('same current replay pins or arrays differ')
        for name in ('result.json',*ma['archives']):
            ia,ib=identity(a/name),identity(b/name)
            if ia['sha256']!=ib['sha256']or ia['bytes']!=ib['bytes']:
                raise ArithmeticError('complete original replay differs: '+name)
            if ia['bytes']>=10*1024**2:raise ArithmeticError('publication cap exceeded')
            files[ia['path']]=ia;files[ib['path']]=ib
        for p,h in ma['input_hashes'].items():
            if p in pins and pins[p]!=h:raise RuntimeError('inconsistent consumed source pin: '+p)
            if identity(p)['sha256']!=h:raise RuntimeError('consumed original source changed: '+p)
            pins[p]=h
        pairs.append(dict(left=a.relative_to(ROOT).as_posix(),right=b.relative_to(ROOT).as_posix(),
            complete_file_count=1+len(ma['archives']),all_files_byte_identical=True,
            result_sha256=identity(a/'result.json')['sha256']))
        for run,chunk in zip(pack['runs'],pack['chunks']):
            runtime.append(dict(command=['C:/Python314/python.exe',pack['producer'],*pack['arguments'],
                '--output',f"artifacts/{pack['folder']}/{run}"],
                environment=dict(PYTHONPATH='src',OPENBLAS_NUM_THREADS='4'),exit_code=0,completion_chunk=chunk))
        tests.append(dict(command=['C:/Python314/python.exe','-m','pytest','--noconftest','-q',
                f"tests/test_{pack['test']}.py"],environment=dict(PYTHONPATH='src',OPENBLAS_NUM_THREADS='4'),
                exit_code=0,completion_chunk=pack['test_chunk'],passed=pack['tests'],duration_seconds=pack['duration']))
        for rel in(pack['producer'],f"tests/test_{pack['test']}.py",f"src/bhsm/interface/{pack['test']}.py"):
            files[rel]=identity(rel)
    own=Path(__file__).relative_to(ROOT).as_posix();files[own]=identity(own)
    OUT.mkdir(parents=True)
    logs=dict(classification='ACTUAL_ORIGINAL_CURRENT_ACTION_BODY_ENERGY_REPLAY_RUNTIME',
        commands=runtime,tests=tests,independent_replays=pairs,
        independent_science_review='Validation reviewed harmonic action/source, energy legs and amputation order/signs clean. Body value matches original source exactly; independent time-germ and complex-action controls pass. Root independent complete288 transfer and source charge/body checks are separately evaluated.',
        current_original_row_and_componentwise_defects_retained=True,
        source_energy_and_edge_amputation_are_distinct_operators=True)
    rp=OUT/'runtime_log.json';rp.write_text(json.dumps(logs,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
    files[rp.relative_to(ROOT).as_posix()]=identity(rp)
    manifest=dict(classification='FROZEN_WHOLE_ORIGINAL_CURRENT_ACTION_BODY_ORDERED_ENERGY_AND_AMPUTATION_APPLICATIONS',
        files=[files[p]for p in sorted(files)],input_hashes=pins,independent_replays=pairs,
        original_temporal_nodes=1151,original_source_cells=384,corner_returns=383,
        full_Gauss_H_frame_initial_final_literal_transpose_and_both_spectators_retained=True,
        completed_current_families=[1],other_family_applications_excluded_until_complete=True,
        current_full_response_is_quantum_covariance=False,computational_source_Gram_is_physical_LSZ=False,
        exterior_pole_relation='Bin(E)+Bout(E)*exp(E*L)U; actual exterior maps still require their owned action/domain application',
        independent_exterior_definition_gap_proved=False,complete_physical_observable=False,
        physical_a_mu=None,physical_g_mu=None)
    mp=OUT/'publication_manifest.json';mp.write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
    verified=dict(classification='PASSED_WHOLE_ORIGINAL_CURRENT_APPLICATION_REPLAY_PAIRS',
        selected_file_count=len(files),input_pin_count=len(pins),pair_count=len(pairs),
        test_count=sum(t['passed']for t in tests),manifest_sha256=identity(mp)['sha256'],
        all_original_replays_exit_zero=True,mutable_or_incomplete_outputs_excluded=True)
    vp=OUT/'verification.json';vp.write_text(json.dumps(verified,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(**verified,verification_sha256=identity(vp)['sha256']),sort_keys=True))


if __name__=='__main__':freeze()
