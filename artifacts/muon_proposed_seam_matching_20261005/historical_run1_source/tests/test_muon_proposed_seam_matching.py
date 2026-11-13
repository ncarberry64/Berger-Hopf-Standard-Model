"""New direct-action matching checks; no previous production/check replay."""
from pathlib import Path
import importlib.util
import numpy as np
import pytest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('matching_replay',ROOT/'scripts/replay_muon_proposed_seam_matching.py')
replay=importlib.util.module_from_spec(spec);spec.loader.exec_module(replay)


@pytest.fixture(scope='module')
def computed():return replay.calculate(ROOT)


def test_full_cap_norm_and_actual_both_chiral_residues(computed):
    refs,c,fields,*_=computed
    assert abs(float(c['parent_volume_norm'].mid())-1)<3e-14
    assert float(c['Z_L'].mid())==float(c['Z_R'].mid())
    assert float(c['Z_L'].mid())>2.1
    assert abs(float(c['joint_volume_norm'].mid())-2)<3e-14
    assert not np.isclose(float(c['joint_volume_norm'].mid()),float(c['Z_L'].mid()),rtol=1e-3)
    with np.load(refs['wall']) as z:
        cached=1+z['Cauchy_moments'][0]/z['M4']
    assert abs(float(c['Z_L'].mid())-cached)<2e-14
    assert set(fields['cells'].tolist())==set(range(64))


def test_one_canonical_transform_preserves_time_but_exposes_interactions(computed):
    _,c,fields,maps,guards,identity,comparison,*_=computed
    Z=float(c['Z_L'].mid());C=fields['canonical_field_C'][0]
    Ct=fields['canonical_field_C_tau'][0];zt=float(c['parent_time_tau'].mid())
    assert abs(Z*C*C-1)<4e-16
    assert abs(zt*C*C+2*Z*C*Ct)<4e-15
    assert float(c['spatial_ratio'].mid())>1.05
    assert .47<float(c['canonical_Yukawa_factor'].mid())<.48
    assert np.linalg.norm(maps['Y_canonical_tau']-2*C*Ct*maps['Y_owned'])<2e-17
    assert float(c['canonical_volume_norm'].mid())<.95
    assert abs(float(c['raw_time_comparison_defect'].mid()))<2e-13
    for receipt in comparison.values():
        assert receipt['saved_full_parent_zero_action_projection_residual']<4e-13
        assert receipt['saved_full_parent_time_action_projection_residual']<4e-13


def test_same_photon_vertex_changes_with_spatial_kinetic_not_charge(computed):
    _,c,_,maps,*_=computed
    ratio=float(c['spatial_ratio'].mid())
    assert float(c['photon_residual'].mid())>0
    for n in (1,3):
        target=maps[f'target_same_b_vertex_kernel_n{n}']
        canonical=maps[f'canonical_same_b_vertex_kernel_n{n}']
        assert np.max(np.abs(canonical-ratio*target))<2e-16
        assert np.linalg.norm(maps[f'same_b_vertex_residual_kernel_n{n}'])>0
        assert canonical.shape[:3]==(8,64,64)


def test_full_compact_source_identity_uses_reused_J_not_an_added_load(computed):
    _,_,_,maps,_,identity,*_=computed
    assert identity['old_conditional_J_recomputed'] is False
    assert identity['full_compact_source_readout_cancellation_max_abs']<1e-16
    for n in (1,3):
        assert np.linalg.norm(maps[f'F_L_WBp_n{n}'])>0
        assert np.linalg.norm(maps[f'F_L_chi_reused_n{n}'])>0
        assert not np.any(maps[f'F_L_full_field_identity_residual_n{n}'])
        assert not np.any(maps[f'canonical_F_L_full_field_identity_residual_n{n}'])
