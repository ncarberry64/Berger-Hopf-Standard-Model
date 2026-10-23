"""Constrained retarded applications of the actual full Maxwell reference.

The same affine geometry vector supplies lambda(t), its first derivatives
and all five-component action coefficients.  At is eliminated by its
literal Gauss row.  The radial trial section is an explicit computational
gauge slice, completed by the actual D_A eta columns.  Its nonstationary
gauge Euler reaction is retained: no physical quotient response is claimed.
"""
from __future__ import annotations

from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED,ZipFile,ZipInfo

import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.integrate import solve_ivp,simpson
from scipy.interpolate import CubicSpline
from scipy.linalg import cho_factor,cho_solve

from .muon_birth_candidate_geometry_action import ROOT,RESET_RECEIPT,STATE_SOURCE
from .muon_moving_geometric_action import retained_state
from .muon_parent_maxwell_full_q_application import (
    SOURCE,retained_full_q_angular_space,full_q_reference_operators,
    hessian_response_polynomials,geometric_response_factors)
from .muon_parent_maxwell_geometry_weak import geometric_connection_coefficient_jets
from .muon_parent_maxwell_full_weak import M as MECHANICAL_M
from .muon_parent_retarded_hypercharge import WALL,ALPHA,regular_radial_basis,compact_trace_pulse
from .muon_matched_mechanical_source import epsilon


def constrained_gauss_schur(mass,mixed,stiffness,gauss_count):
    """Eliminate exactly the algebraic temporal one-form, including its source.

    L=.5 zdot M zdot+z B zdot+.5 z K z.  y=At has no
    temporal momentum.  Its full equation is Kyy*y+Kyz*z+Byz*zdot=0.
    No unforced spatial Gauss or invented zero field is imposed.
    """
    if any(not np.isrealobj(x) for x in (mass,mixed,stiffness)):
        raise ValueError('real same-action matrices required; no complex projection')
    A,B,K=(np.asarray(x,float) for x in (mass,mixed,stiffness))
    if (A.ndim!=2 or A.shape[0]!=A.shape[1] or B.shape!=A.shape or K.shape!=A.shape
            or any(not np.isfinite(x).all() for x in (A,B,K))
            or type(gauss_count) is not int or not 0<gauss_count<len(A)):
        raise ValueError('finite same-action matrices and an explicit Gauss block required')
    n=gauss_count
    if np.max(abs(A[:n]))>1e-10 or np.max(abs(A[:,:n]))>1e-10 or np.max(abs(B[:,:n]))>1e-10:
        raise ValueError('At must be algebraic; no omitted temporal momentum is allowed')
    if np.max(abs(A-A.T))>1e-9 or np.max(abs(K-K.T))>1e-9:
        raise ValueError('literal real scalar Hessian mass and stiffness must be symmetric')
    factor=cho_factor(K[:n,:n])
    Y=cho_solve(factor,K[:n,n:]); Z=cho_solve(factor,B[:n,n:])
    return dict(M=A[n:,n:]-B[:n,n:].T@Z,
        B=B[n:,n:]-K[:n,n:].T@Z,K=K[n:,n:]-K[:n,n:].T@Y,
        At_value_map=-Y,At_velocity_map=-Z,Gauss_matrix=K[:n,:n],
        Gauss_value_row=K[:n,n:],Gauss_velocity_row=B[:n,n:])


def _time_forms(poly,factors,w,H,Hr,Q):
    # Each factor has three exact radial moments.  Split mixed profiles
    # before weighting; never multiply separately integrated densities.
    def block(i,j,left,right):
        li,lw=left;ri,rw=right
        out=np.zeros((408,408));P=poly[:,i,j]
        ww=w[:,None]*factors
        ff=np.sum(ww*(li*ri)[:,None],axis=0)
        fw=np.sum(ww*(li*rw)[:,None],axis=0)
        wf=np.sum(ww*(lw*ri)[:,None],axis=0)
        sw=np.sum(ww*(lw*rw)[:,None],axis=0)
        out[:400,:400]=np.einsum('f,fij->ij',ff,P)
        out[:400,400:]=np.einsum('f,fij->ij',fw,P)@Q
        out[400:,:400]=Q.T@np.einsum('f,fij->ij',wf,P)
        out[400:,400:]=Q.T@np.einsum('f,fij->ij',sw,P)@Q
        return out
    value=(H[:,0],H[:,1]); radial=(Hr[:,0],Hr[:,1])
    mass=block(1,1,value,value)
    mixed=block(0,1,value,value)+block(2,1,radial,value)
    stiffness=(block(0,0,value,value)+block(0,2,value,radial)
        +block(2,0,radial,value)+block(2,2,radial,radial))
    return mass,mixed,(stiffness+stiffness.T)/2


