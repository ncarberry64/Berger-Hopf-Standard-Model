"""Necessary C1 start-corner equations and consumed child-data correction.

The incoming boundary germ follows from the ORIGINAL time evolution and
birth profile. All remaining future incoming and birth data stay free.
This is not a selected outer state, normal profile, or physical section.
"""
from __future__ import annotations
import numpy as np
from scipy.linalg import lu_factor,lu_solve

from .muon_d5_child_characteristic_field import _pde_matrix,_characteristic_system
from .muon_d5_temporal_bulk_refinement import time_evaluation_matrix


def _block_coefficients(app,prefix):
    c={k:app[prefix+'original_coefficient_'+k] for k in ('time','radial','body')}
    cx={k:app[prefix+'original_coefficient_'+k+'_source'] for k in c}
    return c,cx


def build_child_corner_compatibility(app):
    """Execute Qin†(partial_t+A partial_rho+B)Phi=0 at birth faces.

    Exact data-germ construction avoids mistaking the saved finite field's
    initializer cancellation for the defining corner equation. Its full
    original-field reconstruction is retained separately for comparison.
    """
    Dt,Dr=app['time_derivative'],app['radial_derivative'];out={};reports={}
    for label in ('plus_particle','plus_conjugate','minus_particle','minus_conjugate'):
      for bi in range(int(app[label+'_block_count'])):
        p=label+'_block'+str(bi)+'_';c,cx=_block_coefficients(app,p)
        nt,nr,d=c['time'].shape[:3];ns=len(cx['time']);half=d//2;nd=(nr+nt-1)*d
        C=np.zeros((d,nd),complex);Cx=np.zeros((ns,d,nd),complex)
        T=c['time'][0];TI=np.linalg.inv(T);TIx=-TI[None]@cx['time'][:,0]@TI[None]
        A=TI@c['radial'][0];B=TI@c['body'][0]
        Ax=TI[None]@cx['radial'][:,0]+TIx@c['radial'][0][None]
        Bx=TI[None]@cx['body'][:,0]+TIx@c['body'][0][None]
        H=app[p+'response'];X=app[p+'response_source']
        Ht=np.einsum('i,irab->rab',Dt[0],H);Hr=np.einsum('rs,sab->rab',Dr,H[0])
        Xt=np.einsum('i,xirab->xrab',Dt[0],X);Xr=np.einsum('rs,xsab->xrab',Dr,X[:,0])
        L=c['time'][0]@Ht+c['radial'][0]@Hr+c['body'][0]@H[0]
        Lx=cx['time'][:,0]@Ht[None]+cx['radial'][:,0]@Hr[None]+cx['body'][:,0]@H[0][None]
        Lx+=c['time'][0][None]@Xt+c['radial'][0][None]@Xr+c['body'][0][None]@X[:,0]
        recovered=[];recoveredx=[]
        for face,r,Q in ((0,0,app[p+'incoming_inner_basis']),(1,nr-1,app[p+'incoming_outer_basis'])):
            rows=slice(face*half,(face+1)*half);Qh=Q.conj().T
            C[rows,r*d:(r+1)*d]+=Dt[0,0]*Qh
            for i in range(1,nt):
                j=(nr+i-1)*d+face*half;C[rows,j:j+half]+=Dt[0,i]*np.eye(half)
            for j in range(nr):
                C[rows,j*d:(j+1)*d]+=Qh@A[r]*Dr[r,j]
                Cx[:,rows,j*d:(j+1)*d]+=Qh@Ax[:,r]*Dr[r,j]
            C[rows,r*d:(r+1)*d]+=Qh@B[r]
            Cx[:,rows,r*d:(r+1)*d]+=Qh@Bx[:,r]
            recovered.append(Qh@TI[r]@L[r])
            recoveredx.append(Qh@(TI[r]@Lx[:,r]+TIx[:,r]@L[r]))
        recovered=np.concatenate(recovered,axis=0);recoveredx=np.concatenate(recoveredx,axis=1)
        pivot=np.arange(nr*d,(nr+1)*d);free=np.setdiff1d(np.arange(nd),pivot);P=C[:,pivot]
        K=np.eye(nd,dtype=complex)[:,free];K[pivot]=-np.linalg.solve(P,C[:,free])
        Kx=np.zeros((ns,nd,len(free)),complex)
        for j in range(ns):Kx[j,pivot]=-np.linalg.solve(P,Cx[j]@K)
        out.update({p+k:v for k,v in dict(corner=C,corner_source=Cx,pivot=pivot,free=free,
            kernel=K,kernel_source=Kx,original_kernel_rows=C@K,
            original_source_kernel_rows=Cx@K+C[None]@Kx,
            saved_field_corner_rows=recovered,saved_field_corner_source_rows=recoveredx,
            saved_field_vs_exact_corner_rows=recovered-C,
            saved_field_vs_exact_corner_source_rows=recoveredx-Cx).items()})
        reports[p[:-1]]=dict(rows=d,data_coordinates=nd,remaining_coordinates=len(free),
            pivot_rank=int(np.linalg.matrix_rank(P)),pivot_condition2=float(np.linalg.cond(P)),
            pivot_coefficient=float(Dt[0,1]),pivot_identity_max=float(np.max(abs(P-Dt[0,1]*np.eye(d)))),
            exact_kernel_original_row_max=float(np.max(abs(C@K))),
            exact_kernel_source_original_row_max=float(np.max(abs(Cx@K+C[None]@Kx))),
            saved_field_corner_difference_max=float(np.max(abs(recovered-C))),
            saved_field_corner_source_difference_max=float(np.max(abs(recoveredx-Cx))))
    return out,dict(classification='EXECUTED_NECESSARY_CHILD_C1_START_CORNER_GERM_CONSTRAINT',blocks=reports,
        original_equation='Qin^dagger[partial_t Phi+T^-1 R partial_rho Phi+T^-1 K Phi]=0 at t=0 and each radial face',
        trace_germ='b_dot(0)=Dt[0,0] Qin^dagger Phi_birth(face)+sum_i>0 Dt[0,i] b_i',
        source_equation='Ccorner delta_z+Ccorner_Xi z=0, including both derivatives of T^-1R and T^-1K',
        eliminated_coordinates='only first future incoming data slot3, from square original corner equations; all remaining birth/future data retained',
        corner_rows_per_collar=384,remaining_data_per_collar=2688,
        physical_boundary_state_selected=False,whole_event_cap_extension_assumed=False,
        fixed_numerical_domain_only=True,physical_moving_domain_ports_unassigned=True,
        physical_admission=False,physical_guard=2e-10,
        error_scope='finite time/radial data germ with original coefficients; no continuum or complete physical outer bound')


