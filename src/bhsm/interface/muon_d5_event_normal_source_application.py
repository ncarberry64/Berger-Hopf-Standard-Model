"""Source-only D5 application of an executed event-normal tangency pivot.

The completed value operator, value fields, and all homogeneous value
coordinates are retained. Only the consumed LR/RL particular first-source
equations are solved. The constant-psi history extension is provisional;
it neither selects a formation mode nor determines the free psi-time data.
"""
from __future__ import annotations

import numpy as np
from scipy.linalg import lu_factor, lu_solve

from .muon_actual_normal_shape_source import proper_normal_shape_coefficient
from .muon_d5_complement_bulk_response import _collocation_rule, _generator, _fresh_endpoint, _wall_maps
from .muon_d5_temporal_bulk_refinement import coefficient_rows, time_evaluation_matrix
from .muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace


class ProvisionalNormalSourceHistory:
    """Original affine value callback plus an explicitly provisional source.

    b_s=a psi and b_sdot=(D_t a)psi are extended with constant psi_E1.
    The independent D_t psi coordinate remains free in the physical joint
    problem; setting its *particular extension* to zero does not solve it.
    """
    def __init__(self, history, psi_e1):
        self.history=history
        self.psi=complex(psi_e1)
        if not np.isfinite(self.psi):raise ValueError('finite executed event-normal pivot required')
        self.times=np.asarray(history.times,float)
        self.original_phase_operands=history.original_phase_operands
        self.P=np.asarray(self.original_phase_operands['resolved_phase_coordinate_lift'])
        if self.P.shape!=(268,252):raise ValueError('original full canonical coordinate lift required')
        self.gauge_basis=history.gauge_basis
        self._cache={}
        rate=np.asarray(history.value(self.times[0])[1])
        for time in self.times:
            if not np.array_equal(np.asarray(history.value(time)[1]),rate):
                raise ValueError('the declared original affine history must have constant coordinate rate')

    def value(self,time):return self.history.value(time)

    def source(self,time):
        key=complex(time)
        if key not in self._cache:
            raw,rate=self.history.value(time)
            xi,xit=(np.asarray(a,complex) for a in self.history.source(time))
            a=proper_normal_shape_coefficient(raw,self.P)
            rate100=np.asarray(rate)[:100]
            at=a['raw_gradient']@rate100
            att=rate100@a['raw_hessian']@rate100
            correction=np.zeros(268,complex);correction_t=np.zeros_like(correction)
            correction[98],correction[99]=a['value']*self.psi,at*self.psi
            correction_t[98],correction_t[99]=at*self.psi,att*self.psi
            self._cache[key]=(xi+correction,xit+correction_t)
        return tuple(a.copy() for a in self._cache[key])


def source_gauss_update(generators, source_generators, value_stages,
        initial_source, step, gauss_matrix, source_initializer):
    """Solve only (I-h A G)V_Xi=V0_Xi+h A G_Xi V_saved.

    The value stages are explicit completed operands. The unchanged value
    matrix is factored; no value right-hand side is solved again.
    """
    G,Gx,V,V0x,A,guess=(np.asarray(a,complex) for a in (
        generators,source_generators,value_stages,initial_source,gauss_matrix,source_initializer))
    q,d,k=V.shape
    if G.shape!=(q,d,d) or Gx.shape!=G.shape or V0x.shape!=(d,k) or A.shape!=(q,q) or guess.shape!=V.shape:
        raise ValueError('complete same-stage value/source operands required')
    if not all(np.isfinite(a).all() for a in (G,Gx,V,V0x,A,guess)) or not np.isfinite(step):
        raise ValueError('finite completed Gauss value/source operands required')
    matrix=(-step*np.einsum('ij,jab->iajb',A,G))
    for i in range(q):matrix[i,:,i,:]+=np.eye(d)
    matrix=matrix.reshape(q*d,q*d)
    rhs=np.broadcast_to(V0x,(q,d,k)).copy()+step*np.einsum('ij,jab,jbc->iac',A,Gx,V)
    before=rhs.reshape(q*d,k)-matrix@guess.reshape(q*d,k)
    correction=lu_solve(lu_factor(matrix),before).reshape(q,d,k)
    stages=guess+correction
    slopes=np.einsum('qab,qbk->qak',G,stages)+np.einsum('qab,qbk->qak',Gx,V)
    report=dict(initializer_residual_max=float(np.max(abs(before))),
        corrected_stage_residual_max=float(np.max(abs(matrix@stages.reshape(q*d,k)-rhs.reshape(q*d,k)))),
        correction_norm=float(np.linalg.norm(correction)),value_equations_resolved=False)
    return slopes,stages,report


