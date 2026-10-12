"""Clifford-derived weak action on complete supplied angular images.

The angular derivative/Gaunt matrices are the retained representation
maps, rather than eigenvectors of a source-compressed square.  This
module composes the executed proper-clock coefficient branches with
those maps before squaring and before constructing current moments.
It preserves the declared initial/free-final temporal graph.
"""
from __future__ import annotations
import numpy as np
from .muon_piecewise_euclidean_action import _basis,FAMILY_INDICES
from .muon_native_dirac_hamiltonian import lepton_current_hilbert_representation


def euclidean_open_action_vertices(radius,lapse,*,family=1):
    """Holomorphic action vertices, including the Clifford temporal phase.

R/N are the executed coefficient branch, and their opposite reflected
branch supplies the independent action dual.  Hreal coordinates are
ReH1,ReH2,ImH1,ImH2 before continuation.  No extra electric charge is
inserted in an already calibrated magnetic field coordinate.
    """
    from .muon_native_product_factor_graph import lepton_unit_trace_gauge_representation
    from .muon_continued_action_reality import _higgs_mass_realified
    R,N=complex(radius),complex(lapse)
    if not np.isfinite([R,N]).all()or abs(R)==0 or abs(N)==0:
        raise ValueError('nonzero executed coframe branch required')
    fi=FAMILY_INDICES[int(family)]
    rep=lepton_current_hilbert_representation();G=lepton_unit_trace_gauge_representation()['generators']
    gauge=np.zeros((5,4,18,18),complex)
    gauge[0]=-1j*G/N
    gauge[2:]=-1j*np.einsum('iuv,cvw->icuw',rep['alpha'],G)/R
    scalar=np.array([_higgs_mass_realified(e)for e in np.eye(4)])
    vertices=np.concatenate((gauge.reshape(20,18,18),scalar))[:,fi][:,:,fi]
    return dict(vertices=vertices,gauge=gauge[:,:,fi][:,:,:,fi],scalar=scalar[:,fi][:,:,fi],
        family_indices=fi,temporal_phase='-iG/N in the Clifford-derived A_E body',
        realified_H_coordinate_order=['ReH1','ReH2','ImH1','ImH2'],
        radial_zero_scope='intrinsic Dirac wall action only; parent radial/conormal action is separate',
        canonical_Gram=np.eye(6),electric_charge_inserted_again=False,
        field_coordinate='material Lorentz At_L,Ar_L,Ai_L evaluated on the complex physical-time branch; At_E=-iAt_L conversion belongs in a Euclidean-coordinate field map once')


def euclidean_node_field_images(phase,curves,nodes,*,source_axes=(0,1,2)):
    """Recover the same-action fields on both executed proper-clock branches.

The connection coefficients remain material Lorentz one-form coordinates.
This application does not insert an extra Wick rotation into field-chart
variables.  The explicit dt/dtau_E factors below are for time derivatives;
they are separate from an optional At_E=-iAt_L coefficient chart.
    """
    from .muon_continued_action_reality import (
        action_reality_coefficient,action_reality_source,_analytic_polynomial)
    from .muon_parent_maxwell_full_weak import M
    axes=np.asarray(source_axes,int);rows=[]
    for anchor,z,zs in zip(nodes['coordinate_anchor'],nodes['coordinate_offset'],nodes['reflected_coordinate_offset']):
        row={}
        for suffix,offset,sign in(('',z,-1),('_reflected',zs,1)):
            a=action_reality_coefficient(phase,anchor,offset);s=action_reality_source(phase,anchor,curves,offset)
            wall=a['wall_independent_plus_inherited'].copy()
            wall[2:]+=M*(a['geometry']['mechanical_lambda']-1)
            u=float(anchor)+abs(float(phase['receipt']['span']))if phase['receipt']['side']=='incoming'else float(anchor)
            pd=_analytic_polynomial(curves['positions'].derivative(),u,offset)
            source_Hd=pd[320:400].T.reshape(8,4,20)[axes]
            wd=_analytic_polynomial(curves['wall'].derivative(),u,offset).T.reshape(8,5,4,20)[axes]
            factor=sign*1j/a['geometry']['N']
            row.update({k+suffix:v for k,v in dict(
                raw_fields=a['raw'],wall_connection=wall,H_realified=a['raw'][-8:-4],
                H_coordinate_rate=a['raw'][-4:],H_Euclidean_proper_rate=factor*a['raw'][-4:],
                R=a['geometry']['R4'],N=a['geometry']['N'],mechanical_lambda=a['geometry']['mechanical_lambda'],
                source_wall=s['source_wall'][axes],source_H_realified=s['source_H'][axes],
                source_wall_coordinate_rate=wd,source_H_coordinate_rate=source_Hd,
                source_wall_Euclidean_proper_rate=factor*wd,source_H_Euclidean_proper_rate=factor*source_Hd).items()})
        rows.append(row)
    result={k:np.array([r[k]for r in rows])for k in rows[0]}
    result.update(source_axes=axes,
        field_coordinate='complexified material Lorentz one-form coefficients; no At coefficient rotation inserted',
        mechanical_connection_counted_once=True,inherited_profile_counted_once=True,
        Euclidean_rate='dt/dtau_E=-i/N; independent reflected dt_sharp/dtau_E=+i/Nsharp',
        reflected_wall_identity_max=float(np.max(abs(result['wall_connection_reflected']-result['wall_connection'].conj()))),
        reflected_H_identity_max=float(np.max(abs(result['H_realified_reflected']-result['H_realified'].conj()))))
    return result


