"""Same restored contour graph Clifford square and its field cotangent.

The action uses the original holomorphic measure, the independently
reflected clock/coframe branch, and an initial-only right restriction.
No real-positive Gram or two-face tent domain replaces those data.
"""
from __future__ import annotations
import numpy as np
from scipy.linalg import eig,solve


def restored_clifford_coefficient_forms(quadrature,*,temporal_nodes,angular_derivatives,
        mean_source_gaunt,angular_levels,starting_loop_max_level,family):
    from .muon_native_dirac_hamiltonian import lepton_current_hilbert_representation
    from .muon_piecewise_euclidean_action import FAMILY_INDICES
    E=np.asarray(angular_derivatives,float);G=np.asarray(mean_source_gaunt,float)
    levels=np.asarray(angular_levels,int);n=temporal_nodes-1;h=E.shape[-1]
    if (type(temporal_nodes)is not int or temporal_nodes<2 or E.shape!=(3,h,h)
        or G.ndim!=3 or G.shape[:2]!=(h,h) or levels.shape!=(h,) or family not in(0,1,2)):
        raise ValueError('complete action angular and even mean-source images required')
    if np.max(abs(E+E.transpose(0,2,1)))>3e-12:raise ValueError('literal unit-Haar angular pairing required')
    if np.any(E[:,levels[:,None]!=levels[None,:]]!=0):raise ValueError('the base must preserve every degree exactly')
    fi=FAMILY_INDICES[family]
    alpha=lepton_current_hilbert_representation()['alpha'][:,fi][:,:,fi];B=-1j*alpha
    i0=np.zeros((n,n,6,6),complex);ie=np.zeros((n,n,3,6,6),complex)
    iee=np.zeros((n,n,3,3,6,6),complex);gram=np.zeros((n,n),complex)
    c0=np.zeros((n,n,n,24,6,6),complex)
    cl=np.zeros((n,n,n,24,3,6,6),complex);cr=np.zeros_like(cl)
    for q in quadrature:
        H,Hs,X,Xs=(np.asarray(q[k],complex)for k in('H','Hsharp','vertices','vertices_sharp'))
        if H.shape!=(6,6)or Hs.shape!=H.shape or X.shape!=(24,6,6)or Xs.shape!=X.shape:
            raise ValueError('independent full action coefficient and source branches required')
        w,ws,weight=map(complex,(q['right_clock'],q['reflected_clock'],q['measure']))
        R,Rs=map(complex,(q['R'],q['Rsharp']))
        if 0 in(w,ws,R,Rs):raise ValueError('nonzero coframe and both clocks required')
        rows=[(j-1,p,d)for j,p,d in q['rows']if j!=0]
        for j,pj,dj in rows:
            for k,pk,dk in rows:
                gram[j,k]+=weight*pj*pk
                i0[j,k]+=weight*(dj*dk*np.eye(6)/(ws*w)+dj*pk*H/ws+pj*dk*Hs/w+pj*pk*(Hs@H))
                for b in range(3):
                    ie[j,k,b]+=weight*(dj*pk*B[b]/(ws*R)+pj*dk*B[b]/(w*Rs)
                        +pj*pk*(Hs@B[b]/R+B[b]@H/Rs))
                    for a in range(3):iee[j,k,b,a]+=weight*pj*pk*(B[b]@B[a])/(Rs*R)
                for l,pl,dl in rows:
                    c0[j,k,l]+=weight*pl*(pj*dk*Xs/w+pk*dj*X/ws+pj*pk*(Xs@H+Hs@X))
                    for b in range(3):
                        cl[j,k,l,:,b]+=weight*pl*pj*pk*(Xs@B[b])/R
                        cr[j,k,l,:,b]+=weight*pl*pj*pk*(B[b]@X)/Rs
    d=6*h;K=np.zeros((n*d,n*d),complex)
    for j in range(n):
        for k in range(n):
            value=np.kron(i0[j,k],np.eye(h))
            value+=sum(np.kron(ie[j,k,b],E[b])for b in range(3))
            value+=sum(np.kron(iee[j,k,b,a],E[b]@E[a])for b in range(3)for a in range(3))
            K[j*d:(j+1)*d,k*d:(k+1)*d]=value
    return dict(K=K,M=np.kron(gram,np.eye(d)),first_identity_spin=c0,
        first_left_angular_spin=cl,first_right_angular_spin=cr,source_gaunt=G,
        angular_derivatives=E,angular_levels=levels,starting_loop_max_level=starting_loop_max_level,
        temporal_free_nodes=n,angular_count=h,mean_source_harmonics=G.shape[-1],
        original_complex_temporal_Gram=gram,complex_measure_replaced_by_absolute_value=False,
        scalar_current_removed_does_not_remove_induced_H=True)


def restored_clifford_first_form(coefficients,node,field,harmonic):
    c=coefficients;n,h=c['temporal_free_nodes'],c['angular_count'];d=6*h
    if node not in range(n)or field not in range(24)or harmonic not in range(c['mean_source_harmonics']):
        raise ValueError('actual field mean-source coefficient required')
    G=c['source_gaunt'][:,:,harmonic];E=c['angular_derivatives'];K=np.zeros_like(c['K'])
    for j in range(n):
        for k in range(n):
            a=np.kron(c['first_identity_spin'][j,k,node,field],G)
            a+=sum(np.kron(c['first_left_angular_spin'][j,k,node,field,b],G@E[b])
                +np.kron(c['first_right_angular_spin'][j,k,node,field,b],E[b]@G)for b in range(3))
            K[j*d:(j+1)*d,k*d:(k+1)*d]=a
    return K


