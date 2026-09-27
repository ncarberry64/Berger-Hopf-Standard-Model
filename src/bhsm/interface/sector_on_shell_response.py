"""Sector response through one common interior solve at fixed external data.

The entries are caller-owned Hessian blocks of the same action/domain, not
separately postulated sector boundary conditions. Algebraic contribution
labels need not define orthogonal physical sectors or positive energies.
"""
from flint import arb_mat


def shared_sector_response(sectors, dq, dSigma):
    """Return each D Lambda_s and their sum without independent sector inverses."""
    if not sectors:
        raise ValueError('at least one owned action contribution is required')
    if dq.ncols()!=dSigma.ncols():
        raise ValueError('shared child/seam parameter columns required')
    first=next(iter(sectors.values()))
    required=('ii','iq','iSigma','qi','qq','qSigma')
    if any(set(s)!=set(required) for s in sectors.values()):
        raise ValueError('all six signed Hessian blocks must be explicit')
    total={}
    for key in required:
        shape=(first[key].nrows(),first[key].ncols())
        if any((s[key].nrows(),s[key].ncols())!=shape for s in sectors.values()):
            raise ValueError('sector blocks must share coordinates')
        total[key]=sum((s[key] for s in sectors.values()),arb_mat(*shape))
    interior=-total['ii'].solve(total['iq']*dq+total['iSigma']*dSigma)
    contributions={name:s['qq']*dq+s['qSigma']*dSigma+s['qi']*interior
                   for name,s in sectors.items()}
    summed=sum(contributions.values(),arb_mat(dq.nrows(),dq.ncols()))
    return contributions,summed,interior
