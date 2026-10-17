"""Spatial birth-map jets from the existing real worldvolume variational IVP.

This is an additive, conditional evaluator. It selects neither a physical
worldvolume nor initial data. In particular a temporal Wilson line is not
asserted to transport the spatial gauge connection without curvature.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
from scipy.linalg import expm

REPO = Path(r'C:\Users\carbe\Downloads\BHSM_muon_parent_maxwell_worktree_20261001')
sys.path.insert(0, str(REPO / 'src'))
from bhsm.interface.muon_intrinsic_worldvolume_scalar_transport import (
    unit_s3_material_frame, worldvolume_scalar_transport_ivp,
)


try:
    from bhsm.interface.muon_worldvolume_spatial_birth_jet import (
        spatial_birth_map_one_jet, affine_birth_connection,
    )
except ModuleNotFoundError as exc:
    if exc.name != 'bhsm.interface.muon_worldvolume_spatial_birth_jet':
        raise
    # Workspace preview of the exact public module before repository copy.
    import importlib.util
    _public_path = Path(__file__).with_name('muon_worldvolume_spatial_birth_jet.py')
    _spec = importlib.util.spec_from_file_location(
        'bhsm.interface.muon_worldvolume_spatial_birth_jet', _public_path)
    _public = importlib.util.module_from_spec(_spec)
    sys.modules[_spec.name] = _public
    _spec.loader.exec_module(_public)
    spatial_birth_map_one_jet = _public.spatial_birth_map_one_jet
    affine_birth_connection = _public.affine_birth_connection


SIGMA = np.array([[[0, 1], [1, 0]], [[0, -1j], [1j, 0]],
                  [[1, 0], [0, -1]]], complex)
POINTS = np.array([[.8, .3, -.2, .4], [.7, -.4, .3, .2],
                   [.6, .2, .4, -.3]], float)
POINTS /= np.linalg.norm(POINTS, axis=1)[:, None]


def _initial(labels, rotated):
    frame = unit_s3_material_frame(labels)
    if rotated:
        alpha = .19
        q = np.cos(alpha)*labels+np.sin(alpha)*frame[:, :, 1]
        # Right-invariant E2 is linear in quaternion coordinates.
        k = np.empty((len(labels), 3, 4))
        for axis in range(3):
            v = frame[:, :, axis]
            w, x, y, z = v.T
            E2v = np.column_stack((-y, z, w, -x))
            k[:, axis] = np.cos(alpha)*v+np.sin(alpha)*E2v
    else:
        q, k = labels.copy(), frame.transpose(0, 2, 1).copy()
    axis = 2 if rotated else 1
    strength = .17
    U = np.stack([expm(1j*strength*w*SIGMA[axis]) for w in q[:, 0]])
    dU = 1j*strength*k[:, :, 0, None, None]*(SIGMA[axis] @ U)[:, None]
    return q, U, np.ones(len(q)), k, dU, np.zeros((len(q), 3))


def _evaluator(rotated):
    """Two manufactured real timelike histories; neither is a muon state."""
    def evaluate(t, q, c, v):
        p = len(q)
        E = unit_s3_material_frame(q)
        b = np.zeros((p, 3)); db = np.zeros((p, 3, 3))
        ddb = np.zeros((p, 3, 3, 3))
        if rotated:
            b[:, 2] = .31
        else:
            b[:, 0] = .23*q[:, 0]
            db[:, :, 0] = .23*E[:, 0, :]
            # E_c E_a w=-E_c(q_a).
            ddb[:, :, :, 0] = -.23*E[:, 1:, :].transpose(0, 2, 1)
        h = np.zeros((p, 4, 4))
        h[:, 1:, 1:] = -np.eye(3)
        h[:, 0, 1:] = h[:, 1:, 0] = b
        h[:, 0, 0] = 1.3**2-np.sum(b*b, axis=1)
        dh = np.zeros((p, 3, 4, 4)); ddh = np.zeros((p, 3, 3, 4, 4))
        dh[:, :, 0, 1:] = dh[:, :, 1:, 0] = db
        dh[:, :, 0, 0] = -2*np.einsum('pi,pai->pa', b, db)
        ddh[:, :, :, 0, 1:] = ddh[:, :, :, 1:, 0] = ddb
        ddh[:, :, :, 0, 0] = -2*(np.einsum('pci,pai->pca', db, db)
            +np.einsum('pi,pcai->pca', b, ddb))
        A = np.zeros((p, 4, 2, 2), complex)
        dA = np.zeros((p, 3, 4, 2, 2), complex)
        if rotated:
            phase = .21+.13*q[:, 0]-.11*q[:, 1]
            A[:, 0] = 1j*phase[:, None, None]*SIGMA[2]
            A[:, 1] = 1j*.07*SIGMA[0]
            A[:, 3] = 1j*.09*SIGMA[2]
            dA[:, :, 0] = 1j*(.13*E[:, 0, :]-.11*E[:, 1, :])[:, :, None, None]*SIGMA[2]
        else:
            A[:, 0] = 1j*(.21*SIGMA[0]+.13*q[:, 0, None, None]*SIGMA[1]+.08*t*SIGMA[2])
            A[:, 1:] = 1j*.07*SIGMA
            dA[:, :, 0] = 1j*.13*E[:, 0, :, None, None]*SIGMA[1]
        out = dict(metric=h, metric_spatial_derivatives=dh,
            metric_spatial_second_derivatives=ddh, connection=A)
        if v is not None:
            if np.any(v):
                raise ValueError('fixture only binds literal zero coefficient tangent')
            out.update(metric_variation=np.zeros_like(h),
                metric_spatial_derivative_variation=np.zeros_like(dh),
                connection_variation=np.zeros_like(A), connection_spatial_derivatives=dA)
        return out
    return evaluate


def _solve(labels, rotated, with_jets):
    q, U, J, K, dU, dJ = _initial(labels, rotated)
    kw = dict(coefficients=np.array([.7]), times=np.array([0., .13, .27]),
        initial_material_points=q, initial_bundle_transport=U,
        initial_jacobian=J, evaluator=_evaluator(rotated), rtol=3e-14, atol=2e-15)
    if not with_jets:
        return worldvolume_scalar_transport_ivp(**kw)
    return spatial_birth_map_one_jet(**kw, parent_label_points=labels,
        initial_material_point_spatial_derivatives=K,
        initial_bundle_transport_spatial_derivatives=dU,
        initial_jacobian_spatial_derivatives=dJ)


def fixture_report(rotated):
    jets = _solve(POINTS, rotated, True)
    base = jets['base']; E = unit_s3_material_frame(POINTS)
    h = 1e-3
    errors = {}
    keymap = [('material_points', 'material_point_spatial_derivatives'),
              ('bundle_transport', 'bundle_transport_spatial_derivatives'),
              ('haar_jacobian', 'haar_jacobian_spatial_derivatives')]
    for output, derivative in keymap:
        errors[output] = 0.
    for axis in range(3):
        values = []
        for step in (2*h, h, -h, -2*h):
            labels = np.cos(step)*POINTS+np.sin(step)*E[:, :, axis]
            values.append(_solve(labels, rotated, False))
        for output, derivative in keymap:
            fd = (-values[0][output]+8*values[1][output]-8*values[2][output]+values[3][output])/(12*h)
            errors[output] = max(errors[output], float(np.max(abs(fd-jets[derivative][:, :, axis]))))
    analytic = None
    if rotated:
        q0, U0, _, _, _, _ = _initial(POINTS, True)
        Ek = unit_s3_material_frame(q0)[:, :, 2]
        analytic = 0.
        beta=.31
        for index, t in enumerate(base['times']):
            q = np.cos(beta*t)*q0+np.sin(beta*t)*Ek
            w, x, _, z = q0.T; y=q0[:, 2]
            integral=(.21+beta*.09)*t+.13*(w*np.sin(beta*t)+z*(np.cos(beta*t)-1))/beta
            integral-=.11*(x*np.sin(beta*t)+y*(np.cos(beta*t)-1))/beta
            U=np.stack([expm(-1j*phase*SIGMA[2])@u for phase,u in zip(integral,U0)])
            analytic=max(analytic,float(np.max(abs(q-base['material_points'][index]))),
                float(np.max(abs(U-base['bundle_transport'][index]))))
    last=-1
    parent = _evaluator(rotated)(0., POINTS, np.array([.7]), None)['connection'][:, 1:]
    child=affine_birth_connection(parent_connection=parent,
        bundle_transport=base['bundle_transport'][last],
        spatial_tangent_map=jets['spatial_tangent_map'][last],
        bundle_spatial_derivatives=jets['bundle_transport_spatial_derivatives'][last])
    M=jets['spatial_tangent_map'][last]; U=base['bundle_transport'][last]
    dU=jets['bundle_transport_spatial_derivatives'][last]
    residual=dU+np.einsum('pbi,pbjk->pijk',M,child)@U[:,None]-U[:,None]@parent
    literal_child=_evaluator(rotated)(base['times'][last],
        base['material_points'][last],np.array([.7]),None)['connection'][:,1:]
    # U is an interior temporal Wilson line. The actual connection on the
    # later slice need not equal the separately imposed birth incidence.
    interior_residual=dU+np.einsum('pbi,pbjk->pijk',M,literal_child)@U[:,None]-U[:,None]@parent
    def transported_connection(index):
        q=base['material_points'][index];u=base['bundle_transport'][index]
        adj=u.conj().swapaxes(-1,-2)
        connection=_evaluator(rotated)(base['times'][index],q,np.array([.7]),None)['connection'][:,1:]
        pull=np.einsum('pbi,pbjk->pijk',jets['spatial_tangent_map'][index],connection)
        return adj[:,None]@pull@u[:,None]+adj[:,None]@jets['bundle_transport_spatial_derivatives'][index]
    # This subtracts any initial incidence mismatch. For a temporal Wilson
    # line its evolution is the pulled curvature contraction, not zero.
    memory=transported_connection(last)-transported_connection(0)
    return dict(fixture='constant right flow, Abelian Wilson generator' if rotated else
        'spatially varying right flow, noncommuting Wilson generator',
        finite_five_point_spatial_derivative_max=errors,
        analytic_q_U_max_error=analytic,
        jacobian_consistency_defect=jets['jacobian_consistency_defect'],
        independent_base_agreement=jets['independent_base_agreement'],
        affine_incidence_residual=float(np.max(abs(residual))),
        interior_Wilson_connection_incidence_defect=float(np.max(abs(interior_residual))),
        initial_subtracted_Wilson_connection_memory=float(np.max(abs(memory))),
        interior_incidence_defect_contains_initial_mismatch=True,
        induced_child_connection_norm=float(np.linalg.norm(child)),
        initial_bundle_spatial_jet_norm=float(np.linalg.norm(_initial(POINTS,rotated)[4])),
        retained_nonzero_time_connection=True,
        physical_history=False, physical_outgoing_E_B_derivative=False)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out', required=True);args=ap.parse_args()
    rows=[fixture_report(True),fixture_report(False)]
    result=dict(classification='CONDITIONAL_LOCAL_BIRTH_SPATIAL_ONE_JET_WITH_TWO_NONPHYSICAL_CONTROLS',
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        public_api_sha256=hashlib.sha256(Path(sys.modules[spatial_birth_map_one_jet.__module__].__file__).read_bytes()).hexdigest(),
        fixtures=rows,physical_primal_selected=False,
        physical_outgoing_derivative_gate_passed=False,coupled_corrections=0,
        muon_magnetic_moment=None,
        caution='Wilson interior evolution retains curvature; affine incidence is a separate same-E1 birth row.')
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(result,sort_keys=True))


if __name__=='__main__':
    main()
