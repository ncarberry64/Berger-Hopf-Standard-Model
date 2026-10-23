import numpy as np
from bhsm.interface.muon_chronological_cauchy_trace_current import cauchy_trace_point_sources
from bhsm.interface.muon_chronological_exterior_current_source import exterior_current_point_sources


def test_structural_complete_C6_action_equals_full_Kronecker_interface():
    rng=np.random.default_rng(8041)
    def draw(shape):return rng.normal(size=shape)+1j*rng.normal(size=shape)
    S=dict(literal_right_source=draw((7,288)),literal_left_transpose_source=draw((7,288)))
    F=[draw((6,6))for _ in range(4)];tau=.17+.31j
    a=cauchy_trace_point_sources(S,tau,right_trace=F[0],left_trace=F[1],
        right_trace_energy_first=F[2],left_trace_energy_first=F[3])
    b=exterior_current_point_sources(S,tau,continued_energy=0,
        right_trace_map=np.kron(F[0],np.eye(48)),left_trace_map=np.kron(F[1],np.eye(48)),
        right_trace_map_energy_first=np.kron(F[2],np.eye(48)),
        left_trace_map_energy_first=np.kron(F[3],np.eye(48)))
    for x,y in(('literal_right_source','exterior_right_source'),
                ('literal_left_transpose_source','exterior_left_transpose_source'),
                ('right_energy_source','exterior_right_energy_source'),
                ('left_energy_source','exterior_left_energy_source')):
        np.testing.assert_allclose(a[x],b[y],rtol=3e-15,atol=1e-14)


def test_complete_Cauchy_phase_contacts_cancel_without_projecting_internal_tests():
    rng=np.random.default_rng(2208)
    S={k:rng.normal(size=(9,288))+1j*rng.normal(size=(9,288))for k in
       ('literal_right_source','literal_left_transpose_source')}
    R=rng.normal(size=(6,6))+1j*rng.normal(size=(6,6));L=np.linalg.inv(R).T
    tau=.043+.71j
    a=cauchy_trace_point_sources(S,tau,right_trace=R,left_trace=L,
        right_trace_energy_first=tau*R,left_trace_energy_first=-tau*L)
    np.testing.assert_allclose(a['right_energy_source'],0,atol=4e-15)
    np.testing.assert_allclose(a['left_energy_source'],0,atol=6e-15)
    assert np.linalg.norm(a['literal_right_source']-S['literal_right_source'])>1
    assert a['source_columns'].tolist()==[6,2,6,4]