def _gauge_row_polynomials(poly,operators):
    """Actual gradient-row maps, not a zero Ward surrogate."""
    maps=[operators['radial_selector'].T,
        operators['spatial_selector'].T@operators['G0'],
        operators['spatial_selector'].T@operators['G1'],operators['temporal_selector'].T]
    return np.array([np.einsum('ac,fijab->fijcb',L,poly,optimize=True) for L in maps])


def _gauge_weak_rows(gpoly,factors,coefficients,w,H,Hr,rho,Q):
    """Full D_A eta weak row, including eta_dot's At and all second jets."""
    phi,lift=H.T;phir,liftr=Hr.T
    x=rho/WALL;normalization=phi/(x**ALPHA*(1-x))
    phirr=normalization/WALL**2*(ALPHA*(ALPHA-1)*x**(ALPHA-2)*(1-x)-2*ALPHA*x**(ALPHA-1))
    h=coefficients[:,5]-1;lt=coefficients[:,6];lr=coefficients[:,7]
    left0=[(0,0,phir),(0,1,phi),(0,2,phi*h),(1,2,phi*lt),
        (2,0,phirr),(2,1,phir),(2,2,phir*h+phi*lr)]
    left1=[(0,3,phi),(1,0,phir),(1,1,phi),(1,2,phi*h),(2,3,phir)]
    def integrate(left,right_derivatives):
        out=np.zeros((80,408))
        for i,L,profile in left:
            for j,interior,wall in right_derivatives:
                fi=np.sum((w*profile*interior)[:,None]*factors,axis=0)
                fw=np.sum((w*profile*wall)[:,None]*factors,axis=0)
                out[:,:400]+=np.einsum('f,fab->ab',fi,gpoly[L,:,i,j])
                out[:,400:]+=np.einsum('f,fab->ab',fw,gpoly[L,:,i,j])@Q
        return out
    position=[(0,phi,lift),(2,phir,liftr)];velocity=[(1,phi,lift)]
    return [integrate(left,right) for left in (left0,left1) for right in (position,velocity)]


