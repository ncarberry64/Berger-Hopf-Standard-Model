"""Executed constitutive applications for the source-paired mean descriptor.

The prescribed-wall restriction comes from the same finite Dirichlet
source core. The certificate concerns exact stored binary64 matrices,
not a stationary physical base or a continuum error bound.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

import numpy as np


def prescribed_wall_mean_restriction(coordinates):
    """Restrict the affine source's second wall trace, retaining its reactions."""
    if (coordinates['x_count'], coordinates['v_count'], coordinates['y_count']) != (90, 90, 36):
        raise ValueError('the retained x90/v90/y36 mean representation is required')
    labels = coordinates['raw_gauge_labels']
    dynamic = coordinates['dynamic_gauge_indices']
    algebraic = coordinates['At_indices']
    wall_x = np.array([38+j for j, i in enumerate(dynamic) if labels[int(i)]['wall_lift']], int)
    wall_y = np.array([24+j for j, i in enumerate(algebraic) if labels[int(i)]['wall_lift']], int)
    if len(wall_x) != 16 or len(wall_y) != 4:
        raise ValueError('literal sixteen dynamic and four At wall lifts are required')
    x = np.setdiff1d(np.arange(90), wall_x)
    y = np.setdiff1d(np.arange(36), wall_y)
    lift = np.eye(216)[:, np.r_[x, 90+x, 180+y]]
    return dict(x_indices=x, y_indices=y, wall_x_indices=wall_x,
                wall_y_indices=wall_y, full_to_restricted_lift=lift,
                x_count=len(x), y_count=len(y),
                restriction_owner='same prescribed raw-beta Dirichlet source core: affine boundary trace has zero second partial at fixed core',
                wall_reaction_rows_discarded=False, gauge_pseudoinverse_used=False)


def certify_frozen_legendre_application(matrix, source, *, precision_bits=192):
    """Apply D X=-source and bound the exact stored linear error with Arb.

    No positivity, gauge quotient, or physical stationarity is assumed.
    A verified ||I-QD||_F<1 establishes invertibility. Then
    ||X-X_exact||_F <= ||D^-1||_2 ||DX+source||_F.
    Numerical sign diagnostics refer to a balanced congruence only.
    """
    from flint import arb, arb_mat, ctx

    D, B = np.asarray(matrix, float), np.asarray(source, float)
    if (D.ndim != 2 or D.shape[0] != D.shape[1] or not len(D)
            or B.ndim != 2 or B.shape[0] != len(D)
            or not np.isfinite(D).all() or not np.isfinite(B).all()
            or not np.array_equal(D, D.T)):
        raise ValueError('finite exactly symmetric stored D and column source required')
    if type(precision_bits) is not int or precision_bits < 96:
        raise ValueError('at least96 bits of outward arithmetic required')
    row = np.max(abs(D), axis=1)
    if np.any(row == 0):
        raise ArithmeticError('unbound constitutive row; no regularizer is introduced')
    scale = 1/np.sqrt(row)
    balanced = scale[:, None]*D*scale[None, :]
    try:
        inverse = np.linalg.solve(balanced, np.eye(len(D)))
    except np.linalg.LinAlgError as error:
        raise ArithmeticError('singular frozen constitutive matrix') from error
    Q = scale[:, None]*inverse*scale[None, :]
    X = -scale[:, None]*np.linalg.solve(balanced, scale[:, None]*B)
    eigenvalues, eigenvectors = np.linalg.eigh((balanced+balanced.T)/2)
    old_precision = ctx.prec
    ctx.prec = precision_bits
    try:
        def balls(value):
            return arb_mat([[arb(float(v)) for v in r] for r in value])
        def norm(value):
            return sum((value[i, j]**2 for i in range(value.nrows())
                        for j in range(value.ncols())), arb(0)).sqrt()
        def upper(value):
            return float(np.nextafter(float(value.upper()), np.inf))
        DD, QQ, XX, BB = map(balls, (D, Q, X, B))
        VV = balls(eigenvectors)
        orthogonal_defect = norm(VV.transpose()*VV-balls(np.eye(len(D))))
        SS = balls(np.diag(scale))
        congruence_error = norm(VV.transpose()*SS*DD*SS*VV-balls(np.diag(eigenvalues)))
        gap = arb(float(np.min(abs(eigenvalues))))
        inertia_certified = bool(orthogonal_defect < 1 and congruence_error < gap)
        defect = norm(balls(np.eye(len(D)))-QQ*DD)
        if not defect < 1:
            raise ArithmeticError('constitutive inverse fails verified Neumann test')
        inverse_bound = norm(QQ)/(1-defect)
        residual = norm(DD*XX+BB)
        certificate = dict(precision_bits=precision_bits,
            Neumann_defect_upper=upper(defect),
            inverse_operator_norm_upper=upper(inverse_bound),
            linear_residual_Frobenius_upper=upper(residual),
            source_Frobenius_upper=upper(norm(BB)),
            response_error_Frobenius_upper=upper(inverse_bound*residual),
            exact_input_convention='each stored binary64 matrix/source entry is an exact real number',
            matrix_invertibility_certified=True,
            numerical_sign_counts=dict(positive=int(np.sum(eigenvalues > 0)),
                negative=int(np.sum(eigenvalues < 0)), zero=int(np.sum(eigenvalues == 0))),
            numerical_sign_counts_are_certificates=False,
            exact_stored_inertia_certified=inertia_certified,
            inertia_congruence_defect_upper=upper(congruence_error),
            eigenvector_Gram_defect_upper=upper(orthogonal_defect),
            inertia_reference_gap=float(np.min(abs(eigenvalues))),
            certified_sign_counts=(dict(positive=int(np.sum(eigenvalues > 0)),
                negative=int(np.sum(eigenvalues < 0)), zero=0) if inertia_certified else None),
            balanced_condition_number=float(np.linalg.cond(balanced)),
            balanced_smallest_singular_value=float(np.linalg.svd(balanced, compute_uv=False)[-1]),
            positive_action_assumed=False, regularizing_shift=0.,
            producer_rounding_or_continuum_error_enclosed=False)
    finally:
        ctx.prec = old_precision
    return dict(response=X, inverse_preconditioner=Q, certificate=certificate)