def apply_child_corner_to_data(app,corner,side,data,data_source=None,*,source_slot=0):
    """Eliminate the named pivot using equations, preserving every free port.

    The input's slot3 is the eliminated coordinate; its prior trial value
    does not select data. Other input slots are never altered. A None
    source remains unknown rather than being silently zeroed.
    """
    z=np.asarray(data,complex);zx=None if data_source is None else np.asarray(data_source,complex)
    if z.ndim!=3 or z.shape[:2]!=(8,384) or (zx is not None and zx.shape!=z.shape):
        raise ValueError('same explicit full8x384 data and optional source required')
    result=z.copy();rx=None if zx is None else zx.copy();reports=[]
    for family in range(3):
      for b,branch in enumerate(('particle','conjugate')):
        sl=slice((2*family+b)*64,(2*family+b+1)*64);label=side+'_'+branch
        raw=z[:,sl].reshape(512,-1);rawx=None if zx is None else zx[:,sl].reshape(512,-1)
        target=result[:,sl].reshape(512,-1).copy();targetx=None if rx is None else rx[:,sl].reshape(512,-1).copy()
        for bi in range(int(app[label+'_block_count'])):
            p=label+'_block'+str(bi)+'_';di=app[p+'data_indices'];free=corner[p+'free'];K=corner[p+'kernel']
            v=K@raw[di][free];target[di]=v
            C=corner[p+'corner'];Cx=corner[p+'corner_source'][source_slot]
            reports.append(float(np.max(abs(C@v))))
            if rx is not None:
                vx=K@rawx[di][free]+corner[p+'kernel_source'][source_slot]@raw[di][free]
                targetx[di]=vx;reports.append(float(np.max(abs(C@vx+Cx@v))))
        result[:,sl]=target.reshape(8,64,-1)
        if rx is not None:rx[:,sl]=targetx.reshape(8,64,-1)
    return result,rx,dict(original_corner_value_or_source_max=max(reports),all_nonpivot_data_retained=True,
        eliminated_data_slot=3,physical_state_selected=False,physical_admission=False)


def _compiled_block(app,label,bi,cache):
    key=(label,bi)
    if key in cache:return cache[key]
    p=label+'_block'+str(bi)+'_';c,cx=_block_coefficients(app,p);nt,nr,d=c['time'].shape[:3]
    Dt,Dr=app['time_derivative'],app['radial_derivative'];scale=float(app['times'][-1]-app['times'][0])
    TI=np.linalg.inv(c['time']);P=_pde_matrix(c,Dt,Dr)
    inner,outer=app[p+'incoming_inner_basis'],app[p+'incoming_outer_basis']
    M,B=_characteristic_system(P,nt,nr,d,inner,outer,scale,TI)
    cache[key]=dict(prefix=p,c=c,cx=cx,TI=TI,P=P,M=M,B=B,lu=lu_factor(M),nt=nt,nr=nr,d=d,scale=scale,inner=inner,outer=outer,Mx={})
    return cache[key]


