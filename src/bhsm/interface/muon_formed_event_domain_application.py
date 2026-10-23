"""Actual E1 interacting seam NUMERATORS and local frame incidence.

The two eta collars live on each history separately.  Their temporal
frame intertwiners are different.  No normal-mode value is assigned, and
this numerator application supplies neither a formed mode, occupation,
nor global reset history.
"""
from __future__ import annotations
import numpy as np

from .muon_full_d5_localized_lepton_trace import (
    full_d5_localized_lepton_trace, moving_d5_material_trace_frame,
)
from .muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
from .muon_continued_action_reality import _higgs_mass_realified
from .muon_adopted_incoming_reference import static_field_maps
from .muon_parent_retarded_hypercharge import WALL
from .muon_parent_maxwell_full_weak import M, _curl_bracket
from .muon_native_product_factor_graph import lepton_unit_trace_gauge_representation
from .muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation


def _finite_real(value, shape, name):
    a = np.asarray(value)
    if a.shape != shape or not np.isrealobj(a) or not np.isfinite(a).all():
        raise ValueError('finite real '+name+' required with shape '+str(shape))
    return a.astype(float)


def _product(a, b):
    return a[0]@b[0], a[1]@b[0]+a[0]@b[1]


def _constant(a):
    a = np.asarray(a, complex)
    return a, np.zeros_like(a)


def _maximum(a):
    return float(np.max(abs(a)))


