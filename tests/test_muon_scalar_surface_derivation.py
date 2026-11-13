"""Original-functional and coarea checks of the new coefficient applications."""
from decimal import Decimal, localcontext
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path

import pytest


ROOT=Path(__file__).resolve().parents[1]


def run_audit(name, output):
    spec=spec_from_file_location(name,ROOT/'audits'/f'{name}.py')
    module=module_from_spec(spec)
    spec.loader.exec_module(module)
    module.evaluate(ROOT,output)
    return json.loads((output/'result.json').read_bytes())


@pytest.fixture(scope='module')
def applications(tmp_path_factory):
    folder=tmp_path_factory.mktemp('muon_coefficient_derivation')
    return {
        'quartic':run_audit('bhsm_current_c2_e1_quartic_20261015',folder/'quartic'),
        'coarea':run_audit('bhsm_c2_graded_surface_volume_component_20261015',folder/'coarea'),
        'inertia':run_audit('bhsm_original_area_inertia_contact_20261015',folder/'inertia'),
    }


def test_noncommuting_quartic_against_fresh_literal_e1(applications):
    with localcontext() as ctx:
        ctx.prec=80
        for channel in applications['quartic']['channels'].values():
            result=channel['precision105']
            value=Decimal(result['reduced_HS_dimensionless_u_derivatives'][3])
            parts=[Decimal(x) for x in result['fourth_parts_dimensionless'].values()]
            assert abs(sum(parts)-value)<Decimal('1e-60')
            assert value<0
            assert all(abs(x)>abs(value) for x in parts)
            coarse,fine=result['literal_E1_fd_checks']
            assert Decimal(fine['relative_error'])<Decimal('2e-10')
            ratio=Decimal(coarse['absolute_error'])/Decimal(fine['absolute_error'])
            assert Decimal(32)<ratio<Decimal(128)
            assert Decimal(result['outer_trace_tail_fourth_Cauchy_bound'])<Decimal('1e-30')
            assert Decimal(channel['previous_dense_binary64_HS_curvature_relative_discrepancy'])>Decimal('2e-10')


def test_coarea_action_jets_keep_the_fibre_contacts(applications):
    for row in applications['coarea']['records']:
        assert abs(row['full_density_value_identity_residual'])<2e-10
        assert row['full_density_gradient_identity_max_residual']<2e-10
        assert row['full_density_Hessian_identity_max_residual']<2e-10
        assert row['omitted_fibre_first_contact_norm_if_gamma7_held']>1e-3


def test_membrane_inertia_against_literal_mp_rate_derivative(applications):
    for row in applications['inertia']['records']:
        inertia=row['coordinate_normal_rate_inertia_per_gamma']
        assert inertia>0
        assert row['MP80_literal_vs_saved_Hessian_absolute']<1e-12
        assert row['normal_rate_geometry_mixed_row_norm']>inertia
        assert abs(row['proper_clock_normal_rate_inertia_per_gamma']
                   -row['induced_proper_clock']*inertia)<1e-12
