"""Reuse a verified physical-point base without narrowing interval states."""
from contextlib import contextmanager
import numpy as np
from flint import ctx
from bhsm.interface.physical_arb_inputs import preserve_ball, same_ball_vector
from bhsm.interface.physical_hs_value import verified_eigenline
from bhsm.interface.current_green_midpoint_coordinate_error import _real_binary64


class VerifiedHessianBase:
    """Original action jets and index-24 eigenpair, reusable across row tasks.

    The producer owns source/point fingerprints and independent recomputation.
    This object is process-local and must not be shared between threads.
    """

    def __init__(self, cert, state, reference):
        self.cert = cert
        self.precision = ctx.prec
        self.state = np.asarray([preserve_ball(v) for v in state], dtype=object)
        self.reference = _real_binary64(reference, 'stored branch reference').copy()
        if self.state.shape != (cert.STATE,) or self.reference.shape != (cert.REDUCED,):
            raise ValueError('complete physical state and stored reference required')
        self.state.flags.writeable = False
        self.reference.flags.writeable = False
        self.jets = cert._arb_action_jets(self.state)
        checks = []
        with verified_eigenline(cert, checks, expected_index=24, normalize_proposal_center=True):
            self.eigenpair = cert._eigenline(self.jets.hessian_arb, self.jets.hessian_mid, self.reference)
        if len(checks) != 1 or checks[0].get('validation_passed') is not True:
            raise ArithmeticError('one verified physical-point eigenpair required')
        self.eigenpair_verification = checks[0]
        if ctx.prec != self.precision:
            raise RuntimeError('physical base construction changed precision')

    @contextmanager
    def use(self):
        """Install only checked base lookups; restore both original functions."""
        cert = self.cert
        original_jets, original_eigen = cert._arb_action_jets, cert._eigenline
        if ctx.prec != self.precision:
            raise RuntimeError('cached physical base precision differs')

        def jets(state):
            if ctx.prec != self.precision or not same_ball_vector(state, self.state):
                raise RuntimeError('cached physical base state or precision differs')
            return self.jets

        def eigen(hessian, midpoint, reference):
            if (ctx.prec != self.precision or hessian is not self.jets.hessian_arb
                    or midpoint is not self.jets.hessian_mid
                    or not np.array_equal(reference, self.reference)):
                raise RuntimeError('cached physical eigenpair operands differ')
            return self.eigenpair

        cert._arb_action_jets, cert._eigenline = jets, eigen
        try:
            yield self
        finally:
            cert._arb_action_jets, cert._eigenline = original_jets, original_eigen
