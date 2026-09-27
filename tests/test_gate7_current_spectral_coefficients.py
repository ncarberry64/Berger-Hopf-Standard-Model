import json
from pathlib import Path
import sys
from flint import arb, arb_mat, ctx

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'src')]
from certify_n12_gate7_coupled_center_neighborhood import load
from checkpoint_n12_gate7_66d_tangent_binding import digest

OUT=ROOT/'artifacts/flagship_integration/gate7_current_spectral_20260927'


def packet():
    ctx.prec=512
    return json.loads((OUT/'report.json').read_bytes()),load(OUT/'arrays.npz')


def test_current_radius_jet_matches_owned_native_trace():
    d,a=packet()
    assert all(v.contains(0) for v in a['native_trace_log_radius_replay'].flat)
    assert d['trace_binding_replay']['approximate_upper']<8.915423761304125e-7
    assert a['log_R4_first_73'].shape==(1,73)


def test_stored_core_base_is_certifiably_disjoint():
    d,a=packet()
    assert arb(d['current_minus_old_global_upper']['lower'])>arb('1.33935349e-7')
    assert a['log_R4_value'][0,0]>arb(d['old_family_log_R4']['upper'])
    assert not d['old_family_contains_current_point']
    assert not d['physical_owner_absence_claimed']


def test_zeta_density_preserves_moving_lapse():
    _,a=packet()
    N=a['lapse_value'][0,0];D=a['zeta_proper_density_value'][0,0]
    lhs=arb_mat(a['zeta_coordinate_density_first_73'].tolist())
    rhs=arb_mat(a['zeta_proper_density_first_73'].tolist())*N+arb_mat(a['lapse_first_73'].tolist())*D
    assert all(v.contains(0) for v in (lhs-rhs).entries())
    assert a['zeta_proper_density_value'][0,0]<0


def test_all_angular_sectors_have_exact_retained_grading():
    d,_=packet();g=d['grading']
    assert (g['Weyl']['species'],g['Weyl']['supertrace_sign'])==(48,-1)
    assert (g['gauge_transverse']['species'],g['gauge_transverse']['supertrace_sign'])==(12,1)
    assert (g['Hubbard_Strattonovich']['species'],g['Hubbard_Strattonovich']['supertrace_sign'])==(4,1)
    assert g['gauge_longitudinal_ghost']['net_supertrace_sign']==0


def test_no_second_jet_or_false_full_history_promotion():
    d,_=packet()
    assert not d['operator_law']['second_operator_jet_computed']
    assert not d['complete_joint_operator_instantiated']
    assert d['complete_seven_response'] is None and d['seven_adjoint_residuals'] is None
    for k in ('local_native_derivative_recomputed','historical_test_covectors_run','expensive_1222_rows_recomputed','heat_seed_set_to_zero','Gate7_closed','FULL_BHSM_COMPLETE'):
        assert not d[k]


def test_source_hashes_and_repeat():
    d,_=packet()
    assert digest(OUT/'arrays.npz')==d['arrays_SHA256']
    for p,h in d['source_SHA256'].items():assert digest(ROOT/p)==h
    receipt=json.loads((OUT/'reproduction.json').read_bytes())
    for name,item in receipt['files'].items():
        assert item['byte_identical'] and digest(OUT/name)==item['SHA256']
