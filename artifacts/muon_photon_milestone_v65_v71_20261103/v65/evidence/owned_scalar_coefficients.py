import math
import numpy as np

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
