"""Evaluate the omitted uniform-lapse/time-source Euler comparison."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from evaluate_muon_continued_current_factor import retained_input
from bhsm.interface.muon_uniform_clock_action_identity import uniform_clock_action_twojet
from bhsm.interface.muon_holomorphic_child_action import holomorphic_inherited_child_action
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def clock_direction(raw,rep):
    d=np.zeros(268,complex);d[37:74]=raw[37:74];d[99]=raw[99]
    d[86:98]=raw[86:98];d[180:260]=raw[180:260];d[264:]=raw[264:]
    at=[j for j,label in enumerate(rep['gauge_labels'])if label['field']=='A_tau']
    d[100+np.asarray(at)]=raw[100+np.asarray(at)]
    return d


def materialize(source_folder,output):
    src,out=ROOT/source_folder,ROOT/output
    if out.exists():raise FileExistsError('preserve every uniform-clock application')
    refs={}
    def read(path):
        b=path.read_bytes();refs[path.relative_to(ROOT).as_posix()]=sha256(b).hexdigest()
        if path.suffix=='.json':return json.loads(b)
        with np.load(path,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    md=read(src/'result.json');refs.update(md['input_hashes']);saved=read(src/'application.npz')
    if refs[(src/'application.npz').relative_to(ROOT).as_posix()]!=md['archives']['application.npz']['sha256']:
        raise ValueError('same recorded original action point changed')
    phase,_=retained_input('outgoing',refs);rep=phase['representation'];P=phase['coordinates']['lift']
    raw=saved['raw_fields'];time=saved['coordinate_time'].item()
    pairs=phase['arrays']['initial_pair'],phase['arrays']['reference_pair'];params=md['action_parameters']
    action=holomorphic_inherited_child_action(raw,time,*pairs,rep,**params)
    app=uniform_clock_action_twojet(raw,time,*pairs,rep,**params);jet=app['action']
    D=clock_direction(raw,rep);represented=action['raw_gradient']@D
    defect=represented+sum(jet.gradient)-action['value']
    controls=[]
    for alpha in (1.0001,1+.0001j):
        a=uniform_clock_action_twojet(raw+(alpha-1)*D,time,*pairs,rep,**params,
            log_uniform_lapse=np.log(alpha),inherited_time_increment=alpha-1)['action']
        controls.append(dict(alpha=[alpha.real,alpha.imag],
            scaled_action_relative_defect=float(abs(a.value-alpha*action['value'])/max(1.,abs(a.value)))))
    value_relative=float(abs(jet.value-action['value'])/max(1.,abs(action['value'])))
    euler_relative=float(abs(defect)/max(1.,abs(action['value']),abs(represented)))
    if max(value_relative,euler_relative,*[a['scaled_action_relative_defect']for a in controls])>3e-10:
        raise ArithmeticError('literal uniform clock comparison failed')
    eta=saved['coefficients'];p0=saved['canonical_momentum_target'];n=106
    residual=np.r_[action['gradient'][n:2*n]-p0,action['gradient'][2*n:]]
    target_energy=eta[n:2*n]@p0-action['value']
    actual_energy=eta[n:2*n]@action['gradient'][n:2*n]-action['value']
    out.mkdir(parents=True)
    arrays=dict(original_raw_fields=raw,coordinate_time=np.array(time),clock_raw_direction=D,
        original_action_value=np.array(action['value']),uniform_comparison_gradient=jet.gradient,
        uniform_comparison_hessian=jet.hessian,represented_time_direction_first=np.array(represented),
        exact_clock_Euler_identity_defect=np.array(defect),target_Legendre_energy=np.array(target_energy),
        actual_Legendre_energy=np.array(actual_energy),original_constitutive_rows=residual,
        target_momentum_work_difference=np.array(eta[n:2*n]@(action['gradient'][n:2*n]-p0)))
    p=out/'application.npz';_compressed_npz(p,arrays)
    for name,module in sorted(sys.modules.items()):
        path=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and path:
            try:rel=Path(path).relative_to(ROOT).as_posix()
            except ValueError:continue
            refs[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    refs[Path(__file__).relative_to(ROOT).as_posix()]=sha256(Path(__file__).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('same action source changed')
    c=lambda z:[complex(z).real,complex(z).imag]
    result=dict(classification='EVALUATED_UNREPRESENTED_UNIFORM_LAPSE_AND_INHERITED_CLOCK_ACTION_IDENTITY',
        input_hashes=refs,archives={p.name:dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())},
        controls=dict(original_action_value_relative_defect=value_relative,clock_Euler_relative_defect=euler_relative,
                      simultaneous_clock_scaling=controls),
        uniform_lapse_first=c(jet.gradient[0]),inherited_connection_time_work=c(jet.gradient[1]),
        represented_clock_first=c(represented),original_action_value=c(action['value']),
        target_Legendre_energy=c(target_energy),actual_Legendre_energy=c(actual_energy),
        original_constitutive_rows_max=float(np.max(abs(residual))),
        identity='L = D_raw_time L + partial_logN0 L + inherited_lambda_tau partial_lambda_tau L',
        represented_lapse_modes='cos(4k chi), k=1..12; uniform log lapse0 excluded',
        uniform_lapse_is_an_original146_row=False,physical_zero_energy_constraint_selected=False,
        source_clock_work_not_dropped=True,action_parameters=params,
        target_position_or_momentum_changed=False,original_constitutive_rows_removed=0,
        error_scope='binary64 action comparison and Euler identity, not a phase-space incompatibility or physical exterior proof')
    p=out/'result.json';p.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps({k:result[k]for k in('classification','controls','uniform_lapse_first','inherited_connection_time_work','target_Legendre_energy','original_constitutive_rows_max')},sort_keys=True))


if __name__=='__main__':
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('--source-folder',type=Path,default=Path('artifacts/muon_material_rate_canonical_geometry_20261011/run_2'))
    a.add_argument('--output',type=Path,required=True);args=a.parse_args();materialize(args.source_folder,args.output)
