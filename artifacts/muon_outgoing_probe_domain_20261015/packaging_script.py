"""Bind new independently evaluated diagnostics without promoting a moment."""
from hashlib import sha256
import json
from pathlib import Path
from shutil import copyfile
from argparse import ArgumentParser

WORK=Path(r'C:/Users/carbe/OneDrive/Documents/CODEX')
REPO=Path(r'C:/Users/carbe/Downloads/BHSM_muon_parent_maxwell_worktree_20261001')
OUT=REPO/'artifacts/muon_outgoing_probe_domain_20261015'


def digest(path):return sha256(path.read_bytes()).hexdigest()


def encoded(value):return (json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()


def copy(source,target):
    target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists() and target.read_bytes()!=source.read_bytes():
        raise ValueError('Preserve different archived bytes: '+str(target))
    copyfile(source,target)


def pair(base,left,right,component,selected=None):
    a,b=base/left,base/right
    names=sorted(p.relative_to(a).as_posix() for p in a.rglob('*') if p.is_file())
    other=sorted(p.relative_to(b).as_posix() for p in b.rglob('*') if p.is_file())
    if names!=other:raise ValueError('Different scientific output files')
    hashes={}
    archived=[]
    for name in names:
        if (a/name).read_bytes()!=(b/name).read_bytes():raise ValueError('Different scientific repeat bytes: '+name)
        hashes[name]=digest(a/name)
        if selected is None or selected(name):
            for run in (left,right):copy(base/run/name,OUT/component/run/name)
            archived.append(name)
    return dict(component=component,source_base=str(base),actual_independent_evaluations=[left,right],
        all_output_sha256=hashes,archived_files=archived)


def chunks(source,relative):
    data=source.read_bytes();parts=[]
    for index,start in enumerate(range(0,len(data),4*1024**2)):
        part=data[start:start+4*1024**2]
        target=OUT/(relative+f'.{index:03d}.bin');target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists() and target.read_bytes()!=part:raise ValueError('Different old chunk')
        target.write_bytes(part)
        parts.append(dict(path=target.relative_to(OUT).as_posix(),bytes=len(part),sha256=sha256(part).hexdigest()))
    if b''.join((OUT/q['path']).read_bytes() for q in parts)!=data:raise ValueError('Chunk reconstruction mismatch')
    return dict(original_source=str(source),original_name=source.name,bytes=len(data),sha256=digest(source),chunks=parts)


def main(radial_binding,canonical_left,canonical_right):
    pairs=[pair(WORK/'outputs/bhsm_outgoing_missing_jet_sensitivity_20261015','run_1','run_2','missing_jet_sensitivity'),
           pair(WORK/'outputs/bhsm_outgoing_trace_two_parameter_jet_20261015','run_1','run_2','mixed_domain_consumer'),
           pair(WORK/'outputs/bhsm_physical_outgoing_operand_evidence_20261015','run_1','run_2','physical_operand_evidence')]
    radial=json.loads(radial_binding.read_bytes())
    radial2=radial_binding.with_name(radial_binding.name.replace('_3.json','_4.json'))
    if radial_binding.read_bytes()!=radial2.read_bytes():raise ValueError('Radial comparison repeats differ')
    copy(radial_binding,OUT/'radial_binding_run_1.json')
    copy(radial2,OUT/'radial_binding_run_2.json')
    for n in (1,2):copy(radial_binding.parent/f'binding_run_{n}.json',OUT/f'radial_prior_failed_binding_run_{n}.json')
    actual_base=radial_binding.parent
    pairs.append(pair(actual_base,canonical_left,canonical_right,'actual_canonical_polynomials'))
    canonical=json.loads((actual_base/canonical_left/'result.json').read_bytes())
    chunkmap=[]
    for repeat in radial['repeat_pairs']:
        role,order=repeat['kind'],repeat['order']
        if role=='actual_canonical_algebraic_reconstruction':continue
        component=f'radial/{role}/order{order}'
        source_dirs=[Path(repeat['left']),Path(repeat['right'])]
        archived=[];chunked=[]
        for name,expected in repeat['files'].items():
            left,right=(p/name for p in source_dirs)
            if left.read_bytes()!=right.read_bytes() or digest(left)!=expected:
                raise ValueError('Radial actual numerical repeat differs: '+str(left))
            if left.stat().st_size>10*1024**2:
                target_relative=f'{component}/{name}'
                item=chunks(left,f'radial_reduced_chunks/order{order}/{name}')
                item['target_relative']=target_relative;chunkmap.append(item);chunked.append(name)
            else:
                for i,source in enumerate((left,right),1):copy(source,OUT/component/f'run_{i}'/name)
                archived.append(name)
        pairs.append(dict(component=component,source_base=str(source_dirs[0].parent),
            actual_independent_evaluations=[str(p)for p in source_dirs],
            all_output_sha256=repeat['files'],archived_files=archived,chunked_files=chunked,
            coefficient64_metadata_different_because_first_order_is_different=(role=='actual_coefficient_integration'and order==64)))
    (OUT/'radial_reduced_chunk_manifest.json').write_bytes(encoded(chunkmap))
    base=radial_binding.parent
    for order in (64,96):
        for role in ('field','lepton'):
            folder=base/f'order{order}_{role}_run_1'
            selected=[p for p in folder.iterdir() if p.is_file() and (
                p.name=='result.json' or p.name.startswith('piece_')or p.name.startswith('actual_nonzero_final')
                or p.name=='finite_polynomial_angular_response.npz')]
            for p in selected:copy(p,OUT/f'radial/lower_order_diagnostics/order{order}/{role}'/p.name)
    for name in ('bhsm_muon_same_epoch_n1_radial_quadrature_20261015.py',
                 'bhsm_muon_radial_response_orchestrator_20261015.py','bhsm_muon_radial_response_binding_20261015.py',
                 'bhsm_muon_actual_canonical_radial_polynomials_20261015.py','bhsm_muon_actual_canonical_radial_binding_20261015.py'):
        copy(WORK/name,OUT/'sources'/name);copy(WORK/name,REPO/'audits'/name)
    source_sha={p.name:digest(p) for p in sorted((OUT/'sources').glob('*.py'))}
    report=dict(classification='EVALUATED_FINITE_RADIAL_REFINEMENT_AND_OUTGOING_PROBE_DOMAIN_CONTACTS',
        actual_scientific_repeat_pairs=pairs,original_source_sha256=source_sha,
        radial_comparison_sha256=digest(radial_binding),
        radial_comparison_scope='See both original shifted-w and canonical-z diagnostics, including every failed criterion. Finite observed comparisons do not establish physical exterior convergence.',
        observed_actual_canonical_z_coefficient_relative=canonical['max_actual_z_polynomial_coefficient_relative'],
        observed_actual_full336_coefficient_relative=canonical['max_actual_full336_polynomial_coefficient_relative'],
        retained_failed_shifted_w_coefficient_relative=canonical['retained_failed_shifted_w_comparison'],
        shifted_chart_broad_criterion_pass=canonical['broad_all_reported_criterion_from_prior_binding_pass'],
        installed_consumer_matches_evaluated_source_bytes=(REPO/'src/bhsm/interface/muon_outgoing_trace_probe_jet.py').read_bytes()==(OUT/'sources/bhsm_outgoing_trace_two_parameter_jet_20261015.py').read_bytes(),
        physical_outgoing_energy_jet=None,physical_outgoing_magnetic_jet=None,
        physical_full_derivative_passed=False,physical_radial_convergence_established=False,
        normalized_physical_two_spin_state=None,physical_magnetic_moment=None,physical_g_mu=None,physical_a_mu=None,
        coupled_matching_corrections_applied=0,after_correction_Maxwell_all226_pass=False,
        completed_source_D5_profile_history_canonical_pairing_campaigns_restarted=False,
        empirical_muon_mass_or_anomaly_consumed=False,
        serialization_is_not_an_independent_scientific_evaluation=True)
    payload=encoded(report)
    for number in (1,2):(OUT/f'binding_run_{number}.json').write_bytes(payload)
    target=OUT/'packaging_script.py'
    if target.exists()and target.read_bytes()!=Path(__file__).read_bytes():
        copy(target,OUT/'pre_radial_packaging_script.py')
    target.write_bytes(Path(__file__).read_bytes())
    print(json.dumps(dict(binding_sha256=sha256(payload).hexdigest(),scientific_pairs=len(pairs))))


if __name__=='__main__':
    parser=ArgumentParser(description=__doc__);parser.add_argument('--radial-binding',type=Path,required=True)
    parser.add_argument('--canonical-left',default='actual_canonical_polynomials_run_1')
    parser.add_argument('--canonical-right',default='actual_canonical_polynomials_run_2')
    args=parser.parse_args();main(args.radial_binding,args.canonical_left,args.canonical_right)
