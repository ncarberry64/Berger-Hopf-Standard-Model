"""Original weak/current and finite child-event consumers of refined D5 fields."""
from __future__ import annotations
import numpy as np
from numpy.polynomial.legendre import leggauss
from .muon_d5_temporal_bulk_refinement import (
    coefficient_rows,time_evaluation_matrix,evaluate_refined_factor,evaluate_refined_field)
from .muon_d5_complement_event_return import (
    original_time_fibre_radial_operator,radial_analytic_left_from_inverse,
    consume_original_d5_bulk_weak_jacobi,original_d5_green_return,consume_event_trace_operand)
from .muon_d5_fitted_birth_domain import evaluate_child_fitted_operator

def polynomial_time_pairing(times,D):
    """Dense exact mass for the declared polynomial; no product exactness claim."""
    t=np.asarray(times,float);q,w=leggauss(len(t));h=(t[-1]-t[0])/2
    p=(t[-1]+t[0])/2+h*q;V=time_evaluation_matrix(t,p)
    M=h*np.einsum('q,qi,qj->ij',w,V,V)
    E=np.zeros_like(M);E[-1,-1]=1;E[0,0]=-1
    return M,M@D+D.T@M-E

def consume_refined_domain_family(arrays,history,child_history,*,child_application=None):
    """Retain analytic Green/weak rows and apply actual t=0 event incidence.

    U_R, the base incidence F_B and their derivatives, the child section, independent normal profiles and
    all366 homogeneous coordinates per node remain UNKNOWN. This consumer
    supplies their computed parent operands; it solves no event condition.
    """
    t=arrays['times'];r=arrays['radial_nodes'];D=arrays['time_derivative'];n=len(t)
    c,mu,mux=coefficient_rows(history,t,r);M,sbp=polynomial_time_pairing(t,D)
    weights=np.zeros(len(r));bounds=arrays['radial_boundaries'];order=int(arrays['radial_order'])
    q,w=leggauss(order)
    for a,b in zip(bounds[:-1],bounds[1:]):
        for rho,weight in zip((a+b)/2+(b-a)*q/2,abs(b-a)*w/2):
            i=int(np.argmin(abs(r-rho)))
            if abs(r[i]-rho)>4*np.spacing(abs(rho)):raise ValueError('actual radial Gauss stage required')
            weights[i]+=weight
    output=dict(temporal_mass=M,temporal_SBP_rows=sbp,radial_weights=weights)
    reports={};norm=lambda a:float(np.linalg.norm(a));maximum=lambda a:float(np.max(abs(a)))
    for op_label,coeff in c.items():
        side,branch=op_label.split('_');branch_index=0 if branch=='particle' else 1
        labels=('plus_seed',) if side=='plus' else ('minus_seed','minus_LR','minus_RL')
        for bi in range(int(arrays[op_label+'_block_count'])):
            prefix=op_label+'_block'+str(bi)+'_';indices=arrays[prefix+'indices'];d=len(indices)
            take=lambda k:coeff[k][:,:,indices][:,:,:,indices]
            op=original_time_fibre_radial_operator(take('time'),take('radial'),take('body'),
                time_principal_first=take('time_source'),radial_principal_first=take('radial_source'),
                body_first=take('body_source'),time_derivative=D,time_derivative_first=np.zeros_like(D),
                density=2*np.pi**2*mu,density_first=2*np.pi**2*mux,
                temporal_pairing=M,temporal_pairing_first=np.zeros_like(M))
            R,Rx,Q,Qx,W,Wx=(op[k] for k in ('radial_principal','radial_principal_first',
                'zero_time_operator','zero_time_operator_first','weak_density','weak_density_first'))
            factor=evaluate_refined_factor(arrays,op_label,bi,r)
            left=radial_analytic_left_from_inverse(factor['L'],factor['Lx'],R,Rx,W,Wx)
            L,Lx=left['independent_left'],left['independent_left_first']
            tag=op_label+'_block'+str(bi)
            reports[tag]=dict(current_recovery_max=maximum(left['original_current_recovery_rows']),
                current_source_recovery_max=maximum(left['original_current_source_recovery_rows']),
                inverse_max=maximum(factor['L']@factor['H']-np.eye(n*d)),
                inverse_source_max=maximum(factor['Lx']@factor['H']+factor['L']@factor['Hx']),
                discrete_temporal_Green_max=maximum(op['temporal_discrete_Green_assembly_rows']),
                discrete_temporal_Green_source_max=maximum(op['temporal_discrete_Green_assembly_source_rows']),
                variable_coefficient_aliasing_norm=norm(op['variable_coefficient_time_product_aliasing']))
            for label in labels:
                for family in range(3):
                    rows=(2*family+branch_index)*64+indices
                    get=lambda key:arrays[label+'_'+key][:,:,rows].reshape(len(r),n*d,-1)
                    V,Vr,Vx,Vrx=(get(k) for k in ('value','radial','source','radial_source'))
                    app=consume_original_d5_bulk_weak_jacobi(R,Q,V,Vr,radial_principal_first=Rx,
                        zero_time_operator_first=Qx,value_first=Vx,radial_derivative_first=Vrx,
                        independent_left=L,independent_left_first=Lx,weak_density=W,weak_density_first=Wx,
                        coordinate_weights=weights,coordinate_weights_first=np.zeros_like(weights))
                    key=label+'_family'+str(family)+'_'+branch+'_block'+str(bi)
                    for k in ('ordered_direct_field_vertex','ordered_bulk_state_response','complete_ordered_weak_source'):
                        output[key+'_'+k]=app[k]
                    currents=[];currentsx=[]
                    for i,sign,name in ((0,1,'wall'),(-1,-1,'inner')):
                        sl=slice(i,i+1) if i>=0 else slice(i,None)
                        face=original_d5_green_return(R[sl],V[sl],radial_principal_first=Rx[sl],value_first=Vx[sl],
                            independent_left=L[sl],independent_left_first=Lx[sl],weak_density=W[sl],
                            weak_density_first=Wx[sl],orientation=sign)
                        current=face['signed_original_Green_return'][0];currentx=face['signed_original_Green_return_first'][0]
                        output[key+'_'+name+'_Green']=current;output[key+'_'+name+'_Green_source']=currentx
                        currents.append(current);currentsx.append(currentx)
                    for name,opkey in (('endpoint','original_temporal_boundary_current'),('commutator','complete_temporal_commutator_contact')):
                        A,Ax=op[opkey],op[opkey+'_first']
                        output[key+'_time_'+name]=np.einsum('q,qij->ij',weights,L@(A@V))
                        output[key+'_time_'+name+'_source']=np.einsum('q,qij->ij',weights,Lx@(A@V)+L@(Ax@V)+L@(A@Vx))
                    reports[key]=dict(collocation_rows_max=maximum(app['original_full_D5_rows'][weights>0]),
                        collocation_source_rows_max=maximum(app['original_full_D5_source_rows'][weights>0]),
                        signed_Green_sum_max=maximum(sum(currents)),signed_Green_sum_source_max=maximum(sum(currentsx)))
    # The normal depth is computational, not an assigned physical wall width.
    depth=float(arrays['computational_strip_width'])*.47
    vartheta=float(child_history.times[-1])*.2
    if child_application is None:
        child_arrays,child_report=evaluate_child_fitted_operator(child_history,depth,vartheta)
    else:
        child_arrays,child_report=child_application
        if not np.array_equal(child_arrays['fitted_coordinates'],[vartheta,depth]):
            raise ValueError('completed child domain application has different point identity')
    output.update(child_arrays)
    event_reports={}
    parent_rho=bounds[0]-float(arrays['computational_strip_width'])*np.array([.11,.47,.89])
    output['parent_event_sample_radii']=parent_rho
    for label in ('plus_seed','minus_seed','minus_LR','minus_RL'):
        app=evaluate_refined_field(arrays,label,[0.],parent_rho)
        # These are OWN parent-chart samples, not an identity assignment of
        # the physical base map F_B from the child birth chart. Its unknown
        # Jacobi displacement contracts the saved original t/rho gradients.
        V=app['value'][:,0];Vx=app['source'][:,0]
        ev=consume_event_trace_operand(V,Vx,coordinate_times=np.array([0.]),event_time_index=0,
            fibre_width=384,branch_identity='original_incoming_history_'+label+'_own_parent_chart')
        for k in ('event_incoming_bulk_trace_operand','event_incoming_bulk_trace_operand_first',
                  'event_row_coefficient_of_reset_lift','event_Jacobi_coefficient_of_reset_lift','event_Jacobi_coefficient_of_reset_lift_first'):
            output[label+'_'+k]=ev[k]
        output[label+'_parent_event_time_gradient']=app['time'][:,0]
        output[label+'_parent_event_radial_gradient']=app['radial'][:,0]
        event_reports[label]=dict(parent_trace_norm=norm(V),complete_parent_trace_source_norm=norm(Vx),
            base_map_assigned=False,base_map_Jacobi_gradient_norm=norm(app['radial'][:,0]),event_residual=None)
    report=dict(classification='PROVISIONAL_REFINED_D5_WEAK_GREEN_PARENT_EVENT_OPERANDS_AND_FINITE_CHILD_BIRTH_DOMAIN',
        operator_checks=reports,event_operands=event_reports,temporal_SBP_max=maximum(sbp),
        child_birth_equation='t_child(q_birth(s),s)=0, obtained by outward original sigma-normal flow from t=0',
        child_fitted_operator_application=child_report,
        child_minimum_evaluated_time=child_report['minimum_evaluated_child_time'],
        child_maximum_evaluated_time=child_report['maximum_evaluated_child_time'],
        original_event_row='Gamma0_child-U_R (Gamma0_parent composed with F_B)=0',
        original_event_Jacobi='delta Gamma0_child-(delta U_R)(Gamma0_parent composed with F_B)-U_R[(delta Gamma0_parent composed with F_B)+(d Gamma0_parent composed with F_B)delta F_B]=0',
        base_incidence_F_B_assigned=False,parent_child_numeric_rho_identified=False,
        event_equations_solved=False,U_R_assigned=False,child_physical_section_assigned=False,
        homogeneous_coordinates_per_time_node=366,homogeneous_coordinates_assigned=False,
        amplitude_input_slot_relations='a_R=(u_R,+P_L+u_R,-P_R)g; a_LR=g/u_L,+; a_RL=g/u_L,-; same physical g, independent unassigned normal profiles',
        physical_outer_equations_solved=False,full_normal_profile_normalizations=None,
        mechanical_formation_equations_solved=False,physical_admission=False,
        derivative_scope='declared original common Xi, fixed computational time/radial faces; child birth source evaluated separately; unknown F_B/contact, physical face/amplitude/normal/state derivatives retained',
        angular_scope='unit Haar Y0=1; physical S3 volume2*pi^2 included once in weak/current density',
        gauge_scope='evaluated SU2/U1 background and n0 angular sector; colored homogeneous coordinates retained, their strong-gauge action unevaluated, never defaulted to zero',
        local_removal_repeated=False,native_temporal_corner_substituted=False)
    return output,report
