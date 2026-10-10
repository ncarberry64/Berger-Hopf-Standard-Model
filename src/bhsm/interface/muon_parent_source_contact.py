"""Parent tangential source/contact on retained M5 cut data.

This muon worked instance evaluates an unreduced local form jet, not a
stratified heat trace. The columns are compactly supported Spin4 x SM16
coordinate probes per family, not the child16 frame or a physical state.
"""
from fractions import Fraction
import numpy as np


def parent_insertion(gamma, coefficients, carrier):
    """i gamma^a Omega_a, without the separate T_b profile/r factor.

    coefficients: (source, right spatial coframe, carrier, m, k).
    Output keeps every angular coefficient and all 64 spin/carrier columns.
    Anti-Hermitian carrier generators and the saved LR Clifford sign are
    inputs; neither the action index nor a family multiplicity enters.
    """
    val = np.einsum('aij,Baemk,euv->Biujvmk',
                    1j * gamma[1:], coefficients, carrier, optimize=True)
    n = coefficients.shape[-1]
    return val.reshape(len(coefficients), 64, 64, n, n)


def local_mixed_contact(xi_z, xi_a):
    """Unweighted Xi_Z^dagger Xi_A + Xi_A^dagger Xi_Z on these probes.

    This is a form derivative at fixed metric/section, not A_ZA=M^-1 K_ZA
    for the full pencil. No heat of this finite restriction is constructed.
    """
    z = xi_z.transpose(0, 1, 3, 4, 2).reshape(8, -1, 64)
    a = xi_a.transpose(0, 1, 3, 4, 2).reshape(8, -1, 64)
    za = np.einsum('Boi,Aoj->BAij', z.conj(), a, optimize=True)
    az = np.einsum('Aoi,Boj->BAij', a.conj(), z, optimize=True)
    return za + az


def computational_profiles(rho):
    """Explicit auxiliary lifting and zero-material-trace H1 test.

    The trace lifting is zero near the pole, one before the test support.
    The test hat vanishes near both radial ends. Neither is a selected
    physical extension or a changed time continuation of the photon.
    """
    rho = np.asarray(rho)
    if rho.shape != (65,) or np.any(np.diff(rho) <= 0):
        raise ValueError('the retained 65-node radial chart is required')
    s = np.clip((rho - rho[8]) / (rho[16] - rho[8]), 0, 1)
    lifting = s**3 * (10 - 15*s + 6*s*s)
    hat = np.maximum(0, np.minimum((rho-rho[24])/(rho[32]-rho[24]),
                                  (rho[40]-rho)/(rho[40]-rho[32])))
    return lifting, hat


def exact_affine_integral(rho, factors):
    """Exact rational integral of products of binary64 affine nodal data.

    Integrates in a unit cell coordinate; the nodal values and cell widths
    are exact Fractions. This bounds neither the history reconstruction nor
    the replacement of the continuous fields by their nodal interpolants.
    """
    r = [Fraction(float(x)) for x in rho]
    total = Fraction(0)
    for i in range(len(r)-1):
        poly = [Fraction(1)]
        for factor in factors:
            a = Fraction(float(factor[i]))
            b = Fraction(float(factor[i+1])) - a
            nxt = [Fraction(0)] * (len(poly)+1)
            for j, value in enumerate(poly):
                nxt[j] += a*value
                nxt[j+1] += b*value
            poly = nxt
        total += (r[i+1]-r[i])*sum((c/Fraction(j+1) for j, c in enumerate(poly)), Fraction(0))
    return total


def gauss_affine_integral(rho, factors):
    """Independent four-point quadrature for degree <= 7 products."""
    points, weights = np.polynomial.legendre.leggauss(4)
    x = (points+1)/2
    value = np.ones((len(rho)-1, 4))
    for a in factors:
        value *= np.asarray(a)[:-1,None]*(1-x) + np.asarray(a)[1:,None]*x
    return float(np.sum(np.diff(rho)[:,None]*weights/2*value))


