"""Full18 analytic current coefficients and source-varied unsquared returns.

The caller supplies the actual parent and reference at each stage, with
their independent coefficient tangents. No affine history is manufactured
here. The child total mechanical profile is pp-rp+rc before its wall value
is consumed. The evolution below belongs to the supplied computational
canonical domain; it selects no physical exterior or pole.
"""
from __future__ import annotations
import numpy as np
from scipy.linalg import expm_frechet
from .muon_holomorphic_normal_geometry import (
    _geometry_variables, _fields, _sqrt, holomorphic_geometry_rows,
)
from .muon_continued_action_reality import _higgs_mass_realified
from .muon_native_dirac_hamiltonian import lepton_current_hilbert_representation
from .muon_native_product_factor_graph import lepton_unit_trace_gauge_representation
from .muon_parent_maxwell_full_weak import M
from .muon_parent_retarded_hypercharge import WALL
from .muon_unsquared_forced_boundary_attachment import (
    unsquared_boundary_source_two_jet, attached_current_two_jet,
)


def _finite(value, shape, name):
    a=np.asarray(value,complex)
    if a.shape!=shape or not np.isfinite(a).all():
        raise ValueError(name+' must keep every finite original coordinate')
    return a


def two_term_complex_sum(high,low):
    """Retain the rounding remainder of each real/imaginary two-term sum."""
    h,l=np.asarray(high,complex),np.asarray(low,complex)
    if h.shape!=l.shape or not np.isfinite(h).all()or not np.isfinite(l).all():
        raise ValueError('same finite high/low operands required')
    def add(a,b):
        s=a+b;v=s-a
        return s,(a-(s-v))+(b-v)
    r,rl=add(h.real,l.real);i,il=add(h.imag,l.imag)
    return r+1j*i,rl+1j*il


def _wall_coframe(raw):
    q,v,m,delta,dr,wall,_=_geometry_variables(raw[:100])
    f=_fields(12,q,v,m,wall)
    R=f['A']*f['B']/_sqrt(f['A']**2+f['B']**2)
    U=f['C']*(dr+f['beta'])/f['N']
    N=f['N']*_sqrt(1-U*U)
    return R,N,U


def _profile(raw, direction, points):
    a=holomorphic_geometry_rows(raw[:100],points,connection_only=True)
    names=('connection_lambda','lambda_tau','lambda_rho')
    value=np.array([[row[k].value for k in names]for row in a['rows']])
    first=np.array([[row[k].gradient@direction[:100]for k in names]for row in a['rows']])
    return value,first.transpose(2,0,1)


