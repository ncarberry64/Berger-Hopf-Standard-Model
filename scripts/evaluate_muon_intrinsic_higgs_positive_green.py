"""Execute reached intrinsic-Higgs Jacobi and mixed open-field Green blocks."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_intrinsic_higgs_positive_green import intrinsic_higgs_mixed_green_application
from bhsm.interface.muon_magnetic_source_mean_load import load_magnetic_reached_mean_inputs
from bhsm.interface.muon_magnetic_open_lepton_vertex import magnetic_open_fields_at_node
from bhsm.interface.muon_parent_maxwell_full_q_application import retained_full_q_angular_space
from evaluate_muon_reached_trace_action import deterministic_archive


def materialize(output):
    out=Path(output);out=out if out.is_absolute() else ROOT/out
    if out.exists():raise FileExistsError('preserve previous finite applications')
    angular=retained_full_q_angular_space(ROOT);arrays={};hashes={};rows=[]
    for side in ('incoming','outgoing'):
        b=load_magnetic_reached_mean_inputs('artifacts/muon_electromagnetic_soft_magnetic_source_20261011/'+side+'_run_1',repository=ROOT)
        hashes.update(b['input_hashes']);fields=magnetic_open_fields_at_node(b,b['source']['times'][2])
        rep=dict(b['representation'],native_positive_nu_squared_action=b['receipt']['action_parameters']['nu_squared_action'])
        L=b['receipt']['chronological_response_span']
        from bhsm.interface.muon_primal_trace_enriched_lepton_operator import primal_trace_enriched_lepton_operator
        op=primal_trace_enriched_lepton_operator(fields['raw_fields'],rep)
        c=(op['N']*L)**2/12 # existing shared numerical c=q/gap, q1 probe.
        r=intrinsic_higgs_mixed_green_application(fields['raw_fields'],rep,angular,length=L,cutoff=c,order=24)
        r2=intrinsic_higgs_mixed_green_application(fields['raw_fields'],rep,angular,length=L,cutoff=c,order=48)
        for key in ('fermion_positive_operator','fermion_factor','fermion_eigenvalues','mixed_vertices','mixed_Green_contraction','unregulated_mixed_Green_contraction'):
            arrays[side+'_'+key]=r[key]
        for key in ('operator','action_Hessian','action_Gram','Green','eigenvalues','eigenvectors','temporal','time_connection','spatial','potential'):
            arrays[side+'_Higgs_'+key]=r['Higgs'][key]
        arrays[side+'_mixed_Green_order48']=r2['mixed_Green_contraction']
        rows.append(dict(side=side,cutoff_probe=c,length=L,
            Higgs_minimum_eigenvalue=float(r['Higgs']['eigenvalues'][0]),
            scalar_action_Gram=r['Higgs']['action_Gram_scalar'],scalar_matching=r['Higgs']['scalar_matching'],
            inverse_residual=r['Higgs']['inverse_residual'],
            mixed_Green_norm=float(np.linalg.norm(r['mixed_Green_contraction'])),
            unregulated_mixed_Green_norm=float(np.linalg.norm(r['unregulated_mixed_Green_contraction'])),
            divided_difference_order24_48_difference=float(np.linalg.norm(r['mixed_Green_contraction']-r2['mixed_Green_contraction'])),
            quantum_statistics_or_complete_selfenergy_sign_assigned=False))
        print(json.dumps(dict(stage='positive_Higgs_and_fixedY_mixed_Green',**rows[-1])),flush=True)
    for name in ('src/bhsm/interface/muon_intrinsic_higgs_positive_green.py','src/bhsm/interface/muon_magnetic_open_lepton_vertex.py',
                 'src/bhsm/interface/muon_parent_maxwell_corrected_retarded.py','src/bhsm/interface/muon_current_source_motion_cubic.py',
                 'src/bhsm/interface/muon_primal_trace_enriched_lepton_operator.py',Path(__file__).relative_to(ROOT).as_posix()):
        hashes[name]=sha256((ROOT/name).read_bytes()).hexdigest()
    out.mkdir(parents=True);deterministic_archive(out/'application.npz',arrays)
    if (out/'application.npz').stat().st_size>10*1024**2:raise ValueError('lossless archive exceeds publication limit')
    if any(sha256((ROOT/n).read_bytes()).hexdigest()!=h for n,h in hashes.items()):raise RuntimeError('consumed action changed')
    result=dict(classification='EVALUATED_SAME_CELL_INTRINSIC_HIGGS_POSITIVE_JACOBI_MIXED_GREEN',
        numerical_sha256=sha256((out/'application.npz').read_bytes()).hexdigest(),numerical_bytes=(out/'application.npz').stat().st_size,
        input_hashes=hashes,records=rows,actual_H_and_all_material_gauge_fields_used=True,
        temporal_domain='existing finite native Dirichlet tent, constant actual solved midpoint coefficients',
        complete_scalar_n1_n3_real80_and_full_lepton18_used=True,EC_HS_auxiliary_substituted=False,
        mixed_contraction='sum B_Ha dagger L_c(P_F,p_Ha) A_F dagger B_Ha / Gram_H; B temporal moment3/4',
        regulator_kernel='integral_{u,v>=0,u+v>=c} exp(-uP_F-vP_H); common total cutoff, no separate double cutoff',
        intrinsic_scalar_pairing='real2Re; raw intrinsic S4/V² in cap action; V=2pi²',
        lepton_current='chi_hat=R4^(3/2)psi/V; no extra1/V² source insertion',
        no_c_number_fermion_or_CAR_state_selected=True,positive_field_block_is_positive_Gamma_claim=False,
        complete_graded_P_A_ghost_EC_HS_loop_or_statistics=False,
        physical_external_photon_derivative_LSZ_or_Pauli_completed=False,
        physical_a_mu=None,physical_g_mu=None,
        error_scope='finite binary64 coefficient-cell operator/inverse and24/48 quadrature comparison only; no outward upstream, continuous domain, physical cutoff or LSZ enclosure')
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
    return dict(classification=result['classification'],numerical_sha256=result['numerical_sha256'],records=rows)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();print(json.dumps(materialize(a.output),sort_keys=True))
