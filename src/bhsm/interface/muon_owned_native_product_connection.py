"""Common-A temporal binding of the retained covariant product factor.

The real corrected coefficient curve binds A=(partial_t+Omega_t)/N+W.
Its geometric L2 adjoint is -D_tau+W.  This is an owner-derived component
with the same anti-Hermitian bundle connection, not the analytic causal
factor partial_tau+Hcan, and not a completed stratified realization.
"""
from __future__ import annotations
import numpy as np
from .muon_continued_action_reality import action_reality_coefficient, action_reality_source, _higgs_mass_realified
from .muon_native_dirac_hamiltonian import lepton_current_hilbert_representation
from .muon_native_product_factor_graph import lepton_unit_trace_gauge_representation
from .muon_piecewise_euclidean_action import FAMILY_INDICES
from .muon_chronological_clifford_graph import chronological_clifford_blocks


def native_real_action_vertices(radius,lapse,*,family=None):
    """Common material-field vertices of A=D_tau+W and its action adjoint."""
    if family is not None and(type(family)is not int or family not in(0,1,2)):
        raise ValueError('family is None or an exact retained index 0,1,2')
    R,N=complex(radius),complex(lapse)
    if not np.isfinite([R,N]).all() or R.imag!=0 or N.imag!=0 or min(R.real,N.real)<=0:
        raise ValueError('positive real coframe radius and induced lapse required')
    rep=lepton_current_hilbert_representation();G=lepton_unit_trace_gauge_representation()['generators']
    gauge=np.zeros((5,4,18,18),complex);gauge[0]=G/N
    gauge[2:]=-1j*np.einsum('aij,cjk->acik',rep['alpha'],G)/R
    scalar=np.array([_higgs_mass_realified(e) for e in np.eye(4)])
    X=np.concatenate((gauge.reshape(20,18,18),scalar));fi=np.arange(18) if family is None else FAMILY_INDICES[family]
    return dict(vertices=X[:,fi][:,:,fi],vertices_sharp=X.conj().transpose(0,2,1)[:,fi][:,:,fi],
        family_indices=fi,canonical_temporal_vertices=(-1j*G/N)[:,fi][:,:,fi],
        native_temporal_vertices=(G/N)[:,fi][:,:,fi])


def owned_native_product_node(phase, coordinate_time, *, family=None):
    """Execute W and the factor connection from one real common-A germ.

    Field coordinates are the material Lorentz one-form coefficients and
    the four real Higgs coordinates.  The native temporal vertex is G/N;
    -i G/N is separately exported as the canonical Lorentz vertex.  Both
    independent analytic tangent branches use the same coefficient, never
    its conjugate.  Their fixed matrices are the real-action adjoints.
    """
    if isinstance(coordinate_time, bool) or not np.isreal(coordinate_time):
        raise ValueError('a real coordinate-time anchor is required')
    t=float(coordinate_time)
    if not np.isfinite(t):raise ValueError('finite real coordinate time required')
    if family is not None and (type(family)is not int or family not in (0,1,2)):
        raise ValueError('family is None or an exact retained index 0,1,2')
    a=action_reality_coefficient(phase,t,0j);geo=a['geometry']
    N,R=complex(geo['N']),complex(geo['R4'])
    if N.imag!=0 or R.imag!=0 or N.real<=0 or R.real<=0:
        raise ValueError('the real positive coframe chart is required')
    W,Om=a['W'],a['Omega'];herm=float(np.max(abs(W-W.conj().T)))
    anti=float(np.max(abs(Om+Om.conj().T)))
    if max(herm,anti)>1e-12:raise ArithmeticError('common-A real action reality failed')
    rep=lepton_current_hilbert_representation()
    vertex=native_real_action_vertices(R,N,family=family)
    fi=np.arange(18) if family is None else FAMILY_INDICES[family]
    restrict=lambda x:x[...,fi,:][...,fi]
    return dict(W=restrict(W),Omega_factor=restrict(Om),
        factor_body=restrict(W+Om),adjoint_body=restrict(W-Om),
        canonical_Hcan=restrict(W-1j*Om),vertices=vertex['vertices'],vertices_sharp=vertex['vertices_sharp'],
        canonical_temporal_vertices=vertex['canonical_temporal_vertices'],
        native_temporal_vertices=vertex['native_temporal_vertices'],alpha=restrict(rep['alpha']),
        R=R.real,N=N.real,raw_fields=a['raw'].real.copy(),
        wall_independent_plus_inherited=a['wall_independent_plus_inherited'].real.copy(),
        inherited_image=float(a['inherited_image'].real) if hasattr(a['inherited_image'],'real') else float(a['inherited_image']),
        family_indices=fi,coordinate_time=t,W_Hermitian_defect=herm,
        Omega_anti_Hermitian_defect=anti,
        factor_owner='ae4_current_c2_factorized_hs_calderon.factorized_product_dirac_hs_weyl_jet',
        bundle_connection_owner='completion.foundational_dirac_spin_glue_v14_45 collar common total connection',
        native_equation='A=(partial_t+Omega_L,t)/N+W; Omega_factor=Omega_L,t/N',
        current_equation='i D_tau chi=W chi; Hcan=W-i Omega_factor',
        native_pairing='d_tau*dOmega after the retained canonical density isometry; d_tau=N dt',
        field_coordinate='material At_L,Ar_L,Ai_L; realified Higgs ReH1,ReH2,ImH1,ImH2',
        temporal_connection_inferred_from_Hcan=False,
        physical_outer_domain_or_relative_completion_identified=False)