def endpoint_seam_numerator(raw, coordinate_rate):
    """Execute J Nhat=C_hat (rho M_Y) B_hat and its actual time jet.

    Hats retain every independent u_L/u_R inverse factor symbolically.
    They are not the physical choice u_L=u_R=1.  The column application
    Nhat Ehat uses all eighteen action-owned coefficient generators and
    retains its full384 off-mode complement.
    """
    x = _finite_real(raw, (268,), 'original raw268')
    xt = _finite_real(coordinate_rate, (268,), 'original coordinate rate268')
    f = full_d5_localized_lepton_trace()
    W, D = f['localized_lepton18_trace_lift'], f['localized_lepton18_literal_dual']
    G0 = np.kron(np.eye(3), f['gamma5D_self_dual128'][0])
    PL = np.diag(np.r_[np.ones(12), np.zeros(6)])
    PR = np.eye(18)-PL
    weight = intrinsic_m4_weight_jet(12, x[:37], x[37:74], x[74:98],
        source_value=x[98], source_rate=x[99])
    U = weight['U']; rho = weight['induced_lapse']*weight['R4']**3
    udot = float(U.gradient@xt[:100]); rhodot = float(rho.gradient@xt[:100])
    frame = {}
    for side, eps in (('plus', 1), ('minus', -1)):
        a = moving_d5_material_trace_frame(-eps*U.value, -eps*udot,
            full_representation=f)
        lift = lambda key: np.kron(np.eye(3), a[key])
        frame[side] = dict(
            S=(lift('spin_boost128'), lift('spin_boost_first128')),
            SI=(lift('spin_boost_inverse128'), lift('spin_boost_inverse_first128')),
            GN=(eps*lift('unit_normal_Clifford128'),
                eps*lift('unit_normal_Clifford_first128')),
            spin_boost128=a['spin_boost128'],
            spin_boost_time128=a['spin_boost_first128'])
    p, m = frame['plus'], frame['minus']
    geo = _product(m['S'], p['SI'])
    geoi = _product(p['S'], m['SI'])
    leftgeo = _product(_product(_constant(G0), geoi), _constant(G0))
    bp = _product(_constant(D), p['SI'])
    bm = _product(_constant(D), m['SI'])
    cp = _product(_product(_product(_constant(G0), p['S']), _constant(G0)), _constant(W))
    cm = _product(_product(_product(_constant(G0), m['S']), _constant(G0)), _constant(W))
    leftb = _product(_constant(PL), bp)
    rightb = _product(_product(_constant(PR), bm), geo)
    Bhat = tuple(a+b for a,b in zip(leftb,rightb))
    leftc = _product(cp, _constant(PL))
    rightc = _product(_product(leftgeo,cm), _constant(PR))
    Chat = tuple(a+b for a,b in zip(leftc,rightc))
    jp = (1j*rho.value*G0@p['GN'][0],
        1j*G0@(rhodot*p['GN'][0]+rho.value*p['GN'][1]))
    jm = (1j*rho.value*G0@m['GN'][0],
        1j*G0@(rhodot*m['GN'][0]+rho.value*m['GN'][1]))
    mass = _higgs_mass_realified(x[260:264])
    massdot = _higgs_mass_realified(xt[260:264])
    T = rho.value*mass, rhodot*mass+rho.value*massdot
    JC = np.linalg.solve(jp[0], Chat[0])
    JCt = np.linalg.solve(jp[0], Chat[1]-jp[1]@JC)
    Nhat = _product(_product((JC,JCt), T), Bhat)
    Ehat = _product(p['S'], _constant(W))
    image = _product(Nhat, Ehat)
    weak = tuple(a-b for a,b in zip(_product(jp,Nhat),_product(_product(Chat,T),Bhat)))
    isotropy = _product(Bhat,(JC,JCt))
    nilpotence = _product(Nhat,Nhat)
    trace_image = _product(Bhat,image)
    adapted_image = _product(p['SI'],image)
    complement = _product(_constant(f['full_retained_complement']),adapted_image)
    domain_complement = _product(_constant(np.eye(384)-W@D),adapted_image)
    channels = {}
    for name, left, right in (('LR',PL,PR),('RL',PR,PL)):
        t = _product(_product(_constant(left),T),_constant(right))
        n = _product(_product((JC,JCt),t),Bhat)
        e = _product(n,Ehat)
        adapted = _product(p['SI'],e)
        channels[name] = dict(Nhat=n,image=e,
            domain_complement_image=_product(_constant(np.eye(384)-W@D),adapted),
            retained36_complement_image=_product(_constant(f['full_retained_complement']),adapted),
            original_weak_rows=tuple(a-b for a,b in zip(_product(jp,n),_product(_product(Chat,t),Bhat))),
            selected_trace_rows=_product(Bhat,n))
    # The family order is supplied by the action owner, heavy,middle,light.
    # Both charged weak-L spin entries and both e_R spin entries are retained.
    middle = np.zeros((18,18));middle[[8,9,14,15],[8,9,14,15]]=1.
    singular_values=np.linalg.svd(domain_complement[0],compute_uv=False)
    middle_singular_values=np.linalg.svd(domain_complement[0]@middle,compute_uv=False)
    rank_tol=float(singular_values[0]*1e-12)
    green = tuple(a+b for a,b in zip(jp,_product(_product(leftgeo,jm),geo)))
    channel_nilpotence = {}
    for left in ('LR','RL'):
        for right in ('LR','RL'):
            product=_product(channels[left]['Nhat'],channels[right]['Nhat'])
            channel_nilpotence[left+'_'+right]=dict(value_max=_maximum(product[0]),
                coordinate_time_max=_maximum(product[1]))
    return dict(raw268=x, raw_coordinate_time_derivative268=xt,
        velocity=float(U.value), velocity_time=udot,
        surface_density=float(rho.value), surface_density_time=rhodot,
        R4=float(weight['R4'].value), induced_lapse=float(weight['induced_lapse'].value),
        Cauchy_density_factor=float(weight['R4'].value**1.5),
        frames=frame, geometric_right=geo, Nhat=Nhat, Bhat=Bhat,
        Ehat=Ehat, image=image, complement_image=complement,
        domain_complement_image=domain_complement,channels=channels,
        domain_complement_singular_values=singular_values,
        middle_charged_projector18=middle,
        middle_charged_forcing_singular_values=middle_singular_values,
        forcing_numerical_rank=int(np.sum(singular_values>rank_tol)),
        middle_charged_forcing_numerical_rank=int(np.sum(middle_singular_values>rank_tol)),
        forcing_rank_absolute_threshold=rank_tol,
        independent_channel_nilpotence=channel_nilpotence,
        original_weak_rows=weak, isotropy_rows=isotropy,
        nilpotence_rows=nilpotence, selected_trace_image_rows=trace_image,
        geometric_green_rows=green,
        free_hard_graph_defect=_product(_product(Chat,T),Bhat),
        normal_mode_values_assigned=False,
        normal_factor_rule='LR:1/(u_L_plus*u_R_minus); RL:1/(u_L_minus*u_R_plus), with independent total derivatives',
        temporal_scope='one-sided coordinate derivative of the actual saved provisional history germ')


