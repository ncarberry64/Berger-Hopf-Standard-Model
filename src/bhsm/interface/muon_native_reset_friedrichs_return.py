"""Reset trace and Friedrichs form-core returns on the original native pencil.

AE2 owns the common-frame trace graph and opposite outward fluxes, with no
fermion seam action.  The canonical-stop owner selects the Friedrichs form
closure.  Here its Dirichlet core is evaluated on an existing finite
exhaustion edge; that edge is never reclassified as a physical stop.
The spectral mass pencil and acted-source numerator remain explicit.
"""
from __future__ import annotations
import numpy as np
from .muon_chronological_spectral_blocks import (
    chronological_spectral_factor, chronological_source_solve,
    chronological_source_residual, chronological_selected_inverse)
from .muon_chronological_clifford_graph import _angular_operators
from .action_extension_global_spin_reset_ae2 import validate_unitary


def _pencil(blocks, z):
    z=complex(z)
    if not np.isfinite(z):raise ValueError('finite original spectral point required')
    return tuple(np.asarray(blocks['K_'+k],complex)-z*np.asarray(blocks['M_'+k],complex)
        for k in ('diagonal','upper','lower'))


def chain_apply(diagonal,upper,lower,x):
    """Apply independent original directed rows, including both endpoint rows."""
    D,U,L=map(np.asarray,(diagonal,upper,lower));x=np.asarray(x,complex)
    if len(x)!=len(D):raise ValueError('all original chronological coordinates required')
    y=np.einsum('nij,nj...->ni...',D,x)
    y[:-1]+=np.einsum('nij,nj...->ni...',U,x[1:])
    y[1:]+=np.einsum('nij,nj...->ni...',L,x[:-1])
    return y


def fixed_form_core_source_two_jet(pencil,rhs,*,first_pencils=None,first_sources=None,
        mixed_pencil=None,mixed_source=None):
    """Differentiate the selected terminal Dirichlet core BEFORE inversion.

    The last coefficient is removed, not assigned a finite Weyl load.
    All remaining original rows are solved.  Fixed numerical trace projector
    scope is explicit; moving physical-stop/domain jets are not set to zero.
    F x_AB=b_AB-F_AB x-F_A x_B-F_B x_A keeps both ordered insertions.
    """
    D,U,L=map(np.asarray,pencil);b=np.asarray(rhs,complex)
    if len(D)<2 or len(b)!=len(D):raise ValueError('complete finite chain and source required')
    f=chronological_spectral_factor(D[:-1],U[:-1],L[:-1])
    def solve(source):
        ans=np.zeros_like(b);ans[:-1]=np.asarray(chronological_source_solve(f,source[:-1]));return ans
    x=solve(b);res=chain_apply(D,U,L,x)-b
    out=dict(solution=x,original_row_residual=res,terminal_reaction=res[-1],
        fixed_numerical_trace_projector=True,moving_physical_stop_jet_evaluated=False)
    if first_pencils is None:
        if any(v is not None for v in(first_sources,mixed_pencil,mixed_source)):
            raise ValueError('first pencils required with source/mixed jets')
        return out
    if len(first_pencils)!=2:raise ValueError('both ordered source directions required')
    bs=(np.zeros_like(b),np.zeros_like(b))if first_sources is None else first_sources
    if len(bs)!=2:raise ValueError('both first source contacts required')
    first=[solve(np.asarray(s)-chain_apply(*p,x))for p,s in zip(first_pencils,bs)]
    pab=tuple(np.zeros_like(a)for a in(D,U,L))if mixed_pencil is None else mixed_pencil
    bab=np.zeros_like(b)if mixed_source is None else np.asarray(mixed_source)
    xab=solve(bab-chain_apply(*pab,x)-chain_apply(*first_pencils[0],first[1])
        -chain_apply(*first_pencils[1],first[0]))
    out.update(first_solutions=np.asarray(first),mixed_solution=xab,
        mixed_original_row_residual=chain_apply(D,U,L,xab)+chain_apply(*pab,x)
            +chain_apply(*first_pencils[0],first[1])+chain_apply(*first_pencils[1],first[0])-bab,
        direct_contact_and_both_inverse_orders_retained=True)
    return out


def terminal_friedrichs_source_return(blocks,rhs,*,spectral_parameter):
    """Execute full-minus-core forced return without substituting S(0) for heat.

    x_D=x_N-G_:F G_FF^-1 x_N(F) enforces the owned Dirichlet form core.
    Its independent restricted original-row solve is also evaluated.  The
    returned reaction is the final weak equation, not an invented Neumann
    condition or independent terminal datum.
    """
    D,U,L=_pencil(blocks,spectral_parameter);b=np.asarray(rhs,complex)
    f=chronological_spectral_factor(D,U,L)
    x=np.asarray(chronological_source_solve(f,b));n,d,_=D.shape
    bf=np.zeros((n,d,d),complex);bf[-1]=np.eye(d)
    GF=np.asarray(chronological_source_solve(f,bf));Gff=GF[-1]
    amplitude=np.linalg.solve(Gff,x[-1]);forced=np.einsum('nij,j...->ni...',GF,amplitude)
    xd=x-forced;direct=fixed_form_core_source_two_jet((D,U,L),b)
    res=chain_apply(D,U,L,xd)-b
    return dict(natural_solution=x,form_core_solution=xd,forced_final_face_return=forced,
        independent_form_core_solution=direct['solution'],final_face_Green=Gff,
        final_return_amplitude=amplitude,form_core_original_row_residual=res,
        natural_original_row_residual=np.asarray(chronological_source_residual(f,x,b)),
        final_reaction=res[-1],terminal_Dirichlet_trace=xd[-1],
        independent_restriction_defect=xd-direct['solution'],
        original_spectral_parameter=complex(spectral_parameter),
        spectral_mass_and_forced_source_return_retained=True,
        finite_edge_identified_with_physical_stop=False,
        zero_frequency_Schur_identified_with_heat_return=False)


