"""Copy exact already-evaluated states; no optimizer/optical arithmetic is added."""
from contextlib import contextmanager
from copy import deepcopy
import json
import math

TRACE_SCHEMA='bhsm.photometry_mc.exact_evaluation_state.v1'


def _canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)


@contextmanager
def capture_evaluation_states():
    """Only for the isolated single-job child; never patch another process.

The source search/decoder is called exactly once as before. Copy the full vector
that source _search already passes to decode, then attach metadata to its report.
Parameters, returned x, state arrays, seeds, optimizer and caches are untouched.
"""
    from . import photometry_inference as kernel
    original=kernel._search
    serial=0
    def search(model,*args,**kwargs):
        nonlocal serial
        serial+=1;call_index=serial
        decoded=[];decode=model.base.decode
        def traced(full):
            parameters=decode(full)
            trace={'schema':TRACE_SCHEMA,'search_call_index':call_index,'full_transformed_state_hex':[float(v).hex() for v in full],
                'parameter_names':list(model.base.parameter_names),'time_center_hex':float(model.base.center).hex(),
                'time_scale_hex':float(model.base.scale).hex(),'numeric_origin_jd_hex':float(model.base.data.common_origin_jd).hex(),
                'noise_scale_hex':float(model.base.noise_scale).hex(),'equal_instrument_weight':model.base.equal_weight,
                'allow_negative_blend':model.base.allow_negative_blend,'paired_physical_parameters':deepcopy(parameters)}
            decoded.append((parameters,trace));return parameters
        model.base.decode=traced
        try:result,state=original(model,*args,**kwargs)
        finally:model.base.decode=decode
        for parameters,trace in decoded:
            matches=[row for row in result['starts'] if row.get('parameters') is parameters]
            if len(matches)!=1:raise ValueError('Exact-state trace cannot be associated to a unique reported trial')
            trace['trial_index']=matches[0]['start']
            matches[0]['saved_numerical_state']=trace
            if result.get('parameters') is parameters:result['saved_numerical_state']=trace
        for row in result['starts']:
            if row.get('objective_chi_square') is not None and 'saved_numerical_state' not in row:
                raise ValueError('Reported finite state lacks its exact source evaluation vector')
        return result,state
    kernel._search=search
    try:yield
    finally:kernel._search=original


def evaluate_saved_state(data,trace,physical):
    """Re-evaluate an exact vector directly; no encode, clipping or profiling."""
    import numpy as np
    from .photometry import _Model
    if not isinstance(trace,dict) or trace.get('schema')!=TRACE_SCHEMA:raise ValueError('Missing exact transformed state; numerical replay refused')
    if trace.get('equal_instrument_weight') is not False or trace.get('allow_negative_blend') is not False or trace.get('noise_scale_hex')!=float(1.).hex():
        raise ValueError('Saved likelihood/run conventions differ from the fixed method')
    model=_Model(data,1.,False,False)
    expected={'parameter_names':model.parameter_names,'time_center_hex':model.center.hex(),
        'time_scale_hex':model.scale.hex(),'numeric_origin_jd_hex':data.common_origin_jd.hex()}
    if any(_canonical(trace.get(k))!=_canonical(v) for k,v in expected.items()):raise ValueError('Saved transformed basis/numeric-origin convention differs')
    cells=trace.get('full_transformed_state_hex')
    if not isinstance(cells,list) or len(cells)!=len(model.lower) or any(not isinstance(v,str) for v in cells):raise ValueError('Missing exact state vector coordinates')
    try:x=np.asarray([float.fromhex(v) for v in cells])
    except (ValueError,OverflowError) as exc:raise ValueError('Invalid exact state representation') from exc
    if np.any(~np.isfinite(x)):raise ValueError('Nonfinite exact state')
    if np.any(x<model.lower) or np.any(x>model.upper):raise ValueError('Saved exact state is outside the unchanged numerical domain')
    decoded=model.decode(x)
    if _canonical(decoded)!=_canonical(trace.get('paired_physical_parameters')) or _canonical(decoded)!=_canonical(physical):
        raise ValueError('Saved physical/transformed state pair changed')
    residual=model.evaluate(x)
    value=float(residual@residual)
    if not math.isfinite(value):raise ValueError('Nonfinite numerical replay objective')
    return value
