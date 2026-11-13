"""Finite canonical lepton current -> Higgs -> wall response on saved histories.

The application follows the recorded reviewed Phase A publication. No density, reference, physical packet, exterior or arm glue is chosen.
All returned arrays are operator coefficients on the real Hermitian initial30
coefficient chart. New solves concern only the additional matter-current forcing.
"""
from __future__ import annotations

import numpy as np
from scipy.linalg import solve


def magnitude(a):
    a = np.asarray(a)
    return float(np.max(np.abs(a))) if a.size else 0.0


def norms(a):
    a = np.asarray(a)
    return {"maximum_entry_absolute": magnitude(a),
            "Frobenius": float(np.linalg.norm(a.ravel()))}


def gauss_table():
    """Exactly the existing four-stage Gauss rule, including its stage matrix."""
    from numpy.polynomial import Polynomial
    x, b = np.polynomial.legendre.leggauss(4)
    c, b = (x + 1) / 2, b / 2
    lagrange, integrals = [], []
    for j in range(4):
        p = Polynomial.fromroots(np.delete(c, j)); p = p / p(c[j])
        ip = p.integ(); ip = ip - ip(0)
        lagrange.append(p); integrals.append(ip)
    return c, b, np.array([[p(ci) for p in integrals] for ci in c])


def pulled_current(path, U, vertices, nodes, weights, interpolate):
    """Explicit matter action variation along saved scalar/wall test fields.

    Returns T times the common-action current, since the classical maps use
    S_hat=T*S. At scaling 1/T already belongs to path.coefficients().
    """
    direct = np.zeros((166, 30, 30), complex)
    scalar = np.zeros_like(direct)
    for s, w in zip(nodes, weights):
        ue = U(float(s))[:, :30]
        B = np.einsum('ai,bac,cj->bij', ue.conj(), vertices, ue, optimize=True)
        C = path.coefficients(float(s))
        direct -= path.T**2 * w * np.tensordot(C[:64].T, B[:64], axes=1)
        scalar -= path.T**2 * w * np.tensordot(C[64:].T, B[64:], axes=1)
    return direct, scalar


def scalar_current_stages(path, U, vertices, c, interpolate):
    """Original canonical Higgs-value source; no invented scalar-rate vertex."""
    result = []
    for s in c:
        ue = U(float(s))[:, :30]
        B = np.einsum('ai,bac,cj->bij', ue.conj(), vertices[64:], ue,
                      optimize=True)
        lapse = float(interpolate(path.s, path.N, float(s)))
        # H_original = J_H h_conditioned, so this is the actual dual J_H^T.
        j = -path.T**2 * lapse * np.tensordot(path.J[:16, :16].T, B, axes=1)
        result.append(j)
    return np.asarray(result)


def forced_scalar_canonical(path, forcing, a, b):
    """Reuse all existing F_j; solve only the new128-by128 matter-forcing RHS."""
    rhs = np.zeros((4, 32, 900), complex)
    rhs[:, 16:] = forcing.reshape(4, 16, 900)
    stage_matrix = np.zeros((128, 128))
    stage_rhs = np.einsum('ij,jab->iab', a, rhs).reshape(128, 900)
    for i in range(4):
        for j in range(4):
            block = -a[i, j] * path.F[j]
            if i == j:
                block = block + np.eye(32)
            stage_matrix[32*i:32*i+32, 32*j:32*j+32] = block
    stage = solve(stage_matrix, stage_rhs, assume_a='gen').reshape(4, 32, 900)
    rate = np.einsum('iab,ibc->iac', path.F, stage) + rhs
    final = np.einsum('i,iab->ab', b, rate)
    return dict(stages=stage, rates=rate, final=final,
                canonical_equation_residual=(stage_matrix @ stage.reshape(128,900)
                                            - stage_rhs),
                matrix_inf_norm=float(np.linalg.norm(stage_matrix, ord=np.inf)))


