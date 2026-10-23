"""New exact variational controls; no prior production/check replay."""
from pathlib import Path
import importlib.util

import sympy as sp


ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('seam_evidence', ROOT/'scripts/replay_muon_fermion_seam_identification.py')
EVIDENCE=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(EVIDENCE)


def test_zero_fermionic_derivative_is_tied_to_actual_typed_incidence():
    records, inventory=EVIDENCE.retained_action_inventory(ROOT)
    assert len(inventory['incidence'])==5
    assert all(r['execution'].startswith('AST read only') for r in records)
    proof=EVIDENCE.exact_compatibility_derivatives()
    assert proof['fermionic_constraint_rank']==0
    assert proof['D_bar_w_D_Psi_Scompat']=='0'
    assert proof['D_b_D_bar_w_D_Psi_Scompat']=='0'


def test_seam_chain_rule_contains_unselected_identification_jets():
    # Independent barred/unbarred Grassmann labels retain the action's
    # bilinear order. Even coefficient jets commute; no fermion reordering.
    b=sp.Symbol('b',real=True)
    L4=sp.Function('L4')(b);L5=sp.Function('L5')(b);H=sp.Function('H')(b)
    direct=sp.diff(-L4*H*L5,b)
    expected=-(sp.diff(L4,b)*H*L5+L4*sp.diff(H,b)*L5+L4*H*sp.diff(L5,b))
    assert sp.expand(direct-expected)==0
    assert direct.has(sp.Derivative(L4,b),sp.Derivative(L5,b))


def test_on_mode_identity_does_not_select_complement_attachment():
    # Operator restriction theorem, not a model/domain choice or new fit.
    # From B W=I, (I-W B)W=0. Thus a restriction T W=I does not
    # determine T on ker B. This proof does not require the complement to
    # be finite dimensional, or require insertion p to be in Dom(D).
    W,B,T=sp.symbols('W B T',commutative=False)
    residual=sp.expand((T*(1-W*B))*W)
    # Use the single known relation explicitly inside each ordered word.
    reduced=sp.expand(residual).subs(T*W*B*W,T*W)
    assert reduced==0


def test_nonlinear_identification_retains_gradient_second_jet_and_source_jet():
    # An even coefficient-jet chain-rule control, not a physical field map.
    # It tests the nonlinear term that the three-factor linear rule omits.
    w,g,b=sp.symbols('w g b')
    F=sp.Function('F')(w,g,b)
    H=sp.Function('H')(b)
    action=-H*F**2/2
    pair=-H*sp.diff(F,w)*sp.diff(F,g)
    gradient_second=-H*F*sp.diff(F,w,g)
    assert sp.simplify(sp.diff(action,w,g)-pair-gradient_second)==0
    assert sp.simplify(sp.diff(action,w,g,b)-sp.diff(pair+gradient_second,b))==0
    assert sp.diff(gradient_second,b).has(sp.diff(F,w,g,b))
