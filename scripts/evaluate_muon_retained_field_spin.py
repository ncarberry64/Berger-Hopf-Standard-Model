"""Run the saved-field-to-spin connection and independent scoped checks."""
from __future__ import annotations
import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
import argparse,json,time,hashlib
from pathlib import Path
import numpy as np
from scipy.linalg import solve
from bhsm.interface.retained_response.field_spin_connection import *
from bhsm.interface.retained_response.retained_magnetic_application import FRAME


def json_write(path,obj):
    p=Path(path);tmp=p.with_suffix(p.suffix+'.tmp')
    tmp.write_text(json.dumps(obj,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8');tmp.replace(p)


def angular_checks():
    Y=real_n1_multiplication();errors=[]
    for degree in (5,7):
        sg,w,q=haar_rule(degree);phi=scalar_values(sg,2)
        ref=np.einsum('p,pt,ph,ps->hts',w,phi.conj(),2*q,phi)
        errors.append(mx(Y-ref))
    large=real_n1_multiplication(3);n=Y.shape[-1]
    return dict(CG_vs_independent_Haar=max(errors),matrix_Hermiticity=mx(Y-dagger(Y)),
                all_reached_n_leq1_outputs_preserved=mx(large[:,:n,:5]-Y[:,:,:5]),
                n3_output_from_n_leq1=mx(large[:,n:,:5]),
                omitted_n3_for_arbitrary_n2_input_nonzero=mx(large[:,n:,5:n]))


def local_gauge_check(path):
    """Check gauge covariance of the ORIGINAL field-to-H map, including Higgs motion.

    A->A+D alpha, H->H-alpha_H H, psi->exp(-alpha)psi.
    Thus dh=[h,alpha]-i alpha_dot. This is a representation check, not a
    claim that these off-shell gauge variations solve the linearized field EOM.
    """
    vr=field_vertices();G=vr['G'];Y=vr['Y'];err=0.;rel=0.;omitted=0.
    pauli=PAULI
    GH=np.concatenate((-1j*pauli/(2*np.sqrt(2)),(-.5j*np.eye(2)/np.sqrt(10/3))[None]))
    for ind in (0,2,5):
        s=path.s[ind];eta=.17+s*(1-s);etad=(1-2*s)/path.T
        wall=path.wall[ind];H=path.raw[ind,260:262]+1j*path.raw[ind,262:264];con=wall['connection'][[0,2,3,4]]
        for c,harm in np.ndindex(4,4):
            gg=np.zeros((4,4,4));hh=np.zeros((4,4))
            gg[0,c,harm]+=etad
            for f in range(4):
                if c<3:gg[f,:3,harm]+=eta*np.cross(con[f,:3],np.eye(3)[c])/np.sqrt(2)
                if f>0:gg[f,c,:]+=eta*FRAME[f-1,harm,:]
            dh=-eta*GH[c]@H;hh[:,harm]=np.r_[dh.real,dh.imag]
            coeff=np.r_[gg.ravel(),hh.ravel()]
            coeff[16:64]*=wall['lapse']/wall['R4'];coeff[64:]*=wall['lapse']
            value=np.einsum('b,bij->ij',coeff,vr['V'])
            a=eta*np.kron(Y[harm],G[c]);ad=etad*np.kron(Y[harm],G[c]);h0=path.history['H'][ind]
            target=h0@a-a@h0-1j*ad
            err=max(err,mx(value-target));rel=max(rel,mx(value-target)/max(1.,mx(target)))
            omitted=max(omitted,mx(np.einsum('b,bij->ij',coeff[:64],vr['V'][:64])-target))
    return dict(original_field_gauge_identity_absolute=err,original_field_gauge_identity_relative=rel,
                omit_gauge_motion_of_Higgs_identity_difference=omitted)


def neutral_contact_check(path):
    """Already established neutral-Higgs coordinate contact, consumed in same scaling.

    This tests the different FIELD-DEPENDENT neutral insertion, not permission
    to delete the scalar response on generic original Cartesian wall directions.
    Maxwell and other sectors need their own corresponding residual contacts.
    """
    residual=0.;first=0.;momentum=0.
    for i,label in enumerate(LABELS):
        G,Gd=path.wall_input_at_sample(i);K=path.hc[label+'_K'];B=path.hc[label+'_B']
        W=G[:,128:131];raw_contact=path.hc[label+'_moving_axis_gradient_contact']
        source=K[:16,16:]@W
        contact=path.T**2*path.J[:16,:16].T@raw_contact
        residual=max(residual,mx(source+contact));first=max(first,mx(source))
        momentum=max(momentum,mx(B[16:,:16].T@W))
    return dict(scaled_neutral_Higgs_source_before_contact=first,
                scaled_neutral_Higgs_source_after_contact=residual,
                neutral_Higgs_gauge_rate_contact=momentum,
                scope='Higgs action alone; complete physical neutral magnetic derivative not assembled')


def finite_difference_checks(path,result):
    sources={}
    d=np.zeros(166);d[0]=.6;d[18]=.3;d[36]=.5;d[120]=.7;d[160]=.2
    sources['mixed_original_wall_and_scalar']=d
    d=np.zeros(166);d[160]=1;d[164]=-.4
    sources['fixed_axis_magnetic_profile']=d
    checks=[]
    for name,d in sources.items():
        target=np.einsum('c,cij->ij',d,result['propagator_first'])
        spin=np.einsum('c,cbij->bij',d,result['spin_first'])
        rows=[]
        for eps in ((.02,.01,.005) if name.startswith('mixed') else (.5,.25,.125)):
            values=[evolve_perturbed(path,d,a*eps) for a in (2,1,-1,-2)]
            fd=(-values[0]+8*values[1]-8*values[2]+values[3])/(12*eps)
            obs=[dagger(u)@path.history['S']@u for u in values]
            ds=(-obs[0]+8*obs[1]-8*obs[2]+obs[3])/(12*eps)
            rows.append(dict(step=eps,propagator_max=mx(fd[:,:30]-target),
                             spin_max=mx(ds[:,:30,:30]-spin),
                             derivative_amplitude=max(mx(target),mx(spin))))
        checks.append(dict(direction=name,direction_nonzeros={str(i):float(x) for i,x in enumerate(d) if x},rows=rows))
    return checks


def scalar_endpoint_freeze_test(path,U,Jtrue,order=12):
    """Compare the actual saved scalar history against an explicitly WRONG endpoint freeze.

    Only an omission/sensitivity diagnostic; not a new physical source path.
    """
    hfinal=path.J[:16,:16]@path.hs['final'][:16]
    x,w=np.polynomial.legendre.leggauss(order);out=np.zeros_like(Jtrue)
    for s,ww in zip((x+1)/2,w/2):
        u=U(s);bi=dagger(u)@field_vertices()['V'][64:]@u[:,:30]
        N=float(interpolate(path.s,path.N,s))
        out+=path.T*ww*np.tensordot((N*hfinal).T,bi,axes=(1,0))
    return dict(endpoint_freeze_vs_saved_dynamic_scalar_max=mx(out-Jtrue),
                changed_source_not_an_error_assigned_to_the_repository=True)


def combined_open_maps(path,spin_result):
    """Join actual saved classical endpoint/wall maps to the new spin input map.

    No exterior/wall equation is solved and no initial datum is selected.
    The zero direct Maxwell-initial columns apply only while g is prescribed.
    """
    with np.load(ROOT/'inputs'/f'{path.side}_maxwell_maps.npz',allow_pickle=False) as z:
        m={k:z[k].copy() for k in z.files}
    h=path.hs;F=np.zeros((440,574));W=np.zeros((134,574));endpoint=np.zeros_like(W)
    F[:408,:408]=m['initial_to_final'];F[:408,440:]=m['trace_and_probe_to_final']
    F[408:,408:440]=h['final'][:,:32];F[408:,440:]=h['final'][:,32:]
    W[:,:408]=m['weak_wall_from_initial'];W[:,408:440]=h['weak_wall'][:,:32]
    W[:,440:]=m['weak_wall_from_trace_and_probe']+h['weak_wall'][:,32:]
    endpoint[:,:408]=m['wall_temporal_endpoint'][:,:408]
    endpoint[:,408:440]=h['wall_endpoint'][:,:32]
    endpoint[:,440:]=m['wall_temporal_endpoint'][:,408:]+h['wall_endpoint'][:,32:]
    canonical=lambda n:np.block([[np.zeros((n,n)),np.eye(n)],[-np.eye(n),np.zeros((n,n))]])
    Q=np.zeros((440,440));Q[:408,:408]=canonical(204);Q[408:,408:]=canonical(16)
    green=mx(W[:,440:]-W[:,440:].T+F[:,440:].T@Q@F[:,440:])
    # Explicitly constructed coefficient direction, not an actual preparation.
    coeff=np.sin(np.arange(574)+.31)*.02
    original=m['weak_wall_from_initial']@coeff[:408]+m['weak_wall_from_trace_and_probe']@coeff[440:]
    original+=h['weak_wall']@coeff[408:]
    check=mx(original-W@coeff)
    return dict(classical_final_map=F,classical_wall_map=W,wall_temporal_endpoint=endpoint,
                wall_Euler_map=W-endpoint,field_to_spin_input_indices=np.arange(408,574)),dict(
                saved_combined_boundary_Green=green,independent_sector_sum_difference=check)


def run(out):
    out=Path(out)
    if out.exists():raise FileExistsError('preserve existing result folder')
    out.mkdir(parents=True);t0=time.time();provenance=verify_inputs();angular=angular_checks();records=[]
    write_npz(out/'operator_bases.npz',dict(real_n1_multiplication=real_n1_multiplication(),
              field_vertices=field_vertices()['V'],source_in_full574_indices=np.arange(408,574)))
    for side in ('incoming','outgoing'):
        path=OpenFieldPath(side);U=evolve(path.history)
        result=integrated_response(path,U,12);r8=integrated_response(path,U,8);r16=integrated_response(path,U,16)
        old=np.load(ROOT/'inputs'/f'{side}_direct_spin_result.npz',allow_pickle=False)
        direct_J=old['integrated_insertion'].reshape(6,84,84)[:,:,:30]
        old_spin=old['spin_readout_first'].reshape(6,3,84,84)[:,:,:30,:30]
        measures=dict(saved_Higgs_polynomial_reconstruction=path.saved_reconstruction_error,
          unchanged_spin_propagator_sample_difference=mx(U(path.s)-path.ops['sample_U']),
          time_rule8_vs12_J=mx(r8['J_total']-result['J_total']),time_rule12_vs16_J=mx(r16['J_total']-result['J_total']),
          time_rule12_vs16_spin=mx(r16['spin_first']-result['spin_first']),
          original_direct_magnetic_J_recovered=mx(result['J_gauge'][160:]-direct_J),
          original_direct_magnetic_spin_recovered=mx(result['spin_gauge'][160:]-old_spin),
          duplicate_direct_magnetic_addition_error=mx(direct_J),
          source_operator_Hermiticity=mx(field_vertices()['V']-dagger(field_vertices()['V'])),
          projected_integrated_Hermiticity=mx(result['J_total'][:,:30]-dagger(result['J_total'][:,:30])),
          spin_response_Hermiticity=mx(result['spin_first']-dagger(result['spin_first'])),
          integrated_gauge_max=mx(result['J_gauge']),integrated_Higgs_max=mx(result['J_Higgs']),
          magnetic_fixed_axis_Higgs_J_max=mx(result['J_Higgs'][160:]),
          magnetic_fixed_axis_Higgs_spin_max=mx(result['spin_Higgs'][160:]),
          generic_wall_Higgs_J_max=mx(result['J_Higgs'][32:160]),
          arbitrary_scalar_initial_J_max=mx(result['J_Higgs'][:32]),
          source_to_spin_operator_max=mx(result['spin_first']),
          unreachable_readout_leakage=result['spin_readout_leakage'])
        d=np.zeros(166);d[0]=.6;d[18]=.3;d[36]=.5;d[120]=.7;d[160]=.2
        errs=[];rel=[]
        for s in (0.,.31,1.):
            a=path.insertion(s,d);b=independently_projected_insertion(path,s,d)
            errs.append(mx(a-b));rel.append(mx(a-b)/max(1.,mx(a)))
        measures.update(original_point_map_absolute=max(errs),original_point_map_relative=max(rel))
        measures.update(local_gauge_check(path));neutral=neutral_contact_check(path)
        freeze=scalar_endpoint_freeze_test(path,U,result['J_Higgs'])
        measures.update({k:v for k,v in freeze.items() if isinstance(v,float)})
        # Retain actual field maps and derivatives, not just new zero-state columns.
        fields=[];rates=[]
        for s in path.s:
            g,h=path.original_fields(s);fields.append(np.vstack((g,h)));rates.append(path.scalar_rate(s))
        write_npz(out/f'{side}_field_maps.npz',dict(time=path.t,tau=path.s,
                  physical_gauge_Higgs_coefficients=np.array(fields),scalar_canonical_stage_rates=path.stage_rates,
                  scalar_coordinate_frame=path.J[:16,:16],scalar_polynomial_rate_maps=np.array(rates)))
        # No density/pole selection: all outputs are operators or input maps.
        write_npz(out/f'{side}_spin_response.npz',{k:result[k] for k in (
            'J_gauge','J_Higgs','spin_first','initial_isometry','final_unperturbed')})
        finite_spectrum=np.array([[np.linalg.eigvalsh(o) for o in channel] for channel in result['spin_first'][160:]])
        write_npz(out/f'{side}_finite_state_ranges.npz',dict(magnetic_profile_spin_eigenvalues=finite_spectrum))
        combined,cm=combined_open_maps(path,result);measures.update(cm)
        write_npz(out/f'{side}_joint_open_response.npz',combined)
        fds=finite_difference_checks(path,result)
        fn=max(row['propagator_max'] for c in fds for row in c['rows'])
        flast=max(c['rows'][-1]['propagator_max'] for c in fds)
        slast=max(c['rows'][-1]['spin_max'] for c in fds)
        categories=dict(
          saved_input_hashes=True,
          shared_wall_classical_and_spin_input_map=cm['saved_combined_boundary_Green']<2e-12 and cm['independent_sector_sum_difference']<2e-12,
          angular_map_and_reached_outputs=angular['CG_vs_independent_Haar']<2e-13 and angular['n3_output_from_n_leq1']==0,
          scalar_response_reused=measures['saved_Higgs_polynomial_reconstruction']<1e-12,
          original_local_Hamiltonian_map=measures['original_point_map_relative']<2e-13,
          original_gauge_and_Higgs_covariance=measures['original_field_gauge_identity_relative']<2e-13,
          direct_field_not_double_counted=measures['original_direct_magnetic_J_recovered']<1e-18,
          integrated_response_quadrature=measures['time_rule12_vs16_J']<2e-12,
          Hermitian_operator_response=measures['spin_response_Hermiticity']<2e-12,
          independent_finite_field_propagator=flast<2e-10,
          independent_finite_field_spin=slast<2e-10,
          neutral_source_scope_contact=neutral['scaled_neutral_Higgs_source_after_contact']<1e-20,
          scalar_history_not_endpoint_freeze=freeze['endpoint_freeze_vs_saved_dynamic_scalar_max']>1e-12)
        record=dict(side=side,measures=measures,neutral_Higgs_coordinate_check=neutral,
                    finite_field_checks=fds,checks={k:bool(v) for k,v in categories.items()},
                    finite_response_inputs=166,original_combined_input_layout=574,
                    gauge_only_Maxwell_initial_feedthrough_at_fixed_wall='exactly absent from this intrinsic local operator; not absent after wall feedback',
                    source_impulse_causality='saved 4-stage collocation approximates scalar response; no continuum causal-support certificate',
                    full_physical_derivative_admitted=False)
        records.append(record);json_write(out/'progress.json',records)
        print(side,json.dumps({'checks':record['checks'],'J_Higgs':measures['integrated_Higgs_max'],'point_rel':measures['original_point_map_relative'],'gauge_rel':measures['original_field_gauge_identity_relative'],'FD_last':flast,'seconds':time.time()-t0}),flush=True)
    packet=dict(classification='EVALUATED_PRESCRIBED_WALL_AND_SAVED_HIGGS_TO_FINITE_TIME_LEPTON_RESPONSE',
        source_revision=provenance['source_revision'],verified_input_file_count=len(provenance['files']),angular_checks=angular,
        records=records,all_scoped_checks_pass=all(all(r['checks'].values()) for r in records),
        basis_input_order=INPUT_ORDER,initial_quantum_state_selected=False,
        actual_Maxwell_Higgs_closed_feedback=False,quantum_native_or_decay_kernel_evaluated=False,
        complete_physical_derivative_admitted=False,physical_a_mu=None,physical_g_mu=None,
        physical_uncertainty=None,physical_collider_constructed=False,coupled_background_corrections=0,
        git_writes=False,time_scope='same recorded 1e-5 action-unit arms, separate; no seconds/lifetime assignment',
        error_scope='retained fixed geometry, supplied finite classical response,14 harmonics/6-component fiber and n<=1 initial projection; representation tests not physical error enclosure',
        next_operand='Solve the compatible wall/source/reference equation to supply actual delta g and scalar initial data; compose remaining geometry, physical modes/readout, and native memory. Do not add direct magnetic insertion twice.')
    json_write(out/'result.json',packet)
    json_write(out/'BINDING.json',dict(input_manifest_sha256=hashlib.sha256((ROOT/'inputs/PROVENANCE.json').read_bytes()).hexdigest(),files={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(out.glob('*.npz'))}))
    if not packet['all_scoped_checks_pass']:raise ArithmeticError('one or more scoped checks failed; recorded outputs are retained')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True,type=Path)
    run(p.parse_args().output)
