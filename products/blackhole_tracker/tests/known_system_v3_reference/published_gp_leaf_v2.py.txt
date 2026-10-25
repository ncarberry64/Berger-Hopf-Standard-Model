"""Prospective Gaussian covariance prototype; no observation loading or fitting.

Lam et al. 2022 ApJS260:55 AppendixF motivates native diagonal measurement
variance plus a variance-normalized F10-type Matern3/2 approximation
(epsilon=.01, sigma**2=k(0)) and a damped SHO
(F8,Q=1/sqrt2). Lam & Lu2023 sectionV uses this four-parameter law. This is
an instrumental/variability working covariance, not an extra BHSM potential.
The ordinary optical exterior has its BHSM hypersurface interpretation once.

This prototype uses celerite2 public APIs. In particular it implements F10
explicitly after resolving the printed equation's ambiguous normalization
by F9 and its stated epsilon->0 limit: celerite2's built-in Matern32Term uses a different oscillatory
approximation, so that term is not silently substituted for the paper's F10.
No source error, covariance, mass, distance or correction is manufactured.
"""
from dataclasses import dataclass
import math

import numpy as np
from celerite2 import GaussianProcess, terms


@dataclass(frozen=True)
class Hyperparameters:
    matern_sigma_mag: float
    matern_rho_days: float
    sho_sigma_mag: float
    sho_omega_rad_per_day: float
    epsilon: float = .01

    def __post_init__(self):
        values = tuple(self.__dict__.values())
        if any(isinstance(x, (bool, np.bool_)) for x in values):
            raise ValueError('Boolean covariance parameters are invalid')
        if not np.isfinite(values).all():
            raise ValueError('Finite covariance parameters are required')
        if min(self.matern_sigma_mag, self.sho_sigma_mag) < 0:
            raise ValueError('Covariance amplitudes must be nonnegative')
        if min(self.matern_rho_days, self.sho_omega_rad_per_day) <= 0:
            raise ValueError('Positive covariance timescale/frequency required')
        if not 0 < self.epsilon < 1:
            raise ValueError('Matern approximation requires 0<epsilon<1')
        with np.errstate(over='ignore', under='ignore', divide='ignore'):
            derived = np.array([self.matern_sigma_mag, self.sho_sigma_mag])**2
            rate = np.float64(math.sqrt(3.))/self.matern_rho_days
        if not np.isfinite(derived).all() or not np.isfinite(rate) or rate <= 0:
            raise ValueError('Unrepresentable derived covariance variance/rate')
        if any(s > 0 and v == 0 for s,v in zip((self.matern_sigma_mag,self.sho_sigma_mag),derived)):
            raise ValueError('Positive covariance amplitude underflows in variance')

    @property
    def sho_S0(self):
        """S0 = sigma_SHO**2/(omega0*Q), Q=1/sqrt2."""
        return self.sho_sigma_mag ** 2 * math.sqrt(2.) / self.sho_omega_rad_per_day


class PaperMatern32(terms.Term):
    def __init__(self, sigma, rho, epsilon=.01):
        self.sigma, self.rho, self.epsilon = map(float, (sigma, rho, epsilon))

    def get_coefficients(self):
        Hyperparameters(self.sigma, self.rho, 0., 1., self.epsilon)
        w = math.sqrt(3.) / self.rho
        e = self.epsilon
        ar = self.sigma ** 2 / 2 * np.array([1 + 1 / e, 1 - 1 / e])
        cr = w * np.array([1 - e, 1 + e])
        empty = np.empty(0)
        return ar, cr, empty, empty, empty, empty


def kernel(parameters):
    """Positive stationary sum with explicit zero-amplitude faces."""
    p = parameters
    return (PaperMatern32(p.matern_sigma_mag, p.matern_rho_days, p.epsilon)
            + terms.SHOTerm(sigma=p.sho_sigma_mag,
                            w0=p.sho_omega_rad_per_day, Q=1 / math.sqrt(2.)))


def direct_kernel(lag_days, parameters):
    """Independent closed-form F8/F10 evaluation; no celerite coefficients."""
    p = parameters
    tau = np.abs(np.asarray(lag_days, dtype=float))
    x = math.sqrt(3.) * tau / p.matern_rho_days
    # e^-x[cosh(e*x)+sinh(e*x)/e], without large cosh or small-lag subtraction.
    matern = p.matern_sigma_mag ** 2 * np.exp(-(1-p.epsilon)*x) * (
        1 + .5 * (1 - 1 / p.epsilon) * np.expm1(-2*p.epsilon*x))
    a = p.sho_omega_rad_per_day * tau / math.sqrt(2.)
    sho = p.sho_sigma_mag ** 2 * np.exp(-a) * (np.cos(a) + np.sin(a))
    return matern + sho


def dense_covariance(time_days, supplied_sigma_mag, parameters):
    t, s = np.asarray(time_days, dtype=float), np.asarray(supplied_sigma_mag, dtype=float)
    value = direct_kernel(t[:, None] - t[None, :], parameters)
    value[np.diag_indices_from(value)] += s ** 2
    return value


