"""True-birth paired mean rows on the retained fixed-reference event chart.

The source contacts are computed at the actual E1 coefficients.  The
constrained geometric momenta use their same-action saddle variation,
including the paired-functional Hessian.  This numerical restriction
holds q and the normal trace fixed; it does not replace the moving full
worldvolume/reset graph or select the physical E0 mean state.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import numpy as np
from scipy.linalg import qr,solve_triangular

from .muon_parent_gauge_geometry_correction import ROOT
from .muon_birth_attached_phase import load_attached_endpoint
from .muon_birth_trace_enriched_action import generic_coordinate_lift
from .muon_birth_full_field_attachment import constrained_attachment_lift,inherited_full_field_boundary
from .muon_birth_paired_field_endpoint import endpoint_layout
from .muon_birth_phase_continuation import _compressed_npz


def paired_mean_field_rows(raw_sources,energy_sources,representation,state_weights):
    """Source of all 218 literal fixed-q field/constraint/energy rows.

    Parent-final and child-initial canonical contacts have opposite
    signs. The coefficient-dual momentum already includes the density
    and scalar 2Re. No source is assigned to the fixed-reference affine
    trace: the odd first variations have zero geometric displacement.
    This statement does not identify the two unknown geometric means.
    """
    g=np.asarray(raw_sources,float);energy=np.asarray(energy_sources,float)
    layout=endpoint_layout(representation);nr=layout['raw_count'];N=layout['gauge_count'];hs=layout['H_start']
    if g.ndim<3 or g.shape[:2]!=(2,nr) or energy.shape!=(2,)+g.shape[2:]:
        raise ValueError('two actual raw paired cotangents and literal energy contacts required')
    weights=np.asarray(state_weights,float)
    if weights.shape!=(98,) or np.any(weights<=0) or not all(np.isfinite(a).all() for a in (g,energy,weights)):
        raise ValueError('finite same-action source and positive retained state normalization required')
    shape=g.shape[2:];rows=[]
    constraint=np.r_[np.arange(74,98),100+layout['At']]
    scale=np.r_[1/weights[74:],np.ones(len(layout['At']))]
    for side in range(2):
        rows.extend(scale.reshape((-1,)+(1,)*len(shape))*g[side,constraint])
        rows.append(energy[side])
    for fields,momenta in ((100+layout['dynamic'],100+N+layout['dynamic']),
                           (np.arange(hs,hs+4),np.arange(hs+4,hs+8))):
        rows.extend(np.zeros((len(fields),)+shape))
        rows.extend(g[0,momenta]-g[1,momenta])
    return np.asarray(rows)


def attachment_paired_source(base,paired_gradient,paired_gradient_directional,*,coordinate_weights,
        difference_step=2e-5):
    """Apply d(momentum) for the paired action functional through its saddle.

    paired_gradient_directional evaluates the derivative of the complete
    paired gradient at a supplied common-coordinate direction and step.
    Interior first response coefficients are held fixed; the owned
    external Q/Qdot lift moves with the source chart. Four central
    evaluations per step supply Dg along the saddle adjoint directions.
    No inverse-positive or physical normal assumption enters.
    """
    n=base['dynamic_count'];m=base['algebraic_count'];g=np.asarray(paired_gradient,float)
    weights=np.asarray(coordinate_weights,float)
    if g.shape[0]!=2*n+m or weights.shape!=(len(g),) or np.any(weights<=0) or difference_step<=0:
        raise ValueError('same complete paired gradient and positive coordinate weights required')
    a=base['adjoint'];ell=base['lift'];mu=base['reaction']
    av=np.zeros(len(g));av[n:2*n]=a[:n];av[2*n:]=a[n+2:]
    ay=np.zeros(len(g));ay[2*n:]=a[n+2:]
    b=np.zeros((len(g),2));b[n:2*n]=ell;b[2*n:]=mu[2:]
    by=np.zeros_like(b);by[2*n:]=mu[2:]
    def derivative(d):
        magnitude=float(np.max(abs(weights*d)))
        if magnitude==0:return np.zeros_like(g)
        return magnitude*paired_gradient_directional(d/magnitude,difference_step)
    dg_av=derivative(av);dg_ay=derivative(ay)
    hessian_contact=np.einsum('iab,ij->jab',dg_av,b)-np.einsum('iab,ij->jab',dg_ay,by)
    direct=np.einsum('ij,iab->jab',ell,g[n:2*n])
    return dict(momentum_source=direct-hessian_contact,direct_velocity_contact=direct,
        paired_hessian_saddle_contact=hessian_contact,adjoint_direction=av,
        algebraic_adjoint_direction=ay,paired_gradient_directional_adjoint=dg_av,
        paired_gradient_directional_algebraic=dg_ay,difference_step=difference_step,
        source_boundary_derivative_zero_scope='the inherited geometric boundary B has no explicit external magnetic-source argument on this fixed-q chart',
        full_odd_velocity_attachment_space_claimed=False)


def weighted_row_surjection(jacobian,source,row_scale,coefficient_weights):
    """Minimum weighted numerical particular solution without spectral deletion.

    The complete wide row system is factored by QR; every row is solved.
    A singular triangular factor fails rather than removing rows or
    adding a conditioning term. The null space is retained explicitly
    and this particular solution is not a physical branch selection.
    """
    J=np.asarray(jacobian,float);f=np.asarray(source,float);r=np.asarray(row_scale,float);w=np.asarray(coefficient_weights,float)
    if J.ndim!=2 or J.shape[0]>J.shape[1] or f.shape[0]!=len(J) or r.shape!=(len(J),) or w.shape!=(J.shape[1],):
        raise ValueError('complete wide row system with same positive normalization required')
    if np.any(r<=0) or np.any(w<=0) or not all(np.isfinite(a).all() for a in (J,f,r,w)):
        raise ValueError('finite rows and positive scales required')
    A=r[:,None]*J/w[None,:];Q,R=qr(A.T,mode='full');nr=len(J);tri=R[:nr]
    flat=f.reshape(nr,-1);weighted=Q[:,:nr]@solve_triangular(tri.T,-r[:,None]*flat,lower=True)
    delta=weighted/w[:,None];residual=J@delta+flat
    return dict(correction=delta.reshape((J.shape[1],)+f.shape[1:]),
        residual=residual.reshape(f.shape),scaled_residual=(r[:,None]*residual).reshape(f.shape),
        normalized_null_basis=Q[:,nr:],normalized_row_factor=tri,
        row_factor_condition_number=float(np.linalg.cond(tri)),spectral_directions_removed=0,
        numerical_particular_selection='minimum retained coefficient-weight norm; no physical state or branch selection')


def _fixed_interior_paired_gradient_callback(raw,fields,representation,angular,charge,nu_squared_action):
    """Owned external lift varies; solved first interior coefficients stay fixed."""
    from .muon_electromagnetic_soft_magnetic_source import uniform_magnetic_source_first_jets
    from .muon_magnetic_source_mean_load import magnetic_source_complete_mean_load
    from .muon_parent_retarded_hypercharge import regular_radial_basis
    base=uniform_magnetic_source_first_jets(raw,angular,electric_charge=charge)
    B,D=regular_radial_basis(representation['rho'],1)
    if not np.array_equal(B[:,-1],representation['radial_value_map'][:,-1]) or not np.array_equal(D[:,-1],representation['radial_derivative_map'][:,-1]):
        raise ValueError('actual exterior source lift and source-motion lift differ')
    shape=lambda z:z[:,None,None,None,None]
    def evaluate(value):
        source=uniform_magnetic_source_first_jets(value,angular,electric_charge=charge)
        q=(source['Q']-base['Q']).T.reshape(8,5,4,20)
        qt=(source['Qdot']-base['Qdot']).T.reshape(q.shape)
        args=dict(first_gauge=fields['first_gauge']+shape(B[:,-1])*q,
            first_gauge_rate=fields['first_gauge_rate']+shape(B[:,-1])*qt,
            first_gauge_radial=fields['first_gauge_radial']+shape(D[:,-1])*q,
            first_wall_gauge=fields['first_wall_gauge']+q,
            first_H=fields['first_H'],first_H_rate=fields['first_H_rate'],nu_squared_action=nu_squared_action)
        return magnetic_source_complete_mean_load(value,representation,angular,source,1.,0.,**args)['raw_mean_cotangent']
    return evaluate


def retained_true_birth_mean_rows(contact_directory,*,repository=ROOT,difference_step=2e-5):
    """Consume true E1 contacts and apply the same represented birth Jacobian."""
    from .muon_parent_maxwell_full_q_application import retained_full_q_angular_space
    root=Path(repository);folder=Path(contact_directory);folder=folder if folder.is_absolute() else root/folder
    data=(folder/'result.json').read_bytes();receipt=json.loads(data)
    if receipt['classification']!='EVALUATED_TRUE_E1_MAGNETIC_CUBIC_CANONICAL_CONSTRAINT_ENERGY_CONTACTS':
        raise ValueError('actual true-E1 paired contact application required')
    refs=dict(receipt['input_hashes'])
    for path,digest in refs.items():
        if sha256((root/path).read_bytes()).hexdigest()!=digest:raise ValueError('consumed birth source owner changed: '+path)
    archive=folder/receipt['archive']['path'];b=archive.read_bytes()
    if sha256(b).hexdigest()!=receipt['archive']['sha256'] or len(b)!=receipt['archive']['bytes']:
        raise ValueError('true-E1 contacts changed')
    refs[folder.relative_to(root).as_posix()+'/result.json']=sha256(data).hexdigest();refs[archive.relative_to(root).as_posix()]=sha256(b).hexdigest()
    with np.load(archive,allow_pickle=False) as saved:arrays={k:saved[k].copy() for k in saved.files}
    angular=retained_full_q_angular_space(root);sources=[];attachments=[];endpoint=None;diagnostics=[]
    for side in ('incoming','outgoing'):
        phase_refs=[p for p in refs if p.endswith('/result.json') and 'attached_phase_'+side+'_' in p]
        if len(phase_refs)!=1:raise ValueError('unique consumed chronological arm required')
        phase=json.loads((root/phase_refs[0]).read_bytes())
        endpoint=load_attached_endpoint(phase['consumed_paired_endpoint_path'],side=side,repository=root,
            radial_points=phase['radial_points'],cap_points=phase['cap_points'])
        raw=endpoint['raw'];rep=endpoint['representation'];c=generic_coordinate_lift(rep['gauge_labels']);P=c['lift'];n=c['x_count'];m=c['y_count']
        if not np.array_equal(raw,arrays[side+'_raw_fields']):raise ValueError('source cotangent is not at the true attached E1 coefficients')
        packet=endpoint['source'];metadata=endpoint['receipt'];rawbytes=(packet/'application.npz').read_bytes()
        if sha256(rawbytes).hexdigest()!=metadata['numerical_sha256']:raise ValueError('birth action array changed')
        with np.load(packet/'application.npz',allow_pickle=False) as saved:
            weights=saved['state_weights'];masterg=P.T@saved['updated_gradients'][0 if side=='incoming' else 1]
            masterh=P.T@saved['updated_hessians'][0 if side=='incoming' else 1]@P
            J=saved['updated_jacobian'];scale=saved['row_scale'];free=saved['free_indices'];cw=saved['coefficient_weights'];normalization=saved['attachment_normalization']
        boundary,_=inherited_full_field_boundary(raw[:37],n,len(masterg))
        base=constrained_attachment_lift(dict(gradient=masterg,hessian=masterh),boundary,dynamic_count=n,algebraic_count=m)
        g=np.einsum('ij,iab->jab',P,arrays[side+'_raw_mean_cotangent'])
        fields={key:arrays[side+'_'+key] for key in ('first_gauge','first_gauge_rate','first_gauge_radial','first_wall_gauge','first_H','first_H_rate')}
        paths=[p for p in refs if p.endswith('/result.json') and '/muon_electromagnetic_soft_magnetic_source_' in p and '/'+side+'_run_' in p]
        if len(paths)!=1:raise ValueError('unique physical magnetic-source normalization required')
        charge=json.loads((root/paths[0]).read_bytes())['electric_charge']
        callback=_fixed_interior_paired_gradient_callback(raw,fields,rep,angular,charge,metadata['action_parameters']['nu_squared_action'])
        coordinate_weights=abs(P.T)@np.r_[weights,np.ones(len(raw)-98)]
        def directional(d,step):
            return np.einsum('ij,iab->jab',P,(callback(raw+step*(P@d))-callback(raw-step*(P@d)))/(2*step))
        coarse=attachment_paired_source(base,g,directional,coordinate_weights=coordinate_weights,difference_step=difference_step)
        fine=attachment_paired_source(base,g,directional,coordinate_weights=coordinate_weights,difference_step=difference_step/2)
        attachments.append(fine['momentum_source']);sources.append(arrays[side+'_raw_mean_cotangent'])
        diagnostics.append(dict(side=side,coarse=coarse,fine=fine,
            step_halving_difference=fine['momentum_source']-coarse['momentum_source'],
            base_saddle=base['saddle'],base_lift=base['lift'],base_adjoint=base['adjoint']))
        refs[packet.relative_to(root).as_posix()+'/result.json']=endpoint['receipt_sha256'];refs[packet.relative_to(root).as_posix()+'/application.npz']=sha256(rawbytes).hexdigest()
    energy=np.array([arrays[s+'_fixed_action_energy_contact'] for s in ('incoming','outgoing')])
    work=np.array([arrays[s+'_source_motion_velocity_work'] for s in ('incoming','outgoing')])
    f=paired_mean_field_rows(np.array(sources),energy+work,rep,weights)
    attachment=normalization@np.asarray(attachments[1]-attachments[0]).reshape(2,-1)
    source=np.concatenate((f,attachment.reshape(2,8,8)))
    solved=weighted_row_surjection(J[:,free],source,scale,cw)
    raw_mean=np.zeros((2*len(raw),8,8));raw_mean[free]=solved['correction']
    return dict(source=source,field_source=f,attachment_source=attachment.reshape(2,8,8),
        fixed_action_energy_source=energy,source_motion_velocity_work=work,
        raw_mean_correction=raw_mean.reshape(2,len(raw),8,8),solve=solved,
        attachment_diagnostics=diagnostics,input_hashes=refs,jacobian=J,free_indices=free,row_scale=scale,coefficient_weights=cw,
        geometric_mean_scope='q37 and normal/rate fixed numerical restriction; no equality of unknown physical geometric means asserted',
        moving_affine_trace_scope='the source-image reference profile is fixed here; odd first geometric displacement is zero, so its direct paired trace source is zero; a moving mean graph must use its separate q/profile jets',
        full_odd_velocity_attachment_space_claimed=False,physical_chronological_mean_or_formation_completed=False)


def materialize_true_birth_mean_rows(contact_directory,output,*,repository=ROOT,difference_step=2e-5):
    root=Path(repository);out=Path(output);out=out if out.is_absolute() else root/out
    if out.exists():raise FileExistsError('preserve previous birth mean applications')
    a=retained_true_birth_mean_rows(contact_directory,repository=root,difference_step=difference_step);out.mkdir(parents=True)
    arrays={k:v for k,v in a.items() if isinstance(v,np.ndarray)}
    arrays.update({'solve_'+k:v for k,v in a['solve'].items() if isinstance(v,np.ndarray)})
    diagnostics=[]
    for d in a['attachment_diagnostics']:
        side=d['side']
        for k,v in d.items():
            if isinstance(v,np.ndarray):arrays[side+'_'+k]=v
            elif isinstance(v,dict):arrays.update({side+'_'+k+'_'+name:z for name,z in v.items() if isinstance(z,np.ndarray)})
        diagnostics.append(dict(side=side,momentum_source_norm=float(np.linalg.norm(d['fine']['momentum_source'])),
            paired_hessian_saddle_contact_norm=float(np.linalg.norm(d['fine']['paired_hessian_saddle_contact'])),
            direct_velocity_contact_norm=float(np.linalg.norm(d['fine']['direct_velocity_contact'])),
            step_halving_difference_norm=float(np.linalg.norm(d['step_halving_difference'])),difference_step=difference_step,fine_difference_step=difference_step/2))
    refs=dict(a['input_hashes'])
    for name in ('muon_magnetic_birth_mean_rows','muon_birth_full_field_attachment','muon_birth_paired_field_endpoint',
        'muon_magnetic_source_mean_load','muon_electromagnetic_soft_magnetic_source','muon_electromagnetic_source_mean_load'):
        p='src/bhsm/interface/'+name+'.py';refs[p]=sha256((root/p).read_bytes()).hexdigest()
    _compressed_npz(out/'application.npz',arrays)
    md=dict(classification='EVALUATED_TRUE_BIRTH_PAIRED_MEAN_ROW_APPLICATION_FIXED_REFERENCE',input_hashes=refs,
        numerical_sha256=sha256((out/'application.npz').read_bytes()).hexdigest(),attachment_applications=diagnostics,
        source_norm=float(np.linalg.norm(a['source'])),raw_mean_correction_norm=float(np.linalg.norm(a['raw_mean_correction'])),
        original_row_residual_norm=float(np.linalg.norm(a['solve']['residual'])),scaled_row_residual_norm=float(np.linalg.norm(a['solve']['scaled_residual'])),
        row_factor_condition_number=a['solve']['row_factor_condition_number'],spectral_directions_removed=0,
        numerical_particular_selection=a['solve']['numerical_particular_selection'],momentum_source_count=1,
        paired_action_hessian_error_scope='central binary64 directional paired-gradient differences with step halving; no rigorous derivative/continuum error bound',
        geometric_mean_scope=a['geometric_mean_scope'],moving_affine_trace_scope=a['moving_affine_trace_scope'],
        source_motion_energy_scope='separate owned velocity-work pullback added and archived separately; no complete nonlinear angular H-axis source family inferred',
        full_odd_velocity_attachment_space_claimed=False,physical_E0_mean_or_full_birth_graph_selected=False,
        physical_chronological_mean_or_formation_completed=False,physical_native_Pauli_completed=False)
    (out/'result.json').write_text(json.dumps(md,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return md


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--contact-directory',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--difference-step',type=float,default=2e-5)
    args=p.parse_args();print(json.dumps(materialize_true_birth_mean_rows(args.contact_directory,args.output,difference_step=args.difference_step),sort_keys=True))
