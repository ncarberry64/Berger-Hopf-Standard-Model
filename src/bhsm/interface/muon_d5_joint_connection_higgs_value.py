"""Joint nonlinear original spatial-connection/Higgs trace value application.

One explicitly reported gauge-chart coordinate is held in each numerical
initializer. Every original equation and all seven tangent columns are
retained. Neither a physical orientation nor a homogeneous state is selected.
"""
from __future__ import annotations
import numpy as np
from scipy.linalg import expm,expm_frechet,qr
from .muon_d5_spatial_bundle_application import cross_matrix
from .muon_d5_higgs_temporal_bundle_application import complex_higgs,real_higgs,necessary_higgs_phase


J2=-1j*np.array([[[0,1],[1,0]],[[0,-1j],[1j,0]],[[1,0],[0,-1]]])/2


def joint_value_rows_jacobian(parent,child,Hp,Hc,O0,R0,U0,coordinates):
    """Literal16 real rows and all7 analytic Lie-chart derivatives."""
    x=np.asarray(coordinates,float);p,c=np.asarray(parent),np.asarray(child)
    if x.shape!=(7,) or p.shape!=(3,4) or c.shape!=p.shape:
        raise ValueError('all7 rotation/phase coordinates and full spatial connections required')
    b=cross_matrix(x[:3]);g=cross_matrix(x[3:6]);g2=np.einsum('i,iab->ab',x[3:6],J2)
    O=O0@expm(b);R=expm(g)@R0;U=np.exp(1j*x[6])*expm(g2)@U0
    target=np.c_[O.T@p[:,:3]@R.T,O.T@p[:,3]]
    h=Hc-U@Hp;rows=np.r_[(c-target).ravel(),real_higgs(h)]
    jac=np.zeros((16,7))
    for i,v in enumerate(np.eye(3)):
        dO=O0@expm_frechet(b,cross_matrix(v),compute_expm=False)
        jac[:12,i]=-np.c_[dO.T@p[:,:3]@R.T,dO.T@p[:,3]].ravel()
        dR=expm_frechet(g,cross_matrix(v),compute_expm=False)@R0
        dU=np.exp(1j*x[6])*expm_frechet(g2,J2[i],compute_expm=False)@U0
        field=np.zeros((3,4));field[:,:3]=O.T@p[:,:3]@dR.T
        jac[:12,3+i]=-field.ravel();jac[12:,3+i]=real_higgs(-dU@Hp)
    jac[12:,6]=real_higgs(-1j*U@Hp)
    return rows,jac,dict(base_rotation=O,gauge_rotation=R,Higgs_middle=U)


def solve_joint_connection_higgs_value(parent_coefficients,child_coefficients,
        spatial_application,*,candidate_indices=(2,3),max_iterations=6):
    """Use actual full connection and Higgs equations, without a trace fit.

    The held seventh global chart coordinate is gauge_z=0 relative to each
    saved initializer. Six explicitly selected ORIGINAL rows determine the
    other six chart coordinates. Every other row is audited independently;
    the full7-column Jacobian and residual of its reconstructed free tangent
    are returned instead of declaring that tangent a physical null space.
    """
    p,c=(np.asarray(a['gauge_connection_material'][0,2:]).real for a in (parent_coefficients,child_coefficients))
    Hp,Hc=(complex_higgs(a['intrinsic_H_realified']) for a in (parent_coefficients,child_coefficients))
    columns=np.array([0,1,2,3,4,6]);free_column=5
    outs=[];records=[]
    for index in candidate_indices:
        O0=spatial_application['base_rotations'][index];R0=spatial_application['gauge_rotations'][index]
        K0=spatial_application['gauge_SU2_lifts'][index];phase,_=necessary_higgs_phase(Hp,Hc,K0);U0=phase*K0
        x=np.zeros(7)
        first,J0,_=joint_value_rows_jacobian(p,c,Hp,Hc,O0,R0,U0,x)
        _,_,pivot=qr(J0[:,columns].T,pivoting=True,mode='economic');selected=np.array(pivot[:6])
        history=[]
        for step in range(max_iterations):
            rows,J,factors=joint_value_rows_jacobian(p,c,Hp,Hc,O0,R0,U0,x)
            P=J[np.ix_(selected,columns)];condition=np.linalg.cond(P)
            if not np.isfinite(condition) or condition>1e5:raise ValueError('selected actual equation pivot is not well conditioned')
            history.append(dict(iteration=step,all16_max=float(np.max(abs(rows))),pivot_max=float(np.max(abs(rows[selected]))),pivot_condition=float(condition)))
            if np.max(abs(rows[selected]))<4e-16:break
            x[columns]+=np.linalg.solve(P,-rows[selected])
        rows,J,factors=joint_value_rows_jacobian(p,c,Hp,Hc,O0,R0,U0,x)
        P=J[np.ix_(selected,columns)];free=np.zeros(7);free[free_column]=1
        free[columns]=-np.linalg.solve(P,J[selected,free_column])
        singular=np.linalg.svd(J,compute_uv=False)
        out=dict(initial_candidate_index=np.array(index),initial_base_rotation=O0,
            initial_gauge_rotation=R0,initial_Higgs_middle=U0,coordinates=x,
            before_rows=first,after_rows=rows,full_value_Jacobian=J,
            pivot_rows=selected,pivot_columns=columns,free_coordinate=np.array(free_column),
            reconstructed_free_tangent=free,free_tangent_all16_rows=J@free,
            full_Jacobian_singular_values=singular,**factors)
        # Separate SU2 factor from the Higgs unit factor without a new
        # logarithm/global gauge branch: only known initial factor is used.
        out['gauge_SU2_lift']=expm(np.einsum('i,iab->ab',x[3:6],J2))@K0
        out['Higgs_unit_phase']=np.array(np.exp(1j*x[6])*phase)
        outs.append(out)
        records.append(dict(initial_candidate_index=index,before_connection_max=float(np.max(abs(first[:12]))),
            before_Higgs_max=float(np.max(abs(first[12:]))),after_connection_max=float(np.max(abs(rows[:12]))),
            after_Higgs_max=float(np.max(abs(rows[12:]))),after_all16_max=float(np.max(abs(rows))),
            pivot_rows=selected.tolist(),pivot_columns=columns.tolist(),held_numerical_chart_coordinate='relative gauge_z=0; not a physical orientation selection',
            pivot_condition=float(np.linalg.cond(P)),full_Jacobian_singular_values=singular.tolist(),
            reconstructed_free_tangent_all16_max=float(np.max(abs(J@free))),iterations=history,
            physical_map_selected=False))
    arrays={key:np.array([a[key] for a in outs]) for key in outs[0]}
    report=dict(classification='EXECUTED_NONLINEAR_JOINT_ORIGINAL_CONNECTION_AND_HIGGS_VALUE_EQUATIONS',
        original_rows='12 real unit-Tr16 A_child-O.T A_parent Ad(K).T rows plus4 real H_child-u_H K H_parent rows',
        candidates=records,all7_rotation_phase_coordinates_retained=True,
        background_fields_changed=False,fermion_trace_fitted=False,minimum_norm_physical_choice=False,
        other_original_rows_independently_audited=True,physical_admission=False,
        initial_right_translation_unassigned=True,full_SM_phase_lift_unassigned=True,
        parent_homogeneous_coordinates_retained=3660,normal_profile_normalization=None,
        error_scope='finite analytic Newton application at held background; ill-conditioned full seventh direction and finite unscaled component residuals are explicit, not physical or continuum admission')
    return arrays,report
