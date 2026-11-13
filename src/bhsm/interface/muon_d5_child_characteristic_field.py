"""Original child D5 Cauchy/characteristic FIELD response on a finite cell.

Every birth value and future incoming characteristic coordinate is retained.
The response is a linear family, not a selected physical section. The E1
event consumer may replace proved birth-wall coordinates by parent data;
it cannot extrapolate that instantaneous event into a future wall history.
"""
from __future__ import annotations
import numpy as np
from scipy.linalg import lu_factor,lu_solve

from .muon_d5_complement_bulk_response import nodal_derivative
from .muon_d5_temporal_bulk_refinement import (
    carrier_components,component_offblock_max,time_evaluation_matrix,
)
from .muon_d5_child_same_direction_application import ChildNormalCorrectionHistory,_differential_columns
from .muon_d5_event_bundle_incidence import original_event_coefficients
from .muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace


def child_source_names(joint):
    names=[]
    for candidate in joint['initial_candidate_index']:
        names+=['candidate'+str(int(candidate))+'_corrected_particular']
        names+=['candidate'+str(int(candidate))+'_free_map'+str(j) for j in range(7)]
    return names+['free_child_normal_rate']


def original_child_cell_coefficients(history,times,radii,joint,psi_e1):
    """Original inherited pp-rp+rc operator, actual new source applications.

    Fixed ORIGINAL (t,rho) numerical coordinates are used. Moving physical
    face/base/frame contacts are separate ports; no child polynomial is
    evaluated before its original birth face t=0. Source columns contain
    the recorded nonzero inherited jets in each corrected particular.
    Additional normal-induced inherited jets remain independent unknowns.
    """
    times,radii=map(lambda a:np.asarray(a,float),(times,radii))
    if np.any(times<0) or np.any(times>history.times[-1]):
        raise ValueError('child value callback may only be consumed in its actual future cell')
    normal=ChildNormalCorrectionHistory(history,psi_e1)
    nu=ChildNormalCorrectionHistory(history,psi_e1,free_rate_column=True)
    full=full_d5_localized_lepton_trace();count=len(child_source_names(joint))
    pair=np.asarray(history.original_phase_operands['initial_pair'])
    refs=np.asarray(history.original_phase_operands['reference_pair'])
    def geometry_rate(x):
        z=np.zeros(268,complex);z[:37]=x[37:74];z[98]=x[99];return z
    records={side+'_'+branch:{k:[] for k in ('time','radial','body','time_source','radial_source','body_source')}
        for side in ('plus','minus') for branch in ('particle','conjugate')}
    normal_free=[];metrics=[]
    for t in times:
        xi=np.asarray(history.source(t)[0]);correction=normal.source(t)[0]
        raw=np.zeros((268,count),complex);parent=np.zeros_like(raw);references=np.zeros((2,268,count),complex)
        for family in range(len(joint['initial_candidate_index'])):
            s=8*family
            raw[:,s]=xi+correction+joint['child_raw_field_Higgs_source_correction'][family]
            raw[:,s+1:s+8]=joint['child_raw_field_Higgs_free_rotation_phase_coefficients'][family]
            parent[:,s]=geometry_rate(pair[0]);references[:,:,s]=np.array([geometry_rate(x) for x in refs])
        raw[:,-1]=nu.source(t)[0]
        c=original_event_coefficients(history,float(t),radii,side='child',directions=dict(raw=raw,parent=parent,references=references))
        d=_differential_columns(c,full,count)
        metrics.append(np.array([c[k] for k in ('lapse','radial_coframe','coordinate_shift','volume_density')]))
        normal_free.append(raw)
        for side,eps in (('plus',1),('minus',-1)):
          for branch in ('particle','conjugate'):
            target=records[side+'_'+branch]
            for key in ('time','radial','body'):
                target[key].append(d[eps][0]['value']['blocks'][branch][key])
                target[key+'_source'].append(np.array([d[eps][j]['first']['blocks'][branch][key] for j in range(count)]))
    for row in records.values():
        for key in row:
            a=np.array(row[key]);row[key]=a.transpose(1,0,2,3,4) if key.endswith('_source') else a
    return records,dict(metrics=np.array(metrics),raw_source_columns=np.array(normal_free),source_names=child_source_names(joint))


