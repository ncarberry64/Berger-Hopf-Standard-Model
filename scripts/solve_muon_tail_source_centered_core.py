"""Cached source-centered solve; extended precision controls chart cancellation.

All input forms remain the saved binary64 numerical model.  Higher precision
does not certify their interpolation, history, spatial or continuum errors.
"""
from __future__ import annotations
import argparse, hashlib, json, os, time
from pathlib import Path
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')
import numpy as np
import mpmath as mp


def read(p):
    with np.load(p, allow_pickle=False) as z:
        return {k: np.array(z[k]) for k in z.files}


def save(p, j):
    p.write_bytes((json.dumps(j, indent=2, sort_keys=True, allow_nan=False)+'\n').encode())


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def matrix(a):
    a = np.asarray(a)
    if a.ndim == 1:
        a = a[:, None]
    return mp.matrix([[mp.mpc(float(z.real), float(z.imag)) for z in row] for row in a])


def array(a):
    return np.array([[complex(z) for z in row] for row in a.tolist()])


def norm(a):
    return mp.sqrt(sum(abs(z)**2 for z in a))


def cj(z):
    return dict(real=float(mp.re(z)), imag=float(mp.im(z)))


def solve_many(H, rhs):
    """One pivoted factorization for all affine-response columns."""
    P, L, U = mp.lu(H)
    b = P*rhs
    x = mp.matrix(rhs.rows, rhs.cols)
    for k in range(rhs.cols):
        y = mp.matrix(rhs.rows, 1)
        for i in range(rhs.rows):
            y[i] = (b[i,k]-sum(L[i,j]*y[j] for j in range(i)))/L[i,i]
        for i in range(rhs.rows-1, -1, -1):
            x[i,k] = (y[i]-sum(U[i,j]*x[j,k] for j in range(i+1,rhs.rows)))/U[i,i]
    return x


