"""Load source-bound base residuals into the unchanged transport state space."""
import gzip
import json
from pathlib import Path
from flint import arb,arb_mat
from bhsm.interface.shared_action_taylor import Taylor,TaylorDomain
import bhsm.interface.shared_action_taylor as state_arithmetic
from bhsm.interface.base_residual_cancellation import BaseResidualBlock
from certify_n12_gate7_endpoint_vector_transport import restore
import evaluate_n12_gate7_coupled_residual_saved as saved


def load_block(folder,parent_path,refined_path,common,embedding,verified):
    parent=json.loads((parent_path/'record.json').read_bytes())
    record=json.loads((folder/'record.json').read_bytes())
    archive=folder/'models.json.gz'
    if (record['algorithm']!='ORIGINAL_DOMAIN_BASE_IMPLICIT_RESIDUAL_VECTOR_V1'
            or record['components']!=124 or record['component_indices']!=list(range(124))
            or record['all_base_components_certified'] is not True
            or record['family']!=parent['family']
            or record['original_state_groups']!=parent['original_state_groups']
            or len(embedding)!=record['state_dimension'] or len(set(embedding))!=len(embedding)
            or any(not 0<=i<common.dimension for i in embedding)
            or record['source_hashes']['parent_record']!=saved.sha(parent_path/'record.json')
            or record['source_hashes']['refined_base_radii']!=saved.sha(refined_path)
            or record['source_hashes']['arithmetic']!=saved.sha(Path(state_arithmetic.__file__))
            or any(record['source_hashes'].get(k)!=v for k,v in verified['paired_source_hashes'].items())
            or saved.sha(archive)!=record['models_SHA256']):
        raise ValueError('complete matching original-domain base residuals required')
    encoded=json.loads(gzip.decompress(archive.read_bytes()))
    if len(encoded)!=124: raise ValueError('all base equations required')
    local=TaylorDomain(record['original_state_groups'],record['state_dimension'])
    residuals=[]
    for i,(row,values) in enumerate(zip(record['rows'],encoded,strict=True)):
        if row['component']!=i or len(values)!=len(embedding)+2: raise ValueError('complete ordered residual coefficients required')
        v=[restore(pair) for pair in values]
        model=Taylor(local,v[0],arb_mat(1,local.dimension,v[1:-1]),v[-1])
        if str(model.support().fmpq())!=row['support']['exact']: raise ArithmeticError('base residual support replay failed')
        coefficients=[arb(0)]*common.dimension
        for j,k in enumerate(embedding): coefficients[k]=v[j+1]
        residuals.append(Taylor(common,v[0],arb_mat(1,common.dimension,coefficients),v[-1]))
    return BaseResidualBlock(residuals,[embedding[i] for i in record['base_error_state_indices']])
