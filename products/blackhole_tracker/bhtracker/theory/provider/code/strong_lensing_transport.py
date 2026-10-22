"""Action-native, measured-redshift three-segment optical transport.

This is a conditional axial experiment, not an arbitrary-sky lensing solver.
One *normalized* n=2 profile is Q=N_Q sin(2 sqrt(K) chi) cos(theta),
N_Q=sqrt(3/(pi**2 R**3)), R=K**(-1/2), with the observer at chi=0
and the central ray on its declared positive axis. Integral Q**2 dV_gamma=1.
The full nine-component spatial eigenspace is not fitted or selected here.

The frozen action-native propagator supplies independent conventional
Newtonian potentials phi(N), psi(N) and the dust velocity potential v(N).
No legacy positive-spatial-potential adapter is used. The metric is

 ds**2=-A**2 d eta**2+B**2[d chi**2+S_K(chi)**2 d Omega**2],
 A=a sqrt(1+2 phi Q), B=a sqrt(1-2 psi Q).

All reported state derivatives are first order at Y=0. Finite rays use this
explicit truncated-metric completion only as a derivative check, not as a
nonlinear cosmological solution. No galaxy potential is present in the maps.

Here are the actual equations evaluated, with chi increasing into the past,
E the frequency measured by the static tetrad, W=B S_K, and q=Q(theta=0):

 N_chi = -a H sqrt((1-2 psi q)/(1+2 phi q)),
 (ln E)_chi = a H sqrt((1-2 psi q)/(1+2 phi q))
              -a H psi_N q/sqrt((1-2 psi q)(1+2 phi q))
              -phi q_chi/(1+2 phi q),
 lambda_chi=B/E.

The screen variation is obtained by differentiating the ORIGINAL angular
geodesic equation, not by keeping only the Born Weyl Hessian:

 theta_chi = L/(B S_K**2 E),
 L_chi = E B a**2 q [phi/A**2+psi/B**2] theta,
 D = W theta.

The L_chi term is the angular metric variation about cos(theta)=1. Dropping
it would incorrectly treat the axial dipole as a spherically symmetric
metric and would miss Ricci/redshift/endpoint contributions. Axial rotation
symmetry makes both physical screen maps identical scalar multiples of I2.
The screen basis is parallel transported and has no rotation on this ray.

Schutz--Sorkin's partial_i ell=mu u_i and delta ell=mu v imply u_chi=v q_chi.
Thus the first-order physical peculiar velocity is v q_chi/a, rather than
the unadapted legacy v q_chi. Set s=u_chi/B, gamma=sqrt(1+s**2); then the
explicit normalized matter tetrad gives omega=E(gamma+s). We set omega_o=1.
The observed-redshift events are roots omega=1+z, not fixed background N.
At the observer theta_o=gamma_o+s_o (aberration), L_o=0. At the *moving*
lens event theta_l=0, L_l=W_l omega_l, so dD/dlambda|l=omega_l.
The latter is the same global affine normalization; restarting with unit
derivative there without rescaling would be inconsistent.

Reverse propagation initializes L_s=-W_s omega_s on the same ray and checks
D_sl/D_ls=omega_s/omega_l. No observer-distance subtraction or arbitrary
symmetrization occurs. All physical lengths are in c/H0, i.e. H0=1 units.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
from scipy.integrate import quad, solve_ivp
from scipy.interpolate import CubicSpline
from scipy.optimize import brentq

import action_native_matter_n2 as an
import background as bg
import closed_horndeski_n2 as owner
import bhsm_optical_transfer as optical


ANCHOR_NAMES = ("zeta", "Pi2_reference", "delta_m_ADM", "delta_r_ADM",
                "v_m_ADM", "v_r_ADM")
MAP_NAMES = ("D_ol", "D_os", "D_ls")


def harmonic_normalization(K=bg.KCURV):
    if K <= 0:
        raise ValueError("this normalized S3 profile requires positive K")
    return math.sqrt(3.0 / (math.pi**2 * K**(-1.5)))


def physical_anchor_to_canonical(background):
    """Six physical anchor coordinates -> full (x,p), without Pi2=p_zeta.

    D_m=delta_m+3zeta, D_r=3delta_r/4+3zeta; Pi2 is reference-normalized
    2a_i**3 G_S,2 zeta_dot. ADM velocities are reconstructed auxiliaries.
    Inverting these six CURRENT action rows supplies all six initial modes.
    """
    N = an.N_START
    y = background.sol(N)
    vel, aux = an.canonical_maps(N, y)
    eye = np.eye(6)
    rows = np.array([eye[0], 2*np.exp(3*N)*owner.gs_n2(y[1], y[2])*vel[0],
                     eye[1]-3*eye[0], (4/3)*(eye[2]-3*eye[0]), aux[2], aux[3]])
    return np.linalg.solve(rows, eye)


@dataclass(frozen=True)
class TransportMaps:
    D_ol: np.ndarray
    D_os: np.ndarray
    D_ls: np.ndarray
    observer: dict
    lens: dict
    source: dict
    reciprocity: dict
    perturbation_diagnostics: dict
    assumptions: tuple[str, ...]

    @property
    def scalar_maps(self):
        return np.array([self.D_ol[0, 0], self.D_os[0, 0], self.D_ls[0, 0]])

    def as_dict(self):
        return {"D_ol": self.D_ol.tolist(), "D_os": self.D_os.tolist(),
                "D_ls": self.D_ls.tolist(), "units": "c/H0",
                "observer": self.observer, "lens": self.lens,
                "source": self.source, "reciprocity": self.reciprocity,
                "perturbation_diagnostics": self.perturbation_diagnostics,
                "assumptions": list(self.assumptions)}


class ActionNativeAxialTransport:
    """Reusable six-amplitude linear provider, followed by actual ray solves."""

    def __init__(self, background=None, propagator=None, grid_size=801,
                 rtol=2e-11, atol=2e-13):
        self.background = an.frozen_background() if background is None else background
        self.propagator = (an.integrate_propagator(self.background)
                           if propagator is None else propagator)
        self.anchor_to_canonical = physical_anchor_to_canonical(self.background)
        self.K = bg.KCURV
        self.normalization = harmonic_normalization(self.K)
        self.rtol, self.atol = rtol, atol
        ns = np.linspace(an.N_START, 0., grid_size)
        # These are coefficient ROWS per physical anchor amplitude, not an
        # assumed cosmological state or selected two-column fluid slice.
        rows = np.array([an.newtonian_map(N, self.background.sol(N))
                         @ self.propagator.sol(N).reshape(6, 6)
                         @ self.anchor_to_canonical for N in ns])
        self.rows = CubicSpline(ns, rows, axis=0)
        self.max_slip_row = float(np.max(np.abs(rows[:, 0]-rows[:, 1])))
        self.max_relative_slip_row = float(np.max(np.abs(rows[:, 0]-rows[:, 1])/
                                                  np.maximum(1., np.abs(rows[:, 0]))))
        self._chi_max = quad(lambda N: np.exp(-N)/self.background.sol(N)[2],
                             an.N_START, 0., epsabs=2e-12)[0]

    def q(self, chi):
        return self.normalization*np.sin(2*math.sqrt(self.K)*chi)

    def q_prime(self, chi):
        return self.normalization*2*math.sqrt(self.K)*np.cos(2*math.sqrt(self.K)*chi)

    def S(self, chi):
        return np.sin(math.sqrt(self.K)*chi)/math.sqrt(self.K)

    def coefficients(self, N, anchor):
        if N < an.N_START-1e-8 or N > 1e-8:
            raise ValueError("ray left the inherited action-native redshift domain")
        vals = self.rows(N)@anchor
        return float(vals[0]), float(vals[1]), float(vals[4]), float(self.rows(N, 1)[1]@anchor)

    def _geometry(self, chi, N, logE, anchor):
        a = math.exp(N)
        H = float(self.background.sol(N)[2])
        phi, psi, vm, psi_N = self.coefficients(N, anchor)
        q, qp = self.q(chi), self.q_prime(chi)
        P, M = 1+2*phi*q, 1-2*psi*q
        if min(P, M) <= 0:
            raise ValueError("trial amplitude does not have a Lorentzian weak metric")
        A, B, E = a*math.sqrt(P), a*math.sqrt(M), math.exp(logE)
        s = vm*qp/B
        gamma = math.sqrt(1+s*s)
        return {"a": a, "H": H, "phi": phi, "psi": psi,
                "psi_N": psi_N, "q": q, "qp": qp, "P": P, "M": M,
                "A": A, "B": B, "E": E, "W": B*self.S(chi),
                "omega": E*(gamma+s), "aberration": gamma+s,
                "peculiar_velocity": s/gamma}

    def _ray_rhs(self, chi, state, anchor):
        N, logE, affine = state
        g = self._geometry(chi, N, logE, anchor)
        ah = g["a"]*g["H"]
        root = math.sqrt(g["M"]/g["P"])
        return [-ah*root,
                ah*root-ah*g["psi_N"]*g["q"]/math.sqrt(g["M"]*g["P"])
                -g["phi"]*g["qp"]/g["P"], g["B"]/g["E"]]

    def _angular_rhs(self, chi, state, ray, anchor):
        N, logE = ray.sol(chi)[:2]
        g = self._geometry(chi, N, logE, anchor)
        theta, L = state
        m = 1/(g["B"]*self.S(chi)**2*g["E"])
        n = g["E"]*g["B"]*g["a"]**2*g["q"]*(
            g["phi"]/g["A"]**2+g["psi"]/g["B"]**2)
        return [m*L, n*theta]

    def _event_record(self, chi, ray, anchor):
        N, logE, affine = ray.sol(chi)
        g = self._geometry(chi, N, logE, anchor)
        return {"chi": float(chi), "N": float(N), "a": g["a"],
                "affine": float(affine), "observed_z": g["omega"]-1,
                "omega": g["omega"], "static_frequency": g["E"],
                "peculiar_velocity": g["peculiar_velocity"],
                "areal_screen_radius": g["W"],
                "Phi": g["phi"]*g["q"], "Psi": g["psi"]*g["q"]}

    def maps(self, anchor=None, z_l=.3, z_s=1., check_reciprocity=True):
        """Integrate one central ray and all three compatible physical maps.

        Inputs hold observer event, measured redshifts and the chosen sky axis
        fixed. Physical source transverse position is handled by the caller;
        it must not additionally freeze inferred beta and predicted images.
        """
        anchor = np.zeros(6) if anchor is None else np.asarray(anchor, float)
        if anchor.shape != (6,) or not np.all(np.isfinite(anchor)):
            raise ValueError("anchor must contain the six finite physical coordinates")
        if not (0 < z_l < z_s < 2.05):
            raise ValueError("require 0<z_l<z_s<2.05, inside the z=2.1 anchor domain")
        go = self._geometry(0., 0., 0., anchor)
        logEo = -math.log(go["aberration"])
        # Stop beyond the requested source but before the anchor domain. A
        # redshift event avoids extrapolating the propagator even for trials.
        def source_event(chi, state):
            return self._geometry(chi, state[0], state[1], anchor)["omega"]-(1+z_s)
        source_event.terminal = True
        source_event.direction = 1
        ray = solve_ivp(lambda c, y: self._ray_rhs(c, y, anchor),
                        (0., self._chi_max*.999), [0., logEo, 0.],
                        events=source_event, dense_output=True, method="DOP853",
                        rtol=self.rtol, atol=self.atol, max_step=.012)
        if not ray.success or not len(ray.t_events[0]):
            raise RuntimeError("source event was not reached inside the supported domain")
        chi_s = float(ray.t_events[0][0])
        chi_l = brentq(lambda c: self._geometry(c, *ray.sol(c)[:2], anchor)["omega"]
                       -(1+z_l), 0., chi_s, xtol=2e-13)
        observer = self._event_record(0., ray, anchor)
        lens = self._event_record(chi_l, ray, anchor)
        source = self._event_record(chi_s, ray, anchor)
        # Regular singular origin: L=c theta_o chi**2/2+O(chi**3),
        # theta=theta_o[1+q'(0)(phi_o+psi_o)chi/2]+O(chi**2).
        eps = 1e-7
        phi_o, psi_o, _, _ = self.coefficients(0., anchor)
        theta_o = go["aberration"]
        slope = .5*self.q_prime(0.)*(phi_o+psi_o)
        Eo = math.exp(logEo)
        initial = [theta_o*(1+slope*eps),
                   Eo*self.q_prime(0.)*(phi_o+psi_o)*theta_o*eps**2/2]
        optical = solve_ivp(lambda c, y: self._angular_rhs(c, y, ray, anchor),
                            (eps, chi_s), initial, dense_output=True,
                            method="DOP853", rtol=self.rtol, atol=self.atol,
                            max_step=.012)
        ls = solve_ivp(lambda c, y: self._angular_rhs(c, y, ray, anchor),
                       (chi_l, chi_s), [0., lens["areal_screen_radius"]*lens["omega"]],
                       dense_output=True, method="DOP853", rtol=self.rtol,
                       atol=self.atol, max_step=.012)
        if not optical.success or not ls.success:
            raise RuntimeError("angular Jacobi integration failed")
        d_ol = lens["areal_screen_radius"]*optical.sol(chi_l)[0]
        d_os = source["areal_screen_radius"]*optical.y[0, -1]
        d_ls = source["areal_screen_radius"]*ls.y[0, -1]
        if min(d_ol, d_os, d_ls) <= 0:
            raise ValueError("configuration crosses a conjugate point; positive scalar branch required")
        reciprocity = {"checked": bool(check_reciprocity)}
        if check_reciprocity:
            sl = solve_ivp(lambda c, y: self._angular_rhs(c, y, ray, anchor),
                           (chi_s, chi_l), [0., -source["areal_screen_radius"]*source["omega"]],
                           method="DOP853", rtol=self.rtol, atol=self.atol,
                           max_step=.012)
            if not sl.success:
                raise RuntimeError("reverse lens-source Jacobi integration failed")
            d_sl = lens["areal_screen_radius"]*sl.y[0, -1]
            expected = source["omega"]/lens["omega"]
            reciprocity.update({"D_sl": float(d_sl),
                                "omega_s_over_omega_l": expected,
                                "relative_residual": float(d_sl/(d_ls*expected)-1)})
            # The reverse observer-vertex solution is singular only in the
            # polar coordinate theta. Its canonical angular momentum is
            # regular: D_reverse(0)=-L(0)/E_o. Extrapolate that regular limit.
            for label, event, distance in (("ol", lens, d_ol), ("os", source, d_os)):
                reverse = solve_ivp(
                    lambda c, y: self._angular_rhs(c, y, ray, anchor),
                    (event["chi"], eps),
                    [0., -event["areal_screen_radius"]*event["omega"]],
                    method="DOP853", rtol=self.rtol, atol=self.atol, max_step=.012)
                if not reverse.success:
                    raise RuntimeError("reverse observer-segment Jacobi integration failed")
                L0 = reverse.y[1, -1]/(1-2*slope*eps)
                reverse_distance = -L0/Eo
                reciprocity["D_"+label[::-1]] = float(reverse_distance)
                reciprocity["relative_residual_"+label] = float(
                    reverse_distance/(distance*event["omega"])-1)
        assumptions = ("conditional normalized n=2 observer dipole; positive axial ray mu=1",
                       "full six-coordinate physical anchor, linear action-native evolution",
                       "measured endpoint redshifts; matter observer/lens/source tetrads",
                       "cosmological propagation only; main galaxy encounter excluded",
                       "axial isotropic screen, paraxial thin-plane application",
                       "finite amplitudes test only the declared truncated-metric completion")
        sample_chi = np.linspace(0., chi_s, 201)
        sample_state = ray.sol(sample_chi)
        metrics = [self._geometry(c, n, e, anchor)
                   for c, n, e in zip(sample_chi, sample_state[0], sample_state[1])]
        max_phi = float(max(abs(g["phi"]*g["q"]) for g in metrics))
        max_psi = float(max(abs(g["psi"]*g["q"]) for g in metrics))
        diagnostics = {"max_abs_Phi_on_ray": max_phi,
                       "max_abs_Psi_on_ray": max_psi,
                       "max_relative_metric_perturbation": 2*max(max_phi, max_psi),
                       "max_abs_matter_peculiar_velocity": float(
                           max(abs(g["peculiar_velocity"]) for g in metrics)),
                       "metric_check_sampling_points": len(metrics),
                       "lens_redshift_residual": abs(lens["observed_z"]-z_l),
                       "source_redshift_residual": abs(source["observed_z"]-z_s)}
        return TransportMaps(np.eye(2)*d_ol, np.eye(2)*d_os, np.eye(2)*d_ls,
                             observer, lens, source, reciprocity, diagnostics, assumptions)

    def response(self, step=2e-3, z_l=.3, z_s=1.):
        """Central unit sensitivities to all six physical anchor amplitudes.

        Each column has its own step scaled by metric/velocity row size so
        the actual weak perturbation remains small. No physical amplitude,
        reference-state covariance, or supernova calibration is supplied.
        """
        base = self.maps(z_l=z_l, z_s=z_s)
        ns = np.linspace(-math.log1p(z_s)-.01, 0., 120)
        # At the source the harmonic is small; using unweighted rows is a
        # conservative, reproducible weak-field step choice for each mode.
        rows = self.rows(ns)
        scale = np.maximum(1., np.max(np.abs(rows[:, [0, 1, 4], :]), axis=(0, 1)))
        steps = step/scale
        derivatives = np.empty((3, 6))
        event_derivatives = np.empty((4, 6))
        finite = []
        for i, h in enumerate(steps):
            delta = np.eye(6)[i]*h
            plus = self.maps(delta, z_l, z_s)
            minus = self.maps(-delta, z_l, z_s)
            derivatives[:, i] = (plus.scalar_maps-minus.scalar_maps)/(2*h)
            event_derivatives[:, i] = np.array([
                plus.lens["chi"]-minus.lens["chi"], plus.source["chi"]-minus.source["chi"],
                plus.lens["N"]-minus.lens["N"], plus.source["N"]-minus.source["N"]])/(2*h)
            finite.append({"anchor_coordinate": ANCHOR_NAMES[i], "step": float(h),
                           "plus_maps": plus.scalar_maps.tolist(),
                           "minus_maps": minus.scalar_maps.tolist(),
                           "plus_endpoints": {"lens": plus.lens, "source": plus.source},
                           "minus_endpoints": {"lens": minus.lens, "source": minus.source},
                           "plus_reciprocity": plus.reciprocity,
                           "minus_reciprocity": minus.reciprocity,
                           "plus_perturbation_diagnostics": plus.perturbation_diagnostics,
                           "minus_perturbation_diagnostics": minus.perturbation_diagnostics})
        return {"background": base.as_dict(), "anchor_coordinates": list(ANCHOR_NAMES),
                "map_order": list(MAP_NAMES), "d_maps_d_anchor": derivatives.tolist(),
                "event_order": ["chi_l", "chi_s", "N_l", "N_s"],
                "d_events_d_anchor": event_derivatives.tolist(),
                "finite_trials": finite, "profile_normalization": self.normalization,
                "profile": "N_Q sin(2 sqrt(K) chi) mu; mu=1 for executed ray",
                "profile_volume": "dimensional S3 dV_gamma; H0=1",
                "max_no_slip_row_residual": self.max_slip_row,
                "max_relative_no_slip_row_residual": self.max_relative_slip_row,
                "anchor_to_canonical": self.anchor_to_canonical.tolist(),
                "classification": "conditional six-coordinate unit response; no action-derived amplitude"}

    def seven_state_control(self, response=None, z_l=.3, z_s=1.):
        """Apply the inherited seven-state equation as a conformal Jacobi control.

        All six unit columns are evaluated through ``optical_rhs``. On the
        background ray, delta(theta)''+2H_K delta(theta)'=q(phi+psi)/S_K**2.
        Thus kappa=psi*q-delta(theta) obeys precisely the inherited equation
        kappa''+2H_K kappa'=F. The harmonic identity gives a stable expression

          F=q(psi_chichi-8K psi)+2 psi_chi(q_chi+H_K q)
            +(psi-phi)q/S_K**2.

        This is algebraically the original forcing
        (psi*q)''+2H_K(psi*q)'-q(phi+psi)/S_K**2, including the angular
        geodesic term. gamma1=gamma2=0 by axial rotation symmetry.

        The zeta_gamma slot and its source are unused and zero in this
        *conformal Jacobi control*. The complete frequency is supplied by
        the metric ray; zero here is not a claim of zero redshift response.
        The measured-redshift endpoint shifts in ``response`` then give
        delta ln D_ob=delta N_b+H_K delta chi_b-kappa_b. This is compared
        to the independently finite-differenced full physical maps.
        """
        response = self.response(z_l=z_l, z_s=z_s) if response is None else response
        base = response["background"]
        cl, cs = base["lens"]["chi"], base["source"]["chi"]
        eps = 1e-7
        initial = np.zeros((7, 6))
        row0 = self.rows(0.)
        rowN0 = self.rows(0., 1)
        H0 = float(self.background.sol(0.)[2])
        HN0 = float(bg.rhs(0., self.background.sol(0.))[2])
        qp0 = self.q_prime(0.)
        kap0 = -row0[4]*qp0
        p0 = .5*qp0*(row0[1]-row0[0])
        F0 = qp0*(-H0)*(5*rowN0[1]-rowN0[0])
        initial[optical.IDX.kappa] = kap0+p0*eps+F0*eps**2/6
        initial[optical.IDX.p_kappa] = p0+F0*eps/3
        N_eps = -H0*eps+.5*H0*(H0+HN0)*eps**2

        def rhs(chi, state):
            N = state[0]
            a = math.exp(N)
            H = float(self.background.sol(N)[2])
            HN = float(bg.rhs(N, self.background.sol(N))[2])
            Nc = -a*H
            Ncc = a*a*H*(H+HN)
            rows, rowsN, rowsNN = self.rows(N), self.rows(N, 1), self.rows(N, 2)
            phi, psi = rows[0], rows[1]
            psic = rowsN[1]*Nc
            psicc = rowsNN[1]*Nc*Nc+rowsN[1]*Ncc
            S = self.S(chi)
            HK = math.cos(math.sqrt(self.K)*chi)/S
            q, qp = self.q(chi), self.q_prime(chi)
            F = q*(psicc-8*self.K*psi)+2*psic*(qp+HK*q)+(psi-phi)*q/S**2
            states = state[1:].reshape(7, 6)
            rates = np.column_stack([optical.optical_rhs(
                chi, states[:, j], self.K, np.array([0., F[j], 0., 0.]))
                for j in range(6)])
            return np.r_[Nc, rates.ravel()]

        result = solve_ivp(rhs, (eps, cs), np.r_[N_eps, initial.ravel()],
                           dense_output=True, method="DOP853", max_step=.001,
                           rtol=2e-12, atol=2e-14)
        if not result.success:
            raise RuntimeError("inherited seven-state Jacobi control failed")
        states_l = result.sol(cl)[1:].reshape(7, 6)
        states_s = result.y[1:, -1].reshape(7, 6)
        endpoints = np.asarray(response["d_events_d_anchor"])
        actual = np.asarray(response["d_maps_d_anchor"])[:2]
        fractional = np.array([
            endpoints[2]+math.cos(math.sqrt(self.K)*cl)/self.S(cl)*endpoints[0]
            -states_l[optical.IDX.kappa],
            endpoints[3]+math.cos(math.sqrt(self.K)*cs)/self.S(cs)*endpoints[1]
            -states_s[optical.IDX.kappa]])
        distances = np.array([base["D_ol"][0][0], base["D_os"][0][0]])
        predicted = fractional*distances[:, None]
        return {"classification": "inherited seven-state conformal Jacobi control; full frequency from metric ray",
                "map_order": ["D_ol", "D_os"], "anchor_coordinates": list(ANCHOR_NAMES),
                "d_maps_d_anchor": predicted.tolist(),
                "full_metric_d_maps_d_anchor": actual.tolist(),
                "difference": (predicted-actual).tolist(),
                "max_absolute_difference": float(np.max(abs(predicted-actual))),
                "lens_seven_state_unit_columns": states_l.tolist(),
                "source_seven_state_unit_columns": states_s.tolist(),
                "state_order": ["zeta_gamma_unused", "kappa", "p_kappa", "gamma1", "p_gamma1", "gamma2", "p_gamma2"],
                "frequency_slot": "unused zero in this control; not the physical frequency perturbation",
                "initial_kappa": kap0.tolist(), "initial_p_kappa": p0.tolist(),
                "forcing": "(psi*q)''+2H_K(psi*q)'-q*(phi+psi)/S_K^2; derivatives along background chi"}
