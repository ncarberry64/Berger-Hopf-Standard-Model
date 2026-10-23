import numpy as np
from bhsm.interface.muon_material_rate_canonical_reduction import fixed_position_material_rate_chart


def test_material_rate_map_and_literal_canonical_dual_preserve_nonreal_pairing():
    rng=np.random.default_rng(3712125);raw=np.zeros(100,complex)
    raw[:37]=.002*(rng.normal(size=37)+1j*rng.normal(size=37));raw[98]=.003-.002j
    raw[37:74]=rng.normal(size=37)+1j*rng.normal(size=37);raw[99]=.4-.1j
    a=fixed_position_material_rate_chart(raw);T=a['velocity_algebraic_lift'];Ti=a['velocity_algebraic_inverse']
    old=rng.normal(size=146)+1j*rng.normal(size=146);old[:37]=raw[37:74];old[37]=raw[99]
    new=Ti@old
    expected=(raw[99]-raw[98]*(a['wall_log_rate_covector']@raw[37:74]))/a['Cstar']
    np.testing.assert_allclose(new[37],expected,atol=6e-17)
    np.testing.assert_allclose(T@new,old,atol=3e-16)
    p=rng.normal(size=146)+1j*rng.normal(size=146);d=rng.normal(size=146)+1j*rng.normal(size=146)
    np.testing.assert_allclose((T.T@p)@d,p@(T@d),rtol=2e-15,atol=3e-14)
    assert len(a['field_indices'])==121 and len(a['nonlinear_geometry_indices'])==25
    assert not a['canonical_x_force_transform_without_chart_contacts']
