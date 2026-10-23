import json
import numpy as np
import pytest
from bhsm.interface.muon_parent_gauge_geometry_correction import ROOT
from bhsm.interface.muon_birth_trace_enriched_phase import load_enriched_endpoint,enriched_representation_from_values
from bhsm.interface.muon_birth_trace_enriched_action import trace_enriched_radial_basis


SOURCE=ROOT/'artifacts/muon_parent_gauge_geometry_correction_20261010/paired_field_endpoint_enriched_run_1'


def test_enriched_endpoint_lift_consumes_every_actual_field_and_wall_map():
    data=load_enriched_endpoint(SOURCE,side='outgoing')
    np.testing.assert_array_equal(data['coordinates']['lift']@data['master'],data['raw'])
    assert data['raw'].shape==(268,)
    assert data['master'].shape==(252,)
    assert data['coordinates']['x_count']==106 and data['coordinates']['y_count']==40
    assert data['representation']['wall_trace_map'].shape==(5,4,80)
    assert np.linalg.norm(data['raw'][100:180])>0


def test_quadrature_refinement_preserves_the_actual_profile_basis_instead_of_reprojecting():
    receipt=json.loads((SOURCE/'result.json').read_bytes())
    with np.load(SOURCE/'application.npz',allow_pickle=False) as f:arrays={k:f[k] for k in f.files}
    base=enriched_representation_from_values(receipt,arrays)
    fine=enriched_representation_from_values(receipt,arrays,radial_points=64,cap_points=64)
    np.testing.assert_array_equal(base['affine_interior_projection'],fine['affine_interior_projection'])
    assert base['affine_complement_norm']==fine['affine_complement_norm']
    np.testing.assert_array_equal(base['wall_trace_map'],fine['wall_trace_map'])
    value,derivative=trace_enriched_radial_basis(fine,base['rho'])
    np.testing.assert_array_equal(value,base['radial_value_map'])
    np.testing.assert_array_equal(derivative,base['radial_derivative_map'])
    assert fine['rho'].shape==(64,)


def test_reconstruction_rejects_a_different_saved_basis():
    receipt=json.loads((SOURCE/'result.json').read_bytes())
    with np.load(SOURCE/'application.npz',allow_pickle=False) as f:arrays={k:f[k] for k in f.files}
    arrays['gauge_basis']=arrays['gauge_basis'].copy();arrays['gauge_basis'][0,0,0,0,0]+=1e-5
    with pytest.raises(ValueError,match='reconstruct exactly'):
        enriched_representation_from_values(receipt,arrays)