def owned_native_product_source(phase,coordinate_time,source_curves,*,family=None):
    """Actual first magnetic fields in the native common-A factor coordinates.

    The retained source already contains its calibrated charge.  Only the
    temporal connection placement is converted from delta Hcan.  There is
    no multiplication of the source by another electric charge and no
    deletion of Higgs response.  Real anchors make the opposite branch's
    matrices the dagger; arbitrary complex source coefficients themselves
    remain independent analytic tangent coordinates.
    """
    a=owned_native_product_node(phase,coordinate_time,family=family)
    source=action_reality_source(phase,float(coordinate_time),source_curves,0j)
    G=lepton_unit_trace_gauge_representation()['generators']
    dOm=np.einsum('ach,cij->ahij',source['source_wall'][:,0],G)/a['N']
    Xi=source['Xi']+(1+1j)*dOm;fi=a['family_indices']
    Xi=Xi[:,:,fi][:,:,:,fi]
    return dict(Xi=Xi,Xisharp=Xi.conj().transpose(0,1,3,2),
        canonical_Xi=source['Xi'][:,:,fi][:,:,:,fi],delta_Omega=dOm[:,:,fi][:,:,:,fi],
        source_wall=source['source_wall'],source_H=source['source_H'],
        source_axes=np.arange(8),family_indices=fi,electric_charge_added_again=False,
        source_equation='delta A=delta W+delta Omega; delta Hcan=delta W-i delta Omega',
        independent_source_coefficients_conjugated=False)


def owned_native_product_quadrature(phases, temporal_grids, *, family,
                                    quadrature_order=4):
    """Actual two-arm real product core with a single common birth trace.

    Incoming nodes run toward birth, outgoing nodes run away from birth.
    The initial-only restriction and final natural row are computational
    finite-core conditions.  Both original endpoint locations are retained;
    neither is called E0 or the canonical stop. No corner interval or Wick
    continuation of the causal current action is asserted by this graph.
    """
    if type(quadrature_order)is not int or quadrature_order<2:
        raise ValueError('explicit quadrature order at least two required')
    gx,gw=np.polynomial.legendre.leggauss(quadrature_order)
    q=[];provenance=[];node=0;birth=None
    for side in ('incoming','outgoing'):
        grid=np.asarray(temporal_grids[side],float)
        if grid.ndim!=1 or len(grid)<2 or np.any(np.diff(grid)<=0):
            raise ValueError('strictly future real grids are required')
        if (side=='incoming' and grid[-1]!=0) or (side=='outgoing' and grid[0]!=0):
            raise ValueError('birth is the shared real time zero')
        for lo,hi in zip(grid[:-1],grid[1:]):
            h=hi-lo
            for x,g in zip((gx+1)/2,gw*h/2):
                t=lo+h*x;a=owned_native_product_node(phases[side],t,family=family)
                q.append(dict(H=a['factor_body'],Hsharp=a['adjoint_body'],
                    R=a['R'],Rsharp=a['R'],vertices=a['vertices'],
                    vertices_sharp=a['vertices_sharp'],right_clock=a['N'],
                    reflected_clock=a['N'],measure=g*a['N'],
                    rows=((node,1-x,-1/h),(node+1,x,1/h)),
                    W=a['W'],Omega_factor=a['Omega_factor'],N=a['N'],
                    raw_fields=a['raw_fields'],coordinate_time=t,side=side))
                provenance.append((t,g*a['N'],0 if side=='incoming' else 1,node,node+1))
            node+=1
        if side=='incoming':birth=node
    return dict(quadrature=q,temporal_nodes=node+1,chronological_birth_trace_node=birth,
        provenance=np.array(provenance),initial_right_trace_node=0,
        final_natural_trace_node=node,real_product_core=True,
        physical_outer_domain_or_relative_completion_identified=False)


def owned_native_product_blocks(graph, angular_derivatives, *, alpha):
    """Positive geometric-L2 square on this exact real core, before inverse."""
    b=chronological_clifford_blocks(graph['quadrature'],temporal_nodes=graph['temporal_nodes'],
        angular_derivatives=angular_derivatives,alpha=alpha)
    defects=[np.max(abs(b['K_diagonal']-b['K_diagonal'].conj().transpose(0,2,1))),
        np.max(abs(b['K_upper']-b['K_lower'].conj().transpose(0,2,1)))]
    b.update(native_product_connection_bound=True,geometric_L2_real_positive_core=True,
        original_quadratic_Hermitian_defect=float(max(defects)),
        causal_Hcan_used_as_native_temporal_connection=False,
        physical_outer_domain_or_relative_completion_identified=False)
    return b


def native_product_green_boundary(W,Omega,*,value,proper_derivative):
    """Return the original endpoint product conormal A u, before orientation."""
    W,Om,u,du=(np.asarray(x,complex) for x in (W,Omega,value,proper_derivative))
    if W.ndim!=2 or W.shape[0]!=W.shape[1] or Om.shape!=W.shape or u.shape!=du.shape or u.shape[0]!=len(W):
        raise ValueError('matching endpoint body, value and proper derivative required')
    return du+(W+Om)@u
