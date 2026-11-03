"""Eight angular sources, four existing velocity profiles, affine radial Gauss return.

The physical entering flux and complete bulk current remain independent operands.
Numbers below belong to the saved initializer and its existing quadrature only.
"""
from pathlib import Path
from decimal import Decimal,localcontext,ROUND_CEILING
from hashlib import sha256
import argparse,json,math
import numpy as np
from prepare_evidence import npz,save

HERE=Path(__file__).resolve().parent;W=math.pi/2
EPS=np.zeros((3,3,3));EPS[0,1,2]=EPS[1,2,0]=EPS[2,0,1]=1;EPS[0,2,1]=EPS[2,1,0]=EPS[1,0,2]=-1
def ad(a):
    out=np.zeros(a.shape[:-1]+(4,4));out[...,:3,:3]=np.einsum('ijk,...j->...ik',EPS,a[...,:3])/np.sqrt(2)
    return out
def bracket(a,b):return np.einsum('...cd,...d->...c',ad(a),b)
def choose(x,n):return math.prod(x-k for k in range(n))/math.factorial(n)


def basis_polynomials(alpha):
    """Original j=0,1,2 shifted Jacobi polynomials and the existing wall lift."""
    out=np.zeros((4,4));a=2.;b=4+2*alpha
    for j in range(3):
        ln=math.lgamma(j+a+1)+math.lgamma(j+b+1)-math.lgamma(j+1)-math.lgamma(j+a+b+1)-math.log(2*j+a+b+1)
        norm=math.exp(-ln/2)
        P=np.zeros(j+1)
        for k in range(j+1):
            factor=(-1)**(j-k)*choose(j+a,k)*choose(j+b,j-k)
            for m in range(j-k+1):P[k+m]+=factor*choose(j-k,m)*(-1)**m
        out[j,:j+2]=norm*np.convolve(P,[1.,-1.])
    out[3,0]=1.
    return out


def integrated_connection(coeff,alpha,rho,upper=W):
    """Integral of the exact frozen fractional-polynomial A_rho representation."""
    powers=alpha+np.arange(4)+1
    x=np.asarray(rho)/W;y=upper/W
    factors=W*(y**powers-x[...,None]**powers)/powers
    return np.einsum('...m,mc->...c',factors,coeff)


def directed_tail_bound(coeff,alpha):
    """Upper bound for the frozen polynomial, not for unknown physical coefficients.

||ad(A)||_2 <= sum(abs(A_SU2)); the central component has zero adjoint action.
Decimal upward rounding bounds the finite coefficient expression. For a<1,
sum_{k>=2} a^k/k! <= a^2/[2(1-a)]. No exp-small-number subtraction is used.
"""
    with localcontext() as c:
        c.prec=80;c.rounding=ROUND_CEILING
        dec=Decimal.from_float
        a=sum(dec(W)*sum(abs(dec(float(x))) for x in row[:3])/(dec(alpha)+Decimal(m+1)) for m,row in enumerate(coeff))
        if not 0<=a<1:raise ValueError('This bounded first-order application is not justified')
        tail=a*a/(2*(1-a))
        return str(a),str(tail),float(np.nextafter(float(a),np.inf)),float(np.nextafter(float(tail),np.inf))


