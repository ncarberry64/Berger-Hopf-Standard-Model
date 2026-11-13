"""Independent explicit temporal Gauss mixed-clock polynomial, all36x7.

No charge/Noether identity is used to construct a Gauss derivative. Exact
FD4 polynomial extraction differentiates the literal covector on supplied
bilinear h/R/hR and affine Rdot germs. Other24 rows are mechanical, not
the temporal Gauss polynomial evaluated by this audit.
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
FAMILY='artifacts/muon_baton_zoo_maximal_current_realization_20261013'
RUNTIME=FAMILY+'/actual_new620_fresh_native_MP_new_exact_R7_clock_control_run_1'
RADIAL='artifacts/muon_baton_zoo_radial_convergence_20261014'


def run(repository,coefficient_folder,SU2_corner_folder,gauss_folder,output):
    root,cdir,sdir,gdir,out=map(lambda p:Path(p).resolve(),(repository,coefficient_folder,SU2_corner_folder,gauss_folder,output))
    out.mkdir(parents=True,exist_ok=False);producer=Path(__file__).read_bytes();(out/'executed_producer.py').write_bytes(producer);pins={}
    def pin(path):
        p=Path(path);p=p if p.is_absolute()else root/p
        key=p.relative_to(root).as_posix()if p.is_relative_to(root)else str(p);pins[key]=sha256(p.read_bytes()).hexdigest();return p
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
    from bhsm.interface.muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation
    from bhsm.interface.muon_parent_mean_causal_action import MAXWELL_TO_CAP
    from bhsm.interface.muon_literal_euclidean_wall_action import VOLUME
    ctx.prec=256
    module('bhsm_baton_zoo_exact_acb_packets',RUNTIME+'/bhsm_baton_zoo_exact_acb_packets_imported_runtime.py')
    ex=module('bhsm_exact_action_balls',RUNTIME+'/bhsm_exact_action_balls_imported_runtime.py')
    def exact(z,k):return ex.parse_acb_exact_dyadic(z,k+'_exact')
    def C(v):return v if isinstance(v,acb)else acb(complex(v))
    def rows(m,indices):return acb_mat([[m[int(i),j]for j in range(m.ncols())]for i in indices])
    def metadata(folder,expected):
        m=read(folder/'result.json')
        if m['source_sha256']!=expected or sha256(pin(folder/'executed_producer.py').read_bytes()).hexdigest()!=expected:raise ValueError('Exact reviewed input source required')
        return m
    def archive(folder,meta,name=None):
        name=meta['archive']['name']if name is None else name;p=folder/name;receipt=meta['archives'][name]if 'archives'in meta else meta['archive']
        if sha256(pin(p).read_bytes()).hexdigest()!=receipt['sha256']:raise ValueError('Exact same-source archive bytes required')
        return read(p)
    cm=metadata(cdir,'c744590f986e47c946f128641b071808f527d230ba60fc2fa70adf87d351c851')
    sm=metadata(sdir,'3504d6dd8fefffa7704d00321ef3e404c59313ac9b913e8256f7844dcfcfaeb2')
    gm=metadata(gdir,'519371278ad0884047147d7b97364d2af7f5f7ae145d15cda1549b56cce35902')
    a=archive(cdir,cm,'actual_same_ea02_D4_seven_point_density_R_hR.npz');ad=archive(cdir,cm,'actual_same_ea02_D4_seven_point_density_Rdot.npz')
    s,g=archive(sdir,sm),archive(gdir,gm)
    for z in(ad,s,g):
        if not np.array_equal(z['master368'],a['master368'])or z['coordinate_time'].item()!=a['coordinate_time'].item():raise ValueError('No field/source/clock epoch splice')
    if _upper(exact(a,'actual_complete_right')-exact(g,'actual_same_seven_field'))>1e-30 or _upper(exact(a,'actual_complete_right')-exact(s,'actual_full_seven_fields'))>1e-30:raise ValueError('Complete identical retained seven fields required')
    prof=read(RADIAL+'/literal_MP_radial_complex192_run_2/degree_04_literal_MP_radial_profiles_and_derivative_complex.npz')
    ph,phr,wp=[_matrix(prof[k+'_high'])+_matrix(prof[k+'_low'])for k in('values','first','wall_values')]
    phase=read(RADIAL+'/actual_common_cut_degree4_complete_phase_blocks_run_1/actual_same_current_complete_phase_and_literal_temporal_generator_operands.npz')
    Z=_matrix(phase['actual_literal_temporal_generators_high'])+_matrix(phase['actual_literal_temporal_generators_low']);Cg=rows(Z,np.arange(217,Z.nrows()))
    if Cg.nrows()!=60 or Cg.ncols()!=36:raise ValueError('Complete ordinary temporal U2 incidence required')
    factor=C(float(1/np.sqrt(2)))
    def add(x,y):return[a+b for a,b in zip(x,y)]
    def sub(x,y):return[a-b for a,b in zip(x,y)]
    def scale(c,x):return[c*v for v in x]
    def dot(x,y):return sum((u*v for u,v in zip(x,y)),C(0))
    def comm(x,y):return[factor*(x[1]*y[2]-x[2]*y[1]),factor*(x[2]*y[0]-x[0]*y[2]),factor*(x[0]*y[1]-x[1]*y[0]),C(0)]
    generators=higgs_u2_real_representation()['real_generators']
    def O(conn,h):return[sum((conn[k]*sum((C(generators[k][i,j])*h[j]for j in range(4)),C(0))for k in range(4)),C(0))for i in range(4)]
    keys=('point','density','wall','raw_child','boundary_weights');base={k:exact(a,k)for k in keys};hs={k:exact(a,k+'_h')for k in keys}
    right={k:exact(a,k+'_R')for k in keys};mixed={k:exact(a,k+'_hR')for k in keys};rd={k:exact(ad,k+'_R')for k in keys}
    def column_shape(flat,j,shape):return acb_mat([[flat[i*shape[1]+k,j]for k in range(shape[1])]for i in range(shape[0])])
    R=[{k:column_shape(right[k],j,(base[k].nrows(),base[k].ncols()))for k in keys}for j in range(7)]
    HR=[{k:column_shape(mixed[k],j,(base[k].nrows(),base[k].ncols()))for k in keys}for j in range(7)]
    RD=[{k:column_shape(rd[k],j,(base[k].nrows(),base[k].ncols()))for k in keys}for j in range(7)]
    def literal_Gauss(j,x,y,kind):
        # This is the only evaluator: values of the explicit Gauss covector.
        # It neither calls the charge function nor any AD/product-rule class.
        if kind=='bilinear':q={k:base[k]+hs[k]*x+R[j][k]*y+HR[j][k]*(x*y)for k in keys}
        elif kind=='Rdot':q={k:base[k]+RD[j][k]*y for k in keys}
        else:raise ValueError('Explicit supplied coefficient germ required')
        point,density=q['point'],q['density'];g0,gr=acb_mat(point.nrows(),4),acb_mat(point.nrows(),4)
        for ir in range(point.nrows()):
            A=[[point[ir,4*f+c]for c in range(4)]for f in range(5)]
            At=[[point[ir,20+4*f+c]for c in range(4)]for f in range(5)]
            Ar=[[point[ir,40+4*f+c]for c in range(4)]for f in range(5)]
            e,k,beta=density[ir,0],density[ir,3],density[ir,4]
            X=add(sub(At[1],Ar[0]),comm(A[0],A[1]))
            Y=[sub(add(At[f],comm(A[0],A[f])),scale(beta,add(Ar[f],comm(A[1],A[f]))))for f in range(2,5)]
            covector=scale(k,comm(A[1],X))
            for f,v in zip(range(2,5),Y):covector=add(covector,scale(e,comm(A[f],v)))
            weight=C(float(MAXWELL_TO_CAP)*float(a['radial_quadrature'][ir]))
            for c in range(4):g0[ir,c]=weight*covector[c];gr[ir,c]=-weight*k*X[c]
        result=ph.transpose()*g0+phr.transpose()*gr
        raw,wall=q['raw_child'],q['wall'];H=[raw[0,260+i]for i in range(4)];Ht=[raw[0,264+i]for i in range(4)]
        PiH=scale(C(2)*q['boundary_weights'][0,0]/C(VOLUME),add(Ht,O([wall[0,c]for c in range(4)],H)))
        for c in range(4):
            unit=[C(int(k==c))for k in range(4)];current=dot(PiH,O(unit,H))
            for p in range(9):result[p,c]+=wp[0,p]*current
        return acb_mat([[result[p,c]]for p in range(9)for c in range(4)])
    stencil=((-2,1),(-1,-8),(1,8),(2,-1));powers=(12,18,24)
    firsts=[];mixes=[];rates=[]
    for power in powers:
        step=acb(2)**(-power);F,M,D=[acb_mat(36,7)for _ in range(3)]
        print(json.dumps(dict(stage='independent_value_only_Gauss_polynomial',step_power=-power,temporal_rows=36,rights=7)),flush=True)
        for j in range(7):
            f,m,d=acb_mat(36,1),acb_mat(36,1),acb_mat(36,1)
            for iy,wy in stencil:
                f+=literal_Gauss(j,C(0),iy*step,'bilinear')*wy
                d+=literal_Gauss(j,C(0),iy*step,'Rdot')*wy
                for ix,wx in stencil:m+=literal_Gauss(j,ix*step,iy*step,'bilinear')*(wx*wy)
            f/=12*step;d/=12*step;m/=144*step*step
            for i in range(36):F[i,j],M[i,j],D[i,j]=f[i,0],m[i,0],d[i,0]
        firsts.append(F);mixes.append(M);rates.append(D)
    # Every term of the explicit temporal Gauss functional has coefficient
    # degree<=5 (including e*beta*Ar*Ai*Ai). A bilinear coefficient germ
    # has bidegree<=5. FD4 selects powers1 and5 on each axis, so its mixed
    # output is EXACTLY a polynomial a+b*s^4+c*s^8. Interpolation at0 from
    # the three fixed dyadic scales extracts the actual derivative, with
    # acb error propagation. This is a polynomial identity, not a fitted
    # physical extrapolation or selection of a favorable finite step.
    ts=[(acb(2)**(-p))**4 for p in powers]
    coeff=[]
    for i in range(3):
        w=acb(1)
        for k in range(3):
            if i!=k:w*=(-ts[k])/(ts[i]-ts[k])
        coeff.append(w)
    combine=lambda matrices:sum((a*c for a,c in zip(matrices,coeff)),acb_mat(36,7))
    F,M,D=combine(firsts),combine(mixes),combine(rates);total=M+D
    independent_Gauss=Cg.transpose()*exact(g,'actual_native_Gauss_Kz_trial')
    su2=np.asarray([4*p+c for p in range(9)for c in range(3)],int)
    chargeclock=exact(s,'actual_SU2_initial_charge_variation_total_clock')
    controls=[]
    for power,f,m,d in zip(powers,firsts,mixes,rates):
        controls.append(dict(step_power=-power,first_error_upper=_upper(f-F),mixed_error_upper=_upper(m-M),Rdot_error_upper=_upper(d-D),
            total_clock_error_upper=_upper(m+d-total)))
    values=dict(independent_literal_temporal_Gauss_H_R=F,independent_literal_temporal_Gauss_h_H_R=M,
        independent_literal_temporal_Gauss_H_Rdot=D,independent_literal_temporal_Gauss_variation_total_clock=total,
        first_variation_minus_independent_native_Gauss_projection=F-independent_Gauss,
        independent_SU2_Gauss_variation_total_clock=rows(total,su2),
        independently_differentiated_SU2_Gauss_clock_plus_charge_clock=rows(total,su2)+chargeclock,
        old_literal_product_rule_Gauss_clock_minus_new_independent_clock=exact(s,'literal_temporal_Gauss_parameter_variation_total_clock')-rows(total,su2))
    for power,f,m,d in zip(powers,firsts,mixes,rates):values[f'value_only_FD4_first_step2m{power}']=f;values[f'value_only_FD4_mixed_step2m{power}']=m;values[f'value_only_FD4_Rdot_step2m{power}']=d
    arrays=dict(master368=a['master368'],coordinate_time=a['coordinate_time'],temporal_profile_internal_labels=np.asarray([(p,c)for p in range(9)for c in range(4)]),SU2_rows_in_temporal36=su2)
    for key,m in values.items():arrays[key+'_high'],arrays[key+'_low']=_split(m);arrays.update(ex.export_acb_exact_dyadic(m,key+'_exact'))
    path=out/'independent_literal_temporal36x7_Gauss_mixed_clock.npz';_compressed_npz(path,arrays);pin(Path(__file__))
    result=dict(classification='INDEPENDENT_EXPLICIT_TEMPORAL_GAUSS_POLYNOMIAL_MIXED_CLOCK_ALL36_BY7',source_sha256=sha256(producer).hexdigest(),input_and_source_hashes=dict(sorted(pins.items())),
        archive=dict(name=path.name,sha256=sha256(path.read_bytes()).hexdigest(),bytes=path.stat().st_size),arithmetic_precision_bits=256,
        temporal_Gauss_rows=36,SU2_rows=27,rights=7,other24_mechanical_constraints_evaluated=False,
        independent_H_R_vs_native_all60_projection_upper=_upper(F-independent_Gauss),
        independent_SU2_Gauss_clock_plus_direct_charge_clock_upper=_upper(rows(total,su2)+chargeclock),
        independent_Gauss_clock_vs_previous_product_rule_upper=_upper(exact(s,'literal_temporal_Gauss_parameter_variation_total_clock')-rows(total,su2)),
        actual_temporal_Gauss_variation_total_clock_upper=_upper(total),fixed_FD4_polynomial_controls=controls,
        exact_coefficient_degree_bound=5,bilinear_germ_bidegree_bound=[5,5],mixed_FD4_is_polynomial_in_step_fourth_power_degree2=True,
        all_fixed_scales_retained=True,no_Noether_identity_or_charge_used_to_construct_derivative=True,no_packed_action_or_derivative_AD_called=True,
        sourceDot_and_Rdot_and_native_Th_Wh_in_right_coefficient_jets_once=True,
        ordinary_temporal_left_phi_tests_fixed_by_retained_parameter_chart=True,
        no_new_state_or_history_or_coupled_correction=True,full_physical_outgoing_derivative_pass=False,
        physical_radial_solution_convergence=False,physical_Maxwell226_after_pass=False,
        physical_normalized_two_spin_state=False,physical_muon_magnetic_moment=None,original_coupled_corrections=0)
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps({k:result[k]for k in('independent_H_R_vs_native_all60_projection_upper','independent_SU2_Gauss_clock_plus_direct_charge_clock_upper','independent_Gauss_clock_vs_previous_product_rule_upper','actual_temporal_Gauss_variation_total_clock_upper')}),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repository',type=Path,default=ROOT)
    for key in('coefficient-folder','SU2-corner-folder','gauss-folder','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();run(a.repository,a.coefficient_folder,a.SU2_corner_folder,a.gauss_folder,a.output)
