import numpy as np
from bhsm.interface.muon_parent_gauge_geometry_correction import ROOT
from bhsm.interface.muon_birth_attached_phase import load_attached_endpoint


def test_actual_full_field_attachment_fields_are_carried_into_the_canonical_phase():
    source=ROOT/'artifacts/muon_parent_gauge_geometry_correction_20261010/paired_attachment_endpoint_run_1'
    incoming=load_attached_endpoint(source,side='incoming');outgoing=load_attached_endpoint(source,side='outgoing')
    with np.load(source/'application.npz',allow_pickle=False) as f:
        raw=f['updated_raw_pair'];mom=f['full_field_attachment_momenta']
    for index,d in enumerate((incoming,outgoing)):
        np.testing.assert_array_equal(d['raw'],raw[index])
        np.testing.assert_array_equal(d['coordinates']['lift']@d['master'],raw[index])
        assert d['receipt']['row_count']==220
        assert not d['receipt']['physical_formation_closed']
        assert d['receipt']['action_parameters']['surface_gamma'] is None
    np.testing.assert_allclose(mom[1],mom[0],rtol=0,atol=2e-10)
    assert np.linalg.norm(incoming['raw'][100:180])>0
    assert np.linalg.norm(outgoing['raw'][100:180])>0
