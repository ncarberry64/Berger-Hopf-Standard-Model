"""Source-directed tangent columns of the retained mixed Higgs/lepton graph.

The starting Higgs field domain retains both its pinned n1+n3 block and
the already evaluated even n0+n2+n4 image.  The external coordinate probes
have n1 support, so their complete first-source image has n0+n2 output and
larger internal fermion shells.  Homogeneity of
the retained coefficient base makes these finite image restrictions
exact for these diagrams; this is not a bound on the starting loop domain.
"""
from __future__ import annotations
from functools import lru_cache
import numpy as np
from scipy.linalg import eigh
from .muon_intrinsic_scalar_discretization import scalar_s3_discretization
from .muon_intrinsic_scalar_temporal_image import temporal_image_green_kernel,temporal_yukawa_source_image
from .muon_common_cutoff_green_kernel import contraction_series_tail_upper,outward_positive_product_sum
from .muon_magnetic_mixed_green import _finite,_positive


@lru_cache(maxsize=1)
def soft_current_angular_images():
    """Complete Peter--Weyl product images, in the inherited real frame."""
    s=scalar_s3_discretization(6);labels=s['real_basis_labels']
    groups=dict(Fodd=[1,3,5],Feven=[0,2,4,6],Hodd=[1,3],Heven=[0,2,4],Xin=[1],Xout=[0,2],source=[1])
    ids={k:np.array([i for i,l in enumerate(labels)if l[0]in ns])for k,ns in groups.items()}
    values={k:s['real_basis_values'][:,v]for k,v in ids.items()};w=s['haar_weights']
    def gaunt(left,field,right):
        products=(values[field][:,:,None]*values[right][:,None,:]).reshape(len(w),-1)
        G=(values[left].T@(w[:,None]*products)).reshape(len(ids[left]),len(ids[field]),len(ids[right]))
        # Exact triangle/parity zeros follow from representation degree,
        # rather than deleting small evaluated coefficients.
        nl=np.array([labels[i][0]for i in ids[left]])[:,None,None]
        nf=np.array([labels[i][0]for i in ids[field]])[None,:,None]
        nr=np.array([labels[i][0]for i in ids[right]])[None,None,:]
        forbidden=(nl<abs(nf-nr))|(nl>nf+nr)|((nl+nf+nr)%2!=0)
        G[forbidden]=0
        remainder=products-values[left]@G.reshape(len(ids[left]),-1)
        residual=float(np.sqrt(np.max(np.sum(w[:,None]*remainder**2,axis=0))))
        return G,residual
    specifications=dict(left_odd=('Fodd','Hodd','Xout'),right_even=('Feven','Hodd','Xin'),
        left_even=('Feven','Heven','Xout'),right_odd=('Fodd','Heven','Xin'))
    maps={};residuals={}
    for key,spec in specifications.items():maps[key],residuals[key]=gaunt(*spec)
    maps['magnetic_odd_even'],_=gaunt('Fodd','source','Feven')
    # The magnetic map alone need not close Feven6 -> Fodd7.  Its omitted
    # image cannot return through the left vertex, whose degree is <=5,
    # and the homogeneous base has no cross-shell propagation.
    return dict(gaunts=maps,product_residuals=residuals,
        labels={k:[labels[i]for i in v]for k,v in ids.items()},
        derivatives={k:s['real_angular_derivative_matrices'][:,v][:,:,v]for k,v in ids.items()},
        quadrature_polynomial_degree=s['quadrature_polynomial_degree'],
        harmonic_source_image_proof='Hodd<=3 times Xin1 gives Feven<=4; Hodd<=3 times Xout<=2 gives Fodd<=5; Heven<=4 times Xout<=2 gives Feven<=6; magnetic source1 gives only neighboring levels; homogeneous base preserves every shell',
        no_starting_Higgs_loop_complement_bound=True)


def _vertices(G,mass):
    return .75*np.einsum('ihx,cuv->chiuxv',G,mass).reshape(4*G.shape[1],G.shape[0]*6,G.shape[2]*6)


