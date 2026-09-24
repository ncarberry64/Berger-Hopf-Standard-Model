"""Matrix compiler for the shared output recipe's affine relaxation.

Signed coefficient projection precedes the common normalization recurrence.
Higher-order parent tails remain explicitly unresolved; this backend does
not claim a complete bilinear coefficient or full-correlation certificate.
"""
from flint import arb,arb_mat,fmpq
from bhsm.interface.shared_expression_graph import restore
from bhsm.interface.sparse_affine_enclosure import SparseAffine


def restore_model(domain,row):
    return SparseAffine(domain,restore(row['c']),{i:restore(v) for i,v in row['a']},arb(fmpq(row['r'])))


class ProjectedAffineModels:
    def __init__(self,domain,metadata,size=99):
        self.domain,self.size=domain,size
        enclosures=metadata['affine_enclosures'];self.jets={}
        for key in ('value','u','v','uv'):
            names=[f'factored_numerator/{key}/{i}' for i in range(size)]
            identities={};positions=[];models=[]
            for name in names:
                node=metadata['roots'][name]
                if node not in identities:
                    identities[node]=len(models);models.append(restore_model(domain,enclosures[name]))
                positions.append(identities[node])
            count=len(models)
            shared=arb_mat(size,count,[arb(positions[i]==j) for i in range(size) for j in range(count)])
            indices=sorted({j for x in models for j in x.coefficients})
            C=arb_mat(count,1,[x.c for x in models])
            A=arb_mat(count,len(indices),[x.coefficients.get(j,arb(0)) for x in models for j in indices])
            R=arb_mat(count,1,[x.r for x in models])
            self.jets[key]=C,A,R,indices,shared
        self.nu,self.nuu,self.nuv,self.nuuv=[restore_model(domain,enclosures['normalization/'+k]) for k in ('norm','norm_u','norm_v','norm_uv')]
        safe=min(arb(1),self.nu.c.lower())
        if not safe>0:raise ValueError('positive center and same-domain common norm lower required')
        self.inverse=self.nu._unary(1/self.nu.c,-1/self.nu.c**2,(2/safe**3).upper())

    def mixed(self,P):
        if P.ncols()!=self.size:raise ValueError('complete projected output required')
        numerators={}
        for key,(C,A,R,indices,shared) in self.jets.items():
            effective=P*shared
            absolute=arb_mat(effective.nrows(),effective.ncols(),[abs(x).upper() for x in effective.entries()])
            centers=effective*C;coefficients=effective*A;tails=absolute*R
            numerators[key]=[SparseAffine(self.domain,centers[i,0],
                {j:coefficients[i,k] for k,j in enumerate(indices) if not coefficients[i,k].is_zero()},
                tails[i,0].upper()) for i in range(P.nrows())]
        result=[]
        for N,Nu,Nv,Nuv in zip(*(numerators[k] for k in ('value','u','v','uv'))):
            value=N*self.inverse
            du=(Nu-self.nuu*value)*self.inverse
            dv=(Nv-self.nuv*value)*self.inverse
            result.append((Nuv-self.nuuv*value-self.nuu*dv-self.nuv*du)*self.inverse)
        return result


def booked_affine_relaxation(domain,blocks,rL,rT):
    """Compile the signed bilinear booking after equal monomial fusion.

    The exact coefficient matrices remain frozen input operands. This is
    the outward affine tail of that polynomial, with no fictitious affine
    coefficients for its degree-two directional monomials.
    """
    LL,LT=blocks['LL'],blocks['LT'];rows=LL['00'].nrows()
    values=[]
    for i in range(rows):
        bound=2*rL*rL*(abs(LL['00'][i,0]).upper()+abs(LL['11'][i,0]).upper()+abs(LL['01'][i,0]+LL['10'][i,0]).upper())
        for Q in LT.values():
            bound+=4*rL*rT*sum((abs(Q[i,j]).upper()**2 for j in range(Q.ncols())),arb(0)).sqrt().upper()
        values.append(SparseAffine(domain,arb(0),{},bound.upper()))
    return values
