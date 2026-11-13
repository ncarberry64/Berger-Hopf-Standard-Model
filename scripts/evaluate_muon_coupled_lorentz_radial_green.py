"""Evaluate original radial/wall Green, local poles and overlap contacts."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_coupled_lorentz_radial_green import (coupled_radial_trace_application,
    coupled_radial_pole_application,radial_section_overlap_application)
from bhsm.interface.muon_static_coupled_charged_current import static_coupled_charged_current
from bhsm.interface.muon_calibrated_local_pauli import fixed_yukawa_higgs_pauli
from bhsm.interface.muon_geodesic_normal_current import local_radial_higgs_charge_vertices
from evaluate_muon_reached_trace_action import deterministic_archive


def encode(x):
    if isinstance(x,np.ndarray):return encode(x.item())if x.ndim==0 else encode(x.tolist())
    if isinstance(x,complex):return dict(real=x.real,imag=x.imag)
    if isinstance(x,dict):return {k:encode(v)for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [encode(v)for v in x]
    if isinstance(x,np.generic):return x.item()
    return x


def materialize(output):
    out=Path(output);out=out if out.is_absolute()else ROOT/out
    if out.exists():raise FileExistsError('preserve original coupled radial applications')
    folder=ROOT/'artifacts/muon_coupled_lorentz_field_symbol_20261011/run_1'
    md=json.loads((folder/'result.json').read_bytes());refs=dict(md['input_hashes'])
    for name in('result.json','application.npz'):
        p=folder/name;h=sha256(p.read_bytes()).hexdigest()
        if name=='application.npz' and h!=md['archive']['sha256']:raise ValueError('original full signed field archive required')
        refs[p.relative_to(ROOT).as_posix()]=h
    if md['classification']!='EVALUATED_ORIGINAL_COUPLED_CAP_RADIAL_FIELD_FREQUENCY_APPLICATION':raise ValueError('original coupled action producer required')
    config_path=ROOT/'artifacts/muon_calibrated_pauli_20261009/inputs.json'
    config=json.loads(config_path.read_bytes());values=config['selected_consumer_values']
    calibrated=fixed_yukawa_higgs_pauli(muon_mass_GeV=values['m_mu_GeV']['value'],higgs_mass_GeV=values['m_h_GeV']['value'])
    refs[config_path.relative_to(ROOT).as_posix()]=sha256(config_path.read_bytes()).hexdigest()
    pending=[];records=[]
    frequencies=np.array([0,.25,.5,1,.5j,1j,2j],complex)
    with np.load(folder/'application.npz',allow_pickle=False)as archive:
        for record in md['records']:
            side=record['side'];N=record['lapse'];R=record['radius']
            data=[archive[side+'_'+k].copy()for k in('proper_frequency_coefficients','field_quotient_lift','joint_trace_map','scalar_radial_source','central_radial_frame_rows')]
            raw=archive[side+'_raw_fields'].copy();hr=raw[-8:-4];H=hr[:2]+1j*hr[2:]
            zero=coupled_radial_trace_application(*data,frequency=0)
            pole=coupled_radial_pole_application(*data)
            pending.append((side+'_poles.npz',{k:v for k,v in pole.items()if isinstance(v,np.ndarray)}))
            order=np.argsort(abs(pole['canonical_radial_squared_pole_weights']))[::-1]
            records.append(dict(side=side,kind='all_finite_local_poles',finite_pole_count=pole['finite_pole_count'],
                infinite_pole_count=pole['infinite_pole_count'],largest_radial_poles=pole['local_poles'][order[:8]],
                largest_radial_squared_pole_weights=pole['canonical_radial_squared_pole_weights'][order[:8]],
                max_polynomial_relative_residual=float(max(np.max(pole['right_polynomial_relative_residual']),np.max(pole['left_polynomial_relative_residual']))),
                max_radial_modal_minus_direct=float(np.max(abs(pole['radial_modal_minus_direct']))),
                unstable_modes_and_small_residues_deleted=False,physical_pole_selected=False))
            for i,z in enumerate(frequencies):
                green=zero if i==0 else coupled_radial_trace_application(*data,frequency=z)
                overlap=radial_section_overlap_application(data[0],data[3],zero,green)
                arrays={k:v for k,v in green.items()if isinstance(v,np.ndarray)}
                for k,v in green.items():
                    if isinstance(v,(complex,np.generic)):arrays[k]=np.asarray(v)
                arrays.update({k:np.asarray(v)for k,v in overlap.items()if isinstance(v,(np.ndarray,complex,np.generic))})
                arrays.update(proper_frequency_coefficients=data[0],field_quotient_lift=data[1],joint_trace_map=data[2],
                    scalar_radial_tangent=data[3],central_radial_frame_rows=data[4],raw_fields=raw)
                pending.append((f'{side}_frequency_{i}.npz',arrays))
                records.append(dict(side=side,kind='coupled_source_Green',frequency=z,
                    canonical_radial_Green=green['canonical_radial_Green'],
                    canonical_radial_inverse=green['canonical_radial_inverse'],
                    canonical_radial_inverse_frequency_derivative=green['canonical_radial_inverse_frequency_derivative'],
                    scalar_radial_restricted_quadratic_coefficient=green['scalar_radial_restricted_quadratic_coefficient'],
                    radial_gauge_wall_return_norm=float(np.linalg.norm(green['radial_to_gauge_wall_Green'])),
                    quotient_relative_residual=float(np.linalg.norm(green['quotient_equation_residual'])/np.linalg.norm(green['joint_source_matrix'])),
                    resolved_original_relative_residual=float(np.linalg.norm(green['reaction_resolved_original_residual'])/np.linalg.norm(green['joint_source_matrix'])),
                    Schur_full_relative_difference=float(np.linalg.norm(green['Schur_full_response_difference'])/np.linalg.norm(green['full_field_response'])),
                    weak_matrix_condition_number=green['weak_matrix_condition_number'],
                    static_inverse_matching_contact=overlap['static_inverse_matching_contact'],
                    kinetic_inverse_matching_contact=overlap['kinetic_inverse_matching_contact'],
                    surviving_nonquadratic_inverse_response=overlap['surviving_nonquadratic_inverse_response']))
            for family in(1,2):
                current=static_coupled_charged_current(zero['joint_wall_Green'],H,radius=R,lapse=N,family=family)
                charge=local_radial_higgs_charge_vertices(H,family=family)
                arrays={k:v for k,v in current.items()if isinstance(v,np.ndarray)}
                arrays.update({k:v for k,v in charge.items()if isinstance(v,np.ndarray)})
                pending.append((f'{side}_family_{family}_static_current.npz',arrays))
                records.append(dict(side=side,family=family,kind='full24_static_charged_current',
                    VA_coefficient=current['VA_projection_coefficient'],VA_relative_remainder=current['VA_relative_remainder'],
                    gauge_tensor_norm=float(np.linalg.norm(current['gauge_gauge_tensor'])),
                    scalar_tensor_norm=float(np.linalg.norm(current['scalar_scalar_tensor'])),
                    mixed_tensor_norm=float(np.linalg.norm(current['gauge_scalar_tensor'])+np.linalg.norm(current['scalar_gauge_tensor'])),
                    exact_sector_sum_difference_norm=float(np.linalg.norm(current['exact_sector_sum_difference'])),
                    literal_left_adjoint_difference_norm=float(np.linalg.norm(current['literal_left_minus_vertex_adjoint'])),
                    angular_current_integral=current['constant_angular_current_integral'],physical_GF_or_unit_selected=False))
            print(json.dumps(encode(records[-1]),sort_keys=True),flush=True)
    sources=('muon_coupled_lorentz_radial_green','muon_static_coupled_charged_current',
        'muon_magnetic_open_lepton_vertex','muon_calibrated_local_pauli','muon_geodesic_normal_current')
    for name in sources:
        p='src/bhsm/interface/'+name+'.py';refs[p]=sha256((ROOT/p).read_bytes()).hexdigest()
    for p in('tests/test_muon_coupled_lorentz_radial_green.py','tests/test_muon_static_coupled_charged_current.py',Path(__file__).relative_to(ROOT).as_posix()):
        refs[p]=sha256((ROOT/p).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('consumed signed action or local reference changed')
    out.mkdir(parents=True);files={}
    for name,arrays in pending:
        p=out/name;deterministic_archive(p,arrays)
        if p.stat().st_size>10*1024**2:raise ValueError('split complete arrays within publication policy')
        files[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    result=dict(classification='EVALUATED_COUPLED_SIGNED_RADIAL_WALL_GREEN_POLE_AND_LOCAL_MATCHING_APPLICATION',
        input_hashes=refs,array_archives=files,records=records,numerical_frequency_probes=frequencies,
        calibrated_local_Higgs_reference=calibrated,
        overlap_ledger=dict(reference_already_counted_in_calibrated_local_ledger=True,
            new_reference_value_added=False,full_minus_radial_section_Green_evaluated=True,
            static_kinetic_and_nonquadratic_matching_contacts_evaluated=True,
            continuum_Yukawa_redefined_by_finite_mode_pole_residue=False,
            calibrated_measured_pole_reference_subtracted=False,
            actual_consumer='same normalized scalar-current/contour restriction plus action-unit and local counterterm matching before the standard scalar Pauli integral; complex and imaginary local poles retained'),
        pole_scope='original frozen signed cap/radial field polynomial in its inherited four central radial slices; physical BRST, exterior and continuous stationary pole not inferred',
        radial_normalization='deltaH=r*h with r^T r=1/2; canonical radial source d=2r, G_h=4r^T K^-1r. Finite mode residues include the original cap/spatial normalization and do not independently redefine continuum Y.',
        charged_current_scope='all24 original field sources and full H-selected neutral-left/charged fiber; unit L2(dOmega) external constant spinors and literal canonical vertices; full V-A remainder retained',
        physical_overlap_subtracted=False,physical_unit_selected=False,physical_F2=None,physical_a_mu=None,physical_g_mu=None,
        errors='binary64 original signed polynomial solves/companion eigensystem and independent Schur/modal checks; no outward matrix-production, eigensystem, global domain, continuum or physical uncertainty enclosure')
    (out/'result.json').write_text(json.dumps(encode(result),sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return dict(classification=result['classification'],archives=len(files),largest_archive_bytes=max(v['bytes']for v in files.values()),result_sha256=sha256((out/'result.json').read_bytes()).hexdigest())


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    print(json.dumps(materialize(p.parse_args().output),sort_keys=True))
