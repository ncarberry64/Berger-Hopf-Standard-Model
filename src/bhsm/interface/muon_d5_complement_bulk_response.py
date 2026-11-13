"""Original full-carrier D5 on a finite incoming collar strip.

This is a finite, non-null bulk solution FAMILY.  The inner strip face,
time faces, physical normal normalization and event transmission remain
coupled unknowns.  No particular solution is promoted to a physical state.
The two eta signs here belong to the same incoming history.
"""
from __future__ import annotations

import numpy as np
from numpy.polynomial import Polynomial
from numpy.polynomial.legendre import leggauss
from scipy.linalg import lu_factor, lu_solve

from .muon_adopted_incoming_reference import static_field_maps
from .muon_combined_f_eta_contact import combined_f_eta_contact
from .muon_full_d5_differential_form import full_d5_differential_coefficients
from .muon_full_d5_source_first import full_d5_differential_source_first
from .muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace
from .muon_holomorphic_d5_trace_action import d5_trial_stage_coefficients
from .muon_formed_event_domain_application import endpoint_seam_numerator
from .muon_parent_retarded_hypercharge import WALL


def nodal_derivative(nodes):
    """Derivative of the declared polynomial, with stable scaled nodes."""
    x = np.asarray(nodes, float)
    if x.ndim != 1 or len(x) < 2 or not np.isfinite(x).all() or np.any(np.diff(x) <= 0):
        raise ValueError('ordered distinct finite nodes required')
    z = (x-x[0])/(x[-1]-x[0])
    weights = np.array([1/np.prod(z[j]-np.delete(z,j)) for j in range(len(z))])
    D = np.zeros((len(z),len(z)))
    for i in range(len(z)):
        for j in range(len(z)):
            if i != j:
                D[i,j] = weights[j]/weights[i]/(z[i]-z[j])
        D[i,i] = -np.sum(D[i])
    return D/(x[-1]-x[0])


def _collocation_rule(order):
    if type(order) is not int or order < 2 or order > 5:
        raise ValueError('bounded radial Gauss order2 through5 required')
    nodes = (leggauss(order)[0]+1)/2
    polynomials = []
    for j in range(order):
        p = Polynomial([1.])
        for k in range(order):
            if k != j:
                p *= Polynomial([-nodes[k],1])/(nodes[j]-nodes[k])
        polynomials.append(p)
    antiderivatives = [p.integ() for p in polynomials]
    integral = lambda theta: np.array([p(theta)-p(0) for p in antiderivatives])
    A = np.array([integral(theta) for theta in nodes])
    return nodes, polynomials, integral, A


def _generator(time, radial, body, time_first, radial_first, body_first, D):
    """Original R Psi_r + T D_t Psi + K Psi=0, including R source."""
    n,d = len(D),len(time[0])
    G = np.zeros((n,d,n,d),complex)
    Gx = np.zeros_like(G)
    for i in range(n):
        A = -np.linalg.solve(radial[i],time[i])
        B = -np.linalg.solve(radial[i],body[i])
        for j in range(n):
            G[i,:,j,:] = A*D[i,j]
        G[i,:,i,:] += B
        for j in range(n):
            contact = time_first[i]*D[i,j] + radial_first[i]@G[i,:,j,:]
            if i == j:
                contact += body_first[i]
            Gx[i,:,j,:] = -np.linalg.solve(radial[i],contact)
    return G.reshape(n*d,n*d),Gx.reshape(n*d,n*d)


def _linear_collocation(generators, source_generators, initial, initial_source, h, A):
    """Solve every original stage, retaining a source solve with the same LU."""
    q,d = len(A),len(initial)
    block = np.zeros((q,d,q,d),complex)
    for i in range(q):
        for j in range(q):
            block[i,:,j,:] = -h*A[i,j]*generators[j]
        block[i,:,i,:] += np.eye(d)
    matrix = block.reshape(q*d,q*d)
    lu = lu_factor(matrix)
    rhs = np.broadcast_to(initial,(q,d,d)).astype(complex,copy=True)
    stage = lu_solve(lu,rhs.reshape(q*d,d)).reshape(q,d,d)
    source_rhs = np.broadcast_to(initial_source,(q,d,d)).astype(complex,copy=True)
    source_rhs += h*np.einsum('ij,jab,jbc->iac',A,source_generators,stage)
    stage_source = lu_solve(lu,source_rhs.reshape(q*d,d)).reshape(q,d,d)
    slopes = np.einsum('iab,ibc->iac',generators,stage)
    slopes_source = np.einsum('iab,ibc->iac',source_generators,stage)
    slopes_source += np.einsum('iab,ibc->iac',generators,stage_source)
    residual = matrix@stage.reshape(q*d,d)-rhs.reshape(q*d,d)
    source_residual = matrix@stage_source.reshape(q*d,d)-source_rhs.reshape(q*d,d)
    return stage,stage_source,slopes,slopes_source,float(np.max(abs(residual))),float(np.max(abs(source_residual)))