def event_frame_incidence(incoming, outgoing):
    """Execute local E1 numerator diagrams, retaining both eta boosts.

    Spatial gauge tests below use independent plus OWN mechanical wall
    fields. A child inherited image must be separately checked before
    promoting those tests to a total outgoing connection statement.
    """
    transforms = {}
    for side in ('plus','minus'):
        transforms[side] = _product(outgoing['frames'][side]['S'],incoming['frames'][side]['SI'])
    tp, tm = transforms['plus'], transforms['minus']
    graph = tuple(a-b for a,b in zip(
        _product(outgoing['geometric_right'],tp),
        _product(tm,incoming['geometric_right'])))
    trace = tuple(a-b for a,b in zip(_product(outgoing['Bhat'],tp),incoming['Bhat']))
    seam = tuple(a-b for a,b in zip(_product(outgoing['Nhat'],tp),_product(tp,incoming['Nhat'])))
    gauge = lepton_unit_trace_gauge_representation()['generators']
    hg = higgs_u2_real_representation()['real_generators']
    wallmap = static_field_maps(np.array([WALL]))[0][0].reshape(5,4,80)
    fields = []
    from .muon_continued_action_reality import _geometry
    for a in (incoming,outgoing):
        x = a['raw268']; A = np.einsum('acj,j->ac',wallmap,x[100:180])
        A[2:] += M*(_geometry(x)['mechanical_lambda'].real-1)
        F = 2*A[2:]+.5*_curl_bracket(A[2:],A[2:])
        fields.append((A,F))
    A,F = fields[0]
    Fmat = np.einsum('ac,cij->aij',F,gauge)
    stabilizer = np.column_stack([np.r_[
        np.array([f@g-g@f for f in Fmat]).reshape(-1),
        hg[k]@incoming['raw268'][260:264]] for k,g in enumerate(gauge)])
    return dict(plus_boost=tp, minus_boost=tm,
        geometric_intertwining_rows=graph, selected_numerator_intertwining_rows=trace,
        interacting_seam_intertwining_rows=seam,
        incoming_independent_plus_own_wall_connection=A,
        outgoing_independent_plus_own_wall_connection=fields[1][0],
        incoming_homogeneous_spatial_curvature=F,
        outgoing_homogeneous_spatial_curvature=fields[1][1],
        spatial_SU2_curvature_singular_values=np.linalg.svd(F[:,:3],compute_uv=False),
        simultaneous_curvature_H_stabilizer_singular_values=np.linalg.svd(stabilizer,compute_uv=False),
        simultaneous_curvature_H_stabilizer_rank=int(np.linalg.matrix_rank(stabilizer)),
        Cauchy_density_ratio=outgoing['Cauchy_density_factor']/incoming['Cauchy_density_factor'],
        normalized_right_trace_rule='b_out T_plus E_in=(u_R_in/u_R_out) I18; ratio remains uncomputed',
        normalized_left_trace_rule='independent u_L incidence and its jets remain uncomputed',
        paired_jet_scope='formal product-direction contact of two independently supplied one-sided germs; no common physical event-flow derivative is established',
        gauge_scope='local homogeneous spatial independent+own-mechanical connection; outgoing inherited image, temporal derivative gauge incidence and global topology remain explicit',
        gauge_center_rule='CONDITIONAL LEMMA: if full spatial curvature is equal and the intertwiner is admissible, rank3 SU2 curvature forces SU2 center; matched nonzero H fixes hypercharge phase; this discrete center is invisible on L(Y=-1/2),e_R(Y=-1)',
        common_spin_sign_rule='common +/- spin lift cancels in operator conjugations, but no global coherent section/FR history is reconstructed')


def endpoint_checks(application):
    """Small report of original equations and non-null operands."""
    result = {name:dict(value_max=_maximum(application[name][0]),
        coordinate_time_max=_maximum(application[name][1])) for name in (
            'original_weak_rows','isotropy_rows','nilpotence_rows',
            'selected_trace_image_rows','geometric_green_rows')}
    channels={name:dict(original_weak_value_max=_maximum(a['original_weak_rows'][0]),
        original_weak_time_max=_maximum(a['original_weak_rows'][1]),
        selected_trace_value_max=_maximum(a['selected_trace_rows'][0]),
        selected_trace_time_max=_maximum(a['selected_trace_rows'][1]),
        image_norm=float(np.linalg.norm(a['image'][0])),
        domain_complement_forcing_norm=float(np.linalg.norm(a['domain_complement_image'][0])))
        for name,a in application['channels'].items()}
    result.update(image_norm=float(np.linalg.norm(application['image'][0])),
        image_time_norm=float(np.linalg.norm(application['image'][1])),
        adapted_retained_complement_norm=float(np.linalg.norm(application['complement_image'][0])),
        adapted_selected18_domain_complement_norm=float(np.linalg.norm(application['domain_complement_image'][0])),
        free_hard_graph_defect_norm=float(np.linalg.norm(application['free_hard_graph_defect'][0])),
        channel_coefficients=channels,
        forcing_numerical_rank=application['forcing_numerical_rank'],
        middle_charged_forcing_numerical_rank=application['middle_charged_forcing_numerical_rank'])
    result['independent_channel_nilpotence']=application['independent_channel_nilpotence']
    return result
