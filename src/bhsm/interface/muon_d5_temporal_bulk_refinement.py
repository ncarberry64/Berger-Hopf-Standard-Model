"""Consistent-history, factorized temporal refinement of the original D5 strip.

The physical outer/formation data remain independent unknowns.  This module
changes a numerical representation, not the incoming prescription, the normal
profiles, the 384 carrier, or the action.  Every connected carrier block and
every homogeneous wall coordinate is retained.  The saved six amplitude
coordinates are embedded in the refined temporal space rather than refitted.
"""
from __future__ import annotations

import numpy as np
from numpy.polynomial.chebyshev import chebvander, chebder, chebval
from scipy.linalg import lu_factor, lu_solve
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components

from .muon_sigma_normal_collar_transport import CanonicalC1History
from .muon_birth_trace_enriched_action import generic_coordinate_lift
from .muon_parent_gauge_geometry_correction import correction_representation
from .muon_d5_complement_bulk_response import (
    _collocation_rule, _generator, _endpoint_from_cache, _fresh_endpoint,
    _wall_maps, _extension_cutoff, nodal_derivative,
)
from .muon_adopted_incoming_reference import static_field_maps
from .muon_combined_f_eta_contact import combined_f_eta_contact
from .muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace
from .muon_full_d5_source_first import full_d5_differential_source_first
from .muon_holomorphic_d5_trace_action import d5_trial_stage_coefficients
from .muon_parent_retarded_hypercharge import WALL


def time_evaluation_matrix(nodes, points, order=0):
    """Evaluate the declared polynomial and its derivative off the nodes."""
    t=np.asarray(nodes,float);p=np.atleast_1d(np.asarray(points))
    if t.ndim!=1 or len(t)<2 or np.any(np.diff(t)<=0) or order not in (0,1):
        raise ValueError('ordered time nodes and derivative order0/1 required')
    if not np.isfinite(t).all() or not np.isfinite(p).all():
        raise ValueError('finite time chart required')
    if np.any(p.real<t[0]-1e-20) or np.any(p.real>t[-1]+1e-20):
        raise ValueError('temporal extrapolation is not a supplied domain')
    z=2*(t-t[0])/(t[-1]-t[0])-1
    coeff=np.linalg.solve(chebvander(z,len(t)-1),np.eye(len(t)))
    if order:coeff=chebder(coeff,axis=0)*2/(t[-1]-t[0])
    zp=2*(p-t[0])/(t[-1]-t[0])-1
    return chebval(zp,coeff).T


class RefinedCanonicalHistory:
    """C1 position/velocity history and a separately named legacy source Xi.

    Xi is the old six-node raw-rate interpolation, so comparisons of source
    applications retain their original direction.  It is not assumed to be
    the tangent of a new constrained background solution.  ``value`` supplies
    the position Hermite derivative as its own velocity and acceleration.
    """
    def __init__(self,times,raw,raw_rates,coordinates=None):
        self.times=np.asarray(times,float)
        self.raw=np.asarray(raw,float);self.rates=np.asarray(raw_rates,float)
        if coordinates is None:
            rep=correction_representation(radial_points=4,radial_order=3,
                cap_points=4,include_wall_lift=True,include_scalar_mean=True)
            coordinates=generic_coordinate_lift(rep['gauge_labels'])
        self.coordinates=coordinates
        self.canonical=CanonicalC1History(self.times,self.raw,self.rates,coordinates)
        self.P=np.asarray(coordinates['lift']);self.n=int(coordinates['x_count'])
        discarded=self.raw-self.raw@self.P@self.P.T
        discarded_rates=self.rates-self.rates@self.P@self.P.T
        if max(np.max(abs(discarded)),np.max(abs(discarded_rates)))>1e-14:
            raise ValueError('raw history contains coordinates absent from the declared canonical chart')

    def value(self,t,cell=None):
        return self.canonical.value(t,cell)

    def source(self,t):
        p=complex(t)
        a=time_evaluation_matrix(self.times,[p])[0]@self.rates
        at=time_evaluation_matrix(self.times,[p],1)[0]@self.rates
        return a.astype(complex),at.astype(complex)

    def diagnostics(self):
        values=np.array([self.value(t)[0] for t in self.times])
        rates=np.array([self.value(t)[1] for t in self.times])
        probes=(self.times[:-1]+self.times[1:])/2
        tangent=[]
        for t in probes:
            a,at=self.source(t);a=a@self.P;at=at@self.P
            tangent.append(at[:self.n]-a[self.n:2*self.n])
        return dict(canonical_node_value_change_max=float(np.max(abs(values-self.raw))),
            canonical_node_rate_change_max=float(np.max(abs(rates-self.rates))),
            original_D_raw_minus_rate_max=float(np.max(abs(nodal_derivative(self.times)@self.raw-self.rates))),
            legacy_source_kinematic_tangent_defect_max=float(np.max(abs(np.asarray(tangent)))),
            source_scope='legacy Xi=degree5 interpolation of supplied raw-rate germs; fixed numerical faces; not a complete constrained physical derivative')


