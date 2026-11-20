from pathlib import Path
import sys,numpy as np,json
o=Path(__file__).resolve().parent;p=o.parent;sys.path.insert(0,str(p))
from source_retained_magnetic import wall_data
raw=np.load(p/'incoming_history.npz')['hi_raw_fields'];w=wall_data(raw);q=w['charge']/np.linalg.norm(w['charge']);G=w['connection'][2:];b=np.sqrt(10/3);y=np.eye(4)[3];z=y-q*q[3];z/=np.linalg.norm(z)
QN=np.linalg.norm(w['charge'])
def z_at(x):
 q=wall_data(x)['charge']/QN; zz=y-q*q[3];return zz/np.sqrt(zz@zz)
Z_H=np.array([z_at(raw+1e-24j*d).imag/1e-24 for d in np.eye(268)[260:264]]).T
zraw=np.r_[np.zeros(8),z,np.zeros(4)]; ze=zraw.copy();ze[12:]=G[2]@Z_H
E=np.load(o/'formed_n0_equal_local_field_test.npz'); W=np.load(o/'formed_n0_wall_spin_transfer.npz');A=W['action_A'];g=W['spin_gap_covector'];C=E['field_covector']
P=lambda v:np.r_[np.kron(np.eye(3),v[:,None]),np.zeros((4,3))]
X=np.linalg.solve(A,np.c_[P(y),P(q)])
def assess(rows):
 d={}
 for tag,F in [('full16',np.eye(16)),('six_force',X)]:
  cf=rows@F;gf=g@F; k=np.linalg.lstsq(cf.T,gf,rcond=None)[0];d[tag]={'relative_residual':float(np.linalg.norm(gf-k@cf)/np.linalg.norm(gf)), 'coefficients':k.tolist()}
 return d
# Local central gauge jet: theta=0 at the point, E3 theta=1; delta A3Y=-1,
# delta H=0 and delta E3 H=-i H/(2b). Not an n0 gauge transformation on the full compact slice.
H=raw[260:262]+1j*raw[262:264];drH=-1j*H/(2*b);central_gauge_companion_raw=-z[3]
phase_contact=-np.sqrt(5)*np.vdot(H,drH).imag/np.vdot(H,H).real
# Constant central gauge transformation belongs to n0, with no dtheta.
cc=np.r_[-H.imag,H.real]/(-2*b)
# Higgs action's axial spatial gauge Hessian alone.
K=np.load(p/'native_n0_coupled_static.npz')['KH20'];wall_axial=np.r_[np.zeros(16),z]
expected=-2/(2*np.pi**2)*w['lapse']*w['R4']*(H.conj()@H).real/5
out=dict(scope='frozen incoming-hi n0 trace; J projected in body coframe. No native outer solution supplied.',raw=assess(np.r_[C,zraw[None]]),covariant=assess(np.r_[C,ze[None]]),Higgs_orientation_contact=ze[12:].tolist(),Higgs_orientation_contact_norm=float(np.linalg.norm(ze[12:])),raw_row_norm=float(np.linalg.norm(zraw)),constant_global_central_gauge_full_companion=float(ze[12:]@cc),local_pure_central_gauge_raw=float(central_gauge_companion_raw),local_pure_central_gauge_phase_contact=float(phase_contact),local_pure_central_gauge_residual=float(central_gauge_companion_raw+phase_contact),native_axial_Higgs_action_curvature=float(wall_axial@K@wall_axial),predicted_by_J_spatial_energy=float(expected))
print(json.dumps(out,indent=2));Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n');np.savez(Path(__file__).with_suffix('.npz'),invariant_companion=ze,raw_companion=zraw,field=C,six_force_state_lift=X)