def _family_positions(nodes,family):
    fi=FAMILY_INDICES[int(family)]
    indices=np.asarray(nodes.get('lepton_indices',np.arange(18)),int)
    if any(np.count_nonzero(indices==i)!=1 for i in fi):
        raise ValueError('all six fixed family coordinates required')
    return fi,np.array([np.flatnonzero(indices==i)[0]for i in fi])


def angular_action_coefficients(nodes,derivative_matrices,*,family=1):
    """Actual A_E and independent reflected body on one angular sector.

Derivative matrices use the real unit-Haar frame and are antisymmetric.
The canonical body is Hcan=W-iOmega_L.  No anti-Hermitian positive-reference
temporal gauge placement is imported.
    """
    fi,pos=_family_positions(nodes,family)
    E=np.asarray(derivative_matrices,float)
    if E.ndim!=3 or E.shape[0]!=3 or E.shape[1]!=E.shape[2]or not np.isfinite(E).all():
        raise ValueError('three complete square angular derivative maps required')
    if np.max(abs(E+E.swapaxes(-1,-2)))>2e-12:
        raise ValueError('retained unit-Haar derivative pairing required')
    alpha=lepton_current_hilbert_representation()['alpha'][:,fi][:,:,fi]
    angular=-1j*sum(np.kron(a,e)for a,e in zip(alpha,E))
    h=E.shape[1]
    forward=np.array([np.kron(H[np.ix_(pos,pos)],np.eye(h))+angular/R
                      for H,R in zip(nodes['H'],nodes['R'])])
    reflected=np.array([np.kron(H[np.ix_(pos,pos)],np.eye(h))+angular/R
                        for H,R in zip(nodes['Hsharp'],nodes['Rsharp'])])
    return dict(forward=forward,reflected=reflected,family_indices=fi,
        angular_count=h,angular_derivative_maps=E,
        reflected_identity_max=float(np.max(abs(reflected-forward.conj().swapaxes(-1,-2)))))


def angular_magnetic_coefficients(nodes,gaunt_target_source,*,family=1):
    """Both directed canonical Xi and the reflected reverse placement.

G[t,s,h] multiplies the actual source harmonic h.  The reverse Gaunt
placement is transposed explicitly.  Its independent reflected dagger
enters the square and numerator; Xi_ts alone cannot supply both contacts.
    """
    _,pos=_family_positions(nodes,family)
    G=np.asarray(gaunt_target_source,float)
    if G.ndim!=3 or G.shape[-1]!=nodes['Xi'].shape[2]or not np.isfinite(G).all():
        raise ValueError('complete real target/source/source-image Gaunt required')
    X=nodes['Xi'][:,:,:,pos][:,:,:,:,pos]
    Xs=nodes['Xisharp'][:,:,:,pos][:,:,:,:,pos]
    q,a=len(X),X.shape[1];ht,hs=G.shape[:2]
    forward=np.einsum('tsh,qahij->qaitjs',G,X,optimize=True).reshape(q,a,6*ht,6*hs)
    reverse=np.einsum('sth,qahij->qaisjt',G.transpose(1,0,2),X,optimize=True).reshape(q,a,6*hs,6*ht)
    reflected_reverse_dual=np.einsum('tsh,qahij->qaitjs',G,Xs,optimize=True).reshape(q,a,6*ht,6*hs)
    return dict(forward=forward,reverse=reverse,reflected_reverse_dual=reflected_reverse_dual,
        reverse_dual_identity_max=float(np.max(abs(reflected_reverse_dual-reverse.conj().swapaxes(-1,-2)))),
        source_axes=np.asarray(nodes['source_axes'],int))


