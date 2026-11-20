"""Source-restricted amplitude-force reduction of the saved formed-muon trial.

No exterior impedance, incident state, or physical magnetic moment is chosen.
Rebuild only the original 84-coordinate action at 96 quadrature points, then
compare the new projection against the saved 384-point action. One worker.
"""
import sys
from pathlib import Path
assert sys.flags.isolated and sys.flags.no_site
import argparse,hashlib,json,os
ap=argparse.ArgumentParser();ap.add_argument('--site-packages',required=True);ap.add_argument('--output',required=True)
args=ap.parse_args()
runtime=Path(sys.base_prefix).resolve();site=Path(args.site_packages).resolve()
assert site.is_relative_to(runtime) and site.name=='site-packages'
assert all(Path(p).resolve().is_relative_to(runtime) for p in sys.path)
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
sys.dont_write_bytecode=True
root=Path(__file__).resolve().parents[2];p=root/'artifacts/operation_muon_incominghi_20261120/evidence'
source_hashes={}
for line in (p/'SHA256SUMS').read_text().splitlines():
    h,name=line.split('  ',1);path=(p/name).resolve()
    assert path.is_relative_to(p.resolve()) and hashlib.sha256(path.read_bytes()).hexdigest()==h
    source_hashes[name]=h
sys.path[:0]=[str(site),str(p)]
if sys.platform=='win32':
    import platform,sysconfig
    win=sys.getwindowsversion();arch={'win-amd64':'AMD64','win-arm64':'ARM64','win32':'x86'}[sysconfig.get_platform()]
    platform._uname_cache=platform.uname_result('Windows','',f'{win.major}.{win.minor}',f'{win.major}.{win.minor}.{win.build}',arch)
def hook(e,d):
    if e in ('subprocess.Popen','os.system','socket.connect','socket.getaddrinfo'):raise RuntimeError(e)
sys.addaudithook(hook)
import numpy as np
from source_retained_magnetic import wall_data
raw=np.load(p/'incoming_history.npz')['hi_raw_fields'];w=wall_data(raw);n=w['lapse'];rad=w['R4']
ops=np.load(p/'incoming_spin_operators.npz');H=ops['H_coordinate_time'][-1,:6,:6]
cur=np.load(p/'independent_review/native_spin_odd_current.npz');rho=cur['incoming_density_difference6']
pair=np.load(p/'independent_review/n0_spin_pair_audit.npz')['incoming_approximate_n0_spin_pair'][:6]
eig,U=np.linalg.eigh(H);idx=np.argmax(abs(pair.conj().T@U)**2,axis=1)
rhox=np.outer(U[:,idx[1]],U[:,idx[1]].conj())-np.outer(U[:,idx[0]],U[:,idx[0]].conj())
pauli=np.array([[[0,1],[1,0]],[[0,-1j],[1j,0]],[[1,0],[0,-1]]],complex)
G=np.zeros((4,6,6),complex);alpha=np.zeros((3,6,6),complex)
for k in range(3):
    G[k,:4,:4]=-1j*np.kron(pauli[k]/2,np.eye(2))/np.sqrt(2)
    alpha[k,:4,:4]=-np.kron(np.eye(2),pauli[k]);alpha[k,4:,4:]=pauli[k]
G[3]=-1j*np.diag([-.5]*4+[-1.]*2)/np.sqrt(10/3)
gauge=(-1j*n/rad*np.einsum('aij,kjl->akil',alpha,G)).reshape(12,6,6)
y=ops['family_yukawa'][1];dH=[]
for s in np.eye(4):
    c=s[:2]+1j*s[2:];Y=y*np.kron(c[:,None],np.eye(2))
    dH.append(n*np.block([[np.zeros((4,4)),Y],[Y.conj().T,np.zeros((2,2))]]))
