"""Area-source application at a positive, solved represented endpoint.

The retained analytic source and implicit cotangent derivative apply at
the consumed base. Only the finite parameter check is generalized here:
the trial coefficient is gamma_base + step, rather than step. No length,
physical normal mode or formation drive is inferred from this derivative.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import numpy as np

from .muon_parent_gauge_geometry_correction import ROOT, STATE_SOURCE
from .muon_birth_reset_evaluation import NORMALIZATION_SOURCE
from .muon_birth_finite_normal_phase import load_finite_normal_endpoint
from .muon_birth_area_endpoint_response import area_endpoint_parameter_application
from .muon_birth_finite_geometric_trace_endpoint import moving_endpoint_rows
from .muon_birth_phase_continuation import _compressed_npz


def positive_parameter_checks(base_gamma, residual, source, evaluate, steps):
    """Compare the exact owned source with increments about its SAME base.

    ``evaluate(gamma)`` holds the endpoint coefficients fixed and returns
    the full represented action rows. These are producer diagnostics,
    not rigorous derivative or nonlinear solution error bounds.
    """
    if not np.isfinite(base_gamma) or base_gamma <= 0:
        raise ValueError('actual positive base area coefficient required')
    r = np.asarray(residual, float); f = np.asarray(source, float)
    if r.shape != f.shape or not np.isfinite(r).all() or not np.isfinite(f).all():
        raise ValueError('finite same-row base residual and parameter source required')
    result = []
    for step in steps:
        h = float(step)
        if not np.isfinite(h) or h == 0 or base_gamma + h <= 0:
            raise ValueError('nonzero increment within positive area domain required')
        trial = np.asarray(evaluate(base_gamma+h), float)
        if trial.shape != r.shape or not np.isfinite(trial).all():
            raise ValueError('finite full action rows on identical coordinates required')
        derivative = (trial-r)/h
        result.append(dict(base_gamma=float(base_gamma), step=h,
            trial_gamma=float(base_gamma+h), derivative_norm=float(np.linalg.norm(derivative)),
            source_difference_norm=float(np.linalg.norm(derivative-f))))
    return result


def positive_area_endpoint_parameter_application(base_directory, *, repository=ROOT,
                                                 difference_steps=(1e-4, 5e-5)):
    """Apply the owned area derivative and coupled row correction at gamma>0."""
    root = Path(repository)
    loaded = load_finite_normal_endpoint(base_directory, side='incoming', repository=root)
    receipt = loaded['receipt']; source = loaded['source']; rep = loaded['representation']
    gamma = receipt['action_parameters']['surface_gamma']
    if gamma is None or not np.isfinite(gamma) or gamma <= 0:
        raise ValueError('positive solved area member required')
    # The analytic producer is unchanged. Its historical zero-base
    # finite checks are deliberately not invoked on a positive member.
    result = area_endpoint_parameter_application(base_directory, repository=root, difference_steps=())
    with np.load(source/'application.npz', allow_pickle=False) as z:
        raw = z['updated_raw_pair'].copy(); reference = z['reference_raw_pair'].copy()
        residual = z['updated_residual'].copy()
    with np.load(root/STATE_SOURCE, allow_pickle=False) as z: weights = z['state_weights'].copy()
    with np.load(root/NORMALIZATION_SOURCE, allow_pickle=False) as z: normalization = z['normalization_coordinates'].copy()
    parameters = dict(receipt['action_parameters'])
    def evaluate(trial_gamma):
        rep['endpoint_action_parameters'] = dict(parameters, surface_gamma=float(trial_gamma))
        return moving_endpoint_rows(raw, reference, rep, weights, normalization,
                                    compute_cotangent_derivative=False)['residual']
    result['finite_parameter_checks'] = positive_parameter_checks(
        gamma, residual, result['area_parameter_source'], evaluate, difference_steps)
    result['base_gamma'] = float(gamma)
    result['analytic_core_owner'] = 'muon_birth_area_endpoint_response.area_endpoint_parameter_application'
    result['same_base_parameter_increment'] = True
    return result


def materialize_positive_area_endpoint_parameter(base_directory, output, *, repository=ROOT):
    root = Path(repository); out = Path(output); out = out if out.is_absolute() else root/out
    if out.exists(): raise FileExistsError('preserve earlier positive parameter applications')
    a = positive_area_endpoint_parameter_application(base_directory, repository=root)
    arrays = {k:v for k,v in a.items() if isinstance(v, np.ndarray)}
    arrays.update({'response_'+k:v for k,v in a['response'].items() if isinstance(v,np.ndarray)})
    out.mkdir(parents=True); _compressed_npz(out/'application.npz', arrays)
    refs = dict(a['input_hashes'])
    for name in ('muon_positive_area_endpoint_response','muon_birth_area_endpoint_response',
                 'muon_birth_finite_normal_phase','muon_magnetic_birth_ward_mean'):
        p = 'src/bhsm/interface/'+name+'.py'; refs[p] = sha256((root/p).read_bytes()).hexdigest()
    md = dict(classification='EVALUATED_POSITIVE_BASE_OWNED_AREA_SOURCE_AND_ENDPOINT_RESPONSE',
        input_hashes=refs, numerical_sha256=sha256((out/'application.npz').read_bytes()).hexdigest(),
        base_gamma=a['base_gamma'], analytic_core_owner=a['analytic_core_owner'],
        same_base_parameter_increment=True, finite_parameter_checks=a['finite_parameter_checks'],
        source_norm=float(np.linalg.norm(a['area_parameter_source'])),
        raw_response_norm=float(np.linalg.norm(a['raw_parameter_response'])),
        original_row_residual_norm=float(np.linalg.norm(a['response']['original_residual'])),
        arithmetic_certificate=a['response']['stored_action_arithmetic_certificate'],
        gamma_law=a['gamma_law'], alpha_EM_substituted=False,
        physical_formation_or_cutoff_or_Pauli_selected=False,
        error_scope='Arb encloses exact stored row/source arithmetic; action producer rounding and finite-parameter diagnostics are not rigorously enclosed')
    (out/'result.json').write_text(json.dumps(md,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return md


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--base-directory',required=True,type=Path)
    p.add_argument('--output',required=True,type=Path)
    a = p.parse_args()
    print(json.dumps(materialize_positive_area_endpoint_parameter(a.base_directory,a.output),sort_keys=True))
