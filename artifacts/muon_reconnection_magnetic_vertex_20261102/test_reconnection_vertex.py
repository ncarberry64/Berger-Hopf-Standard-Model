"""Focused independent sign, contact and scope checks for the v64 milestone."""
import importlib.util
import json
from pathlib import Path
import pytest
import sympy as s

P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('v64',P/'derive_reconnection_vertex.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


@pytest.fixture(scope='module')
def result():return m.build_result()


def test_original_cap_normalization_and_energy(result):
    g=result['groups']['central_action']
    assert all(s.sympify(v)==0 for v in g['residuals'].values())
    assert 'kappa' in g['material_F_u_i']
    assert g['coefficient_work_identically_zero'] is False


def test_photon_projection_requires_higgs_direction_motion(result):
    g=result['groups']['projected_Bianchi']
    assert all(s.sympify(v)==0 for v in g['residuals'].values())
    assert g['omitted_Dq_identically_zero'] is False


def test_all_ordered_first_order_insertions_and_domain_contact(result):
    g=result['groups']['first_order_insertion']
    assert all(s.sympify(v)==0 for v in g['residuals'].values())
    assert g['domain_contact']=='-B*GD*C'
    for term in ('BY*G*C','B*G*CY','B*G*DY*G*C','B*GD*C'):assert term in g['insertion']


def test_owned_centrality_is_not_an_abelian_substitution(result):
    assert s.sympify(result['groups']['owned_curvature']['residuals']['owned_hypercharge_bracket']).is_zero is True


def test_scope_and_original_guard(result):
    assert result['physical_guard']==2e-10
    assert result['admitted_temporal_strength']==2**-9
    for name in ('complete_native_a_mu','complete_g_mu','total_physical_uncertainty'):assert result[name] is None
    assert result['physical_event_reconnection_evaluated'] is False
    assert result['physical_common_background_realized'] is False


def test_portable_source_ledger():
    from hashlib import sha256
    ledger=json.loads((P/'source_ledger.json').read_text(encoding='utf-8'))
    assert ledger['base_commit']=='4a650a61a6e0e4cd3674650c399b435c106d66c3'
    for item in ledger['sources']:
        assert len(item['working_file_sha256'])==64
        for excerpt in item['excerpts']:
            assert sha256(excerpt['text'].encode()).hexdigest()==excerpt['sha256']
    assert ledger['v63_preserved_sha256']=='d7f77c03a3e3544325b16ddd104acde83928c76781e2f96f2f86eea54328bc28'