V=np.concatenate([gauge,dH]);gx=np.einsum('aij,ji->a',V,rhox).real;gs=np.einsum('aij,ji->a',V,rho).real
z=np.load(p/'native_patch_first_jet/formed_n0_wall_spin_transfer.npz');A=z['action_A'];g=z['spin_gap_covector']
C=np.load(p/'native_patch_first_jet/formed_n0_equal_local_field_test.npz')['field_covector']
j=np.load(p/'native_patch_first_jet/formed_higgs_invariant_companion.npz')['invariant_companion']
kh=np.load(p/'native_n0_coupled_static.npz')['KH20'];sheet=kh[19,np.r_[np.arange(8,20),np.arange(4)]]
out=dict(indices=idx.tolist(),eigenvalues=eig.tolist(),rho_difference=float(np.linalg.norm(rhox-rho)),
  g_difference=float(np.linalg.norm(gx-g)),saved_g_reconstruction=float(np.linalg.norm(gs-g)),
  saved_density_commutator=float(np.linalg.norm(H@rho-rho@H)),pair_gram=(pair.conj().T@pair).real.tolist(),cases={})
for name,gg in [('saved',g),('tracked_exact6',gx)]:
    t=np.linalg.solve(A.T,gg)
    for key,R in [('field',C),('phase',np.vstack([C,j])),('both',np.vstack([C,j,sheet]))]:
        F=np.linalg.solve(A.T,R.T).T;c=np.linalg.lstsq(F.T,t,rcond=None)[0];rr=t-F.T@c
        out['cases'][name+'_'+key]=dict(norm=float(np.linalg.norm(rr)),coeff=c.tolist(),residual=rr.tolist())
z=np.load(p/'native_n0_coupled_static.npz');K,L,b,I=z['K84'],z['lift84x20'],z['boundary20'],z['interior64']
Rt=np.linalg.solve(A.T,(K@L[:,4:])[b[:4]].T).T
R=np.vstack([C,j,sheet]);F=np.linalg.solve(A.T,R.T).T
constraints={'readouts':F,'plus_zero_scalar_force':np.vstack([F,np.eye(16)[12:]]),
  'plus_zero_temporal_reaction':np.vstack([F,Rt]),
  'plus_both_zero_diagnostics':np.vstack([F,np.eye(16)[12:],Rt])}
radialH=np.r_[np.zeros(12),raw[260:264]/np.linalg.norm(raw[260:264])]
constraints['plus_Higgs_amplitude_force']=np.vstack([F,radialH])
out['constraint_tests']={}
t=np.linalg.solve(A.T,g)
for name,E in constraints.items():
    scale=np.linalg.norm(E,axis=1);En=E/np.where(scale>0,scale,1)[:,None]
    u,sv,v=np.linalg.svd(En,full_matrices=True)
    cases=[]
    for cut in (1e-8,1e-10,1e-12,1e-14):
        rank=int(np.sum(sv>cut*sv[0]));N=v[rank:].T;rr=N@(N.T@t)
        cases.append(dict(cut=cut,rank=rank,projection=float(np.linalg.norm(rr)),
           null_residual=float(np.linalg.norm(En@rr)/np.linalg.norm(rr)) if np.linalg.norm(rr) else 0))
    out['constraint_tests'][name]=dict(singular=sv.tolist(),cases=cases)
def reduce(rows,target):
    scale=np.linalg.norm(rows,axis=1);rr=rows/scale[:,None]
    c=np.linalg.lstsq(rr.T,target,rcond=None)[0]/scale
    return c,target-rows.T@c,np.linalg.svd(rr,compute_uv=False)
E=np.vstack([F,radialH]);coef,remainder,sv=reduce(E,t)
out['radial_force_reduction']=dict(coefficients=coef.tolist(),residual=float(np.linalg.norm(t-E.T@coef)),
  radial_force_covector=radialH.tolist(),remaining_force_covector=remainder.tolist(),
  scaled_singular_values=sv.tolist(),scaled_condition=float(sv[0]/sv[-1]))
