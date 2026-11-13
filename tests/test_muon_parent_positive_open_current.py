"""Full current image and stable curvature return, no LSZ substitution."""
import numpy as np
import pytest
from bhsm.interface.muon_parent_positive_open_current import canonical_current_wall_contraction,actual_positive_open_current_application


def test_full_current_contraction_matches_explicit_image_columns():
    rng=np.random.default_rng(107) # CONTROL_ONLY test kernel, not a state.
    V=rng.normal(size=(5,4,18,18))+1j*rng.normal(size=(5,4,18,18))
    W=rng.normal(size=(400,7));K=W@W.T
    got=canonical_current_wall_contraction(K,V)
    direct=np.zeros((18,18),complex)
    for h in range(20):
        for c in range(7):
            image=np.einsum('fc,fcij->ij',W.reshape(5,4,20,7)[:,:,h,c],V)
            direct+=image.conj().T@image
    np.testing.assert_allclose(got,direct,rtol=5e-15,atol=2e-10)
    with pytest.raises(ValueError):canonical_current_wall_contraction(K,V[:,:,:4,:4])


def test_actual_curvature_is_consumed_by_full_wall_current_and_not_removed_by_lorenz():
    from pathlib import Path
    from bhsm.interface.muon_magnetic_source_mean_load import load_magnetic_reached_mean_inputs
    from bhsm.interface.muon_magnetic_open_lepton_vertex import magnetic_open_fields_at_node
    from bhsm.interface.muon_parent_gauge_geometry_correction import ROOT
    p=Path(ROOT)/'artifacts/muon_parent_positive_gauge_form_20261011/run_1';g={}
    for part in ('action','hilbert','green'):
        with np.load(p/('incoming_'+part+'.npz'),allow_pickle=False) as a:g.update({k:a[k].copy() for k in a.files})
    b=load_magnetic_reached_mean_inputs('artifacts/muon_electromagnetic_soft_magnetic_source_20261011/incoming_run_1',repository=ROOT)
    f=magnetic_open_fields_at_node(b,b['source']['times'][2]);r=actual_positive_open_current_application(f['raw_fields'],b['representation'],g)
    assert r['full18_open_current_curvature_form'].shape==(18,18)
    assert np.linalg.norm(r['full18_open_current_curvature_form'])>16000
    assert r['current_image_Lorenz_relative_defect']<1e-18
    assert np.linalg.norm(r['full18_open_current_curvature_Green_return_cap'])>8e-8
    assert r['no_curvature_inverse_majorant']['defect_infinity_upper']<1
    assert r['stable_inverse_difference_used']
    assert not r['intermediate_fermion_Green_inserted']
    assert not r['physical_Gauss_BRST_quotient_or_canonical_P_strat_identified']
    assert r['physical_a_mu'] is None


def test_stable_inverse_difference_retains_tiny_curvature_without_subtraction():
    # CONTROL_ONLY exact mathematical identity, not a photon/Pauli packet.
    import sympy as s
    K=s.Matrix([[3,1],[1,5]]);C=s.Matrix([[s.Rational(1,10**30),0],[0,s.Rational(1,10**31)]])
    G=K.inv();G0=(K-C).inv()
    assert (G-G0+G0*C*G)==s.zeros(2)
    assert any(v!=0 for v in G-G0)