def coefficient_rows(history,times,radii):
    """Original coefficient callbacks at every requested independent point.

    The firsts are in Xi, not a replacement of coordinate-time derivatives.
    No coefficient polynomial or radial interpolation is used here.
    """
    t=np.asarray(times,float);r=np.asarray(radii,float)
    if t.ndim!=1 or r.ndim!=1 or not len(t) or not len(r):
        raise ValueError('nonempty independent time and radial axes required')
    full=full_d5_localized_lepton_trace()
    if hasattr(history,'gauge_basis'):
        basis=np.asarray(history.gauge_basis(r))
        if basis.shape==(len(r),20,80):
            basis=basis.transpose(0,2,1).reshape(len(r),80,1,5,4)
        if basis.shape!=(len(r),80,1,5,4):raise ValueError('original full80 radial coefficient lift required')
        rep=dict(rho=r,gauge_basis=basis)
    else:
        basis=static_field_maps(r,enrich_temporal=False)[0]
        rep=dict(rho=r,gauge_basis=basis.transpose(0,2,1).reshape(len(r),80,1,5,4))
    records={label:[] for label in ('plus_particle','plus_conjugate','minus_particle','minus_conjugate')}
    density=[];densityx=[]
    for time in t:
        x,rate=history.value(time);xi,_=history.source(time)
        c=d5_trial_stage_coefficients(x,xi[:,None],x,xi[:,None],np.array([x,x]),
            np.array([xi[:,None],xi[:,None]]),rep,r,side='parent')
        density.append(c['volume_density']);densityx.append(c['volume_density_first'][0])
        for side,eps in (('plus',1),('minus',-1)):
            eta={};etax={}
            for branch in ('particle','conjugate'):
                e=combined_f_eta_contact(c,gamma=full['gamma5D_'+branch],carrier_count=16,
                    angular_count=1,sheet_orientation=eps)
                eta[branch]=e['combined_f_eta_contact'];etax[branch]=e['combined_f_eta_contact_first'][0]
            germ=full_d5_differential_source_first(c,np.zeros((3,1,1)),source_slot=0,
                sheet_orientation=eps,full_representation=full,eta_contacts=eta,eta_contacts_first=etax)
            for branch in ('particle','conjugate'):
                records[side+'_'+branch].append((germ['value']['blocks'][branch],germ['first']['blocks'][branch]))
    result={}
    for label,rows in records.items():
        result[label]={}
        for k in ('time','radial','body'):
            result[label][k]=np.array([row[0][k] for row in rows]).transpose(1,0,2,3)
            result[label][k+'_source']=np.array([row[1][k] for row in rows]).transpose(1,0,2,3)
    return result,np.array(density).T,np.array(densityx).T


