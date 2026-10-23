"""Consume matched comparison and Gauss jets in the original charge equation.

This is an operator application on the saved homogeneous comparison. It
does not contract a quantum state, construct a collider incidence, or
choose any incoming characteristic datum. Independent time/packet/domain
variations remain outside the declared stationary coefficient family.
"""
from __future__ import annotations

import numpy as np

from .muon_native_dirac_hamiltonian import (
    fixed_y_higgs_hamiltonian, lepton_current_hilbert_representation,
)


def consume_charge_balance(comparison, gauss):
    """Original covariant continuity versus causal Heisenberg operator.

    On this constant-angular stationary comparison only,
      E_Q = [Omega,Q]+sum_i alpha_i [A_i,Q]/R+i[M,Q]
          = i[h,Q], h=W-i Omega.
    The first expression consumes the already evaluated Gauss test jets;
    the second consumes the independently evaluated causal generator jets.
    The temporal connection is included once. No expectation or field
    source is inferred from a nonzero operator coefficient.
    """
    for left, right in (
        ('input_iterate151', 'input_iterate151'),
        ('input_theta22', 'actual_theta22'),
        ('input_theta_gradient22x151', 'actual_theta_gradient22x151'),
    ):
        if not np.array_equal(comparison[left], gauss[right]):
            raise ValueError('comparison and Gauss background/source identities differ')
    t = np.asarray(gauss['actual_theta22'])
    gradient = np.asarray(gauss['actual_theta_gradient22x151'])
    H = np.asarray(comparison['H'])
    Hx = np.asarray(comparison['H_source'])
    if t.shape != (22,) or gradient.shape != (22, 151):
        raise ValueError('the exact same22-by151 comparison chart is required')
    if H.shape != (18, 18) or Hx.shape != (151, 18, 18):
        raise ValueError('full18 causal generator and all declared source columns required')
    vertices = np.asarray(gauss['original_At_action_vertices'])  # i G_c
    Q = np.asarray(gauss['physical_charge18'])
    Qx = np.einsum('ck,cab->kab', gauss['charge_test_gradient'], vertices)
    temporal = np.einsum('c,cab->ab',
        gauss['proper_stationary_temporal_covariant_charge_derivative_value'], vertices)
    temporal_x = np.einsum('ck,cab->kab',
        gauss['proper_stationary_temporal_covariant_charge_derivative_gradient'], vertices)
    spatial_coeff = np.asarray(gauss['proper_spatial_covariant_charge_derivative_value']).reshape(3, 4)
    spatial_coeff_x = np.asarray(gauss['proper_spatial_covariant_charge_derivative_gradient']).reshape(3, 4, 151)
    covariant_spatial = np.einsum('ic,cab->iab', spatial_coeff, vertices)
    covariant_spatial_x = np.einsum('ick,cab->kiab', spatial_coeff_x, vertices)
    alpha = lepton_current_hilbert_representation()['alpha']
    spatial = np.einsum('iab,ibc->ac', alpha, covariant_spatial)
    spatial_x = np.einsum('iab,kibc->kac', alpha, covariant_spatial_x)
    higgs = t[18:20]+1j*t[20:22]
    higgs_x = gradient[18:20].T+1j*gradient[20:22].T
    M = fixed_y_higgs_hamiltonian(higgs[None])[0]
    Mx = fixed_y_higgs_hamiltonian(higgs_x)
    torque = 1j*(M@Q-Q@M)
    torque_x = 1j*(Mx@Q-Q@Mx+M@Qx-Qx@M)
    exchange = temporal+spatial+torque
    exchange_x = temporal_x+spatial_x+torque_x
    heisenberg = 1j*(H@Q-Q@H)
    heisenberg_x = 1j*(Hx@Q-Q@Hx+H@Qx-Qx@H)
    C = np.asarray(comparison['electron_family_lift'])
    if C.shape != (18, 6):
        raise ValueError('the full original electron-family6 is required')
    E = C.T@exchange@C
    Ex = np.einsum('ai,kab,bj->kij', C, exchange_x, C)
    P = np.asarray(comparison['electron_positive'])
    Px = np.asarray(comparison['electron_positive_source'])
    negative = np.asarray(comparison['electron_negative'])
    pair = P@E@negative
    pair_x = Px@E@negative+P@Ex@negative-P@E@Px
    return dict(
        covariant_temporal_charge=temporal,
        covariant_temporal_charge_source=temporal_x,
        covariant_spatial_charge=covariant_spatial,
        covariant_spatial_charge_source=covariant_spatial_x,
        spatial_charge_continuity=spatial,
        spatial_charge_continuity_source=spatial_x,
        Higgs_mass_charge_torque=torque,
        Higgs_mass_charge_torque_source=torque_x,
        charge_exchange=exchange, charge_exchange_source=exchange_x,
        causal_Heisenberg_charge=heisenberg,
        causal_Heisenberg_charge_source=heisenberg_x,
        original_charge_balance_rows=exchange-heisenberg,
        original_charge_balance_source_rows=exchange_x-heisenberg_x,
        original_exchange_Hermiticity_rows=exchange-exchange.conj().T,
        electron_charge_exchange=E, electron_charge_exchange_source=Ex,
        electron_pair_charge_exchange=pair,
        electron_pair_charge_exchange_source=pair_x,
        physical_d_in=None, physical_Cauchy_state=None,
        state_contracted=False, physical_admission=False, physical_guard=2e-10,
    )
