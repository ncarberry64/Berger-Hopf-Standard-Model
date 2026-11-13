import numpy as np
from bhsm.interface.muon_global_causal_laplace_response import (
    represented_global_proper_clock,global_causal_laplace_response,
    global_laplace_weak_boundary_identity)


def test_complex_clock_Laplace_integral_keeps_original_density_and_endpoints():
    nodes=6;g,gw=np.polynomial.legendre.leggauss(8);f=(g+1)/2
    rows=np.array([[(j,1-a,-1),(j+1,a,1)]for j in range(nodes-1)for a in f],complex)
    w=np.full(len(rows),.8+.3j);m=np.tile(gw/2,nodes-1)*w
    clock=represented_global_proper_clock(rows,w,m,temporal_nodes=nodes)
    np.testing.assert_allclose(clock['proper_clock_nodes'],(.8+.3j)*np.arange(nodes),atol=3e-15)
    birth=2;x=np.maximum(np.arange(nodes)-birth,0).reshape(nodes,1,1).astype(complex)
    s=np.array([.23,.4+.1j]);a=global_causal_laplace_response(rows,w,m,x,np.ones((1,1)),s,birth_node=birth)
    T=(nodes-1-birth)*w[0]
    expected=(1-np.exp(-s*T)*(1+s*T))/(s*s*w[0])
    np.testing.assert_allclose(a['global_future_Laplace_Green'][:,0,0],expected,rtol=3e-14,atol=4e-15)
    assert np.max(abs(a['global_future_Laplace_Green'].imag))>.01
    assert np.max(abs(a['before_source_Laplace_pairing']))==0
    b=np.zeros((nodes-1,1,1),complex);b[birth-1]=1
    final=np.array([[.7+.2j]]);r=np.zeros_like(b);r[-1]=final
    q=global_laplace_weak_boundary_identity(r,b,np.ones((1,1)),clock['proper_clock_nodes'],s,
        np.zeros((1,1)),final,birth_node=birth)
    np.testing.assert_allclose(q['global_weak_source_endpoint_identity'],0.,atol=3e-16)
    assert np.linalg.norm(q['final_canonical_endpoint_contact'])>0
