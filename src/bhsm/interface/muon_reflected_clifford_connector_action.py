"""Independent reflected proper-frame coefficients on corner connectors.

The right clock is w=i*N*t_s and the reflected clock is
w_sharp=-i*N_sharp*conj(t_s).  The original holomorphic action measure
w ds is retained.  In particular, this module does not replace it by
sqrt(w_sharp*w) ds, identify that pairing with a maximal OS heat domain,
or turn a spectral Schur value at zero into a heat return.
"""
from __future__ import annotations
import numpy as np


def reflected_clock_pair(N, Nsharp, coordinate_slope):
    """Pull back the two independently reflected Clifford coframes."""
    slope = complex(coordinate_slope)
    w = 1j*complex(N)*slope
    ws = -1j*complex(Nsharp)*slope.conjugate()
    if w == 0 or ws == 0:
        raise ValueError('a regular nonzero action clock is required')
    return dict(right_clock=w, reflected_clock=ws,
                paired_principal=1/(ws*w), left_boundary_ratio=w/ws,
                original_holomorphic_density=w,
                reflected_clock_identity_defect=abs(ws-w.conjugate()))


def reflected_connector_forms(segments, *, current, cells_per_segment=4,
                              quadrature_order=4):
    """Integrate the reflected weak product, source jets and all face rows.

    A segment is (branches, source_branches, start, stop).  ``branches(t)``
    returns (H_s,H_t,N,H_s_sharp,H_t_sharp,N_sharp) by the original realified
    action reality map.  ``source_branches(t)`` returns the two directed
    Xi matrices and their INDEPENDENT reflected placements in the same
    coefficient coordinate, not conjugated direction coefficients.

    This is the explicit reflected-frame product with the retained right
    action density. Its integration-by-parts contact is w/w_sharp at each
    face; the derivative of that ratio enters the formal transpose.  A
    separate density/domain identification is required for positive OS heat.
    """
    n, q = cells_per_segment, quadrature_order
    if type(n) is not int or n < 1 or type(q) is not int or q < 2 or not segments:
        raise ValueError('resolved actual connector intervals are required')
    hs, ht, _, sh, th, _ = segments[0][0]((segments[0][2]+segments[0][3])/2)
    x10, x01, xs10, xs01 = segments[0][1]((segments[0][2]+segments[0][3])/2)
    ds, dt, axes = len(hs), len(ht), len(x10)
    Q = np.asarray(current, complex)
    if Q.shape != (ds, ds):
        raise ValueError('the literal current operator on the source carrier is required')
    count = len(segments)*n+1
    f = dict(source_K=np.zeros((count*ds, count*ds), complex),
             source_M=np.zeros((count*ds, count*ds), complex),
             target_K=np.zeros((count*dt, count*dt), complex),
             target_M=np.zeros((count*dt, count*dt), complex),
             magnetic_delta_K10=np.zeros((axes, count*dt, count*ds), complex),
             magnetic_delta_K01=np.zeros((axes, count*ds, count*dt), complex),
             source_square_contact=np.zeros((axes, axes, count*ds, count*ds), complex),
             source_numerator=np.zeros((count*ds, ds), complex),
             magnetic_delta_numerator=np.zeros((axes, count*dt, ds), complex),
             literal_left_current=np.zeros((ds, count*ds), complex))
    clocks, sharpclocks, principal, ratio, endpoints = [], [], [], [], []
    gx, gw = np.polynomial.legendre.leggauss(q)
    for seg, (branches, sources, start, stop) in enumerate(segments):
        slope = complex(stop)-complex(start)
        for t in (complex(start), complex(stop)):
            _, _, N, _, _, Ns = branches(t)
            clock = reflected_clock_pair(N, Ns, slope)
            endpoints.append([t, clock['left_boundary_ratio']])
        for cell in range(n):
            for z, g in zip(gx, gw):
                v = (1+z)/2
                s = (cell+v)/n
                t = complex(start)+s*slope
                hs, ht, N, sh, th, Ns = branches(t)
                x10, x01, xs10, xs01 = sources(t)
                hs, ht, sh, th = (np.asarray(a, complex) for a in (hs,ht,sh,th))
                x10, x01, xs10, xs01 = (np.asarray(a, complex) for a in (x10,x01,xs10,xs01))
                if (hs.shape != (ds,ds) or ht.shape != (dt,dt)
                        or sh.shape != hs.shape or th.shape != ht.shape
                        or x10.shape != (axes,dt,ds) or xs10.shape != x10.shape
                        or x01.shape != (axes,ds,dt) or xs01.shape != x01.shape):
                    raise ValueError('both complete coefficient/source branches must be retained')
                clock = reflected_clock_pair(N, Ns, slope)
                w, ws = clock['right_clock'], clock['reflected_clock']
                measure = g/(2*n)*w
                clocks.append(w); sharpclocks.append(ws)
                principal.append(clock['paired_principal']); ratio.append(clock['left_boundary_ratio'])
                rows = ((seg*n+cell,1-v,-n), (seg*n+cell+1,v,n))
                for j,pj,dj in rows:
                    sj, tj = slice(j*ds,(j+1)*ds), slice(j*dt,(j+1)*dt)
                    Lj, Tj = dj/ws*np.eye(ds)+pj*sh, dj/ws*np.eye(dt)+pj*th
                    f['source_numerator'][sj] += measure*Lj@Q
                    f['magnetic_delta_numerator'][:,tj] += measure*pj*np.einsum('aij,jk->aik',xs10,Q)
                    f['literal_left_current'][:,sj] += measure*pj*Q
                    for k,pk,dk in rows:
                        sk, tk = slice(k*ds,(k+1)*ds), slice(k*dt,(k+1)*dt)
                        Ak, Tk = dk/w*np.eye(ds)+pk*hs, dk/w*np.eye(dt)+pk*ht
                        f['source_K'][sj,sk] += measure*Lj@Ak
                        f['target_K'][tj,tk] += measure*Tj@Tk
                        f['source_M'][sj,sk] += measure*pj*pk*np.eye(ds)
                        f['target_M'][tj,tk] += measure*pj*pk*np.eye(dt)
                        f['magnetic_delta_K10'][:,tj,sk] += measure*(pj*np.einsum('aij,jk->aik',xs10,Ak)
                            +pk*np.einsum('ij,ajk->aik',Tj,x10))
                        f['magnetic_delta_K01'][:,sj,tk] += measure*(pj*np.einsum('aij,jk->aik',xs01,Tk)
                            +pk*np.einsum('ij,ajk->aik',Lj,x01))
                        c = np.einsum('aij,bjk->abik',xs01,x10)
                        f['source_square_contact'][:,:,sj,sk] += measure*pj*pk*(c+c.swapaxes(0,1))
    f.update(right_clock=np.array(clocks), reflected_clock=np.array(sharpclocks),
             paired_principal=np.array(principal), left_boundary_ratio=np.array(ratio),
             endpoint_coordinate_and_boundary_ratio=np.array(endpoints),
             source_count=ds,target_count=dt,source_axes=axes,temporal_nodes=count,
             original_holomorphic_density_replaced=False,
             independent_source_coefficients_conjugated=False,
             both_endpoint_trace_and_clock_conormal_contacts_retained=True,
             formal_transpose_clock_contact='-(d_s(w/w_sharp))/w',
             positive_OS_or_native_relative_domain_identified=False)
    return f


