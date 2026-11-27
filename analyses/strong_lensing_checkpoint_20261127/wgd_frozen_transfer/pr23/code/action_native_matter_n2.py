"""R1 n=2 ADM + Schutz--Sorkin dust/radiation, reduced at action level.

H0=Mpl=1. One real harmonic has integral sqrt(gamma) Q**2 = 1.
x=(zeta,D_m,D_r), D_I=delta rho_I/(rho_I+p_I)+3*zeta.
u=(alpha,chi,v_m,v_r). No fluid sound-speed regularizer or fitted coupling.
See docs/R1_ACTION_NATIVE_MATTER_BACKREACTION_V1_DERIVATION.md.
The frozen background and closed_horndeski_n2 owner are read, never modified.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp

import background as bg
import closed_horndeski_n2 as owner

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'preregistration/prediction_manifest.json'
N_START = -np.log(3.1)
W = np.array([0.0, 1.0 / 3.0])


def frozen_background():
    manifest = json.loads(MANIFEST.read_text(encoding='utf8'))
    p = manifest['background_R1']
    for key, expected in [('Omega_m0', bg.OMEGA_M0), ('Omega_r0', bg.OMEGA_R0),
                          ('Omega_k0', bg.OMEGA_K0), ('lambda', bg.LAMBDA), ('q', bg.Q)]:
        if p[key] != expected:
            raise ValueError(f'Frozen background mismatch: {key}')
    # Reuse the frozen shooting result. No new shooting/calibration is done.
    sol = bg.integrate(p['V0_over_Mpl2H02'])
    if not sol.success:
        raise RuntimeError(sol.message)
    return sol


def scales(N):
    a = np.exp(N)
    kappa = bg.KCURV / a**2
    h = np.array([3 * bg.OMEGA_M0 / a**3, 4 * bg.OMEGA_R0 / a**4])
    return a, kappa, 8 * kappa, 5 * kappa, h


def action_blocks(N, y, include_fluids=True):
    """L2/a^3 = .5 u A u + u(B xdot+D x) + .5 xdot K0 xdot + .5 x E x.

    Fluid current spatial auxiliaries have already been varied exactly.
    The remaining velocity potentials are auxiliary in this IBP convention.
    include_fluids=False removes fluid sectors for the owner recovery gate;
    it is not evolution with fluid perturbations forcibly set to zero.
    """
    _, v, H = y
    theta, sigma = owner.theta_sigma(v, H)
    _, kap, k, s, h_all = scales(N)
    h = h_all if include_fluids else h_all[:0]
    w = W if include_fluids else W[:0]
    nx, nu = 1 + len(h), 2 + len(h)
    dtype = np.result_type(N, y, float)
    A = np.zeros((nu, nu), dtype=dtype)
    B = np.zeros((nu, nx), dtype=dtype)
    D = np.zeros((nu, nx), dtype=dtype)
    K0 = np.zeros((nx, nx), dtype=dtype)
    E = np.zeros((nx, nx), dtype=dtype)
    A[0, 0], A[0, 1], A[1, 0], A[1, 1] = 2*sigma, 2*k*theta, 2*k*theta, -2*k*kap
    B[0, 0], B[1, 0] = 6*theta, -2*k
    D[0, 0] = 2*s + 3*np.sum(h)
    K0[0, 0], E[0, 0] = -6, 2*s
    for i, (hi, wi) in enumerate(zip(h, w)):
        j, u = i+1, i+2
        A[u, u], A[1, u], A[u, 1] = -hi*k, hi*k, hi*k
        B[u, j] = hi
        D[0, j] = -hi
        delta = np.zeros(nx, dtype=dtype)
        delta[0], delta[j] = -3, 1
        E -= hi*wi*np.outer(delta, delta)
    return A, B, D, K0, E


def full_hessian(N, y, include_fluids=True):
    """Finite harmonic Hessian in the order (u,xdot,x)."""
    A, B, D, K0, E = action_blocks(N, y, include_fluids)
    zero = np.zeros_like(K0)
    return np.block([[A, B, D], [B.T, K0, zero], [D.T, zero, E]])


def unreduced_lagrangian(N, y, u, x, xdot):
    """Independent polynomial form, used to verify all Hessian entries."""
    alpha, chi, vm, vr = u
    z, dm, dr = x
    zd, dmd, drd = xdot
    theta, sigma = owner.theta_sigma(y[1], y[2])
    _, kap, k, s, h = scales(N)
    L = (-3*zd**2+s*z**2+sigma*alpha**2+2*k*theta*alpha*chi
         -2*k*zd*chi+6*theta*alpha*zd+2*s*alpha*z-k*kap*chi**2)
    for hi, wi, vi, di, ddi in zip(h, W, [vm, vr], [dm, dr], [dmd, drd]):
        delta = di-3*z
        L += hi*(vi*ddi-.5*k*vi**2+k*chi*vi-.5*wi*delta**2-alpha*delta)
    return L


def reduced_blocks(N, y, include_fluids=True):
    A, B, D, K0, E = action_blocks(N, y, include_fluids)
    AB, AD = np.linalg.solve(A, B), np.linalg.solve(A, D)
    return K0-B.T@AB, -B.T@AD, E-D.T@AD


def reconstruct(N, y, x, xdot, include_fluids=True):
    A, B, D, _, _ = action_blocks(N, y, include_fluids)
    return -np.linalg.solve(A, B@xdot+D@x)


def canonical_maps(N, y, include_fluids=True):
    """Return xdot and auxiliary rows acting on canonical state (x,p).

    p=a^3(M xdot+L x). Matrices are complex-step compatible.
    """
    M, L, V = reduced_blocks(N, y, include_fluids)
    nx = len(M)
    invM = np.linalg.solve(M, np.eye(nx))
    vel = np.column_stack((-invM@L, invM/np.exp(3*N)))
    A, B, D, _, _ = action_blocks(N, y, include_fluids)
    aux = -np.linalg.solve(A, B@vel+np.column_stack((D, np.zeros_like(D))))
    return vel, aux


def hamiltonian_matrix(N, y, include_fluids=True):
    M, L, V = reduced_blocks(N, y, include_fluids)
    vel, _ = canonical_maps(N, y, include_fluids)
    force = np.exp(3*N)*(L.T@vel+np.column_stack((V, np.zeros_like(V))))
    return np.vstack((vel, force))/y[2]


def along_background_derivative(function, N, y, step=1e-25):
    """Exact first directional derivative to floating precision, not differenced constraints."""
    yN = bg.rhs(float(N), np.asarray(y, dtype=float))
    return np.imag(function(N+1j*step, np.asarray(y)+1j*step*yN))/step


def newtonian_map(N, y):
    """Rows: Phi,Psi,pi,delta_m,v_m,delta_r,v_r; no GP evolution input."""
    H = y[2]
    F = hamiltonian_matrix(N, y)
    vel, aux = canonical_maps(N, y)
    auxN = along_background_derivative(lambda n, b: canonical_maps(n, b)[1], N, y)
    chi_dot = H*(auxN[1]+aux[1]@F)
    zrow = np.eye(6)[0]
    phi, psi, pi = aux[0]+chi_dot, -zrow-H*aux[1], -aux[1]
    rows = [phi, psi, pi]
    for i, wi in enumerate(W):
        density = (1+wi)*(np.eye(6)[i+1]-3*zrow-3*H*aux[1])
        velocity = aux[i+2]-aux[1]
        rows.extend([density, velocity])
    return np.asarray(rows)


def topographic_seed(sol):
    """X2=(zeta,Pi_AK) with Pi_AK=2 a^3 G_S zeta_dot at the anchor.

    Physical prescription: delta_m=delta_r=v_m=v_r=0 in uniform-T ADM
    gauge at z=2.1. Induced Newtonian responses follow the constraints.
    This selects two columns of the six-dimensional solution space; it
    does not exclude independent primordial fluid modes in general.
    """
    N = N_START
    y = sol.sol(N)
    a, _, k, _, _ = scales(N)
    G = owner.gs_n2(y[1], y[2])
    M, L, _ = reduced_blocks(N, y)
    seed = np.zeros((6, 2))
    for j in range(2):
        z, Pi = np.eye(2)[:, j]
        zd = Pi/(2*a**3*G)
        _, chi = owner.constraint_solution_n2(a, y[1], y[2], z, zd)
        x = np.array([z, 3*z, 3*z])
        xd = np.array([zd, -k*chi, -k*chi])
        seed[:, j] = np.r_[x, a**3*(M@xd+L@x)]
    return seed


def integrate_propagator(sol, rtol=2e-10, atol=2e-12, max_step=.01):
    """Full six-state fundamental matrix. No projection/restart operation."""
    def rhs(N, flat):
        return (hamiltonian_matrix(N, sol.sol(N))@flat.reshape(6, 6)).ravel()
    result = solve_ivp(rhs, (N_START, 0.), np.eye(6).ravel(), method='DOP853',
                       rtol=rtol, atol=atol, max_step=max_step, dense_output=True)
    if not result.success:
        raise RuntimeError(result.message)
    return result


def constraint_residuals(N, y, x, xd, u):
    """Original action equations, independently of matrix assembly."""
    alpha, chi, vm, vr = u
    theta, sigma = owner.theta_sigma(y[1], y[2])
    _, kap, k, s, h = scales(N)
    delta = np.asarray(x[1:])-3*x[0]
    return np.array([sigma*alpha+k*theta*chi+3*theta*xd[0]+s*x[0]-.5*h@delta,
                     theta*alpha-xd[0]-kap*chi+.5*h@np.array([vm, vr]),
                     xd[1]-k*(vm-chi), xd[2]-k*(vr-chi)])


def fluid_residuals(N, y, state):
    H = y[2]
    F = hamiltonian_matrix(N, y)
    vel, aux = canonical_maps(N, y)
    auxN = along_background_derivative(lambda n, b: canonical_maps(n, b)[1], N, y)
    udot = H*(auxN+aux@F)@state
    u, xd = aux@state, vel@state
    delta = state[1:3]-3*state[0]
    # The Euler equations of the Schutz action, not GP equations.
    euler = udot[2:]-3*W*H*u[2:]+u[0]+W*delta
    _, _, k, _, _ = scales(N)
    continuity = xd[1:]-k*(u[2:]-u[1])
    return np.r_[continuity, euler]


def heldout_gp_constraints(N, y, state):
    # Import is intentionally confined to this audit. Neither action assembly
    # nor evolution depends on the defective GP trace/scalar representation.
    import matter_sourced_n2 as gp
    obs = newtonian_map(N, y)@state
    F = hamiltonian_matrix(N, y)
    _, aux = canonical_maps(N, y)
    auxN = along_background_derivative(lambda n, b: canonical_maps(n, b)[1], N, y)
    pidot = -y[2]*(auxN[1]+aux[1]@F)@state
    # The Psi derivative needs only a first background derivative. Using
    # Phi_dot=Psi_dot here is separately certified by the no-slip row test.
    yN = bg.rhs(N, y)
    zd = canonical_maps(N, y)[0][0]@state
    psidot = -zd-y[2]*yN[2]*(aux[1]@state)+y[2]*pidot
    p, psi, pi, dm, vm, dr, vr = obs
    st = gp.SourceState(p, pi, dm, vm, dr, vr)
    return gp.constraint_residuals(N, y, st, psidot, pidot)


def make_artifact(sol, prop, grid=401):
    seed = topographic_seed(sol)
    J = np.block([[np.zeros((3, 3)), np.eye(3)], [-np.eye(3), np.zeros((3, 3))]])
    scans, maxima = [], dict(constraint=0., fluid=0., no_slip=0., gp_local=0., symplectic=0.)
    for N in np.linspace(N_START, 0., grid):
        y = sol.sol(N)
        A, B, D, _, _ = action_blocks(N, y)
        # Metric-only block after exactly eliminating the two velocity auxiliaries.
        metric = A[:2, :2]-A[:2, 2:]@np.linalg.solve(A[2:, 2:], A[2:, :2])
        M, _, _ = reduced_blocks(N, y)
        U = prop.sol(N).reshape(6, 6)
        vel, aux = canonical_maps(N, y)
        R = newtonian_map(N, y)
        maxima['symplectic'] = max(maxima['symplectic'], float(np.max(np.abs(U.T@J@U-J))))
        maxima['no_slip'] = max(maxima['no_slip'], float(np.max(np.abs(R[0]-R[1]))))
        for state in (U@seed).T:
            scale = max(1., float(np.max(np.abs(state))))
            for key, value in [('constraint', constraint_residuals(N,y,state[:3],vel@state,aux@state)),
                               ('fluid', fluid_residuals(N,y,state)),
                               ('gp_local', heldout_gp_constraints(N,y,state))]:
                maxima[key] = max(maxima[key], float(np.max(np.abs(value)))/scale)
        scans.append({'z':float(np.expm1(-N)), 'aux_det':float(np.linalg.det(A)),
                      'aux_condition':float(np.linalg.cond(A)),
                      'metric_det':float(np.linalg.det(metric)),
                      'metric_condition':float(np.linalg.cond(metric)),
                      'kinetic_eigenvalues':np.linalg.eigvalsh(M).tolist()})
    samples=[]
    for z in [2.1,1.5,1.,.8,.5,.3,0.]:
        N=-np.log1p(z); y=sol.sol(N); U=prop.sol(N).reshape(6,6)
        samples.append({'z':z, 'full_canonical_propagator':U.tolist(),
                        'topographic_canonical_columns':(U@seed).tolist(),
                        'newtonian_columns':(newtonian_map(N,y)@U@seed).tolist()})
    return {'schema':'R1-action-native-matter-backreaction-v1',
            'owner':'code/closed_horndeski_n2.py',
            'frozen_manifest_sha256':hashlib.sha256(MANIFEST.read_bytes()).hexdigest(),
            'background':json.loads(MANIFEST.read_text())['background_R1'],
            'observational_fits':0, 'extra_force_coefficients':0,
            'harmonics':{'k_squared_over_K':8,'shifted_laplacian_over_K':-5},
            'variables':['zeta','D_m','D_r','p_zeta','p_Dm','p_Dr'],
            'column_coordinates':['q2=zeta_anchor','Pi2=2*a_anchor^3*G_S2*zeta_dot_anchor'],
            'IC':'zero ADM density and velocity perturbations at z=2.1; no fitted fluid modes',
            'seed':seed.tolist(), 'scan':scans, 'samples':samples,
            'residual_maxima':maxima,
            'kinetic_min':min(min(r['kinetic_eigenvalues']) for r in scans),
            'prior_GP_evidence':'User-supplied prior: differentiated constraints close at 2.16e-9; trace discrepancy -6*kappa*(pi_dot+H*pi); scalar Noether identity still defective. Not rerun or patched.',
            'scope':'R1 minimally coupled ideal barotropic scalar fluids; not full microscopic BHSM normalization, nonlinear fluid physics, or a gradient-stability theorem'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'artifacts/R1_ACTION_NATIVE_MATTER_BACKREACTION_V1.json')
    args=parser.parse_args()
    sol=frozen_background(); prop=integrate_propagator(sol)
    data=make_artifact(sol,prop)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n',encoding='utf8')
    print(json.dumps({'kinetic_min':data['kinetic_min'],'residuals':data['residual_maxima']},indent=2))


if __name__=='__main__': main()

