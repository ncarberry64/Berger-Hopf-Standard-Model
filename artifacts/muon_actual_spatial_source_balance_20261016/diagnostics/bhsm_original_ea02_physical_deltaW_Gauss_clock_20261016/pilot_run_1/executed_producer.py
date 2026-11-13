"""Actual unprojected deltaW*G from retained same-cut gauge/source germs.

W=[A0,phi] is the temporal CONNECTION commutator, not a time derivative.
Only literal weak Gauss contractions are evaluated. No action/coefficient/
history replay, projected test, clock selection or outer correction occurs.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys
import textwrap
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
OWNER='audits/bhsm_original_ea02_physical_deltaV_Euler_clock_20261016.py'
OWNER_SHA='979045f0e0869905d7e66c926e0cb28ba4d38c0df6d3c6873eaca7d9581839ac'
POSITION='audits/bhsm_original_ea02_d4_position_operator_20261016.py'
POSITION_SHA='70670f411a2a11d301677359500be28fb9769f1557000b3262eb5939816ae389'
CLOCK_SHA='8d4a7fe4fe24501c6d2e00681ed9ca4f1e2b5eb9d0793b3e775bab4c92b58574'
CLOCK_NPZ='2e0b2140004e37699f80ed25d14c8d988f657598f6b7d4b1269bce292cf7039d'
COEFF_SHA='c744590f986e47c946f128641b071808f527d230ba60fc2fa70adf87d351c851'
COEFF_NPZ='6cf8979c6d81fb427a23a93848f13a87400a615daae0e1496698d042f85755a2'
DELTA_V_NPZ='7c8f3b515139473a664c94a394a3cf1afd09078a0be57795793ec296f390fe87'


def run(clock_folder,coefficient_folder,deltaV_folder,output):
    out=Path(output).resolve();out.mkdir(parents=True,exist_ok=False)
    source=Path(__file__).read_bytes();(out/'executed_producer.py').write_bytes(source)
    path=ROOT/POSITION
    if sha256(path.read_bytes()).hexdigest()!=POSITION_SHA:raise ValueError('Reviewed locked position metadata changed')
    spec=importlib.util.spec_from_file_location('same_ea02_metadata_for_deltaW',path)
    m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
    position=m.ActualEa02D4PositionOperator();op=position.phase;op.pin(path,POSITION_SHA)
    from flint import acb,acb_mat
    from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
    from bhsm.interface.muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation
    from bhsm.interface.muon_parent_mean_causal_action import MAXWELL_TO_CAP
    from bhsm.interface.muon_literal_euclidean_wall_action import VOLUME
    def packet(folder,ss,ns,name=None):
        folder=Path(folder).resolve();meta=op.read(folder/'result.json')
        if meta['source_sha256']!=ss:raise ValueError('Reviewed operand source changed')
        op.pin(folder/'executed_producer.py',ss)
        return op.read(folder/(meta['archive']['name']if name is None else name),ns)
    clock=packet(clock_folder,CLOCK_SHA,CLOCK_NPZ)
    a=packet(coefficient_folder,COEFF_SHA,COEFF_NPZ,'actual_same_ea02_D4_seven_point_density_R_hR.npz')
    dv=packet(deltaV_folder,OWNER_SHA,DELTA_V_NPZ)
    for z in(clock,a,dv):
        if not np.array_equal(z['master368'],op.target['master368'])or z['coordinate_time'].item()!=op.target['coordinate_time'].item():raise ValueError('Exact original state/source/time required')
    owner=op.pin(OWNER,OWNER_SHA).read_text()
    start=owner.index('    def C(v):');end=owner.index('    def weak_E(',start)
    block=textwrap.dedent(owner[start:end])
    # This is exact, hashed literal owner code, not a changed callback or
    # runtime patch. Explicit namespace excludes ambient frame inspection.
    ns=dict(op=op,a=a,np=np,acb=acb,acb_mat=acb_mat,value=op.value,rows=op.rows,upper=op.upper,
        higgs_u2_real_representation=higgs_u2_real_representation,MAXWELL_TO_CAP=MAXWELL_TO_CAP,VOLUME=VOLUME)
    exec(compile(block,str(ROOT/OWNER)+':literal_context','exec'),ns)
    C,comm,add,scale,dot,O=(ns[k]for k in('C','comm','add','scale','dot','O'))
    nodes,PiH,H,point,pointR,wall,wallR,phi,phir,phiw=(ns[k]for k in
        ('nodes','PiH','H','point','pointR','wall','wallR','phi','phir','phiw'))
    nr=len(nodes);v=op.value;rows=op.rows;upper=op.upper
    Rold=v(a,'actual_complete_right');Rnew=v(clock,'actual_open_family_particular_full746_right');change=Rnew-Rold
    original=np.asarray(op.maps['old504_to_full'],int)[252:];extra=np.asarray(op.maps['extra_coordinates_to_full'],int)
    rawchange=op.matrix(op.P)*rows(change,original);extrachange=rows(change,extra)
    T=op.packed._coefficient_array(None,op.native_maps['extra_point_lift_high'],op.native_maps['extra_point_lift_low'])
    W=op.packed._coefficient_array(None,op.native_maps['extra_wall_lift_high'],op.native_maps['extra_wall_lift_low']).reshape(20,len(extra))
    def cmatrix(obj):return acb_mat([[C(z)for z in row]for row in obj])
    gaugechange=rows(rawchange,np.arange(100,180));potential=acb_mat(nr*4,7);radial=acb_mat(nr*4,7)
    for ir in range(nr):
        gb=op.matrix(op.maps['original_gauge_basis_high'].reshape(nr,80,20)[ir])+op.matrix(op.maps['original_gauge_basis_low'].reshape(nr,80,20)[ir])
        gr=op.matrix(op.maps['original_gauge_radial_basis_high'].reshape(nr,80,20)[ir])+op.matrix(op.maps['original_gauge_radial_basis_low'].reshape(nr,80,20)[ir])
        delta=gb.transpose()*gaugechange+cmatrix(T[ir,:20,:])*extrachange
        deltar=gr.transpose()*gaugechange+cmatrix(T[ir,40:60,:])*extrachange
        for i in range(4):
            for j in range(7):potential[4*ir+i,j]=delta[i,j];radial[4*ir+i,j]=deltar[i,j]
    wb=op.matrix(op.maps['original_wall_trace_map_high'].reshape(20,80))+op.matrix(op.maps['original_wall_trace_map_low'].reshape(20,80))
    wallchange=rows(wb*gaugechange+cmatrix(W)*extrachange,np.arange(4))
    frame=op.F*rows(change,op.phaseids)
    potential_guards=dict(point_A0_potential=upper(potential),point_A0_radial=upper(radial),wall_A0_potential=upper(wallchange),fixed_allAt_frame_change=upper(frame))
    for z in(potential,radial,wallchange,frame):
        if upper(z)>1e-30 or any(not z[i,j].contains(0)for i in range(z.nrows())for j in range(z.ncols())):
            raise ValueError('Updated particular does not preserve actual temporal potential germ')
    def Gauss(theta,thetar,thetawall):
        bulk=C(0)
        for ir,(t,tr)in enumerate(zip(theta,thetar)):
            A,_,_,_,_,_,_,_,_,_,weight,momentum,_=nodes[ir]
            image=[add(scale(C(-1),tr),comm(t,A[1]))]+[comm(t,A[f])for f in range(2,5)]
            bulk+=weight*sum((dot(p,k)for p,k in zip(momentum,image)),C(0))
        scalar=dot(PiH,O(thetawall,H))
        return bulk+scalar,bulk,scalar
    # Check the arbitrary-test functional on every represented temporal phi.
    control=acb_mat(36,1);base=v(clock,'actual_bare_primal277_gradient')
    for p0 in range(9):
        for c0 in range(4):
            theta=[[C(int(i==c0))*phi[ir,p0]for i in range(4)]for ir in range(nr)]
            thetar=[[C(int(i==c0))*phir[ir,p0]for i in range(4)]for ir in range(nr)]
            tw=[C(int(i==c0))*phiw[0,p0]for i in range(4)]
            control[4*p0+c0,0]=Gauss(theta,thetar,tw)[0]-base[217+24+4*p0+c0,0]
    if upper(control)>2e-10:raise ArithmeticError('Literal arbitrary Gauss functional disagrees with every actual represented temporal row')
    result,bulk,scalar=(acb_mat(36,7)for _ in range(3));primalW=acb_mat(36,1)
    print(json.dumps(dict(stage='actual_unprojected_deltaW_primal_Gauss',parameters=36,rights=7)),flush=True)
    for p0 in range(9):
        for c0 in range(4):
            row=4*p0+c0
            Wtheta=[];Wradial=[]
            for ir in range(nr):
                par=[C(int(i==c0))*phi[ir,p0]for i in range(4)]
                parr=[C(int(i==c0))*phir[ir,p0]for i in range(4)]
                A0=[point[ir,i]for i in range(4)];A0r=[point[ir,40+i]for i in range(4)]
                Wtheta.append(comm(A0,par));Wradial.append(add(comm(A0r,par),comm(A0,parr)))
            wallpar=[C(int(i==c0))*phiw[0,p0]for i in range(4)]
            Wwall=comm([wall[0,i]for i in range(4)],wallpar)
            primalW[row,0]=Gauss(Wtheta,Wradial,Wwall)[0]
            for col in range(7):
                theta=[];thetar=[]
                for ir in range(nr):
                    par=[C(int(i==c0))*phi[ir,p0]for i in range(4)]
                    parr=[C(int(i==c0))*phir[ir,p0]for i in range(4)]
                    A0R=[pointR[ir*60+i,col]for i in range(4)]
                    A0rR=[pointR[ir*60+40+i,col]for i in range(4)]
                    theta.append(comm(A0R,par));thetar.append(add(comm(A0rR,par),comm(A0R,parr)))
                tw=comm([wallR[i,col]for i in range(4)],wallpar)
                r=Gauss(theta,thetar,tw);result[row,col]=r[0];bulk[row,col]=r[1];scalar[row,col]=r[2]
    chi=v(clock,'all36_clock_compatibility_compression');dVE=v(dv,'actual_unprojected_physical_deltaV_Euler')
    oldremainder=v(dv,'chi_plus_actual_deltaV_Euler_unresolved_remainder')
    if upper(chi+dVE-oldremainder)>1e-25:raise ValueError('Exact same projected RHS/Euler contribution required')
    remainder=chi+dVE+result
    values=dict(actual_unprojected_deltaW_primal_Gauss=result,deltaW_G_bulk=bulk,deltaW_G_scalar=scalar,
        actual_unprojected_primal_W_Gauss=primalW,all36_represented_temporal_Gauss_controls=control,
        actual_projected_clock_rhs_chi=chi,actual_physical_deltaV_Euler=dVE,
        chi_plus_deltaV_Euler_remainder=oldremainder,chi_plus_deltaV_Euler_plus_deltaW_G_remainder=remainder,
        updated_particular_A0_potential_change=potential,updated_particular_A0_radial_change=radial,
        updated_particular_wall_A0_potential_change=wallchange,updated_particular_allAt_frame_change=frame)
    arrays=dict(master368=op.target['master368'],coordinate_time=op.target['coordinate_time'],
        temporal_profile_internal_labels=np.asarray([(p,c)for p in range(9)for c in range(4)]))
    for key,z in values.items():arrays[key+'_high'],arrays[key+'_low']=op.split(z);arrays.update(op.exact.export_acb_exact_dyadic(z,key+'_exact'))
    path=out/'actual_unprojected_deltaW_Gauss_and_clock_remainder.npz';_compressed_npz(path,arrays)
    for name,mod in list(sys.modules.items()):
        p=getattr(mod,'__file__',None)
        if p and(name=='bhsm'or name.startswith('bhsm.'))and Path(p).resolve().is_relative_to(ROOT):op.pin(Path(p).resolve())
    op.pin(Path(__file__))
    report=dict(classification='ACTUAL_UNPROJECTED_DELTA_W_PRIMAL_GAUSS_CLOCK_CONTRIBUTION',
        source_sha256=sha256(source).hexdigest(),input_and_source_sha256=dict(sorted(op.pins.items())),
        exact_literal_context_owner_sha256=OWNER_SHA,exact_literal_context_block_sha256=sha256(block.encode()).hexdigest(),
        archive=dict(name=path.name,sha256=sha256(path.read_bytes()).hexdigest(),bytes=path.stat().st_size),
        temporal_connection_preservation_guards=potential_guards,all36_literal_Gauss_controls_upper=upper(control),
        actual_deltaW_G_upper=upper(result),actual_deltaW_G_bulk_upper=upper(bulk),actual_deltaW_G_scalar_upper=upper(scalar),
        actual_primal_W_G_upper=upper(primalW),chi_plus_deltaV_Euler_before_upper=upper(oldremainder),
        chi_plus_deltaV_Euler_plus_deltaW_G_after_upper=upper(remainder),
        W_uses_temporal_connection_A0_not_point_time_derivative=True,deltaW_test_unprojected_with_radial_and_actual_wall=True,
        actual_updated_A0_A0radial_wall_potential_preservation_verified=True,
        original48_quadrature_density_scalar_current_retained_once=True,
        coefficient_action_or_history_sampling_calls=0,remaining_W_times_affine_Gauss_evaluated=False,
        remaining_source_domain_operator_terms_not_individually_zeroed=True,
        exact_Z_leftnull_or_required_chi_zero_claimed=False,unknown_phase_clock_or_free31_source_values_selected=False,
        physical_outgoing_derivative_radial_Maxwell226_spin_moment_claimed=False,original_coupled_corrections=0)
    (out/'result.json').write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps({k:report[k]for k in('all36_literal_Gauss_controls_upper','actual_deltaW_G_upper','chi_plus_deltaV_Euler_before_upper','chi_plus_deltaV_Euler_plus_deltaW_G_after_upper')}),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for k in('clock-folder','coefficient-folder','deltaV-folder','output'):p.add_argument('--'+k,type=Path,required=True)
    a=p.parse_args();sys.path.insert(0,str(ROOT/'src'))
    try:run(a.clock_folder,a.coefficient_folder,a.deltaV_folder,a.output)
    except Exception as e:
        import traceback
        if a.output.exists():(a.output/'failure.json').write_text(json.dumps(dict(error=repr(e),traceback=traceback.format_exc(),source_sha256=sha256(Path(__file__).read_bytes()).hexdigest()),sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
        raise