def independent_original_scalar_DAE(path, forcing, a, b):
    """Independent original position/momentum/Euler system, no F_j assembly.

    Unknowns at each stage are h16, v16, p16. The actual original M/B/K
    enforce p=M v+B^T h and p'=B v+K h+j_H. This verifies the new forcing
    and its endpoint without deriving an identity from the canonical solver.
    """
    matrix = np.zeros((192, 192))
    rhs = np.zeros((192, 900), complex)
    eye = np.eye(16)
    for i in range(4):
        row = 48*i
        M, B, K = [path.hc[f'q{i:03d}_'+name][:16,:16]
                   for name in ('M','B','K')]
        matrix[row:row+16, row:row+16] = eye
        matrix[row+16:row+32, row:row+16] = -B.T
        matrix[row+16:row+32, row+16:row+32] = -M
        matrix[row+16:row+32, row+32:row+48] = eye
        matrix[row+32:row+48, row+32:row+48] = eye
        for j in range(4):
            col = 48*j
            Bj, Kj = [path.hc[f'q{j:03d}_'+name][:16,:16]
                      for name in ('B','K')]
            matrix[row:row+16, col+16:col+32] -= a[i,j]*eye
            matrix[row+32:row+48, col:col+16] -= a[i,j]*Kj
            matrix[row+32:row+48, col+16:col+32] -= a[i,j]*Bj
            rhs[row+32:row+48] += a[i,j]*forcing[j].reshape(16,900)
    value = solve(matrix, rhs, assume_a='gen')
    stages = value.reshape(4,48,900)
    q, v, p = stages[:,:16], stages[:,16:32], stages[:,32:]
    pdot=[]
    for j in range(4):
        B, K = [path.hc[f'q{j:03d}_'+name][:16,:16] for name in ('B','K')]
        pdot.append(B@v[j]+K@q[j]+forcing[j].reshape(16,900))
    final=np.vstack((np.einsum('i,iab->ab',b,v),
                     np.einsum('i,iab->ab',b,np.asarray(pdot))))
    return dict(stages=np.concatenate((q,p),axis=1), velocities=v, final=final,
                equation_residual=matrix@value-rhs)


def gauge_return_at(path, label, z):
    """Original scalar action's wall value and rate covectors on (h,g=0)."""
    M,B,K=[path.hc[label+'_'+name] for name in ('M','B','K')]
    h,p=z[:16],z[16:]
    v=solve(M[:16,:16],p-B[:16,:16].T@h,assume_a='pos')
    ell=K[16:,:16]@h+B[16:,:16]@v
    momentum=B[:16,16:].T@h+M[16:,:16]@v
    return ell,momentum


