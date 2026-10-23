"""Exact intrinsic Dirac action reduction of the reached radial enrichment.

The intrinsic first-order lepton action consumes the full wall trace, not
the bulk radial gauge extension.  This reduction applies only to that
operator.  It neither projects the Maxwell action nor selects a physical
field, covariance, or carrier.  The reference radial frame is held fixed.
"""
from __future__ import annotations
import numpy as np

from .muon_parent_gauge_geometry_correction import correction_representation
from .muon_parent_maxwell_full_weak import FIELD_ORDER
from .muon_parent_retarded_hypercharge import WALL,regular_radial_basis
from .muon_primal_intrinsic_lepton_operator import primal_intrinsic_lepton_operator


def intrinsic_wall_coordinate_reduction(representation):
    """Prove the sufficient trace action map for the complete first-order block."""
    rep=representation
    count=len(rep['gauge_labels'])
    trace=np.asarray(rep['wall_trace_map'],float)
    if trace.shape!=(5,4,count) or not np.isfinite(trace).all():
        raise ValueError('complete actual fixed-frame wall trace map required')
    original=correction_representation(radial_points=48,cap_points=48,radial_order=2,
        include_wall_lift=True,include_scalar_mean=True)
    basis,_=regular_radial_basis(np.array([WALL]),original['radial_order'])
    legacy_trace=np.zeros((5,4,60))
    reduction=np.zeros((60,count))
    for j,label in enumerate(original['gauge_labels']):
        f=FIELD_ORDER.index(label['field']);c=label['internal']
        b=basis[0,label['radial']]
        legacy_trace[f,c,j]=b
        if label['wall_lift']:
            if b==0:raise ValueError('retained wall lift does not represent the action trace')
            reduction[j]=trace[f,c]/b
    defect=legacy_trace@reduction-trace
    if np.max(abs(defect))>8*np.finfo(float).eps*max(1.,np.max(abs(trace))):
        raise ValueError('wall action reduction is incomplete')
    raw_map=np.zeros((228,108+2*count))
    raw_map[:100,:100]=np.eye(100)
    raw_map[100:160,100:100+count]=reduction
    raw_map[160:220,100+count:100+2*count]=reduction
    raw_map[-8:,-8:]=np.eye(8)
    return dict(original_representation=original,raw_action_map=raw_map,
        complete_trace_reconstruction_defect=float(np.max(abs(defect))),
        wall_action_rank=int(np.linalg.matrix_rank(trace.reshape(20,count))),
        reduction_scope='intrinsic first-order Dirac action only; bulk Maxwell/radial conormal not reduced')


def primal_trace_enriched_lepton_operator(raw_fields,representation):
    """Evaluate the full operator and raw268 jet on actual enlarged primal fields."""
    count=len(representation['gauge_labels']);nr=108+2*count
    raw=np.asarray(raw_fields)
    if not np.isrealobj(raw) or raw.shape!=(nr,) or not np.isfinite(raw).all():
        raise ValueError('complete finite real enriched primal vector required')
    reduction=intrinsic_wall_coordinate_reduction(representation)
    P=reduction['raw_action_map']
    answer=primal_intrinsic_lepton_operator(P@raw,reduction['original_representation'])
    for key in ('W_raw_first_jet','Omega_tau_raw_first_jet','H_can_raw_first_jet'):
        answer[key]=np.einsum('aj,auv->juv',P,answer[key])
    answer['proper_time_Haar_measure_first_jet']=P.T@answer['proper_time_Haar_measure_first_jet']
    answer['raw_fields']=raw.copy()
    answer['wall_trace']=np.einsum('fcj,j->fc',representation['wall_trace_map'],raw[100:100+count])
    answer['intrinsic_raw_action_map']=P
    answer['complete_trace_reconstruction_defect']=reduction['complete_trace_reconstruction_defect']
    answer['wall_action_rank']=reduction['wall_action_rank']
    answer['radial_reduction_scope']=reduction['reduction_scope']
    answer['fixed_computational_radial_frame']=True
    return answer
