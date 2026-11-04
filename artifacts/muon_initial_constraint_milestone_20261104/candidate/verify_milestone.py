"""Portable coefficient replay, not a physical evolution or heat integration."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
PREFIX=Path(sys.base_prefix).resolve()
assert sys.flags.isolated and sys.flags.no_site and sys.flags.no_user_site
assert all(p and Path(p).resolve().is_relative_to(PREFIX) for p in sys.path)
import argparse,ast,cmath,hashlib,json,math
HERE=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
INPUT_PINS={'OPERANDS.json': '272404d69c90a4ce00ba50134ac8d75ab7d736fde1ee84b6913a24b7026a737f', 'OWNED_COEFFICIENTS.py': '74fdc681baea003c5d31278032b604ee16eb918d5658f6189a85bd89afe36142'}
for p,h in INPUT_PINS.items():assert sha(HERE/p)==h,p
d=json.loads((HERE/'OPERANDS.json').read_text())
raw={'gradient':d['stored_gradient536']}
native={'legs':[{'theta22':a['theta22'],'lorentz':{'gradient22':a['gradient22']}} for a in d['native_legs']]}
port={'wall_trace_map':d['wall_trace_map']}
pair,refs=d['trial_pair'],d['reference_pair']
dot=lambda a,b:sum(x*y for x,y in zip(a,b))
checks=[]
def ck(name,error,tolerance=2e-11):
    error=float(error)
    assert math.isfinite(error) and error<=tolerance,(name,error,tolerance)
    checks.append(dict(name=name,error=error,tolerance=tolerance))
tree=ast.parse((HERE/'OWNED_COEFFICIENTS.py').read_text())
fs=[f for f in tree.body if isinstance(f,ast.FunctionDef)]
assert {f.name for f in fs}=={'intrinsic','theta','area_value_rate_gradient'}
assert not any(isinstance(n,(ast.Import,ast.ImportFrom,ast.Global,ast.Nonlocal)) for f in fs for n in ast.walk(f))
ns={'math':math,'cmath':cmath,'dot':dot,'wm':port['wall_trace_map']}
exec(compile(ast.Module(body=fs,type_ignores=[]),'<reviewed-pure-coefficients>','exec'),ns)
intrinsic,theta,area=[ns[k] for k in ('intrinsic','theta','area_value_rate_gradient')]

base = theta(pair, refs)
eps = 1e-25
applications = []
for side, x in enumerate(pair):
    g = intrinsic(x)
    nv = native['legs'][side]['lorentz']
    ck('matching_native_argument_' + str(side),
       max(abs(a-b) for a, b in zip(base[side], native['legs'][side]['theta22'])))
    lapse_gradient = [v.real for v in g['ell_rate'][38:]]
    area_value, area_gradient = area(x)
    # rho is independently recovered from the original area value -rho*ell.
    rho = (-area_value/g['ell']).real
    ck('area_constraint_gradient_' + str(side),
       max(abs(area_gradient[38+j].real + rho*lapse_gradient[j]) for j in range(24)))
    native_constraints = [nv['gradient22'][1]*v for v in lapse_gradient]
    theta_constraint_jac = []
    for j in range(24):
        pp = [[complex(v) for v in xx] for xx in pair]
        pp[side][74+j] += 1j*eps
        tt = theta(pp, refs)
        actual = [[v.imag/eps for v in t] for t in tt]
        err = max(abs(actual[s][a] - (lapse_gradient[j] if s == side and a == 1 else 0.))
                  for s in range(2) for a in range(22))
        ck('native_multiplier_chain_' + str(side) + '_' + str(j), err)
        theta_constraint_jac.append(actual[side])
    known = raw['gradient'][268*side+74:268*side+98]
    # The native pieces are per native leg, before full relative/domain
    # completion. No unowned common sign or relative combination is chosen.
    m_rows = [dict(raw_index=74+j, stored_classical=known[j],
                   native18_piece=native_constraints[j],
                   area_per_gamma=area_gradient[38+j].real,
                   d_induced_lapse=lapse_gradient[j]) for j in range(24)]
    gauss = []
    for radial in range(4):
        for c in range(4):
            j = radial*20+c
            wall = [port['wall_trace_map'][0][a][j] for a in range(4)]
            native_value = dot(wall, nv['gradient22'][2:6])
            # Original radial temporal basis: only its fourth member has
            # nonzero wall value. Interior and extra regular tests still exist.
            ck('temporal_wall_trace_' + str(side) + '_' + str(j),
               max(abs(wall[a] - float(radial == 3 and a == c)) for a in range(4)), 0)
            gauss.append(dict(raw_index=100+j, generator=c, radial_profile=radial,
                              stored_classical=raw['gradient'][268*side+100+j],
                              native18_piece=native_value, wall_generator_weights=wall))
    applications.append(dict(side=('incoming', 'outgoing')[side],
        normal_position=x[98], normal_velocity=x[99], induced_lapse=g['ell'].real,
        native_lapse_derivative=nv['gradient22'][1], area_density=rho,
        multiplier_rows=m_rows, temporal_gauge_rows=gauss,
        stored_classical_constraint_max=max(map(abs, known)),
        native18_constraint_piece_max=max(map(abs, native_constraints)),
        complete_initial_constraint_residual=None))

# Explicit polynomial coefficients for the retained canonical pair source.
# These are action coefficients of unknown independent left/right sections,
# not sampled or assigned physical columns. Ordering is L[weak,family,spin],
# e_R[family,spin]. No second Haar volume or electromagnetic coupling.
pauli = [[[0j, 1+0j], [1+0j, 0j]],
         [[0j, -1j], [1j, 0j]], [[1+0j, 0j], [0j, -1+0j]]]
Q = [[[0j]*18 for _ in range(18)] for _ in range(4)]
for c in range(3):
    for a in range(2):
        for b in range(2):
            for f in range(6):
                Q[c][6*a+f][6*b+f] = pauli[c][a][b]/(2*math.sqrt(2))
for i in range(18):
    Q[3][i][i] = (-.5 if i < 12 else -1.)/math.sqrt(10/3)

# Independent assembly from the original full-carrier current m*gamma0*Dt:
# m*gamma0*Dt = i*mu*I. After the owned canonical density normalization,
# its temporal gauge variation is i*G, whose W literal-dual restriction is Q.
# Build the sparse full-SM diagonal/weak slots, including conjugate e_c.
W = []
for weak in range(2):
    for family in range(3):
        for spin in range(2):
            W.append((family, 0, spin, 6+weak))
for family in range(3):
    for spin in range(2):
        W.append((family, 1, 2+spin, 14))
assert len(set(W)) == 18
for c in range(4):
    projected = [[0j]*18 for _ in range(18)]
    for i, (fi, ci, si, ai) in enumerate(W):
        for j, (fj, cj, sj, aj) in enumerate(W):
            if (fi, ci, si) != (fj, cj, sj):
                continue
            if c < 3 and ci == 0 and ai in (6, 7) and aj in (6, 7):
                projected[i][j] = pauli[c][ai-6][aj-6]/(2*math.sqrt(2))
            elif c == 3 and i == j:
                charge = -.5 if ci == 0 else -1.
                projected[i][j] = charge/math.sqrt(10/3)
    ck('independent_full_carrier_temporal_current_restriction_' + str(c),
       max(abs(Q[c][i][j]-projected[i][j]) for i in range(18) for j in range(18)), 0)

mix = [.5, .5, -.5, -.5]
sparse = []
for c in range(4):
    for col, weight in enumerate(mix):
        for i in range(18):
            for j in range(18):
                z = weight*Q[c][i][j]
                if z:
                    sparse.append(dict(generator=c, column=col, left_index=i,
                                       right_index=j, coefficient=[z.real, z.imag]))
# Polynomial differentiation preserves both ordered independent legs. Verify
# coefficient extraction, not an arbitrary physical trial state.
for c in range(4):
    for col, weight in enumerate(mix):
        terms = {(t['left_index'], t['right_index']): complex(*t['coefficient'])
                 for t in sparse if t['generator'] == c and t['column'] == col}
        ck('ordered_pair_source_coefficient_' + str(c) + '_' + str(col),
           max(abs(terms.get((i,j),0j)-weight*Q[c][i][j]) for i in range(18) for j in range(18)), 0)


# Preservation check: the compact replay must give the original application.
assert applications==d['expected_constraint_applications'],'Initial constraint application changed'
ck('exact_original_constraint_application_replayed',0,0)
eye=lambda n:[[complex(i==j) for j in range(n)] for i in range(n)]
sc=lambda c,a:[[c*x for x in row] for row in a]
add=lambda a,b:[[x+y for x,y in zip(r,s)] for r,s in zip(a,b)]
mm=lambda a,b:[[sum(x*y for x,y in zip(r,c)) for c in zip(*b)] for r in a]
adj=lambda a:[[x.conjugate() for x in col] for col in zip(*a)]
block=lambda a,b,c,d:[r+s for r,s in zip(a,b)]+[r+s for r,s in zip(c,d)]
err=lambda a,b:max(abs(x-y) for r,s in zip(a,b) for x,y in zip(r,s))
i2=eye(2);z2=sc(0,i2);i4=eye(4)
g0=block(z2,i2,i2,z2);gs=[block(z2,s,sc(-1,s),z2) for s in pauli]
g4=sc(-1,mm(mm(mm(g0,gs[0]),gs[1]),gs[2]))
alpha=[mm(g0,g4)]+[mm(g0,g) for g in gs]
for j,a in enumerate(alpha):
    ck('Dirac_Hermitian_alpha_'+str(j),err(a,adj(a)),0)
    for k,b in enumerate(alpha):
        ck('Dirac_Clifford_principal_'+str(j)+'_'+str(k),err(add(mm(a,b),mm(b,a)),sc(2 if j==k else 0,i4)),0)
cones=[]
for side,g in enumerate(d['dirac_germs']):
    N,C,R,z,mu=[g[k] for k in ('N','C','R','z','mu')]
    assert min(N,C,R,mu)>0
    v=N/C;va=N/R
    row=dict(side=('incoming','outgoing')[side],positive_time_weight=mu,
             radial_speeds=[-z-v,-z+v],angular_speed_coefficient=va)
    e=d['expected_dirac_applications'][side]
    ck('Dirac_preserved_cone_'+str(side),max(abs(row['radial_speeds'][i]-e['radial_characteristic_speeds'][i]) for i in range(2)),0)
    ck('Dirac_preserved_angular_'+str(side),abs(va-e['angular_speed_coefficient']),0)
    for j,b in enumerate([sc(mu,i4),sc(mu,add(sc(-z,i4),sc(v,alpha[0])))]+[sc(mu*va,a) for a in alpha[1:]]):
        ck('Dirac_current_principal_'+str(side)+'_'+str(j),err(b,adj(b)),0)
    cones.append(row)
for name,module in tuple(sys.modules.items()):
    f=getattr(module,'__file__',None)
    if f and name!='__main__':assert Path(f).resolve().is_relative_to(PREFIX),(name,f)
result=dict(schema='bhsm.portable-constraint-milestone-replay.v1',input_pins=INPUT_PINS,
    constraint_applications=applications,polarized_source_coefficients=sparse,
    source_pairing_scope='Real-base pair density uses its owned adjoint; independent Green/source dual is not assigned by conjugating the right source.',
    dirac_principal_components=cones,checks=checks,check_count=len(checks),
    max_error=max(c['error'] for c in checks),
    complete_constraint_residual=None,complete_event_Green_balance=None,
    physical_initial_state_admitted=False,formation_crossing_established=False,
    physical_a_mu=None,physical_g_mu=None,total_physical_uncertainty=None,
    native_heat_reintegrated=False,native_spectral_completion=False,
    physical_guard=2e-10,method_tolerance=2e-11,admitted_baseline='2^-9 temporal-only',
    history_solves=0,new_workers=0,git_mutations=False)
ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);args=ap.parse_args()
out=Path(args.out);out.mkdir(parents=True,exist_ok=False)
(out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8')
print(json.dumps(dict(checks=result['check_count'],max_error=result['max_error'],sha256=sha(out/'result.json'))))