def _endpoint_from_cache(cache, raw, rate, full):
    """Reuse evaluated E1 coefficients; reconstruct only exact fixed frame maps."""
    if cache is None:
        raise ValueError('completed e02747f2 incoming endpoint cache required')
    if not np.array_equal(cache['incoming_raw268'],raw) or not np.array_equal(cache['incoming_raw_coordinate_time_derivative268'],rate):
        raise ValueError('cached E1 branch/background/rate identity mismatch')
    out = {}
    for key in ('Ehat','Bhat'):
        out[key] = (np.asarray(cache['incoming_'+key]),np.asarray(cache['incoming_'+key+'_coordinate_time']))
    for channel in ('LR','RL'):
        out[channel+'_image'] = (np.asarray(cache['incoming_'+channel+'_image']),
            np.asarray(cache['incoming_'+channel+'_image_coordinate_time']))
    spin = {}
    for side in ('plus','minus'):
        s = np.kron(np.eye(3),cache['incoming_'+side+'_spin_boost128'])
        sx = np.kron(np.eye(3),cache['incoming_'+side+'_spin_boost_coordinate_time128'])
        si = np.linalg.inv(s)
        spin[side] = (s,sx,si,-si@sx@si)
    p,m = spin['plus'],spin['minus']
    out['geometric_right'] = (m[0]@p[2],m[1]@p[2]+m[0]@p[3])
    out['plus_S'] = p[:2]
    return out


def _fresh_endpoint(raw, rate):
    a = endpoint_seam_numerator(raw,rate)
    return dict(Ehat=a['Ehat'],Bhat=a['Bhat'],
        LR_image=a['channels']['LR']['image'],RL_image=a['channels']['RL']['image'],
        geometric_right=a['geometric_right'],plus_S=a['frames']['plus']['S'])


def _wall_maps(endpoints, full):
    n = len(endpoints)
    W = full['localized_lepton18_trace_lift']
    unselected = np.flatnonzero(np.sum(abs(W),axis=1)==0)
    if len(unselected) != 366:
        raise ValueError('same full384/selected18 complement required')
    arrays = {}
    for label in ('plus_seed','minus_seed','minus_LR','minus_RL'):
        arrays[label] = np.zeros((n,384,18*n),complex)
        arrays[label+'_source'] = np.zeros_like(arrays[label])
    for label in ('plus','minus'):
        arrays['wall_'+label+'_complement_basis'] = np.zeros((n,384,366),complex)
        arrays['wall_'+label+'_complement_basis_source'] = np.zeros((n,384,366),complex)
    arrays['wall_selected_Bhat'] = np.array([e['Bhat'][0] for e in endpoints])
    arrays['wall_selected_Bhat_source'] = np.array([e['Bhat'][1] for e in endpoints])
    arrays['wall_geometric_right'] = np.array([e['geometric_right'][0] for e in endpoints])
    arrays['wall_geometric_right_source'] = np.array([e['geometric_right'][1] for e in endpoints])
    for j,e in enumerate(endpoints):
        E,Ex=e['Ehat'];U,Ux=e['geometric_right'];S,Sx=e['plus_S']
        sl=slice(18*j,18*(j+1))
        arrays['plus_seed'][j,:,sl]=E
        arrays['plus_seed_source'][j,:,sl]=Ex
        for label,image in (('minus_seed',(E,Ex)),('minus_LR',e['LR_image']),('minus_RL',e['RL_image'])):
            V,Vx=image
            arrays[label][j,:,sl]=U@V
            arrays[label+'_source'][j,:,sl]=Ux@V+U@Vx
        Q,Qx=S[:,unselected],Sx[:,unselected]
        arrays['wall_plus_complement_basis'][j]=Q
        arrays['wall_plus_complement_basis_source'][j]=Qx
        arrays['wall_minus_complement_basis'][j]=U@Q
        arrays['wall_minus_complement_basis_source'][j]=Ux@Q+U@Qx
    return arrays


