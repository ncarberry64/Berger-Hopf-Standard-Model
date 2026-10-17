"""Independent full336 action checks and bounded 8/16 finite-step comparison.

Only newly evaluated response packets are consumed. No source/action/history
integration or pole calculation is repeated by this binder.
"""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import sys


def bind(repository,base,output):
    import numpy as np
    from flint import acb,acb_mat,arb,ctx
    root,base,out=map(lambda p:Path(p).resolve(),(repository,base,output))
    out.mkdir(parents=True,exist_ok=False);sys.path[:0]=[str(Path(__file__).parent)]
    from bhsm_exact_action_balls import parse_acb_exact_dyadic
    ctx.prec=256;pins={}
    def read(p):
        p=Path(p);pins[str(p)]=sha256(p.read_bytes()).hexdigest()
        if p.suffix=='.json':return json.loads(p.read_text(encoding='utf8'))
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    def matrix(a):return acb_mat([[acb(arb(float(v.real)),arb(float(v.imag)))for v in row]for row in np.asarray(a)])
    def bound(a):return max(float(np.nextafter(float(abs(a[i,j]).upper()),np.inf))for i in range(a.nrows())for j in range(a.ncols()))
    def norm(a):return sum((abs(a[i,j])**2 for i in range(a.nrows())for j in range(a.ncols())),arb(0)).sqrt()
    def extract(a,key):return parse_acb_exact_dyadic(a,key+'_exact')
    def subset(a,start,end):return acb_mat([[a[i,j]for j in range(a.ncols())]for i in range(start,end)])
    c1,c2=[read(base/f'coefficients_run_{i}/result.json')for i in (1,2)]
    coeff_repeat={n:(base/'coefficients_run_1'/n).read_bytes()==(base/'coefficients_run_2'/n).read_bytes()for n in c1['archives']}
    coeff_repeat['result.json']=c1==c2
    if not all(coeff_repeat.values()):raise ValueError('Coefficient epoch repeat changed')
    coeff=[]
    for j in range(2):
        a=read(base/f'coefficients_run_1/stage_{j:04d}_exact_raw_signed_n1_forms_and_source.npz')
        S=a['interior_field_lift'][:,48:]
        coeff.append(dict(Sd=matrix(S),K=matrix(a['K']),M=matrix(a['M']),BF=matrix(a['B_forward']),BR=matrix(a['B_reverse']),step=complex(a['coordinate_step'].item())))
    controls={};repeat={};endpoints={}
    for n in (8,16):
        folder=base/f'midpoint{n}_run_1';md=read(folder/'result.json')
        repeat[n]={};other=base/f'midpoint{n}_run_2'
        if not (other/'result.json').is_file():raise ValueError('Actual deterministic repeat is required')
        for name in list(md['archives'])+['result.json']:
            repeat[n][name]=(folder/name).read_bytes()==(other/name).read_bytes()
        if not all(repeat[n].values()):raise ValueError('Actual finite response repeat changed')
        maxima={}
        def check(k,a):maxima[k]=max(maxima.get(k,0.),bound(a))
        for k in range(n):
            a=read(folder/f'cell_{k:04d}_same_stage_retarded_n1_midpoint.npz')
            left=read(folder/f'cell_{k:04d}_left_one_sided_node.npz');right=read(folder/f'cell_{k:04d}_right_one_sided_node.npz')
            f=coeff[int(a['stage'])];dt=acb(2*f['step'])/n
            q,v=extract(a,'actual_total_field336'),extract(a,'actual_total_coordinate_rate336')
            xi,xf=[extract(z,'free_position196')for z in(left,right)];pi,pf=[extract(z,'free_momentum196')for z in(left,right)]
            # This uses the FULL original matrices afresh, independently of
            # the propagation's Kaa/U/V/Schur action and reduced source loads.
            full_momentum=f['M']*v+f['BR']*q;full_force=f['K']*q+f['BF']*v
            check('original_full_action_projected_canonical_momentum',f['Sd'].transpose()*full_momentum-(pi+pf)/2)
            check('original_full_action_canonical_force_increment',dt*f['Sd'].transpose()*full_force-(pf-pi))
            check('original_kinematic_position_increment',xf-xi-dt*f['Sd'].transpose()*v)
            check('saved_midpoint_position',(xi+xf)/2-extract(a,'free_position196'))
            check('saved_midpoint_momentum',(pi+pf)/2-extract(a,'free_momentum196'))
        controls[n]=dict(independent_full_original_action_upper_bounds=maxima,all_pass=max(maxima.values())<=2e-10,
            producer_original336_frame_wall_and_Gauss_upper_bounds=md['original_row_upper_bounds'])
        endpoints[n]=read(folder/f'cell_{n-1:04d}_right_one_sided_node.npz')
    comparisons=[]
    for k in range(1,9):
        a=read(base/f'midpoint8_run_1/cell_{k-1:04d}_right_one_sided_node.npz')
        b=read(base/f'midpoint16_run_1/cell_{2*k-1:04d}_right_one_sided_node.npz')
        fa,fb=extract(a,'wall_gauge80_and_natural_H16'),extract(b,'wall_gauge80_and_natural_H16')
        ha,hb=subset(fa,80,96),subset(fb,80,96)
        comparisons.append(dict(coordinate_time=[complex(a['coordinate_time']).real,complex(a['coordinate_time']).imag],
            complete_wall_source_difference_upper=bound(extract(a,'source_Q80')-extract(b,'source_Q80')),
            natural_H16_absolute_difference_upper=bound(ha-hb),natural_H16_relative_Frobenius_difference=float(norm(ha-hb)/norm(hb))if norm(hb)>0 else None,
            full_field336_absolute_difference_upper=bound(extract(a,'actual_total_field336')-extract(b,'actual_total_field336'))))
    for n in ('bhsm_muon_exact_stage_n1_weak_probe_20261015.py','bhsm_muon_same_stage_retarded_n1_20261015.py',
              'bhsm_exact_action_balls.py','bhsm_baton_zoo_exact_acb_packets.py',Path(__file__).name):
        p=Path(__file__).parent/n;pins[str(p)]=sha256(p.read_bytes()).hexdigest()
    result=dict(classification='INDEPENDENT_ORIGINAL336_ACTION_BINDING_OF_NEW_SAME_STAGE_RETARDED_WEAK_PROBE',
        coefficient_repeats_byte_identical=coeff_repeat,response_repeats_byte_identical=repeat,
        finite_canonical_action_controls=controls,all_independent_finite_original_action_guards_pass=all(x['all_pass']for x in controls.values()),
        eight_to_sixteen_step_comparison=comparisons,
        no_fresh_original_nonlinear_B_derivative_claimed=True,
        physical_formed_state_or_outgoing_domain_or_continuum_or_soft_limit_not_admitted=True,
        coupled_matching_corrections_applied=0,input_hashes=pins,
        interpretation='These are original signed quadratic action and canonical/constraint checks at fixed declared stage coefficients. Small rows are arithmetic/finite-discretization controls, not a whole physical source/domain derivative or a convergence certificate. Nonzero self-field, natural H probe, named reactions and final remainder persist.',
        producer_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
    p=out/'result.json';p.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8')
    print(json.dumps(dict(result=str(p),sha256=sha256(p.read_bytes()).hexdigest(),all_original_action_guards_pass=result['all_independent_finite_original_action_guards_pass'])),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repository',required=True);p.add_argument('--base',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();bind(a.repository,a.base,a.output)
