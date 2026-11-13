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
                    radius_upper=float(result.rad().upper()), bits=256,
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
