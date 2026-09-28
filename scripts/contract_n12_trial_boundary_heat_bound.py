"""Full-domain fixed-channel heat-pressure bounds at the current trial base."""
import argparse
import json
from pathlib import Path
import sys
from flint import arb, arb_mat, ctx

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'scripts')]
from evaluate_n12_gate7_current_contractions import packet, scalar, BASE
from checkpoint_n12_gate7_66d_tangent_binding import restore, digest, encoded
from differentiate_n12_gate7_fiber_constrained_center import save_arrays
from bhsm.interface.boundary_heat_moment import collar_weyl_upper, boundary_heat_moment_upper


def calculate(out, collar):
    ctx.prec = 512
    collar = collar.resolve()
    if out.exists(): raise ValueError('new output directory required')
    report, z = packet(collar)
    if report['status'] != 'CURRENT_RESET_COUPLED_TRIAL_C2_COLLAR_ENCLOSED':
        raise ValueError('current trial collar required')
    T = restore(z, 'proper_duration')[0, 0]
    V = restore(z, 'unit_scalar_gauge_potential_domain')[0, 0]
    W = restore(z, 'unit_Weyl_superpotential_domain')[0, 0]
    data = {}; arrays = {}
    for name, kind, value in [('HS_m1', 'scalar', V), ('gauge_m2', 'scalar', 4*V),
                              ('Weyl_n0_plus', 'product_Dirac', arb(3)*W/2),
                              ('Weyl_n0_minus', 'product_Dirac', arb(3)*W/2)]:
        upper = collar_weyl_upper(duration=T, coefficient_upper=value.upper(),
                                  spectral_shift=1, channel=kind)
        pressure = boundary_heat_moment_upper(weyl_shift_upper=upper, weyl_zero_lower=0,
                                              heat_length=1, spectral_shift=1)
        arrays[name+'_weyl_upper'] = arb_mat([[upper]])
        arrays[name+'_heat_pressure_upper'] = arb_mat([[pressure]])
        data[name] = dict(weyl_upper=scalar(upper), heat_pressure_upper=scalar(pressure),
                          heat_pressure_lower=0, channel=kind)
    z.close()
    out.mkdir(parents=True); save_arrays(out/'arrays.npz', arrays)
    sources = [Path(__file__), collar/'arrays.npz', collar/'report.json',
        ROOT/'src/bhsm/interface/boundary_heat_moment.py',
        ROOT/'src/bhsm/interface/aether_forward_scalar_weyl_enclosures.py',
        ROOT/'src/bhsm/interface/aether_forward_product_dirac_weyl_enclosures.py',
        ROOT/'theory/n12_joint_trial_operator_collar.md']
    result = dict(status='CURRENT_TRIAL_FIXED_CHANNEL_FULL_DOMAIN_HEAT_MOMENTS_BOUNDED',
        collar_SHA256=report['arrays_SHA256'], channels=data,
        operator_scope='Complete nonnegative C2 continuation with the current collar; not the truncated-collar spectrum',
        root_scope='Off-root current reset trial; nonzero event defect remains in KKT',
        heat_length=1, spectral_shift=1,
        assumed_new_far_boundary_condition=False, unknown_exterior_zeroed=False,
        formula='0<=H(1)<=0.5*(M(-1)-M(0))<=0.5*collar_trial_energy(-1)',
        all_angular_levels_summed=False, joint_incoming_arm_composed=False,
        retained_contacts_zeroed=False, retained_contacts_composed=False,
        signed_graded_force=None, amplitude_row=None, q66=None,
        qualification='A consumed complete-domain fixed-channel bound. Its width does not establish physical failure or certify the signed force.',
        source_SHA256={path.relative_to(ROOT).as_posix(): digest(path) for path in sources},
        arrays_SHA256=digest(out/'arrays.npz'), Gate7_closed=False, FULL_BHSM_COMPLETE=False)
    (out/'report.json').write_bytes(encoded(result))
    print(json.dumps({name: float(arrays[name+'_heat_pressure_upper'][0, 0].upper()) for name in data}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--collar', type=Path, required=True)
    a = parser.parse_args(); calculate(a.out, a.collar)
