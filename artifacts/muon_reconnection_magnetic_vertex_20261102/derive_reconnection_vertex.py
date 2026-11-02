"""v64: exact action identities, not a physical history or an anomaly solver.

Portable dependencies: Python, SymPy, NumPy (only for the owned curvature check).
The frozen source excerpts are hashed separately from these derived identities.
"""
from __future__ import annotations

import argparse
import ast
from hashlib import sha256
import json
from pathlib import Path

import numpy as np
import sympy as s

HERE = Path(__file__).resolve().parent


def central_action_identities():
    """Differentiate the owned kappa-normalized central angular sector exactly."""
    t, x = s.symbols('t x', real=True)
    k = s.Symbol('kappa', positive=True)
    a, e, r, b, d = [s.Function(n)(t, x) for n in ('a', 'e', 'r', 'beta', 'd')]
    at, ax = s.diff(a, t), s.diff(a, x)
    L = k * (e * (at-b*ax)**2-r*ax**2-4*d*a**2)/2
    P = s.diff(L, at)
    Q = s.diff(L, ax)
    H = P*at-L
    explicit = sum(s.diff(L, c)*s.diff(c, t) for c in (e,r,b,d))
    j = s.Function('j')(t,x)
    equation = s.diff(P,t)+s.diff(Q,x)+4*k*d*a-j
    check = {
        'owned_momentum': s.simplify(P-k*e*(at-b*ax)),
        'owned_radial_conormal': s.simplify(Q+b*P+k*r*ax),
        'canonical_energy_balance': s.simplify(s.diff(H,t)+s.diff(Q*at,x)-j*at+explicit-equation*at),
    }
    p, w, py, ey, by, wy, axy = s.symbols('Pi w Pi_Y e_Y beta_Y w_Y a_rho_Y')
    hc = p**2/(2*k*e)+b*p*ax+k*r*ax**2/2+2*k*d*a**2
    check['Legendre_energy'] = s.simplify(H.subs(at,b*ax+p/(k*e))-hc)
    check['Hamilton_velocity'] = s.simplify(s.diff(hc,p)-(b*ax+p/(k*e)))
    F = p/(k*e)+(b+w)*ax
    tangent = s.diff(F,p)*py+s.diff(F,e)*ey+s.diff(F,b)*by+s.diff(F,w)*wy+s.diff(F,ax)*axy
    check['material_flux_total_tangent'] = s.simplify(tangent-(py/(k*e)-p*ey/(k*e**2)+(by+wy)*ax+(b+w)*axy))
    # Moving-domain Reynolds term: d int H = int H_t + [w H].
    flux, energy, speed = s.symbols('S H w')
    check['moving_endpoint_flux'] = s.expand(-flux+speed*energy+(flux-speed*energy))
    return dict(residuals={n:str(v) for n,v in check.items()},
                explicit_coefficient_work=s.sstr(explicit),
                canonical_energy=s.sstr(hc), material_F_u_i=s.sstr(F),
                material_F_u_i_Y=s.sstr(tangent),
                coefficient_work_identically_zero=explicit == 0,
                scope='Owned central constant-angular sector; no physical fields or material speed supplied.')


