"""Actual unprojected physical deltaV(A,H) paired with bare Euler.

Uses retained exact coefficient/source germs only. No new action, field,
coefficient sampling, projection, clock solve or outer correction occurs.
The clock RHS compression remains an operator projection, not a proven
left-null obstruction.
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
POSITION='audits/bhsm_original_ea02_d4_position_operator_20261016.py'
POSITION_SHA='70670f411a2a11d301677359500be28fb9769f1557000b3262eb5939816ae389'
CLOCK_SHA='8d4a7fe4fe24501c6d2e00681ed9ca4f1e2b5eb9d0793b3e775bab4c92b58574'
CLOCK_ARCHIVE_SHA='2e0b2140004e37699f80ed25d14c8d988f657598f6b7d4b1269bce292cf7039d'
COEFF_SHA='c744590f986e47c946f128641b071808f527d230ba60fc2fa70adf87d351c851'
COEFF_ARCHIVE_SHA='6cf8979c6d81fb427a23a93848f13a87400a615daae0e1496698d042f85755a2'
RADIAL='artifacts/muon_baton_zoo_radial_convergence_20261014'


def run(clock_folder,coefficient_folder,output):
    out=Path(output).resolve();out.mkdir(parents=True,exist_ok=False)
    source=Path(__file__).read_bytes();(out/'executed_producer.py').write_bytes(source)
    p=ROOT/POSITION
    if sha256(p.read_bytes()).hexdigest()!=POSITION_SHA:raise ValueError('Reviewed same-cut position backend changed')
    spec=importlib.util.spec_from_file_location('position_metadata_for_physical_Euler',p)
    m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
    position=m.ActualEa02D4PositionOperator();op=position.phase;op.pin(p,POSITION_SHA)
    from flint import acb,acb_mat
    from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
    from bhsm.interface.muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation
    from bhsm.interface.muon_parent_mean_causal_action import MAXWELL_TO_CAP
    from bhsm.interface.muon_literal_euclidean_wall_action import VOLUME
    def packet(folder,expected_source,expected_archive,name=None):
        folder=Path(folder).resolve();meta=op.read(folder/'result.json')
        if meta['source_sha256']!=expected_source:raise ValueError('Reviewed source bytes required')
        op.pin(folder/'executed_producer.py',expected_source)
        name=meta['archive']['name']if name is None else name
        return op.read(folder/name,expected_archive)
    clock=packet(clock_folder,CLOCK_SHA,CLOCK_ARCHIVE_SHA)
    a=packet(coefficient_folder,COEFF_SHA,COEFF_ARCHIVE_SHA,'actual_same_ea02_D4_seven_point_density_R_hR.npz')
    for z in(clock,a):
        if not np.array_equal(z['master368'],op.target['master368'])or z['coordinate_time'].item()!=op.target['coordinate_time'].item():raise ValueError('No source/field/epoch splice')
    value=op.value;rows=op.rows;upper=op.upper
    Rold=value(a,'actual_complete_right');Rnew=value(clock,'actual_open_family_particular_full746_right')
    preserved=rows(Rnew-Rold,np.r_[np.arange(252),252+np.arange(217)])
    if upper(preserved)>1e-30 or any(not preserved[i,j].contains(0)for i in range(preserved.nrows())for j in range(7)):
        raise ValueError('The updated family must preserve original source and spatial/H positions')
    def C(v):return v if isinstance(v,acb)else acb(complex(v))
    def fields(row,k):return[row[20*k+4*f:20*k+4*f+4]for f in range(5)]
    def add(a,b):return[x+y for x,y in zip(a,b)]
    def sub(a,b):return[x-y for x,y in zip(a,b)]
    def scale(t,a):return[t*x for x in a]
    def dot(a,b):return sum((x*y for x,y in zip(a,b)),C(0))
    factor=C(float(1/np.sqrt(2)))
    def comm(a,b):return[factor*(a[1]*b[2]-a[2]*b[1]),factor*(a[2]*b[0]-a[0]*b[2]),factor*(a[0]*b[1]-a[1]*b[0]),C(0)]
    gens=[op.matrix(g)for g in higgs_u2_real_representation()['real_generators']]
    def O(conn,H):return[sum((conn[k]*sum((gens[k][i,j]*H[j]for j in range(4)),C(0))for k in range(4)),C(0))for i in range(4)]
    point,pointh,density,densityh,wall,wallh,raw,rawh,weights,weightsh=[value(a,k)for k in
        ('point','point_h','density','density_h','wall','wall_h','raw_child','raw_child_h','boundary_weights','boundary_weights_h')]
    pointR,wallR,rawR=[value(a,k)for k in('point_R','wall_R','raw_child_R')]
    nr=point.nrows()
    prof=op.read(RADIAL+'/literal_MP_radial_complex192_run_2/degree_04_literal_MP_radial_profiles_and_derivative_complex.npz')
    phi,phir,phiw=[value(prof,k)for k in('values','first','wall_values')]
    if nr!=48 or phi.nrows()!=48 or phi.ncols()!=9:raise ValueError('Original48 radial rule and nine fixed gauge profiles required')
    H=[raw[0,260+i]for i in range(4)];Ht=[raw[0,264+i]for i in range(4)]
    Hh=[rawh[0,260+i]for i in range(4)];Hth=[rawh[0,264+i]for i in range(4)]
    W=[[wall[0,4*f+c]for c in range(4)]for f in range(5)]
    Wh=[[wallh[0,4*f+c]for c in range(4)]for f in range(5)]
    wT,wS,wV=[weights[0,i]for i in range(3)];wTh=weightsh[0,0]
    Dt=add(Ht,O(W[0],H));Dth=add(Hth,add(O(Wh[0],H),O(W[0],Hh)))
    Ds=[O(W[f],H)for f in range(2,5)]
    PiH=scale(C(2)*wT/C(VOLUME),Dt)
    PiHh=scale(C(2)/C(VOLUME),add(scale(wTh,Dt),scale(wT,Dth)))
    lambdaH=C(op.rep['scalar_matching']['lambda_H']);nu=C(op.params['nu_squared_action'])
    nodes=[]
    for ir in range(nr):
        A,At,Ar=(fields([point[ir,j]for j in range(60)],k)for k in range(3))
        Ah,Ath,Arh=(fields([pointh[ir,j]for j in range(60)],k)for k in range(3))
        e,r,d,k,beta=[density[ir,j]for j in range(5)]
        eh,_,_,kh,betah=[densityh[ir,j]for j in range(5)]
        X=add(sub(At[1],Ar[0]),comm(A[0],A[1]))
        Xh=add(sub(Ath[1],Arh[0]),add(comm(Ah[0],A[1]),comm(A[0],Ah[1])))
        Rs=[add(Ar[f],comm(A[1],A[f]))for f in range(2,5)]
        Rsh=[add(Arh[f],add(comm(Ah[1],A[f]),comm(A[1],Ah[f])))for f in range(2,5)]
        Y=[sub(add(At[f],comm(A[0],A[f])),scale(beta,Rs[f-2]))for f in range(2,5)]
        Yh=[sub(add(Ath[f],add(comm(Ah[0],A[f]),comm(A[0],Ah[f]))),
            add(scale(betah,Rs[f-2]),scale(beta,Rsh[f-2])))for f in range(2,5)]
        B=[add(scale(C(2),A[i+2]),comm(A[j+2],A[l+2]))for i,j,l in((0,1,2),(1,2,0),(2,0,1))]
        weight=C(float(MAXWELL_TO_CAP)*float(a['radial_quadrature'][ir]))
        momentum=[scale(k,X)]+[scale(e,y)for y in Y]
        momentumh=[add(scale(kh,X),scale(k,Xh))]+[add(scale(eh,y),scale(e,yh))for y,yh in zip(Y,Yh)]
        nodes.append((A,e,r,d,k,beta,X,Rs,Y,B,weight,momentum,momentumh))
    def weak_E(test,testr,walltest,Htest):
        """Instantaneous physical a_t=h_t=0 extension, with actual p_dot."""
        Lg,clockg=C(0),C(0)
        for ir,(Aa,aar)in enumerate(zip(test,testr)):
            A,e,r,d,k,beta,X,Rs,Y,B,weight,mom,momh=nodes[ir]
            a1=Aa[0]
            dx=comm(A[0],a1)
            dr=[add(aar[f-1],add(comm(a1,A[f]),comm(A[1],Aa[f-1])))for f in range(2,5)]
            dy=[sub(comm(A[0],Aa[f-1]),scale(beta,dr[f-2]))for f in range(2,5)]
            db=[add(scale(C(2),Aa[i+1]),add(comm(Aa[j+1],A[l+2]),comm(A[j+2],Aa[l+1])))for i,j,l in((0,1,2),(1,2,0),(2,0,1))]
            Lg+=weight*(k*dot(X,dx)+e*sum((dot(x,y)for x,y in zip(Y,dy)),C(0))-
                r*sum((dot(x,y)for x,y in zip(Rs,dr)),C(0))-d*sum((dot(x,y)for x,y in zip(B,db)),C(0)))
            clockg+=weight*sum((dot(p,x)for p,x in zip(momh,Aa)),C(0))
        Ls=C(2)*wT/C(VOLUME)*dot(Dt,O(W[0],Htest))
        Ls-=C(2)*wS/C(VOLUME)*sum((dot(ds,add(O(aw,H),O(W[f],Htest)))for f,ds,aw in zip(range(2,5),Ds,walltest[1:])),C(0))
        Ls-=C(4)*wV/C(VOLUME)*lambdaH*(dot(H,H)-nu)*dot(H,Htest)
        clocks=dot(PiHh,Htest)
        return Lg-clockg+Ls-clocks,Lg,clockg,Ls,clocks
    # Build the literal fixed-chart physical q test maps. Geometry columns
    # are excluded; no coordinate representation is invented for deltaV.
    n=217;original=np.asarray(op.maps['old504_to_full'],int)[252:]
    selector=acb_mat(252,n)
    for i,d in enumerate(original):
        if 252<=int(d)<252+n:selector[i,int(d)-252]=1
    rawQ=op.matrix(op.P)*selector
    extra=np.asarray(op.maps['extra_coordinates_to_full'],int);extraQ=acb_mat(len(extra),n)
    for i,d in enumerate(extra):
        if 252<=int(d)<252+n:extraQ[i,int(d)-252]=1
    T=op.packed._coefficient_array(None,op.native_maps['extra_point_lift_high'],op.native_maps['extra_point_lift_low'])
    Wextra=op.packed._coefficient_array(None,op.native_maps['extra_wall_lift_high'],op.native_maps['extra_wall_lift_low']).reshape(20,len(extra))
    def cmatrix(obj):return acb_mat([[C(v)for v in row]for row in obj])
    Qpoint=[];Qr=[]
    for ir in range(nr):
        gb=op.matrix(op.maps['original_gauge_basis_high'].reshape(nr,80,20)[ir])+op.matrix(op.maps['original_gauge_basis_low'].reshape(nr,80,20)[ir])
        gr=op.matrix(op.maps['original_gauge_radial_basis_high'].reshape(nr,80,20)[ir])+op.matrix(op.maps['original_gauge_radial_basis_low'].reshape(nr,80,20)[ir])
        Qpoint.append(gb.transpose()*rows(rawQ,np.arange(100,180))+cmatrix(T[ir,:20,:])*extraQ)
        Qr.append(gr.transpose()*rows(rawQ,np.arange(100,180))+cmatrix(T[ir,40:60,:])*extraQ)
    wb=op.matrix(op.maps['original_wall_trace_map_high'].reshape(20,80))+op.matrix(op.maps['original_wall_trace_map_low'].reshape(20,80))
    Qwall=wb*rows(rawQ,np.arange(100,180))+cmatrix(Wextra)*extraQ
    selected=[j for j in range(n)if all(rawQ[i,j].is_zero()for i in range(100))]
    if not set(position.newq).issubset(selected):raise ValueError('Allnew59 physical gauge tests must be included')
    control=acb_mat(len(selected),1);Lcontrols=acb_mat(len(selected),4)
    Euler=value(clock,'actual_bare_primal217_Euler')
    for row,j in enumerate(selected):
        if any(not Qpoint[ir][c,j].is_zero()for ir in range(nr)for c in range(4))or any(not Qwall[c,j].is_zero()for c in range(4)):
            raise ValueError('Physical position control has an unaccounted temporal A0 test')
        if any(not rawQ[i,j].is_zero()for i in range(264,268)):raise ValueError('Position control has an unaccounted raw Hdot contact')
        test=[[[Qpoint[ir][4*f+c,j]for c in range(4)]for f in range(1,5)]for ir in range(nr)]
        testr=[[[Qr[ir][4*f+c,j]for c in range(4)]for f in range(1,5)]for ir in range(nr)]
        wt=[[Qwall[4*f+c,j]for c in range(4)]for f in range(1,5)]
        result=weak_E(test,testr,wt,[rawQ[260+i,j]for i in range(4)])
        control[row,0]=result[0]-Euler[j,0]
        for k in range(4):Lcontrols[row,k]=result[k+1]
    if upper(control)>2e-10:raise ArithmeticError('Literal physical Eulerfunctional disagrees with represented sameaction q rows')
    pairing=acb_mat(36,7);parts=[acb_mat(36,7)for _ in range(4)]
    print(json.dumps(dict(stage='actual_unprojected_deltaV_Euler',profiles=9,channels=4,rights=7,represented_controls=len(selected))),flush=True)
    for p0 in range(9):
        for channel in range(4):
            row=4*p0+channel
            for col in range(7):
                test=[];testr=[]
                for ir in range(nr):
                    par=[C(int(c==channel))*phi[ir,p0]for c in range(4)]
                    parr=[C(int(c==channel))*phir[ir,p0]for c in range(4)]
                    aa=[[pointR[ir*60+4*f+c,col]for c in range(4)]for f in range(1,5)]
                    ar=[[pointR[ir*60+40+4*f+c,col]for c in range(4)]for f in range(1,5)]
                    test.append([comm(x,par)for x in aa])
                    testr.append([add(comm(x,par),comm(y,parr))for x,y in zip(ar,aa)])
                wallpar=[C(int(c==channel))*phiw[0,p0]for c in range(4)]
                wt=[comm([wallR[4*f+c,col]for c in range(4)],wallpar)for f in range(1,5)]
                dH=[rawR[260+i,col]for i in range(4)]
                htest=scale(C(-1),O(wallpar,dH))
                result=weak_E(test,testr,wt,htest);pairing[row,col]=result[0]
                for k in range(4):parts[k][row,col]=result[k+1]
    chi=value(clock,'all36_clock_compatibility_compression');remainder=chi+pairing
    values=dict(actual_unprojected_physical_deltaV_Euler=pairing,
        deltaV_Euler_bulk_Lq=parts[0],deltaV_Euler_bulk_momentum_clock=parts[1],
        deltaV_Euler_scalar_Lq=parts[2],deltaV_Euler_scalar_momentum_clock=parts[3],
        actual_clock_projected_rhs_chi=chi,chi_plus_actual_deltaV_Euler_unresolved_remainder=remainder,
        same_action_physical_Euler_controls=control,represented_control_Lq_and_momentum_clock_terms=Lcontrols,
        actual_bare_scalar_momentum=acb_mat([[x]for x in PiH]),
        actual_bare_scalar_momentum_clock=acb_mat([[x]for x in PiHh]),
        actual_bare_full217_Euler=Euler,unchanged_parent_and_position_rights_guard=preserved)
    arrays=dict(master368=op.target['master368'],coordinate_time=op.target['coordinate_time'],
        temporal_profile_internal_labels=np.asarray([(p,c)for p in range(9)for c in range(4)]),
        represented_pure_gauge_or_Higgs_position_control_indices=np.asarray(selected))
    for k,v in values.items():
        arrays[k+'_high'],arrays[k+'_low']=op.split(v);arrays.update(op.exact.export_acb_exact_dyadic(v,k+'_exact'))
    path=out/'actual_unprojected_deltaV_bare_Euler_and_clock_projection.npz';_compressed_npz(path,arrays)
    for name,mod in list(sys.modules.items()):
        p=getattr(mod,'__file__',None)
        if p and(name=='bhsm'or name.startswith('bhsm.'))and Path(p).resolve().is_relative_to(ROOT):op.pin(Path(p).resolve())
    op.pin(Path(__file__))
    report=dict(classification='ACTUAL_UNPROJECTED_PHYSICAL_DELTA_V_BARE_EULER_CLOCK_CONTRIBUTION',
        source_sha256=sha256(source).hexdigest(),input_and_source_sha256=dict(sorted(op.pins.items())),
        archive=dict(name=path.name,bytes=path.stat().st_size,sha256=sha256(path.read_bytes()).hexdigest()),
        original_source_and_spatial_position_rights_guard_upper=upper(preserved),
        literal_physical_Euler_represented_controls_count=len(selected),
        literal_physical_Euler_vs_sameaction_canonical_Euler_upper=upper(control),
        actual_unprojected_deltaV_Euler_upper=upper(pairing),
        actual_SU2_deltaV_Euler_upper=upper(rows(pairing,[4*p+c for p in range(9)for c in range(3)])),
        actual_central_deltaV_Euler_upper=upper(rows(pairing,np.arange(9)*4+3)),
        actual_projected_clock_rhs_upper=upper(chi),chi_plus_actual_deltaV_Euler_remainder_upper=upper(remainder),
        bulk_Lq_upper=upper(parts[0]),bulk_actual_momentum_clock_upper=upper(parts[1]),
        scalar_Lq_upper=upper(parts[2]),scalar_actual_momentum_clock_upper=upper(parts[3]),
        coefficient_action_or_field_sampling_calls=0,base_Euler_not_assumed_zero=True,
        actual_physical_generator_not_derivative_of_cached_Z=True,deltaV_test_not_projected_into_state_carrier=True,
        zero_instantaneous_testtime_extension_is_not_zero_physical_Rdot=True,
        all_original48_nodes_actual_wall_YM_Higgs_potential_contacts_retained=True,
        unrepresented_test_is_weak_functional_not_new_state_coordinate=True,
        remaining_source_domain_operator_projection_terms_evaluated_separately=False,
        chi_is_not_proven_solvability_obstruction=True,exact_Z_leftnull_or_required_chi_zero_assumed=False,
        unknown_phase_clock_or_free31_or_source_correction_selected=False,
        physical_outgoing_or_full_derivative_Maxwell226_spin_moment_claimed=False,
        original_coupled_corrections=0)
    (out/'result.json').write_text(json.dumps(report,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps({k:report[k]for k in('literal_physical_Euler_represented_controls_count','literal_physical_Euler_vs_sameaction_canonical_Euler_upper','actual_unprojected_deltaV_Euler_upper','actual_projected_clock_rhs_upper','chi_plus_actual_deltaV_Euler_remainder_upper')}),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for k in('clock-folder','coefficient-folder','output'):p.add_argument('--'+k,type=Path,required=True)
    a=p.parse_args();sys.path.insert(0,str(ROOT/'src'))
    try:run(a.clock_folder,a.coefficient_folder,a.output)
    except Exception as e:
        import traceback
        if a.output.exists():(a.output/'failure.json').write_text(json.dumps(dict(error=repr(e),traceback=traceback.format_exc(),source_sha256=sha256(Path(__file__).read_bytes()).hexdigest()),indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
        raise