def holomorphic_current_stage(raw, raw_first, parent_raw, parent_first,
        reference_pair, reference_first, representation, *, side):
    """Bind full18 Hcan, coframe, wall vertices and all supplied first jets.

    raw_first has (268,ndir). Parent/reference directions are mandatory,
    including an explicitly held reference. The four realified Higgs
    entries retain HR+iHI and HR-iHI as independent analytic placements.
    """
    x=_finite(raw,(268,),'stage raw');dx=np.asarray(raw_first,complex)
    if dx.ndim!=2 or dx.shape[0]!=268 or not dx.shape[1]:
        raise ValueError('explicit complete raw268 source directions required')
    k=dx.shape[1];dx=_finite(dx,(268,k),'stage direction')
    p=_finite(parent_raw,(268,),'same-stage parent')
    dp=_finite(parent_first,(268,k),'same-stage parent direction')
    refs=_finite(reference_pair,(2,268),'same-stage reference pair')
    drefs=_finite(reference_first,(2,268,k),'same-stage reference directions')
    if side not in ('parent','child'):raise ValueError('original parent/child orientation required')
    W=_finite(representation['wall_trace_map'],(5,4,80),'original full20 wall map')
    rho=np.asarray(representation['rho'],float)
    if rho.ndim!=1 or not len(rho)or not np.isfinite(rho).all():
        raise ValueError('all declared original radial source points required')
    points=np.r_[rho,WALL]
    own,down=_profile(x,dx,points)
    if side=='parent':total,dtotal=own,down
    else:
        pp,dpp=_profile(p,dp,points)
        rp,drp=_profile(refs[0],drefs[0],points)
        rc,drc=_profile(refs[1],drefs[1],points)
        total,dtotal=pp-rp+rc,dpp-drp+drc
    R,N,U=_wall_coframe(x)
    dR=R.gradient@dx[:100];dN=N.gradient@dx[:100]
    independent=np.einsum('acj,j->ac',W,x[100:180])
    dindependent=np.einsum('acj,jk->kac',W,dx[100:180])
    connection=independent.copy();connection[2:]+=M*(total[-1,0]-1)
    dconnection=dindependent.copy();dconnection[:,2:]+=M[None]*dtotal[:,-1,0,None,None]
    G=lepton_unit_trace_gauge_representation()['generators']
    h=lepton_current_hilbert_representation();alpha=h['alpha']
    space=np.einsum('ac,cij->aij',connection[2:],G)
    dspace=np.einsum('kac,cij->kaij',dconnection[:,2:],G)
    temporal=np.einsum('c,cij->ij',connection[0],G)/N.value
    dtemporal=np.einsum('kc,cij->kij',dconnection[:,0],G)/N.value-temporal[None]*dN[:,None,None]/N.value
    kinetic=-1j*np.einsum('aij,ajl->il',alpha,space)+1.5*h['gamma5']
    dkinetic=-1j*np.einsum('aij,kajl->kil',alpha,dspace)
    mass=_higgs_mass_realified(x[260:264])
    dmass=np.array([_higgs_mass_realified(d)for d in dx[260:264].T])
    body=kinetic/R.value+mass-1j*temporal
    dbody=dkinetic/R.value-kinetic[None]*dR[:,None,None]/R.value**2+dmass-1j*dtemporal
    vertices=np.zeros((24,18,18),complex);dv=np.zeros((k,24,18,18),complex)
    vertices[:4]=-1j*G/N.value
    dv[:,:4]=-vertices[None,:4]*dN[:,None,None,None]/N.value
    for a in range(3):
        sl=slice(8+4*a,12+4*a)
        vertices[sl]=-1j*np.einsum('ij,cjl->cil',alpha[a],G)/R.value
        dv[:,sl]=-vertices[None,sl]*dR[:,None,None,None]/R.value
    vertices[20:]=np.array([_higgs_mass_realified(e)for e in np.eye(4)])
    return dict(Hcan=body,Hcan_first=dbody,R4=np.array(R.value),R4_first=dR,
        induced_lapse=np.array(N.value),induced_lapse_first=dN,wall_U=np.array(U.value),
        wall_U_first=U.gradient@dx[:100],fixed_Y_mass=mass,fixed_Y_mass_first=dmass,
        full_wall_connection=connection,full_wall_connection_first=dconnection,
        independent_wall_connection=independent,independent_wall_connection_first=dindependent,
        temporal_connection=temporal,temporal_connection_first=dtemporal,
        spatial_connection=space,spatial_connection_first=dspace,
        source_profile_points=points,total_profile=total,total_profile_first=dtotal,
        own_profile=own,own_profile_first=down,
        canonical_wall_current_vertices=vertices,canonical_wall_current_vertices_first=dv,
        spatial_principal_alpha_over_R=alpha/R.value,
        spatial_principal_alpha_over_R_first=-alpha[None]*dR[:,None,None,None]/R.value**2,
        parent_reference_supplied_at_actual_stage=True,source_image_projected=False,
        coefficient_direction_conjugated=False,mechanical_profile_count=1,
        angular_scope='homogeneous full18 coefficient germ; principal angular factor exported, no shell loop selected',
        physical_exterior_pole_or_LSZ_selected=False)


def _component(U,r,L,c,dU,dr,dL,dc):
    return dict(trace=U,source_return=r,initial_target=L,direct_current=c,
        trace_first=dU,source_return_first=dr,initial_target_first=dL,direct_current_first=dc)