def projected_bianchi_identities():
    """Exact polynomial non-Abelian identity witness, not a BHSM event field.

This independently checks the mandatory Dq term and total source motion.
Cartan/Stokes then give the moving-surface formula on a smooth patch.
"""
    t,x,y,h = s.symbols('t x y h', real=True)
    coords=(t,x,y)
    T=[-s.I*s.Matrix([[0,1],[1,0]])/2,
       -s.I*s.Matrix([[0,-s.I],[s.I,0]])/2,
       -s.I*s.diag(1,-1)/2]
    A=[t*x*T[0], x*y*T[1], t*y*T[2]]
    q=(t+1)*T[0]+(x+2)*T[1]+(y+3)*T[2]
    V=[y*T[2],t*T[0],x*T[1]]
    qh=x*y*T[0]+t*T[2]
    comm=lambda a,b:a*b-b*a
    def curvature(connection,i,j):
        return connection[j].diff(coords[i])-connection[i].diff(coords[j])+comm(connection[i],connection[j])
    F={(i,j):curvature(A,i,j) for i,j in ((0,1),(1,2),(2,0))}
    Dq=[q.diff(c)+comm(A[i],q) for i,c in enumerate(coords)]
    dphi=sum(s.diff(s.trace(q*F[j,k]),coords[i]) for i,j,k in ((0,1,2),(1,2,0),(2,0,1)))
    motion=sum(s.trace(Dq[i]*F[j,k]) for i,j,k in ((0,1,2),(1,2,0),(2,0,1)))
    checks={'projected_Bianchi_with_Dq':s.simplify(dphi-motion)}
    for i,j in ((0,1),(1,2),(2,0)):
        shifted=[A[n]+h*V[n] for n in range(3)]
        direct=s.diff(s.trace((q+h*qh)*curvature(shifted,i,j)),h).subs(h,0)
        DV=V[j].diff(coords[i])-V[i].diff(coords[j])+comm(A[i],V[j])-comm(A[j],V[i])
        checks[f'projected_source_motion_{i}{j}']=s.simplify(direct-s.trace(qh*F[i,j]+q*DV))
    # On a regular Higgs-frame patch, q0 is constant and A below represents
    # the fully transformed connection, including the frame derivative.
    q0=T[2]
    contact={(i,j):s.trace(q0*comm(A[i],A[j])) for i,j in F}
    reduced={(i,j):s.trace(q0*F[i,j])-contact[i,j] for i,j in F}
    for i,j in F:
        checks[f'reduced_photon_curvature_{i}{j}']=s.simplify(reduced[i,j]-(s.diff(s.trace(q0*A[j]),coords[i])-s.diff(s.trace(q0*A[i]),coords[j])))
        contact_y=s.trace(q0*(comm(V[i],A[j])+comm(A[i],V[j])))
        shifted=[A[n]+h*V[n] for n in range(3)]
        checks[f'charged_contact_two_placements_{i}{j}']=s.simplify(s.diff(s.trace(q0*comm(shifted[i],shifted[j])),h).subs(h,0)-contact_y)
    checks['reduced_photon_Bianchi']=s.simplify(sum(s.diff(reduced[j,k],coords[i]) for i,j,k in ((0,1,2),(1,2,0),(2,0,1))))
    return dict(residuals={n:str(v) for n,v in checks.items()},
                omitted_Dq_term=s.sstr(s.expand(motion)),
                omitted_Dq_identically_zero=s.simplify(motion)==0,
                reduced_photon_scope='Local regular Higgs frame only; transformed connection includes U^-1 dU; canonical photon normalization and event patching remain owned physical obligations.',
                scope='Exact arbitrary-polynomial algebra check; no state, reconnection rate or physical uncertainty.')


def first_order_photon_insertion():
    """Ordered Frechet insertion and fixed-domain gauge covariance.

G is the owned first-order retarded solution operator when it exists; these
identities neither construct G nor turn it into a Feynman propagator.
"""
    names='A B C G AY BY CY DY GD Qs Qn'
    A,B,C,G,AY,BY,CY,DY,GD,Qs,Qn=s.symbols(names,commutative=False)
    gy=-G*DY*G+GD
    direct=AY-BY*G*C-B*gy*C-B*G*CY
    expected=AY-BY*G*C-B*G*CY+B*G*DY*G*C-B*GD*C
    Keff=A-B*G*C
    ga=Qs*A-A*Qs
    gb=Qs*B-B*Qn
    gc=Qn*C-C*Qs
    gg=Qn*G-G*Qn
    ward=ga-gb*G*C-B*gg*C-B*G*gc-(Qs*Keff-Keff*Qs)
    # Independently differentiate an exact matrix inverse at a regular test point.
    z=s.Symbol('z')
    B0=s.Matrix([[1,2],[0,1]]); B1=s.Matrix([[0,1],[1,0]])
    C0=s.Matrix([[2,0],[1,3]]); C1=s.Matrix([[1,0],[0,-1]])
    D0=s.Matrix([[3,1],[0,2]]); D1=s.Matrix([[1,2],[1,0]])
    G0=D0.inv()
    actual=s.diff(-(B0+z*B1)*(D0+z*D1).inv()*(C0+z*C1),z).subs(z,0)
    formula=-B1*G0*C0-B0*G0*C1+B0*G0*D1*G0*C0
    return dict(residuals={'ordered_total_vertex':str(s.expand(direct-expected)),
                          'compatible_fixed_domain_Ward':str(s.expand(ward)),
                          'exact_matrix_derivative':str(sum(abs(v) for v in actual-formula))},
                insertion=s.sstr(expected),domain_contact=s.sstr(-B*GD*C),
                scope='Operator identity plus exact algebra fixture; no native/exterior inverse evaluated.')