def carrier_components(coefficient):
    """Exact sparsity components of all values/firsts, without thresholding."""
    adjacent=np.zeros((64,64),bool)
    for value in coefficient.values():
        a=np.asarray(value)
        if a.shape[-2:]!=(64,64):raise ValueError('full original64 carrier coefficient required')
        adjacent|=np.any(a!=0,axis=tuple(range(a.ndim-2)))
    count,labels=connected_components(csr_matrix(adjacent|adjacent.T),directed=False)
    components=[np.flatnonzero(labels==i) for i in range(count)]
    if not np.array_equal(np.sort(np.concatenate(components)),np.arange(64)):
        raise ValueError('carrier reduction omitted an original coordinate')
    return components


def component_offblock_max(coefficient,components):
    mask=np.ones((64,64),bool)
    for indices in components:mask[np.ix_(indices,indices)]=False
    return max(float(np.max(abs(v[...,mask]))) if np.any(mask) else 0. for v in coefficient.values())


def _rectangular_collocation(gs,gxs,initial,initialx,h,A,stage_initializer=None,source_initializer=None):
    """Original Gauss stage equations for arbitrary field columns."""
    q,d=len(A),len(initial);k=initial.shape[1]
    block=-h*np.einsum('ij,jab->iajb',A,gs)
    for i in range(q):block[i,:,i,:]+=np.eye(d)
    matrix=block.reshape(q*d,q*d);lu=lu_factor(matrix)
    rhs=np.broadcast_to(initial,(q,d,k)).copy()
    guess=np.zeros((q,d,k),complex) if stage_initializer is None else np.asarray(stage_initializer,complex)
    if guess.shape!=(q,d,k):raise ValueError('initializer must retain every stage and every solution column')
    before=rhs.reshape(q*d,k)-matrix@guess.reshape(q*d,k)
    correction=lu_solve(lu,before).reshape(q,d,k)
    stage=guess+correction
    rhsx=np.broadcast_to(initialx,(q,d,k)).copy()+h*np.einsum('ij,jab,jbc->iac',A,gxs,stage)
    guessx=np.zeros_like(guess) if source_initializer is None else np.asarray(source_initializer,complex)
    if guessx.shape!=guess.shape:raise ValueError('explicit same-shape source initializer required')
    beforex=rhsx.reshape(q*d,k)-matrix@guessx.reshape(q*d,k)
    correctionx=lu_solve(lu,beforex).reshape(q,d,k)
    sx=guessx+correctionx
    slope=np.einsum('iab,ibc->iac',gs,stage)
    slopex=np.einsum('iab,ibc->iac',gxs,stage)+np.einsum('iab,ibc->iac',gs,sx)
    return slope,slopex,float(np.max(abs(matrix@stage.reshape(q*d,k)-rhs.reshape(q*d,k)))),float(np.max(abs(matrix@sx.reshape(q*d,k)-rhsx.reshape(q*d,k)))),dict(
        initializer_residual=float(np.max(abs(before))),initializer_source_residual=float(np.max(abs(beforex))),
        correction_norm=float(np.linalg.norm(correction)),source_correction_norm=float(np.linalg.norm(correctionx)))


def _saved_factor_guess(saved,label,indices,newtimes,radii,inverse=False):
    """Prolong the completed six-node transfer; retain new high-time columns.

    The identity on higher temporal components is only a stage initializer.
    The complete new stage equations correct all columns before application.
    """
    oldt=saved['times'];r=np.asarray(saved['radial_nodes'])
    choose=np.r_[0,np.flatnonzero(saved['radial_node_is_collocation'])]
    # The old single-step degree3 polynomial is completely identified here.
    if len(np.unique(saved['radial_node_step']))!=1:
        raise ValueError('this saved initializer adapter owns the completed single-step application')
    rr=r[choose];z=(rr-rr[0])/(rr[-1]-rr[0]);zp=(np.asarray(radii)-rr[0])/(rr[-1]-rr[0])
    V=np.polynomial.polynomial.polyvander(z,len(choose)-1)
    P=np.polynomial.polynomial.polyvander(zp,len(choose)-1)@np.linalg.inv(V)
    d=len(indices);oldindices=(64*np.arange(len(oldt))[:,None]+indices).ravel()
    E=np.kron(time_evaluation_matrix(oldt,newtimes),np.eye(d))
    R=np.kron(time_evaluation_matrix(newtimes,oldt),np.eye(d))
    name='analytic_inverse' if inverse else 'fundamental'
    source_name=name+'_source'
    H=saved[label+'_'+name][choose][:,oldindices][:,:,oldindices]
    Hx=saved[label+'_'+source_name][choose][:,oldindices][:,:,oldindices]
    hv=np.einsum('ij,jab->iab',P,H);hx=np.einsum('ij,jab->iab',P,Hx)
    eye=np.eye(len(newtimes)*d);oldeye=np.eye(len(oldt)*d)
    return np.array([eye+E@(a-oldeye)@R for a in hv]),np.array([E@a@R for a in hx])


