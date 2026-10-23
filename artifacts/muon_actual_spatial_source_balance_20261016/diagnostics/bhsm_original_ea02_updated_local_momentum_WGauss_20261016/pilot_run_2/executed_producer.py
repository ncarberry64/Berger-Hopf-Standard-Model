"""Updated local gauge/Higgs momentum variations and unprojected W*A_G.

Exact algebraic phase-particular reconstruction;179 gauge/Higgs momentum
rows are independently projected,38 geometry momentum rows remain separately
cached. No action/coefficient/history resampling or clock choice occurs.
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
POSITION='audits/bhsm_original_ea02_d4_position_operator_20261016.py'
POSITION_SHA='70670f411a2a11d301677359500be28fb9769f1557000b3262eb5939816ae389'
OWNER='audits/bhsm_original_ea02_physical_deltaV_Euler_clock_20261016.py'
OWNER_SHA='979045f0e0869905d7e66c926e0cb28ba4d38c0df6d3c6873eaca7d9581839ac'
CLOCK_SHA='8d4a7fe4fe24501c6d2e00681ed9ca4f1e2b5eb9d0793b3e775bab4c92b58574'
CLOCK_NPZ='2e0b2140004e37699f80ed25d14c8d988f657598f6b7d4b1269bce292cf7039d'
MIXED_NPZ='455dd5ad74325e5b6a0d3e7a0c4c3133d99635e6ca3416fe204513821def387f'
COEFF_SHA='c744590f986e47c946f128641b071808f527d230ba60fc2fa70adf87d351c851'
COEFF_NPZ='6cf8979c6d81fb427a23a93848f13a87400a615daae0e1496698d042f85755a2'
DW_SHA='e24c29222001f4ec1fd16b73612cb232cee1978058bbae62bb0ba876d73265ea'
DW_NPZ='7fc855345c6c6b8c7ed0c086925897826529a3aeacab2c91075cd25e34ad2914'
CANDIDATE_SHA='9dfa4106cf342144657327aea1a84303651264474091f2a9affe8f39bb19c60c'
CANDIDATE_NPZ='f26c230209ba793905793bcd71aabed6e6e26051370a5f8ac578a24ea9f3c609'


def run(clock_folder,coefficient_folder,deltaW_folder,candidate_folder,output):
    out=Path(output).resolve();out.mkdir(parents=True,exist_ok=False)
    source=Path(__file__).read_bytes();(out/'executed_producer.py').write_bytes(source)
    p=ROOT/POSITION
    if sha256(p.read_bytes()).hexdigest()!=POSITION_SHA:raise ValueError('Locked position metadata changed')
    spec=importlib.util.spec_from_file_location('same_ea02_for_updated_p',p)
    m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
    position=m.ActualEa02D4PositionOperator();op=position.phase;op.pin(p,POSITION_SHA)
    from flint import acb,acb_mat
    from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
    from bhsm.interface.muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation
    from bhsm.interface.muon_parent_mean_causal_action import MAXWELL_TO_CAP
    from bhsm.interface.muon_literal_euclidean_wall_action import VOLUME
    from bhsm.interface.muon_parent_retarded_hypercharge import WALL
    def packet(folder,ss,ns,name=None):
        folder=Path(folder).resolve();meta=op.read(folder/'result.json');op.pin(folder/'executed_producer.py',ss)
        if meta['source_sha256']!=ss:raise ValueError('Reviewed source required')
        z=op.read(folder/(meta['archive']['name']if name is None else name),ns)
        if not np.array_equal(z['master368'],op.target['master368'])or z['coordinate_time'].item()!=op.target['coordinate_time'].item():raise ValueError('No state/source/epoch splice')
        return z
    clock=packet(clock_folder,CLOCK_SHA,CLOCK_NPZ)
    a=packet(coefficient_folder,COEFF_SHA,COEFF_NPZ,'actual_same_ea02_D4_seven_point_density_R_hR.npz')
    dw=packet(deltaW_folder,DW_SHA,DW_NPZ)
    candidate=packet(candidate_folder,CANDIDATE_SHA,CANDIDATE_NPZ)
    mixed=op.read(Path(clock_folder)/'fresh_material_clock_application.npz',MIXED_NPZ)
    owner=op.pin(OWNER,OWNER_SHA).read_text();start=owner.index('    def C(v):');end=owner.index('    def weak_E(',start)
    block=textwrap.dedent(owner[start:end])
    ns=dict(op=op,a=a,np=np,acb=acb,acb_mat=acb_mat,value=op.value,rows=op.rows,upper=op.upper,
        RADIAL='artifacts/muon_baton_zoo_radial_convergence_20261014',
        higgs_u2_real_representation=higgs_u2_real_representation,MAXWELL_TO_CAP=MAXWELL_TO_CAP,VOLUME=VOLUME)
    exec(compile(block,OWNER+':literal_context','exec'),ns)
    C,comm,add,sub,scale,dot,O=(ns[k]for k in('C','comm','add','sub','scale','dot','O'))
    nodes,PiH,H,Dt,point,pointR,wall,wallR,raw,rawR,weights,phi,phir,phiw=(ns[k]for k in
        ('nodes','PiH','H','Dt','point','pointR','wall','wallR','raw','rawR','weights','phi','phir','phiw'))
    value,rows,upper=op.value,op.rows,op.upper;nr=len(nodes);n=217
    Rold=value(a,'actual_complete_right');Rnew=value(clock,'actual_open_family_particular_full746_right');change=Rnew-Rold
    if upper(value(mixed,'actual_right')-Rnew)>1e-25:raise ValueError('Fresh native momentum matvec must use identical updated rights')
    preserved=rows(change,np.r_[np.arange(252),252+np.arange(217)])
    if upper(preserved)>1e-30 or any(not preserved[i,j].contains(0)for i in range(preserved.nrows())for j in range(7)):raise ValueError('Only child phase particular may change')
    original=np.asarray(op.maps['old504_to_full'],int)[252:];extra=np.asarray(op.maps['extra_coordinates_to_full'],int)
    rawpart=op.matrix(op.P)*rows(change,original);extrapart=rows(change,extra)
    T=op.packed._coefficient_array(None,op.native_maps['extra_point_lift_high'],op.native_maps['extra_point_lift_low'])
    We=op.packed._coefficient_array(None,op.native_maps['extra_wall_lift_high'],op.native_maps['extra_wall_lift_low']).reshape(20,len(extra))
    def cmatrix(obj):return acb_mat([[C(z)for z in row]for row in obj])
    # Admit the prior exact A0-potential guard, not a new zero-potential choice.
    for key in('updated_particular_A0_potential_change','updated_particular_A0_radial_change','updated_particular_wall_A0_potential_change'):
        z=value(dw,key)
        if upper(z)>1e-30 or any(not z[i,j].contains(0)for i in range(z.nrows())for j in range(z.ncols())):raise ValueError('Actual A0 potential preservation required')
    mat=value(a,'material_coordinates');wallchi,Cstar,dr=(mat[0,i]for i in(2,3,1))
    s=raw[0,98];jac=C(2)*wallchi/C(WALL)
    # Cstar/lcstar are owned at FIXED chi*=pi/4, not displaced wallchi.
    dlc=acb_mat(1,7);ddr=acb_mat(1,7)
    for col in range(7):
        dlc[0,col]=rawpart[37,col]+sum((C((-1)**k)*rawpart[37+k,col]for k in range(1,13)),C(0))+sum((C((-1)**j)*rawpart[50+j,col]for j in range(12)),C(0))
        ddr[0,col]=(rawpart[99,col]-s*dlc[0,col])/Cstar
    def logNpart(chi,col):return sum((rawpart[74+k-1,col]*(C(4*k)*chi).cos()for k in range(1,13)),C(0))
    def betaPart(chi,col):return(C(4)*chi).sin()*sum((rawpart[86+j,col]*(C(4*j)*chi).cos()for j in range(12)),C(0))
    def shapeC(chi):return sum((raw[0,k]*(C(4*k)*chi).cos()for k in range(1,13)),C(0))+(C(2)*chi).sin()**2*sum((raw[0,13+j]*(C(4*j)*chi).cos()for j in range(12)),C(0))
    fixedchi=C(float(np.pi/4))
    Cwall=Cstar*(shapeC(wallchi)-shapeC(fixedchi)).exp()
    Nwall=sum((raw[0,74+k-1]*(C(4*k)*wallchi).cos()for k in range(1,13)),C(0)).exp()
    betaWall=(C(4)*wallchi).sin()*sum((raw[0,86+j]*(C(4*j)*wallchi).cos()for j in range(12)),C(0))
    U=weights[0,5];Ucheck=Cwall/Nwall*(dr+betaWall)-U
    if upper(acb_mat([[Ucheck]]))>1e-30:raise ValueError('Literal current wall coefficient reconstruction changed branch/source')
    wT=weights[0,0];wTR=value(a,'boundary_weights_R');wallpart=acb_mat(1,7)
    for col in range(7):
        dn=logNpart(wallchi,col);du=Cwall/Nwall*(ddr[0,col]+betaPart(wallchi,col))-U*dn
        wallpart[0,col]=-wT*(dn-U*du/(1-U*U))
    pR=acb_mat(nr*16,7);pPart=acb_mat(nr*16,7);densitypart=acb_mat(nr*5,7);Atpart=acb_mat(nr*20,7)
    densityR=value(a,'density_R')
    for ir in range(nr):
        chi=C(float(a['rho'][ir]))/C(WALL)*wallchi
        gb=op.matrix(op.maps['original_gauge_basis_high'].reshape(nr,80,20)[ir])+op.matrix(op.maps['original_gauge_basis_low'].reshape(nr,80,20)[ir])
        dAt=gb.transpose()*rows(rawpart,np.arange(180,260))+cmatrix(T[ir,20:40,:])*extrapart
        A,e,r,d,k,beta,X,Rs,Y,_,_,_,_=nodes[ir]
        for col in range(7):
            logn=logNpart(chi,col);dbeta=(C(2)*betaPart(chi,col)+C(2)*C(float(a['rho'][ir]))/C(WALL)*ddr[0,col])/jac
            densitypart[5*ir,col]=-e*logn;densitypart[5*ir+1,col]=r*logn
            densitypart[5*ir+2,col]=d*logn;densitypart[5*ir+3,col]=-k*logn;densitypart[5*ir+4,col]=dbeta
            for ii in range(20):Atpart[20*ir+ii,col]=dAt[ii,col]
            dA=[[pointR[ir*60+4*f+i,col]for i in range(4)]for f in range(5)]
            dAr=[[pointR[ir*60+40+4*f+i,col]for i in range(4)]for f in range(5)]
            dOldAt=[[pointR[ir*60+20+4*f+i,col]for i in range(4)]for f in range(5)]
            dX=add(sub(dOldAt[1],dAr[0]),add(comm(dA[0],A[1]),comm(A[0],dA[1])))
            dRs=[add(dAr[f],add(comm(dA[1],A[f]),comm(A[1],dA[f])))for f in range(2,5)]
            dYs=[sub(add(dOldAt[f],add(comm(dA[0],A[f]),comm(A[0],dA[f]))),add(scale(densityR[5*ir+4,col],Rs[f-2]),scale(beta,dRs[f-2])))for f in range(2,5)]
            old=[add(scale(densityR[5*ir+3,col],X),scale(k,dX))]+[add(scale(densityR[5*ir,col],y),scale(e,dy))for y,dy in zip(Y,dYs)]
            part=[add(scale(-k*logn,X),scale(k,[dAt[4+i,col]for i in range(4)]))]+[
                add(scale(-e*logn,Y[f-2]),scale(e,sub([dAt[4*f+i,col]for i in range(4)],scale(dbeta,Rs[f-2]))))for f in range(2,5)]
            for f in range(4):
                for i in range(4):pPart[16*ir+4*f+i,col]=part[f][i];pR[16*ir+4*f+i,col]=old[f][i]+part[f][i]
    PiHR=acb_mat(4,7)
    for col in range(7):
        dH=[rawR[260+i,col]for i in range(4)];dHt=[rawR[264+i,col]for i in range(4)]
        dA0=[wallR[i,col]for i in range(4)];A0=[wall[0,i]for i in range(4)]
        dDt=add(dHt,add(O(dA0,H),O(A0,dH)))
        total=add(scale(wTR[0,col]+wallpart[0,col],Dt),scale(wT,add(dDt,[rawpart[264+i,col]for i in range(4)])))
        for i,z in enumerate(scale(C(2)/C(VOLUME),total)):PiHR[i,col]=z
    # Independent projection of all179 gauge/Higgs velocity rows. The other
    #38 geometry momenta contain cap/eta terms and remain separately cached.
    sv=acb_mat(252,n);ev=acb_mat(len(extra),n)
    for i,d in enumerate(original):
        if 252+n<=int(d)<252+2*n:sv[i,int(d)-252-n]=1
    for i,d in enumerate(extra):
        if 252+n<=int(d)<252+2*n:ev[i,int(d)-252-n]=1
    rawV=op.matrix(op.P)*sv;selected=[j for j in range(n)if all(rawV[i,j].is_zero()for i in range(100))]
    if len(selected)!=179 or not set(position.newq).issubset(selected):raise ValueError('Every actual pure gauge/Higgs velocity row required')
    native=rows(value(mixed,'phase_Hessian_on_actual_right'),np.arange(217));reconstructed=acb_mat(179,7)
    for ir in range(nr):
        gb=op.matrix(op.maps['original_gauge_basis_high'].reshape(nr,80,20)[ir])+op.matrix(op.maps['original_gauge_basis_low'].reshape(nr,80,20)[ir])
        basis=gb.transpose()*rows(rawV,np.arange(180,260))+cmatrix(T[ir,20:40,:])*ev
        weight=nodes[ir][10]
        for row,j in enumerate(selected):
            for col in range(7):reconstructed[row,col]+=weight*sum((pR[16*ir+4*f+i,col]*basis[4*(f+1)+i,j]for f in range(4)for i in range(4)),C(0))
    for row,j in enumerate(selected):
        for col in range(7):reconstructed[row,col]+=sum((PiHR[i,col]*rawV[264+i,j]for i in range(4)),C(0))
    control=reconstructed-rows(native,selected);geometry=np.setdiff1d(np.arange(217),selected)
    if upper(control)>2e-10:raise ArithmeticError('Updated local gauge/Higgs momentum reconstruction failed actual179 native rows')
    def Gvar(theta,thetar,tw,col):
        result=C(0)
        for ir,(t,tr)in enumerate(zip(theta,thetar)):
            A,_,_,_,_,_,_,_,_,_,weight,mom,_=nodes[ir]
            image=[add(scale(C(-1),tr),comm(t,A[1]))]+[comm(t,A[f])for f in range(2,5)]
            dAi=[[pointR[ir*60+4*f+i,col]for i in range(4)]for f in range(1,5)]
            result+=weight*sum((dot([pR[16*ir+4*f+i,col]for i in range(4)],image[f])+dot(mom[f],comm(t,dAi[f]))for f in range(4)),C(0))
        return result+dot([PiHR[i,col]for i in range(4)],O(tw,H))+dot(PiH,O(tw,[rawR[260+i,col]for i in range(4)]))
    Gcontrols=acb_mat(36,7);nativeG=rows(value(mixed,'phase_Hessian_on_actual_right'),np.arange(217+24,277))
    WAG=acb_mat(36,7);WGR=acb_mat(36,7);Wprimal=value(dw,'actual_unprojected_primal_W_Gauss')
    for p0 in range(9):
        for c0 in range(4):
            row=4*p0+c0;theta=[];thetar=[];wt=[];wtr=[]
            for ir in range(nr):
                par=[C(int(i==c0))*phi[ir,p0]for i in range(4)];pr=[C(int(i==c0))*phir[ir,p0]for i in range(4)]
                theta.append(par);thetar.append(pr)
                A0=[point[ir,i]for i in range(4)];A0r=[point[ir,40+i]for i in range(4)]
                wt.append(comm(A0,par));wtr.append(add(comm(A0r,par),comm(A0,pr)))
            tw=[C(int(i==c0))*phiw[0,p0]for i in range(4)];ww=comm([wall[0,i]for i in range(4)],tw)
            for col in range(7):
                Gcontrols[row,col]=Gvar(theta,thetar,tw,col)-nativeG[row,col]
                WGR[row,col]=Gvar(wt,wtr,ww,col);WAG[row,col]=WGR[row,col]+(Wprimal[row,0]if col==0 else C(0))
    if upper(Gcontrols)>2e-10:raise ArithmeticError('Updated arbitrary Gauss variation failed all36 independently evaluated native rows')
    before=value(dw,'chi_plus_deltaV_Euler_plus_deltaW_G_remainder');after=before+WAG
    candidate_rhs_guard=value(candidate,'saved_projected36_clock_rhs')-value(dw,'actual_projected_clock_rhs_chi')
    if upper(candidate_rhs_guard)>1e-25 or any(not candidate_rhs_guard[i,j].contains(0)for i in range(36)for j in range(7)):
        raise ValueError('Candidate must consume the identical same-cut projected clock RHS')
    projected_LHS=value(candidate,'actual_projected_clock_LHS')
    combined_defect=projected_LHS-after
    values=dict(updated_local_spatial_momentum_variation=pR,phase_particular_local_momentum_increment=pPart,
        phase_particular_density_variation=densitypart,phase_particular_connection_time_derivative_increment=Atpart,
        phase_particular_dr=ddr,phase_particular_fixed_reference_lc=dlc,phase_particular_boundary_wT_increment=wallpart,
        updated_local_scalar_momentum_variation=PiHR,literal_wall_U_reconstruction_guard=acb_mat([[Ucheck]]),
        independent179_updated_momentum_covectors=reconstructed,independent179_vs_fresh_native_momentum_rows=control,
        cached38_geometry_momentum_rows_separate=rows(native,geometry),actual_full217_native_momentum_rows_separate=native,
        independent36_updated_Gauss_variation_controls=Gcontrols,actual_unprojected_W_times_trial_Gauss=WGR,
        actual_unprojected_W_times_affine_Gauss=WAG,cumulative_remainder_before_W_affine_Gauss=before,
        cumulative_remainder_after_W_affine_Gauss=after)
    values.update(saved_candidate_projected_clock_LHS=projected_LHS,
        combined_source_domain_pullback_identity_defect=combined_defect,
        exact_same_candidate_projected_RHS_guard=candidate_rhs_guard,
        saved_candidate_original277_rows_separate=value(candidate,'fresh_original277_clock_rows'),
        saved_candidate_frame_reaction_separate=value(candidate,'computational_frame_reaction'))
    arrays=dict(master368=op.target['master368'],coordinate_time=op.target['coordinate_time'],
        independent_gauge_Higgs_velocity_indices=np.asarray(selected),cached_geometry_velocity_indices=geometry)
    for key,z in values.items():arrays[key+'_high'],arrays[key+'_low']=op.split(z);arrays.update(op.exact.export_acb_exact_dyadic(z,key+'_exact'))
    path=out/'actual_updated_local_momenta_and_unprojected_W_affine_Gauss.npz';_compressed_npz(path,arrays)
    for name,mod in list(sys.modules.items()):
        p=getattr(mod,'__file__',None)
        if p and(name=='bhsm'or name.startswith('bhsm.'))and Path(p).resolve().is_relative_to(ROOT):op.pin(Path(p).resolve())
    op.pin(Path(__file__))
    report=dict(classification='ACTUAL_UPDATED_PHASE_LOCAL_MOMENTA_AND_W_AFFINE_GAUSS',
        source_sha256=sha256(source).hexdigest(),input_and_source_sha256=dict(sorted(op.pins.items())),
        exact_literal_context_owner_sha256=OWNER_SHA,exact_literal_context_block_sha256=sha256(block.encode()).hexdigest(),
        archive=dict(name=path.name,bytes=path.stat().st_size,sha256=sha256(path.read_bytes()).hexdigest()),
        independent_gauge_Higgs_momentum_rows=179,cached_geometry_momentum_rows=38,
        independent179_momentum_control_upper=upper(control),independent36_updated_Gauss_control_upper=upper(Gcontrols),
        actual_updated_local_momentum_upper=upper(pR),actual_updated_scalar_momentum_upper=upper(PiHR),
        actual_unprojected_W_trial_Gauss_upper=upper(WGR),actual_unprojected_W_affine_Gauss_upper=upper(WAG),
        cumulative_remainder_before_upper=upper(before),cumulative_remainder_after_upper=upper(after),
        saved_candidate_projected_clock_LHS_upper=upper(projected_LHS),
        combined_source_domain_pullback_identity_defect_upper=upper(combined_defect),
        saved_candidate_original277_rows_upper=upper(values['saved_candidate_original277_rows_separate']),
        candidate_projection_is_actual_framed_candidate_not_unframed_clock_pass=True,
        wall_U_reconstruction_guard_upper=upper(acb_mat([[Ucheck]])),
        fixed_reference_lc_star_at_pi_over4_not_moving_wall=True,
        original_primal_Gauss_added_once_only_affine_column0=True,
        independent179_not_mislabeled_full217_independent=True,cached38_cap_momentum_not_reconstructed_from_gauge_p=True,
        no_action_AD_coefficient_history_sampling_calls=True,no_projection_of_W_into_temporal_basis=True,
        exact_Z_leftnull_chi_zero_or_physical_clock_solution_claimed=False,
        remaining_source_domain_projected_operator_defects_not_set_zero=True,
        physical_outgoing_full_derivative_Maxwell226_spin_moment_claimed=False,original_coupled_corrections=0)
    (out/'result.json').write_text(json.dumps(report,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps({k:report[k]for k in('independent179_momentum_control_upper','independent36_updated_Gauss_control_upper','actual_unprojected_W_affine_Gauss_upper','cumulative_remainder_after_upper')}),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for k in('clock-folder','coefficient-folder','deltaW-folder','candidate-folder','output'):p.add_argument('--'+k,type=Path,required=True)
    a=p.parse_args();sys.path.insert(0,str(ROOT/'src'))
    try:run(a.clock_folder,a.coefficient_folder,a.deltaW_folder,a.candidate_folder,a.output)
    except Exception as e:
        import traceback
        if a.output.exists():(a.output/'failure.json').write_text(json.dumps(dict(error=repr(e),traceback=traceback.format_exc(),source_sha256=sha256(Path(__file__).read_bytes()).hexdigest()),sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
        raise

