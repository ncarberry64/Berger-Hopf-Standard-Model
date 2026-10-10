"""Compact source-bound even-Y coefficient export for the finite-core audit."""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from evaluate_muon_native_product_factor_graph import record,serial,array_record,deterministic_npz
from bhsm.interface.muon_native_coupled_source_heat import retained_corrected_scalar_photon_response
from bhsm.interface.muon_native_mean_core_heat_target import corrected_even_y_paired_heat_cotangent


def evaluate():
    response=retained_corrected_scalar_photon_response(ROOT)
    a=corrected_even_y_paired_heat_cotangent(response,time_nodes=np.linspace(-.001,0,17),quadrature_order=4,
        parameter=4.7240808471919143e-8,divided_difference_order=64)
    keys=('normalized_P0_eigenvalues','normalized_P1','normalized_P2','normalized_LR_sign_grading',
          'actual_FE_K0','actual_FE_Gram','actual_FE_K1','actual_FE_K2','actual_FE_LR_sign_grading','computed_generalized_eigenvectors','computed_eigenbasis_K0','computed_eigenbasis_Gram',
          'weighted_raw228_Z0_Z1_Z2_norm_majorant_inputs',
          'weighted_raw228_Y_fourth_majorant','coefficient_time_samples','response_time_samples')
    arrays={k:a[k] for k in keys};arrays['paired_raw228_heat_target']=a['families']['middle_minus_light']['weighted_raw228_cotangent']
    primitives=a['stored_primitive_frobenius_norm_upper_inputs']
    for key in primitives[0]:arrays[key]=np.array([r[key] for r in primitives])
    packet={k:v for k,v in a.items() if k not in keys+('families','stored_primitive_frobenius_norm_upper_inputs')}
    packet.update(classification='EVALUATED_STABLE_EVEN_Y_PAIRED_FINITE_CORE_HEAT_TARGET_COEFFICIENTS',
        normalized_polynomial='P(Y)=diag(lambda0)+Y*P1+Y²*P2 in computed generalized-eigen FEGram coordinates',
        coefficient_scope='actual corrected material130 outgoing24 numerical germ, all18 representation reduced by exact fixedY family invariance; no physical cutoff/birth/domain claim',
        consumed_input_records=response['source_records'],
        source_records=[record('src/bhsm/interface/muon_native_mean_core_heat_target.py',('corrected_even_y_paired_heat_cotangent','_stored_frobenius_upper','_cutoff_divided_differences')),
                        record('scripts/evaluate_muon_native_even_y_heat_target.py',('evaluate',))],
        array_records={k:array_record(v) for k,v in arrays.items()})
    return serial(packet),arrays


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    packet,arrays=evaluate();args.output.mkdir(parents=True,exist_ok=True);archive=deterministic_npz(arrays)
    packet['matrix_archive']=dict(path='paired_target_coefficients.npz',bytes=len(archive),sha256=sha256(archive).hexdigest())
    raw=(json.dumps(packet,indent=2,sort_keys=True,allow_nan=False)+'\n').encode()
    (args.output/'paired_target_coefficients.npz').write_bytes(archive);(args.output/'paired_target_coefficients.json').write_bytes(raw)
    print(json.dumps(dict(receipt_bytes=len(raw),receipt_sha256=sha256(raw).hexdigest(),archive_bytes=len(archive),archive_sha256=sha256(archive).hexdigest()),sort_keys=True))


if __name__=='__main__':main()
