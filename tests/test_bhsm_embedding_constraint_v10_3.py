import numpy as np

from bhsm.interface.envelopment import embedding_constraint_v10_3 as embedding


def test_induced_metric_and_reparametrized_frame_agree_covariantly():
    metric = np.diag([-1.0, 1.0, 1.0, 1.0])
    frame = np.eye(4)[:, :2]
    jacobian = np.array([[1.0, 1.0], [0.0, 1.0]])
    h = embedding.induced_metric(metric, frame)
    transformed = embedding.induced_metric(metric, frame @ jacobian)
    assert np.allclose(transformed, jacobian.T @ h @ jacobian)


def test_codimension_prevents_silent_unique_M4_normal():
    rows = embedding.codimension_audit()
    assert rows[0]["normal_rank"] == 4
    assert rows[0]["unique_normal_scalar"] is False
    assert rows[1]["normal_rank"] == 1


def test_embedding_payload_preserves_fixed_support_result_but_no_shape_equation():
    payload = embedding.embedding_payload()
    assert payload["validation_passed"] is True
    assert payload["embedding"]["fixed_support_prior_result"] == "BHSM_DYNAMICAL_B1_EMBEDDING_NOT_REQUIRED"
    assert payload["embedding"]["shape_equation_current"] is None
