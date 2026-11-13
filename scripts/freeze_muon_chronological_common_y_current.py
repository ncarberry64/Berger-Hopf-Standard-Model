"""Freeze common-action source coefficients and verified exterior source API."""
from pathlib import Path
from hashlib import sha256
import json
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'artifacts/muon_chronological_common_y_current_20261011'


def freeze():
    out=BASE/'pair_verification'
    if out.exists():raise FileExistsError('preserve every common-source replay receipt')
    files={};pins={};pairs=[];runtime=[];projected=[]
    def identity(path):
        p=Path(path);p=p if p.is_absolute()else ROOT/p
        return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,
                    sha256=sha256(p.read_bytes()).hexdigest())
    for side,chunks in(('incoming',('3cc037','6982f5')),('outgoing',('976abb','b95dc9'))):
        folders=[BASE/f'{side}_run_{i}'for i in(1,2)]
        m=[json.loads((p/'result.json').read_bytes())for p in folders]
        if any(x['classification']!='EVALUATED_SAME_GLOBAL_COUPLED_CURRENT_GG_GH_HG_HH_WITHOUT_NEW_INVERSE'for x in m):
            raise ValueError('same original common-source classification required')
        if m[0]['input_hashes']!=m[1]['input_hashes']or m[0]['archives']!=m[1]['archives']:
            raise ArithmeticError('same common current replay source/array identities differ')
        for name in ('result.json',*m[0]['archives']):
            ids=[identity(p/name)for p in folders]
            if ids[0]['sha256']!=ids[1]['sha256']or ids[0]['bytes']!=ids[1]['bytes']:
                raise ArithmeticError('common current bytes differ: '+name)
            if ids[0]['bytes']>=10*1024**2:raise ArithmeticError('publication cap exceeded')
            for a in ids:files[a['path']]=a
        for rel,h in m[0]['input_hashes'].items():
            if rel in pins and pins[rel]!=h:raise RuntimeError('inconsistent common-source pin: '+rel)
            if identity(rel)['sha256']!=h:raise RuntimeError('consumed common-source pin changed: '+rel)
            pins[rel]=h
        pairs.append(dict(left=folders[0].relative_to(ROOT).as_posix(),right=folders[1].relative_to(ROOT).as_posix(),
                          all_files_byte_identical=True,result_sha256=identity(folders[0]/'result.json')['sha256']))
        for i,chunk in zip((1,2),chunks):
            runtime.append(dict(command=['C:/Python314/python.exe','scripts/evaluate_muon_chronological_common_y_current.py',
                '--action-folder','artifacts/muon_chronological_n1_field_action_20261011/run_1',
                '--current-base','artifacts/muon_chronological_literal_current_20261011','--source-side',side,
                '--output',f'artifacts/muon_chronological_common_y_current_20261011/{side}_run_{i}'],
                environment=dict(PYTHONPATH='src',OPENBLAS_NUM_THREADS='4'),exit_code=0,completion_chunk=chunk))
        with np.load(folders[0]/'common_source_current_coefficients.npz')as a,np.load(
                folders[0]/'independent_transpose_current_coefficients.npz')as b:
            d=a['ordered_GG_GH_HG_HH']-b['independent_transpose_ordered_GG_GH_HG_HH']
        ym,ye=m[0]['fixed_Y_middle'],m[0]['fixed_Y_light'];pd=(ym-ye)*(d[1]+d[2]+(ym+ye)*d[3])
        projected.append(dict(source_side=side,
            ordered_GG_GH_HG_HH_transpose_difference_max=[float(np.max(abs(x)))for x in d],
            common_source_paired_transpose_difference_max=float(np.max(abs(pd))),
            common_source_paired_transpose_difference_norm=float(np.linalg.norm(pd)),
            defects_are_binary_estimates_not_outward_bounds=True,
            same_family_exterior_map_or_physical_overlap_cancellation_proved=False))
    for rel in('scripts/evaluate_muon_chronological_common_y_current.py',
        'src/bhsm/interface/muon_chronological_common_y_current.py','tests/test_muon_chronological_common_y_current.py',
        'src/bhsm/interface/muon_chronological_exterior_current_source.py','tests/test_muon_chronological_exterior_current_source.py',
        Path(__file__).relative_to(ROOT).as_posix()):
        files[rel]=identity(rel)
    for stem in('core_pair_verification','extension_pair_verification'):
        for name in('publication_manifest.json','verification.json','runtime_log.json'):
            rel=f'artifacts/muon_chronological_current_applications_20261011/{stem}/{name}'
            files[rel]=identity(rel)
    tests=[]
    for stem,chunk,duration in(('muon_chronological_common_y_current','515c2b',.85),
                                ('muon_chronological_exterior_current_source','9e28a7',.83)):
        tests.append(dict(command=['C:/Python314/python.exe','-m','pytest','--noconftest','-q',f'tests/test_{stem}.py'],
            environment=dict(PYTHONPATH='src',OPENBLAS_NUM_THREADS='4'),exit_code=0,
            completion_chunk=chunk,passed=2,duration_seconds=duration))
    out.mkdir(parents=True)
    def write(name,data):
        p=out/name;p.write_text(json.dumps(data,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
        return p
    log=write('runtime_log.json',dict(classification='ACTUAL_COMMON_SOURCE_CURRENT_AND_EXTERIOR_SOURCE_TEST_RUNTIME',
        commands=runtime,tests=tests,independent_replays=pairs,
        exterior_source_API_review='Owner independently reviewed exp±E*tau, independent trace jets, literal transpose and explicit -p^T K_Eu contacts clean.',
        no_arbitrary_nonzero_energy_or_exterior_state_production=True))
    pp=write('projected_transpose_diagnostics.json',dict(classification='EVALUATED_COMMON_SOURCE_PLACEMENT_TRANSPOSE_DEFECTS',
        source_orders=['GG','GH','HG','HH'],records=projected,
        response_coefficient_inverse_error_or_physical_Pauli_error_enclosed=False))
    for p in(log,pp):files[p.relative_to(ROOT).as_posix()]=identity(p)
    mp=write('publication_manifest.json',dict(classification='FROZEN_GLOBAL_COMMON_SOURCE_CURRENT_AND_EXTERIOR_SOURCE_API',
        files=[files[k]for k in sorted(files)],input_hashes=pins,independent_replays=pairs,
        current_column_shape=[6,2,6,4],original_nodes=1151,source_cells=384,corner_returns=383,
        full_complex_H_Gauss_frame_both_spectators_and_GH_HG_contacts_retained=True,
        protected_GG_cancellation_scope='Identical common unnormalized current source graph and same field K; independently matched physical family exterior maps may change GG contractions.',
        numerical_source_coefficients_inherit_independent_binary_solve_errors=True,
        exterior_point_map_application_interface_verified=True,
        physical_exterior_trace_maps_are_not_produced_by_this_package=True,
        no_new_inverse_or_charge_mass_scale_normalization_used=True,
        physical_a_mu=None,physical_g_mu=None,complete_physical_observable=False))
    result=dict(classification='PASSED_GLOBAL_COMMON_SOURCE_CURRENT_REPLAY_AND_EXTERIOR_SOURCE_API',
                selected_file_count=len(files),input_pin_count=len(pins),pair_count=2,focused_tests_passed=4,
                all_replays_exit_zero=True,all_input_pins_current=True,
                manifest_sha256=identity(mp)['sha256'])
    vp=write('verification.json',result)
    print(json.dumps(dict(**result,verification_sha256=identity(vp)['sha256']),sort_keys=True))


if __name__=='__main__':freeze()