def solve_event_normal_source_application(saved, history, psi_e1, *,
        labels=('plus_seed','minus_seed','minus_LR','minus_RL')):
    """Re-use saved values and solve only explicitly named source equations.

    ``labels`` permits an append application for an affected subset without
    replaying completed sources. Each label has its own saved source record.
    """
    labels=tuple(labels)
    if not labels or len(set(labels))!=len(labels) or any(label not in (
            'plus_seed','minus_seed','minus_LR','minus_RL') for label in labels):
        raise ValueError('nonempty distinct completed particular labels required')
    new_history=ProvisionalNormalSourceHistory(history,psi_e1)
    t=np.asarray(saved['times']);bounds=np.asarray(saved['radial_boundaries'])
    order=int(saved['radial_order']);n=len(t);D=saved['time_derivative']
    cn,_,integral,A=_collocation_rule(order)
    radii=np.concatenate([a+(b-a)*cn for a,b in zip(bounds[:-1],bounds[1:])])
    old_coefficients,_,_=coefficient_rows(history,t,radii)
    coefficients,_,_=coefficient_rows(new_history,t,radii)
    endpoint=[]
    for time in t:
        raw,xi=(np.asarray(a) for a in (history.value(time)[0],new_history.source(time)[0]))
        if np.any(raw.imag!=0) or np.any(xi.imag!=0):
            raise ValueError('real original endpoint application required; no imaginary source is discarded')
        endpoint.append(_fresh_endpoint(raw.real,xi.real))
    wall=_wall_maps(endpoint,full_d5_localized_lepton_trace())
    embed=np.kron(time_evaluation_matrix(saved['amplitude_times'],t),np.eye(18))
    result=dict(times=t.copy(),radial_boundaries=bounds.copy(),radial_order=np.array(order),
        provisional_constant_psi_E1=np.array(psi_e1),source_Xi268_nodes=np.array([new_history.source(time)[0] for time in t]),
        source_coordinate_time268_nodes=np.array([new_history.source(time)[1] for time in t]),
        source_label_codes=np.array([('plus_seed','minus_seed','minus_LR','minus_RL').index(label)
            for label in labels],dtype=np.int64))
    reports={};wall_value_max=coefficient_value_max=0.
    for label in ('plus_seed','minus_seed','minus_LR','minus_RL'):
        value=wall[label]@embed
        wall_value_max=max(wall_value_max,float(np.max(abs(value-saved[label+'_wall']))))
        result[label+'_wall']=saved[label+'_wall'].copy(order='K')
        result[label+'_wall_source']=wall[label+'_source']@embed
    for key,value in wall.items():
        if not key.startswith('wall_'):continue
        if key.endswith('_source'):
            result[key]=value
        else:
            wall_value_max=max(wall_value_max,float(np.max(abs(value-saved[key]))))
            result[key]=saved[key].copy(order='K')
    # Fresh first-source inputs may change derivatives, never the saved value application.
    if wall_value_max>2e-12:raise ValueError('changed source application does not preserve the saved wall-value identity')
    for side in ('plus','minus'):
      side_labels=[label for label in labels if label.startswith(side+'_')]
      if not side_labels:continue
      for branch_index,branch in enumerate(('particle','conjugate')):
        op_label=side+'_'+branch;c=coefficients[op_label];old=old_coefficients[op_label]
        for key in ('time','radial','body'):
            coefficient_value_max=max(coefficient_value_max,float(np.max(abs(c[key]-old[key]))))
        if coefficient_value_max!=0:raise ValueError('source-only application changed original value coefficients')
        for bi in range(int(saved[op_label+'_block_count'])):
            base=op_label+'_block'+str(bi)+'_';indices=saved[base+'indices'];d=len(indices)
            chunks=[(label,family,(2*family+branch_index)*64+indices)
                for label in side_labels for family in range(3)]
            initialx=np.concatenate([result[label+'_wall_source'][:,rows].reshape(n*d,108)
                for label,family,rows in chunks],axis=1)
            initials=[];all_slopes=[];block_reports=[]
            for step,(left,right) in enumerate(zip(bounds[:-1],bounds[1:])):
                gs=[];gxs=[];vs=[];guesses=[]
                for j,rho in enumerate(left+(right-left)*cn):
                    ci=step*order+j
                    args=[c[key][ci][:,indices][:,:,indices] for key in (
                        'time','radial','body','time_source','radial_source','body_source')]
                    g,gx=_generator(*args,D);gs.append(g);gxs.append(gx)
                    ri=int(np.argmin(abs(saved['radial_nodes']-rho)))
                    if abs(saved['radial_nodes'][ri]-rho)>4*np.spacing(abs(rho)):
                        raise ValueError('completed original Gauss value stage not present')
                    vs.append(np.concatenate([saved[label+'_value'][ri][:,rows].reshape(n*d,108)
                        for label,family,rows in chunks],axis=1))
                    guesses.append(np.concatenate([saved[label+'_source'][ri][:,rows].reshape(n*d,108)
                        for label,family,rows in chunks],axis=1))
                initials.append(initialx)
                slopes,stages,report=source_gauss_update(np.array(gs),np.array(gxs),np.array(vs),
                    initialx,right-left,A,np.array(guesses))
                all_slopes.append(slopes);block_reports.append(report)
                initialx=initialx+(right-left)*np.einsum('q,qdk->dk',integral(1.),slopes)
            for li,label in enumerate(side_labels):
                column=slice(li*3*108,(li+1)*3*108)
                result[label+'_'+base+'indices']=indices.copy()
                result[label+'_'+base+'source_initial']=np.array(initials)[...,column]
                result[label+'_'+base+'source_slopes']=np.array(all_slopes)[...,column]
                result[label+'_'+op_label+'_block_count']=np.array(int(saved[op_label+'_block_count']))
            reports[base]=block_reports
        result[op_label+'_block_count']=np.array(int(saved[op_label+'_block_count']))
    report=dict(classification='PROVISIONAL_SOURCE_ONLY_EVENT_NORMAL_TANGENCY_APPLICATION',
        source_equation='D5 V_newXi=-(D_newXi D5) V_saved; original value fields unchanged',
        source_direction='original Xi+B_normal(t)*psi_parent_E1; explicit constant-psi particular extension only',
        constant_psi_parent_E1=float(np.real(psi_e1)),free_psi_time_coordinate_determined=False,
        normal_source_kinematics='delta raw98=a*psi; delta raw99=(D_t a)*psi; D_t(delta raw99)=(D_t² a)*psi on the original affine history',
        saved_value_coefficients_changed_max=coefficient_value_max,
        independently_rebuilt_wall_value_difference_max=wall_value_max,
        original_value_fields_reused=True,value_equations_resolved=False,
        consumed_particular_columns_per_label=108,executed_source_labels=list(labels),
        source_stage_checks=reports,homogeneous_value_coordinates_per_time_node=366,
        new_homogeneous_source_response=None,homogeneous_source_data=None,
        homogeneous_wall_basis_source_evaluated=True,
        homogeneous_wall_basis_source_is_bulk_source_response=False,
        old_homogeneous_value_family_retained=True,
        physical_g_or_normal_profiles_assigned=False,
        amplitude_scope='old six-node unit-amplitude input coordinates held fixed for this response derivative; physical g and independent normal-profile derivatives remain unassigned',
        mechanical_formation_mode_selected=False,outer_equations_solved=False,
        event_fermion_trace_equation_solved=False,complete_physical_derivative=False,
        physical_admission=False,finite_application_is_continuum_bound=False)
    return result,report,new_history


