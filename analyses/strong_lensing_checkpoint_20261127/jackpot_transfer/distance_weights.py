"""Known-source-plane geometry, not a fitted Jackpot mass map."""
from pathlib import Path
import json,sys
import numpy as np
from scipy.integrate import quad
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parent/'bhsm_environment_audit'/'pinned_extra'))
from r1_background_geometry import D as R1
def flat(a,b):
    return quad(lambda z:1/np.sqrt(.315*(1+z)**3+.685),a,b,epsabs=1e-12)[0]/(1+b)
def matrix(D,z):
    return np.array([[D(zi,zj)/D(0,zj) if i<j else 0. for i,zi in enumerate(z[:-1])] for j,zj in enumerate(z[1:],1)])
def report(D):
    W=matrix(D,[.222,.609,2.035,5.975])
    old=matrix(D,[.222,.609,2.410,5.975])
    assert np.all(np.diag(W)>0) and np.all(W<1) and np.linalg.matrix_rank(W)==3
    return dict(jackpot_weights=W.tolist(),he0435_weights=matrix(D,[.4546,.7821,1.693]).tolist(),main_response_third_over_first=W[2,0]/W[0,0],
      main_response_change_at_second_pct=100*(W[1,0]/old[1,0]-1),
      first_source_plane_response_change_at_second_pct=100*(W[1,1]/old[1,1]-1))
out={'scope':'Geometry only; deflections evaluated at different impact points; no map identifiability claim from a triangular geometry matrix.',
     'R1':report(R1),'flat_LCDM_Omega_m_0.315':report(flat)}
(P/'distance_weights.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