def _factor_solution(c,D,components,boundaries,order,*,saved=None,label=None,newtimes=None):
    cn,polys,integral,A=_collocation_rule(order);n=len(D);steps=len(boundaries)-1
    outputs={};stagemax=stagexmax=inversemax=inversexmax=0.;initializer_reports=[]
    for bi,indices in enumerate(components):
        d=len(indices);size=n*d
        initial=np.eye(size,dtype=complex);initialx=np.zeros_like(initial)
        left=initial.copy();leftx=initialx.copy()
        init=[];initx=[];slopes=[];slopexs=[];linits=[];linitxs=[];lslopes=[];lslopexs=[]
        for step in range(steps):
            gs=[];gxs=[]
            for j in range(order):
                ci=step*order+j
                args=[c[k][ci][:,indices][:,:,indices] for k in ('time','radial','body','time_source','radial_source','body_source')]
                g,gx=_generator(*args,D);gs.append(g);gxs.append(gx)
            gs=np.array(gs);gxs=np.array(gxs);h=boundaries[step+1]-boundaries[step]
            guess=guessx=lguess=lguessx=None
            if saved is not None:
                radius=boundaries[step]+h*cn
                guess,guessx=_saved_factor_guess(saved,label,indices,newtimes,radius)
                lguess,lguessx=_saved_factor_guess(saved,label,indices,newtimes,radius,True)
                lguess=lguess.transpose(0,2,1);lguessx=lguessx.transpose(0,2,1)
            s,sx,a,b,ig=_rectangular_collocation(gs,gxs,initial,initialx,h,A,guess,guessx)
            ls,lsx,la,lb,ilg=_rectangular_collocation(-gs.transpose(0,2,1),-gxs.transpose(0,2,1),left.T,leftx.T,h,A,lguess,lguessx)
            initializer_reports.append(dict(block=bi,step=step,right=ig,left=ilg))
            stagemax=max(stagemax,a,la);stagexmax=max(stagexmax,b,lb)
            init.append(initial);initx.append(initialx);slopes.append(s);slopexs.append(sx)
            linits.append(left);linitxs.append(leftx);lslopes.append(ls);lslopexs.append(lsx)
            initial=initial+h*np.einsum('i,ijk->jk',integral(1.),s)
            initialx=initialx+h*np.einsum('i,ijk->jk',integral(1.),sx)
            left=(left.T+h*np.einsum('i,ijk->jk',integral(1.),ls)).T
            leftx=(leftx.T+h*np.einsum('i,ijk->jk',integral(1.),lsx)).T
            inversemax=max(inversemax,float(np.max(abs(left@initial-np.eye(size)))))
            inversexmax=max(inversexmax,float(np.max(abs(leftx@initial+left@initialx))))
        prefix='block'+str(bi)+'_'
        outputs[prefix+'indices']=indices
        for key,value in zip(('initial','initial_source','slopes','slopes_source','inverse_initial','inverse_initial_source','inverse_slopes','inverse_slopes_source'),
                (init,initx,slopes,slopexs,linits,linitxs,lslopes,lslopexs)):
            outputs[prefix+key]=np.array(value)
    return outputs,dict(stage_value=stagemax,stage_source=stagexmax,
        independent_left_inverse_endpoint=inversemax,independent_left_inverse_source_endpoint=inversexmax,
        initializer_corrections=initializer_reports)


