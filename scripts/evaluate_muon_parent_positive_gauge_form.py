"""Execute the actual augmented one-form form, finite Lorenz fixing and Green."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_parent_positive_gauge_form import positive_parent_gauge_application
from bhsm.interface.muon_magnetic_source_mean_load import load_magnetic_reached_mean_inputs
from bhsm.interface.muon_magnetic_open_lepton_vertex import magnetic_open_fields_at_node
from bhsm.interface.muon_parent_maxwell_full_q_application import retained_full_q_angular_space
from evaluate_muon_reached_trace_action import deterministic_archive


def materialize(output):
    out=Path(output);out=out if out.is_absolute() else ROOT/out
    if out.exists():raise FileExistsError('preserve previous applications')
    out.mkdir(parents=True);hashes={};records=[];files={};angular=retained_full_q_angular_space(ROOT)
    for side in ('incoming','outgoing'):
        b=load_magnetic_reached_mean_inputs('artifacts/muon_electromagnetic_soft_magnetic_source_20261011/'+side+'_run_1',repository=ROOT)
        hashes.update(b['input_hashes']);f=magnetic_open_fields_at_node(b,b['source']['times'][2]);L=b['receipt']['chronological_response_span']
        r=positive_parent_gauge_application(f['raw_fields'],b['representation'],angular,length=L)
        # Keep every matrix. Separate deterministic lossless archives keep
        # the existing publication-size threshold without deleting entries.
        groups={'action':{},'hilbert':{},'green':{}}
        action={'one_form_YM_Hessian','one_form_curvature_contact','gauge_fixed_one_form_Hessian'}
        green={'normalized_gauge_fixed_operator','gauge_fixed_Green','normalized_gauge_fixed_Green','projected_wall_one_form_Green','gauge_fixed_eigenvalues'}
        for key,value in r.items():
            if isinstance(value,np.ndarray):groups['action' if key in action else 'green' if key in green else 'hilbert'][key]=value
        groups['hilbert']['raw_fields']=f['raw_fields'];groups['hilbert']['ghost_angular_derivative_matrices']=angular['derivative_matrices']
        for name,arrays in groups.items():
            path=out/(side+'_'+name+'.npz');deterministic_archive(path,arrays)
            if path.stat().st_size>10*1024**2:raise ValueError('lossless '+name+' archive exceeds publication limit')
            files[path.name]=dict(sha256=sha256(path.read_bytes()).hexdigest(),bytes=path.stat().st_size,keys=sorted(arrays))
        records.append(dict(side=side,length=L,coordinates=1120,field_coordinates=800,complete_ghost_gradient_images=320,
            minimum_gauge_fixed_eigenvalue=float(r['gauge_fixed_eigenvalues'][0]),
            maximum_gauge_fixed_eigenvalue=float(r['gauge_fixed_eigenvalues'][-1]),
            actual_finite_gauge_fixed_form_positive=r['finite_gauge_fixed_form_positive'],
            ghost_image_FP_relative_error=r['ghost_image_FP_relative_error'],
            curvature_contact_norm=float(np.linalg.norm(r['one_form_curvature_contact'])),
            inverse_original_coordinate_residual=r['inverse_residual'],
            inverse_relative_backward_error=float(r['inverse_relative_backward_error']),
            inverse_normalized_residual=r['normalized_inverse_residual'],
            exact_stored_normalized_inverse_majorant=r['stored_normalized_inverse_majorant'],
            projected_wall_Green_norm=float(np.linalg.norm(r['projected_wall_one_form_Green'])),
            single_tent_source_product_residual_squared=L/80,
            source_product_fraction_not_in_single_tent=1/16))
        print(json.dumps(dict(stage='actual_full_one_form_Lorenz_Green',**records[-1]),sort_keys=True),flush=True)
    for p in ('src/bhsm/interface/muon_parent_positive_gauge_form.py',
        'src/bhsm/interface/muon_parent_positive_brst_ghost.py',
        'src/bhsm/interface/muon_parent_maxwell_geometry_weak.py',
        'src/bhsm/interface/muon_parent_maxwell_full_weak.py',
        'src/bhsm/interface/muon_parent_maxwell_corrected_retarded.py',
        'src/bhsm/interface/muon_magnetic_open_lepton_vertex.py',
        'src/bhsm/interface/muon_parent_retarded_hypercharge.py',
        'src/bhsm/interface/aether_event_shell_joint_operator_v15_73.py',
        'src/bhsm/interface/aether_nonabelian_derham_response_v16_04.py',
        'src/bhsm/interface/aether_common_source_frechet_response_v15_99.py',
        Path(__file__).relative_to(ROOT).as_posix()):hashes[p]=sha256((ROOT/p).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in hashes.items()):raise RuntimeError('consumed source changed')
    result=dict(classification='EVALUATED_ACTUAL_POSITIVE_ADM_AUGMENTED_PARENT_ONE_FORM_LORENZ_GREEN',
        input_hashes=hashes,numerical_files=files,records=records,
        reference_metric='N²dt²+(C_rho J)²(drho+beta dt)²+R²dOmega3²',
        reference_measure='weighted mu=d R^4; mu*g^{-1}: R²[[e,-e beta],[-e beta,r+e beta²]], angular d R²',
        field_coordinates='tent x radial2 x field5 x unit-Tr16 adjoint4 x real n1/n3 harmonic20=800',
        augmented_coordinates='320 exact D_A eta images (H2 smooth ghosts); total1120',
        temporal_profiles=['tent','tent_rate','u²(1-u)²','rate_u²(1-u)²','(2u-1)u²(1-u)²','rate_(2u-1)u²(1-u)²'],
        gauge_fixing='B^T Gram0^-1 B, B=<D_A eta,a>_1; finite weak Lorenz fixing on same320 ghosts',
        curvature_contact_and_all_temporal_radial_components_retained=True,
        same_ghost_gradient_images_fitted_or_dropped=False,
        boundary_value_maps_and_temporal_source_product_complement_exported=True,
        scalar_intrinsic_M4_gauge_boundary_mass_and_mixed_rows_included=False,
        EC_HS_auxiliary_replaced_by_intrinsic_Higgs=False,
        positive_Green_reference='actual midpoint coefficient-cell values/connection first jets held as germ; not varying full-history quantum operator',
        native_heat_statistical_grading_or_physical_Wick_relative_BRST_quotient_completed=False,
        physical_external_LSZ_or_soft_Pauli_completed=False,
        physical_a_mu=None,physical_g_mu=None,
        error_scope='binary64 literal form/Gram and direct normalized solve; IEEE guarded Neumann bounds cover exact stored normalized matrix only. Original-coordinate residual, normalization/field assembly, upstream trajectory, continuum mesh, Wick/domain and observable matching are separate. No anomaly bound.')
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return dict(classification=result['classification'],records=records,numerical_files=files)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();print(json.dumps(materialize(a.output),sort_keys=True))
