"""Integrate paired primal-refined derivatives in the frozen HS local operator."""
import os
for key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[key] = '1'
from copy import deepcopy
import json
from pathlib import Path
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'scripts')]
import certify_n12_gate7_preconditioned_uniform_physical_local_defects as base
import certify_n12_gate7_coupled_endpoint_uniform_derivatives as endpoint
import certify_n12_gate7_coupled_midpoint_uniform_derivatives as midpoint

engine, p = base.engine, base.p
WORK = ROOT/'artifacts/flagship_integration/.primal_preconditioned_uniform_physical_local_defect_work'
base.WORK = base.base.WORK = engine.WORK = WORK
engine.ALGORITHM = 'PRIMAL_PRECONDITIONED_UNIFORM_PHYSICAL_HS_LOCAL_ENCLOSURE_ARB512_V1'
original_load = base.load_inputs


def read_derivative(unused_producer, index, stage):
    if stage not in ('endpoint', 'midpoint'):
        raise ValueError('explicit physical derivative stage required')
    producer = endpoint if stage == 'endpoint' else midpoint
    reference = producer.load_inputs(index)
    key = 'endpoint' if stage == 'endpoint' else 'interval'
    directory = ROOT/f'artifacts/flagship_integration/.primal_mean_value_component_centered_{stage}_uniform_df_work/{key}_{index:03d}'
    path, data, receipt_path = (directory/name for name in ('record.json', 'derivative.npz', 'reproduction.json'))
    record = json.loads(path.read_bytes())
    receipt = json.loads(receipt_path.read_bytes())
    report = record.get('report', {})
    algorithm = f'PRIMAL_MEAN_VALUE_COMPONENT_CENTERED_{stage.upper()}_UNIFORM_DF_ARB512_V1'
    if (record.get('algorithm') != algorithm or record.get(key) != index
            or record.get('binding', {}).get('algorithm') != algorithm
            or report.get('validation_passed') is not True
            or report.get('uniform_physical_first_derivatives_enclosed') is not True
            or report.get('weighted_augmented_basis_columns') != 99
            or report.get('full_descriptor_direction_included') is not True
            or report.get('actual_HS_midpoint_domain_enclosed') is not (stage == 'midpoint')
            or report.get('paired_uniform_primal_values_used') is not True
            or report.get('verified_anchor_derivative_contained') is not True
            or path.read_bytes() != p.geometry.encoded(record)
            or record.get('data_SHA256') != p.values.sha(data)
            or receipt.get('record_SHA256') != p.values.sha(path)
            or receipt.get('byte_identical') is not True
            or receipt.get('independent_recomputation') is not True):
        raise RuntimeError('paired complete primal-refined physical derivatives required')
    # The refined producer adds its own sources and algorithm, but must keep
    # every original physical-domain dependency and geometry field identical.
    binding = record['binding']
    for name, value in reference['binding'].items():
        if name == 'files':
            if any(binding['files'].get(file) != digest for file, digest in value.items()):
                raise RuntimeError('primal derivative physical-domain source changed')
        elif name != 'algorithm' and binding.get(name) != value:
            raise RuntimeError('primal derivative geometry changed: ' + name)
    p.verify_sources(binding)
    with np.load(data, allow_pickle=False) as a:
        matrix = p.hs.restore_balls(a['derivative_mid_q'], a['derivative_rad_q'])
    if matrix.shape != (99, 99) or not all(v.is_finite() for v in matrix.flat):
        raise ArithmeticError('complete finite physical derivative required')
    reference['binding'] = deepcopy(binding)
    for file in (path, data, receipt_path):
        p.geometry.residual.merge(reference['binding']['files'], {p.df.file_key(file): p.values.sha(file)})
    return reference, matrix


def load_inputs(index):
    source = original_load(index)
    for file in (Path(__file__), ROOT/'theory/n12_gate7_midpoint_primal_mean_value.md'):
        p.geometry.residual.merge(source['binding']['files'], {p.df.file_key(file): p.values.sha(file)})
    p.verify_sources(source['binding'])
    return source


engine.read_derivative = read_derivative
engine.load_inputs = load_inputs
main = base.main
if __name__ == '__main__':
    main()