def compose_current_components(left, right):
    """Apply the later component after the earlier one, without conjugation."""
    a,b=left,right;U,r,L,c=(a[n]for n in ('trace','source_return','initial_target','direct_current'))
    V,s,T,d=(b[n]for n in ('trace','source_return','initial_target','direct_current'))
    dU,dr,dL,dc=(a[n+'_first']for n in ('trace','source_return','initial_target','direct_current'))
    dV,ds,dT,dd=(b[n+'_first']for n in ('trace','source_return','initial_target','direct_current'))
    return _component(U@V,U@s+r,T+L@V,d+L@s+c,
        dU@V+U@dV,dU@s+U@ds+dr,dT+dL@V+L@dV,dd+dL@s+L@ds+dc)


def source_varied_unsquared_current_chain(coordinate_steps,lapse,body,right_source,
        literal_left,direct_density,*,coordinate_steps_first,lapse_first,body_first,
        right_source_first,literal_left_first,direct_density_first,energy,energy_first):
    """Exact constant-stage unsquared transfer, source return and target jets.

    In coordinate t, A=(iN)^-1 d_t+H, A chi=J and the target is
    integral iN(L chi+D)dt. The envelope energy enters B=iN(E-H).
    All supplied clock/body/current variations precede integration. A
    3d exponential computes the entire moments; no source-rank inverse,
    local pole division, or positive squared operator is introduced.
    """
    dt=np.asarray(coordinate_steps,complex);N=np.asarray(lapse,complex);H=np.asarray(body,complex)
    if dt.ndim!=1 or not len(dt)or N.shape!=dt.shape or H.ndim!=3 or H.shape[0]!=len(dt)or H.shape[1]!=H.shape[2]:
        raise ValueError('complete same-stage coordinate steps/coframe/body required')
    q,d=len(dt),H.shape[-1];dh=np.asarray(coordinate_steps_first,complex)
    if dh.ndim!=2 or dh.shape[0]!=q or not dh.shape[1]:raise ValueError('explicit step source jets required')
    k=dh.shape[1];J=np.asarray(right_source,complex);L=np.asarray(literal_left,complex)
    if J.ndim!=3 or J.shape[:2]!=(q,d)or L.ndim!=3 or L.shape[0]!=q or L.shape[2]!=d:
        raise ValueError('independent original right source and literal left target required')
    nr,nl=J.shape[2],L.shape[1]
    arrays=[(dt,(q,),'steps'),(N,(q,),'lapse'),(H,(q,d,d),'body'),(dh,(q,k),'step jets'),
        (lapse_first,(q,k),'lapse jets'),(body_first,(q,k,d,d),'body jets'),
        (J,(q,d,nr),'right source'),(L,(q,nl,d),'literal target'),(direct_density,(q,nl,nr),'direct density'),
        (right_source_first,(q,k,d,nr),'right source jets'),(literal_left_first,(q,k,nl,d),'literal target jets'),
        (direct_density_first,(q,k,nl,nr),'direct density jets'),(energy_first,(k,),'energy jets')]
    vals=[_finite(*a)for a in arrays]
    dt,N,H,dh,dN,dH,J,L,D,dJ,dL,dD,dE=vals;E=complex(energy)
    if not np.isfinite(E)or np.any(dt==0)or np.any(N==0):raise ValueError('finite nonzero original clocks required')
    U=np.eye(d,dtype=complex);r=np.zeros((d,nr),complex);T=np.zeros((nl,d),complex);c=np.zeros((nl,nr),complex)
    base=_component(U,r,T,c,np.zeros((k,d,d),complex),np.zeros((k,d,nr),complex),np.zeros((k,nl,d),complex),np.zeros((k,nl,nr),complex))
    for j in range(q):
        B=1j*N[j]*(E*np.eye(d)-H[j]);F=1j*N[j]*J[j];left=1j*N[j]*L[j];direct=1j*N[j]*D[j]
        dB=1j*dN[j,:,None,None]*(E*np.eye(d)-H[j])+1j*N[j]*(dE[:,None,None]*np.eye(d)-dH[j])
        dF=1j*dN[j,:,None,None]*J[j]+1j*N[j]*dJ[j]
        dleft=1j*dN[j,:,None,None]*L[j]+1j*N[j]*dL[j]
        ddirect=1j*dN[j,:,None,None]*D[j]+1j*N[j]*dD[j]
        A=np.zeros((3*d,3*d),complex);A[:d,:d]=B;A[:d,d:2*d]=np.eye(d);A[d:2*d,2*d:]=np.eye(d)
        Z=dt[j]*A;derivatives=[];expZ=None
        for a in range(k):
            da=np.zeros_like(A);da[:d,:d]=dB[a]
            value,deriv=expm_frechet(Z,dh[j,a]*A+dt[j]*da)
            if expZ is None:expZ=value
            derivatives.append(deriv)
        dx=np.array(derivatives);V=expZ[:d,:d];M0=expZ[:d,d:2*d];M1=expZ[:d,2*d:]
        dV=dx[:,:d,:d];dM0=dx[:,:d,d:2*d];dM1=dx[:,:d,2*d:]
        stage=_component(V,M0@F,left@M0,left@M1@F+direct*dt[j],dV,
            dM0@F+M0@dF,dleft@M0+left@dM0,
            dleft@M1@F+left@dM1@F+left@M1@dF+ddirect*dt[j]+direct*dh[j,:,None,None])
        base=compose_current_components(stage,base)
    base.update(analytic_left_conjugated=False,proper_clock_span=np.array(np.sum(1j*N*dt)),
        proper_clock_span_first=np.sum(1j*(dN*dt[:,None]+N[:,None]*dh),axis=0),
        coordinate_source_equation='d_t chi=iN[(E-Hcan)chi+J]',
        fixed_constant_stage_representation=True,physical_event_exterior_pole_or_LSZ_selected=False)
    return base


