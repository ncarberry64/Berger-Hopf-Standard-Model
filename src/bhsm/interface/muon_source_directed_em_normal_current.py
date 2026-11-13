"""Actual neutral-current and normal-test restrictions BEFORE field inverse.

The H-aligned connection-coordinate projection is derived from the retained
unit-Tr16 representation. Full coupled gauge/H, Gauss and named frame rows
are retained. C dyads are matching-test covectors on their owned normal
symbol, not an identification of this Euclidean current with Lorentz Pauli.
"""
from __future__ import annotations
from functools import lru_cache
import numpy as np
from scipy.linalg import solve


def holomorphic_charge_projection(realified_H):
    """Continue the SAME real H-selected neutral line, not H† at complex z.

    Coordinates are (ReH1,ReH2,ImH1,ImH2) before continuation. The algebraic
    opposite branch is formed before substituting complex coefficients.
    No measured charge or photon canonical normalization is inserted here.
    """
    h=np.asarray(realified_H,complex)
    if h.shape!=(4,)or not np.isfinite(h).all():raise ValueError('all four action H coordinates required')
    q=h@h
    if q==0:raise ValueError('the action H-selected neutral chart requires nonzero H norm')
    b=np.array([2*(h[0]*h[1]+h[2]*h[3]),2*(h[0]*h[3]-h[2]*h[1]),h[0]**2+h[2]**2-h[1]**2-h[3]**2])/q
    s=np.r_[-np.sqrt(2)*b,np.sqrt(10/3)]
    P=np.outer(s,s)/(16/3)
    return dict(unit_Tr16_charge_coefficients=s,projection=P,holomorphic_H_norm=q,
        exact_charge_norm_squared=16/3,projection_idempotence_max=float(np.max(abs(P@P-P))),
        normalized_physical_photon_or_charge_selected=False)


def neutral_wall_trace_map(trace_map,realified_H):
    """Project the current generator before inversion; H response remains.

    Scalar-current rows are zero only in this electromagnetic SOURCE
    restriction. Scalar columns and all mixing in the field action persist.
    """
    P=np.asarray(trace_map,complex)
    if P.ndim!=2 or P.shape[0]%24:raise ValueError('all24 wall field images required')
    nh=P.shape[0]//24;charge=holomorphic_charge_projection(realified_H)
    f=P.reshape(24,nh,-1);g=f[:20].reshape(5,4,nh,-1)
    selected=np.einsum('cd,fdhb->fchb',charge['projection'],g).reshape(20,nh,-1)
    result=np.concatenate((selected,np.zeros_like(f[20:])),axis=0).reshape(P.shape)
    return dict(wall_trace_map=result,**charge,scalar_field_action_removed=False,
        electromagnetic_connection_source_only=True,electric_charge_inserted=False)


@lru_cache(maxsize=1)
def normal_left_current_gaunt():
    """n1 external × n1 field has the COMPLETE n0+n2 internal image."""
    from .muon_intrinsic_scalar_discretization import scalar_s3_discretization
    s=scalar_s3_discretization(2);labels=s['real_basis_labels'];w=s['haar_weights']
    odd=np.array([j for j,l in enumerate(labels)if l[0]==1])
    even=np.array([j for j,l in enumerate(labels)if l[0]in(0,2)])
    y=s['real_basis_values'];g=np.einsum('qt,qh,qx,q->thx',y[:,even],y[:,odd],y[:,odd],w,optimize=True)
    n=np.array([labels[j][0]for j in even])
    g[(n[:,None,None]>2)*np.ones((1,4,4),bool)]=0
    return dict(gaunt=g,internal_harmonic_count=10,field_harmonic_count=4,external_harmonic_count=4,
        internal_labels=[labels[j]for j in even],external_labels=[labels[j]for j in odd],
        internal_derivatives=s['real_angular_derivative_matrices'][:,even][:,:,even])


def neutral_normal_current_moments(nodes,odd_coefficients,trace_map,H_coordinates,*,temporal_cells,family):
    """Build source J_R and n1-output literal left in its even image space.

    The left current uses the same literal action vertex, with real Gaunts
    and no conjugated left generator. At_L=iN At_E is applied ONCE. Right
    numerator and pure right current stay distinct. No fermion inverse is
    inserted before the normal left tests.
    """
    from .muon_piecewise_euclidean_action import _basis
    from .muon_euclidean_angular_weak_action import euclidean_open_action_vertices
    from .muon_literal_euclidean_wall_action import natural_wall_current_maps
    from .muon_changing_magnetic_momentum_columns import generalized_vertex_sources
    n=int(temporal_cells);P=np.asarray(trace_map,complex);H=np.asarray(H_coordinates,complex)
    if type(temporal_cells)is not int or n<1 or P.ndim!=2 or P.shape[0]!=96 or H.shape!=(len(nodes['weight']),4):
        raise ValueError('same complete n1 wall action and temporal coefficient representation required')
    db=P.shape[1];right=np.zeros((n*24,6,n*db),complex);num=np.zeros_like(right)
    left=np.zeros((24,n*60,n*db),complex);projections=[]
    G=normal_left_current_gaunt()['gaunt']
    for iq,t in enumerate(nodes['proper_time']):
        p=neutral_wall_trace_map(P,H[iq]);projections.append(p['projection'])
        V=euclidean_open_action_vertices(nodes['R'][iq],nodes['N'][iq],family=family)['vertices']
        maps=natural_wall_current_maps(V,p['wall_trace_map'],nodes['N'][iq],4)
        field=maps['Lorentz_field_image'].reshape(24,4,db)
        _,ell=generalized_vertex_sources(field,V,np.eye(10),G)
        for j,pj,dj in _basis(t,nodes['total_proper_clock'],n):
            sf,se=slice(j*24,(j+1)*24),slice(j*60,(j+1)*60)
            dual=dj*np.eye(24)+pj*odd_coefficients['reflected'][iq]
            for k,pk,dk in _basis(t,nodes['total_proper_clock'],n):
                sb=slice(k*db,(k+1)*db);w=float(nodes['weight'][iq])
                right[sf,:,sb]+=w*pj*pk*maps['right']
                num[sf,:,sb]+=w*pk*np.einsum('fg,gib->fib',dual,maps['right'])
                left[:,se,sb]+=w*pj*pk*ell
    return dict(literal_right_current=right,actual_A_sharp_numerator=num,
        literal_n1_left_current=left,charge_projection_nodes=np.array(projections),
        left_internal_even_image_count=10,right_internal_odd_image_count=4,
        source_charge_factor_inserted=False,physical_soft_Pauli_domain_identified=False)


