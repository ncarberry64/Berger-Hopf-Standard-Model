"""Actual signed wall/outer/interface work of the partial D5 collar trial."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_sigma_collar_boundary_return import collar_surface_work_projection
from bhsm.interface.muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
from evaluate_muon_d5_finite_trace_pole_match import clean


def materialize(collar,output):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve prior bulk and return applications')
    pins={}
    def read(p):
        p=ROOT/collar/p;pins[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
        if p.suffix=='.json':return json.loads(p.read_bytes())
        with np.load(p)as z:return{k:z[k].copy()for k in z.files}
    receipt=read(Path('result.json'));pins.update(receipt['input_hashes'])
    a=read(Path('partial_two_sheet_action_and_Gamma.npz'));g=read(Path('partial_collar_integrands_and_returns.npz'))
    result=collar_surface_work_projection(g['initial_normal_Green'],g['final_normal_Green'],g['before_after_interface_Green_returns'],
        a['complete_field_Poisson'],a['complete_field_Poisson_energy'],full=full_d5_localized_lepton_trace())
    out.mkdir(parents=True);p=out/'application.npz';_compressed_npz(p,{k:v for k,v in result.items()if isinstance(v,np.ndarray)})
    for path in(Path(__file__),ROOT/'src/bhsm/interface/muon_sigma_collar_boundary_return.py',ROOT/'tests/test_muon_sigma_collar_boundary_return.py'):
        pins[path.relative_to(ROOT).as_posix()]=sha256(path.read_bytes()).hexdigest()
    if any(sha256((ROOT/k).read_bytes()).hexdigest()!=v for k,v in pins.items()):raise ValueError('exact supplied action/Poisson/current source pins required')
    values={k:float(np.linalg.norm(v))for k,v in result.items()if isinstance(v,np.ndarray)and'surface_work'in k}
    r=dict(classification='EVALUATED_SIGNED_PARTIAL_D5_COLLAR_SURFACE_WORK_PROJECTION',input_hashes=pins,
        archives={'application.npz':dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())},
        projected_work_norms=values,interface_work_individual_norms=[float(np.linalg.norm(v))for v in result['signed_interface_surface_work']],
        finite_bulk_Gamma_norm=float(np.linalg.norm(a['partial_field_Gamma'])),
        surface_work_sign='final-initial-sum(after-minus-before); saved interface jumps are AFTER minus BEFORE',
        complete768_field_Poisson_consumed=True,independent_literal_left_coefficient_test=True,
        physical_domain_transmission_source_motion_and_retarded_exterior_not_selected=True,
        no_surface_counterterm_or_new_matching_parameter=True,normalization_pole_charge_LSZ_and_Pauli_admitted=False,
        actual_failed_birth_relation='same trial original226 row223 remains -4.019897650202032e-7 -4.405744300638686e-6 i',
        physical_a_mu=None,physical_g_mu=None,projected_norms_not_error_enclosures=True)
    p=out/'result.json';p.write_text(json.dumps(clean(r),sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(result_sha256=sha256(p.read_bytes()).hexdigest(),projected_work_norms=values),sort_keys=True),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--collar',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();materialize(a.collar,a.output)
