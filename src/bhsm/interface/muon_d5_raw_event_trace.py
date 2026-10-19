"""Raw AE2 point traces, as distinct from localized normal-mode amplitudes.

The local wall-adapted coframe correspondence is evaluated here.  A map
of the entire E1 Cauchy cap is NOT inferred from its wall restriction.
No physical homogeneous state, color return, global spin sign, or relative
right translation is selected by these coordinate/representation laws.
"""
from __future__ import annotations

import numpy as np
from .muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace
from .muon_d5_child_higgs_seam_source_application import operator_consumed_lepton_lift


def colorless_trace_lift(*,include_neutral=True):
    """Both charge copies of original L6/7,e_c14,(n_c15), all Spin4.

    The neutral singlet is already in the original SM16 carrier; including
    its represented coefficient does not assert a new physical particle.
    Powers refer to u_H, so they are independent of its three sixth-charge
    roots. The full color288 complement remains a separate input sector.
    """
    indices=[];powers=[]
    internal=(6,7,14,15) if include_neutral else (6,7,14)
    hp={6:-1,7:-1,14:2,15:0}
    for family in range(3):
        for charge in range(2):
            for spin in range(4):
                for j in internal:
                    indices.append(128*family+64*charge+16*spin+j)
                    powers.append(hp[j]*(-1 if charge else 1))
    return np.eye(384)[:,indices],np.array(powers)


def colorless_middle_jet(known_middle128,known_middle_first128,unit_Higgs_phase,*,include_neutral=True):
    """Exact72/96 middle and all7 map velocities, no color/root choice."""
    C,powers=colorless_trace_lift(include_neutral=include_neutral)
    K=np.asarray(known_middle128);Kx=np.asarray(known_middle_first128);u=complex(unit_Higgs_phase)
    if K.shape!=(128,128) or Kx.shape!=(6,128,128) or abs(abs(u)-1)>2e-12:
        raise ValueError('actual joint Spin/weak factors and unit Higgs phase required')
    phase=np.diag(u**powers);full=np.kron(np.eye(3),K)
    value=C.T@full@C@phase
    first=np.array([C.T@np.kron(np.eye(3),x)@C@phase for x in Kx]
        +[value@np.diag(1j*powers)])
    return C,value,first


def sm_gauge_lift(weak_su2, hypercharge_sixth_phase, color_su3):
    """Full SM16+conjugate lift, with every group parameter explicit.

    If w=exp(-i alpha/(6 sqrt(10/3))), the Y_H=1/2 Higgs factor is w^3.
    All three roots remain possible until global bundle data identify them.
    This function supplies no identity color default.
    """
    K,C=np.asarray(weak_su2,complex),np.asarray(color_su3,complex)
    w=complex(hypercharge_sixth_phase)
    if K.shape!=(2,2) or C.shape!=(3,3) or abs(abs(w)-1)>2e-12:
        raise ValueError('explicit SU2, SU3 and unit sixth-charge phase required')
    for a in (K,C):
        if np.max(abs(a.conj().T@a-np.eye(len(a))))>2e-12 or abs(np.linalg.det(a)-1)>2e-12:
            raise ValueError('actual special unitary group factors required')
    f=full_d5_localized_lepton_trace()
    y=np.real(1j*np.sqrt(10/3)*np.diag(f['unitTr16_gauge_particle'][3]))
    powers=np.rint(6*y).astype(int)
    if np.max(abs(powers-6*y))>1e-12:
        raise ValueError('retained hypercharge ledger changed')
    G=np.eye(16,dtype=complex)
    G[:6,:6]=np.kron(C,K);G[6:8,6:8]=K
    G[8:11,8:11]=C.conj();G[11:14,11:14]=C.conj()
    G=G@np.diag(w**powers)
    Z=np.zeros((64,64),complex)
    return np.block([[np.kron(np.eye(4),G),Z],[Z,np.kron(np.eye(4),G.conj())]])


def raw_trace_transfer(parent_spin,child_spin,middle,*,spin_sign):
    """Raw point-section M=sign S_c K S_p^-1; no normal-mode division.

    This local wall-frame formula is conditional on that coframe incidence.
    The point trace of a global Dirac section is a spinor, not an arbitrary
    independently normalized full384 normal-mode amplitude.
    """
    p,c,k=map(np.asarray,(parent_spin,child_spin,middle))
    if spin_sign not in (-1,1) or p.shape!=(384,384) or c.shape!=p.shape or k.shape!=p.shape:
        raise ValueError('complete384 point frames, bundle factor and explicit spin sign required')
    return spin_sign*c@k@np.linalg.inv(p)


def raw_trace_transfer_first(parent_spin,child_spin,middle,parent_first,child_first,middle_first,*,spin_sign):
    """Every first placement, with no conjugation of a source coefficient."""
    p,c,k,px,cx,kx=map(np.asarray,(parent_spin,child_spin,middle,parent_first,child_first,middle_first))
    value=raw_trace_transfer(p,c,k,spin_sign=spin_sign);pi=np.linalg.inv(p)
    return value,spin_sign*(cx@k@pi+c@kx@pi-c@k@pi@px@pi)


def point_to_half_density_transfer(point_transfer,parent_density,child_density):
    """Change coordinates only: q_s=sqrt(mu_s) Psi_s, evaluated at F.

    q_c=sqrt(mu_c/(mu_p composed F)) M q_p composed F.  For an isometry,
    mu_c=(mu_p composed F)*|det DF|. The natural half-density pullback
    already contains sqrt(|det DF|); it must never be inserted twice.
    """
    p,c=float(parent_density),float(child_density)
    if min(p,c)<=0:raise ValueError('positive actual point densities required')
    return np.sqrt(c/p)*np.asarray(point_transfer)