def materialize_mean_legendre_application(output, *, time_points=17, repository=None):
    """Evaluate the actual joint mean action and all64 paired source columns."""
    from .muon_parent_mean_causal_action import mean_action_family, local_mean_action, ROOT
    from .muon_parent_gauge_geometry_correction import _deterministic_npz

    root = Path(ROOT if repository is None else repository)
    target = Path(output)
    if not target.is_absolute():
        target = root/target
    if target.exists():
        raise FileExistsError('preserve previous applications; use a new output directory')
    if type(time_points) is not int or time_points < 3:
        raise ValueError('at least three actual descriptor samples required')
    family = mean_action_family(root)
    restriction = prescribed_wall_mean_restriction(family['coordinates'])
    x, y = restriction['x_indices'], restriction['y_indices']
    files = dict(family['source_receipt']['input_hashes'])
    for name in ('src/bhsm/interface/muon_parent_mean_causal_action.py',
                 'src/bhsm/interface/muon_mean_legendre_certificate.py'):
        files[name] = sha256((root/name).read_bytes()).hexdigest()
    times = np.linspace(0., family['length'], time_points)
    records, matrices, sources, responses, preconditioners = [], [], [], [], []
    wall_loads, base_constraints, symmetry_defects = [], [], []
    action_hessians, action_gradients, action_sources = [], [], []
    for time in times:
        action = local_mean_action(time, family)
        action_hessians.append(action['hessian']); action_gradients.append(action['gradient'])
        action_sources.append(np.concatenate((action['Jx'], action['Jv'], action['Jy'])))
        raw = np.block([[action['Lvv'][np.ix_(x, x)], action['Lvy'][np.ix_(x, y)]],
                        [action['Lyv'][np.ix_(y, x)], action['Lyy'][np.ix_(y, y)]]])
        # Hessian symmetry is an exact action identity. Retain the computed
        # antisymmetric rounding defect separately from the frozen symmetric D.
        D = (raw+raw.T)/2
        B = np.concatenate((action['Jv'][x], action['Jy'][y])).reshape(len(D), 64)
        result = certify_frozen_legendre_application(D, B)
        matrices.append(D); sources.append(B); responses.append(result['response'])
        preconditioners.append(result['inverse_preconditioner'])
        symmetry_defects.append(np.linalg.norm(raw-raw.T))
        wall_loads.append(np.concatenate((action['Jx'][restriction['wall_x_indices']],
                                         action['Jy'][restriction['wall_y_indices']])))
        base_constraints.append(action['constraint_base'])
        records.append(dict(time=float(time), **result['certificate']))
    for name, digest in files.items():
        if sha256((root/name).read_bytes()).hexdigest() != digest:
            raise RuntimeError('consumed action source changed during mean constitutive application: '+name)
    arrays = dict(times=times, restricted_legendre_matrices=np.array(matrices),
        paired_constitutive_sources=np.array(sources), particular_responses=np.array(responses),
        inverse_preconditioners=np.array(preconditioners), wall_reaction_source_rows=np.array(wall_loads),
        total_assigned_base_constraints=np.array(base_constraints),
        raw_Hessian_antisymmetry_norm=np.array(symmetry_defects), x_indices=x, y_indices=y,
        wall_x_indices=restriction['wall_x_indices'], wall_y_indices=restriction['wall_y_indices'])
    target.mkdir(parents=True)
    _deterministic_npz(target/'application.npz', arrays)
    _deterministic_npz(target/'action_samples.npz', dict(times=times,
        master_hessians=np.array(action_hessians), master_gradients=np.array(action_gradients),
        master_source_cotangents=np.array(action_sources),
        full_to_restricted_lift=restriction['full_to_restricted_lift']))
    receipt = dict(scope='EVALUATED_JOINT_MEAN_CONSTITUTIVE_ACTION_COMPONENT',
        application_sha256=sha256((target/'application.npz').read_bytes()).hexdigest(),
        action_samples_sha256=sha256((target/'action_samples.npz').read_bytes()).hexdigest(),
        samples=records, input_hashes=files,
        source_receipt_sha256=family['source_receipt_sha256'],
        restriction_owner=restriction['restriction_owner'],
        consumer='same-action causal n0 descriptor constitutive block for v74 and algebraic y32',
        equation='D*[v,y]=- [Jv,Jy] at x=p=0; a particular constitutive component, not the time-evolved mean response',
        total_wall_reaction_rows=20, wall_reactions_exported=True,
        physical_birth_base_or_domain_selected=False, causal_mean_response_solved=False,
        native_mean_heat_contact_evaluated=False, complete_observable=False,
        error_scope='Arb bounds exact stored constitutive matrices and source columns only; action producer rounding, off-shell base, time/radial discretization, and observable errors excluded')
    (target/'result.json').write_text(json.dumps(receipt, sort_keys=True, indent=2, allow_nan=False)+'\n',
        encoding='utf8', newline='\n')
    return receipt