def soft_current_factor_data(*,W,Omega_tau,alpha,R4,lapse,length,mass_vertices,magnetic_vertices):
    """Bind the actual homogeneous coefficient factor and all reached vertices."""
    B=_finite(W,'same-background spatial factor')+_finite(Omega_tau,'same-background temporal connection')
    al=_finite(alpha,'inherited six-component Clifford frame');r=_positive(R4,'actual R4');N=_positive(lapse,'actual lapse');L=_positive(length,'existing cell length')
    M=_finite(mass_vertices,'four fixed-Y scalar vertices');X=_finite(magnetic_vertices,'three complete n1 magnetic coefficient vertices')
    if B.shape!=(6,6)or al.shape!=(3,6,6)or M.shape!=(4,6,6)or X.shape!=(3,4,6,6):
        raise ValueError('complete same-family factors and n1 source required')
    space=soft_current_angular_images();result=dict(angular=space,length=L,lapse=N)
    for parity,key in (('odd','Fodd'),('even','Feven')):
        E=space['derivatives'][key];A=-1j*sum(np.kron(E[i],al[i])for i in range(3))/r+np.kron(np.eye(len(E[0])),B)
        P=12/(N*N*L*L)*np.eye(len(A))+A.conj().T@A;p,V=eigh(P)
        if p[0]<=0:raise ArithmeticError('actual reached factor must be positive')
        result.update({f'A_{parity}':A,f'P_{parity}':P,f'p_{parity}':p,f'V_{parity}':V})
    for name,G in space['gaunts'].items():
        if name!='magnetic_odd_even':result[name]=_vertices(G,M)
    G=space['gaunts']['magnetic_odd_even']
    Xi=np.einsum('isj,Asuv->Aiujv',G,X).reshape(3,len(result['A_odd']),len(result['A_even']))
    Xadj=np.einsum('isj,Asvu->Aiujv',G,X.conj()).reshape(Xi.shape)
    result.update(Xi=Xi,Xadj=Xadj,
        square_left=result['A_odd'].conj().T@Xi,
        square_right=Xadj@result['A_even'])
    return result


