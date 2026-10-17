"""Exact phase-owned normal-frame binding for the contracted readout."""
from __future__ import annotations
import numpy as np

from .muon_changing_normal_current_readout import _finite
from .muon_profile_preserving_phase_sample import profile_preserving_lepton_sample
from .muon_corrected_profile_magnetic_response import corrected_wall_reference


def phase_normal_readout_frame(phase, *, family, electric_charge, coordinate_time=0.):
    """Bind the full inherited child wall, with its two parent/reference maps.

    At common birth the additional profile can coincide to roundoff with
    the unaugmented wall. Its action-defined application is nevertheless
    retained explicitly; a near equality is not used to remove it.
    """
    if type(family) is not int or family not in (1,2):
        raise ValueError('explicit retained middle/light family required')
    e=float(_finite(electric_charge,'independently matched source charge',(),real=True))
    t=float(_finite(coordinate_time,'actual chronological observation time',(),real=True))
    if e <= 0:
        raise ValueError('positive matched source charge required')
    sample=profile_preserving_lepton_sample(phase,t)
    operator=sample['operator'];raw=sample['sample']['raw_fields']
    kw={}
    if phase['receipt']['side']=='outgoing':
        kw=dict(initial_pair=phase['arrays']['initial_pair'],reference_pair=phase['arrays']['reference_pair'])
    wall=corrected_wall_reference(raw,phase['representation'],coordinate_time=t,**kw)
    ids=np.array([2*family,2*family+1,6+2*family,7+2*family,12+2*family,13+2*family])
    return dict(arguments=dict(family_indices=ids,family=family,
        radius=operator['R4'],wall_connection=wall['background_values'][0],
        H=operator['H'],electric_charge=e),
        coordinate_time=t,raw_fields=raw,
        inherited_profile_value_time_radial=wall['inherited_profile_value_time_radial'],
        inherited_parent_and_reference_explicit=bool(kw),
        physical_pole_or_unit_selected=False)
