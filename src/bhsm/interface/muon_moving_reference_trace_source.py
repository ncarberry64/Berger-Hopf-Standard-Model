"""Actual pp-rp+rc reference source before finite coefficient restriction."""
from __future__ import annotations
import numpy as np
from .muon_holomorphic_normal_geometry import holomorphic_geometry_rows
from .muon_holomorphic_joint_reference_clock import reference_affine_raw_rate
from .muon_parent_maxwell_full_weak import M
from .muon_parent_retarded_hypercharge import WALL


def moving_reference_profile_source(reference_pair,rho):
    """Hold actual pp fixed, advance both supplied reference affine germs.

    The source sign is -rp_dot+rc_dot in the child's total connection.
    lambda_tau is its owned Eulerian rate slot, not another material
    advection. Realified coefficient duals introduce no source conjugation.
    """
    ref=np.asarray(reference_pair,complex);rates=reference_affine_raw_rate(ref)
    keys=('connection_lambda','lambda_tau','lambda_rho')
    def at(points):
        rows=[holomorphic_geometry_rows(x[:100],points,connection_only=True)['rows']for x in ref]
        values=[np.array([[row[k].value for k in keys]for row in branch])for branch in rows]
        first=[np.array([[row[k].gradient@rate[:100]for k in keys]for row in branch])for branch,rate in zip(rows,rates)]
        return dict(reference_difference=values[0]-values[1],child_source_first=-first[0]+first[1],
                    parent_reference_profile=values[0],child_reference_profile=values[1])
    radial=at(rho);wall=at([WALL])
    image=np.zeros((3,len(rho),5,4),complex);image[:,:,2:]=radial['child_source_first'].T[:,:,None,None]*M[None,None]
    wallimage=np.zeros((3,5,4),complex);wallimage[:,2:]=wall['child_source_first'][0,:,None,None]*M[None]
    return dict(**radial,wall_reference_difference=wall['reference_difference'][0],
        wall_child_source_first=wall['child_source_first'][0],full_material_field_source=image,
        full_material_wall_source=wallimage,reference_affine_raw_rate=rates,
        source_slot_names=('value','Eulerian_time','radial'),actual_parent_source_motion_count=0,
        source_coefficients_conjugated=False)


def fixed_radial_coefficient_test_restriction(field_basis,radial_weights,source_image):
    """Apply the declared basis-dual TESTS and preserve the complete remainder.

    This is a finite test restriction, not a physical state minimization,
    exact full-profile closure, action norm or wall replacement. The real
    frozen radial basis and positive comparison quadrature define its
    coordinate dual. Complex source coefficients remain unconjugated.
    """
    B=np.asarray(field_basis);w=np.asarray(radial_weights,float);src=np.asarray(source_image,complex)
    if (B.ndim!=2 or not np.isrealobj(B)or src.shape!=(3,len(w),5,4)
            or B.shape[0]!=20*len(w)or np.any(w<=0)):
        raise ValueError('original real finite field basis, radial quadrature and full3xNx5x4 source required')
    root=np.repeat(np.sqrt(w),20);Q,T=np.linalg.qr(root[:,None]*B,mode='reduced')
    dual=np.linalg.solve(T,Q.T*root[None,:]);flat=src.reshape(3,-1).T
    coefficients=dual@flat;remainder=flat-B@coefficients
    return dict(original_coefficient_test_dual=dual,represented_source_test_coefficients=coefficients,
        full_source_image=flat,represented_source_image=B@coefficients,full_source_image_complement=remainder,
        test_map_identity_defect=dual@B-np.eye(B.shape[1]),
        weighted_test_complement=B.T@(root[:,None]**2*remainder),
        weighted_source_norms=np.linalg.norm(root[:,None]*flat,axis=0),
        weighted_complement_norms=np.linalg.norm(root[:,None]*remainder,axis=0),
        coefficient_test_condition=float(np.linalg.cond(T)),source_complement_retained=True,
        comparison_quadrature_not_physical_action_norm=True)