def _branch_application(data,scalar,cutoff,kinetic,vertex,terms):
    """Differentiate the two-Green graph, retaining both ordered placements."""
    Ao,Ae=data['A_odd'],data['A_even'];Vo,Ve=data['V_odd'],data['V_even']
    shift=(kinetic-12)/(data['lapse']**2*data['length']**2)
    po,pe=data['p_odd']+shift,data['p_even']+shift
    ho,Uo=eigh(_finite(scalar['positive_H_odd'],'same scalar odd form',real=True));he,Ue=eigh(_finite(scalar['positive_H_even'],'same scalar even image',real=True))
    if ho[0]<=0 or he[0]<=0:raise ValueError('positive same-action scalar forms required')
    gram=_positive(scalar['action_Gram_scalar'],'same scalar action Gram')
    transform=lambda U,B:np.einsum('ab,bij->aij',U.T,B)*(vertex/.75)
    Blo,Bre=transform(Uo,data['left_odd']),transform(Uo,data['right_even'])
    Ble,Bro=transform(Ue,data['left_even']),transform(Ue,data['right_odd'])
    L=Blo.conj().transpose(0,2,1)@Vo;R=(Ve.conj().T@Ae.conj().T)@Bre
    Lr=Bre.conj().transpose(0,2,1)@Ve;Rr=(Vo.conj().T@Ao.conj().T)@Blo
    Rplain=Ve.conj().T@Bre;Rrplain=Vo.conj().T@Blo
    squares=[Vo.conj().T@data[k]@Ve for k in ('square_left','square_right')]
    numerator=Vo.conj().T@data['Xadj']@Ve
    reverse_numerator=Ve.conj().T@data['Xi'].conj().transpose(0,2,1)@Vo
    names=('fermion_square_left','fermion_square_right','fermion_numerator_contact',
        'scalar_propagator_left_field_image','scalar_propagator_right_field_image')
    forward={k:np.zeros((3,Blo.shape[-1],Bre.shape[-1]),complex)for k in names}
    reverse={k:np.zeros((3,Bre.shape[-1],Blo.shape[-1]),complex)for k in names}
    tails={k:[]for k in names};methods=set()
    def kernel(*p):
        out=temporal_image_green_kernel(*p,cutoff=cutoff,terms=terms);methods.add(out['method']);return out
    def bound(name,k,L,M,R):tails[name].append((contraction_series_tail_upper(k['kernel_approximation_upper'],L,M,R,gram),))
    for a,h in enumerate(ho):
        k3=kernel(po[:,None],pe[None,:],h);ko,ke=kernel(po,h),kernel(pe,h)
        for j in range(3):
            for name,S in zip(names[:2],squares):
                forward[name][j]-=L[a]@(k3['value']*S[j])@R[a]/gram
                reverse[name][j]-=Lr[a]@(k3['value'].T*S[j].conj().T)@Rr[a]/gram
                bound(name,k3,L[a],S[j],R[a]);bound(name,k3,Lr[a],S[j].conj().T,Rr[a])
            forward[names[2]][j]+=L[a]@(ko['value'][:,None]*numerator[j])@Rplain[a]/gram
            reverse[names[2]][j]+=Lr[a]@(ke['value'][:,None]*reverse_numerator[j])@Rrplain[a]/gram
            bound(names[2],ko,L[a],numerator[j],Rplain[a]);bound(names[2],ke,Lr[a],reverse_numerator[j],Rrplain[a])
    dH=Ue.T@_finite(scalar['delta_positive_H_even_odd'],'same scalar insertion',real=True)[:3]@Uo
    LH=Ble.conj().transpose(0,2,1)@Ve;RH=(Ve.conj().T@Ae.conj().T)@Ble
    LRH=Bro.conj().transpose(0,2,1)@Vo;RRH=(Vo.conj().T@Ao.conj().T)@Bro
    plainH=Vo.conj().T@Bro;plainHr=Ve.conj().T@Ble
    # The even field image also has an available unchanged Jacobi block.
    # Its same-background fermion insertions must be evaluated, rather
    # than adding both PH placements to an odd-only loop and calling
    # that the derivative of the complete image-domain action.
    for a,h in enumerate(he):
        k3=kernel(pe[:,None],po[None,:],h);ke,ko=kernel(pe,h),kernel(po,h)
        for j in range(3):
            for name,S in zip(names[:2],squares):
                Sj=S[j].conj().T
                forward[name][j]-=LH[a]@(k3['value']*Sj)@RRH[a]/gram
                reverse[name][j]-=LRH[a]@(k3['value'].T*S[j])@RH[a]/gram
                bound(name,k3,LH[a],Sj,RRH[a]);bound(name,k3,LRH[a],S[j],RH[a])
            forward[names[2]][j]+=LH[a]@(ke['value'][:,None]*reverse_numerator[j])@plainH[a]/gram
            reverse[names[2]][j]+=LRH[a]@(ko['value'][:,None]*numerator[j])@plainHr[a]/gram
            bound(names[2],ke,LH[a],reverse_numerator[j],plainH[a]);bound(names[2],ko,LRH[a],numerator[j],plainHr[a])
    # Both field placements participate in the complete PH source image.
    # Each has a different unchanged fermion shell parity.  This extends
    # the earlier one-placement PH application, which remains a subset.
    for f,F in enumerate(pe):
        k3=kernel(he[:,None],ho[None,:],F)
        l,r=LH[:,:,f].T,R[:,f,:]
        for j in range(3):
            forward[names[3]][j]-=l@(k3['value']*dH[j])@r/gram
            bound(names[3],k3,l,dH[j],r)
            reverse[names[4]][j]-=Lr[:,:,f].T@(k3['value'].T*dH[j].T)@RH[:,f,:]/gram
            bound(names[4],k3,Lr[:,:,f].T,dH[j].T,RH[:,f,:])
    for f,F in enumerate(po):
        k3=kernel(ho[:,None],he[None,:],F)
        l,r=L[:,:,f].T,RRH[:,f,:]
        for j in range(3):
            forward[names[4]][j]-=l@(k3['value']*dH[j].T)@r/gram
            bound(names[4],k3,l,dH[j].T,r)
            reverse[names[3]][j]-=LRH[:,:,f].T@(k3['value'].T*dH[j])@Rr[:,f,:]/gram
            bound(names[3],k3,LRH[:,:,f].T,dH[j],Rr[:,f,:])
    for out in (forward,reverse):
        out['total']=sum(out.values())
        out['scalar_propagator_insertion']=out[names[3]]+out[names[4]]
    return dict(forward=forward,reverse=reverse,kernel_methods=sorted(methods),
        kernel_approximation_contracted_upper={k:outward_positive_product_sum(v)for k,v in tails.items()})


def soft_current_tangent_application(data,scalar,*,cutoff,terms=6):
    """Complete first-source n1 -> n0+n2 columns on both temporal images."""
    c=_positive(cutoff,'same explicit cutoff',zero=True);t=temporal_yukawa_source_image()
    branches=[_branch_application(data,scalar,c,k,v,terms)for k,v in zip(t['temporal_eigenvalues'],t['normalized_vertex_coefficients'])]
    out={p:{name:sum(b[p][name]for b in branches)for name in branches[0][p]}for p in ('forward','reverse')}
    return dict(**out,cutoff=c,temporal_image=t,
        kernel_approximation_contracted_upper={k:outward_positive_product_sum([(b['kernel_approximation_contracted_upper'][k],)for b in branches])for k in branches[0]['kernel_approximation_contracted_upper']},
        kernel_methods=sorted({m for b in branches for m in b['kernel_methods']}),
        external_input='complete real n1 tensor six-component family',external_output='complete real n0+n2 tensor six-component family',
        both_source_squares_numerator_and_scalar_insertion_retained=True,
        source_first_order_differential_complement_removed=False,
        represented_odd_and_even_scalar_loop_blocks_evaluated=True,
        starting_scalar_loop_domain_enclosed=False,
        physical_Pauli_or_native_completion_claimed=False)