def _factor_at(arrays,prefix,radii):
    """Piecewise Gauss dense polynomial; no radial ODE re-execution."""
    r=np.atleast_1d(np.asarray(radii,float));bounds=arrays['radial_boundaries']
    if np.any(r>bounds[0]+1e-15) or np.any(r<bounds[-1]-1e-15):
        raise ValueError('outside the explicitly solved computational strip')
    order=int(arrays['radial_order']);_,polys,integral,_=_collocation_rule(order)
    result=[]
    for radial in r:
        step=min(np.searchsorted(-bounds,-radial,side='right')-1,len(bounds)-2);step=max(step,0)
        h=bounds[step+1]-bounds[step];theta=(radial-bounds[step])/h
        w=integral(theta);dw=np.array([p(theta) for p in polys])
        initial=arrays[prefix+'initial'][step];initialx=arrays[prefix+'initial_source'][step]
        slope=arrays[prefix+'slopes'][step];slopex=arrays[prefix+'slopes_source'][step]
        value=initial+h*np.einsum('i,ijk->jk',w,slope)
        source=initialx+h*np.einsum('i,ijk->jk',w,slopex)
        radial_value=np.einsum('i,ijk->jk',dw,slope)
        radial_source=np.einsum('i,ijk->jk',dw,slopex)
        result.append((value,radial_value,source,radial_source))
    return result


def apply_refined_fundamental(arrays,side,wall,wall_source,*,times=None,radii=None):
    """Apply all exact carrier components to any full384 wall data, including h."""
    t=arrays['times'];r=arrays['radial_nodes'] if radii is None else np.asarray(radii,float)
    p=t if times is None else np.asarray(times,float)
    W=np.asarray(wall,complex);Wx=np.asarray(wall_source,complex);n=len(t)
    if W.ndim!=3 or W.shape[:2]!=(n,384) or Wx.shape!=W.shape:
        raise ValueError('explicit full384 wall values and source columns at every refined node required')
    V=time_evaluation_matrix(t,p);Vt=time_evaluation_matrix(t,p,1)
    out={key:np.zeros((len(r),len(p),384,W.shape[-1]),complex) for key in ('value','radial','time','source','radial_source','time_source')}
    for branch_index,branch in enumerate(('particle','conjugate')):
        label=side+'_'+branch
        for bi in range(int(arrays[label+'_block_count'])):
            prefix=label+'_block'+str(bi)+'_';indices=arrays[prefix+'indices'];d=len(indices)
            transfer=_factor_at(arrays,prefix,r)
            for family in range(3):
                global_indices=(2*family+branch_index)*64+indices
                w=W[:,global_indices].reshape(n*d,-1);wx=Wx[:,global_indices].reshape(n*d,-1)
                for ri,(H,Hr,Hx,Hrx) in enumerate(transfer):
                    vals=(H@w,Hr@w,Hx@w+H@wx,Hrx@w+Hr@wx)
                    for key,a in zip(('value','radial','source','radial_source'),vals):
                        a=a.reshape(n,d,-1)
                        out[key][ri,:,global_indices,:]=(V@a.reshape(n,-1)).reshape(len(p),d,-1).transpose(1,0,2)
                        if key in ('value','source'):
                            time_key='time' if key=='value' else 'time_source'
                            out[time_key][ri,:,global_indices,:]=(Vt@a.reshape(n,-1)).reshape(len(p),d,-1).transpose(1,0,2)
    return out


def evaluate_refined_field(arrays,label,times,radii):
    return apply_refined_fundamental(arrays,label.split('_')[0],arrays[label+'_wall'],
        arrays[label+'_wall_source'],times=times,radii=radii)


