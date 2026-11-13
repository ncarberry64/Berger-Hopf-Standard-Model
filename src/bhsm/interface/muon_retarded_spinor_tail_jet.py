"""Literal action-tail elimination before unsquared exterior pole projection.

The caller supplies the child block on the AE4 retarded domain of the SAME
matched history.  This module neither chooses that domain nor extends a
finite trace endpoint into a physical exterior.  In particular H_cp remains
an independently produced analytic action block, not H_pc.conj().T.
"""
from __future__ import annotations

import numpy as np

_KEYS = ("parent", "parent_child", "child_parent", "retarded_child",
         "parent_source", "child_source", "parent_target", "child_target",
         "direct_current")


def _maps(data, reference=None):
    if set(data) != set(_KEYS):
        raise ValueError("every independent action, source and literal target tail map is required")
    a = {name: np.asarray(data[name], complex) for name in _KEYS}
    if any(value.ndim != 2 or not np.isfinite(value).all() for value in a.values()):
        raise ValueError("finite original matrix coefficients required")
    p, pc, cp, c, jp, jc, lp, lc, direct = (a[k] for k in _KEYS)
    n, m = p.shape[0], c.shape[0]
    ns, nl = jp.shape[1], lp.shape[0]
    shapes = ((n, n), (n, m), (m, n), (m, m), (n, ns), (m, ns),
              (nl, n), (nl, m), (nl, ns))
    if not n or not m or any(a[k].shape != shape for k, shape in zip(_KEYS, shapes)):
        raise ValueError("complete parent/child trace rows and independent source/target columns required")
    if reference is not None and any(a[k].shape != reference[k].shape for k in _KEYS):
        raise ValueError("each jet must keep every original action row and column")
    return a


def _solve_two_jet(operator, rhs):
    """Derivative arrays are value, E, B, EB; no Taylor factors occur."""
    a, ae, ab, aeb = operator
    j, je, jb, jeb = rhs
    x = np.linalg.solve(a, j)
    xe = np.linalg.solve(a, je - ae @ x)
    xb = np.linalg.solve(a, jb - ab @ x)
    xeb = np.linalg.solve(a, jeb - aeb @ x - ae @ xb - ab @ xe)
    return x, xe, xb, xeb


