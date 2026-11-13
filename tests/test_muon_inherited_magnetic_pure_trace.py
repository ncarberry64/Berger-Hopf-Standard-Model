import numpy as np
from scipy.linalg import expm
from bhsm.interface.muon_inherited_magnetic_pure_trace import pure_unsquared_magnetic_trace_jets


def test_pure_trace_and_three_source_slots_match_whole_complex_exponential_transfer():
    rng=np.random.default_rng(576132);draw=lambda s:.17*(rng.normal(size=s)+.4j*rng.normal(size=s))
    G=draw((2,4,4));dG=draw((2,2,4,4));I=draw((2,3,4,4));dI=draw((2,2,3,4,4));h=np.array([.23,.31])
    x,w=np.polynomial.legendre.leggauss(10);cells=[];sigmas=[];weights=[];insertions=[];first=[]
    for j in range(2):
        for xx,ww in zip(x,w):
            cells.append(j);sigmas.append((j+(xx+1)/2)/2);weights.append(h[j]*ww/2);insertions.append(I[j]);first.append(dI[j])
    a=pure_unsquared_magnetic_trace_jets(G,dG,h,dict(cell=np.array(cells),sigma=np.array(sigmas),coordinate_weight=np.array(weights),
        insertion=np.array(insertions),insertion_first=np.array(first)))
    def transfer(s,b,c,axis):
        # Independently vary both generators BEFORE either exponential.
        Q=G+s*dG[:,c]+b*I[:,axis]+s*b*dI[:,c,axis]
        return expm(h[1]*Q[1])@expm(h[0]*Q[0])
    step=2e-4
    for axis in range(3):
        actual=(transfer(0,step,0,axis)-transfer(0,-step,0,axis))/(2*step)
        np.testing.assert_allclose(a['magnetic_transfer'][axis],actual,rtol=4e-8,atol=2e-10)
        for c in range(2):
            mixed=(transfer(step,step,c,axis)-transfer(step,-step,c,axis)-transfer(-step,step,c,axis)+transfer(-step,-step,c,axis))/(4*step**2)
            np.testing.assert_allclose(a['magnetic_transfer_first'][c,axis],mixed,rtol=2e-6,atol=4e-9)
    for name in('left_propagator','insertion','right_propagator'):assert np.linalg.norm(a['magnetic_transfer_first_'+name])>1e-3
    np.testing.assert_allclose(a['literal_transpose_identity_defect'],0,atol=2e-16)
    assert not a['physical_boundary_or_pole_or_source_current_normalization_selected']