def original_wall_green_checks(parent_spin,child_spin,middle,parent_lapse,child_lapse,
        parent_radius,child_radius,clock_differential):
    """Test original coframe/Dirac forms, not a Green form defined by M.

    These are the timelike WALL normal forms at the corner. They must not
    be mislabeled as the as-yet-unconstructed full E1 cap conormal.
    Opposite outward orientations insert a minus in the child Green form.
    """
    f=full_d5_localized_lepton_trace();G=np.array([np.kron(np.eye(3),g) for g in f['gamma5D_self_dual128']])
    p,c,k=map(np.asarray,(parent_spin,child_spin,middle));pi=np.linalg.inv(p);ci=np.linalg.inv(c)
    M=raw_trace_transfer(p,c,k,spin_sign=1)
    Np=p@G[4]@pi;Nc=c@G[4]@ci
    Tp=p@G[0]@pi;Tc=c@G[0]@ci
    rhop=complex(parent_lapse)*complex(parent_radius)**3
    rhoc=complex(child_lapse)*complex(child_radius)**3
    kap=complex(clock_differential)
    Jp=rhop*G[0]@Np;Jc=rhoc*G[0]@Nc
    return dict(point_transfer=M,parent_original_wall_green_form=Jp,child_original_wall_green_form=Jc,
        normal_Clifford_rows=M@Np-Nc@M,time_Clifford_rows=M@Tp-Tc@M,
        Dirac_bar_rows=M.conj().T@G[0]@M-G[0],
        density_pullback_row=np.array(rhoc-kap*rhop),
        original_wall_green_rows=M.conj().T@Jc@M-kap*Jp,
        normal_mode_factor_in_raw_transfer=False,full_E1_cap_incidence_derived=False)


def consume_raw_lepton_event(parent_coordinates,child_coefficients,middle128,child_spin128):
    """Original raw wall trace rows in the proved lepton block.

    Parent coordinates are S_p^-1 Gamma_raw,p from the saved bulk family.
    Child coefficients are unrestricted raw384 point coordinates. All36
    equations and every original parent column are retained. No physical
    child section or incoming/outgoing history continuation is inferred.
    """
    C,_=operator_consumed_lepton_lift();q=np.asarray(parent_coordinates)
    child=np.asarray(child_coefficients);K=np.kron(np.eye(3),np.asarray(middle128))
    Sc=np.kron(np.eye(3),np.asarray(child_spin128));L=C.T@np.linalg.inv(Sc)
    if q.ndim!=2 or q.shape[0]!=384 or child.shape!=q.shape:
        raise ValueError('same evaluated raw384 parent columns and child coordinate columns required')
    rhs=C.T@K@q
    return dict(original_lepton_event_rows=L@child-rhs,parent_rhs=rhs,
        child_trace_coefficient=L,parent_trace_coefficient=-C.T@K,
        structural_row_rank=36,physical_parent_h_constraint_rank_without_child_outer=0,
        parent_h_selected=False,child_bulk_solution_selected=False)


def required_raw_lepton_trace(parent_coordinates,parent_source,child_spin,
        child_spin_source,lepton_middle,lepton_middle_free_first,*,spin_sign):
    """Compute required birth-wall data, without selecting a child bulk field.

    The seven map velocities, independent state variations and total base
    pullback are coefficient ports. Only the supplied particular direction
    is contracted here. All parent columns (including3660 h) survive.
    """
    C,_=operator_consumed_lepton_lift()
    return required_raw_closed_trace(parent_coordinates,parent_source,child_spin,
        child_spin_source,C,lepton_middle,lepton_middle_free_first,spin_sign=spin_sign)


def required_raw_closed_trace(parent_coordinates,parent_source,child_spin,
        child_spin_source,closed_carrier_lift,middle,middle_free_first,*,spin_sign):
    """Same raw event application on any explicitly proved closed carrier."""
    C=np.asarray(closed_carrier_lift);n=C.shape[1]
    q,qx,S,Sx,K,Kx=map(np.asarray,(parent_coordinates,parent_source,
        child_spin,child_spin_source,middle,middle_free_first))
    if (q.ndim!=2 or q.shape[0]!=384 or qx.shape!=q.shape or S.shape!=(384,384)
            or Sx.shape!=S.shape or C.shape[0]!=384 or K.shape!=(n,n) or Kx.shape!=(7,n,n)
            or spin_sign not in (-1,1)):
        raise ValueError('actual complete parent columns, child frame and7 lepton map jets required')
    ql,qxl=C.T@q,C.T@qx
    target=spin_sign*K@ql;targetx=spin_sign*K@qxl
    raw=S@C@target;rawx=Sx@C@target+S@C@targetx
    free=spin_sign*np.einsum('ij,xjk,kl->xil',S@C,Kx,ql,optimize=True)
    left=C.T@np.linalg.inv(S)
    leftx=-left@Sx@np.linalg.inv(S)
    return dict(required_raw_lepton_projection384=raw,
        required_raw_lepton_projection_supplied_source384=rawx,
        required_raw_lepton_projection_free_map_source384=free,
        child_raw_trace_left=left,child_raw_trace_left_source=leftx,
        original_wall_trace_rows=left@raw-target,
        original_wall_trace_source_rows=leftx@raw+left@rawx-targetx,
        independent_state_source_coefficient384=raw,
        child_complement_projection_unassigned=True)
