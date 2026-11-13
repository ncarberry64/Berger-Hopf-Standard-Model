"""Bound a saved angular-response functional; no photon solve or F2 estimate.

G here is explicitly the FLAT REFERENCE gradient supplied by the component
owner.  Its nonzero functional is not a physical gauge-constraint failure.
"""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import sys


def functional_error_bound(gradient_norm_upper, residual_upper, coercivity_lower):
    """Propagate an existing equation certificate through a linear functional."""
    from flint import arb
    if not coercivity_lower > 0:
        raise ValueError('A strictly positive certified coercivity is required')
    residual_frobenius = sum((arb(float(x))**2 for x in residual_upper), arb(0)).sqrt()
    return gradient_norm_upper * residual_frobenius / coercivity_lower


def run(repository, output):
    import numpy as np
    from flint import acb, acb_mat, arb, ctx
    root, out = Path(repository).resolve(), Path(output).resolve()
    out.mkdir(parents=True, exist_ok=False)
    sys.path.insert(0, str(root/'src'))
    from bhsm.interface.muon_native_dirac_hamiltonian import lepton_current_hilbert_representation
    ctx.prec = 256
    pins = {}
    def read(path):
        pins[str(path)] = sha256(path.read_bytes()).hexdigest()
        if path.suffix == '.json':
            return json.loads(path.read_text(encoding='utf8'))
        with np.load(path, allow_pickle=False) as z:
            return {k:z[k].copy() for k in z.files}
    def matrix(x):
        return acb_mat([[acb(arb(float(v.real)), arb(float(v.imag))) for v in row] for row in np.asarray(x)])
    def norm(x):
        return sum((abs(x[i,j])**2 for i in range(x.nrows()) for j in range(x.ncols())), arb(0)).sqrt()
    def bounds(v):
        return {'ball':str(v), 'lower':float(np.nextafter(float(v.lower()), -np.inf)),
                'upper':float(np.nextafter(float(v.upper()), np.inf))}
    saved = root/'artifacts/muon_native_photon_response_20261006/run_1'
    manifest = read(saved/'output_hashes.json')
    a = read(saved/'component_action_and_current.npz')
    G = matrix(a['flat_reference_gradient'])
    Gdag = G.conjugate().transpose()
    gnorm = norm(G)
    Jb, C = matrix(a['dual_current_basis']), matrix(a['mode_current_covector'])
    source_functional = (Gdag*Jb)*C
    duality = matrix(a['source_inclusion']).conjugate().transpose()*(Jb*C)-C
    cases = []
    for i in range(3):
        z, cert = read(saved/f'response_{i}.npz'), read(saved/f'certificate_{i}.json')
        U = matrix(z['current_response'])
        functional = Gdag*U
        fnorm = norm(functional)
        error = functional_error_bound(gnorm.upper(), cert['current_residual_absolute_upper'], arb(float(cert['coercivity_lower'])))
        lower = fnorm.lower()-error.upper()
        if not lower > 0:
            raise ArithmeticError('The saved certificate does not separate the flat-reference functional from solve error')
        cases.append(dict(case=i, stored_response_flat_reference_functional_norm=bounds(fnorm),
            exact_component_response_functional_difference_upper=bounds(error),
            exact_component_response_functional_norm_strict_lower=bounds(lower),
            relative_stored_functional_norm=bounds(fnorm/(gnorm*norm(U))),
            existing_coercivity_lower=cert['coercivity_lower'],
            theorem='||G_flat^dagger u_exact||_F >= ||G_flat^dagger U_saved||_F - ||G_flat||_F sqrt(sum_j rho_j^2)/alpha',
            scope='Exact frozen shifted angular matrix and exact Jbasis*C right side only; existing certificate retains post-solve product rounding'))
    # Check every consumed historical result against its already-published hash.
    for path, digest in list(pins.items()):
        p = Path(path)
        if p.name in manifest and digest != manifest[p.name]:
            raise ValueError('Historical photon output changed: '+str(p))
    magnetic = read(root/'artifacts/muon_continued_current_factor_20261011/run_1/incoming_16.npz')
    rep = lepton_current_hilbert_representation()
    fi = magnetic['family_indices'][1]
    expected = -rep['EM_charge'][np.ix_(fi,fi)]
    checks = dict(source_charge_map_max=float(np.max(abs(magnetic['source_right_map']-expected))),
        target_charge_map_max=float(np.max(abs(magnetic['target_left_map']-expected))),
        reverse_Xi0_literal_transpose_max=float(np.max(abs(magnetic['magnetic_reverse_Xi0']-magnetic['magnetic_Xi0'].swapaxes(-1,-2)))),
        reverse_Xi1_literal_transpose_max=float(np.max(abs(magnetic['magnetic_reverse_Xi1']-magnetic['magnetic_Xi1'].swapaxes(-1,-2)))),
        inactive_source_axes_Xi0_max=float(np.max(abs(magnetic['magnetic_Xi0'][:,3:]))),
        inactive_source_axes_Xi1_max=float(np.max(abs(magnetic['magnetic_Xi1'][:,3:]))))
    if any(v != 0 for v in checks.values()):
        raise ArithmeticError('Saved canonical magnetic/current convention changed')
    for name in ('muon_native_photon_response.py','muon_continued_current_factor.py','muon_magnetic_open_lepton_vertex.py','muon_native_dirac_hamiltonian.py'):
        p=root/'src/bhsm/interface'/name; pins[str(p)]=sha256(p.read_bytes()).hexdigest()
    pins[str(Path(__file__).resolve())]=sha256(Path(__file__).read_bytes()).hexdigest()
    result = dict(classification='CERTIFIED_FLAT_REFERENCE_FUNCTIONAL_OF_AVAILABLE_ANGULAR_RESPONSE_ONLY',
        precision_bits=256, inputs=pins,
        actual_current=dict(shape=list(a['reached_current_dual'].shape), mode_covector_shape=list(a['mode_current_covector'].shape),
            construction='C=f_R*Gamma_bar_complete; J=S*(S^dagger*S)^(-1)*C; all 56x4 connected fermion labels retained',
            actual_dual_pairing_defect=bounds(norm(duality)), flat_reference_source_functional_norm=bounds(norm(source_functional)),
            scope='Available angular geometric dual extension at its saved cut; temporal/radial/native current components remain unevaluated'),
        flat_reference_gradient_shape=list(a['flat_reference_gradient'].shape),
        response_checks=cases,
        magnetic=dict(checks=checks, family_indices=fi.tolist(), Xi0_shape=list(magnetic['magnetic_Xi0'].shape),
            active_Xi0_norm=float(np.linalg.norm(magnetic['magnetic_Xi0'][:,:3])),
            active_Xi1_norm=float(np.linalg.norm(magnetic['magnetic_Xi1'][:,:3])),
            convention='Canonical deltaH=deltaW-i*deltaOmega_tau; temporal At=-iG/N; source=-Q; no second electric charge; reverse is literal transpose',
            domain='Retained C6 finite proper-clock current, fixed initial/free final trace, all eight source and twenty angular coefficient slots'),
        conclusion='The unconstrained angular inverse cannot be identified with an inverse restricted to ker(G_flat^dagger). This nonzero functional may be a correct coupled/background response; no physical quotient failure is claimed and nothing is projected out.',
        missing_maps=[
            'Actual background-dependent BRST/Gauss constraint and trace inclusion I_Q, adjoint/Gram, and completed same-owner photon form K_0,Q on its physical domain; G_flat is not that map.',
            'Same-owner completion R_ind on reached current and response directions, temporal/radial/source/domain/contact terms, and supplied native spectral length/normalization; unavailable terms are not zero.',
            'Action-owned transport/inclusion identifying the retained 240x224 angular dual and finite-time C6 magnetic/source jets on ONE background/domain; no dimension-based composition of these distinct saved epochs.',
            'Physical muon inverse two-point pole, left/right external injections and spectral residue, then normalized electromagnetic soft vertex/Pauli projection. The saved magnetic deltaH is an operand, not F2.'],
        physical_F2=None, physical_a_mu=None, physical_derivative_admitted=False,
        new_photon_solves=0, old_integrations_restarted=0,
        guard_interpretation='The positive functional lower bounds certify arithmetic separation from existing solve error, not a new physical acceptance threshold')
    (out/'result.json').write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8')
    print(json.dumps({'result':str(out/'result.json'),'sha256':sha256((out/'result.json').read_bytes()).hexdigest(),
        'strict_functional_lower':[v['exact_component_response_functional_norm_strict_lower']['lower'] for v in cases]}))


if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('--repository',required=True);p.add_argument('--output',required=True)
    args=p.parse_args();run(args.repository,args.output)
