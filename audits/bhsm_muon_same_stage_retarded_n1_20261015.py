"""MP finite canonical midpoint response of newly bound exact-stage n1 forms.

Zero initial data concern only the new infinitesimal probe. The supplied
background is never changed. This finite signed linear action is not a
physical outgoing field solution or nonlinear matching correction.
"""
from pathlib import Path
from hashlib import sha256
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
import argparse
import json
import sys


def run(repository,coefficients,output,steps,precision):
    import numpy as np
    from flint import acb,acb_mat,arb,ctx
    root,src,out=map(lambda p:Path(p).resolve(),(repository,coefficients,output))
    if steps<4 or steps%4:raise ValueError('Turn-on and stage corner must be resolved by multiples of four')
    out.mkdir(parents=True,exist_ok=False);sys.path[:0]=[str(root/'src'),str(Path(__file__).parent)]
    from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
    from bhsm_exact_action_balls import export_acb_exact_dyadic
    ctx.prec=precision;pins={};archives={}
    def read(p):
        p=Path(p);pins[str(p)]=sha256(p.read_bytes()).hexdigest()
        if p.suffix=='.json':return json.loads(p.read_text(encoding='utf8'))
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    def mat(a):return acb_mat([[acb(arb(float(v.real)),arb(float(v.imag)))for v in row]for row in np.asarray(a)])
    def sub(a,rows,cols):return acb_mat([[a[i,j]for j in cols]for i in rows])
    def bound(a):
        return max(float(np.nextafter(float(abs(a[i,j]).upper()),np.inf))for i in range(a.nrows())for j in range(a.ncols()))
    def save(name,data):
        p=out/name;_compressed_npz(p,data);archives[name]=sha256(p.read_bytes()).hexdigest()
    def ex(a,name):return export_acb_exact_dyadic(a,name+'_exact')
    def split(a,name):
        hi=np.array([[complex(a[i,j].real.mid(),a[i,j].imag.mid())for j in range(a.ncols())]for i in range(a.nrows())])
        lo=np.array([[complex((a[i,j]-acb(hi[i,j])).real.mid(),(a[i,j]-acb(hi[i,j])).imag.mid())for j in range(a.ncols())]for i in range(a.nrows())])
        return {name+'_high':hi,name+'_low':lo,**ex(a,name)}
    md=read(src/'result.json');stages=[]
    for j in range(2):
        name=f'stage_{j:04d}_exact_raw_signed_n1_forms_and_source.npz';p=src/name;z=read(p)
        if pins[str(p)]!=md['archives'][name]:raise ValueError('Different coefficient epoch')
        stages.append(z)
    if not stages[0]['coordinate_step'].item()==stages[1]['coordinate_step'].item():raise ValueError('Actual equal two-stage prefix required')
    total=acb(complex(2*stages[0]['coordinate_step'].item()));dt=total/steps
    Q=[mat(z['Q'].reshape(80,3))for z in stages];Qt=[mat(z['Q_coordinate_time'].reshape(80,3))for z in stages]
    def source(sigma):
        t=2*sigma-acb(.5);h=total/2
        p=[2*t**3-3*t*t+1,t**3-2*t*t+t,-2*t**3+3*t*t,t**3-t*t]
        pp=[6*t*t-6*t,3*t*t-4*t+1,-6*t*t+6*t,3*t*t-2*t]
        ppp=[12*t-6,6*t-4,-12*t+6,6*t-2]
        values=[Q[0],h*Qt[0],Q[1],h*Qt[1]]
        germ=[sum((v*c for v,c in zip(values,coeff)),acb_mat(80,3))/scale for coeff,scale in ((p,1),(pp,h),(ppp,h*h))]
        if sigma.real<=0:g,gt,gtt=acb(0),acb(0),acb(0)
        elif sigma.real>=arb(.25):g,gt,gtt=acb(1),acb(0),acb(0)
        else:
            u=4*sigma;D=total/4
            g=u**3*(10-15*u+6*u*u);gt=30*u*u*(1-u)**2/D;gtt=60*u*(1-u)*(1-2*u)/(D*D)
        return g*germ[0],gt*germ[0]+g*germ[1],gtt*germ[0]+2*gt*germ[1]+g*germ[2]
    reduced=[]
    for j,z in enumerate(stages):
        keep=np.argmax(z['interior_field_lift'],axis=0);na=int(z['coordinate_interior_At_count']);aa=range(na);dd=range(na,len(keep))
        full={k:mat(z[k])for k in ('K','M','B_forward','B_reverse')};S=mat(z['interior_field_lift']);L=mat(z['named_wall_lift']);C=mat(z['wall_and_frame_rows'])
        f={k:mat(z[k][np.ix_(keep,keep)])for k in full}
        K,M,BF,BR=[f[k]for k in('K','M','B_forward','B_reverse')]
        Kaa=sub(K,aa,aa);Kad=sub(K,aa,dd);BFad=sub(BF,aa,dd);Kda=sub(K,dd,aa);BRda=sub(BR,dd,aa)
        U=Kaa.solve(Kad);V=Kaa.solve(BFad)
        Kr=sub(K,dd,dd)-Kda*U;Fr=sub(BF,dd,dd)-Kda*V
        Rr=sub(BR,dd,dd)-BRda*U;Mr=sub(M,dd,dd)-BRda*V
        phase=Mr+dt*(Rr-Fr)/2-dt*dt*Kr/4
        reduced.append(dict(z=z,full=full,S=S,Sa=sub(S,range(336),aa),Sd=sub(S,range(336),dd),L=L,C=C,
            Cgram=C*C.transpose(),Kaa=Kaa,Kad=Kad,BFad=BFad,Kda=Kda,BRda=BRda,U=U,V=V,Kr=Kr,Fr=Fr,Rr=Rr,Mr=Mr,phase=phase,
            known={k:S.transpose()*v*L for k,v in full.items()},na=na,nd=len(keep)-na))
        print(json.dumps(dict(event='prepared_original_Gauss_and_phase',stage=j,Gauss=na,dynamic=len(keep)-na)),flush=True)
    nd=reduced[0]['nd'];x=acb_mat(nd,3);p=acb_mat(nd,3);initial=x.copy()if hasattr(x,'copy')else acb_mat(x)
    maxrows={};node_records=[];mid_records=[];maxima=lambda name,a:maxrows.__setitem__(name,max(maxrows.get(name,0.),bound(a)))
    def loads(r,sigma):
        wall,wt,wtt=source(sigma);G=r['known'];na=r['na'];aa=range(na);dd=range(na,na+nd)
        gv=G['K']*wall+G['B_forward']*wt;gp=G['B_reverse']*wall+G['M']*wt
        gvt=G['K']*wt+G['B_forward']*wtt;gpt=G['B_reverse']*wt+G['M']*wtt
        ag=r['Kaa'].solve(sub(gv,aa,range(3)));agt=r['Kaa'].solve(sub(gvt,aa,range(3)))
        return dict(wall=wall,wt=wt,wtt=wtt,ag=ag,agt=agt,
            gf=sub(gv,dd,range(3))-r['Kda']*ag,gp=sub(gp,dd,range(3))-r['BRda']*ag,
            gpt=sub(gpt,dd,range(3))-r['BRda']*agt)
    def reconstruct(r,x,p,sigma,v=None):
        s=loads(r,sigma)
        if v is None:v=r['Mr'].solve(p-r['Rr']*x-s['gp'])
        a=-r['U']*x-r['V']*v-s['ag'];field=r['Sa']*a+r['Sd']*x+r['L']*s['wall']
        return field,v,s
    for cell in range(steps):
        j=0 if cell<steps//2 else 1;r=reduced[j];sigma=acb(arb(2*cell+1)/(2*steps));s=loads(r,sigma)
        rhs=p-r['Rr']*x-s['gp']+dt*(r['Kr']*x+s['gf'])/2
        v=r['phase'].solve(rhs);xm=x+dt*v/2;pm=r['Mr']*v+r['Rr']*xm+s['gp']
        force=r['Kr']*xm+r['Fr']*v+s['gf'];xf=x+dt*v;pf=p+dt*force
        maxima('canonical_midpoint_momentum_rows',pm-(p+pf)/2)
        field,_,s=reconstruct(r,xm,pm,sigma,v)
        acceleration=r['Mr'].solve(force-r['Rr']*v-s['gpt'])
        at=-r['U']*v-r['V']*acceleration-s['agt'];rate=r['Sa']*at+r['Sd']*v+r['L']*s['wt']
        acc=r['Sd']*acceleration+r['L']*s['wtt'];f=r['full']
        original_force=f['K']*field+f['B_forward']*rate
        original_pt=f['M']*acc+f['B_reverse']*rate;euler=original_force-original_pt
        reaction=r['Cgram'].solve(r['C']*euler);rows=euler-r['C'].transpose()*reaction
        maxima('original336_linearized_Euler_after_named_reactions',rows)
        maxima('all64_At_Gauss_after_named_reactions',sub(rows,range(64),range(3)))
        W=mat(r['z']['wall_value_map'][:80]);F=mat(r['z']['frame_rows'])
        maxima('complete80_wall_value_rows',W*field-s['wall']);maxima('complete80_wall_rate_rows',W*rate-s['wt'])
        maxima('all16_named_frame_value_rows',F*field);maxima('all16_named_frame_rate_rows',F*rate)
        mid={**split(field,'actual_total_field336'),**split(rate,'actual_total_coordinate_rate336'),
             **split(reaction,'named_wall_and_frame_reactions92'),**split(s['wall'],'source_Q80'),**split(s['wt'],'source_Qdot80'),
             **split(rows,'original336_rows'),**split(xm,'free_position196'),**split(pm,'free_momentum196'),
             'cell':np.array(cell),'stage':np.array(j),'sigma':np.array(float(sigma.real)),
             'coordinate_time':np.array(complex(total)*float(sigma.real)),**split(mat(r['z']['wall_value_map'])*field,'wall_gauge80_and_natural_H16')}
        save(f'cell_{cell:04d}_same_stage_retarded_n1_midpoint.npz',mid)
        mid_records.append(dict(cell=cell,stage=j,original336_upper=bound(rows),field336_upper=bound(field)))
        # Two one-sided node traces reconstruct the instantaneous constitutive
        # field from that stage's canonical endpoint and the exact source germ.
        for side,xx,pp,k in(('left',x,p,cell),('right',xf,pf,cell+1)):
            sn=acb(arb(k)/steps);nf,nv,ns=reconstruct(r,xx,pp,sn)
            node={**split(nf,'actual_total_field336'),**split(mat(r['z']['wall_value_map'])*nf,'wall_gauge80_and_natural_H16'),
                **split(ns['wall'],'source_Q80'),**split(ns['wt'],'source_Qdot80'),**split(xx,'free_position196'),**split(pp,'free_momentum196'),
                'cell':np.array(cell),'stage':np.array(j),'node':np.array(k),'coordinate_time':np.array(complex(total)*k/steps)}
            save(f'cell_{cell:04d}_{side}_one_sided_node.npz',node)
        x,p=xf,pf
        print(json.dumps(dict(cell=cell,stage=j,original336_upper=bound(rows),field336_upper=bound(field))),flush=True)
    save('actual_nonzero_final_canonical_probe_remainder.npz',{**split(x,'final_free_position196'),**split(p,'final_free_momentum196'),**split(initial,'incoming_probe_position196')})
    result=dict(classification='NEW_FINITE_RETARDED_SIGNED_N1_WEAK_PROBE_CANONICAL_MIDPOINT_APPLICATION',
        steps=steps,precision_bits=precision,input_hashes=pins,archives=archives,cell_records=mid_records,original_row_upper_bounds=maxrows,
        all_finite_original_row_guards_pass=max(maxrows.values())<=2e-10,absolute_guard=2e-10,
        initial_probe_x_and_momentum_zero=True,full_nonzero_background_self_fields_retained=True,
        final_probe_position_upper=bound(x),final_probe_momentum_upper=bound(p),nonzero_final_remainder_retained=True,
        source_law='Single actual-midpoint Q/Qdot Hermite, multiplied by finite C2 ramp through total/4, then plateau. All three physical magnetic first-jet axes; complete At/Ar wall probe targets are zero by that specific source construction, not missing exterior data.',
        canonical_corner_law='The free x/Pi are carried unchanged across coefficient corners; constitutive velocity and At are reconstructed independently on both one-sided stage charts.',
        node_interpolation='Saved left/right node fields are instantaneous same-stage constitutive reconstructions from carried x/Pi and exact source germs. A consumer may interpolate canonical x/Pi linearly per Cayley cell and reapply this constitutive map/source germ. Raw field interpolation is a separate declared finite approximation; neither is a continuous physical exterior or a continuum error certificate.',
        coefficient_time_law='Exact saved stage M,Bforward,Breverse,K are constant inside each declared finite stage. Original background raw At and its supplied parent/reference motion enter their construction. No claim is made that this freezes the full physical formed-muon coefficient time dependence.',
        derivative_scope='Response is the exact infinitesimal B operand of this signed quadratic action discretization; no fresh full nonlinear-original B directional derivative or physical outgoing source/domain derivative is admitted by small internal rows.',
        field_layout='336=(original84 field coordinates:16 At,64 other gauge,4 H) x4 real n1 harmonics, using saved original_value_permutation. wall_gauge80_and_natural_H16 has24 x4 harmonic rows; first20 gauge traces and natural H4, all3 magnetic axes.',
        actual_physical_exterior_or_muon_pole_or_B_to_zero_limit_evaluated=False,full_physical_derivative_admitted=False,matching_corrections_applied=0,
        producer_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
    pth=out/'result.json';pth.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8')
    print(json.dumps(dict(result=str(pth),sha256=sha256(pth.read_bytes()).hexdigest(),max_original_row=max(maxrows.values()))),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repository',required=True);p.add_argument('--coefficients',required=True);p.add_argument('--output',required=True)
    p.add_argument('--steps',type=int,required=True);p.add_argument('--precision',type=int,default=256)
    a=p.parse_args();run(a.repository,a.coefficients,a.output,a.steps,a.precision)
