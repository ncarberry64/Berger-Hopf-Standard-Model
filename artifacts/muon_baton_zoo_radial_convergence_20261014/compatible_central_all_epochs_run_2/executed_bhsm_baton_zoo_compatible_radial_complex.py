"""Action-owned central derivative-compatible finite radial extension.

Four literal Arho profiles complete derivatives of every represented At
profile. All original action/Gauss/source rows are retained. Named central
At coefficient frames select a temporal representative; no small mode is
projected and no physical boundary or exterior condition is inferred.
"""
from pathlib import Path
from fractions import Fraction as Q
import argparse
import json
import sys


def exact_legendre_derivative_quotients(degree):
    """(d_y(phi P_l)-d_y(phi P_parity))/phi in monomials, rational."""
    def add(a,b):
        c=[Q(0)]*max(len(a),len(b))
        for i,x in enumerate(a):c[i]+=x
        for i,x in enumerate(b):c[i]+=x
        while len(c)>1 and not c[-1]:c.pop()
        return c
    def mul(a,b):
        c=[Q(0)]*(len(a)+len(b)-1)
        for i,x in enumerate(a):
            for j,y in enumerate(b):c[i+j]+=x*y
        return add(c,[Q(0)])
    def derivative(a):return [i*a[i]for i in range(1,len(a))]or[Q(0)]
    P=[[Q(1)],[Q(0),Q(1)]]
    for l in range(1,degree):
        P.append(add([Q(0)]+[Q(2*l+1,l+1)*x for x in P[-1]],[-Q(l,l+1)*x for x in P[-2]]))
    phi=[Q(1),Q(0),Q(-2),Q(0),Q(1)]
    results=[]
    for l in range(degree+1):
        dividend=add(derivative(mul(phi,P[l])),[-x for x in derivative(mul(phi,P[l%2]))])
        quotient=[Q(0)]*max(1,len(dividend)-4)
        while len(dividend)>=5:
            k=len(dividend)-5;c=dividend[-1];quotient[k]=c
            dividend=add(dividend,[Q(0)]*k+[-c*x for x in phi])
        if any(dividend):raise ValueError('literal derivative quotient is not exactly divisible by phi')
        coefficients=[Q(0)]*(degree+1);remainder=quotient[:]
        for k in reversed(range(len(remainder))):
            if k>=len(remainder):continue
            c=remainder[k]/P[k][-1];coefficients[k]=c
            remainder=add(remainder,[-c*x for x in P[k]])
        if any(remainder):raise ValueError('exact Legendre conversion failed')
        results.append(coefficients)
    return results


def derivative_profiles(rep,rho):
    """Actual fixed basis derivatives; affine f second uses spatial Jet."""
    import numpy as np
    from scipy.special import gammaln
    from bhsm.interface.muon_parent_retarded_hypercharge import WALL,ALPHA
    from bhsm.interface.muon_birth_trace_enriched_action import trace_enriched_radial_basis
    from bhsm.interface.muon_holomorphic_normal_geometry import _sin,_cos
    from bhsm.interface.aether_exact_radial_schur_lift_v15_83 import Jet
    rr=np.asarray(rho,float);x=rr/WALL
    B,Dr=trace_enriched_radial_basis(rep,rr)
    a,b=2.,4+2*ALPHA
    norms=np.array([np.exp(-(gammaln(j+a+1)+gammaln(j+b+1)-gammaln(j+1)-gammaln(j+a+b+1)-np.log(2*j+a+b+1))/2)for j in range(2)])
    c0,c1=norms;t=5+2*ALPHA;s=8+2*ALPHA
    wall2=ALPHA*(ALPHA-1)*x**(ALPHA-2)/WALL**2
    poly=[[c0,-c0],[-c1*t,c1*(s+t),-c1*s]]
    regular2=np.array([sum(c*(ALPHA+k)*(ALPHA+k-1)*x**(ALPHA+k-2)/WALL**2 for k,c in enumerate(p))for p in poly]).T
    lam2=[]
    for state in rep['affine_profile_reference_states']:
        q=[Jet.constant(complex(v),1)for v in state[:37]]
        values=[]
        for r in rr:
            chi=Jet.affine(r/2,np.array([.5]))
            shape=_sin(2*chi)**2*sum((q[25+j]*_cos(4*j*chi)for j in range(12)),Jet.constant(0.,1))
            A2=(4*shape).exp()*_cos(chi)**2;B2=_sin(chi)**2
            lam=A2/(A2+B2);values.append(lam.hessian[0,0])
        lam2.append(np.asarray(values))
    f2=(lam2[0]-lam2[1]-regular2@rep['affine_interior_projection']-rep['affine_wall_coefficient']*wall2)/rep['affine_complement_norm']
    y=2*x-1;phi=(1-y*y)**2
    phiy=4*y*(y*y-1);phiyy=12*y*y-4
    psi=np.c_[Dr[:,3],Dr[:,2],2*phiy/WALL,2*(phiy*y+phi)/WALL]
    psir=np.c_[wall2,f2,4*phiyy/WALL**2,4*(phiyy*y+2*phiy)/WALL**2]
    return dict(values=psi,radial_first=psir,old_values=B,old_first=Dr,norms=norms)


