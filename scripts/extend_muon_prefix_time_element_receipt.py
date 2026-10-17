"""Finalize the persisted time element; no field/spatial/temporal replay."""
from __future__ import annotations
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
import numpy as np


def read(p):
    with np.load(p,allow_pickle=False) as z:return {k:np.array(z[k]) for k in z.files}
def save(p,j):p.write_bytes((json.dumps(j,indent=2,sort_keys=True,allow_nan=False)+'\n').encode())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def run(root,source,out):
    if out.exists():raise FileExistsError('new receipt output required')
    out.mkdir(parents=True);sys.path.insert(0,str(root/'src'))
    from flint import arb,ctx
    from bhsm.interface.muon_cut_inverse_coverage import encoded
    from bhsm.interface.muon_prefix_time_element import consume_prefix_element,attached_geometry
    ctx.prec=192
    a=read(source/'prefix_time_element.npz')
    rr=json.loads((source/'temporal_point_receipts.json').read_text())
    rec=json.loads((root/'artifacts/flagship_integration/BHSM_N12_C2_LOHNER_STEP_1222.json').read_text())
    cut=read(root/'artifacts/muon_coupled_cut_forms_20261004/run_1/coupled_cut_source_actions.npz')
    step=read(root/'artifacts/flagship_integration/BHSM_N12_C2_LOHNER_STEP_1222.npz')
    geo=read(root/'artifacts/muon_parent_geometry_20261001/replay_reference/local_parent_velocity_density.npz')
    measures=[]
    for y in a['source_history_states']:
        g=attached_geometry(y,step['endpoint_predictor_center'],geo)
        xx=(cut['points']-g['rho'][cut['cells']])/np.diff(g['rho'])[cut['cells']]
        val=lambda key:g[key][0,cut['cells']]*(1-xx)+g[key][0,cut['cells']+1]*xx
        nu,C,r=(val(key) for key in ('proper_lapse','C_rho','base_radius'))
        measures.append((2*np.pi**2*nu*C*r**3,2*np.pi**2*C*r**3))
    np.savez_compressed(out/'point_volume_and_Cauchy.npz',
        point_volume_density=np.array([v[0] for v in measures]),
        point_Cauchy_density=np.array([v[1] for v in measures]),
        radial_weights=cut['radial_weights'])
    arrays,assembly=consume_prefix_element(a['element_K'],a['element_M'],cut,float(a['temporal_basis_scale']))
    d=len(cut['source_coordinates']);c=cut['source_coordinates'];src=a['source_constant_coefficients']
    mid=rr['0.5']['field'];dlo,dhi=map(lambda z:arb(float(z)),mid['Delta_box']['interval'])
    db=arb(((dlo+dhi)/2).mid(),((dhi-dlo)/2).upper())
    assert db>0
    slo=arb(rec['segment']['signed_descriptor_start']);hs=arb(rec['segment']['signed_descriptor_step'])
    nlo,nhi=map(lambda z:arb(float(z)),rec['domain']['lapse_interval'])
    nb=arb(((nlo+nhi)/2).mid(),((nhi-nlo)/2).upper())
    duration=nb*(slo*hs+hs*hs/2)/db
    energy=sum(float(w*np.vdot(c,A[d:2*d,d:2*d]@c).real) for w,A in zip(a['temporal_weights'],a['temporal_density_A']))
    result=dict(classification='evaluated non-cut temporal weak element consumed in same prefix trace assembly',
        descriptor_domain=[rec['segment']['signed_descriptor_start'],rec['segment']['signed_descriptor_end']],
        branch=24,temporal_region='inherited accepted prefix1222; no added history arm',
        temporal_point_receipts='run_1/temporal_point_receipts.json',
        first_actions='cached selected-line and response derivatives at original proof center, physical-fiber trajectory enclosed by original whole-step chart',
        nominal_proper_duration=float(a['temporal_weights']@a['clock_tau_x']),
        proper_duration_whole_cell_enclosure=encoded(duration),
        temporal_basis=dict(phi0='1',phi1='scale*(x-1/2)',scale=float(a['temporal_basis_scale']),
            coordinate='x=(sigma-sigma_start)/h_sigma; d/dtau=(1/clock_tau_x)d/dx',
            source_in_unprojected_coordinates=True,no_diagonal_regularizer=True),
        temporal_integral=dict(density_interpolant_degree=4,weak_integrand_max_degree=6,
            Gauss_degree_of_exactness=9,temporal_density_polynomials='run_1/prefix_time_element.npz::Legendre_density_A/B/C/M',
            temporal_integral_completed_in_declared_model=True,
            temporal_interpolation_error=None,
            comparison=dict(K_absolute=float(np.linalg.norm(a['element_K']-a['lower_order_element_K'])),
                K_relative=float(np.linalg.norm(a['element_K']-a['lower_order_element_K'])/np.linalg.norm(a['element_K'])),
                M_absolute=float(np.linalg.norm(a['element_M']-a['lower_order_element_M'])),
                source_energy_difference=float(np.vdot(src,(a['element_K']-a['lower_order_element_K'])@src).real),
                certified_remainder=False)),
        direct_source_history_energy=energy,
        direct_vs_assembled_source_energy_difference=abs(energy-assembly['source_element_energy']),
        a0_time_variation_norm=float(np.linalg.norm(a['a0'][-1]-a['a0'][0])),
        first_lapse_rate_range=[float(min(a['action_multiplier_tau'][:,0])),float(max(a['action_multiplier_tau'][:,0]))],
        element_Hermitian_relative_residual=float(np.linalg.norm(a['element_K']-a['element_K'].conj().T)/np.linalg.norm(a['element_K'])),
        assembly=assembly,
        error_scope=dict(point_and_field='whole-step physical descriptor-fiber enclosure plus cached first-action Taylor remainders, recorded pointwise',
            clock='positive whole-cell lapse/Delta bounds including explicit sigma variation; not a fixed endpoint clock',
            temporal_interpolation='explicit degree4 density model integrated; degree2 comparison not a certified remainder',
            radial_quadrature='same8-point/cell grid and64-cell nodal geometry; no old cut refinement',
            history='trajectory enclosure retained; numerical element not enclosed uniformly over it',
            matrix_roundoff=None,continuum=None,full_stratified=None),
        execution=dict(saved_non_cut_points=len(rr),new_field_campaigns=0,new_raw_eigenvalues=0,
            old_cut_replays=0,old_assembly_guards=0,source_image_quotient_replays=0,
            temporal_models_evaluated=2,full_exterior_solutions=0,native_heat=0),
        receipt_repair='original element and coefficients persisted before a wide-Arb display-string reparse lost positivity in the duration receipt; this extension uses outward bounds without recomputation',
        physical_a_mu=None,physical_g_mu=None)
    save(out/'result.json',result);save(out/'assembly.json',assembly)
    save(out/'input_hashes.json',{p.name:dict(path=str(p),sha256=sha(p)) for p in
        (source/'prefix_time_element.npz',source/'temporal_point_receipts.json',Path(__file__),root/'src/bhsm/interface/muon_prefix_time_element.py')})
    save(out/'checkpoint.json',dict(id='BHSM_MUON_INHERITED_PREFIX_TIME_ELEMENT_20261004',
        result='run_2/result.json',arrays='run_1/prefix_time_element.npz',assembled=assembly,
        next='next same-owner neighboring history action with its own valid descriptor chart and full total trace coupling',physical_prediction=False))
    save(out/'output_hashes.json',{p.name:sha(p) for p in out.iterdir() if p.is_file()})
    print(json.dumps({k:result[k] for k in ('nominal_proper_duration','proper_duration_whole_cell_enclosure',
        'direct_source_history_energy','first_lapse_rate_range','a0_time_variation_norm','temporal_integral')},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repository',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();run(a.repository.resolve(),a.source.resolve(),a.output.resolve())
