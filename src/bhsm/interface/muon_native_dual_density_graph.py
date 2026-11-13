"""Executed left-density/domain map for the already-reflected weak graph.

This compares the original chronological Clifford left principal 1/ws
with geometric-L2 density on the SAME principal. It does not convert
the earlier Lorentz analytic principal 1/w into 1/ws. The candidate
ordinary geometric-L2 trace domain and this transported analytic left
domain are retained as distinct action realizations.
"""
from __future__ import annotations
import numpy as np
from .muon_transported_native_pairing import coframe_pairing_transition
from .muon_continued_coefficient_first_germ import geometry_first_germ
from .muon_chronological_clifford_graph import _angular_operators,_rows


def density_transported_left_factor(reflected_body,p,d,transition,reflected_clock):
    """Transport phi_new=rho*phi_old including its derivative and connection."""
    Hs=np.asarray(reflected_body,complex);rho=complex(transition['dual_density_ratio'])
    rate=complex(transition['logarithmic_dual_density_derivative'])
    contact=complex(transition['analytic_left_density_connection'])
    ws=complex(reflected_clock);I=np.eye(len(Hs))
    new_value=rho*p;new_derivative=rho*(d+rate*p)
    return new_derivative*I/ws+new_value*(Hs+contact*I)


def density_graph_action_comparison(quadrature,transitions,*,temporal_nodes,
        angular_derivatives,alpha):
    """Both weak square and acted-source numerator after exact left transport.

    The current source Xi is a full matrix vertex, not a weak source
    moment substituted for a function. Source placement is evaluated
    BEFORE integration and no Riesz projection is assumed. Same scalar
    and gauge tangent coordinates occur in both action branches.
    """
    if len(quadrature)!=len(transitions):raise ValueError('all original density/contact rows required')
    h=np.asarray(angular_derivatives).shape[-1];width=6*h;n=temporal_nodes-1
    old=[np.zeros((n,width,width),complex),np.zeros((n-1,width,width),complex),np.zeros((n-1,width,width),complex)]
    new=[np.zeros_like(x)for x in old]
    maxima=dict(weak_local_absolute=0.,weak_local_relative=0.,current_local_absolute=0.,
        acted_numerator_local_absolute=0.,acted_numerator_local_relative=0.)
    for q,tr in zip(quadrature,transitions):
        A,As=_angular_operators(q,angular_derivatives,alpha)
        m,w,ws=(complex(q[k])for k in('measure','right_clock','reflected_clock'))
        mu=tr['native_geometric_measure'];rho=tr['dual_density_ratio']
        X=np.asarray(q['vertices'],complex)
        if X.shape!=(24,6,6):raise ValueError('all gauge and induced-H vertices required')
        Xi=np.array([np.kron(x,np.eye(h))for x in X]);I=np.eye(width)
        rows=_rows(q,temporal_nodes)
        for j,pj,dj in rows:
            lo=dj*I/ws+pj*As
            ln=density_transported_left_factor(As,pj,dj,tr,ws)
            for k,pk,dk in rows:
                right=dk*I/w+pk*A
                vo=m*lo@right;vn=mu*ln@right;diff=np.max(abs(vo-vn))
                maxima['weak_local_absolute']=max(maxima['weak_local_absolute'],float(diff))
                maxima['weak_local_relative']=max(maxima['weak_local_relative'],float(diff)/(float(np.max(abs(vo)))+1e-300))
                if j==k:index,position=0,j
                elif k==j+1:index,position=1,j
                else:index,position=2,k
                old[index][position]+=vo;new[index][position]+=vn
                co=m*pj*pk*Xi;cn=mu*(rho*pj)*pk*Xi
                maxima['current_local_absolute']=max(maxima['current_local_absolute'],float(np.max(abs(co-cn))))
                bo=m*np.einsum('ij,cjk->cik',lo,Xi)*pk
                bn=mu*np.einsum('ij,cjk->cik',ln,Xi)*pk
                maxima['acted_numerator_local_absolute']=max(maxima['acted_numerator_local_absolute'],float(np.max(abs(bo-bn))))
                maxima['acted_numerator_local_relative']=max(maxima['acted_numerator_local_relative'],
                    float(np.max(abs(bo-bn)))/(float(np.max(abs(bo)))+1e-300))
    maxima['integrated_original_row_absolute']=max(float(np.max(abs(a-b)))for a,b in zip(old,new))
    maxima['integrated_original_row_relative']=max(float(np.max(abs(a-b)))/(float(np.max(abs(a)))+1e-300)for a,b in zip(old,new))
    return dict(original_blocks=tuple(old),transported_left_blocks=tuple(new),residuals=maxima,
        compared_left_principal='the original reflected chronological 1/ws, not Lorentz analytic 1/w',
        source_tangent_conjugated=False,current_Riesz_projection_used=False,
        ordinary_native_shared_left_trace_domain_identified_with_transported_domain=False)


def density_graph_endpoint_maps(quadrature,provenance,*,temporal_nodes):
    """Actual one-sided coframe/dual values and corner transfer on every edge.

    Connector geometry is the same affine q/n germ as the original
    coefficient producer. Source cells retain their declared unit clock.
    The old analytic left field is continuous; hence the transported
    left field jumps by rho_plus/rho_minus. Original conormal balance is
    rho_minus*Pi_native_minus=rho_plus*Pi_native_plus. These are domain
    maps, not an exterior or OS-state selection.
    """
    provenance=np.asarray(provenance,complex)
    if len(provenance)!=len(quadrature):raise ValueError('all actual edge clock provenance required')
    values=np.zeros((temporal_nodes-1,2,6),complex);filled=np.zeros(temporal_nodes-1,bool)
    for q,pr in zip(quadrature,provenance):
        j=q['rows'][0][0]
        if filled[j]:continue
        p=complex(q['rows'][1][1]);d=complex(q['rows'][1][2]);kind=int(pr[6].real);slope=complex(pr[8])
        for end in(0,1):
            if kind==0:w=ws=1.+0j
            else:
                shift=(end-p)/d*slope;clocks=[]
                for raw_key,delta in(('raw_fields',shift),('raw_fields_sharp',shift.conjugate())):
                    raw=q[raw_key].copy();raw[:37]+=delta*raw[37:74];raw[98]+=delta*raw[99]
                    clocks.append(geometry_first_germ(raw,np.zeros_like(raw))['value']['N'])
                w=1j*clocks[0]*slope;ws=-1j*clocks[1]*slope.conjugate()
            tr=coframe_pairing_transition(w,ws,w)
            norm=tr['native_coframe_norm'];rho=tr['dual_density_ratio']
            values[j,end]=(w,ws,norm,rho,w/ws,norm/ws)
        filled[j]=True
    if not np.all(filled):raise ValueError('no omitted chronological interval allowed')
    minus=values[:-1,1,3];plus=values[1:,0,3]
    return dict(edge_clock_density_and_conormal=values,
        edge_columns=('right_clock','reflected_clock','native_metric_norm','rho',
            'original_reflected_conormal_factor','native_geometric_conormal_factor'),
        internal_left_trace_transfer=plus/minus,
        internal_native_conormal_return=minus/plus,
        left_trace_equation='bar_native_plus=(rho_plus/rho_minus)*bar_native_minus when bar_original is continuous',
        conormal_equation='rho_minus*Pi_native_minus=rho_plus*Pi_native_plus',
        initial_right_trace_removed=True,final_natural_weak_row_retained=True,
        complete_exterior_reset_or_OS_domain_selected=False)
