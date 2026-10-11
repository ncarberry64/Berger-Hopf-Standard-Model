"""Both source insertions and their contact on the changing n0 heat target.

The target is the previously differentiated n0/C6 temporal8 trace. Its
complete n1 source image is included before functional calculus; this is
not the heat of a compressed source matrix. The inherited positive
reference domain is explicit and does not identify the physical contour,
starting-loop complement, statistics, relative completion or Pauli value.
"""
from __future__ import annotations
import numpy as np
from scipy.linalg import cholesky, solve_triangular, eigh, eig
from .muon_profile_preserving_phase_sample import profile_preserving_lepton_sample
from .muon_source_directed_temporal_green import source_product_temporal_values
from .muon_native_mean_core_heat_target import _unit_lepton_mass6
from .muon_native_dirac_hamiltonian import lepton_current_hilbert_representation
from .muon_native_product_factor_graph import lepton_unit_trace_gauge_representation
from .muon_magnetic_cell_source_heat import _analytic_lag
from .muon_parent_retarded_hypercharge import WALL


def changing_source_heat_polynomial(phase, angular, first_field_sampler, *, quadrature_order=16):
    """Pull the actual first fields into the same varying proper-clock form.

    The first magnetic fields have gauge/H coordinates only. Geometry
    enters their vertices and the base measure; its second response is
    consumed separately by the joined mean adjoint. No source derivative
    of the held geometry or source Gram is assigned a numerical zero.
    It vanishes in this explicitly fixed-geometry partial by definition.
    """
    if not callable(first_field_sampler) or phase['receipt']['steps'] != 1:
        raise ValueError('same one-cell fields and actual first-field sampler required')
    if type(quadrature_order) is not int or quadrature_order < 8:
        raise ValueError('resolved split-cell quadrature required')
    L=abs(float(phase['receipt']['span']));z,w=np.polynomial.legendre.leggauss(quadrature_order)
    u=np.concatenate(((z+1)*L/4,(z+3)*L/4));weights=np.tile(w*L/4,2)
    apps=[profile_preserving_lepton_sample(phase,float(t-L if phase['receipt']['side']=='incoming' else t)) for t in u]
    tf=source_product_temporal_values(u,L);v,vd=tf['value'],tf['coordinate_rate']
    Gt=np.einsum('t,t,ta,tb->ab',weights,np.array([a['operator']['N'] for a in apps]),v,v)
    T=solve_triangular(cholesky(Gt,lower=True).T,np.eye(8),lower=False);v=v@T;vd=vd@T
    frame=lepton_current_hilbert_representation();fi=np.array([2,3,8,9,14,15]);fj=np.array([4,5,10,11,16,17])
    S=np.diag([1]*4+[-1]*2);alpha=frame['alpha'][:,fi][:,:,fi]
    generators=lepton_unit_trace_gauge_representation()['generators'][:,fi][:,:,fi]
    ids=np.array([j for j,l in enumerate(angular['harmonic_labels']) if l[0]==1])
    rest=np.setdiff1d(np.arange(len(angular['harmonic_labels'])),ids)
    if len(ids)!=4:raise ValueError('complete real n1 harmonic image required')
    E=np.asarray(angular['derivative_matrices'])[:,ids][:,:,ids]
    P=[np.zeros((48,48),complex) for _ in range(3)]
    PN=[np.zeros((192,192),complex) for _ in range(3)]
    F=[np.zeros((3,192,48),complex) for _ in range(3)]
    C=[np.zeros((3,3,48,48),complex) for _ in range(3)]
    G=np.zeros((48,48),complex);I=np.eye(6);records=[]
    for j,(uu,ww,app) in enumerate(zip(u,weights,apps)):
        op=app['operator'];N=float(op['N']);R=float(op['R4'])
        A=op['W'][np.ix_(fi,fi)]+op['Omega_tau'][np.ix_(fi,fi)];A=(A+S@A@S)/2
        other=op['W'][np.ix_(fj,fj)]+op['Omega_tau'][np.ix_(fj,fj)];other=(other+S@other@S)/2
        if np.any(A-other):raise ValueError('the common family Y0 coefficient is not identical')
        M=_unit_lepton_mass6(op['H'])
        V=np.concatenate([a*I for a in v[j]],axis=1);Vd=np.concatenate([a*I for a in vd[j]],axis=1)
        Vn=np.kron(np.eye(4),V)
        f0=Vd/N+A@V;f1=M@V
        bn=-1j*sum(np.kron(E[a],alpha[a]) for a in range(3))/R
        fn0=np.kron(np.eye(4),f0)+bn@Vn;fn1=np.kron(np.eye(4),f1)
        src=first_field_sampler(float(uu),np.array([WALL]))
        gauge=np.asarray(src['wall_gauge'])[:3];h=np.asarray(src['H'])[:3]
        if gauge.shape!=(3,5,4,20) or h.shape!=(3,4,20):raise ValueError('actual all first-field harmonic coefficients required')
        if np.any(gauge[...,rest]) or np.any(h[...,rest]):raise ValueError('a nonzero source complement needs its full shell application')
        xg=np.einsum('cij,Ach->Ahij',generators,gauge[:,0][:,:,ids])/N
        # Select the harmonic axis explicitly: NumPy advanced indices
        # otherwise put it before the field component axis.
        gs=gauge[:,2:][:,:,:,ids]
        xg+=-1j*np.einsum('auv,cvw,Aach->Ahuw',alpha,generators,gs)/R
        hc=h[:,:2][:,:,ids]+1j*h[:,2:][:,:,ids]
        xh=np.array([[_unit_lepton_mass6(a) for a in row.T] for row in hc])
        Xg=np.array([x.reshape(24,6)@V for x in xg]);Xh=np.array([x.reshape(24,6)@V for x in xh])
        # The opposite field vertex is the same indexed action matrix;
        # the adjoint belongs to the factor derivative, not the source.
        Rg=np.array([x.transpose(1,0,2).reshape(6,24)@Vn for x in xg])
        Rh=np.array([x.transpose(1,0,2).reshape(6,24)@Vn for x in xh])
        measure=ww*N;G+=measure*(V.conj().T@V)
        for target,a,b in ((P,f0,f1),(PN,fn0,fn1)):
            target[0]+=measure*(a.conj().T@a)
            target[1]+=measure*(a.conj().T@b+b.conj().T@a)
            target[2]+=measure*(b.conj().T@b)
        F[0]+=measure*(np.einsum('ij,Ajk->Aik',fn0.conj().T,Xg)+np.einsum('Aji,jk->Aik',Rg.conj(),f0))
        F[1]+=measure*(np.einsum('ij,Ajk->Aik',fn1.conj().T,Xg)+np.einsum('ij,Ajk->Aik',fn0.conj().T,Xh)
            +np.einsum('Aji,jk->Aik',Rg.conj(),f1)+np.einsum('Aji,jk->Aik',Rh.conj(),f0))
        F[2]+=measure*(np.einsum('ij,Ajk->Aik',fn1.conj().T,Xh)+np.einsum('Aji,jk->Aik',Rh.conj(),f1))
        products=(np.einsum('Aki,Bkj->ABij',Xg.conj(),Xg),
            np.einsum('Aki,Bkj->ABij',Xg.conj(),Xh)+np.einsum('Aki,Bkj->ABij',Xh.conj(),Xg),
            np.einsum('Aki,Bkj->ABij',Xh.conj(),Xh))
        for k,p in enumerate(products):C[k]+=measure*(p+p.swapaxes(0,1))
        records.append(dict(response_time=float(uu),N=N,R4=R,gauge_source_norm=float(np.linalg.norm(xg)),unit_Y_H_source_norm=float(np.linalg.norm(xh))))
    return dict(n0_pencil=tuple(P),n1_pencil=tuple(PN),first_source=tuple(F),contact=tuple(C),
        n0_Gram=G,n1_Gram=np.kron(np.eye(4),G),records=records,
        source_domain='all three retained e-normalized magnetic directions; real n1 source, exact zero n3 guard',
        target_domain='same n0/C6 all8 source-product temporal functions; all192 n1 image coordinates before inversion',
        normalization='canonical R^(3/2) spinor; unit Haar angular maps; N dt once; common temporal Gram whitening fixed across source directions',
        missing_source_second_operator_contact='for this fixed geometry affine gauge/H partial D_AB A=0; true interacting second response is the separate joined mean term',
        positive_reference_domain=True,physical_native_contour_identified=False)