def evaluate_refined_factor(arrays,label,block,radii):
    """Independent right/left Gauss solutions and radial/source derivatives."""
    prefix=label+'_block'+str(int(block))+'_'
    r=np.atleast_1d(np.asarray(radii,float));bounds=arrays['radial_boundaries']
    right=_factor_at(arrays,prefix,r)
    _,polys,integral,_=_collocation_rule(int(arrays['radial_order']))
    out={key:[] for key in ('H','Hr','Hx','Hrx','L','Lr','Lx','Lrx')}
    for radial,hv in zip(r,right):
        step=min(np.searchsorted(-bounds,-radial,side='right')-1,len(bounds)-2);step=max(step,0)
        h=bounds[step+1]-bounds[step];theta=(radial-bounds[step])/h
        w=integral(theta);dw=np.array([p(theta) for p in polys])
        L0=arrays[prefix+'inverse_initial'][step];Lx0=arrays[prefix+'inverse_initial_source'][step]
        slope=arrays[prefix+'inverse_slopes'][step];slopex=arrays[prefix+'inverse_slopes_source'][step]
        # The independent left system was solved on L.T, not on L.
        L=L0+h*np.einsum('i,ijk->jk',w,slope).T
        Lx=Lx0+h*np.einsum('i,ijk->jk',w,slopex).T
        Lr=np.einsum('i,ijk->jk',dw,slope).T
        Lrx=np.einsum('i,ijk->jk',dw,slopex).T
        for key,value in zip(out,(*hv,L,Lr,Lx,Lrx)):out[key].append(value)
    return {key:np.array(value) for key,value in out.items()}


def independent_factor_residuals(arrays,history,points):
    """Original full-unit transfer residuals at independent (time,rho) pairs.

    Reports both the refined cardinal unit basis and the embedded old six
    amplitude-unit basis.  These finite max-entry norms do not bound a
    continuum operator or determine its physical outer-domain coefficients.
    """
    points=np.asarray(points,float)
    if points.ndim!=2 or points.shape[1]!=2:raise ValueError('explicit independent (time,rho) pairs required')
    labels=('plus_particle','plus_conjugate','minus_particle','minus_conjugate')
    records={label:[] for label in labels};rows={label:[] for label in labels}
    for time,rho in points:
        coefficients,_,_=coefficient_rows(history,[time],[rho])
        E=time_evaluation_matrix(arrays['times'],[time])[0]
        Et=time_evaluation_matrix(arrays['times'],[time],1)[0]
        for label in labels:
            c=coefficients[label];n=len(E);maximum=np.zeros(8)
            components=[]
            for bi in range(int(arrays[label+'_block_count'])):
                indices=arrays[label+'_block'+str(bi)+'_indices'];components.append(indices);d=len(indices)
                f=evaluate_refined_factor(arrays,label,bi,[rho]);f={k:v[0] for k,v in f.items()}
                def temporal(key,derivative=False):
                    return np.einsum('t,tdk->dk',Et if derivative else E,f[key].reshape(n,d,n*d))
                v,vr,vt=temporal('H'),temporal('Hr'),temporal('H',True)
                vx,vrx,vtx=temporal('Hx'),temporal('Hrx'),temporal('Hx',True)
                T,R,K,Tx,Rx,Kx=[c[k][0,0][np.ix_(indices,indices)] for k in ('time','radial','body','time_source','radial_source','body_source')]
                strong=R@vr+T@vt+K@v
                strongx=Rx@vr+Tx@vt+Kx@v+R@vrx+T@vtx+K@vx
                embed=np.kron(time_evaluation_matrix(arrays['amplitude_times'],arrays['times']),np.eye(d))
                inverse=f['L']@f['H']-np.eye(n*d)
                inversex=f['Lx']@f['H']+f['L']@f['Hx']
                maxima=np.array([np.max(abs(strong)),np.max(abs(strongx)),
                    np.max(abs(strong@embed)),np.max(abs(strongx@embed)),
                    np.max(abs(inverse)),np.max(abs(inversex)),np.linalg.norm(strong),np.linalg.norm(strongx)])
                maximum=np.maximum(maximum,maxima)
            offblock=component_offblock_max(c,components)
            if offblock!=0:raise ValueError('an independent original coefficient couples retained carrier components')
            records[label].append(maximum);rows[label].append(offblock)
    outputs={'factor_independent_points_time_rho':points};report={}
    names=('original_strong_max_entry','original_source_max_entry','embedded_old6_strong_max_entry',
        'embedded_old6_source_max_entry','independent_inverse_max_entry','independent_inverse_source_max_entry',
        'largest_carrier_block_strong_Frobenius','largest_carrier_block_source_Frobenius')
    for label in labels:
        a=np.array(records[label]);outputs[label+'_independent_factor_residuals']=a
        report[label]={key:float(np.max(a[:,j])) for j,key in enumerate(names)}
        report[label]['original_coefficient_offblock_max']=max(rows[label])
    report['norm_scope']='max absolute matrix entry over independent points and all retained64 carrier blocks; old6 coordinates embedded without fitting; Frobenius reports largest carrier block only'
    return outputs,report


