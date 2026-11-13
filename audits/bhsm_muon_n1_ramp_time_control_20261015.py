"""Exact owned-ramp quadrature identity and actual bounded 8/16/32 differences.

No fitted correction is applied to a field or action. This is a read-only
explanation/control for the newly saved midpoint responses.
"""
from pathlib import Path
from hashlib import sha256
from fractions import Fraction
import argparse
import json
import sys


def exact_midpoint_ramp_derivative_integral(intervals):
    """Composite midpoint integral of g'=30u²(1-u)², using rationals."""
    m=int(intervals)
    if m!=intervals or m<1:raise ValueError('positive integral midpoint count required')
    return sum((30*(u:=Fraction(2*j+1,2*m))**2*(1-u)**2 for j in range(m)),Fraction(0))/m


def materialize(repository,base,output):
    import numpy as np
    from flint import acb_mat,arb,ctx
    root,base,out=map(lambda p:Path(p).resolve(),(repository,base,output));out.mkdir(parents=True,exist_ok=False)
    sys.path.insert(0,str(Path(__file__).parent))
    from bhsm_exact_action_balls import parse_acb_exact_dyadic
    ctx.prec=256;pins={};proof=[];records={};packets={};repeats={}
    def read(p):
        p=Path(p);pins[str(p)]=sha256(p.read_bytes()).hexdigest()
        if p.suffix=='.json':return json.loads(p.read_text(encoding='utf8'))
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    def take(a,key):return parse_acb_exact_dyadic(a,key+'_exact')
    def norm(a):return sum((abs(a[i,j])**2 for i in range(a.nrows())for j in range(a.ncols())),arb(0)).sqrt()
    def rows(a,start,end):return acb_mat([[a[i,j]for j in range(a.ncols())]for i in range(start,end)])
    def report(a):return dict(ball=str(a),value=float(a))
    for N in(8,16,32):
        m=N//4;v=exact_midpoint_ramp_derivative_integral(m);delta=Fraction(7,8*m**4)
        if v!=1+delta:raise ArithmeticError('Owned C2-ramp exact quadrature identity failed')
        proof.append(dict(total_steps=N,ramp_steps=m,exact_integral_of_gprime='1',
            exact_midpoint_sum=str(v),exact_overshoot=str(delta),stated_identity='midpoint_m[30u²(1-u)²]=1+7/(8m⁴)'))
        folder=base/f'midpoint{N}_run_1';md=read(folder/'result.json');repeats[N]={}
        other=base/f'midpoint{N}_run_2'
        for name in list(md['archives'])+['result.json']:
            repeats[N][name]=(folder/name).read_bytes()==(other/name).read_bytes()
        if not all(repeats[N].values()):raise ValueError('New response repeat changed')
        records[N]=dict(original_row_upper_bounds=md['original_row_upper_bounds'],all_finite_original_rows_pass=md['all_finite_original_row_guards_pass'])
        packets[N]=read(folder/f'cell_{N-1:04d}_right_one_sided_node.npz')
    actual=[]
    for key,label,sub in [('actual_total_field336','full_n1_field336',None),('free_position196','free_position196',None),
                          ('free_momentum196','free_momentum196',None),('wall_gauge80_and_natural_H16','natural_H16',(80,96))]:
        vals={n:take(p,key)for n,p in packets.items()}
        if sub is not None:vals={n:rows(v,*sub)for n,v in vals.items()}
        e0,e1=norm(vals[8]-vals[16]),norm(vals[16]-vals[32]);ratio=e0/e1
        actual.append(dict(operand=label,difference8_to16=report(e0),difference16_to32=report(e1),
            ratio=report(ratio),observed_order_log2=report(ratio.log()/arb(2).log()),relative16_to32=report(e1/norm(vals[32])),
            final32_operand_norm=report(norm(vals[32]))))
    current_code=root/'src/bhsm/interface/muon_holomorphic_n1_magnetic_cauchy.py'
    pins[str(current_code)]=sha256(current_code.read_bytes()).hexdigest()
    pins[str(Path(__file__).resolve())]=sha256(Path(__file__).read_bytes()).hexdigest()
    result=dict(classification='EXACT_C2_RAMP_MIDPOINT_BIAS_AND_ACTUAL_NEW_N1_FINITE_TIME_CONTROL',
        exact_fraction_proof=proof,actual_endpoint_differences=actual,actual_original_row_checks=records,
        all_response_materializations_byte_identical=repeats,input_hashes=pins,
        inference='Full n1 field and canonical endpoint differences have order near4, matching the exact scalar ramp-derivative midpoint overshoot. This identifies a concrete forcing-quadrature channel; it is not a fit, not a subtraction from the original fields, and not a proof that all other time/coefficient/continuum errors vanish.',
        induced_natural_H_not_zeroed=True,actual_unit_probe_fields_preserved=True,
        no_more_midpoint_refinements=True,polynomial_method_repair_required_for_temporal_convergence=True,
        source_or_D5_or_background_campaigns_restarted=False,physical_derivative_gate_pass=False,
        physical_outgoing_boundary_or_muon_or_magnetic_moment_admitted=False,coupled_matching_corrections_applied=0)
    p=out/'result.json';p.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8')
    print(json.dumps(dict(result=str(p),sha256=sha256(p.read_bytes()).hexdigest())),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repository',required=True);p.add_argument('--base',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();materialize(a.repository,a.base,a.output)
