"""Action-contracted, matrix-free first and mixed eigenline variations.

Every solve consumes the already-certified joint bordered inverse defect.
The value enclosure of (psi,lambda) is never differentiated. Original-domain
derivatives are produced from action derivatives and normalization equations.
"""
from flint import arb
from bhsm.interface.shared_implicit_response_jet import dot,solve_with_operator,_domain


def second_variations(evaluate,psi,eigenvalue,u,v,raw_offset,
                      preconditioner,weights,defect_upper):
    """Produce (psi_u,lambda_u,psi_v,lambda_v,psi_uv,lambda_uv).

    evaluate(legs) must return the shared Taylor enclosure of D^len(legs) S
    on the original state domain, including inertia and boundary. In BHSM,
    bind uniform_action_contraction.contract(action,state,legs)[0]. H is the
    RAW reduced Hessian: pad each reduced leg with raw_offset leading zeros.

    K=[[H-lambda I,psi],[psi^T,0]]. Its last solution coordinate equals minus
    the eigenvalue derivative. A preconditioner for the opposite-sign
    eigenproblem Jacobian requires flipping its last ROW, not its column.
    No spectral gap or inverse certificate is inferred from point arithmetic.
    """
    n=len(psi);size=len(u)
    if raw_offset<0 or size!=len(v) or raw_offset+n!=size:
        raise ValueError('complete raw directions and reduced eigenvector required')
    d=_domain(list(psi)+[eigenvalue]+list(u)+list(v))
    zero=d.affine(0)
    def pad(p):return [zero]*raw_offset+list(p)
    basis=[[arb(int(j==raw_offset+i)) for j in range(size)] for i in range(n)]
    p=pad(psi)
    def checked(legs):
        result=evaluate(legs)
        if _domain([zero,result]) is not d:raise ValueError('same-domain action required')
        return result
    def apply_K(z):
        leg=pad(z[:n])
        return [checked([e,leg])-eigenvalue*z[i]+psi[i]*z[-1]
                for i,e in enumerate(basis)]+[dot(psi,z[:n])]
    def solve_rhs(rhs):
        return solve_with_operator(rhs,apply_K,preconditioner,weights,defect_upper)
    hu=[checked([e,p,u]) for e in basis]
    hv=[checked([e,p,v]) for e in basis]
    zu,proofu=solve_rhs([-h for h in hu]+[zero])
    zv,proofv=solve_rhs([-h for h in hv]+[zero])
    pu,pv=pad(zu[:n]),pad(zv[:n])
    # K(psi_uv,-lambda_uv) = (-H_uv psi-H_u psi_v-H_v psi_u
    #                        +lambda_u psi_v+lambda_v psi_u, -psi_u.psi_v).
    rhs=[-checked([e,p,u,v])-checked([e,pv,u])-checked([e,pu,v])
         -zu[-1]*zv[i]-zv[-1]*zu[i] for i,e in enumerate(basis)]
    rhs.append(-dot(zu[:n],zv[:n]))
    zuv,proofuv=solve_rhs(rhs)
    return dict(psi_u=zu[:n],lambda_u=-zu[-1],psi_v=zv[:n],lambda_v=-zv[-1],
                psi_uv=zuv[:n],lambda_uv=-zuv[-1],
                first_u_proof=proofu,first_v_proof=proofv,mixed_proof=proofuv,
                complete_mixed_rhs_models=rhs,normalization_border_retained=True,
                existing_point_quantities_recomputed=False)
