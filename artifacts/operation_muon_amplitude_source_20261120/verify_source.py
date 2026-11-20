"""Direct-zero and indirect mixed amplitude source on the owned finite trial.

No native exterior, state, impedance or calibrated photon residue is chosen.
"""
import sys
from pathlib import Path
assert sys.flags.isolated and sys.flags.no_site
import argparse,hashlib,json,os
ap=argparse.ArgumentParser();ap.add_argument('--site-packages',required=True);ap.add_argument('--output',required=True);args=ap.parse_args()
runtime=Path(sys.base_prefix).resolve();site=Path(args.site_packages).resolve()
assert site.is_relative_to(runtime) and site.name=='site-packages'
root=Path(__file__).resolve().parents[2];p=root/'artifacts/operation_muon_incominghi_20261120/evidence'
assert all(Path(x).resolve().is_relative_to(runtime) for x in sys.path)
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[name]='1'
sys.dont_write_bytecode=True;sys.path[:0]=[str(site),str(p)]
manifest={}
for line in (p/'SHA256SUMS').read_text().splitlines():
    h,name=line.split('  ',1);path=(p/name).resolve()
    assert path.is_relative_to(p.resolve()) and hashlib.sha256(path.read_bytes()).hexdigest()==h
    manifest[name]=h
if sys.platform=='win32':
    import platform,sysconfig
    win=sys.getwindowsversion();arch={'win-amd64':'AMD64','win-arm64':'ARM64','win32':'x86'}[sysconfig.get_platform()]
    platform._uname_cache=platform.uname_result('Windows','',f'{win.major}.{win.minor}',f'{win.major}.{win.minor}.{win.build}',arch)
def hook(e,d):
 if e in ('subprocess.Popen','os.system','socket.connect','socket.getaddrinfo'):raise RuntimeError(e)
sys.addaudithook(hook)
import numpy as np
from source_retained_magnetic import wall_data
raw=np.load(p/'incoming_history.npz')['hi_raw_fields'];w=wall_data(raw);h=raw[260:264];v=np.linalg.norm(h);nh=h/v
q=w['charge']/np.linalg.norm(w['charge'])
P=np.zeros((16,3));P[:12]=np.kron(np.eye(3),q[:,None]);s=np.r_[np.zeros(12),nh]
z=np.load(p/'native_n0_coupled_static.npz');K=z['K84'];A=z['Dirichlet_trial_return20'][4:,4:]
KH=z['KH20'];B=KH[np.ix_(np.r_[np.arange(8,20),np.arange(4)],np.r_[np.arange(8,20),np.arange(4)])]
pauli=np.array([[[0,1],[1,0]],[[0,-1j],[1j,0]],[[1,0],[0,-1]]],complex)
gc=np.concatenate((-1j*pauli/(2*np.sqrt(2)),(-.5j*np.eye(2)/np.sqrt(10/3))[None]))
gr=np.array([np.block([[x.real,-x.imag],[x.imag,x.real]]) for x in gc]);Tq=np.einsum('c,cij->ij',q,gr)
Om=np.einsum('fc,cij->fij',w['connection'],gr);DH=Om@h;DH[0]+=raw[264:268]
weights=np.array([w['R4']**3/w['lapse']]+[-w['lapse']*w['R4']]*3)/(2*np.pi**2)
source=[];weak=[]
for i,mu in enumerate((0,2,3,4)):
    # General scalar weak-test mixed row from both DH placements.
    row=2*weights[i]*(Om[mu].T@Tq@h+Tq.T@DH[mu])
    source.append(row);weak.append(float(nh@row))
source=np.array(source)
columns=np.column_stack([P,s]);_,sv,Vh=np.linalg.svd(columns.T,full_matrices=True);X=Vh[4:].T
R0=columns.T@A@columns;AX=X.T@A@X;coupling=X.T@A@columns;Y=-np.linalg.solve(AX,coupling)
direct=float(s@A@P[:,2]);indirect=float(s@A@X@Y[:,2]);eff=R0+columns.T@A@X@Y
U=columns+X@Y;f=A@U
# Independent algebraic dual, no identification with a guessed exterior.
dual=np.linalg.solve(AX.T,X.T@A.T@s)
return_dual=-dual@(X.T@A@P)
L=z['lift84x20'];I=z['interior64'];bound=z['boundary20']
full=K @ L @ np.vstack([np.zeros((4,4)),U])
out=dict(q=q.tolist(),H_norm=v,TqH_norm=float(np.linalg.norm(Tq@h)),
   DH_norms=np.linalg.norm(DH,axis=1).tolist(),
   charge_connection_commutator_norms=[float(np.linalg.norm(O@Tq-Tq@O)) for O in Om],
   mixed_source_time_and_space=source.tolist(),direct_amplitude_sources=weak,
   direct_KH_amplitude_photon=(s@B@P).tolist(),direct_A_amplitude_photon=(s@A@P).tolist(),
   direct_scalar_photon_block=B[12:]@P,source_Hessian_discrepancy=float(np.linalg.norm(source[1:].T-B[12:]@P)),
   complement_singular_values=np.linalg.svd(AX,compute_uv=False).tolist(),
   direct_axial_mixed=direct,returned_axial_mixed=indirect,effective_retained_matrix=eff.tolist(),
   complement_equation_error=float(np.linalg.norm(X.T@f)),
   Higgs_complement_return_by_photon=(U[12:,:3]-P[12:]).tolist())
out['direct_scalar_photon_block']=out['direct_scalar_photon_block'].tolist()
out['independent_dual']=dict(covector=dual.tolist(),returned_three_photon_couplings=return_dual.tolist(),
    left_equation_error=float(np.linalg.norm(AX.T@dual-X.T@A.T@s)),
    right_left_difference=float(np.linalg.norm(return_dual-s@A@X@Y[:,:3])))
