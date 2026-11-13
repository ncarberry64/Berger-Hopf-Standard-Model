"""Local normal-frequency action of the full inherited two-arm graph.

Shared attachments and proper normal amplitudes are imposed before the
internal equations are solved. The saved joint Hessian includes every
inherited parent/child mixed image and nonlinear action-dual contact.
This frozen common-coordinate density is not the full physical event
domain or a selected resistance/inertia/drive quotient.
"""
from __future__ import annotations
from hashlib import sha256
import json
from pathlib import Path
import numpy as np

from .muon_parent_gauge_geometry_correction import ROOT
from .muon_birth_finite_normal_phase import load_finite_normal_endpoint
from .muon_birth_finite_geometric_trace_endpoint import pair_master_chart
from .muon_birth_chronological_normal_inertia import true_legendre_normal_trial
from .muon_local_normal_action_symbol import frozen_normal_frequency_jet
from .muon_birth_phase_continuation import _compressed_npz


def shared_normal_frequency_jet(hessian,parent_traces,child_traces,gauge_frames,*,lapse):
    """Glue physical trace rows and retain their duals apart from gauge frames.

    Each B lists attachment traces then one proper normal trace. Parent
    and child attachment/normal values agree, and the common normal is
    one. The other trace amplitudes are solved, rather than independently
    eliminated in the two arms. Gauge reactions remain original-row data.
    """
    Bp=np.asarray(parent_traces,float);Bc=np.asarray(child_traces,float)
    if Bp.shape!=Bc.shape or Bp.ndim!=2 or len(Bp)<2 or not np.isfinite(Bp).all()or not np.isfinite(Bc).all():
        raise ValueError('same finite attachment and proper-normal trace maps required')
    nt,n=Bp.shape;H=np.asarray(hessian);dim=len(H)-2*n
    G=np.asarray(gauge_frames,float)
    if dim<=2*n or G.ndim!=2 or G.shape[1]!=dim:
        raise ValueError('all paired dynamic/algebraic fields and named gauge frames required')
    normal=np.r_[Bp[-1],np.zeros(n)]
    glue=np.zeros((nt,dim));glue[:,:n]=Bp;glue[:,n:2*n]=-Bc
    result=frozen_normal_frequency_jet(H,normal,np.vstack((glue,G)),lapse=lapse)
    reactions=result['frame_reaction_coefficients']
    result['physical_trace_gluing_reactions']=reactions[:nt].copy()
    result['named_gauge_frame_reactions']=reactions[nt:].copy()
    result['action_rows_including_trace_gluing_duals']=result['original_action_row_residual']+glue.T@reactions[:nt]
    result['physical_trace_gluing_rows']=glue
    result['named_gauge_frame_rows']=G.copy()
    return result


def paired_local_chronological_normal_symbol(base_directory,*,repository=ROOT):
    """Bind the actual full joint action saved by coupled endpoint Newton."""
    root=Path(repository);loaded=load_finite_normal_endpoint(base_directory,side='incoming',repository=root)
    rep=loaded['representation'];chart=pair_master_chart(rep);n=chart['dynamic_count'];m=chart['algebraic_count']
    with np.load(loaded['source']/'application.npz',allow_pickle=False)as z:
        raw=z['updated_raw_pair'].copy();Hraw=z['graph_raw_hessian'].copy();graw=z['graph_raw_gradient'].copy()
    R=chart['lift'];Hmaster=R.T@Hraw@R;order=np.r_[chart['x_indices'],chart['v_indices'],chart['y_indices']]
    H=Hmaster[np.ix_(order,order)];gradient=(R.T@graw)[order]
    traces=[];lapses=[];P=chart['one_lift']
    for arm in range(2):
        sl=slice(arm*chart['raw_count'],(arm+1)*chart['raw_count'])
        local=P.T@Hraw[sl,sl]@P
        a=true_legendre_normal_trial(local,raw[arm],rep)
        traces.append(a['trial_trace']);lapses.append(a['induced_lapse'])
    labels=rep['gauge_labels'];c=chart['coordinates']
    Ar=[j for j,i in enumerate(c['dynamic_gauge_indices'])if labels[i]['field']=='A_rho'and labels[i]['internal']==3]
    if len(Ar)!=4:raise ValueError('all four central radial coordinates per arm required')
    frames=np.zeros((8,2*n+2*m))
    for arm in range(2):frames[arm*4+np.arange(4),arm*n+38+np.array(Ar)]=1.
    # Both action densities use the same coordinate parameter in the
    # coupled graph. The child-plus clock is the explicit readout here;
    # no independent arm-density clock summation or scale fit is inserted.
    stored=shared_normal_frequency_jet(H,*traces,frames,lapse=lapses[1])
    quadratic=shared_normal_frequency_jet((H+H.T)/2,*traces,frames,lapse=lapses[1])
    return dict(loaded=loaded,stored=stored,quadratic=quadratic,
        joint_raw_hessian=Hraw,joint_master_hessian=H,joint_master_gradient=gradient,
        parent_proper_normal_and_attachment_traces=traces[0],child_proper_normal_and_attachment_traces=traces[1],
        parent_induced_lapse=lapses[0],child_induced_lapse=lapses[1],
        inherited_cross_arm_hessian=Hraw[:chart['raw_count'],chart['raw_count']:],
        action_multiplier_Gauss_density=gradient[4*n:],antisymmetric_producer_rounding=H-H.T)