def retarded_spinor_tail_two_jet(base, energy, magnetic, energy_magnetic):
    """Return Gamma, its forced source and the full Poisson/dual jets.

    The same tail action is
        H_pp x + H_pc y = j_p,
        H_cp x + H_cc^R y = j_c.
    With X=(H_cc^R)^-1 H_cp and r=(H_cc^R)^-1 j_c, its exact
    relation is y=-X x+r.  Consequently Gamma=H_pp-H_pc X and
    f=j_p-H_pc r.  A supplied L_p x+L_c y+c becomes
    (L_p-L_c X)x+c+L_c r. These maps use the same eight-map Gamma/f
    product rules before any pole, current or charge projection. A tail
    Poisson map may be rectangular; it is not a square temporal trace.

    Energy is the UNSQUARED external energy.  Every E/B/EB coefficient is
    supplied explicitly; no absent boundary or quantum contact is zeroed.
    The returned left Poisson lift is an analytic row lift from an
    independent transpose solve.  It does not conjugate source tangents.
    """
    a = _maps(base)
    jets = (a, _maps(energy, a), _maps(magnetic, a), _maps(energy_magnetic, a))
    column = lambda key: tuple(q[key] for q in jets)
    x = _solve_two_jet(column("retarded_child"), column("child_parent"))
    r = _solve_two_jet(column("retarded_child"), column("child_source"))
    zt = _solve_two_jet(tuple(q.T for q in column("retarded_child")),
                        tuple(q.T for q in column("parent_child")))
    z = tuple(q.T for q in zt)
    maps = []
    n, m = a["parent"].shape[0], a["retarded_child"].shape[0]
    right, left, source = [], [], []
    for order, q in enumerate(jets):
        maps.append(dict(trace=-x[order], source_return=r[order],
            initial_boundary=q["parent"], final_boundary=q["parent_child"],
            boundary_source=q["parent_source"], initial_target=q["parent_target"],
            final_target=q["child_target"], direct_current=q["direct_current"]))
        identity = np.eye(n, dtype=complex) if order == 0 else np.zeros((n, n), complex)
        right.append(np.vstack((identity, -x[order])))
        left.append(np.hstack((identity, -z[order])))
        source.append(np.vstack((np.zeros_like(q["parent_source"]), r[order])))
    # The chronological eight-map composer deliberately requires a square
    # temporal trace. Keep that contract: apply the identical product rule
    # to this rectangular Poisson relation without adding/dropping fibers.
    products = (('boundary_matrix','initial_boundary','final_boundary','trace',1),
                ('forced_boundary_source','boundary_source','final_boundary','source_return',-1),
                ('effective_literal_left','initial_target','final_target','trace',1),
                ('direct_source_return_current','direct_current','final_target','source_return',1))
    application = {}
    for name, free, lhs, rhs, sign in products:
        b, e, s, es = maps
        application[name] = b[free]+sign*b[lhs]@b[rhs]
        application[name+'_first'] = np.array([
            q[free]+sign*(q[lhs]@b[rhs]+b[lhs]@q[rhs]) for q in (e, s)])
        application[name+'_mixed'] = es[free]+sign*(es[lhs]@b[rhs]
            + e[lhs]@s[rhs]+s[lhs]@e[rhs]+b[lhs]@es[rhs])
    blocks = [np.block([[q["parent"], q["parent_child"]],
                       [q["child_parent"], q["retarded_child"]]]) for q in jets]
    # Full original child rows for value and BOTH source directions.
    child_rows = [jets[0]["retarded_child"] @ x[0] - jets[0]["child_parent"]]
    source_rows = [jets[0]["retarded_child"] @ r[0] - jets[0]["child_source"]]
    for j in (1, 2):
        child_rows.append(jets[0]["retarded_child"] @ x[j]
            + jets[j]["retarded_child"] @ x[0] - jets[j]["child_parent"])
        source_rows.append(jets[0]["retarded_child"] @ r[j]
            + jets[j]["retarded_child"] @ r[0] - jets[j]["child_source"])
    child_rows.append(jets[0]["retarded_child"] @ x[3]
        + jets[3]["retarded_child"] @ x[0] + jets[1]["retarded_child"] @ x[2]
        + jets[2]["retarded_child"] @ x[1] - jets[3]["child_parent"])
    source_rows.append(jets[0]["retarded_child"] @ r[3]
        + jets[3]["retarded_child"] @ r[0] + jets[1]["retarded_child"] @ r[2]
        + jets[2]["retarded_child"] @ r[1] - jets[3]["child_source"])
    labels = ("", "_energy", "_magnetic", "_energy_magnetic")
    result = dict(application)
    for i, suffix in enumerate(labels):
        result["right_tail_poisson" + suffix] = -x[i]
        result["literal_left_tail_poisson" + suffix] = -z[i]
        result["tail_forced_source_return" + suffix] = r[i]
        result["full_right_trace_lift" + suffix] = right[i]
        result["full_literal_left_trace_lift" + suffix] = left[i]
        result["full_forced_source_lift" + suffix] = source[i]
        result["full_action_block" + suffix] = blocks[i]
        result["original_child_Poisson_rows" + suffix] = child_rows[i]
        result["original_child_source_rows" + suffix] = source_rows[i]
    gamma = application["boundary_matrix"]
    result["full_right_Poisson_substitution_rows"] = blocks[0] @ right[0] - np.vstack((gamma, np.zeros((m, n))))
    result["full_left_Poisson_substitution_rows"] = left[0] @ blocks[0] - np.hstack((gamma, np.zeros((n, m))))
    result.update(retarded_tail_domain_is_caller_supplied=True,
        future_support_or_first_hit_not_selected_by_matrix_elimination=True,
        independent_Hcp_not_replaced_by_Hpc_Hilbert_adjoint=True,
        external_variable="unsquared energy E on the same retarded action domain",
        classical_child_shooting_fiber_not_identified_with_spinor_trace=True,
        physical_exterior_pole_residue_charge_or_Pauli_selected=False)
    return result


def lift_retarded_tail_pole(application, right, left):
    """Lift action-produced null frames and audit the full energy/B residue.

    Differentiated lift terms vanish only by the explicitly returned null
    rows.  This function therefore reports both full and reduced kinetic
    and magnetic matrices and their difference; it does not assume a pole
    or select spin-doublet frames.
    """
    a = application
    R, L = np.asarray(right, complex), np.asarray(left, complex)
    n = a["boundary_matrix"].shape[0]
    if (R.ndim != 2 or L.ndim != 2 or R.shape[0] != n or L.shape[1] != n
            or R.shape[1] != L.shape[0] or not R.shape[1]
            or not np.isfinite(R).all() or not np.isfinite(L).all()):
        raise ValueError("independently produced same-action right/left null traces required")
    right_full = a["full_right_trace_lift"] @ R
    left_full = L @ a["full_literal_left_trace_lift"]
    full_z = left_full @ a["full_action_block_energy"] @ right_full
    full_b = left_full @ a["full_action_block_magnetic"] @ right_full
    reduced_z = L @ a["boundary_matrix_first"][0] @ R
    reduced_b = L @ a["boundary_matrix_first"][1] @ R
    return dict(full_right_pole_trace=right_full, full_literal_left_pole_trace=left_full,
        full_original_right_pole_rows=a["full_action_block"] @ right_full,
        full_original_left_pole_rows=left_full @ a["full_action_block"],
        full_kinetic_matrix=full_z, reduced_kinetic_matrix=reduced_z,
        kinetic_Schur_identity=full_z-reduced_z,
        full_magnetic_matrix=full_b, reduced_magnetic_matrix=reduced_b,
        magnetic_Schur_identity=full_b-reduced_b,
        physical_null_trace_or_domain_admission_not_inferred=True)
