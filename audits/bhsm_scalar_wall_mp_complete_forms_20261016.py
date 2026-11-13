"""Complete scalar-wall common-vector forms on the same REAL MP cell.

No radial integration, background solve, fitted coupling or source/domain
derivative is substituted. The protected MP coefficient owner is reused
at the actual changing wall and coordinate times. All off-shell gauge/H
contacts and dependent -eta H images remain in common1200 coordinates.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
import mpmath as mp
import numpy as np
from scipy import sparse


ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'audits')]
import bhsm_changing_lorenz_mp_coefficient_values_20261016 as owner
from bhsm.interface.muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation
from bhsm.interface.muon_parent_positive_coupled_field import VOLUME,coupled_wall_maps
from bhsm.interface.muon_parent_positive_coupled_temporal import paired_scalar_orbit_maps
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
from bhsm_real_ew_higgs_fp_common_forms_20261016 import scalar_point


OWNER_SHA='1b0a9713749feb062fecdb664598a7a5b3528bd72ec5aa18176ae88eb5b88eff'
PROFILES=(5,7,8,9,11,13,14)
FORM_NAMES=('scalar_kinetic_Hessian','scalar_lambda_coefficient','scalar_lambda_nu_squared_coefficient','scalar_Gram')


def z(shape):return owner.tensor.zeros(shape)
def eye(n):return owner.tensor.identity(n)
def norm(a):return max((abs(x)for x in np.asarray(a).flat),default=mp.mpf(0))
def dot(a,b):return sum(x*y for x,y in zip(a,b))


def mp_tuple_arrays(arrays,name,values):
    strings=[]
    for value in values.flat:
        sign,man,exp,bits=mp.mpf(value)._mpf_;strings.append(f'{sign}:{int(man):x}:{exp}:{bits}')
    arrays[name+'_exact_MP_tuple']=np.array(strings).reshape(values.shape)


def point_images(A,H,Hd,tg,b,bp,T,c):
    """Tiny internal maps for EVERY nonzero original intrinsic wall trace.

    Profile labels are the original15 common80-coordinate blocks. The
    other eight blocks have identically zero intrinsic wall trace under
    the existing radial/tent maps; no physical variable is discarded.
    W[f,p]=(W0 tensor I20)+(W1 tensor E_f) for angular f.
    """
    count=len(PROFILES);I=eye(4);O=np.array([sum((A[f,a]*T[a]for a in range(4)),z((4,4)))for f in range(5)],object)
    U=np.array([a@H for a in T],object).T;Ut=np.array([a@Hd for a in T],object).T
    hp,ht=z((count,4,4)),z((count,4,4));W=z((4,count,2,4,4))
    fslots=(0,2,3,4)
    for p,label in enumerate(PROFILES):
        if label<10:
            f=label-5
            if f in fslots:W[fslots.index(f),p,0]=b*I
        elif label<14:
            temporal=(label-11)//2;tv,tr=tg[temporal,:2]
            hp[p]=-tv*U;ht[p]=-tr*U-tv*Ut
            for fi,f in enumerate(fslots):
                W[fi,p,0]=tv*owner.ad_native(A[f],c)
                if f==0:W[fi,p,0]+=tr*I
                else:W[fi,p,1]=tv*I
        else:hp[p]=b*I;ht[p]=bp*I
    base=np.array([Hd+O[0]@H]+[O[f]@H for f in fslots[1:]],object)
    D=z(W.shape);V=z((4,4,4))
    for fi,f in enumerate(fslots):
        V[fi]=np.array([v@T[a]for a in range(4)for v in [base[fi]]],object)
        for p in range(count):
            D[fi,p,0]=(ht[p]if f==0 else z((4,4)))+O[f]@hp[p]+U@W[fi,p,0]
            if f!=0:D[fi,p,1]=hp[p]+U@W[fi,p,1]
    return hp,ht,W,D,V,base


def point_tensors(A,H,Hd,tg,b,bp,weights,T,c):
    hp,ht,W,D,V,base=point_images(A,H,Hd,tg,b,bp,T,c);n=len(PROFILES)
    result={name:z((n,n,10,4,4))for name in FORM_NAMES};kin=result[FORM_NAMES[0]]
    wT,wS,wV=weights;volume=owner.m(VOLUME);hh=dot(H,H)
    potential=4*np.outer(H,H)+2*hh*eye(4)
    for p in range(n):
        for q in range(n):
            for fi,w in enumerate((wT,wS,wS,wS)):
                a,b0=D[fi,p,0],D[fi,q,0];W0,Wq=W[fi,p,0],W[fi,q,0]
                kin[p,q,0]+=2*w/volume*(a.T@b0+W0.T@V[fi]@hp[q]+hp[p].T@V[fi].T@Wq)
                if fi:
                    ai,bi=D[fi,p,1],D[fi,q,1];Wp1,Wq1=W[fi,p,1],W[fi,q,1];index=fi-1
                    kin[p,q,1+index]+=2*w/volume*(a.T@bi+hp[p].T@V[fi].T@Wq1)
                    kin[p,q,4+index]+=2*w/volume*(ai.T@b0+Wp1.T@V[fi]@hp[q])
                    kin[p,q,7+index]+=2*w/volume*(ai.T@bi)
            pair=hp[p].T@hp[q]
            result[FORM_NAMES[1]][p,q,0]=2*wV/volume*(hp[p].T@potential@hp[q])
            result[FORM_NAMES[2]][p,q,0]=-4*wV/volume*pair
            result[FORM_NAMES[3]][p,q,0]=2*wV/volume*pair
    return result,dict(h=hp,ht=ht,W=W,D=D,V=V,base=base)


def angular_factors(E):
    E=owner.ma(E)
    return np.array([eye(20),*E,*[a.T for a in E],*[a.T@a for a in E]],object)


def assemble(coefficients,angular):
    """Full common1200 sparse MP entries; drop exact zeros only."""
    result={};harmonic=[[(i,j,a[i,j])for i in range(20)for j in range(20)if a[i,j]!=0]for a in angular]
    for p,labelp in enumerate(PROFILES):
        for q,labelq in enumerate(PROFILES):
            for k in range(10):
                for a in range(4):
                    for b in range(4):
                        value=coefficients[p,q,k,a,b]
                        if value==0:continue
                        for i,j,h in harmonic[k]:
                            index=(80*labelp+20*a+i,80*labelq+20*b+j)
                            result[index]=result.get(index,mp.mpf(0))+value*h
    return {k:v for k,v in result.items()if v!=0}


def save_matrix(arrays,name,entries):
    indices=list(sorted(entries));v=[float(entries[i])for i in indices]
    if any(value==0 and entries[i]!=0 for i,value in zip(indices,v)):raise ArithmeticError('Nonzero MP matrix entry underflowed at output')
    a=sparse.coo_matrix((v,([i[0]for i in indices],[i[1]for i in indices])),shape=(1200,1200)).tocsr()
    arrays[name+'_data'],arrays[name+'_indices'],arrays[name+'_indptr'],arrays[name+'_shape']=a.data,a.indices,a.indptr,np.array(a.shape)
    return a


def compare_entries(old,new):
    maximum,scaled,chosen=mp.mpf(0),mp.mpf(0),(0,0)
    for i in old.keys()|new.keys():
        a,b=old.get(i,mp.mpf(0)),new.get(i,mp.mpf(0));d=abs(b-a);maximum=max(maximum,d);r=d/max(mp.mpf(1),abs(a),abs(b))
        if r>scaled:scaled,chosen=r,i
    return dict(max_absolute=mp.nstr(maximum,65),max_entry_scaled=mp.nstr(scaled,65),index=list(chosen),
        old_value=mp.nstr(old.get(chosen,mp.mpf(0)),65),new_value=mp.nstr(new.get(chosen,mp.mpf(0)),65),
        denominator='max(1,abs(old),abs(new)) on every unrounded MP matrix entry, including differing exact supports')


def shadow_control(A,H,Hd,tg,b,bp,weights,E,point):
    """Existing independent literal full1200 owner on held point operands."""
    Af,Hf,Hdf,tgf,wf=[owner.tensor.as_float(a)for a in(A,H,Hd,tg,weights)]
    tf=np.r_[float(b),float(bp),tgf[0,:2],tgf[1,:2]]
    from bhsm.interface.muon_parent_positive_brst_ghost import ghost_radial_values
    radial=ghost_radial_values(np.array([float(owner.constants()['WALL'])]))[0]
    W=np.zeros((400,1200));W[:,:1120]=np.einsum('t,tij->ij',tf,coupled_wall_maps(Af,E,length=1.)['wall_time_profile_value_maps'])
    hs=paired_scalar_orbit_maps(Hf,Hdf,tf,radial)
    literal=scalar_point(wf,Hf,Hdf,Af,E,W,hs)[:4]
    factors=angular_factors(E);result={}
    for name,wanted in zip(FORM_NAMES,literal):
        entries=assemble(point[name],factors);rows,cols=np.array(list(entries)).T
        actual=np.array([float(entries[i])for i in entries]);expected=wanted[rows,cols]
        difference=abs(actual-expected)
        # All omitted positions are exactly zero under the owned maps.
        outside=wanted.copy();outside[rows,cols]=0
        result[name]=dict(max_absolute=float(max(np.max(difference),np.max(abs(outside)))),
            max_entry_scaled=float(max(np.max(difference/np.maximum(1,np.maximum(abs(actual),abs(expected)))),np.max(abs(outside)))),
            comparison='Binary64 literal original1200 point owner evaluated on the SAME rounded MP operands; no source resampling')
    return result


def literal_MP_controls(A,H,Hd,tg,b,bp,weights,E,T,c,length,point):
    """Independent literal polynomial second variation on full wall images.

    This constructs a,eta,h,ht directly from coefficient vectors, without
    point_images/D/V or its tensor factors. Harmonic pair integrals use
    the original orthonormal I20; no angular transpose is projected away.
    """
    em=owner.ma(E);I=eye(4);volume=owner.m(VOLUME)
    O=np.array([sum((A[f,a]*T[a]for a in range(4)),z((4,4)))for f in range(5)],object)
    U=np.array([a@H for a in T],object).T;Ud=np.array([a@Hd for a in T],object).T
    matrices={name:assemble(a,angular_factors(E))for name,a in point.items()};records=[]
    for mode in('mixed_common','independent_scalar'):
        Z=z((7,4,20))
        for p in range(7):
            if mode=='independent_scalar'and p!=6:continue
            for a in range(4):
                for h in range(20):
                    j=80*PROFILES[p]+20*a+h+1
                    Z[p,a,h]=(mp.cos(mp.mpf('.173')*j)+mp.sin(mp.mpf('.119')*j))/mp.sqrt(1200)
                    if p in(4,5):Z[p,a,h]*=length
        eta=tg[0,0]*Z[4]+tg[1,0]*Z[5];et=tg[0,1]*Z[4]+tg[1,1]*Z[5]
        h=b*Z[6]-U@eta;ht=bp*Z[6]-U@et-Ud@eta
        bases=[Hd+O[0]@H]+[O[f]@H for f in(2,3,4)]
        kinetic=mp.mpf(0)
        for fi,f in enumerate((0,2,3,4)):
            a=b*Z[fi]+owner.ad_native(A[f],c)@eta
            a+=et if f==0 else eta@em[fi-1].T
            first=(ht if f==0 else h@em[fi-1].T)+O[f]@h+U@a
            # Literal second covariant placement deltaOmega * deltaH.
            contact=mp.fsum(bases[fi][i]*T[cc,i,j]*a[cc,k]*h[j,k]
                for i in range(4)for cc in range(4)for j in range(4)for k in range(20))
            kinetic+=2*weights[0 if f==0 else 1]/volume*(mp.fsum(x*x for x in first.flat)+2*contact)
        h2=mp.fsum(x*x for x in h.flat);Hh=np.array([sum(H[a]*h[a,k]for a in range(4))for k in range(20)],object)
        literal=dict(zip(FORM_NAMES,(kinetic,weights[2]/volume*(8*sum(x*x for x in Hh)+4*dot(H,H)*h2),-4*weights[2]/volume*h2,2*weights[2]/volume*h2)))
        vector={80*PROFILES[p]+20*a+h:Z[p,a,h]for p in range(7)for a in range(4)for h in range(20)}
        for name,entries in matrices.items():
            q=mp.fsum(value*vector[i]*vector[j]for(i,j),value in entries.items());wanted=literal[name]
            records.append(dict(direction=mode,form=name,literal_MP_polynomial_second_variation=mp.nstr(wanted,65),
                tensor_MP_quadratic_contraction=mp.nstr(q,65),absolute=mp.nstr(abs(q-wanted),20),
                scaled=mp.nstr(abs(q-wanted)/max(mp.mpf(1),abs(q),abs(wanted)),20)))
    return records


def execute(refinement,application,output,orders=(8,12),dps=80):
    out=Path(output)
    if out.exists():raise FileExistsError('Preserve every component/time rule')
    if sha256(Path(owner.__file__).read_bytes()).hexdigest()!=OWNER_SHA:raise ValueError('Frozen reviewed MP coefficient owner required')
    phases,reference,frozen,E,pins=owner.load_inputs(refinement,application)
    Tbinary=higgs_u2_real_representation()['real_generators'];records=[];arrays={};out.mkdir(parents=True)
    (out/'executed_producer.py').write_bytes(Path(__file__).read_bytes())
    input_archives={'refinement/result.json':sha256((Path(refinement)/'result.json').read_bytes()).hexdigest(),
        'original_TIME6_archive':sha256((Path(application)/'changing_forms.npz').read_bytes()).hexdigest()}
    for side in('incoming','outgoing'):
        for q in(32,64,128):
            alias=f'refinement/{side}_radial{q}/forms.npz'
            input_archives[alias]=sha256((Path(refinement)/f'{side}_radial{q}'/'forms.npz').read_bytes()).hexdigest()
    with mp.workdps(dps):
        c=owner.constants();T=owner.ma(Tbinary);angular=angular_factors(E)
        for side in('incoming','outgoing'):
            phase=phases[side];length=abs(owner.m(phase['span']));origin=min(owner.m(phase['span']),mp.mpf(0));previous=None
            for order in orders:
                times,tw=owner.time_nodes(phase,frozen[side,128],'mp',order,dps)
                totals={name:z((7,7,10,4,4))for name in FORM_NAMES};samples=[];control=None;literal_control=None
                for ti,(u,weight)in enumerate(zip(times,tw)):
                    t=u+origin;raw=owner.raw_at(phase,t);g=owner.geometry(raw,c['WALL'],c)
                    chart=owner.response_chart(g['delta'],c,96,'mp',dps)
                    v=owner.coefficient(raw,t,c['WALL'],side,phase.get('parent_reference'),reference,c,chart)
                    # At rho=WALL, Ceff*z=C*(beta+wall_dot),
                    # using the owned material-coordinate shift exactly.
                    H=raw[260:264];Hd=owner.ma(phase['rate'][260:264]);speed=g['C']*g['wall']/c['WALL']*g['shift']/g['N']
                    if abs(speed)>=1:raise ArithmeticError('Same REAL timelike intrinsic wall required')
                    ell=g['N']*mp.sqrt(1-speed*speed);R=g['R'];weights=np.array([R**3/ell,ell*R,ell*R**3],object)
                    tg=owner.temporal_values(u,length);b=2*min(u/length,1-u/length);bp=(2 if u<length/2 else -2)/length
                    point,images=point_tensors(v['A'],H,Hd,tg,b,bp,weights,T,c)
                    for name in FORM_NAMES:totals[name]+=weight*point[name]
                    if ti==0 and order==orders[0]:
                        control=shadow_control(v['A'],H,Hd,tg,b,bp,weights,E,point)
                        literal_control=literal_MP_controls(v['A'],H,Hd,tg,b,bp,weights,E,T,c,length,point)
                    samples.append(dict(coordinate_time=mp.nstr(t,65),u=mp.nstr(u,65),weight=mp.nstr(weight,65),
                        wall_radius=mp.nstr(R,65),proper_clock=mp.nstr(ell,65),wall_speed=mp.nstr(speed,65),
                        wall_A=[[mp.nstr(a,65)for a in row]for row in v['A']],H=[mp.nstr(a,65)for a in H],H_coordinate_time=[mp.nstr(a,65)for a in Hd],
                        anchored_root_residual=mp.nstr(max(map(abs,chart['residual'])),12),
                        dependent_angular_ordinary_derivative_cancellation=mp.nstr(norm(images['D'][1:,4:6,1]),12),
                        offshell_contact_norm=mp.nstr(norm(images['V']),20)))
                    print(json.dumps(dict(side=side,time_order=order,time_node=ti+1,time_nodes=len(times))),flush=True)
                matrices={name:assemble(total,angular)for name,total in totals.items()}
                comparisons=None if previous is None else{name:compare_entries(previous[name],a)for name,a in matrices.items()}
                prefix=f'{side}_time{order}'
                for name,a in matrices.items():save_matrix(arrays,prefix+'_'+name,a)
                for name,total in totals.items():mp_tuple_arrays(arrays,prefix+'_'+name+'_coefficient',total)
                record=dict(side=side,time_order_per_half=order,previous_time_order=None if previous is None else orders[orders.index(order)-1],
                    full_common_coefficient_dimension=1200,independent_scalar_dimension=80,dependent_ghost_coordinate_dimension=320,
                    original_active_wall_common80_profile_labels=PROFILES,nonzero_matrix_entries={name:len(a)for name,a in matrices.items()},
                    all_entry_unrounded_MP_time_comparison=comparisons,
                    finite_scalar_wall_time_rule_pass=None if comparisons is None else all(mp.mpf(r['max_entry_scaled'])<=mp.mpf('2e-10')for r in comparisons.values()),
                    original_point_owner_shadow_control=control,independent_literal_MP_point_controls=literal_control,samples=samples)
                records.append(record);previous=matrices
    arrays['EW4_real_harmonic_derivatives']=E;arrays['Higgs_real_generators_held_binary']=Tbinary;arrays['original_active_wall_common80_profile_labels']=np.array(PROFILES)
    _compressed_npz(out/'scalar_wall_forms.npz',arrays)
    for name,module in list(sys.modules.items()):
        p=getattr(module,'__file__',None)
        if p and(name.startswith('bhsm.')or name.startswith('bhsm_'))and Path(p).is_relative_to(ROOT):pins[Path(p).relative_to(ROOT).as_posix()]=sha256(Path(p).read_bytes()).hexdigest()
    pins[Path(__file__).relative_to(ROOT).as_posix()]=sha256(Path(__file__).read_bytes()).hexdigest()
    for rel,h in pins.items():
        if sha256((ROOT/rel).read_bytes()).hexdigest()!=h:raise ValueError('Frozen owner/input changed: '+rel)
    result=dict(classification='COMPLETE_CHANGING_REAL_SCALAR_WALL_COMMON1200_MP_COMPONENT',records=records,arithmetic_dps=dps,
        source_and_owner_sha256=dict(sorted(pins.items())),numerical_sha256=sha256((out/'scalar_wall_forms.npz').read_bytes()).hexdigest(),
        input_archive_sha256=dict(sorted(input_archives.items())),
        protected_MP_coefficient_owner_sha256=OWNER_SHA,temporal_orders_per_half=list(orders),anchored_response_order=96,
        original_harmonic_basis_and_Higgs_generators_and_chart_constants_held=True,reference_coordinates_renormalized=False,
        independent_H_and_actual_H_coordinate_time_retained=True,dependent_minus_eta_H_and_full_rate_retained=True,
        full_offshell_gauge_scalar_contacts_retained=True,potential_lambda_and_lambda_nu_squared_unassigned=True,
        radial_integration_or_history_or_background_recomputed=False,normal_H_extension_or_second_bulk_Higgs_mass_added=False,
        classical_positive_scalar_component_is_microscopic_Pstrat=False,full15_common_form_or_source_domain_convergence=False,
        physical_outgoing_operator_or_C0_Cj_selected=False,physical_derivative_at_2e_minus10_passed=False,
        original_coupled_corrections=0,normalized_physical_spins=None,physical_muon_moment=None)
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(numerical_sha256=result['numerical_sha256'],result_sha256=sha256((out/'result.json').read_bytes()).hexdigest())),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--refinement',required=True);p.add_argument('--application',required=True);p.add_argument('--output',required=True);p.add_argument('--dps',type=int,default=80)
    a=p.parse_args()
    if a.dps<80:raise ValueError('MP80 or higher required')
    execute(a.refinement,a.application,a.output,dps=a.dps)
