"""Transported native factor, independent source dual and coframe pairing.

The original holomorphic measure is retained alongside the reflected
coframe norm. The latter constructs a geometric-L2 closed form on the
declared real parameter graph. It is not a theorem identifying that
finite graph with the microscopic exterior/relative native realization.
The old analytic square is recovered by the dual density connection,
so a density replacement is never described as a coordinate repair.
"""
from __future__ import annotations
import numpy as np
from .muon_native_dirac_hamiltonian import lepton_current_hilbert_representation
from .muon_native_product_factor_graph import lepton_unit_trace_gauge_representation
from .muon_continued_action_reality import _higgs_mass_realified
from .muon_piecewise_euclidean_action import FAMILY_INDICES


def transported_native_vertices(radius,lapse,reflected_radius,reflected_lapse,*,family=None):
    """Independent complexified real-action vertices; source coefficients fixed.

    Native coordinates are a_tau=-i At_L and a_tau_sharp=+i At_L_sharp.
    The adjoint native temporal matrix is -G/Nsharp. Thus BOTH transported
    At_L matrices are -iG/Nbranch. No tangent coefficient is conjugated.
    """
    co=np.asarray([radius,lapse,reflected_radius,reflected_lapse],complex)
    if np.any(co==0) or not np.isfinite(co).all():raise ValueError('all four executed coframe coefficients required')
    if family is not None and(type(family)is not int or family not in(0,1,2)):
        raise ValueError('family is None or the exact retained index')
    R,N,Rs,Ns=co;rep=lepton_current_hilbert_representation()
    G=lepton_unit_trace_gauge_representation()['generators']
    spatial=-1j*np.einsum('aij,cjk->acik',rep['alpha'],G)
    scalar=np.array([_higgs_mass_realified(e)for e in np.eye(4)])
    right=np.zeros((24,18,18),complex);sharp=np.zeros_like(right)
    right[:4]=G/N;sharp[:4]=-G/Ns
    right[8:20]=(spatial/R).reshape(12,18,18)
    sharp[8:20]=(spatial/Rs).reshape(12,18,18)
    right[20:]=scalar;sharp[20:]=scalar.conj().transpose(0,2,1)
    native_right=right.copy();native_sharp=sharp.copy()
    right[:4]*=-1j;sharp[:4]*=1j
    fi=np.arange(18)if family is None else FAMILY_INDICES[family]
    take=lambda a:a[:,fi][:,:,fi]
    return dict(vertices=take(right),vertices_sharp=take(sharp),
        native_vertices=take(native_right),native_vertices_sharp=take(native_sharp),
        native_coordinate_right_rotation=-1j,native_coordinate_reflected_rotation=1j,
        family_indices=fi,source_coefficients_conjugated=False)


def independent_native_source_images(source_wall,source_H,*,radius,lapse,
        reflected_radius=None,reflected_lapse=None,family=None,transport_lorentz_coordinates=False):
    """Contract identical complex coefficient tangents with fixed action duals.

    source_wall has (...,5,4,h), source_H (...,4,h). The leading axes and
    full angular images are retained. This fixes the real-only frozen
    helper's conjugate-of-source shortcut without changing its old bytes.
    """
    wall=np.asarray(source_wall,complex);H=np.asarray(source_H,complex)
    if wall.ndim<3 or wall.shape[-3:-1]!=(5,4) or H.shape!=wall.shape[:-3]+(4,wall.shape[-1]):
        raise ValueError('same full source leading axes and angular images required')
    Rs=complex(radius) if reflected_radius is None else reflected_radius
    Ns=complex(lapse) if reflected_lapse is None else reflected_lapse
    a=transported_native_vertices(radius,lapse,Rs,Ns,family=family)
    keys=('vertices','vertices_sharp') if transport_lorentz_coordinates else ('native_vertices','native_vertices_sharp')
    coefficients=np.concatenate((wall.reshape(wall.shape[:-3]+(20,wall.shape[-1])),H),axis=-2)
    X=[np.einsum('...ch,cij->...hij',coefficients,a[k])for k in keys]
    return dict(Xi=X[0],Xisharp=X[1],source_coefficients_conjugated=False,
        source_coordinate='material Lorentz At_L' if transport_lorentz_coordinates else 'native real a_tau coordinates',
        electric_charge_added_again=False,full_angular_image_retained=True)


