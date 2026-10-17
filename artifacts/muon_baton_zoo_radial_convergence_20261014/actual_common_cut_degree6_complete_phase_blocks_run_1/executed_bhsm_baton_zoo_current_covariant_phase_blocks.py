"""New current phase columns with all old same-scalar columns retained."""
from pathlib import Path
import argparse
import importlib.util
import sys
import numpy as np


def temporal_generators(rep, P, maps, raw, degree):
    from flint import acb_mat
    from bhsm.interface.muon_stored_admission_correction import _matrix
    from bhsm.interface.muon_parent_maxwell_full_weak import FIELD_ORDER
    from bhsm.interface.muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation
    from bhsm_baton_zoo_literal_radial_profile_precision import literal_profiles
    n, dim = int(maps['dynamic_count']), int(maps['full_dimension'])-252
    original, extra = np.asarray(maps['child_original252_to_augmented'], int), np.asarray(maps['extra_coordinates_to_full'], int)-252
    profile = literal_profiles(rep, rep['rho'], degree)
    wall = literal_profiles(rep, [np.pi/2], degree)['values']
    count = degree+5
    Z, F = acb_mat(dim-n, 4*count), acb_mat(4*count, dim-n)
    coefficient = {}
    for j, label in enumerate(rep['gauge_labels']):
        if label['field'] not in ('A_tau', 'A_rho'):
            continue
        rawrow = np.asarray(P[100+j])
        k = int(np.flatnonzero(rawrow)[0])
        coefficient[(label['field'], int(label['radial']), int(label['internal']))] = (int(original[k]), _matrix([[rawrow[k]]])[0, 0])
    N, compatible = 3*count, 36*(degree+1)+8
    H = _matrix(raw[1, 260:264])
    T = [_matrix(v) for v in higgs_u2_real_representation()['real_generators']]
    for p in range(count):
        for c in range(4):
            j = 4*p+c
            if p < 4:
                dest, scale = coefficient[('A_tau', p, c)]
                Z[dest-n, j] = 1/scale
            else:
                dest = int(extra[36*(p-4)+32+c])
                Z[dest-n, j] = 1
            F[j, dest-n] = 1
            if c < 3:
                # K has a separate rate for every SU2/chi pair.
                rate = int(extra[compatible+N+3*p+c])
                Z[rate-n, j] = 1
            else:
                for row in range(degree+9):
                    value = profile['derivative_coefficients'][row, p]
                    if value == 0:
                        continue
                    if row < 4:
                        ar, scale = coefficient[('A_rho', row, 3)]
                        Z[ar, j] += value/scale
                    elif row < degree+5:
                        ar = int(extra[36*(row-4)+3])
                        Z[ar, j] += value
                    else:
                        ar = int(extra[36*(degree+1)+row-(degree+5)])
                        Z[ar, j] += value
            scalar = -T[c]*H*wall[0, p]
            for i in range(4):
                Z[int(original[102+i]), j] += scalar[i, 0]
    return Z, F


