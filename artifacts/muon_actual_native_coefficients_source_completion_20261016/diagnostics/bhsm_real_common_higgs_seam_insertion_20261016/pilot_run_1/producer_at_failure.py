"""Actual common1200 Higgs seam coefficients on the same REAL wall germs.

All known full384 chiral/boost/Yukawa/angular coefficients are evaluated.
Unknown independent normal-mode values/source jets stay explicit factors;
they cancel in the normalized intrinsic18 coefficient, not in the ambient
768-field realization. No Higgs bulk mass or native seam phase is appended.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np
from scipy.sparse import csr_matrix

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.muon_common_higgs_seam_insertion import (
    common_higgs_seam_maps,full_higgs_seam_numerator_jet)
from bhsm.interface.muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace
from bhsm.interface.muon_real_positive_d5_covector_binding import real_positive_d5_covector_binding
from bhsm.interface.muon_parent_positive_brst_ghost import ghost_radial_values,smooth_ghost_temporal_values
from bhsm.interface.muon_parent_retarded_hypercharge import WALL
from bhsm.interface.muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz

SOURCE='artifacts/muon_real_coupled_open_operator_20261016/source_first_run_1'
SOURCE_JSON_SHA='d15def102e329c38f35b62c137d8398aa72eeda626924498a426246d66c88df1'
SOURCE_ARCHIVE_SHA='7da8ddd5fa4bda397aa6a2d50e845338a3ef92fb3f0e837a5a6d0d166915e177'
GAUGE_REPORT_SHA='af5872c113abcbed953b75699be0b764550dfabe5269fd90d5d91bee9c157f06'


def compare(a,b):
    a,b=np.asarray(a),np.asarray(b);d=float(np.max(abs(a-b)))
    return dict(max_absolute=d,relative_max_norm=d/max(float(np.max(abs(a))),float(np.max(abs(b))),1e-300))


def save_sparse(arrays,name,a):
    a=csr_matrix(a);arrays[name+'_data']=a.data;arrays[name+'_indices']=a.indices
    arrays[name+'_indptr']=a.indptr;arrays[name+'_shape']=np.array(a.shape)


def real(a,name):
    a=np.asarray(a)
    if not np.isfinite(a).all()or(np.iscomplexobj(a)and np.any(a.imag!=0)):raise ValueError('Exact REAL saved operand required:'+name)
    return np.asarray(a.real,float)


def operator_gram(vertices,gaunt,other=None):
    """Frobenius diagnostic of the COMPLETE operator map, not a heat trace."""
    if other is None:internal=np.einsum('cij,dij->cd',vertices.conj(),vertices,optimize=True)
    else:
        internal=np.einsum('cij,dij->cd',vertices.conj(),other,optimize=True)
        internal+=np.einsum('cij,dij->cd',other.conj(),vertices,optimize=True)
    angular=np.einsum('ohk,opk->hp',gaunt.conj(),gaunt,optimize=True)
    return np.einsum('cd,hp->chdp',internal,angular).reshape(80,80)


def execute(gauge_folder,output):
    gauge,out=Path(gauge_folder).resolve(),Path(output).resolve()
    if out.exists():raise FileExistsError('Preserve independent actual coefficient evaluations')
    pins={}
    def pin(path,expected=None):
        p=Path(path);p=p if p.is_absolute()else ROOT/p;h=sha256(p.read_bytes()).hexdigest()
        if expected and h!=expected:raise ValueError('Frozen source epoch/bytes changed:'+str(p))
        pins[p.relative_to(ROOT).as_posix()if p.is_relative_to(ROOT)else str(p)]=h;return p
    source=json.loads(pin(SOURCE+'/result.json',SOURCE_JSON_SHA).read_bytes())
    with np.load(pin(SOURCE+'/application.npz',SOURCE_ARCHIVE_SHA),allow_pickle=False)as z:saved={k:z[k].copy()for k in z.files if '_input_'in k}
    gm=json.loads(pin(gauge/'result.json',GAUGE_REPORT_SHA).read_bytes())
    if gm['input_and_source_sha256'][SOURCE+'/application.npz']!=SOURCE_ARCHIVE_SHA or gm['input_fermion_harmonics']!=5 or gm['complete_product_output_harmonics']!=55:
        raise ValueError('Original SAME REAL common/D5/angular epoch required')
    angular_path=gauge/'angular_product_incidence.npz'
    with np.load(pin(angular_path,gm['archives'][angular_path.name]['sha256']),allow_pickle=False)as z:gaunt=z['gaunt_full55_real20_input5'].copy()
    if gaunt.shape!=(55,20,5):raise ValueError('Complete connected angular product required')
    full=full_d5_localized_lepton_trace();records=[];out.mkdir(parents=True)
    common=dict(gaunt_full55_real20_input5=gaunt,full384_localized18_lift=full['localized_lepton18_trace_lift'],
        full384_localized18_literal_dual=full['localized_lepton18_literal_dual'],
        full384_retained_complement=full['full_retained_complement'])
    for side in('incoming','outgoing'):
        prefix=side+'_input_';c={k[len(prefix):]:real(v,k)for k,v in saved.items()if k.startswith(prefix)}
        raw,rawtime=c.pop('raw'),c.pop('rawtime')
        gp=gauge/(side+'_saved_geometry.npz')
        with np.load(pin(gp,gm['archives'][gp.name]['sha256']),allow_pickle=False)as z:
            if not np.array_equal(raw,z[side+'_raw'])or not np.array_equal(rawtime,z[side+'_rawtime']):raise ValueError('No mean/source epoch splice')
            for k,a in c.items():
                if not np.array_equal(a,z[side+'_c_'+k]):raise ValueError('No field/clock/trace splice:'+k)
        rs=[r for r in source['records']if r['side']==side and r['angular_level']==1]
        t0=float(rs[0]['coordinate_time']);length=2*abs(t0)
        H,Hdot=c['intrinsic_H_realified'],c['intrinsic_H_realified_first'][0]
        R,Rdot=c['radius'][-1],c['radius_first'][0,-1];ell,elldot=c['surface_proper_clock_rate'][-1],c['surface_proper_clock_rate_first'][0,-1]
        rho=ell*R**3;rhodot=elldot*R**3+3*ell*R**2*Rdot
        U,Udot=c['material_wall_velocity'][-1],c['material_wall_velocity_first'][0,-1]
        seam=full_higgs_seam_numerator_jet(H,Hdot,U,Udot,rho,rhodot,full_representation=full)
        wall={k:(a[:,-1:]if k.endswith('_first')else a[-1:])for k,a in c.items()if(k.endswith('_first')or a.shape[:1]==(5,))}
        positive=real_positive_d5_covector_binding(wall,gamma=full['gamma5D_particle'],sheet_orientation=1)
        s=positive['input_output_density_isometry'][0];sdot=positive['input_output_density_isometry_first'][0,0]
        ratio=rho/s**2;ratiodot=rhodot/s**2-2*rho*sdot/s**3
        C,Cdot=c['radial_coframe'][-1],c['radial_coframe_first'][0,-1]
        density_check=compare(np.array([ratio,ratiodot]),np.array([ell/C,elldot/C-ell*Cdot/C**2]))
        arrays=dict(H_real=H,H_real_time=Hdot,raw_fields=raw,raw_fields_time=rawtime,
            original_surface_density=np.array(rho),original_surface_density_time=np.array(rhodot),
            material_velocity=np.array(U),material_velocity_time=np.array(Udot),
            bulk_density_isometry=np.array(s),bulk_density_isometry_time=np.array(sdot),
            original_bilinear_density_pulled_coefficient=np.array(ratio),original_bilinear_density_pulled_coefficient_time=np.array(ratiodot))
        for k in('fixed_real_Higgs_vertices','background_intrinsic_mass','background_intrinsic_mass_time',
            'intrinsic_normalized_vertex','intrinsic_normalized_vertex_time','intrinsic_normalized_background','intrinsic_normalized_background_time'):
            arrays[k]=seam[k]
        covariance=[];TH=higgs_u2_real_representation()['real_generators'];TF=full['localized_gauge_intertwiner'];V=seam['fixed_real_Higgs_vertices']
        for j in range(4):
            vertical=np.einsum('c,cij->ij',-TH[j]@H,V);verticalt=np.einsum('c,cij->ij',-TH[j]@Hdot,V)
            covariance.append(dict(internal=j,value=compare(vertical,-TF[j]@seam['background_intrinsic_mass']+seam['background_intrinsic_mass']@TF[j]),
                time=compare(verticalt,-TF[j]@seam['background_intrinsic_mass_time']+seam['background_intrinsic_mass_time']@TF[j])))
        recovered=np.zeros((4,18,18),complex);recoveredt=recovered.copy();recoveries={}
        for label,ch in seam['channels'].items():
            L=seam['frames'][ch['left_sheet']];B=seam['frames'][ch['right_sheet']]
            n,nt=ch['ambient_vertex_numerators'],ch['ambient_vertex_numerators_time']
            a=L['mode_Dirac_bar_left_numerator']@n@B['mode_right_numerator']
            at=L['mode_Dirac_bar_left_numerator_time']@n@B['mode_right_numerator']
            at+=L['mode_Dirac_bar_left_numerator']@nt@B['mode_right_numerator']
            at+=L['mode_Dirac_bar_left_numerator']@n@B['mode_right_numerator_time']
            target=-rho*ch['left_chiral_projector']@V@ch['right_chiral_projector']
            targett=-rhodot*ch['left_chiral_projector']@V@ch['right_chiral_projector']
            recovered+=a;recoveredt+=at
            recoveries[label]=dict(value=compare(a,target),time=compare(at,targett),
                unknown_normal_factor=ch['unknown_normal_factor'],unknown_normal_factor_time=ch['unknown_normal_factor_time'])
            Lm, Lmt=L['mode_Dirac_bar_left_numerator'],L['mode_Dirac_bar_left_numerator_time']
            Rm, Rmt=B['mode_right_numerator'],B['mode_right_numerator_time']
            npull=n/s**2;npullt=nt/s**2-2*n*sdot/s**3
            apull=(s*Lm)@npull@(s*Rm)
            apullt=(sdot*Lm+s*Lmt)@npull@(s*Rm)+(s*Lm)@npullt@(s*Rm)+(s*Lm)@npull@(sdot*Rm+s*Rmt)
            recoveries[label]['density_isometry_value']=compare(apull,target)
            recoveries[label]['density_isometry_time']=compare(apullt,targett)
            for j in range(4):
                save_sparse(arrays,label+f'_ambient_numerator_vertex{j}',n[j]);save_sparse(arrays,label+f'_ambient_numerator_vertex{j}_time',nt[j])
            save_sparse(arrays,label+'_ambient_background_numerator',ch['ambient_background_numerator'])
            save_sparse(arrays,label+'_ambient_background_numerator_time',ch['ambient_background_numerator_time'])
            arrays[label+'_complete_operator_coefficient_Gram']=operator_gram(n,gaunt)
            arrays[label+'_complete_operator_coefficient_Gram_time']=operator_gram(n,gaunt,nt)
        for label,frame in seam['frames'].items():
            for k,a in frame.items():save_sparse(arrays,label+'_'+k,a)
        intrinsicG=operator_gram(seam['intrinsic_normalized_vertex'],gaunt)
        intrinsicGt=operator_gram(seam['intrinsic_normalized_vertex'],gaunt,seam['intrinsic_normalized_vertex_time'])
        arrays['intrinsic_complete_operator_coefficient_Gram']=intrinsicG
        arrays['intrinsic_complete_operator_coefficient_Gram_time']=intrinsicGt
        tg=smooth_ghost_temporal_values([length/2],length)[0];wr=ghost_radial_values(np.array([WALL]))[0]
        for sign in(-1,1):
            temporal=np.r_[1.,sign*2/length,tg[0,:2],tg[1,:2]]
            hs=common_higgs_seam_maps(H,Hdot,temporal,wr)
            save_sparse(arrays,f'tent{sign}_common_scalar_map',hs['value']);save_sparse(arrays,f'tent{sign}_common_scalar_map_time',hs['time'])
            norm2=np.einsum('ai,ab,bi->i',hs['value'],intrinsicG,hs['value'],optimize=True).real
            arrays[f'tent{sign}_all1200_intrinsic_operator_norm_squared']=norm2
            arrays[f'tent{sign}_all1200_intrinsic_operator_norm_squared_time']=(np.einsum('ai,ab,bi->i',hs['time'],intrinsicG,hs['value'],optimize=True)
                +np.einsum('ai,ab,bi->i',hs['value'],intrinsicG,hs['time'],optimize=True)
                +np.einsum('ai,ab,bi->i',hs['value'],intrinsicGt,hs['value'],optimize=True)).real
            for label in seam['channels']:
                G=arrays[label+'_complete_operator_coefficient_Gram']
                arrays[f'tent{sign}_{label}_all1200_ambient_numerator_norm_squared']=np.einsum('ai,ab,bi->i',hs['value'],G,hs['value'],optimize=True).real
            records.append(dict(side=side,coordinate_time=t0,tent_one_sided_sign=sign,
                independent_scalar80_nonzero_columns=int(np.count_nonzero(norm2[1120:])),dependent_gauge_orbit320_nonzero_value_columns=int(np.count_nonzero(norm2[800:1120])),
                independent_scalar80_complete_operator_norm_min=float(np.sqrt(np.min(norm2[1120:]))),
                complete_operator_norm_max=float(np.sqrt(np.max(norm2))),
                all1200_norms_are_full_operator_Frobenius_diagnostics_not_spectral_traces=True,
                normal_trace_values_or_source_jets_evaluated=False,normal_factor_cancellation=recoveries,
                normalized_intrinsic_recovery=compare(recovered,seam['intrinsic_normalized_vertex']),
                normalized_intrinsic_recovery_time=compare(recoveredt,seam['intrinsic_normalized_vertex_time']),
                scalar_gauge_covariance=covariance,bulk_density_isometry_original_bilinear_coefficient_check=density_check))
        _compressed_npz(out/(side+'_common_higgs_seam_coefficients.npz'),arrays)
    _compressed_npz(out/'common_angular_and_full_trace_incidence.npz',common)
    for name,m in list(sys.modules.items()):
        p=getattr(m,'__file__',None)
        if name.startswith('bhsm.')and p and Path(p).is_relative_to(ROOT):pin(p)
    pin(__file__);(out/'executed_producer.py').write_bytes(Path(__file__).read_bytes())
    archives={p.name:dict(sha256=sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)for p in sorted(out.glob('*.npz'))}
    if max(r['bytes']for r in archives.values())>10*1024*1024:raise ArithmeticError('Compact archive exceeds publication limit')
    result=dict(classification='ACTUAL_SAME_REAL_COMMON1200_HIGGS_TWO_SHEET_SEAM_OPERATOR_COEFFICIENTS',records=records,
        common_dimension=1200,ambient_two_eta_field_dimension=768,full_one_sheet_carrier_dimension=384,intrinsic_dimension=18,
        independent_H80_and_dependent_minus_eta_H_retained=True,Hdot_and_both_tent_time_jets_retained=True,
        fixed_noncentral_Yukawa_and_all_three_families_retained=True,complete_product_output_harmonics=55,
        exact_normal_factor_cancellation_in_intrinsic18_source_equation=True,ambient_normal_mode_values_and_source_jets=None,
        complete_known_operator_coefficients_evaluated_not_only_probe_columns=True,original_Dirac_bar_Gamma0_count=1,
        Higgs_seam_added_once_no_second_intrinsic_kinetic_or_bulk_D5_mass=True,independent_left_or_complex_source_conjugated=False,
        density_pullback_is_original_bilinear_representation_change_only=True,native_positive_Higgs_seam_identification=False,
        normalized_intrinsic_coefficient_invariant_under_bulk_density_isometry=True,
        actual_bare_Higgs_bridge_affine_does_not_zero_inverse_or_quantum_Higgs_susceptibility=True,
        physical_exterior_or_graded_domain_or_spin_normalization_selected=False,physical_E_B_total_derivative_pass=False,
        original_coupled_corrections=0,new_D5_or_source_or_history_campaigns=0,physical_Maxwell226_after_pass=False,physical_muon_magnetic_moment=None,
        input_and_source_sha256=dict(sorted(pins.items())),archives=archives)
    (out/'result.json').write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--gauge-insertion-folder',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();execute(a.gauge_insertion_folder,a.output)
