"""Add dependent error propagation to saved endpoint arrays; no action replay."""
from pathlib import Path
import argparse,hashlib,json,shutil,sys
import numpy as np
from flint import arb,ctx
parser=argparse.ArgumentParser()
parser.add_argument('--repository',type=Path,default=Path(__file__).resolve().parents[1])
parser.add_argument('--input',type=Path,required=True)
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args();ROOT=args.repository.resolve();OLD=args.input.resolve();OUT=args.output.resolve()
if OUT.exists():raise FileExistsError('immutable output already exists')
shutil.copytree(OLD,OUT);ctx.prec=192;sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.muon_endpoint_clock_actions import norm_ball
from bhsm.interface.muon_cut_inverse_coverage import encoded
from bhsm.interface.muon_radial_inclusion_action import nodal_jets
from bhsm.interface.muon_parent_maxwell_velocity import current_parent_fields
from bhsm.interface.aether_forward_boundary_radius import boundary_log_radius
def read(p):
    with np.load(p,allow_pickle=False) as z:return {k:np.array(z[k]) for k in z.files}
def save(p,j):p.write_bytes((json.dumps(j,indent=2,sort_keys=True,allow_nan=False)+'\n').encode())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ball(pair):
    lo,hi=map(lambda x:arb(float(x)),pair)
    return arb(((lo+hi)/2).mid(),((hi-lo)/2).upper())
z=read(OLD/'endpoint_clock_source_and_interface.npz')
a=ROOT/'artifacts';old=read(a/'muon_radial_inclusion_action_20261004/replay_reference/radial_source_action_and_interface.npz')
geo=read(a/'muon_parent_geometry_20261001/replay_reference/local_parent_velocity_density.npz')
pair=read(a/'muon_wall_source_pairing_20261003/replay_reference/source_reached_pairings.npz')
contact=read(a/'muon_parent_source_contact_20261003/replay_reference/parent_source_contact.npz')
corrected=read(a/'muon_parent_source_rate_20261003/replay_reference/parent_source_rate_corrected.npz')
j=nodal_jets(geo,pair['gauss_rho'],pair['gauss_cells'])
step=read(a/'flagship_integration/BHSM_N12_C2_LOHNER_STEP_1222.npz');y=step['endpoint_predictor_center']
fields=current_parent_fields(y[None],np.array([boundary_log_radius(12,y[:37])]),geo['rho'])
ratios=[arb(float(new))/arb(float(previous)) for new,previous in zip(fields['proper_lapse'][0],geo['proper_lapse'][0])]
ratio=arb(min((x.lower() for x in ratios),key=lambda x:float(x.mid())))
hi=max((x.upper() for x in ratios),key=lambda x:float(x.mid()))
ratio=arb(((ratio+hi)/2).mid(),((hi-ratio)/2).upper())
source=z['endpoint_source_Lnu_direct'];nu=j['proper_lapse'];u=old['radial_u_vol']
interp=[];tube=[];instant=[]
for k in range(len(u)):
    point=ball(z['endpoint_lapse_only_D5W_scalar'][k]);tube_ball=ball(z['endpoint_lapse_only_D5W_scalar_tube'][k])
    nominal=sum(z['endpoint_lapse_only_D5W_scalar'][k])/2
    tube.append((tube_ball-arb(float(nominal))).abs_upper())
    interp.append((ball(z['endpoint_source_Lnu_direct'][k])-ball(z['endpoint_source_Lnu_nodal'][k])).abs_upper()*arb(float(u[k]))/(2*arb(float(nu[k]))))
    instant.append((ratio**arb('-1.5')-1).abs_upper()*ball(source[k]).abs_upper()*arb(float(u[k]))/(2*arb(float(nu[k]))))
result=json.loads((OLD/'result.json').read_text())
for n in (1,3):
    xi=contact[f'Xi_A_unit_n{n}'][:,:,corrected['source_image_probe_columns']]
    factor=norm_ball(old['common_parent_Gamma'][0].real)*(norm_ball(xi.real)**2+norm_ball(xi.imag)**2).sqrt()
    bound=lambda values:encoded(sum((x*x for x in values),arb(0)).sqrt()*factor)
    result['norms'][f'n{n}'].update(endpoint_tube_lapse_action_error_bound=bound(tube),
        direct_vs_nodal_action_difference_bound=bound(interp),instantaneous_nu_lapse_action_change_bound=bound(instant))
result['instantaneous_nu_ratio']=encoded(ratio)
bulk=json.loads((a/'muon_radial_inclusion_action_20261004/replay_reference/source_scalar_integral.json').read_text())['scalar']
trace=json.loads((a/'muon_radial_inclusion_action_20261004/replay_reference/cut_trace_scalar_integral.json').read_text())['scalar']
result['overlap_input_change_bounds']=dict(full_cap_C_and_I_unchanged=True,
    bulk_scalar_endpoint_input_enclosure=encoded(arb(bulk['arb'])*ratio.sqrt()),
    Cauchy_scalar_endpoint_input_enclosure=encoded(arb(trace['arb'])/ratio.sqrt()),
    original_scalar_certificates_unchanged=True,new_integrations=0,
    scope='point reconstructed lapse change only; affine-cell ratio lies in the nodal ratio hull; no tube/global continuum promotion')
result['error_receipt_extension']=dict(reused='all run_1 arrays and rates',new_work='tube, interpolation and fixed-instantaneous lapse error propagation; changed-overlap input bound',
    unchanged_array_sha256=sha(OLD/'endpoint_clock_source_and_interface.npz'),mathematical_action_replayed=False,
    executed_module_sha256=json.loads((OLD/'input_hashes.json').read_text())['module']['sha256'],
    final_module_sha256=sha(ROOT/'src/bhsm/interface/muon_endpoint_clock_actions.py'),
    later_source_change='added only dependent coefficient-error receipts; action/rate/interface algorithms unchanged')
save(OUT/'result.json',result)
save(OUT/'output_hashes.json',{p.name:sha(p) for p in OUT.iterdir() if p.is_file() and p.name!='output_hashes.json'})
print(json.dumps(dict(array_reused=True,interpolation_bound_n1=result['norms']['n1']['direct_vs_nodal_action_difference_bound'],
    tube_bound_n1=result['norms']['n1']['endpoint_tube_lapse_action_error_bound'],
    instantaneous_nu_bound_n1=result['norms']['n1']['instantaneous_nu_lapse_action_change_bound'],
    overlap_bounds=result['overlap_input_change_bounds']),indent=2))