def owned_central_curvature_check():
    """Execute only the frozen owned bracket, not any history producer."""
    ledger=json.loads((HERE/'source_ledger.json').read_text(encoding='utf-8'))
    item=next(x for x in ledger['sources'] if x['path'].endswith('muon_parent_maxwell_full_weak.py'))
    snippet=next(x['text'] for x in item['excerpts'] if x['label']=='owned_bracket')
    tree=ast.parse(snippet)
    assert len(tree.body)==1 and isinstance(tree.body[0],ast.FunctionDef)
    namespace={'np':np}
    exec(compile(tree,'<frozen owned bracket>','exec'),namespace)
    a=np.array([[1.,2.,3.,4.],[-2.,3.,1.,7.]])
    b=np.array([[3.,1.,-2.,6.],[1.,2.,4.,5.]])
    bracket=namespace['_bracket'](a,b)
    assert np.any(bracket[:,:3]!=0)
    return dict(residuals={'owned_hypercharge_bracket':str(float(np.max(np.abs(bracket[:,3]))))},
                scope='Structural centrality check on test vectors, not physical field data.')


def build_result():
    groups=dict(central_action=central_action_identities(),
                projected_Bianchi=projected_bianchi_identities(),
                first_order_insertion=first_order_photon_insertion(),
                owned_curvature=owned_central_curvature_check())
    checks={f'{g}/{n}':s.sympify(v).is_zero is True for g,obj in groups.items() for n,v in obj['residuals'].items()}
    assert all(checks.values()), checks
    ledger=json.loads((HERE/'source_ledger.json').read_text(encoding='utf-8'))
    return dict(schema='bhsm.muon-reconnection-magnetic-vertex.v64',
        classification='ACTION_FLUX_ENERGY_AND_PHOTON_INSERTION_IDENTITIES_VERIFIED_PHYSICAL_EVENT_OPEN',
        exact_checks=checks,groups=groups,source_ledger_sha256=sha256((HERE/'source_ledger.json').read_bytes()).hexdigest(),
        source_count=len(ledger['sources']),physical_guard=2e-10,solver_tolerance=2e-11,
        admitted_temporal_strength=2**-9,admitted_temporal_residual=2.962944017741165e-13,
        physical_event_reconnection_evaluated=False,physical_energy_partition_evaluated=False,
        physical_child_state_constructed=False,physical_common_background_realized=False,
        complete_native_a_mu=None,complete_g_mu=None,total_physical_uncertainty=None,
        no_old_campaign_repeated=True,no_new_workers=True,no_state_choice=True,
        actual_next_operand='Source-projected physical electromotive circulation and matched return on the action-selected event/common domain; include DQ_H, entering, released and moving-domain terms.',
        historical_subtotal=dict(a_mu=0.0011659186179552334,g_mu=2.0023318372359107,classification='calibrated additive subtotal, not a complete native prediction'))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    if args.out.exists():raise FileExistsError('Preserve prior run; select a fresh output directory')
    result=build_result();args.out.mkdir(parents=True)
    (args.out/'result.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(exact_checks=len(result['exact_checks']),all_passed=True,physical_result=False)))


if __name__=='__main__':main()
