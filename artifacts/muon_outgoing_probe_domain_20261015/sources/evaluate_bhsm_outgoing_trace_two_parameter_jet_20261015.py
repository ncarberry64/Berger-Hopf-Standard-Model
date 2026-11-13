"""Materialize the independently evaluated two-parameter domain-jet checks.

The nontrivial polynomial graph is a test fixture, not physical Cauchy data.
These checks do not satisfy the physical outgoing derivative admission gate.
"""
from pathlib import Path
from hashlib import sha256
import argparse
import json

from test_bhsm_outgoing_trace_two_parameter_jet_20261015 import checks


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',required=True)
    args=p.parse_args();out=Path(args.output).resolve();out.mkdir(parents=True,exist_ok=False)
    here=Path(__file__).resolve().parent
    names=(Path(__file__).name,'bhsm_outgoing_trace_two_parameter_jet_20261015.py',
        'test_bhsm_outgoing_trace_two_parameter_jet_20261015.py')
    result=dict(classification='EVALUATED_ALGEBRAIC_TWO_PARAMETER_OUTGOING_TRACE_JET_CONSUMER_CHECKS',
        checks=checks(),fixture='Explicit nontrivial bivariate polynomial graph C(E,B)V(E,B)=0 with independent joined trace T(E,B). This is an algebraic test, not physical exterior data.',
        derivative_scope='Literal E/B/EB derivatives of Gamma=C T, projected on supplied fixed analytic left/right frames. Total pole-path EB derivative additionally requires moving mode jets.',
        exact_mixed_contact='L C (T_EB R-V_EB a)+L C_E (T_B R-V_B a)+L C_B (T_E R-V_E a)',
        exact_remainder='L C_EB (T R-V a)+L (C_EB V+C_E V_B+C_B V_E+C V_EB) a',
        allowed_frame_basis_scope='V->V H(E,B), a->H(0,0)^-1 a. Complete transverse mixed sum invariant under nonconstant allowed-frame basis; transport-only term generally changes.',
        boundary_row_basis_scope='An energy/field dependent change of C rows changes the fixed-frame mixed pairing through lower derivative contacts. No unconditional row-basis invariance is claimed.',
        missing_physical_jets_assumed_zero=False,actual_physical_outgoing_operator_supplied=False,
        physical_derivative_gate_passed=False,physical_two_spin_normalization=None,
        physical_magnetic_moment=None,coupled_matching_corrections_applied=0,
        source_sha256={name:sha256((here/name).read_bytes()).hexdigest()for name in names})
    (out/'result.json').write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(output=str(out),result_sha256=sha256((out/'result.json').read_bytes()).hexdigest())))


if __name__=='__main__':main()