def extend(stage,a,rep,*,local_operands=None):
    """Assemble new x/v pairs from the literal local action at SAME state."""
    import numpy as np
    from bhsm_baton_zoo_radial_completion import pointwise_action_operands
    from bhsm.interface.muon_parent_retarded_hypercharge import WALL,ALPHA
    from bhsm.interface.muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation
    profiles=derivative_profiles(rep,a['rho']);nr=len(a['rho']);dim=len(a['Hessian']);n0=int(a['dynamic_count']);n=n0+4
    T=np.zeros((nr,60,8),complex)
    T[:,7,:4]=profiles['values'];T[:,47,:4]=profiles['radial_first'];T[:,27,4:]=profiles['values']
    local=pointwise_action_operands(stage)if local_operands is None else local_operands
    h,gd,g=[local[k]for k in('local_hessian','local_density_gradient','local_gradient')]
    E,D=a['full_augmented_point_lift'],a['full_augmented_density_lift'];P=stage['inherited_point_lift'];w=a['quadrature']
    bil=lambda l,r:np.einsum('rai,rab,r->ib',l,r,w,optimize=True)
    zc=bil(T,h@E+gd@D);cz=bil(E,h@T)+bil(D,gd.transpose(0,2,1)@T)
    zz=bil(T,h@T);zp=bil(T,h@P);pz=bil(P,h@T)
    gz=np.einsum('rai,ra,r->i',T,g,w,optimize=True)
    gt=h@stage['point_rate'][:,:,None]+gd@stage['density_rate'][:,:,None]
    gzt=np.einsum('rai,ra,r->i',T,gt[:,:,0],w,optimize=True)
    perm=np.r_[np.arange(n0),dim+np.arange(4),np.arange(n0,2*n0),dim+np.arange(4,8),np.arange(2*n0,dim)]
    inv=np.argsort(perm);old=inv[:dim]
    force=np.r_[a['baseline_Euler_force'],gz[:4]-gzt[4:],np.zeros(4,complex)]
    H=np.block([[a['Hessian'],cz],[zc,zz]])[np.ix_(perm,perm)]
    result={k:np.asarray(v).copy()for k,v in a.items()}
    for key in('added_position_indices','added_rate_indices','added_Gauss_indices','current288_to_augmented'):
        result[key]=old[np.asarray(a[key],int)]
    result.update(Hessian=H,baseline_Euler_force=force[perm],dynamic_count=np.asarray(n),
        inherited_source_Hcp=np.r_[a['inherited_source_Hcp'],zp][perm],
        inherited_source_Hpc=np.c_[a['inherited_source_Hpc'],pz][:,perm],
        full_augmented_point_lift=np.concatenate((E,T),axis=2)[:,:,perm],
        full_augmented_density_lift=np.pad(D,((0,0),(0,0),(0,8)))[:,:,perm],
        derivative_compatible_position_indices=inv[dim+np.arange(4)],
        derivative_compatible_rate_indices=inv[dim+np.arange(4,8)],
        previous_radial_to_augmented=old,derivative_compatible_point_lift=T,
        derivative_compatible_profile_values=profiles['values'],derivative_compatible_profile_radial_first=profiles['radial_first'],
        derivative_compatible_gradient=gz,derivative_compatible_gradient_rate=gzt)
    current=result['current288_to_augmented'];Ddegree=len(a['profile_degrees']);ng=Ddegree+5
    Z=np.zeros((len(H),ng),complex);F=np.zeros((ng,len(H)-n),complex)
    # Original x106/v106/y40 chart is mapped literally by the saved stage.
    original=current[np.asarray(stage['original_order_to_augmented'][:252],int)]
    At=original[212+24+np.array([3,7,11,15])]
    Ar=original[106+38+np.array([3,19,35,51])]
    phiAt=np.r_[current[284:288],result['added_Gauss_indices']].reshape(Ddegree+1,4)[:,3]
    phiAr=np.r_[current[228:244],result['added_rate_indices']].reshape(Ddegree+1,16)[:,3]
    ex=result['derivative_compatible_rate_indices'];c0,c1=profiles['norms'];t=5+2*ALPHA;s=8+2*ALPHA
    Z[At,np.arange(4)]=1
    Z[ex[0],0]=c0;Z[Ar[3],0]=-c0*(ALPHA+1)/WALL
    Z[ex[0],1]=-c1*t;Z[Ar[0],1]=c1*s*(ALPHA+2)/(WALL*c0);Z[Ar[3],1]=c1*(t*(ALPHA+1)-s)/WALL
    Z[ex[1],2]=1;Z[ex[0],3]=1
    rational=exact_legendre_derivative_quotients(Ddegree)
    for l in range(Ddegree+1):
        Z[phiAt[l],4+l]=1;Z[ex[2+l%2],4+l]=1
        for k,c in enumerate(rational[l]):Z[phiAr[k],4+l]=2*float(c)/WALL
    wall=np.r_[np.array([0.,0.,0.,1.]),np.zeros(Ddegree+1)]
    generatorH=higgs_u2_real_representation()['real_generators'][3]
    scalarH=np.asarray(stage['raw_pair'])[1,260:264]
    Z[np.ix_(original[208:212],np.arange(ng))]=-np.outer(generatorH@scalarH,wall)
    Atall=np.r_[At,phiAt];F[np.arange(ng),Atall-n]=1
    result['frames']=F
    # Evaluate the actual six-row proper owner independently of spatial
    # gauge traces. Its rows depend only on raw geometry100; Ar profiles
    # have zero geometry incidence, even when their wall gauge value is nonzero.
    from bhsm.interface.muon_complex_paired_normal_action import complex_proper_normal_trace
    from bhsm.interface.muon_holomorphic_two_arm_reset import holomorphic_moving_trace
    from bhsm.interface.muon_holomorphic_normal_geometry import _geometry_variables
    from bhsm.interface.muon_birth_trace_enriched_action import generic_coordinate_lift
    Praw=generic_coordinate_lift(rep['gauge_labels'])['lift']
    owned=complex_proper_normal_trace(np.asarray(stage['raw_pair'])[1],Praw)
    faces=derivative_profiles(rep,np.array([WALL]))
    face_lift=np.zeros((1,60,8),complex)
    face_lift[:,7,:4]=faces['values'];face_lift[:,47,:4]=faces['radial_first'];face_lift[:,27,4:]=faces['values']
    raw_geometry_new=np.zeros((100,len(H)),complex)
    raw_geometry_new[:,original]=Praw[:100]
    geometry_variables=_geometry_variables(np.asarray(stage['raw_pair'])[1,:100])
    proper_geo_rows=np.vstack((holomorphic_moving_trace(np.asarray(stage['raw_pair'])[1])['attachment_first'],
        owned['normal_projection']*geometry_variables[5].gradient))
    proper_child=np.zeros((3,len(H)-n),complex)
    proper_child[:,:n]=proper_geo_rows@raw_geometry_new[:,:n]
    proper_extra=proper_geo_rows@raw_geometry_new[:,inv[dim+np.arange(8)]]
    if np.max(abs(proper_child[:,original[106:212]-n]-owned['trace']))>2e-10:
        raise ValueError('fresh geometry-owner proper row does not reproduce saved original trace')
    result.update(actual_child_proper_trace=proper_child,actual_extra_geometry_incidence=raw_geometry_new[:,inv[dim+np.arange(8)]],
        actual_extra_proper_trace=proper_extra,spatial_face_added_point_lift=face_lift,
        spatial_wall_added_connection_reset_incidence=face_lift[0,:20],
        spatial_wall_added_radial_connection_reset_incidence=face_lift[0,40:60],
        spatial_origin_added_Ar_values=np.zeros(4),
        spatial_origin_radial_first_exponent=np.asarray(ALPHA-2),
        spatial_origin_radial_first_for_phi_derivatives=np.array([32.,-32.])/WALL**2,
        original_profile_derivative_origin_radial_first_is_bounded=np.asarray(False),
        full_augmented_original_geometry100_lift=raw_geometry_new,
        explicit_dynamic_position_indices=np.arange(n),explicit_dynamic_rate_indices=n+np.arange(n),
        explicit_original_Gauss_indices=np.arange(2*n,len(H)))
    point=result['full_augmented_point_lift']@Z;density=result['full_augmented_density_lift']@Z
    curvature=point[:,27]-point[:,43]
    fullHZ=H@Z;phaseHZ=fullHZ[n:]
    sourceZ=Z.T@result['inherited_source_Hcp'];parentZ=result['inherited_source_Hpc']@Z
    FZ=F@Z[n:];oldF=np.zeros((len(a['frames']),len(H)-n),complex);oldF[:,old[np.arange(n0,dim)]-n]=a['frames']
    gx=stage['original_child_gradient']if'original_child_gradient'in stage else None
    arrays=dict(literal_action_generators=Z,literal_phase_generators=Z[n:],frames_completed=F,
        original_and_previous_frames_embedded=oldF,all_central_At_coefficient_indices=Atall,
        completed_frame_generator_incidence=FZ,original_full_Hessian_generator_rows=fullHZ,
        original_phase_Hessian_generator_rows=phaseHZ,inherited_source_generator_rows=sourceZ,
        inherited_parent_generator_rows=parentZ,F_tau_rho_gauge_variation=curvature,
        gauge_density_variation=density,chi_wall=wall,literal_point_gauge_direction=point,
        full_scalar_velocity_generator_higgs_contact=-np.outer(generatorH@scalarH,wall),
        higgs_generator_first_per_scalar_position=-generatorH[:,:,None]*wall[None,None,:],
        actual_child_proper_trace=proper_child,actual_extra_proper_trace=proper_extra,
        added_spatial_face_point_lift=face_lift,
        added_profile_values=profiles['values'],added_profile_radial_first=profiles['radial_first'],
        old_to_new_full_action=old,previous_dynamic_count=np.asarray(n0),dynamic_count=np.asarray(n),
        material_At_frame_first_zero=np.asarray(True),coordinate_time=a['coordinate_time'])
    maximum=lambda v:float(np.max(abs(v)))if np.size(v)else 0.
    report=dict(degree=Ddegree,previous_dynamic_count=n0,dynamic_count=n,
        added_Ar_position_rate_pairs=4,new_At_or_Gauss_rows_added=0,all_original_Gauss_retained=True,
        complete_literal_central_generator_count=ng,completed_frame_count=ng,
        F_tau_rho_gauge_variation_max=maximum(curvature),phase_Hessian_generator_max=maximum(phaseHZ),
        full_Hessian_generator_max=maximum(fullHZ),source_generator_compatibility_max=maximum(sourceZ),
        parent_generator_compatibility_max=maximum(parentZ),frame_generator_identity_max=maximum(FZ-np.eye(ng)),
        independent_added_cross_transpose_difference=maximum(zc-cz.T),added_gradient_position_max=maximum(gz[:4]),
        added_position_Hessian_max=maximum(H[result['derivative_compatible_position_indices']]),
        added_position_source_max=maximum(result['inherited_source_Hcp'][result['derivative_compatible_position_indices']]),
        local_Arho_radial_gradient_max=maximum(g[:,47]),local_Arho_radial_Hessian_max=maximum(h[:,47]),
        scalar_Higgs_contact_included=True,full_Hessian_generator_requires_position_Noether_contact=True,
        actual_extra_proper_geometry_trace_max=maximum(proper_extra),
        spatial_wall_added_Ar_trace_max=maximum(face_lift[0,7]),
        spatial_wall_added_radial_Ar_trace_max=maximum(face_lift[0,47]),
        new_derivative_profiles_origin_value_zero_by_ALPHAgreater1=True,
        original_lift_derivative_radial_first_origin_finite=False,
        spatial_wall_extra_gauge_trace_assumed_zero=False,
        frame_selection_by_literal_coefficient_identity=True,numerical_eigenvector_or_threshold_projection=False,
        physical_or_exterior_domain_admitted=False)
    return dict(arrays=result,gauge_arrays=arrays,report=report)


