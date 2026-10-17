"""Common-Y coefficient and energy contacts of the literal joint wall current.

Y0 is an analytic expansion point of the same action coefficient, not a
massless physical state or a replacement of the calibrated external pole.
Odd coefficients are retained.  The field Green is one original coupled
gauge/H inverse, with its existing Gauss/frame reactions.
"""
from __future__ import annotations
import numpy as np
from scipy.linalg import solve
from .muon_piecewise_euclidean_action import _basis,FAMILY_INDICES
from .muon_continued_action_reality import _higgs_mass_realified
from .muon_euclidean_angular_weak_action import angular_action_coefficients,euclidean_open_action_vertices
from .muon_literal_euclidean_wall_action import natural_wall_current_maps
from .muon_native_dirac_hamiltonian import lepton_current_hilbert_representation


def inverse_polynomial_coefficients(K0,K1,K2,*,order):
    """Exact algebraic recurrence G_j=-G0(K1 G_(j-1)+K2 G_(j-2))."""
    p=tuple(np.asarray(a,complex)for a in(K0,K1,K2));n=len(p[0])
    if type(order)is not int or order<0 or any(a.shape!=(n,n)or not np.isfinite(a).all()for a in p):
        raise ValueError('complete quadratic operator polynomial and explicit order required')
    G=[solve(p[0],np.eye(n),assume_a='gen')]
    for j in range(1,order+1):G.append(-G[0]@(p[1]@G[j-1]+(p[2]@G[j-2]if j>1 else 0)))
    return np.array(G)


def joint_wall_current_y_coefficients(nodes,fields,derivatives,field_inverse,trace_map,*,temporal_cells,order=3):
    """Execute the shared Taylor current and literal continued-energy jets.

    The external analytic dual is exp(+E*tau), and the right source is
    exp(-E*tau).  Its first contacts are +tau and -tau.  This does not
    continue an internal operator or identify an interacting LSZ pole.
    """
    n=int(temporal_cells);P=np.asarray(trace_map,complex);E=np.asarray(derivatives,float)
    if type(temporal_cells)is not int or n<1 or type(order)is not int or order<2:
        raise ValueError('explicit FE domain and at least quadratic Y coefficient required')
    h=E.shape[1];df=6*h;db=P.shape[1];q=len(nodes['weight'])
    GH=np.asarray(field_inverse,complex)
    if P.shape!=(24*h,db)or GH.shape!=(n*db,n*db):raise ValueError('same full coupled wall Green and trace map required')
    Y=np.diag(lepton_current_hilbert_representation()['family_Y']);ym=float(Y[1]);fi=FAMILY_INDICES[1]
    fn=dict(nodes);fn['lepton_indices']=fi
    masses=[]
    for key,suffix in(('H',''),('Hsharp','_reflected')):
        original=np.asarray(nodes[key],complex);Hs=np.asarray(fields['H_realified'+suffix],complex)
        if original.shape!=(q,6,6)or Hs.shape!=(q,4):raise ValueError('same middle coefficient and both actual H branches required')
        mass=np.array([_higgs_mass_realified(x)[np.ix_(fi,fi)]/ym for x in Hs])
        fn[key]=original-ym*mass;masses.append(mass)
    c=angular_action_coefficients(fn,E,family=1)
    A1=np.array([np.kron(m,np.eye(h))for m in masses[0]])
    As1=np.array([np.kron(m,np.eye(h))for m in masses[1]])
    K=np.zeros((3,n*df,n*df),complex)
    R=np.zeros((3,n*df,6,n*db),complex);RE=np.zeros_like(R)
    L=np.zeros((2,6,n*df,n*db),complex);LE=np.zeros_like(L)
    for iq,tau in enumerate(nodes['proper_time']):
        vertex=euclidean_open_action_vertices(nodes['R'][iq],nodes['N'][iq],family=1)['vertices']
        vg=vertex.copy();vg[20:]=0
        vh=np.zeros_like(vertex);vh[20:]=vertex[20:]/ym
        maps=[natural_wall_current_maps(v,P,nodes['N'][iq],int(h))for v in(vg,vh)]
        for j,pj,dj in _basis(tau,nodes['total_proper_clock'],n):
            sf=slice(j*df,(j+1)*df);D0=dj*np.eye(df)+pj*c['reflected'][iq];D1=pj*As1[iq]
            for k,pk,dk in _basis(tau,nodes['total_proper_clock'],n):
                tf=slice(k*df,(k+1)*df);tb=slice(k*db,(k+1)*db);w=float(nodes['weight'][iq])
                U0=dk*np.eye(df)+pk*c['forward'][iq];U1=pk*A1[iq]
                K[0,sf,tf]+=w*D0@U0
                K[1,sf,tf]+=w*(D1@U0+D0@U1)
                K[2,sf,tf]+=w*D1@U1
                for degree,pairs in enumerate((((D0,maps[0]['right']),),
                         ((D0,maps[1]['right']),(D1,maps[0]['right'])),((D1,maps[1]['right']),))):
                    moment=w*pk*sum(np.einsum('fg,gib->fib',d,r,optimize=True)for d,r in pairs)
                    R[degree,sf,:,tb]+=moment;RE[degree,sf,:,tb]-=float(tau)*moment
                for degree,m in enumerate(maps):
                    moment=w*pj*pk*m['literal_left']
                    L[degree,:,sf,tb]+=moment;LE[degree,:,sf,tb]+=float(tau)*moment
    G=inverse_polynomial_coefficients(*K,order=order)
    coefficient=np.zeros((order+1,6,6),complex);energy=np.zeros_like(coefficient)
    for degree in range(order+1):
        for l in range(2):
            for r in range(3):
                g=degree-l-r
                if g<0:continue
                u=np.einsum('fg,gik->fik',G[g],R[r],optimize=True)
                ue=np.einsum('fg,gik->fik',G[g],RE[r],optimize=True)
                coefficient[degree]-=np.einsum('ofb,fik,bk->oi',L[l],u,GH,optimize=True)
                energy[degree]-=np.einsum('ofb,fik,bk->oi',LE[l],u,GH,optimize=True)
                energy[degree]-=np.einsum('ofb,fik,bk->oi',L[l],ue,GH,optimize=True)
    invariant=[Y[1]**j-Y[2]**j for j in range(order+1)]
    paired=np.einsum('j,jab->ab',invariant,coefficient)
    pairedE=np.einsum('j,jab->ab',invariant,energy)
    perturb=[float(np.linalg.norm(G[0]@(y*K[1]+y*y*K[2]),ord=2))for y in(Y[1],Y[2])]
    return dict(current_Y_coefficients=coefficient,continued_energy_first_Y_coefficients=energy,
        paired_current_coefficients_through_order=paired,paired_energy_coefficients_through_order=pairedE,
        fermion_K0_K1_K2=K,inverse_Y_coefficients=G,right_numerator_coefficients=R,
        literal_left_coefficients=L,right_energy_coefficients=RE,left_energy_coefficients=LE,
        family_Y=np.array([Y[1],Y[2]]),paired_monomial_coefficients=np.array(invariant),
        finite_operator_relative_perturbation_norm=perturb,
        analytic_Y0_does_not_strip_a_matched_external_pole=True,
        odd_Y_coefficients_retained=True,field_Green_is_same_full_coupled_inverse=True,
        external_energy_variable='continued Lorentz energy, analytic dual exp(+E*tau), source exp(-E*tau)',
        mass_counterterm_or_physical_LSZ_matching_completed=False,physical_a_mu=None,physical_g_mu=None)