def _extension_cutoff(rho,width):
    x=(WALL-np.asarray(rho))/width
    z=np.clip((x-.2)/.6,0,1)
    value=1-10*z**3+15*z**4-6*z**5
    derivative=(30*z*z-60*z**3+30*z**4)/(.6*width)
    derivative[(x<=.2)|(x>=.8)]=0.
    return value,derivative


def apply_fundamental_blocks(arrays, side, wall_value, wall_source=None):
    """Apply repeated full64 blocks to ANY full384 boundary data, including h."""
    value=np.asarray(wall_value,complex)
    if value.ndim!=3 or value.shape[:2]!=(len(arrays['times']),384):
        raise ValueError('all time nodes/full384 boundary field columns required')
    if wall_source is None:
        raise ValueError('explicit boundary coefficient source required; unknown source is not zero')
    source=np.asarray(wall_source,complex)
    if source.shape!=value.shape or not np.isfinite(value).all() or not np.isfinite(source).all():
        raise ValueError('same finite boundary coefficient source required')
    nr=len(arrays['radial_nodes']);n=len(arrays['times']);k=value.shape[-1]
    out={key:np.zeros((nr,n,384,k),complex) for key in ('value','radial','source','radial_source')}
    for family in range(3):
        for b,branch in enumerate(('particle','conjugate')):
            sl=slice((2*family+b)*64,(2*family+b+1)*64)
            prefix=side+'_'+branch+'_'
            v=value[:,sl].reshape(n*64,k);vx=source[:,sl].reshape(n*64,k)
            H,Hx,Hr,Hrx=(arrays[prefix+key] for key in (
                'fundamental','fundamental_source','fundamental_radial','fundamental_radial_source'))
            out['value'][:,:,sl]=np.einsum('rij,jk->rik',H,v).reshape(nr,n,64,k)
            out['radial'][:,:,sl]=np.einsum('rij,jk->rik',Hr,v).reshape(nr,n,64,k)
            out['source'][:,:,sl]=(np.einsum('rij,jk->rik',Hx,v)+np.einsum('rij,jk->rik',H,vx)).reshape(nr,n,64,k)
            out['radial_source'][:,:,sl]=(np.einsum('rij,jk->rik',Hrx,v)+np.einsum('rij,jk->rik',Hr,vx)).reshape(nr,n,64,k)
    D=arrays['time_derivative']
    out['time']=np.einsum('ij,rjdk->ridk',D,out['value'])
    out['time_source']=np.einsum('ij,rjdk->ridk',D,out['source'])
    return out


