"""Preserve the reproduced local vector models and their exact lineage.

This packages already verified arithmetic; it neither runs a new action
calculation nor promotes local scope to a full-history or Gate-7 theorem.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil


def sha(path):
    digest=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):digest.update(block)
    return digest.hexdigest().upper()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--campaign',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();source=args.campaign.resolve();out=args.out.resolve()
    if out.exists():raise FileExistsError('fresh scientific evidence package required')
    receipt=json.loads((source/'refined_retained_axis_vector_reproduction.json').read_bytes())
    transport=source/'full_input_refined_retained_axis_first'
    if (receipt['transport']['byte_identical'] is not True
            or receipt['transport']['independent_transport_arithmetic'] is not True):
        raise ValueError('independent complete transport pair required')
    for name,digest in receipt['transport']['SHA256'].items():
        if sha(transport/name)!=digest:raise ValueError('transport fingerprint mismatch')
    lineage=[]
    def copy(original,relative):
        destination=out/relative
        destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(original,destination)
        digest=sha(original)
        if sha(destination)!=digest:raise IOError('scientific evidence copy differs')
        lineage.append(dict(path=relative,bytes=destination.stat().st_size,SHA256=digest,
            campaign_source=str(original.relative_to(source)).replace('\\','/')))
    for name in ('record.json','constants.json.gz'):copy(transport/name,name)
    copy(source/'refined_retained_axis_vector_reproduction.json','REPRODUCTION.json')
    for label in ('first','repeat'):
        copy(source/f'refined_retained_axis_verification_{label}.json',f'receipts/transport_{label}.json')
    for family in ('midpoint','endpoint'):
        numerical=receipt['directional_residuals'][family]
        if numerical['byte_identical'] is not True:raise ValueError('reproduced directional equations required')
        for name,digest in numerical['SHA256'].items():
            original=source/f'{family}_directional_residuals_first'/name
            if sha(original)!=digest:raise ValueError('directional equation fingerprint mismatch')
            copy(original,f'{family}/directional_residuals/{name}')
        refined=source/f'{family}_retained_axis_error_first.json'
        if sha(refined)!=receipt['retained_axis_refinements'][family]['SHA256']:
            raise ValueError('refined directional inclusion fingerprint mismatch')
        copy(refined,f'{family}/error_refinement.json')
        for name in ('record.json','models.json.gz'):
            copy(source/f'{family}_base_residual_complete_first'/name,f'{family}/base_residual/{name}')
        copy(source/f'{family}_base_residual_complete_repeat/record.json',f'receipts/{family}_base_repeat.json')
        for name in ('record.json','scalar_model_receipt.json','scalar_model.json.gz'):
            copy(source/f'full_input_{family}_compact_first'/name,f'{family}/parent/{name}')
        copy(source/f'full_input_{family}_adjoint_first.json',f'{family}/anchor_adjoint.json')
        velocity=source/f'{family}_directional_numerator_complete_first'
        for name in ['record.json']+[f'component_{i:02d}.json.gz' for i in range(61)]:
            copy(velocity/name,f'{family}/velocity/{name}')
        copy(velocity.with_suffix('.terms')/'sources.json',f'{family}/velocity.terms/sources.json')
        for label in ('first','repeat'):
            copy(source/f'{family}_complete_verification_{label}.json',f'receipts/{family}_complete_verification_{label}.json')
    result=dict(algorithm='REPRODUCED_LOCAL_VECTOR_EVIDENCE_PACKAGE_V1',files=lineage,
        total_bytes=sum(row['bytes'] for row in lineage),packager_SHA256=sha(Path(__file__)),
        physical_input_columns=74,projected_output_rows=74,interval=13,side='right',
        original_physical_evidence_root_required_for_full_reproduction=True,
        raw_action_derivative_caches_recomputed=False,
        diagnostic_uncorrected_longitudinal_support_is_not_a_certified_total=True,
        diagnostic_explanation='The raw producer field uncorrected_longitudinal_input_support excludes the endpoint base-residual tail and is not used in any certified norm or two-radius bound.',
        full_history_certified=False,Gate7_closed=False,FULL_BHSM_COMPLETE=False)
    (out/'LINEAGE.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(files=len(lineage),bytes=result['total_bytes'],Gate7_closed=False)))


if __name__=='__main__':main()
