"""Literal nonzero angular/connection controls for the frozen MP tensor audit."""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import sys
import numpy as np
import mpmath as mp

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'audits'))
import bhsm_changing_lorenz_tensor_precision_20261016 as owner

OWNER_SHA = 'a0fafae124d00be5954e0284fb2ed5891f645b4955af211a53a2e7494b39238a'


def execute(refinement, application, output):
    refinement, application, output = map(Path, (refinement, application, output))
    if output.exists():
        raise FileExistsError('Preserve previous controls')
    source = Path(owner.__file__)
    if sha256(source.read_bytes()).hexdigest() != OWNER_SHA:
        raise ValueError('Tensor owner changed')
    with np.load(application / 'changing_forms.npz', allow_pickle=False) as z:
        E = z['EW4_real_angular_derivatives'].copy()
    h, k = map(int, np.argwhere(E[0] != 0)[0])
    controls = [(40, 180), (20 + h, 180 + k), (40 + h, 820 + k)]
    inputs = {}
    records = []
    for side in ('incoming', 'outgoing'):
        p = refinement / f'{side}_radial32/forms.npz'
        inputs[f'{side}_radial32/forms.npz'] = sha256(p.read_bytes()).hexdigest()
        with np.load(p, allow_pickle=False) as z:
            ti, r = 6, 16
            A = z['A'][ti, r]
            metric = z['positive_metric'][ti, r]
            temporal = z['ghost_temporal_value_rate_second'][ti]
            radial = z['ghost_radial_value_rate_second'][r]
            u = z['temporal_u'][ti]
            tent = 2 * min(u / 1e-5, 1 - u / 1e-5)
        precision_records = []
        for dps in (80, 100):
            with mp.workdps(dps):
                tensors = owner.point_tensors(A, metric, temporal, radial, tent)
                for row, col in controls:
                    literal = owner.literal_entry(row, col, A, E, metric, temporal, radial, tent)
                    expanded = owner.tensor_entry(tensors, E, row, col)
                    g, ik = divmod(row, 80)
                    ii, hh = divmod(ik, 20)
                    block, jk = divmod(col, 80)
                    jj, kk = divmod(jk, 20)
                    left = mp.fsum(tensors['L'][g, block, a, ii, jj] * owner.number(E[a, hh, kk]) for a in range(3))
                    right = mp.fsum(tensors['R'][g, block, a, ii, jj] * owner.number(E[a, kk, hh]) for a in range(3))
                    precision_records.append(dict(dps=dps, row=row, column=col,
                        literal=mp.nstr(literal, 60), tensor=mp.nstr(expanded, 60),
                        absolute_error=mp.nstr(abs(literal - expanded), 8),
                        angular_left=mp.nstr(left, 60), angular_right=mp.nstr(right, 60)))
                if any(literal_record['literal'] == '0.0' for literal_record in precision_records):
                    raise ArithmeticError('Meaningful nonzero controls required')
        for i in range(len(controls)):
            if precision_records[i]['literal'] != precision_records[i + len(controls)]['literal']:
                raise ArithmeticError('Displayed MP80/100 point values did not agree')
        records.append(dict(side=side, time_index=ti, radial_index=r,
                            nonzero_connection_angular_and_mixed_controls=precision_records))
    result = dict(classification='LITERAL_NONZERO_ACTUAL_CONNECTION_ANGULAR_MIXED_TENSOR_CONTROLS',
        records=records, input_archive_sha256=inputs,
        owner_source_sha256=OWNER_SHA, control_source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        angular_input_archive_sha256=sha256((application / 'changing_forms.npz').read_bytes()).hexdigest(),
        physical_derivative_pass=False, fields_changed=False, coupled_corrections=0)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + '\n', encoding='utf8', newline='\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--refinement', required=True)
    parser.add_argument('--application', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    execute(args.refinement, args.application, args.output)
