"""Materialize same-phase full5040 even source-image fermion weak forms."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase
from bhsm.interface.muon_even_source_temporal_fermion import changing_even_fermion_application
from evaluate_muon_reached_trace_action import deterministic_archive


def materialize(output,*,quadrature_order=12):
    out=Path(output);out=out if out.is_absolute()else ROOT/out
    if out.exists():raise FileExistsError('preserve prior even source-image applications')
    parent=ROOT/'artifacts/muon_even_coupled_temporal_field_20261011/run_3/result.json'
    raw=parent.read_bytes();receipt=json.loads(raw)
    if receipt['classification']!='EVALUATED_COMPLETE_EVEN_CHANGING_COUPLED_FIELD_GREEN':
        raise ValueError('same changing complete even field image required')
    refs=dict(receipt['input_hashes']);refs[parent.relative_to(ROOT).as_posix()]=sha256(raw).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise ValueError('consumed same-background owner changed')
    out.mkdir(parents=True);files={};records=[]
    for side in ('incoming','outgoing'):
        phase=load_profile_preserving_phase('artifacts/muon_finite_normal_phase_20261011/incoming_run_1'if side=='incoming'else'artifacts/muon_inherited_finite_normal_phase_20261011/run_1')
        refs.update(phase['input_hashes'])
        app=changing_even_fermion_application(phase,length=abs(phase['receipt']['span']),quadrature_order=quadrature_order,
            progress=lambda r:print(json.dumps(dict(stage='complete_even_fermion_block',side=side,**r),sort_keys=True),flush=True))
        for i,b in enumerate(app['block_arrays']):
            p=out/(side+'_block_'+str(i)+'.npz');deterministic_archive(p,b)
            if p.stat().st_size>10*1024**2:raise ValueError('complete lossless even block exceeds publication threshold')
            files[p.name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
        keys=('real_to_complex','complex_derivatives','temporal_basis_values','temporal_basis_coordinate_rates',
            'source_temporal_Gram','source_temporal_congruence','chronological_quadrature_times',
            'chronological_quadrature_weights','coordinate_times','coefficient_N_R','coefficient_W',
            'coefficient_Omega','coefficient_rate_norms')
        p=out/(side+'_samples.npz');deterministic_archive(p,{k:app[k]for k in keys})
        files[p.name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
        records.append(dict(side=side,block_records=app['block_records'],temporal_Gram_condition=app['temporal_Gram_condition'],
            spectator_off_block_max=app['spectator_off_block_max'],complex_frame_unitary_residual=app['complex_frame_unitary_residual'],
            real_to_complex_derivative_residual=app['real_to_complex_derivative_residual']))
    for p in ('src/bhsm/interface/muon_even_source_temporal_fermion.py','src/bhsm/interface/muon_source_directed_temporal_green.py',
            'tests/test_muon_even_source_temporal_fermion.py',Path(__file__).relative_to(ROOT).as_posix()):
        refs[p]=sha256((ROOT/p).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('source/action changed during evaluation')
    result=dict(classification='EVALUATED_COMPLETE_EVEN_SAME_PHASE_SOURCE_TEMPORAL_FERMION_FORM',input_hashes=refs,numerical_files=files,
        records=records,action_parameters=phase['receipt']['action_parameters'],quadrature_order=quadrature_order,
        full_fermion_dimension=5040,full_even_harmonic_count=35,full_canonical_fiber_count=18,source_temporal_function_count=8,
        exact_reduction='literal fixed-family and complex Wigner spectator blocks of the homogeneous changing angular body; all rows retained',
        angular_image='magnetic n1 times odd n1/n3 has complete even n0/n2/n4 image; no statistical or small-mode truncation',
        geometry_clock='same chronological x-linear/vy-midpoint phase; outgoing inherited profile and explicit reference-clock image once',
        temporal_derivative_and_changing_coefficient_contacts_retained=True,
        numerical_rank_deletion=False,variable_coefficient_differential_closure_claimed=False,
        completed_P_strat_or_physical_Wick_LSZ_Pauli=False,physical_a_mu=None,physical_g_mu=None,
        error_scope='binary64 split-Gauss finite weak integration and generalized-eigen diagnostics; no upstream producer/Gram/eigen/continuum or physical-matching enclosure')
    (out/'result.json').write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return dict(classification=result['classification'],record_count=sum(len(a['block_records'])for a in records),numerical_files=files)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--quadrature-order',type=int,default=12)
    a=p.parse_args();print(json.dumps(materialize(a.output,quadrature_order=a.quadrature_order),sort_keys=True))
