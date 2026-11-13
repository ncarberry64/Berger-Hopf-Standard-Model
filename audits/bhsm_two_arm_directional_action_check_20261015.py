"""Independent scalar directional two-jet of the retained reset action.

This is an instantaneous full536 coefficient-graph check, never a solved
exterior, outgoing-domain derivative or coupled matching correction.
"""
from pathlib import Path
from hashlib import sha256
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'
import argparse
import inspect
import json
import sys


def evaluate(repository, output):
    import numpy as np
    root, out = Path(repository).resolve(), Path(output).resolve()
    if out.exists():
        raise FileExistsError('Preserve every earlier diagnostic.')
    out.mkdir(parents=True)
    sys.path[:0] = [str(root/'src'), str(root/'scripts')]
    from evaluate_muon_continued_current_factor import retained_input
    import bhsm.interface.muon_holomorphic_normal_geometry as geo
    from bhsm.interface.aether_exact_radial_schur_lift_v15_83 import Jet
    from bhsm.interface.muon_holomorphic_two_arm_action import holomorphic_two_arm_action
    from bhsm.interface.muon_parent_maxwell_full_weak import M
    from bhsm.interface.muon_parent_mean_causal_action import MAXWELL_TO_CAP
    from bhsm.interface.muon_parent_retarded_hypercharge import WALL
    from bhsm.interface.muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation
    from bhsm.interface.muon_literal_euclidean_wall_action import VOLUME
    from bhsm.interface.muon_matched_mechanical_source import epsilon
    from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
    pins = {}
    phase, _ = retained_input('outgoing', pins)
    rep = phase['representation']
    candidate = root/'artifacts/muon_fixed_parent_finite_shooting_20261012/run_1/trial_0000/candidate.npz'
    params_path = candidate.parent.parent/'result.json'
    pins[str(candidate)] = sha256(candidate.read_bytes()).hexdigest()
    pins[str(params_path)] = sha256(params_path.read_bytes()).hexdigest()
    with np.load(candidate, allow_pickle=False) as z:
        raw, reference = z['raw_pair'].copy(), z['reference_pair'].copy()
    params = json.loads(params_path.read_bytes())['action_parameters']
    original_variables = geo._geometry_variables
    cap_code = inspect.getsource(geo.holomorphic_cap_and_weights).replace(
        'def holomorphic_cap_and_weights(', 'def directional_cap(').replace(
        'q,v,m,delta,dr,wall,Cstar=_geometry_variables(raw);n=100',
        'q,v,m,delta,dr,wall,Cstar=_geometry_variables(raw);n=len(delta.gradient)')
    local = {}
    exec(cap_code, geo.__dict__, local)
    cap_function = local['directional_cap']
    def geometry(x, d, rho=None):
        def variables(values, *, differentiate=True):
            xj = [Jet.affine(v, np.array([w], complex)) for v, w in zip(values, d)]
            q, v, m = xj[:37], xj[37:74], xj[74:98]
            s, rate = xj[98:]
            sk, sj = (-1.)**np.arange(1,13), (-1.)**np.arange(12)
            Cstar = geo.RADIUS0*(q[0]+sum((a*b for a,b in zip(q[1:13],sk)),Jet.constant(0.,1))
                +sum((a*b for a,b in zip(q[13:25],sj)),Jet.constant(0.,1))).exp()
            lc = v[0]+sum((a*b for a,b in zip(v[1:13],sk)),Jet.constant(0.,1))
            lc += sum((a*b for a,b in zip(v[13:25],sj)),Jet.constant(0.,1))
            delta = s/Cstar
            return q,v,m,delta,(rate-lc*s)/Cstar,np.pi/4+delta,Cstar
        geo._geometry_variables = variables
        try:
            if rho is None:
                return cap_function(x, points=rep['cap_points'])
            return geo.holomorphic_geometry_rows(x, rho)
        finally:
            geo._geometry_variables = original_variables
    C = lambda x: Jet.constant(complex(x), 1)
    dot = lambda a,b: sum((x*y for x,y in zip(a,b)), C(0))
    sq = lambda a: dot(np.ravel(a),np.ravel(a))
    eps = epsilon()
    def adprod(a,b):
        return np.array([sum((eps[i,j,k]*a[j]*b[k] for j in range(3) for k in range(3)),C(0))/np.sqrt(2)
            for i in range(3)]+[C(0)],object)
    generators = higgs_u2_real_representation()['real_generators']
    def value_jet(x, d):
        parent = geometry(x[0,:100],d[0,:100],rep['rho'])
        parent_wall = geometry(x[0,:100],d[0,:100],[WALL])
        refs = [geo.holomorphic_geometry_rows(t[:100],rep['rho'],differentiate=False,connection_only=True) for t in reference]
        refs_wall = [geo.holomorphic_geometry_rows(t[:100],[WALL],differentiate=False,connection_only=True) for t in reference]
        gb = np.asarray(rep['gauge_basis'])[:,:,0].reshape(len(rep['rho']),80,20)
        gr = np.asarray(rep['gauge_radial_basis'])[:,:,0].reshape(len(rep['rho']),80,20)
        total = C(0)
        for arm in range(2):
            fields = [Jet.affine(v,np.array([w],complex)) for v,w in zip(x[arm],d[arm])]
            cap = geometry(x[arm,:100],d[arm,:100])
            rows = geometry(x[arm,:100],d[arm,:100],rep['rho'])['rows']
            total += cap['total']
            if params['surface_gamma'] is not None:
                total += params['surface_gamma']*cap['surface_per_gamma']
            for j,(row,weight) in enumerate(zip(rows,rep['radial_quadrature'])):
                eff = [parent['rows'][j][key] for key in ('connection_lambda','lambda_tau','lambda_rho')]
                if arm:
                    eff = [v+C(-refs[0]['rows'][j][key].value+refs[1]['rows'][j][key].value)
                        for v,key in zip(eff,('connection_lambda','lambda_tau','lambda_rho'))]
                A = np.array([dot(gb[j,:,k],fields[100:180]) for k in range(20)],object).reshape(5,4)
                At = np.array([dot(gb[j,:,k],fields[180:260]) for k in range(20)],object).reshape(5,4)
                Ar = np.array([dot(gr[j,:,k],fields[100:180]) for k in range(20)],object).reshape(5,4)
                for h in range(3):
                    for k in range(4):
                        A[2+h,k] += M[h,k]*(eff[0]-1)
                        At[2+h,k] += M[h,k]*eff[1]
                        Ar[2+h,k] += M[h,k]*eff[2]
                X = At[1]-Ar[0]+adprod(A[0],A[1])
                T = np.array([At[2+h]+adprod(A[0],A[2+h]) for h in range(3)],object)
                R = np.array([Ar[2+h]+adprod(A[1],A[2+h]) for h in range(3)],object)
                B = 2*A[2:].copy()
                for h,jj,kk in np.argwhere(eps):
                    B[h] += .5*eps[h,jj,kk]*adprod(A[2+jj],A[2+kk])
                e,r,ang,k,beta = [row[key] for key in ('electric','radial','angular','electric_radial','shift')]
                # Multiply elementwise explicitly: ndarray*Jet dispatch can
                # attempt to construct a Jet with an array-valued scalar.
                Y = np.array([[T[h,k]-beta*R[h,k] for k in range(4)] for h in range(3)],object)
                full = .5*(k*sq(X)+e*sq(Y)-r*sq(R)-ang*sq(B))
                lam,lt,lr = [row[key] for key in ('connection_lambda','lambda_tau','lambda_rho')]
                baseline = .5*np.sum(M*M)*(e*(lt-beta*lr)**2-r*lr**2-ang*(2*(lam-1)*lam)**2)
                total += MAXWELL_TO_CAP*weight*(full-baseline)
            effwall = parent_wall['rows'][0]['connection_lambda']
            if arm:
                effwall += -refs_wall[0]['rows'][0]['connection_lambda'].value+refs_wall[1]['rows'][0]['connection_lambda'].value
            wall = np.array([[dot(rep['wall_trace_map'][f,c],fields[100:180]) for c in range(4)] for f in range(5)],object)
            for h in range(3):
                for k in range(4):
                    wall[2+h,k] += M[h,k]*(effwall-1)
            O = np.array([[[dot(wall[f],generators[:,j,k]) for k in range(4)] for j in range(4)] for f in range(5)],object)
            H, Hd = fields[260:264], fields[264:]
            DH = np.array([[Hd[j]+dot(O[0,j],H) for j in range(4)]]+
                [[dot(O[f,j],H) for j in range(4)] for f in range(2,5)],object)
            q = dot(H,H)-params['nu_squared_action']
            total += (cap['wT']*sq(DH[0])-cap['wS']*sq(DH[1:])-
                cap['wV']*rep['scalar_matching']['lambda_H']*q*q)/VOLUME
        return total
    base = holomorphic_two_arm_action(raw,reference,rep,**params)
    rng = np.random.default_rng(20261015)
    directions = []
    for name,mask in [('all536',np.ones((2,268),bool)),('parent_geometry',np.r_[np.ones(100,bool),np.zeros(436,bool)].reshape(2,268)),
        ('child_geometry',np.r_[np.zeros(268,bool),np.ones(100,bool),np.zeros(168,bool)].reshape(2,268)),
        ('gauge_and_H',np.tile(np.r_[np.zeros(100,bool),np.ones(168,bool)],(2,1)))]:
        d = (rng.standard_normal((2,268))+1j*rng.standard_normal((2,268)))*mask
        d /= np.linalg.norm(d)
        directions.append((name,d))
    records = []
    for name,d in directions:
        a = value_jet(raw,d)
        first = base['raw_gradient']@d.ravel()
        second = d.ravel()@base['raw_hessian']@d.ravel()
        rec = dict(direction=name,value_relative_error=float(abs(a.value-base['value'])/max(1.,abs(base['value']))),
            first_relative_error=float(abs(a.gradient[0]-first)/max(1.,abs(first))),
            second_relative_error=float(abs(a.hessian[0,0]-second)/max(1.,abs(second))),
            first_directional=[float(first.real),float(first.imag)],second_directional=[float(second.real),float(second.imag)])
        records.append(rec)
        print(json.dumps(rec,sort_keys=True),flush=True)
    # One deliberately bounded independent finite-difference stencil.  It
    # perturbs the literal exported full536 action, never a projected row
    # or the independent scalar composition above.  No step tuning is used.
    d = directions[0][1]
    h = 1e-3
    branches = {}
    for multiple in (-2,-1,1,2):
        branches[multiple] = holomorphic_two_arm_action(raw+multiple*h*d,reference,rep,**params)
        print(json.dumps(dict(stage='literal_full536_finite_difference',multiple=multiple,step=h)),flush=True)
    value_first = (branches[-2]['value']-8*branches[-1]['value']+8*branches[1]['value']-branches[2]['value'])/(12*h)
    gradient_first = (branches[-2]['raw_gradient']-8*branches[-1]['raw_gradient']+
        8*branches[1]['raw_gradient']-branches[2]['raw_gradient'])/(12*h)
    first = base['raw_gradient']@d.ravel()
    hessian_direction = base['raw_hessian']@d.ravel()
    fd = dict(direction='all536',formula='five-point centered first derivative',step=h,
        scalar_value_to_gradient_relative_error=float(abs(value_first-first)/max(1.,abs(first))),
        all536_gradient_to_Hessian_vector_relative_error=float(np.linalg.norm(gradient_first-hessian_direction)/
            max(1.,np.linalg.norm(hessian_direction))),
        all536_gradient_to_Hessian_vector_max_component_scaled_error=float(np.max(abs(gradient_first-hessian_direction))/
            max(1.,np.max(abs(hessian_direction)))),
        truncation_and_roundoff_not_rigorously_enclosed=True)
    print(json.dumps(dict(finite_difference=fd),sort_keys=True),flush=True)
    R = base['master_lift']
    q = R.T@raw.ravel()
    feedback = base['gradient'][:252]-base['parent']['gradient']
    endpoint = -base['gradient'][base['velocity_indices']].copy()
    endpoint[:106] += 2*base['parent']['gradient'][106:212]
    _compressed_npz(out/'literal_action_and_directional_contacts.npz',dict(raw_pair=raw,reference_pair=reference,
        master_coefficients=q,raw_gradient=base['raw_gradient'],raw_hessian=base['raw_hessian'],
        full_gradient=base['gradient'],full_hessian=base['hessian'],parent_own_gradient=base['parent']['gradient'],
        parent_child_feedback=feedback,source_gradient_contact=base['source_gradient_contact'],
        source_Hessian_contact=base['source_Hessian_contact'],temporal_cotangent=base['temporal_cotangent'],
        master_lift=R,directions=np.array([d for _,d in directions])))
    for name,module in list(sys.modules.items()):
        p = getattr(module,'__file__',None)
        if name.startswith('bhsm.') and p and Path(p).is_relative_to(root):
            pins[str(Path(p))] = sha256(Path(p).read_bytes()).hexdigest()
    for p,h in pins.items():
        if not Path(p).is_absolute():
            p = str(root/p)
        if sha256(Path(p).read_bytes()).hexdigest()!=h:
            raise ValueError('Consumed input changed: '+p)
    result = dict(classification='LITERAL_FULL536_RESET_ACTION_INDEPENDENT_DIRECTIONAL_SCALAR_TWO_JET_CHECK',
        records=records,input_hashes=pins,producer_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        geometry_jet_dimension_compression='One independent analytic directional coordinate; cap n=100 replaced by actual directional dimension only. Original scalar integrand, branches, quadratures and response chart retained.',
        independence='No returned source gradient or Hessian used by the scalar directional path. Independent polynomial Maxwell/Higgs composition, original geometry/chart scalar primitives.',
        endpoint_cotangent_identity_max=float(np.max(abs(endpoint-base['temporal_cotangent']))),
        raw_Hessian_transpose_error=float(np.max(abs(base['raw_hessian']-base['raw_hessian'].T))),
        parent_child_feedback_norm=float(np.linalg.norm(feedback)),
        parent_child_feedback_position_norm=float(np.linalg.norm(feedback[:106])),
        parent_child_feedback_velocity_norm=float(np.linalg.norm(feedback[106:212])),
        parent_child_feedback_algebraic_norm=float(np.linalg.norm(feedback[212:])),
        mixed_parent_child_Hessian_norm=float(np.linalg.norm(base['hessian'][:252,252:])),
        parent_raw_geometry_source_gradient_norm=float(np.linalg.norm(base['source_gradient_contact'][:100])),
        independent_literal_full536_finite_difference=fd,Higgs_terms_preserved=True,
        fermion_spin_terms_or_state_evaluated=False,physical_outgoing_energy_field_domain_derivative_passed=False,
        coupled_matching_corrections=0,physical_muon_moment=None)
    result['finite_directional_scalar_two_jet_within_2e10'] = max(max(r[k] for k in
        ('value_relative_error','first_relative_error','second_relative_error')) for r in records)<=2e-10
    result['archives'] = {p.name:sha256(p.read_bytes()).hexdigest() for p in out.glob('*.npz')}
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return result


if __name__=='__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--repository',required=True)
    p.add_argument('--output',required=True)
    a = p.parse_args()
    evaluate(a.repository,a.output)
