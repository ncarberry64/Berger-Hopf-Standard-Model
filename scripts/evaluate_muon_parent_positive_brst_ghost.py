"""Execute actual positive-ADM FP Green and magnetic source Ward contacts."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_parent_positive_brst_ghost import positive_parent_ghost_application
from bhsm.interface.muon_magnetic_source_mean_load import load_magnetic_reached_mean_inputs
from bhsm.interface.muon_magnetic_open_lepton_vertex import magnetic_open_fields_at_node
from bhsm.interface.muon_parent_maxwell_full_q_application import retained_full_q_angular_space
from evaluate_muon_reached_trace_action import deterministic_archive


def materialize(output):
    out=Path(output);out=out if out.is_absolute() else ROOT/out
    if out.exists():raise FileExistsError('preserve previous applications')
    arrays={};hashes={};records=[];angular=retained_full_q_angular_space(ROOT)
    for side in ('incoming','outgoing'):
        b=load_magnetic_reached_mean_inputs('artifacts/muon_electromagnetic_soft_magnetic_source_20261011/'+side+'_run_1',repository=ROOT)
        hashes.update(b['input_hashes']);f=magnetic_open_fields_at_node(b,b['source']['times'][2]);L=b['receipt']['chronological_response_span']
        r=positive_parent_ghost_application(f['raw_fields'],b['representation'],angular,length=L,
            first_gauge=f['first_gauge'],first_gauge_rate=f['first_gauge_rate'],first_gauge_radial=f['first_gauge_radial'])
        for key,value in r.items():
            if isinstance(value,np.ndarray):arrays[side+'_'+key]=value
        for key in ('first_gauge','first_gauge_rate','first_gauge_radial','raw_fields'):arrays[side+'_'+key]=f[key]
        for key,value in r['ghost_temporal_moments'].items():arrays[side+'_ghost_temporal_moment_'+key]=value
        records.append(dict(side=side,length=L,minimum_FP_eigenvalue=float(r['ghost_eigenvalues'][0]),
            maximum_FP_eigenvalue=float(r['ghost_eigenvalues'][-1]),inverse_residual=r['inverse_residual'],
            covariant_curvature_image_relative_error=r['covariant_curvature_image_relative_error'],
            source_YM_gauge_Hessian_norm=float(np.linalg.norm(r['source_gauge_hessian_against_all_ghost_gradients'])),
            source_YM_Euler_contact_norm=float(np.linalg.norm(r['source_gauge_Euler_contact'])),
            source_YM_Ward_residual_norm=float(np.linalg.norm(r['source_offshell_Ward_residual'])),
            coefficient_reference_scope=r['coefficient_reference_scope']))
        print(json.dumps(dict(stage='actual_positive_ADM_FP_and_offshell_Ward',**records[-1])),flush=True)
    sources=('src/bhsm/interface/muon_parent_positive_brst_ghost.py',
        'src/bhsm/interface/muon_parent_maxwell_geometry_weak.py',
        'src/bhsm/interface/muon_parent_maxwell_corrected_retarded.py',
        'src/bhsm/interface/muon_parent_maxwell_full_weak.py',
        'src/bhsm/interface/muon_moving_geometric_action.py',
        'src/bhsm/interface/muon_parent_retarded_hypercharge.py',
        'src/bhsm/interface/muon_magnetic_open_lepton_vertex.py',
        'src/bhsm/interface/aether_event_shell_joint_operator_v15_73.py',
        'src/bhsm/interface/aether_nonabelian_derham_response_v16_04.py',
        'src/bhsm/interface/aether_common_source_frechet_response_v15_99.py',
        Path(__file__).relative_to(ROOT).as_posix())
    for name in sources:hashes[name]=sha256((ROOT/name).read_bytes()).hexdigest()
    out.mkdir(parents=True);deterministic_archive(out/'application.npz',arrays)
    if (out/'application.npz').stat().st_size>10*1024**2:raise ValueError('lossless archive exceeds publication limit')
    if any(sha256((ROOT/n).read_bytes()).hexdigest()!=h for n,h in hashes.items()):raise RuntimeError('consumed source changed')
    result=dict(classification='EVALUATED_ACTUAL_POSITIVE_ADM_PARENT_FP_GREEN_AND_MAGNETIC_WARD_CONTACT',
        numerical_sha256=sha256((out/'application.npz').read_bytes()).hexdigest(),
        numerical_bytes=(out/'application.npz').stat().st_size,input_hashes=hashes,records=records,
        reference_metric='N²dt²+(C_rho J)²(drho+beta dt)²+R²dOmega3²',
        reference_measure='weighted mu=d R^4; mu*g^{-1}: R²[[e,-e beta],[-e beta,r+e beta²]], angular d R²',
        temporal_ghost_basis=['u²(1-u)²','(2u-1)u²(1-u)²'],
        temporal_domain='smooth H2 ghost bubble and complete covariant gradient images; value and first rate zero at both finite faces',
        ghost_coordinates='parity2 x radial2 x unit-Tr16 adjoint4 x complete real n1/n3 harmonics20=320',
        gauge_variation_sign='deltaA=D_A eta; in scalar sector the paired orbit is deltaH=-T(eta)H',
        actual_temporal_radial_and_angular_gradient_images_retained=True,
        source_YM_offshell_Euler_contact_retained=True,scalar_Ward_rows_not_substituted_by_YM_rows=True,
        source_coefficients='actual all-eight magnetic first gauge/rate/radial fields; active3 and probe-defined padding5',
        direct_open_lepton_ghost_vertex=0,
        zero_vertex_provenance='cbar M_FP[A,H] c has no Psi derivative at fixed bosons and zero classical ghosts; no removal from graded response or gauge Green',
        Lorentz_Hessian_squared_or_periodic_ghost_substituted=False,
        full_one_form_gauge_fixed_inverse_completed=False,
        physical_Wick_relative_BRST_quotient_or_LSZ_completed=False,
        complete_graded_quantum_Sigma_or_Pauli_assigned=False,
        physical_a_mu=None,physical_g_mu=None,
        error_scope='finite positive-ADM coefficient-cell germ and binary64 Green/Ward application; inverse residual and covariant-image/metric checks are diagnostics, not outward assembly/continuous-domain or physical observable enclosures')
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
    return dict(classification=result['classification'],numerical_sha256=result['numerical_sha256'],records=records)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();print(json.dumps(materialize(a.output),sort_keys=True))
