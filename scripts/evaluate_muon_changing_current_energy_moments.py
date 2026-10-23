"""Execute the two-sided energy jet on the same changing current action."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from evaluate_muon_changing_magnetic_open_exchange import retained_inputs
from evaluate_muon_reached_trace_action import deterministic_archive
from bhsm.interface.muon_changing_current_energy_moments import changing_constant_energy_application,proper_clock_at_nodes
from bhsm.interface.muon_changing_magnetic_current_jets import magnetic_open_current_point
from bhsm.interface.muon_profile_preserving_phase_sample import profile_preserving_raw_sample,profile_preserving_lepton_sample
from bhsm.interface.muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
from bhsm.interface.muon_native_dirac_hamiltonian import lepton_current_hilbert_representation
from bhsm.interface.muon_magnetic_open_lepton_vertex import charged_dirac_injection


def materialize(output,*,cutoff=1e-11,variable='proper_clock_frequency'):
    out=Path(output);out=out if out.is_absolute()else ROOT/out
    if out.exists():raise FileExistsError('preserve completed external-energy applications')
    refs={};arrays={};records=[];common_energy=None
    for side in('incoming','outgoing'):
        phase,sampler,F,B,_,sample=retained_inputs(side,refs)
        L=abs(phase['receipt']['span']);times=sample['chronological_quadrature_times'];weights=sample['chronological_quadrature_weights']
        def lapse(u):
            t=float(u-L if side=='incoming'else u);x=profile_preserving_raw_sample(phase,t)['raw_fields']
            return intrinsic_m4_weight_jet(12,x[:37],x[37:74],x[74:98],source_value=x[98],source_rate=x[99])['induced_lapse'].value
        clock=proper_clock_at_nodes(times,lapse,order=16)
        birth=profile_preserving_lepton_sample(phase,0.)['operator'];Y=lepton_current_hilbert_representation()['family_Y'][1,1].real
        if common_energy is None:common_energy=float(Y*np.linalg.norm(birth['H']))
        points=[magnetic_open_current_point(phase,float(u),length=L,first_field_sampler=sampler,include_maps=False)for u in times]
        for a in points:a['length']=L
        measure=weights*np.array([a['N']for a in points])
        print(json.dumps(dict(stage='same_current_two_sided_energy',side=side,common_tree_symbol_energy=common_energy,variable=variable)),flush=True)
        app=changing_constant_energy_application(F,B,points,sample['temporal_basis_values'],sample['temporal_basis_coordinate_rates'],measure,
            clock['proper_times'],energy=common_energy,variable=variable,cutoff=cutoff,
            progress=lambda r:print(json.dumps(dict(stage='constant_current_energy_block',side=side,**r),sort_keys=True),flush=True))
        J=charged_dirac_injection(birth['H'],family=1)['charged']
        for k,v in app.items():
            if isinstance(v,np.ndarray):arrays[side+'_'+k]=v
        for k,v in clock.items():
            if isinstance(v,np.ndarray):arrays[side+'_'+k]=v
        arrays[side+'_charged_value']=J.conj().T@app['value']@J
        arrays[side+'_charged_energy_first']=J.conj().T@app['energy_first']@J
        arrays[side+'_charged_injection']=J
        records.append(dict(side=side,block_records=app['block_records'],external_tent_Gram=app['external_tent_Gram'],
            value_norm=float(np.linalg.norm(app['value'])),energy_first_norm=float(np.linalg.norm(app['energy_first'])),
            left_contact_norm=float(np.linalg.norm(app['left_energy_contact'])),right_contact_norm=float(np.linalg.norm(app['right_energy_contact'])),
            charged_energy_first_norm=float(np.linalg.norm(arrays[side+'_charged_energy_first'])),
            proper_clock_refinement_max=float(np.max(abs(clock['quadrature_refinement_difference'])))))
        del F,B,points
    for path in('src/bhsm/interface/muon_changing_current_energy_moments.py','tests/test_muon_changing_current_energy_moments.py',
        'src/bhsm/interface/muon_changing_magnetic_open_exchange.py','scripts/evaluate_muon_changing_magnetic_open_exchange.py',
        Path(__file__).relative_to(ROOT).as_posix()):refs[path]=sha256((ROOT/path).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('same current owner changed during energy application')
    out.mkdir(parents=True);deterministic_archive(out/'application.npz',arrays)
    result=dict(classification='EVALUATED_SAME_CHANGING_CURRENT_TWO_SIDED_EXTERNAL_ENERGY_JET',input_hashes=refs,records=records,
        archive=dict(path='application.npz',bytes=(out/'application.npz').stat().st_size,sha256=sha256((out/'application.npz').read_bytes()).hexdigest()),
        common_probe_cutoff=float(cutoff),energy_variable=variable,common_external_energy_action=common_energy,
        energy_source='actual incoming-birth fixed-Y charged tree-symbol mass Y_mu*norm(H), a local computational rest probe; not an interacting pole determination',
        both_external_leg_derivatives=True,analytic_left_dual_retained=True,Gaussian_sign=-1,
        complete_starting_field_coordinates=[1200,2100],full18_return_before_charge_projection=True,
        internal_operator_or_domain_continued=False,physical_LSZ_residue_or_Pauli_completed=False,
        physical_a_mu=None,physical_g_mu=None,
        error_scope='Actual binary64 source-directed current and two-sided energy-moment application on the declared changing positive reference; clock refinement is a diagnostic. Internal Lorentz/contour/domain identification, matrix/eigen/quadrature/continuum and physical matching errors remain separate.')
    (out/'result.json').write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return dict(classification=result['classification'],records=records)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--cutoff',type=float,default=1e-11)
    p.add_argument('--variable',choices=('proper_clock_frequency','continued_Lorentz_energy'),default='proper_clock_frequency')
    a=p.parse_args();print(json.dumps(materialize(a.output,cutoff=a.cutoff,variable=a.variable),sort_keys=True))
