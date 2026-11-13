"""One-coefficient intrinsic scalar space and its exact derivative maps.

Scalar Peter--Weyl sections on unit S3 are tensor weak C2.  They are not
spinor/Weyl carrier labels.  The returned maps construct field values and
derivatives from the same temporal/angular coefficient array.  The finite
band and polynomial mesh are numerical choices, not physical modes,
Cauchy data, a selected state, or a closed nonlinear truncation.
"""
from __future__ import annotations

import math

import numpy as np
from numpy.polynomial import Legendre


UNIT_S3_VOLUME=2*math.pi**2


def _integer(value,name,minimum=0):
    if not isinstance(value,(int,np.integer)) or isinstance(value,(bool,np.bool_)) or value<minimum:
        raise ValueError(f'{name} must be an integer >= {minimum}')
    return int(value)


def scalar_section_labels(max_level):
    """Return (n,m,k) scalar labels, with doubled weights m,k."""
    N=_integer(max_level,'max_level')
    return [(n,m,k) for n in range(N+1)
            for m in range(n,-n-1,-2) for k in range(n,-n-1,-2)]


def real_scalar_basis_labels(max_level):
    """One independent real harmonic per scalar Peter--Weyl dimension.

    A conjugate pair contributes sqrt(2) Re(phi) and sqrt(2) Im(phi),
    in that order.  Only the even-level m=k=0 harmonic is self-conjugate.
    The first member in scalar_section_labels fixes each pair's sign.
    These are coordinates for a real scalar, not a selected gauge field.
    """
    labels=scalar_section_labels(max_level); seen=set(); result=[]
    for n,m,k in labels:
        if (n,m,k) in seen:
            continue
        partner=(n,-m,-k)
        seen.update(((n,m,k),partner))
        if m==k==0:
            result.append((n,m,k,'self'))
        else:
            result.extend(((n,m,k,'real'),(n,m,k,'imag')))
    return result


