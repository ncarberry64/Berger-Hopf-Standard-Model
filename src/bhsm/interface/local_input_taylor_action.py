"""Evaluate local action jets in 13 inputs, then restore the common input map.

Only the local nonlinear remainder uses the induced map norm. All constant
and state-linear input coefficients are transported exactly in Arb before
bulk and global inertia are combined. The original boundary is evaluated
without compression. No state domain is reduced.
"""
from contextlib import contextmanager
import hashlib
from pathlib import Path
import numpy as np
from flint import arb,arb_mat
from bhsm.interface.input_linear_taylor import InputLinearTaylor,vector_norm,matrix_norm_bound
from bhsm.interface.input_linear_taylor import input_linear_taylor_action as dense_action
from bhsm.interface.shared_parameter_residual import linear_support
from bhsm.interface.shared_action_taylor import Taylor
import bhsm.interface.input_linear_taylor as dense_arithmetic

# The compressed evaluator is source-bound to the independently exercised
# common input arithmetic; its own fingerprint alone must not hide a change.
DENSE_ARITHMETIC_SHA256='6F3005208CDE197D8214FAE62A809B114181F2801071BB2EA89FB659934E3BF9'
DENSE_ARITHMETIC_PATH=Path(dense_arithmetic.__file__)


def map_norm(matrix,groups):
    total=arb(0)
    for start,stop,kind in groups:
        if kind=='euclidean':
            total+=matrix_norm_bound(arb_mat(matrix.nrows(),stop-start,
                [matrix[i,j] for i in range(matrix.nrows()) for j in range(start,stop)]))
        else:
            total+=sum((vector_norm([matrix[i,j] for i in range(matrix.nrows())])
                        for j in range(start,stop)),arb(0))
    return total.upper()


@contextmanager
def input_linear_taylor_action(module):
    if hashlib.sha256(DENSE_ARITHMETIC_PATH.read_bytes()).hexdigest().upper()!=DENSE_ARITHMETIC_SHA256:
        raise ValueError('reviewed common input arithmetic fingerprint required')
    with dense_action(module):
        original=module._contracted_action
        def contracted(state_values,raw_legs,dense_maps):
            selected=[i for i,leg in enumerate(raw_legs)
                      if any(isinstance(v,InputLinearTaylor) for v in leg)]
            if not selected:
                return original(state_values,raw_legs,dense_maps)
            if len(selected)!=1:
                raise ValueError('exactly one arbitrary input leg required')
            axis=selected[0]
            template=next(v for v in raw_legs[axis] if isinstance(v,InputLinearTaylor))
            dimension=template.c.ncols()
            if dimension<=module.LOCAL:
                return original(state_values,raw_legs,dense_maps)
            for value in raw_legs[axis]:
                if isinstance(value,InputLinearTaylor):
                    if (value.domain is not template.domain or value.input_groups!=template.input_groups
                            or not value.linear_bound().is_zero() or not value.r.is_zero()):
                        raise ValueError('state-constant common input leg required')
                elif isinstance(value,Taylor):
                    if not (value.c.is_zero() and value.r.is_zero() and value.linear_bound().is_zero()):
                        raise ValueError('homogeneous input leg required')
                elif not arb(value).is_zero():
                    raise ValueError('homogeneous input leg required')
            state=[module._a(v) for v in state_values]
            input_matrix=arb_mat(module.STATE,dimension)
            for i,value in enumerate(raw_legs[axis]):
                if isinstance(value,InputLinearTaylor):
                    for j in range(dimension): input_matrix[i,j]=value.c[0,j]
            count=len(raw_legs)
            bulk=module.Mixed.constant(0,count);inertia=module.Mixed.constant(0,count)
            for node in range(module.POINTS):
                local=[]
                for leg_index,leg in enumerate(raw_legs):
                    if leg_index==axis:
                        local.append(None)
                        continue
                    rows=[]
                    for mapping in dense_maps[node]:
                        total=arb(0)
                        for column in np.flatnonzero(mapping):
                            total+=arb(float(mapping[column]))*leg[column]
                        rows.append(total)
                    local.append(np.array(rows,dtype=object))
                mapping=arb_mat(module.LOCAL,module.STATE,[arb(float(v)) for v in dense_maps[node].flat])
                transform=mapping*input_matrix
                # Scale each local axis by its own common-input support.
                # An isotropic local ball loses the strong anisotropy of
                # the physical input map and unnecessarily widens the tail.
                widths=[linear_support([transform[i,j] for j in range(dimension)],template.input_groups)
                        for i in range(module.LOCAL)]
                pullback=arb_mat(module.LOCAL,dimension)
                for i,width in enumerate(widths):
                    if not width.is_zero():
                        for j in range(dimension): pullback[i,j]=transform[i,j]/width
                scale=max(linear_support([pullback[i,j] for j in range(dimension)],template.input_groups)
                          for i in range(module.LOCAL))
                units=[]
                for i in range(module.LOCAL):
                    value=InputLinearTaylor(template.domain,
                        arb_mat(1,module.LOCAL,[widths[i] if i==j else arb(0) for j in range(module.LOCAL)]),
                        arb_mat(template.domain.dimension,module.LOCAL),input_groups=[(0,module.LOCAL,'box')])
                    value._linear=arb(0)
                    units.append(value)
                local[axis]=np.array(units,dtype=object)
                term=module._integrand(state,node,count,local)
                def restore(jet):
                    values=[]
                    for value in jet.d:
                        if isinstance(value,InputLinearTaylor):
                            value=InputLinearTaylor(template.domain,value.c*pullback,value.a*pullback,
                                                   value.r*scale,template.input_groups)
                        values.append(value)
                    return module.Mixed(tuple(values))
                bulk+=restore(term.bulk);inertia+=restore(term.inertia)
            action=bulk-(0.25/(2.0*module.HOPF_ORBIT_VOLUME**2))/inertia
            _,boundary=module._boundary(state,count,raw_legs)
            return (action+boundary).d[-1]
        module._contracted_action=contracted
        try:
            yield
        finally:
            module._contracted_action=original
