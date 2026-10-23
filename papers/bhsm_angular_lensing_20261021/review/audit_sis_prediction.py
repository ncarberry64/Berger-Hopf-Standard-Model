"""Independent units, stationary-variation and diagonal-map SIS checks.

Run from any working directory. This audit reads the saved temporal/strong-
lens outputs and independently reconstructs the physical SIS delay in SI
units. It also compares the reduced derivative with the original three-term
Fermat variation, including symmetric non-diagonal map probes.
"""
from pathlib import Path
import json
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'code'))
import strong_lensing_prediction as lens


def independent_delay_seconds(z_l, d_l, d_s, source_kpc=.8, sigma_km_s=200.):
    # Direct physical expression: 2(1+z_l)b*s*(D_l/D_s)/c.
    # No H0 scale appears after fixing physical source displacement s.
    c = 299792458.
    source_m = source_kpc * 3.085677581491367e19
    physical_deflection = 4*np.pi*(sigma_km_s*1000/c)**2
    return 2*(1+z_l)*physical_deflection*source_m*(d_l/d_s)/c


def original_fermat_derivative(p, baseline, matrices):
    """Unreduced variation with metric, source and impact terms separate."""
    A, B, C = matrices
    beta = np.asarray(baseline['beta_radian'])
    delta_T = p.T0*(A.T-C+B)
    delta_beta = -B@beta
    values = []
    terms = []
    for image in baseline['images']:
        theta = np.asarray(image['theta_radian'])
        v = theta-beta
        impact = p.d_ol*theta
        alpha_hat = p.b*impact/np.linalg.norm(impact)
        pieces = [float(.5*v@delta_T@v),
                  float(-p.T0*v@delta_beta),
                  float(-(1+p.z_l)*alpha_hat@(p.d_ol*A@theta))]
        values.append(sum(pieces))
        terms.append(pieces)
    return (values[1]-values[0])*p.seconds_per_length, terms


def main():
    saved = json.loads((ROOT/'artifacts/lensing/nodal_sis_prediction.json').read_text())
    temporal = json.loads((ROOT/'artifacts/temporal/angular_response.json').read_text())
    reports = []
    max_units = 0.
    max_original = 0.
    max_linear = 0.
    max_axes = 0.
    # Independent symmetric probes include off-diagonal shear and trace terms.
    # At first order about isotropic maps these retain a symmetric delta T.
    probes = [
        [np.array([[.7,.2],[.2,-.1]]),np.array([[.3,-.4],[-.4,.6]]),np.array([[.2,.1],[.1,.5]])],
        [np.zeros((2,2)),np.zeros((2,2)),np.array([[.8,-.3],[-.3,-.2]])],
        [np.array([[0.,1.],[1.,0.]]),np.zeros((2,2)),np.zeros((2,2))],
    ]
    for record, output in zip(temporal['configurations'], saved['configurations']):
        p = lens.from_record(record)
        direct = independent_delay_seconds(p.z_l,p.d_ol,p.d_os)
        units_error = abs(direct-output['baseline_delay_seconds'])/direct
        max_units = max(max_units,units_error)
        g_l = np.array(record['segments']['ol']['g_per_physical_anchor'])
        g_s = np.array(record['segments']['os']['g_per_physical_anchor'])
        q = np.array(saved['preparation']['illustrative_state'])
        kernel = np.sqrt(2)*(g_s-g_l)
        angles = []
        maps = lens.state_maps(p,record['segments'],q)
        for row in output['illustrative_angular_response']:
            alpha = np.deg2rad(row['source_azimuth_deg'])
            prediction = direct*np.dot(kernel,q)*np.cos(2*alpha)
            error = abs(prediction-row['linear_delta_delay_seconds'])
            max_linear = max(max_linear,error)
            angles.append({'azimuth_deg':row['source_azimuth_deg'],
                           'independent_linear_seconds':float(prediction),
                           'saved_difference_seconds':float(error)})
        zero = [d*np.eye(2) for d in [p.d_ol,p.d_os,p.d_ls]]
        derivative_checks = []
        for alpha in [0.,.23,.71,1.24]:
            base = lens.solve_images(p,zero,alpha)
            for probe_index, matrices in enumerate(probes):
                original, pieces = original_fermat_derivative(p,base,matrices)
                reduced = lens.full_delay_derivative(p,base,matrices)
                e = np.array([np.cos(alpha),np.sin(alpha)])
                analytic = direct*e@(matrices[0]-matrices[1])@e
                error = max(abs(original-reduced),abs(original-analytic))/direct
                max_original = max(max_original,error)
                derivative_checks.append({'azimuth_radian':alpha,'probe_index':probe_index,
                    'unreduced_derivative_seconds':float(original),
                    'reduced_derivative_seconds':float(reduced),
                    'independent_SIS_derivative_seconds':float(analytic),
                    'relative_to_background_delay_error':float(error),
                    'separate_fermat_terms_per_image':pieces})
        axis_checks = []
        for axis, alpha in [(0,0.),(1,np.pi/2)]:
            # Exact diagonal-map SIS result: Delta t/Delta t0 =
            # (D_ol,axis/d_ol)/(D_os,axis/d_os). D_ls cancels identically.
            exact = direct*(maps[0][axis,axis]/p.d_ol)/(maps[1][axis,axis]/p.d_os)
            numerical = lens.solve_images(p,maps,alpha)['delay_seconds']
            error = abs(numerical-exact)/direct
            max_axes = max(max_axes,error)
            axis_checks.append({'axis':axis,'exact_completed_delay_seconds':float(exact),
                                'numerical_completed_delay_seconds':float(numerical),
                                'relative_to_background_delay_error':float(error)})
        reports.append({'z_l':p.z_l,'z_s':p.z_s,'independent_delay_seconds':float(direct),
                        'SI_units_relative_error':float(units_error),
                        'linear_angle_checks':angles,'unreduced_derivative_checks':derivative_checks,
                        'exact_diagonal_map_checks':axis_checks})
    result = {'schema':'BHSM-SIS-INDEPENDENT-REVIEW-V1',
              'scope':'units and full first-order Fermat response; conditional model, no observational admission',
              'checks':{'max_SI_units_relative_error':max_units,
                        'max_unreduced_variation_error_per_baseline_delay':max_original,
                        'max_saved_linear_delay_error_seconds':max_linear,
                        'max_exact_diagonal_completion_error_per_baseline_delay':max_axes},
              'configurations':reports,
              'finite_completion_limit':'Finite diagonal ratios are exact for the chosen map completion, not an action-derived nonlinear metric.'}
    assert max_units < 1e-13
    assert max_original < 1e-12
    assert max_linear < 1e-12
    assert max_axes < 1e-13
    (ROOT/'review/sis_independent_review.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps(result['checks'],indent=2))


if __name__ == '__main__':
    main()