def real_scalar_basis_transform(max_level):
    """Unitary complex-to-real harmonic transform, V_real=V_complex U.

    phi(n,m,k)*=(-1)^((m-k)/2) phi(n,-m,-k).  If i is a pair's
    representative and j its partner, the columns are
    (e_i+sign e_j)/sqrt(2) and -i(e_i-sign e_j)/sqrt(2).
    Real coefficients in these columns produce actual real functions;
    splitting every complex coefficient into Re/Im would be redundant.
    The weak C2 field still has independent complex coefficients.
    """
    labels=scalar_section_labels(max_level); index={row:i for i,row in enumerate(labels)}
    U=np.zeros((len(labels),len(labels)),complex)
    for column,(n,m,k,part) in enumerate(real_scalar_basis_labels(max_level)):
        i=index[n,m,k]
        if part=='self':
            U[i,column]=1.
            continue
        j=index[n,-m,-k]; sign=1 if ((m-k)//2)%2==0 else -1
        if part=='real':
            U[i,column]=1/math.sqrt(2); U[j,column]=sign/math.sqrt(2)
        else:
            U[i,column]=-1j/math.sqrt(2); U[j,column]=1j*sign/math.sqrt(2)
    return U


def _spin_matrices(n):
    j=n/2; weights=np.arange(n,-n-1,-2)/2
    plus=np.zeros((n+1,n+1),complex)
    for col in range(1,n+1):
        m=weights[col]
        plus[col-1,col]=math.sqrt((j-m)*(j+m+1))
    return np.array([(plus+plus.T)/2,(plus-plus.T)/(2j),np.diag(weights)])


def scalar_angular_derivative_matrices(max_level):
    """Coefficient E_a maps in the inherited right coframe, E_a=2i J_a.

    The active m index transforms; k is a spectator.  The scalar functions
    phi=sqrt(n+1)*conj(D^{n/2}_{mk}) have E_a phi = phi E_a as coefficient
    maps.  These anti-Hermitian maps use the unit S3 radius, not R4.
    """
    labels=scalar_section_labels(max_level); size=len(labels)
    result=np.zeros((3,size,size),complex); offset=0
    for n in range(int(max_level)+1):
        block=2j*_spin_matrices(n)
        width=(n+1)**2
        for a in range(3):
            result[a,offset:offset+width,offset:offset+width]=np.kron(block[a],np.eye(n+1))
        offset+=width
    return result


def symmetric_power_matrix(su2_points,level):
    """Evaluate the normalized degree-n SU2 symmetric representation.

    Basis index r counts lower-component occupation.  The polynomial
    expression avoids Euler-coordinate singularities and phase fitting.
    """
    n=_integer(level,'level')
    g=np.asarray(su2_points,dtype=complex)
    if g.ndim!=3 or g.shape[1:]!=(2,2) or len(g)==0 or not np.isfinite(g).all():
        raise ValueError('finite SU2 matrices with shape (points,2,2) required')
    if (not np.allclose(g.conj().transpose(0,2,1)@g,np.eye(2),atol=2e-13,rtol=0)
            or not np.allclose(np.linalg.det(g),1,atol=2e-13,rtol=0)):
        raise ValueError('unitary determinant-one SU2 points required')
    a,b,c,d=g[:,0,0],g[:,0,1],g[:,1,0],g[:,1,1]
    D=np.zeros((len(g),n+1,n+1),complex)
    for row in range(n+1):
        for col in range(n+1):
            scale=math.sqrt(math.comb(n,col)/math.comb(n,row))
            for ell in range(max(0,row-(n-col)),min(row,col)+1):
                power=row-ell
                D[:,row,col]+=scale*math.comb(n-col,power)*math.comb(col,ell)*(
                    a**(n-col-power)*c**power*b**(col-ell)*d**ell)
    return D


def scalar_basis_values(su2_points,max_level):
    """Haar-normalized scalar values, one column per scalar_section_labels."""
    N=_integer(max_level,'max_level')
    return np.concatenate([math.sqrt(n+1)*symmetric_power_matrix(su2_points,n).conj().reshape(len(su2_points),-1)
                           for n in range(N+1)],axis=1)


def adjoint_rotation_values(su2_points):
    """Actual Ad_g coefficients at the same quadrature points.

    g(-i sigma_d)g^dagger = R_ad(-i sigma_a).  This is a geometric
    representation map, not an independently selected scalar/gauge field.
    """
    g=np.asarray(su2_points,dtype=complex)
    # Reuse the fundamental representation validation.
    symmetric_power_matrix(g,1)
    sigma=np.array([[[0,1],[1,0]],[[0,-1j],[1j,0]],[[1,0],[0,-1]]],complex)
    transformed=np.einsum('pij,djk,plk->pdil',g,sigma,g.conj())
    R=.5*np.einsum('aij,pdji->pad',sigma,transformed)
    if np.max(np.abs(R.imag))>2e-13:
        raise ValueError('Ad SU2 rotation is not real within representation rounding')
    return R.real


def scalar_s3_discretization(max_level,*,quadrature_polynomial_degree=None):
    """Build scalar values, exact coefficient derivatives and S3 quadrature.

    Hopf coordinates use x in [0,1], z1=sqrt(x)e^(i alpha),
    z2=sqrt(1-x)e^(i beta), g=[[z1,z2],[-conj(z2),conj(z1)]].
    Haar=dx d_alpha d_beta/(4*pi^2).  The physical unit S3 volume is
    2*pi^2 and is included once in ``unit_s3_weights``.

    A product with total polynomial degree d has phase frequencies at most
    d.  A torus grid of d+1 points integrates every nonzero phase to zero.
    Phase-balanced terms have even z1/z2 counts, hence are x-polynomials
    of degree <=floor(d/2).  The chosen Gauss rule integrates that degree.
    Four scalar band-N factors have d<=4N.  The default also covers the
    degree-two Ad_g connection in a complete squared kinetic product.
    Larger source/gauge bands must request their actual product degree.
    """
    N=_integer(max_level,'max_level')
    required=4*N
    degree=max(required,2*N+4) if quadrature_polynomial_degree is None else _integer(
        quadrature_polynomial_degree,'quadrature_polynomial_degree')
    if degree<required:
        raise ValueError('quadrature polynomial degree must cover four scalar factors')
    torus_count=degree+1
    radial_count=(degree//2+2)//2
    nodes,weights=np.polynomial.legendre.leggauss(radial_count)
    x=(nodes+1)/2; wx=weights/2
    angles=2*math.pi*np.arange(torus_count)/torus_count
    X,A,B=np.meshgrid(x,angles,angles,indexing='ij')
    z1=np.sqrt(X.ravel())*np.exp(1j*A.ravel())
    z2=np.sqrt(1-X.ravel())*np.exp(1j*B.ravel())
    g=np.empty((len(z1),2,2),complex)
    g[:,0,0]=z1;g[:,0,1]=z2;g[:,1,0]=-z2.conj();g[:,1,1]=z1.conj()
    haar=np.repeat(wx,torus_count**2)/torus_count**2
    values=scalar_basis_values(g,N)
    derivative=scalar_angular_derivative_matrices(N)
    dvalues=np.einsum('pm,amn->pan',values,derivative)
    real_transform=real_scalar_basis_transform(N)
    real_values=values@real_transform
    real_dvalues=np.einsum('pan,nm->pam',dvalues,real_transform)
    real_derivative=real_transform.conj().T@derivative@real_transform
    # Reality follows from the conjugation identity, not from fitted data.
    # Verify only that evaluation/representation rounding respects it.
    for value in (real_values,real_dvalues,real_derivative):
        rounding=64*np.finfo(float).eps*max(1.,float(np.max(abs(value))))
        if np.max(abs(value.imag))>rounding:
            raise ValueError('real harmonic transform violates conjugation identity')
    labels=scalar_section_labels(N); scalar_count=len(labels)
    return dict(max_level=N,scalar_labels=labels,
                weak_section_labels=[(n,m,k,w) for n,m,k in labels for w in (0,1)],
                scalar_count=scalar_count,complex_doublet_coefficient_count=2*scalar_count,
                real_doublet_coefficient_count=4*scalar_count,
                su2_points=g,hopf_points=np.column_stack((X.ravel(),A.ravel(),B.ravel())),
                basis_values=values,basis_derivative_values=dvalues,
                angular_derivative_matrices=derivative,
                real_basis_values=real_values.real,real_basis_derivative_values=real_dvalues.real,
                real_basis_coefficient_transform=real_transform,
                real_angular_derivative_matrices=real_derivative.real,
                real_basis_labels=real_scalar_basis_labels(N),
                real_basis_normalization='paired sqrt(2) Re/Im phi; self m=k=0; unit Haar Gram',
                weak_angular_derivative_matrices=np.array([np.kron(a,np.eye(2)) for a in derivative]),
                haar_weights=haar,unit_s3_weights=UNIT_S3_VOLUME*haar,
                unit_s3_volume=UNIT_S3_VOLUME,adjoint_rotations=adjoint_rotation_values(g),
                quadrature_polynomial_degree=degree,torus_count=torus_count,radial_count=radial_count,
                quartic_scalar_products_exact=True,
                normalization='sqrt(n+1) conjugate Wigner D; unit Haar Gram',
                measure_rule='Use either Haar weights with 2*pi^2 once or unit_s3_weights directly',
                truncation='Numerical scalar band n<=max_level; not invariant under full nonlinear/source action',
                physical_mode_selected=False,physical_boundary_conditions_selected=False)


def realify_coefficients(coefficients):
    """Unscaled real coefficient vector: concatenate Re(flat), Im(flat)."""
    value=np.asarray(coefficients,dtype=complex)
    if value.size==0 or not np.isfinite(value).all():
        raise ValueError('finite nonempty complex coefficient array required')
    flat=value.ravel()
    return np.concatenate((flat.real,flat.imag))


def unrealify_coefficients(real_coefficients,complex_shape):
    """Inverse in an explicitly specified complex coefficient-array shape."""
    raw=np.asarray(real_coefficients)
    if np.iscomplexobj(raw) and np.any(raw.imag!=0):
        raise ValueError('real coefficient vector required')
    value=np.asarray(raw,dtype=float)
    try:
        shape=tuple(_integer(x,'complex_shape axis',1) for x in complex_shape)
    except TypeError as error:
        raise ValueError('explicit positive complex coefficient shape required') from error
    count=math.prod(shape)
    if not shape or value.shape!=(2*count,) or not np.isfinite(value).all():
        raise ValueError('finite real vector matching the declared complex shape required')
    return (value[:count]+1j*value[count:]).reshape(shape)


def realify_complex_linear_map(matrix):
    """Exact real block map [[Re A,-Im A],[Im A,Re A]]."""
    A=np.asarray(matrix,dtype=complex)
    if A.ndim!=2 or not np.isfinite(A).all():
        raise ValueError('finite complex matrix required')
    return np.block([[A.real,-A.imag],[A.imag,A.real]])


def polynomial_temporal_discretization(t_start,t_end,degree,*,quadrature_order=None):
    """Lobatto polynomial coefficients and derivative maps on [t_start,t_end].

    This computational interval must be bound by the solve driver to the
    owned physical clock/domain.  No initial value, final value, periodic
    cycle or retarded Cauchy component is assigned.  The separate Gauss
    quadrature integrates quartic temporal trial products exactly for
    constant weights; nonpolynomial geometric coefficients need refinement.
    """
    degree=_integer(degree,'temporal degree',1)
    start,end=float(t_start),float(t_end)
    if not math.isfinite(start) or not math.isfinite(end) or end<=start:
        raise ValueError('explicit finite future-oriented interval required')
    count=2*degree+1 if quadrature_order is None else _integer(quadrature_order,'quadrature_order',1)
    if count<2*degree+1:
        raise ValueError('temporal quadrature must cover quartic trial products')
    interior=Legendre.basis(degree).deriv().roots() if degree>1 else np.array([])
    nodes=np.concatenate(([-1.],interior,[1.]))
    # Barycentric cardinal evaluation avoids monomial cancellation at
    # higher temporal degree.  The same nodal derivative defines every map.
    bary=np.array([1/np.prod(node-np.delete(nodes,i)) for i,node in enumerate(nodes)])
    nodal=np.zeros((degree+1,degree+1))
    for i in range(degree+1):
        for j in range(degree+1):
            if i!=j:
                nodal[i,j]=bary[j]/(bary[i]*(nodes[i]-nodes[j]))
        nodal[i,i]=-sum(nodal[i,j] for j in range(degree+1) if i!=j)
    def evaluate(points):
        values=np.zeros((len(points),degree+1)); rates=np.zeros_like(values)
        for row,point in enumerate(points):
            distance=point-nodes
            matches=np.flatnonzero(abs(distance)<=16*np.finfo(float).eps)
            if len(matches):
                index=int(matches[0]); values[row,index]=1.; rates[row]=nodal[index]
            else:
                u=bary/distance; B=u/u.sum()
                values[row]=B
                rates[row]=B*(np.sum(B/distance)-1/distance)
        return values,rates
    x,w=np.polynomial.legendre.leggauss(count); duration=end-start
    B,reference_rate=evaluate(x)
    Bt=2/duration*reference_rate
    nodal_rate=2/duration*nodal
    endpoint,reference_endpoint_rate=evaluate(np.array([-1.,1.]))
    endpoint_rate=2/duration*reference_endpoint_rate
    return dict(t_start=start,t_end=end,duration=duration,degree=degree,
                interpolation_times=start+(nodes+1)*duration/2,
                quadrature_times=start+(x+1)*duration/2,quadrature_weights=w*duration/2,
                basis_values=B,basis_time_derivatives=Bt,nodal_time_derivative_matrix=nodal_rate,
                endpoint_values=endpoint,endpoint_time_derivatives=endpoint_rate,
                endpoint_orientations=(-1,1),coefficient_count=degree+1,
                quartic_constant_weight_products_exact=True,
                derivative_clock='supplied coordinate physical-time chart; lapse conversion belongs to action coefficients',
                selected_cauchy_data=None,retarded_homogeneous_component_selected=False,
                physical_boundary_conditions_selected=False)


def tensor_product_scalar_fields(angular,temporal,coefficients):
    """Construct H, partial_t H and E_i H from one complex coefficient block.

    Shape is (temporal coefficient, scalar harmonic, weak component).
    The same operation can construct the independent p_H unknown block.
    Covariant A_t and spatial connection applications must then be added
    from their coupled unknowns/owned background, never inferred as zero.
    """
    c=np.asarray(coefficients,dtype=complex)
    shape=(temporal['coefficient_count'],angular['scalar_count'],2)
    if c.shape!=shape or not np.isfinite(c).all():
        raise ValueError('finite common temporal/scalar/doublet coefficient block required')
    B=temporal['basis_values']; Bt=temporal['basis_time_derivatives']
    V=angular['basis_values']; EV=angular['basis_derivative_values']
    return dict(field_values=np.einsum('tl,an,lnw->taw',B,V,c),
                coordinate_time_derivatives=np.einsum('tl,an,lnw->taw',Bt,V,c),
                unit_s3_derivatives=np.einsum('tl,ain,lnw->taiw',B,EV,c),
                endpoint_values=np.einsum('el,an,lnw->eaw',temporal['endpoint_values'],V,c),
                endpoint_time_derivatives=np.einsum('el,an,lnw->eaw',temporal['endpoint_time_derivatives'],V,c),
                spacetime_quadrature_weights=np.outer(temporal['quadrature_weights'],angular['unit_s3_weights']),
                coefficient_shape=shape,all_derivatives_from_same_coefficients=True,
                full_covariant_derivatives_selected=False,physical_field_selected=False)