def scalar_enclosure(rational, multiplier=Fraction(1)):
    """256-bit Arb enclosure of 2*pi^2 times a rational scalar."""
    from flint import arb, ctx, fmpq
    with ctx.workprec(256):
        q = rational * multiplier
        result = 2*arb.pi()**2*arb(fmpq(q.numerator, q.denominator))
        return dict(arb_interval=str(result), midpoint=float(result.mid()),
                    radius_upper=float(np.nextafter(float(result.rad().upper()), np.inf)), bits=256,
                    scope='exact binary64 nodal piecewise-affine model only')


def evaluate_cut(source, geometry):
    """Actual source coefficients at the inherited step1222 past cut.

    q5 volume density per coordinate-time is 2*pi^2*nu*C*r^3.
    It is not the Cauchy/CAR slice measure (which omits nu), and the
    restricted Gram is not the full stratified M. The hat is an admissible
    central-hypercharge Gauss-complex test, not an exhaustive parent frame.
    """
    rho = geometry['rho']
    if not np.array_equal(rho, source['rho']):
        raise ValueError('source and parent radial charts differ')
    gamma = source['saved_gamma_LR']
    carrier = source['unit_trace_carrier_basis']
    # sigma1 SAME-source coefficients include n3. Hypercharge is central:
    # it is unchanged by the saved carrier transport and supplies a useful
    # zero-trace test subset in the gauge/constraint complex.
    z_coeff = np.zeros_like(source['original_n1'])
    z_coeff[:,:,3] = source['original_n1'][:,:,3]
    xi_a1 = parent_insertion(gamma, source['transformed_n1'], carrier)
    xi_a3 = parent_insertion(gamma, source['transformed_n3'], carrier)
    xi_z1 = parent_insertion(gamma, z_coeff, carrier)
    contact = local_mixed_contact(xi_z1, xi_a1)
    lifting, hat = computational_profiles(rho)
    nu, C, r = (geometry[k][0] for k in ('proper_lapse', 'C_rho', 'base_radius'))
    Tb = float(source['T_b'])
    support = hat > 0
    if not np.array_equal(lifting[support], np.ones(np.count_nonzero(support))):
        raise ValueError('lifting must be identically one on this contact support')
    # On the support L=1. No pole divisions or new physical radial profiles.
    contact_factors = [nu, C, r, hat, hat, hat]
    gram_factors = [nu, C, r, r, r, hat, hat]
    contact_rational = exact_affine_integral(rho, contact_factors)
    gram_rational = exact_affine_integral(rho, gram_factors)
    Tb_squared = Fraction(Tb)**2
    contact_scalar = scalar_enclosure(contact_rational, Tb_squared)
    gram_scalar = scalar_enclosure(gram_rational)
    exact_trace = scalar_enclosure(contact_rational, Tb_squared*Fraction(80,3))
    pair_checks = dict(
        unit_contact_Hermitian_residual=float(np.linalg.norm(contact-contact.conj().transpose(0,1,3,2))),
        unit_trace_identity_residual=float(np.linalg.norm(np.trace(contact, axis1=2, axis2=3)-(80/3)*np.eye(8))),
        connected_n3_source_action_norm=float(np.linalg.norm(xi_a3)),
        n1_source_action_norm=float(np.linalg.norm(xi_a1)),
        test_hypercharge_constraint_residual=float(np.linalg.norm(source['constraint_gradient_n1'][:,:,3])),
        test_hypercharge_commutator_residual=float(np.linalg.norm(
            carrier[:3]@carrier[3]-carrier[3]@carrier[:3])),
        material_test_trace=float(hat[-1]), pole_test_trace=float(hat[0]),
        lifting_material_trace=float(lifting[-1]),
        contact_quadrature_residual=abs(gauss_affine_integral(rho,contact_factors)-float(contact_rational)),
        gram_quadrature_residual=abs(gauss_affine_integral(rho,gram_factors)-float(gram_rational)))
    # Preserve source images in their entire n1+n3 range before taking the
    # selected finite form matrix. Orthogonality makes Z_n1^dagger A_n3=0
    # for this one contact; it does not eliminate n3 from Q or a resolvent.
    profile_a = np.zeros_like(r)
    profile_z = np.zeros_like(r)
    away = r > 0
    profile_a[away] = Tb*lifting[away]/r[away]
    profile_z[away] = Tb*hat[away]/r[away]
    arrays = dict(rho=rho, proper_time=geometry['proper_times'][0],
        nu=nu, C_rho=C, base_radius=r, T_b=Tb,
        lifting_nodes=lifting, zero_trace_hat_nodes=hat, spinor_probe_hat_nodes=hat,
        profile_a=profile_a, profile_z=profile_z,
        Xi_A_unit_n1=xi_a1, Xi_A_unit_n3=xi_a3, Xi_Z_unit_n1=xi_z1,
        Xi_A_on_probe_radial_nodes=profile_a*hat,
        Xi_Z_on_probe_radial_nodes=profile_z*hat,
        K_ZA_unit_contact=contact,
        K_ZA_cut_density_contact=contact_scalar['midpoint']*contact,
        M_cut_density_probe=gram_scalar['midpoint']*np.eye(64))
    scalars = dict(contact_scalar=contact_scalar, gram_scalar=gram_scalar,
        algebraic_trace_diagonal=exact_trace,
        contact_integral_rational=str(contact_rational),
        gram_integral_rational=str(gram_rational), T_b_squared_rational=str(Tb_squared))
    return arrays, scalars, pair_checks


