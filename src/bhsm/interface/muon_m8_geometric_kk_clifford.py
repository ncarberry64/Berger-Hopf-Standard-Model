"""Full16 geometric Hopf Clifford coefficients on supplied analytic jets.

The supplied fixed Cl(1,4) matrices use base order (0,chi,1,2,3).  The
rank16 construction is Gamma_mu=gamma_mu (x) I2 (x) sigma1 and
Gamma_i=I4 (x) i sigma_i (x) sigma2.  It is the complete odd/odd spin
branching, not a selection of the native graded/SM carrier or a new UV
fermion.  No Clifford matrix or source coefficient is conjugated here.

Geometric operands come from the existing M8/M5 scalar coefficient owner.
The returned principal coefficients refer to the ADAPTED horizontal/fiber
frame; they must not be combined with an original-(u,v) spin frame without
its actual spin-lift derivative.  Only the stated coefficient blocks are
constructed: no associated-mode connection, full native body, positive
pairing, contour, field solution, outgoing domain, or physical gate is
selected.  Every scalar/tensor operand has explicit value/x/y/xy jets.
"""
from __future__ import annotations

from collections.abc import Mapping

import numpy as np


JET_ORDER = ("value", "x", "y", "xy")
BASE_FRAME_ORDER = ("0", "chi", "1", "2", "3")


def _finite(value, shape, name):
    array = np.asarray(value, complex)
    if array.shape != shape or not np.isfinite(array).all():
        raise ValueError(f"{name} requires finite shape {shape}")
    return array.copy()


def _jet(value, shape, name):
    if not isinstance(value, Mapping) or set(value) != set(JET_ORDER):
        raise ValueError(f"{name} requires explicit value/x/y/xy jets")
    return {key: _finite(value[key], shape, name+"."+key) for key in JET_ORDER}


def _product(a, b):
    return dict(value=a["value"]*b["value"],
        x=a["x"]*b["value"]+a["value"]*b["x"],
        y=a["y"]*b["value"]+a["value"]*b["y"],
        xy=a["xy"]*b["value"]+a["x"]*b["y"]
           +a["y"]*b["x"]+a["value"]*b["xy"])


def _inverse(a, name):
    v = a["value"]
    if v == 0:
        raise ValueError(name+" must have a nonzero regular value")
    return dict(value=1/v, x=-a["x"]/v**2, y=-a["y"]/v**2,
        xy=2*a["x"]*a["y"]/v**3-a["xy"]/v**2)


def _times_matrix(a, matrix):
    return {key: a[key]*matrix for key in JET_ORDER}


def _matrix_sum(a, b):
    return {key: a[key]+b[key] for key in JET_ORDER}


