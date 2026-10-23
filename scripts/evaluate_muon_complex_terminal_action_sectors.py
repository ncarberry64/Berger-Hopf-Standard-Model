"""Literal cap, Maxwell and Higgs gradient split of the terminal defect."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from evaluate_muon_continued_current_factor import retained_input
from bhsm.interface.muon_holomorphic_normal_geometry import holomorphic_cap_and_weights
from bhsm.interface.muon_holomorphic_child_action import _affine_geometry,_parameters
from bhsm.interface.muon_nonlinear_n0_field_action import analytic_intrinsic_n0_jet
from bhsm.interface.muon_parent_maxwell_full_weak import M
from bhsm.interface.muon_parent_retarded_hypercharge import WALL
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def original_sector_gradients(raw,full_gradient,time,phase,parameters):
    """The scalar/cap terms are literal owners; Maxwell is their remainder."""
    rep=phase['representation'];P=phase['coordinates']['lift'];nr=len(raw);ng=80;hs=260
    cap=holomorphic_cap_and_weights(raw[:100],points=rep['cap_points'])
    cap_gradient=np.zeros(nr,complex);cap_gradient[:100]=cap['total'].gradient
    if parameters['surface_gamma'] is not None:
        cap_gradient[:100]+=parameters['surface_gamma']*cap['surface_per_gamma'].gradient
    p=_affine_geometry(phase['arrays']['initial_pair'][0],time)
    rp,rc=(_affine_geometry(a,time)for a in phase['arrays']['reference_pair'])
    eff=(_parameters(p,np.array([WALL]))-_parameters(rp,np.array([WALL]))+_parameters(rc,np.array([WALL])))[0]
    wall=np.einsum('fcj,j->fc',rep['wall_trace_map'],raw[100:180]);wall[2:]+=M*(eff[0]-1)
    weights=[cap[k]for k in('wT','wS','wV')]
    args=dict(lambda_H=rep['scalar_matching']['lambda_H'],nu_squared_action=parameters['nu_squared_action'])
    scalar=analytic_intrinsic_n0_jet(wall,raw[260:264],raw[264:],np.array([w.value for w in weights]),**args)
    S=np.zeros((28,nr-100));S[:4,2*ng:2*ng+4]=np.eye(4)
    S[4:24,:ng]=rep['wall_trace_map'].reshape(20,ng);S[24:,2*ng+4:]=np.eye(4)
    scalar_gradient=np.zeros(nr,complex);scalar_gradient[100:]=S.T@scalar['gradient']
    for j,w in enumerate(weights):
        unit=analytic_intrinsic_n0_jet(wall,raw[260:264],raw[264:],np.eye(3)[j],**args)
        scalar_gradient[:100]+=w.gradient*unit['value']
    cap_g=P.T@cap_gradient;scalar_g=P.T@scalar_gradient
    maxwell_g=full_gradient-cap_g-scalar_g
    return dict(cap=cap_g,Maxwell=maxwell_g,Higgs=scalar_g)


def materialize(attribution_folder,output):
    base=ROOT/attribution_folder;out=ROOT/output
    if out.exists():raise FileExistsError('preserve every action-sector application')
    rb=(base/'result.json').read_bytes();md=json.loads(rb);refs=dict(md['input_hashes'])
    refs[(base/'result.json').relative_to(ROOT).as_posix()]=sha256(rb).hexdigest()
    p=base/'application.npz';h=sha256(p.read_bytes()).hexdigest()
    if h!=md['archives'][p.name]['sha256']:raise ValueError('actual defect attribution changed')
    refs[p.relative_to(ROOT).as_posix()]=h
    with np.load(p,allow_pickle=False)as z:data={k:z[k].copy()for k in z.files}
    phase,_=retained_input('outgoing',refs);parameters=phase['receipt']['action_parameters'];tm=phase['arrays']['stage_coordinate_time'][-1]
    raw_mid=phase['arrays'][phase['stage_key']][-1].astype(complex)
    candidates=dict(same_real_midpoint=(raw_mid,data['same_real_midpoint_gradient'],tm),
        same_complex_terminal_before_field_correction=(data['uncorrected_chart_raw'],data['uncorrected_chart_gradient'],data['coordinate_time'].item()),
        actual_corrected_complex_terminal=(data['actual_raw'],data['actual_terminal_gradient'],data['coordinate_time'].item()))
    arrays={};records={};gradients={}
    def blocks(g):
        return dict(Lv_norm=float(np.linalg.norm(g[106:212])),lapse_max=float(np.max(abs(g[212:224]))),
                    shift_max=float(np.max(abs(g[224:236]))),At_Gauss_max=float(np.max(abs(g[236:]))))
    for key,(raw,g,time)in candidates.items():
        print(json.dumps(dict(stage='original_terminal_action_sector',candidate=key)),flush=True)
        a=original_sector_gradients(raw,g,time,phase,parameters);gradients[key]=a
        records[key]={sector:blocks(gg)for sector,gg in a.items()}
        for sector,gg in a.items():arrays[key+'_'+sector+'_gradient']=gg
        arrays[key+'_sector_sum_residual']=sum(a.values())-g
    left=gradients['same_complex_terminal_before_field_correction'];right=gradients['actual_corrected_complex_terminal']
    effects={sector:right[sector]-left[sector]for sector in left}
    for sector,g in effects.items():arrays['global_field_effect_'+sector+'_gradient']=g
    arrays['lapse_shift_defect_rows']=data['actual_terminal_gradient'][212:236]
    arrays['lapse_shift_row_labels']=np.array([f'lapse_cos_{k}'for k in range(1,13)]+[f'shift_cos_{k}'for k in range(12)])
    out.mkdir(parents=True);p=out/'application.npz';_compressed_npz(p,arrays)
    for name,module in sorted(sys.modules.items()):
        path=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and path:
            try:rel=Path(path).relative_to(ROOT).as_posix()
            except ValueError:continue
            refs[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    refs[Path(__file__).relative_to(ROOT).as_posix()]=sha256(Path(__file__).read_bytes()).hexdigest()
    if any(sha256((ROOT/r).read_bytes()).hexdigest()!=h for r,h in refs.items()):raise RuntimeError('original action sector pins changed')
    result=dict(classification='EVALUATED_ORIGINAL_COMPLEX_TERMINAL_ACTION_SECTOR_CONSTRAINT_SPLIT',
        input_hashes=refs,archives={p.name:dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())},
        candidate_sector_rows=records,global_field_correction_sector_effect={k:blocks(g)for k,g in effects.items()},
        sum_identity_max=max(float(np.max(abs(arrays[k])))for k in arrays if k.endswith('_sector_sum_residual')),
        action_parameters=parameters,lambda_H=phase['representation']['scalar_matching']['lambda_H'],
        Maxwell_to_cap_and_scalar_volume_factor_included_once=True,
        Maxwell_gradient_definition='original full gradient minus separately literal cap and intrinsic Higgs gradients',
        actual_terminal_x_Pi_target_changed=False,canonical_constraint_convergence_claimed=False,
        error_scope='binary64 literal retained action-sector attribution, not independent Maxwell reassembly or physical matching bound')
    p=out/'result.json';p.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(stage='original_terminal_action_sector_complete',
        field_correction_effect=result['global_field_correction_sector_effect'],result_sha256=sha256(p.read_bytes()).hexdigest())),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--attribution-folder',type=Path,default=Path('artifacts/muon_complex_terminal_defect_attribution_20261011/run_1'))
    p.add_argument('--output',type=Path,required=True);a=p.parse_args();materialize(a.attribution_folder,a.output)