def actual_reflected_branches(phase, curves, anchor, family=1):
    """Bind coefficient and source reality branches from the executed action.

    This existing three-axis magnetic source is used only to evaluate the
    connector coefficient/action map. It is not an assignment of those
    axes to the source-directed p/u photon or to the physical Pauli current.
    """
    from .muon_continued_action_reality import action_reality_coefficient, action_reality_source
    from .muon_piecewise_euclidean_action import FAMILY_INDICES
    from .muon_native_dirac_hamiltonian import lepton_current_hilbert_representation
    from .muon_changing_magnetic_current_jets import magnetic_current_angular_images
    fi = FAMILY_INDICES[int(family)]
    rep = lepton_current_hilbert_representation()
    alpha = rep['alpha'][:,fi][:,:,fi]
    E = magnetic_current_angular_images()['derivatives']['field_odd']
    angular = -1j*sum(np.kron(a,e) for a,e in zip(alpha,E))
    def branches(t):
        z = complex(t)-float(anchor)
        a = action_reality_coefficient(phase,float(anchor),z)
        reflected = action_reality_coefficient(phase,float(anchor),z.conjugate())
        H = a['Hcan'][np.ix_(fi,fi)]
        # This is the opposite coefficient branch used by the executed
        # Clifford cells.  On the realified reality branch it is H(t)^dagger,
        # not H(conj(t))^dagger (the latter is a different holomorphic map).
        Hs = reflected['Hcan'][np.ix_(fi,fi)]
        N, Ns = a['geometry']['N'],reflected['geometry']['N']
        R, Rs = a['geometry']['R4'],reflected['geometry']['R4']
        return H,np.kron(H,np.eye(20))+angular/R,N,Hs,np.kron(Hs,np.eye(20))+angular/Rs,Ns
    def sources(t):
        z = complex(t)-float(anchor)
        X = action_reality_source(phase,float(anchor),curves,z)['Xi'][:3][:,:,fi][:,:,:,fi]
        S = action_reality_source(phase,float(anchor),curves,z.conjugate())['Xi'][:3][:,:,fi][:,:,:,fi]
        return (X.transpose(0,2,1,3).reshape(3,120,6),
                X.transpose(0,2,3,1).reshape(3,6,120),
                S.transpose(0,2,1,3).reshape(3,120,6),
                S.transpose(0,2,3,1).reshape(3,6,120))
    return branches,sources


def reflected_derivative_green_identity(w, wsharp, w_first, wsharp_first,
                                       left,left_first,right,right_first,weights):
    """Integrate the exact clock contact of the reflected derivative.

    Returns the integrand whose integral is [rho*left^T*right], with
    rho=w/w_sharp.  Supplied derivatives are with respect to the SAME
    real connector parameter; this displays, rather than suppresses,
    the extra clock contact in the literal formal transpose.
    """
    w,ws,dw,dws = (np.asarray(a,complex) for a in (w,wsharp,w_first,wsharp_first))
    l,dl,r,dr = (np.asarray(a,complex) for a in (left,left_first,right,right_first))
    q = np.asarray(weights,float)
    if w.ndim != 1 or any(a.shape != w.shape for a in (ws,dw,dws,q)) or any(a.shape != l.shape for a in (dl,r,dr)) or l.shape[0]!=len(w):
        raise ValueError('same clock/test/right germs and quadrature are required')
    rho = w/ws
    rhoprime = dw/ws-w*dws/ws**2
    pair = np.einsum('qi,qi->q',l,r)
    integrand = rho*(np.einsum('qi,qi->q',dl,r)+np.einsum('qi,qi->q',l,dr))+rhoprime*pair
    return dict(boundary_derivative_integral=np.dot(q,integrand),
                clock_contact_integral=np.dot(q,rhoprime*pair),
                coefficient_conjugated=False)
