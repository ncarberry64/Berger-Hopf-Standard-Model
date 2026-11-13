from pathlib import Path
import argparse
import json
from bhsm.interface.muon_mean_legendre_certificate import materialize_mean_legendre_application

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Apply and certify the actual restricted joint mean constitutive operator.')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--time-points', type=int, default=17)
    args = parser.parse_args()
    print(json.dumps(materialize_mean_legendre_application(args.output, time_points=args.time_points), sort_keys=True))
