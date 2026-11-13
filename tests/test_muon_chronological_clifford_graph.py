import numpy as np
from bhsm.interface.muon_chronological_clifford_graph import (
    chronological_clifford_blocks,chronological_dense_blocks,
    chronological_pencil_blocks,chronological_clifford_field_trace)
from bhsm.interface.muon_chronological_spectral_blocks import (
    chronological_spectral_factor,chronological_selected_inverse,
    homogeneous_scalar_degree_reduction)


def fixture():
    rng=np.random.default_rng(1047)
    alpha=np.array([np.kron(np.eye(3),s)for s in(
        np.array([[0,1],[1,0]]),np.array([[0,-1j],[1j,0]]),np.diag([1,-1]))])
    q=[]
    for edge in range(3):
        for p in(.2113248654,.7886751346):
            H=rng.normal(size=(6,6))*.1+np.diag(np.arange(6)+1)
            Hs=rng.normal(size=(6,6))*.1+np.diag(np.arange(6)+1)
            q.append(dict(H=H,Hsharp=Hs,R=1.1+.02j,Rsharp=.9-.01j,
                vertices=rng.normal(size=(24,6,6))*.07,
                vertices_sharp=rng.normal(size=(24,6,6))*.09,
                rows=((edge,1-p,-1.),(edge+1,p,1.)),
                measure=.5*(1+.03j),right_clock=.7+.1j,reflected_clock=.8-.13j))
    return q,alpha


def test_complete_cell_action_and_natural_final_row_against_unsquared_integral():
    q,alpha=fixture();E=homogeneous_scalar_degree_reduction(1)['angular_derivatives']
    b=chronological_clifford_blocks(q,temporal_nodes=4,angular_derivatives=E,alpha=alpha)
    h=2;d=12;expected=np.zeros((36,36),complex)
    spatial=sum(np.kron(-1j*a,e)for a,e in zip(alpha,E))
    for x in q:
        right=np.zeros((d,36),complex);left=np.zeros((36,d),complex)
        for j,p,v in x['rows']:
            if j:
                at=slice((j-1)*d,j*d)
                right[:,at]=v*np.eye(d)/x['right_clock']+p*(np.kron(x['H'],np.eye(h))+spatial/x['R'])
                left[at,:]=v*np.eye(d)/x['reflected_clock']+p*(np.kron(x['Hsharp'],np.eye(h))+spatial/x['Rsharp'])
        expected+=x['measure']*left@right
    np.testing.assert_allclose(chronological_dense_blocks(b),expected,rtol=3e-15,atol=3e-14)
    assert np.linalg.norm(b['K_diagonal'][-1])>0
    assert not np.allclose(b['K_lower'],b['K_upper'].conj().transpose(0,2,1))


def test_streamed_source_trace_matches_independent_action_derivative_and_dense_inverse():
    q,alpha=fixture();E=homogeneous_scalar_degree_reduction(1)['angular_derivatives']
    b=chronological_clifford_blocks(q,temporal_nodes=4,angular_derivatives=E,alpha=alpha)
    z=.3+1.4j;D,U,L=chronological_pencil_blocks(b,z)
    sel=chronological_selected_inverse(chronological_spectral_factor(D,U,L))
    g=chronological_clifford_field_trace(q,sel,temporal_nodes=4,angular_derivatives=E,alpha=alpha)
    rng=np.random.default_rng(93);direction=rng.normal(size=(3,24))
    def perturbed(eps):
        out=[]
        for x in q:
            v=sum(p*direction[j-1]for j,p,_ in x['rows']if j)
            out.append(dict(x,H=x['H']+eps*np.einsum('c,cij->ij',v,x['vertices']),
                Hsharp=x['Hsharp']+eps*np.einsum('c,cij->ij',v,x['vertices_sharp'])))
        return chronological_dense_blocks(chronological_clifford_blocks(out,temporal_nodes=4,angular_derivatives=E,alpha=alpha))
    eps=2e-6;dK=(perturbed(eps)-perturbed(-eps))/(2*eps)
    A=chronological_dense_blocks(b)-z*chronological_dense_blocks(b,prefix='M')
    expected=np.trace(np.linalg.solve(A,dK))
    np.testing.assert_allclose(np.einsum('nc,nc->',g,direction),expected,rtol=2e-8,atol=4e-9)


def test_complete_spectator_trace_equals_full_degree_without_choosing_a_carrier():
    q,alpha=fixture();r=homogeneous_scalar_degree_reduction(1)
    def trace(E,multiplicity):
        b=chronological_clifford_blocks(q,temporal_nodes=4,angular_derivatives=E,alpha=alpha)
        D,U,L=chronological_pencil_blocks(b,.8j)
        sel=chronological_selected_inverse(chronological_spectral_factor(D,U,L))
        return chronological_clifford_field_trace(q,sel,temporal_nodes=4,
            angular_derivatives=E,alpha=alpha,trace_multiplicity=multiplicity)
    np.testing.assert_allclose(trace(r['angular_derivatives'],2),
        trace(r['full_complex_angular_derivatives'],1),rtol=8e-14,atol=8e-14)
