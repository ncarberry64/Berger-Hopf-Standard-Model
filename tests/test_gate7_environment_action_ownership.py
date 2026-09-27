"""Ownership regression controls; no N12 action/derivative producer runs."""
import hashlib
import json
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'src')]
import record_n12_gate7_environment_action_ownership as audit
from bhsm.interface.aether_forward_channel_transfer import restrict_two_boundary_weyl_to_dirichlet_birth_jets
from bhsm.interface.ae2_covariant_seam_response import covariant_seam_response, covariant_effective_event_load_jet

OUT=ROOT/'artifacts/flagship_integration/gate7_environment_ownership_20260927'


def packet():return json.loads((OUT/'report.json').read_bytes())


def test_ten_local_terms_do_not_claim_full_joint_operator_exhaustion():
    d=packet();rows=d['local_ten_term_ledger']
    assert len(rows)==10 and len({x['name'] for x in rows})==10
    assert all(x['included_in_frozen_local_derivative'] for x in rows)
    assert all(not x['independent_external_environment_action'] for x in rows)
    assert d['local_action_exhausted_by_ten_terms']
    assert not d['full_outside_closed_operator_response_exhausted_by_ten_terms']
    calls=d['function_provenance'][audit.ACTION]['functions']['_arb_action_jets']['calls']
    assert '_integrand' in calls and '_boundary' in calls
    assert 'covariant_seam_response' not in calls and 'heat_regulator_value_and_force' not in calls
    coefficient=d['function_provenance']['src/bhsm/interface/aether_m4_standard_model_zeta_backreaction_v15_51.py']['functions']['standard_model_casimir_coefficient']
    assert 'Fraction(59, 30)' in coefficient['text']


def test_zero_external_source_retains_nonzero_formation_jet():
    # Algebra control of the actual zero-source owner; not a physical N12 value.
    jets={k:np.array([[1.,2.],[2.,v]]) for k,v in
          zip(('base','first_left','first_right','mixed_second'),(7.,3.,5.,11.))}
    result=restrict_two_boundary_weyl_to_dirichlet_birth_jets(jets)
    assert result['response']=='M_f=M11'
    for k in jets:assert np.array_equal(result[k],jets[k][1:,1:])
    assert result['base'][0,0]==7 and result['mixed_second'][0,0]==11
    assert not result['endpoint_load_imposed']


def test_existing_joint_response_keeps_child_and_contact_exactly_once():
    # Existing assembler, same retained sign convention, deliberately nonzero.
    mf=np.diag([3.,5.]);mc=np.diag([7.,11.]);w=np.diag([2.,4.]);u=np.array([[0.,1.],[-1.,0.]])
    seam=covariant_seam_response(mf,mc,w,u)
    assert np.array_equal(seam,mf+u.T@mc@u+w)
    assert np.array_equal(seam,np.diag([16.,16.]))
    derivative=covariant_effective_event_load_jet(np.eye(2),2*np.eye(2),u)
    assert np.array_equal(derivative,3*np.eye(2))


def test_absent_external_arm_does_not_trigger_invalid_promotion():
    d=packet()
    assert d['N12_ADDITIONAL_ENVIRONMENT_BOUNDARY_ACTION']=='ABSENT_BY_DECLARED_MODEL'
    assert d['promotion_conditions']['external_birth_forcing_zero']
    assert d['promotion_conditions']['no_separate_instantiated_N12_W_E']
    assert not d['promotion_conditions']['all_active_fixed_environment_blocks_inside_native_packet']
    assert not d['promoted_to_N12_FIXED_ENVIRONMENT_MATERIAL_RESPONSE_7x73']
    assert all(x['retained_in_declared_closed_model'] and not x['zeroed_by_this_audit'] for x in d['retained_internal_blocks'])
    assert d['no_internal_response_relabelled_as_extra_Lambda_E']
    assert not d['scientific_producers_run'] and not d['derivative_7x73_recomputed']
    assert not d['Gate7_closed'] and not d['FULL_BHSM_COMPLETE']


def test_provenance_hashes_and_frozen_derivative_unchanged():
    d=packet()
    for name,h in d['frozen_artifact_SHA256'].items():assert audit.sha(ROOT/name)==h
    for name,h in d['source_SHA256'].items():assert audit.sha(ROOT/name)==h
    for name,info in d['function_provenance'].items():assert audit.sha(ROOT/name)==info['SHA256']
    assert audit.calculate()==d
    receipt=json.loads((OUT/'reproduction.json').read_bytes())
    assert receipt['byte_identical']
    assert audit.sha(OUT/'report.json')==receipt['SHA256']