def full_reference_retarded_form(repository=ROOT,*,duration=.001,final_time=.003,
                                 time_nodes=17,radial_points=48):
    """Assemble all full400 angular rows on a fixed-trace finite radial core.

    The computational interval and radialorder1 are not physical lifetime,
    mode selection or continuum closure.  q(t)=q_E1+t*v_E1 is an initial
    iterate.  It retains the actual initial field jet and does not recover
    the physical nonlinear history.  All coefficient paths are sampled from
    that SAME vector; no independent frozen lambda_tau is inserted.
    """
    if (not np.isfinite([duration,final_time]).all() or duration<=0 or final_time<=duration
            or type(time_nodes) is not int or time_nodes<5 or type(radial_points) is not int or radial_points<12):
        raise ValueError('explicit positive resolved numerical interval and form quadrature required')
    angular=retained_full_q_angular_space(repository);op=full_q_reference_operators(angular)
    poly=hessian_response_polynomials(op,np.eye(400));Q=angular['source_coefficients']
    gpoly=_gauge_row_polynomials(poly,op)
    x,w=leggauss(radial_points);rho=(x+1)*WALL/2;w=w*WALL/2
    H,Hr=regular_radial_basis(rho,1);times=np.linspace(0,final_time,time_nodes)
    q,v,m=retained_state(repository); forms=[]; raw=[];values=[];gauge_mass=[];gauge_rows=[]
    for t in times:
        c=geometric_connection_coefficient_jets(12,q+t*v,v,m,rho,clock='coordinate_time')
        fac=np.array([[z.value for z in geometric_response_factors(row)] for row in c['rows']])
        matrices=_time_forms(poly,fac,w,H,Hr,Q); raw.append(matrices)
        reduced=constrained_gauss_schur(*matrices,80);forms.append(reduced)
        values.append(np.array([[row[k].value for k in ('electric','radial','angular','electric_radial','shift','connection_lambda','lambda_tau','lambda_rho')] for row in c['rows']]))
        gauge_rows.append(_gauge_weak_rows(gpoly,fac,values[-1],w,H,Hr,rho,Q))
        # Genuine finite gauge-gradient completion, including radial eta'.
        G=np.zeros((radial_points,320,80))
        for j,row in enumerate(c['rows']):
            G[j,:80]=Hr[j,0]*np.eye(80)
            G[j,80:]=H[j,0]*(op['G0']+(row['connection_lambda'].value-1)*op['G1'])
        Gb=np.zeros((80,320)); GG=np.zeros((80,80))
        for j,row in enumerate(c['rows']):
            metric=np.repeat([row['electric_radial'].value]+[row['electric'].value]*3,80)
            Gb+=w[j]*H[j,0]*(G[j].T*metric)
            GG+=w[j]*(G[j].T*metric)@G[j]
        # With At=eta_dot the completed gradient's principal curvatures
        # vanish exactly.  Compare its mass to the actual Gauss elliptic row.
        gauge_mass.append(float(np.max(abs(GG-reduced['Gauss_matrix']))))
    result=dict(angular=angular,operators=op,rho=rho,quadrature=w,H=H,Hr=Hr,
        time_nodes=times,forms=forms,raw_forms=raw,coefficient_values=np.array(values),
        duration=duration,final_time=final_time,actual_geometry=dict(q=q,velocity=v,lapse_shift=m),
        gauge_gradient_mass_identity_max=max(gauge_mass),
        computational_gauge_slice='independent fixed radial field coefficients; add actual D_A eta gradient columns as complementary gauge coordinates and set those coordinates to zero',
        actual_gauge_gradient_columns=80,all_five_one_forms_retained=True,
        physical_gauge_quotient_closed=False,stationary_background=False)
    for index,key in enumerate(('raw_M','raw_B','raw_K')):
        result[key]=CubicSpline(times,np.array([f[index] for f in raw]),axis=0)
    result['gauge_weak_rows']=CubicSpline(times,np.array(gauge_rows),axis=0)
    result['coefficient_spline']=CubicSpline(times,result['coefficient_values'],axis=0)
    result['minimum_interior_mass_eigenvalue']=min(float(np.linalg.eigvalsh(f['M'][:320,:320])[0]) for f in forms)
    if result['minimum_interior_mass_eigenvalue']<=0:
        raise ArithmeticError('the declared finite gauge slice has no positive interior kinetic form')
    return result


def _reduced_at(form,t):
    # Interpolate the unreduced scalar action, then eliminate its literal
    # Gauss row.  Interpolating its Schur blocks independently would no
    # longer be a single same-action system between coefficient nodes.
    return constrained_gauss_schur(*(form[k](t) for k in ('raw_M','raw_B','raw_K')),80)


def _hamilton_rhs(form,t,y):
    state=np.asarray(y).reshape(640,8);x,p=state[:320],state[320:]
    current=_reduced_at(form,t);M,B,K=(current[k] for k in ('M','B','K'))
    g,gd,_=compact_trace_pulse(t,form['duration'])
    solve=lambda b:cho_solve(cho_factor(M[:320,:320]),b)
    velocity=solve(p-B[:320,:320].T@x-g*B[320:,:320].T-gd*M[:320,320:])
    force=B[:320,:320]@velocity+g* K[:320,320:]+gd*B[:320,320:]+K[:320,:320]@x
    return np.concatenate((velocity,force)).ravel()


