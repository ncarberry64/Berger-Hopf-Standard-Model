"""Conditional finite-field pole rows; no physical tail or mode selection."""
from __future__ import annotations
import numpy as np


def charged_two_spin_trace(gamma,gamma_energy):
    """Keep the full neutral/negative charged four-complement of C6.

    The two eR coefficient tests are the action-owned final two C6 rows.
    This fixed trace section is not an eigenfit or a physical null frame.
    Its scalar center equation cannot replace its full 2x2 pole equation.
    """
    G,GE=map(lambda a:np.asarray(a,complex),(gamma,gamma_energy))
    if G.shape!=(6,6)or GE.shape!=G.shape or not np.isfinite(G).all()or not np.isfinite(GE).all():
        raise ValueError('same full C6 finite field equation and energy first required')
    C=G[:4,:4];X=np.linalg.solve(C,G[:4,4:]);Y=np.linalg.solve(C.T,G[4:,:4].T).T
    R=np.r_[-X,np.eye(2)];L=np.c_[-Y,np.eye(2)]
    K=G[4:,4:]-G[4:,:4]@X;Z=L@GE@R
    center=np.trace(K)/2;centerE=np.trace(Z)/2
    return dict(charged_two_spin_equation=K,charged_two_spin_equation_energy=Z,
        literal_right_trace_lift=R,literal_left_trace_lift=L,
        scalar_trace_center=np.array(center),scalar_trace_center_energy=np.array(centerE),
        traceless_two_spin_pole_rows=K-center*np.eye(2),
        original_full_right_pole_rows=G@R,original_full_left_pole_rows=L@G,
        full_four_complement_rows=C@X-G[:4,4:],
        full_four_complement_left_rows=Y@C-G[4:,:4],
        scalar_center_root_is_not_semisimple_doublet_admission=True)


def finite_trace_center_root(evaluate,energy_seed,*,max_iterations=12,tolerance=1e-10):
    """Newton-apply the explicit charged trace-center equation, all rows kept.

    Every nonlinear trial calls the exact finite Gamma(E), not Gamma0+
    E GammaE0 after an inverse. Backtracking follows only the declared
    scalar trace test. The full doublet rows remain the admission test.
    """
    E=complex(energy_seed);history=[];status='FINITE_ITERATION_LIMIT';a=None
    for iteration in range(max_iterations+1):
        G,GE=evaluate(E);a=charged_two_spin_trace(G,GE)
        f=a['scalar_trace_center'].item();df=a['scalar_trace_center_energy'].item()
        rec=dict(iteration=iteration,energy=np.array(E),trace_center=np.array(f),
            full_two_spin_rows_norm=float(np.linalg.norm(a['charged_two_spin_equation'])))
        history.append(rec)
        if abs(f)<=tolerance:status='SCALAR_TRACE_CENTER_TOLERANCE_ONLY';break
        if iteration==max_iterations:break
        if abs(df)<1e-20:status='SCALAR_TRACE_DERIVATIVE_SINGULAR';break
        step=-f/df;accepted=False;rec['trials']=[]
        for k in range(12):
            trial=E+2.**(-k)*step
            try:
                b=charged_two_spin_trace(*evaluate(trial));new=abs(b['scalar_trace_center'].item())
            except (ValueError,np.linalg.LinAlgError,FloatingPointError,OverflowError):new=None
            good=new is not None and np.isfinite(new)and new<abs(f)
            rec['trials'].append(dict(energy=np.array(trial),trace_center_abs=new,accepted=bool(good)))
            if good:E=trial;accepted=True;break
        if not accepted:status='FINITE_TRACE_NEWTON_STALL';break
    G,GE=evaluate(E);a=charged_two_spin_trace(G,GE)
    R,L,Z=(a[k]for k in('literal_right_trace_lift','literal_left_trace_lift','charged_two_spin_equation_energy'))
    residue=R@np.linalg.solve(Z,L)
    border=np.block([[G,GE@R],[L@GE,np.zeros((2,2),complex)]])
    inverse=np.linalg.solve(border,np.eye(8))
    return dict(a,energy_candidate=np.array(E),energy_seed=np.array(energy_seed),history=history,status=status,
        candidate_rank2_kinetic=Z,candidate_rank2_residue=residue,
        candidate_residue_right_rows=G@residue,candidate_residue_left_rows=residue@G,
        candidate_full_Keldysh_border_rows=border@inverse-np.eye(8),
        full_boundary_range_return=inverse[:6,:6],full_gamma=G,full_gamma_energy=GE,
        full_rank2_null_rows_admitted=bool(max(np.max(abs(G@R)),np.max(abs(L@G)))<=tolerance),
        numerical_null_row_guard=tolerance,physical_retarded_pole_or_charge_admitted=False)
