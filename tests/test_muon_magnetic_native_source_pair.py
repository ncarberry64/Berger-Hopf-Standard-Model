from pathlib import Path
from fractions import Fraction
import json
import numpy as np
import pytest
from bhsm.interface.muon_magnetic_native_source_pair import combine_magnetic_direct_and_verified_mean
ROOT=Path(__file__).resolve().parents[1]

def actual_pair():
    with np.load(ROOT/'artifacts/muon_magnetic_native_source_heat_20261011/run_1/source_heat.npz') as f:
        pieces={name:f['incoming_q_1p0_paired_middle_minus_light_Y2_source_pair_'+name] for name in
            ('source_square_contact','ordered_two_insertion','opposite_order_two_insertion')}
    data=json.loads((ROOT/'artifacts/muon_magnetic_native_phase_adjoint_20261011/certificate_run_1/result.json').read_bytes())
    row=next(a for a in data['applications'] if a['side']=='incoming' and a['frame']=='temporal')
    return pieces,np.asarray(row['contraction_lower'][1]),np.asarray(row['contraction_upper'][1])

def test_verified_mean_bounds_and_statistics_once():
    pieces,lo,hi=actual_pair();a=combine_magnetic_direct_and_verified_mean(pieces,lo,hi)
    D=pieces['source_square_contact']+pieces['ordered_two_insertion']+pieces['opposite_order_two_insertion']
    for i in range(3):
        for j in range(3):
            exactlo=(Fraction(float(D[i,j].real))+Fraction(float(lo[i,j])))/2
            exacthi=(Fraction(float(D[i,j].real))+Fraction(float(hi[i,j])))/2
            assert Fraction(float(a['graded_exact_stored_mean_plus_stored_direct_real_lower'][i,j]))<=exactlo
            assert Fraction(float(a['graded_exact_stored_mean_plus_stored_direct_real_upper'][i,j]))>=exacthi
    assert a['fermion_statistics_factor']==.5
    assert a['complex_fermion_copy_count']==1
    assert not a['common_birth_second_mean_transfer_completed']
    assert not np.any(a['graded_source_pair'][3:])

def test_absent_axis_cannot_be_pseudoinverted_as_physical_source():
    pieces,lo,hi=actual_pair();hi[3,3]=1e-20
    with pytest.raises(ValueError,match='three actual magnetic'):
        combine_magnetic_direct_and_verified_mean(pieces,lo,hi)

def test_exact_mean_not_replaced_by_original_ill_conditioned_binary():
    pieces,lo,hi=actual_pair();a=combine_magnetic_direct_and_verified_mean(pieces,lo,hi)
    with np.load(ROOT/'artifacts/muon_magnetic_native_phase_adjoint_20261011/run_1/application.npz') as f:
        old=f['incoming_q_1p0_temporal_native_mean_response_pair']
    assert np.max(abs(old-a['induced_mean_operator_contact']))>1e-23
