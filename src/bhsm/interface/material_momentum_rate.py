"""Narrow material momentum-rate contractions for the native dynamic flux.

The caller supplies owned, already-reduced action contractions at one base.
No action derivative tensor or missing formation/history data is fabricated.
"""
from flint import arb_mat


def momentum_rate_jet(*, action_third_P_X_B, action_second_X_DB_P,
                      action_second_P_DB_X, action_first_D2B_P_X,
                      action_second_DX_P_B, action_first_DB_DX_P):
    """D(DPi[X])[P] for Pi=DGamma[B], with the complete moving seed.

    All six inputs have shape 2x73. The first four give D2Pi[P,X];
    the last two give DPi[DX[P]]. This is the ordinary derivative in
    the retained native coordinates. For another frame, first compose its
    owned pullback/connection jets; do not append frame terms twice.

    A contracted third scalar-action derivative occurs, but no generic
    second/third operator tensor is needed: differentiate the contracted
    momentum adjoint along X. The internal solution and duration dependence
    must already be included in Gamma_red, B and X.
    """
    terms = {
        'action_third_P_X_B': action_third_P_X_B,
        'action_second_X_DB_P': action_second_X_DB_P,
        'action_second_P_DB_X': action_second_P_DB_X,
        'action_first_D2B_P_X': action_first_D2B_P_X,
        'action_second_DX_P_B': action_second_DX_P_B,
        'action_first_DB_DX_P': action_first_DB_DX_P,
    }
    if any(x is None or (x.nrows(), x.ncols()) != (2, 73) for x in terms.values()):
        raise ValueError('six owned 2x73 momentum-rate contractions required')
    second_pi = (action_third_P_X_B + action_second_X_DB_P
                 + action_second_P_DB_X + action_first_D2B_P_X)
    changing_rate = action_second_DX_P_B + action_first_DB_DX_P
    return dict(momentum_mixed=second_pi, momentum_rate_direction=changing_rate,
                total=second_pi+changing_rate, terms=terms)


def duration_contraction(duration_cotangent, duration_jets):
    """Signed four-row segment contraction, with no prior support/norm.

    duration_jets contains separate segment integrals. Identical interval
    enclosures in two segments do NOT mean an identical uncertain quantity;
    this routine deliberately does not factor them into one shared variable.
    A common component may be factored only with a separately proved model.
    """
    if duration_cotangent is None or duration_jets is None:
        raise ValueError('owned material duration cotangents and jets required')
    if duration_cotangent.nrows()!=4 or duration_jets.ncols()!=73:
        raise ValueError('four material rows and 73 launch directions required')
    if duration_cotangent.ncols()!=duration_jets.nrows():
        raise ValueError('one cotangent and first jet per same ordered segment required')
    return duration_cotangent*duration_jets


def sum_disjoint_material_pieces(pieces):
    """Sum disjoint owned 4x73 pieces, retaining exact incidence identities.

    Each piece provides `owner_ids`, identifying atomic source contributions,
    and `value`. Geography (formation/C2/contact) and differentiation mechanism
    (duration/mixed/adjoint) are alternative views, not additive sources.
    The supplied identifiers must come from the actual assembly owner.
    """
    if not pieces:
        raise ValueError('explicit material contributions required')
    seen=set();total=arb_mat(4,73)
    for name,piece in pieces.items():
        ids=piece.get('owner_ids');value=piece.get('value')
        if not ids or len(set(ids))!=len(ids) or seen.intersection(ids):
            raise ValueError('missing or duplicate source incidence: '+name)
        if value is None or (value.nrows(),value.ncols())!=(4,73):
            raise ValueError('owned 4x73 contribution required: '+name)
        seen.update(ids);total+=value
    return total
