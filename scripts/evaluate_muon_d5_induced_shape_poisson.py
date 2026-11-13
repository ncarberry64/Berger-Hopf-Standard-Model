"""Consume actual child direct+induced shape in its SAME finite D5 field action.

The unit normal amplitude is a computational source. This application keeps
all represented coefficient rows and full rate work; it does not turn its
raw radial point boundary into the physical retarded exterior or a pole.
"""
from pathlib import Path
from hashlib import sha256
import argparse, json, sys
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src')); sys.path.insert(0, str(ROOT/'scripts'))
from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase
from bhsm.interface.muon_holomorphic_current_source import holomorphic_current_stage, two_term_complex_sum
from bhsm.interface.muon_holomorphic_d5_trace_action import d5_trial_stage_coefficients, d5_sigma_foliation_eta, d5_material_green_trace
from bhsm.interface.muon_d5_shape_coefficient_source import d5_coefficient_source
from bhsm.interface.muon_d5_weak_shape_source import fixed_radial_d5_weak_source
from bhsm.interface.muon_d5_fixed_radial_source_consumption import fixed_field_source_and_frame,response_raw_slots
from bhsm.interface.muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace, moving_d5_material_trace_frame
from bhsm.interface.muon_birth_trace_enriched_action import trace_enriched_radial_basis
from bhsm.interface.muon_parent_retarded_hypercharge import WALL
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
from evaluate_muon_d5_finite_trace_pole_match import clean


