import importlib.util
from pathlib import Path
import numpy as np
import pytest

ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'scripts/certify_n12_gate7_symmetric_quadratic_representatives.py'
spec=importlib.util.spec_from_file_location('quadratic_representatives',PATH)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def raw_record():
    keys=(
        'all_370_defined_axis_endpoint_tensors_recovered', 'all_370_midpoint_tensors_recovered',
        'one_recovery_campaign_fingerprint_retained',
        'all_recovered_total_norms_reproduce_published_norms',
        'all_recovered_output_norms_reproduce_published_norms',
        'all_persisted_transverse_bases_are_orthonormal',
        'all_persisted_transverse_bases_annihilate_their_Green_axes',
        'all_exported_summary_values_finite', '512_bit_Arb_CPU_aggregation_used',
        'no_action_center_mesh_frame_axis_parameter_or_precision_changed',
        'raw_tensor_cache_not_committed_as_release_payload',
        'outward_remainder_and_Gate7_not_claimed')
    return dict(validation=dict.fromkeys(keys,True)|{module.RAW_SKEW_KEY:False,'FULL_BHSM_COMPLETE':False},
                validation_passed=False)


def test_raw_skew_failure_stays_false_after_scoped_admission():
    record=raw_record()
    module.validate_raw_scope(record)
    assert record['validation_passed'] is False
    assert record['validation'][module.RAW_SKEW_KEY] is False


@pytest.mark.parametrize('fault',['norm','missing','completion','inconsistent_status'])
def test_other_raw_failures_cannot_be_admitted(fault):
    record=raw_record()
    if fault=='norm': record['validation']['all_recovered_output_norms_reproduce_published_norms']=False
    if fault=='missing': record['validation'].pop('all_370_midpoint_tensors_recovered')
    if fault=='completion': record['validation']['FULL_BHSM_COMPLETE']=True
    if fault=='inconsistent_status': record['validation_passed']=True
    with pytest.raises(RuntimeError,match='unadjudicated'):
        module.validate_raw_scope(record)


def test_causal_tensor_reader_uses_quadratic_representative_without_rewriting_raw(tmp_path,monkeypatch):
    path=ROOT/'scripts/certify_n12_gate7_current_green_signed_transverse_causal_center.py'
    spec=importlib.util.spec_from_file_location('causal_representation_test',path)
    causal=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(causal)
    raw=np.array([[[1.,2.],[4.,3.]]])
    shard=tmp_path/'midpoint_000.npz'
    np.savez(shard,quadratic_tensor=raw,transverse_basis=np.eye(2))
    before=shard.read_bytes()
    monkeypatch.setattr(causal.recovery,'WORK',tmp_path)
    monkeypatch.setattr(causal.scalar_correction_certificate.correction,'corrected_tensor',
                        lambda kind,index:(raw.copy(),np.eye(2)))
    represented,basis=causal._tensor('midpoint',0)
    np.testing.assert_array_equal(represented,np.array([[[1.,3.],[3.,3.]]]))
    np.testing.assert_array_equal(basis,np.eye(2))
    assert shard.read_bytes()==before


def test_unverified_representation_record_does_not_enable_composition():
    with pytest.raises(RuntimeError,match='complete current'):
        module.validate_for_consumption(raw_record(), {'validation_passed':False})
