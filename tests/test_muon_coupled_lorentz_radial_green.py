from pathlib import Path
import numpy as np
import pytest
from bhsm.interface.muon_coupled_lorentz_radial_green import (coupled_radial_trace_application,
    coupled_radial_pole_application,radial_section_overlap_application)
ROOT=Path(__file__).resolve().parents[1]


def actual(side='incoming'):
    with np.load(ROOT/'artifacts/muon_coupled_lorentz_field_symbol_20261011/run_1/application.npz',allow_pickle=False)as a:
        return[a[side+'_'+k].copy()for k in('proper_frequency_coefficients','field_quotient_lift','joint_trace_map','scalar_radial_source','central_radial_frame_rows')]


def test_actual_full_schur_original_reactions_and_frequency_derivative():
    data=actual();z=1j;a=coupled_radial_trace_application(*data,frequency=z)
    errors=[]
    for h in(1e-4,3e-5):
        p=coupled_radial_trace_application(*data,frequency=z+h)
        m=coupled_radial_trace_application(*data,frequency=z-h)
        fd=(p['full_joint_source_Green']-m['full_joint_source_Green'])/(2*h)
        errors.append(np.linalg.norm(fd-a['full_joint_source_frequency_derivative'])/np.linalg.norm(fd))
    assert errors[1]<1e-6
    assert .07<errors[1]/errors[0]<.11
    assert np.linalg.norm(a['Schur_full_response_difference'])/np.linalg.norm(a['full_field_response'])<1e-10
    assert np.linalg.norm(a['quotient_equation_residual'])/np.linalg.norm(a['joint_source_matrix'])<1e-10
    assert np.linalg.norm(a['reaction_resolved_original_residual'])/np.linalg.norm(a['joint_source_matrix'])<1e-10
    assert np.linalg.norm(a['radial_to_gauge_wall_Green'])>0


def test_radial_tangent_and_dual_are_distinct_in_the_owned_coordinate_map():
    data=actual('outgoing');r=data[3];a=coupled_radial_trace_application(*data,frequency=2j)
    assert np.array_equal(a['radial_canonical_dual'],2*r)
    assert np.allclose(a['canonical_radial_Green'],4*a['unnormalized_radial_weak_pairing'],rtol=1e-15)
    # Independent coordinate change: normalized full radial/perp scalar
    # basis uses r as the first tangent and2r as its first dual.
    assert np.isclose(r@a['radial_canonical_dual'],1.,rtol=2e-14)
    assert not np.isclose(r@r,1.)


def test_complex_coordinate_map_cannot_silently_change_the_analytic_dual():
    data=actual();data[1]=data[1].astype(complex);data[1][0,0]+=1e-10j
    with pytest.raises(ValueError,match='must be real'):
        coupled_radial_trace_application(*data,frequency=1j)


def test_all_local_poles_reconstruct_the_actual_radial_source_without_mode_deletion():
    for side in('incoming','outgoing'):
        data=actual(side);a=coupled_radial_pole_application(*data)
        assert a['finite_pole_count']==128
        assert a['infinite_pole_count']==32
        assert a['all_joint_source_pole_residues'].shape==(128,25,25)
        assert np.max(a['right_polynomial_relative_residual'])<2e-13
        assert np.max(a['left_polynomial_relative_residual'])<2e-13
        assert np.max(abs(a['radial_modal_minus_direct']))<2e-11
    # The largest incoming radial residues lie away from the real axis;
    # retaining them is essential, even though a measured scalar reference
    # is a single positive-mass pole.
    data=actual();a=coupled_radial_pole_application(*data)
    j=np.argmax(abs(a['canonical_radial_squared_pole_weights']))
    assert abs(a['local_poles'][j].imag)>.1


def test_actual_overlap_retains_static_kinetic_and_nonquadratic_coupled_response():
    data=actual();zero=coupled_radial_trace_application(*data,frequency=0)
    probe=coupled_radial_trace_application(*data,frequency=1j)
    a=radial_section_overlap_application(data[0],data[3],zero,probe)
    assert abs(a['matching_identity_residual'])<1e-14
    assert abs(a['kinetic_inverse_matching_contact'])>1e-3
    assert abs(a['surviving_nonquadratic_inverse_response'])>1e-3
    # Independently differentiate the inverse contracted radial Green.
    h=3e-4
    p=coupled_radial_trace_application(*data,frequency=h)['canonical_radial_inverse']
    m=coupled_radial_trace_application(*data,frequency=-h)['canonical_radial_inverse']
    fd=(p+m-2*zero['canonical_radial_inverse'])/(2*h*h)
    assert abs(fd-a['full_inverse_zero_frequency_coefficients'][2])<1e-8
