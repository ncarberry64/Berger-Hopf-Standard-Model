"""Reconstruct source-bound normalized directional-error matrices."""
import json
import hashlib
from pathlib import Path
import numpy as np
from flint import arb,arb_mat
from bhsm.interface.input_linear_taylor import vector_norm
import evaluate_n12_gate7_coupled_residual_saved as saved


def load_error_map(root,record,adjoint_path):
    if record['source_hashes']['adjoint']!=saved.sha(adjoint_path):
        raise ValueError('same complete-input anchor required')
    adjoint=json.loads(adjoint_path.read_bytes())
    if adjoint['input_map']!=record['input_map']:
        raise ValueError('unchanged common physical input map required')
    family=record['family']
    if family not in ('endpoint','midpoint'): raise ValueError('known source family required')
    kind,index=('endpoint',14) if family=='endpoint' else ('interval',13)
    path=root/f'artifacts/flagship_integration/.primal_mean_value_component_centered_{family}_uniform_df_work/{kind}_{index:03d}/derivative.npz'
    if record['source_hashes'].get(path.relative_to(root).as_posix())!=saved.sha(path):
        raise ValueError('same original full derivative inclusion required')
    U=arb_mat([[arb(v) for v in row] for row in record['input_map']])
    radii=[arb(v) for v in record['axis_correction_radii']]
    result=arb_mat(124,74)
    with np.load(path,allow_pickle=False) as z:
        for offset,uniform_key,point_key in ((0,'selected_line_variation','point_line_map'),
                                             (62,'response_variation','point_response_map')):
            point=arb_mat([[arb(v) for v in row] for row in adjoint[point_key]])
            error=saved.read_matrix(z,uniform_key)*U-point
            for i in range(62):
                radius=radii[offset+i]
                bound=vector_norm([error[i,j] for j in range(74)])
                if not bound<=radius: raise ValueError('original directional-error radius must contain its common-input row')
                if radius.is_zero():
                    if not all(error[i,j].is_zero() for j in range(74)):
                        raise ValueError('zero correction radius requires an exact zero row')
                else:
                    for j in range(74): result[offset+i,j]=error[i,j]/radius
    return result


def load_projected_anchor(root,record):
    import diagnose_n12_gate7_directed_trial_hs_column as base
    p=base.p;residual=p.geometry.residual
    with base.cache.cache_hashes([(p.values,'sha'),(residual.center,'_sha'),(residual.foundation.coordinate.center,'_sha')]):
        local=base.reader.load_inputs(13)
    P=base.matrix(local['frozen_right']).solve(base.matrix(local['test']))
    axisfile=root/'artifacts/action_extension/BHSM_AE4_CURRENT_C2_GREEN_IMAGE_PARTITION_RECONCILIATION.npz'
    with np.load(axisfile,allow_pickle=False) as z: axes=z['current_center_green_image_unit_mid'].copy()
    axes[1:]/=np.linalg.norm(axes[1:],axis=1)[:,None];axes[0]=0
    if hashlib.sha256(np.asarray(axes,dtype='<f8').tobytes()).hexdigest().upper()!=local['binding']['axes_SHA256']:
        raise ValueError('unchanged physical projection required')
    a=[arb(float(v)) for v in axes[14]]
    Q=arb_mat(74,74,[arb(i==j)-a[i]*a[j] for i in range(74) for j in range(74)])
    L=Q*P*(2*arb(float(local['step']))/3)
    family=record['family'];kind,index=('interval',13) if family=='midpoint' else ('endpoint',14)
    path=root/f'artifacts/flagship_integration/.primal_mean_value_component_centered_{family}_uniform_df_work/{kind}_{index:03d}/derivative.npz'
    if record['source_hashes'].get(path.relative_to(root).as_posix())!=saved.sha(path):
        raise ValueError('same point derivative source required')
    U=arb_mat([[arb(v) for v in row] for row in record['input_map']])
    with np.load(path,allow_pickle=False) as z:
        return L*(saved.read_matrix(z,'point_derivative')*U)
