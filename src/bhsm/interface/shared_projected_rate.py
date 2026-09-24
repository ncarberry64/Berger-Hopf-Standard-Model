"""Signed output recipes acting on the same normalized mixed-rate graph.

The recipe is exact before enclosure. Importing a parent's affine model is
an explicit numerical relaxation; its full expression remains identified
by the parent's content hash and root. It is not a new independent error.
"""
from flint import arb,fmpq
from bhsm.interface.shared_expression_graph import restore


class LinkedModels:
    def __init__(self,domain,metadata,parent_sha):
        self.domain,self.metadata,self.parent_sha=domain,metadata,parent_sha
        self.cache={}

    def root(self,name):
        node=self.metadata['roots'][name]
        if node not in self.cache:
            model=self.metadata['affine_enclosures'][name]
            a=[arb(0)]*self.domain.dimension
            for i,v in model['a']:a[i]=restore(v)
            self.cache[node]=self.domain.affine(restore(model['c']),a,arb(fmpq(model['r'])),provenance={
                'role':'external_shared_expression','parent_SHA256':self.parent_sha,
                'parent_root':name,'parent_node':node,
                'interpretation':'same referenced function; full parent expression is authoritative',
                'numerical_relaxation':'parent affine remainder retained as an unresolved shared function'})
        return self.cache[node]


def projected_mixed(models,row,prefix=''):
    """Project every numerator jet before the common implicit quotient.

    Projection is independent of the physical theta/u/v parameters. The
    scalar nu and its derivatives are shared across all output components.
    """
    d=models.domain
    numerator={k:sum((co*models.root(prefix+f'factored_numerator/{k}/{i}')
        for i,co in enumerate(row) if not co.is_zero()),d.affine(0)) for k in ('value','u','v','uv')}
    nu,nuu,nuv,nuuv=[models.root(prefix+'normalization/'+k) for k in ('norm','norm_u','norm_v','norm_uv')]
    iv=nu.reciprocal_positive(1)
    value=numerator['value']*iv
    du=(numerator['u']-nuu*value)*iv
    dv=(numerator['v']-nuv*value)*iv
    return (numerator['uv']-nuuv*value-nuu*dv-nuv*du)*iv


def booked_mixed(domain,projected_blocks,rL,rT,variables):
    """Differentiate the frozen half-Hessian LL and doubled LT booking.

    u/v blocks refer to the same physical endpoint directions as every
    endpoint and midpoint rate. Cross-endpoint LL monomials combine by
    identity before the final support, including Q01 + Q10.
    """
    def var(i):
        if i not in variables:variables[i]=domain.variable(i)
        return variables[i]
    result=domain.affine(0)
    for family,blocks in projected_blocks.items():
        for pair,Q in blocks.items():
            a,b=map(int,pair)
            ua,va=var(150+75*a),var(300+75*a)
            if family=='LL':
                result+=Q[0]*rL*rL*(ua*var(300+75*b)+va*var(150+75*b))
            elif family=='LT':
                result+=2*rL*rT*sum((co*(ua*var(301+75*b+j)+va*var(151+75*b+j))
                    for j,co in enumerate(Q)),domain.affine(0))
            else:raise ValueError('only frozen LL and LT booking is authorized')
    return result