def application(path, U, vertices, interpolate, *, saved_spin_file=None,
                independent_insertion=None):
    """Actual additional operator-current forcing and causal scalar return."""
    c,b,a=gauss_table()
    if magnitude(c-path.c)>2e-14:
        raise ValueError('different chronological nodes; input identity changed')
    jH=scalar_current_stages(path,U,vertices,c,interpolate)
    canonical=forced_scalar_canonical(path,jH,a,b)
    original=independent_original_scalar_DAE(path,jH,a,b)
    direct,pullH=pulled_current(path,U,vertices,c,b,interpolate)
    scalar_return=np.zeros((134,900),complex)
    momenta=[]
    for j in range(4):
        G,Gd=path.wall_input_at_sample(j+1)
        ell,p=gauge_return_at(path,f'q{j:03d}',canonical['stages'][j])
        scalar_return+=b[j]*(G.T@ell+Gd.T@p)
        momenta.append(p)
    final=canonical['final']
    Hc,Pc=path.hs['final'][:16],path.hs['final'][16:]
    # The test/source initial canonical states are respectively arbitrary
    # and held fixed. The *forced correction* has initial h=p=0 by definition.
    scalar_endpoint=Pc.T@final[:16]-Hc.T@final[16:]
    causal_wall=direct[32:].reshape(134,900)+scalar_return
    pull_wall=(direct+pullH)[32:].reshape(134,900)
    green=scalar_return-pullH[32:].reshape(134,900)-scalar_endpoint[32:]
    e0,p0=gauge_return_at(path,'lo',np.zeros_like(final))
    ef,pf=gauge_return_at(path,'hi',final)
    G0,_=path.wall_input_at_sample(0);Gf,_=path.wall_input_at_sample(5)
    gauge_temporal_endpoint=Gf.T@pf-G0.T@p0
    Jx=path.J[:16,:16]
    original_final_h=Jx@final[:16]
    original_final_p=solve(Jx.T,final[16:],assume_a='gen')/path.T
    direct12,pull12=pulled_current(path,U,vertices,
        (np.polynomial.legendre.leggauss(12)[0]+1)/2,
        np.polynomial.legendre.leggauss(12)[1]/2,interpolate)
    direct16,pull16=pulled_current(path,U,vertices,
        (np.polynomial.legendre.leggauss(16)[0]+1)/2,
        np.polynomial.legendre.leggauss(16)[1]/2,interpolate)
    full_pull=np.zeros((574,30,30),complex);full_pull[408:]=direct+pullH
    full_endpoint=np.zeros_like(full_pull)
    full_endpoint[408:]=scalar_endpoint.reshape(166,30,30)
    arrays=dict(
        stage_tau=c, stage_weights=b,
        Higgs_current_stage_hat=jH,
        scalar_forced_stages=canonical['stages'].reshape(4,32,30,30),
        scalar_forced_final=final.reshape(32,30,30),
        scalar_forced_original_H_final=original_final_h.reshape(16,30,30),
        scalar_forced_original_p_final=original_final_p.reshape(16,30,30),
        direct_matter_pullback166_hat=direct,
        scalar_matter_pullback166_hat=pullH,
        matter_pullback574_hat=full_pull,
        scalar_causal_wall_return134_hat=scalar_return.reshape(134,30,30),
        actual_direct_plus_causal_wall134_hat=causal_wall.reshape(134,30,30),
        scalar_symplectic_endpoint166_hat=scalar_endpoint.reshape(166,30,30),
        scalar_symplectic_endpoint574_hat=full_endpoint,
        wall_gauge_temporal_endpoint_hat=gauge_temporal_endpoint.reshape(134,30,30),
        wall_gauge_Euler_return_hat=(scalar_return-gauge_temporal_endpoint).reshape(134,30,30),
        pullback12_hat=direct12+pull12,
        pullback16_hat=direct16+pull16,
        original_DAE_stages=original['stages'].reshape(4,32,30,30))
    metrics={
        'new_canonical_stage_residual':norms(canonical['canonical_equation_residual']),
        'independent_original_DAE_residual':norms(original['equation_residual']),
        'independent_original_DAE_stage_difference':norms(original['stages']-canonical['stages']),
        'independent_original_DAE_final_difference':norms(original['final']-final),
        'same_rule_scalar_Green_identity':norms(green),
        'causal_vs_pullback_including_endpoint':norms(causal_wall-pull_wall-scalar_endpoint[32:]),
        'omitted_scalar_endpoint_negative_control':norms(causal_wall-pull_wall),
        'scalar_endpoint_itself':norms(scalar_endpoint[32:]),
        'matter_time_rule4_vs12':norms(direct+pullH-direct12-pull12),
        'matter_time_rule12_vs16':norms(direct12+pull12-direct16-pull16),
        'Higgs_current_Hermiticity':norms(jH-jH.conj().swapaxes(-1,-2)),
        'causal_wall_Hermiticity':norms(arrays['actual_direct_plus_causal_wall134_hat']-
                                      arrays['actual_direct_plus_causal_wall134_hat'].conj().swapaxes(-1,-2)),
        'saved_unperturbed_propagator_difference':norms(U(path.s)-path.ops['sample_U']),
        'sample_U_unitarity':norms(U(path.s).conj().swapaxes(-1,-2)@U(path.s)-np.eye(84)),
        'canonical_stage_matrix_inf_norm':canonical['matrix_inf_norm'],
        'current_magnitude':norms(arrays['actual_direct_plus_causal_wall134_hat'])}
    if saved_spin_file is not None:
        with np.load(saved_spin_file,allow_pickle=False) as z:
            old=-path.T*(z['J_gauge']+z['J_Higgs'])[:,:30]
        metrics['saved_current_dual_reuse12_difference']=norms(direct12+pull12-old)
        # This is the independently stored continuous finite-path endpoint
        # insertion. Do not pretend the four-node current quadrature is an
        # exact derivative of the same continuous quantum propagator.
        quantum_endpoint=np.zeros((574,30,30),complex)
        quantum_endpoint[408:]=-old
        arrays['saved_quantum_Cauchy_endpoint12_hat']=quantum_endpoint
        metrics['quantum_endpoint_vs_stage4_bulk_quadrature_defect']=norms(
            quantum_endpoint+full_pull)
    if independent_insertion is not None:
        rng=np.random.default_rng(20261018)
        errors=[]
        for _ in range(3):
            d=rng.normal(size=166);d=d/np.linalg.norm(d)
            value=np.zeros((30,30),complex)
            for s,w in zip(c,b):
                ue=U(float(s))[:,:30]
                v=independent_insertion(path,float(s),d)
                value-=path.T**2*w*(ue.conj().T@v@ue)
            errors.append(value-np.einsum('c,cij->ij',d,direct+pullH))
        metrics['independent_original_point_current_contraction']=norms(np.asarray(errors))
    return arrays,metrics
