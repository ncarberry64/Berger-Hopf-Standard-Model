"""Actual central Gauss/source-corner balance at the original ea02 field.

Consumes saved native position/clock applications; no action, primal or
response history is replayed. The off-shell charge is retained as a
required affine source-corner row, not removed by a Gauss retraction.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
CURRENT='artifacts/muon_baton_zoo_maximal_current_realization_20261013'
RADIAL='artifacts/muon_baton_zoo_radial_convergence_20261014'
TARGET=CURRENT+'/actual_linear_cut_compatible368_MP_full_operator_blocked_run_2/actual_precise_direct_CHILD620_and_full368_canonical_source_operands.npz'
CLOCK=CURRENT+'/actual_same_cut_native_MP_matrixfree_continuous_clock_run_1/actual_continuous_phase210_clock_and_same_owner_point_density_rate.npz'
RUNTIME=CURRENT+'/actual_new620_fresh_native_MP_new_exact_R7_clock_control_run_1'


def run(repository,position_application,output):
    root,appdir,out=map(lambda p:Path(p).resolve(),(repository,position_application,output))
    out.mkdir(parents=True,exist_ok=False);pins={}
    (out/'executed_producer.py').write_bytes(Path(__file__).read_bytes())
    sys.path[:0]=[str(root/'src'),str(root/'scripts')]
    from flint import ctx,acb_mat
    from bhsm.interface.muon_stored_admission_correction import _matrix,_upper
    from bhsm.interface.muon_stored_fiber_canonical_tangent import _rows,_split
    from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
    from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase
    from bhsm.interface.muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation
    ctx.prec=256
    def pin(p):
        p=Path(p);p=p if p.is_absolute()else root/p
        name=p.relative_to(root).as_posix()if p.is_relative_to(root)else str(p)
        pins[name]=sha256(p.read_bytes()).hexdigest();return p
    def read(p):
        p=pin(p)
        if p.suffix=='.json':return json.loads(p.read_bytes())
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    def module(name,p):
        p=pin(p);spec=importlib.util.spec_from_file_location(name,p)
        m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
    module('bhsm_baton_zoo_exact_acb_packets',RUNTIME+'/bhsm_baton_zoo_exact_acb_packets_imported_runtime.py')
    exactowner=module('bhsm_exact_action_balls',RUNTIME+'/bhsm_exact_action_balls_imported_runtime.py')
    def exact(z,k):
        if k+'_exact_real_mid_mantissa'in z:return exactowner.parse_acb_exact_dyadic(z,k+'_exact')
        return _matrix(z[k+'_high'])+_matrix(z[k+'_low'])
    def take(a,indices):return acb_mat([[a[int(i),j]for j in range(a.ncols())]for i in indices])
    target,clock=read(TARGET),read(CLOCK)
    if pins[TARGET]!='ea02ed6aee45310c5651fef5c8f103e868007d4f125582ab2b64ff7651f76b2b'or pins[CLOCK]!='18fcc0d4fa588c4fcd7aaa8822be76c132b660e0a2f223f7be55fcb9d8d41290':raise ValueError('Exact original ea02/native CUT required')
    meta=read(appdir/'result.json');degree=int(meta['degree'])
    if degree not in(4,6)or meta['classification']!='SAME_ORIGINAL_EA02_FIELD_OFF_SHELL_NEW_RADIAL_POSITION_EULER_APPLICATION':raise ValueError('Corrected same-field D4/D6 position application required')
    if meta['source_sha256']!='d6b0dbb2e34185011f243f7f571da2f536ebc58c6138fab380f856a2f5db96b9'or not meta['epoch_basis_value_and_clock_reconstructed_from_native_point_germs']:raise ValueError('Exact reviewed native-epoch reconstruction source required')
    archive=appdir/meta['archive']['name']
    if sha256(archive.read_bytes()).hexdigest()!=meta['archive']['sha256']:raise ValueError('Position application changed')
    a=read(archive)
    if not np.array_equal(a['master368'],target['master368'])or a['coordinate_time'].item()!=target['coordinate_time'].item():raise ValueError('No field/clock epoch splice')
    if not np.array_equal(clock['master368'],target['master368'])or clock['coordinate_time'].item()!=target['coordinate_time'].item():raise ValueError('Native clock is not the exact cut')
    if max(meta['physical_point_germ_preservation_upper'].values())>2e-10:raise ValueError('Actual native field/clock germs must be preserved')
    map_archive=appdir/meta['native_epoch_map_archive']['name']
    if sha256(map_archive.read_bytes()).hexdigest()!=meta['native_epoch_map_archive']['sha256']:raise ValueError('Corrected native epoch-map bytes changed')
    native_maps=read(map_archive)
    if native_maps['coordinate_time'].item()!=target['coordinate_time'].item():raise ValueError('Native epoch-map time differs')
    phasepacket=read(f'{RADIAL}/actual_common_cut_degree{degree}_complete_phase_blocks_run_1/actual_same_current_complete_phase_and_literal_temporal_generator_operands.npz')
    profiles=read(f'{RADIAL}/literal_MP_radial_complex192_run_2/degree_{degree:02d}_literal_MP_radial_profiles_and_derivative_complex.npz')
    mapdata=read(f'{RADIAL}/actual_linear_cut_degree{degree}_complete_clock_epoch_maps_run_1/actual_degree_{degree:02d}_complete_clock_covariant_product_epoch_maps.npz')
    n=int(a['enlarged_dynamic_count']);oldmap=np.asarray(a['old368_to_enlarged_child'],int);newq=np.asarray(a['new_position_indices'],int);m=len(newq)
    if not np.array_equal(mapdata['actual_nonzero_current_master368'],target['master368']):raise ValueError('Temporal generator index chart belongs to another field')
    if not np.array_equal(phasepacket['phase_to_full_action_indices'],252+np.arange(n,int(meta['full_dimension'])-252)):raise ValueError('Temporal generator phase ordering differs')
    if not np.array_equal(np.sort(np.r_[oldmap[:158],newq]),np.arange(n)):raise ValueError('Every old and new position must appear once')
    if not np.array_equal(oldmap[158:316],n+oldmap[:158]):raise ValueError('Original q/v incidence changed')
    selected=np.asarray(a['test_full_action_indices'],int)-252
    expected=np.r_[newq,n+newq,np.arange(2*n,int(meta['full_dimension'])-252)]
    if not np.array_equal(selected,expected):raise ValueError('Original selected new q/v/allGauss order required')
    G,Gt=exact(a,'phase_gradient'),exact(a,'phase_gradient_first')
    oldG,oldGt=exact(clock,'phase_gradient'),exact(clock,'phase_gradient_first')
    oldrows=exact(clock,'original_unreacted_phase210_clock_rows')
    nqg=G.nrows()-2*m;Pi,Pidot,Gq=acb_mat(n,1),acb_mat(n,1),acb_mat(n,1)
    for i,dest in enumerate(oldmap[:158]):
        Pi[int(dest),0]=oldG[i,0];Pidot[int(dest),0]=oldGt[i,0]
        Gq[int(dest),0]=oldGt[i,0]-oldrows[i,0]
    for j,dest in enumerate(newq):
        Pi[int(dest),0]=G[m+j,0];Pidot[int(dest),0]=Gt[m+j,0];Gq[int(dest),0]=G[j,0]
    Euler=Gq-Pidot;rG=_rows(G,2*m,G.nrows());rGdot=_rows(Gt,2*m,Gt.nrows())
    Z=exact(phasepacket,'actual_literal_temporal_generators');count=degree+5
    if Z.nrows()!=n+nqg or Z.ncols()!=4*count:raise ValueError('Complete declared temporal generator carrier required')
    # The CENTRAL columns are independent of the old/native K,Kdot product
    # map: temporal_generators() places only literal derivative coefficients,
    # At profiles and -T_Y H phi(wall). Their unchanged field/index operands
    # are pinned; no old-clock SU2 product column is used here.
    sourcefile=f'{RADIAL}/actual_common_cut_degree{degree}_complete_phase_blocks_run_1/executed_bhsm_baton_zoo_current_covariant_phase_blocks.py';pin(sourcefile)
    central=take(Z.transpose(),[4*p+3 for p in range(count)]).transpose()
    V,C=_rows(central,0,n),_rows(central,n,n+nqg)
    phase=load_profile_preserving_phase('artifacts/muon_inherited_finite_normal_phase_20261011/run_1',repository=root)
    pins.update(phase['input_hashes']);P=phase['coordinates']['lift']
    oldrate=exact(clock,'actual_child_master_rate');rawrate=_matrix(P)*take(oldrate,target['original252_to_augmented368'])
    Hdot=_rows(rawrate,260,264);HY=_matrix(higgs_u2_real_representation()['real_generators'][3])
    wall=exact(profiles,'wall_values');Vdot=acb_mat(n,count);original=np.asarray(mapdata['child_original252_to_augmented'],int)
    for p in range(count):
        d=-HY*Hdot*wall[0,p]
        for i in range(4):Vdot[int(original[102+i]),p]=d[i,0]
    # Gauge parameter chi=g(t)*phi_p(rho): deltaAt=gdot*phi,
    # deltaAr=g*phi_rho, deltaH=-g*T_Y*H*phi(wall).
    charge=V.transpose()*Pi;gauss=C.transpose()*rG
    charge_rate=V.transpose()*Pidot+Vdot.transpose()*Pi;gauss_rate=C.transpose()*rGdot
    primary=charge+gauss;dprimary=charge_rate+gauss_rate
    static=V.transpose()*Gq+Vdot.transpose()*Pi
    divergence=V.transpose()*Euler-gauss_rate
    oldK=exact(a,'saved_original_binary_Gauss_Kz_trial');oldr=exact(a,'saved_original_binary_primal_Gauss_r')
    arrays=dict(coordinate_time=a['coordinate_time'],master368=a['master368'],central_profile_indices=np.arange(count),
        full_original_phase_generator_columns=np.arange(count)*4+3,all_original_and_new_position_indices=np.arange(n),
        new_position_indices=newq,old368_to_enlarged_child=oldmap,
        original_prefix_cell7_complete_density_time_derivative_admitted=np.asarray(False))
    values=dict(full_canonical_momentum=Pi,full_canonical_momentum_total_clock=Pidot,full_position_gradient=Gq,
        full_position_Euler=Euler,full_primal_Gauss_r=rG,full_primal_Gauss_total_clock=rGdot,
        central_gauge_position_map=V,central_gauge_position_map_total_clock=Vdot,central_gauge_Gauss_map=C,
        actual_primal_initial_corner_charge=charge,actual_primal_Gauss_charge_projection=gauss,
        actual_primal_future_arm_initial_outward_corner_flux=-charge,
        actual_initial_corner_charge_total_clock=charge_rate,actual_Gauss_charge_total_clock=gauss_rate,
        primary_Noether_rows=primary,differentiated_primary_Noether_rows=dprimary,
        static_gauge_action_rows=static,source_conservation_rows=divergence,
        required_affine_defect_Gauss_rhs=-rG,required_affine_defect_initial_corner_charge=gauss,
        required_affine_defect_future_arm_initial_outward_corner_flux=-gauss,
        saved_original_binary_Gauss_Kz_trial=oldK,saved_original_binary_primal_Gauss_r=oldr,
        saved_original_binary_Gauss_Kz_central_projection=C.transpose()*oldK,
        native_primal_Gauss_minus_saved_original_binary=rG-oldr)
    for key,value in values.items():
        arrays[key+'_high'],arrays[key+'_low']=_split(value);arrays.update(exactowner.export_acb_exact_dyadic(value,key+'_exact'))
    path=out/'actual_central_Gauss_source_corner_and_conservation.npz';_compressed_npz(path,arrays)
    pin('src/bhsm/interface/muon_intrinsic_higgs_gauge_action.py');pin(Path(__file__))
    report=dict(classification='ACTUAL_ORIGINAL_EA02_NATIVE_CENTRAL_GAUSS_SOURCE_CORNER_APPLICATION',degree=degree,
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),input_and_source_hashes=dict(sorted(pins.items())),
        archive=dict(name=path.name,sha256=sha256(path.read_bytes()).hexdigest(),bytes=path.stat().st_size),
        arithmetic_precision_bits=256,central_parameter_count=count,full_position_count=n,full_Gauss_count=nqg,
        primary_Noether_upper=_upper(primary),differentiated_primary_Noether_upper=_upper(dprimary),
        static_gauge_action_upper=_upper(static),source_conservation_upper=_upper(divergence),
        conservation_minus_static_plus_differentiated_identity_upper=_upper(divergence-static+dprimary),
        actual_primal_initial_corner_charge_upper=_upper(charge),actual_primal_Gauss_charge_projection_upper=_upper(gauss),
        actual_Gauss_charge_total_clock_upper=_upper(gauss_rate),actual_full_primal_Gauss_upper=_upper(rG),
        old_position_Euler_rows_retained_not_zeroed=True,central_generator_uses_no_old_clock_SU2_product_columns=True,
        scalar_wall_H_and_Hdot_contact_retained_once=True,inherited_parent_and_both_reference_clocks_retained_once=True,
        canonical_charge_is_Pi_pairing=True,future_arm_initial_outward_conormal_sign=-1,
        no_extra_Haar_or_source_charge_normalization_inserted=True,
        primal_rG_and_saved_KGz_kept_separate=True,saved_KGz_is_original_binary_formation_not_native_certified=True,
        linearized_native_source_corner_for_seven=None,new_physical_initial_data_selected=False,Gauss_retraction_applied=False,
        no_action_or_primal_or_source_history_sampling_replayed=True,original_coupled_corrections=0,
        native_in_name_is_material_precision_not_native_operator_identification=True,
        microscopic_graded_induced_current_evaluated=False,physical_charge_units_assigned=False,
        full_reset_and_ghost_boundary_domain_application=False,
        classical_Lorentz_canonical_charge_not_unsquared_boundary_Gamma_or_native_square=True,
        physical_outgoing_Y_R=None,physical_affine_s_R=None,physical_C0_Cj=None,
        physical_full_derivative_pass=False,physical_radial_convergence=False,physical_Maxwell226_after_pass=False,
        normalized_two_spin_state=False,physical_muon_magnetic_moment=None)
    (out/'result.json').write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps({k:report[k]for k in('degree','primary_Noether_upper','differentiated_primary_Noether_upper','source_conservation_upper','actual_primal_initial_corner_charge_upper','actual_full_primal_Gauss_upper')}),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repository',default=ROOT,type=Path)
    p.add_argument('--position-application',required=True,type=Path);p.add_argument('--output',required=True,type=Path)
    a=p.parse_args();run(a.repository,a.position_application,a.output)
