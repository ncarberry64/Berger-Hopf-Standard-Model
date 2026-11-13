"""Complete held-coefficient source-face germs, including algebraic At rate."""
import numpy as np
from scipy.linalg import solve
from .muon_holomorphic_magnetic_inherited_cauchy import signed_field_face_source_first


def signed_field_face_source_complete(forms,forms_first,S,L,wall_germ,wall_first,state_first,base,interior_At_count):
    """Differentiate the literal Gauss/Legendre face and its time Gauss row.

    All coefficients are constant on the declared cell. Qtt is the caller's
    actual declared source second germ. No physical jerk or At acceleration
    is invented: M/ BF At-rate columns vanish in the underlying action.
    """
    answer=signed_field_face_source_first(forms,forms_first,S,L,wall_first[:2],state_first,base,interior_At_count)
    na=int(interior_At_count);Sa,Sd=S[:,:na],S[:,na:];nd=Sd.shape[1]
    K,BF,BR,M=[forms[n]for n in('K','B_forward','B_reverse','M')]
    A=np.block([[Sd.T@M@Sd,Sd.T@BR@Sa],[Sa.T@BF@Sd,Sa.T@K@Sa]])
    f,ft=base['total_field'],base['total_coordinate_rate'];known_second=L@np.asarray(wall_germ[2]).reshape(L.shape[1],f.shape[1])
    vd=solve(Sd.T@M@Sd,Sd.T@(base['canonical_momentum_time']-BR@ft-M@known_second),assume_a='gen')
    ftt=Sd@vd+known_second;complete=[];rows=[]
    for k in range(len(state_first)):
        dK,dBF,dBR,dM=[forms_first[n][k]for n in('K','B_forward','B_reverse','M')]
        df=answer['total_field_first'][k];dft=answer['action_coordinate_rate_first'][k]
        dknown2=L@np.asarray(wall_first[2][k]).reshape(L.shape[1],f.shape[1])
        dpdot=Sd.T@(dK@f+K@df+dBF@ft+BF@dft)
        top=dpdot-Sd.T@(dM@ftt+dBR@ft+M@dknown2+BR@dft)
        bottom=-Sa.T@(dK@ft+dBF@ftt+K@dft+BF@dknown2)
        eta=solve(A,np.r_[top,bottom],assume_a='gen');rate=dft+Sa@eta[nd:]
        complete.append(rate);rows.append(A@eta-np.r_[top,bottom])
    answer.update(total_coordinate_rate_first=np.array(complete),original_time_Gauss_and_momentum_first_rows=np.array(rows),
        original_dynamic_coordinate_acceleration=vd,At_time_rate_first_computed_in_declared_constant_cell=True)
    return answer