def coframe_pairing_transition(right_clock,reflected_clock,holomorphic_measure,*,
        right_clock_derivative=0j,reflected_clock_derivative=0j):
    """Derive the reflected coframe norm and exact dual-density connection.

    Right e=w ds and reflected e_sharp=ws ds give the one-dimensional
    Hermitian metric e_sharp*e. Its positive real norm is sqrt(ws*w), not
    a modified holomorphic action measure. m/w is the original reference
    quadrature measure. The original analytic action is recovered after
    bar_old=(mu/m)bar_native by ADDING -rho'/rho/ws to its left body.
    """
    w,ws,m,wd,wsd=map(complex,(right_clock,reflected_clock,holomorphic_measure,
        right_clock_derivative,reflected_clock_derivative))
    if not np.isfinite([w,ws,m,wd,wsd]).all()or w==0 or ws==0:
        raise ValueError('finite nonzero original clock branches required')
    base=m/w;metric=ws*w;scale=max(abs(metric),1e-300)
    defect=abs(ws-w.conjugate())
    if abs(metric.imag)>2e-12*scale or metric.real<=0 or abs(base.imag)>2e-12*max(abs(base),1e-300) or base.real<=0:
        raise ValueError('independently reflected positive coframe metric and reference quadrature required')
    norm=np.sqrt(metric.real);mu=base.real*norm;rho=m/mu
    logarithmic_rho_derivative=.5*(wd/w-wsd/ws)
    return dict(native_geometric_measure=float(mu),original_holomorphic_measure=m,
        native_coframe_norm=float(norm),reflected_coframe_metric=metric,
        reflection_rounding_defect=float(defect),dual_density_ratio=rho,
        logarithmic_dual_density_derivative=logarithmic_rho_derivative,
        analytic_left_density_connection=-logarithmic_rho_derivative/ws,
        original_measure_changed_by_coordinate_relabeling=False,
        finite_parameter_graph_geometric_pairing_defined=True,
        physical_OS_or_global_relative_domain_identified=False)


def transported_native_quadrature(original_quadrature,*,family,clock_derivatives=None):
    """Construct both original-analytic and reflected-geometric graph rows.

    Original nodes/incidence/right restriction are unchanged. Field and
    source vertices are rotated together. Native conormal is
    (mu/ws) A u; its jumps are the retained interior weak rows.
    An optional clock derivative callback supplies the comparison body's
    density contact; omitted derivatives do not claim it vanishes.
    """
    if type(family)is not int or family not in(0,1,2):raise ValueError('exact retained family index required')
    fi=FAMILY_INDICES[family];native=[];transitions=[]
    for index,q in enumerate(original_quadrature):
        deriv=(0j,0j)if clock_derivatives is None else clock_derivatives(index,q)
        tr=coframe_pairing_transition(q['right_clock'],q['reflected_clock'],q['measure'],
            right_clock_derivative=deriv[0],reflected_clock_derivative=deriv[1])
        v=transported_native_vertices(q['R'],q['N'],q['Rsharp'],q['Nsharp'],family=family)
        # The coframe transport a_tau=-i At_L makes these precisely Hcan,
        # while the reflected a_tau=+i At_Lsharp gives the independent dual.
        H=q['H18'][np.ix_(fi,fi)];Hs=q['Hsharp18'][np.ix_(fi,fi)]
        native.append(dict(q,H=H,Hsharp=Hs,measure=tr['native_geometric_measure'],
            vertices=v['vertices'],vertices_sharp=v['vertices_sharp'],
            original_holomorphic_measure=q['measure'],dual_density_ratio=tr['dual_density_ratio'],
            native_conormal_factor=tr['native_geometric_measure']/q['reflected_clock'],
            original_conormal_factor=q['measure']/q['reflected_clock']))
        transitions.append(tr)
    return dict(quadrature=native,pairing_transitions=transitions,family_indices=fi,
        original_holomorphic_pencil_is_this_native_square=False,
        clock_density_comparison_derivatives_available=clock_derivatives is not None,
        complete_reset_exterior_or_relative_domain_identified=False)