def run(root, source, out, digits):
    if out.exists():
        raise FileExistsError('fresh output required')
    out.mkdir(parents=True)
    began = time.perf_counter()
    mp.mp.dps = digits
    a = read(source/'partial_system_with_tail_core.npz')
    base = root/'artifacts/muon_prefix_time_element_20261004'
    pre = read(base/'run_1/prefix_time_element.npz')
    br = read(base/'assembly_run_1/cut_to_future1_element.npz')
    fut = read(base/'future_run_2/retained_arc_time_element.npz')
    tail = read(source/'tail_response.npz')
    H, f = matrix(a['H']), matrix(a['rhs'])
    n, d = H.rows, 24
    sp, sb, sf = [mp.mpf(float(z['temporal_basis_scale'])) for z in (pre, br, fut)]
    # Exact algebraic chart in the inherited coordinates; no rank threshold.
    O, Z = mp.matrix(n,d), mp.matrix(n,3*d)
    for i in range(d):
        O[i,i] = 1; O[2*d+i,i] = mp.mpf('0.5'); O[3*d+i,i] = -1/sb
        Z[i,i] = sp/2; Z[d+i,i] = 1
        Z[2*d+i,i] = sp/2; Z[3*d+i,i] = -sp/sb
        Z[2*d+i,d+i] = mp.mpf('0.5'); Z[3*d+i,d+i] = 1/sb
        Z[4*d+i,d+i] = mp.mpf('0.5'); Z[5*d+i,d+i] = -1/sf
        Z[4*d+i,2*d+i] = mp.mpf('0.5'); Z[5*d+i,2*d+i] = 1/sf
    Hz = Z.H*H*Z
    scaling = [1/mp.sqrt(abs(Hz[i,i])) for i in range(3*d)]
    Zd = Z*mp.diag(scaling)
    HZd, HO = H*Zd, H*O
    Hr = Zd.H*HZd
    g = matrix(pre['left_source_trace'])
    # Combine the SAME correlated source before applying H. In particular,
    # no source is reconstructed by differences of W and chi quadratic forms.
    original = matrix(a['original_source_coefficients'])
    original_residual = H*original-f
    rhs_source = -Zd.H*original_residual
    rhs_ports = Zd.H*HO
    rhs = mp.matrix(3*d,d+1)
    for i in range(3*d):
        rhs[i,0] = rhs_source[i]
        for j in range(d):
            rhs[i,j+1] = rhs_ports[i,j]
    solved = solve_many(Hr, rhs)
    delta = Zd*solved[:,0]
    u = original+delta
    residual = original_residual+HZd*solved[:,0]
    conormal = O.H*residual
    U = O-Zd*solved[:,1:]
    S = O.H*(HO-HZd*solved[:,1:])
    r = S*g-conormal
    # Independent coefficients of the joining and free-port duals. This
    # coefficient solve is separate from the geometric Cauchy Riesz map.
    C = matrix(a['trace_continuity'])
    L = mp.matrix(d,n)
    for i in range(d):
        L[i,i] = 1; L[i,d+i] = -sp/2
    A = mp.matrix(C.rows+d,n)
    for i in range(C.rows):
        for j in range(n): A[i,j] = C[i,j]
    for i in range(d):
        for j in range(n): A[C.rows+i,j] = L[i,j]
    lam = solve_many(A*A.H, -A*residual)
    eq = residual+A.H*lam
    target = mp.matrix(A.rows,1)
    for i in range(d): target[C.rows+i] = g[i]
    tr = A*u-target
    tg = matrix(a['tail_trace_injection'])*u
    td = matrix(tail['S'])*tg-matrix(tail['r'])
    riesz = solve_many(matrix(pre['left_trace_Cauchy_Gram']), conormal)
    np.savez_compressed(out/'source_centered_core_solution.npz',
        solution=array(u).ravel(), exact_original_source=a['original_source_coefficients'],
        source_centered_correction=array(delta).ravel(), independent_chart=array(Z),
        scaled_independent_chart=array(Zd), port_injection=array(O), reduced_H=array(Hr),
        source_centered_reduced_rhs=array(rhs_source).ravel(), reduced_solution=array(solved[:,0]).ravel(),
        stationary_model_conormal_dual=array(conormal).ravel(), stationary_model_conormal_Riesz=array(riesz).ravel(),
        incoming_response_S=array(S), incoming_affine_r=array(r).ravel(), incoming_trace_solution_map=array(U),
        incoming_source_trace=pre['left_source_trace'], joining=a['trace_continuity'],
        incoming_trace_operator=array(L), solved_node2_trace=array(tg).ravel(),
        node2_stationary_tail_dual=array(td).ravel(), reaction=array(lam).ravel())
    # Export high-precision values actually used in diagnostics, since a
    # binary64 export of u alone reintroduces cancellation in H*u-f.
    decimal = lambda v: [[mp.nstr(mp.re(z),digits),mp.nstr(mp.im(z),digits)] for z in v]
    save(out/'high_precision_solution.json',dict(digits=digits,solution=decimal(u),
        source_centered_correction=decimal(delta),conormal=decimal(conormal),
        reduced_solution=decimal(solved[:,0]),model_coefficients='exact values of saved binary64 arrays'))
    rounded_u = array(u).ravel()
    rounded_res = a['H']@rounded_u-a['rhs']
    rounded_cn = array(O).conj().T@rounded_res
    redres = Hr*solved[:,0]-rhs_source
    result = dict(classification='source-centered open-port parent-bulk plus temporal minimal-core tail numerical model',
        source_solution=True,full_owned_source_solution=False,incoming_physical_port_unselected=True,
        reduced_dimension=3*d,reduced_condition=float(np.linalg.cond(array(Hr))),decimal_precision=digits,
        equation_absolute_residual=float(norm(eq)),trace_absolute_residual=float(norm(tr)),
        reduced_equation_absolute_residual=float(norm(redres)),
        reduced_backward_residual=float(norm(redres)/(norm(Hr)*norm(solved[:,0])+norm(rhs_source))),
        conormal_reaction_identity_residual=float(norm(conormal+lam[C.rows:,:])),
        incoming_port_output_contraction=cj((g.H*conormal)[0]),
        solved_node2_output_contraction=cj((tg.H*td)[0]),
        stationary_model_conormal_dual_norm=float(norm(conormal)),
        rounded_binary64_conormal_reconstruction_error=float(np.linalg.norm(rounded_cn-array(conormal).ravel())),
        source_centered_correction_norm=float(norm(delta)),
        native_heat_evaluations=0,new_history_points=0,new_field_campaigns=0,earlier_element_replays=0,
        error_scope='extended-precision algebra of saved binary64 model; residuals are diagnostics, not coefficient/continuum or Pauli error bounds',
        unknown_owned_blocks=dict(source_restricted_wall_action=None,constraint_complex_pullback=None,relative_completion=None),
        native_length=None,physical_a_mu=None,physical_g_mu=None,elapsed_seconds=time.perf_counter()-began)
    save(out/'result.json',result)
    save(out/'input_hashes.json',{name:dict(path=str(p),sha256=sha(p)) for name,p in dict(
        attachment=source/'partial_system_with_tail_core.npz',tail=source/'tail_response.npz',
        prefix=base/'run_1/prefix_time_element.npz',bridge=base/'assembly_run_1/cut_to_future1_element.npz',
        future=base/'future_run_2/retained_arc_time_element.npz',script=Path(__file__)).items()})
    save(out/'output_hashes.json',{p.name:sha(p) for p in out.iterdir() if p.is_file()})
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--repository',type=Path,default=Path(__file__).resolve().parents[1])
    p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--digits',type=int,default=80)
    a=p.parse_args();run(a.repository.resolve(),a.source,a.output,a.digits)
