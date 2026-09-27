"""Sector sum, common canonical response and conditional Schur tests."""
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
from flint import arb,arb_mat,ctx

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'src')]
from certify_n12_gate7_coupled_center_neighborhood import load
from bhsm.interface.sector_on_shell_response import shared_sector_response
from bhsm.interface.moving_seam_response import on_shell_reaction_jet
import derive_n12_gate7_parent_sector_jets as s

OUT=ROOT/'artifacts/flagship_integration/gate7_parent_sectors_20260927'


def packet():
    ctx.prec=512
    return json.loads((OUT/'report.json').read_bytes()),load(OUT/'arrays.npz')


def zero(x):return all(v.contains(0) for v in x.entries())


def test_signed_sector_gradients_and_hessians_replay_owned_total():
    report,a=packet()
    G=sum((s.r.mat(a[n+'_gradient']) for n in s.NAMES),arb_mat(98,1))
    H=sum((s.r.mat(a[n+'_hessian']) for n in s.NAMES),arb_mat(98,98))
    assert zero(G-s.r.mat(a['gradient_owner']))
    assert zero(H-s.r.mat(a['hessian_owner']))
    assert report['replay']['hessian']['approximate_upper']<1e-120


def test_native_response_is_five_rows_and_same_canonical_lift():
    report,a=packet()
    assert report['native_response_shape']==[5,98]
    assert report['same_total_canonical_lift_for_all_sectors']
    assert not report['independent_sector_inverse_used']
    assert report['replay']['canonical_inverse']['approximate_upper']<1
    native=s.r.mat(a['native_trace_momentum_jet'])
    summed=sum((s.r.mat(a[n+'_momentum_jet']) for n in s.NAMES),arb_mat(2,98))
    assert zero(summed-s.block(native,[3,4],range(98)))
    assert report['replay']['momentum_derivative']['approximate_upper']<1e-120
    # Only ADM has velocity dependence in this retained Lagrangian.
    # Other terms still affect force/constraints; zero here does not remove them.
    for n in s.NAMES:
        if n!='adm_kinetic':assert zero(s.r.mat(a[n+'_momentum_jet']))


def test_casimir_species_split_preserves_frozen_coefficient():
    report,a=packet()
    shares=(arb(1)/118,arb(33)/59,arb(51)/118)
    assert (sum(shares,arb(0))-1).contains(0)
    g=[s.r.mat(a[n+'_gradient']) for n in s.NAMES[7:]]
    assert zero(g[1]-66*g[0]) and zero(g[2]-51*g[0])
    assert report['sector_split_is_algebraic_not_independent_energy_decomposition']


def test_common_schur_keeps_cross_sector_coupling():
    ctx.prec=256;m=lambda v:arb_mat([[v]])
    # Sector A has singular interior Hessian; the sum is regular.
    # Independent per-sector inverses would fail and are not permissible.
    A=dict(ii=m(0),iq=m(2),iSigma=m(1),qi=m(2),qq=m(3),qSigma=m(4))
    B=dict(ii=m(2),iq=m(-1),iSigma=m(2),qi=m(-1),qq=m(5),qSigma=m(-2))
    pieces,total,interior=shared_sector_response({'A':A,'B':B},m(4),m(2))
    expected,delta=on_shell_reaction_jet(m(2),m(1),m(3),m(1),m(8),m(2),m(4),m(2))
    assert zero(total-expected) and zero(interior-delta)
    assert total==m(31) and pieces['A']==m(10) and pieces['B']==m(21)


def test_point_packet_does_not_claim_seam_or_dynamic_flux_authority():
    report,a=packet()
    assert report['point_key']=='center_state[:98]'
    assert not report['environment_response_7x73_derived']
    assert not report['on_shell_environment_Hessian_derived']
    assert len(report['missing_for_7x73'])==2
    assert report['environment_physical_inputs']==0
    assert not report['Gate7_closed'] and not report['FULL_BHSM_COMPLETE']
    with np.load(s.SOURCE) as z:
        assert all(a['parent_center'][i].contains(arb(float(z['center_state'][i]))) for i in range(98))


def test_frozen_sources_and_independent_reproduction():
    report,_=packet();h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest().upper()
    assert h(OUT/'arrays.npz')==report['arrays_SHA256']
    for p,sha in report['source_SHA256'].items():assert h(Path(p))==sha
    receipt=json.loads((OUT/'reproduction.json').read_bytes())
    for name,item in receipt['files'].items():
        assert item['byte_identical'] and h(OUT/name)==item['SHA256']
