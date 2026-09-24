"""Local radial extensions of a frozen moving chart to a Hermite image.

The history and radial parameters are different. The predictor and inverse
share the history parameter. Endpoint state and rate parameters are reused.
"""
from flint import arb
from bhsm.interface.shared_action_taylor import TaylorDomain
from bhsm.interface.history_eigenbranch_variation import hermite_history


def tube_operands(left, right, rates, step, chart, tau_bounds, *, variation):
    """Enclose D3S[R(s)^T W^-1 dual, eta, history(tau)-line(s)]."""
    a, b, weights, half = chart
    low, high = map(arb, tau_bounds)
    if not (0 <= low < high <= 1 and half/2 <= low and high <= (half+1)/2):
        raise ValueError('cell must lie in its declared half interval')
    dimension = 471 if variation else 410
    groups = [(0, 1, 'interval'), (1, 2, 'interval'),
              (2, 3, 'interval'), (3, 77, 'euclidean'),
              (77, 78, 'interval'), (78, 152, 'euclidean'),
              (152, 348, 'box'), (348, 410, 'euclidean')]
    if variation:
        groups.append((410, 471, 'box'))
    d = TaylorDomain(groups, dimension)
    def variable(index, center=0, radius=1):
        co = [arb(0)]*dimension
        co[index] = arb(radius)
        return d.affine(center, co)
    tau = variable(0, (low+high)/2, (high-low)/2)
    sigma = variable(1, arb(1)/2, arb(1)/2)
    s = 2*tau-half
    states, fields = [], []
    for side, ep in enumerate((left, right)):
        state, field = [], []
        for i in range(98):
            co = [arb(0)]*dimension
            co[2+75*side:77+75*side] = ep['scaled'][i]
            state.append(d.affine(ep['x'][i], co))
            field.append(variable(152+98*side+i, rates[side][i].mid(), rates[side][i].rad()))
        states.append(state)
        fields.append(field)
    curve = hermite_history(*states, *fields, step, tau)
    line = [x+s*(y-x) for x, y in zip(a['x'], b['x'], strict=True)]
    displacement = [x-y for x, y in zip(curve, line, strict=True)]
    state = [x+sigma*dx for x, dx in zip(line, displacement, strict=True)]
    dual = [variable(348+i) for i in range(62)]
    lhs = [d.affine(0)]*37+[
        sum((dual[i]*(a['R'][i,j]+s*(b['R'][i,j]-a['R'][i,j]))/weights[i]
             for i in range(62)), d.affine(0)) for j in range(61)]
    eta = [d.affine(0)]*37+[
        weights[j]*variable(410+j) if variation else a['y'][j]+s*(b['y'][j]-a['y'][j])
        for j in range(61)]
    return dict(domain=d, state=state, curve=curve, displacement=displacement,
                legs=[lhs, eta, displacement], tau=tau, chart_parameter=s)
