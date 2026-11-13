import numpy as np
from bhsm.interface.muon_reached_geometry_canonical_return import sourced_original_canonical_batch,structural_geometry_port_lift,complete_natural_boundary_work


def test_independent_sourced_midpoint_and_literal_dual():
    rng=np.random.default_rng(4721);n=2;m=1;d=3*n+m
    H=rng.normal(size=(5,5))+1j*rng.normal(size=(5,5));H[2:,2:]+=4*np.eye(3)
    initial=rng.normal(size=(4,3))+1j*rng.normal(size=(4,3));g=rng.normal(size=(5,3))+1j*rng.normal(size=(5,3));h=.07+.02j
    T=rng.normal(size=(2,n))+1j*rng.normal(size=(2,n));F=np.empty((0,3))
    a=sourced_original_canonical_batch(H,h,F,initial,np.zeros_like(initial),g,T)
    # Independently assemble the nonlinear quadratic action midpoint rows.
    def rows(z):
        xf,pf,v,y=z[:n],z[n:2*n],z[2*n:3*n],z[3*n:]
        eta=np.vstack(((initial[:n]+xf)/2,v,y));cot=H@eta+g
        return np.vstack((xf-initial[:n]-h*v,pf-initial[n:]-h*cot[:n],cot[n:2*n]-(initial[n:]+pf)/2,cot[2*n:]))
    zero=np.zeros((d,3),complex);r0=rows(zero)
    J=np.column_stack([(rows(np.eye(d,dtype=complex)[:,j,None]@np.ones((1,3)))-r0)[:,0]for j in range(d)])
    answer=np.linalg.solve(J,-r0)
    out=a['canonical_final_high']+a['canonical_final_low']
    assert np.max(abs(out-answer[:4]))<3e-15
    assert a['original_rows_upper']<1e-28
    assert a['literal_pairing_upper']<1e-28


def test_named_port_coordinate_lift_and_both_boundary_terms():
    B=np.zeros((3,40),complex);B[:,[0,1,37]]=[[1,.2j,.1],[-.3,2,.2],[.1j,.4,1.7j]]
    a=structural_geometry_port_lift(B)
    assert np.max(abs(B@a['lift']-np.eye(3)))<4e-16
    assert np.count_nonzero(a['lift'][[i for i in range(40)if i not in (0,1,37)]])==0
    rng=np.random.default_rng(514);z=rng.normal(size=(80,4))+1j*rng.normal(size=(80,4));w=2*z
    pi=rng.normal(size=40);pf=rng.normal(size=40)
    b=complete_natural_boundary_work(z,0*z,w,0*w,pi,pf,coordinate_interval=.2)
    actual=b['complete_boundary_work_high']+b['complete_boundary_work_low']
    assert np.max(abs(actual-(pf@w[:40]-pi@z[:40])[None]))<4e-15
    assert np.linalg.norm(actual-b['terminal_cotangent_work'])>1
