"""Apply completed constant/tangent current columns in one normal frame."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_intrinsic_normal_coordinate_readout import normal_coordinate_operator_action,local_matched_spin_functional
from bhsm.interface.muon_native_dirac_hamiltonian import lepton_current_hilbert_representation
from bhsm.interface.muon_magnetic_source_mean_load import load_magnetic_reached_mean_inputs
from bhsm.interface.muon_magnetic_open_lepton_vertex import magnetic_open_fields_at_node
from bhsm.interface.muon_primal_cell_reached_source_heat import actual_reached_cell_vertices
from bhsm.interface.muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
from bhsm.interface.muon_parent_maxwell_full_weak import M
from evaluate_muon_reached_trace_action import deterministic_archive
from evaluate_muon_intrinsic_scalar_regulator_correction import source_record


def _packet(folder,classification):
    p=ROOT/folder;b=(p/'result.json').read_bytes();r=json.loads(b)
    if r['classification']!=classification:raise ValueError('one completed same-image action required')
    refs=dict(r['input_hashes']);refs[(p/'result.json').relative_to(ROOT).as_posix()]=sha256(b).hexdigest()
    a=(p/r['archive']['path']).read_bytes()
    if len(a)!=r['archive']['bytes']or sha256(a).hexdigest()!=r['archive']['sha256']:raise ValueError('completed current columns changed')
    refs[(p/r['archive']['path']).relative_to(ROOT).as_posix()]=sha256(a).hexdigest()
    if any(sha256((ROOT/n).read_bytes()).hexdigest()!=h for n,h in refs.items()):raise ValueError('pinned action input changed')
    with np.load(p/r['archive']['path'],allow_pickle=False)as f:arrays={k:f[k].copy()for k in f.files}
    return r,arrays,refs


def materialize(output,constant,tangent):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve previous normal-frame applications')
    rc,C,refs=_packet(constant,'EVALUATED_MATCHED_IMAGE_ACTION_CONSTANT_INPUT_SOFT_COLUMNS')
    rt,T,other=_packet(tangent,'EVALUATED_REACHED_SOFT_CURRENT_TANGENT_COLUMNS')
    if rc['common_cutoff_probe']!=rt['common_cutoff_probe']:raise ValueError('same complete regulator required')
    if any(refs[n]!=h for n,h in other.items()if n in refs):raise ValueError('constant/tangent action identities differ')
    refs.update(other);arrays={};rows=[]
    config='artifacts/muon_calibrated_pauli_20261009/inputs.json';cfg=json.loads((ROOT/config).read_bytes())
    e=float(np.sqrt(4*np.pi*cfg['alpha_consumer']['value']));refs[config]=sha256((ROOT/config).read_bytes()).hexdigest()
    for side in ('incoming','outgoing'):
        bound=load_magnetic_reached_mean_inputs('artifacts/muon_electromagnetic_soft_magnetic_source_20261011/'+side+'_run_1',repository=ROOT)
        fields=magnetic_open_fields_at_node(bound,bound['source']['times'][2]);op=actual_reached_cell_vertices(fields,bound['representation'])['operator']
        raw=fields['raw_fields']
        # Raw scalar order is ReH1,ReH2,ImH1,ImH2. Keep this explicit.
        h=raw[-8:-4][:2]+1j*raw[-8:-4][2:]
        wall=np.einsum('fcj,j->fc',bound['representation']['wall_trace_map'],raw[100:180])
        # The old attached operator includes its mechanical action once.
        # Recover exactly that total wall from the reached operator binder.
        w=intrinsic_m4_weight_jet(12,raw[:37],raw[37:74],raw[74:98],source_value=raw[98],source_rate=raw[99])
        wall[2:]+=M*(w['mechanical_connection_lambda'].value-1)
        for family in range(3):
            p=side+'_family_'+str(family)+'_'
            cr=next(x for x in rc['records']if x['side']==side and x['family']==family)
            tr=next(x for x in rt['records']if x['side']==side and x['family']==family)
            if any(cr[k]!=tr[k]for k in ('R4','lapse','length')):raise ValueError('constant and tangent background/domain differs')
            mass=float(lepton_current_hilbert_representation()['family_Y'][family,family].real*np.linalg.norm(h))
            for name in ('fermion_square_left','fermion_square_right','fermion_numerator_contact','scalar_propagator_left_field_image','scalar_propagator_right_field_image','total'):
                r=normal_coordinate_operator_action(C[p+'forward_'+name],T[p+'forward_'+name],C[p+'reverse_'+name],T[p+'reverse_'+name],
                    radius=cr['R4'],wall_connection=wall,H=h,family=family)
                f=local_matched_spin_functional(r['charged_constant_symbol'],r['charged_Wilson_source_spatial_first_jet'],mass=mass,electric_charge=e)
                for k,v in r.items():
                    if isinstance(v,np.ndarray):arrays[p+name+'_'+k]=v
                for k,v in f.items():
                    if isinstance(v,np.ndarray):arrays[p+name+'_'+k]=v
                if name=='total':
                    rows.append(dict(side=side,family=family,local_symbol_mass_action=mass,electric_charge=e,
                        point_symbol_norm=float(np.linalg.norm(r['full_constant_symbol'])),
                        first_momentum_symbol_norm=float(np.linalg.norm(r['full_first_momentum_symbol'])),
                        Wilson_source_jet_norm=float(np.linalg.norm(r['full_Wilson_source_spatial_first_jet'])),
                        represented_matched_spin_functional_norm=float(np.linalg.norm(f['matched_dimensionless_spin_functional'])),
                        complex_spin_imaginary_norm=float(np.linalg.norm(f['matched_dimensionless_spin_functional'].imag)),
                        Hermitian_symbol_remainder_norm=float(np.linalg.norm(f['Hermitian_symbol_remainder'])),
                        no_physical_Lorentz_operator_identification=True))
        for name in ('total',):
            for key in ('charged_constant_symbol','charged_first_momentum_symbol','charged_Wilson_source_spatial_first_jet','matched_dimensionless_spin_functional'):
                arrays[side+'_paired_middle_minus_light_'+key]=arrays[side+'_family_1_'+name+'_'+key]-arrays[side+'_family_2_'+name+'_'+key]
        arrays[side+'_actual_raw_fields']=raw;arrays[side+'_actual_total_wall_connection']=wall
    sources=[source_record(n,syms)for n,syms in (
        ('src/bhsm/interface/muon_intrinsic_normal_coordinate_readout.py',['normal_coordinate_operator_action','local_matched_spin_functional']),
        ('src/bhsm/interface/muon_intrinsic_covariant_open_current_jet.py',['normal_coordinate_first_momentum_lift','round_spatial_spin_connection']),
        ('src/bhsm/interface/muon_intrinsic_soft_current_columns.py',['_branch_application','soft_current_tangent_application']),
        ('src/bhsm/interface/muon_intrinsic_soft_constant_columns.py',['constant_input_image_data']))]
    for r in sources:refs[r['path']]=r['sha256']
    for n in (Path(__file__).relative_to(ROOT).as_posix(),'tests/test_muon_intrinsic_normal_coordinate_readout.py'):refs[n]=sha256((ROOT/n).read_bytes()).hexdigest()
    if any(sha256((ROOT/n).read_bytes()).hexdigest()!=h for n,h in refs.items()):raise RuntimeError('consumed current/action changed during application')
    out.mkdir(parents=True);path=out/'application.npz';deterministic_archive(path,arrays)
    info=dict(path=path.name,bytes=path.stat().st_size,sha256=sha256(path.read_bytes()).hexdigest())
    if info['bytes']>10*1024**2:raise ValueError('complete normal-frame archive exceeds cap')
    result=dict(classification='EVALUATED_SAME_IMAGE_ACTION_NORMAL_COORDINATE_CURRENT_AND_MATCHED_SPIN_FUNCTIONAL',
        input_hashes=refs,source_records=sources,archive=info,records=rows,common_cutoff_probe=rc['common_cutoff_probe'],
        complete_constant_and_18_first_momentum_input_columns_applied=True,
        neutral_fiber_and_two_open_placements_retained=True,
        scalar_domain='SAME Hodd80 plus Heven140 image action, both FF loops and both PH source insertions',
        angular_normalization='operator action on unit constant and local coordinate X=R*q: sqrt(V) input and1/sqrt(V) output cancel',
        local_symbol_mass_scope='fixed-Y*actual norm(H) only for dimensionless local symbol contraction; no measured mass used to change the background',
        finite_factor_to_Lorentz_Sigma_or_native_statistics_assignment_executed=False,
        required_next_Lorentz_consumer='deltaH_Lorentz(E,p)=signed open self-energy action with temporal source converted from positive G/N to canonical -iG/N, matched external energy derivative and LSZ/F1 counterterm; regulated internal factor numerator/domain must be identified before treating this finite spin functional as F2',
        overlap='this is intrinsic-Higgs open exchange, not paired lepton photon VP; no VP number subtracted. Same fixed-Y local scalar overlap requires the same Lorentz/current and regulator/domain match.',
        differential_Wigner_completion='these chord-coordinate columns fix the represented local operator-action jet; their higher-coordinate and omitted starting-loop images are not enclosed',
        physical_a_mu=None,physical_g_mu=None,
        error_scope='original constant/tangent exact-stored kernel tails preserved in consumed packets; binary Gaunt/assembly/eigen/contraction and this local coefficient readout are not outward enclosed. No physical Pauli uncertainty inferred.')
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(classification=result['classification'],archive=info,records=rows),sort_keys=True))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--constant',type=Path,default=Path('artifacts/muon_intrinsic_soft_constant_columns_20261011/run_2'))
    p.add_argument('--tangent',type=Path,default=Path('artifacts/muon_intrinsic_soft_current_columns_20261011/run_3'))
    a=p.parse_args();materialize(a.output,a.constant,a.tangent)
