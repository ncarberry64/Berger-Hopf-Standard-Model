"""Execute matched constant-input soft columns on the SAME image action."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_intrinsic_soft_current_columns import soft_current_factor_data,soft_current_tangent_application
from bhsm.interface.muon_intrinsic_soft_constant_columns import constant_input_image_data
from bhsm.interface.muon_magnetic_mixed_green import family_fiber_indices
from bhsm.interface.muon_native_dirac_hamiltonian import lepton_current_hilbert_representation
from bhsm.interface.muon_magnetic_source_mean_load import load_magnetic_reached_mean_inputs
from bhsm.interface.muon_magnetic_open_lepton_vertex import magnetic_open_fields_at_node
from bhsm.interface.muon_primal_cell_reached_source_heat import actual_reached_cell_vertices
from evaluate_muon_reached_trace_action import deterministic_archive


def materialize(output,source):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve previous source applications')
    folder=ROOT/source;raw=(folder/'result.json').read_bytes();md=json.loads(raw);hashes=dict(md['input_hashes'])
    hashes[(folder/'result.json').relative_to(ROOT).as_posix()]=sha256(raw).hexdigest()
    consumed={}
    for name,info in md['array_archives'].items():
        p=folder/name;b=p.read_bytes()
        if len(b)!=info['bytes']or sha256(b).hexdigest()!=info['sha256']:raise ValueError('consumed archive changed '+name)
        hashes[p.relative_to(ROOT).as_posix()]=info['sha256']
        with np.load(p,allow_pickle=False)as z:consumed[name]={k:z[k].copy()for k in z.files}
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in hashes.items()):raise ValueError('pinned action input changed')
    ss=consumed['scalar_sources.npz'];arrays={};rows=[];familyresults={}
    for side in ('incoming','outgoing'):
        bound=load_magnetic_reached_mean_inputs('artifacts/muon_electromagnetic_soft_magnetic_source_20261011/'+side+'_run_1',repository=ROOT)
        fields=magnetic_open_fields_at_node(bound,bound['source']['times'][2])
        for key in ('raw_fields','first_wall_gauge','first_H'):
            if not np.array_equal(fields[key],ss[side+'_'+key]):raise ValueError('same-background actual field binding mismatch '+key)
        rep=bound['representation'];v=actual_reached_cell_vertices(fields,rep);op=v['operator']
        row=next(r for r in md['records']if r['side']==side)
        scalar={k:ss[side+'_'+k]for k in ('positive_H_odd','positive_H_even','delta_positive_H_even_odd')};scalar['action_Gram_scalar']=row['action_Gram_scalar']
        for family in range(3):
            ids=family_fiber_indices(family);prefix=side+'_family_'+str(family)+'_'
            d=soft_current_factor_data(W=op['W'][np.ix_(ids,ids)],Omega_tau=op['Omega_tau'][np.ix_(ids,ids)],
                alpha=lepton_current_hilbert_representation()['alpha'][:,ids][:,:,ids],R4=op['R4'],lapse=op['N'],length=row['length'],
                mass_vertices=ss[prefix+'bare_scalar_mass_vertices'],magnetic_vertices=v['vertex_n0_to_angular'][:3,:4][:,:,ids][:,:,:,ids])
            old={k[len(prefix):]:value for k,value in consumed[side+'_family_'+str(family)+'_fermion_operators.npz'].items()}
            # Exact shell restriction from the same coefficient producer.
            defects={par:float(np.linalg.norm(d['A_'+par][:len(old['A_'+par]),:len(old['A_'+par])]-old['A_'+par]))for par in ('odd','even')}
            if max(defects.values())>1e-12:raise ValueError('new image factor is not the inherited operator restriction')
            d=constant_input_image_data(d,ss[prefix+'bare_scalar_mass_vertices'])
            a=soft_current_tangent_application(d,scalar,cutoff=md['common_cutoff_probe']);familyresults[side,family]=a
            for place in ('forward','reverse'):
                for name,value in a[place].items():arrays[prefix+place+'_'+name]=value
            rows.append(dict(side=side,family=family,R4=op['R4'],lapse=op['N'],length=row['length'],
                coefficient_restriction_defects=defects,angular_product_residuals=d['angular']['product_residuals'],
                forward_component_norms={k:float(np.linalg.norm(x))for k,x in a['forward'].items()},
                reverse_component_norms={k:float(np.linalg.norm(x))for k,x in a['reverse'].items()},
                kernel_approximation_contracted_upper=a['kernel_approximation_contracted_upper'],kernel_methods=a['kernel_methods']))
            print(json.dumps(rows[-1],sort_keys=True),flush=True)
        for place in ('forward','reverse'):
            for key in familyresults[side,1][place]:arrays[side+'_paired_middle_minus_light_'+place+'_'+key]=familyresults[side,1][place][key]-familyresults[side,2][place][key]
    paths=['src/bhsm/interface/muon_intrinsic_soft_constant_columns.py','src/bhsm/interface/muon_intrinsic_soft_current_columns.py','src/bhsm/interface/muon_intrinsic_scalar_temporal_image.py','tests/test_muon_intrinsic_soft_current_columns.py',Path(__file__).relative_to(ROOT).as_posix()]
    for p in paths:hashes[p]=sha256((ROOT/p).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in hashes.items()):raise RuntimeError('consumed input changed during application')
    out.mkdir(parents=True);deterministic_archive(out/'application.npz',arrays)
    info=dict(path='application.npz',bytes=(out/'application.npz').stat().st_size,sha256=sha256((out/'application.npz').read_bytes()).hexdigest())
    if info['bytes']>10*1024**2:raise ValueError('lossless source columns exceed publication cap')
    result=dict(classification='EVALUATED_MATCHED_IMAGE_ACTION_CONSTANT_INPUT_SOFT_COLUMNS',archive=info,input_hashes=hashes,records=rows,
        common_cutoff_probe=md['common_cutoff_probe'],all_three_fixed_Y_families=True,
        incoming_domain='constant scalar n0 tensor complete C6',
        outgoing_domain='complete scalar n1 tensor C6; source magnetic axes retained',
        starting_Higgs_domain='same pinned real Hodd80 plus the already evaluated Heven140 source-image block; both unchanged blocks and their mixed first-source images are consumed; no differential starting-loop complement assigned zero',
        temporal_domain='same coefficient cell, tent b, exact internal source b² in span(b,b²)',
        scalar_image_placement_extension='both Heven-left/Hodd-right and Hodd-left/Heven-right are differentiated; old constant-input PH term is one explicitly preserved source-directed subset',
        both_PF_squares_and_numerator_contact_retained=True,Gaussian_quantum_statistics_sign_applied=False,
        physical_cutoff_or_native_Pauli_selected=False,physical_a_mu=None,physical_g_mu=None,
        error_scope='outward exact-stored kernel approximation and norm products only; angular/assembly/eigenvalue/contraction rounding, differential complements, adopted native completion, pole/overlap/soft normalization and total observable error excluded')
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(classification=result['classification'],archive=info),sort_keys=True))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--source',type=Path,default=Path('artifacts/muon_magnetic_mixed_green_20261011/run_3'))
    a=p.parse_args();materialize(a.output,a.source)