def calculate():
    p=HERE/'evidence/inputs.npz';provenance=json.loads((HERE/'evidence/provenance.json').read_text())
    assert sha256(p.read_bytes()).hexdigest()==provenance['input_sha256']
    b=dict(np.load(p,allow_pickle=False));rho=b['radial_nodes49'];alpha=float(b['alpha']);weights=b['radial_weights'];n=len(weights)
    assert len(rho)==n+1 and abs(rho[-1]-W)<1e-15
    P=basis_polynomials(alpha);powers=alpha+np.arange(4);x=rho/W
    basis=x[:,None]**powers@P.T
    basis_r=(powers*x[:,None]**(powers-1)/W)@P.T
    coeff=b['iterate151'][62:142].reshape(4,5,4)
    Ar_poly=P.T@coeff[:,1]
    Ar=x[:,None]**powers@Ar_poly
    Ar_r=(powers*x[:,None]**(powers-1)/W)@Ar_poly
    J=ad(integrated_connection(Ar_poly,alpha,rho));H=np.eye(4)-J
    J0=ad(integrated_connection(Ar_poly,alpha,0.));H0=np.eye(4)-J0
    atext,ttext,abound,tail=directed_tail_bound(Ar_poly,alpha)
    s=np.sqrt(16/3)*b['stabilizer_value'];q=b['stabilizer_value'];qg=b['stabilizer_gradient']
    M=np.sqrt(8)*np.column_stack((np.eye(3),np.zeros(3)))
    Ai=b['gauge_values49x5x4'][:,2:]+(b['density49x8'][:,5]-1)[:,None,None]*M
    omega=b['omega'];div=np.einsum('ihl,ilA->hA',b['E'],omega)
    Dq=bracket(Ai,s)
    G=np.einsum('nic,ihA->nchA',Dq,omega)+np.einsum('c,hA->chA',s,div)[None]
    kappa=float(b['MAXWELL_TO_CAP']);e=b['density49x8'][:,0]
    K=kappa*np.einsum('n,np,nchA->nchpA',e,basis,G)
    R0=-np.einsum('n,nchpA->chpA',weights,K[:n])
    R1=np.einsum('n,ncd,ndhpA->chpA',weights,J[:n],K[:n])
    R=R0+R1
    # The zeroth-order photon contraction cancels identically by invariance;
    # evaluate its small surviving term separately instead of subtracting big numbers.
    photon=np.einsum('c,chpA->hpA',s,R1)
    raw_zero=np.einsum('c,chpA->hpA',s,R0)
    raw_total=np.einsum('c,chpA->hpA',s,R)
    # The boundary range check consumes the same raw return as T R. Keep
    # floating symmetry drift visible beside the analytically reduced component.
    unit_projection=np.einsum('c,chpA->hpA',q,R)
    T=b['momentum_from_load_value'];B=b['orbit_value']
    lift=np.einsum('ac,chpA->ahpA',T,R)
    neutral_remainder=-np.einsum('c,hpA->chpA',q,unit_projection)
    L1=np.einsum('n,nhpA->hpA',np.abs(weights),np.sum(np.abs(K[:n]),axis=1))
    absolute_first=np.einsum('n,c,ncd,ndhpA->hpA',np.abs(weights),np.abs(s),np.abs(J[:n]),np.abs(K[:n]))
    projected_order_bound=np.linalg.norm(s)*tail*L1
    # A conservative floating contraction allowance; not quadrature/input uncertainty.
    round_bound=(4096*np.finfo(float).eps/(1-4096*np.finfo(float).eps))*absolute_first
    checks={
        'original_radial_basis':float(np.max(abs(basis-b['radial_basis49x4']))),
        'original_radial_basis_derivative':float(np.max(abs(basis_r-b['radial_derivative49x4']))),
        'original_A_rho':float(np.max(abs(Ar-b['gauge_values49x5x4'][:,1]))),
        'original_A_rho_derivative':float(np.max(abs(Ar_r-b['gauge_radial49x5x4'][:,1]))),
        'same_full_wall_connection':float(np.max(abs(Ai[-1].reshape(-1)-b['theta22'][6:18]))),
        'coexact_angular_divergence':float(np.max(abs(div))),
        'adjoint_generator_skew':float(np.max(abs(ad(Ar)+ad(Ar).swapaxes(-1,-2)))),
        'endpoint_identity':float(np.max(abs(H[-1]-np.eye(4)))),
        'zeroth_photon_return_cancellation':float(np.max(abs(np.einsum('c,chpA->hpA',s,R0)))),
        'boundary_broken_range_match':float(np.max(abs(-R+np.einsum('ca,ahpA->chpA',B.T,lift)-neutral_remainder))),
        'fixed_rule_weight_sum':float(abs(weights.sum()-W)),
    }
    # Exact defect of U1(W,rho) as a right-source propagator: d_rho U1-U1 ad A=J ad A.
    A=ad(Ar);defect=A-np.einsum('ncd,nde->nce',H,A)
    checks['transport_first_order_defect_identity']=float(np.max(abs(defect-np.einsum('ncd,nde->nce',J,A))))
    # Complete local-chart first derivatives; stream columns, no 49x189 source tensor.
    photon_grad=np.zeros((189,20,4,8));Rgrad=np.zeros((189,4,20,4,8));lift_grad=np.zeros_like(Rgrad)
    for j in range(189):
        ds=np.zeros(4);dq=np.zeros(4);dAi=np.zeros_like(Ai);de=np.zeros(49);dpoly=np.zeros_like(Ar_poly);dT=np.zeros((4,4))
        if j<100:
            de=b['density_gradient49x8x100'][:,0,j]
            dAi=b['density_gradient49x8x100'][:,5,j,None,None]*M
        elif 100<=j<180:
            profile,local=divmod(j-100,20);field,c=divmod(local,4)
            if field==1:dpoly[:,c]=P[profile]
            if field>=2:dAi[:,field-2,c]=basis[:,profile]
        elif 184<=j<188:
            dq=qg[:,j-184];ds=np.sqrt(16/3)*dq;dT=b['momentum_from_load_gradient'][:,:,j-184]
        dJ=ad(integrated_connection(dpoly,alpha,rho))
        dG=np.einsum('nic,ihA->nchA',bracket(dAi,s)+bracket(Ai,ds),omega)+np.einsum('c,hA->chA',ds,div)[None]
        dK=kappa*(np.einsum('n,np,nchA->nchpA',de,basis,G)+np.einsum('n,np,nchA->nchpA',e,basis,dG))
        dR0=-np.einsum('n,nchpA->chpA',weights,dK[:n])
        dR1=np.einsum('n,ncd,ndhpA->chpA',weights,dJ[:n],K[:n])+np.einsum('n,ncd,ndhpA->chpA',weights,J[:n],dK[:n])
        Rgrad[j]=dR0+dR1
        photon_grad[j]=np.einsum('c,chpA->hpA',ds,R1)+np.einsum('c,chpA->hpA',s,dR1)
        lift_grad[j]=np.einsum('ac,chpA->ahpA',dT,R)+np.einsum('ac,chpA->ahpA',T,Rgrad[j])
        if j in (0,62,104,124,146,184,185):
            checks[f'projected_zeroth_tangent_{j}']=float(np.max(abs(np.einsum('c,chpA->hpA',ds,R0)+np.einsum('c,chpA->hpA',s,dR0))))
    assert max(checks.values())<2e-11,checks
    arrays=dict(radial_nodes49=rho,radial_connection_polynomial=Ar_poly,radial_connection49=Ar,
        kernel_integral49x4x4=J,source_return_kernel49x4x4=H,inherited_transfer4x4=H0,
        known_canonical_Gauss_load49x4x20x4x8=K,known_return_zeroth=R0,known_return_first_order=R1,
        known_return=R,known_return_gradient189=Rgrad,photon_return_first_order=photon,
        raw_photon_zeroth_contraction=raw_zero,raw_photon_total_contraction=raw_total,
        photon_return_gradient189=photon_grad,boundary_Higgs_range_lift=lift,
        boundary_Higgs_range_lift_gradient189=lift_grad,boundary_neutral_remainder=neutral_remainder,
        projected_transport_order_bound=projected_order_bound,projected_contraction_roundoff_allowance=round_bound,
        pole_basis_polynomials=P)
    result=dict(schema='bhsm.muon-eight-source-radial-gauss.v66',classification='EVALUATED_INITIALIZER_AFFINE_RADIAL_GAUSS_RETURN_AND_BOUNDARY_RANGE_BLOCK',
        consistency_checks=checks,maximum_consistency_defect=max(checks.values()),angular_sources=8,existing_radial_profiles=4,
        existing_quadrature_nodes=48,wall_evaluation_nodes=1,new_resolution=False,new_quadrature=False,
        radial_connection_SU2_integral_norm_upper=atext,omitted_Dyson_orders_norm_upper=ttext,
        radial_connection_max=float(np.max(abs(Ar))),known_return_norm=float(np.linalg.norm(R)),
        known_return_first_order_norm=float(np.linalg.norm(R1)),photon_return_norm=float(np.linalg.norm(photon)),
        photon_return_max=float(np.max(abs(photon))),maximum_projected_transport_order_bound=float(np.max(projected_order_bound)),
        raw_zeroth_photon_contraction_norm=float(np.linalg.norm(raw_zero)),
        raw_zeroth_photon_contraction_max=float(np.max(abs(raw_zero))),
        raw_total_photon_contraction_norm=float(np.linalg.norm(raw_total)),
        raw_total_minus_first_order_norm=float(np.linalg.norm(raw_total-photon)),
        maximum_projected_contraction_allowance=float(np.max(round_bound)),
        boundary_Higgs_lift_norm=float(np.linalg.norm(lift)),boundary_neutral_remainder_norm=float(np.linalg.norm(neutral_remainder)),
        kernel_bound_scope='Frozen fractional-polynomial connection; fixed quadrature source sum. Does not bound source/representation drift, quadrature error, input/model error or physical state uncertainty.',
        small_projection_scope='First transport component is symmetry-reduced. Raw zeroth/total contractions are retained separately; their finite drift is not covered by the Dyson-order bound.',
        inherited_flux_selected=False,bulk_native_current_evaluated=False,regular_pole_entering_trace_assigned=False,
        boundary_matching_complete=False,physical_event_domain_realized=False,physical_reconnection_proved=False,
        physical_a_mu=None,total_physical_uncertainty=None,physical_guard=2e-10,temporal_baseline=2**-9,
        source_scope='Partial derivative with respect to original field velocities: delta Pi_i=kappa e B_p s_H omega_i,A. Actual source amplitudes and full photon response not selected.',
        complete_equation='P_wall=U_wall,in P_in - integral U_wall,rho (K_known + j_bulk_rest + [delta A_m,Pi^m] + domain terms) d rho; match -P_wall+B^T delta p_H+(delta B)^T p_H+rho_Gamma,rest with released flux.',
        derivative_scope='189 saved local coefficient coordinates; physical source, event and domain motion remain additional coupled operands')
    return arrays,result


def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    if a.out.exists():raise FileExistsError('Preserve prior output')
    arrays,result=calculate();a.out.mkdir();npz(a.out/'radial_gauss_return.npz',arrays);save(a.out/'result.json',result)
    print(json.dumps({k:result[k] for k in ('maximum_consistency_defect','radial_connection_SU2_integral_norm_upper','known_return_norm','photon_return_norm','maximum_projected_transport_order_bound','boundary_matching_complete')}))

if __name__=='__main__':main()