def m8_geometric_kk_clifford_jets(*, gamma5_base, geometric_coefficients):
    """Construct the geometric full16 KK block and retained principal jets.

    gamma5_base is a FIXED array[5,4,4] in base order (0,chi,1,2,3),
    satisfying signature (+----).  geometric_coefficients is the output of
    m8_m5_geometric_coefficient_jets, with all required contacts explicit.
    x/y are independent analytic source axes; no source reality is assumed.
    """
    g = _finite(gamma5_base, (5, 4, 4), "gamma5_base")
    identity4 = np.eye(4, dtype=complex)
    signature5 = np.array([1, -1, -1, -1, -1])
    clifford5 = max(float(np.max(np.abs(
        g[a]@g[b]+g[b]@g[a]
        - (2*signature5[a]*identity4 if a == b else 0))))
        for a in range(5) for b in range(5))
    gamma_scale = max(1., float(np.max(np.abs(g)))**2)
    if clifford5 > 5e-12*gamma_scale:
        raise ValueError("gamma5_base does not satisfy the supplied (+----) Clifford algebra")
    if not isinstance(geometric_coefficients, Mapping):
        raise ValueError("geometric_coefficients requires the existing scalar coefficient mapping")
    c = geometric_coefficients
    if tuple(c.get("base_frame_order", ())) != BASE_FRAME_ORDER:
        raise ValueError("curvature base frame must have explicit order (0,chi,1,2,3)")
    LF = _jet(c["LF"], (), "LF")
    if LF["value"] == 0:
        raise ValueError("LF must have a nonzero regular value")
    radius = _jet(c["r"], (), "r")
    F = _jet(c["F_full"], (3, 5, 5), "F_full")
    Ninv = _jet(c["original_time_principal_coefficient"], (), "1/N")
    shift = _jet(c["original_chi_Gamma0_principal_coefficient"], (), "-beta/N")
    spatial = _jet(c["original_seven_spatial_coframe_inverse_scales"], (7,), "spatial coframe scales")
    Linv = _jet(c["vertical_DF_coefficient"], (), "1/LF")
    h08 = _jet(c["h0_M8"], (), "h0_M8")
    hc8 = _jet(c["hchi_M8"], (), "hchi_M8")
    h05 = _jet(c["h0_M5"], (), "h0_M5")
    hc5 = _jet(c["hchi_M5"], (), "hchi_M5")
    norm0 = _jet(c["fiber_norm_E0_over_norm"], (), "fiber normalized E0 derivative")
    normchi = _jet(c["fiber_norm_Echi_over_norm"], (), "fiber normalized Echi derivative")
    curvature_antisymmetry = {key: float(np.max(np.abs(F[key]+F[key].swapaxes(1, 2))))
                            for key in JET_ORDER}
    if max(curvature_antisymmetry.values()) > 5e-12*max(1., max(
            float(np.max(np.abs(F[key]))) for key in JET_ORDER)):
        raise ValueError("F_full and each supplied contact must be antisymmetric in mu,nu")

    sigma = np.array([[[0, 1], [1, 0]], [[0, -1j], [1j, 0]], [[1, 0], [0, -1]]], complex)
    identity2 = np.eye(2, dtype=complex)
    Gbase = np.array([np.kron(np.kron(a, identity2), sigma[0]) for a in g])
    Gfiber = np.array([np.kron(np.kron(identity4, 1j*a), sigma[1]) for a in sigma])
    G8 = np.concatenate((Gbase, Gfiber))
    signature8 = np.array([1, -1, -1, -1, -1, -1, -1, -1])
    identity16 = np.eye(16, dtype=complex)
    clifford8 = max(float(np.max(np.abs(
        G8[a]@G8[b]+G8[b]@G8[a]
        - (2*signature8[a]*identity16 if a == b else 0))))
        for a in range(8) for b in range(8))
    triple = np.array([[[Gbase[mu]@Gbase[nu]@Gfiber[i]
                        for nu in range(5)] for mu in range(5)] for i in range(3)])
    LF_F = _product(LF, F)
    KK = {key: (-1j/8)*np.einsum("imn,imnab->ab", LF_F[key], triple)
          for key in JET_ORDER}
    KK_by_fiber = {key: (-1j/8)*np.einsum("imn,imnab->iab", LF_F[key], triple)
                   for key in JET_ORDER}
    KK_upper = {key: sum((-1j/4)*LF_F[key][i, mu, nu]*triple[i, mu, nu]
                        for i in range(3) for mu in range(5) for nu in range(mu+1, 5))
                for key in JET_ORDER}

    Cinv = {key: spatial[key][0] for key in JET_ORDER}
    rinv = _inverse(radius, "r")
    time = _times_matrix(Ninv, 1j*Gbase[0])
    normal = _matrix_sum(_times_matrix(Cinv, 1j*Gbase[1]),
                         _times_matrix(shift, 1j*Gbase[0]))
    base_angular = {key: 1j*rinv[key]*Gbase[2:] for key in JET_ORDER}
    vertical = {key: 1j*Linv[key]*Gfiber for key in JET_ORDER}
    vertical_spin = _times_matrix(Linv, 1.5j*Gfiber[0]@Gfiber[1]@Gfiber[2])
    density8 = _matrix_sum(_times_matrix(h08, 1j*Gbase[0]), _times_matrix(hc8, 1j*Gbase[1]))
    density5 = _matrix_sum(_times_matrix(h05, 1j*Gbase[0]), _times_matrix(hc5, 1j*Gbase[1]))
    normalization = _matrix_sum(_times_matrix(norm0, 1j*Gbase[0]),
                                 _times_matrix(normchi, 1j*Gbase[1]))
    normalized_density = _matrix_sum(density8, normalization)
    inverse_rows = _product(LF, Linv)
    inverse_rows["value"] = inverse_rows["value"]-1
    return dict(gamma8_base=Gbase, gamma8_vertical=Gfiber, gamma8_all=G8,
        KK=KK, KK_by_fiber=KK_by_fiber,
        time_coordinate_principal=time, chi_coordinate_principal=normal,
        horizontal_angular_principal=base_angular, vertical_unit_derivative_principal=vertical,
        vertical_left_MC_spin_body=vertical_spin,
        M8_time_normal_spin_density=density8, M5_time_normal_spin_density=density5,
        normalized_M8_time_normal_spin_density=normalized_density,
        mean_spin_density_cancellation={key: normalized_density[key]-density5[key] for key in JET_ORDER},
        LF_inverse_contact_rows=inverse_rows,
        clifford5_residual=clifford5, clifford8_residual=clifford8,
        curvature_antisymmetry_residual=curvature_antisymmetry,
        full_vs_upper_ordered_KK_residual={key: float(np.max(np.abs(KK[key]-KK_upper[key])))
                                         for key in JET_ORDER},
        base_frame_order=BASE_FRAME_ORDER, full_frame_order=BASE_FRAME_ORDER+("v1", "v2", "v3"),
        jet_order=JET_ORDER, spinor_fiber_dimension=16,
        fixed_clifford_frame=True, source_coefficients_conjugated=False,
        full_ordered_mu_nu_sum=True, vertical_DF_or_spin_set_to_zero=False,
        temporal_and_shift_principals_retained=True,
        all_seven_spatial_principal_directions_retained=True,
        adapted_horizontal_fiber_frame=True,
        associated_mode_connection_or_full_body_constructed=False,
        native_graded_or_SM_carrier_selected=False,
        positive_pairing_or_contour_selected=False,
        full_physical_outgoing_derivative_pass=False,
        coupled_correction_performed=False, physical_moment_computed=False)