def materialize(source, output, sector, point, energy):
    out = ROOT/output
    if out.exists(): raise FileExistsError('preserve every same-action source consumption')
    pins, archives = {}, {}
    def read(folder, name):
        p = ROOT/folder/name; pins[p.relative_to(ROOT).as_posix()] = sha256(p.read_bytes()).hexdigest()
        if p.suffix == '.json': return json.loads(p.read_bytes())
        with np.load(p) as z: return {k: z[k].copy() for k in z.files}
    receipt = read(source, 'result.json'); pins.update(receipt['input_hashes'])
    data = read(source, f'{sector}_{point}_induced_and_total.npz')
    work = read(source, f'{sector}_complete_temporal_and_born_work.npz')
    phase = load_profile_preserving_phase('artifacts/muon_inherited_finite_normal_phase_20261011/run_1', repository=ROOT)
    pins.update(phase['input_hashes']); rep = phase['representation']; full = full_d5_localized_lepton_trace()
    dirs,labels = response_raw_slots(data,sector)
    raw, parent = data['actual_raw_pair'][1], data['actual_raw_pair'][0]; refs = data['actual_reference_pair']
    zeros = np.zeros_like(dirs); refzeros = np.zeros((2,268,len(labels)), complex)
    stage = holomorphic_current_stage(raw, dirs, parent, zeros, refs, refzeros, rep, side='child')
    wallrep = dict(rep, rho=np.array([WALL]), gauge_basis=rep['wall_trace_map'].transpose(2,0,1)[None,:,None])
    c = d5_trial_stage_coefficients(raw,dirs,parent,zeros,refs,refzeros,rep,rep['rho'],side='child')
    cw = d5_trial_stage_coefficients(raw,dirs,parent,zeros,refs,refzeros,wallrep,wallrep['rho'],side='child')
    wall_B, wall_Br = trace_enriched_radial_basis(rep,np.array([WALL]))
    if np.max(abs(wall_B-np.array([[0,0,0,1]]))) > 2e-12:
        raise ValueError('named original three interior profiles and unit wall lift required before field Schur')
    out.mkdir(parents=True)
    def save(name, arrays):
        p = out/name; _compressed_npz(p,{k:v for k,v in arrays.items() if isinstance(v,np.ndarray)})
        if p.stat().st_size >= 10*1024**2: raise ValueError('compact source/operator split required')
        archives[name] = dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    save('actual_full18_direct_induced_total_and_rate_work.npz',dict(stage,
        actual_raw_pair=data['actual_raw_pair'], actual_reference_pair=refs, actual_coordinate_time=data['actual_coordinate_time'],
        source_directions_high_low=dirs, source_slot_order=np.array(labels),
        full504_effective_source=data['full504_effective_source'],full504_rate_conormal=data['full504_rate_conormal'],
        original_child_gradient=data['original_child_gradient'],literal_child_Hessian=data['literal_child_Hessian'],**work))
    save('actual_radial_geometry_density_source.npz',dict(c))
    records = []
    for eps in (1,-1):
        for branch in ('particle','conjugate'):
            gamma = full['gamma5D_'+branch]; G0 = np.kron(gamma[0],np.eye(16))
            generators = full['unitTr16_gauge_particle']
            if branch == 'conjugate': generators = generators.conj() # FIXED representation only
            normal = d5_sigma_foliation_eta(c,gamma=gamma,carrier_count=16,angular_count=1,sheet_orientation=eps)
            normal_wall = d5_sigma_foliation_eta(cw,gamma=gamma,carrier_count=16,angular_count=1,sheet_orientation=eps)
            weak, weakE = [], []
            # Exact unsquared E coefficient, not a difference of large D(E).
            DE = np.array([G0*s/n for s,n in zip(c['surface_proper_clock_rate'],c['lapse'])])
            dDE = np.array([[G0*(ds/n-s*dn/n**2) for s,n,ds,dn in zip(c['surface_proper_clock_rate'],
                c['lapse'],c['surface_proper_clock_rate_first'][k],c['lapse_first'][k])] for k in range(len(labels))])
            for k in range(len(labels)):
                operand = d5_coefficient_source(c,gamma=gamma,generators=generators,
                    eta=normal['sigma_normal_eta_contact'],eta_first=normal['sigma_normal_eta_contact_first'][k],
                    energy=energy,sheet_orientation=eps,source_slot=k)
                kw = dict(volume=c['volume_density'],volume_first=c['volume_density_first'][k],
                    weights=rep['radial_quadrature'],radial_values=rep['radial_value_map'],
                    radial_first=rep['radial_derivative_map'],time_Clifford=G0)
                weak.append(fixed_radial_d5_weak_source(operand,**kw))
                eoperand = dict(original_D5_zero_order=DE,direct_source_D5_zero_order=dDE[k],
                    original_D5_radial_principal=np.zeros_like(DE),direct_source_D5_radial_principal=np.zeros_like(DE))
                weakE.append(fixed_radial_d5_weak_source(eoperand,**kw))
            K = weak[0]['original_fixed_radial_weak_action']; KE = weakE[0]['original_fixed_radial_weak_action']
            dK = np.array([a['direct_shape_fixed_radial_weak_action'] for a in weak])
            dKE = np.array([a['direct_shape_fixed_radial_weak_action'] for a in weakE])
            prefix = f'eta_{eps:+d}_{branch}'
            save(prefix+'_original_field_and_energy.npz',dict(original_fixed_radial_action=K,
                original_fixed_radial_action_energy=KE,wall_basis_value=wall_B,wall_basis_coordinate_radial_first=wall_Br))
            for j,name in enumerate(('direct','induced','total')):
                sh, sl = two_term_complex_sum(dK[2*j],dK[2*j+1]); eh, el = two_term_complex_sum(dKE[2*j],dKE[2*j+1])
                save(prefix+'_'+name+'_field_source_high_low.npz',dict(source_high=dK[2*j],source_low=dK[2*j+1],
                    source_energy_high=dKE[2*j],source_energy_low=dKE[2*j+1],complete_source_high=sh,
                    complete_source_low=sl,complete_source_energy_high=eh,complete_source_energy_low=el))
            green = d5_material_green_trace(cw,gamma=gamma,carrier_count=16,angular_count=1,
                sheet_orientation=eps,point_index=0)
            n0, n4 = normal_wall['sigma_normal_timelike_component'][0],normal_wall['sigma_normal_radial_component'][0]
            U = n0/n4
            dU = (normal_wall['sigma_normal_timelike_component_first'][:,0]*n4-
                n0*normal_wall['sigma_normal_radial_component_first'][:,0])/n4**2
            boost = moving_d5_material_trace_frame(-eps*U,0,full_representation=full)
            idx = slice(0,64) if branch == 'particle' else slice(64,128)
            S, SI = boost['spin_boost128'][idx,idx],boost['spin_boost_inverse128'][idx,idx]
            A = G0 @ SI @ G0
            dS, dA = [], []
            for v in dU:
                jet = moving_d5_material_trace_frame(-eps*U,-eps*v,full_representation=full)
                dS.append(jet['spin_boost_first128'][idx,idx]);dA.append(G0@jet['spin_boost_inverse_first128'][idx,idx]@G0)
            app = fixed_field_source_and_frame(K,KE,dK,dKE,A,S,np.array(dA),np.array(dS),
                green['original_Dirac_bar_Green_matrix'],green['original_Dirac_bar_Green_matrix_first'])
            arrays = dict(app,source_slot_order=np.array(labels),actual_normal_velocity=np.array(U),
                actual_normal_velocity_first=dU,raw_Green=green['original_Dirac_bar_Green_matrix'],
                raw_Green_first=green['original_Dirac_bar_Green_matrix_first'],right_Spin_map=S,left_coefficient_Spin_map=A,
                right_Spin_first=np.array(dS),left_coefficient_Spin_first=np.array(dA),
                same_field_energy_coefficient_comparison=np.array(max(np.max(abs(a['original_fixed_radial_weak_action']-KE)) for a in weakE)))
            for key in ('source_field_boundary_contact','complete_source_energy_return','adapted_complete_source',
                        'adapted_complete_source_energy','adapted_complete_Green_source'):
                for j,name in enumerate(('direct','induced','total')):
                    high,low=two_term_complex_sum(app[key][2*j],app[key][2*j+1])
                    arrays[name+'_'+key+'_high']=high;arrays[name+'_'+key+'_low']=low
            source_images=('original_raw_field_Poisson_source','original_literal_left_field_Poisson_source',
                'original_raw_field_Poisson_source_energy','original_literal_left_field_Poisson_source_energy',
                'original_right_source_field_rows','original_left_source_field_rows',
                'original_right_source_energy_field_rows','original_left_source_energy_field_rows')
            for j,name in enumerate(('direct','induced','total')):
                save(prefix+'_'+name+'_full_source_Poisson_images_and_rows.npz',
                    {key:arrays[key][2*j:2*j+2] for key in source_images})
            save(prefix+'_same_field_Poisson_energy_Spin_and_wall_return.npz',
                {key:value for key,value in arrays.items() if key not in source_images})
            record=dict(eta_sheet=eps,representation=branch,original_field_norm=float(np.linalg.norm(K)),
                original_field_energy_norm=float(np.linalg.norm(KE)),raw_field_boundary_norm=float(np.linalg.norm(app['finite_raw_field_boundary_equation'])),
                raw_field_boundary_energy_norm=float(np.linalg.norm(app['finite_raw_field_boundary_equation_energy'])),
                original_right_field_rows_max=float(np.max(abs(app['original_right_field_rows']))),
                original_left_field_rows_max=float(np.max(abs(app['original_literal_left_field_rows']))),
                original_right_energy_rows_max=float(np.max(abs(app['original_right_energy_field_rows']))),
                original_left_energy_rows_max=float(np.max(abs(app['original_literal_left_energy_field_rows']))),
                original_right_source_rows_max=float(np.max(abs(app['original_right_source_field_rows']))),
                original_left_source_rows_max=float(np.max(abs(app['original_left_source_field_rows']))),
                original_right_source_energy_rows_max=float(np.max(abs(app['original_right_source_energy_field_rows']))),
                original_left_source_energy_rows_max=float(np.max(abs(app['original_left_source_energy_field_rows']))),
                normal_wall_material_velocity_difference=U-cw['material_wall_velocity'][0],
                total_minus_direct_induced_field_first_norm=float(np.linalg.norm(dK[4]+dK[5]-dK[0]-dK[1]-dK[2]-dK[3])),
                sources=[dict(channel=name,raw_weak_source_norm=float(np.linalg.norm(dK[2*j]+dK[2*j+1])),
                    raw_weak_low_norm=float(np.linalg.norm(dK[2*j+1])),
                    complete_adapted_boundary_source_norm=float(np.linalg.norm(app['adapted_complete_source'][2*j]+app['adapted_complete_source'][2*j+1])),
                    complete_adapted_boundary_energy_source_norm=float(np.linalg.norm(app['adapted_complete_source_energy'][2*j]+app['adapted_complete_source_energy'][2*j+1])),
                    complete_signed_wall_return_source_norm=float(np.linalg.norm(app['adapted_complete_Green_source'][2*j]+app['adapted_complete_Green_source'][2*j+1])))
                    for j,name in enumerate(('direct','induced','total'))])
            records.append(record);print(json.dumps(clean(record),sort_keys=True),flush=True)
    # SH is a once-only intrinsic fixed point-trace density coefficient.
    # No physical scalar normal-mode first or exterior trace map is inferred.
    N,R=stage['induced_lapse'].item(),stage['R4'].item();density=N*R**3
    dd=stage['induced_lapse_first']*R**3+3*N*R**2*stage['R4_first']
    seam=-density*stage['fixed_Y_mass'];dseam=-dd[:,None,None]*stage['fixed_Y_mass']-density*stage['fixed_Y_mass_first']
    save('once_only_SH_fixed_point_trace_density_source.npz',dict(surface_density=np.array(density),surface_density_first=dd,
        fixed_Y_seam_coefficient=seam,fixed_Y_seam_coefficient_first=dseam,source_slot_order=np.array(labels)))
    for name,module in sorted(sys.modules.items()):
        p=getattr(module,'__file__',None)
        if name.startswith('bhsm.') and p and Path(p).is_relative_to(ROOT):
            p=Path(p);pins[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    for p in (Path(__file__),ROOT/'tests/test_muon_d5_fixed_radial_poisson.py',ROOT/'tests/test_muon_d5_fixed_radial_source_consumption.py'):
        pins[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    if any(sha256((ROOT/k).read_bytes()).hexdigest()!=v for k,v in pins.items()):
        raise ValueError('same source/action/history/representation required')
    result=dict(classification='EVALUATED_SAME_COMPLEX_CHILD_DIRECT_INDUCED_D5_FIELD_POISSON_E_AND_SIGNED_WALL_SOURCE',
        input_hashes=pins,archives=archives,records=records,sector=sector,point=point,energy=energy,
        actual_coordinate_time=data['actual_coordinate_time'].item(),source_slot_order=labels,
        actual_source_raw_norms=[float(np.linalg.norm(dirs[:,2*j]+dirs[:,2*j+1])) for j in range(3)],
        actual_source_low_raw_norms=[float(np.linalg.norm(dirs[:,2*j+1])) for j in range(3)],
        original_birth226_max=receipt['original_birth226_max'],original_all67_work=receipt['original_all67_work'],
        full_child_rate_work=work['complete_child_source_work'].item(),born_parameter_source_cotangent_norm=float(np.linalg.norm(work['born_parameter_source_cotangent'])),
        once_only_fixed_trace_SH_source_norms=[float(np.linalg.norm(dseam[2*j]+dseam[2*j+1])) for j in range(3)],
        source_equation=('actual source-complete original358/146 response; total raw=b+induced before coefficient, density and finite field projection' if sector=='base' else
            'common gamma coefficient response; total raw=induced, direct normal shape incidence zero, no second b or independent child gamma family'),
        field_equation='raw-wall finite Gamma=L K P, Gamma_E=L K_E P; mixed source/E=L_E dK P+L dK_E P+L dK P_E',
        pairing='literal independent left Poisson; K already contains Gamma0; adapted left=Gamma0 S^-1 Gamma0, right=S',
        surface_work='signed outward material-wall Green return kept separately; regular-pole and temporal/retarded domain maps not replaced by this raw-wall value test',
        basis_scope='same original four coordinate radial profiles and full64 Spin4/SM16 per particle/conjugate/oriented-sheet; n0 only, not full strong/radial/angular/domain realization',
        source_scope='actual child direct+induced partial; parent-born source held parameter, incoming OWN response/reset/physical exterior source not yet consumed',
        parent_reference_actual_values_composed_once=True,parent_source_not_future_parent_bulk=True,
        high_low_before_every_product_and_kept_separately=True,unit_source_not_a_nonlinear_shift_or_physical_mode=True,
        energy_is_unsquared_free_matching_variable_not_a_selected_pole=True,
        fixed_coordinate_basis_Vt_zero_exactly_not_physical_normal_first_zero=True,
        normalized_normal_mode_and_physical_trace_domain_firsts_unassigned_not_zero=True,
        retarded_Hcc_or_physical_Bi_Bf_not_replaced_by_finite_field_Poisson=True,
        seam_fixed_trace_coefficient_not_independently_added_kinetic=True,
        physical_Gamma2_pole_charge_LSZ_Pauli_or_native_observable_admitted=False,
        physical_a_mu=None,physical_g_mu=None,error_enclosure=None)
    p=out/'result.json';p.write_text(json.dumps(clean(result),sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(result_sha256=sha256(p.read_bytes()).hexdigest()),sort_keys=True),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,default=Path('artifacts/muon_normal_shape_induced_canonical_response_20261013/run_1'))
    p.add_argument('--sector',choices=('base','area'),default='base');p.add_argument('--point',default='final')
    p.add_argument('--energy',type=float,default=0);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();materialize(a.source,a.output,a.sector,a.point,a.energy)