# Algebraic witness for local underdetermination, NOT a supplied exterior load.
# Preserve all five readouts and zero temporal reaction while varying only
# the measured Higgs-amplitude force projection by one coordinate unit.
W=np.vstack([F,Rt,radialH]);rhs=np.r_[np.zeros(9),1.]
ws=np.linalg.norm(W,axis=1);f=np.linalg.lstsq(W/ws[:,None],rhs/ws,rcond=None)[0]
u=np.linalg.solve(A,f);u84=L@np.r_[np.zeros(4),u];p84=K@u84
out['local_witness']=dict(classification='LOCAL_CONSTRAINT_WITNESS_NOT_PHYSICAL_EXTERIOR',force=f.tolist(),state=u.tolist(),
  rank=int(np.linalg.matrix_rank(W/ws[:,None])),constraint_error=float(np.linalg.norm(W@f-rhs)),
  original_bulk_gauss_error=float(np.linalg.norm(p84[I])),temporal_reaction_error=float(np.linalg.norm(p84[b[:4]])),
  spin_gap=float(g@u),predicted_amplitude_term=float(coef[-1]),force_norm=float(np.linalg.norm(f)),
  remaining_contraction=float(remainder@f))
assert out['local_witness']['constraint_error']<1e-10
assert out['local_witness']['original_bulk_gauss_error']<2e-10
assert abs(g@u-coef[-1])<1e-10
# Higgs-amplitude forces are orthogonal to every infinitesimal compact gauge
# orbit. This proves only that gauge symmetry cannot fix their scalar value.
gh=np.concatenate((-1j*pauli/(2*np.sqrt(2)),(-.5j*np.eye(2)/np.sqrt(10/3))[None]))
gr=np.array([np.block([[a.real,-a.imag],[a.imag,a.real]]) for a in gh])
h=raw[260:264];noether=np.einsum('i,aij,j->a',h/np.linalg.norm(h),gr,h)
out['gauge_orbit_amplitude_pairing']=noether.tolist()
assert np.linalg.norm(noether)<1e-14
# Passive Spin/SU(2) frame change, with independent covectors transformed
# along with the action. This is representation covariance, not a proof
# of native moving-domain Ward completion.
theta=.37;U2=np.cos(theta/2)*np.eye(2)-1j*np.sin(theta/2)*pauli[1]
O=np.array([[np.trace(pauli[a]@U2@pauli[c]@U2.conj().T).real/2 for c in range(3)] for a in range(3)])
O4=np.eye(4);O4[:3,:3]=O
TH=np.block([[U2.real,-U2.imag],[U2.imag,U2.real]])
T=np.zeros((16,16));T[:12,:12]=np.kron(np.eye(3),O4);T[12:,12:]=TH
Us=np.eye(6,dtype=complex);Us[:4,:4]=np.kron(U2,np.eye(2))
Vp=np.einsum('ab,aij->bij',T,V)
Vp=np.einsum('ij,ajk,kl->ail',Us.conj().T,Vp,Us)
rhop=Us.conj().T@rho@Us
gp=np.einsum('aij,ji->a',Vp,rhop).real
Ap=T.T@A@T;Rp=R@T;hp=T.T@radialH;tp=np.linalg.solve(Ap.T,gp)
Fp=np.linalg.solve(Ap.T,Rp.T).T;cp,remp,_=reduce(np.vstack([Fp,hp]),tp)
out['frame_check']=dict(spin_covector_error=float(np.linalg.norm(gp-T.T@g)),
  coefficients_error=float(np.linalg.norm(cp-coef)),
  residual_covariance_error=float(np.linalg.norm(remp-T.T@remainder)),
  gauge_amplitude_force_invariant_error=float(abs(hp@(T.T@f)-radialH@f)))
