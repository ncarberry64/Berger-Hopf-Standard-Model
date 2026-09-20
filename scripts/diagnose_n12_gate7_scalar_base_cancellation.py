"""Check base-error cancellation on the retained descriptor before transport."""
import argparse
import gzip
import json
from pathlib import Path
import sys
import numpy as np
from flint import arb,arb_mat,ctx
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
from bhsm.interface.shared_action_taylor import TaylorDomain
from bhsm.interface.input_linear_taylor import InputLinearTaylor
from bhsm.interface.common_input_error_full_pullback import pullback_all_errors
from bhsm.interface.base_residual_cancellation import weighted_tail_at_input,weighted_tail_on_physical_input
from certify_n12_gate7_endpoint_vector_transport import restore,upper
import n12_gate7_base_residual_models as residual_models
import n12_gate7_common_input_error_maps as maps
import evaluate_n12_gate7_coupled_residual_saved as saved


def main():
    parser=argparse.ArgumentParser()
    for name in ('evidence-root','parent','base-residual','refined','adjoint','out'):
        parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args();ctx.prec=512
    if args.out.exists(): raise FileExistsError('fresh scalar diagnostic required')
    root=args.evidence_root.resolve()
    import bhsm.interface
    bhsm.interface.__path__.insert(0,str(root/'src/bhsm/interface'))
    verified=saved.evaluate(root)
    parent=json.loads((args.parent/'record.json').read_bytes())
    dim={'midpoint':373,'endpoint':199}[parent['family']]
    domain=TaylorDomain(parent['original_state_groups'],dim)
    block=residual_models.load_block(args.base_residual,args.parent,args.refined,domain,list(range(dim)),verified)
    receipt=json.loads((args.parent/'scalar_model_receipt.json').read_bytes())
    scalar=args.parent/'scalar_model.json.gz'
    if receipt['scalar_model_SHA256']!=saved.sha(scalar): raise ValueError('exact descriptor coefficients required')
    v=[restore(pair) for pair in json.loads(gzip.decompress(scalar.read_bytes()))]
    old=InputLinearTaylor(domain,arb_mat(1,198,v[:198]),arb_mat(dim,198,v[198:-1]),v[-1],parent['input_groups'])
    corrected,weighted=block.cancel(old)
    error=maps.load_error_map(root,parent,args.adjoint)
    with np.load(root/'artifacts/action_extension/BHSM_AE4_CURRENT_C2_GREEN_IMAGE_PARTITION_RECONCILIATION.npz',allow_pickle=False) as z:
        a=z['current_center_green_image_unit_mid'][14].copy();a/=np.linalg.norm(a)
    axis=arb_mat(74,1,[arb(float(x)) for x in a])
    direction=arb_mat(198,1,axis.entries()+(error*axis).entries())
    extra_axis=weighted_tail_at_input(weighted,direction)
    extra_physical=weighted_tail_on_physical_input(weighted,[(74,error)])
    restricted=corrected.at_input(direction)
    pulled=pullback_all_errors(corrected,[(74,error)])
    result=dict(scope='BASE_CANCELLED_FIXED_DESCRIPTOR_DIAGNOSTIC_NOT_COMPLETE_TRANSPORT',family=parent['family'],
        original_axis_support=upper(old.at_input(direction).support()),
        corrected_axis_support=upper(restricted.support()+extra_axis),
        corrected_axis_linear=upper(restricted.linear_bound()),original_axis_remainder=upper(restricted.r),
        added_axis_residual_remainder=upper(extra_axis),added_physical_residual_remainder=upper(extra_physical),
        corrected_physical_input_support=upper(pulled.support()+extra_physical),
        largest_remaining_base_coefficient=upper(max(abs(corrected.a[i,j]).upper() for i in block.indices for j in range(198))),
        source_hashes=dict(parent=saved.sha(args.parent/'record.json'),scalar=saved.sha(scalar),
            base_residual=saved.sha(args.base_residual/'record.json'),evaluator=saved.sha(Path(__file__))),
        Gate7_closed=False,FULL_BHSM_COMPLETE=False)
    args.out.write_bytes(saved.encoded(result))
    print(json.dumps({k:(v.get('approximate') if isinstance(v,dict) and 'approximate' in v else v)
                      for k,v in result.items() if k!='source_hashes'},indent=2))


if __name__=='__main__': main()
