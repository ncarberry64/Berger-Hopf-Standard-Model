"""Execute the original natural-wall coupled gauge/H Green and current."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
from scipy.interpolate import CubicSpline
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from evaluate_muon_continued_current_factor import retained_input
from evaluate_muon_literal_euclidean_higgs_green import _read
from bhsm.interface.muon_literal_euclidean_wall_action import (
    natural_wall_lorentz_forms,natural_wall_weak_inverse,natural_wall_open_current)
from bhsm.interface.muon_euclidean_angular_weak_action import angular_action_coefficients,angular_weak_square
from bhsm.interface.muon_parent_positive_coupled_field import corrected_positive_parent_reference
from bhsm.interface.muon_profile_preserving_phase_sample import profile_preserving_raw_sample
from bhsm.interface.muon_continued_action_reality import action_reality_coefficient
from bhsm.interface.muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
from bhsm.interface.muon_parent_maxwell_full_weak import M
from bhsm.interface.muon_parent_maxwell_full_q_application import retained_full_q_angular_space
from bhsm.interface.muon_piecewise_euclidean_action import FAMILY_INDICES
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def materialize(output,*,temporal_cells=(2,),sides=('incoming','outgoing')):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve completed literal wall applications')
    refs={};pending=[];records=[]
    epath=ROOT/'artifacts/muon_piecewise_euclidean_action_20261011/run_2/result.json'
    em=json.loads(epath.read_bytes());refs[epath.relative_to(ROOT).as_posix()]=sha256(epath.read_bytes()).hexdigest()
    E=retained_full_q_angular_space(ROOT)['derivative_matrices'][:,:4,:4]
    for side in sides:
        phase,_=retained_input(side,refs);rep=phase['representation'];length=abs(float(phase['receipt']['span']))
        times=np.linspace(0,length,5);saved=[];maps=None
        def actual(u):
            t=float(u)-length if side=='incoming'else float(u)
            raw=profile_preserving_raw_sample(phase,t)['raw_fields']
            kw={}if side=='incoming'else dict(initial_pair=phase['arrays']['initial_pair'],reference_pair=phase['arrays']['reference_pair'])
            bg=corrected_positive_parent_reference(raw,rep,coordinate_time=t,**kw)
            weights=intrinsic_m4_weight_jet(12,raw[:37],raw[37:74],raw[74:98],source_value=raw[98],source_rate=raw[99])
            wall=action_reality_coefficient(phase,t)['wall_independent_plus_inherited'].copy()
            wall[2:]+=M*(weights['mechanical_connection_lambda'].value-1)
            return natural_wall_lorentz_forms(bg,rep,E,wall_connection=wall,H=raw[-8:-4],Hdot=raw[-4:],
                metric_weights=[weights[k].value for k in ('wT','wS','wV')],lambda_H=rep['scalar_matching']['lambda_H'],
                nu_squared_action=phase['receipt']['action_parameters']['nu_squared_action'])
        for u in times:
            r=actual(u);saved.append(r['forms']);maps=r
            print(json.dumps(dict(stage='actual_original_n1_natural_wall_action',side=side,source_time=float(u),
                scalar_gauge_cross_norm=r['scalar_gauge_cross_norm']),sort_keys=True),flush=True)
        values=tuple(np.array([r[k]for r in saved])for k in range(3));polys=tuple(CubicSpline(times,a)for a in values)
        def polynomial(u,z=0j):
            j=min(max(np.searchsorted(times,float(u),side='right')-1,0),len(times)-2)
            delta=complex(u)+complex(z)-times[j]
            return tuple(sum(p.c[k,j]*delta**(3-k)for k in range(4))for p in polys)
        checks=[]
        for u in (.375*length,.625*length):
            a=actual(u)['forms'];b=polynomial(u)
            checks.append(dict(source_time=float(u),maximum_absolute=max(float(np.max(abs(x-y)))for x,y in zip(a,b)),
                relative_Frobenius=max(float(np.linalg.norm(x-y)/max(np.linalg.norm(x),np.finfo(float).tiny))for x,y in zip(a,b))))
        pending.append((side+'_original_nodes.npz',dict(times=times,**dict(zip(('M','B','K'),values)),
            value_permutation=maps['value_permutation'],wall_trace_map=maps['original_wall_trace_map'],
            central_radial_frame_indices=maps['central_radial_frame_indices'],E=E)))
        nodes=_read(epath.parent/f'{side}_nodes.npz',refs,em['archives'][f'{side}_nodes.npz']['sha256'])
        nodes['total_proper_clock']=next(r['total_proper_clock']for r in em['records']if r['side']==side)
        def point(q):
            u=float(nodes['coordinate_anchor'][q])+length if side=='incoming'else float(nodes['coordinate_anchor'][q])
            return polynomial(u,nodes['coordinate_offset'][q])
        for n in temporal_cells:
            field=natural_wall_weak_inverse(nodes,point,temporal_cells=int(n),
                frame_indices=maps['central_radial_frame_indices'],At_count=maps['At_count'])
            # Preserve every original row, splitting only packaging.  The
            # residual matrices compress less than the sparse action.
            for key,value in field.items():
                if isinstance(value,np.ndarray):
                    pending.append((f'{side}_cells_{n}_field_{key}.npz',{key:value}))
            rr=dict(side=side,temporal_cells=int(n),field_dimension=len(field['original_Hessian']),
                original_row_residual_max=field['original_row_residual_max'],original_Gauss_row_residual_max=field['original_Gauss_row_residual_max'],
                frame_residual_max=field['frame_residual_max'],saddle_condition_number=field['saddle_condition_number'],
                nonzero_scalar_gauge_cross_norm=maps['scalar_gauge_cross_norm'],fresh_original_action_interpolation_checks=checks,families=[])
            for family in(1,2):
                fi=FAMILY_INDICES[family];fn=dict(nodes);fn['lepton_indices']=fi
                for key,zkey in(('H','coordinate_offset'),('Hsharp','reflected_coordinate_offset')):
                    fn[key]=np.array([action_reality_coefficient(phase,float(t),z)['Hcan'][np.ix_(fi,fi)]
                        for t,z in zip(nodes['coordinate_anchor'],nodes[zkey])])
                coeff=angular_action_coefficients(fn,E,family=family);ff=angular_weak_square(fn,coeff,temporal_cells=int(n))
                current=natural_wall_open_current(fn,coeff,ff,field,maps['original_wall_trace_map'],temporal_cells=int(n),family=family)
                arrays={k:v for k,v in current.items()if isinstance(v,np.ndarray)};arrays.update(KF=ff['K'],fermion_Gram=ff['M'],family_indices=fi)
                pending.append((f'{side}_family_{family}_cells_{n}_current.npz',arrays))
                row=dict(family=family,current_norm=float(np.linalg.norm(current['open_Gaussian_current'])),
                    current_real_trace=float(np.trace(current['open_Gaussian_current']).real),current_imag_trace=float(np.trace(current['open_Gaussian_current']).imag),
                    fermion_original_rows=current['original_fermion_source_residual_max'])
                rr['families'].append(row)
                print(json.dumps(dict(stage='literal_coupled_natural_wall_current',side=side,temporal_cells=int(n),**row),sort_keys=True),flush=True)
            records.append(rr)
    for name in('muon_literal_euclidean_wall_action','muon_parent_maxwell_corrected_retarded','muon_parent_positive_coupled_field',
                 'muon_intrinsic_higgs_gauge_action','muon_euclidean_angular_weak_action','muon_continued_action_reality'):
        p='src/bhsm/interface/'+name+'.py';refs[p]=sha256((ROOT/p).read_bytes()).hexdigest()
    for p in(Path(__file__).relative_to(ROOT).as_posix(),'tests/test_muon_literal_euclidean_wall_action.py'):
        refs[p]=sha256((ROOT/p).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('consumed action changed')
    out.mkdir(parents=True);archives={}
    for name,a in pending:
        p=out/name;_compressed_npz(p,a)
        if p.stat().st_size>10*1024*1024:raise ArithmeticError('split packaging required; preserve every row')
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    result=dict(classification='EVALUATED_LITERAL_CONTINUED_NATURAL_WALL_COUPLED_GAUGE_H_CURRENT',input_hashes=refs,archives=archives,records=records,
        domain='four original radial unknown functions including natural wall values; full n1 gauge320+H16; initial-zero shared temporalFE/free-final action cotangent; named central Ar coordinate frames with original reactions',
        field_pairing='literal continued signed Maxwell/H action, analytic transpose, material At rotated once before original Gauss solve',
        current='Gaussian -1, one complete coupled field Green across both literal action vertices; Clifford factor and independently reflected source numerator',
        computational_frame_is_full_BRST_quotient=False,common_birth_transmission_selected=False,
        common_native_cutoff=None,starting_shell_tail_zero=False,physical_F2=None,physical_a_mu=None,physical_g_mu=None,
        error_scope='binary64 original-action interpolation/finiteFE/inverse residual diagnostics; no continuum, statistical P_cycle, relative/native/domain or external pole enclosure')
    (out/'result.json').write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--temporal-cells',type=int,nargs='+',default=[2]);p.add_argument('--sides',nargs='+',choices=('incoming','outgoing'),default=['incoming','outgoing']);a=p.parse_args()
    materialize(a.output,temporal_cells=tuple(a.temporal_cells),sides=tuple(a.sides))