def materialize(repository,assembly,output,degrees=(2,4,6,8),roles=('birth',)):
    from bhsm_baton_zoo_radial_convergence import environment
    root,out,read,save,finish=environment(repository,output)
    import numpy as np
    from evaluate_muon_continued_current_factor import retained_input
    from bhsm_baton_zoo_radial_completion import pointwise_action_operands
    phase,_=retained_input('outgoing',{});rep=phase['representation'];base=root/'artifacts/muon_baton_zoo_radial_completion_20261013'
    records=[]
    for role in roles:
        if role=='birth':stage=read(base/'action_gauge_degree2_run_1/birth_current288_connected_action_and_rate_operands.npz')
        elif role.startswith('cell_'):stage=read(root/f'artifacts/muon_baton_zoo_saved_rate_operands_20261013/joint_run_1/{role}_independent_rate_and_source_operands.npz')
        else:stage=read(base/'new_future_run_1'/f'{role}_connected_action_and_rate_operands.npz')
        local=pointwise_action_operands(stage)
        for degree in degrees:
            if degree in(2,4):
                if role=='birth':path=base/f'action_gauge_degree{degree}_run_1/enlarged_birth_radial_action.npz'
                elif role.startswith('cell_'):path=base/'assembly_run_1'/f'{role}_degree_{degree:02d}_connected_radial_action.npz'
                else:path=base/'new_future_run_1'/f'{role}_degree_{degree:02d}_connected_radial_action.npz'
            else:path=Path(assembly)/f'{role}_degree_{degree:02d}_connected_radial_action.npz'
            old=read(path);new=extend(stage,old,rep,local_operands=local)
            save(f'{role}_degree_{degree:02d}_compatible_connected_radial_action.npz',new['arrays'])
            save(f'{role}_degree_{degree:02d}_compatible_literal_central_frames.npz',new['gauge_arrays'])
            records.append(dict(role=role,**new['report']))
            print(json.dumps(dict(stage='compatible_central_radial_action',role=role,**new['report'])),flush=True)
    finish(dict(classification='EVALUATED_LITERAL_CENTRAL_DERIVATIVE_COMPATIBLE_RADIAL_ACTION_EXTENSION',
        records=records,physical_radial_convergence_admitted=False,
        literal_profile_derivatives_frozen_basis=True,spatial_derivative_contact_retained=True),producer_paths=(Path(__file__),))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repository',type=Path,required=True)
    p.add_argument('--assembly',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--degrees',type=int,nargs='+',default=[2,4,6,8]);p.add_argument('--all-epochs',action='store_true')
    args=p.parse_args();roles=[f'cell_{i:04d}'for i in range(15)]+['new_midpoint','new_endpoint','birth']if args.all_epochs else['birth']
    materialize(args.repository,args.assembly,args.output,tuple(args.degrees),tuple(roles))