def finite_native_form_lower_comparison(quadrature,*,temporal_nodes,
        angular_derivatives,alpha):
    """Finite quadrature comparison for the reflected geometric-L2 form.

    With only the initial trace removed the scalar derivative stiffness
    is a chain of springs k_e. Its inverse is exactly
    (Kd^-1)_ij=sum(e<min(i,j))1/k_e. A row-norm bound on Kd^-1
    and the scalar mass gives a derivative-form Rayleigh lower bound.
    The triangle inequality then subtracts the full body operator norm.
    The returned binary arithmetic is a comparison, not an outward
    certificate or a bound on an unsampled continuum realization.
    """
    from .muon_chronological_clifford_graph import _angular_operators
    if type(temporal_nodes)is not int or temporal_nodes<2:
        raise ValueError('the complete initial-only finite trace domain is required')
    n=temporal_nodes-1;edges=np.zeros(n);mass_rows=np.zeros(n);body_sup=0.
    reflection_defect=0.
    for q in quadrature:
        w,ws,m=(complex(q[k])for k in('right_clock','reflected_clock','measure'))
        if m.imag!=0 or m.real<=0 or w==0:
            raise ValueError('positive geometric measure and nonzero coframe required')
        rows=q['rows'];(j,p,d),(k,pp,dd)=rows
        if k!=j+1 or not 0<=j<k<temporal_nodes:
            raise ValueError('every original nearest-neighbor trace incidence is required')
        if max(abs(complex(z).imag)for z in(p,pp,d,dd))>1e-14 or not np.isclose(d,-dd,rtol=1e-14,atol=0):
            raise ValueError('real affine cell basis and its exact derivative pair required')
        edges[j]+=m.real*abs(complex(d)/w)**2
        free=[(node-1,float(complex(value).real))for node,value,_ in rows if node!=0]
        for a,pa in free:
            mass_rows[a]+=sum(m.real*pa*pb for _,pb in free)
        A,As=_angular_operators(q,angular_derivatives,alpha)
        body_sup=max(body_sup,float(np.linalg.norm(A,2)))
        reflection_defect=max(reflection_defect,float(np.max(abs(As-A.conj().T))),abs(ws-w.conjugate()))
    if np.any(edges<=0)or np.any(mass_rows<=0):raise ValueError('no omitted or zero-action finite edge allowed')
    cumulative_inverse=np.cumsum(1/edges)
    inverse_row_bound=float(cumulative_inverse.sum());mass_row_bound=float(mass_rows.max())
    derivative_lower=1/(inverse_row_bound*mass_row_bound)
    product_lower=max(np.sqrt(derivative_lower)-body_sup,0.)**2
    return dict(derivative_form_lower_comparison=float(derivative_lower),
        product_form_lower_comparison=float(product_lower),body_operator_norm_sup=body_sup,
        derivative_inverse_row_norm_bound=inverse_row_bound,mass_row_norm_bound=mass_row_bound,
        edge_derivative_stiffness=edges,scalar_mass_row_sum=mass_rows,
        independent_reflection_rounding_defect=reflection_defect,
        comparison_equation='lambda_D>=1/(||Kd^-1||infinity*||M||infinity); lambda_product>=(sqrt(lambda_D)-sup||body||)^2 when positive',
        outward_arithmetic_certificate=False,unsampled_continuum_or_exterior_bound=False)
