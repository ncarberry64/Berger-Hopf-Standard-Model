"""New normalized MP proper birth on literal covariant radial functions.

The same fixed material traces, source, scalar action, all original Gauss
rows and nonzero canonical seeds are retained. This phase application
does not supply a whole nonlinear wave operator or a physical exterior.
"""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import sys


def run(repository,assembly,products,tables,output,degree=2):
    from bhsm_baton_zoo_radial_convergence import environment
    root,out,read,save,finish=environment(repository,output)
    import numpy as np
    import importlib.util
    from flint import acb,acb_mat,ctx
    from bhsm.interface.muon_stored_admission_correction import _matrix,_mid,_upper
    from bhsm.interface.muon_stored_fiber_canonical_tangent import _rows,_split,_cat
    from evaluate_muon_continued_current_factor import retained_input
    from bhsm_baton_zoo_literal_radial_profile_precision import literal_profiles
    from bhsm_baton_zoo_point_function_preconditioning import normalize
    workspace=Path(__file__).parent;owner=workspace/'bhsm_baton_zoo_phase_clock_analytic_jet.py'
    snap=out/'executed_phase_clock_analytic_jet.py';snap.write_bytes(owner.read_bytes())
    spec=importlib.util.spec_from_file_location('covariant_birth_phase_jet_snapshot',snap);packed=importlib.util.module_from_spec(spec);sys.modules[spec.name]=packed;spec.loader.exec_module(packed)
    ctx.prec=192;phase,_=retained_input('outgoing',{});rep,P=phase['representation'],phase['coordinates']['lift']
    a=read(Path(assembly)/f'birth_degree_{degree:02d}_compatible_connected_radial_action.npz')
    product=read(Path(products)/f'birth_degree_{degree:02d}_covariant_product_functions_and_moving_contacts.npz')
    lt=read(Path(tables)/f'degree_{degree:02d}_literal_MP_original_and_extra_point_wall_tables.npz')
    b=read(root/f'artifacts/muon_baton_zoo_radial_convergence_20261014/compatible_degree{degree}_birth_run_1/enlarged_birth_proper_three_columns_and_canonical_seeds.npz')
    stage=read(root/'artifacts/muon_baton_zoo_radial_completion_20261013/action_gauge_degree2_run_1/birth_current288_connected_action_and_rate_operands.npz')
    n0,dim0=int(a['dynamic_count']),len(a['Hessian']);N=int(product['new_profile_count']);n=n0+N;dim=dim0+2*N
    order=np.r_[np.arange(n0),dim0+np.arange(N),np.arange(n0,2*n0),dim0+N+np.arange(N),np.arange(2*n0,dim0)]
    inverse=np.argsort(order);oldmap=inverse[:dim0];oldoriginal=a['child_original252_to_augmented'].astype(int);original=oldmap[oldoriginal]
    current=a['current288_to_augmented'].astype(int)
    logical=[np.r_[current[106:122],current[228:244],current[284:288]]]
    for l in range(degree):logical.append(np.r_[a['added_position_indices'].reshape(degree,16)[l],a['added_rate_indices'].reshape(degree,16)[l],a['added_Gauss_indices'].reshape(degree,4)[l]])
    logical=np.r_[*logical,a['derivative_compatible_position_indices'],a['derivative_compatible_rate_indices']].astype(int)
    # Original zero-profile birth, explicit MP physical tables, no new state.
    oldmaps=dict(old504_to_full=a['old504_to_full'],extra_coordinates_to_full=252+logical,
        full_dimension=252+dim0,extra_point_lift_high=lt['compatible_extra_point_lift_high'],extra_point_lift_low=lt['compatible_extra_point_lift_low'],
        extra_wall_lift_high=lt['compatible_extra_wall_lift_high'],extra_wall_lift_low=lt['compatible_extra_wall_lift_low'])
    for k in('original_gauge_basis','original_gauge_radial_basis','original_wall_trace_map'):
        for half in('high','low'):oldmaps[k+'_'+half]=lt[k+'_'+half]
    zero=np.zeros(252+dim0);zeroR=np.zeros((252+dim0,1))
    scalar_probe=np.array([252+int(a['child_original252_to_augmented'][208])])
    print(json.dumps(dict(stage='covariant_birth_literal_MP_point_owner',degree=degree)),flush=True)
    body=packed.phase_action_contractions(a['raw_pair'],a['reference_pair'],rep,P,oldmaps,scalar_probe,zero,zero,zeroR,zeroR,
        include_directional_first=False,material_chart_precision='native_mp',include_parent_action=False)
    primal=np.zeros(252+dim0,complex);primal[:106]=(P.T@a['raw_pair'][0])[106:212]
    childrate=_matrix(stage['original_phase_rate_high'])+_matrix(stage['original_phase_rate_low'])
    ph,pl=_split(childrate)
    for i,j in enumerate(a['child_original252_to_augmented']):primal[252+int(j)]=ph[i,0]
    low=np.zeros_like(primal)
    for i,j in enumerate(a['child_original252_to_augmented']):low[252+int(j)]=pl[i,0]
    motion=packed.phase_action_contractions(a['raw_pair'],a['reference_pair'],rep,P,oldmaps,scalar_probe,primal,low,zeroR,zeroR,
        include_directional_first=True,material_chart_precision='native_mp',include_parent_action=False)
    point=_matrix(body['child_point_coefficients_high'])+_matrix(body['child_point_coefficients_low'])
    rate=_matrix(motion['child_point_coefficients_directional_first_high'])+_matrix(motion['child_point_coefficients_directional_first_low'])
    wallpoint=_matrix(body['child_wall_connection_high'])+_matrix(body['child_wall_connection_low'])
    profiles=literal_profiles(rep,a['rho'],degree);wallprofiles=literal_profiles(rep,[np.pi/2],degree)
    chi,chif,chiff=profiles['values'],profiles['first'],profiles['second'];cw,cwr=wallprofiles['values'],wallprofiles['first']
    labels=product['generator_profile_internal_labels'].astype(int)
    def comm(v,c,scale):
        # Retained epsilon/sqrt(2) bracket, evaluated MP from its formula.
        w=[acb(0)for _ in range(4)];factor=scale/acb(2).sqrt()
        for i,j,k in((0,1,2),(1,2,0),(2,0,1)):
            if c==k:w[i]+=v[j]*factor
            if c==j:w[i]-=v[k]*factor
        return w
    Trows=[];Ttimerows=[];Vrows=[]
    for r in range(len(a['rho'])):
        TT=acb_mat(60,2*N);Dt=acb_mat(60,2*N)
        for j,(p,c)in enumerate(labels):
            for f in range(1,5):
                K=comm([point[r,4*f+i]for i in range(4)],int(c),chi[r,int(p)])
                Kt=comm([rate[r,4*f+i]for i in range(4)],int(c),chi[r,int(p)])
                Kr=comm([point[r,40+4*f+i]for i in range(4)],int(c),chi[r,int(p)])
                more=comm([point[r,4*f+i]for i in range(4)],int(c),chif[r,int(p)])
                Ktt=comm([rate[r,20+4*f+i]for i in range(4)],int(c),chi[r,int(p)])
                Krt=comm([rate[r,40+4*f+i]for i in range(4)],int(c),chi[r,int(p)])
                mrt=comm([rate[r,4*f+i]for i in range(4)],int(c),chif[r,int(p)])
                for i in range(4):
                    if f==1 and i==c:K[i]+=chif[r,int(p)];Kr[i]+=chiff[r,int(p)]
                    TT[4*f+i,j]=K[i];TT[20+4*f+i,j]=Kt[i];TT[40+4*f+i,j]=Kr[i]+more[i];TT[20+4*f+i,N+j]=K[i]
                    Dt[4*f+i,j]=Kt[i];Dt[20+4*f+i,j]=Ktt[i];Dt[40+4*f+i,j]=Krt[i]+mrt[i];Dt[20+4*f+i,N+j]=Kt[i]
        Trows.append(TT);Ttimerows.append(Dt)
    W=acb_mat(20,2*N)
    for j,(p,c)in enumerate(labels):
        for f in range(1,5):
            K=comm([wallpoint[0,4*f+i]for i in range(4)],int(c),cw[0,int(p)])
            for i in range(4):
                if f==1 and i==c:K[i]+=cwr[0,int(p)]
                W[4*f+i,j]=K[i]
    def split_stack(matrices):
        pairs=[_split(m)for m in matrices];return np.asarray([v[0]for v in pairs]),np.asarray([v[1]for v in pairs])
    Th,Tl=split_stack(Trows);Tdh,Tdl=split_stack(Ttimerows);Wh,Wl=_split(W)
    newextra=np.r_[252+oldmap[logical],252+inverse[dim0+np.arange(2*N)]]
    maps=dict(old504_to_full=np.r_[np.arange(252),252+original],extra_coordinates_to_full=newextra,full_dimension=252+dim)
    maps['extra_point_lift_high']=np.concatenate((lt['compatible_extra_point_lift_high'],Th),axis=2)
    maps['extra_point_lift_low']=np.concatenate((lt['compatible_extra_point_lift_low'],Tl),axis=2)
    maps['extra_wall_lift_high']=np.concatenate((lt['compatible_extra_wall_lift_high'].reshape(20,-1),Wh),axis=1).reshape(5,4,-1)
    maps['extra_wall_lift_low']=np.concatenate((lt['compatible_extra_wall_lift_low'].reshape(20,-1),Wl),axis=1).reshape(5,4,-1)
    for k in('original_gauge_basis','original_gauge_radial_basis','original_wall_trace_map'):
        for half in('high','low'):maps[k+'_'+half]=lt[k+'_'+half]
    ids=np.r_[np.arange(106,212),252+np.arange(n,2*n),np.arange(212,252),252+np.arange(2*n,dim)]
    invphase=np.full(252+dim,-1,int);invphase[ids]=np.arange(len(ids));q= len(ids)
    # Complete MP spatial-function basis including the new independent
    # vector profiles, normalized with no rank or coordinate deletion.
    fieldold=np.setdiff1d(np.arange(n0),np.r_[oldoriginal[:38],oldoriginal[102:106]])
    fieldpositions=np.r_[oldmap[fieldold],inverse[dim0+np.arange(N)]]
    fieldpoint=[]
    Praw=P
    for r in range(len(a['rho'])):
        G=acb_mat(16,dim)
        for labelindex,label in enumerate(rep['gauge_labels']):
            from bhsm.interface.muon_parent_maxwell_full_weak import FIELD_ORDER
            f=FIELD_ORDER.index(label['field']);c=label['internal'];l=label['radial']
            if f<1:continue
            rawrow=Praw[100+labelindex]
            for j in np.flatnonzero(rawrow):G[4*(f-1)+c,int(original[j])]+=chi[r,l]*rawrow[j]
        for l in range(degree+1):
            positions=oldmap[logical[36*l:36*l+16]]
            for i,dest in enumerate(positions):G[i,int(dest)]=chi[r,4+l]
        for j,dest in enumerate(oldmap[a['derivative_compatible_position_indices']]):G[3,int(dest)]=profiles['psi'][r,j]
        for j,dest in enumerate(inverse[dim0+np.arange(N)]):
            for i in range(16):G[i,int(dest)]=Trows[r][4+i,j]
        w=_matrix([[a['quadrature'][r]]])[0,0].sqrt()
        fieldpoint.extend([[w*G[i,int(j)]for j in fieldpositions]for i in range(16)])
    norm=normalize(acb_mat(fieldpoint));S=norm['coordinate_to_original'];Mphase=acb_mat([[int(i==j)for j in range(q)]for i in range(q)])
    fi=invphase[252+n+fieldpositions]
    for i,ii in enumerate(fi):
        for j,jj in enumerate(fi):Mphase[int(ii),int(jj)]=S[i,j]
    R=acb_mat(252+dim,q)
    for i,master in enumerate(ids):
        for j in range(q):R[int(master),j]=Mphase[i,j]
    Rh,Rl=_split(R);zero=np.zeros(252+dim)
    save('actual_product_domain_lifts_and_normalization.npz',dict(**maps,product_point_lift_time_first_high=Tdh,product_point_lift_time_first_low=Tdl,
        child_original252_to_augmented=original,previous_radial_to_augmented=oldmap,dynamic_count=np.asarray(n),
        phase_to_full_action_indices=ids,field_position_indices=fieldpositions,normalized_phase_right_high=Rh,normalized_phase_right_low=Rl))
    print(json.dumps(dict(stage='covariant_birth_full_MP_phase_application',degree=degree,phase_rows=q,full_dimension=252+dim,normalization=norm['metrics'])),flush=True)
    app=packed.phase_action_contractions(a['raw_pair'],a['reference_pair'],rep,P,maps,ids,zero,zero,Rh,Rl,
        include_directional_first=False,material_chart_precision='native_mp',include_parent_action=True)
    save('actual_complete_MP_phase_action_on_normalized_rights.npz',app)
    Dnorm=Mphase.transpose()*(_matrix(app['phase_Hessian_on_actual_right_high'])+_matrix(app['phase_Hessian_on_actual_right_low']))
    totalgrad=_matrix(app['phase_gradient_high'])+_matrix(app['phase_gradient_low'])
    parentgrad=_matrix(app['parent_own_phase_gradient_high'])+_matrix(app['parent_own_phase_gradient_low'])
    E=np.zeros((6,q),complex);oldids=b['phase_to_full_action_indices'].astype(int)
    fullmap=np.r_[np.arange(252),252+oldmap];mappedphase=invphase[fullmap[oldids]];E[:,mappedphase]=b['proper_trace']
    oldAt=original[212+24+np.arange(16)].reshape(4,4)
    phiAt=oldmap[np.r_[current[284:288],a['added_Gauss_indices']].reshape(degree+1,4)]
    At=np.r_[oldAt.reshape(-1),phiAt.reshape(-1)];F=np.zeros((2+len(At),q),complex);F[:2,mappedphase]=b['named_frames'][:2]
    F[2+np.arange(len(At)),invphase[252+At]]=1
    EN,FN=_matrix(E)*Mphase,_matrix(F)*Mphase;nf,ne=len(F),6
    K=acb_mat(q+ne+nf,q+ne+nf)
    for i in range(q):
        for j in range(q):K[i,j]=Dnorm[i,j]
    for i in range(ne):
        for j in range(q):K[q+i,j]=EN[i,j];K[j,q+i]=EN[i,j]
    for i in range(nf):
        for j in range(q):K[q+ne+i,j]=FN[i,j];K[j,q+ne+i]=FN[i,j]
    rhs=_cat(acb_mat(q,3),_matrix(b['common_port_map']),acb_mat(nf,3));X=K.solve(rhs)
    L=Mphase*_rows(X,0,q);ports=_rows(X,q,q+ne);reactions=_rows(X,q+ne,q+ne+nf)
    action=_matrix(app['phase_Hessian_on_actual_right_high'])+_matrix(app['phase_Hessian_on_actual_right_low'])
    rawphase=action*_rows(X,0,q)+_matrix(E.T)*ports
    childgauss=_rows(rawphase,106+n+40,q);parentgauss=_rows(rawphase,106+n,106+n+40)
    U=acb_mat(252+dim,3)
    for i,master in enumerate(ids):
        for j in range(3):U[int(master),j]=L[i,j]
    Pi=_rows(action*_rows(X,0,q),106,106+n);seed=_cat(acb_mat(n,3),Pi)
    theta=acb_mat(q,1)
    for i in range(106):theta[i,0]=2*parentgrad[i,0]-totalgrad[i,0]
    for i in range(n):theta[106+i,0]=-totalgrad[106+i,0]
    target=_cat(Mphase.transpose()*theta,acb_mat(ne+nf,1));alpha=K.transpose().solve(target)
    natural=theta.transpose()*L;paired=alpha.transpose()*rhs
    values=dict(solution=X,phase_lifts=L,full_two_arm_fixed_position_phase=U,
        fixed_position_parent_phase=_rows(U,0,252),fixed_position_child_augmented_phase=_rows(U,252,252+dim),
        child_source_complete_canonical_pair=seed,child_original_Gauss_rows_without_reactions=childgauss,
        parent_joint_Gauss_rows_without_reactions=parentgauss,original_phase_without_named_reactions=rawphase,
        original_saddle_rows=K*X-rhs,named_reactions=reactions,analytic_adjoint=alpha,
        natural_cotangent=natural,independent_transpose_natural_cotangent=paired,natural_pairing_rows=natural-paired)
    resultpacket=dict(raw_pair=a['raw_pair'],reference_pair=a['reference_pair'],birth_coordinate_time=a['coordinate_time'],
        dynamic_count=np.asarray(n),phase_to_full_action_indices=ids,child_original252_to_augmented=original,
        proper_trace=E,named_frames=F,common_port_map=b['common_port_map'])
    for key,value in values.items():resultpacket[key+'_high'],resultpacket[key+'_low']=_split(value)
    save('actual_covariant_product_MP_proper_birth_columns_and_nonzero_seeds.npz',resultpacket)
    finish(dict(classification='EVALUATED_NEW_NORMALIZED_COVARIANT_PRODUCT_MP_PROPER_BIRTH_PHASE_APPLICATION',degree=degree,
        full_dimension=252+dim,phase_dimension=q,dynamic_count=n,normalization=norm['metrics'],
        child_original_Gauss_rows_upper=_upper(childgauss),parent_joint_Gauss_rows_upper=_upper(parentgauss),
        original_phase_without_named_reactions_upper=_upper(rawphase),original_saddle_upper=_upper(K*X-rhs),
        named_reaction_upper=_upper(reactions),natural_pairing_upper=_upper(natural-paired),
        child_canonical_seed_norm=float(np.linalg.norm(_mid(seed))),
        all_original_guard_pass=max(_upper(rawphase),_upper(childgauss),_upper(parentgauss))<=2e-10,
        held_chart_phase_source_contact_zero_by_parent_phase_lambda_value_incidence=True,
        full_new_wave_position_Hessian_or_nonlinear_Cauchy_operator_supplied=False,
        radial_temporal_quadrature_or_exterior_convergence_admitted=False,
        packed_owner_snapshot_sha256=sha256(snap.read_bytes()).hexdigest()),producer_paths=(Path(__file__),snap,workspace/'bhsm_baton_zoo_point_function_preconditioning.py'))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in('repository','assembly','products','tables','output'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--degree',type=int,default=2);a=p.parse_args();run(a.repository,a.assembly,a.products,a.tables,a.output,a.degree)
