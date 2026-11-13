"""Literal orientation symmetries of the homogeneous finite action chart.

The SU2 generators combine a constant internal gauge rotation with a
rotation of the three isotropic body-frame indices.  Their combination
leaves the mechanical M_i=lambda*sqrt8*H_i attachment unchanged.  The
central generator is the constant Higgs phase.  These are finite-chart
Ward directions, not a physical gauge quotient of the full event domain.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

import numpy as np

from .muon_parent_maxwell_full_weak import _bracket,FIELD_ORDER
from .muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation


def orientation_coefficient_generators(gauge_labels,scalar_count):
    """Generate D_eta A=[A,eta] and delta H=-rho_H(eta)H.

    For eta=H_k, Omega_ij=-epsilon_ikj/sqrt2 rotates the body indices
    and cancels [sqrt8 H_i,eta].  All independent At/Ar fields and
    central spatial components rotate by their actual representation.
    """
    if type(scalar_count) is not int or scalar_count<4 or scalar_count%4:
        raise ValueError('complete four-real-component Higgs blocks required')
    labels=list(gauge_labels);n=62+len(labels)+scalar_count
    matrices=np.zeros((4,n,n));eps=np.zeros((3,3,3))
    eps[0,1,2]=eps[1,2,0]=eps[2,0,1]=1.
    eps[0,2,1]=eps[2,1,0]=eps[1,0,2]=-1.
    keys={(label['radial'],label['field'],label['internal']):j for j,label in enumerate(labels)}
    if len(keys)!=len(labels):raise ValueError('independent finite gauge labels required')
    real=higgs_u2_real_representation()['real_generators']
    for k in range(4):
        eta=np.eye(4)[k]
        for j,label in enumerate(labels):
            field=label['field'];rad=label['radial'];internal=label['internal']
            bracket=_bracket(np.eye(4)[internal],eta)
            for out in range(4):
                matrices[k,62+keys[(rad,field,out)],62+j]+=bracket[out]
            if k<3 and field in FIELD_ORDER[2:]:
                column=FIELD_ORDER[2:].index(field)
                for row,target in enumerate(FIELD_ORDER[2:]):
                    matrices[k,62+keys[(rad,target,internal)],62+j]+=-eps[row,k,column]/np.sqrt(2)
        start=62+len(labels)
        for block in range(scalar_count//4):
            sl=slice(start+4*block,start+4*block+4)
            matrices[k,sl,sl]=-real[k]
    return matrices


def recorded_orientation_ward_application(coefficients,residual,hessian,gauge_labels,scalar_count,*,normal_index=61,rank_tolerance=1e-11):
    c=np.asarray(coefficients,float);r=np.asarray(residual,float);h=np.asarray(hessian,float)
    generators=orientation_coefficient_generators(gauge_labels,scalar_count)
    if c.shape!=(len(generators[0]),) or r.shape!=c.shape or h.shape!=(len(c),len(c)):
        raise ValueError('one recorded common action vector, residual and Hessian required')
    directions=np.einsum('aij,j->ia',generators,c)
    defects=h@directions+np.einsum('aji,j->ia',generators,r)
    # g^T R=0 and H g+M^T R=0 follow by differentiating S(exp(tM)c)=S(c).
    first=np.einsum('i,ia->a',r,directions)
    singular=np.linalg.svd(directions,compute_uv=False)
    image_rank=int(np.count_nonzero(singular>1e-10*max(float(np.max(singular)),1e-30)))
    indices=np.delete(np.arange(len(c)),normal_index)
    sym=(h+h.T)/2;k=sym[np.ix_(indices,indices)];b=sym[indices,normal_index]
    scale=1/np.sqrt(np.maximum(np.max(abs(k),axis=1),1e-30))
    eigen,u=np.linalg.eigh(scale[:,None]*k*scale[None,:]);inactive=abs(eigen)<=rank_tolerance*max(abs(eigen))
    return dict(orientation_generators=generators,orientation_directions=directions,
        orientation_first_Ward_pairing=first,orientation_differentiated_Ward_defect=defects,
        orientation_direction_singular_values=singular,orientation_image_rank=image_rank,
        orientation_source_projections=directions[indices].T@b,
        scaled_internal_eigenvalues=eigen,scaled_internal_eigenvectors=u,
        internal_congruence_scale=scale,internal_indices=indices,
        literal_numeric_null_directions=scale[:,None]*u[:,inactive],
        literal_numeric_null_source_projections=u[:,inactive].T@(scale*b),
        literal_numeric_nullity=int(np.count_nonzero(inactive)),
        first_Ward_defect_max=float(np.max(abs(first))),
        differentiated_Ward_defect_norm=float(np.linalg.norm(defects)),
        Hessian_on_orientation_norm=float(np.linalg.norm(h@directions)),
        physical_gauge_quotient_selected=False,physical_nullity_identified=False,
        scope='EVALUATED_HOMOGENEOUS_FINITE_CHART_ORIENTATION_WARD_DIRECTIONS')


def materialize_orientation_application(application,output):
    from .muon_parent_retarded_hypercharge import _deterministic_npz
    source=Path(application);out=Path(output)
    if out.exists():raise FileExistsError('preserve prior applications; choose a new output')
    raw=(source/'result.json').read_bytes();receipt=json.loads(raw)
    npz_hash=sha256((source/'application.npz').read_bytes()).hexdigest()
    if npz_hash!=receipt['numerical_sha256']:raise ValueError('coefficient bytes disagree with action receipt')
    with np.load(source/'application.npz',allow_pickle=False) as f:
        result=recorded_orientation_ward_application(f['updated_coefficients'],f['updated_residual'],f['updated_hessian'],
            receipt['gauge_labels'],receipt['scalar_unknowns'])
    arrays={k:v for k,v in result.items() if isinstance(v,np.ndarray)}
    out.mkdir(parents=True);_deterministic_npz(out/'application.npz',arrays)
    metadata={k:v for k,v in result.items() if not isinstance(v,np.ndarray)}
    metadata.update(consumed_application_sha256=npz_hash,consumed_receipt_sha256=sha256(raw).hexdigest(),
        producer_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        numerical_sha256=sha256((out/'application.npz').read_bytes()).hexdigest(),
        infinitesimal_law='delta A_t/r=[A_t/r,eta]; delta A_i=[A_i,eta]+Omega_ij A_j; delta H=-rho_H(eta)H',
        Ward_law='R^T M c=0; H M c+M^T R=0',
        domain_scope='homogeneous n0 body frame; all finite radial/time columns rotate together',
        normal_source_projection='g_internal^T B; normal coordinate is invariant under these transformations',
        numeric_rank_is_action_orbit_count=False,
        frozen_matrix_nullity_proved=False,finite_residual_is_pointwise_action_solution=False,
        stationary_E1_claim=False,physical_Pauli_contraction=False,
        error_scope='floating-point Ward application and literal eigendirections; no exact stored-matrix null theorem or physical-domain quotient certificate')
    (out/'result.json').write_text(json.dumps(metadata,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return metadata


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--application',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();print(json.dumps(materialize_orientation_application(a.application,a.output),sort_keys=True))