def characteristic_bases(branch,eps,indices=None):
    """Exact spin-coordinate bases of original radial characteristic spaces.

    T^-1 R=eps*(N/C)*Gamma0 Gamma4-zI. The ± bases below diagonalize
    that fixed Clifford product, retaining both32-dimensional spaces.
    This is not an incoming particle polarization or a vacuum projector.
    """
    if branch not in ('particle','conjugate') or eps not in (-1,1):
        raise ValueError('owned charge-copy and independent collar orientation required')
    sign=1 if branch=='particle' else -1
    def basis(eigen):
        return np.kron(np.vstack((np.eye(2),-1j*sign*eigen*np.eye(2)))/np.sqrt(2),np.eye(16))
    # Inner-face incoming lambda>0; outer-face incoming lambda<0.
    inner,outer=basis(eps),basis(-eps)
    if indices is None:return inner,outer
    indices=np.asarray(indices,int);outside=np.setdiff1d(np.arange(64),indices)
    output=[]
    for Q in (inner,outer):
        selected=np.flatnonzero(np.any(Q[indices]!=0,axis=0))
        if np.any(Q[np.ix_(outside,selected)]!=0) or 2*len(selected)!=len(indices):
            raise ValueError('a claimed carrier component does not preserve both characteristic spaces')
        output.append((Q[np.ix_(indices,selected)],selected))
    return tuple(output)


def _pde_matrix(c,Dt,Dr):
    nt,nr,d=c['time'].shape[:3];A=np.zeros((nt,nr,d,nt,nr,d),complex)
    for i in range(nt):
      for r in range(nr):
        for j in range(nt):A[i,r,:,j,r,:]+=c['time'][i,r]*Dt[i,j]
        for s in range(nr):A[i,r,:,i,s,:]+=c['radial'][i,r]*Dr[r,s]
        A[i,r,:,i,r,:]+=c['body'][i,r]
    return A.reshape(nt*nr*d,nt*nr*d)


def _characteristic_system(pde,nt,nr,d,inner,outer,scale,inverse_time):
    """Solve interior/outgoing PDE plus incoming data; retain other PDE rows."""
    M=scale*pde.copy();B=np.zeros((nt*nr*d,(nr+nt-1)*d),complex)
    half=d//2
    for r in range(nr):
        rows=slice(r*d,(r+1)*d);M[rows]=0;M[rows,rows]=np.eye(d);B[rows,rows]=np.eye(d)
    for i in range(1,nt):
      for r,Qin,Qout,face in ((0,inner,outer,0),(nr-1,outer,inner,1)):
        start=(i*nr+r)*d;node=slice(start,start+d)
        M[start:start+half]=0;M[start:start+half,node]=Qin.conj().T
        # The characteristic covector belongs to the evolution equation,
        # not to the unmultiplied Clifford output of the Dirac equation.
        M[start+half:start+d]=scale*Qout.conj().T@inverse_time[i,r]@pde[node]
        data=(nr+i-1)*d+face*half
        B[start:start+half,data:data+half]=np.eye(half)
    return M,B


