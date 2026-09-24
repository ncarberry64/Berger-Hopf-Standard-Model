"""Fail closed at the boundary between one local column and global Gate 7."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from fractions import Fraction

ROOT=Path(__file__).resolve().parents[1]
BASE='b33d94e4eaa94b6be9d7ca423d45205a23f5e797'


def encoded(value):return (json.dumps(value,sort_keys=True,indent=2)+'\n').encode()
def sha(payload):return hashlib.sha256(payload).hexdigest().upper()


def evaluate(evidence_root):
    endpoint_path=ROOT/'artifacts/gate7/GATE7_ENDPOINT_VECTOR_CERTIFICATE_v1/record.json'
    midpoint_path=ROOT/'artifacts/gate7/GATE7_PROJECTED_VECTOR_CERTIFICATE_v2.json'
    receipt_path=ROOT/'artifacts/gate7/GATE7_ENDPOINT_VECTOR_REPRODUCTION_v1.json'
    endpoint=json.loads(endpoint_path.read_bytes());midpoint=json.loads(midpoint_path.read_bytes())
    receipt=json.loads(receipt_path.read_bytes())
    if receipt['pairs']['endpoint_vector']['SHA256']!=sha(endpoint_path.read_bytes()):
        raise ValueError('independently reproduced endpoint vector required')
    if not all(receipt['pairs']['endpoint_vector'].get(k) is True for k in ('byte_identical','fresh_process','independent_arithmetic_recomputation')):
        raise ValueError('independent arithmetic pair required')
    bound=Fraction(endpoint['transport']['norm_upper']['exact'])
    margin=Fraction(endpoint['transport']['margin_lower_exact'])
    if not 0<=bound<1 or not 0<margin<=1-bound:
        raise ValueError('strict complete local column margin required')
    if len(endpoint['components'])!=74 or len(midpoint['components'])!=74:
        raise ValueError('all projected output rows required')
    sources={str(endpoint_path.relative_to(ROOT)):sha(endpoint_path.read_bytes()),
             str(midpoint_path.relative_to(ROOT)):sha(midpoint_path.read_bytes()),
             str(receipt_path.relative_to(ROOT)):sha(receipt_path.read_bytes())}
    inherited={}
    for key,name in (
        ('physical_Y','BHSM_N12_GATE7_DIRECT_PHYSICAL_VALUE_RESIDUAL_ENVELOPE.json'),
        ('physical_Z1','BHSM_N12_GATE7_FULL_DIRECT_CAUSAL_LINEAR_DEFECT.json'),
        ('physical_Z2','BHSM_N12_GATE7_SELECTED_013_DIRECT_CAUSAL_QUADRATIC.json')):
        path=evidence_root/'artifacts/flagship_integration'/name
        payload=path.read_bytes();record=json.loads(payload)
        if record.get('validation_passed') is not True:raise ValueError('validated inherited record required')
        inherited[key]=dict(artifact='artifacts/flagship_integration/'+name,
            scope=record['scope'],claim_boundary=record['claim_boundary'])
        sources['evidence/'+name]=sha(payload)
    # Bind the owner's explicit checkpoint specifications, unaffected by
    # historical tests that rematerialize files in the working directory.
    for name in ('docs/BHSM_1_0_DEFINITION_OF_DONE.md','theory/n12_joint_finite_history_operator_data_gate.md',
                 'theory/n12_gate7_joint_kkt_information_gate.md','theory/n12_finite_endpoint_forward_adjoint_kkt.md'):
        payload=subprocess.check_output(['git','show',BASE+':'+name],cwd=ROOT)
        sources[BASE+':'+name]=sha(payload)
    recertified=[inherited[k]['claim_boundary'].get(k+'_recertified') is True
                 for k in ('physical_Y','physical_Z1','physical_Z2')]
    if any(recertified):
        raise ValueError('inherited physical authority changed; reconcile before issuing this audit')
    polynomial='B_i(r)=Y_i+sum_j Z_ij*r_j+C_i*r_L^2+2*M_i*r_L*r_T+T_i*r_T^2'
    conditions=[]
    for name,form in [('longitudinal_self_map','B_L(r)<r_L'),('transverse_self_map','B_T(r)<r_T'),
                      ('weighted_contraction','max_i sum_j partial_j(B_i(r))*r_j/r_i < 1')]:
        conditions.append(dict(name=name,exact_condition=form,status='UNDECIDED',rigorous_bound=None,
            margin=None,missing_input='same-map full-input-space full-history physical Y/Z1/Z2 enclosures'))
    other=[
        dict(name='complete_joint_operator',condition='action-owned P[Y,T], endpoint form and required physical quotient geometry jets'),
        dict(name='joint_KKT_root',condition='N_phys^dagger(D_xi R_AE2^dagger p(0)+q_xi,direct)=0 with the retained forward/adjoint equations and endpoint load'),
        dict(name='constrained_physical_Hessian',condition='strict positive lower spectral bound on the physical constraint tangent at the same-action certified KKT root'),
        dict(name='continuum_closure',condition='source-restricted Jacobi-Calderon right-inverse control and strong-graph Cauchy/compactness sufficient for the unchanged nonlinear event-child radius')]
    for item in other:item.update(status='UNDECIDED',rigorous_bound=None,margin=None)
    return dict(algorithm='LOCAL_VECTOR_TO_GLOBAL_GATE7_AUTHORITY_AUDIT_V1',
        source_commit=BASE,source_hashes=sources,evaluator_SHA256=sha(Path(__file__).read_bytes()),
        local_column=dict(interval=13,side='right',input_column=14,output_rows=74,
                          norm_upper_exact=str(bound),positive_margin_lower_exact=str(margin),status='PASS'),
        full_input_basis_certified=False,full_history_physical_contraction_certified=False,
        inherited_physical_authority=inherited,physical_majorant=polynomial,
        global_radii_inequalities=conditions,global_radii_passed=0,global_radii_total=3,
        other_retained_requirements=other,physical_global_margin=None,
        Gate7_verdict='OPEN — SPECIFIC REMAINING OBSTRUCTION',BHSM_status='OPEN',
        exact_remaining_numerical_obstruction='sup over the original domain of the full physical derivative operator in the retained weighted norm; the new certificate controls only interval 13 right input column 14',
        exact_remaining_KKT_obstruction='nonempty regular finite-endpoint forward-adjoint KKT root existence and certification on the physical reset quotient',
        physical_violation_proved=False,completion_audit_started=False,
        Gate7_closed=False,FULL_BHSM_COMPLETE=False)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--evidence-root',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True);args=parser.parse_args()
    result=evaluate(args.evidence_root.resolve())
    with args.out.open('xb') as f:f.write(encoded(result))
    print(json.dumps(dict(Gate7_verdict=result['Gate7_verdict'],global_radii_passed=0,global_radii_total=3)))


if __name__=='__main__':main()
