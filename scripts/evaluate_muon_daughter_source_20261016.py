"""Apply owned daughter vertices and spin readout to the retained field symbol.

No new measured input sets the local spin model or frozen family ratio.
The retained field-symbol background DOES have calibrated scalar ancestry:
lambda_H=G_F*m_h^2/sqrt(2). It is replayed, not made into a BHSM prediction.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import io
import json
from pathlib import Path
import sys
import zipfile
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
from bhsm.interface.muon_coupled_lorentz_radial_green import coupled_radial_trace_application
from bhsm.interface.muon_owned_static_charged_current import owned_static_charged_current
from bhsm.interface.ae31_c2_intrinsic_m4_lepton_action import charged_lepton_yukawa_operator
from bhsm.interface.muon_daughter_action_source import (
    daughter_tensor, daughter_tensor_first, quotient_trace_return_first,
    owned_daughter_vertices_first,
)
from bhsm.interface.muon_daughter_spin_channel import (
    local_decay_spectrum,local_joint_spin_kernel,parent_analyzer,va_tensor,
)
from bhsm.interface.muon_daughter_neutrino_channel import (
    neutrino_parent_analyzer,neutrino_phase_prefactor,
)


def neutral_spectrum(C, *, m, order):
    """Two full parent-spin neutral marginals in the same local M=1 model."""
    v,w=np.polynomial.legendre.leggauss(order);v,w=(v+1)/2,w/2
    # Pair invariant s=m^2+(1-m^2)v^2 resolves the massive endpoint.
    E=(1-m*m)*(1-v*v)/2;ew=w*(1-m*m)*v
    from bhsm.interface.muon_daughter_spin_channel import sphere_rule
    normals,aw=sphere_rule(3);outputs={}
    for species in ('nu_mu','anti_nu_e'):
        matrices=[]
        for energy in E:
            d=np.array([neutrino_parent_analyzer(C,M=1.,m=m,E=energy,direction=n,species=species) for n in normals])
            matrices.append(neutrino_phase_prefactor(M=1.,m=m,E=energy)*np.einsum('p,pij->ij',aw,d))
        matrices=np.asarray(matrices);total=np.einsum('p,pij->ij',ew,matrices)
        moment=np.einsum('p,p,pij->ij',ew,E,matrices)
        outputs[species]=dict(energy_nodes=E,energy_weights=ew,parent_density=matrices,
            integrated_parent_analyzer=total,integrated_energy_analyzer=moment,
            mean_scaled_energy=float(2*np.trace(moment).real/np.trace(total).real))
    return outputs


def digest(p):
    return sha256(p.read_bytes()).hexdigest()


def archive(path, arrays):
    with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,a in sorted(arrays.items()):
            b=io.BytesIO();np.lib.format.write_array(b,np.asarray(a),allow_pickle=False)
            info=zipfile.ZipInfo(name+'.npy',(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(info,b.getvalue(),compresslevel=9)


def materialize(output):
    out=Path(output);out=out if out.is_absolute() else ROOT/out
    if out.exists():raise FileExistsError('preserve earlier daughter applications')
    folder=ROOT/'artifacts/muon_coupled_lorentz_field_symbol_20261011/run_1'
    md=json.loads((folder/'result.json').read_text());refs=dict(md['input_hashes'])
    for p in (folder/'result.json',folder/'application.npz'):
        refs[p.relative_to(ROOT).as_posix()]=digest(p)
    if digest(folder/'application.npz')!=md['archive']['sha256']:
        raise ValueError('original frozen field-symbol archive changed')
    for path,h in refs.items():
        if digest(ROOT/path)!=h:raise ValueError('retained field-symbol provenance changed: '+path)
    prep='artifacts/muon_ideal_collider_preparation_20261016/BHSM_IDEAL_COLLIDER_PREPARATION_V1.json'
    refs[prep]=digest(ROOT/prep)
    if refs[prep]!='dcc4ad850ea38dcd405637d24b306efe8789ab08e144f559d7cc294cd72e8f0f':
        raise ValueError('adopted preparation must remain exact')
    y=np.asarray(charged_lepton_yukawa_operator()['family_operator'])
    ratio=float(y[2,2]/y[1,1]);arrays={};records=[]
    with np.load(folder/'application.npz',allow_pickle=False) as a:
        for record in md['records']:
            side=record['side'];prefix=side+'_'
            coeff,Q,T,r,F=[a[prefix+k].copy() for k in
                ('proper_frequency_coefficients','field_quotient_lift','joint_trace_map',
                 'scalar_radial_source','central_radial_frame_rows')]
            raw=a[prefix+'raw_fields'];h=raw[-8:-4];H=h[:2]+1j*h[2:]
            original=coupled_radial_trace_application(coeff,Q,T,r,F,frequency=0)
            owned=owned_static_charged_current(original['joint_wall_Green'],H,
                                              radius=record['radius'],lapse=record['lapse'])
            C=owned['full_charged_current_tensor'];R=owned['charged_current_right_vertices'];L=owned['charged_current_left_vertices']
            first=quotient_trace_return_first(coeff[0],Q,T,coeff[1],np.zeros_like(Q),np.zeros_like(T))
            dC=daughter_tensor_first(R,first['returned'],L,np.zeros_like(R),first['returned_first'],np.zeros_like(L))
            comparisons=[]
            for step in (1e-3,1e-4,1e-5,1e-6):
                values=[]
                for mult in (2,1,-1,-2):
                    value=coupled_radial_trace_application(coeff,Q,T,r,F,frequency=mult*step)
                    values.append(daughter_tensor(R,value['joint_wall_Green'],L))
                literal=(-values[0]+8*values[1]-8*values[2]+values[3])/(12*step)
                comparisons.append(dict(step=step,maximum_absolute=float(np.max(abs(literal-dC))),
                    relative_Frobenius=float(np.linalg.norm(literal-dC)/max(np.linalg.norm(dC),np.finfo(float).tiny))))
            for key,value in owned.items():
                if isinstance(value,np.ndarray):arrays[prefix+'owned_'+key]=value
            arrays[prefix+'tensor_frequency_first']=dC
            rows=[]
            for name,m in (('massless',0.),('conditional_family_ratio',ratio)):
                applications=[local_decay_spectrum(C,M=1.,m=m,energy_order=n) for n in (24,48,96)]
                final=applications[-1];refined=local_decay_spectrum(C,M=1.,m=m,energy_order=96,angular_order=4)
                projected=local_decay_spectrum(owned['VA_projection_coefficient']*owned['VA_template'],M=1.,m=m,energy_order=96)
                differences=[float(np.max(abs(b['integrated_joint_spin_map']-aa['integrated_joint_spin_map'])))
                             for aa,b in zip(applications,applications[1:])]
                angular=float(np.max(abs(final['integrated_joint_spin_map']-refined['integrated_joint_spin_map'])))
                neutrals=neutral_spectrum(C,m=m,order=96)
                neutral_refined=neutral_spectrum(C,m=m,order=192)
                electron_energy=np.einsum('p,p,pij->ij',final['energy_measure_weights'],final['energy_nodes'],final['parent_density_per_energy'])
                total_energy=electron_energy.copy()
                neutral_rows=[]
                for species,neutral in neutrals.items():
                    for key,value in neutral.items():
                        if isinstance(value,np.ndarray):arrays[prefix+name+'_'+species+'_'+key]=value
                    total_energy+=neutral['integrated_energy_analyzer']
                    neutral_rows.append(dict(species=species,mean_scaled_energy=neutral['mean_scaled_energy'],
                        total_rate_spin_matrix_difference=float(np.max(abs(neutral['integrated_parent_analyzer']-final['integrated_parent_analyzer']))),
                        q96_q192_spin_matrix_difference=float(np.max(abs(neutral['integrated_parent_analyzer']-neutral_refined[species]['integrated_parent_analyzer'])))))
                for key,value in final.items():
                    if isinstance(value,np.ndarray):arrays[prefix+name+'_'+key]=value
                rows.append(dict(test_operand=name,dimensionless_parent_rest_mass=1.,electron_ratio=m,
                    rate_coefficient=final['unpolarized_rate_coefficient'],
                    VA_projected_rate_coefficient=projected['unpolarized_rate_coefficient'],
                    full_over_VA_rate=final['unpolarized_rate_coefficient']/projected['unpolarized_rate_coefficient'],
                    mean_scaled_electron_energy=final['mean_scaled_electron_energy'],
                    mean_electron_helicity=final['unpolarized_mean_electron_helicity'],
                    parent_up_mean_electron_direction_cosine=final['parent_up_mean_direction_cosine'],
                    neutral_daughter_tests=neutral_rows,
                    energy_conservation_spin_matrix_difference=float(np.max(abs(total_energy-final['integrated_parent_analyzer']))),
                    joint_spin_map_energy_absolute_differences=differences,
                    joint_spin_map_angular_absolute_difference=angular,
                    hermiticity_defect=final['full_spin_map_hermiticity_defect'],
                    minimum_Choi_eigenvalue=final['minimum_integrated_Choi_eigenvalue']))
            # The unnormalized analyzer is the spin-sensitive magnetic measurement
            # consumer. It does not supply the magnetic Hamiltonian or F2.
            analyzers=[]
            for x in (.25,.5,.75,.95):
                K=local_joint_spin_kernel(C,M=1.,m=0.,E=x/2,direction=np.array([0.,0.,1.]))
                analyzers.append(parent_analyzer(K))
            arrays[prefix+'massless_parent_analyzer_at_x']=np.asarray(analyzers)
            records.append(dict(side=side,owned_VA_relative_tensor_remainder=owned['VA_relative_remainder'],
                source_value_identity_max=float(np.max(abs(C-daughter_tensor(R,first['returned'],L)))),
                source_frequency_jet_comparisons=comparisons,
                derivative_scope='all64 complex tensor coefficients for frequency only, fixed inherited Q/T/H/R/N; no physical outgoing-domain gate',
                distribution_tests=rows,
                original_quotient_equation_residual=float(np.max(abs(first['reduced_equation_residual']))),
                original_radial_frame_reaction=float(np.max(abs(original['original_radial_frame_reactions'])))))
            print(json.dumps(dict(side=side,frequency_jet=comparisons,distributions=rows),sort_keys=True),flush=True)
    for name in ('muon_daughter_action_source','muon_daughter_spin_channel','muon_daughter_neutrino_channel','muon_owned_static_charged_current',
                 'muon_coupled_lorentz_radial_green','muon_magnetic_open_lepton_vertex',
                 'ae31_c2_intrinsic_m4_lepton_action'):
        path='src/bhsm/interface/'+name+'.py';refs[path]=digest(ROOT/path)
    refs[Path(__file__).relative_to(ROOT).as_posix()]=digest(Path(__file__))
    out.mkdir(parents=True);archive(out/'application.npz',arrays)
    packet=dict(classification='EVALUATED_OWNED_ACTION_DAUGHTER_SOURCE_AND_LOCAL_JOINT_SPIN_CHANNEL',
        records=records,input_sha256=refs,numerical_sha256=digest(out/'application.npz'),
        adopted_preparation_consumed_as_physical_history=False,
        local_test_masses='M=1; m=0 or fixed family-Y eigenvalue ratio. Neither is an interacting BHSM pole.',
        new_measured_spin_model_inputs_used=False,
        inherited_scalar_calibration=dict(preserved=True,formula='lambda_H=G_F*m_h^2/sqrt(2)',
            owner='src/bhsm/interface/muon_parent_gauge_geometry_correction.py:retained_scalar_matching_coefficients',
            empirically_matched_inputs=['G_F','m_h'],physical_action_derived_prediction=False),
        source_weak_spin_swap_corrected=True,
        complete_tensor_retained=True,initial_spin_average_in_joint_maps=False,
        decay_charge=-1,physical_cap_radial_convergence_admitted=False,
        temporal_and_spatial_nonlocal_decay_symbol_completed=False,
        physical_daughter_sections_or_CAR_state_selected=False,physical_outgoing_derivative_admitted=False,
        matching_guard=2e-10,coupled_corrections=0,fresh_adopted_preparation_Maxwell=None,
        fresh_adopted_preparation_original226=None,physical_Pauli_F2=None,physical_g_mu=None,total_uncertainty=None,
        magnetic_readout='Tr[D(E,n) rho_mu(B,t)] retained with full2x2 D; physical pole/residue and rho_mu(B,t) remain required.',
        error_scope='finite local frozen-frequency tensor, explicit free-rest spin model, binary64 quadrature/solve differences; no continuum, retarded initial-boundary, radiative, physical state or full operator/domain error enclosure',
        NEXT_OPERAND='Physical external muon/electron/neutrino mode sections and current projection on the common sourced moving domain; retain full nonlocal returned kernel and its source/domain jets before the2e-10 outgoing gate.')
    (out/'result.json').write_text(json.dumps(packet,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
    return dict(result_sha256=digest(out/'result.json'),numerical_sha256=packet['numerical_sha256'])


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    print(json.dumps(materialize(p.parse_args().output),sort_keys=True))
