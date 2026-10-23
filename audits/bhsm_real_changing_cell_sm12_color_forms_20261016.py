"""Append color8 to the exact supplied changing-real EW/Higgs coefficient forms.

Every metric, clock, quadrature and fixed trial basis comes from the consumed
changing-EW archive. This does not inherit the fermion quadrature check or
construct a physical color background, coupling, native domain or P_strat.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

import numpy as np
from scipy import sparse
from scipy.linalg import cho_factor, cho_solve

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'audits'))
import bhsm_real_color_common_forms_20261016 as color
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
from bhsm.interface.muon_parent_positive_coupled_temporal import one_form_point_row
from bhsm.interface.muon_parent_mean_causal_action import MAXWELL_TO_CAP
from bhsm.interface.muon_intrinsic_scalar_discretization import scalar_s3_discretization
from bhsm.interface.muon_matched_mechanical_source import epsilon

COLOR_PRODUCER_SHA='cc72f127af65009e14a2d5f78009d1026a372442143416ce5be9a73c7b6670ec'


def point_unit_color(E,radial,tg,b,bp,metric,density):
    """Literal scalar-unit d/dagger form; d² is retained as an exact identity."""
    t=np.r_[b,bp,tg[0],tg[1]]
    V,Vt,Vr,Ea=color.scalar_point_maps(E,radial,t)
    X=Vt[1]-Vr[0]
    T=np.array([Vt[2+i]-Ea[i,0]for i in range(3)])
    R=np.array([Vr[2+i]-Ea[i,1]for i in range(3)])
    B=2*V[2:].copy()
    for i,j,k in np.argwhere(epsilon()):B[i]+=epsilon()[i,j,k]*Ea[j,2+k]
    e,r,d,k,z=density
    curves=(X,T,R,B)
    # Exact gauge-gradient columns have d(d eta)=0. The actual numerical
    # direct-map residual is returned, not hidden by a new projection.
    C=np.concatenate((np.sqrt(k)*X,np.sqrt(e)*(T-z*R).reshape(60,280),
        np.sqrt(r)*R.reshape(60,280),np.sqrt(d)*B.reshape(60,280)))
    K=np.zeros((280,280));K[:200,:200]=C[:,:200].T@C[:,:200]
    mu,gt,gr,gs,beta,radius=metric
    normal=V[0]-beta*V[1]
    G=gt*normal.T@normal+gr*V[1].T@V[1]+gs*sum(v.T@v for v in V[2:])
    eta=np.concatenate([tg[a,0]*radial[j,0]*np.eye(20)for a in range(2)for j in range(2)],axis=1)
    et=np.concatenate([tg[a,1]*radial[j,0]*np.eye(20)for a in range(2)for j in range(2)],axis=1)
    er=np.concatenate([tg[a,0]*radial[j,1]*np.eye(20)for a in range(2)for j in range(2)],axis=1)
    na=et-beta*er
    KG=gt*na.T@na+gr*er.T@er+gs*sum((a@eta).T@(a@eta)for a in E)
    GG=mu*(eta.T@eta)
    return K,G,KG,GG,curves,float(np.max(abs(C[:,200:])))


def independent_Haar_probe(curves,z,Y,haar,gram,density):
    """Literal curvature values and the actual full-rank16 trace Gram."""
    coeff=[np.einsum('...hz,cz->...hc',a,z)for a in curves]
    values=[np.einsum('ph,...hc->...pc',Y,a)for a in coeff]
    # Retain the coframe component index while summing through NumPy.
    inner=lambda a,b:float(np.sum(np.einsum('...pc,...pd,cd->...p',a,b,gram)*haar))
    X,T,R,B=values;e,r,d,k,shift=density
    return k*inner(X,X)+e*inner(T-shift*R,T-shift*R)+r*inner(R,R)+d*inner(B,B)


def relative(a,b):
    return color.norm(a-b)/max(color.norm(a),color.norm(b),np.finfo(float).tiny)


def execute(ew_application,output):
    application,out=Path(ew_application).resolve(),Path(output).resolve()
    if out.exists():raise FileExistsError('Preserve independent applications')
    pins={}
    def pin(path,expected=None):
        path=Path(path);path=path if path.is_absolute()else ROOT/path
        value=sha256(path.read_bytes()).hexdigest()
        if expected is not None and value!=expected:raise ValueError('Pinned input changed: '+str(path))
        label=path.relative_to(ROOT).as_posix()if path.is_relative_to(ROOT)else'retained_inputs/'+path.name
        pins[label]=value
        return path
    report=json.loads(pin(application/'result.json').read_text())
    if not report['classification'].startswith('ACTUAL_CHANGING_REAL_ONE_CELL_EW4_HIGGS_FP'):
        raise ValueError('Actual changing-real EW component required')
    if not report.get('rounded_sigma_not_used_to_reconstruct_production_weight',False):
        raise ValueError('The supplied production metric must use the stable probability-weight owner')
    if report['time_order_per_tent_half']<6:
        raise ValueError('The known degree10 ghost moments require at least Gauss6 per tent half')
    source=pin(application/'changing_forms.npz',report['numerical_sha256'])
    for path,expected in report['input_and_source_sha256'].items():pin(path,expected)
    pin(ROOT/'audits/bhsm_real_color_common_forms_20261016.py',COLOR_PRODUCER_SHA)
    with np.load(source,allow_pickle=False)as z:old={k:z[k].copy()for k in z.files}
    generators,f,algebra=color.rank16_generators()
    gram=-np.einsum('cij,dji->cd',generators[4:],generators[4:]).real
    angular=scalar_s3_discretization(3)
    ids=[i for i,row in enumerate(angular['real_basis_labels'])if row[0]in(1,3)]
    Y,haar=angular['real_basis_values'][:,ids],angular['haar_weights']
    E=old['EW4_real_angular_derivatives']
    if not np.array_equal(E,angular['real_angular_derivative_matrices'][:,ids][:,:,ids]):
        raise ValueError('The exact same fixed angular coordinate basis is required')
    arrays=dict(rank16_unit_trace_generators=generators,color_structure_constants=f,
        EW4_real_angular_derivatives=E)
    records=[];comparisons=[];previous={}
    index,_=color.channel_indices(0)
    D0=np.eye(280)[:,200:];DEW=np.eye(1200)[:,800:1120]
    for rec in report['records']:
        side,q=rec['side'],rec['radial_order'];prefix=f'{side}_radial{q}_'
        rho=old[prefix+'radial_points'];rw=old[prefix+'radial_coordinate_weights']
        u=old[prefix+'temporal_u'];tw=old[prefix+'temporal_coordinate_weights']
        clock=old[prefix+'temporal_coordinate_time'];tg=old[prefix+'ghost_temporal_value_rate_second']
        radial=old[prefix+'ghost_radial_value_rate_second']
        metric=old[prefix+'positive_metric'];density=old[prefix+'positive_two_form_densities']
        if len(rw)!=q or metric.shape!=(len(u),q+1,6)or density.shape!=(len(u),q+1,5):
            raise ValueError('Complete supplied changing-core coefficient arrays required')
        if len(u)!=2*report['time_order_per_tent_half']or not np.array_equal(clock,u+rec['future_coordinate_time_origin']):
            raise ValueError('Exact original changing-cell time/clock incidence required')
        length=rec['retained_cell_length']
        K,G=np.zeros((280,280)),np.zeros((280,280));KG,GG=np.zeros((80,80)),np.zeros((80,80))
        z=np.random.default_rng(16162026).normal(size=(8,280))*length/np.sqrt(8*280)
        direct=0.;max_gradient_curvature=0.;owner_controls=[]
        for it,(time,weight,ghost)in enumerate(zip(u,tw,tg)):
            b=2*min(time/length,1-time/length);bp=(2 if time<length/2 else-2)/length
            for j in range(q):
                k,g,kg,gg,curves,residual=point_unit_color(E,radial[j],ghost,b,bp,metric[it,j],density[it,j])
                scale=weight*rw[j]
                K+=scale*k;G+=scale*g;KG+=scale*kg;GG+=scale*gg
                max_gradient_curvature=max(max_gradient_curvature,residual)
                direct+=scale*independent_Haar_probe(curves,z,Y,haar,gram,density[it,j])
                if it==0 and j==0:
                    tf=np.r_[b,bp,ghost[0,:2],ghost[1,:2]]
                    reference=one_form_point_row(np.zeros((5,4)),np.zeros((5,4)),np.zeros((5,4)),
                        E,radial[j],metric[it,j],density[it,j],tf)
                    owner_controls.append(dict(time_index=it,radial_index=j,
                        Hessian_relative=relative(k,reference['Hessian'][np.ix_(index,index)]),
                        Gram_relative=relative(g,reference['Gram'][np.ix_(index,index)])))
        target=float(sum(v@K@v for v in z));probe=abs(target-direct)/max(abs(target),abs(direct),np.finfo(float).tiny)
        B=G[200:];F=cho_solve(cho_factor(GG,lower=True),B)
        Pi=np.eye(280)-D0@cho_solve(cho_factor(KG,lower=True),B)
        expand=lambda a:sparse.kron(sparse.eye(8,format='csr'),sparse.csr_matrix(a),format='csr')
        use=lambda name:color.load_sparse(old,prefix+name)
        common={
            'kinetic_Hessian':sparse.block_diag((use('common_kinetic_Hessian'),MAXWELL_TO_CAP*expand(K)),format='csr'),
            'Gram':sparse.block_diag((use('common_Gram'),MAXWELL_TO_CAP*expand(G)),format='csr'),
            'lambda_coefficient':sparse.block_diag((use('scalar_lambda_coefficient'),sparse.csr_matrix((2240,2240))),format='csr'),
            'lambda_nu_squared_coefficient':sparse.block_diag((use('scalar_lambda_nu_squared_coefficient'),sparse.csr_matrix((2240,2240))),format='csr'),
            'finite_Lorenz_fixing':sparse.block_diag((use('finite_Lorenz_fixing'),MAXWELL_TO_CAP*expand(B.T@F)),format='csr'),
            'finite_Lorenz_representative':sparse.block_diag((use('finite_Lorenz_slice_projector'),expand(Pi)),format='csr'),
            'ghost_Hessian_per_kappa':sparse.block_diag((use('FP_Hessian_per_kappa'),expand(KG)),format='csr'),
            'ghost_Gram_per_kappa':sparse.block_diag((use('ghost_Gram_per_kappa'),expand(GG)),format='csr'),
            'weak_gradient_pairing':sparse.block_diag((use('weak_gradient_pairing'),expand(B)),format='csr'),
            'weak_Lorenz':sparse.block_diag((use('weak_Lorenz'),expand(F)),format='csr'),
            'gauge_generator_D':sparse.block_diag((sparse.csr_matrix(DEW),expand(D0)),format='csr'),
        }
        for name,value in common.items():color.save_sparse(arrays,prefix+'SM12_'+name,value)
        unit=dict(one_form_Hessian=K,one_form_Gram=G,ghost_Hessian=KG,ghost_Gram=GG,weak_Lorenz=F)
        for name,value in unit.items():color.save_sparse(arrays,prefix+'single_color_'+name,value)
        for name in ('radial_points','radial_coordinate_weights','temporal_u','temporal_coordinate_time',
                'temporal_coordinate_weights','ghost_temporal_value_rate_second','ghost_radial_value_rate_second',
                'positive_metric','positive_two_form_densities','pushforward_weight'):
            arrays[prefix+name]=old[prefix+name]
        if probe>2e-12 or max(max(c['Hessian_relative'],c['Gram_relative'])for c in owner_controls)>2e-12:
            raise ArithmeticError('Independent point-owner/Haar color form control failed')
        records.append(dict(side=side,radial_order=q,time_order_per_tent_half=report['time_order_per_tent_half'],
            coordinate_time_minimum=float(clock.min()),coordinate_time_maximum=float(clock.max()),
            exact_supplied_time_and_radial_rules_retained=True,common_bosonic_test_dimension=3440,
            separate_Grassmann_ghost_dimension=960,color_ghost_form_nonzero_norm=color.norm(KG),
            color_one_form_Hessian_nonzero_norm=color.norm(K),color_Hessian_on_D_absolute=color.maximum(K@D0),
            FP_equals_D_Gram_D_relative=relative(KG,G[200:,200:]),
            Pi_idempotence_absolute=color.maximum(Pi@Pi-Pi),
            direct_finite_map_d_squared_curvature_roundoff_absolute=max_gradient_curvature,
            structured_Hessian_exact_d_squared_identity_retained=True,
            independent_zero_connection_existing_point_owner=owner_controls,
            independent_full_changing_Haar_rank16_trace_relative=probe))
        if side in previous:
            oldq,oldunit,oldcommon=previous[side]
            table={name:dict(symmetric_Frobenius_relative=relative(value,oldunit[name]),
                maximum_absolute_entry=color.maximum(value-oldunit[name]))for name,value in unit.items()}
            comparisons.append(dict(side=side,radial_orders=[oldq,q],single_color=table,
                common_SM12={name:dict(symmetric_Frobenius_relative=relative(value,oldcommon[name]),
                    maximum_absolute_entry=float(np.max(abs((value-oldcommon[name]).data)))if(value-oldcommon[name]).nnz else 0.)
                    for name,value in common.items()},
                identical_fixed_trial_columns_and_supplied_clock=True))
        previous[side]=q,unit,common
        print(json.dumps(dict(completed=side,radial_order=q,Haar_trace_relative=probe)),flush=True)
    for name,module in list(sys.modules.items()):
        path=getattr(module,'__file__',None)
        if(name.startswith('bhsm.')or name=='bhsm_real_color_common_forms_20261016')and path and Path(path).is_relative_to(ROOT):pin(path)
    pin(__file__)
    result=dict(classification='ACTUAL_CHANGING_REAL_SM12_CLASSICAL_COLOR_EW_HIGGS_FP_FORMS',
        records=records,radial_comparisons=comparisons,radial_orders=report['radial_orders'],
        time_order_per_tent_half=report['time_order_per_tent_half'],rank16_trace_controls=algebra,
        consumed_EW_classification=report['classification'],consumed_EW_numerical_sha256=report['numerical_sha256'],
        density_scope='Exact positive_metric and density arrays from the consumed EW archive; no recomputation from saved sigma',
        consumed_density_owner=report.get('stable_weight_owner',report.get('positive_geometry_owner',
            report.get('YM_density_owner','See pinned EW source and receipt'))),
        density_or_radial_precision_inferred_from_fermion_forms=False,
        full_actual_EW_Higgs_matrices_copied_without_modification=True,
        zero_color_background_scope='Retained declared EW background ansatz; not a physical SM12 stationary state',
        color_gradient_image_coordinates_are_bosonic_and_separate_from_FP_Grassmann_variables=True,
        EW_color_or_Higgs_color_mixing='Exactly zero by commuting trace-orthogonal Lie factors and color-singlet Higgs',
        physical_color_coupling_or_new_continuous_coefficient_selected=False,
        scalar_matching_lambda_and_nu_squared_selected=False,
        microscopic_Pstrat_identity_or_M8_SM_tensor_copy_added=False,
        global_reset_native_BRST_quotient_or_outgoing_domain_completed=False,
        physical_radial_or_time_convergence_passed=False,full_physical_E_B_derivative_at_2e_minus10=False,
        physical_two_spin_normalization=None,physical_muon_magnetic_moment=None,coupled_corrections=0,
        new_history_or_field_profile_evaluations=0,input_and_source_sha256=dict(sorted(pins.items())))
    out.mkdir(parents=True);_compressed_npz(out/'changing_SM12_forms.npz',arrays)
    result['numerical_sha256']=sha256((out/'changing_SM12_forms.npz').read_bytes()).hexdigest()
    (out/'result.json').write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ew-application',required=True)
    p.add_argument('--output',required=True);args=p.parse_args()
    execute(args.ew_application,args.output)