assert max(out['frame_check'].values())<1e-10
# Convert the entire action and spin energy to wall proper time. The
# weighted sheet row is an action covector and is divided by the same lapse.
Rp=R.copy();Rp[-1]/=n
Fp=np.linalg.solve((A/n).T,Rp.T).T;tp=np.linalg.solve((A/n).T,g/n)
cp,remp,_=reduce(np.vstack([Fp,radialH]),tp)
expected=coef.copy();expected[:4]/=n
out['proper_clock_check']=dict(lapse=float(n),coefficient_error=float(np.linalg.norm(cp-expected)),
  witness_gap_error=float(abs((cp@np.r_[Rp@u,radialH@(f/n)]+remp@(f/n))-(g@u)/n)))
assert max(out['proper_clock_check'][k] for k in ('coefficient_error','witness_gap_error'))<1e-10
# A real quadrature change of the SAME owned action, with no exterior solve
# and no new radial state/profile. Current/refined branches remain trial-only.
from native_n0_action_builder import build
K96,B96,M96=build(raw,order=96)
Ki=K96[np.ix_(I,I)];Cib=K96[np.ix_(I,b)]
UU,ss,VV=np.linalg.svd(Ki);keep=ss>ss[0]*1e-11
Y=-(VV[keep].T/ss[keep])@UU[:,keep].T@Cib
L96=np.zeros((84,20));L96[b]=np.eye(20);L96[I]=Y
D96=L96.T@K96@L96;A96=D96[4:,4:]
t96=np.linalg.solve(A96.T,g);F96=np.linalg.solve(A96.T,R.T).T
c96,rem96,sv96=reduce(np.vstack([F96,radialH]),t96)
bare96=t96-F96.T@np.linalg.lstsq(F96.T,t96,rcond=None)[0]
out['quadrature_96_vs_saved_384']=dict(interior_rank=int(keep.sum()),
  original_interior_compatibility=float(np.linalg.norm(Ki@Y+Cib)),
  K84_max_difference=float(np.max(abs(K96-K))),A16_max_difference=float(np.max(abs(A96-A))),
  amplitude_coefficient_96=float(c96[-1]),amplitude_coefficient_384=float(coef[-1]),
  amplitude_coefficient_difference=float(abs(c96[-1]-coef[-1])),
  unreduced_remainder_norm_96=float(np.linalg.norm(bare96)),
  reduced_remainder_norm_96=float(np.linalg.norm(rem96)),
  coefficients_96=c96.tolist(),scope='Quadrature refinement on the original four radial profiles; no radial-basis or exterior-domain convergence claim.')
assert abs(c96[-1]-coef[-1])<1e-10
assert np.linalg.norm(rem96)<1e-10
assert np.linalg.norm(remainder)<1e-10
assert abs(coef[-1])>1e-7
assert out['saved_g_reconstruction']<1e-12 and out['g_difference']<1e-10
for module in tuple(sys.modules.values()):
    loc=getattr(module,'__file__',None)
    if loc:
        path=Path(loc).resolve()
        assert path.is_relative_to(runtime) or path.is_relative_to(p.resolve()) or path==Path(__file__).resolve(),str(path)
out.update(classification='FINITE_CONDITIONAL_SOURCE_PROJECTION',physical_guard='2e-10',physical_moment=None,
  physical_uncertainty=None,physical_exterior_supplied=False,physical_outgoing_branch_evaluated=False,
  source_hashes=source_hashes,passed=True,
  missing_datum='chi_H=(H/|H|).T f_H on the same formed-background held-incident matched source, conditional on the five readouts; retain numerical remainder epsilon.T f',
  noether_scope='Radial Higgs-amplitude force is gauge invariant. This does not determine the native-relative reaction or allow assigning it zero.')
Path(args.output).write_bytes((json.dumps(out,sort_keys=True,indent=2)+'\n').encode())
print(json.dumps({k:out[k] for k in ('radial_force_reduction','local_witness','frame_check','proper_clock_check','quadrature_96_vs_saved_384','passed')},indent=2))