def solve_child_characteristic_cell(coefficients,times,radii,*,initializer=None):
    """Solve a factorized finite Cauchy/characteristic field family.

    Per64 branch, data slots0..2 are full birth values. Slots3..7 contain
    [inner incoming32,outer incoming32] at five positive-time nodes. Each
    source is an operator partial: Phi_x=H_x z+H delta_z, and delta_z is
    NEVER assigned by the construction of H_x.
    """
    t,r=map(lambda a:np.asarray(a,float),(times,radii));nt,nr=len(t),len(r)
    if nt!=6 or nr!=3 or t[0]!=0 or np.any(np.diff(t)<=0) or np.any(np.diff(r)<=0):
        raise ValueError('explicit future t6/rho3 finite cell required')
    Dt,Dr=nodal_derivative(t),nodal_derivative(r);scale=t[-1]-t[0]
    app=dict(times=t,radii=r,time_derivative=Dt,radial_derivative=Dr);reports={}
    for label,c in coefficients.items():
        side,branch=label.split('_');eps=1 if side=='plus' else -1
        components=carrier_components(c);off=component_offblock_max(c,components)
        app[label+'_block_count']=np.array(len(components),dtype=np.int64)
        for bi,indices in enumerate(components):
            d=len(indices);cut=lambda a:np.asarray(a)[...,indices,:][...,indices]
            values={k:cut(c[k]) for k in ('time','radial','body')}
            source={k:cut(c[k+'_source']) for k in ('time','radial','body')}
            (inner,ii),(outer,oi)=characteristic_bases(branch,eps,indices)
            pde=_pde_matrix(values,Dt,Dr);TI=np.linalg.inv(values['time'])
            M,B=_characteristic_system(pde,nt,nr,d,inner,outer,scale,TI)
            prefix=label+'_block'+str(bi)+'_'
            guess=np.zeros_like(B) if initializer is None else np.asarray(initializer[prefix+'response']).reshape(B.shape)
            lu=lu_factor(M);before=B-M@guess;H=guess+lu_solve(lu,before)
            Hx=[];source_res=[];source_before=[]
            for j in range(len(source['time'])):
                px=_pde_matrix({k:a[j] for k,a in source.items()},Dt,Dr)
                Mx,_=_characteristic_system(px,nt,nr,d,inner,outer,scale,TI)
                TIx=-TI@source['time'][j]@TI
                # Boundary/birth DATA coordinates have constant covectors.
                # Only their actual PDE rows are differentiated here.
                for rb in range(nr):Mx[rb*d:(rb+1)*d]=0
                for ti in range(1,nt):
                    for rr,Qout in ((0,outer),(nr-1,inner)):
                        z=(ti*nr+rr)*d;Mx[z:z+d//2]=0
                        Mx[z+d//2:z+d]+=scale*Qout.conj().T@TIx[ti,rr]@pde[z:z+d]
                old=np.zeros_like(H) if initializer is None else np.asarray(initializer[prefix+'response_source'][j]).reshape(H.shape)
                rhs=-Mx@H;xbefore=rhs-M@old;X=old+lu_solve(lu,xbefore);Hx.append(X)
                source_before.append(float(np.max(abs(xbefore))))
                source_res.append(float(np.max(abs(M@X+Mx@H))))
            Hx=np.array(Hx)
            data_indices=np.r_[np.concatenate([64*j+indices for j in range(nr)]),
                np.concatenate([64*(nr+j)+np.r_[ii,32+oi] for j in range(nt-1)])]
            app.update({prefix+k:v for k,v in dict(indices=indices,data_indices=data_indices,
                response=H.reshape(nt,nr,d,-1),response_source=Hx.reshape(len(Hx),nt,nr,d,-1),
                incoming_inner_basis=inner,incoming_outer_basis=outer,
                original_pde_rows=(pde@H).reshape(nt,nr,d,-1)).items()})
            reports[prefix[:-1]]=dict(carrier_count=d,data_coordinates=(nr+nt-1)*d,
                finite_square_size=len(M),equation_scaled_stage_max=float(np.max(abs(M@H-B))),
                equation_scaled_source_stage_max=max(source_res),matrix_condition2=float(np.linalg.cond(M)),
                reused_field_initializer=initializer is not None,initializer_residual_max=float(np.max(abs(before))),
                initializer_source_residual_max=max(source_before),
                full_original_nodal_D5_max=float(np.max(abs(pde@H))),
                boundary_incoming_PDE_rows_retained=True,exact_carrier_offblock_max=off)
    return app,dict(classification='SOLVED_ORIGINAL_CHILD_FINITE_CAUCHY_CHARACTERISTIC_FIELD_FAMILY',blocks=reports,
        original_equation='T partial_t Phi+R partial_rho Phi+K Phi=0 with original inherited child coefficients',
        computational_domain='fixed original t>=0 Cauchy cell; no child polynomial evaluated at pre-birth time',
        equations_solved='full birth data; original interior and outgoing-characteristic PDE rows; explicit incoming-characteristic boundary data',
        outgoing_covector='Q_out^dagger T^-1 applied to original L; its derivative includes -Q_out^dagger T^-1 (deltaT) T^-1 L',
        additional_PDE_checks='incoming-characteristic PDE rows at both radial faces retained as residual equations, not assumed zero',
        data_layout='(8,384,k): birth inner/middle/wall slots0:3; five positive-time slots contain per64 [inner incoming32,outer incoming32]',
        coordinates_per_collar=3072,birth_coordinates=1152,future_incoming_coordinates=1920,
        source_rule='deltaPhi=H_source z+H delta_z; delta_z independent and unassigned',
        fixed_numerical_domain_source=True,physical_moving_domain_and_base_contacts_unassigned=True,
        all_families_repeated_without_projection=3,all_charge_copies_and_both_eta_collars_retained=True,
        unknown_full_strong_and_complementary_angular_terms_not_assigned=True,
        initial_data_selected=False,future_incoming_data_selected=False,physical_admission=False,physical_guard=2e-10)


def evaluate_child_cell_factor(app,label,block,times,radii):
    p=label+'_block'+str(block)+'_';Et=time_evaluation_matrix(app['times'],times);Er=time_evaluation_matrix(app['radii'],radii)
    Et1=time_evaluation_matrix(app['times'],times,1);Er1=time_evaluation_matrix(app['radii'],radii,1)
    H=app[p+'response'];X=app[p+'response_source']
    apply=lambda A,B,V:np.einsum('ti,rj,ijab->trab',A,B,V,optimize=True)
    return dict(value=apply(Et,Er,H),time=apply(Et1,Er,H),radial=apply(Et,Er1,H),
        source=np.array([apply(Et,Er,a) for a in X]),time_source=np.array([apply(Et1,Er,a) for a in X]),
        radial_source=np.array([apply(Et,Er1,a) for a in X]))


def apply_child_cell_field(app,side,data,data_source=None,*,source_slot=0,times,radii):
    """Apply actual response to explicit data coefficients, preserving unknowns.

    ``data_source=None`` returns only value/gradients and source=None. It
    does not replace unknown boundary/source data by numerical zero.
    A coordinate partial may hold other data fixed, but is not a state.
    """
    z=np.asarray(data,complex)
    if z.ndim!=3 or z.shape[:2]!=(8,384) or side not in ('plus','minus'):
        raise ValueError('all8 full384 Cauchy/characteristic data slots required')
    zx=None if data_source is None else np.asarray(data_source,complex)
    if zx is not None and zx.shape!=z.shape:raise ValueError('same explicit data-source coordinates required')
    shape=(len(np.atleast_1d(times)),len(np.atleast_1d(radii)),384,z.shape[-1])
    out={key:np.zeros(shape,complex) for key in ('value','time','radial')}
    for key in ('source','time_source','radial_source'):out[key]=None if zx is None else np.zeros(shape,complex)
    for family in range(3):
      for b,branch in enumerate(('particle','conjugate')):
        sl=slice((2*family+b)*64,(2*family+b+1)*64);label=side+'_'+branch
        dz=z[:,sl].reshape(512,-1);dx=None if zx is None else zx[:,sl].reshape(512,-1)
        for bi in range(int(app[label+'_block_count'])):
            p=label+'_block'+str(bi)+'_';indices=app[p+'indices'];di=app[p+'data_indices']
            f=evaluate_child_cell_factor(app,label,bi,times,radii);rows=(2*family+b)*64+indices
            for key in ('value','time','radial'):out[key][:,:,rows]=f[key]@dz[di]
            if zx is not None:
                for key,base in (('source','value'),('time_source','time'),('radial_source','radial')):
                    out[key][:,:,rows]=f[key][source_slot]@dz[di]+f[base]@dx[di]
    return out


def independent_child_cell_checks(app,coefficients,times,radii):
    """Original differential rows at independent points, all field inputs.

    Neither derivative is replaced by the equation it checks. The returned
    unit-family rows bound no continuum norm and choose no physical data.
    """
    times,radii=map(lambda x:np.asarray(x,float),(times,radii));checks={};summary={}
    values_max=sources_max=0.
    for label,c in coefficients.items():
      for bi in range(int(app[label+'_block_count'])):
        p=label+'_block'+str(bi)+'_';ind=app[p+'indices']
        f=evaluate_child_cell_factor(app,label,bi,times,radii)
        cut=lambda a:np.asarray(a)[...,ind,:][...,ind]
        T,R,K=(cut(c[k]) for k in ('time','radial','body'))
        Tx,Rx,Kx=(cut(c[k+'_source']) for k in ('time','radial','body'))
        value=T@f['time']+R@f['radial']+K@f['value']
        source=Tx@f['time'][None]+Rx@f['radial'][None]+Kx@f['value'][None]
        source+=T[None]@f['time_source']+R[None]@f['radial_source']+K[None]@f['source']
        vm=np.max(abs(value),axis=(-2,-1));xm=np.max(abs(source),axis=(-2,-1))
        checks[p+'original_strong_max_by_point']=vm
        checks[p+'original_source_max_by_direction_point']=xm
        checks[p+'original_strong_Frobenius_by_point']=np.linalg.norm(value,axis=(-2,-1))
        checks[p+'original_source_Frobenius_by_direction_point']=np.linalg.norm(source,axis=(-2,-1))
        summary[p[:-1]]=dict(original_strong_max=float(np.max(vm)),original_source_max=float(np.max(xm)),
            source_max_by_direction=np.max(xm,axis=(1,2)).tolist(),unit_data_columns=value.shape[-1])
        values_max=max(values_max,float(np.max(vm)));sources_max=max(sources_max,float(np.max(xm)))
    checks.update(independent_times=times,independent_radii=radii)
    return checks,dict(norm='maximum absolute ORIGINAL strong coordinate component across stated independent points and every factorized Cauchy/incoming-data unit column',
        original_strong_max=values_max,original_source_max=sources_max,blocks=summary,
        physical_field_data_selected=False,physical_admission=False,physical_guard=2e-10,
        error_scope='finite t6/rho3 field and source polynomial, original coefficient callbacks; no continuum/angular/native/exterior bound')