def _source_matrix(block,slot,Dt,Dr):
    if slot in block['Mx']:return block['Mx'][slot]
    b=block;px=_pde_matrix({k:a[slot] for k,a in b['cx'].items()},Dt,Dr)
    X,_=_characteristic_system(px,b['nt'],b['nr'],b['d'],b['inner'],b['outer'],b['scale'],b['TI'])
    d=b['d'];TIx=-b['TI']@b['cx']['time'][slot]@b['TI']
    X[:b['nr']*d]=0
    for i in range(1,b['nt']):
      for r,Qout in ((0,b['outer']),(b['nr']-1,b['inner'])):
        row=(i*b['nr']+r)*d;X[row:row+d//2]=0
        X[row+d//2:row+d]+=b['scale']*Qout.conj().T@TIx[i,r]@b['P'][row:row+d]
    b['Mx'][slot]=X
    return X


def prepare_child_data_response(app,side,data,*,factor_cache=None):
    """ONE LU residual correction on actual consumed VALUE data columns."""
    z=np.asarray(data,complex)
    if z.ndim!=3 or z.shape[:2]!=(8,384):raise ValueError('all explicit full384 data slots required')
    nt,nr=len(app['times']),len(app['radii']);V=np.zeros((nt,nr,384,z.shape[-1]),complex)
    cache={} if factor_cache is None else factor_cache;before=after=0.
    for family in range(3):
      for b,branch in enumerate(('particle','conjugate')):
        sl=slice((2*family+b)*64,(2*family+b+1)*64);label=side+'_'+branch;raw=z[:,sl].reshape(512,-1)
        for bi in range(int(app[label+'_block_count'])):
            cb=_compiled_block(app,label,bi,cache);p=cb['prefix'];di=app[p+'data_indices'];idx=app[p+'indices']
            initial=app[p+'response'].reshape(nt*nr*len(idx),-1)@raw[di]
            rhs=cb['B']@raw[di];residual=rhs-cb['M']@initial
            actual=initial+lu_solve(cb['lu'],residual)
            before=max(before,float(np.max(abs(residual))));after=max(after,float(np.max(abs(rhs-cb['M']@actual))))
            V[:,:,(2*family+b)*64+idx]=actual.reshape(nt,nr,len(idx),-1)
    return dict(application=app,side=side,data=z,nodal_value=V,factor_cache=cache,
        report=dict(value_stage_before_max=before,value_stage_after_max=after,
            actual_input_columns=z.shape[-1],LU_residual_corrections=1,physical_data_selection=False))


def apply_child_data_source(prepared,data_source,*,source_slot=0):
    """ONE same-matrix source correction, using corrected consumed values."""
    a=prepared;app=a['application'];z=a['data'];zx=np.asarray(data_source,complex)
    if zx.shape!=z.shape:raise ValueError('all same explicit data-source slots required; unknown is not zero')
    nt,nr=len(app['times']),len(app['radii']);X=np.zeros_like(a['nodal_value']);before=after=0.
    for family in range(3):
      for b,branch in enumerate(('particle','conjugate')):
        sl=slice((2*family+b)*64,(2*family+b+1)*64);label=a['side']+'_'+branch
        raw=z[:,sl].reshape(512,-1);rawx=zx[:,sl].reshape(512,-1)
        for bi in range(int(app[label+'_block_count'])):
            cb=_compiled_block(app,label,bi,a['factor_cache']);p=cb['prefix'];di=app[p+'data_indices'];idx=app[p+'indices']
            initial=app[p+'response_source'][source_slot].reshape(nt*nr*len(idx),-1)@raw[di]
            initial+=app[p+'response'].reshape(nt*nr*len(idx),-1)@rawx[di]
            value=a['nodal_value'][:,:,(2*family+b)*64+idx].reshape(nt*nr*len(idx),-1)
            Mx=_source_matrix(cb,source_slot,app['time_derivative'],app['radial_derivative'])
            rhs=cb['B']@rawx[di]-Mx@value;residual=rhs-cb['M']@initial
            actual=initial+lu_solve(cb['lu'],residual)
            before=max(before,float(np.max(abs(residual))));after=max(after,float(np.max(abs(rhs-cb['M']@actual))))
            X[:,:,(2*family+b)*64+idx]=actual.reshape(nt,nr,len(idx),-1)
    return X,dict(source_slot=source_slot,source_stage_before_max=before,source_stage_after_max=after,
        actual_input_columns=z.shape[-1],LU_residual_corrections=1,physical_data_selection=False)


def evaluate_child_data_response(prepared,nodal_source,*,times,radii):
    """Differentiate actual corrected field polynomials, never the PDE RHS."""
    app=prepared['application'];Et=time_evaluation_matrix(app['times'],times);Er=time_evaluation_matrix(app['radii'],radii)
    Et1=time_evaluation_matrix(app['times'],times,1);Er1=time_evaluation_matrix(app['radii'],radii,1)
    evaluate=lambda A,B,V:np.einsum('ti,rj,ijab->trab',A,B,V,optimize=True)
    V=prepared['nodal_value'];X=nodal_source
    return dict(value=evaluate(Et,Er,V),time=evaluate(Et1,Er,V),radial=evaluate(Et,Er1,V),
        source=None if X is None else evaluate(Et,Er,X),
        time_source=None if X is None else evaluate(Et1,Er,X),
        radial_source=None if X is None else evaluate(Et,Er1,X))