def source_heat_pair_at_y(polynomial,Y,cutoff,*,lag_order=32):
    """Exact-domain contact plus the two ordered Duhamel insertions."""
    y=complex(Y);c=float(cutoff)
    if not np.isfinite([y.real,y.imag,c]).all() or c<=0:raise ValueError('actual finite parameter and positive cutoff required')
    ev=lambda coeff:sum(y**k*p for k,p in enumerate(coeff))
    p,pn=ev(polynomial['n0_pencil']),ev(polynomial['n1_pencil'])
    # Keep the small computed generalized-Gram defects instead of
    # replacing their matrices by the identity after whitening.
    G,GN=polynomial['n0_Gram'],polynomial['n1_Gram']
    lam,V=eig(p,G);ln,Vn=eig(pn,GN);Vi=np.linalg.solve(V,np.eye(len(V)));Vni=np.linalg.solve(Vn,np.eye(len(Vn)))
    if min(lam.real)<=0 or min(ln.real)<=0:raise ValueError('full represented analytic family must remain accretive')
    cc=np.array([[np.linalg.solve(G,a) for a in row] for row in ev(polynomial['contact'])])
    diagonal=np.einsum('ij,ABjk,ki->ABi',Vi,cc,V)
    contact=-np.einsum('i,ABi->AB',np.exp(-c*lam)/lam,diagonal)
    first=ev(polynomial['first_source'])
    reverse=ev(tuple(a.conj().swapaxes(-1,-2) for a in polynomial['first_source']))
    forward=np.einsum('ij,Ajk,kl->Ail',Vni,np.array([np.linalg.solve(GN,a)for a in first]),V)
    backward=np.einsum('ij,Ajk,kl->Ail',Vi,np.array([np.linalg.solve(G,a)for a in reverse]),Vn)
    lag=_analytic_lag(lam,ln,c,lag_order)
    ordered=np.einsum('Aij,Bji,ij->AB',backward,forward,lag)
    return dict(source_square_contact=contact,ordered_two_insertion=ordered,
        opposite_order_two_insertion=ordered.T.copy(),available_source_pair=contact+ordered+ordered.T)