def evaluate_event_normal_source(arrays,label,times,radii):
    """Differentiate the new source dense polynomial; preserve old values externally."""
    label_order=('plus_seed','minus_seed','minus_LR','minus_RL')
    allowed=tuple(label_order[int(x)] for x in arrays['source_label_codes']) if 'source_label_codes' in arrays else ('minus_LR','minus_RL')
    if label not in allowed:raise ValueError('executed particular source label required')
    t=np.asarray(arrays['times']);p=np.atleast_1d(np.asarray(times,float));r=np.atleast_1d(np.asarray(radii,float))
    bounds=arrays['radial_boundaries'];order=int(arrays['radial_order']);n=len(t)
    if np.any(r>bounds[0]+1e-15) or np.any(r<bounds[-1]-1e-15):
        raise ValueError('source evaluation outside completed original numerical strip')
    _,polys,integral,_=_collocation_rule(order)
    V=time_evaluation_matrix(t,p);Vt=time_evaluation_matrix(t,p,1)
    out={key:np.zeros((len(r),len(p),384,108),complex) for key in ('source','radial_source','time_source')}
    for branch_index,branch in enumerate(('particle','conjugate')):
        op_label=label.split('_')[0]+'_'+branch
        for bi in range(int(arrays[op_label+'_block_count'])):
            original_base=op_label+'_block'+str(bi)+'_'
            specific=label+'_'+original_base
            base=specific if specific+'indices' in arrays else original_base
            indices=arrays[base+'indices'];d=len(indices)
            for ri,rho in enumerate(r):
                step=min(np.searchsorted(-bounds,-rho,side='right')-1,len(bounds)-2);step=max(step,0)
                h=bounds[step+1]-bounds[step];theta=(rho-bounds[step])/h
                slopes=arrays[base+'source_slopes'][step]
                value=arrays[base+'source_initial'][step]+h*np.einsum('q,qdk->dk',integral(theta),slopes)
                radial=np.einsum('q,qdk->dk',np.array([pol(theta) for pol in polys]),slopes)
                for family in range(3):
                    column=family if base==specific else (0 if label=='minus_LR' else 3)+family
                    sl=slice(column*108,(column+1)*108)
                    rows=(2*family+branch_index)*64+indices
                    for key,weights,a in (('source',V,value),('time_source',Vt,value),('radial_source',V,radial)):
                        b=a[:,sl].reshape(n,d,108)
                        out[key][ri,:,rows,:]=(weights@b.reshape(n,-1)).reshape(len(p),d,108).transpose(1,0,2)
    return out
