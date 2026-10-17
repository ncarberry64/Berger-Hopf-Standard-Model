"""Actual SU2 primary corners and unprojected temporal commutator tests.

Uses saved same-ea02 point/density/clock operands. The additional temporal
weak tests [At,phi T_a] are functional tests, never admitted state columns.
No action gradient, field/source history, projection or correction is run.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
CURRENT='artifacts/muon_baton_zoo_maximal_current_realization_20261013'
RADIAL='artifacts/muon_baton_zoo_radial_convergence_20261014'
RUNTIME=CURRENT+'/actual_new620_fresh_native_MP_new_exact_R7_clock_control_run_1'
TARGET=CURRENT+'/actual_linear_cut_compatible368_MP_full_operator_blocked_run_2/actual_precise_direct_CHILD620_and_full368_canonical_source_operands.npz'
CLOCK=CURRENT+'/actual_same_cut_native_MP_matrixfree_continuous_clock_run_1/actual_continuous_phase210_clock_and_same_owner_point_density_rate.npz'


def run(repository,central_folder,position_folder,output):
    root,cdir,pdir,out=map(lambda p:Path(p).resolve(),(repository,central_folder,position_folder,output))
    out.mkdir(parents=True,exist_ok=False);pins={};producer=Path(__file__).read_bytes();(out/'executed_producer.py').write_bytes(producer)
    def pin(path):
        p=Path(path);p=p if p.is_absolute()else root/p
        k=p.relative_to(root).as_posix()if p.is_relative_to(root)else str(p);pins[k]=sha256(p.read_bytes()).hexdigest();return p
    def read(path):
        p=pin(path)
        if p.suffix=='.json':return json.loads(p.read_bytes())
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    def module(name,path):
        p=pin(path);s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
    sys.path[:0]=[str(root/'src'),str(root/'scripts')]
    from flint import ctx,acb,acb_mat
    from bhsm.interface.muon_stored_admission_correction import _matrix,_upper
    from bhsm.interface.muon_stored_fiber_canonical_tangent import _split
    from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
    from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase
    from bhsm.interface.muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation
    from bhsm.interface.muon_parent_mean_causal_action import MAXWELL_TO_CAP
    from bhsm.interface.muon_parent_retarded_hypercharge import ALPHA
    from bhsm.interface.muon_literal_euclidean_wall_action import VOLUME
    ctx.prec=256
    module('bhsm_baton_zoo_exact_acb_packets',RUNTIME+'/bhsm_baton_zoo_exact_acb_packets_imported_runtime.py')
    ex=module('bhsm_exact_action_balls',RUNTIME+'/bhsm_exact_action_balls_imported_runtime.py')
    packed=module('nonabelian_corner_scalar',RUNTIME+'/new620_fresh_actual_native_MP_scalar_imported_runtime.py')
    chart=module('nonabelian_corner_chart4',RUNTIME+'/new620_fresh_same_material_equations_chart4_imported_runtime.py')
    def exact(z,k):return ex.parse_acb_exact_dyadic(z,k+'_exact')
    def hi(z,k):return _matrix(z[k+'_high'])+_matrix(z[k+'_low'])
    def rows(a,ids):return acb_mat([[a[int(i),j]for j in range(a.ncols())]for i in ids])
    def C(v):return v if isinstance(v,acb)else acb(complex(v))
    def add(a,b):return[x+y for x,y in zip(a,b)]
    def sub(a,b):return[x-y for x,y in zip(a,b)]
    def scale(s,a):return[s*x for x in a]
    def dot(a,b):return sum((x*y for x,y in zip(a,b)),C(0))
    factor=C(float(1/np.sqrt(2))) # literal scalar action's frozen coefficient
    def comm(a,b):return[factor*(a[1]*b[2]-a[2]*b[1]),factor*(a[2]*b[0]-a[0]*b[2]),factor*(a[0]*b[1]-a[1]*b[0]),C(0)]
    def groups(a,r,k):return[[a[r,20*k+4*f+c]for c in range(4)]for f in range(5)]
    cm,pm=read(cdir/'result.json'),read(pdir/'result.json');D=int(cm['degree'])
    if D not in(4,6)or pm['degree']!=D:raise ValueError('Same corrected D4/D6 classical application required')
    for folder,meta,h in((cdir,cm,'56c5dc1d082e01e2903d544f327ebf16e64155125e01af0601c2c7038c55aa47'),
                          (pdir,pm,'d6b0dbb2e34185011f243f7f571da2f536ebc58c6138fab380f856a2f5db96b9')):
        if meta['source_sha256']!=h or sha256(pin(folder/'executed_producer.py').read_bytes()).hexdigest()!=h:raise ValueError('Frozen reviewed source required')
        if sha256(pin(folder/meta['archive']['name']).read_bytes()).hexdigest()!=meta['archive']['sha256']:raise ValueError('Frozen archive bytes changed')
    central,p=read(cdir/cm['archive']['name']),read(pdir/pm['archive']['name']);target,clock=read(TARGET),read(CLOCK)
    if pins[TARGET]!='ea02ed6aee45310c5651fef5c8f103e868007d4f125582ab2b64ff7651f76b2b'or pins[CLOCK]!='18fcc0d4fa588c4fcd7aaa8822be76c132b660e0a2f223f7be55fcb9d8d41290':raise ValueError('Original ea02 and native cut clock required')
    for z in(central,p,clock):
        if not np.array_equal(z['master368'],target['master368'])or z['coordinate_time'].item()!=target['coordinate_time'].item():raise ValueError('No source/field/clock epoch splice')
    if not pm['epoch_basis_value_and_clock_reconstructed_from_native_point_germs']:raise ValueError('Native product basis and clock required')
    native=read(pdir/pm['native_epoch_map_archive']['name'])
    if sha256((pdir/pm['native_epoch_map_archive']['name']).read_bytes()).hexdigest()!=pm['native_epoch_map_archive']['sha256']:raise ValueError('Native product map bytes changed')
    z=read(f'{RADIAL}/actual_common_cut_degree{D}_complete_phase_blocks_run_1/actual_same_current_complete_phase_and_literal_temporal_generator_operands.npz')
    prof=read(f'{RADIAL}/literal_MP_radial_complex192_run_2/degree_{D:02d}_literal_MP_radial_profiles_and_derivative_complex.npz')
    mapdata=read(f'{RADIAL}/actual_linear_cut_degree{D}_complete_clock_epoch_maps_run_1/actual_degree_{D:02d}_complete_clock_covariant_product_epoch_maps.npz')
    generator_source=f'{RADIAL}/actual_common_cut_degree{D}_complete_phase_blocks_run_1/executed_bhsm_baton_zoo_current_covariant_phase_blocks.py';pin(generator_source)
    product_source=f'{RADIAL}/actual_linear_cut_degree4_complete_clock_epoch_maps_run_1/executed_bhsm_baton_zoo_complete_covariant_epoch_maps.py';pin(product_source)
    n=len(central['all_original_and_new_position_indices']);count=D+5
    Pi,Pidot,Gq,E,rG,rGdot=[exact(central,k)for k in('full_canonical_momentum','full_canonical_momentum_total_clock','full_position_gradient','full_position_Euler','full_primal_Gauss_r','full_primal_Gauss_total_clock')]
    Z=hi(z,'actual_literal_temporal_generators');ids=np.asarray([4*j+a for j in range(count)for a in range(3)],int)
    allmap=rows(Z.transpose(),ids).transpose();V=rows(allmap,np.arange(n));Cg=rows(allmap,np.arange(n,allmap.nrows()))
    if V.ncols()!=3*count or Cg.nrows()!=rG.nrows():raise ValueError('All3 SU2 channels and Gauss rows required')
    phase=load_profile_preserving_phase('artifacts/muon_inherited_finite_normal_phase_20261011/run_1',repository=root);pins.update(phase['input_hashes']);rep=phase['representation']
    H=[C(v)for v in target['raw_pair'][1,260:264]]
    rawclock=_matrix(phase['coordinates']['lift'])*rows(exact(clock,'actual_child_master_rate'),target['original252_to_augmented368'])
    Ht=[rawclock[260+i,0]for i in range(4)];Htt=[rawclock[264+i,0]for i in range(4)]
    gens=[_matrix(g)for g in higgs_u2_real_representation()['real_generators']]
    ph,phr,wallphi=hi(prof,'values'),hi(prof,'first'),hi(prof,'wall_values')
    original=np.asarray(mapdata['child_original252_to_augmented'],int);Vdot=acb_mat(n,3*count)
    for j,(q,a)in enumerate((q,a)for q in range(count)for a in range(3)):
        d=-gens[a]*acb_mat([[x]for x in Ht])*wallphi[0,q]
        for i in range(4):Vdot[int(original[102+i]),j]=d[i,0]
    charge=V.transpose()*Pi;gauss=Cg.transpose()*rG
    charge_t=V.transpose()*Pidot+Vdot.transpose()*Pi;gauss_t=Cg.transpose()*rGdot
    primary=charge+gauss;dprimary=charge_t+gauss_t
    static_without_W=V.transpose()*Gq+Vdot.transpose()*Pi
    divergence_without_W=V.transpose()*E-gauss_t
    point,pt=exact(p,'child_point_coefficients'),exact(p,'child_point_coefficients_directional_first')
    density,dt=exact(p,'child_metric_density'),exact(p,'child_metric_density_directional_first')
    wall,wallt=exact(p,'child_wall_connection'),exact(p,'child_wall_connection_directional_first')
    if point.nrows()!=ph.nrows()or point.nrows()!=len(rep['radial_quadrature']):raise ValueError('Original literal point grid required')
    def O(a,h):
        return[sum((a[k]*sum((gens[k][i,j]*h[j]for j in range(4)),C(0))for k in range(4)),C(0))for i in range(4)]
    # The only new geometry evaluation is the original cap weight and its
    # supplied total-clock contact, with no action/gradient/test/right seed.
    packed.PhaseJet.nj=0;packed.PhaseJet.nr=0;packed.PhaseJet.include_first=True
    q=[packed.PhaseJet(C(v),h=rawclock[i,0])for i,v in enumerate(target['raw_pair'][1,:100])]
    with packed.OriginalGeometryPatch('independent_mp_same_material_equations',3,chart.anchored_material_chart4)as G:
        cap=G.holomorphic_cap_and_weights(q,points=rep['cap_points']);wT,wTt=cap['wT'].value,cap['wT'].h
    functional,functional_t=acb_mat(3*count,1),acb_mat(3*count,1)
    Wvalue,Wrvalue,Wtime,Wrtime=[acb_mat(4*point.nrows(),3*count)for _ in range(4)]
    Wwall,Wwallt=acb_mat(4,3*count),acb_mat(4,3*count)
    for ir in range(point.nrows()):
        A,At,Ar=(groups(point,ir,k)for k in range(3));Ad,Atd,Ard=(groups(pt,ir,k)for k in range(3))
        e,_,_,k,beta=[density[ir,j]for j in range(5)];ed,_,_,kd,betad=[dt[ir,j]for j in range(5)]
        X=add(sub(At[1],Ar[0]),comm(A[0],A[1]));Xt=add(sub(Atd[1],Ard[0]),add(comm(Ad[0],A[1]),comm(A[0],Ad[1])))
        Rs=[add(Ar[f],comm(A[1],A[f]))for f in range(2,5)]
        Rt=[add(Ard[f],add(comm(Ad[1],A[f]),comm(A[1],Ad[f])))for f in range(2,5)]
        Ts=[add(At[f],comm(A[0],A[f]))for f in range(2,5)]
        Tt=[add(Atd[f],add(comm(Ad[0],A[f]),comm(A[0],Ad[f])))for f in range(2,5)]
        Y=[sub(a,scale(beta,b))for a,b in zip(Ts,Rs)]
        Yt=[sub(a,add(scale(betad,b),scale(beta,c)))for a,b,c in zip(Tt,Rs,Rt)]
        weight=C(float(MAXWELL_TO_CAP)*float(rep['radial_quadrature'][ir]))
        for j,(pp,a)in enumerate((pp,a)for pp in range(count)for a in range(3)):
            basis=[C(int(c==a))*ph[ir,pp]for c in range(4)];basisr=[C(int(c==a))*phr[ir,pp]for c in range(4)]
            W=comm(A[0],basis);Wr=add(comm(Ar[0],basis),comm(A[0],basisr))
            Wt=comm(Ad[0],basis);Wrt=add(comm(Ard[0],basis),comm(Ad[0],basisr))
            for c in range(4):Wvalue[4*ir+c,j],Wrvalue[4*ir+c,j],Wtime[4*ir+c,j],Wrtime[4*ir+c,j]=W[c],Wr[c],Wt[c],Wrt[c]
            dx=add(scale(C(-1),Wr),comm(W,A[1]));dxt=add(scale(C(-1),Wrt),add(comm(Wt,A[1]),comm(W,Ad[1])))
            dy=[comm(W,A[f])for f in range(2,5)];dyt=[add(comm(Wt,A[f]),comm(W,Ad[f]))for f in range(2,5)]
            functional[j,0]+=weight*(k*dot(X,dx)+e*sum((dot(u,v)for u,v in zip(Y,dy)),C(0)))
            functional_t[j,0]+=weight*(kd*dot(X,dx)+k*dot(Xt,dx)+k*dot(X,dxt)+
                ed*sum((dot(u,v)for u,v in zip(Y,dy)),C(0))+e*sum((dot(u,v)+dot(w,z)for u,v,w,z in zip(Yt,dy,Y,dyt)),C(0)))
    wa=[wall[0,c]for c in range(4)];wat=[wallt[0,c]for c in range(4)]
    DtH=add(Ht,O(wa,H));DtHt=add(Htt,add(O(wat,H),O(wa,Ht)))
    for j,(pp,a)in enumerate((pp,a)for pp in range(count)for a in range(3)):
        basis=[C(int(c==a))*wallphi[0,pp]for c in range(4)]
        W,Wt=comm(wa,basis),comm(wat,basis)
        for c in range(4):Wwall[c,j],Wwallt[c,j]=W[c],Wt[c]
        ZH=O(W,H);ZHt=add(O(Wt,H),O(W,Ht))
        functional[j,0]+=C(2)*wT*dot(DtH,ZH)/C(VOLUME)
        functional_t[j,0]+=C(2)*(wTt*dot(DtH,ZH)+wT*dot(DtHt,ZH)+wT*dot(DtH,ZHt))/C(VOLUME)
    static=static_without_W+functional;divergence=divergence_without_W+functional
    # Independent value-only fourth-order differences of this actual weak
    # functional on the explicitly supplied affine point/wall/density germ.
    # No clock formula above is called by this path and no new history is
    # inferred from this finite diagnostic displacement.
    def literal_functional_at(x):
        result=acb_mat(3*count,1);pc=point+pt*x;gc=density+dt*x;ww=wall+wallt*x
        hc=add(H,scale(x,Ht));htc=add(Ht,scale(x,Htt));wc=wT+x*wTt
        for ir in range(pc.nrows()):
            A,At,Ar=(groups(pc,ir,k)for k in range(3))
            e,_,_,k,beta=[gc[ir,j]for j in range(5)]
            X=add(sub(At[1],Ar[0]),comm(A[0],A[1]))
            Y=[sub(add(At[f],comm(A[0],A[f])),scale(beta,add(Ar[f],comm(A[1],A[f]))))for f in range(2,5)]
            weight=C(float(MAXWELL_TO_CAP)*float(rep['radial_quadrature'][ir]))
            for j,(pp,a)in enumerate((pp,a)for pp in range(count)for a in range(3)):
                b=[C(int(c==a))*ph[ir,pp]for c in range(4)];br=[C(int(c==a))*phr[ir,pp]for c in range(4)]
                W=comm(A[0],b);Wr=add(comm(Ar[0],b),comm(A[0],br))
                dx=add(scale(C(-1),Wr),comm(W,A[1]));dy=[comm(W,A[f])for f in range(2,5)]
                result[j,0]+=weight*(k*dot(X,dx)+e*sum((dot(u,v)for u,v in zip(Y,dy)),C(0)))
        wa=[ww[0,c]for c in range(4)];D=add(htc,O(wa,hc))
        for j,(pp,a)in enumerate((pp,a)for pp in range(count)for a in range(3)):
            W=comm(wa,[C(int(c==a))*wallphi[0,pp]for c in range(4)])
            result[j,0]+=C(2)*wc*dot(D,O(W,hc))/C(VOLUME)
        return result
    clock_controls=[];literal_zero=literal_functional_at(C(0));clock_differences=[]
    for bits in(12,18,24):
        step=acb(2)**(-bits)
        diff=(-literal_functional_at(2*step)+8*literal_functional_at(step)-8*literal_functional_at(-step)+literal_functional_at(-2*step))/(12*step)
        clock_differences.append(diff)
        clock_controls.append(dict(step_power_of_two=-bits,absolute_defect_upper=_upper(diff-functional_t),
            relative_defect_upper=_upper(diff-functional_t)/max(_upper(functional_t),1e-300)))
    # Exact finite-span witness: all ordinary retained At profiles have
    # fractional part x^alpha times a polynomial of degree<=2. The fixed
    # affine-reference lambda differences and phi P_l are analytic at x0.
    # Multiplication by phi=16x^2(1-x)^2 generates nonzero higher fractional
    # powers whenever the corresponding actual At component is nonzero.
    dc=hi(prof,'derivative_coefficients');alpha=C(float(ALPHA));t=5+2*alpha;s=8+2*alpha;c0=dc[D+5,0];c1=-dc[D+5,1]/t
    p0,p1=map(C,rep['affine_interior_projection']);wc,fn=C(rep['affine_wall_coefficient']),C(rep['affine_complement_norm'])
    coef=acb_mat(4,4)
    for j,label in enumerate(rep['gauge_labels']):
        if label['field']=='A_tau':coef[int(label['radial']),int(label['internal'])]=C(target['raw_pair'][1,100+j])
    frac=acb_mat(3,4)
    for c in range(4):
        b0=coef[0,c]-coef[2,c]*p0/fn;b1=coef[1,c]-coef[2,c]*p1/fn;br=coef[3,c]-coef[2,c]*wc/fn
        frac[0,c]=c0*b0-c1*t*b1+br;frac[1,c]=-c0*b0+c1*(t+s)*b1;frac[2,c]=-c1*s*b1
    productfrac=acb_mat(7,12)
    for a in range(3):
        unit=[C(int(c==a))for c in range(4)]
        for d in range(3):
            vector=comm([frac[d,c]for c in range(4)],unit)
            for shift,mul in((2,16),(3,-32),(4,16)):
                for c in range(4):productfrac[d+shift,4*a+c]+=C(mul)*vector[c]
    outside_by_channel=[max(float(abs(productfrac[d,4*a+c]).upper())for d in range(3,7)for c in range(4))for a in range(3)]
    outside_lower=[max(float(abs(productfrac[d,4*a+c]).lower())for d in range(3,7)for c in range(4))for a in range(3)]
    if not all(v>0 for v in outside_lower):raise ValueError('Actual finite-span witness must exclude zero, never assume it')
    values=dict(SU2_gauge_position_map=V,SU2_gauge_position_map_total_clock=Vdot,SU2_Gauss_map=Cg,
        actual_full_primal_Gauss_r=rG,actual_full_primal_Gauss_total_clock=rGdot,
        actual_SU2_initial_corner_charge=charge,actual_SU2_Gauss_charge_projection=gauss,
        actual_SU2_future_arm_initial_outward_corner_flux=-charge,actual_SU2_initial_corner_charge_total_clock=charge_t,
        required_affine_defect_SU2_initial_corner_charge=gauss,
        required_affine_defect_SU2_future_arm_initial_outward_corner_flux=-gauss,
        actual_SU2_Gauss_projection_total_clock=gauss_t,SU2_primary_Noether_rows=primary,SU2_differentiated_primary_Noether_rows=dprimary,
        static_without_temporal_commutator_test=static_without_W,divergence_without_temporal_commutator_test=divergence_without_W,
        actual_unprojected_temporal_commutator_test=Wvalue,actual_unprojected_temporal_commutator_radial_first=Wrvalue,
        actual_unprojected_temporal_commutator_test_total_clock=Wtime,actual_unprojected_temporal_commutator_radial_clock=Wrtime,
        actual_unprojected_temporal_commutator_wall_test=Wwall,actual_unprojected_temporal_commutator_wall_clock=Wwallt,
        actual_augmented_temporal_Gauss_functional=functional,actual_augmented_temporal_Gauss_functional_total_clock=functional_t,
        independent_literal_temporal_Gauss_value=literal_zero,
        actual_full_SU2_static_gauge_variation=static,actual_full_SU2_covariant_source_conservation=divergence,
        At_fractional_polynomial_coefficients=frac,At_commutator_phi0_fractional_polynomial_coefficients=productfrac,
        original_scalar_wall_weight_and_total_clock=acb_mat([[wT,wTt]]))
    for bits,a in zip((12,18,24),clock_differences):values[f'independent_literal_temporal_Gauss_clock_FD4_step_2m{bits}']=a
    arrays=dict(coordinate_time=target['coordinate_time'],master368=target['master368'],profile_internal_labels=np.asarray([(p,a)for p in range(count)for a in range(3)]),
        radial_quadrature=np.asarray(rep['radial_quadrature']),fractional_exponent=np.asarray(float(ALPHA)))
    for key,a in values.items():arrays[key+'_high'],arrays[key+'_low']=_split(a);arrays.update(ex.export_acb_exact_dyadic(a,key+'_exact'))
    path=out/'actual_SU2_source_corner_and_unprojected_temporal_Gauss_functionals.npz';_compressed_npz(path,arrays)
    for name,m in list(sys.modules.items()):
        f=getattr(m,'__file__',None)
        if f and(name=='bhsm'or name.startswith('bhsm.'))and Path(f).resolve().is_relative_to(root):pin(Path(f).resolve())
    pin(Path(__file__))
    report=dict(classification='ACTUAL_ORIGINAL_EA02_SU2_PRIMARY_CORNER_AND_UNPROJECTED_TEMPORAL_GAUSS_FUNCTIONAL',degree=D,
        source_sha256=sha256(producer).hexdigest(),input_and_source_hashes=dict(sorted(pins.items())),archive=dict(name=path.name,sha256=sha256(path.read_bytes()).hexdigest(),bytes=path.stat().st_size),
        arithmetic_precision_bits=256,SU2_parameters=3*count,primary_Noether_upper=_upper(primary),differentiated_primary_Noether_upper=_upper(dprimary),
        full_static_gauge_variation_upper=_upper(static),full_covariant_source_conservation_upper=_upper(divergence),
        conservation_minus_static_plus_differentiated_primary_upper=_upper(divergence-static+dprimary),
        actual_SU2_corner_charge_upper=_upper(charge),actual_SU2_Gauss_projection_clock_upper=_upper(gauss_t),
        actual_full_primal_Gauss_upper=_upper(rG),actual_full_primal_Gauss_constraints_satisfied=bool(_upper(rG)<=2e-10),
        actual_augmented_temporal_Gauss_functional_upper=_upper(functional),actual_augmented_temporal_Gauss_functional_clock_upper=_upper(functional_t),
        independent_value_only_temporal_Gauss_value_defect_upper=_upper(literal_zero-functional),
        independent_value_only_temporal_Gauss_clock_FD4_controls=clock_controls,
        temporal_commutator_fractional_coefficients_outside_existing_At_span_upper_by_channel=outside_by_channel,
        temporal_commutator_fractional_coefficient_nonzero_lower_witness_by_channel=outside_lower,
        temporal_weak_tests_are_unprojected_augmented_functional_tests_not_state_coordinates=True,
        exact_owned_spatial_Dphi_products_are_represented=True,product_basis_total_clock_contacts_retained_once=True,
        fixed_chart_coordinate_Vdot_contains_Hdot_not_duplicate_physical_Kdot=True,
        Gauss_covector_includes_scalar_wall_temporal_Higgs_contact_once=True,
        full_clock_of_static_conservation_not_claimed=True,explicit_temporal_Gauss_functional_clock_evaluated=True,
        clock_control_is_supplied_affine_point_wall_density_germ_not_new_mean_history=True,
        literal_action_binary64_commutator_coefficient_retained=True,canonical_charge_is_not_physical_unit_charge=True,
        future_arm_initial_outward_conormal_sign=-1,
        no_action_gradient_or_source_history_or_field_solve_replayed=True,new_geometry_evaluation_only_original_wT_and_supplied_clock=True,
        primal_rG_and_required_affine_corner_not_retracted=True,full_retarded_reset_domain_or_microscopic_induced_current_evaluated=False,
        original_prefix_cell7_complete_density_time_derivative_admitted=False,physical_outgoing_Y_R=None,physical_affine_s_R=None,physical_C0_Cj=None,
        physical_full_derivative_pass=False,physical_radial_convergence=False,physical_Maxwell226_after_pass=False,
        normalized_two_spin_state=False,physical_muon_magnetic_moment=None,original_coupled_corrections=0)
    (out/'result.json').write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps({k:report[k]for k in('degree','primary_Noether_upper','differentiated_primary_Noether_upper','full_static_gauge_variation_upper','full_covariant_source_conservation_upper','actual_augmented_temporal_Gauss_functional_clock_upper')}),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repository',type=Path,default=ROOT)
    for key in('central-folder','position-folder','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();run(a.repository,a.central_folder,a.position_folder,a.output)
