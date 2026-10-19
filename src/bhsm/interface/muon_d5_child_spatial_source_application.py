"""Consume equation-derived child wall-gauge source on the same child domain.

Both value-compatible orientation candidates and all six free rotation
coefficients are returned. No candidate, boundary state or rotation is
selected by its fermion trace. Geometry and the computed normal source
are unchanged by these additional gauge-coordinate columns.
"""
from __future__ import annotations
import numpy as np
from .muon_d5_child_same_direction_application import _differential_columns,recover_cached_original_coefficients
from .muon_d5_event_bundle_incidence import original_event_coefficients
from .muon_d5_fitted_birth_domain import fitted_d5_coefficients
from .muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace
from .muon_parent_retarded_hypercharge import WALL


def evaluate_child_spatial_source(history,child,field_corrections,free_rotation_coefficients,*,candidate_indices=(2,3)):
    """Append the solved field-source particular and its free rotation image.

    The constant original wall-lift coefficient extension has zero added
    coordinate-time derivative and zero added velocity coordinate. This
    is an explicit provisional kinematic extension, not a field equation
    or a choice of physical exterior/time data.
    """
    field=np.asarray(field_corrections,complex);free=np.asarray(free_rotation_coefficients,complex)
    if field.ndim!=2 or field.shape[1]!=268 or free.shape!=(len(field),268,6):
        raise ValueError('complete equation-derived raw268 field/rotation columns required')
    if not np.isfinite(field).all() or not np.isfinite(free).all():raise ValueError('finite field source columns required')
    candidates=tuple(candidate_indices)
    if not candidates or len(set(candidates))!=len(candidates) or any(not 0<=j<len(field) for j in candidates):
        raise ValueError('explicit saved candidate indices required')
    columns=np.concatenate([np.column_stack((field[j],free[j])) for j in candidates],axis=-1)
    held=np.r_[np.arange(168),np.arange(180,268)]
    if np.any(columns[held]!=0):raise ValueError('this append owns only the original12 spatial wall-lift gauge coordinates')
    t,r=np.asarray(child['original_child_coordinates']);count=columns.shape[1]
    directions=dict(raw=columns,parent=np.zeros((268,count),complex),references=np.zeros((2,268,count),complex))
    c=original_event_coefficients(history,float(t),[r],side='child',directions=directions)
    wall=original_event_coefficients(history,0.,[WALL],side='child',directions=directions)
    full=full_d5_localized_lepton_trace();d=_differential_columns(c,full,count)
    out=dict(child_field_source_columns268=columns,child_field_source_coordinate_time_columns268=np.zeros_like(columns),
        child_field_candidate_indices=np.asarray(candidates,dtype=np.int64),
        child_field_connection_at_fitted_point=c['gauge_connection_material_first'][:,0],
        child_field_connection_at_wall=wall['gauge_connection_material_first'][:,0])
    # These zeros follow from the operator's actual geometry dependence,
    # rather than assigning an unknown geometric/native source to zero.
    geometry_keys=('lapse','radial_coframe','radius','coordinate_shift','sigma','sigma_radial','sigma_coordinate_time','volume_density')
    geometry=max(float(np.max(abs(c[key+'_first']))) for key in geometry_keys)
    if geometry!=0:raise ValueError('a purported pure gauge source moves the child geometry')
    chart=dict(forward_jacobian=child['child_fitted_forward_jacobian'],inverse_jacobian=child['child_fitted_inverse_jacobian'],
        forward_jacobian_source=np.zeros((2,2)))
    value_checks=[];source_norms=[]
    for eps,name in ((1,'plus'),(-1,'minus')):
      for branch in ('particle','conjugate'):
        prefix='child_'+name+'_'+branch+'_'
        # Recover values from the completed operator; its updated source
        # does not enter value recovery. Original time/radial jets are unused.
        X=chart['inverse_jacobian'];tf,nf=child[prefix+'time64'],child[prefix+'normal64']
        values=(tf*X[0,0]+nf*X[0,1],tf*X[1,0]+nf*X[1,1],child[prefix+'body64'])
        live=d[eps][0]['value']['blocks'][branch]
        value_checks.extend(float(np.max(abs(value-live[key][0]))) for value,key in zip(values,('time','radial','body')))
        apps=[]
        for j in range(count):
            source=tuple(d[eps][j]['first']['blocks'][branch][key][0] for key in ('time','radial','body'))
            apps.append(fitted_d5_coefficients(*values,chart,source=source))
        for ci,index in enumerate(candidates):
            tag='candidate'+str(index)+'_'+prefix
            for key in ('time','normal','body'):
                increments=np.array([app[key+'_source'] for app in apps[ci*7:(ci+1)*7]])
                out[tag+key+'_spatial_field_additional_source64']=increments
                out[tag+key+'_corrected_particular_source64']=child[prefix+key+'_source64']+increments[0]
                source_norms.append(float(np.max(abs(increments))))
    report=dict(classification='EVALUATED_SPATIAL_CONSTRAINT_CHILD_FIELD_SOURCE_ON_SAME_VALID_DOMAIN',
        candidate_indices=list(candidates),candidate_selected_as_physical_map=False,
        source_columns_per_candidate='equation-derived field particular followed by six free base/gauge rotation coefficient columns',
        field_extension='constant raw168:180 original spatial wall-lift coefficients through the child cell; additional raw time derivative and velocity coordinates explicitly zero in this provisional extension',
        physical_field_time_equation_solved=False,physical_rotation_coefficients=None,
        child_normal_displacement_source_reused=True,child_free_normal_rate_source_retained=True,
        prescribed_born_parent_reference_source_reused=True,
        additional_geometry_density_chart_source_from_pure_gauge_exact_max=geometry,
        original_value_identity_max=max(value_checks),additional_operator_source_max=max(source_norms),
        normal_or_birth_domain_recomputed=False,child_value_operator_recomputed=False,
        inherited_additional_gauge_source_scope='only child own wall-gauge correction; independently required inherited field variations remain open',
        full_physical_derivative=False,physical_admission=False,physical_guard=2e-10,
        normal_profile_normalization=None,physical_outer_conditions_solved=False,child_D5_solution_residual=None,
        local_native_removal_repeated=False)
    return out,report
