"""Literal two-parameter controls of the reusable geometric incidence map.

The synthetic off-shell metrics, embeddings and coefficient jets are NOT
physical BHSM inputs. They check the constructed map without selecting a
carrier, gamma, quantum operator, outgoing domain or matching correction.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import sys
from pathlib import Path

import mpmath as mp
import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO/'src'))
from bhsm.interface import muon_surface_incidence_second_jet as surface


def control_inputs(seed, lorentzian):
    rng = np.random.default_rng(seed)
    q = np.diag([-1.4, 1.2, 1.5, 1.7, 1.9] if lorentzian
                else [1.4, 1.2, 1.5, 1.7, 1.9])
    c = np.diag([1.1, 1.3, 1.6])
    b = rng.normal(size=(5, 3)) / 7
    a = q + b @ np.linalg.solve(c, b.T)
    g0 = np.block([[a, b], [b.T, c]])
    dg = []
    for _ in range(3):
        z = rng.normal(size=(8, 8)) / 30
        dg.append((z + z.T) / 2)
    G = np.stack((g0, *dg))
    t0 = np.vstack((np.eye(4), np.zeros(4))) + rng.normal(size=(5, 4)) / 40
    T = np.stack((t0, *(rng.normal(size=(5, 4)) / 20 for _ in range(3))))
    gamma = np.array((1.23, .17, -.11, .09))
    return G, T, gamma


def literal_mp_jets(G, T, gamma):
    """Independent nonlinear quotient and determinant on a tiny real box.

    There is no differentiated solve/product recursion from the tested map.
    A 75-digit literal centered difference with step 1e-14 makes its O(h^2)
    truncation negligible compared with binary64 assembly errors here.
    These evaluated formulas are not outward interval enclosures.
    """
    def matrix(a):
        return mp.matrix([[mp.mpf(str(z)) for z in row] for row in a])
    with mp.workdps(75):
        gg = [matrix(a) for a in G]
        tt = [matrix(a) for a in T]
        ss = [mp.mpf(str(z)) for z in gamma]

        def literal(x, y):
            g = gg[0] + x * gg[1] + y * gg[2] + x*y * gg[3]
            t = tt[0] + x * tt[1] + y * tt[2] + x*y * tt[3]
            gam = ss[0] + x * ss[1] + y * ss[2] + x*y * ss[3]
            a, b, c = g[:5, :5], g[:5, 5:], g[5:, 5:]
            cols = [mp.lu_solve(c, b.T[:, k]) for k in range(5)]
            solution = mp.matrix(3, 5)
            for j, col in enumerate(cols):
                solution[:, j] = col
            q = a - b * solution
            h = t.T * q * t
            density = mp.sqrt(abs(mp.det(h)))
            return q, h, mp.matrix([density, -gam * density])

        step = mp.mpf('1e-14')
        z = mp.mpf(0)
        values = {(i, j): literal(i*step, j*step)
                  for i, j in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1),
                               (1, 1), (1, -1), (-1, 1), (-1, -1))}
        outputs = []
        for k in range(3):
            jets = [values[(0, 0)][k],
                (values[(1, 0)][k] - values[(-1, 0)][k]) / (2*step),
                (values[(0, 1)][k] - values[(0, -1)][k]) / (2*step),
                (values[(1, 1)][k] - values[(1, -1)][k]
                 - values[(-1, 1)][k] + values[(-1, -1)][k]) / (4*step**2)]
            outputs.append(np.array([[[float(z) for z in row] for row in x.tolist()]
                                     for x in jets]))
    return outputs[0], outputs[1], outputs[2][:, 0, 0], outputs[2][:, 1, 0]


def flat_normal_shape_control():
    """A genuine flat K=0 embedding germ, with nonzero normal gradients.

    X(z;x,y)=(z,x f(z)+y g(z)); at z=0, f=g=0 and gradients a,b.
    h_x=h_y=0, h_xy=a b.T+b a.T, yet the area mixed variation is nonzero.
    Time gradients remain present in this Lorentzian geometry control.
    """
    G = np.zeros((4, 8, 8))
    G[0] = np.diag([-1., 1., 1., 1., 1., 1.1, 1.3, 1.7])
    T = np.zeros((4, 5, 4))
    T[0, :4] = np.eye(4)
    a, b = np.array([.2, .3, -.1, .4]), np.array([-.25, .15, .2, .35])
    T[1, 4], T[2, 4] = a, b
    gamma = np.array([1.17, 0., 0., 0.])
    result = surface.surface_incidence_second_jet(
        metric8_jet=G, tangent_inclusion_jet=T, gamma_jet=gamma)
    expected_hxy = np.outer(a, b) + np.outer(b, a)
    expected_density_xy = a @ np.diag([-1., 1., 1., 1.]) @ b
    return result, expected_hxy, expected_density_xy, -gamma[0]*expected_density_xy


def evaluate(output):
    output = Path(output).resolve()
    if output.exists():
        raise FileExistsError('preserve earlier controls')
    records = []
    for seed, lorentzian in ((16131, False), (16153, True)):
        G, T, gamma = control_inputs(seed, lorentzian)
        result = surface.surface_incidence_second_jet(
            metric8_jet=G, tangent_inclusion_jet=T, gamma_jet=gamma)
        q, h, rho, action = literal_mp_jets(G, T, gamma)
        errors = dict(quotient=float(np.max(abs(result['quotient_metric_jet']-q))),
            induced=float(np.max(abs(result['induced_metric_jet']-h))),
            density=float(np.max(abs(result['worldvolume_density_jet']-rho))),
            signed_action=float(np.max(abs(result['signed_area_action_jet']-action))))
        covector_errors = []
        for axis in (1, 2):
            contraction = (np.sum(result['metric8_covector_density'] * G[axis])
                + np.sum(result['tangent_inclusion_covector_density'] * T[axis])
                + result['gamma_covector_density'] * gamma[axis])
            covector_errors.append(float(abs(contraction-result['signed_area_action_jet'][axis])))
        if max(errors.values()) > 1e-12 or max(covector_errors) > 1e-12:
            raise AssertionError((errors, covector_errors))
        records.append(dict(classification='SYNTHETIC_OFF_SHELL_GEOMETRIC_MAP_CONTROL',
            seed=seed, signature=result['induced_signature'],
            nonzero_B_norm=float(np.linalg.norm(G[0, :5, 5:])),
            moving_T_jet_norms=[float(np.linalg.norm(z)) for z in T[1:]],
            literal_mp75_jet_absolute_errors=errors,
            covector_first_contact_errors=covector_errors,
            signed_action_jet=result['signed_area_action_jet'].tolist()))
    shape, hxy, rhoxy, actionxy = flat_normal_shape_control()
    shape_record = dict(classification='FLAT_K_ZERO_NORMAL_SHAPE_GERM_CONTROL_NOT_PHYSICAL_CARRIER',
        first_induced_metric_norm=float(np.linalg.norm(shape['induced_metric_jet'][1:3])),
        mixed_induced_metric_closed_form_error=float(np.max(abs(shape['induced_metric_jet'][3]-hxy))),
        mixed_density_closed_form_error=float(abs(shape['worldvolume_density_jet'][3]-rhoxy)),
        mixed_action_closed_form_error=float(abs(shape['signed_area_action_jet'][3]-actionxy)),
        nonzero_mixed_action=float(shape['signed_area_action_jet'][3]))
    if (shape_record['first_induced_metric_norm'] != 0
            or max(shape_record[k] for k in ('mixed_induced_metric_closed_form_error',
                'mixed_density_closed_form_error', 'mixed_action_closed_form_error')) > 1e-13
            or abs(shape_record['nonzero_mixed_action']) < .1):
        raise AssertionError(shape_record)
    anchors = ('src/bhsm/interface/completion/tensor_differential_incidence_v14_69.py',
               'src/bhsm/interface/covariant_bubble_interface_mechanics.py')
    payload = dict(classification='OWNED_GEOMETRIC_SURFACE_SECOND_INCIDENCE_IMPLEMENTED',
        producer_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        module_sha256=sha256(Path(surface.__file__).read_bytes()).hexdigest(),
        owner_source_hashes={p:sha256((REPO/p).read_bytes()).hexdigest() for p in anchors},
        records=records, flat_normal_shape_control=shape_record,
        physical_carrier_or_gamma_selected=False, physical_microscopic_operator_selected=False,
        physical_outgoing_domain_evaluated=False, full_derivative_2e_minus_10_passed=False,
        coupled_matching_corrections=0, physical_spin_normalization=None,
        physical_muon_magnetic_moment=None,
        error_scope='Binary64 map checked against mp75 literal nonlinear quotient/determinant finite differences; no outward input/continuum/physical certificate.')
    output.mkdir(parents=True)
    (output/'result.json').write_text(json.dumps(payload, sort_keys=True, indent=2)+'\n',
                                     encoding='utf-8', newline='\n')
    print(json.dumps(dict(output=str(output), records=records, shape=shape_record), sort_keys=True))
    return payload


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    evaluate(parser.parse_args().output)