def run(repository, current_operator, projection, epoch_maps, output, *, degree=2, block_size=16):
    from bhsm_baton_zoo_radial_convergence import environment
    root, out, read, save, finish = environment(repository, output)
    from flint import acb_mat, ctx
    from bhsm.interface.muon_stored_admission_correction import _matrix, _upper
    from bhsm.interface.muon_stored_fiber_canonical_tangent import _split
    from evaluate_muon_continued_current_factor import retained_input
    ctx.prec=192
    actual, data, maps = read(Path(current_operator)), read(Path(projection)), read(Path(epoch_maps))
    exact=lambda z,k:_matrix(z[k+'_high'])+_matrix(z[k+'_low'])
    time=actual['coordinate_time'].item()
    if time!=data['authoritative_node_time'].item() or time!=maps['coordinate_time'].item():
        raise ValueError('same accepted current cut and physical projection required')
    retained,_=retained_input('outgoing',{})
    rep,P=retained['representation'],retained['coordinates']['lift']
    params=read(root/'artifacts/muon_coupled_birth_full_application_20261012/run_1/result.json')['action_parameters']
    n,dim=int(maps['dynamic_count']),int(maps['full_dimension'])-252
    old_to_new=np.asarray(data['explicit_current368_to_complete_child'],int)
    old_phase=old_to_new[158:]-n
    if len(np.unique(old_phase))!=210 or np.any(old_phase<0):raise ValueError('all original current210 phase rows required')
    q=dim-n
    added=np.setdiff1d(np.arange(q),old_phase)
    H=acb_mat(q,q)
    oldH=exact(actual,'true_child_Hessian368')
    for i,ii in enumerate(old_phase):
        for j,jj in enumerate(old_phase):H[int(ii),int(jj)]=oldH[158+i,158+j]
    owner=Path(projection).parent/'same_current_cut_packed_scalar_owner.py'
    snap=out/'same_current_packed_scalar_owner.py';snap.write_bytes(owner.read_bytes())
    spec=importlib.util.spec_from_file_location('current_covariant_phase_blocks_owner',snap)
    packed=importlib.util.module_from_spec(spec);sys.modules[spec.name]=packed;spec.loader.exec_module(packed)
    tests=252+np.arange(n,dim)
    extra=np.asarray(maps['extra_coordinates_to_full'],int)
    base=data['full_current_primal_child_coefficients'][extra-252]
    gradient=None;blocks=[];max_gradient=0.;formed=set();new_transpose_difference=0.
    for start in range(0,len(added),block_size):
        stop=min(start+block_size,len(added));selected=added[start:stop]
        R=np.zeros((252+dim,len(selected)),complex);R[tests[selected],np.arange(len(selected))]=1
        app=packed.phase_action_contractions(actual['raw_pair'],actual['reference_pair'],rep,P,maps,tests,
            np.zeros(252+dim),np.zeros(252+dim),R,np.zeros_like(R),extra_base=base,
            include_directional_first=False,include_parent_action=False,material_chart_precision='original_binary',
            nu_squared_action=params['nu_squared_action'],surface_gamma=params['surface_gamma'])
        block=exact(app,'phase_Hessian_on_actual_right');G=exact(app,'phase_gradient')
        if gradient is None:gradient=G
        else:max_gradient=max(max_gradient,_upper(G-gradient))
        for j,jj in enumerate(selected):
            for k,kk in enumerate(selected):
                new_transpose_difference=max(new_transpose_difference,_upper(acb_mat([[block[int(kk),j]-block[int(jj),k]]])))
        for i in range(q):
            for j,jj in enumerate(selected):
                if i in formed:
                    new_transpose_difference=max(new_transpose_difference,_upper(acb_mat([[H[int(jj),i]-block[i,j]]])))
                H[i,int(jj)]=block[i,j];H[int(jj),i]=block[i,j]
        formed.update(map(int,selected))
        save(f'new_phase_columns_{start:04d}_{stop:04d}.npz',dict(new_phase_right_indices=selected,
            phase_Hessian_on_actual_right_high=app['phase_Hessian_on_actual_right_high'],
            phase_Hessian_on_actual_right_low=app['phase_Hessian_on_actual_right_low']))
        blocks.append(dict(start=start,stop=stop))
        print(dict(stage='new_current_phase_columns_saved',degree=degree,start=start,stop=stop,total=len(added)),flush=True)
    if max_gradient>2e-10 or new_transpose_difference>2e-10:
        raise ArithmeticError('same scalar new columns disagree; no completed phase matrix admission')
    Z,F=temporal_generators(rep,P,maps,actual['raw_pair'],degree)
    arrays=dict(coordinate_time=actual['coordinate_time'],dynamic_count=np.asarray(n),full_dimension=np.asarray(252+dim),
        phase_to_full_action_indices=tests,all_old_current210_phase_indices=old_phase,
        new_phase_indices=added,explicit_current368_to_complete_child=old_to_new,
        child_original252_to_augmented=maps['child_original252_to_augmented'])
    for name,value in [('actual_complete_child_phase_Hessian',H),('actual_literal_temporal_generators',Z),
                       ('literal_all_At_frames',F),('actual_phase_Hessian_generator_rows',H*Z),
                       ('literal_frame_generator_incidence',F*Z)]:arrays[name+'_high'],arrays[name+'_low']=_split(value)
    save('actual_same_current_complete_phase_and_literal_temporal_generator_operands.npz',arrays)
    finish(dict(classification='ACTUAL_SAME_CURRENT_COMPLETE_PHASE_FROM_RETAINED_AND_NEW_SAME_SCALAR_COLUMNS',degree=degree,
        actual_phase_dimension=q,new_original_action_columns=len(added),all_old_current210_rows_retained=True,
        blocks=blocks,same_scalar_gradient_between_new_blocks_upper=max_gradient,
        original_phase_Hessian_generator_rows_upper=_upper(H*Z),
        original_phase_Hessian_transpose_symmetry_upper=_upper(H-H.transpose()),
        independently_evaluated_new_column_transpose_difference_upper=new_transpose_difference,
        old_new_opposite_block_filled_by_literal_scalar_Hessian_analytic_transpose=True,
        full_position_gauge_or_Hxx_Ward_or_outgoing_domain_admitted=False),producer_paths=(Path(__file__),snap))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in('repository','current-operator','projection','epoch-maps','output'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--degree',type=int,choices=(2,4,6,8),default=2)
    p.add_argument('--block-size',type=int,default=16)
    a=p.parse_args();run(a.repository,a.current_operator,a.projection,a.epoch_maps,a.output,degree=a.degree,block_size=a.block_size)
