"""Execute native local coframe/current and coupled radial overlap contacts."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_owned_native_product_connection import owned_native_product_node
from bhsm.interface.muon_native_local_overlap_matching import (native_local_normal_matching,
    matched_local_square_application,coupled_radial_matching_contacts,radial_scalar_Pauli_covector_probe)
from bhsm.interface.muon_saved_wall_complex_coefficients import saved_original_wall_coefficient_family,forms_at_complex_offset
from bhsm.interface.muon_inherited_normal_readout_frame import phase_normal_readout_frame
from bhsm.interface.muon_profile_preserving_phase_sample import profile_preserving_raw_sample
from evaluate_muon_reached_trace_action import deterministic_archive


def materialize(output):
    out=Path(output);out=out if out.is_absolute()else ROOT/out
    if out.exists():raise FileExistsError('preserve previous matching applications')
    out.mkdir(parents=True);family=saved_original_wall_coefficient_family();refs=dict(family['input_hashes'])
    def pin(p):
        p=Path(p);p=p if p.is_absolute()else ROOT/p;refs[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest();return p
    config=json.loads(pin('artifacts/muon_calibrated_pauli_20261009/inputs.json').read_bytes())
    lifetime=json.loads(pin('artifacts/muon_owned_observation_lifetime_20261011/run_2/result.json').read_bytes())
    vals=config['selected_consumer_values'];e=np.sqrt(4*np.pi*config['alpha_consumer']['value'])
    E=next(a for a in lifetime['records']if a['side']=='incoming')['tree_matching']['conditional_E_kappa_GeV']
    mMu=vals['m_mu_GeV']['value']/E;mE=vals['m_e_GeV']['value']/E;Mh=vals['m_h_GeV']['value']/E
    archives={};records=[]
    def save(obj,name):
        arrays={}
        def pack(v,key):
            if isinstance(v,np.ndarray):arrays[key]=v;return dict(array_key=key,shape=list(v.shape))
            if isinstance(v,dict):return{k:pack(a,key+'_'+k)for k,a in v.items()}
            if isinstance(v,(tuple,list)):return[pack(a,key+'_'+str(j))for j,a in enumerate(v)]
            if isinstance(v,np.generic):return pack(v.item(),key)
            if isinstance(v,complex):return dict(real=v.real,imag=v.imag)
            return v
        r=pack(obj,'data');p=out/name;deterministic_archive(p,arrays)
        if p.stat().st_size>10*1024**2:raise ArithmeticError('split complete arrays before publication')
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest());return r
    for side in('incoming','outgoing'):
        phase=family['arms'][side]['phase'];span=float(phase['receipt']['span'])
        for observation,t in(('birth',0.),('midpoint',span/2),('far',span)):
            for f,m in((1,mMu),(2,mE)):
                node=owned_native_product_node(phase,t,family=f)
                frame=phase_normal_readout_frame(phase,family=f,electric_charge=e,coordinate_time=t)['arguments']
                raw=profile_preserving_raw_sample(phase,t)
                hp=raw['raw_coordinate_time_derivative'][-8:-4]/node['N'];hp=hp[:2]+1j*hp[2:]
                a=native_local_normal_matching(node,frame['H'],frame['wall_connection'],family=f,
                    matched_mass_action=m,electric_charge=e,H_proper_rate=hp)
                square=matched_local_square_application(a,proper_frequency=m,spatial_momentum=[m/3,-m/4,m/5])
                result=dict(side=side,observation=observation,coordinate_time=t,family=f,native_node=node,
                    normal_matching=a,local_square_application=square,actual_wall_connection=frame['wall_connection'],
                    actual_H=frame['H'],actual_H_proper_rate=hp)
                rec=save(result,f'{side}_{observation}_family_{f}_local.npz')
                norms={k:float(np.linalg.norm(a[k]))for k in('normal_body_residual','mass_matching_residual',
                    'full_EM_current_restriction_residual','charged_radial_vertex_residual',
                    'charge_factor_body_commutator','covariant_mass_time_first','covariant_mass_spatial_first','required_mass_matching_load')}
                records.append(dict(kind='native_local_matching',side=side,observation=observation,family=f,
                    archive=f'{side}_{observation}_family_{f}_local.npz',record=rec,norms=norms,
                    square_matching_residual=float(np.linalg.norm(square['square_matching_residual']))))
                print(json.dumps(dict(stage='native_local_matching',side=side,observation=observation,family=f,**norms),sort_keys=True),flush=True)
        # Same original full n1 field polynomial at the common birth germ.
        node=owned_native_product_node(phase,0.,family=1)
        p=forms_at_complex_offset(side,0.,family=family);hr=node['raw_fields'][-8:-4]
        zs=1j*mMu*np.array([.1,.5,.9])/np.sqrt(1-np.array([.1,.5,.9]))
        a=coupled_radial_matching_contacts(p['Lorentz_forms'],p['wall_trace_map'].real,
            p['central_radial_frame_indices'],hr,lapse=node['N'],radius=node['R'],
            matched_scalar_mass_action=Mh,frequencies=zs)
        probes=[]
        Y=float(native_local_normal_matching(node,hr[:2]+1j*hr[2:],
            phase_normal_readout_frame(phase,family=1,electric_charge=e)['arguments']['wall_connection'],
            family=1,matched_mass_action=mMu,electric_charge=e)['fixed_Y'])
        for order in(8,12):
            probe=radial_scalar_Pauli_covector_probe(a,matched_fermion_mass_action=mMu,fixed_Y=Y,quadrature_order=order,
                log_endpoint_edges=[0,4,8,12,16,20,24,32])
            probes.append(probe)
        result=dict(side=side,coordinate_time=0.,common_action_scale_probe_GeV=E,
            conditional_scale_is_physical_common_matching=False,coupled_matching=a,
            calibrated_external_covector_probes=probes,
            probe_order_difference=probes[1]['reached_minus_reference_covector']-probes[0]['reached_minus_reference_covector'])
        rec=save(result,f'{side}_coupled_scalar_matching.npz')
        norms=dict(static_linear_kinetic_contact_norm=np.linalg.norm(a['static_linear_kinetic_matching_contacts']),
            actual_vs_reference_kinetic_norm=np.linalg.norm(a['actual_radial_restricted_kinetic']-a['actual_scalar_kinetic_residue']*np.eye(4)),
            radial_gauge_return_norm=np.linalg.norm(a['zero_application']['radial_gauge_wall_Green']),
            reaction_resolved_equation_residual_max=max(np.max(abs(v['original_reaction_resolved_residual']))for v in[a['zero_application']]+a['probe_applications']),
            reached_covector_real=probes[-1]['reached_radial_covector_value'].real,
            reached_covector_imag=probes[-1]['reached_radial_covector_value'].imag,
            reference_covector_real=probes[-1]['same_coordinate_reference_covector_value'].real,
            reached_minus_reference_real=probes[-1]['reached_minus_reference_covector'].real,
            probe_order_difference_absolute=abs(result['probe_order_difference']))
        norms={k:float(v)for k,v in norms.items()}
        records.append(dict(kind='coupled_radial_matching',side=side,archive=f'{side}_coupled_scalar_matching.npz',record=rec,norms=norms))
        print(json.dumps(dict(stage='coupled_radial_matching',side=side,**norms),sort_keys=True),flush=True)
    # Pin the exact loaded implementation graph, including its fixed action
    # representations. This list is source provenance, not physical inputs.
    for name,module in sorted(sys.modules.items()):
        f=getattr(module,'__file__',None)
        if name.startswith('bhsm.interface.')and f and Path(f).suffix=='.py':pin(f)
    for p in(Path(__file__),'tests/test_muon_native_local_overlap_matching.py','scripts/evaluate_muon_reached_trace_action.py'):pin(p)
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('a consumed owner changed')
    Earms={a['side']:a['tree_matching']['conditional_E_kappa_GeV']for a in lifetime['records']}
    receipt=dict(classification='EVALUATED_OWNED_NATIVE_LOCAL_CURRENT_AND_COUPLED_RADIAL_OVERLAP_MATCHING_CONTACTS',
        input_hashes=refs,archives=archives,records=records,
        common_action_scale_probe_GeV=E,independent_arm_conditional_lifetime_scales_GeV=Earms,
        conditional_scale_ratio=Earms['outgoing']/Earms['incoming'],physical_common_action_scale_selected=False,
        native_product_owner='muon_owned_native_product_connection.owned_native_product_node',
        physical_calibrations='selected recoil alpha, optical/calibrated lepton masses, independent Higgs mass and lifetime; no magnetic/anomaly target',
        matching_scope='actual pointwise native factor/current; original n1 signed coupled scalar/gauge Green with all four canonical radial sources and named frames',
        probe_scope='calibrated local scalar soft covector, matched internal/external mass, trace-average n1 finite Green; it does not replace native interacting fermion propagation or select an exterior/contour',
        own_heat_mean_or_connector_return_removed=False,continuum_overlap_subtracted_from_native_current=False,
        fixed_Y_refitted=False,gauge_H_or_strong_omitted_load_identified_zero=False,
        physical_pole_residue_and_native_domain_matched=False,physical_a_mu=None,physical_g_mu=None,
        error_scope='binary64 source action and matching/contact identities; 8/12 Gauss per log-partition difference is diagnostic, not a contour/pole or numerical enclosure. The reached y>32 tail is not bounded; reference tail alone is bounded analytically. E_kappa probe, mass CT, scalar/gauge returns, native/continuum domain and angular complements remain explicit matching residuals.')
    rp=out/'result.json';rp.write_text(json.dumps(receipt,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return dict(result_sha256=sha256(rp.read_bytes()).hexdigest(),archives=len(archives),records=len(records))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    print(json.dumps(materialize(p.parse_args().output),sort_keys=True),flush=True)