def _mean_bracket_sources(spatial,scalar_profile):
    """Exact Haar mean [u_i,eta] for every80 real harmonic gauge parameter."""
    u=np.asarray(spatial).reshape(3,4,20,8).transpose(3,0,1,2)
    mean=np.zeros((8,80,3,4));eps=epsilon()
    for c in range(3):
        for x in range(3):
            for y in range(3):
                mean[:,y*20:(y+1)*20,:,c]+=scalar_profile*eps[x,y,c]*u[:,:,x,:].transpose(0,2,1)/np.sqrt(2)
    return mean


def retarded_gauge_euler_reaction(form,time,state,velocity):
    """Consume the off-shell Ward identity; compact eta has no endpoint term.

    This retained reaction, not an artificial zero, diagnoses the Euler
    contact left by the constrained finite reference application.  It is
    not a completed physical gauge-quotient or stationary-base certificate.
    """
    g,gd,_=compact_trace_pulse(time,form['duration']);Q=form['angular']['source_coefficients']
    z=np.vstack((state[:320],g*np.eye(8)));zd=np.vstack((velocity,gd*np.eye(8)))
    coeff=form['coefficient_spline'](time);reaction=np.zeros((80,8))
    for j,(row,w) in enumerate(zip(coeff,form['quadrature'])):
        e,r,d,k,beta,lam,lt,lr=row;h=lam-1;n=lt-beta*lr
        hi,hl=form['H'][j];di,dl=form['Hr'][j]
        ui=hi*z[80:320]+hl*g*Q[160:]
        uit=hi*zd[80:320]+hl*gd*Q[160:]
        uir=di*z[80:320]+dl*g*Q[160:]
        W=_mean_bracket_sources(ui,hi*g)
        Wt=_mean_bracket_sources(uit,hi*g)+_mean_bracket_sources(ui,hi*gd)
        Wr=_mean_bracket_sources(uir,hi*g)+_mean_bracket_sources(ui,di*g)
        curl=2*W.copy();eps=epsilon()
        for a,b,c in np.argwhere(eps):
            curl[:,:,a,:3]+=eps[a,b,c]*h*np.cross(MECHANICAL_M[b,:3],W[:,:,c,:3])/np.sqrt(2)
        contact=e*n*np.einsum('ic,abic->ab',MECHANICAL_M,Wt-beta*Wr)
        contact-=r*lr*np.einsum('ic,abic->ab',MECHANICAL_M,Wr)
        contact-=d*np.einsum('ic,abic->ab',2*lam*h*MECHANICAL_M,curl)
        reaction-=w*contact.T
    return reaction


