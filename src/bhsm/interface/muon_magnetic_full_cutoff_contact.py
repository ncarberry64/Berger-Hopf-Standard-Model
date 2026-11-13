"""Cutoff partial of the same-background magnetic contact and both insertions.

The fixed source/mean partial supplies the coefficient of cutoff motion in
the existing AE4 chain rule. It does not select c or replace its total jet.
The polynomial, source images and ungraded E1 sign are inherited unchanged.
"""
from __future__ import annotations
import numpy as np
from scipy.linalg import eig, eigh
from flint import acb,acb_mat,arb,ctx
from .muon_magnetic_cell_source_heat import _evaluate
from .muon_primal_cell_native_heat import _positive_length
from .muon_native_dirac_hamiltonian import lepton_current_hilbert_representation


def cutoff_lag_partial(left, right, cutoff, *, order=64):
    """d_c int_0^1 (1-v)e^-ck(c/k+1/k²)dv = -c int(1-v)e^-ck dv."""
    a,b=np.asarray(left),np.asarray(right);c=_positive_length(cutoff)
    if a.ndim!=1 or b.ndim!=1 or not len(a) or not len(b) or not all(np.isfinite(x).all() for x in (a,b)):
        raise ValueError('finite same operator spectra required')
    if min(a.real)<=0 or min(b.real)<=0 or type(order) is not int or order<8:
        raise ValueError('accretive spectra and resolved lag rule required')
    x,w=np.polynomial.legendre.leggauss(order);x=(x+1)/2;w=w/2
    result=np.zeros((len(a),len(b)),complex)
    for v,weight in zip(x,w):
        k=(1-v)*a[:,None]+v*b[None,:]
        result-=c*weight*(1-v)*np.exp(-c*k)
    return result


def analytic_magnetic_cutoff_partial(polynomial, yukawa_parameter, cutoff, *, lag_order=64):
    """Literal cutoff derivative of the retained ungraded source Hessian."""
    c=_positive_length(cutoff);z=complex(yukawa_parameter)
    if not np.isfinite([z.real,z.imag]).all():raise ValueError('finite analytic parameter required')
    P=_evaluate(polynomial['n0_pencil'],z);lam,V=eig(P);Vi=np.linalg.solve(V,np.eye(len(P)))
    if min(lam.real)<=0:raise ValueError('accretive source block required')
    C=_evaluate(polynomial['contact'],z)
    diagonal=np.einsum('ij,ABjk,ki->ABi',Vi,C,V)
    contact=np.einsum('i,ABi->AB',np.exp(-c*lam),diagonal)
    ordered=np.zeros_like(contact)
    for shell in polynomial['shells'].values():
        Pn=_evaluate(shell['pencil'],z);ln,Vn=eig(Pn);Vni=np.linalg.solve(Vn,np.eye(len(Pn)))
        if min(ln.real)<=0:raise ValueError('accretive actual source image required')
        F=_evaluate(shell['first_source'],z)
        reverse=_evaluate(tuple(p.conj().transpose(0,2,1) for p in shell['first_source']),z)
        forward=np.einsum('ij,Ajk,kl->Ail',Vni,F,V)
        backward=np.einsum('ij,Ajk,kl->Ail',Vi,reverse,Vn)
        weight=cutoff_lag_partial(lam,ln,c,order=lag_order)
        ordered+=np.einsum('Aij,Bji,ij->AB',backward,forward,weight)
    return dict(source_square_contact=contact,ordered_two_insertion=ordered,
        opposite_order_two_insertion=ordered.T.copy(),available_source_pair=contact+ordered+ordered.T)


