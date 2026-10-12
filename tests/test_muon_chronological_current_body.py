from pathlib import Path
import sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from evaluate_muon_continued_current_factor import retained_input
from bhsm.interface.muon_chronological_current_body import analytic_geometry_coordinate_first,chronological_current_body_point
from bhsm.interface.muon_continued_action_reality import _geometry,action_reality_coefficient
from bhsm.interface.muon_nonlinear_chronological_n0_action import chronological_n0_field_lifts
from bhsm.interface.muon_profile_preserving_phase_sample import profile_preserving_raw_sample
from bhsm.interface.muon_euclidean_angular_weak_action import euclidean_open_action_vertices
from bhsm.interface.muon_piecewise_euclidean_action import FAMILY_INDICES


def actual(side):
    phase,_=retained_input(side,{})
    labels=phase['representation']['gauge_labels'];at=[j for j,a in enumerate(labels)if a['field']=='A_tau'];dy=[j for j,a in enumerate(labels)if a['field']!='A_tau']
    ids=np.r_[at,dy,np.arange(80,84)]
    return phase,chronological_n0_field_lifts(phase['representation'],ids)


def test_exact_owned_geometry_first_jet_on_a_nonreal_actual_coefficient_germ():
    phase,_=actual('incoming');s=profile_preserving_raw_sample(phase,-4e-6);x=s['raw_fields'].astype(complex)
    rate=s['raw_coordinate_time_derivative'];x+=2e-8j*rate
    a=analytic_geometry_coordinate_first(x,rate);h=1e-9
    ap,am=_geometry(x+h*rate),_geometry(x-h*rate)
    for key,first in a['coordinate_first'].items():
        np.testing.assert_allclose(first,(ap[key]-am[key])/(2*h),rtol=3e-6,atol=2e-7)


def test_full18_body_vertex_and_clock_germ_include_child_inherited_and_nodal_motion_once():
    rng=np.random.default_rng(711);v=1e-6*(rng.normal(size=84)+1j*rng.normal(size=84));t=.04*(rng.normal(size=84)+1j*rng.normal(size=84))
    for side in('incoming','outgoing'):
        phase,lifts=actual(side);anchor=-4e-6 if side=='incoming'else 4e-6;z=1e-8j
        a=chronological_current_body_point(phase,anchor,z,v,t,lifts)
        zero=chronological_current_body_point(phase,anchor,z,np.zeros(84),np.zeros(84),lifts)
        np.testing.assert_allclose(zero['Hcan'],action_reality_coefficient(phase,anchor,z)['Hcan'],rtol=2e-14,atol=2e-14)
        field=np.r_[lifts['W']@v,lifts['hv']@v]
        for family in(1,2):
            fi=FAMILY_INDICES[family];V=euclidean_open_action_vertices(a['R'],a['N'],family=family)['vertices']
            np.testing.assert_allclose((a['Hcan']-zero['Hcan'])[np.ix_(fi,fi)],np.einsum('c,cij->ij',field,V),rtol=2e-9,atol=2e-14)
        h=1e-9
        ap=chronological_current_body_point(phase,anchor,z+h,v+h*t,t,lifts)
        am=chronological_current_body_point(phase,anchor,z-h,v-h*t,t,lifts)
        np.testing.assert_allclose(a['Hcan_coordinate_first'],(ap['Hcan']-am['Hcan'])/(2*h),rtol=2e-5,atol=1e-7)