def retarded_full_q_application(form,*,time_steps=128,rtol=2e-9,atol=2e-11):
    """Apply eight actual angular traces to the full finite retarded operator."""
    T,D=form['final_time'],form['duration']
    if type(time_steps) is not int or time_steps<16:
        raise ValueError('resolved retarded computational time grid required')
    sol=solve_ivp(lambda t,y:_hamilton_rhs(form,t,y),(0,T),np.zeros(640*8),method='DOP853',
        rtol=rtol,atol=atol,max_step=D/time_steps,dense_output=True)
    if not sol.success:raise ArithmeticError('full constrained retarded application failed: '+sol.message)
    times=np.linspace(0,T,3*time_steps+1);states=sol.sol(times).T.reshape(-1,640,8)
    velocities=np.array([_hamilton_rhs(form,t,s.ravel()).reshape(640,8)[:320] for t,s in zip(times,states)])
    gauss=[];At=[];reactions=[];native_contacts=[];wall=[];bilinear=[];gauss_relative=[]
    for t,s,xd in zip(times,states,velocities):
        g,gd,_=compact_trace_pulse(t,D);z=np.vstack((s[:320],g*np.eye(8)));zd=np.vstack((xd,gd*np.eye(8)))
        current=_reduced_at(form,t)
        y=current['At_value_map']@z+current['At_velocity_map']@zd;At.append(y)
        parts=(current['Gauss_matrix']@y,current['Gauss_value_row']@z,current['Gauss_velocity_row']@zd)
        gauss.append(sum(parts));gauss_relative.append(float(np.max(abs(sum(parts)))/(1+sum(np.max(abs(a)) for a in parts))))
        full_z=np.vstack((y,z));full_velocity=np.vstack((np.zeros_like(y),zd))
        G0z,G0v,G1z,G1v=form['gauge_weak_rows'](t)
        reactions.append(g*(G0z@full_z+G0v@full_velocity)+gd*(G1z@full_z+G1v@full_velocity))
        native_contacts.append(retarded_gauge_euler_reaction(form,t,s,xd))
        mass,mixed,stiffness=(current[k] for k in ('M','B','K'))
        momentum=mass@zd+mixed.T@z
        wall.append(-gd*momentum[320:]-g*(mixed[320:]@zd+stiffness[320:]@z))
        bilinear.append(zd.T@mass@zd+z.T@mixed@zd+zd.T@mixed.T@z+z.T@stiffness@z)
    # Symplectic first-order action provides a direct forward/advanced
    # contraction test without a guessed Pauli tensor or boundary adjoint.
    Q=form['angular']['source_coefficients'][160:]
    H,_=regular_radial_basis(np.array([.75*WALL]),1)
    readout=np.zeros((8,640));readout[:,80:320]=H[0,0]*Q.T
    def adjoint_rhs(t,z):
        z=z.reshape(640,8);current=_reduced_at(form,t);M,B,K=(current[k] for k in ('M','B','K'))
        Mi=cho_factor(M[:320,:320]);Bi=B[:320,:320];Ki=K[:320,:320]
        # A^T(zx,zp)=(-B Mi zx+(K-B Mi B^T)^T zp, Mi zx+Mi B^T zp).
        v=cho_solve(Mi,z[:320]+Bi.T@z[320:])
        return np.concatenate((Bi@v-Ki.T@z[320:],-v)).ravel()
    adj=solve_ivp(adjoint_rhs,(T,0),readout.T.ravel(),method='DOP853',rtol=rtol,atol=atol,
        max_step=D/time_steps,dense_output=True)
    if not adj.success:raise ArithmeticError('full constrained advanced adjoint failed')
    az=adj.sol(times).T.reshape(-1,640,8);integrand=[]
    for t,z in zip(times,az):
        zero=_hamilton_rhs(form,t,np.zeros(640*8)).reshape(640,8)
        integrand.append(z.T@zero)
    contraction=simpson(np.array(integrand),x=times,axis=0);output=readout@states[-1]
    wall_pairing=simpson(np.array(wall),x=times,axis=0)
    endpoint=states[-1,:320].T@states[-1,320:]-states[0,:320].T@states[0,320:]
    action_boundary=endpoint-simpson(np.array(bilinear),x=times,axis=0)
    return dict(times=times,state=states,velocity=velocities,A_tau=np.array(At),
        Gauss_residual=np.array(gauss),gauge_Euler_reaction_integrand=np.array(reactions),
        paired_gauge_Euler_reaction=simpson(np.array(reactions),x=times,axis=0),
        native_Ward_Euler_contact_estimate=simpson(np.array(native_contacts),x=times,axis=0),
        finite_row_native_Ward_contact_maximum_difference=float(np.max(abs(simpson(np.array(reactions)-np.array(native_contacts),x=times,axis=0)))),
        wall_trace_reaction_pairing=wall_pairing,action_temporal_endpoint=endpoint,
        action_boundary_pairing=action_boundary,
        action_boundary_maximum_defect=float(np.max(abs(wall_pairing-action_boundary))),
        action_boundary_relative_defect=float(np.max(abs(wall_pairing-action_boundary))/(1+np.max(abs(wall_pairing)))),
        advanced_adjoint=az,adjoint_output=output,adjoint_source_pairing=contraction,
        adjoint_pairing_maximum_defect=float(np.max(abs(output-contraction))),
        Gauss_residual_maximum=float(np.max(abs(np.array(gauss)))),
        Gauss_residual_maximum_relative=max(gauss_relative),
        numerical_integrator=dict(method='DOP853',rtol=rtol,atol=atol,evaluations=sol.nfev),
        source_scope='CONTROL_ONLY compact walltrace; actual8 angular Q directions; no physical interval/source profile selected',
        retarded_initial_data='zero perturbation field and canonical momentum before source support',
        stationary_background=False,physical_gauge_quotient_closed=False,native_heat_evaluated=False,physical_Pauli_form=None)