out['common_trial_checks']=dict(interior_Gauss_error=float(np.linalg.norm(full[I])),
    held_temporal_reaction_norm=float(np.linalg.norm(full[bound[:4]])),
    temporal_reaction_set_to_zero=False,common_higgs_sheet_count=1,
    orthonormal_basis_error=float(np.linalg.norm(np.c_[columns,X].T@np.c_[columns,X]-np.eye(16))))
assert out['TqH_norm']<1e-14
assert max(abs(x) for x in weak)<1e-14
assert out['source_Hessian_discrepancy']<1e-14
assert np.linalg.norm(source[1:])>.03
assert out['charge_connection_commutator_norms'][2]>.4
assert out['charge_connection_commutator_norms'][3]>.4
assert abs(direct)<1e-14 and abs(indirect-.1253556148577143)<2e-10
assert out['complement_equation_error']<2e-10
assert out['common_trial_checks']['interior_Gauss_error']<2e-10
assert out['independent_dual']['right_left_difference']<1e-12
# The canonical scalar amplitude is neutral in the retained charged fermion
# representation; neutrality alone does not commute the full background body.
ops=np.load(p/'incoming_spin_operators.npz',allow_pickle=False)
G=np.zeros((4,6,6),complex)
for k in range(3):G[k,:4,:4]=-1j*np.kron(pauli[k]/2,np.eye(2))/np.sqrt(2)
G[3]=-1j*np.diag([-.5]*4+[-1.]*2)/np.sqrt(10/3)
Q=-1j*np.einsum('c,cij->ij',q,G)
nhc=nh[:2]+1j*nh[2:];Yh=ops['family_yukawa'][1]*np.kron(nhc[:,None],np.eye(2))
Mh=np.block([[np.zeros((4,4)),Yh],[Yh.conj().T,np.zeros((2,2))]])
H6=ops['H_coordinate_time'][-1,:6,:6]
out['retained_fermion_body_check']=dict(amplitude_vertex_charge_commutator=float(np.linalg.norm(Q@Mh-Mh@Q)),
    actual_background_body_charge_commutator=float(np.linalg.norm(Q@H6-H6@Q)),
    scope='Saved finite six-dimensional body only, not a complete native propagator or violation of covariant charge conservation.')
assert out['retained_fermion_body_check']['amplitude_vertex_charge_commutator']<1e-14
# Re-evaluate only the changed mixed-source projection at another quadrature.
from native_n0_action_builder import build
K96,_,_=build(raw,order=96);Ki=K96[np.ix_(I,I)];Kib=K96[np.ix_(I,bound)]
uu,ss,vv=np.linalg.svd(Ki);keep=ss>ss[0]*1e-11
L96=np.zeros((84,20));L96[bound]=np.eye(20);L96[I]=-(vv[keep].T/ss[keep])@uu[:,keep].T@Kib
A96=(L96.T@K96@L96)[4:,4:]
return96=-float(s @ A96 @ X @ np.linalg.solve(X.T@A96@X,X.T@A96@P[:,2]))
out['quadrature_check']=dict(lower_order=96,saved_order=384,lower_return=return96,
    saved_return=indirect,difference=abs(return96-indirect),
    scope='Same four radial profiles and fixed trial; no physical exterior refinement.')
assert abs(return96-indirect)<2e-10
# Check the local mixed return after a passive internal basis change.
angle=.31;O2=np.cos(angle/2)*np.eye(2)-1j*np.sin(angle/2)*pauli[0]
O3=np.array([[np.trace(pauli[a]@O2@pauli[c]@O2.conj().T).real/2 for c in range(3)] for a in range(3)])
O4=np.eye(4);O4[:3,:3]=O3;OH=np.block([[O2.real,-O2.imag],[O2.imag,O2.real]])
T=np.zeros((16,16));T[:12,:12]=np.kron(np.eye(3),O4);T[12:,12:]=OH
Ar=T.T@A@T;Pr=T.T@P;sr=T.T@s;Xr=T.T@X
return_rot=-float(sr @ Ar @ Xr @ np.linalg.solve(Xr.T@Ar@Xr,Xr.T@Ar@Pr[:,2]))
out['passive_frame_return_error']=abs(return_rot-indirect)
assert out['passive_frame_return_error']<1e-12
for module in tuple(sys.modules.values()):
    loc=getattr(module,'__file__',None)
    if loc:
        path=Path(loc).resolve()
        assert path.is_relative_to(runtime) or path.is_relative_to(p.resolve()) or path==Path(__file__).resolve(),str(path)
out.update(passed=True,classification='FINITE_CLASSICAL_SOURCE_SELECTION_TEST',physical_guard='2e-10',
    source_hashes=manifest,physical_chi_H=None,physical_a_mu=None,physical_g_mu=None,physical_uncertainty=None,
    calibrated_Higgs_potential_preserved=True,physical_held_incident_source_supplied=False,
    actual_native_exterior_or_relative_overlap_evaluated=False,
    conclusion='Pointwise Higgs-null direct amplitude forcing vanishes, but the same-background coupled complement does not decouple. The known .1253556 coupling is recovered and its indirect source identified; it is not the physical exterior reaction.')
Path(args.output).write_bytes((json.dumps(out,sort_keys=True,indent=2)+'\n').encode())
print(json.dumps({k:out[k] for k in ('direct_amplitude_sources','source_Hessian_discrepancy','returned_axial_mixed',
  'common_trial_checks','independent_dual','retained_fermion_body_check','quadrature_check','passive_frame_return_error','passed')},indent=2))
