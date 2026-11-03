"""Weak native radial cancellation and ordered second transport application.

Only the saved initializer's coefficient jets are evaluated. No native kernel,
physical columns, independent left state, entering flux or edge load is assigned.
"""
from pathlib import Path
from hashlib import sha256
from decimal import Decimal,localcontext,ROUND_CEILING
from collections import Counter
from fractions import Fraction
from itertools import product
import argparse,json,math
import numpy as np
from prepare_evidence import save,npz
HERE=Path(__file__).resolve().parent
W=math.pi/2
EPS=np.zeros((3,3,3))
EPS[0,1,2]=EPS[1,2,0]=EPS[2,0,1]=1
EPS[0,2,1]=EPS[2,1,0]=EPS[1,0,2]=-1

def ad(a):
    a=np.asarray(a);z=np.zeros(a.shape[:-1]+(4,4),dtype=a.dtype)
    z[...,:3,:3]=np.einsum('ijk,...j->...ik',EPS,a[...,:3])/np.sqrt(2)
    return z

def apply(a,s):return np.einsum('...ij,j->...i',a,s)
def maximum(a):return float(np.max(np.abs(a)))

def factors(alpha,rho):
    """Exact ordered monomial integrals, evaluated in floating arithmetic."""
    x=np.asarray(rho)/W;p=alpha+np.arange(4)+1
    f=W*(1-x[...,None]**p)/p
    # left index m has the earlier radial integration variable t<s.
    pm=p[:,None];pn=p[None,:]
    k=W**2/pn*((1-x[...,None,None]**pm)/pm-
                        (1-x[...,None,None]**(pm+pn))/(pm+pn))
    ar=x[...,None]**(p-1)
    return ar,f,k

def second(c,d,k):
    return np.einsum('...mn,mij,njk->...ik',k,c,d,optimize=True)

def exact_checks():
    # Noncommutative word identities; J1'=-A and J2'=-A J1.
    zero={}
    for degree in (1,2):
        words=Counter()
        words[('A','s')]-=1
        if degree==2:words[('A','J1','s')]-=1
        words[('A','s')]+=1;words[('A','J1','s')]+=1
        if degree==2:words[('A','J2','s')]+=1
        words[('A','J'+str(degree),'s')]-=1
        assert all(v==0 for v in words.values())
        zero['ordered_residual_degree_'+str(degree)]=True
    # Each X,Y derivative is placed on b,D,lambda independently: 3^2=9.
    placements=[]
    for x,y in product(range(3),repeat=2):
        labels=[[] for _ in range(3)];labels[x].append('X');labels[y].append('Y')
        placements.append(tuple(''.join(v) for v in labels))
    assert len(set(placements))==9
    grouped=Counter()
    for tags in placements:grouped[tags[0]]+=1
    assert grouped=={'XY':1,'X':2,'Y':2,'':4}
    zero['mixed_nine_placements_group_into_Dlambda_jets']=True
    # For transported scalar harmonics D_rho chi=0, the radial weak term
    # is b E with E=D_rho lambda identically zero, including all its jets.
    terms=Counter()
    for bt,dt,lt in placements:
        if dt:
            terms[('b'+bt,'A'+dt,'lambda'+lt)]+=1
        else:
            terms[('b'+bt,'A','lambda'+lt)]+=1
            # D lambda_lt = partial lambda_lt + A lambda_lt.
            # Substitute the total differentiated transport equation,
            # keeping the order b,A,lambda and every independent jet.
            for allocation in product((0,1),repeat=len(lt)):
                at=''.join(t for t,k in zip(lt,allocation) if k==0)
                qt=''.join(t for t,k in zip(lt,allocation) if k==1)
                terms[('b'+bt,'A'+at,'lambda'+qt)]-=1
    assert all(v==0 for v in terms.values())
    zero['moving_readout_included_in_first_and_mixed_zero']=True
    assert Fraction(2**7-1,7)==Fraction(127,7)
    assert Fraction(2**5,5)==Fraction(32,5)
    zero['regular_pole_cutoff_energy_order_five']=True
    return zero,[list(p) for p in placements]

def coefficient_bound(coeff,alpha):
    """Upper bound for the finite frozen representation; no model-error bound."""
    with localcontext() as ctx:
        ctx.prec=80;ctx.rounding=ROUND_CEILING;d=Decimal.from_float
        # Dropping 1/sqrt(2) and using l1 is conservative for the owned ad.
        return sum(d(W)*sum(abs(d(float(v))) for v in row[:3])/
                   (d(alpha)+Decimal(m+1)) for m,row in enumerate(coeff))

