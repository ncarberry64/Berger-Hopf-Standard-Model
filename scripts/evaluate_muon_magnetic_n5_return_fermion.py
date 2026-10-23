"""Evaluate the necessary n5 fermion return on the same changing magnetic core."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase
from bhsm.interface.muon_magnetic_n5_return_fermion import changing_n5_return_fermion_application
from evaluate_muon_reached_trace_action import deterministic_archive


def materialize(output,*,quadrature_order=12):
    out=Path(output);out=out if out.is_absolute()else ROOT/out
    if out.exists():raise FileExistsError('preserve earlier source-return applications')
    parent=ROOT/'artifacts/muon_even_source_temporal_fermion_20261011/run_1/result.json'
    raw=parent.read_bytes();receipt=json.loads(raw)
    if receipt['classification']!='EVALUATED_COMPLETE_EVEN_SAME_PHASE_SOURCE_TEMPORAL_FERMION_FORM':
        raise ValueError('same complete even source-image application required')
    refs=dict(receipt['input_hashes']);refs[parent.relative_to(ROOT).as_posix()]=sha256(raw).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise ValueError('same-background source owner changed')
    out.mkdir(parents=True);files={};records=[]
    for side in ('incoming','outgoing'):
        phase=load_profile_preserving_phase('artifacts/muon_finite_normal_phase_20261011/incoming_run_1'if side=='incoming'else'artifacts/muon_inherited_finite_normal_phase_20261011/run_1')
        refs.update(phase['input_hashes'])
        app=changing_n5_return_fermion_application(phase,length=abs(phase['receipt']['span']),quadrature_order=quadrature_order,
            progress=lambda r:print(json.dumps(dict(stage='magnetic_n5_return',side=side,**r),sort_keys=True),flush=True))
        for i,b in enumerate(app['block_arrays']):
            p=out/(side+'_block_'+str(i)+'.npz');deterministic_archive(p,b)
            if p.stat().st_size>10*1024**2:raise ValueError('lossless complete return block exceeds publication limit')
            files[p.name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
        keys=('real_to_complex','complex_derivatives','temporal_basis_values','temporal_basis_coordinate_rates',
            'source_temporal_Gram','source_temporal_congruence','chronological_quadrature_times',
            'chronological_quadrature_weights','coordinate_times','coefficient_N_R','coefficient_W','coefficient_Omega')
        p=out/(side+'_samples.npz');deterministic_archive(p,{k:app[k]for k in keys})
        files[p.name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
        records.append(dict(side=side,block_records=app['block_records'],temporal_Gram_condition=app['temporal_Gram_condition'],spectator_off_block_max=app['spectator_off_block_max']))
    for p in ('src/bhsm/interface/muon_magnetic_n5_return_fermion.py','tests/test_muon_magnetic_n5_return_fermion.py',Path(__file__).relative_to(ROOT).as_posix()):
        refs[p]=sha256((ROOT/p).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('same action changed during return application')
    result=dict(classification='EVALUATED_SAME_PHASE_MAGNETIC_N5_FERMION_RETURN_FORM',input_hashes=refs,numerical_files=files,records=records,
        action_parameters=phase['receipt']['action_parameters'],quadrature_order=quadrature_order,
        full_n5_harmonic_count=36,full_n5_return_dimension=5184,
        exact_image_reason='field-even n4 times externalconstant gives F-even n4; magnetic n1 reaches F-odd n5, which returns through field-even n4 times externaln1',
        exact_reduction='all18 fibers and n5 scalar orbital functions, reorganized by literal family/Wigner spectator identities with all8 source temporal functions',
        starting_field_loop_domain_enlarged=False,source_return_not_filled_zero=True,small_mode_deletion=False,
        variable_coefficient_differential_closure_claimed=False,physical_P_strat_Wick_LSZ_Pauli_completed=False,
        physical_a_mu=None,physical_g_mu=None,error_scope='actual binary64 finite source-return weak form and eigen diagnostics; no producer/eigen/continuum or physical matching enclosure')
    (out/'result.json').write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return dict(classification=result['classification'],record_count=sum(len(r['block_records'])for r in records))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--quadrature-order',type=int,default=12)
    a=p.parse_args();print(json.dumps(materialize(a.output,quadrature_order=a.quadrature_order),sort_keys=True))
