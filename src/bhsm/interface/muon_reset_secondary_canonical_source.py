"""Initial trace/source secondary compatibility for canonical variations."""
from __future__ import annotations
import numpy as np
from .muon_complex_paired_normal_action import _balanced_solver


def secondary_compatible_action_source(H,embedding,B,Bt,N,Nt,C,*,normal_amplitude,
        normal_rate=0,trace_source=None,trace_source_rate=None,normal_source=0,normal_source_rate=0):
    """Signed action trial with exact primary and secondary trace conditions.

    These conditions admit initial canonical data before a reaction can
    stabilize its evolution. Energy/temporal traction is not constrained.
    Direct b_s/n_s are independent of the constitutive source embedding.
    """
    H=np.asarray(H,complex);a=embedding;R=a['embedding'];s=a['source_embedding'];x=a['x_indices'];v=a['v_indices']
    B=np.asarray(B,complex);Bt=np.asarray(Bt,complex);N=np.asarray(N,complex).reshape(1,-1);Nt=np.asarray(Nt,complex).reshape(1,-1);C=np.asarray(C,complex)
    bs=np.zeros(len(B),complex)if trace_source is None else np.asarray(trace_source,complex)
    bst=np.zeros(len(B),complex)if trace_source_rate is None else np.asarray(trace_source_rate,complex)
    primary=np.vstack((B@R,a['compatibility_map'],C@R,N@R))
    secondary=np.vstack((Bt@R+B[:,x]@R[v],C[:,x]@R[v],Nt@R+N[:,x]@R[v]))
    E=np.vstack((primary,secondary))
    rp=np.r_[-B@s-bs,-a['compatibility_source'],-C@s,normal_amplitude-normal_source-(N@s)[0]]
    rt=np.r_[-Bt@s-B[:,x]@s[v]-bst,-C[:,x]@s[v],normal_rate-normal_source_rate-(Nt@s+N[:,x]@s[v])[0]]
    Q=R.T@H@R;force=R.T@(H@s+a['source_gradient'])
    K=np.block([[Q,E.T],[E,np.zeros((len(E),len(E)),complex)]]);rhs=np.r_[-force,rp,rt];solve,balance=_balanced_solver(K)
    z=solve(rhs);q=z[:R.shape[1]];delta=R@q+s
    # The operator solve keeps producer asymmetry. This separate row is
    # the derivative of the literal quadratic, with no change to the solve.
    quadratic_rows=R.T@((H+H.T)@delta/2+a['source_gradient'])+E.T@z[len(q):]
    return dict(canonical_coordinates=q,original_master_direction=delta,original_KKT=K,original_rhs=rhs,solution=z,
        original_rows=K@z-rhs,primary_constraint_rows=primary,secondary_constraint_rows=secondary,
        primary_constraint_rhs=rp,secondary_constraint_rhs=rt,primary_constraint_residual=primary@q-rp,
        secondary_constraint_residual=secondary@q-rt,true_quadratic_stationarity_rows=quadratic_rows,
        stored_operator_minus_quadratic_stationarity=(K@z-rhs)[:len(q)]-quadratic_rows,
        normal_amplitude=(N@delta)[0]+normal_source,
        normal_rate=(Nt@delta+N[:,x]@delta[v])[0]+normal_source_rate,
        normal_primary_force=z[len(q)+len(primary)-1],normal_secondary_reaction=z[-1],
        balanced_condition=float(np.linalg.cond(balance)),
        direct_trace_source=bs,direct_trace_source_rate=bst,
        natural_rows_not_forced_zero=True,initial_data_is_computational_source_basis=True)
