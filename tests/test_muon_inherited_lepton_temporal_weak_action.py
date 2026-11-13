import numpy as np
from bhsm.interface.muon_inherited_lepton_temporal_weak_action import smooth_temporal_trial


def test_weak_factor_contains_time_contact_once():
    # Independently integrate the weak factor and its strong by-parts
    # expression on smooth Dirichlet tests with noncommuting Ω and W.
    W0=np.array([[2,.3],[.3,1.]],complex)
    W1=np.array([[.2,.7j],[-.7j,-.4]],complex)
    O=np.array([[.1j,.2],[-.2,-.3j]])
    x,w=np.polynomial.legendre.leggauss(16)
    weak=np.zeros((4,4),complex);strong=weak.copy();omitted=weak.copy()
    for t,wt in zip((x+1)/2,w/2):
        b,d=smooth_temporal_trial(t,1.);dd=np.array([-8.,2*d[0]**2-16*b[0]])
        V=np.hstack([z*np.eye(2) for z in b]);D=np.hstack([z*np.eye(2) for z in d]);DD=np.hstack([z*np.eye(2) for z in dd])
        W=W0+t*W1;A=D+(O+W)@V
        core=-DD-2*O@D-O@O@V+W@W@V-(W1+O@W-W@O)@V
        weak+=wt*A.conj().T@A;strong+=wt*V.conj().T@core
        omitted+=wt*V.conj().T@W1@V
    np.testing.assert_allclose(weak,strong,atol=2e-14,rtol=2e-14)
    assert np.linalg.norm(omitted)>.1
    assert np.linalg.norm(weak-(strong-omitted))>.1


def test_physical_clock_gram_is_not_coordinate_gram():
    # For a constant lapse the derivative term is 1/N, while the Gram is
    # N.  This independently detects a missing proper-time measure.
    x,w=np.polynomial.legendre.leggauss(12);N=.7
    kinetic=np.zeros((2,2));gram=kinetic.copy()
    for t,wt in zip((x+1)/2,w/2):
        b,d=smooth_temporal_trial(t,1.);kinetic+=wt*np.outer(d,d)/N;gram+=wt*N*np.outer(b,b)
    np.testing.assert_allclose(kinetic[0,0],16/(3*N),rtol=1e-14)
    np.testing.assert_allclose(gram[0,0],8*N/15,rtol=1e-14)
    assert np.linalg.det(gram)>0