def paired_source_heat_y2(polynomial,cutoff,*,radius=16384.,contour_order=32,lag_order=32):
    """Literal common-family Y2 coefficient; no subtraction at close poles."""
    r=float(radius)
    if r<=0 or type(contour_order)is not int or contour_order<16 or contour_order%2:
        raise ValueError('resolved even coefficient circle required')
    margins=[]
    for key,gkey in (('n0_pencil','n0_Gram'),('n1_pencil','n1_Gram')):
        coeff=polynomial[key];g=polynomial[gkey]
        x=solve_triangular(cholesky(g,lower=True).conj().T,np.eye(len(g)),lower=False)
        norm=[x.conj().T@a@x for a in coeff]
        margins.append(float(eigh(norm[0],eigvals_only=True)[0])-r*np.linalg.norm(norm[1],2)-r*r*np.linalg.norm(norm[2],2))
    if min(margins)<=0:raise ValueError('represented coefficient circle is not certified numerically accretive')
    sums={k:np.zeros((3,3),complex)for k in ('source_square_contact','ordered_two_insertion','opposite_order_two_insertion','available_source_pair')}
    for j in range(contour_order):
        theta=2*np.pi*(j+.5)/contour_order
        value=source_heat_pair_at_y(polynomial,r*np.exp(1j*theta),cutoff,lag_order=lag_order)
        weight=np.exp(-2j*theta)/(r*r*contour_order)
        for k in sums:sums[k]+=weight*value[k]
    sums['opposite_order_two_insertion']=sums['ordered_two_insertion'].T.copy()
    sums['available_source_pair']=sums['source_square_contact']+sums['ordered_two_insertion']+sums['opposite_order_two_insertion']
    Y=np.diag(lepton_current_hilbert_representation()['family_Y']).real;dy=Y[1]**2-Y[2]**2
    return dict(unit_Y2=sums,paired_Y2={k:dy*v for k,v in sums.items()},
        numerical_accretivity_margin=min(margins),radius=r,contour_order=contour_order,lag_order=lag_order,
        full_n1_source_image_retained=True,both_source_orders_retained=True,
        statistics_or_relative_completion_applied=False,physical_a_mu=None,physical_g_mu=None)