def materialize_paired_local_chronological_normal_symbol(base_directory,output,*,repository=ROOT):
    root=Path(repository);out=Path(output);out=out if out.is_absolute()else root/out
    if out.exists():raise FileExistsError('preserve earlier paired density applications')
    a=paired_local_chronological_normal_symbol(base_directory,repository=root)
    arrays={k:v for k,v in a.items()if isinstance(v,np.ndarray)};rows={}
    for name in ('stored','quadratic'):
        b=a[name];arrays.update({name+'_'+k:v for k,v in b.items()if isinstance(v,np.ndarray)})
        rows[name]={k:v for k,v in b.items()if not isinstance(v,np.ndarray)}
        for key in ('bordered_row_residual','action_rows_including_trace_gluing_duals','named_gauge_frame_reactions'):
            rows[name][key+'_max']=float(np.max(abs(b[key])))
    out.mkdir(parents=True);_compressed_npz(out/'application.npz',arrays)
    refs=dict(a['loaded']['input_hashes'])
    for name in ('muon_paired_local_normal_action_symbol','muon_local_normal_action_symbol',
                 'muon_birth_finite_geometric_trace_endpoint','muon_birth_chronological_normal_inertia'):
        p='src/bhsm/interface/'+name+'.py';refs[p]=sha256((root/p).read_bytes()).hexdigest()
    md=dict(classification='EVALUATED_FULL_INHERITED_TWO_ARM_LOCAL_NORMAL_ACTION_SYMBOL',
        input_hashes=refs,numerical_sha256=sha256((out/'application.npz').read_bytes()).hexdigest(),
        action_parameters=a['loaded']['receipt']['action_parameters'],applications=rows,
        parent_induced_lapse=a['parent_induced_lapse'],child_plus_readout_lapse=a['child_induced_lapse'],
        common_coordinate_action_clock=True,proper_clock_readout='child-plus d_tau=l_child d_t of the common-coordinate paired action',
        inherited_cross_arm_hessian_norm=float(np.linalg.norm(a['inherited_cross_arm_hessian'])),
        action_multiplier_Gauss_density_max=float(np.max(abs(a['action_multiplier_Gauss_density']))),
        antisymmetric_producer_rounding_max=float(np.max(abs(a['antisymmetric_producer_rounding']))),
        all_80_multiplier_Gauss_rows_and_212_dynamic_fields_retained=True,
        physical_trace_gluing_reactions_retained=True,full_inherited_profile_not_projected=True,
        scope='frozen local density of the evaluated complete paired trace graph; common attachments before elimination; outer-face/causal-domain and selected formation mode are not inferred',
        local_density_not_endpoint_DtN_divided_by_duration=True,
        actual_physical_R_I_drive_delta_imp_c_or_Pauli_selected=False,
        error_scope='binary64 complete stored paired action polynomial; no producer-rounding, frozen-coefficient or continuum/domain certificate')
    (out/'result.json').write_text(json.dumps(md,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return md


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base-directory',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();print(json.dumps(materialize_paired_local_chronological_normal_symbol(a.base_directory,a.output),sort_keys=True))