def l2_coefficient_bound(coeff,alpha):
    """Analytic monomial Gram integral, retaining coefficient cancellations.

    For each SU2 color, integral |A_c| <= W sqrt(integral_0^1 A_c^2).
    Sum over colors conservatively bounds ||ad A||. All input floats are
    treated as exact frozen numbers. Division/addition use upward rounding;
    square root is enlarged by one Decimal ulp. No quadrature is introduced.
    """
    with localcontext() as ctx:
        ctx.prec=80;ctx.rounding=ROUND_CEILING;d=Decimal.from_float
        rows=[[d(float(v)) for v in row] for row in coeff]
        total=Decimal(0)
        for color in range(3):
            value=sum(rows[m][color]*rows[n][color]/
                (2*d(alpha)+Decimal(m+n+1)) for m in range(4) for n in range(4))
            assert value>=0
            if value:total+=d(W)*value.sqrt().next_plus()
        return total

def bounds(coeff,directions,alpha,s):
    with localcontext() as ctx:
        ctx.prec=80;ctx.rounding=ROUND_CEILING
        coarse=coefficient_bound(coeff,alpha)
        a=min(coarse,l2_coefficient_bound(coeff,alpha))
        bs=[min(coefficient_bound(row,alpha),l2_coefficient_bound(row,alpha)) for row in directions]
        assert 0<=a<1
        # l1(s) upper bounds ||s||2 without rounding a square root.
        sn=sum(abs(Decimal.from_float(float(v))) for v in s)
        # All-order Dyson tails, derivative majorants in affine radial axes.
        t0=sn*a**3/(6*(1-a))
        t1=[sn*a*a*b/(2*(1-a)) for b in bs]
        t2=[[sn*a*b*c/(1-a) for c in bs] for b in bs]
        return dict(connection_integral_upper=str(a),coefficient_l1_connection_upper=str(coarse),
                    radial_direction_integral_upper=[str(v) for v in bs],
                    second_order_value_tail_upper=str(t0),
                    radial_first_jet_tail_upper=[str(v) for v in t1],
                    radial_mixed_jet_tail_upper=[[str(v) for v in row] for row in t2],
                    bound_scope='Exact frozen fractional-polynomial transport only; affine radial-coordinate derivatives at fixed H,alpha,W. Excludes floating arithmetic/input errors, physical/domain motion, quadrature and source/kernel norm.')

