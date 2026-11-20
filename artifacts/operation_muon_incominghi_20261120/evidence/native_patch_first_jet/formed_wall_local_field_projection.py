"""Local projected curvature only; does not provide a physical incident-field match."""
import sys,json
from pathlib import Path
import numpy as np
from scipy.linalg import null_space
f=Path(__file__).resolve();p=f.parents[1];sys.path.insert(0,str(p))
from source_retained_magnetic import wall_data
from source_action_magnetic_kernel import bracket
z=np.load(f.with_name('formed_n0_wall_spin_transfer.npz'));D=z['action_A'];g=z['spin_gap_covector']
raw=np.load(p/'incoming_history.npz')['hi_raw_fields'];own=wall_data(raw)
A=own['connection'][2:];H=raw[260:264];Q=own['charge'];q=Q/np.linalg.norm(Q);R=own['R4']
def projector(h):
    tmp=raw.copy();tmp[260:264]=h
    q=wall_data(tmp)['charge']
    return q/np.linalg.norm(q)
def readout(A,q):
    return np.array([q@ (2*A[2]),q@(2*A[2]+bracket(A[0],A[1]).real)])/R**2
rows={}
for name,axis in [('central',np.eye(4)[3]),('H_aligned',q)]:
    e=np.zeros(16);e[8:12]=axis
    V=null_space(e[None]);T=e-V@np.linalg.solve(V.T@D@V,V.T@D@e)
    v,h=T[:12].reshape(3,4),T[12:]
    a,b,c,d=H; da,db,dc,dd=h
    P=np.array([2*(a*b+c*d),2*(a*d-c*b),a*a+c*c-b*b-d*d])
    DP=np.array([2*(da*b+a*db+dc*d+c*dd),2*(da*d+a*dd-dc*b-c*db),2*(a*da+c*dc-b*db-d*dd)])
    HH=H@H
    dq=np.r_[-np.sqrt(2)*(DP/HH-P*(2*H@h)/HH**2),0.]/np.linalg.norm(Q)
    X=np.array([2*A[2],2*A[2]+bracket(A[0],A[1]).real])
    Y=np.array([2*v[2],2*v[2]+(bracket(v[0],A[1])+bracket(A[0],v[1])).real])
    value=(Y@q+X@dq)/R**2
    fd=(readout(A+1e-6*v,projector(H+1e-6*h))-readout(A-1e-6*v,projector(H-1e-6*h)))/2e-6
    assert np.linalg.norm(value-fd)<1e-7
    rows[name]={'Abelian_spatial_curl_axis_derivative':value[0],'Higgs_projected_full_curvature_derivative':value[1],'Higgs_direction_contact':(X@dq/R**2).tolist(),'coordinate_gap_per_local_curl_projection':float(g@T/value[0]),'coordinate_gap_per_local_full_projection':float(g@T/value[1]),'FD_error':float(np.linalg.norm(value-fd))}
# A combination of the two separately held directions whose local Abelian axial curvature
# vanishes. Its reaction is not zero: it may need loads in the complementary channel.
r1,r2=rows.values();a1=r1['Abelian_spatial_curl_axis_derivative'];a2=r2['Abelian_spatial_curl_axis_derivative']
G1=a1*r1['coordinate_gap_per_local_curl_projection'];G2=a2*r2['coordinate_gap_per_local_curl_projection']
out={'scope':'fixed geometry, standing n0 wall, local curl and projected nonabelian curvature from saved response; not physical photon B or laboratory moment','rows':rows,'abelian_axial_null_combination':{'weights_central_and_aligned':[1,-a1/a2], 'linear_coordinate_gap_response':G1-a1/a2*G2}}
f.with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2))
