import numpy as np
EPS=np.array([[[0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, -1.0, 0.0]], [[0.0, 0.0, -1.0], [0.0, 0.0, 0.0], [1.0, 0.0, 0.0]], [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, 0.0, 0.0]]])
def epsilon():return EPS
M=np.sqrt(8)*np.column_stack((np.eye(3),np.zeros(3)))

def _bracket(a, b):
    """[H_a,H_b]=epsilon_abc H_c/sqrt(2); H_Y is central."""
    out = np.zeros(np.broadcast_shapes(a.shape, b.shape), float)
    out[..., :3] = np.cross(a[..., :3], b[..., :3])/np.sqrt(2)
    return out

def _curl(a, angular):
    return 2*a+np.einsum('ijk,...jkc->...ic', epsilon(), angular)

def _curl_bracket(a, b):
    result = np.zeros(np.broadcast_shapes(a.shape, b.shape), float)
    eps = epsilon()
    for i in range(3):
        for j in range(3):
            for k in range(3):
                if eps[i, j, k]:
                    result[..., i, :] += eps[i, j, k]*_bracket(a[..., j, :], b[..., k, :])
    return result

def _direction_polynomials(a, direction, dt, dr, ed):
    """Literal first curvature variation for every five-component test."""
    Ai, At, Ar = a[..., 2:, :], a[..., 0, :], a[..., 1, :]
    di, d0, d1 = direction[..., 2:, :], direction[..., 0, :], direction[..., 1, :]
    Ft, Fr, B = (np.zeros((5,)+di.shape) for _ in range(3))
    X = dt[..., 1, :]-dr[..., 0, :]+_bracket(d0, Ar)+_bracket(At, d1)
    Ft[0] = dt[..., 2:, :]-ed[..., :, 0, :]+_bracket(d0[..., None, :], Ai)+_bracket(At[..., None, :], di)
    Ft[1] = _bracket(d0[..., None, :], M)
    Fr[0] = dr[..., 2:, :]-ed[..., :, 1, :]+_bracket(d1[..., None, :], Ai)+_bracket(Ar[..., None, :], di)
    Fr[1] = _bracket(d1[..., None, :], M)
    B[0] = _curl(di, ed[..., :, 2:, :])+_curl_bracket(Ai, di)
    B[1] = _curl_bracket(M, di)
    return X, Ft, Fr, B
