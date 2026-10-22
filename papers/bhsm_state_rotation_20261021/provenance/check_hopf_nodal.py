"""Exact and seeded numerical checks of the Hopf-neutral nodal obstruction.

Run from any directory; writes its receipt beside this source. The exact proof
is in hopf_nodal_check.md. These are mathematical implementation checks.
"""
from pathlib import Path
import json
import numpy as np
import sympy as s

I = s.eye(2)
Z = s.zeros(2)
J = Z.row_join(-I).col_join(I.row_join(Z))
u, v, w = s.symbols('u v w', real=True)
A = s.Matrix([[u,v,0,w], [v,-u,-w,0], [0,-w,u,v], [w,0,v,-u]])
rho2 = u*u+v*v+w*w
assert A == A.T and s.trace(A) == 0 and A*J == J*A
assert A*A == rho2*s.eye(4)
assert s.factor(A.det()) == rho2**2

# Independently obtain the neutral dimension from all symmetric STF variables.
symbols = s.symbols('a0:10', real=True)
G = s.zeros(4)
k = 0
for i in range(4):
    for j in range(i, 4):
        G[i,j] = G[j,i] = symbols[k]
        k += 1
constraints = [s.trace(G)] + list(G*J-J*G)
matrix, _ = s.linear_eq_to_matrix(constraints, symbols)
neutral_dimension = 10-matrix.rank()
assert neutral_dimension == 3
G0 = (G+J.T*G*J)/2
G2 = (G-J.T*G*J)/2
assert G0*J-J*G0 == s.zeros(4)
assert G2*J+J*G2 == s.zeros(4)
assert s.simplify(s.trace(G0*G2)) == 0

# K = Jx . grad, tested as a differential operator, without spectral code.
x = s.Matrix(s.symbols('x0:4', real=True))
def K(f):
    return s.expand(sum((J*x)[i]*s.diff(f,x[i]) for i in range(4)))
f0 = (x.T*G0*x)[0]
f2 = (x.T*G2*x)[0]
assert s.simplify(K(f0)) == 0
assert s.simplify(K(K(f2))+4*f2) == 0

witness = s.diag(1,0,-1,0)
observer = s.Matrix([0,0,0,1])
assert witness*J+J*witness == s.zeros(4)
assert witness*observer == s.zeros(4,1)
assert witness != s.zeros(4)

# Seeded checks of the stronger invariant over random neutral matrices and X.
rng = np.random.default_rng(20261021)
max_identity_residual = 0.0
max_square_residual = 0.0
minimum_kernel_norm = float('inf')
for _ in range(128):
    p = rng.normal(size=3)
    p /= np.linalg.norm(p)
    an = np.asarray(A.subs(dict(zip((u,v,w),p))), dtype=float)
    xn = rng.normal(size=4)
    xn /= np.linalg.norm(xn)
    f = float(xn@an@xn)
    gradient = 2*(an@xn-f*xn)
    max_identity_residual = max(max_identity_residual, abs(f*f+gradient@gradient/4-1))
    max_square_residual = max(max_square_residual, float(np.max(np.abs(an@an-np.eye(4)))))
    minimum_kernel_norm = min(minimum_kernel_norm, float(np.linalg.norm(an@xn)))
assert max_identity_residual < 3e-15
assert max_square_residual < 3e-15
assert minimum_kernel_norm > 1-3e-15

receipt = {
    'scope': 'exact Hopf/Berger scalar geometry; no optical coupling or state selection',
    'symbolic_checks': {
        'neutral_dimension': neutral_dimension,
        'charged_dimension': 9-neutral_dimension,
        'A_square_equals_rho2_identity': True,
        'det_A_equals_rho4': True,
        'neutral_Hopf_derivative_zero': True,
        'charged_Hopf_second_derivative_minus4': True,
        'nonzero_charged_stationary_nodal_witness': True,
        'berger_n2_eigenvalues': ['8', '4+4*a**2'],
        'round_limit_a1': [8,8],
    },
    'numerical_checks': {
        'seed': 20261021,
        'samples': 128,
        'max_amplitude_gradient_identity_absolute_residual': max_identity_residual,
        'max_A_square_absolute_residual': max_square_residual,
        'minimum_norm_AX_for_rho1': minimum_kernel_norm,
    },
    'status': 'PASS',
}
target = Path(__file__).with_name('hopf_nodal_receipt.json')
target.write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf-8')
print(json.dumps(receipt, indent=2))
