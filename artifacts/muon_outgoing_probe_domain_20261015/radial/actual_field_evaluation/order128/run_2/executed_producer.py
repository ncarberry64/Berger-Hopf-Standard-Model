"""Certified polynomial-moment solution of the NEW finite signed n1 action.

The fixed stage coefficients and actual Hermite-times-C2 source are consumed
without redoing any background/source/D5 history. The canonical source shift
removes Qdot exactly. This finite time-ODE result is not a physical retarded
exterior, continuum certificate, complete B derivative, or matching correction.
"""
from __future__ import annotations
from hashlib import sha256
from math import comb
from pathlib import Path
import argparse
import json
import os
import sys

os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
import numpy as np
from flint import acb, acb_mat, arb, ctx


def upper_float(a):
    return float(np.nextafter(float(a.upper()), np.inf))


def entry_bound(a):
    result=arb(0)
    for i in range(a.nrows()):
        for j in range(a.ncols()):
            result=max(result,arb(abs(a[i,j]).upper()))
    return result


def induced_inf_bound(a):
    result=arb(0)
    for i in range(a.nrows()):
        row=arb(0)
        for j in range(a.ncols()): row+=abs(a[i,j]).upper()
        result=max(result,arb(row.upper()))
    return result


def inflated(a,error):
    """A complex norm error bounds each real and imaginary component too."""
    ball=acb(arb(0,error.upper()),arb(0,error.upper()))
    return acb_mat([[a[i,j]+ball for j in range(a.ncols())]for i in range(a.nrows())])


def horner(coefficients,u):
    result=acb_mat(coefficients[-1])
    for c in coefficients[-2::-1]:result=result*u+c
    return result


def derivative_coefficients(coefficients):
    if len(coefficients)==1:return [acb_mat(coefficients[0].nrows(),coefficients[0].ncols())]
    return [coefficients[k]*k for k in range(1,len(coefficients))]


def shifted_polynomial_step(A,B0,B1,source_coefficients,z0,duration,*,tolerance=arb('1e-50'),max_order=64):
    """z'=Az+B0 Q+B1 Qdot; w=z-B1 Q, exact degree-d polynomial Q(u).

    With D=duration*A, F_n=duration*(A*B1+B0)*Q_n and u in [0,1],
    c0=w0; c[n+1]=(D*c[n]+F_n)/(n+1). After N>d, subsequent coefficients
    are D^j*cN*N!/(N+j)!. A geometric majorant of this factorial tail
    rigorously bounds value, first and second coordinate-time derivatives.
    Source shifts must be recomputed when stage coefficients change; z is
    the carried canonical state, so its stage corner is unchanged.
    """
    if not source_coefficients or duration==0:raise ValueError('nonempty polynomial and nonzero time interval required')
    q=source_coefficients; D=A*duration; beta=induced_inf_bound(D)
    force=(A*B1+B0)*duration
    forcing=[force*c for c in q]
    c=[z0-B1*q[0]]; zero=acb_mat(z0.nrows(),z0.ncols())
    for n in range(max_order):
        c.append((D*c[-1]+(forcing[n]if n<len(forcing)else zero))/(n+1))
        N=n+1
        if N<len(forcing):continue
        if not beta<arb(N+2):raise ArithmeticError('factorial-tail ratio not below one; recondition or subdivide mathematically')
        last=entry_bound(c[-1])
        tail=arb((last*beta/(N+1)/(1-beta/(N+2))).upper())
        if tail<=tolerance:break
    else:raise ArithmeticError('bounded polynomial-series order exhausted')
    residual=arb((beta*last).upper())
    first=arb(((beta*tail+residual)/abs(duration)).upper())
    second=arb(((beta*(beta*tail+residual)+N*residual)/(abs(duration)**2)).upper())
    q1=horner(q,acb(1)); w1=inflated(horner(c,acb(1)),tail)
    return dict(coefficients=c,source=q,duration=duration,B1=B1,
        beta=beta,order=N,tail=tail,first_tail=first,second_tail=second,
        z_start=acb_mat(z0),z_end=w1+B1*q1,
        normalized_ODE_defect_bound=residual)