def birth_action_and_numerator(quadrature,*,birth_trace_node,temporal_nodes,
        angular_derivatives,alpha):
    """Integrate the two arm diagonal forms and A_sharp birth-function source.

    The source is the complete spin/angular coefficient of the birth FE hat.
    A_sharp acts before quadrature.  This is distinct from a coefficient-dual
    delta load; neither is labeled a pole/LSZ or Pauli source.
    """
    if type(birth_trace_node)is not int or not 0<birth_trace_node<temporal_nodes-1:
        raise ValueError('actual interior parent/child birth trace required')
    h=np.asarray(angular_derivatives).shape[-1];d=6*h;I=np.eye(d)
    parentK=np.zeros((d,d),complex);childK=np.zeros_like(parentK)
    parentM=np.zeros_like(parentK);childM=np.zeros_like(parentK)
    numerator=np.zeros((temporal_nodes-1,d,d),complex)
    for q in quadrature:
        rows=q['rows'];birth=[(p,v)for j,p,v in rows if j==birth_trace_node]
        if not birth:continue
        pb,db=map(complex,birth[0]);A,As=_angular_operators(q,angular_derivatives,alpha)
        m,w,ws=(complex(q[k])for k in('measure','right_clock','reflected_clock'))
        kp=m*(db*I/ws+pb*As)@(db*I/w+pb*A);mp=m*pb*pb*I
        if rows[-1][0]<=birth_trace_node:parentK+=kp;parentM+=mp
        elif rows[0][0]>=birth_trace_node:childK+=kp;childM+=mp
        else:raise ValueError('original cell cannot cross the owned birth trace')
        for j,p,v in rows:
            if j:numerator[j-1]+=m*(complex(v)*I/ws+complex(p)*As)*pb
    return dict(parent_birth_K=parentK,child_birth_K=childK,parent_birth_M=parentM,
        child_birth_M=childM,acted_birth_function_numerator=numerator,
        source_Riesz_projection_used=False,physical_external_source_identified=False)


def reset_birth_schur(blocks,birth_forms,*,birth_trace_node,spectral_parameter,
        reset_lift=None,terminal_form_core=False):
    """Apply AE2 value/variation and opposite-conormal graph before elimination.

    Parent and child Schur forms act on outward duals. Their sum is
    S_parent+U^dagger S_child U; hence the source-free seam equation is
    Pi_parent+U^dagger Pi_child=0, equivalent to the owned opposite-normal
    flux graph. No independent fermion boundary action is inserted.
    """
    D,U,L=_pencil(blocks,spectral_parameter);b=birth_trace_node-1;d=len(D[0]);z=complex(spectral_parameter)
    if not 0<=b<len(D)-1:raise ValueError('interior birth in the original free-node order required')
    R=np.eye(d)if reset_lift is None else validate_unitary(reset_lift)
    if R.shape!=(d,d):raise ValueError('actual same-representation reset lift required')
    pD=D[:b+1].copy();cD=D[b:].copy()
    pD[-1]=birth_forms['parent_birth_K']-z*birth_forms['parent_birth_M']
    cD[0]=birth_forms['child_birth_K']-z*birth_forms['child_birth_M']
    if not np.allclose(pD[-1]+cD[0],D[b],rtol=2e-14,atol=1e-12):
        raise ValueError('all original parent/child birth action density required')
    cu=U[b:].copy();cl=L[b:].copy()
    if terminal_form_core:
        if len(cD)<2:raise ValueError('child interior before terminal core required')
        cD,cu,cl=cD[:-1],cu[:-1],cl[:-1]
    pf=chronological_spectral_factor(pD,U[:b],L[:b]);cf=chronological_spectral_factor(cD,cu,cl)
    Gp=chronological_selected_inverse(pf)['diagonal'][-1]
    Gc=chronological_selected_inverse(cf)['diagonal'][0]
    Sp=np.linalg.solve(Gp,np.eye(d));Sc=np.linalg.solve(Gc,np.eye(d))
    S=Sp+R.conj().T@Sc@R;phi=np.linalg.solve(S,np.eye(d))
    cp=R@phi;pip=Sp@phi;pic=Sc@cp
    return dict(parent_outward_Schur=Sp,child_outward_Schur=Sc,
        reset_glued_birth_Schur=S,birth_Green=phi,reset_lift=R,
        parent_trace=phi,child_trace=cp,parent_outward_dual=pip,child_outward_dual=pic,
        trace_graph_residual=cp-R@phi,
        sourced_opposite_normal_residual=pip+R.conj().T@pic-np.eye(d),
        independent_fermion_seam_action_added=False,
        nonconstant_base_pullback_or_selected_exterior_domain_proved=False)