def solve_refined_incoming_bulk_family(times,raw_nodes,raw_rates,*,saved_endpoint,
        temporal_count=10,radial_steps=2,radial_order=5,strip_fraction=.01,saved_application=None,
        history=None):
    """Refine time products and radial dense output, retaining the full family.

    Saved fields are evaluated as an initializer/comparison, not recomputed
    with a new physical source.  The exact linear stage solve is a correction
    to that initializer and does not fit any physical amplitude or h datum.
    """
    if type(temporal_count)is not int or not 6<=temporal_count<=24:
        raise ValueError('explicit refined temporal order6 through24 required')
    if type(radial_steps)is not int or not 1<=radial_steps<=8:
        raise ValueError('explicit bounded computational radial partition required')
    canonical=RefinedCanonicalHistory(times,raw_nodes,raw_rates)
    if history is None:history=canonical
    for ti,raw,rate in zip(times,raw_nodes,raw_rates):
        actual,actual_time=history.value(ti);xi,_=history.source(ti)
        if max(np.max(abs(actual-raw)),np.max(abs(xi-rate)))>1e-12:
            raise ValueError('refined original callback does not match the saved background/source identities')
    oldt=np.asarray(times,float)
    t=oldt[0]+(oldt[-1]-oldt[0])*(1-np.cos(np.linspace(0,np.pi,temporal_count)))/2
    t[[0,-1]]=oldt[[0,-1]];D=nodal_derivative(t)
    # Preserve the previous strip width when an application is supplied.
    if saved_application is not None:
        width=float(saved_application['computational_strip_width'])
    else:
        c,_,_=coefficient_rows(history,t,[WALL])
        speed=[]
        for x in t:
            raw,rate=history.value(x)
            from .muon_sigma_normal_collar_transport import sigma_geometry_point
            a=sigma_geometry_point(raw,rate,WALL)
            speed.append(abs(a['lapse'][0]/a['radial_coframe'][0]))
        width=float(strip_fraction*(t[-1]-t[0])*min(speed))
    if not 0<width<WALL:raise ValueError('positive previously declared finite numerical strip required')
    boundaries=np.linspace(WALL,WALL-width,radial_steps+1)
    cn,_,_,_=_collocation_rule(radial_order)
    stage_r=np.concatenate([a+(b-a)*cn for a,b in zip(boundaries[:-1],boundaries[1:])])
    c,density,densityx=coefficient_rows(history,t,stage_r)
    eval_r=np.sort(np.r_[boundaries,stage_r])[::-1]
    arrays=dict(times=t,time_derivative=D,amplitude_times=oldt,radial_nodes=eval_r,
        radial_boundaries=boundaries,radial_order=np.array(radial_order),
        computational_strip_width=np.array(width),original_raw268_nodes=np.asarray(raw_nodes),
        original_raw_coordinate_rates268_nodes=np.asarray(raw_rates),
        raw268_nodes=np.array([history.value(s)[0] for s in t]),
        canonical_coordinate_rates268_nodes=np.array([history.value(s)[1] for s in t]),
        source_Xi268_nodes=np.array([history.source(s)[0] for s in t]))
    reports={}
    for label,coefficient in c.items():
        components=carrier_components(coefficient)
        factors,r=_factor_solution(coefficient,D,components,boundaries,radial_order,
            saved=saved_application,label=label,newtimes=t)
        arrays.update({label+'_'+key:value for key,value in factors.items()})
        arrays[label+'_block_count']=np.array(len(components))
        r.update(carrier_component_sizes=[len(x) for x in components],
            coefficient_offblock_max=component_offblock_max(coefficient,components),retained_carrier_count=64)
        reports[label]=r
    full=full_d5_localized_lepton_trace();endpoints=[];time_endpoints=[]
    for i,s in enumerate(t):
        x,xt=history.value(s);xi,_=history.source(s)
        if s==oldt[-1]:
            # Xi and raw have the saved E1 identities; canonical acceleration
            # is deliberately a different coordinate-time derivative.
            endpoints.append(_endpoint_from_cache(saved_endpoint,np.asarray(raw_nodes)[-1],np.asarray(raw_rates)[-1],full))
        else:endpoints.append(_fresh_endpoint(x,xi))
        time_endpoints.append(endpoints[-1] if np.array_equal(xt,xi) else _fresh_endpoint(x,xt))
    wall=_wall_maps(endpoints,full);wall_t=_wall_maps(time_endpoints,full)
    embed=np.kron(time_evaluation_matrix(oldt,t),np.eye(18))
    for label in ('plus_seed','minus_seed','minus_LR','minus_RL'):
        arrays[label+'_wall']=wall[label]@embed
        arrays[label+'_wall_source']=wall[label+'_source']@embed
        # Coordinate-time product derivative includes d g/dt independently.
        shape=(len(t),384,18*len(oldt));a=np.zeros(shape,complex)
        amp=time_evaluation_matrix(oldt,t);amp_t=time_evaluation_matrix(oldt,t,1)
        for i in range(len(t)):
            for j in range(len(oldt)):
                basis=wall[label][i,:,18*i:18*(i+1)]
                basis_t=wall_t[label+'_source'][i,:,18*i:18*(i+1)]
                a[i,:,18*j:18*(j+1)]=basis_t*amp[i,j]+basis*amp_t[i,j]
        arrays[label+'_wall_coordinate_time_product']=a
        app=evaluate_refined_field(arrays,label,t,eval_r)
        for key,value in app.items():arrays[label+'_'+key]=value
    for key,value in wall.items():
        if key.startswith('wall_'):arrays[key]=value
    z,zr=_extension_cutoff(eval_r,width);arrays['extension_cutoff']=z;arrays['extension_cutoff_radial']=zr
    report=dict(classification='PROVISIONAL_REFINED_ORIGINAL_D5_INCOMING_BULK_FAMILY',
        time_representation='global refined Chebyshev-Lobatto field polynomial; supplied original coefficient/history callbacks',
        temporal_count=len(t),amplitude_count=len(oldt)*18,
        homogeneous_wall_unknown_shape=[len(t),366],homogeneous_coordinates_assigned=False,
        radial_order=radial_order,radial_steps=radial_steps,strip_width=width,
        history=(history.diagnostics() if hasattr(history,'diagnostics') else dict(
            callback_type=type(history).__name__,original_saved_node_value_and_Xi_identities_checked=True,
            original_radial_callback_used=hasattr(history,'gauge_basis'))),
        canonical_C1_alternative_diagnostics=canonical.diagnostics(),factorized_operator=reports,
        old_saved_application_reused=saved_application is not None,
        full_outer_event_and_formation_conditions_solved=False,physical_admission=False,
        normal_profile_ratios_assigned=False,Higgs_seam_added_as_bulk_mass=False,
        local_Maxwell_Higgs_removed_again=False)
    return arrays,report,history
