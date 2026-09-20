"""Locate width in a retained, unresolved interval; never replace a frozen lemma."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
from flint import arb, arb_mat, ctx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from bhsm.interface.centered_causal_linear_defect import projected_row_bounds
from bhsm.interface.current_green_midpoint_coordinate_error import _float_upper


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def evaluate(root, index, out):
    if index == 13:
        raise ValueError('Interval 13 is frozen and excluded from this diagnostic')
    ctx.prec = 512
    base = root/'artifacts/flagship_integration'
    folder = base/f'.uniform_physical_local_defect_work/interval_{index:03d}'
    record_path, data = folder/'record.json', folder/'blocks.npz'
    record = json.loads(record_path.read_bytes())
    if record['interval'] != index or sha(data) != record['data_SHA256']:
        raise ValueError('Retained interval operand required')
    axes_path = root/'artifacts/action_extension/BHSM_AE4_CURRENT_C2_GREEN_IMAGE_PARTITION_RECONCILIATION.npz'
    radius_path = base/'BHSM_N12_GATE7_PHYSICAL_INCIDENCE_CAUSAL_ENVELOPE.json'
    with np.load(axes_path) as z:
        axes = z['current_center_green_image_unit_mid'].copy()
    axes[1:] /= np.linalg.norm(axes[1:], axis=1)[:, None]
    axes[0] = 0
    axis_sha = hashlib.sha256(np.asarray(axes, dtype='<f8').tobytes()).hexdigest().upper()
    if axis_sha != record['axes_SHA256']:
        raise ValueError('Unchanged retained axes required')
    radii = json.loads(radius_path.read_bytes())['stored_polynomial_adjudication']['witness']['radius']
    outputs = []
    with np.load(data, allow_pickle=False) as z:
        for side, node in (('DL', index), ('DR', index+1)):
            mids, rads = z[f'{side}_mid_q'], z[f'{side}_rad_q']
            values = [arb(str(m))+arb(0, arb(str(r)))
                      for m, r in zip(mids.flat, rads.flat, strict=True)]
            matrix = arb_mat(74, 74, values)
            majorant = projected_row_bounds(matrix, [axes[node]], axes[index+1])
            rows = [_float_upper(sum(arb(v)*arb(r) for v, r in zip(row, radii))/arb(radii[i]))
                    for i, row in enumerate(majorant)]
            width = [[abs(arb(str(rads[i,j]))).upper() for j in range(74)] for i in range(74)]
            ranked = sorted(((width[i][j], i, j) for i in range(74) for j in range(74)),
                            key=lambda item: float(item[0]), reverse=True)[:8]
            outputs.append(dict(side=side, input_node=node,
                retained_box_projected_majorant_upper=majorant,
                retained_box_weighted_rows_upper=rows,
                largest_entry_radii=[dict(output_coordinate=i, input_coordinate=j,
                    radius_upper=_float_upper(value)) for value, i, j in ranked]))
    payload = dict(algorithm='UNRESOLVED_HISTORY_INTERVAL_WIDTH_DIAGNOSTIC_V1',
        interval=index, original_radii=radii, outputs=outputs,
        scope='DIAGNOSIS_OF_OLD_COORDINATE_ENCLOSURE_ONLY',
        no_structured_certificate_replaced=True, local_interval_13_reopened=False,
        physical_inequality_violation_proved=False, Gate7_closed=False,
        source_SHA256={str(p.resolve()):sha(p) for p in (record_path,data,axes_path,radius_path,Path(__file__))})
    with out.open('xb') as stream:
        stream.write((json.dumps(payload, sort_keys=True, indent=2)+'\n').encode())
    print(json.dumps(outputs, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--evidence-root', type=Path, required=True)
    parser.add_argument('--interval', type=int, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    evaluate(args.evidence_root.resolve(), args.interval, args.out)
