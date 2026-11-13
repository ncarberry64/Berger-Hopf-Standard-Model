"""Explicit unit-clock contract for the frozen ordinary source correction."""
from __future__ import annotations
from .muon_common_domain_charge_source_clock import corrected_source_clock_higgs_first


def validated_source_clock_higgs_first(coordinate_first, lifted_field_coordinate_rate,
                                     graph_part, coordinate_slope, right_clock, lapse):
    """Guard the actual part-zero clock; connector clocks stay independent.

The source-cell ODE dz/dtau_E=-i/N belongs to the owner's unit proper-clock
rows. A differently scaled part-zero clock needs its own coordinate chart
and cannot be silently interpreted as this application.
    """
    if graph_part == 0 and right_clock != 1:
        raise ValueError('ordinary source-cell right clock must equal its owned unit proper-clock coefficient')
    return corrected_source_clock_higgs_first(coordinate_first, lifted_field_coordinate_rate,
                                             graph_part, coordinate_slope, right_clock, lapse)