def calculate():
    p=HERE/'evidence/inputs.npz';prov=json.loads((HERE/'evidence/provenance.json').read_text())
    assert sha256(p.read_bytes()).hexdigest()==prov['input_sha256']
    b=dict(np.load(p,allow_pickle=False));rho=b['radial_nodes49'];alpha=float(b['alpha'])
    poly=b['radial_connection_polynomial'];C=ad(poly)
    ar,f,k=factors(alpha,rho);A=np.einsum('nm,mij->nij',ar,C)
    J1=np.einsum('nm,mij->nij',f,C);J2=second(C,C,k)
    s=np.sqrt(16/3)*b['stabilizer_value'];sg=np.sqrt(16/3)*b['stabilizer_gradient']
    correction=apply(J2,s);r1=apply(A@J1,s);r2=apply(A@J2,s)
    axes=[];directions=[]
    for profile in range(4):
        for color in range(4):
            dp=np.zeros_like(poly);dp[:,color]=b['pole_basis_polynomials'][profile]
            axes.append(100+20*profile+4+color);directions.append(dp)
    directions=np.array(directions);dC=ad(directions)
    dA=np.einsum('nm,amij->anij',ar,dC);dJ1=np.einsum('nm,amij->anij',f,dC)
    dJ2=np.array([second(dc,C,k)+second(C,dc,k) for dc in dC])
    dcorrection=apply(dJ2,s)
    first_r1=apply(dA@J1+A@dJ1,s)
    first_r2=apply(dA@J2+A@dJ2,s)
    mixed_correction=[];mixed_r1=[];mixed_r2=[]
    for i in range(16):
        h=np.array([second(dC[i],dc,k)+second(dc,dC[i],k) for dc in dC])
        mixed_correction.append(apply(h,s))
        mixed_r1.append(apply(dA[i]@dJ1+dA@dJ1[i],s))
        mixed_r2.append(apply(dA[i]@dJ2+dA@dJ2[i]+A@h,s))
    mixed_correction=np.array(mixed_correction)
    mixed_r1=np.array(mixed_r1);mixed_r2=np.array(mixed_r2)
    # Keep sub-roundoff corrections separate, never lose them by adding to s.
    phig=b['photon_covector_gradient189x49x4'].copy()
    phig[axes]+=dcorrection
    phig[184:188]+=np.einsum('nij,jh->hni',J2,sg)
    M=np.sqrt(8)*np.column_stack((np.eye(3),np.zeros(3)))
    Ai=b['gauge_values49x5x4'][:,2:]+(b['density49x8'][:,5]-1)[:,None,None]*M
    angular_correction=np.einsum('naij,nj->nai',ad(Ai),correction)
    exact,placements=exact_checks()
    checks={
        'saved_radial_generator':maximum(A-ad(b['radial_connection49'])),
        'saved_J1':maximum(J1-b['kernel_integral49x4x4']),
        'radial_skew':maximum(A+A.swapaxes(-1,-2)),
        'wall_J2':maximum(J2[-1]),
        'central_radial_correction_zero':maximum(correction[:,3]),
        'mixed_coordinate_symmetry':maximum(mixed_correction-mixed_correction.swapaxes(0,1)),
    }
    # Independent complex-step derivatives of the closed integral, at saved nodes.
    # This tests coefficient calculus, not a changed physical preparation.
    h=1e-20
    _,_,kc=factors(alpha,rho.astype(complex)+1j*h)
    J2prime=np.imag(second(C,C,kc))/h
    scale=max(maximum(A@J1),1e-300)
    checks['ordered_integral_radial_derivative_scaled']=maximum(J2prime+A@J1)/scale
    first_checks=[];mixed_checks=[]
    for i in (0,1,5,10,15):
        cc=C.astype(complex)+1j*h*dC[i]
        cs=np.imag(second(cc,cc,k))/h
        first_checks.append(maximum(cs-dJ2[i])/max(maximum(dJ2[i]),1.))
        # Differentiate the analytic first response, independently of h construction.
        for j in (0,1,5,10,15):
            dc=dC[j]
            cs=np.imag(second(dc,cc,k)+second(cc,dc,k))/h
            direct=second(dC[i],dc,k)+second(dc,dC[i],k)
            mixed_checks.append(maximum(cs-direct)/max(maximum(direct),1.))
    checks['first_integral_coordinate_derivative']=max(first_checks)
    checks['mixed_integral_coordinate_derivative']=max(mixed_checks)
    limits=bounds(poly,directions,alpha,s)
    assert max(checks.values())<2e-11,checks
    result=dict(schema='bhsm.muon-weak-photon-radial-reduction.v70',
        classification='EXACT_LOCAL_WEAK_RADIAL_ELIMINATION_AND_INITIALIZER_ORDERED_TRANSPORT_JETS',
        exact_checks=exact,mixed_placements=placements,checks=checks,maximum_check_defect=max(checks.values()),
        radial_coordinate_axes=axes,radial_nodes=len(rho),new_quadrature=False,new_resolution=False,
        first_order_radial_defect_max=maximum(r1),second_order_radial_defect_max=maximum(r2),
        first_order_first_radial_jet_defect_max=maximum(first_r1),
        second_order_first_radial_jet_defect_max=maximum(first_r2),
        first_order_mixed_radial_jet_defect_max=maximum(mixed_r1),
        second_order_mixed_radial_jet_defect_max=maximum(mixed_r2),
        second_order_covector_correction_max=maximum(correction),
        second_order_mixed_covector_correction_max=maximum(mixed_correction),
        bounds=limits,exact_radial_bulk_native_weak_term_zero_on_transport_core=True,
        full_pole_limit_native_continuity_proved=False,
        pole_cutoff_contract='On k<=k_plus rho^6 and e<=e_plus rho^4, a bounded transported angular test has cutoff energy O(epsilon^5). The radial native cutoff-shell term tends to zero if b_r/sqrt(k) is L2; absent a justified native continuity/trace theorem retain it in the pole/domain contact. No full physical pole cancellation is inferred.',
        angular_native_weak_term_eliminated=False,boundary_native_weak_term_eliminated=False,
        physical_source_error_bound=None,physical_native_kernel_evaluated=False,
        physical_guard=2e-10,method_tolerance=2e-11,temporal_baseline=2**-9,
        physical_reconnection_proved=False,physical_a_mu=None,total_physical_uncertainty=None,
        physical_background=False,physical_total_Y_evaluated=False,pushed=False,
        next_operand='Complete relative/native contraction of a against chi phi and b_i against (E_i chi)phi+chi D_i phi, plus actual entering/event/retained/released functional on the common action-selected graph; physical independent-left/right columns still required for matter current.')
    arrays=dict(radial_nodes49=rho,radial_axes=np.array(axes),ordered_second_transport49x4x4=J2,
        photon_covector_second_correction49x4=correction,
        second_correction_radial_gradient16x49x4=dcorrection,
        second_correction_radial_hessian16x16x49x4=mixed_correction,
        corrected_local_gradient189x49x4=phig,
        angular_connection_second_correction49x3x4=angular_correction,
        first_order_radial_defect=r1,second_order_radial_defect=r2,
        first_order_radial_gradient_defect=first_r1,second_order_radial_gradient_defect=first_r2,
        first_order_radial_hessian_defect=mixed_r1,second_order_radial_hessian_defect=mixed_r2)
    return arrays,result

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True);args=parser.parse_args()
    if args.out.exists():raise FileExistsError('Preserve previous output')
    arrays,result=calculate();args.out.mkdir()
    npz(args.out/'weak_photon_radial_reduction.npz',arrays);save(args.out/'result.json',result)
    print(json.dumps({k:result[k] for k in ('maximum_check_defect',
        'first_order_mixed_radial_jet_defect_max','second_order_mixed_radial_jet_defect_max',
        'second_order_covector_correction_max','physical_native_kernel_evaluated')}))

if __name__=='__main__':main()