def retained_source_cut_rate(repository):
    """Bind the SAME source derivative to the recovered step1222 record.

    The geometry cache's endpoint boundary_H is a reconstruction placeholder.
    This is an explicit existing producer binding, not a new rate selection.
    """
    import hashlib
    import json
    from pathlib import Path
    root=Path(repository)
    result_path=root/'artifacts/muon_exterior_face_source_20261002/replay_reference/result.json'
    refs_path=root/'artifacts/muon_exterior_face_source_20261002/input_refs.json'
    result=json.loads(result_path.read_text())
    refs=json.loads(refs_path.read_text())
    h=float(result['frontier_source']['H'])
    interval=result['frontier_H_reused_certified_interval']
    if not interval[0]<=h<=interval[1]:raise ValueError('retained rate outside its certified interval')
    return dict(value=h,interval=interval,cut_id='C2_step1222',
        T_b=float(result['frontier_source']['T_b']),
        coordinate='D_tau log R4; inherited boundary proper time',
        result_path=result_path.relative_to(root).as_posix(),
        result_sha256=hashlib.sha256(result_path.read_bytes()).hexdigest(),
        defining_equation='H=(D_q log R4 . qdot)/N_boundary',
        producer='aether_forward_boundary_radius.proper_time_log_radius_rate',
        state_key='endpoint_predictor_center',order=12,
        prefix_state=refs['inputs']['prefix'],prefix_certificate=refs['inputs']['prefix_report'],
        excluded_affine_logR_slope=result['H_reconstruction_scope']['source_affine_H'],
        uncertainty_scope='inherited step1222 interval at fixed other saved inputs; separate from body/interpolation error')


def repair_source_time_rate(old, *, H_used, cut_rate):
    """Apply only the supplied affine source-time repair; keep body/contact.

    C_b,new=C_b,old-(H_new-H_used) C_b_tau,old/2. H_used is documented from
    the consumed old cache/code. The caller preserves the historical arrays.
    """
    if cut_rate['cut_id']!='C2_step1222':raise ValueError('wrong source cut')
    new={k:old[k] for k in old}
    delta_h=float(cut_rate['value'])-float(H_used)
    delta={}
    for n in (1,3):
        key=f'D5_on_same_source_image_b_coefficient_n{n}'
        tau=f'D5_on_same_source_image_b_tau_coefficient_n{n}'
        change=-(delta_h/2)*old[tau]
        new[key]=old[key]+change
        delta[f'C_b_old_n{n}']=old[key]
        delta[f'C_b_new_n{n}']=new[key]
        delta[f'C_b_delta_n{n}']=change
    key='source_kernel_time_log_derivative'
    new[key]=old[key]-delta_h/2
    delta.update(kernel_log_derivative_old=old[key],kernel_log_derivative_new=new[key],
                 kernel_log_derivative_delta=np.full_like(old[key],-delta_h/2))
    return new,delta


