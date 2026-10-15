"""Action-normalized color complement of the saved-real EW constituent forms.

SU3 fluctuations and independent FP ghosts remain nonzero at the retained
zero-color background. The single rank16 trace fixes their normalization;
it is not a tensor copy of the M8 geometric spin module or a physical g3.
These finite classical coefficient-cell forms are not microscopic P_strat.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

import numpy as np
from scipy import sparse
from scipy.linalg import block_diag, cho_factor, cho_solve

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from bhsm.interface.aether_sm_gauge_color_completion_v15_58 import carrier_trace_extension_contract
from bhsm.interface.bhsm_standard_model_gauge_vertices import (
    multiplet_generators, su3_fundamental_generators, structure_constants)
from bhsm.interface.particle_chirality_anomaly_normalization import (
    one_family_multiplets, connection_trace_indices)
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
from bhsm.interface.muon_intrinsic_scalar_discretization import scalar_s3_discretization
from bhsm.interface.muon_parent_positive_brst_ghost import (
    _ghost_form_row, ghost_temporal_moments, smooth_ghost_temporal_values)
from bhsm.interface.muon_parent_positive_coupled_temporal import one_form_point_row
from bhsm.interface.muon_parent_positive_gauge_form import one_form_cell_row, one_form_temporal_moments
from bhsm.interface.muon_parent_mean_causal_action import MAXWELL_TO_CAP
from bhsm.interface.muon_matched_mechanical_source import epsilon

EW = 'artifacts/muon_real_ew_common_forms_20261016/application_run_1'
EW_JSON_SHA = 'b05b563d075fc96537bb034d78caeb572e3aae7c7b8c5d25e0d58f3fd4616470'
EW_NPZ_SHA = '03f7e6b12f348d62cc9c2722e373f4bba8d101f4ba5ba87549e202ff1027fb3d'


def maximum(a):
    return float(np.max(np.abs(a)))


def norm(a):
    return float(sparse.linalg.norm(a) if sparse.issparse(a) else np.linalg.norm(a))


def load_sparse(a, name):
    return sparse.csr_matrix((a[name+'_data'], a[name+'_indices'], a[name+'_indptr']),
        shape=tuple(a[name+'_shape']))


def save_sparse(a, name, value):
    s = sparse.csr_matrix(value)
    s.sum_duplicates(); s.sort_indices(); s.eliminate_zeros()
    a[name+'_data'], a[name+'_indices'], a[name+'_indptr'] = s.data, s.indices, s.indptr
    a[name+'_shape'] = np.array(s.shape, np.int64)


def rank16_generators():
    """Invariant trace basis only, in the actual multiplet ledger order."""
    rows = one_family_multiplets(include_neutral_singlet=True)
    color = np.array([block_diag(*(multiplet_generators(r.name, 'SU3')[i] for r in rows))
                      for i in range(8)])
    weak = np.array([block_diag(*(multiplet_generators(r.name, 'SU2')[i] for r in rows))
                     for i in range(3)])
    hyper = block_diag(*(multiplet_generators(r.name, 'U1')[0] for r in rows))
    generators = np.concatenate((-1j*weak/np.sqrt(2),
        (-1j*hyper/np.sqrt(10/3))[None], -1j*color/np.sqrt(2)))
    gram = -np.einsum('aij,bji->ab', generators, generators).real
    cross_comm = np.array([[a@b-b@a for b in generators[4:]] for a in generators[:4]])
    f = structure_constants(su3_fundamental_generators()) / np.sqrt(2)
    closure = np.array([[a@b-b@a for b in generators[4:]] for a in generators[4:]])
    closure -= np.einsum('abc,cij->abij', f, generators[4:])
    controls = dict(rank16_dimension=generators.shape[-1],
        trace_indices={k:str(v) for k,v in connection_trace_indices().items()},
        unit_trace_Gram_absolute=maximum(gram-np.eye(12)),
        EW_color_commutator_absolute=maximum(cross_comm),
        color_Lie_closure_absolute=maximum(closure),
        nonabelian_color_structure_norm=norm(f),
        quark_color_generator_norm=norm(color),
        lepton_color_generator_absolute=max(maximum(multiplet_generators(name,'SU3'))
            for name in ('L_L','e_c','nu_c')),
        Higgs_color_action='zero by the owned (1,2,1/2) Higgs representation',
        basis='one_family_multiplets order; invariant trace, not an asserted native-spin intertwiner')
    if max(controls[k] for k in ('unit_trace_Gram_absolute','EW_color_commutator_absolute',
            'color_Lie_closure_absolute')) > 2e-14:
        raise ArithmeticError('Owned single-carrier trace algebra failed')
    return generators, f, controls


def channel_indices(channel):
    physical = [((r*5+f)*4+channel)*20+h for r in range(2) for f in range(5) for h in range(20)]
    ghost = [((t*2+r)*4+channel)*20+h for t in range(2) for r in range(2) for h in range(20)]
    return np.array(physical+[800+i for i in ghost]), np.array(ghost)


def scalar_point_maps(E, radial, t):
    """Independent one-color exterior derivative maps on the same trials."""
    h, n = 20, 280
    value = np.zeros((5,h,n)); time = value.copy(); rho = value.copy()
    I = np.eye(h)
    for r in range(2):
        for f in range(5):
            sl = slice((r*5+f)*h,(r*5+f+1)*h)
            value[f,:,sl] = t[0]*radial[r,0]*I
            time[f,:,sl] = t[1]*radial[r,0]*I
            rho[f,:,sl] = t[0]*radial[r,1]*I
    for a in range(2):
        for r in range(2):
            sl = slice(200+(2*a+r)*h,200+(2*a+r+1)*h)
            p,p1,p2=radial[r]; g,g1,g2=t[2+3*a:5+3*a]
            value[0,:,sl],value[1,:,sl]=g1*p*I,g*p1*I
            time[0,:,sl],time[1,:,sl]=g2*p*I,g1*p1*I
            rho[0,:,sl],rho[1,:,sl]=g1*p1*I,g*p2*I
            for i in range(3):
                value[2+i,:,sl]=g*p*E[i]
                time[2+i,:,sl]=g1*p*E[i]
                rho[2+i,:,sl]=g*p1*E[i]
    angle=np.einsum('aij,fjz->afiz',E,value)
    return value,time,rho,angle


def comm(a,b):
    return a@b-b@a


def matrix_curvatures(A,At,Ar,Ea):
    X=At[:,1]-Ar[:,0]+comm(A[:,0],A[:,1])
    T=np.array([At[:,2+i]-Ea[i,:,0]+comm(A[:,0],A[:,2+i]) for i in range(3)])
    R=np.array([Ar[:,2+i]-Ea[i,:,1]+comm(A[:,1],A[:,2+i]) for i in range(3)])
    B=2*A[:,2:].transpose(1,0,2,3).copy()
    for i,j,k in np.argwhere(epsilon()):
        B[i]+=epsilon()[i,j,k]*(Ea[j,:,2+k]+.5*comm(A[:,2+j],A[:,2+k]))
    return X,T,R,B


def matrix_pair(F,G,density,haar):
    e,r,d,k,z=density
    inner=lambda a,b: -float(np.sum(np.einsum('...pij,...pji->...p',a,b)*haar).real)
    X,T,R,B=F; x,t,rr,b=G
    return float(k*inner(X,x)+e*inner(T-z*R,t-z*rr)+r*inner(R,rr)+d*inner(B,b))


def literal_color_control(A,At,Ar,E,Y,haar,radial,metric,density,length,generators,indices):
    """Full rank16 trace and unprojected Haar second variation, independently."""
    u=.37*length; tg=smooth_ghost_temporal_values([u],length)[0]
    # For the independent maps: b,b',g0,g0',g0'',g1,g1',g1''.
    t=np.r_[2*u/length,2/length,tg[0],tg[1]]
    maps=scalar_point_maps(E,radial,t)
    rng=np.random.default_rng(16162026)
    z=rng.normal(size=(8,280))*length/np.sqrt(8*280)
    coeff=[np.einsum('fhz,cz->cfh',m,z) for m in maps[:3]]
    a,at,ar=[np.einsum('ph,cfh,cij->pfij',Y,m,generators[4:]) for m in coeff]
    ea=np.einsum('ph,acfh,cij->apfij',Y,
        np.einsum('afhz,cz->acfh',maps[3],z),generators[4:])
    bg=lambda x: np.broadcast_to(np.einsum('fc,cij->fij',x,generators[:4]),(len(Y),5,16,16))
    baseA,baseAt,baseAr=map(bg,(A,At,Ar))
    def value(s):
        F=matrix_curvatures(baseA+s*a,baseAt+s*at,baseAr+s*ar,s*ea)
        return .5*matrix_pair(F,F,density,haar)
    pt=np.r_[t[:2],tg[0,:2],tg[1,:2]]
    point=one_form_point_row(np.zeros((5,4)),np.zeros((5,4)),np.zeros((5,4)),
        E,radial,metric,density,pt)['Hessian'][np.ix_(indices,indices)]
    target=float(sum(v@point@v for v in z))
    zero=value(0.); sweep=[]
    for step in (.08,.04,.02):
        derivative=(16*(value(step)+value(-step)-2*zero)
            -(value(2*step)+value(-2*step)-2*zero))/(12*step**2)
        sweep.append(dict(step=step,literal=derivative,target=target,absolute_error=abs(derivative-target),
            relative_to_nonzero=abs(derivative-target)/abs(target)))
    # Linear color curvature around zero is computed without subtraction
    # of the nonzero EW action, but still in the full rank16 trace.
    F1=matrix_curvatures(a,at,ar,ea)
    Q=(comm(a[:,0],a[:,1]),
       np.array([comm(a[:,0],a[:,2+i]) for i in range(3)]),
       np.array([comm(a[:,1],a[:,2+i]) for i in range(3)]),
       np.array([sum(epsilon()[i,j,k]*.5*comm(a[:,2+j],a[:,2+k])
           for j in range(3) for k in range(3)) for i in range(3)]))
    linear=tuple(x-y for x,y in zip(F1,Q))
    direct=matrix_pair(linear,linear,density,haar)
    return dict(full_rank16_Haar_linear_curvature_target=direct,
        full_rank16_Haar_linear_curvature_relative=abs(direct-target)/abs(target),
        literal_nonlinear_color_plus_nonzero_EW_action_second_sweep=sweep,
        color_quadratic_curvature_norm=sum(norm(q)for q in Q),
        color_nonabelian_vertices_not_set_zero=True,nonlinear_products_projected_to_20_harmonics=False)


def execute(output, *, ew_application=EW):
    out=Path(output)
    if out.exists(): raise FileExistsError('Preserve independent readouts')
    pins={}
    def pin(path,expected=None):
        p=Path(path);p=p if p.is_absolute()else ROOT/p
        value=sha256(p.read_bytes()).hexdigest()
        if expected is not None and value!=expected: raise ValueError('Pinned bytes changed: '+str(p))
        pins[p.relative_to(ROOT).as_posix()]=value
        return p
    ew=Path(ew_application);ew=ew if ew.is_absolute()else ROOT/ew
    report=json.loads(pin(ew/'result.json',EW_JSON_SHA).read_text())
    with np.load(pin(ew/'forms.npz',EW_NPZ_SHA),allow_pickle=False)as z:old={k:z[k].copy()for k in z.files}
    for path,expected in report['input_and_source_sha256'].items():pin(path,expected)
    generators,f,algebra=rank16_generators()
    extension=carrier_trace_extension_contract()
    E=old['EW_real_angular_derivatives'];radial=old['ghost_radial_value_rate_second'];rw=old['core_coordinate_weights']
    angular=scalar_s3_discretization(3)
    ids=[i for i,row in enumerate(angular['real_basis_labels'])if row[0]in(1,3)]
    Y,haar=angular['real_basis_values'][:,ids],angular['haar_weights']
    index,ghostindex=channel_indices(0)
    arrays=dict(rank16_unit_trace_generators=generators,color_normalized_structure_constants=f,
        single_color_one_form_indices_in_zero_EW_owner=index,single_color_ghost_indices=ghostindex,
        radial_points=old['radial_points'],core_coordinate_weights=rw,EW_real_angular_derivatives=E)
    records=[]
    D0=np.eye(280)[:,200:];DEW=np.eye(1200)[:,800:1120]
    for rec in report['records']:
        side=rec['side'];length=rec['retained_cell_coordinate_length']
        metric,density=(old[side+'_'+name]for name in('positive_metric','positive_two_form_densities'))
        K,G=np.zeros((280,280)),np.zeros((280,280))
        KG,GG=np.zeros((80,80)),np.zeros((80,80))
        moments,gmoments=one_form_temporal_moments(length),ghost_temporal_moments(length)
        channel_residual=0.
        for j in range(4):
            k,g,contact=one_form_cell_row(np.zeros((5,4)),np.zeros((5,4)),np.zeros((5,4)),
                E,radial[j],metric[j],density[j],moments)
            kg,gg=_ghost_form_row(np.zeros((5,4)),E,radial[j],metric[j],gmoments)
            if maximum(contact)!=0:raise ArithmeticError('Zero-color curvature contact is not zero')
            k0,g0=k[np.ix_(index,index)],g[np.ix_(index,index)]
            for c in range(1,4):
                ii,ig=channel_indices(c)
                channel_residual=max(channel_residual,maximum(k[np.ix_(ii,ii)]-k0),maximum(g[np.ix_(ii,ii)]-g0))
            K+=rw[j]*k0;G+=rw[j]*g0
            KG+=rw[j]*kg[np.ix_(ghostindex,ghostindex)];GG+=rw[j]*gg[np.ix_(ghostindex,ghostindex)]
        B=G[200:];F=cho_solve(cho_factor(GG,lower=True),B)
        FP=cho_solve(cho_factor(GG,lower=True),KG)
        Pi=np.eye(280)-D0@cho_solve(cho_factor(KG,lower=True),B)
        fixing=B.T@F
        I8=sparse.eye(8,format='csr')
        expand=lambda x:sparse.kron(I8,sparse.csr_matrix(x),format='csr')
        common={
            'kinetic_Hessian':sparse.block_diag((load_sparse(old,side+'_common_kinetic_Hessian'),MAXWELL_TO_CAP*expand(K)),format='csr'),
            'Gram':sparse.block_diag((load_sparse(old,side+'_common_Gram'),MAXWELL_TO_CAP*expand(G)),format='csr'),
            'lambda_coefficient':sparse.block_diag((load_sparse(old,side+'_scalar_lambda_coefficient'),sparse.csr_matrix((2240,2240))),format='csr'),
            'lambda_nu_squared_coefficient':sparse.block_diag((load_sparse(old,side+'_scalar_lambda_nu_squared_coefficient'),sparse.csr_matrix((2240,2240))),format='csr'),
            'finite_Lorenz_fixing':sparse.block_diag((load_sparse(old,side+'_finite_Lorenz_fixing'),MAXWELL_TO_CAP*expand(fixing)),format='csr'),
            'finite_Lorenz_representative':sparse.block_diag((load_sparse(old,side+'_finite_Lorenz_slice_projector'),expand(Pi)),format='csr'),
            'ghost_Hessian_per_kappa':sparse.block_diag((load_sparse(old,side+'_FP_Hessian_per_kappa'),expand(KG)),format='csr'),
            'ghost_Gram_per_kappa':sparse.block_diag((load_sparse(old,side+'_ghost_Gram_per_kappa'),expand(GG)),format='csr'),
            'weak_gradient_pairing':sparse.block_diag((load_sparse(old,side+'_weak_gradient_pairing'),expand(B)),format='csr'),
            'weak_Lorenz':sparse.block_diag((load_sparse(old,side+'_weak_Lorenz'),expand(F)),format='csr'),
            'gauge_generator_D':sparse.block_diag((sparse.csr_matrix(DEW),expand(D0)),format='csr'),
        }
        for name,value in common.items():save_sparse(arrays,side+'_SM12_'+name,value)
        for name,value in dict(one_form_Hessian_per_kappa=K,one_form_Gram_per_kappa=G,
                FP_Hessian_per_kappa=KG,ghost_Gram_per_kappa=GG,weak_gradient_pairing=B,
                weak_Lorenz=F,FP_Riesz_operator=FP,finite_Lorenz_representative=Pi).items():
            save_sparse(arrays,side+'_single_color_'+name,value)
        literal=literal_color_control(old[side+'_A'][-1],old[side+'_A_time'][-1],old[side+'_A_radial'][-1],
            E,Y,haar,radial[-1],metric[-1],density[-1],length,generators,index)
        if norm(K)==0 or norm(KG)==0 or maximum(K@D0)!=0:
            raise ArithmeticError('Color fluctuation/FP or exact gauge image algebra failed')
        if norm(G[200:,200:]-KG)/norm(KG)>2e-13:
            raise ArithmeticError('Color FP is not the same gradient Gram')
        if literal['full_rank16_Haar_linear_curvature_relative']>2e-12:
            raise ArithmeticError('Independent full-rank16 trace does not reproduce the color form')
        records.append(dict(side=side,coordinate_cell_length=length,common_test_dimension=3440,
            EW_H_test_dimension=1200,color_test_dimension=2240,common_ghost_dimension=960,
            color_ghost_dimension=640,single_color_channels_equal_absolute=channel_residual,
            color_one_form_Hessian_nonzero_norm=norm(K),color_ghost_Hessian_nonzero_norm=norm(KG),
            color_curvature_contact_absolute=0.,color_Higgs_or_EW_mixed_Hessian_absolute=0.,
            zero_mixed_blocks_proved_by_direct_sum_trace_and_Higgs_singlet=True,
            color_Hessian_on_ghost_image_absolute=maximum(K@D0),
            FP_equals_D_Gram_D_relative=norm(G[200:,200:]-KG)/norm(KG),
            finite_Lorenz_representative_idempotence_absolute=maximum(Pi@Pi-Pi),
            finite_Lorenz_representative_on_D_absolute=maximum(Pi@D0),
            literal_full_rank16_action_controls=literal))
        print(json.dumps(dict(completed=side,color_Hessian_norm=norm(K),color_FP_norm=norm(KG),
            literal_relative=literal['full_rank16_Haar_linear_curvature_relative'])),flush=True)
    for name,module in list(sys.modules.items()):
        path=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and path and Path(path).is_relative_to(ROOT):pin(path)
    pin(__file__)
    for path in ('src/bhsm/interface/aether_m5_m4_gauge_higgs_ownership_v15_60.py',
        'src/bhsm/interface/ae4_stratified_dirac_zeta_induced_owner.py',
        'src/bhsm/interface/ae4_current_c2_stop_gauge_brst_calderon.py',
        'src/bhsm/interface/muon_regular_reset_brst_domain.py'):pin(path)
    result=dict(classification='REAL_SM12_CLASSICAL_EW_COLOR_HIGGS_FP_COMMON_COEFFICIENT_FORMS',
        records=records,rank16_trace_controls=algebra,selected_carrier_trace_extension=extension,
        background='Exactly the frozen-real EW midpoint/core4+wall constituent packet; color background0 in that ansatz',
        zero_color_background_does_not_remove_fluctuations_or_ghosts=True,
        internal_normalization='Hcolor=-i Tcolor/sqrt2, -Tr16(Ha Hb)=delta_ab; same single overall action coefficient as SU2',
        physical_g3_or_local_renormalized_residue_selected=False,measured_coupling_or_new_factor_coefficient_used=False,
        coordinate_order='EW1200 then8 colors, each(physical200,exact gauge-gradient one-form image80)',
        ghost_coordinate_order='EW320 then8 colors each80',
        common_classical_operator_map='K=Kkin+lambda*Klambda+(lambda*nu2)*Klambda_nu2; G and finite F=Gghost^-1 B, FP=F D supplied separately',
        finite_Lorenz_representative_is_physical_BRST_quotient=False,
        positive_pairing='Inherited YM common pushforward; never substituted bare fermion N C R^3',
        gauge_statistics='12 real adjoint one-form directions are bosonic; one independent complex FP ghost/antighost pair per direction is Grassmann',
        gauge_gradient_image_coefficients_are_bosonic_one_form_coordinates=True,
        independent_FP_Grassmann_variables_are_not_inserted_into_bosonic_fields=True,
        statistics_multiplicity='Color8 is the Lie algebra dimension, not8 rank16 fermion families or8 bosonic ghost copies',
        grading_scope='AE4 uses statistics supertrace; -2 real ghost weight only after matching operator/domain, not applied as a state count here',
        rank16_trace_basis_identified_with_native_D5_or_M8_spin_basis=False,
        M8_spin16_tensor_SM16_or_extra_UV_fermion_copy_added=False,
        quark_color_generators_preserved_but_fermion_native_vertices_or_loops_evaluated=False,
        color_center_reset_or_outgoing_domain_selected=False,full_graded_native_Dstrat_or_Pstrat_identity=False,
        full_physical_outgoing_E_B_derivative_at_2e_minus10=False,
        physical_stationary_background_solved=False,physical_two_spin_normalization=None,
        physical_muon_magnetic_moment=None,coupled_corrections=0,new_field_profile_or_history_integrations=0,
        input_and_source_sha256=dict(sorted(pins.items())))
    out.mkdir(parents=True);_compressed_npz(out/'forms.npz',arrays)
    result['numerical_sha256']=sha256((out/'forms.npz').read_bytes()).hexdigest()
    (out/'result.json').write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True)
    p.add_argument('--ew-application',default=EW)
    args=p.parse_args();execute(args.output,ew_application=args.ew_application)
