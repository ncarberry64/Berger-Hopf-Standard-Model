"""Conditional fixed-parent child shooting with all original birth audits.

The terminal graph is REQUIRED. Y=0 is a finite-natural control, not a
retarded exterior. Canonical inputs obey the two named central momentum
identities, and original v/y equations are reconstituted before launch.
"""
import itertools
import numpy as np
from scipy.linalg import qr
from .muon_complex_canonical_compatibility import canonical_central_frame
from .muon_trace_enriched_charged_current_response import enriched_central_profiles
from .muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation
from .muon_coupled_phase_trace_projection import _solve
from .muon_complex_coupled_reset_continuation import coupled_reset_application,central_reset_Ward_rows
from .muon_holomorphic_child_action import holomorphic_inherited_child_action,_affine_geometry
from .muon_holomorphic_two_arm_action import holomorphic_two_arm_action
from .muon_warm_complex_canonical_compatibility import warm_complex_constitutive_compatibility
from .muon_complex_canonical_midpoint import solve_complex_canonical_midpoint
from .muon_full_canonical_terminal_return import full_canonical_jacobi_generator,full_canonical_midpoint_transfer


def ward_canonical_input(raw,representation,independent_momentum,*,pivot_columns=None):
    """Literal analytic central Ward momentum chart and its full H contact."""
    raw=np.asarray(raw,complex);rep=representation
    frame=canonical_central_frame(raw,rep);C=frame['literal_generators'][:106].T
    if pivot_columns is None:
        ids=np.flatnonzero(np.max(abs(C),axis=0)>0)
        pivot_columns=max(itertools.combinations(ids.tolist(),2),key=lambda p:abs(np.linalg.det(C[:,p])))
    piv=np.asarray(pivot_columns,int);keep=np.array([i for i in range(106)if i not in piv])
    pp=np.asarray(independent_momentum,complex)
    if pp.shape!=(104,):raise ValueError('all104 independent canonical momenta required')
    pi=np.zeros(106,complex);pi[keep]=pp;pi[piv]=-np.linalg.solve(C[:,piv],C[:,keep]@pp)
    E=np.zeros((212,210),complex);E[:106,:106]=np.eye(106);E[106+keep,106+np.arange(104)]=1
    E[np.ix_(106+piv,106+np.arange(104))]=-np.linalg.solve(C[:,piv],C[:,keep])
    profiles=enriched_central_profiles(rep);coordinates=frame.get('coordinates')
    # At ordering is the original radial x internal coefficient ordering.
    from .muon_birth_trace_enriched_action import generic_coordinate_lift
    coordinates=generic_coordinate_lift(rep['gauge_labels'])
    ids=np.array(coordinates['At_indices']);central=[i for i in ids if rep['gauge_labels'][i]['internal']==3]
    wall=rep['wall_trace_map'][0,3,central]@profiles['theta_coefficients']
    G=higgs_u2_real_representation()['real_generators'][3]
    contact=-np.outer(wall,G.T@pi[102:106])
    E[np.ix_(106+piv,np.arange(102,106))]=-np.linalg.solve(C[:,piv],contact)
    return dict(momentum=pi,canonical_embedding=E,compatibility_rows=C@pi,
                named_momentum_pivots=piv,independent_momentum_columns=keep,momentum_Ward_map=C)


def complete_finite_action_work(transfer,canonical_embedding,fiber,x_birth,Pi_birth,
                              x_terminal,Pi_terminal,terminal_matrix,terminal_source,
                              explicit_source_domain_work):
    """Complete endpoint variation, retaining the initial/source term.

    δS=Pi_T δx_T−Pi_B δx_B plus explicit source/domain work. A terminal
    graph contributes −δx_T(Y x_T+s). All terms are separately returned.
    """
    T=np.asarray(transfer,complex);E=np.asarray(canonical_embedding,complex);N=np.asarray(fiber,complex)
    n=len(x_birth);Y=np.asarray(terminal_matrix,complex);s=np.asarray(terminal_source,complex)
    work=np.asarray(explicit_source_domain_work,complex)
    if T.shape!=(2*n,2*n)or Y.shape!=(n,n)or s.shape!=(n,)or work.shape!=(N.shape[1],):
        raise ValueError('same canonical transfer and explicit terminal/source domain required')
    XB=(E@N)[:n];XT=(T@E@N)[:n]
    tail=np.asarray(Pi_terminal)-Y@np.asarray(x_terminal)-s
    terminal=XT.T@tail;initial=XB.T@np.asarray(Pi_birth)
    full=terminal-initial+work
    sv=np.linalg.svd(XT,compute_uv=False);threshold=max(XT.shape)*np.finfo(float).eps*sv[0]
    return dict(full_action_work=full,terminal_only_work=terminal,initial_cotangent_work=initial,
        explicit_source_domain_work=work,full_terminal_graph_residual=tail,
        initial_fiber_position_map=XB,terminal_fiber_position_map=XT,
        terminal_fiber_singular_values=sv,terminal_fiber_rank=int(np.sum(sv>threshold)),
        terminal_fiber_condition=float(sv[0]/sv[-1]),projected_work_does_not_imply_full_tail_zero=True)


