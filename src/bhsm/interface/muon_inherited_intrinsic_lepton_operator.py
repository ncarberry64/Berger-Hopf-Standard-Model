"""All-family intrinsic Dirac application with the inherited wall image.

The exact finite f/sigma chart has the same geometric wall pi/4+s/Cstar
as the intrinsic metric owner.  The spatial connection image is retained
before the exact twenty-axis wall action reduction; its child derivative
is composed as a nonlinear map, not projected into the radial basis.
"""
from __future__ import annotations
import numpy as np

from .muon_birth_inherited_finite_normal_phase import affine_geometry_germ
from .muon_birth_finite_normal_trace_graph import affine_connection_profile_two_jet
from .muon_primal_trace_enriched_lepton_operator import intrinsic_wall_coordinate_reduction
from .muon_inherited_wall_lepton_application import inherited_wall_lepton_application
from .muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
from .muon_exact_material_response import exact_geometric_connection_coefficient_jets
from .muon_parent_maxwell_full_weak import M
from .muon_parent_retarded_hypercharge import WALL


def inherited_intrinsic_lepton_operator(raw_child, coordinate_time, initial_pair,
        reference_pair, representation):
    """Apply W/Omega/Hcan and every child raw first derivative.

    The parent/reference affine first germs are the same explicitly scoped
    computational chart as the corrected phase.  A joint parent variation
    is not claimed by this fixed-parent child derivative application.
    The returned independent wall slot plus inherited image still receives
    its mechanical M*(lambda_child-1) exactly once in the Dirac owner.
    """
    child=np.asarray(raw_child,float);rep=representation;N=rep['gauge_count'];nr=108+2*N
    initial=np.asarray(initial_pair,float);reference=np.asarray(reference_pair,float)
    if child.shape!=(nr,) or initial.shape!=(2,nr) or reference.shape!=initial.shape:
        raise ValueError('same complete corrected child/pair/reference representation required')
    parent=affine_geometry_germ(initial[0],coordinate_time)
    refs=np.array([affine_geometry_germ(x,coordinate_time) for x in reference])
    wall=affine_connection_profile_two_jet(np.array([parent,child]),np.array([WALL]))
    refwall=affine_connection_profile_two_jet(refs,np.array([WALL]))
    increment=wall['value'][0]-refwall['value'][0]
    reduction=intrinsic_wall_coordinate_reduction(rep);P=reduction['raw_action_map']
    D=P.copy()
    wall_independent=np.einsum('fcj,j->fc',rep['wall_trace_map'],child[100:100+N])
    wall_rate=np.einsum('fcj,j->fc',rep['wall_trace_map'],child[100+N:100+2*N])
    wall_independent[2:]+=M*increment[0];wall_rate[2:]+=M*increment[1]
    answer=inherited_wall_lepton_application(child,wall_independent,rep)
    section=answer['trace_realization']
    raw=answer['raw_fields'].copy()
    rate_image=np.zeros((5,4));rate_image[2:]=M*increment[1]
    raw[160:220]+=section@rate_image.reshape(20)
    for order,rows in ((0,slice(100,160)),(1,slice(160,220))):
        derivative=np.zeros((5,4,100));derivative[2:]=M[:,:,None]*wall['first'][0,order,100:]
        D[rows,:100]+=section@derivative.reshape(20,100)
    for key in ('W_raw_first_jet','Omega_tau_raw_first_jet','H_can_raw_first_jet'):
        answer[key]=np.einsum('aj,auv->juv',D,answer[key])
    answer['proper_time_Haar_measure_first_jet']=D.T@answer['proper_time_Haar_measure_first_jet']
    w=intrinsic_m4_weight_jet(12,child[:37],child[37:74],child[74:98],source_value=child[98],source_rate=child[99])
    exact=exact_geometric_connection_coefficient_jets(12,child[:37],child[37:74],child[74:98],
        np.array([WALL]),source_value=child[98],source_rate=child[99])['rows'][0]
    lam=w['mechanical_connection_lambda'];rate=exact['lambda_tau']/w['induced_lapse']
    geometry={}
    for name,jet in (('R4',w['R4']),('induced_lapse',w['induced_lapse']),
                     ('mechanical_lambda',lam),('mechanical_lambda_proper_time_rate',rate)):
        first=np.zeros(nr);first[:100]=jet.gradient
        geometry[name]=dict(value=float(jet.value),raw_first_jet=first)
    wall_total=wall_independent.copy();wall_total[2:]+=M*(lam.value-1)
    wall_total_rate=wall_rate.copy();wall_total_rate[2:]+=M*exact['lambda_tau'].value
    answer.update(raw_fields=child.copy(),intrinsic_reduced_raw_fields=raw,
        intrinsic_raw_action_map=D,geometry=geometry,coordinate_time=float(coordinate_time),
        inherited_wall_profile=increment,wall_independent_plus_inherited_image=wall_independent,
        wall_independent_plus_inherited_image_coordinate_rate=wall_rate,
        total_wall_connection=wall_total,total_wall_spatial_connection_coordinate_rate=wall_total_rate[2:],
        mechanical_lambda_owner_difference=float(lam.value-exact['connection_lambda'].value),
        mechanical_lambda_owner_first_jet_difference=float(np.max(abs(lam.gradient-exact['connection_lambda'].gradient))),
        complete_trace_reconstruction_defect=reduction['complete_trace_reconstruction_defect'],
        exact_wall_geometry_owner=True,mechanical_connection_count=1,
        child_raw_first_jet_parent_reference_held_fixed=True,
        algebraic_At_coordinate_rate_not_claimed=True,
        joint_parent_jet_or_physical_history_selected=False,physical_Pauli_value=False,
        source_image_projected=False,angular_scope='same homogeneous all-family18 action component; full radial image is retained only in its exact intrinsic wall readout')
    return answer
