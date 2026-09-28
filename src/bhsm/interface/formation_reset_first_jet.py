"""First-order reset incidence, requiring the actual upstream stationarity jet."""
from flint import arb_mat


def reset_hit_jet(fixed_arc_jet,arc_rate,event_covector):
    """Differentiate a transverse event hit, including its moving arc endpoint.

    Inputs must be current transported quantities. This does not produce a
    trajectory or authorize historical jets at a different base point.
    """
    n=fixed_arc_jet.nrows()
    if (arc_rate.nrows(),arc_rate.ncols())!=(n,1) or (event_covector.nrows(),event_covector.ncols())!=(1,n):
        raise ValueError('matching flow and event covector required')
    speed=(event_covector*arc_rate)[0,0]
    if speed.contains(0):raise ValueError('transverse event speed must exclude zero')
    arc_shift=-(event_covector*fixed_arc_jet)/speed
    return dict(hit_jet=fixed_arc_jet+arc_rate*arc_shift,arc_shift=arc_shift)


def incoming_reset_jet(reset_jacobian,outgoing_hit_jet,upstream_stationarity_jacobian):
    """Solve 32 incoming reset + 66 upstream equations in weighted action coordinates.

    Reset rows retain the existing 58-row terminal-reset order: outgoing
    constraints 0:25, outgoing selected descriptor 25, configuration matching
    26:30, incoming constraints 30:55, momenta 55:57, incoming descriptor 57.
    The 66 upstream rows must be the differentiated, internally reduced
    formation/contact stationarity equations, not a zero-kernel convention.
    The first 26 reset equations are replayed separately in the return value.
    """
    if reset_jacobian is None or (reset_jacobian.nrows(),reset_jacobian.ncols())!=(58,196):
        raise ValueError('current complete 58x196 terminal reset Jacobian required')
    if (outgoing_hit_jet.nrows(),outgoing_hit_jet.ncols())!=(98,73):
        raise ValueError('current outgoing event-hit 98x73 jet required')
    if upstream_stationarity_jacobian is None or (upstream_stationarity_jacobian.nrows(),upstream_stationarity_jacobian.ncols())!=(66,196):
        raise ValueError('current action-owned reduced upstream 66x196 stationarity derivative required')
    rows=[[reset_jacobian[i,j] for j in range(196)] for i in range(26,58)]
    rows += [[upstream_stationarity_jacobian[i,j] for j in range(196)] for i in range(66)]
    C=arb_mat([[r[j] for j in range(98)] for r in rows])
    E=arb_mat([[r[j] for j in range(98,196)] for r in rows])
    incoming=E.solve(-C*outgoing_hit_jet)
    joint=arb_mat(196,73,outgoing_hit_jet.entries()+incoming.entries())
    return dict(incoming_hit_jet=incoming,
                reset_replay=reset_jacobian*joint,
                upstream_replay=upstream_stationarity_jacobian*joint)
