"""Replay every complete input/output row and its point-anchor deviation."""
import os
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS'): os.environ[key]='1'
import argparse
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
from flint import arb,arb_mat,ctx
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
from bhsm.interface.input_linear_taylor import InputLinearTaylor,vector_norm
import certify_n12_gate7_full_input_transport as transport
import evaluate_n12_gate7_coupled_residual_saved as saved


def verify(root,path):
    import bhsm.interface
    bhsm.interface.__path__.insert(0,str(root/'src/bhsm/interface'))
    verified=saved.evaluate(root)
    declared=json.loads((path/'record.json').read_bytes())
    family=declared['family']
    if family not in ('midpoint','endpoint'):
        raise ValueError('known original physical family required')
    record,domain,rows,decode=transport.read_models(path,family,verified)
    if (record['algorithm']!='FULL_INPUT_SHARED_RESIDUAL_VECTOR_OUTER_BOUND_V1'
            or record['input_groups']!=[[0,74,'euclidean'],[74,198,'box']]
            or record.get('Gate7_closed') or record.get('FULL_BHSM_COMPLETE')
            or record.get('full_history_certified')):
        raise ValueError('complete local input sphere and unpromoted scope required')
    import diagnose_n12_gate7_directed_trial_hs_column as base
    p=base.p;residual=p.geometry.residual
    with base.cache.cache_hashes([(p.values,'sha'),(residual.center,'_sha'),(residual.foundation.coordinate.center,'_sha')]):
        local=base.reader.load_inputs(13)
    P=base.matrix(local['frozen_right']).solve(base.matrix(local['test']))
    axisfile=root/'artifacts/action_extension/BHSM_AE4_CURRENT_C2_GREEN_IMAGE_PARTITION_RECONCILIATION.npz'
    with np.load(axisfile,allow_pickle=False) as z: axes=z['current_center_green_image_unit_mid'].copy()
    axes[1:]/=np.linalg.norm(axes[1:],axis=1)[:,None];axes[0]=0
    if hashlib.sha256(np.asarray(axes,dtype='<f8').tobytes()).hexdigest().upper()!=local['binding']['axes_SHA256']:
        raise ValueError('original physical projection required')
    a=[arb(float(v)) for v in axes[14]]
    Q=arb_mat(74,74,[arb(i==j)-a[i]*a[j] for i in range(74) for j in range(74)])
    L=Q*P*(2*arb(float(local['step']))/3)
    kind,index=('interval',13) if family=='midpoint' else ('endpoint',14)
    source=root/f'artifacts/flagship_integration/.primal_mean_value_component_centered_{family}_uniform_df_work/{kind}_{index:03d}/derivative.npz'
    if record['source_hashes'].get(source.relative_to(root).as_posix())!=saved.sha(source):
        raise ValueError('original complete derivative source required')
    U=arb_mat([[arb(v) for v in row] for row in record['input_map']])
    with np.load(source,allow_pickle=False) as z:
        anchors=L*(saved.read_matrix(z,'point_derivative')*U)
    norms=[];deviations=[];linear=[];nonlinear=[];constants=[]
    for i,encoded in enumerate(rows):
        value=decode(encoded)
        anchor=InputLinearTaylor(domain,arb_mat(1,198,[anchors[i,j] for j in range(74)]+[arb(0)]*124),
                                arb_mat(domain.dimension,198),input_groups=record['input_groups'])
        anchor._linear=arb(0)
        difference=value-anchor
        actual=dict(support=value.support(),linear=value.linear_bound(),nonlinear=value.r,
                    anchor_deviation=difference.support())
        stored=record['rows'][i]
        if stored['component']!=i:
            raise ValueError('every physical output row required in canonical order')
        for key,bound in actual.items():
            if str(bound.fmpq())!=stored[key]['exact']:
                raise ArithmeticError(f'{family} row {i} {key} does not replay exactly')
        norms.append(actual['support']);deviations.append(actual['anchor_deviation'])
        linear.append(actual['linear']);nonlinear.append(actual['nonlinear']);constants.append(difference.constant_bound())
        print(json.dumps(dict(family=family,verified_row=i)),flush=True)
    total=vector_norm(norms);deviation=vector_norm(deviations)
    if (str(total.fmpq())!=record['complete_fixed_family_operator_norm_upper']['exact']
            or str(deviation.fmpq())!=record['anchor_deviation_operator_norm_upper']['exact']):
        raise ArithmeticError('complete operator bounds must replay exactly')
    return dict(all_74_input_and_74_output_bounds_replayed=True,all_anchor_deviations_replayed=True,
        family=family,complete_fixed_family_operator_norm_upper=transport.upper(total),
        anchor_deviation_operator_norm_upper=transport.upper(deviation),
        component_diagnostics=dict(constant_deviation=transport.upper(vector_norm(constants)),
            linear=transport.upper(vector_norm(linear)),nonlinear=transport.upper(vector_norm(nonlinear))),
        record_SHA256=saved.sha(path/'record.json'),models_SHA256=record['models_SHA256'],
        verifier_SHA256=saved.sha(Path(__file__)),Gate7_closed=False,FULL_BHSM_COMPLETE=False)


def main():
    parser=argparse.ArgumentParser()
    for key in ('evidence-root','certificate','out'): parser.add_argument('--'+key,type=Path,required=True)
    args=parser.parse_args();ctx.prec=512
    result=verify(args.evidence_root.resolve(),args.certificate.resolve())
    with args.out.open('xb') as file: file.write(saved.encoded(result))
    print(json.dumps(result),flush=True)


if __name__=='__main__': main()
