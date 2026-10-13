"""Complete finite raw-field Schur jets on an explicitly supplied radial basis.

This matrix action retains every represented opposite-Spin/carrier row. Its
point value boundary is not a retarded selector or normalized physical mode.
"""
import numpy as np


def fixed_radial_field_poisson(K,KE,source,source_energy,*,wall_dimension):
    """Same K inverse for source contact and both energy-state placements."""
    K,KE,S,SE=map(lambda a:np.asarray(a,complex),(K,KE,source,source_energy));nw=int(wall_dimension);ni=len(K)-nw
    if K.shape!=(ni+nw,)*2 or KE.shape!=K.shape or S.ndim!=3 or S.shape[1:]!=K.shape or SE.shape!=S.shape or ni<1 or nw<1:
        raise ValueError('complete raw finite field action and every source/E coefficient required')
    A=K[:ni,:ni];B=K[:ni,ni:];C=K[ni:,:ni]
    X=np.linalg.solve(A,B);Y=np.linalg.solve(A.T,C.T).T
    P=np.r_[-X,np.eye(nw)];L=np.c_[-Y,np.eye(nw)]
    XE=np.linalg.solve(A,KE[:ni,ni:]-KE[:ni,:ni]@X)
    YE=np.linalg.solve(A.T,(KE[ni:,:ni]-Y@KE[:ni,:ni]).T).T
    PE=np.r_[-XE,np.zeros((nw,nw))];LE=np.c_[-YE,np.zeros((nw,nw))]
    Gamma=L@K@P;GammaE=L@KE@P
    contact=np.array([L@s@P for s in S]);left=np.array([LE@s@P for s in S]);right=np.array([L@s@PE for s in S]);energy_contact=np.array([L@s@P for s in SE])
    return dict(original_raw_field_Poisson=P,original_literal_left_field_Poisson=L,
        original_raw_field_Poisson_energy=PE,original_literal_left_field_Poisson_energy=LE,
        finite_raw_field_boundary_equation=Gamma,finite_raw_field_boundary_equation_energy=GammaE,
        source_field_boundary_contact=contact,source_energy_contact=energy_contact,
        source_energy_left_state=left,source_energy_right_state=right,
        complete_source_energy_return=left+energy_contact+right,
        original_right_field_rows=K@P-np.r_[np.zeros((ni,nw)),Gamma],
        original_literal_left_field_rows=L@K-np.c_[np.zeros((nw,ni)),Gamma],
        original_right_energy_field_rows=KE@P+K@PE-np.r_[np.zeros((ni,nw)),GammaE],
        original_literal_left_energy_field_rows=LE@K+L@KE-np.c_[np.zeros((nw,ni)),GammaE],
        normal_mode_or_retarded_tail_boundary_not_selected=True,
        every_represented_interior_field_row_retained=True)
