import json
from hashlib import sha256
import numpy as np
import pytest
from bhsm.interface.muon_global_current_wall_loader import GlobalCurrentWallLoader
from bhsm.interface.muon_chronological_spectral_blocks import homogeneous_scalar_degree_reduction


def fixture(tmp_path):
    rng=np.random.default_rng(427);current=tmp_path/'current';action=tmp_path/'action'
    current.mkdir();action.mkdir();ca={};aa={}
    def save(folder,archives,name,**data):
        p=folder/name;np.savez(p,**data);archives[name]={'sha256':sha256(p.read_bytes()).hexdigest()}
    U=homogeneous_scalar_degree_reduction(1)['real_to_complex_coefficient_map']
    ids=np.array([(np.arange(84)[:,None]*4+np.arange(2)[None,:]*2+s).ravel()for s in range(2)])
    W=rng.normal(size=(24,84))
    save(action,aa,'original_n1_angular_and_source_incidence.npz',real_to_complex=U,
         spectator_field_indices=ids,original_wall_map_real=np.kron(W,np.eye(4)))
    y={}
    for s in range(2):
        for spin in(0,5):
            u=rng.normal(size=(3,176,48))+1j*rng.normal(size=(3,176,48))
            p=rng.normal(size=u.shape)+1j*rng.normal(size=u.shape);y[s,spin]=u,p
            save(current,ca,f'spectator_{s}_external_{spin}_nodes_1.npz',original_node_start=1,
                original_node_stop_exclusive=4,source_column_indices=spin*48+np.arange(48),
                original_current_response=u,original_transpose_current_adjoint=p)
    md=dict(archives=ca,full_right_source_columns=288,complete_external_C6_columns=6,
            exact_spectators=2,original_initial_face_held=0,original_free_temporal_nodes=3)
    (current/'result.json').write_text(json.dumps(md));(action/'result.json').write_text(json.dumps({'archives':aa}))
    return current,action,U,ids,W,y


def test_streamed_global_images_equal_independent_source_lifts(tmp_path):
    current,action,U,ids,W,y=fixture(tmp_path);a=GlobalCurrentWallLoader(current,action,cache_chunks=2)
    columns=np.array([1,287]);rows=np.array([[1,.3,-2],[2,.7,2]])
    z=a.point(rows,columns,lapse=.8+.1j,right_clock=.4+.6j)
    change=np.kron(np.eye(84),U);wall=np.kron(W,np.eye(4))
    for label,adj in(('u',False),('p',True)):
        expected=np.zeros((96,2),complex);rate=np.zeros_like(expected)
        for s in range(2):
            # Right u restores with the literal LEFT source lift; p with
            # the RIGHT source lift. Their analytic pairing is transpose.
            lift=(change if adj else change.conj())@wall.T
            for col,global_col in enumerate(columns):
                y0=y[s,global_col//48][int(adj)][:,:168,global_col%48]
                expected[:,col]+=lift[ids[s]].T@(.3*y0[0]+.7*y0[1])
                rate[:,col]+=1j*(.8+.1j)/(.4+.6j)*lift[ids[s]].T@(-2*y0[0]+2*y0[1])
        np.testing.assert_allclose(z[label+'_wall_coefficients'].reshape(96,2),expected,rtol=3e-14,atol=3e-13)
        np.testing.assert_allclose(z[label+'_wall_coordinate_rate'].reshape(96,2),rate,rtol=3e-14,atol=1e-12)
    np.testing.assert_array_equal(a.nodal_directions(0,columns,spectator=0),np.zeros((176,2)))
    assert len(a._cache)<=2
    a.verify_consumed_hashes()


def test_hash_and_exact_incidence_fail_closed(tmp_path):
    current,action,*_=fixture(tmp_path);a=GlobalCurrentWallLoader(current,action)
    with pytest.raises(ValueError):a.nodal_directions(1.5,[1],spectator=0)
    with pytest.raises(ValueError):a.point([[1.5,.3,-2],[2.5,.7,2]],[1],lapse=1,right_clock=1)
    with pytest.raises(ValueError):a.nodal_directions(1,[1.5],spectator=0)
    p=current/'spectator_0_external_0_nodes_1.npz';p.write_bytes(p.read_bytes()+b'changed')
    with pytest.raises(ValueError,match='hash changed'):a.nodal_directions(1,[1],spectator=0)


def test_complete_even_source_spectators_equal_unreduced_current_action():
    from bhsm.interface.muon_global_current_wall_loader import even_current_source_components
    from bhsm.interface.muon_native_unsquared_domain_matching import native_unsquared_domain_matching
    from bhsm.interface.muon_source_directed_em_normal_current import normal_left_current_gaunt
    from bhsm.interface.muon_native_dirac_hamiltonian import lepton_current_hilbert_representation
    from bhsm.interface.muon_piecewise_euclidean_action import FAMILY_INDICES
    rng=np.random.default_rng(452);fi=FAMILY_INDICES[1]
    alpha=lepton_current_hilbert_representation()['alpha'][:,fi][:,:,fi]
    q=[];sources=[];parts=[]
    for edge in range(2):
        for p1 in(.211324865405187,.788675134594813):
            H=np.diag(np.linspace(.2,.7,6))
            q.append(dict(H=H,Hsharp=H,R=.9,Rsharp=.9,right_clock=1,reflected_clock=1,
                measure=.25,original_holomorphic_measure=.25*(1+.1j),
                rows=((edge,1-p1,-2),(edge+1,p1,2)),index=len(q)))
            JR=rng.normal(size=(60,3))+1j*rng.normal(size=(60,3))
            LT=rng.normal(size=(3,60))+1j*rng.normal(size=(3,60))
            sources.append((JR,LT));parts.append(even_current_source_components(JR,LT))
    full=native_unsquared_domain_matching(q,temporal_nodes=3,
        angular_derivatives=normal_left_current_gaunt()['internal_derivatives'],alpha=alpha,
        source_sampler=lambda a:sources[a['index']])
    total={}
    for k in range(4):
        n=parts[0][k]['degree'];E=homogeneous_scalar_degree_reduction(n)['angular_derivatives']
        def source(a):
            z=parts[a['index']][k];return z['right_source'],z['literal_left']
        r=native_unsquared_domain_matching(q,temporal_nodes=3,angular_derivatives=E,alpha=alpha,source_sampler=source)
        for key in('analytic_current','analytic_factor_current','geometric_current','geometric_factor_current'):
            total[key]=total.get(key,0)+r[key]
    for key,v in total.items():np.testing.assert_allclose(v,full[key],rtol=2e-13,atol=2e-13)
