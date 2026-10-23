"""Named central gauge compatibility on an evaluated complex child252 action."""
from hashlib import sha256
import argparse
import json
from pathlib import Path
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
sys.path.insert(0, str(ROOT/'scripts'))
from evaluate_muon_continued_current_factor import retained_input
from bhsm.interface.muon_birth_trace_enriched_action import generic_coordinate_lift
from bhsm.interface.muon_trace_enriched_charged_current_response import enriched_central_profiles
from bhsm.interface.muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation


def application(terminal):
    pins = {}
    phase, _ = retained_input('outgoing', pins)
    rep = phase['representation']
    coordinates = generic_coordinate_lift(rep['gauge_labels'])
    n, m = coordinates['x_count'], coordinates['y_count']
    path = ROOT/terminal
    pins[path.relative_to(ROOT).as_posix()] = sha256(path.read_bytes()).hexdigest()
    with np.load(path, allow_pickle=False) as a:
        raw = a['raw_fields']; H = a['action_hessian']; g = a['action_gradient']
    if raw.shape != (268,) or H.shape != (252,252) or g.shape != (252,):
        raise ValueError('complete actual raw268/master252 action required')
    profiles = enriched_central_profiles(rep)
    theta, radial = profiles['theta_coefficients'], profiles['radial_derivative_coefficients']
    labels = rep['gauge_labels']
    at = np.array([j for j,i in enumerate(coordinates['At_indices']) if labels[i]['internal']==3])
    ar = np.array([j for j,i in enumerate(coordinates['dynamic_gauge_indices'])
                   if labels[i]['field']=='A_rho' and labels[i]['internal']==3])
    if len(at)!=4 or len(ar)!=4:
        raise ValueError('all original enriched central profiles required')
    Z = np.zeros((n+m,2),complex)
    Z[38+ar] = radial
    Z[n+24+at] = theta
    wall = rep['wall_trace_map'][0,3,coordinates['At_indices'][at]]@theta
    generator = higgs_u2_real_representation()['real_generators'][3]
    Z[n-4:n] = -np.outer(generator@raw[-8:-4],wall)
    K = H[n:,n:]
    residual = np.r_[np.zeros(n),g[2*n:]]
    for rel in ('scripts/evaluate_muon_holomorphic_child_ward_review.py',
                'src/bhsm/interface/muon_trace_enriched_charged_current_response.py',
                'src/bhsm/interface/muon_intrinsic_higgs_gauge_action.py'):
        pins[rel] = sha256((ROOT/rel).read_bytes()).hexdigest()
    return dict(classification='EVALUATED_NAMED_CENTRAL_WARD_COMPATIBILITY_ON_COMPLEX_TERMINAL',
        legendre_dimension=n+m,named_generators=2,input_hashes=pins,
        Hessian_Ward_image_max=float(np.max(abs(K@Z))),
        action_Ward_pairing_max=float(np.max(abs(Z.T@g[n:]))),
        target_Pi_Ward_pairing_max=float(np.max(abs(Z[:n].T@g[n:2*n]))),
        same_x_same_Pi_initial_residual_named_compatibility_max=float(np.max(abs(Z.T@residual))),
        original_algebraic_residual_max=float(np.max(abs(g[2*n:]))),
        generator_equation='delta At=theta; delta Ar_dot=theta_r; delta H_dot=-G_Y H theta_wall',
        additional_numerical_nulls_deleted=False,
        physical_stationarity_or_compatibility_error_certified=False,
        scope='Binary64 stored full action application; exact named gauge identities only. '
              'The two generators do not remove the independent multiplier residual.')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--terminal',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args(); out=ROOT/a.output
    if out.exists():
        raise FileExistsError('preserve every independent Ward application')
    md=application(a.terminal)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(md,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
    print(json.dumps({k:v for k,v in md.items() if k!='input_hashes'},sort_keys=True))
