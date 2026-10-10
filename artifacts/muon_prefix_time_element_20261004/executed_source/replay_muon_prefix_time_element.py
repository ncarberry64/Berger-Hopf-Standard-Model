"""Evaluate one owned non-cut temporal element; consume cached first actions."""
from __future__ import annotations
import argparse,hashlib,json,os,subprocess,sys,time
from pathlib import Path

os.environ.setdefault('OPENBLAS_NUM_THREADS','1');os.environ.setdefault('OMP_NUM_THREADS','1')
import numpy as np


def read(p):
    with np.load(p,allow_pickle=False) as z:return {k:np.array(z[k]) for k in z.files}


def save(p,j):p.write_bytes((json.dumps(j,indent=2,sort_keys=True,allow_nan=False)+'\n').encode())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def run(root,out):
    if out.exists():raise FileExistsError('new output required; existing caches immutable')
    out.mkdir(parents=True);began=time.perf_counter();sys.path.insert(0,str(root/'src'))
    from bhsm.interface.muon_prefix_time_element import (interior_first_actions,attached_geometry,
        moving_coefficients,spatial_weak_actions,assemble_time_element,consume_prefix_element)
    from bhsm.interface.muon_cut_inverse_coverage import encoded
    from flint import arb,ctx
    b=root/'artifacts/flagship_integration';c=root/'artifacts/muon_coupled_cut_forms_20261004'
    refs=dict(step=b/'BHSM_N12_C2_LOHNER_STEP_1222.npz',record=b/'BHSM_N12_C2_LOHNER_STEP_1222.json',
        branch=b/'BHSM_N12_C2_LOHNER_BORDERED_MATRIX_1221.npz',
        field=b/'BHSM_N12_C2_LOHNER_FIXED_S_FIELD_1221.npz',field_report=b/'BHSM_N12_C2_LOHNER_FIXED_S_FIELD_1221.json',
        growth=b/'BHSM_N12_C2_LOHNER_GROWTH_1221.json',response=b/'BHSM_N12_C2_LOHNER_RESPONSE_BALL_1221.json',
        cut=c/'run_1/coupled_cut_source_actions.npz',cut_receipt=c/'run_1/result.json',
        radial=root/'artifacts/muon_radial_inclusion_action_20261004/replay_reference/radial_source_action_and_interface.npz',
        norm=root/'artifacts/muon_radial_inclusion_action_20261004/replay_reference/full_normalization.json',
        geometry=root/'artifacts/muon_parent_geometry_20261001/replay_reference/local_parent_velocity_density.npz',
        contact=root/'artifacts/muon_parent_source_contact_20261003/replay_reference/parent_source_contact.npz',
        corrected=root/'artifacts/muon_parent_source_rate_20261003/replay_reference/parent_source_rate_corrected.npz',
        frozen=c/'run_1/frozen_local.json',ledger=c/'run_1/inherited_contribution_ledger.json',
        module=root/'src/bhsm/interface/muon_prefix_time_element.py',script=Path(__file__),
        clock_producer=root/'scripts/certify_n12_c2_cancelled_field_lohner_step.py',
        first_action_producer=root/'scripts/audit_n12_c2_bordered_hard_response_matrix.py',
        fixed_field_producer=root/'scripts/audit_n12_c2_exact_center_fixed_s_field_matrix.py',
        domain=root/'src/bhsm/interface/action_extension_global_spin_reset_ae2.py')
    save(out/'input_hashes.json',{k:dict(path=str(p.relative_to(root)),sha256=sha(p)) for k,p in refs.items()})
    git=lambda *a:subprocess.check_output(['git','-C',str(root),*a],text=True).strip()
    save(out/'workspace.json',dict(head=git('rev-parse','HEAD'),branch=git('branch','--show-current'),status=git('status','--short'),
        starting_revision='58e5941b38faae24e67be87aa55537aadeec656e',reference='524ed90689bd5923c249bba2e699abf627e703cd'))
    data={k:read(refs[k]) for k in ('step','branch','field','cut','radial','geometry','contact','corrected')}
    rec={k:json.loads(refs[k].read_text()) for k in ('record','field_report','growth','response','norm','cut_receipt')}
    # Reuse the established actual source image; do not repeat its quotient.
    basis={}
    S=data['cut']['independent_source_map']
    for n in (1,3):
        xi=data['contact'][f'Xi_A_unit_n{n}'][:,:,data['corrected']['source_image_probe_columns']]
        flat=xi.transpose(1,3,4,0,2).reshape(64,n+1,n+1,32)
        basis[n]=np.einsum('omki,ij->omkj',flat,S)
    cache={};coeff_rows={};state_rows={};geom_rows={};point_receipts={}
    def point(x):
        if x in cache:return cache[x]
        f=interior_first_actions(x,data['step'],rec['record'],data['branch'],data['field'],rec['field_report'],rec['growth'],rec['response'])
        geometry=attached_geometry(f['y'],data['step']['endpoint_predictor_center'],data['geometry'])
        s,arrays,receipt=moving_coefficients(f,geometry,data['contact'],data['cut'],rec['norm'],data['geometry'])
        p=spatial_weak_actions(s,basis,data['radial'],data['cut'],receipt)
        p['tau_x']=f['tau_nom'];p['tau_x_interval']=f['tau_x'];p['first_action']=f
        cache[x]=p;coeff_rows[x]=arrays;state_rows[x]=f['y'];geom_rows[x]=geometry
        point_receipts[x]=dict(field=f['result'],attachment=receipt)
        save(out/f'point_{len(cache):02d}.json',point_receipts[x])
        return p
    # No cut endpoint is reevaluated: all coefficient quadrature points are
    # strictly inside the inherited1222 descriptor segment.
    sets={}
    for n in (5,3):
        gx,gw=np.polynomial.legendre.leggauss(n);xx=(gx+1)/2;ww=gw/2
        pp=[point(float(x)) for x in xx]
        if n==5:scale=pp[n//2]['tau_x']
        K,M,polys=assemble_time_element(xx,ww,pp,scale)
        sets[n]=dict(x=xx,w=ww,points=pp,K=K,M=M,polys=polys)
        save(out/'stage.json',dict(stage=f'new{n}-point temporal density interpolant integrated',
            saved_first_actions_consumed=len(cache),new_Hessians=0,new_98_direction_campaigns=0,
            old_cut_contractions=0))
    high,low=sets[5],sets[3]
    assembled,assembly=consume_prefix_element(high['K'],high['M'],data['cut'],scale)
    # Element face loads are duals in the actual temporal Cauchy pairing;
    # right-face action is reused from the saved cut cotangent, not replayed.
    left=point(0.0);d=S.shape[1];dim=2*d
    left_velocity=left['B'].conj().T[:,d:2*d]@data['cut']['source_coordinates']
    right_velocity=data['cut']['rhs_K'][2*d:4*d]
    assembled.update(left_trial_outward_conormal_dual=-left_velocity,
        right_trial_outward_conormal_dual=right_velocity,left_trace_Cauchy_Gram=left['Ms'],
        right_trace_Cauchy_Gram=data['cut']['local_cut_Cauchy_Wp'])
    # source(phi0+phi1) is formed as exact(1,0) in value/derivative coordinates
    # BEFORE F0/F1 application; the temporal density polynomial is explicit.
    source=data['cut']['source_coordinates'];src=assembled['source_constant_coefficients']
    energy_direct=sum(float(w*p['tau_x']*np.vdot(source,p['A'][d:2*d,d:2*d]@source).real)
        for w,p in zip(high['w'],high['points']))
    duration_nom=sum(w*p['tau_x'] for w,p in zip(high['w'],high['points']))
    ctx.prec=192;sigma0=arb(rec['record']['segment']['signed_descriptor_start']);hs=arb(rec['record']['segment']['signed_descriptor_step'])
    # A whole-cell clock enclosure integrates sigma exactly and uses the
    # inherited lapse/Delta box. No quadrature-discrepancy-as-bound claim.
    fmid=high['points'][2]['first_action'];db=arb(fmid['result']['Delta_box']['arb'])
    nblo,nbhi=rec['record']['domain']['lapse_interval'];nb=arb((nblo+nbhi)/2,(nbhi-nblo)/2)
    duration_box=nb*(sigma0*hs+hs*hs/2)/db
    arrays=dict(**assembled,temporal_x=high['x'],temporal_weights=high['w'],temporal_basis_scale=np.array(scale),
        temporal_density_A=np.array([p['tau_x']*p['A'] for p in high['points']]),
        temporal_density_B=np.array([p['B'] for p in high['points']]),
        temporal_density_C=np.array([p['C']/p['tau_x'] for p in high['points']]),
        temporal_density_M=np.array([p['tau_x']*p['M'] for p in high['points']]),
        source_history_states=np.array([state_rows[float(x)] for x in high['x']]),
        lower_order_element_K=low['K'],lower_order_element_M=low['M'],
        clock_tau_x=np.array([p['tau_x'] for p in high['points']]),
        action_q_tau=np.array([p['first_action']['qnom'] for p in high['points']]),
        action_multiplier_tau=np.array([p['first_action']['mnom'] for p in high['points']]))
    for k in ('a0','Lnu_direct','C_tau_nodes','r_tau_nodes','u','p'):
        arrays[k]=np.array([coeff_rows[float(x)][k] for x in high['x']])
    for k,v in high['polys'].items():arrays[f'Legendre_density_{k}']=v
    for n in (1,3):arrays[f'actual_source_Dp_n{n}']=np.array([p[f'Dp_n{n}'] for p in high['points']])
    np.savez_compressed(out/'prefix_time_element.npz',**arrays)
    save(out/'temporal_point_receipts.json',{str(x):point_receipts[x] for x in sorted(point_receipts)})
    delta=lambda a,b:float(np.linalg.norm(a-b))
    result=dict(classification='evaluated non-cut local Dirac temporal weak element consumed in inherited prefix trace assembly',
        descriptor_domain=[rec['record']['segment']['signed_descriptor_start'],rec['record']['segment']['signed_descriptor_end']],
        branch=24,temporal_region='accepted physical prefix1222 immediately before cut; not an added past arm',
        physical_history_is_predictor=False,representative='saved quadratic predictor plus whole-step Lohner/fiber enclosure',
        nominal_proper_duration=duration_nom,proper_duration_whole_cell_enclosure=encoded(duration_box),
        temporal_basis=dict(phi0='1',phi1='scale*(x-1/2)',scale=scale,
            coordinate='x=(sigma-sigma_start)/h_sigma; physical derivative=partial_x/clock_tau_x',
            scaling='fixed action-derived midpoint clock Jacobian; congruently applied to forms, source duals and endpoint traces',
            no_diagonal_regularizer=True),
        temporal_integral=dict(density_interpolant_degree=4,weak_integrand_max_degree=6,
            Gauss_degree_of_exactness=9,integrated_density_polynomial=True,
            quadrature_exactness='exact polynomial identity, up to unvalidated matrix arithmetic; not certified physical-history integration',
            interpolation_comparison=dict(K_absolute=delta(high['K'],low['K']),
                K_relative=delta(high['K'],low['K'])/np.linalg.norm(high['K']),
                M_absolute=delta(high['M'],low['M']),
                source_energy_difference=float(np.vdot(src,(high['K']-low['K'])@src).real),certified_remainder=False)),
        direct_source_history_energy=energy_direct,
        direct_vs_assembled_source_energy_difference=abs(energy_direct-assembly['source_element_energy']),
        element_Hermitian_relative_residual=float(np.linalg.norm(high['K']-high['K'].conj().T)/np.linalg.norm(high['K'])),
        a0_time_variation_norm=float(np.linalg.norm(arrays['a0'][-1]-arrays['a0'][0])),
        source_first_lapse_rate_range=[float(np.min(arrays['action_multiplier_tau'][:,0])),float(np.max(arrays['action_multiplier_tau'][:,0]))],
        assembly=assembly,
        error_scope=dict(first_action='point receipts enclose saved Taylor and whole-step line/response/trajectory errors; no new raw eigenvalue',
            clock='whole-cell original-domain Delta interval enlarged for explicit sigma dependence',
            temporal_interpolation='degree4 density model integrated; degree2 comparison is not a rigorous remainder',
            spatial_quadrature='same saved8-point grid; no old cut quadrature refinement or new certified radial error',
            history='physical fiber lies in inherited whole-step enclosure; nominal temporal forms not certified over that enclosure',
            continuum=None,matrix_roundoff=None,full_stratified_operator=None),
        execution=dict(new_first_action_campaigns=0,non_cut_field_points=len(cache),old_cut_replays=0,
            source_image_quotients_replayed=0,old_guards_replayed=0,full_exterior_solutions=0,heat=0),
        physical_a_mu=None,physical_g_mu=None,elapsed_seconds=time.perf_counter()-began)
    save(out/'result.json',result);save(out/'assembly.json',assembly)
    save(out/'checkpoint.json',dict(id='BHSM_MUON_INHERITED_PREFIX_TIME_ELEMENT_20261004',
        arrays='prefix_time_element.npz',result='result.json',point_receipts='temporal_point_receipts.json',
        assembled='one local Dirac prefix element with full W/p frame and moving complement',
        solved='no completed exterior source equation',physical_prediction=False))
    save(out/'frozen_local.json',json.loads(refs['frozen'].read_text()))
    save(out/'inherited_native_ledger.json',json.loads(refs['ledger'].read_text()))
    save(out/'output_hashes.json',{p.name:sha(p) for p in out.iterdir() if p.is_file()})
    print(json.dumps({k:result[k] for k in ('nominal_proper_duration','proper_duration_whole_cell_enclosure',
        'direct_source_history_energy','a0_time_variation_norm','source_first_lapse_rate_range','temporal_integral','execution','elapsed_seconds')},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repository',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();run(a.repository.resolve(),a.output.resolve())
