"""Execute Wilson/local-momentum applications on the frozen magnetic current."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_intrinsic_covariant_open_current_jet import (
    source_image_covariant_current_jet,reached_first_momentum_source_image,
    normal_frame_magnetic_principal_symbol_application,round_spatial_spin_connection,
)
from bhsm.interface.muon_magnetic_source_mean_load import load_magnetic_reached_mean_inputs
from bhsm.interface.muon_magnetic_open_lepton_vertex import magnetic_open_fields_at_node,reached_magnetic_open_vertex
from bhsm.interface.muon_parent_maxwell_full_q_application import retained_full_q_angular_space
from bhsm.interface.muon_native_product_factor_graph import lepton_unit_trace_gauge_representation
from bhsm.interface.muon_parent_maxwell_full_weak import M
from bhsm.interface.muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
from evaluate_muon_reached_trace_action import deterministic_archive
from evaluate_muon_intrinsic_scalar_regulator_correction import source_record


def materialize(output,*,source):
    folder=Path(source);folder=folder if folder.is_absolute() else ROOT/folder
    out=Path(output);out=out if out.is_absolute() else ROOT/out
    if out.exists():raise FileExistsError('preserve existing current jet applications')
    data=(folder/'result.json').read_bytes();md=json.loads(data)
    if md['classification']!='EVALUATED_COMPLETE_CHARGED_NEUTRAL_EXTERNAL_CURRENT_APPLICATION_OF_TEMPORAL_SOURCE_IMAGE':
        raise ValueError('same-background complete charged/neutral current source required')
    hashes=dict(md['input_hashes']);hashes[(folder/'result.json').relative_to(ROOT).as_posix()]=sha256(data).hexdigest()
    for p,h in hashes.items():
        if sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise ValueError('consumed owner changed: '+p)
    archive=folder/md['archive']['path'];b=archive.read_bytes()
    if sha256(b).hexdigest()!=md['archive']['sha256'] or len(b)!=md['archive']['bytes']:raise ValueError('actual current archive changed')
    hashes[archive.relative_to(ROOT).as_posix()]=md['archive']['sha256']
    with np.load(archive,allow_pickle=False) as f:currents={k:f[k] for k in f.files}
    base=ROOT/'artifacts/muon_magnetic_mixed_green_20261011/run_3'
    with np.load(base/'scalar_sources.npz',allow_pickle=False) as f:scalar={k:f[k] for k in f.files}
    base_md=json.loads((base/'result.json').read_text());arrays={};rows=[]
    angular=retained_full_q_angular_space(ROOT)
    for side in ('incoming','outgoing'):
        bound=load_magnetic_reached_mean_inputs('artifacts/muon_electromagnetic_soft_magnetic_source_20261011/'+side+'_run_1',repository=ROOT)
        hashes.update(bound['input_hashes']);t=bound['source']['times'][2]
        fields=magnetic_open_fields_at_node(bound,t);raw=fields['raw_fields']
        if not np.array_equal(raw,scalar[side+'_raw_fields']):raise ValueError('current and source background differ')
        rep=bound['representation'];w=intrinsic_m4_weight_jet(12,raw[:37],raw[37:74],raw[74:98],source_value=raw[98],source_rate=raw[99])
        wall=np.einsum('fcj,j->fc',rep['wall_trace_map'],raw[100:180])
        wall[2:]+=M*(w['mechanical_connection_lambda'].value-1)
        R=float(w['R4'].value);H=raw[-8:-6]+1j*raw[-6:-4]
        full_connection=round_spatial_spin_connection(R)['connection']+np.einsum('ac,cij->aij',wall[2:],lepton_unit_trace_gauge_representation()['generators'])/R
        row=next(x for x in base_md['records'] if x['side']==side)
        outputs={}
        for family in range(3):
            prefix=side+'_family_'+str(family)+'_'
            current={k:currents[prefix+k] for k in ('forward_full_Green_insertion','reverse_full_Green_insertion')}
            jet=source_image_covariant_current_jet(current,wall,R,H,family=family)
            with np.load(base/(side+'_family_'+str(family)+'_fermion_operators.npz'),allow_pickle=False) as f:
                Xi=f[prefix+'Xi_even_odd']
            X=Xi[:,:6,:24].reshape(3,6,4,6).transpose(0,2,1,3)
            image=reached_first_momentum_source_image(X,scalar[side+'_gaunt_even_odd_source'],row['even_harmonic_labels'],R)
            vertex=reached_magnetic_open_vertex(fields,rep,angular,electric_charge=bound['electric_charge'],family=family)
            local=normal_frame_magnetic_principal_symbol_application(vertex['canonical_point_vertices'][:3],
                vertex['canonical_physical_spatial_gradient'][:3],full_connection,H,family=family,electric_charge=bound['electric_charge'])
            for label,r in (('jet',jet),('momentum',image),('canonical_symbol',local)):
                for k,v in r.items():
                    if isinstance(v,np.ndarray):arrays[prefix+label+'_'+k]=v
            outputs[family]=jet
            norm=np.linalg.norm(jet['point_kernel'])
            rows.append(dict(side=side,family=family,coordinate_time=float(fields['coordinate_time']),
                cutoff_probe=base_md['common_cutoff_probe'],radius=R,
                point_kernel_norm=float(norm),Wilson_center_jet_norm=float(np.linalg.norm(jet['Wilson_center_first_jet'])),
                Wilson_relative_jet_norm=float(np.linalg.norm(jet['Wilson_relative_first_jet'])),
                represented_endpoint_Hermitian_pair_defect=float(np.linalg.norm(jet['endpoint_Hermitian_pair_difference'])),
                point_Hermiticity_relative_defect=float(np.linalg.norm(jet['point_Hermiticity_difference'])/norm) if norm else 0,
                contracted_spin_reconstruction_max_defect=float(np.max(abs(jet['owned_contracted_spin_difference']))),
                new_n2_first_momentum_source_image_norm=float(np.linalg.norm(image['source_image_n2'])),
                retained_n0_first_momentum_source_image_norm=float(np.linalg.norm(image['source_image_n0'])),
                normalized_local_action_principal_symbol_spin_response_real=local['relative_to_minimal_Dirac_spin_coefficient'].real.tolist(),
                normalized_local_action_principal_symbol_spin_response_imag=local['relative_to_minimal_Dirac_spin_coefficient'].imag.tolist(),
                normal_frame_source_derivative_contact_norm=float(np.linalg.norm(local['ordinary_to_covariant_source_jet_contact'])),
                local_symbol_mass_action=local['matched_mass_action'],
                normalized_native_loop_Pauli=None))
        for k in ('point_kernel','Wilson_center_first_jet','Wilson_relative_first_jet','charged_Dirac_spin_component','charged_Dirac_spin_center_jet','charged_Dirac_spin_relative_jet'):
            arrays[side+'_paired_middle_minus_light_'+k]=outputs[1][k]-outputs[2][k]
        print(json.dumps(dict(side=side,paired_Wilson_relative_norm=float(np.linalg.norm(arrays[side+'_paired_middle_minus_light_Wilson_relative_first_jet']))),sort_keys=True),flush=True)
    sources=[source_record(p,symbols) for p,symbols in (
        ('src/bhsm/interface/muon_intrinsic_covariant_open_current_jet.py',['round_spatial_spin_connection','normal_coordinate_first_momentum_lift','covariant_bilocal_first_jet','source_image_covariant_current_jet','normal_frame_magnetic_principal_symbol_application','reached_first_momentum_source_image']),
        ('src/bhsm/interface/muon_intrinsic_scalar_discretization.py',['scalar_angular_derivative_matrices','scalar_basis_values']),
        ('src/bhsm/interface/muon_magnetic_open_lepton_vertex.py',['charged_dirac_injection','reached_magnetic_open_vertex']),
    )]
    for p in sources:hashes[p['path']]=p['sha256']
    hashes[Path(__file__).relative_to(ROOT).as_posix()]=sha256(Path(__file__).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in hashes.items()):raise RuntimeError('source changed during local current application')
    out.mkdir(parents=True);deterministic_archive(out/'application.npz',arrays)
    result=dict(classification='EVALUATED_WILSON_TRANSPORTED_REACHED_CURRENT_JET_AND_MINIMAL_NORMAL_MOMENTUM_IMAGE',
        input_hashes=hashes,source_records=sources,records=rows,
        archive=dict(path='application.npz',bytes=(out/'application.npz').stat().st_size,sha256=sha256((out/'application.npz').read_bytes()).hexdigest()),
        source_scope='same frozen three magnetic first-jet directions and total solved gauge/H source; no new source state, profile, momentum or charge normalization',
        connection_scope='torsion-free Levi-Civita spin lift of the retained right round coframe plus actual full weak/U1 wall connection; mechanical sigma1 once',
        angular_normalization='phi=Y/sqrt(2pi²); bidirectional n0/n1 kernel coincidence includes 1/(2pi²) once',
        local_normal_frame_equations=['d_center K_W=dxK+dyK+[Omega,K]','d_relative K_W=(dxK-dyK+{Omega,K})/2','dV_normal=dV+[Omega,V]'],
        charged_neutral_return_removed=False,
        local_action_symbol_spin_normalization='actual fixed-Y norm(H) local charged principal mass; signed minimal electron spin energy +e sigma.B/(2m); no interacting pole identified',
        next_source_application=dict(incoming_tangent_columns=18,incoming_lift_shape=[24,18],complete_output_shape=[3,60,18],
            new_output_n2_shape=[3,54,18],operator='same enlarged-temporal mixed Green with both open placements/source squares/numerator/PH insertion',
            reached_internal_fermion_shells=dict(odd=[1,3,5],even=[0,2,4,6]),
            starting_scalar_loop='preserve pinned PHodd80 and its PHeven140 first-source image; no new full-loop sum assumed'),
        overlap_scope='No local H1 or continuum paired VP subtraction made: a Wilson Clifford contraction of an unamputated finite factor current is not the matched on-shell local loop.',
        normal_frame_transport_completed_for_represented_kernel=True,
        minimal_extra_columns_have_actual_nonzero_n2_source_image=True,
        interacting_pole_LSZ_or_native_signed_soft_Pauli_completed=False,
        physical_a_mu=None,physical_g_mu=None,
        error_scope='binary64 represented source/current/normal-coordinate/Clifford application only; upstream kernel and solve errors preserved in the consumed source packet; no bound assigned to missing incoming tangent/current images or Lorentz matching')
    if result['archive']['bytes']>10*1024**2:raise ValueError('complete archive exceeds public cap')
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return dict(classification=result['classification'],archive=result['archive'],records=rows)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--source',type=Path,default=Path('artifacts/muon_intrinsic_open_current_schur_20261011/run_1'))
    a=p.parse_args();print(json.dumps(materialize(a.output,source=a.source),sort_keys=True))
