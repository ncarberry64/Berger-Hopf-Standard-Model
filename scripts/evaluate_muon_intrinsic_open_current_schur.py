"""Carry the frozen temporal source image through actual external current Greens."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_intrinsic_open_current_schur import source_image_external_current_application
from bhsm.interface.muon_common_cutoff_green_kernel import rigorous_frobenius_upper,outward_positive_product_sum
from evaluate_muon_reached_trace_action import deterministic_archive
from evaluate_muon_intrinsic_scalar_regulator_correction import source_record


def materialize(output,*,source):
    folder=Path(source);folder=folder if folder.is_absolute() else ROOT/folder
    out=Path(output);out=out if out.is_absolute() else ROOT/out
    if out.exists():raise FileExistsError('preserve previous current applications')
    raw=(folder/'result.json').read_bytes();md=json.loads(raw)
    if md['classification']!='EVALUATED_EXACT_TEMPORAL_YUKAWA_SOURCE_IMAGE_GREEN_APPLICATION':
        raise ValueError('actual complete temporal source-image owner required')
    hashes=dict(md['input_hashes']);hashes[(folder/'result.json').relative_to(ROOT).as_posix()]=sha256(raw).hexdigest()
    for p,h in hashes.items():
        if sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise ValueError('consumed action changed: '+p)
    archive=folder/md['archive']['path'];data=archive.read_bytes()
    if len(data)!=md['archive']['bytes'] or sha256(data).hexdigest()!=md['archive']['sha256']:
        raise ValueError('temporal result changed')
    hashes[archive.relative_to(ROOT).as_posix()]=md['archive']['sha256']
    with np.load(archive,allow_pickle=False) as f:temporal={k:f[k] for k in f.files}
    base=ROOT/'artifacts/muon_magnetic_mixed_green_20261011/run_3'
    with np.load(base/'scalar_sources.npz',allow_pickle=False) as f:scalar={k:f[k] for k in f.files}
    arrays={};rows=[];names=('fermion_square_left','fermion_square_right','fermion_numerator_contact','scalar_propagator_insertion','total')
    for side in ('incoming','outgoing'):
        h=scalar[side+'_raw_fields'][-8:-4];H=h[:2]+1j*h[2:]
        family_outputs={}
        for family in range(3):
            prefix=side+'_family_'+str(family)+'_'
            with np.load(base/(side+'_family_'+str(family)+'_fermion_operators.npz'),allow_pickle=False) as f:
                operators={k.removeprefix(prefix):f[k] for k in f.files}
            forward=temporal[prefix+'forward_total'];reverse=temporal[prefix+'reverse_total']
            result=source_image_external_current_application(operators,forward,reverse,H,family=family)
            family_outputs[family]=result
            for key,value in result.items():
                if isinstance(value,np.ndarray):arrays[prefix+key]=value
                elif isinstance(value,dict):
                    for k,v in value.items():
                        if isinstance(v,np.ndarray):arrays[prefix+key+'_'+k]=v
            component_outputs={}
            for name in names[:-1]:
                Z=temporal[prefix+'forward_'+name]
                Zr=temporal[prefix+'reverse_'+name]
                G0=result['external_n0']['Green'];G1=result['external_n1']['Green']
                J0=result['charged_injection_n0'];J1=result['charged_injection_n1']
                value=-J1.conj().T@G1@Z@G0@J0
                arrays[prefix+'charged_forward_'+name]=value
                arrays[prefix+'charged_reverse_'+name]=-J0.conj().T@G0@Zr@G1@J1
                component_outputs[name]=value
            sum_difference=sum(component_outputs.values())-result['forward_charged_current_insertion']
            arrays[prefix+'charged_component_sum_difference']=sum_difference
            record=next(r for r in md['records'] if r['side']==side and r['family']==family)
            left=result['charged_injection_n1'].conj().T@result['external_n1']['Green']
            right=result['external_n0']['Green']@result['charged_injection_n0']
            upper=outward_positive_product_sum([(v,rigorous_frobenius_upper(left),rigorous_frobenius_upper(right))
                for v in record['exact_stored_contracted_kernel_approximation_upper'].values()])
            schur=[]
            for key in ('external_n0','external_n1'):
                r=result[key];scale=np.linalg.norm(r['charged_source_response'])
                schur.append(dict(shell=key,positive_form_minimum_eigenvalue=r['positive_form_minimum_eigenvalue'],
                    neutral_factor_source_leakage_norm=float(np.linalg.norm(r['neutral_factor_source_leakage'])),
                    neutral_response_norm=float(np.linalg.norm(r['neutral_response'])),
                    complete_current_source_response_norm=float(scale),
                    charged_only_omission_norm=float(np.linalg.norm(r['complete_response_difference_from_isolated'])),
                    Schur_full_solve_relative_difference=float(np.linalg.norm(r['Schur_full_solve_difference'])/scale),
                    actual_stored_source_residual_norm=float(np.linalg.norm(r['source_response_residual']))))
            rows.append(dict(side=side,family=family,
                cutoff_probe=record['cutoff_probe'],length=record['length'],lapse=record['lapse'],
                forward_charged_current_norm=float(np.linalg.norm(result['forward_charged_current_insertion'])),
                reverse_charged_current_norm=float(np.linalg.norm(result['reverse_charged_current_insertion'])),
                neutral_open_image_norm=float(np.linalg.norm(result['forward_neutral_image_of_charged_source'])),
                charged_neutral_placement_norms={k:float(np.linalg.norm(v)) for k,v in result['forward_charged_neutral_placements'].items()},
                placement_sum_absolute_difference=float(np.linalg.norm(result['forward_placement_sum_difference'])),
                component_sum_absolute_difference=float(np.linalg.norm(sum_difference)),
                actual_n0_canonical_neutral_leakage_norm=float(np.linalg.norm(result['neutral_n0_canonical_source_leakage'])),
                charged_free_rest_symbol_difference_norm=float(np.linalg.norm(result['charged_free_rest_symbol_difference'])),
                fixed_Y_background_mass_action=result['fixed_Y_background_mass_action'],
                external_current_Greens=schur,
                exact_stored_upstream_kernel_remainder_current_contraction_upper=upper))
        for place in ('forward','reverse'):
            key=place+'_charged_current_insertion'
            arrays[side+'_paired_middle_minus_light_'+key]=family_outputs[1][key]-family_outputs[2][key]
        print(json.dumps(dict(side=side,paired_charged_forward_norm=float(np.linalg.norm(arrays[side+'_paired_middle_minus_light_forward_charged_current_insertion']))),sort_keys=True),flush=True)
    sources=[source_record(p,symbols) for p,symbols in (
        ('src/bhsm/interface/muon_intrinsic_open_current_schur.py',['external_current_schur_application','source_image_external_current_application']),
        ('src/bhsm/interface/muon_magnetic_open_lepton_vertex.py',['charged_dirac_injection']),
        ('src/bhsm/interface/muon_native_dirac_hamiltonian.py',['lepton_current_hilbert_representation']),
    )]
    for p in sources:hashes[p['path']]=p['sha256']
    hashes[Path(__file__).relative_to(ROOT).as_posix()]=sha256(Path(__file__).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in hashes.items()):raise RuntimeError('consumed action changed during current application')
    out.mkdir(parents=True);deterministic_archive(out/'application.npz',arrays)
    result=dict(classification='EVALUATED_COMPLETE_CHARGED_NEUTRAL_EXTERNAL_CURRENT_APPLICATION_OF_TEMPORAL_SOURCE_IMAGE',
        source_records=sources,input_hashes=hashes,records=rows,
        archive=dict(path='application.npz',bytes=(out/'application.npz').stat().st_size,sha256=sha256((out/'application.npz').read_bytes()).hexdigest()),
        current_domain='existing external tent times complete scalar n0 C6 input and scalar n1 C6 output, for each fixed-Y family; no signed spatial Dirac-shell identification',
        current_normalization='phi_h=Y_h/sqrt(2pi²) on dOmega; Haar average one; same canonical chi normalization as frozen source. No additional charge/volume inserted.',
        source_direction='actual three local magnetic directions including solved gauge and H first response; common explicit cutoff probe; internal b² temporal image retained',
        exact_current_identities=['G=P^-1 A^dagger','Pcc_eff=Pcc-Pcn Pnn^-1 Pnc','rhs_c_eff=J^dagger A^dagger J-Pcn Pnn^-1 K^dagger A^dagger J',
            'D=-G1 Sigma G0; its charged current contraction sums all charged/neutral internal placements'],
        Gaussian_statistics_or_native_Sigma_sign_assigned=False,
        overlap_status='No subtraction applied: this projected mixed scalar field kernel is not the matched continuum charged-lepton VP kernel. The open scalar topology shares frozen local H1 only after the same exterior current/pole/domain matching is established, not by equating these finite matrices.',
        reached_external_matching='Actual charged-neutral Schur/source return evaluated. The actual canonical neutral coupling and free-rest-symbol difference are nonzero, so the calibrated free Dirac-symbol Pauli projector is not an action equivalence on this reached kernel.',
        next_action_application='Solve/project the same chronological full charged-neutral Dirac exterior current with its physical pole/residue/domain and analytically matched native quantum mixed factor; do not replace actual neutral return by a chosen free spinor.',
        physical_external_pole_or_LSZ_matching_completed=False,
        Pauli_projection_completed=False,complete_native_quantum_loop=False,
        physical_a_mu=None,physical_g_mu=None,
        error_scope='Outward exact-stored upstream kernel remainder times exact-stored computed current norms only; Schur/Green solve rounding, original eigensystem/action formation, temporal differential complement, quantum/domain/exterior-current and soft matching errors excluded.')
    if result['archive']['bytes']>10*1024**2:raise ValueError('complete current archive exceeds public cap')
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return dict(classification=result['classification'],archive=result['archive'],records=rows)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--source',type=Path,default=Path('artifacts/muon_intrinsic_scalar_temporal_image_20261011/run_1'))
    a=p.parse_args();print(json.dumps(materialize(a.output,source=a.source),sort_keys=True))