def cut_metric_dirac_actions(source, geometry, contact, *, cut_rate):
    """Canonical metric/common-A summand, on the same compact probes.

    Coframe: theta0=nu dtau, theta4=C(drho+zeta dtau), thetaa=r thetaR_a.
    The current cached metric is interpolated affinely in rho and on the
    first forward time cell. Four Gauss points per test-support cell are
    evaluation points, not a quadrature certification for this rational
    Dirac density. Full stratified domain/other summands are not fabricated.
    """
    gamma=source['saved_gamma_LR']
    gamma5=1j*gamma[0]@gamma[1]@gamma[2]@gamma[3]
    gamma4=1j*gamma5  # outward spatial normal; signature +----
    G=np.concatenate((gamma,gamma4[None]))
    I16=np.eye(16)
    G64=np.array([np.kron(g,I16) for g in G])
    angular_spin=-1.5j*np.kron(gamma[1]@gamma[2]@gamma[3],I16)
    # jmath=-i sigma=2sqrt2 Hweak, from the retained mechanical attachment.
    jmath=2*np.sqrt(2)*source['unit_trace_carrier_basis'][:3]
    gauge_unit=sum(np.kron(1j*gamma[a+1],jmath[a]) for a in range(3))
    rho=geometry['rho']; _,hat=computational_profiles(rho)
    cells=np.arange(24,40)
    gx,gw=np.polynomial.legendre.leggauss(4)
    x=np.tile((gx+1)/2,len(cells)); cell=np.repeat(cells,4)
    widths=np.diff(rho)[cell]
    points=rho[cell]+x*widths
    def interp(a):return a[cell]*(1-x)+a[cell+1]*x
    def dr(a):return (a[cell+1]-a[cell])/widths
    fields={k:interp(geometry[k][0]) for k in
            ('proper_lapse','C_rho','base_radius','proper_shift_rho','A','B')}
    nu,C,r,zeta=(fields[k] for k in
                ('proper_lapse','C_rho','base_radius','proper_shift_rho'))
    nu_r,C_r,r_r,zeta_r=(dr(geometry[k][0]) for k in
                         ('proper_lapse','C_rho','base_radius','proper_shift_rho'))
    dt=float(geometry['proper_times'][1]-geometry['proper_times'][0])
    if dt<=0:raise ValueError('inherited forward time cell required')
    C_t=interp((geometry['C_rho'][1]-geometry['C_rho'][0])/dt)
    r_t=interp((geometry['base_radius'][1]-geometry['base_radius'][0])/dt)
    h0=(C_t/C+3*r_t/r-zeta*(C_r/C+3*r_r/r)-zeta_r)/(2*nu)
    h4=(nu_r/nu+3*r_r/r)/(2*C)
    A,B=fields['A'],fields['B']
    bg=-B/(A*np.sqrt(A*A+B*B))
    spin=h0[:,None,None]*(1j*G64[0])+h4[:,None,None]*(1j*G64[4])+angular_spin[None]/r[:,None,None]
    body=spin+bg[:,None,None]*gauge_unit
    chi=interp(hat); chi_r=dr(hat)
    Dprobe=(body*chi[:,None,None]
            +(-zeta*chi_r/nu)[:,None,None]*(1j*G64[0])
            +(chi_r/C)[:,None,None]*(1j*G64[4]))
    if cut_rate['cut_id']!='C2_step1222':raise ValueError('wrong source cut')
    Tb=float(source['T_b']); H=float(cut_rate['value'])
    if Tb!=cut_rate['T_b']:raise ValueError('retained rate and source refer to different cut frames')
    Q=1j*(np.sqrt(2)*source['unit_trace_carrier_basis'][2]
          +np.sqrt(10/3)*source['unit_trace_carrier_basis'][3])
    # A computational charged weak-doublet carrier coordinate, not LSZ or
    # a selected physical muon. All 64 output rows remain available.
    charged=np.flatnonzero(np.isclose(np.diag(Q),-1) &
                           (np.sum(abs(jmath[0]),axis=0)>0))[0]
    columns=16*np.arange(4)+charged
    arrays=dict(gauss_rho=points, gauss_cells=cell, gamma5=gamma5,
        normal_gamma=gamma4, parent_gamma=G, normal_orientation='outward_rho',
        spin_connection_contracted=spin, common_A_zero_order=bg[:,None,None]*gauge_unit,
        D5_metric_common_A_on_compact_probes=Dprobe,
        source_image_probe_columns=columns, h0=h0, h4=h4,
        source_kernel_time_log_derivative=-H/2-r_t/r)
    for n in (1,3):
        xi=contact[f'Xi_A_unit_n{n}'][:,:,columns]
        j=n/2; w=np.arange(n,-n-1,-2)/2
        plus=np.zeros((n+1,n+1),complex)
        for k in range(1,n+1):plus[k-1,k]=np.sqrt((j-w[k])*(j+w[k]+1))
        J=np.array([(plus+plus.T)/2,(plus-plus.T)/(2j),np.diag(w)])
        angular=sum(np.einsum('oi,Aicmk,vm->Aocvk',1j*G64[a+1],xi,2j*J[a],optimize=True)
                    for a in range(3))
        # For coefficients f_mk phi_mk, the saved active-weight E action is
        # +2i J acting on the coefficient m index. No angular compression.
        f=Tb*chi/r
        f_r=Tb*(chi_r/r-chi*r_r/(r*r))
        f_t=(-H/2-r_t/r)*f
        D=(np.einsum('goi,Aicmk->gAocmk',body,xi,optimize=True)*f[:,None,None,None,None,None]
           +np.einsum('oi,Aicmk->Aocmk',1j*G64[0],xi,optimize=True)[None]
             *((f_t-zeta*f_r)/nu)[:,None,None,None,None,None]
           +np.einsum('oi,Aicmk->Aocmk',1j*G64[4],xi,optimize=True)[None]
             *(f_r/C)[:,None,None,None,None,None]
           +angular[None]*(f/r)[:,None,None,None,None,None])
        arrays[f'D5_on_same_source_image_b_coefficient_n{n}']=D
        arrays[f'D5_on_same_source_image_b_tau_coefficient_n{n}']=(
            np.einsum('oi,Aicmk->Aocmk',1j*G64[0],xi,optimize=True)[None]
            *(f/nu)[:,None,None,None,None,None])
    weights=np.tile(gw/2,len(cells))*widths*2*np.pi**2*nu*C*r**3
    gram=chi@ (weights*chi)
    K0=np.einsum('g,gki,gkj->ij',weights,Dprobe.conj(),Dprobe,optimize=True)
    arrays.update(K0_metric_common_A_probe_cut_density=K0,
                  M0_probe_cut_density=gram*np.eye(64),
                  node_volume_quadrature_weights=weights)
    metric=np.diag([1,-1,-1,-1,-1])
    cliff=G[:,None]@G[None]+G[None]@G[:,None]-2*metric[:,:,None,None]*np.eye(4)
    checks=dict(parent_Clifford_residual=float(np.linalg.norm(cliff)),
        K0_cut_Hermitian_residual=float(np.linalg.norm(K0-K0.conj().T)),
        K0_cut_norm=float(np.linalg.norm(K0)),
        source_image_n1_body_action_norm=float(np.linalg.norm(arrays['D5_on_same_source_image_b_coefficient_n1'])),
        source_image_n3_body_action_norm=float(np.linalg.norm(arrays['D5_on_same_source_image_b_coefficient_n3'])),
        probe_Gram_consistency_residual=abs(gram-contact['M_cut_density_probe'][0,0]))
    return arrays, checks