def normal_test_wall_inverse(field,moments,normal_bundles):
    """Compute p/u using full action, with actual C tests BEFORE inverse.

    Each compressed C bundle has six literal left24 rows and rightI6.
    The n0+n2 internal fermion image is retained for p. p and u therefore
    have different internal index sets; no old eight-source inverse or
    uniform-three magnetic equivalence is asserted.
    """
    K=np.asarray(field['original_Hessian'],complex);C=np.asarray(field['frame_rows'],complex)
    X=np.asarray(field['original_action_Green'],complex);R=np.asarray(field['frame_reactions'],complex)
    J=np.asarray(moments['literal_right_current'],complex)
    B=np.asarray(moments['actual_A_sharp_numerator'],complex);L=np.asarray(moments['literal_n1_left_current'],complex)
    nb=len(K);jr=J.transpose(2,0,1).reshape(nb,-1);br=B.transpose(2,0,1).reshape(nb,-1)
    u,un=X@jr,X@br;ur=R@jr;nr=R@br
    saddle=np.block([[K,C.T],[C,np.zeros((len(C),len(C)),complex)]])
    answer=dict(literal_field_response=u,numerator_field_response=un,
        literal_response_reactions=ur,numerator_response_reactions=nr,
        literal_original_row_residual=K@u+C.T@ur-jr,
        numerator_original_row_residual=K@un+C.T@nr-br,normal_test_adjoint={})
    for name,rows in normal_bundles.items():
        result=[]
        for bundle in rows:
            ell=np.asarray(bundle['left_tests'],complex);right=np.asarray(bundle['right_tests'],complex)
            if ell.shape!=(6,24)or not np.array_equal(right,np.eye(6)):
                raise ValueError('complete C6 literal normal C covector required')
            soft=np.einsum('do,ofb->dfb',ell,L)
            jl=soft.transpose(2,0,1).reshape(nb,-1)
            rhs=np.vstack((jl,np.zeros((len(C),jl.shape[1]),complex)))
            p=solve(saddle.T,rhs,assume_a='gen')
            residual=K.T@p[:nb]+C.T@p[nb:]-jl
            result.append(dict(field_adjoint=p[:nb],frame_reactions=p[nb:],
                literal_normal_left_current=soft,literal_adjoint_source=jl,
                original_adjoint_residual=residual,frame_residual=C@p[:nb],
                original_adjoint_residual_max=float(np.max(abs(residual))),
                neutral_fibers_removed=False,normal_LSZ_transform_consumed=False))
        answer['normal_test_adjoint'][name]=result
    return answer


def full_wall_direction_images(nodes,trace_map,coefficients,*,node_index,temporal_cells,family):
    """Apply the FULL action vertex to solved p/u, including induced H.

    The neutral restriction belonged to the driving current. It is not
    reimposed on the solved coupled field, which can leave that source line.
    The opposite image is a literal reverse action placement, not a dagger.
    """
    from .muon_piecewise_euclidean_action import _basis
    from .muon_euclidean_angular_weak_action import euclidean_open_action_vertices
    from .muon_literal_euclidean_wall_action import natural_wall_current_maps
    if type(node_index)is not int or not 0<=node_index<len(nodes['weight']):raise ValueError('actual integer node required')
    P=np.asarray(trace_map,complex);q=np.asarray(coefficients,complex);n=int(temporal_cells)
    if type(temporal_cells)is not int or n<1 or q.ndim!=2 or q.shape[0]!=n*P.shape[1]:
        raise ValueError('same solved full-field temporal coefficient vector required')
    iq=node_index;v=euclidean_open_action_vertices(nodes['R'][iq],nodes['N'][iq],family=family)['vertices']
    maps=natural_wall_current_maps(v,P,nodes['N'][iq],4)
    values=sum(p*q[j*P.shape[1]:(j+1)*P.shape[1]]for j,p,d in _basis(nodes['proper_time'][iq],nodes['total_proper_clock'],n))
    return dict(wall_image=maps['Lorentz_field_image']@values,
        Xi_forward=np.einsum('fib,bc->fic',maps['right'],values),
        Xi_literal_reverse=np.einsum('ifb,bc->ifc',maps['literal_left'],values),
        induced_H_response_retained=True,source_neutral_projection_reimposed_on_response=False,
        independent_reflected_heat_dual_or_physical_Pauli_selected=False)
