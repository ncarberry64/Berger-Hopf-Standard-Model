"""Independent augmented-exponential control of the magnetic Duhamel slots."""
import numpy as np
from scipy.linalg import expm

import bhsm.interface.muon_holomorphic_n1_magnetic_action as magnetic
from bhsm.interface.muon_native_dirac_hamiltonian import lepton_current_hilbert_representation


def _angular_offdiagonal(coefficients):
    # Literal unit-Haar <phi_h*phi_0*phi_k>=delta_hk. No background or
    # tangent coefficient is conjugated in either directed placement.
    result = np.zeros((90, 90), complex)
    for h in range(4):
        rows = 18 + 4*np.arange(18) + h
        result[np.ix_(rows, np.arange(18))] = coefficients[h]
        result[np.ix_(np.arange(18), rows)] = coefficients[h]
    return result


def test_three_magnetic_current_slots_match_independent_full_exponential(monkeypatch):
    rng = np.random.default_rng(221012)
    draw = lambda shape, scale: scale*(rng.normal(size=shape)+.3j*rng.normal(size=shape))
    H, JR, LT = [draw((18, 18), .025) for _ in range(3)]
    # Keep the target independent: a wrong dagger or swapped current slot
    # cannot pass through a symmetry of the fixture.
    assert np.linalg.norm(LT-JR.T) > .1
    DJ, DL = draw((4, 18, 18), .03), draw((4, 18, 18), .04)
    def current(h, dh, lapse, dlapse):
        return dict(literal_right=JR, literal_left=LT,
                    literal_right_first=np.einsum('hk,hij->kij', dh, DJ),
                    literal_left_first=np.einsum('hk,hij->kij', dh, DL))
    monkeypatch.setattr(magnetic, 'holomorphic_unit_em_moments', current)
    E = magnetic.magnetic_angular_trace()['derivative_matrices']
    alpha = lepton_current_hilbert_representation()['alpha']
    R, N = 1.2+.02j, .9-.03j
    body = np.zeros((90, 90), complex); body[:18, :18] = H
    body[18:, 18:] = np.kron(H, np.eye(4))-1j*sum(np.kron(a, e) for a, e in zip(alpha, E))/R
    J, L = np.zeros_like(body), np.zeros_like(body)
    J[:18, :18] = JR; J[18:, 18:] = np.kron(JR, np.eye(4))
    L[:18, :18] = LT; L[18:, 18:] = np.kron(LT, np.eye(4))
    vertices = draw((24, 18, 18), .04); vertices[4:8] = 0
    wall = draw((24, 4, 3), .08)
    W = np.zeros((20, 84)); W[:, :20] = np.eye(20)
    hv = np.zeros((4, 84)); hv[:, 80:] = np.eye(4)
    field = np.zeros((84, 4, 3), complex); field[:20] = wall[:20]; field[80:] = wall[20:]
    stage = dict(R4=np.array(R), induced_lapse=np.array(N), Hcan=H,
                 canonical_wall_current_vertices=vertices)
    binding = dict(stage=stage, row=dict(H=np.array([1., .2, .1, -.05])), lifts=dict(W=W, hv=hv))
    steps = np.array([.025, .025])
    z, w = np.polynomial.legendre.leggauss(10)
    points = []
    for cell in range(2):
        for point, weight in zip(z, w):
            local = (point+1)/2; sigma = (cell+local)/2
            points.append(dict(cell=cell, sigma=sigma, scale=-1j*steps[cell]*weight/2,
                               total_field=field.reshape(336, 3)))
    actual = magnetic.magnetic_unsquared_unit_em_current([binding, binding], steps, dict(point_sources=points))
    Xi, dJ, dL = [], [], []
    for axis in range(3):
        Xi.append(_angular_offdiagonal(np.einsum('ch,cij->hij', wall[:, :, axis], vertices)))
        dJ.append(_angular_offdiagonal(np.einsum('ch,cij->hij', wall[20:, :, axis], DJ)))
        dL.append(_angular_offdiagonal(np.einsum('ch,cij->hij', wall[20:, :, axis], DL)))
    def full_current(B, F, T):
        # Constant source is an independent middle block; integrating the
        # literal target is a third block. This uses no Duhamel placement.
        generator = np.zeros((270, 270), complex)
        generator[:90, :90] = B; generator[:90, 90:180] = F
        generator[180:, :90] = T
        return expm(np.sum(steps)*generator)[180:, 90:180]
    B, F, T = -1j*N*body, 1j*N*J, 1j*N*L
    for name, directions in (
        ('operator_insertion', [(-1j*N*x, np.zeros_like(F), np.zeros_like(T)) for x in Xi]),
        ('right_current_motion', [(np.zeros_like(B), 1j*N*x, np.zeros_like(T)) for x in dJ]),
        ('literal_left_motion', [(np.zeros_like(B), np.zeros_like(F), 1j*N*x) for x in dL]),
        ('total', list(zip(-1j*N*np.array(Xi), 1j*N*np.array(dJ), 1j*N*np.array(dL)))),
    ):
        for axis, (dB, dF, dT) in enumerate(directions):
            step = 2e-4
            derivative = (full_current(B+step*dB, F+step*dF, T+step*dT)
                          -full_current(B-step*dB, F-step*dF, T-step*dT))/(2*step)
            np.testing.assert_allclose(actual[name][axis], derivative, rtol=8e-8, atol=3e-15)
    assert np.linalg.norm(actual['operator_insertion']) > 1e-8
    assert np.linalg.norm(actual['right_current_motion']) > 1e-8
    assert np.linalg.norm(actual['literal_left_motion']) > 1e-8
