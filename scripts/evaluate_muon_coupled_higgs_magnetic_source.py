"""Evaluate actual coupled intrinsic scalar source blocks on corrected fields."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_coupled_higgs_magnetic_source import intrinsic_coupled_magnetic_source_point
from bhsm.interface.muon_intrinsic_higgs_positive_source import higgs_magnetic_source_image_space
from bhsm.interface.muon_parent_maxwell_full_q_application import retained_full_q_angular_space
from bhsm.interface.muon_parent_positive_brst_ghost import smooth_ghost_temporal_values,ghost_radial_values
from bhsm.interface.muon_parent_retarded_hypercharge import WALL
from bhsm.interface.muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
from bhsm.interface.muon_birth_finite_normal_phase import load_finite_normal_endpoint
from evaluate_muon_reached_trace_action import deterministic_archive
from evaluate_muon_intrinsic_scalar_regulator_correction import source_record


def materialize(output,*,source):
    folder=Path(source);folder=folder if folder.is_absolute() else ROOT/folder
    out=Path(output);out=out if out.is_absolute() else ROOT/out
    if out.exists():raise FileExistsError('preserve previous source applications')
    raw=(folder/'result.json').read_bytes();md=json.loads(raw)
    if md['classification']!='EVALUATED_CORRECTED_PROFILE_SAME_BIRTH_LOCAL_MAGNETIC_FULL488_RETARDED_RESPONSE':
        raise ValueError('corrected same-profile magnetic source response required')
    hashes=dict(md['input_hashes']);hashes[(folder/'result.json').relative_to(ROOT).as_posix()]=sha256(raw).hexdigest()
    for name,h in hashes.items():
        if sha256((ROOT/name).read_bytes()).hexdigest()!=h:raise ValueError('consumed corrected source changed: '+name)
    loaded={}
    for side in ('incoming','outgoing'):
        for label in ('primal_and_source','phase','velocity','contacts'):
            name=side+'_'+label+'.npz';p=folder/name;data=p.read_bytes();record=md['array_archives'][name]
            if len(data)!=record['bytes'] or sha256(data).hexdigest()!=record['sha256']:raise ValueError('actual field archive changed: '+name)
            hashes[p.relative_to(ROOT).as_posix()]=record['sha256']
            with np.load(p,allow_pickle=False) as f:loaded[side,label]={k:f[k] for k in f.files}
    angular=retained_full_q_angular_space(ROOT);rows=[];output_archives={};arrays={}
    out.mkdir(parents=True)
    for side in ('incoming','outgoing'):
        base=load_finite_normal_endpoint('artifacts/muon_parent_gauge_geometry_correction_20261010/finite_moving_trace_run_1',side=side,repository=ROOT)
        hashes.update(base['input_hashes'])
        lambda_H=base['representation']['scalar_matching']['lambda_H']
        primal,phase,velocity,contact=[loaded[side,label]for label in ('primal_and_source','phase','velocity','contacts')]
        L=float(primal['times'][-1]);side_record=next(x for x in md['records']if x['side']==side)
        for fraction in (.25,.75):
            u=L*fraction;hit=np.flatnonzero(primal['times']==u);rhs=np.flatnonzero(phase['times']==u)
            if len(hit)!=1 or len(rhs)!=1:raise ValueError('actual retained non-kink source/action node required')
            j,i=int(hit[0]),int(rhs[0]);raw=primal['raw_fields'][j]
            source_gauge=contact['source_trace'][i].T.reshape(8,5,4,20)
            source_H=phase['state'][i,320:400].T.reshape(8,4,20)
            source_Hdot=velocity['velocity'][i,320:400].T.reshape(8,4,20)
            # Rate support participates in this actual action application,
            # so a nonzero rate n3 cannot be dropped by a value-only guard.
            support=np.where((source_H!=0)|(source_Hdot!=0),1.,0.)
            image=higgs_magnetic_source_image_space(angular,source_gauge,support)
            maximum=image['source_maximum_level'];ids=[k for k,l in enumerate(angular['harmonic_labels'])if l[0]<=maximum]
            geo=intrinsic_m4_weight_jet(12,raw[:37],raw[37:74],raw[74:98],source_value=raw[98],source_rate=raw[99])
            weights=[geo[k].value for k in ('wT','wS','wV')]
            ghost=smooth_ghost_temporal_values(np.array([u]),L)[0]
            b=2*min(fraction,1-fraction);bp=2/L if fraction<.5 else -2/L
            tf=np.array([b,bp,ghost[0,0],ghost[0,1],ghost[1,0],ghost[1,1]])
            wallrad=ghost_radial_values(np.array([WALL]))[0]
            r=intrinsic_coupled_magnetic_source_point(weights=weights,H=raw[-8:-4],Hdot=raw[-4:],
                connection=primal['wall_background_values'][j],odd_derivatives=image['odd_derivative_matrices'],
                even_derivatives=image['even_derivative_matrices'],source_derivatives=image['source_derivative_matrices'],
                gaunt=image['gaunt_even_odd_source'],temporal=tf,wall_radial=wallrad,
                source_gauge=source_gauge[:3,:,:,ids],source_H=source_H[:3,:,ids],source_Hdot=source_Hdot[:3,:,ids],
                lambda_H=lambda_H,
                nu_squared_action=md['action_parameters']['nu_squared_action'])
            tag=side+'_quarter_'+str(int(fraction*4))
            # Preserve every source row while splitting dense blocks below
            # the inherited per-file public artifact cap.
            for A in range(3):
                data={k:r[k][A]for k in ('intrinsic_coupled_delta_Hessian_even_odd','intrinsic_coupled_delta_Gram_even_odd','source_covariant_first_image_even_odd')}
                name=tag+'_axis_'+str(A)+'.npz';p=out/name;deterministic_archive(p,data)
                if p.stat().st_size>10*1024**2:raise ValueError('complete source axis archive exceeds cap')
                output_archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest(),arrays=sorted(data))
            arrays[tag+'_raw_fields']=raw;arrays[tag+'_actual_wall_connection']=primal['wall_background_values'][j]
            arrays[tag+'_source_H']=source_H;arrays[tag+'_source_Hdot']=source_Hdot;arrays[tag+'_source_wall_gauge']=source_gauge
            arrays[tag+'_intrinsic_weights']=np.array(weights);arrays[tag+'_temporal_image']=tf;arrays[tag+'_wall_radial_image']=wallrad
            arrays[tag+'_image_motion_norms']=r['dependent_gauge_scalar_rate_image_motion_norms']
            rows.append(dict(side=side,response_time=float(u),coordinate_time=float(primal['coordinate_times'][j]),fraction=fraction,
                source_maximum_level=maximum,source_n3_and_rate_bit_exact_zero=maximum==1,
                lambda_H=lambda_H,lambda_H_owner='retained same finite-normal representation scalar_matching.lambda_H',
                source_block_shape=list(r['intrinsic_coupled_delta_Hessian_even_odd'].shape),
                source_H_norm=float(np.linalg.norm(source_H[:3])),source_H_rate_norm=float(np.linalg.norm(source_Hdot[:3])),
                source_gauge_norm=float(np.linalg.norm(source_gauge[:3])),
                intrinsic_coupled_source_block_norm=float(np.linalg.norm(r['intrinsic_coupled_delta_Hessian_even_odd'])),
                intrinsic_source_Gram_block_norm=float(np.linalg.norm(r['intrinsic_coupled_delta_Gram_even_odd'])),
                dependent_gauge_scalar_rate_image_motion_norms=r['dependent_gauge_scalar_rate_image_motion_norms'].tolist(),
                product_image_residual_max=float(np.max(image['scalar_product_image_residual']))))
            print(json.dumps(rows[-1],sort_keys=True),flush=True)
    p=out/'source_inputs.npz';deterministic_archive(p,arrays);output_archives[p.name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest(),arrays=sorted(arrays))
    sources=[source_record(p,names)for p,names in (
        ('src/bhsm/interface/muon_coupled_higgs_magnetic_source.py',['coupled_intrinsic_wall_images','intrinsic_coupled_magnetic_source_point']),
        ('src/bhsm/interface/muon_parent_positive_coupled_temporal.py',['intrinsic_coupled_point_form','paired_scalar_orbit_maps']),
        ('src/bhsm/interface/muon_intrinsic_higgs_positive_source.py',['higgs_magnetic_source_image_space']),
    )]
    for r in sources:hashes[r['path']]=r['sha256']
    hashes[Path(__file__).relative_to(ROOT).as_posix()]=sha256(Path(__file__).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in hashes.items()):raise RuntimeError('source changed during intrinsic application')
    result=dict(classification='EVALUATED_CORRECTED_MAGNETIC_COUPLED_INTRINSIC_HIGGS_SOURCE_IMAGE_BLOCKS',
        input_hashes=hashes,source_records=sources,array_archives=output_archives,records=rows,
        sector='intrinsic coupled Higgs weak Hessian and Gram source variation; all dependent DG field images kept',
        temporal_scope='actual quarter/three-quarter nodes of corrected chronological phase; no tent derivative at its midpoint kink selected',
        normalization='same real2Re intrinsic scalar action prefactor2*w_mu/(2pi²), source magnetic e already included once',
        bulk_YM_curvature_Lorenz_ghost_derivatives_not_filled_zero=True,
        one_coupled_field_Green_source_derivative_composed=False,
        physical_P_strat_quantum_statistics_LSZ_Pauli_completed=False,physical_a_mu=None,physical_g_mu=None,
        error_scope='binary64 actual stored field/source/Gaunt point application; no outward field/action/Gaunt formation or time/radial integration bound; no physical observable uncertainty assigned')
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return dict(classification=result['classification'],array_archives=output_archives,records=rows)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--source',type=Path,default=Path('artifacts/muon_corrected_profile_magnetic_response_20261011/run_1'))
    a=p.parse_args();print(json.dumps(materialize(a.output,source=a.source),sort_keys=True))