def angular_weak_square(nodes,coefficient,*,temporal_cells):
    """Integrate the full angular form and its L2 Gram before inversion."""
    n=int(temporal_cells);H,Hs=coefficient['forward'],coefficient['reflected']
    d=H.shape[1];K=np.zeros((n*d,n*d),complex);M=np.zeros_like(K);I=np.eye(d)
    for q,t in enumerate(nodes['proper_time']):
        w=float(nodes['weight'][q]);basis=_basis(t,nodes['total_proper_clock'],n)
        product=Hs[q]@H[q]
        for j,pj,dj in basis:
            sj=slice(j*d,(j+1)*d)
            for k,pk,dk in basis:
                sk=slice(k*d,(k+1)*d)
                K[sj,sk]+=w*(dj*dk*I+dj*pk*H[q]+pj*dk*Hs[q]+pj*pk*product)
                M[sj,sk]+=w*pj*pk*I
    return dict(K=K,M=M,temporal_cells=n,field_count=d,
        right_initial_trace_zero=True,final_natural_trace_kept=True,
        shared_corner_trace=True,complete_angular_image_squared_before_inverse=True,
        Hermiticity_rounding_max=float(np.max(abs(K-K.conj().T))))


def angular_weak_square_contact(nodes,source,target,magnetic,*,temporal_cells):
    """Apply both square placements on the identical temporal graph."""
    n=int(temporal_cells);Hs,Ht=source['forward'],target['reflected']
    X,Xs=magnetic['forward'],magnetic['reflected_reverse_dual']
    a=X.shape[1];dt,ds=X.shape[-2:];delta=np.zeros((a,n*dt,n*ds),complex)
    for q,t in enumerate(nodes['proper_time']):
        w=float(nodes['weight'][q]);basis=_basis(t,nodes['total_proper_clock'],n)
        for j,pj,dj in basis:
            sj=slice(j*dt,(j+1)*dt);left=dj*np.eye(dt)+pj*Ht[q]
            for k,pk,dk in basis:
                sk=slice(k*ds,(k+1)*ds);right=dk*np.eye(ds)+pk*Hs[q]
                delta[:,sj,sk]+=w*(pj*np.einsum('aij,jk->aik',Xs[q],right)
                                  +pk*np.einsum('ij,ajk->aik',left,X[q]))
    return delta


def angular_current_moments(nodes,coefficient,right,left,*,temporal_cells,
                            delta_left=None):
    """Literal weak numerator and independent left-current moment.

    R/L are action-derived current maps at these nodes, without a hidden
    conjugation of the analytic left current.  deltaL is the actual left
    chart motion.  Rectangular deltaR and its Xi_st dagger numerator are
    applied by angular_current_contact_moments.  No shell is assigned.
    """
    R,L=np.asarray(right,complex),np.asarray(left,complex)
    Hs=coefficient['reflected'];n=int(temporal_cells);q,d=Hs.shape[:2]
    if R.shape[:2]!=(q,d)or L.shape[0]!=q or L.shape[-1]!=d:
        raise ValueError('current maps must use this executed coefficient graph')
    B=np.zeros((n*d,*R.shape[2:]),complex);target=np.zeros((*L.shape[1:-1],n*d),complex)
    dL=None
    if delta_left is not None:
        dl=np.asarray(delta_left,complex);dL=np.zeros((*dl.shape[1:-1],n*d),complex)
    for iq,t in enumerate(nodes['proper_time']):
        w=float(nodes['weight'][iq]);basis=_basis(t,nodes['total_proper_clock'],n)
        for j,pj,dj in basis:
            sj=slice(j*d,(j+1)*d);dual=dj*np.eye(d)+pj*Hs[iq]
            B[sj]+=w*np.einsum('ij,j...->i...',dual,R[iq]);target[...,sj]+=w*pj*L[iq]
            if dL is not None:dL[...,sj]+=w*pj*dl[iq]
    return dict(numerator=B,left_current=target,delta_left_current=dL)


def angular_current_contact_moments(nodes,source,target,magnetic,right,delta_right,
                                   *,temporal_cells):
    """Rectangular numerator: target dual deltaR + Xi_st dagger R."""
    R,dR=np.asarray(right,complex),np.asarray(delta_right,complex)
    Xs=magnetic['reflected_reverse_dual'];q,a,dt,ds=Xs.shape;n=int(temporal_cells)
    if R.shape[:2]!=(q,ds)or dR.shape[:3]!=(q,a,dt):
        raise ValueError('same source/target current maps required')
    result=np.zeros((a,n*dt,*R.shape[2:]),complex)
    for iq,t in enumerate(nodes['proper_time']):
        w=float(nodes['weight'][iq]);basis=_basis(t,nodes['total_proper_clock'],n)
        for j,pj,dj in basis:
            sj=slice(j*dt,(j+1)*dt);dual=dj*np.eye(dt)+pj*target['reflected'][iq]
            result[:,sj]+=w*(np.einsum('ij,aj...->ai...',dual,dR[iq])
                            +pj*np.einsum('aij,j...->ai...',Xs[iq],R[iq]))
    return result
