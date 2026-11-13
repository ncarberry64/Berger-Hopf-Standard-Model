"""Reconcile the retained formation operator with AE4's length prescription.

No independent impedance-energy functional is selected here. The formation
quotient fixes a resistance operator; it does not by itself identify AE4's
energy-normalization or support-loss event. Finite eigenbranch routines below
evaluate SUPPLIED arithmetic-control matrices, not physical BHSM operators.
"""
from __future__ import annotations
import numpy as np


def reconcile_owners(ae4,mechanics,interface):
    """Read the actual retained owner statements without materializing them."""
    form=mechanics['formation_number']
    if form['classification']!='RHO-B2':raise ValueError('retained operator-valued owner required')
    return dict(
        classification='AE4_LENGTH_IDENTIFICATION_UNRECONCILED_AFTER_RHO_B2',
        formation_authority=mechanics['action_version'],
        current_formation_operator='R=gamma J_Sigma+H_impedance; D=H_event,drive; A_form=R-D on the common reduced space',
        actual_formation_definition=form['definition'],
        actual_historical_relation=form['historical_relation'],
        actual_formation_threshold=form['threshold'],
        actual_AE4_surface=ae4['surface_rule'],
        actual_AE4_length=ae4['spectral_length_rule_natural_units'],
        resistance_in_historical_formation_ratio='gamma J_Sigma+H_impedance, not H_impedance alone',
        scalar_formation_reduction='rho_line=(psi_dagger D psi)/(psi_dagger R psi) on the same common-charge line',
        bulk_only_threshold_residual='at (R-D)psi=0: psi_dagger(H_impedance-D)psi=-gamma psi_dagger J_Sigma psi',
        surface_term_proved_zero=False,
        interface_scalar_exclusion=interface['interface_action']['invariant_controls']['excluded'],
        independent_scalar_law_route_withdrawn=True,
        full_heat_owner_superseded=False,
        scalar_holding_hypothesis_superseded_by_RHO_B2=True,
        AE4_inverse_energy_amended_by_mechanics=False,
        selected_event_equivalence_supplied=False,
        common_charge_energy_pairing_supplied=False,
        physical_H_owned=None,physical_M_owned=None,physical_psi_star=None,
        physical_E=None,physical_E_v=None,physical_E_J=None,physical_E_vJ=None,
        minimal_amendment=dict(
            name='same-action one-mode/common-charge identification of AE4 length and crossing',
            equation='E_impedance_AE4 = iota_star_dagger R iota_star / (iota_star_dagger M_E iota_star); E_core_AE4 = iota_star_dagger D iota_star / (iota_star_dagger M_E iota_star)',
            required_derivation='identify the SAME AE4 support-loss surface/eigenline with the relevant constrained formation branch, and derive M_E with energy units from the owned common-charge/clock pairing',
            scope='compatibility schema for the historical formation-ratio interpretation; NOT adopted here and NOT uniquely fixed by RHO-B2',
            alternative='a different already-owned scalarization/event relation would require its explicit action equality and provenance',
            prohibited='no arbitrary function, fitted scale, M_E=I shortcut, ell_s=ell_star equality, inverse eigenvalue/frequency choice or surface-term deletion'),
        not_a_logical_no_go_for_compatible_future_matching=True,
        not_an_unfinished_scalar_numerical_solve=True)


def generalized_simple_mode_jets(H,M,psi,E,Hx,Hy,Hxy,Mx,My,Mxy):
    """Conditional Hermitian simple ENERGY eigenbranch, supplied matrices.

    Both source parameters are REAL. Complex current directions must be
    obtained by complex-linear extension of the real Hessian coefficients,
    not by conjugating complex current weights in a quadratic formula.
    The bordered solve is the reduced action; no inverse is formed.
    A simple FORMATION zero mode need not satisfy this energy eigenproblem.
    """
    H=np.asarray(H,complex);M=np.asarray(M,complex);psi=np.asarray(psi,complex)
    n=len(psi);A=H-E*M;mpsi=M@psi
    if abs(np.vdot(psi,mpsi)-1)>1e-12:raise ValueError('M-normalized supplied eigenline required')
    if np.linalg.norm(A@psi)>1e-12:raise ValueError('energy eigenline, not an arbitrary formation mode, required')
    border=np.zeros((n+1,n+1),complex)
    border[:n,:n]=A;border[:n,n]=mpsi;border[n,:n]=mpsi.conj()
    Tx=Hx-E*Mx;Ty=Hy-E*My
    Ex=np.vdot(psi,Tx@psi);Ey=np.vdot(psi,Ty@psi)
    rx=np.linalg.solve(border,np.r_[-Tx@psi,0])[:n]
    ry=np.linalg.solve(border,np.r_[-Ty@psi,0])[:n]
    mx=np.vdot(psi,Mx@psi);my=np.vdot(psi,My@psi)
    psix=rx-mx*psi/2;psiy=ry-my*psi/2
    # r_x=-R_red T_x psi, so these are the signed pair terms.
    mixed=np.vdot(psi,(Hxy-E*Mxy-Ex*My-Ey*Mx)@psi)
    mixed+=np.vdot(Tx@psi,ry)+np.vdot(Ty@psi,rx)
    reverse=np.vdot(psi,(Hxy-E*Mxy-Ey*Mx-Ex*My)@psi)
    reverse+=np.vdot(Ty@psi,rx)+np.vdot(Tx@psi,ry)
    checks=dict(eigen_residual=float(np.linalg.norm(A@psi)),
        M_norm_residual=float(abs(np.vdot(psi,M@psi)-1)),
        x_directional_residual=float(np.linalg.norm(A@psix+(Tx-Ex*M)@psi)),
        y_directional_residual=float(np.linalg.norm(A@psiy+(Ty-Ey*M)@psi)),
        x_normalization_residual=float(abs(2*np.vdot(psi,M@psix).real+mx)),
        y_normalization_residual=float(abs(2*np.vdot(psi,M@psiy).real+my)),
        mixed_symmetry_residual=float(abs(mixed-reverse)))
    return dict(E=E,E_x=Ex,E_y=Ey,E_xy=mixed,
        r_x=rx,r_y=ry,psi_x=psix,psi_y=psiy,checks=checks)


def moving_rayleigh_first(R,M,psi,psix,Rx,Mx):
    """Energy contraction on a selected normalized line, not assumed stationary.

    Shows the embedding term which bare Hellmann--Feynman would omit.
    """
    E=np.vdot(psi,R@psi)/np.vdot(psi,M@psi)
    explicit=np.vdot(psi,(Rx-E*Mx)@psi)
    motion=np.vdot(psix,(R-E*M)@psi)+np.vdot(psi,(R-E*M)@psix)
    return E,explicit+motion,explicit,motion
