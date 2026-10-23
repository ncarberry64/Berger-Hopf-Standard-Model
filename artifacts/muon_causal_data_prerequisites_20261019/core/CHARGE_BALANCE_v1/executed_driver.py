"""Consume matched comparison/Gauss operators without selecting a state."""
from pathlib import Path
from hashlib import sha256
import os,sys,json
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
import numpy as np
R=Path('C:/Users/carbe/Downloads/BHSM_muon_parent_maxwell_worktree_20261001')
W=Path(__file__).resolve().parent;O=W/'CHARGE_BALANCE_v1'
sys.path[:0]=[str(R/'src'),str(R)]
from bhsm.interface.muon_comparison_charge_balance import consume_charge_balance
from bhsm.interface.retained_response.finite_time_response import write_npz
def pin(p):return sha256(p.read_bytes()).hexdigest()
def load(p):
 with np.load(p,allow_pickle=False) as z:return {k:z[k].copy() for k in z.files}
def dump(p,v):p.write_bytes((json.dumps(v,sort_keys=True,indent=2,allow_nan=False)+'\n').encode())
def mx(v):return float(np.max(abs(v)))
assert not O.exists();O.mkdir()
cp=W/'COMPARISON_TIME_LIFT_v2/application.npz';gp=W/'PREPARED_GAUSS_v2/application.npz'
inputs=[cp,gp,cp.with_name('result.json'),gp.with_name('result.json'),Path(__file__)]
for name in ('muon_comparison_charge_balance.py','muon_native_dirac_hamiltonian.py',
 'muon_intrinsic_higgs_weak_action.py','muon_intrinsic_lepton_primal.py',
 'muon_native_product_factor_graph.py'):
 inputs.append(R/'src/bhsm/interface'/name)
pins={str(p):pin(p) for p in inputs}
dump(O/'BEFORE.json',dict(input_sha256=pins,
 equation='E_Q=D_tau Q+sum_i alpha_i D_i Q+i[M,Q]=ordinary_d_tau_Q+i[h,Q]',
 held='same saved stationary comparison151, complete constant-angular18, independent source151; no physical packet or domain change',
 NEXT_OPERAND='consume actual Gauss charge-test derivatives in independently evaluated causal generator/current blocks'))
c,g=load(cp),load(gp)
record=json.loads(cp.with_name('result.json').read_bytes())
assert record['physical_admission'] is False
a=consume_charge_balance(c,g)
write_npz(O/'application.npz',{k:v for k,v in a.items() if isinstance(v,np.ndarray)})
checks={k:mx(a[k]) for k in ('original_charge_balance_rows','original_charge_balance_source_rows','original_exchange_Hermiticity_rows')}
assert max(checks.values())<2e-10
result=dict(schema='bhsm.comparison-charge-dressing-connection.v1',input_sha256=pins,
 arrays=dict(sha256=pin(O/'application.npz')),
 equations=dict(original_continuity='E_Q=[Omega,Q]+sum_i alpha_i[A_i,Q]/R+i[M_Y,Q] on the represented stationary constant-angular component',
  independent_causal='E_Q=i[h,Q], h=W-iOmega; temporal connection counted once',
  source='D E_Q=D[Omega,Q]+sum_i alpha_i D([A_i,Q]/R)+iD[M_Y,Q]; all vertex and charge-axis placements retained',
  consumption='P_e,+ E_Q P_e,-; D(P+ E_Q P-)=DP+ E_Q P-+P+ DE_Q P--P+ E_Q DP+'),
 original_checks=checks,
 component_maxima={k:mx(a[k]) for k in ('covariant_temporal_charge','spatial_charge_continuity','Higgs_mass_charge_torque',
  'charge_exchange','charge_exchange_source','electron_pair_charge_exchange','electron_pair_charge_exchange_source')},
 physical_interpretation='non-null fermionic charge-exchange operator that the coupled field/constraint construction must retain; it is not a current expectation, an independently added force, or physical causal data',
 ordinary_H_time_derivative_zero_scope='saved stationary coefficient family only; full nonstationary H/time/source contacts remain required',
 physical_d_in=None,physical_initial_Cauchy_data=None,physical_state_contracted=False,
 physical_Cauchy_norm_error=None,complete_Gauss_residual=None,
 physical_guard=2e-10,physical_admission=False,local_native_accounting_changed=False,
 NEXT_OPERAND='construct the same-domain constrained charged comparison/prepared state and collider-to-parent Cauchy incidence; then contract this retained operator and apply the physical initial/incoming data to all saved h/child fields')
dump(O/'result.json',result)
(O/'executed_driver.py').write_bytes(Path(__file__).read_bytes())
(O/'executed_source_owner.py').write_bytes((R/'src/bhsm/interface/muon_comparison_charge_balance.py').read_bytes())
print(json.dumps(dict(result_sha256=pin(O/'result.json'),arrays_sha256=pin(O/'application.npz'),checks=checks,components=result['component_maxima']),sort_keys=True,indent=2))