def materialize(output,repository=ROOT):
    output=Path(output)
    if output.exists():raise FileExistsError('preserve evidence; use a new output directory')
    form=full_reference_retarded_form(repository);response=retarded_full_q_application(form)
    arrays={k:v for k,v in response.items() if isinstance(v,np.ndarray)}
    arrays.update(form['actual_geometry']);arrays.update(rho=form['rho'],radial_quadrature=form['quadrature'],
        coefficient_times=form['time_nodes'],coefficient_values=form['coefficient_values'],source_Gram=form['angular']['source_gram'])
    output.mkdir(parents=True)
    with ZipFile(output/'application.npz','w',compression=ZIP_DEFLATED,compresslevel=9) as archive:
        for name,value in sorted(arrays.items()):
            stream=BytesIO();np.lib.format.write_array(stream,np.asarray(value),allow_pickle=False)
            member=ZipInfo(name+'.npy',date_time=(1980,1,1,0,0,0));member.external_attr=0o600<<16;member.compress_type=ZIP_DEFLATED
            archive.writestr(member,stream.getvalue(),compresslevel=9)
    refs=[SOURCE,STATE_SOURCE,RESET_RECEIPT,
        'src/bhsm/interface/muon_parent_maxwell_full_retarded.py',
        'src/bhsm/interface/muon_parent_maxwell_full_q_application.py',
        'src/bhsm/interface/muon_parent_maxwell_geometry_weak.py',
        'src/bhsm/interface/muon_parent_maxwell_full_weak.py',
        'src/bhsm/interface/muon_parent_retarded_hypercharge.py']
    receipt={k:v for k,v in response.items() if not isinstance(v,np.ndarray)}
    receipt.update(scope='EVALUATED_AFFINE_ACTUAL_E1_PLUS_REFERENCE_FULL5_CONSTRAINED_RETARDED_APPLICATION',
        input_hashes={p:sha256((Path(repository)/p).read_bytes()).hexdigest() for p in refs},
        application_sha256=sha256((output/'application.npz').read_bytes()).hexdigest(),
        gauge_Euler_reaction_norm=float(np.linalg.norm(response['paired_gauge_Euler_reaction'])),
        full_angular_space=400,At_Gauss_rows=80,spatial_interior_unknowns=320,
        actual_gauge_gradient_columns=form['actual_gauge_gradient_columns'],
        gauge_gradient_mass_identity_max=form['gauge_gradient_mass_identity_max'],
        minimum_interior_mass_eigenvalue=form['minimum_interior_mass_eigenvalue'],
        computational_gauge_slice=form['computational_gauge_slice'],
        radial_trial_order=1,radial_quadrature_count=48,time_coefficient_nodes=17,
        duration=form['duration'],final_time=form['final_time'],
        coefficient_policy='same affine q(t)=q_E1+t*v_E1, qdot=v_E1, m=m_E1; lambda and lambda_tau fromsameproducer',
        coefficient_interpolation='cubic spline of unreduced SAME-action scalar Hessian, then exact Gauss elimination at each evaluation; sampled actual coefficients; no interpolation enclosure',
        time_freeze_lambda_tau=False,background_is_initial_iterate=True,corrected_primal_inserted=False,
        pole_domain='finite-energy radial formcore; coexact positive exponent used as numerical coordinate, not all-channel indicial selection',
        wall_domain='given compact8Q spatial trace; At=Arwalltrace0 in this computational application; parent reaction not an interface closure',
        gauge_reaction_rule='actual interpolated SAME-action D_A eta weak rows including eta_dot At and Gdot/Gr; compact eta has zero endpoint trace. Native Ward Eulercontact evaluated independently as a sampled estimate.',
        error_scope='finite radial/time application; ODEtolerance plus sampled spline; no continuum, primal or native Pauli enclosure')
    (output/'result.json').write_text(json.dumps(receipt,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return receipt


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();print(json.dumps(materialize(args.output),sort_keys=True))
