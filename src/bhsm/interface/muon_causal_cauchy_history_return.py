"""Oriented canonical history response, with the full Cauchy trace retained.

Retarded chronological evolution is an initial-value response to the owned
history. It does not by itself produce a temporal Dirichlet-to-Neumann graph.
"""
from flint import ctx
from .muon_stored_admission_correction import _matrix,_upper
from .muon_stored_fiber_canonical_tangent import _split


def causal_history_application(transfer_high,transfer_low,source_high,source_low,
        seed_high,seed_low,source_coordinates_high,source_coordinates_low,
        independent_target_high,independent_target_low,*,stored_direction,
        known_first_high,known_first_low,precision_bits=192):
    """Apply the causal history and its literal independent target.

    For a stored backward incoming map q_past=Mback q_birth+Rback s,
    solve only consumed columns Mback q_birth=q_past−Rback s. Its target
    pullback solves Mback.T ell_past=ell_birth. The known source first
    likewise obeys Mback k_forward=−k_backward. Original past/state/source
    jets remain explicit operands; no physical environment is selected.
    """
    if stored_direction not in('forward','backward'):
        raise ValueError('actual stored chronological orientation required')
    old=ctx.prec;ctx.prec=int(precision_bits)
    try:
        M=_matrix(transfer_high)+_matrix(transfer_low)
        R=_matrix(source_high)+_matrix(source_low)
        Q=_matrix(seed_high)+_matrix(seed_low)
        S=_matrix(source_coordinates_high)+_matrix(source_coordinates_low)
        L=_matrix(independent_target_high)+_matrix(independent_target_low)
        K=_matrix(known_first_high)+_matrix(known_first_low)
        if (M.nrows()!=M.ncols()or Q.nrows()!=M.nrows()or L.nrows()!=M.nrows()
                or R.nrows()!=M.nrows()or S.nrows()!=R.ncols()
                or S.ncols()!=Q.ncols()or K.nrows()!=M.nrows()):
            raise ValueError('complete same-domain Cauchy/source/target columns required')
        if stored_direction=='backward':
            final=M.solve(Q-R*S);dual=M.transpose().solve(L)
            source_dual=-R.transpose()*dual
            known=M.solve(-K)
            original=M*final+R*S-Q
            target_rows=M.transpose()*dual-L
            known_rows=M*known+K
        else:
            final=M*Q+R*S;dual=M.transpose()*L
            source_dual=R.transpose()*L;known=K
            original=final-M*Q-R*S
            target_rows=dual-M.transpose()*L
            known_rows=known-K
        pair=L.transpose()*final-dual.transpose()*Q-source_dual.transpose()*S
        arrays={}
        for name,value in dict(final_canonical=final,initial_literal_target=dual,
                source_literal_target=source_dual,known_source_first=known,
                original_history_rows=original,literal_target_rows=target_rows,
                known_source_first_rows=known_rows,literal_history_pair_rows=pair).items():
            arrays[name+'_high'],arrays[name+'_low']=_split(value)
        return dict(arrays=arrays,original_history_rows_upper=_upper(original),
            literal_target_rows_upper=_upper(target_rows),
            source_first_rows_upper=_upper(known_rows),literal_pair_rows_upper=_upper(pair),
            actual_chronological_forward=True,temporal_graph_or_exterior_state_selected=False,
            future_Cauchy_remainder_annihilated=False,analytic_target_conjugated=False)
    finally:ctx.prec=old
