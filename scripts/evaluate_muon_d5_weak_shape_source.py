"""Actual density+coefficient direct shape source on fixed original radial tests."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_d5_weak_shape_source import fixed_radial_d5_weak_source
from bhsm.interface.muon_holomorphic_d5_trace_action import d5_trial_stage_coefficients
from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase
from bhsm.interface.muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
from evaluate_muon_d5_finite_trace_pole_match import clean


def materialize(direct_source,output):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve every direct weak source')
    pins={};archives={}
    def read(p):
        p=ROOT/direct_source/p;pins[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
        if p.suffix=='.json':return json.loads(p.read_bytes())
        with np.load(p)as z:return{k:z[k].copy()for k in z.files}
    receipt=read(Path('result.json'));pins.update(receipt['input_hashes']);data=read(Path('actual_full18_current_and_direct_shape.npz'))
    phase=load_profile_preserving_phase('artifacts/muon_inherited_finite_normal_phase_20261011/run_1',repository=ROOT);pins.update(phase['input_hashes'])
    rep=phase['representation'];full=full_d5_localized_lepton_trace();pair=data['actual_raw_pair'];refs=data['actual_reference_pair'];b=data['direct_child_raw_shape']
    c=d5_trial_stage_coefficients(pair[1],b[:,None],pair[0],np.zeros((268,1),complex),refs,np.zeros((2,268,1),complex),rep,rep['rho'],side='child')
    out.mkdir(parents=True);records=[]
    def save(name,a):
        p=out/name;_compressed_npz(p,{k:v for k,v in a.items()if isinstance(v,np.ndarray)})
        if p.stat().st_size>=10*1024**2:raise ValueError('compact operator source required')
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    for eps in(1,-1):
        for branch in('particle','conjugate'):
            point=read(Path(f'eta_{eps:+d}_{branch}_D5_direct_coefficient_source.npz'))
            a=fixed_radial_d5_weak_source(point,c['volume_density'],c['volume_density_first'][0],rep['radial_quadrature'],
                rep['radial_value_map'],rep['radial_derivative_map'],time_Clifford=np.kron(full['gamma5D_'+branch][0],np.eye(16)))
            save(f'eta_{eps:+d}_{branch}_original_weak_density_and_shape_source.npz',a)
            records.append(dict(eta_sheet=eps,representation=branch,original_weak_norm=float(np.linalg.norm(a['original_fixed_radial_weak_action'])),
                direct_weak_source_norm=float(np.linalg.norm(a['direct_shape_fixed_radial_weak_action'])),field_dimension=256))
    R,N,dR,dN=(data[k].item()for k in('R4','induced_lapse','R4_first','induced_lapse_first'))
    density=N*R**3;dDensity=dN*R**3+3*N*R**2*dR
    save('once_only_fixed_trace_Higgs_density_source.npz',dict(surface_density=np.array(density),surface_density_source=np.array(dDensity),
        fixed_trace_Higgs_seam_coefficient=-density*data['fixed_Y_mass'],
        direct_fixed_trace_Higgs_seam_coefficient_source=-dDensity*data['fixed_Y_mass']-density*data['fixed_Y_mass_first'][0]))
    for name,module in sorted(sys.modules.items()):
        p=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and p and Path(p).is_relative_to(ROOT):
            p=Path(p);pins[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    for p in(Path(__file__),ROOT/'tests/test_muon_d5_weak_shape_source.py'):
        pins[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    if any(sha256((ROOT/k).read_bytes()).hexdigest()!=v for k,v in pins.items()):raise ValueError('same current direct coefficient source required')
    result=dict(classification='EVALUATED_DIRECT_CHILD_D5_WEAK_DENSITY_AND_FIXED_RADIAL_SOURCE',input_hashes=pins,archives=archives,records=records,
        source_law='delta(mu D)=delta(mu)*D+mu*delta(D), including radial principal and all four original fixed radial tests; coordinate V_t=0 by fixed basis definition',
        once_only_SH_density_source=dDensity,direct_fixed_trace_Higgs_density_contact_norm=float(np.linalg.norm(dDensity*data['fixed_Y_mass'])),
        full_common_incoming_parent_born_reset_induced_state_and_rate_source_not_consumed=True,
        field_source_not_a_new_parent_bulk_or_child_gamma_family=True,
        physical_normal_mode_trace_and_exterior_firsts_unassigned_not_zero=True,
        finite_256_field_component_not_full_retarded_D5_complement=True,no_inverse_pole_or_heat_application=True,
        physical_Gamma2_charge_LSZ_Pauli_or_native_observable_admitted=False,physical_a_mu=None,physical_g_mu=None,errors_not_enclosed=True)
    p=out/'result.json';p.write_text(json.dumps(clean(result),sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(result_sha256=sha256(p.read_bytes()).hexdigest(),records=records,density_source=clean(dDensity)),sort_keys=True),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--direct-source',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();materialize(a.direct_source,a.output)
