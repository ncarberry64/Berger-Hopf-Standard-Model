"""First variation of the existing complete-child dynamic attachment rows.

Owner: v17.93 required_child_cauchy_flux, v18.24 _child_rows, extended
to generic finite N by v21.35 _child_rows_at_order. No new flux law.
All arguments are derivatives in the same declared parameter columns.
"""
from flint import arb_mat


def dynamic_flux_first_jet(child_conormal, force, momentum_mixed,
                          momentum_rate_direction, event_conormal):
    """D R = D Gamma_c - D F_c + D2P_c[X,u] + DP_c[DX u] + D Gamma_e.

The event conormal is only the event contribution to the dynamic equation;
it does not replace the child momentum-rate or duplicate it on the event side.
"""
    blocks = (child_conormal, force, momentum_mixed,
              momentum_rate_direction, event_conormal)
    if any(x.nrows() != 2 for x in blocks):
        raise ValueError('two attachment rows required')
    if len({x.ncols() for x in blocks}) != 1:
        raise ValueError('all terms must share parameter columns')
    return child_conormal - force + momentum_mixed + momentum_rate_direction + event_conormal


def pullback_sector_five(trace, momentum_sectors, material, explicit_shape):
    """Compose owned native jets with an explicitly supplied material map.

Trace geometry is included once, separately from additive action sectors.
The shape term must be supplied explicitly, even when proved zero. Dimensions
alone do not certify that material is the fixed-environment seam pullback.
"""
    if trace.nrows() != 3 or not momentum_sectors:
        raise ValueError('three trace rows and action sector jets required')
    if trace.ncols() != material.nrows():
        raise ValueError('native coordinate frames differ')
    if (explicit_shape.nrows(), explicit_shape.ncols()) != (5, material.ncols()):
        raise ValueError('explicit shape jet must have five shared rows')
    pieces = {}
    for name, jet in momentum_sectors.items():
        if (jet.nrows(), jet.ncols()) != (2, material.nrows()):
            raise ValueError('sector momentum frame differs')
        pieces[name] = jet * material
    momentum = sum(pieces.values(), arb_mat(2, material.ncols()))
    total = arb_mat((trace * material).tolist() + momentum.tolist()) + explicit_shape
    return total, pieces
