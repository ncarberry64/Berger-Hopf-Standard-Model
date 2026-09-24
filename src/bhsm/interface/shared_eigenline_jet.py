"""Action-contracted, matrix-free first and mixed eigenline variations.

Every solve consumes the already-certified joint bordered inverse defect.
The value enclosure of (psi,lambda) is never differentiated. Original-domain
derivatives are produced from action derivatives and normalization equations.
"""
from flint import arb
from bhsm.interface.shared_implicit_response_jet import dot,solve_with_operator,_domain


def second_variations(evaluate,psi,eigenvalue,u,v,raw_offset,
                      preconditioner,weights,defect_upper,first_variations=None):
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
    def rows(legs):
        if hasattr(evaluate,'gradient'):
            result=evaluate.gradient(legs)
            if len(result)!=size or _domain([zero]+list(result)) is not d:
                raise ValueError('complete same-domain raw action gradient required')
            return result[raw_offset:]
        return [checked([e]+legs) for e in basis]
    def apply_K(z):
        leg=pad(z[:n])
        return [h-eigenvalue*z[i]+psi[i]*z[-1]
                for i,h in enumerate(rows([leg]))]+[dot(psi,z[:n])]
    def solve_rhs(rhs):
        return solve_with_operator(rhs,apply_K,preconditioner,weights,defect_upper)
    if first_variations is None:
        hu=rows([p,u]);hv=rows([p,v])
        zu,proofu=solve_rhs([-h for h in hu]+[zero])
        zv,proofv=solve_rhs([-h for h in hv]+[zero])
    else:
        zu=list(first_variations['psi_u'])+[-first_variations['lambda_u']]
        zv=list(first_variations['psi_v'])+[-first_variations['lambda_v']]
        if len(zu)!=n+1 or len(zv)!=n+1 or _domain(zu+zv) is not d:
            raise ValueError('certified complete same-domain first variations required')
        proofu=proofv={'inherited_first_variations_reused':True}
    pu,pv=pad(zu[:n]),pad(zv[:n])
    # K(psi_uv,-lambda_uv) = (-H_uv psi-H_u psi_v-H_v psi_u
    #                        +lambda_u psi_v+lambda_v psi_u, -psi_u.psi_v).
    terms=[rows([p,u,v]),rows([pv,u]),rows([pu,v]),
           [-zu[-1]*zv[i] for i in range(n)],[-zv[-1]*zu[i] for i in range(n)]]
    rhs=[-terms[0][i]-terms[1][i]-terms[2][i]+terms[3][i]+terms[4][i] for i in range(n)]
    border=-dot(zu[:n],zv[:n]);rhs.append(border)
    zuv,proofuv=solve_rhs(rhs)
    return dict(psi_u=zu[:n],lambda_u=-zu[-1],psi_v=zv[:n],lambda_v=-zv[-1],
                psi_uv=zuv[:n],lambda_uv=-zuv[-1],
                first_u_proof=proofu,first_v_proof=proofv,mixed_proof=proofuv,
                mixed_rhs_terms=terms,normalization_border=border,
                complete_mixed_rhs_models=rhs,normalization_border_retained=True,
                existing_point_quantities_recomputed=False)
