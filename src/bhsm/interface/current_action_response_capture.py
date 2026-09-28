"""Read the local internal solves of an unchanged, fingerprinted rate owner.

The saved endpoint-sector packets bind the original evaluator byte for byte.
A scoped return observer exposes its already-computed local variables without
patching that evaluator or evaluating a second, sector-specific internal state.
The source fingerprint is a contract for the observed local-variable layout.
"""
import hashlib
import inspect
import sys
import numpy as np
from flint import arb


RATE_SOURCE_SHA256 = '0DC531574372EAA6C69AFAD3B4790A1C7EF52C18E7BA52B6C8FAAA1D442BFC2C'


def evaluate_shared_rate(owner, state, descriptor, weights, reference, directions):
    """Return the unchanged owner's result and its common local internal state.

    This observer is confined to the calling Python thread and restored even
    on failure. Existing profiling is rejected instead of being overwritten.
    """
    function = owner._rate_enclosure
    actual = hashlib.sha256(inspect.getsource(function).encode()).hexdigest().upper()
    if actual != RATE_SOURCE_SHA256:
        raise ValueError('rate owner changed; reconcile the internal capture explicitly')
    if sys.getprofile() is not None:
        raise RuntimeError('shared-rate return capture requires an unprofiled thread')
    captured = {}
    def observe(frame, event, arg):
        if event == 'return' and frame.f_code is function.__code__ and arg is not None:
            captured.update(frame.f_locals)
    sys.setprofile(observe)
    try:
        result = function(state, descriptor, weights, reference, directions)
    finally:
        sys.setprofile(None)
    if not captured:
        raise RuntimeError('rate owner returned without the expected internal state')
    names = dict(H='Hraw', psi='psi', eigenvalue='eigenvalue', border='K',
                 rhs='rhs', hard='hard', bpsi='bpsi', cpsi='cpsi',
                 remainder='remainder', delta='delta', norm_G='norm',
                 descriptor='s', raw_state='state', configuration='configuration')
    shared = {name: captured[local] for name, local in names.items()}
    if directions is None:
        return result, shared
    c = captured
    count, n = c['count'], owner.REDUCED
    shared.update(dpsi=c['dline'], deigenvalue=np.array(c['slopes'], dtype=object),
                  dhard_b=c['dresponse'], H_first_on_psi=c['directional'][:, 0, :count],
                  H_first_on_hard=c['directional'][:, 1, :count],
                  hard_first_rhs=c['response_direction_rhs'],
                  raw_directions=c['raw_ball'], descriptor_first=c['ds'])
    scalar_first = np.empty((4, count), dtype=object)
    # These short scalar contractions are recomposed from the owner's D3/D4
    # operands and solves, without reevaluating any action derivatives.
    for k in range(count):
        dc = c['fourth'][k, 0]+c['dynamic_T'][k]
        dR = c['fourth'][k, 1]+c['dynamic_T'][count+k]
        for i in range(n):
            dc += 2*c['dline'][i, k]*c['output_fixed'][i, 0]
            dR += 2*c['dline'][i, k]*c['output_fixed'][i, 1]
        db = c['dresponse'][n, k]
        dd = dc*c['bpsi']+c['cpsi']*db+c['ds'][k]*c['remainder']+c['s']*dR
        scalar_first[:, k] = [dc, dR, db, dd]
    if not all(isinstance(v, arb) and v.is_finite() for v in scalar_first.flat):
        raise ArithmeticError('finite shared scalar response required')
    shared['scalar_first_dc_dR_db_ddelta'] = scalar_first
    return result, shared
