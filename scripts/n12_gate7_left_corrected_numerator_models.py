# Left-family specialization: retained endpoint 13 and positive HS input chain.
# The original right-family proof sources remain immutable.
"""Reconstruct normalized derivatives from complete coupled velocity models."""
import gzip
import json
import numpy as np
from flint import arb, arb_mat
from bhsm.interface.input_linear_taylor import InputLinearTaylor
from bhsm.interface.shared_action_taylor import TaylorDomain
from certify_n12_gate7_full_input_transport import read_models
from certify_n12_gate7_endpoint_vector_transport import restore
import n12_gate7_left_saved_family as saved


def dot(a, b):
    return sum((x*y for x,y in zip(a,b,strict=True)),arb(0))


def reconstruct(root, family, parent_path, corrected_path, adjoint_path, refined_path, verified):
    """Return one common domain, descriptor pivot, and all 98 rate rows."""
    import diagnose_n12_gate7_directed_trial_hs_column as base
    p,cert=base.p,base.p.values.cert
    compact=parent_path/'scalar_model_receipt.json'
    native_record=json.loads((parent_path/'record.json').read_bytes())
    if native_record.get('algorithm') == 'LEFT_DEFERRED_BASE_SHARED_SCALAR_PIVOT_V1':
        parent=native_record
        scalar_file=parent_path/'scalar_model.json.gz'
        from pathlib import Path
        producer=Path(__file__).resolve().parent/'certify_n12_gate7_left_deferred_base_output.py'
        if (parent.get('side')!='left' or parent['family']!=family
                or parent['physical_input_columns']!=74 or parent['projected_output_rows']!=74
                or parent.get('saved_scalar_rows')!=1 or parent.get('scalar_row')!=73
                or parent.get('base_cancellation_deferred') is not True
                or parent.get('all_projected_rows_require_complete_velocity_reconstruction') is not True
                or parent['source_hashes']['evaluator']!=saved.sha(producer)
                or parent['scalar_model_SHA256']!=saved.sha(scalar_file)
                or any(parent['source_hashes'].get(k)!=v for k,v in verified['paired_source_hashes'].items())):
            raise ValueError('source-bound native left scalar pivot required')
        domain=TaylorDomain(parent['original_state_groups'],373 if family=='midpoint' else 199)
        def decode(row):
            if len(row)!=198+domain.dimension*198+1:
                raise ValueError('complete common coefficients required')
            v=[restore(pair) for pair in row]
            return InputLinearTaylor(domain,arb_mat(1,198,v[:198]),
                arb_mat(domain.dimension,198,v[198:-1]),v[-1],parent['input_groups'])
        W=decode(json.loads(gzip.decompress(scalar_file.read_bytes())))
        actual={'support':W.support(),'linear':W.linear_bound(),'nonlinear':W.r}
        if any(str(value.fmpq())!=parent['scalar_row_bound'][key]['exact'] for key,value in actual.items()):
            raise ArithmeticError('native scalar bounds failed exact replay')
    elif compact.exists():
        parent=json.loads((parent_path/'record.json').read_bytes())
        receipt=json.loads(compact.read_bytes())
        scalar_file=parent_path/'scalar_model.json.gz'
        if (parent['family']!=family or parent['physical_input_columns']!=74 or parent['projected_output_rows']!=74
                or receipt['parent_record_SHA256']!=saved.sha(parent_path/'record.json')
                or receipt['parent_models_SHA256']!=parent['models_SHA256']
                or receipt['scalar_model_SHA256']!=saved.sha(scalar_file) or receipt['scalar_row']!=73
                or receipt['source_archive_scanned_rows']!=74
                or any(parent['source_hashes'].get(k)!=v for k,v in verified['paired_source_hashes'].items())):
            raise ValueError('exact source-bound descriptor extraction required')
        domain=TaylorDomain(parent['original_state_groups'],373 if family=='midpoint' else 199)
        def decode(row):
            if len(row)!=198+domain.dimension*198+1: raise ValueError('complete common coefficients required')
            v=[restore(pair) for pair in row]
            return InputLinearTaylor(domain,arb_mat(1,198,v[:198]),arb_mat(domain.dimension,198,v[198:-1]),v[-1],parent['input_groups'])
        W=decode(json.loads(gzip.decompress(scalar_file.read_bytes())))
        if str(W.support().fmpq())!=parent['rows'][73]['support']['exact']:
            raise ArithmeticError('compact descriptor support failed exact replay')
    else:
        parent,domain,encoded,decode=read_models(parent_path,family,verified)
        W=None
        for i,row in enumerate(encoded):
            if i==73: W=decode(row)
        if W is None: raise ValueError('complete descriptor pivot required')
    corrected=json.loads((corrected_path/'record.json').read_bytes())
    if (corrected['family']!=family or corrected['all_61_velocity_components_certified'] is not True
            or corrected['components']!=list(range(61)) or len(corrected['records'])!=61
            or corrected['input_map']!=parent['input_map']
            or corrected['original_state_groups']!=parent['original_state_groups']
            or corrected['input_groups']!=parent['input_groups']
            or corrected['axis_correction_radii']!=parent['axis_correction_radii']):
        raise ValueError('all 61 corrected velocity models on the unchanged common domain required')
    for record in (parent,corrected):
        if (record['source_hashes']['adjoint']!=saved.sha(adjoint_path)
                or record['source_hashes']['refined_base_radii']!=saved.sha(refined_path)
                or any(record['source_hashes'].get(k)!=v for k,v in verified['paired_source_hashes'].items())):
            raise ValueError('identical source-bound physical family required')
    binding=saved.sha(corrected_path.with_suffix('.terms')/'sources.json')
    velocities=[]
    for i,record in enumerate(corrected['records']):
        if record['component']!=i: raise ValueError('ordered complete velocity records required')
        path=corrected_path/f'component_{i:02d}.json.gz'
        if saved.sha(path)!=record['models_SHA256']: raise ValueError('velocity coefficient fingerprint mismatch')
        payload=json.loads(gzip.decompress(path.read_bytes()))
        if payload['component']!=i or payload['source_binding']!=binding:
            raise ValueError('velocity source binding mismatch')
        value=decode(payload['coefficients'])
        if (str(value.support().fmpq())!=record['cancelled_support']['exact']
                or str(value.linear_bound().fmpq())!=record['linear']['exact']):
            raise ArithmeticError('velocity support does not replay exactly')
        velocities.append(value)
    middle=family=='midpoint'
    pair='bhsm_midpoint_center_mean_value_left_pair_20260913' if middle else 'bhsm_endpoint_trial_mean_value_bootstrap_left_pair_20260913'
    eigen_name='.coupled_midpoint_eigenpair_pilot_work/interval_013' if middle else '.affine_eigenpair_pilot_work/endpoint_013'
    with np.load(root/'tmp'/pair/'value/first/column.npz',allow_pickle=False) as z, np.load(root/'artifacts/flagship_integration'/eigen_name/'eigenpair.npz',allow_pickle=False) as e:
        centers=[saved.read_matrix(z,f'point_center_{i}',center=True) for i in range(7)]
        center=saved.read_matrix(e,'center_state',center=True)
        ep=saved.read_matrix(e,'eigenpair_center',center=True)
        directions=saved.read_matrix(z,'weighted_tube_directions')
        raw=saved.read_matrix(z,'raw_domain')
    nstate=directions.ncols()
    refined=json.loads(refined_path.read_bytes())
    radii=[arb(v) for v in refined['correction_radii_exact'][:124]]
    U=arb_mat([[arb(v) for v in row] for row in parent['input_map']])
    def linear(c):
        value=InputLinearTaylor(domain,arb_mat(1,198,c),arb_mat(domain.dimension,198),input_groups=parent['input_groups'])
        value._linear=arb(0)
        return value
    def model(c,derivative,rows,offset):
        values=[]
        for i in range(rows):
            a=[derivative[i,j] for j in range(nstate)]+[arb(0)]*124
            a[nstate+offset+i]=radii[offset+i]
            values.append(domain.affine(c[i,0],a))
        return values
    psi=model(ep,centers[3],61,0)
    hard=model(centers[0],centers[4],62,62)
    _,weights,_,_,_=p.values.operands();qw,rw,_,_=cert.metric_data()
    weights,qw,rw=[[arb(float(v)) for v in vv] for vv in (weights,qw,rw)]
    state=[domain.affine(center[i,0],[directions[i,j]/weights[i] for j in range(nstate)]+[arb(0)]*124) for i in range(98)]
    u=[linear([U[i,j]/weights[i] for j in range(74)]+[arb(0)]*124) for i in range(98)]
    s=domain.affine(raw[98,0].mid(),[directions[98,j] for j in range(nstate)]+[arb(0)]*124)
    su=linear([U[98,j] for j in range(74)]+[arb(0)]*124)
    q=[qw[i]*state[37+i] for i in range(37)]
    qu=[qw[i]*u[37+i] for i in range(37)]
    N=[s*v for v in q]+[rw[i]*(hard[61]*psi[i]+s*hard[i]) for i in range(61)]
    Nu=[su*x+s*y for x,y in zip(q,qu)]+[rw[i]*velocities[i] for i in range(61)]
    norm=(dot(N,N).log()/2).exp()
    inner=dot(N,Nu)
    numerator=[Nu[i]/norm-N[i]*inner/(norm**3) for i in range(98)]
    return parent,domain,W,numerator,U,directions
