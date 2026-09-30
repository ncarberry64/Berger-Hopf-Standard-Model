"""Light numerical benchmark on the retained current N12 point."""
import os
for name in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "JAX_NUM_THREADS", "TF_NUM_INTRAOP_THREADS", "TF_NUM_INTEROP_THREADS"):
    os.environ[name] = "1"
os.environ.setdefault("XLA_FLAGS", "--xla_cpu_multi_thread_eigen=false intra_op_parallelism_threads=1")

import json
from pathlib import Path
import sys
import time
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts")]
from bhsm.interface.aether_hybrid_c2_graph_jacobian import graph_jacobian_action
from bhsm.interface.aether_forward_c2_descriptor_cover import metric_data
from recon_n12_c2_stop_physical_tangent_transfer import _constraint_geometry

center = ROOT / "artifacts/flagship_integration/BHSM_N12_C2_STOP_HIGH_ORDER_QUARTER_STEP_RETAINED_RECONNAISSANCE.npz"
with np.load(center) as z:
    states, descriptors, rates, weights, reference = (np.asarray(z[k], dtype=float) for k in ("centers", "signed_descriptors", "action_rates", "state_weights", "branch_reference"))
qweights = metric_data()[0]
rows = []
for index in (0, 1):
    started = time.perf_counter()
    flow_q = rates[index, :37]
    numerator_q = descriptors[index] * qweights * states[index, 37:74]
    norm = float(numerator_q @ flow_q / (flow_q @ flow_q))
    if not np.isfinite(norm) or norm <= 0:
        raise ValueError("stored actual action rate cannot recover positive cancelled-field norm")
    cancelled = rates[index] * norm
    result = graph_jacobian_action(states[index], weights, reference, float(descriptors[index]), cancelled_field_action=cancelled)
    jacobian_seconds = time.perf_counter() - started
    geom = _constraint_geometry((index, states[index], weights))
    Q = geom[2]
    reduced = Q.T @ result["graph_Jacobian_action"] @ Q
    symmetric_eigenvalues = np.linalg.eigvalsh((reduced + reduced.T) / 2)
    row = dict(node=index, selected_branch=int(result["selected_branch"]), tangent_dimension=int(Q.shape[1]), jacobian_seconds=jacobian_seconds, total_seconds=time.perf_counter()-started, reduced_jacobian_operator_norm=float(np.linalg.norm(reduced, 2)), local_action_arc_rate_symmetric_min=float(symmetric_eigenvalues[0]), local_action_arc_rate_symmetric_max=float(symmetric_eigenvalues[-1]), action_constraint_value_norm=float(np.linalg.norm(geom[3])), actual_cancelled_field_norm=norm, normalization_q_replay_relative=float(np.linalg.norm(norm*flow_q-numerator_q)/np.linalg.norm(numerator_q)), interpretation="INSTANTANEOUS_CONSTRAINED_FINITE_RATE_NOT_EQUILIBRIUM_STABILITY")
    rows.append(row)
    print(json.dumps(row), flush=True)
    Path(__file__).with_name("report.json").write_text(json.dumps(dict(center=str(center), rows=rows), indent=2)+"\n", encoding="utf-8")
    if row["total_seconds"] > 60:
        break
