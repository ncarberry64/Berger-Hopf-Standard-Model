"""Consume completed family responses on one global action without a new inverse."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from evaluate_muon_reached_trace_action import deterministic_archive
from bhsm.interface.muon_native_dirac_hamiltonian import lepton_current_hilbert_representation
from bhsm.interface.muon_chronological_common_y_current import common_y_current_chunk


def materialize(action_folder,current_base,output,*,source_side):
    out=ROOT/output;action=ROOT/action_folder;base=ROOT/current_base
    if out.exists():raise FileExistsError('preserve every common-Y current application')
    refs={}
    def read(path,expected=None):
        p=Path(path);h=sha256(p.read_bytes()).hexdigest()
        if expected is not None and h!=expected:raise ValueError('common action current input changed: '+str(p))
        refs[p.relative_to(ROOT).as_posix()]=h
        if p.suffix=='.json':return json.loads(p.read_bytes())
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    am=read(action/'result.json')
    folders=[base/f'{source_side}_family_{f}_run_1'for f in(1,2)]
    md=[read(p/'result.json')for p in folders]
    if any(m['classification']!='EVALUATED_WHOLE_ORIGINAL_N1_LITERAL_CURRENT_AND_TRANSPOSE_ADJOINT'
           or m['source_side']!=source_side or m['family']!=f or m['current_kind']!='literal'
           for f,m in zip((1,2),md)):
        raise ValueError('completed literal middle/light current on the same source arm required')
    if md[0]['input_hashes']!=md[1]['input_hashes']:
        raise ValueError('family responses do not bind the identical field action/source germ')
    refs.update(md[0]['input_hashes']);refs.update(am['input_hashes'])
    inc=read(action/'original_n1_angular_and_source_incidence.npz',
             am['archives']['original_n1_angular_and_source_incidence.npz']['sha256'])
    y=np.diag(lepton_current_hilbert_representation()['family_Y']);ym,ye=float(y[1]),float(y[2])
    for rel in(Path(__file__).relative_to(ROOT).as_posix(),
                'src/bhsm/interface/muon_chronological_common_y_current.py',
                'tests/test_muon_chronological_common_y_current.py',
                'src/bhsm/interface/muon_native_dirac_hamiltonian.py',
                'scripts/evaluate_muon_reached_trace_action.py'):
        refs[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    names=('original_literal_right_current_source','original_literal_left_transpose_source',
           'original_current_response','original_transpose_current_adjoint')
    totals={k:np.zeros(shape,complex)for k,shape in(
        ('ordered_GG_GH_HG_HH',(4,288,288)),('independent_transpose_ordered_GG_GH_HG_HH',(4,288,288)),
        ('source_current_Y_coefficients',(3,288,288)),('independent_transpose_Y_coefficients',(3,288,288)),
        ('direct_family_current',(2,288,288)),('reconstructed_family_current',(2,288,288)),
        ('source_polynomial_paired_current',(288,288)),('independent_family_binary_difference',(288,288)))}
    records=[];source_defect=0.;source_scale=0.;source_rows=[]
    for s in range(2):
        R,L=(inc[k][s].reshape(168,24,4)for k in
             ('right_current_field_source_lifts','literal_left_current_field_source_lifts'))
        rows=np.flatnonzero(np.any(R[:,20:]!=0,axis=(1,2)))
        if (not np.array_equal(rows,np.flatnonzero(np.any(L[:,20:]!=0,axis=(1,2))))
            or np.count_nonzero(R[rows,:20])or np.count_nonzero(L[rows,:20])
            or len(rows)!=8):
            raise ValueError('literal field incidence does not separate original real-H scalar source rows')
        source_rows.append(rows)
        for start in range(1,1151,8):
            data=[]
            for folder,m in zip(folders,md):
                fields={k:[]for k in names};residuals=[]
                for spin in range(6):
                    name=f'spectator_{s}_external_{spin}_nodes_{start}.npz'
                    a=read(folder/name,m['archives'][name]['sha256'])
                    if not np.array_equal(a['source_column_indices'],np.arange(48*spin,48*(spin+1))):
                        raise ValueError('complete original288 source order required')
                    for k in names:fields[k].append(a[k])
                    residuals.append(a['original_response_residual'])
                b={k:np.concatenate(v,axis=2)for k,v in fields.items()}
                b['original_response_residual']=np.concatenate(residuals,axis=2);data.append(b)
            a=common_y_current_chunk(ym,ye,*data,scalar_rows=rows)
            for k in totals:totals[k]+=a[k]
            source_defect=max(source_defect,a['scalar_unit_source_reconstruction_max'])
            source_scale=max(source_scale,a['scalar_unit_source_scale'])
            dy=ym-ye
            rg=(ym*data[1]['original_response_residual']-ye*data[0]['original_response_residual'])/dy
            rh=(data[0]['original_response_residual']-data[1]['original_response_residual'])/dy
            records.append(dict(spectator=s,original_node_start=start,
                original_node_stop_exclusive=min(start+8,1151),
                inferred_common_gauge_original_row_residual_max=float(np.max(abs(rg))),
                inferred_unit_scalar_original_row_residual_max=float(np.max(abs(rh)))))
            if (start-1)%128==0:print(json.dumps(dict(stage='common_Y_four_source_orders',spectator=s,
                original_nodes_done=min(start+7,1150),scalar_unit_source_defect=source_defect)),flush=True)
    out.mkdir(parents=True);archives={}
    def save(name,data):
        p=out/name;deterministic_archive(p,data)
        if p.stat().st_size>=10*1024**2:raise ArithmeticError('split complete common-Y coefficient matrices')
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    save('common_source_current_coefficients.npz',{k:totals[k]for k in
        ('ordered_GG_GH_HG_HH','source_current_Y_coefficients')})
    save('independent_transpose_current_coefficients.npz',{k:totals[k]for k in
        ('independent_transpose_ordered_GG_GH_HG_HH','independent_transpose_Y_coefficients')})
    save('family_source_current_reconstruction.npz',{k:totals[k]for k in
        ('direct_family_current','reconstructed_family_current','source_polynomial_paired_current',
         'independent_family_binary_difference')})
    save('common_action_source_incidence.npz',dict(fixed_Y_middle=np.array(ym),fixed_Y_light=np.array(ye),
        scalar_rows=np.array(source_rows),current_column_shape=np.array([6,2,6,4]),
        ordered_source_names=np.array(['GG','GH','HG','HH']),
        paired_GG_coefficient=np.zeros((288,288),complex)))
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):
        raise RuntimeError('same common current/action source bytes changed')
    result=dict(classification='EVALUATED_SAME_GLOBAL_COUPLED_CURRENT_GG_GH_HG_HH_WITHOUT_NEW_INVERSE',
        input_hashes=refs,archives=archives,source_side=source_side,
        fixed_Y_middle=ym,fixed_Y_light=ye,original_temporal_nodes=1151,source_cells=384,corner_returns=383,
        scalar_unit_source_reconstruction_max=source_defect,scalar_unit_source_scale=source_scale,
        gauge_source_identical_on_every_original_row=True,
        scalar_source_rows_derived_from_exact_original_wall_incidence=True,
        all_H_Gauss_frame_negative_neutral_and_complex_coupled_current_rows_retained=True,
        independent_transpose_ordered_coefficient_difference_max=float(np.max(abs(
            totals['ordered_GG_GH_HG_HH']-totals['independent_transpose_ordered_GG_GH_HG_HH']))),
        reconstructed_family_current_difference_max=float(np.max(abs(
            totals['direct_family_current']-totals['reconstructed_family_current']))),
        source_polynomial_paired_current_norm=float(np.linalg.norm(totals['source_polynomial_paired_current'])),
        independent_family_binary_difference_norm=float(np.linalg.norm(totals['independent_family_binary_difference'])),
        paired_polynomial_minus_binary_difference_max=float(np.max(abs(
            totals['source_polynomial_paired_current']-totals['independent_family_binary_difference']))),
        ordered_GG_GH_HG_HH_norms=[float(np.linalg.norm(x))for x in totals['ordered_GG_GH_HG_HH']],
        inferred_response_difference_amplification=1/abs(ym-ye),original_row_records=records,
        GG_paired_cancellation_is_exact_source_algebra=True,
        scalar_mixed_current_orders_discarded=False,new_inverse_or_normalization_used=False,
        physical_mu_minus_e_native_Pauli_or_overlap_identified=False,physical_a_mu=None,physical_g_mu=None,
        error_scope='Source-affine identity uses one unchanged coupled field action. Numerical response coefficients are reconstructed from independent binary64 solves, with their 1/(Ymu-Ye) amplification and original residuals retained. No inverse/assembly error enclosure, physical exterior current, quantum grading, LSZ or Pauli bound is inferred.')
    rp=out/'result.json';rp.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(result_sha256=sha256(rp.read_bytes()).hexdigest(),
        paired_current_norm=result['source_polynomial_paired_current_norm'],
        ordered_norms=result['ordered_GG_GH_HG_HH_norms'])),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--action-folder',type=Path,required=True)
    p.add_argument('--current-base',type=Path,required=True);p.add_argument('--source-side',choices=('incoming','outgoing'),required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    materialize(a.action_folder,a.current_base,a.output,source_side=a.source_side)
