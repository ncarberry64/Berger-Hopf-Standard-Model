import numpy as np

from bhsm.interface.muon_continued_connector_field_action import (
    common_field_proper_forms, continued_field_weak_action,
    continued_field_wall_inverse, joint_literal_wall_current_sources,
    joint_wall_current_responses)


def test_common_material_at_pullback_is_literal_action_not_equal_proper_trace():
    rng=np.random.default_rng(832)
    M=rng.normal(size=(5,5));M=M.T@M;M[0]=0;M[:,0]=0
    B=rng.normal(size=(5,5));B[:,0]=0
    K=rng.normal(size=(5,5));K=K+K.T
    x=rng.normal(size=5)+1j*rng.normal(size=5)
    v=rng.normal(size=5)+1j*rng.normal(size=5)
    for N in (.71+.02j,1.19-.04j):
        app=common_field_proper_forms((M,B,K),N,1)
        Me,Be,Ke=app['forms']
        literal=-((1j*N*v)@M@(1j*N*v)/2+x@B@(1j*N*v)+x@K@x/2)/N
        assert abs(v@Me@v/2+x@Be@v+x@Ke@x/2-literal)<2e-13
    # Equal original At values have unequal proper-coordinate values.
    assert -.1j/.71 != -.1j/1.19


def test_complete_weak_inverse_retains_gauss_frames_and_initial_reaction():
    M=np.diag([0.,2.,3.]);B=np.array([[0.,.2,.3],[0.,.1,-.2],[0.,.4,.1]])
    K=np.array([[4.,.4,.1],[.4,3.,.2],[.1,.2,2.]])
    q=[]
    gx,gw=np.polynomial.legendre.leggauss(4)
    for segment,w in enumerate((.7+.1j,.8-.06j)):
        for g,a in zip(gw,gx):
            u=(a+1)/2
            q.append(dict(forms=(M,B,K),right_clock=w,measure=w*g/2,
                          rows=((segment,1-u,-1),(segment+1,u,1))))
    act=continued_field_weak_action(q,temporal_nodes=3,At_count=1,frame_indices=[2])
    P=np.zeros((24,3));P[:3]=np.eye(3)
    app=continued_field_wall_inverse(act,P)
    assert app['original_action_row_residual_max']<4e-15
    assert app['original_Gauss_row_residual_max']<4e-15
    assert app['frame_residual_max']<4e-15
    assert np.linalg.norm(app['initial_face_reaction'])>0
    assert app['field_wall_source_response'].shape==(6,48)
    # Compare the declared derivative action with an independent scalar
    # polynomial evaluation rather than mirroring matrix assembly.
    z=np.arange(9)/13+1j*np.arange(9)[::-1]/17
    total=0j
    for r in q:
        value=sum(p*z[3*j:3*j+3] for j,p,d in r['rows'])
        rate=sum(d*z[3*j:3*j+3] for j,p,d in r['rows'])/r['right_clock']
        total+=r['measure']*(rate@M@rate/2+value@B@rate+value@K@value/2)
    assert abs(z@act['original_all_trace_Hessian']@z/2-total)<3e-14


def test_current_integration_has_literal_two_halves_and_transpose_dual():
    rng=np.random.default_rng(29)
    V=rng.normal(size=(24,6,6))+1j*rng.normal(size=(24,6,6))
    gaunt=rng.normal(size=(3,4,2));C=rng.normal(size=(2,6,12))
    rows=((1,.3,-1),(2,.7,1));weight=.6+.07j
    q=[dict(selected_vertices_common=V,rows=rows,measure=weight)]
    src=joint_literal_wall_current_sources(q,temporal_nodes=3,wall_fields=24,
        right_harmonics=4,even_gaunt=gaunt,left_tests=C)
    # Individual literal right current and left current coefficient,
    # including both independent temporal shape factors.
    assert np.allclose(src['literal_right_current'][4+2,4,96+4*3+2],
                       weight*.3*.7*V[3,1,4])
    expected=sum(C[0,5,2*i+x]*V[3,i,4]*gaunt[1,2,x]
                 for x in range(2) for i in range(6))
    assert np.allclose(src['C_literal_left_current'][0,5,18+4*3+1,96+12+2],
                       weight*.7*.7*expected)
    G=rng.normal(size=(192,192))+1j*rng.normal(size=(192,192))
    out=joint_wall_current_responses(dict(wall_source_Green=G),src)
    Jr=src['literal_right_current'].transpose(2,0,1).reshape(192,-1)
    left=src['C_literal_left_current']
    assert np.allclose(out['wall_u'],G@Jr)
    for axis in range(2):
        assert np.allclose(out['wall_p'][:,axis],G.T@left[axis].reshape(-1,192).T)
    assert not np.allclose(out['wall_p'][:,0],G.conj().T@left[0].reshape(-1,192).T)