def magnetic_cutoff_even_y2_partial(polynomial, cutoff, *, contour_radius=16384., contour_order=32, lag_order=64):
    """Same accretive-circle coefficient algorithm; no near-family subtraction."""
    c=_positive_length(cutoff);r=_positive_length(contour_radius)
    if type(contour_order) is not int or contour_order<16 or contour_order%2:
        raise ValueError('even resolved analytic contour required')
    margins=[]
    for p in [polynomial['n0_pencil']]+[s['pencil'] for s in polynomial['shells'].values()]:
        margins.append(float(min(eigh(p[0],eigvals_only=True)))-r*np.linalg.norm(p[1],2)-r*r*np.linalg.norm(p[2],2))
    if min(margins)<=0:raise ValueError('actual complete contour must remain accretive')
    sums={name:np.zeros(polynomial['contact'][0].shape[:2],complex) for name in
          ('source_square_contact','ordered_two_insertion','opposite_order_two_insertion','available_source_pair')}
    for j in range(contour_order):
        t=2*np.pi*(j+.5)/contour_order;z=r*np.exp(1j*t)
        value=analytic_magnetic_cutoff_partial(polynomial,z,c,lag_order=lag_order)
        weight=np.exp(-2j*t)/(r*r*contour_order)
        for name in sums:sums[name]+=weight*value[name]
    sums['opposite_order_two_insertion']=sums['ordered_two_insertion'].T.copy()
    sums['available_source_pair']=sums['source_square_contact']+sums['ordered_two_insertion']+sums['opposite_order_two_insertion']
    y=np.diag(lepton_current_hilbert_representation()['family_Y']).real;factor=y[1]**2-y[2]**2
    paired={name:factor*value for name,value in sums.items()}
    paired['available_source_pair']=paired['source_square_contact']+paired['ordered_two_insertion']+paired['opposite_order_two_insertion']
    return dict(unit_y2_partial=sums,paired_middle_minus_light_partial=paired,
        contour_radius=r,contour_order=contour_order,lag_order=lag_order,
        numerical_circle_accretivity_margin=min(margins),cutoff_probe=c,
        fixed_field_source_partial=True,physical_total_cutoff_jet_selected=False,
        physical_Pauli_or_overlap_cutoff_cancellation_claimed=False)


def enclosed_source_return_cutoff_partial(bare, native_lower, native_upper, native_imaginary,
        partial_lower, partial_upper, partial_imaginary, *, precision_bits=192):
    """Fixed-bare action partial U_c=-U R_c U, retaining all stored intervals."""
    arrays=[np.asarray(x) for x in (bare,native_lower,native_upper,native_imaginary,
                                  partial_lower,partial_upper,partial_imaginary)]
    if any(x.shape!=(3,3) or not np.isrealobj(x) or not np.isfinite(x).all() for x in arrays):
        raise ValueError('same active three-axis real stored coefficient arrays required')
    B,lo,hi,im,dl,du,di=arrays
    if np.any(lo>hi) or np.any(dl>du):raise ValueError('ordered real bounds required')
    if type(precision_bits) is not int or precision_bits<128:raise ValueError('certified precision>=128 required')
    with ctx.workprec(precision_bits):
        def hull(a,b):
            a,b=arb(float(a)),arb(float(b))
            return (a+b)/2+arb(0,(b-a)/2)
        A=acb_mat([[float(x) for x in row] for row in B])
        R=acb_mat([[acb(hull(lo[i,j],hi[i,j]),arb(float(im[i,j]))) for j in range(3)] for i in range(3)])
        Rc=acb_mat([[acb(hull(dl[i,j],du[i,j]),arb(float(di[i,j]))) for j in range(3)] for i in range(3)])
        I=acb_mat(np.eye(3).tolist());U=(A+R).solve(I);Uc=-U*Rc*U
        residual=(A+R)*Uc+Rc*U
        if not all(residual[i,j].contains(0) for i in range(3) for j in range(3)):
            raise ArithmeticError('interval differentiated source equation failed')
        def bound(x,upper):
            if x.is_zero():return 0.
            return np.nextafter(float(x.upper() if upper else x.lower()),np.inf if upper else -np.inf)
        result=dict(source_return_cutoff_partial=np.array([[complex(float(Uc[i,j].real.mid()),float(Uc[i,j].imag.mid()))
            for j in range(3)] for i in range(3)]),
            differentiated_source_equation_residual_upper=max(bound(abs(residual[i,j]),True) for i in range(3) for j in range(3)),
            fixed_bare_and_source_and_mean_partial=True,quantum_photon_Green_or_Pauli_promoted=False)
        for component in ('real','imag'):
            for upper in (False,True):result['source_return_cutoff_partial_'+component+('_upper' if upper else '_lower')]=np.array([
                [bound(getattr(Uc[i,j],component),upper) for j in range(3)] for i in range(3)])
        return result
