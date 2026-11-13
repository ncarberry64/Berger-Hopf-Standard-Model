"""Cutoff differentiation on the actual inherited coefficient cell."""
import numpy as np
from bhsm.interface.muon_magnetic_cutoff_mean_contact import actual_cell_even_y_cutoff_target
from bhsm.interface.muon_primal_cell_native_heat import actual_cell_heat_polynomial,actual_cell_even_y_target


def test_actual_cutoff_target_keeps_gram_jets_and_agrees_with_independent_difference():
    from bhsm.interface.muon_magnetic_source_mean_load import load_magnetic_reached_mean_inputs
    from bhsm.interface.muon_magnetic_open_lepton_vertex import magnetic_open_fields_at_node
    from bhsm.interface.muon_parent_gauge_geometry_correction import ROOT
    b=load_magnetic_reached_mean_inputs('artifacts/muon_electromagnetic_soft_magnetic_source_20261011/incoming_run_1',repository=ROOT)
    f=magnetic_open_fields_at_node(b,b['source']['times'][2])
    p=actual_cell_heat_polynomial(f['raw_fields'],b['representation'],length=b['times'][-1])
    c=1e-11;h=1e-15;a=actual_cell_even_y_cutoff_target(p,c)
    plus=actual_cell_even_y_target(p,c+h);minus=actual_cell_even_y_target(p,c-h)
    derivative=(plus['paired_middle_minus_light_raw_cotangent']-minus['paired_middle_minus_light_raw_cotangent'])/(2*h)
    np.testing.assert_allclose(a['paired_middle_minus_light_raw_cutoff_cotangent'],derivative,rtol=1e-7,atol=1e-20)
    assert np.linalg.norm(a['paired_middle_minus_light_raw_cutoff_cotangent'][:100])>0
    assert a['normalized_Gram_contacts_included']
    assert not a['full_native_overlap_cutoff_cancellation_claimed']