def polynomial_state(piece,u):
    """Enclose the actual continuous finite ODE state and its derivatives."""
    c,q,B1,h=(piece[k]for k in('coefficients','source','B1','duration'))
    qd=derivative_coefficients(q); qdd=derivative_coefficients(qd)
    Q=horner(q,u); Qt=horner(qd,u)/h; Qtt=horner(qdd,u)/(h*h)
    w=inflated(horner(c,u),piece['tail'])
    wt=inflated(horner(derivative_coefficients(c),u)/h,piece['first_tail'])
    wtt=inflated(horner(derivative_coefficients(derivative_coefficients(c)),u)/(h*h),piece['second_tail'])
    return dict(z=w+B1*Q,zt=wt+B1*Qt,ztt=wtt+B1*Qtt,Q=Q,Qt=Qt,Qtt=Qtt)


def run(repository,coefficients,reduced_maps,output,*,steps=16,precision=256):
    if steps<4 or steps%4:raise ValueError('sample grid must resolve ramp and coefficient corners')
    root,src,redsrc,out=map(lambda p:Path(p).resolve(),(repository,coefficients,reduced_maps,output))
    if out.exists():raise FileExistsError('preserve every independent actual polynomial application')
    ctx.prec=precision;sys.path[:0]=[str(root/'src'),str(Path(__file__).parent)]
    from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
    from bhsm_exact_action_balls import export_acb_exact_dyadic,parse_acb_exact_dyadic
    pins={};archives={};maxrows={};records=[];pieces=[]
    def read(p):
        p=Path(p);raw=p.read_bytes();pins[str(p)]=sha256(raw).hexdigest()
        if p.suffix=='.json':return json.loads(raw)
        with np.load(p,allow_pickle=False)as a:return{k:a[k].copy()for k in a.files}
    def mat(a):return acb_mat([[acb(arb(float(v.real)),arb(float(v.imag)))for v in row]for row in np.asarray(a)])
    def sub(a,rows,cols):return acb_mat([[a[i,j]for j in cols]for i in rows])
    def block(a,b,c,d):return acb_mat([[a[i,j]if j<a.ncols()else b[i,j-a.ncols()]for j in range(a.ncols()+b.ncols())]for i in range(a.nrows())]
        +[[c[i,j]if j<c.ncols()else d[i,j-c.ncols()]for j in range(c.ncols()+d.ncols())]for i in range(c.nrows())])
    def horizontal(a,b):return acb_mat([[a[i,j]if j<a.ncols()else b[i,j-a.ncols()]for j in range(a.ncols()+b.ncols())]for i in range(a.nrows())])
    def split(a,name):
        hi=np.array([[complex(a[i,j].real.mid(),a[i,j].imag.mid())for j in range(a.ncols())]for i in range(a.nrows())])
        lo=np.array([[complex((a[i,j]-acb(hi[i,j])).real.mid(),(a[i,j]-acb(hi[i,j])).imag.mid())for j in range(a.ncols())]for i in range(a.nrows())])
        return {name+'_high':hi,name+'_low':lo,**export_acb_exact_dyadic(a,name+'_exact')}
    def save(name,data):
        path=out/name;_compressed_npz(path,data);archives[name]=sha256(path.read_bytes()).hexdigest()
    def maxima(name,a):maxrows[name]=max(maxrows.get(name,0.),upper_float(entry_bound(a)))
    md=read(src/'result.json');rmd=read(redsrc/'result.json');stages=[]
    for j in range(2):
        name=f'stage_{j:04d}_exact_raw_signed_n1_forms_and_source.npz';p=src/name;z=read(p)
        if pins[str(p)]!=md['archives'][name]:raise ValueError('original coefficient epoch changed')
        name=f'stage_{j:04d}_original_reduced_operator_and_polynomial_source_maps.npz';p=redsrc/name;rr=read(p)
        if pins[str(p)]!=rmd['archives'][name]:raise ValueError('reduced coefficient epoch changed')
        for key in ('Q','Q_coordinate_time','interior_field_lift','named_wall_lift','wall_and_frame_rows'):
            if not np.array_equal(z[key],rr[key]):raise ValueError('reduced/source stage differs: '+key)
        keep=np.argmax(z['interior_field_lift'],axis=0);na=int(z['coordinate_interior_At_count']);nd=len(keep)-na
        parse=lambda key:parse_acb_exact_dyadic(rr,key+'_exact')
        Mr,Kr,Fr,Rr=[parse(k)for k in('Mr','Kr','Fr','Rr')]
        gp0,gp1,gf0,gf1=[parse(k)for k in('Gp0','Gp1','Gf0','Gf1')]
        inv=Mr.inv();top0=-inv*gp0;top1=-inv*gp1
        A=block(-inv*Rr,inv,Kr-Fr*inv*Rr,Fr*inv)
        B0=block(top0,acb_mat(nd,0),gf0+Fr*top0,acb_mat(nd,0))
        B1=block(top1,acb_mat(nd,0),gf1+Fr*top1,acb_mat(nd,0))
        S=mat(z['interior_field_lift']);L=mat(z['named_wall_lift']);C=mat(z['wall_and_frame_rows'])
        full={k:mat(z[k])for k in('K','M','B_forward','B_reverse')}
        Sa=sub(S,range(336),range(na));Sd=sub(S,range(336),range(na,na+nd))
        maxima('original_M_annihilates_At_columns',full['M']*Sa)
        if maxrows['original_M_annihilates_At_columns']>2e-10:raise ArithmeticError('At second derivative cannot be omitted from original mass action')
        stage=dict(original=z,A=A,B0=B0,B1=B1,Mr=Mr,Minv=inv,Kr=Kr,Fr=Fr,Rr=Rr,
            Gp0=gp0,Gp1=gp1,Gf0=gf0,Gf1=gf1,U=parse('original_Gauss_position_map'),V=parse('original_Gauss_velocity_map'),
            ag0=parse('Gauss_wall_value_map'),ag1=parse('Gauss_wall_rate_map'),
            Sa=Sa,Sd=Sd,L=L,C=C,reaction_inverse=(C*C.transpose()).inv(),
            W=mat(z['wall_value_map'][:80]),F=mat(z['frame_rows']),wall_full=mat(z['wall_value_map']),full=full,nd=nd)
        fieldx=Sd-Sa*stage['U']+Sa*stage['V']*inv*Rr
        fieldp=-Sa*stage['V']*inv
        stage['field_state_map']=horizontal(fieldx,fieldp)
        stage['field_source_value_map']=L+Sa*(stage['V']*inv*gp0-stage['ag0'])
        stage['field_source_rate_map']=Sa*(stage['V']*inv*gp1-stage['ag1'])
        stage['field_state_inf']=induced_inf_bound(stage['field_state_map'])
        stage['wall_state_inf']=induced_inf_bound(stage['wall_full']*stage['field_state_map'])
        stages.append(stage)
        print(json.dumps(dict(event='prepared_MP_original_stage',stage=j,nd=nd,
            canonical_A_stage_h_inf=upper_float(induced_inf_bound(A*acb(complex(z['coordinate_step'].item())))))),flush=True)
    if stages[0]['nd']!=196 or stages[1]['nd']!=196:raise ValueError('same represented canonical fiber required')
    if not np.array_equal(stages[0]['original']['coordinate_step'],stages[1]['original']['coordinate_step']):raise ValueError('same saved equal two-stage prefix required')
    h=acb(complex(stages[0]['original']['coordinate_step'].item()));total=2*h
    Q=[mat(r['original']['Q'].reshape(80,3))for r in stages]
    Qt=[mat(r['original']['Q_coordinate_time'].reshape(80,3))for r in stages]
    # Actual Hermite basis at sigma=1/4 and 3/4, t=2sigma-1/2.
    # These exact rational coefficient lists are not fitted quadrature data.
    # Derive the basis by exact polynomial arithmetic.
    def pmul(a,b):
        c=[acb(0)for _ in range(len(a)+len(b)-1)]
        for i,x in enumerate(a):
            for j,y in enumerate(b):c[i+j]+=x*y
        return c
    t=[-acb(1)/2,acb(2)];t2=pmul(t,t);t3=pmul(t2,t)
    def pcomb(*terms):
        v=[acb(0)for _ in range(max(len(a)for _,a in terms))]
        for scale,a in terms:
            for k,x in enumerate(a):v[k]+=scale*x
        return v
    H=[pcomb((2,t3),(-3,t2),(1,[acb(1)])),pcomb((1,t3),(-2,t2),(1,t)),
       pcomb((-2,t3),(3,t2)),pcomb((1,t3),(-1,t2))]
    values=[Q[0],h*Qt[0],Q[1],h*Qt[1]]
    base=[sum((v*c[k]for v,c in zip(values,H)),acb_mat(80,3))for k in range(4)]
    ramp=[acb(0),acb(0),acb(0),acb(640),acb(-3840),acb(6144)]
    rampQ=[acb_mat(80,3)for _ in range(9)]
    for i,a in enumerate(base):
        for k,b in enumerate(ramp):rampQ[i+k]+=a*b
    def affine_poly(poly,a,b):
        return [sum((poly[n]*(comb(n,k)*a**(n-k)*b**k)for n in range(k,len(poly))),acb_mat(80,3))for k in range(len(poly))]
    zcarry=acb_mat(392,3);initial=acb_mat(zcarry);boundaries=[acb(0),acb(1)/4,acb(1)/2,acb(1)]
    out.mkdir(parents=True)
    for k,(s0,s1)in enumerate(zip(boundaries[:-1],boundaries[1:])):
        j=0 if k<2 else 1;r=stages[j];q=affine_poly(rampQ if k==0 else base,s0,s1-s0)
        piece=shifted_polynomial_step(r['A'],r['B0'],r['B1'],q,zcarry,total*(s1-s0))
        piece.update(sigma0=s0,sigma1=s1,stage=j)
        start=polynomial_state(piece,acb(0))['z'];maxima('canonical_piece_corner_rows',start-zcarry)
        if pieces:
            old=pieces[-1];oldQ=horner(old['source'],acb(1));newQ=q[0]
            maxima('source_piece_corner_value_rows',newQ-oldQ)
            maxima('source_piece_corner_rate_rows',horner(derivative_coefficients(q),acb(0))/piece['duration']-
                   horner(derivative_coefficients(old['source']),acb(1))/old['duration'])
        zcarry=piece['z_end'];pieces.append(piece)
        arrays={}
        for n,c in enumerate(piece['coefficients']):arrays.update(export_acb_exact_dyadic(c,f'canonical_shifted_coefficient_{n:03d}_exact'))
        for n,c in enumerate(q):arrays.update(export_acb_exact_dyadic(c,f'actual_source_coefficient_{n:03d}_exact'))
        arrays.update(split(piece['z_start'],'canonical_start392'));arrays.update(split(zcarry,'canonical_end392'))
        arrays['sigma_bounds']=np.array([float(s0.real),float(s1.real)])
        save(f'piece_{k:03d}_certified_canonical_polynomial_and_source.npz',arrays)
        # Entire wall96 polynomial, avoiding downstream sample-and-hold error.
        wallcoeff=[];wallarrays={};hi_list=[];lo_list=[]
        recon_value=arb(0);recon_rate=arb(0);recon_acc=arb(0)
        zeroq=acb_mat(80,3)
        for n,c in enumerate(piece['coefficients']):
            qn=q[n]if n<len(q)else zeroq
            qtn=q[n+1]*(n+1)/piece['duration']if n+1<len(q)else zeroq
            zn=c+r['B1']*qn
            fc=r['field_state_map']*zn+r['field_source_value_map']*qn+r['field_source_rate_map']*qtn
            wc=r['wall_full']*fc;wallcoeff.append(wc)
            packed=split(wc,f'wall96_polynomial_coefficient_{n:03d}')
            wallarrays.update(packed)
            hi=packed[f'wall96_polynomial_coefficient_{n:03d}_high'];lo=packed[f'wall96_polynomial_coefficient_{n:03d}_low']
            hi_list.append(hi);lo_list.append(lo)
            reconstruction=mat(hi)+mat(lo);err=entry_bound(wc-reconstruction)
            recon_value+=err
            if n:recon_rate+=n*err/abs(piece['duration'])
            if n>1:recon_acc+=n*(n-1)*err/(abs(piece['duration'])**2)
        walltail=r['wall_state_inf']*piece['tail']
        walltail1=r['wall_state_inf']*piece['first_tail']
        walltail2=r['wall_state_inf']*piece['second_tail']
        wallarrays.update(wall96_polynomial_coefficients_high=np.array(hi_list),wall96_polynomial_coefficients_low=np.array(lo_list),
            coordinate_bounds=np.array([complex(total*s0),complex(total*s1)]),
            sigma_bounds=np.array([float(s0.real),float(s1.real)]),stage=np.array(j),
            wall96_value_tail_upper=np.array(upper_float(walltail)),
            wall96_coordinate_rate_tail_upper=np.array(upper_float(walltail1)),
            wall96_coordinate_acceleration_tail_upper=np.array(upper_float(walltail2)),
            full336_value_tail_upper=np.array(upper_float(r['field_state_inf']*piece['tail'])),
            full336_coordinate_rate_tail_upper=np.array(upper_float(r['field_state_inf']*piece['first_tail'])),
            full336_coordinate_acceleration_tail_upper=np.array(upper_float(r['field_state_inf']*piece['second_tail'])),
            wall96_saved_highlow_value_enclosure_upper=np.array(upper_float(walltail+recon_value)),
            wall96_saved_highlow_coordinate_rate_enclosure_upper=np.array(upper_float(walltail1+recon_rate)),
            wall96_saved_highlow_coordinate_acceleration_enclosure_upper=np.array(upper_float(walltail2+recon_acc)))
        wallname=f'piece_{k:03d}_certified_wall96_polynomial.npz';save(wallname,wallarrays)
        record=dict(piece=k,stage=j,source_degree=len(q)-1,series_order=piece['order'],
            A_duration_inf_upper=upper_float(piece['beta']),tail_state_upper=upper_float(piece['tail']),
            tail_coordinate_rate_upper=upper_float(piece['first_tail']),tail_coordinate_acceleration_upper=upper_float(piece['second_tail']),
            normalized_polynomial_ODE_defect_upper=upper_float(piece['normalized_ODE_defect_bound']),
            wall96_polynomial_file=wallname,wall96_value_tail_upper=upper_float(walltail),
            wall96_coordinate_rate_tail_upper=upper_float(walltail1),wall96_coordinate_acceleration_tail_upper=upper_float(walltail2),
            wall96_saved_highlow_value_enclosure_upper=upper_float(walltail+recon_value))
        records.append(record);print(json.dumps(record),flush=True)
    nd=196
    def sample(sigma,stage):
        k=2 if stage==1 else (0 if sigma.real<=arb(1)/4 else 1)
        piece=pieces[k];u=(sigma-piece['sigma0'])/(piece['sigma1']-piece['sigma0'])
        s=polynomial_state(piece,u);r=stages[stage];cols=range(3)
        x=sub(s['z'],range(nd),cols);p=sub(s['z'],range(nd,2*nd),cols)
        xt=sub(s['zt'],range(nd),cols);pt=sub(s['zt'],range(nd,2*nd),cols)
        xtt=sub(s['ztt'],range(nd),cols)
        Q,Qt,Qtt=s['Q'],s['Qt'],s['Qtt']
        gp=r['Gp0']*Q+r['Gp1']*Qt;gpt=r['Gp0']*Qt+r['Gp1']*Qtt
        gf=r['Gf0']*Q+r['Gf1']*Qt
        v=r['Minv']*(p-r['Rr']*x-gp)
        vt=r['Minv']*(pt-r['Rr']*xt-gpt)
        ag=r['ag0']*Q+r['ag1']*Qt;agt=r['ag0']*Qt+r['ag1']*Qtt
        a=-r['U']*x-r['V']*v-ag;at=-r['U']*xt-r['V']*vt-agt
        field=r['Sa']*a+r['Sd']*x+r['L']*Q
        rate=r['Sa']*at+r['Sd']*xt+r['L']*Qt
        # M*Sa=0 was checked literally, so the omitted At second derivative
        # cannot contribute to this ORIGINAL mass Euler row.
        relevant_acc=r['Sd']*xtt+r['L']*Qtt;f=r['full']
        euler=f['K']*field+f['B_forward']*rate-f['M']*relevant_acc-f['B_reverse']*rate
        reaction=r['reaction_inverse']*(r['C']*euler);rows=euler-r['C'].transpose()*reaction
        maxima('continuous_canonical_velocity_rows',xt-v)
        maxima('continuous_canonical_force_rows',pt-r['Kr']*x-r['Fr']*v-gf)
        maxima('continuous_canonical_momentum_rows',r['Mr']*xt+r['Rr']*x+gp-p)
        maxima('original336_linearized_Euler_after_named_reactions',rows)
        maxima('all64_At_Gauss_after_named_reactions',sub(rows,range(64),cols))
        maxima('complete80_wall_value_rows',r['W']*field-Q);maxima('complete80_wall_rate_rows',r['W']*rate-Qt)
        maxima('all16_named_frame_value_rows',r['F']*field);maxima('all16_named_frame_rate_rows',r['F']*rate)
        return dict(field=field,rate=rate,reaction=reaction,rows=rows,x=x,p=p,Q=Q,Qt=Qt,
                    wall=r['wall_full']*field,source=s)
    midrecords=[]
    for cell in range(steps):
        j=0 if cell<steps//2 else 1;sigma=acb(arb(2*cell+1)/(2*steps));a=sample(sigma,j)
        arrays={**split(a['field'],'actual_total_field336'),**split(a['rate'],'actual_total_coordinate_rate336'),
            **split(a['reaction'],'named_wall_and_frame_reactions92'),**split(a['Q'],'source_Q80'),**split(a['Qt'],'source_Qdot80'),
            **split(a['rows'],'original336_rows'),**split(a['x'],'free_position196'),**split(a['p'],'free_momentum196'),
            **split(a['wall'],'wall_gauge80_and_natural_H16'),
            'cell':np.array(cell),'stage':np.array(j),'sigma':np.array(float(sigma.real)),
            'coordinate_time':np.array(complex(total)*float(sigma.real))}
        save(f'cell_{cell:04d}_same_stage_retarded_n1_midpoint.npz',arrays)
        midrecords.append(dict(cell=cell,stage=j,original336_upper=upper_float(entry_bound(a['rows'])),
                               field336_upper=upper_float(entry_bound(a['field']))))
        for side,node in(('left',cell),('right',cell+1)):
            sn=acb(arb(node)/steps);n=sample(sn,j)
            arrays={**split(n['field'],'actual_total_field336'),**split(n['rate'],'actual_total_coordinate_rate336'),
                **split(n['wall'],'wall_gauge80_and_natural_H16'),**split(n['Q'],'source_Q80'),**split(n['Qt'],'source_Qdot80'),
                **split(n['x'],'free_position196'),**split(n['p'],'free_momentum196'),
                'cell':np.array(cell),'stage':np.array(j),'node':np.array(node),
                'coordinate_time':np.array(complex(total)*node/steps)}
            save(f'cell_{cell:04d}_{side}_one_sided_node.npz',arrays)
        print(json.dumps(dict(event='evaluated_continuous_polynomial_sample',cell=cell,stage=j,
            original336_upper=midrecords[-1]['original336_upper'])),flush=True)
    save('actual_nonzero_final_canonical_probe_remainder.npz',{
        **split(sub(zcarry,range(nd),range(3)),'final_free_position196'),
        **split(sub(zcarry,range(nd,2*nd),range(3)),'final_free_momentum196'),
        **split(sub(initial,range(nd),range(3)),'incoming_probe_position196')})
    result=dict(classification='CERTIFIED_SHIFTED_POLYNOMIAL_FINITE_RETARDED_SIGNED_N1_WEAK_PROBE',
        steps=steps,sampling_steps=steps,precision_bits=precision,input_hashes=pins,archives=archives,
        polynomial_piece_records=records,cell_records=midrecords,original_row_upper_bounds=maxrows,
        all_finite_original_row_guards_pass=max(maxrows.values())<=2e-10,absolute_guard=2e-10,
        integration_law='z=w+B1Q; wdot=A w+(AB1+B0)Q; exact actual source polynomials degree8/3/3 on three pieces; MP factorial-tail bounds for state/rate/acceleration.',
        canonical_corner_law='Carry the SAME z=(x,Pi) across each source/coefficient corner; shifted w changes by (B1_before-B1_after)Q. All one-sided velocities/At/reactions reconstructed independently.',
        source_law='The original two-midpoint cubic Hermite Q/Qdot times finite C2 ramp through total/4, then plateau. No source term or endpoint remainder is reset.',
        initial_probe_x_and_momentum_zero=True,full_nonzero_background_self_fields_retained=True,
        final_probe_position_upper=upper_float(entry_bound(sub(zcarry,range(nd),range(3)))),
        final_probe_momentum_upper=upper_float(entry_bound(sub(zcarry,range(nd,2*nd),range(3)))),
        nonzero_final_remainder_retained=True,
        node_interpolation='Nodes and midpoints evaluate the SAME continuous finite polynomial-series solution. A downstream sample-and-hold lepton integration still has its OWN separate sampling error; no field interpolation is needed to define this finite ODE solution.',
        coefficient_time_law='Original saved M/Bforward/Breverse/K are constant inside each declared stage; no physical formed-muon coefficient/time-domain completion is inferred.',
        derivative_scope='Original336 rows use differentiation of the polynomial canonical solution within each piece, with certified derivative tails. This is not a fresh full nonlinear-original B derivative or physical outgoing domain/source derivative.',
        exact_shift_removes_source_Qdot_before_time_integration=True,large_MP_exponential_used=False,
        actual_physical_exterior_or_muon_pole_or_B_to_zero_limit_evaluated=False,
        full_physical_derivative_admitted=False,matching_corrections_applied=0,
        producer_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
    path=out/'result.json';encoded=json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n'
    path.write_text(encoded,encoding='utf8',newline='\n');(out/'executed_producer.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps(dict(result=str(path),sha256=sha256(encoded.encode()).hexdigest(),
        max_original_row=max(maxrows.values()),all_finite_rows_pass=result['all_finite_original_row_guards_pass'])),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repository',required=True)
    p.add_argument('--coefficients',required=True);p.add_argument('--reduced-maps',required=True);p.add_argument('--output',required=True)
    p.add_argument('--steps',type=int,default=16);p.add_argument('--precision',type=int,default=256)
    a=p.parse_args();run(a.repository,a.coefficients,a.reduced_maps,a.output,steps=a.steps,precision=a.precision)