class FixedParentFiniteShooter:
    def __init__(self,raw_pair,reference_pair,representation,weights,normalization,action_parameters,
                 *,terminal_matrix,terminal_source,step=1e-8,cells=2,guard=2e-10,inner_iterations=6):
        self.raw=np.asarray(raw_pair,complex).copy();self.reference=np.asarray(reference_pair,complex).copy()
        self.rep=representation;self.weights=weights;self.normalization=normalization;self.params=dict(action_parameters)
        self.Y=np.asarray(terminal_matrix,complex);self.s=np.asarray(terminal_source,complex)
        if self.Y.shape!=(106,106)or self.s.shape!=(106,):raise ValueError('explicit original full terminal graph required')
        self.h=complex(step);self.cells=int(cells);self.guard=float(guard);self.maxinner=int(inner_iterations)
        seed=holomorphic_two_arm_action(self.raw,self.reference,self.rep,**self.params)
        self.P=seed['one_lift'];self.eta=(self.P.T@self.raw.T).T;self.initial_child=self.eta[1].copy()
        self.parent_Pi_target=seed['parent']['gradient'][106:212].copy()
        self.frames=[canonical_central_frame(x,self.rep)for x in self.raw]
        self.frame_refs=[e[106:].copy()for e in self.eta]
        self.parent_cache={};self.piv=None;self.freeq=None;self.freep=None;self.keep_birth=None
        pi=seed['gradient'][seed['velocity_indices']][106:]
        C0=self.frames[1]['literal_generators'][:106].T
        columns=np.flatnonzero(np.max(abs(C0),axis=0)>0)
        piv=max(itertools.combinations(columns.tolist(),2),key=lambda p:abs(np.linalg.det(C0[:,p])))
        keep=np.array([i for i in range(106)if i not in piv])
        packet=ward_canonical_input(self.raw[1],self.rep,pi[keep],pivot_columns=piv)
        self.piv=packet['named_momentum_pivots'];self.keep_pi=packet['independent_momentum_columns']
        self.start=np.r_[self.eta[1,:106],pi[self.keep_pi]]

    def parent(self,surface_gamma=None):
        key=surface_gamma
        if key in self.parent_cache:return self.parent_cache[key]
        params=dict(self.params);params['surface_gamma']=surface_gamma
        def action(e):
            r=self.P@e;pair=np.stack((r,r))
            return holomorphic_two_arm_action(pair,pair,self.rep,**params)['parent']
        w=warm_complex_constitutive_compatibility(self.eta[0],self.parent_Pi_target,action,self.frames[0],
            frame_reference=self.frame_refs[0],max_iterations=self.maxinner,tolerance=self.guard)
        self.parent_cache[key]=w
        return w

    def evaluate(self,canonical_input,*,surface_gamma=None,guess=None,save=None,progress=None):
        u=np.asarray(canonical_input,complex)
        if u.shape!=(210,):raise ValueError('complete child canonical chart210 required')
        parent=self.parent(surface_gamma)
        if parent['status']!='ALL_ORIGINAL_COMPLEX_CONSTITUTIVE_ROWS_TOLERANCE':
            return dict(valid=False,status='PARENT_ORIGINAL146_RECONSTITUTION_FAILED',parent=parent)
        parent_raw=self.P@parent['coefficients'];params=dict(self.params);params['surface_gamma']=surface_gamma
        e=self.initial_child.copy()if guess is None else np.asarray(guess,complex).copy();e[:106]=u[:106]
        packet=ward_canonical_input(self.P@e,self.rep,u[106:],pivot_columns=self.piv);pi=packet['momentum']
        rawpair=np.array([parent_raw,self.P@e])
        def callback(eta,t):return holomorphic_inherited_child_action(self.P@eta,t,rawpair,self.reference,self.rep,**params)
        if progress is not None:progress('child_initial_constitutive')
        initial=warm_complex_constitutive_compatibility(e,pi,lambda z:callback(z,0),self.frames[1],
            frame_reference=self.frame_refs[1],max_iterations=self.maxinner,tolerance=self.guard)
        if initial['status']!='ALL_ORIGINAL_COMPLEX_CONSTITUTIVE_ROWS_TOLERANCE':
            return dict(valid=False,status='CHILD_ORIGINAL146_RECONSTITUTION_FAILED',parent=parent,initial=initial)
        e=initial['coefficients'];rawpair[1]=self.P@e
        if save is not None:save('candidate.npz',dict(raw_pair=rawpair,reference_pair=self.reference,
            master_child=e,own_child_Pi=pi,parent_own_Pi=self.parent_Pi_target,
            child_original146_rows=initial['original_constitutive_rows'],child_frame_rows=initial['framed_rows'][-2:],
            parent_original146_rows=parent['original_constitutive_rows'],canonical_input210=u))
        if progress is not None:progress('all_original_birth_Jacobian')
        birth=coupled_reset_application(rawpair,self.reference,self.rep,self.weights,self.normalization,
                                       action_parameters=params,compute_jacobian=True)
        ward=central_reset_Ward_rows(birth,rawpair,self.rep)
        if self.keep_birth is None:
            skip=set(birth['groups']['incoming_constraints']+birth['groups']['incoming_energy']+birth['groups']['child_constraints'])
            coordinates=birth['action']['constant_profile_child']['coordinates'];labels=self.rep['gauge_labels']
            ar=[j for j,i in enumerate(coordinates['dynamic_gauge_indices'])if labels[i]['field']=='A_rho'and labels[i]['internal']==3]
            candidates=np.array(birth['groups']['gauge_temporal_dual'])[ar]
            dependent=max(itertools.combinations(candidates.tolist(),2),key=lambda p:abs(np.linalg.det(ward['rows'][:,p])))
            skip.update(dependent);self.keep_birth=np.array([i for i in range(226)if i not in skip])
        if len(self.keep_birth)!=143:raise ValueError('named original143 non-Ly birth equations required')
        gen=full_canonical_jacobi_generator(initial['action']['hessian'],106,
            self.frames[1]['named_frame_covectors'],np.zeros(252,complex),np.zeros(2,complex))
        E=packet['canonical_embedding'];J= birth['jacobian'][self.keep_birth,252:]@gen['action_embedding']@E
        if self.freeq is None:
            trows=birth['groups']['moving_geometric_trace']+birth['groups']['normal_position_trace']
            qmap=birth['jacobian'][trows,252:290];self.freeq=np.sort(qr(qmap,mode='economic',pivoting=True)[2][5:])
            nat=birth['groups']['common_attachment_temporal_dual']+birth['groups']['common_normal_temporal_dual']+birth['groups']['child_energy']
            pm=birth['jacobian'][nat,252:]@gen['action_embedding'][:,106:144]
            self.freep=np.sort(qr(pm,mode='economic',pivoting=True)[2][4:])
        coordinate=np.zeros((67,210),complex);coordinate[np.arange(33),self.freeq]=1
        pp=np.array([np.flatnonzero(self.keep_pi==j)[0]for j in self.freep])
        coordinate[33+np.arange(34),106+pp]=1
        rhs=np.zeros((210,67),complex);rhs[143:]=np.eye(67)
        fiber=_solve(np.vstack((J,coordinate)),rhs)[0]
        eta_initial=e.copy();pi_initial=pi.copy();M=np.eye(212,dtype=complex);hist=[]
        for k in range(self.cells):
            t=(k+.5)*self.h
            if progress is not None:progress(f'canonical_cell_{k}')
            def cp(i,z,rho,a,f,K,scale,history):
                if progress is not None:progress(f'cell_{k}_Newton_{i}',history[-1])
            b=solve_complex_canonical_midpoint(e[:106],pi,e.copy(),self.h,lambda z:callback(z,t),self.frames[1],
                frame_reference=self.frame_refs[1],tolerance=self.guard,max_iterations=self.maxinner,checkpoint=cp)
            a=b['application'];praw=_affine_geometry(parent_raw,t);refs=np.array([_affine_geometry(r,t)for r in self.reference])
            if save is not None:save(f'stage_{k:04d}.npz',dict(stage_raw=self.P@a['midpoint_coefficients'],
                parent_source_raw=praw,reference_stage_pair=refs,coordinate_time=np.array(t),coordinate_step=np.array(self.h),
                stage_master=a['midpoint_coefficients'],stage_gradient=a['action']['gradient'],stage_Hessian=a['action']['hessian'],
                original358_rows=a['residual'],initial_Pi=pi,Pi_final=a['p_new'],x_final=a['x_new'],
                initial_action_dual=a['initial_action_cotangent'],final_action_dual=a['final_action_cotangent']))
            if b['status']!='ALL_ORIGINAL_COMPLEX_CANONICAL_ROWS_TOLERANCE':
                return dict(valid=False,status='ORIGINAL358_STAGE_FAILED',parent=parent,initial=initial,birth=birth,stage=b)
            tr=full_canonical_midpoint_transfer(a['action']['hessian'],106,self.frames[1]['named_frame_covectors'],
                np.zeros(252,complex),np.zeros(2,complex),self.h)
            M=tr['transfer']@M
            guess=np.r_[a['x_new'],a['v_mid'],a['y_mid']]
            end=warm_complex_constitutive_compatibility(guess,a['p_new'],lambda z:callback(z,(k+1)*self.h),self.frames[1],
                frame_reference=self.frame_refs[1],max_iterations=self.maxinner,tolerance=self.guard)
            if save is not None:save(f'endpoint_{k:04d}.npz',dict(endpoint_raw=self.P@end['coefficients'],
                parent_source_raw=_affine_geometry(parent_raw,(k+1)*self.h),
                reference_stage_pair=np.array([_affine_geometry(r,(k+1)*self.h)for r in self.reference]),
                endpoint_master=end['coefficients'],endpoint_Pi=a['p_new'],coordinate_time=np.array((k+1)*self.h),
                original146_rows=end['original_constitutive_rows'],frame_rows=end['framed_rows'][-2:],
                endpoint_gradient=end['action']['gradient'],endpoint_Hessian=end['action']['hessian'],
                canonical_transfer=tr['transfer'],canonical_transfer_original_rows=tr['original358_rows_with_named_reactions']))
            if end['status']!='ALL_ORIGINAL_COMPLEX_CONSTITUTIVE_ROWS_TOLERANCE':
                return dict(valid=False,status='ORIGINAL146_ENDPOINT_FAILED',parent=parent,initial=initial,birth=birth,endpoint=end)
            e=end['coefficients'];pi=a['p_new'];hist.append(dict(stage=b,endpoint=end,transfer=tr))
        work=complete_finite_action_work(M,E,fiber,eta_initial[:106],pi_initial,e[:106],pi,
                                        self.Y,self.s,np.zeros(67,complex))
        r=np.r_[birth['residual'][self.keep_birth],work['full_action_work']]
        # This inexact Newton term omits d(fiber/flow position sensitivity)
        # contracted with the nonzero endpoint covectors. True residuals
        # and all gates are reevaluated on every nonlinear line-search trial.
        jt=work['terminal_fiber_position_map'].T@(M[106:]-self.Y@M[:106])@E
        jt-=work['initial_fiber_position_map'].T@E[106:]
        # The literal first variation is O(h) even for an unmatched force.
        # Use the fixed nonzero coordinate interval in the equation rows,
        # retaining the original work and both endpoint terms separately.
        interval=self.cells*self.h
        if interval==0:raise ValueError('nonzero recorded coordinate interval required')
        work['recorded_coordinate_interval']=np.array(interval)
        work['clock_scaled_full_action_work']=work['full_action_work']/interval
        work['clock_scaled_terminal_fiber_position_map']=work['terminal_fiber_position_map']/interval
        r=np.r_[birth['residual'][self.keep_birth],work['clock_scaled_full_action_work']]
        jt=jt/interval
        return dict(valid=True,status='EVALUATED_CONDITIONAL_FINITE_ACTION_SHOOTING',residual=r,jacobian=np.vstack((J,jt)),
            parent=parent,initial=initial,birth=birth,ward=ward,canonical_input=u,raw_pair=rawpair,reference_pair=self.reference,
            fiber=fiber,fiber_coordinate_map=coordinate,fiber_birth_rows=J@fiber,
            independent_birth_rows=self.keep_birth,canonical_embedding=E,canonical_transfer=M,
            work=work,history=hist,terminal_master=e,terminal_Pi=pi,
            omitted_Jacobian_contact='d(Xterminal,fiber)^T tail−d(Xbirth,fiber)^T Pi_birth; no derivative enclosure',
            explicit_source_domain_work_scope='parent/ref/time/h held for child-state fiber; moving event/parameter source work is not asserted zero')
