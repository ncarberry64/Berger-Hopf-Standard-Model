"""Export a verified scalar Taylor model from existing action checkpoints.

This is algebraic recovery, not an independent action-arithmetic reproduction.
The recovered result must match the original certificate byte for byte.
"""
import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

import certify_n12_gate7_shared_scalar_output as scalar
from flint import arb, ctx


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--evidence-root', type=Path, required=True)
    parser.add_argument('--adjoint', type=Path, required=True)
    parser.add_argument('--certificate', type=Path, required=True)
    parser.add_argument('--checkpoints', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise FileExistsError('preserve prior evidence; choose a fresh output')
    ctx.prec = 512
    original = args.certificate.read_bytes()
    certificate = json.loads(original)
    wanted = {certificate[k]['coefficients_SHA256']
              for k in ('physical_scalar', 'physical_scalar_anchor_deviation')}
    captured = {}
    summarize = scalar.summary

    def capture(value):
        result = summarize(value)
        key = result['coefficients_SHA256']
        if key in wanted:
            captured[key] = [[str(v.mid().fmpq()), str(v.rad().fmpq())]
                             for v in [value.c, *value.a.entries(), value.r]]
        return result

    # Fail before evaluation if an action checkpoint is absent. This command
    # must never silently turn export into fresh expensive action arithmetic.
    for term in certificate['action_terms']:
        if not (args.checkpoints / (term + '.json')).is_file():
            raise FileNotFoundError(term)
    scalar.summary = capture
    def exact_radius_constructor(mid=None, rad=None):
        if rad is None:
            return arb(mid)
        # Passing a rational-string radius through an Arb value can inflate
        # its 30-bit magnitude by one ulp. Its exact dyadic tuple preserves
        # the saved magnitude. Equality is mandatory: never shrink a ball.
        if not rad.rad().is_zero():
            raise ArithmeticError('checkpoint radius must be exact')
        rational = Fraction(str(rad.fmpq()))
        denominator = rational.denominator
        if denominator & (denominator-1):
            raise ArithmeticError('checkpoint radius must be dyadic')
        value = arb(mid, (rational.numerator, 1-denominator.bit_length()))
        if value.rad().fmpq() != rad.fmpq():
            # A full-width odd 30-bit magnitude is rounded up even through
            # the tuple constructor. An interior preimage recovers that same
            # stored magnitude. The result, not the preimage, must equal the
            # original radius exactly; a smaller resulting ball is rejected.
            value = arb(mid, (2*rational.numerator-1, -denominator.bit_length()))
            if value.rad().fmpq() != rad.fmpq():
                raise ArithmeticError('checkpoint radius did not round-trip exactly')
        return value

    scalar.arb = exact_radius_constructor
    recovered = scalar.evaluate(args.evidence_root.resolve(), certificate['family'],
                                args.adjoint.resolve(), lambda *_: None,
                                args.checkpoints.resolve())
    if scalar.saved_reader.encoded(recovered) != original:
        raise ArithmeticError('checkpoint recovery differs from original certificate')
    if set(captured) != wanted:
        raise ArithmeticError('missing physical Taylor coefficients')
    for digest, values in captured.items():
        if hashlib.sha256(scalar.saved_reader.encoded(values)).hexdigest().upper() != digest:
            raise ArithmeticError('coefficient fingerprint mismatch')
    result = dict(
        algorithm='VERIFIED_SCALAR_TAYLOR_CHECKPOINT_EXPORT_V1',
        certificate_SHA256=hashlib.sha256(original).hexdigest().upper(),
        exporter_SHA256=scalar.saved_reader.sha(Path(__file__)),
        checkpoint_recovery_byte_identical=True,
        independent_action_reproduction=False,
        groups=certificate['groups'], parameters=certificate['parameters'],
        coefficient_order='constant, all linear coefficients, nonlinear remainder',
        coefficient_encoding='exact rational midpoint and radius pairs',
        models={k: captured[certificate[k]['coefficients_SHA256']]
                for k in ('physical_scalar', 'physical_scalar_anchor_deviation')},
        Gate7_closed=False, FULL_BHSM_COMPLETE=False)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('xb') as output:
        output.write(scalar.saved_reader.encoded(result))
    print(json.dumps(dict(checkpoint_recovery_byte_identical=True,
                         coefficient_models=len(captured), output=str(args.out))))


if __name__ == '__main__':
    main()
