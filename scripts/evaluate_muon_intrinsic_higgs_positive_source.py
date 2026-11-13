"""Evaluate actual magnetic Higgs-Jacobi images and shared-cutoff contraction."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_intrinsic_higgs_positive_source import intrinsic_higgs_positive_source_application
from bhsm.interface.muon_intrinsic_higgs_positive_green import intrinsic_higgs_mixed_green_application
from bhsm.interface.muon_magnetic_source_mean_load import load_magnetic_reached_mean_inputs
from bhsm.interface.muon_magnetic_open_lepton_vertex import magnetic_open_fields_at_node
from bhsm.interface.muon_parent_maxwell_full_q_application import retained_full_q_angular_space
from evaluate_muon_reached_trace_action import deterministic_archive


def materialize(output,cutoff):
    out=Path(output);out=out if out.is_absolute() else ROOT/out
    if out.exists():raise FileExistsError('preserve previous applications')
    c=float(cutoff)
    if not np.isfinite(c) or c<0:raise ValueError('one explicit nonnegative common birth probe required')
    angular=retained_full_q_angular_space(ROOT);arrays={};hashes={};rows=[]
    for side in ('incoming','outgoing'):
        b=load_magnetic_reached_mean_inputs('artifacts/muon_electromagnetic_soft_magnetic_source_20261011/'+side+'_run_1',repository=ROOT)
        hashes.update(b['input_hashes']);fields=magnetic_open_fields_at_node(b,b['source']['times'][2])
        rep=dict(b['representation'],native_positive_nu_squared_action=b['receipt']['action_parameters']['nu_squared_action'])
        L=b['receipt']['chronological_response_span']
        r=intrinsic_higgs_positive_source_application(fields['raw_fields'],rep,angular,length=L,
            first_wall_gauge=fields['first_wall_gauge'],first_H=fields['first_H'])
        mixed=intrinsic_higgs_mixed_green_application(fields['raw_fields'],rep,angular,length=L,cutoff=c,order=48)
        for key in ('positive_H_odd','positive_H_even','delta_positive_H_even_odd',
            'delta_temporal_connection_even_odd','delta_spatial_even_odd','delta_potential_even_odd',
            'delta_action_Hessian_even_odd','gaunt_even_odd_source',
            'odd_derivative_matrices','even_derivative_matrices','source_derivative_matrices',
            'source_wall_gauge','source_H','scalar_product_image_residual','background_real_H'):
            arrays[side+'_'+key]=r[key]
        arrays[side+'_action_Gram_scalar']=np.array(r['action_Gram_scalar'])
        arrays[side+'_raw_fields']=fields['raw_fields']
        arrays[side+'_shared_cutoff_mixed_Green']=mixed['mixed_Green_contraction']
        rows.append(dict(side=side,length=L,common_cutoff_probe=c,
            action_Gram_scalar=r['action_Gram_scalar'],scalar_matching=r['scalar_matching'],
            even_harmonic_labels=r['even_harmonic_labels'],odd_harmonic_labels=r['odd_harmonic_labels'],
            source_harmonic_labels=r['source_harmonic_labels'],source_n3_exactly_zero=r['source_n3_exactly_zero'],
            product_image_residual_max=float(np.max(r['scalar_product_image_residual'])),
            source_variation_norms=[float(np.linalg.norm(d)) for d in r['delta_positive_H_even_odd']],
            potential_variation_norms=[float(np.linalg.norm(d)) for d in r['delta_potential_even_odd']],
            shared_cutoff_mixed_Green_norm=float(np.linalg.norm(mixed['mixed_Green_contraction'])),
            source_projection_scope=r['source_temporal_scope']))
        print(json.dumps(dict(stage='actual_positive_scalar_source_image',**rows[-1])),flush=True)
    sources=('src/bhsm/interface/muon_intrinsic_higgs_positive_source.py',
        'src/bhsm/interface/muon_intrinsic_higgs_positive_green.py',
        'src/bhsm/interface/muon_magnetic_open_lepton_vertex.py',
        'src/bhsm/interface/muon_intrinsic_scalar_discretization.py',
        'src/bhsm/interface/muon_parent_maxwell_full_q_application.py',
        'src/bhsm/interface/muon_parent_maxwell_corrected_retarded.py',
        'src/bhsm/interface/muon_primal_trace_enriched_lepton_operator.py',
        Path(__file__).relative_to(ROOT).as_posix())
    for name in sources:hashes[name]=sha256((ROOT/name).read_bytes()).hexdigest()
    out.mkdir(parents=True);deterministic_archive(out/'application.npz',arrays)
    if (out/'application.npz').stat().st_size>10*1024**2:raise ValueError('lossless archive exceeds publication limit')
    if any(sha256((ROOT/n).read_bytes()).hexdigest()!=h for n,h in hashes.items()):raise RuntimeError('consumed source changed')
    result=dict(classification='EVALUATED_MAGNETIC_INTRINSIC_HIGGS_POSITIVE_SOURCE_COMPLETE_EVEN_IMAGE',
        numerical_sha256=sha256((out/'application.npz').read_bytes()).hexdigest(),
        numerical_bytes=(out/'application.npz').stat().st_size,input_hashes=hashes,records=rows,
        common_child_plus_birth_cutoff_probe=c,cutoff_physically_selected=False,
        active_source_indices=[0,1,2],inactive_source_indices=[3,4,5,6,7],
        source_support_reduction='bit-exact zero n3 directions permit even n0/n2/n4; no threshold deletion',
        both_derivative_placements_and_potential_source_retained=True,
        source_odd_geometry_response_included=False,
        temporal_derivative_projection='int b² bprime=0 is the same tent source moment only; no full differential image cancellation',
        scalar_pairing='real2Re; unit Haar timesV once; intrinsic S4/V² in common cap action',
        positive_block_is_complete_quantum_superdeterminant=False,
        complete_native_P_A_ghost_EC_HS_or_external_LSZ_or_Pauli=False,
        physical_a_mu=None,physical_g_mu=None,
        error_scope='binary64 coefficient-cell variation, exact harmonic product rule with quadrature diagnostic; no outward upstream/continuum or physical matching enclosure')
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
    return dict(classification=result['classification'],numerical_sha256=result['numerical_sha256'],records=rows)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--common-cutoff',type=float,required=True)
    a=p.parse_args();print(json.dumps(materialize(a.output,a.common_cutoff),sort_keys=True))