def _gradient_from_density(coefficients,density):
    c=coefficients;n,h=c['temporal_free_nodes'],c['angular_count'];d=6*h
    G=c['source_gaunt'].transpose(2,0,1);E=c['angular_derivatives']
    GL=np.array([g@e for g in G for e in E]).reshape(len(G),3,h,h)
    GR=np.array([e@g for g in G for e in E]).reshape(len(G),3,h,h)
    result=np.zeros((n,24,len(G)),complex)
    for j in range(n):
        for k in range(n):
            R=density[k*d:(k+1)*d,j*d:(j+1)*d].reshape(6,h,6,h)
            t=np.einsum('byax,zxy->zba',R,G,optimize=True)
            result+=np.einsum('zba,lcab->lcz',t,c['first_identity_spin'][j,k],optimize=True)
            for b in range(3):
                tl=np.einsum('byax,zxy->zba',R,GL[:,b],optimize=True)
                tr=np.einsum('byax,zxy->zba',R,GR[:,b],optimize=True)
                result+=np.einsum('zba,lcab->lcz',tl,c['first_left_angular_spin'][j,k,:,:,b],optimize=True)
                result+=np.einsum('zba,lcab->lcz',tr,c['first_right_angular_spin'][j,k,:,:,b],optimize=True)
    return result


def restored_clifford_heat_field_cotangent(coefficients,cutoff,*,statistics_factor=.5):
    """Evaluate g/g_c on the literal generalized square, or reject its branch.

    Degree blocks keep the starting0..3 projector before any eigenbasis
    change; the full reached0..4 action is not compressed first. A complex
    spectrum or measure is not projected to a Hermitian reference.
    """
    c=coefficients;cutoff=float(cutoff);factor=float(statistics_factor)
    if cutoff<=0 or not np.isfinite([cutoff,factor]).all():raise ValueError('positive unchanged physical-cutoff probe required')
    M,K=c['M'],c['K'];P=solve(M,K);Mi=solve(M,np.eye(len(M)))
    lev=np.tile(c['angular_levels'],c['temporal_free_nodes']*6)
    cross=lev[:,None]!=lev[None,:]
    if np.any(P[cross]!=0):raise ValueError('exact invariant degree decomposition was changed')
    lam=np.empty(len(P),complex);V=np.zeros_like(P);Vi=np.zeros_like(P)
    residual=0.
    for degree in sorted(set(c['angular_levels'].tolist())):
        at=np.flatnonzero(lev==degree);value,basis=eig(P[np.ix_(at,at)])
        lam[at]=value;V[np.ix_(at,at)]=basis;Vi[np.ix_(at,at)]=solve(basis,np.eye(len(at)))
        residual=max(residual,float(np.max(abs(P[np.ix_(at,at)]@basis-basis*value))))
    starting=(lev<=c['starting_loop_max_level']).astype(float)
    common=dict(eigenvalues=lam,starting_eigenvector_weights=starting,
        minimum_real_eigenvalue=float(min(lam.real)),maximum_imaginary_eigenvalue=float(max(abs(lam.imag))),
        eigen_equation_absolute_residual=residual,eigen_equation_relative_residual=residual/float(np.max(abs(P))),
        original_K=K,original_M=M,statistics_factor=factor,
        original_complex_Gram_retained=True,original_initial_free_final_domain_retained=True,
        global_OS_relative_contour_or_physical_Pauli_identified=False)
    if min(lam.real)<=0:
        return dict(**common,heat_cotangent_evaluated=False,
            rejected_reason='the literal restored generalized spectrum is outside the declared accretive E1 branch; no absolute-value or sign replacement')
    exponential=np.exp(-cutoff*lam);left=Vi@Mi
    density=(V*(-starting*exponential/lam)[None,:])@left
    density_c=(V*(starting*exponential)[None,:])@left
    g=factor*_gradient_from_density(c,density);gc=factor*_gradient_from_density(c,density_c)
    # A different contraction computes representative original first-form
    # derivatives, checking all spin/angular/temporal trace placements.
    examples=[]
    for node,field,harmonic in((0,0,0),(c['temporal_free_nodes']-1,20,0),(0,3,c['mean_source_harmonics']-1)):
        F=restored_clifford_first_form(c,node,field,harmonic)
        examples.append(abs(factor*np.trace(density@F)-g[node,field,harmonic]))
    return dict(**common,heat_cotangent_evaluated=True,closed_field_cotangent=g,
        closed_field_cotangent_fixed_cutoff_partial=gc,
        gradient_original_first_form_identity_max=float(max(examples)),
        floating_exponential_underflow_count=int(np.count_nonzero(exponential==0)),
        source_coordinate_order=('all free trace nodes','wall field24','even0/2 mean source harmonics'),
        own_mean_geometry_clock_corner_or_total_c_jets_included=False,
        underflow_is_not_a_physical_error_enclosure=True)
