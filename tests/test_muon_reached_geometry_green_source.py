import numpy as np
from bhsm.interface.muon_reached_geometry_canonical_return import sourced_original_canonical_batch
from bhsm.interface.muon_reached_geometry_green_source import canonical_green_source_cell


def test_sourced_changing_two_cells_preserve_boundary_and_unsymmetric_work():
    rng=np.random.default_rng(544);n=2;m=1;nu=4;nv=3
    u=rng.normal(size=(4,nu))+1j*rng.normal(size=(4,nu));v=rng.normal(size=(4,nv))+1j*rng.normal(size=(4,nv))
    ulo=0*u;vlo=0*v;first=u.copy();firstv=v.copy();total=0
    for h in (.07+.02j,.04-.01j):
        H=rng.normal(size=(5,5))+1j*rng.normal(size=(5,5));H[2:,2:]+=5*np.eye(3)
        g=rng.normal(size=(5,nv))+1j*rng.normal(size=(5,nv));F=np.empty((0,3));T=np.eye(n)
        U=sourced_original_canonical_batch(H,h,F,u,ulo,np.zeros((5,nu)),T)
        V=sourced_original_canonical_batch(H,h,F,v,vlo,g,T)
        a=canonical_green_source_cell(H,h,u,ulo,U['canonical_final_high'],U['canonical_final_low'],
            v,vlo,V['canonical_final_high'],V['canonical_final_low'],
            U['stage_direction_high'],U['stage_direction_low'],V['stage_direction_high'],V['stage_direction_low'],
            g,U['frame_reaction_rows'],V['frame_reaction_rows'])
        assert a['green_identity_upper']<1e-28
        assert np.linalg.norm(a['literal_action_asymmetry_work'])>.01
        assert np.linalg.norm(a['initial_boundary_pairing'])>.01
        total=total+a['full_source_work']+a['literal_action_asymmetry_work']+a['named_frame_work']
        u,ulo=U['canonical_final_high'],U['canonical_final_low'];v,vlo=V['canonical_final_high'],V['canonical_final_low']
    W=lambda a,b:a[:n].T@b[n:]-a[n:].T@b[:n]
    assert np.max(abs(W(u+ulo,v+vlo)-W(first,firstv)-total))<4e-15
