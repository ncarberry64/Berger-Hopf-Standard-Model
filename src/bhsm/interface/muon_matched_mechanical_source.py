"""Within-child mechanical connection on the actual saved muon photon modes.

This realizes a geometric attachment and the primitive Maxwell weak row.
It does not assert that the physical SM total connection is the mechanical
connection, or replace the same-owner finite-E1 induced Hessian by this row.
The differentiated coordinate is b, beta=T_b b. The carrier rotation below
depends only on w, so its b, tau and rho derivatives are zero at fixed base.
"""
from functools import lru_cache
import numpy as np
from bhsm.interface.muon_local_source_jet import _gaunt


def epsilon():
    e = np.zeros((3, 3, 3))
    for a, b, c in ((0, 1, 2), (1, 2, 0), (2, 0, 1)):
        e[a, b, c] = 1
        e[a, c, b] = -1
    return e


def rotation_coefficients():
    """Ad_w in phi_nmk=sqrt(n+1) conjugate(D^{n/2}_mk).

    The saved normalized Gaunt/reality conventions are unchanged. This
    1/sqrt(3) normalizes the new spin1 rotation, not the saved n1 source.
    """
    h = 1/np.sqrt(2)
    M = np.array([[-h, 0, h], [-1j*h, 0, -1j*h], [0, 1, 0]])
    R = np.zeros((3, 3, 3, 3), complex)
    labels = (2, 0, -2)
    for mi, m in enumerate(labels):
        for ki, k in enumerate(labels):
            R[:, :, labels.index(-m), labels.index(-k)] = (
                (-1.)**((m-k)//2)*np.outer(M[:, mi], M[:, ki].conj())/np.sqrt(3))
    return R


@lru_cache(None)
def product_tensor(ng, ns, nt):
    out = np.zeros((nt+1, nt+1, ng+1, ng+1, ns+1, ns+1))
    for gi, mg in enumerate(range(ng, -ng-1, -2)):
        for gj, kg in enumerate(range(ng, -ng-1, -2)):
            for si, ms in enumerate(range(ns, -ns-1, -2)):
                for sj, ks in enumerate(range(ns, -ns-1, -2)):
                    mt, kt = mg+ms, kg+ks
                    if abs(mt) <= nt and abs(kt) <= nt:
                        out[(nt-mt)//2, (nt-kt)//2, gi, gj, si, sj] = (
                            _gaunt((nt, mt, kt), (ng, mg, kg), (ns, ms, ks)))
    return out


def product(g, f, ns, nt):
    """Scalar normalized-harmonic multiplication; f may have leading axes."""
    return np.einsum('uvijkl,ij,...kl->...uv', product_tensor(2, ns, nt), g, f)


def transport(f, R):
    """Carrier-only Ad_U; preserve every connected angular output.

    f[n] has axes source, spatial coframe, unit-trace internal, m, k.
    Hypercharge is unchanged; the weak adjoint is R. No spatial spin frame
    is rotated here: all coefficients remain in the saved right coframe.
    """
    out = {}
    for ns, val in f.items():
        for nt in range(abs(ns-2), ns+3, 2):
            z = out.setdefault(nt, np.zeros((8, 3, 4, nt+1, nt+1), complex))
            for a in range(3):
                for b in range(3):
                    z[:, :, a] += product(R[a, b], val[:, :, b], ns, nt)
        out[ns][:, :, 3] += val[:, :, 3]
    return out


def angular_blocks(n, saved_curl=None):
    """Right coframe curl=*d and full weak curvature contact matrix."""
    e = epsilon()
    j = n/2
    weights = np.arange(n, -n-1, -2)/2
    plus = np.zeros((n+1, n+1), complex)
    for k in range(1, n+1):
        m = weights[k]
        plus[k-1, k] = np.sqrt((j-m)*(j+m+1))
    J = np.array([(plus+plus.T)/2, (plus-plus.T)/(2j), np.diag(weights)])
    S = -1j*e
    C = 2*np.eye(3*(n+1)) + sum(np.kron(S[a], 2*J[a]) for a in range(3))
    if saved_curl is not None:
        if np.linalg.norm(C-saved_curl) > 1e-13:
            raise ValueError('saved right-coframe curl convention differs')
        C = np.asarray(saved_curl)
    # axes spatial, internal, active weight (spectator weight untouched).
    C = np.einsum('imjn,cd->icmjdn', C.reshape(3,n+1,3,n+1), np.eye(4))
    ad = np.zeros((3, 4, 4))
    ad[:, :3, :3] = 2*e.transpose(0, 2, 1)
    T = np.einsum('iaj,acd,mn->icmjdn', e, ad, np.eye(n+1))
    B = np.zeros((3, 4, 3, 4))
    B[:, :3, :, :3] = np.einsum('kij,kcd->icjd', e, e)
    B = np.einsum('icjd,mn->icmjdn', B, np.eye(n+1))
    size = 12*(n+1)
    return C.reshape(size,size), T.reshape(size,size), B.reshape(size,size), J, ad


def apply(matrix, val):
    return np.einsum('ij,ajk->aik', matrix, val.reshape(8, matrix.shape[1], -1)).reshape(val.shape)


def direct_section0(source, R, lam, saved_curl):
    """d_Omega0 in the saved RIGHT coframe; Omega0_a=lambda R_ad jmath_d."""
    e = epsilon()
    C, _, _, _, ad = angular_blocks(1, saved_curl)
    out = {1: apply(C, source[1]), 3: np.zeros((8,3,4,4,4),complex)}
    for nt in (1,3):
        for c in range(3):
            for a in range(3):
                for b in range(3):
                    if not e[c,a,b]:
                        continue
                    for d in range(3):
                        comm = np.einsum('ij,Ajmk->Aimk', ad[d], source[1][:,b])
                        out[nt][:,c] += lam*e[c,a,b]*product(R[a,d], comm, 1, nt)
    return out


def realize(real_modes, saved_curl, lam):
    """Evaluate all eight actual sources; no fitted frame choice or pruning."""
    Y = np.asarray(real_modes)
    if Y.shape != (8,3,2,2):
        raise ValueError('actual saved eight photon lifts required')
    R = rotation_coefficients()
    # Hweak=-iT/sqrt2, HY=-iY/sqrt(10/3), unit primitive Tr16.
    s = np.array([0,0,np.sqrt(2),np.sqrt(10/3)])
    original = {1: np.einsum('Acmk,i->Acimk', Y, s)}
    transformed = transport(original, R)
    if set(transformed) != {1,3}:
        raise AssertionError('connected support changed')
    section0 = direct_section0(original,R,lam,saved_curl)
    rhs = transport(section0,R)  # retains n5 BEFORE testing cancellation
    direct = {}
    rows, curls, gradients, contacts = {}, {}, {}, {}
    gauss_action = {}
    for n, val in transformed.items():
        C,T,B,J,ad = angular_blocks(n, saved_curl if n==1 else None)
        direct[n] = apply(C+(lam-1)*T,val)
        # H(lambda)=C_h^dagger C_h+4lambda(lambda-1)B.
        Z = C-T
        rows[n] = np.array([apply(Z.conj().T@Z,val),
                           apply(Z.conj().T@T+T.conj().T@Z-4*B,val),
                           apply(T.conj().T@T+4*B,val)])
        curls[n] = np.array([apply(Z,val),apply(T,val)])
        contacts[n] = apply(4*lam*(lam-1)*B,val)
        # G_h=iP+h ad; retain temporal/radial constraint test rows.
        G0 = np.einsum('imn,cd->icmdn', 2j*J, np.eye(4))
        G1 = np.einsum('icd,mn->icmdn', ad, np.eye(n+1))
        G0=G0.reshape(12*(n+1),4*(n+1)); G1=G1.reshape(G0.shape)
        flat=val.reshape(8,12*(n+1),n+1)
        gradients[n] = np.array([np.einsum('ij,Ajk->Aik',(G0-G1).conj().T,flat),
                                 np.einsum('ij,Ajk->Aik',G1.conj().T,flat)]).reshape(2,8,4,n+1,n+1)
        gauss_action[n] = -np.einsum('icd,Aidmk->Acmk',ad,val)
    residual = np.sqrt(sum(np.linalg.norm(rhs[n]-direct.get(n,np.zeros_like(rhs[n])))**2 for n in rhs))
    # Exact representation identity proves cancellation, including n5;
    # this residual is only a binary64 implementation control.
    return dict(rotation=R, original=original, transformed=transformed,
                section0_curvature=section0, covariance_rhs=rhs,
                section1_curvature=direct, mixed_rows=rows, curls=curls,
                gradients=gradients, gauss_contact=gauss_action,
                curvature_contacts=contacts,
                covariance_absolute_residual=float(residual),
                connected_n5_cancellation_residual=float(np.linalg.norm(rhs[5])))


def lambda_jets(state, rho, lam, boundary_lapse, order=12):
    """Differentiate the retained parent ansatz; no new parent solve.

    v=sin(rho)^2 sum q_v,j cos(2j rho), qdot is coordinate time.
    lambda_rho=2lambda(1-lambda)(2v_rho-csc rho),
    lambda_tau=4lambda(1-lambda) vdot/N_boundary. Pole limits are zero.
    """
    y=np.asarray(state); j=np.arange(order); qdim=1+3*order
    qv=y[1+2*order:qdim]; dv=y[qdim+1+2*order:2*qdim]
    cs=np.cos(2*np.outer(rho,j)); sn=np.sin(2*np.outer(rho,j))
    vr=np.sin(2*rho)*(cs@qv)-2*np.sin(rho)**2*(sn@(j*qv))
    vt=np.sin(rho)**2*(cs@dv)/boundary_lapse
    lr=np.zeros_like(rho)
    good=rho!=0
    lr[good]=2*lam[good]*(1-lam[good])*(2*vr[good]-1/np.sin(rho[good]))
    return 4*lam*(1-lam)*vt, lr


def primitive_weak_application(realization, lam, electric, radial, shift, density, H, Tb,
                               lambda_tau, lambda_rho):
    """Apply corrected angular row in the inherited Lorentz weak operator.

    Return the dual spatial row and temporal/radial derivative pencils.
    The source is T_b*b*A; tests are T_b*v in the same moving frame. Thus
    D_tau=b_tau-H*b/2, and no profile/endpoint condition is invented.
    All coefficients below divide by Tr16 Q^2 ONCE to undo the charge
    trace already present in the saved e,r,d. No vertex gets a 2/3 factor.
    This is the primitive mechanical part; same-owner remainder is null.
    """
    qnorm = 16/3
    arrays = {}
    for n, rows in realization['mixed_rows'].items():
        row = rows[0][None]+lam[:,None,None,None,None,None]*rows[1][None]+lam[:,None,None,None,None,None]**2*rows[2][None]
        arrays[f'weak_angular_row_n{n}'] = -density[:,None,None,None,None,None]*row/qnorm
        val=realization['transformed'][n]
        arrays[f'weak_temporal_row_n{n}'] = electric[:,None,None,None,None,None]*val[None]/qnorm
        arrays[f'weak_radial_row_n{n}'] = -radial[:,None,None,None,None,None]*val[None]/qnorm
        # Each entry is a full internal/coframe/harmonic dual, not QQ only.
        grad=realization['gradients'][n]
        G=grad[0][None]+lam[:,None,None,None,None]*grad[1][None]
        arrays[f'constraint_gradient_n{n}'] = G
        arrays[f'constraint_temporal_jet_row_n{n}'] = -electric[:,None,None,None,None]*G/qnorm
        arrays[f'constraint_radial_Dtau_row_n{n}'] = electric[:,None,None,None,None]*shift[:,None,None,None,None]*G/qnorm
        arrays[f'constraint_radial_drho_row_n{n}'] = radial[:,None,None,None,None]*G/qnorm
        J=realization['gauss_contact'][n]
        fN=lambda_tau-shift*lambda_rho
        arrays[f'constraint_temporal_background_contact_n{n}'] = (
            (electric*fN)[:,None,None,None,None]*J[None]/qnorm)
        arrays[f'constraint_radial_background_contact_n{n}'] = (
            -(electric*shift*fN+radial*lambda_rho)[:,None,None,None,None]*J[None]/qnorm)
        # Spatial rows paired with a scalar temporal/radial test above
        # include curvature contacts; no ghost gauge fixing is invented.
    # Temporal conormal on the eight input columns, unintegrated at the cut.
    arrays['temporal_face_known_moving_coefficient'] = -electric*H/2
    arrays['temporal_face_radial_jet_coefficient'] = -electric*shift
    arrays['T_b'] = np.asarray(Tb)
    return arrays