def attach_current_chain_first(chain,boundary,boundary_first):
    """Consume the existing Gamma/f algebra on explicitly supplied rows.

    A dummy independent zero direction only extracts each first derivative
    from the already-owned two-jet algebra. No physical mixed derivative
    is assigned zero or exported. An ordinary inverse is permitted only
    off a selected pole; the physical residue application remains separate.
    """
    keys=('initial_boundary','final_boundary','boundary_source','initial_target','final_target','direct_current')
    if set(boundary)!=set(keys)or set(boundary_first)!=set(keys):
        raise ValueError('all original boundary, source and target rows/jets required')
    base=dict(boundary,trace=chain['trace'],source_return=chain['source_return'])
    base['initial_target']=np.asarray(base['initial_target'],complex)+chain['initial_target']
    base['direct_current']=np.asarray(base['direct_current'],complex)+chain['direct_current']
    zero={n:np.zeros_like(a)for n,a in base.items()};answers=[];apps=[]
    for j in range(len(chain['trace_first'])):
        first={n:np.asarray(boundary_first[n],complex)[j].copy()for n in keys}
        first.update(trace=chain['trace_first'][j],source_return=chain['source_return_first'][j])
        first['initial_target']+=chain['initial_target_first'][j]
        first['direct_current']+=chain['direct_current_first'][j]
        app=unsquared_boundary_source_two_jet(base,(first,zero),zero)
        apps.append(app);answers.append(attached_current_two_jet(app))
    return dict(boundary_matrix=apps[0]['boundary_matrix'],forced_boundary_source=apps[0]['forced_boundary_source'],
        effective_literal_left=apps[0]['effective_literal_left'],direct_source_return_current=apps[0]['direct_source_return_current'],
        boundary_matrix_first=np.array([a['boundary_matrix_first'][0]for a in apps]),
        forced_boundary_source_first=np.array([a['forced_boundary_source_first'][0]for a in apps]),
        current=answers[0]['current'],current_first=np.array([a['current_first'][0]for a in answers]),
        initial_trace=answers[0]['initial_trace'],analytic_transpose_boundary_adjoint=answers[0]['analytic_transpose_boundary_adjoint'],
        independent_transpose_current=answers[0]['independent_transpose_current'],
        independent_transpose_current_first=np.array([a['first_transpose_current'][0]for a in answers]),
        original_boundary_rows=answers[0]['boundary_original_rows'],original_transpose_rows=answers[0]['boundary_transpose_rows'],
        physical_mixed_derivative_not_assigned=True,physical_exterior_relation_or_pole_selected=False)