def solve_incoming_complement_bulk_family(times, raw_nodes, raw_rates, *, saved_endpoint,
        strip_fraction=.01, radial_steps=1, radial_order=3, include_field_maps=True):
    """Execute a provisional bulk Cauchy family with ALL outer data retained.

    Time is the six-node polynomial coefficient chart, not a stationary
    phase ansatz.  The common source direction moves every supplied raw
    node by its actual coordinate-rate germ; coefficient coordinates,
    time nodes and computational strip faces are fixed in this derivative.
    Physical domain/source derivatives and amplitude derivatives remain.
    """
    if not np.isrealobj(raw_nodes) or not np.isrealobj(raw_rates) or not np.isrealobj(times):
        raise ValueError('this application requires the actual real incoming coefficient chart')
    t=np.asarray(times,float);raw=np.asarray(raw_nodes,float);rates=np.asarray(raw_rates,float)
    D=nodal_derivative(t)
    if len(t)!=6 or raw.shape!=(6,268) or rates.shape!=raw.shape or not np.isfinite(raw).all() or not np.isfinite(rates).all() or t[-1]!=0:
        raise ValueError('actual incoming six-node raw268/rate268 history ending at E1 required')
    if not 0<strip_fraction<=.04 or type(radial_steps)is not int or not 1<=radial_steps<=8:
        raise ValueError('bounded explicit numerical strip fraction and radial steps required')
    full=full_d5_localized_lepton_trace()
    # A coefficient-derived numerical strip, never a selected physical end.
    p=static_field_maps(np.array([WALL]),enrich_temporal=False)[0]
    rep=dict(rho=np.array([WALL]),gauge_basis=p.reshape(1,20,80).transpose(0,2,1).reshape(1,80,1,5,4))
    speed=[]
    for x,xt in zip(raw,rates):
        c=d5_trial_stage_coefficients(x,xt[:,None],x,xt[:,None],np.array([x,x]),
            np.array([xt[:,None],xt[:,None]]),rep,np.array([WALL]),side='parent')
        if c['lapse'][0].real<=0 or c['radial_coframe'][0].real<=0 or max(abs(c['lapse'][0].imag),abs(c['radial_coframe'][0].imag))>1e-14:
            raise ValueError('actual positive real lapse/radial coframe required on this strip')
        speed.append(abs(c['lapse'][0]/c['radial_coframe'][0]))
    width=float(strip_fraction*(t[-1]-t[0])*min(speed))
    cn,polys,integral,A=_collocation_rule(radial_order)
    boundaries=np.linspace(WALL,WALL-width,radial_steps+1)
    point_records=[]
    for step in range(radial_steps):
        lo,hi=boundaries[step:step+2];h=hi-lo
        for theta in sorted(set([0.,.5,1.,*cn])):
            if step and theta==0:continue
            point_records.append((step,float(theta),float(lo+h*theta),bool(np.min(abs(cn-theta))<1e-13)))
    rho=np.array([p[2] for p in point_records]);nr=len(rho)
    radial_basis=static_field_maps(rho,enrich_temporal=False)[0]
    rep=dict(rho=rho,gauge_basis=radial_basis.transpose(0,2,1).reshape(nr,80,1,5,4))
    coefficients={};firsts={}
    for side,eps in (('plus',1),('minus',-1)):
        records={k:[] for k in ('particle','conjugate')}
        for x,xt in zip(raw,rates):
            c=d5_trial_stage_coefficients(x,xt[:,None],x,xt[:,None],np.array([x,x]),
                np.array([xt[:,None],xt[:,None]]),rep,rho,side='parent')
            eta={};etax={}
            for branch in ('particle','conjugate'):
                e=combined_f_eta_contact(c,gamma=full['gamma5D_'+branch],carrier_count=16,
                    angular_count=1,sheet_orientation=eps)
                eta[branch]=e['combined_f_eta_contact'];etax[branch]=e['combined_f_eta_contact_first'][0]
            germ=full_d5_differential_source_first(c,np.zeros((3,1,1)),source_slot=0,
                sheet_orientation=eps,full_representation=full,eta_contacts=eta,eta_contacts_first=etax)
            for branch in records:records[branch].append((germ['value']['blocks'][branch],germ['first']['blocks'][branch]))
            if side=='plus':
                coefficients.setdefault('density',[]).append(c['volume_density'])
                firsts.setdefault('density',[]).append(c['volume_density_first'][0])
        for branch,rows in records.items():
            label=side+'_'+branch
            coefficients[label]={k:np.array([r[0][k] for r in rows]).transpose(1,0,2,3) for k in ('time','radial','body')}
            firsts[label]={k:np.array([r[1][k] for r in rows]).transpose(1,0,2,3) for k in ('time','radial','body')}
    arrays=dict(times=t,time_derivative=D,radial_nodes=rho,
        radial_node_is_collocation=np.array([p[3] for p in point_records]),
        radial_node_step=np.array([p[0] for p in point_records]),
        raw268_nodes=raw,raw_coordinate_rates268_nodes=rates,
        raw_temporal_polynomial_defect268=D@raw-rates,
        density=np.array(coefficients['density']).T,density_source=np.array(firsts['density']).T,
        computational_strip_width=np.array(width))
    solve_defects={};strong_defects={};inverse_defects={};radial_conditions={}
    for label in ('plus_particle','plus_conjugate','minus_particle','minus_conjugate'):
        c,cx=coefficients[label],firsts[label]
        singular=np.linalg.svd(c['radial'],compute_uv=False)
        radial_conditions[label]=dict(minimum_singular_value=float(np.min(singular)),
            maximum_condition_number=float(np.max(singular[...,0]/singular[...,-1])))
        for key in ('time','radial','body'):
            arrays[label+'_'+key+'64']=c[key]
            arrays[label+'_'+key+'_source64']=cx[key]
        G=[];Gx=[]
        for i in range(nr):
            g,gx=_generator(c['time'][i],c['radial'][i],c['body'][i],
                cx['time'][i],cx['radial'][i],cx['body'][i],D)
            G.append(g);Gx.append(gx)
        initial=np.eye(384,dtype=complex);initialx=np.zeros_like(initial)
        left=initial.copy();leftx=initialx.copy()
        outputs={k:[] for k in ('fundamental','fundamental_source','fundamental_radial',
            'fundamental_radial_source','analytic_inverse','analytic_inverse_source')}
        max_stage=max_stage_x=0.
        for step in range(radial_steps):
            indices=[i for i,p0 in enumerate(point_records) if p0[0]==step]
            ci=[next(i for i in indices if abs(point_records[i][1]-z)<1e-13) for z in cn]
            gs=np.array([G[i] for i in ci]);gxs=np.array([Gx[i] for i in ci]);h=boundaries[step+1]-boundaries[step]
            _,_,slopes,slopexs,a,b=_linear_collocation(gs,gxs,initial,initialx,h,A)
            _,_,lslopes,lslopexs,la,lb=_linear_collocation(-gs.transpose(0,2,1),
                -gxs.transpose(0,2,1),left.T,leftx.T,h,A)
            max_stage=max(max_stage,a,la);max_stage_x=max(max_stage_x,b,lb)
            for i in indices:
                theta=point_records[i][1];weights=integral(theta);derivative=np.array([p0(theta) for p0 in polys])
                hv=initial+h*np.einsum('i,ijk->jk',weights,slopes)
                hx=initialx+h*np.einsum('i,ijk->jk',weights,slopexs)
                hr=np.einsum('i,ijk->jk',derivative,slopes)
                hrx=np.einsum('i,ijk->jk',derivative,slopexs)
                lv=(left.T+h*np.einsum('i,ijk->jk',weights,lslopes)).T
                lx=(leftx.T+h*np.einsum('i,ijk->jk',weights,lslopexs)).T
                for key,value in zip(outputs,(hv,hx,hr,hrx,lv,lx)):outputs[key].append(value)
            initial=initial+h*np.einsum('i,ijk->jk',integral(1.),slopes)
            initialx=initialx+h*np.einsum('i,ijk->jk',integral(1.),slopexs)
            left=(left.T+h*np.einsum('i,ijk->jk',integral(1.),lslopes)).T
            leftx=(leftx.T+h*np.einsum('i,ijk->jk',integral(1.),lslopexs)).T
        for key,value in outputs.items():arrays[label+'_'+key]=np.array(value)
        H,Hx,Hr,Hrx=(arrays[label+'_'+key].reshape(nr,6,64,384) for key in (
            'fundamental','fundamental_source','fundamental_radial','fundamental_radial_source'))
        Ht=np.einsum('ij,rjdk->ridk',D,H);Htx=np.einsum('ij,rjdk->ridk',D,Hx)
        strong=np.einsum('rtij,rtjk->rtik',c['radial'],Hr)+np.einsum('rtij,rtjk->rtik',c['time'],Ht)+np.einsum('rtij,rtjk->rtik',c['body'],H)
        strongx=np.einsum('rtij,rtjk->rtik',cx['radial'],Hr)+np.einsum('rtij,rtjk->rtik',cx['time'],Ht)+np.einsum('rtij,rtjk->rtik',cx['body'],H)
        strongx+=np.einsum('rtij,rtjk->rtik',c['radial'],Hrx)+np.einsum('rtij,rtjk->rtik',c['time'],Htx)+np.einsum('rtij,rtjk->rtik',c['body'],Hx)
        arrays[label+'_original_strong_rows']=strong
        arrays[label+'_original_strong_source_rows']=strongx
        coll=arrays['radial_node_is_collocation']
        strong_defects[label]=dict(collocation=float(np.max(abs(strong[coll]))),
            offnode=float(np.max(abs(strong[~coll]))),source_collocation=float(np.max(abs(strongx[coll]))),source_offnode=float(np.max(abs(strongx[~coll]))))
        L=arrays[label+'_analytic_inverse'];Lx=arrays[label+'_analytic_inverse_source'];HH=arrays[label+'_fundamental'];HHx=arrays[label+'_fundamental_source']
        inverse_defects[label]=dict(value=float(np.max(abs(L@HH-np.eye(384)))),
            source=float(np.max(abs(Lx@HH+L@HHx))))
        solve_defects[label]=dict(value=max_stage,source=max_stage_x)
    endpoints=[_fresh_endpoint(x,xt) for x,xt in zip(raw[:-1],rates[:-1])]
    endpoints.append(_endpoint_from_cache(saved_endpoint,raw[-1],rates[-1],full))
    wall=_wall_maps(endpoints,full)
    for key,value in wall.items():
        if key.startswith('wall_'):arrays[key]=value
    # This finite time chart does not silently replace the actual one-sided
    # preparation/frame jets with the derivative of a six-node polynomial.
    wall_time=np.einsum('ij,jdk->idk',D,wall['plus_seed'])
    product_time=wall['plus_seed_source'].copy()
    for i,e in enumerate(endpoints):
        for j in range(6):
            product_time[i,:,18*j:18*(j+1)] += e['Ehat'][0]*D[i,j]
    arrays['wall_seed_time_product_rule_defect']=wall_time-product_time
    zeta,zetar=_extension_cutoff(rho,width)
    arrays['extension_cutoff']=zeta;arrays['extension_cutoff_radial']=zetar
    nonnull={}
    if include_field_maps:
        for label in ('plus_seed','minus_seed','minus_LR','minus_RL'):
            side=label.split('_')[0]
            app=apply_fundamental_blocks(arrays,side,wall[label],wall[label+'_source'])
            for key,value in app.items():arrays[label+'_'+key]=value
            # The arbitrary smooth collar extension is a numerical right-inverse.
            # Its amplitude coordinates retain physical u_R at the wall.
            E=wall[label] if label.endswith('seed') else np.zeros_like(wall[label])
            Ex=wall[label+'_source'] if label.endswith('seed') else np.zeros_like(wall[label])
            Et=np.einsum('ij,jdk->idk',D,E);Etx=np.einsum('ij,jdk->idk',D,Ex)
            for key,extension in (
                    ('value',zeta[:,None,None,None]*E),('radial',zetar[:,None,None,None]*E),
                    ('time',zeta[:,None,None,None]*Et),('source',zeta[:,None,None,None]*Ex),
                    ('radial_source',zetar[:,None,None,None]*Ex),('time_source',zeta[:,None,None,None]*Etx)):
                arrays[label+'_chi_'+key]=app[key]-extension
            nonnull[label]=dict(inner_field_norm=float(np.linalg.norm(app['value'][-1])),
                inner_complement_norm=float(np.linalg.norm(arrays[label+'_chi_value'][-1])),
                source_norm=float(np.linalg.norm(app['source'][-1])))
    report=dict(classification='PROVISIONAL_ORIGINAL_D5_FINITE_INCOMING_BULK_SOLUTION_FAMILY',
        carrier='all3families,particle/conjugateSpin4xSM16; noHiggsbulkmass',angular_scope='constantS3angularcoefficient;n0explicittruncation',
        gauge_scope='retained actual SU2/U1 four-channel connection; lepton particular images are SU3 singlets; additional strong-gauge action on colored homogeneous coordinates is not evaluated or assigned zero',
        time_scope='six-node degree5 polynomial in actual coordinate time; D_t retained',
        radial_method='Gauss collocation polynomial; independently differentiated polynomial in original D5 rows',
        radial_order=radial_order,radial_steps=radial_steps,strip_fraction=float(strip_fraction),strip_width=width,
        stage_solve_residuals=solve_defects,original_strong_residuals=strong_defects,independent_analytic_inverse_residuals=inverse_defects,
        original_radial_principal_invertibility=radial_conditions,
        raw_time_polynomial_germ_mismatch_max=float(np.max(abs(arrays['raw_temporal_polynomial_defect268']))),
        wall_seed_time_product_rule_mismatch_max=float(np.max(abs(arrays['wall_seed_time_product_rule_defect']))),
        nonnull_particular_bulk_images=nonnull,endpoint_cache_reused=True,
        source_direction='common actual raw_coordinate_rate268 at6nodes; fixed numerical time/radial chart; amplitude derivatives independent',
        physical_amplitude_relations='a_R=(u_R,+P_L+u_R,-P_R)g; a_LR=g/u_L,+; a_RL=g/u_L,-',
        homogeneous_boundary_unknown_shape=[6,366],homogeneous_complement_assigned=False,
        normal_profile_normalization_residual=None,physical_outer_residual=None,physical_event_residual=None,
        physical_formation_residual=None,physical_admission=False,
        error_scope='finite operator arithmetic and radial polynomial residuals only; n0/time truncation, physical outer/event sewing, independent normal profiles/integrals, full source/domain derivatives and physical state remain unbounded',
        local_Maxwell_Higgs_removed_again=False,Higgs_seam_added_as_bulk_mass=False)
    return arrays,report