class GaussianCovariance:
    """Owned factor; original row identities/order are retained by stable permutation.

    Times must already be native-relative coordinates in days; no clock conversion
    is inferred here. Positive supplied marginal errors stay unchanged. The total
    covariance is a declared hypothesis: diag(sigma_native**2)+K_Matern+K_SHO.
    """
    def __init__(self, time_days, supplied_sigma_mag, parameters):
        if not isinstance(parameters, Hyperparameters):
            raise ValueError('Validated Hyperparameters required')
        original_t = np.asarray(time_days)
        original_s = np.asarray(supplied_sigma_mag)
        if original_t.dtype.kind not in 'iuf' or original_s.dtype.kind not in 'iuf':
            raise ValueError('Numeric finite times/errors required')
        self.time = np.array(original_t, dtype=float, copy=True)
        self.sigma = np.array(original_s, dtype=float, copy=True)
        if self.time.ndim != 1 or self.time.size == 0 or self.sigma.shape != self.time.shape:
            raise ValueError('Nonempty equal-sized time/error vectors required')
        if not np.isfinite(self.time).all() or not np.isfinite(self.sigma).all() or np.any(self.sigma <= 0):
            raise ValueError('Finite times and strictly positive supplied errors required')
        with np.errstate(over='ignore', under='ignore'):
            diagonal = self.sigma**2
        if not np.isfinite(diagonal).all() or np.any(diagonal <= 0):
            raise FloatingPointError('Supplied variances cannot be represented without a floor')
        self.order = np.argsort(self.time, kind='stable')
        self.inverse_order = np.argsort(self.order, kind='stable')
        self.parameters = parameters
        # Translation only; no jitter, diagonal floor or random row tie breaking.
        self.sorted_time = self.time[self.order] - self.time[self.order[0]]
        if not np.isfinite(self.sorted_time).all():
            raise FloatingPointError('Native time differences overflow')
        self.gp = GaussianProcess(kernel(parameters), mean=0.)
        self.gp.compute(self.sorted_time, yerr=self.sigma[self.order], quiet=False)
        self.zero_deviance = -2 * float(self.gp.log_likelihood(np.zeros(len(self.time))))
        self.logdet = self.zero_deviance - len(self.time) * math.log(2*math.pi)
        if not np.isfinite([self.zero_deviance, self.logdet]).all():
            raise FloatingPointError('Unrepresentable covariance determinant')
        for item in (self.time, self.sigma, self.order, self.inverse_order, self.sorted_time):
            item.setflags(write=False)

    def _values(self, values):
        x = np.asarray(values)
        if x.dtype.kind not in 'iuf' or x.ndim not in (1, 2) or x.shape[0] != len(self.time) or not np.isfinite(x).all():
            raise ValueError('Finite original-order observation vector/matrix required')
        return np.asarray(x, dtype=float)

    def deviance(self, residual_mag):
        residual = self._values(residual_mag)
        if residual.ndim != 1:
            raise ValueError('One residual vector required')
        return -2 * float(self.gp.log_likelihood(residual[self.order]))

    def quadratic(self, residual_mag):
        # Direct public inverse/dot avoids cancellation of nearly equal deviances.
        residual = self._values(residual_mag)
        if residual.ndim != 1:
            raise ValueError('One residual vector required')
        value = float(residual @ self.inverse(residual))
        if not np.isfinite(value) or value < 0:
            raise FloatingPointError('Nonfinite/negative positive-covariance quadratic')
        return value

    def inverse(self, values):
        x = self._values(values)
        return self.gp.apply_inverse(x[self.order])[self.inverse_order]

    def color_independent_normal(self, standard_normals):
        """Generate a matching-law daughter from caller-supplied draws, no RNG here.

        Standard normals are in original row order; factorization is in stable
        chronological order. The result returns to original row order.
        """
        x = self._values(standard_normals)
        return self.gp.dot_tril(x[self.order])[self.inverse_order]


def conditional_deviance(time_days, supplied_sigma_mag, residual_mag, training_indices, parameters):
    """Exact Gaussian joint-minus-marginal predictive log density at FIXED params.

    Includes the determinant and Gaussian normalization for omitted rows. It is
    not an exact post-fit goodness pivot; parameters must be fitted on training
    only and the entire refit procedure calibrated separately. Arbitrary row
    subsets are valid for this Gaussian law, unlike independent Student
    innovations with a re-factorized middle deletion.
    """
    t, s, r = map(np.asarray, (time_days, supplied_sigma_mag, residual_mag))
    idx = np.asarray(training_indices)
    if idx.dtype.kind not in 'iu' or idx.ndim != 1 or idx.size == 0 or idx.size >= len(t):
        raise ValueError('A nonempty strict integer-index training subset required')
    if len(set(map(int, idx))) != len(idx) or np.any(idx < 0) or np.any(idx >= len(t)):
        raise ValueError('Unique in-range training indices required')
    full = GaussianCovariance(t, s, parameters)
    train = GaussianCovariance(t[idx], s[idx], parameters)
    return {'deviance': full.deviance(r) - train.deviance(r[idx]),
            'quadratic': full.quadratic(r) - train.quadratic(r[idx]),
            'logdet': full.logdet - train.logdet,
            'predicted_rows': len(t) - len(idx),
            'qualification': 'Fixed-parameter Gaussian conditional density; refit calibration required.'}
