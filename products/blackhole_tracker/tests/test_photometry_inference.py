"""Invented correctness controls, not calibration/holdout seed streams."""
from copy import deepcopy
from fractions import Fraction
from decimal import Decimal, localcontext
import math
from itertools import product
from unittest.mock import patch
from types import SimpleNamespace

import numpy as np
import unittest

from bhtracker.observations import UnresolvedPhotometry
from bhtracker.photometry import predict_photometry
from bhtracker.photometry_inference import (_ProfiledModel, _synthetic_document,
    _search, _inverse_magnification_excess, _magnification_excess,
    _seed_peak_width, _seed_raw_peak_width, _null_peak_width_seeds,
    confidence_set_from_ordinates, monte_carlo_ordinate, profile_ordinate, rank_p_bounds)


def invented_data(two=False):
    times = np.r_[np.linspace(900,980,15),np.linspace(990,1030,30),np.linspace(1050,1160,20)]
    u2 = .3**2+((times-1010.)/25.)**2
    a = (u2+2)/np.sqrt(u2*(u2+4))
    values = 18.-2.5*np.log10(1+.65*(a-1))
    names = ["A","B"] if two else ["A"]
    instruments = {n:{"filter":"I","calibration":"WHOLLY INVENTED correctness control",
        "time":{"reference":"HJD","unit":"day","numeric_origin_jd":2450000.,"clock_scale":"UNSPECIFIED"}} for n in names}
    document = {"schema":"bhsm_unresolved_observations/1","observable":"apparent_magnitude",
        "common_numeric_origin_jd":2450000.,"metadata":{"synthetic":True},"sources":[],"transformations":[],
        "instruments":instruments,"rows":[]}
    for i,(time,value) in enumerate(zip(times,values)):
        name = names[i%len(names)]
        document["rows"].append({"source_row_id":f"INVENTED:{i}","instrument":name,"native_time":float(time),
            "magnitude":float(value+(0.4 if name=="B" else 0.)),"magnitude_error":.01+.001*(i%3),"quality_flags":[]})
    if two:
        document["metadata"]["relative_time_combination_assumption"] = "Invented same arithmetic clock only"
    return UnresolvedPhotometry(document)


def parameters(data,f=.65):
    return {"t0":1010.,"tE_days":25.,"u0":.3,"allow_negative_blend":False,
        "instruments":{n:{"baseline_magnitude":18.+(.4 if n=="B" else 0.),"source_fraction":f} for n in data.instruments}}


def observed_stub(data, statistic=.4):
    return {"statistic":statistic,"status":"PROFILE_ORDINATE_RESOLVED_FINITE_SEARCH",
        "null_constrained":{"parameters":parameters(data,.65)},"unrestricted":{"parameters":parameters(data,.9)},
        "physical_identification":{"mass_msun":None,"lens_distance_pc":None,"theta_E_mas":None,"pi_E":None}}


def test_01_exact_baseline_profile_is_weighted_projection():
    data = invented_data(two=True)
    model = _ProfiledModel(data)
    z = np.array([(1008.-model.base.center)/model.base.scale,np.log(30.),np.log(.4),.45,.75])
    x,_ = model.full_state(z)
    u2 = .4**2+((data.times-1008.)/30.)**2
    a = (u2+2)/np.sqrt(u2*(u2+4))
    for k,name in enumerate(data.instruments):
        select = data.instrument_indices==k
        f = z[3+k]
        d = -2.5*np.log10(1+f*(a[select]-1))
        w2 = 1/data.errors[select]**2
        expected = np.sum(w2*(data.magnitudes[select]-d))/np.sum(w2)
        assert abs(x[3+2*k]-expected)<3e-14
        r = model.evaluate(z)[select]
        assert abs(np.dot(r,1/data.errors[select]))<2e-8


def test_02_profiled_jacobian_matches_independent_finite_differences():
    model = _ProfiledModel(invented_data())
    z = np.array([(1009.-model.base.center)/model.base.scale,np.log(27.),np.log(.35),.6])
    analytic = model.evaluate(z,jac=True)
    numerical = np.column_stack([(model.evaluate(z+np.eye(len(z))[k]*1e-5)-model.evaluate(z-np.eye(len(z))[k]*1e-5))/(2e-5) for k in range(len(z))])
    np.testing.assert_allclose(analytic,numerical,rtol=2e-7,atol=3e-7)


def test_03_profile_nonlinear_ordinate_retains_correct_noiseless_state():
    data = invented_data()
    out = profile_ordinate(data,"tE_days",25.,starts=4,max_nfev=700)
    assert out["status"]=="PROFILE_ORDINATE_RESOLVED_FINITE_SEARCH"
    assert out["statistic"]<1e-10
    assert out["null_constrained"]["objective_chi_square"]<1e-14
    assert out["physical_identification"]["mass_msun"] is None
    assert out["global_optimality_certified"] is False


def test_04_fixed_rank_bounds_match_every_small_completion():
    for slots in range(1,8):
        for observed in range(slots+1):
            for bits in product((False,True),repeat=observed):
                exceed = sum(bits);unknown=slots-observed
                bounds = rank_p_bounds(exceed,unknown,slots,confidence_level=.75)
                possible = [Fraction(1+exceed+added,slots+1) for added in range(unknown+1)]
                if bounds["decision"]=="INCLUDED":
                    assert all(p>Fraction(1,4) for p in possible)
                elif bounds["decision"]=="EXCLUDED":
                    assert all(p<=Fraction(1,4) for p in possible)


def test_05_B199_exact_lazy_boundary_and_invalid_counts():
    assert rank_p_bounds(10,189)["decision"]=="INCLUDED"
    assert rank_p_bounds(9,0)["decision"]=="EXCLUDED"
    assert rank_p_bounds(9,190)["decision"]=="UNRESOLVED"
    for values in ((True,0,199),(0,-1,199),(1,199,199),(0,0,False)):
        with unittest.TestCase().assertRaises(ValueError):rank_p_bounds(*values)


def test_06_unresolved_observation_never_generates_or_refits():
    data = invented_data()
    with patch("bhtracker.photometry_inference.profile_ordinate",return_value=observed_stub(data,None)) as fitting, patch("bhtracker.photometry_inference._synthetic_document",side_effect=AssertionError("must not generate")):
        out = monte_carlo_ordinate(data,"tE_days",25.,entropy=[17],slots=199)
    assert fitting.call_count==1 and out["attempted_slots"]==0
    assert out["rank_bounds"]["decision"]=="UNRESOLVED"


def test_07_generation_uses_null_constrained_nuisance_not_global_MLE():
    data = invented_data()
    actual_means=[]
    def generator(parent,mean,seed,scale):
        actual_means.append(mean.copy());return parent
    with patch("bhtracker.photometry_inference.profile_ordinate",return_value=observed_stub(data)),patch("bhtracker.photometry_inference._synthetic_document",side_effect=generator):
        monte_carlo_ordinate(data,"tE_days",25.,entropy=[18],slots=1,lazy=False)
    np.testing.assert_array_equal(actual_means[0],predict_photometry(data,parameters(data,.65)))
    assert not np.allclose(actual_means[0],predict_photometry(data,parameters(data,.9)))


def test_08_audit_failure_latches_before_any_simulated_fit():
    data=invented_data()
    def failed_writer(*args):raise OSError("invented full journal")
    with patch("bhtracker.photometry_inference.profile_ordinate",return_value=observed_stub(data)) as fitting:
        out=monte_carlo_ordinate(data,"tE_days",25.,entropy=[19],slots=199,audit_callback=failed_writer)
    assert fitting.call_count==1 and out["attempted_slots"]==0
    assert out["audit_failure"] is not None
    assert out["slots"][0]["status"]=="NOT_ATTEMPTED_UNKNOWN"
    assert out["rank_bounds"]["decision"]=="UNRESOLVED" and out["rank_bounds"]["unknown"]==199


def test_09_lazy_inclusion_keeps_complete_fixed_seed_roster():
    data=invented_data();counter=[0]
    def fitting(*args,**kwargs):
        counter[0]+=1;return observed_stub(data,.4 if counter[0]==1 else .8)
    with patch("bhtracker.photometry_inference.profile_ordinate",side_effect=fitting),patch("bhtracker.photometry_inference._synthetic_document",return_value=data):
        out=monte_carlo_ordinate(data,"tE_days",25.,entropy=[20],slots=199)
    assert out["attempted_slots"]==10 and len(out["slots"])==199 and counter[0]==11
    assert out["rank_bounds"]["p_lower_fraction"]==[11,200]
    assert sum(r["status"]=="NOT_ATTEMPTED_UNKNOWN" for r in out["slots"])==189


def test_10_generated_lineage_preserves_parent_and_native_clock():
    data=invented_data();original=data.to_dict()
    generated=_synthetic_document(data,predict_photometry(data,parameters(data)),[21,1],1.)
    assert data.to_dict()==original
    np.testing.assert_array_equal(data.times,generated.times)
    np.testing.assert_array_equal(data.errors,generated.errors)
    assert generated.document["metadata"]["synthetic"] is True
    assert all(r["source_row_id"].startswith("SYNTHETIC:BOOTSTRAP:") for r in generated.rows)


def test_11_grid_retains_disconnected_unknown_components_and_no_fake_endpoints():
    rows=[]
    for x,state in [(1.,"INCLUDED"),(2.,"EXCLUDED"),(3.,"UNRESOLVED"),(4.,"EXCLUDED"),(5.,"INCLUDED")]:
        rows.append({"input_sha256":"INVENTED","parameter":"tE_days","confidence_level":.95,"kind":"INVENTED",
                     "value":x,"rank_bounds":{"decision":state}})
    out=confidence_set_from_ordinates(rows)
    assert len(out["components"])==3
    assert all(c["lower_endpoint"] is None and c["upper_endpoint"] is None for c in out["components"])
    assert out["finite_endpoints_available"] is False
    assert out["components"][1]["lower_endpoint_bracket"]==[2.,3.]


def test_12_time_origin_shift_and_row_permutation_preserve_profile_objective():
    data=invented_data();model=_ProfiledModel(data)
    z=np.array([(1011.-model.base.center)/model.base.scale,np.log(29.),np.log(.32),.61])
    reference=float(model.evaluate(z)@model.evaluate(z))
    document=data.to_dict();document["rows"].reverse()
    document["common_numeric_origin_jd"]=2400000.
    altered=UnresolvedPhotometry(document);other=_ProfiledModel(altered)
    other_z=z.copy();other_z[0]=((1011.+50000)-other.base.center)/other.base.scale
    assert abs(float(other.evaluate(other_z)@other.evaluate(other_z))-reference)<1e-8


def test_13_lower_finite_unresolved_trial_vetoes_higher_resolved_candidate():
    class Toy:
        lower=np.array([-1.]);upper=np.array([1.]);names=["x"]
        def __init__(self):self.base=self
        def seeds(self,n):return [np.array([0.]),np.array([.5])][:n]
        def full_state(self,x):return x,[]
        def decode(self,x):return {"x":float(x[0])}
        def evaluate(self,x,jac=False):
            return np.zeros((1,1)) if jac else np.array([1.+x[0]])
    solutions=iter([SimpleNamespace(x=np.array([0.]),success=False,status=0,message="invented limit",nfev=1),
                    SimpleNamespace(x=np.array([.5]),success=True,status=1,message="invented success",nfev=1)])
    with patch("bhtracker.photometry_inference.least_squares",side_effect=lambda *a,**kw:next(solutions)):
        out,state=_search(Toy(),starts=2,max_nfev=1)
    assert state is None and out["status"]=="LOWER_FEASIBLE_UNRESOLVED_TRIAL"
    assert out["lower_feasible_trial"]["objective_chi_square"]==1.
    assert out["best_resolved_candidate"]["objective_chi_square"]==2.25


def test_14_generated_child_omits_native_source_file_claims():
    data=invented_data();doc=data.to_dict()
    doc["sources"]=[{"filename":"ORIGINAL_NATIVE.dat","sha256":"parent_only"}]
    doc["metadata"]["native_brightness_claim"]="must not survive"
    doc["transformations"]=[{"operation":"ORIGINAL_NATIVE_PARSE"}]
    data=UnresolvedPhotometry(doc)
    generated=_synthetic_document(data,predict_photometry(data,parameters(data)),[22],1.)
    assert generated.document["sources"]==[]
    assert "native_brightness_claim" not in generated.document["metadata"]
    assert len(generated.document["transformations"])==1
    assert generated.document["transformations"][0]["original_source_files_embedded"] is False


def test_15_reference_polish_cannot_erase_lower_unresolved_initial_trial():
    data=invented_data()
    low={"objective_chi_square":1.,"resolved":False}
    high={"objective_chi_square":3.,"resolved":True}
    initial={"status":"LOWER_FEASIBLE_UNRESOLVED_TRIAL","objective_chi_square":None,"starts":[low,high]}
    null={"status":"LOCALLY_RESOLVED_FINITE_SEARCH","objective_chi_square":4.,"starts":[high],"parameters":parameters(data)}
    polish={"status":"LOCALLY_RESOLVED_FINITE_SEARCH","objective_chi_square":2.,"starts":[high],"parameters":parameters(data)}
    with patch("bhtracker.photometry_inference._search",side_effect=[(initial,None),(null,np.zeros(4)),(polish,np.zeros(4))]):
        out=profile_ordinate(data,"tE_days",25.,starts=1,max_nfev=1)
    assert out["statistic"] is None
    assert out["unrestricted"]["status"]=="LOWER_FEASIBLE_UNRESOLVED_REFERENCE_HISTORY"
    assert len(out["all_unrestricted_searches"])==2


def test_16_synthetic_child_preserves_explicit_multiband_clock_assumption():
    data=invented_data(two=True)
    generated=_synthetic_document(data,predict_photometry(data,parameters(data)),[23],1.)
    assert generated.document["metadata"]["relative_time_combination_assumption"]==data.document["metadata"]["relative_time_combination_assumption"]
    assert generated.document["instruments"]==data.document["instruments"]


def test_17_exact_cache_hits_return_copies_and_invalidate_on_state_change():
    model=_ProfiledModel(invented_data())
    z=np.array([(1011.-model.base.center)/model.base.scale,np.log(29.),np.log(.32),.61])
    with patch.object(model.base,"evaluate",wraps=model.base.evaluate) as evaluating:
        r=model.evaluate(z);j=model.evaluate(z,jac=True)
        original_r=r.copy();original_j=j.copy()
        r[0]+=100.;j[0,0]+=100.
        x,contacts=model.full_state(z);x[0]+=100.;contacts.append("invented mutation")
        np.testing.assert_array_equal(model.evaluate(z),original_r)
        np.testing.assert_array_equal(model.evaluate(z,jac=True),original_j)
        assert evaluating.call_count==3
        z[0]+=.1
        changed=model.evaluate(z)
        assert evaluating.call_count==5 and not np.array_equal(changed,original_r)
    with unittest.TestCase().assertRaises(ValueError):model.base.y[0]=999.
    with unittest.TestCase().assertRaises(ValueError):model.base.weights[0]=0.


def test_18_null_seeded_method_has_no_hidden_global_search():
    data=invented_data()
    null={"status":"LOCALLY_RESOLVED_FINITE_SEARCH","objective_chi_square":5.,"starts":[{"objective_chi_square":5.,"resolved":True}],"parameters":parameters(data)}
    refine={"status":"LOCALLY_RESOLVED_FINITE_SEARCH","objective_chi_square":2.,"starts":[{"objective_chi_square":2.,"resolved":True}],"parameters":parameters(data)}
    with patch("bhtracker.photometry_inference._search",side_effect=[(null,np.zeros(4)),(refine,np.zeros(4))]) as search:
        out=profile_ordinate(data,"tE_days",25.,starts=12,max_nfev=1,search_method="NULL12_FREE1")
    assert search.call_count==2 and "fixed" in search.call_args_list[0].kwargs
    assert search.call_args_list[1].kwargs["only_extra_seeds"] is True
    assert out["statistic"]==3. and len(out["all_unrestricted_searches"])==1


def test_19_observation_and_MC_use_identical_statistic_method():
    data=invented_data();methods=[]
    def fitting(*args,**kwargs):
        methods.append(kwargs["search_method"])
        return observed_stub(data,.4 if len(methods)==1 else .8)
    with patch("bhtracker.photometry_inference.profile_ordinate",side_effect=fitting),patch("bhtracker.photometry_inference._synthetic_document",return_value=data):
        out=monte_carlo_ordinate(data,"tE_days",25.,entropy=[24],slots=1,search_method="NULL12_FREE1")
    assert methods==["NULL12_FREE1","NULL12_FREE1"] and out["search_method"]=="NULL12_FREE1"


def test_20_null_seeded_and_full_methods_preserve_invented_noiseless_geometry():
    data=invented_data()
    first=profile_ordinate(data,"u0",.3,starts=4,max_nfev=700,search_method="FULL12_NULL12_POLISH1")
    second=profile_ordinate(data,"u0",.3,starts=4,max_nfev=700,search_method="NULL12_FREE1")
    assert first["statistic"]<1e-10 and second["statistic"]<1e-10
    assert abs(first["unrestricted"]["objective_chi_square"]-second["unrestricted"]["objective_chi_square"])<1e-12
    assert second["physical_identification"]["mass_msun"] is None


def test_21_stable_inverse_matches_independent_decimal_at_extreme_excess():
    with localcontext() as context:
        context.prec=90
        for excess in (1e-30,1e-12,.01,1.,1e6,1e200):
            d=Decimal.from_float(excess)
            root=(d*(d+2)).sqrt()
            expected=float((2/(root*(1+d+root))).sqrt())
            actual=_inverse_magnification_excess(excess)
            assert abs(actual/expected-1.)<8e-15
    for invalid in (0.,-1.,True,float("nan"),float("inf")):
        with unittest.TestCase().assertRaises(ValueError):_inverse_magnification_excess(invalid)


def test_22_inverse_forward_identity_and_halfwidth_monotonicity():
    impacts=np.geomspace(.0001,10.,101)
    widths=[]
    for u in impacts:
        excess=_magnification_excess(float(u))
        assert abs(_inverse_magnification_excess(excess)/u-1.)<2e-14
        other=_inverse_magnification_excess(.5*excess)
        widths.append(math.sqrt((other-u)*(other+u)))
    assert np.all(np.diff(widths)>0)


def test_23_data_summary_is_row_order_time_origin_and_magnitude_offset_invariant():
    data=invented_data();reference=_seed_peak_width(_ProfiledModel(data))
    assert reference["status"]=="DATA_ONLY_PEAK_WIDTH_SUMMARY"
    doc=data.to_dict();doc["rows"].reverse();doc["common_numeric_origin_jd"]=2400000.
    for row in doc["rows"]:row["magnitude"]+=7.
    other=_seed_peak_width(_ProfiledModel(UnresolvedPhotometry(doc)))
    assert abs(other["peak_time"]-reference["peak_time"]-50000)<1e-9
    assert abs(other["half_excess_width_days"]-reference["half_excess_width_days"])<1e-8
    assert abs(other["relative_peak_excess"]-reference["relative_peak_excess"])<2e-14
    assert abs(other["baseline_magnitude"]-reference["baseline_magnitude"]-7.)<1e-13


def exact_invented_peak_summary():
    # Independent high-precision analytic point, not supplied to a production fit.
    with localcontext() as context:
        context.prec=70
        u=Decimal(".3");u2=u*u
        excess=(u2+2)/(u*(u2+4).sqrt())-1
        half=excess/2
        other2=2*((1+half)/(half*(half+2)).sqrt()-1)
        width=25*(other2-u2).sqrt()
    return {"status":"DATA_ONLY_PEAK_WIDTH_SUMMARY","peak_time":1010.,
        "relative_peak_excess":float(Decimal(".65")*excess),
        "half_excess_width_days":float(width)}


def test_24_exact_null_peak_width_initializers_recover_invented_constraints():
    model=_ProfiledModel(invented_data());summary=exact_invented_peak_summary()
    for index,coordinate in ((1,math.log(25.)),(2,math.log(.3))):
        with patch("bhtracker.photometry_inference._seed_peak_width",return_value=summary):
            seeds,info=_null_peak_width_seeds(model,index,coordinate,12)
        assert len(seeds)==12 and info["status"]=="MATCHED8_PLUS_GENERIC4"
        assert not info["all_original_generic_seeds_used"]
        for seed in seeds:
            assert seed[index]==coordinate
            assert np.all(seed>=model.lower) and np.all(seed<=model.upper)
        assert abs(math.exp(seeds[0][1])-25.)<1e-9
        assert abs(math.exp(seeds[0][2])-.3)<1e-10
        assert abs(seeds[0][3]-.65)<1e-9


def test_25_constant_and_multiband_fallback_retain_all_original_seeds():
    doc=invented_data().to_dict()
    for row in doc["rows"]:row["magnitude"]=18.
    for data in (UnresolvedPhotometry(doc),invented_data(two=True)):
        model=_ProfiledModel(data);generic=model.seeds(12)
        seeds,info=_null_peak_width_seeds(model,1,math.log(25.),12)
        assert info["all_original_generic_seeds_used"] is True
        assert len(seeds)==12
        for a,b in zip(seeds,generic):np.testing.assert_array_equal(a,b)
    with unittest.TestCase().assertRaises(ValueError):_null_peak_width_seeds(model,1,math.log(25.),4)


def test_26_multipeak_and_unbracketed_summaries_have_explicit_fallback():
    doc=invented_data().to_dict();doc["rows"]=[]
    for i,t in enumerate(np.linspace(0,100,401)):
        m=18.-np.exp(-.5*((t-25.)/3.)**2)-np.exp(-.5*((t-75.)/3.)**2)
        doc["rows"].append({"source_row_id":f"INVENTED:DOUBLE:{i}","instrument":"A","native_time":float(t),"magnitude":float(m),"magnitude_error":.01,"quality_flags":[]})
    summary=_seed_peak_width(_ProfiledModel(UnresolvedPhotometry(doc)))
    assert summary["reason"]=="MULTIPLE_SUBSTANTIAL_BRIGHTENING_REGIONS"
    doc["rows"]=[r for r in doc["rows"] if r["native_time"]<25]
    summary=_seed_peak_width(_ProfiledModel(UnresolvedPhotometry(doc)))
    assert summary["status"]=="GENERIC_FALLBACK"


def test_27_outside_width_domain_falls_back_without_root_clamping():
    model=_ProfiledModel(invented_data());summary=exact_invented_peak_summary()
    summary["half_excess_width_days"]=1e10
    with patch("bhtracker.photometry_inference._seed_peak_width",return_value=summary):
        seeds,info=_null_peak_width_seeds(model,1,math.log(25.),12)
    assert info["all_original_generic_seeds_used"] and len(seeds)==12
    assert info["reason"]=="NO_SUPPORTED_PHYSICAL_PEAK_WIDTH_INVERSE"


def test_28_seed_policy_is_identical_observation_and_monte_carlo():
    data=invented_data();policies=[]
    def fitting(*args,**kwargs):
        policies.append(kwargs["seed_policy"])
        return observed_stub(data,.4 if len(policies)==1 else .8)
    with patch("bhtracker.photometry_inference.profile_ordinate",side_effect=fitting),patch("bhtracker.photometry_inference._synthetic_document",return_value=data):
        out=monte_carlo_ordinate(data,"tE_days",25.,entropy=[25],slots=1,search_method="NULL12_FREE1",seed_policy="NULL_PEAK_WIDTH12_V1")
    assert policies==["NULL_PEAK_WIDTH12_V1"]*2 and out["seed_policy"]=="NULL_PEAK_WIDTH12_V1"


def test_29_new_policy_preserves_native_objective_and_physical_nulls():
    data=invented_data();before=data.to_dict()
    out=profile_ordinate(data,"u0",.3,starts=12,max_nfev=700,search_method="NULL12_FREE1",seed_policy="NULL_PEAK_WIDTH12_V1")
    assert out["statistic"] is not None and out["statistic"]<1e-10
    assert len(out["null_constrained"]["starts"])==12
    assert len(out["unrestricted"]["starts"])==1
    assert data.to_dict()==before
    assert all(v is None for v in out["physical_identification"].values())


def test_30_repeated_time_and_nonphysical_signal_remain_supported_generic_searches():
    doc=invented_data().to_dict();doc["rows"][1]["native_time"]=doc["rows"][0]["native_time"]
    model=_ProfiledModel(UnresolvedPhotometry(doc))
    assert _seed_peak_width(model)["reason"]=="REPEATED_TIME_SUMMARY_UNSUPPORTED"
    seeds,info=_null_peak_width_seeds(model,2,math.log(.3),12)
    assert len(seeds)==12 and info["all_original_generic_seeds_used"]


def sparse_invented_data():
    doc=invented_data().to_dict();doc["rows"]=[]
    times=np.unique(np.r_[np.linspace(-400,-100,35),[-50,-32,-20,-12,-5,4,17,23,31,38,45,60,80],np.linspace(100,400,35)])
    for i,t in enumerate(times):
        u2=.3**2+(t/25.)**2
        a=(u2+2)/math.sqrt(u2*(u2+4))
        value=18.-2.5*math.log10(1+.65*(a-1))
        doc["rows"].append({"source_row_id":f"INVENTED:SPARSE:{i}","instrument":"A","native_time":float(t),"magnitude":value,"magnitude_error":.02,"quality_flags":[]})
    return UnresolvedPhotometry(doc)


def test_31_sparse_native_summary_avoids_five_row_temporal_peak_erasure():
    model=_ProfiledModel(sparse_invented_data())
    raw=_seed_raw_peak_width(model);median=_seed_peak_width(model)
    assert raw["status"]==median["status"]=="DATA_ONLY_PEAK_WIDTH_SUMMARY"
    assert raw["peak_magnitude"]<median["peak_magnitude"]-.2
    assert raw["half_excess_width_days"]<median["half_excess_width_days"]
    seeds,info=_null_peak_width_seeds(model,1,math.log(25.),12,summary_policy="RAW_FIRST_V1")
    assert len(seeds)==12 and info["status"]=="MATCHED8_PLUS_GENERIC4"
    assert info["summary"]["summary_policy"]=="RAW_PEAK_V1"


def test_32_isolated_spike_and_weak_noisy_peak_use_declared_fallback():
    doc=sparse_invented_data().to_dict()
    for row in doc["rows"]:row["magnitude"]=18.
    doc["rows"][40]["magnitude"]=16.
    model=_ProfiledModel(UnresolvedPhotometry(doc))
    assert _seed_raw_peak_width(model)["reason"]=="ISOLATED_NATIVE_PEAK_UNSUPPORTED"
    seeds,info=_null_peak_width_seeds(model,1,math.log(25.),12,summary_policy="RAW_FIRST_V1")
    assert len(seeds)==12 and info["all_original_generic_seeds_used"]
    doc["rows"][40]["magnitude"]=17.95
    assert _seed_raw_peak_width(_ProfiledModel(UnresolvedPhotometry(doc)))["reason"]=="WEAK_OR_NONBRIGHTENING_NATIVE_PEAK"


def test_33_raw_multiple_peaks_and_unbracketed_peak_remain_unclassified():
    doc=sparse_invented_data().to_dict();doc["rows"]=[]
    for i,t in enumerate(np.linspace(0,100,401)):
        value=18.-math.exp(-.5*((t-25)/3)**2)-math.exp(-.5*((t-75)/3)**2)
        doc["rows"].append({"source_row_id":f"INVENTED:DOUBLE:{i}","instrument":"A","native_time":float(t),"magnitude":value,"magnitude_error":.01,"quality_flags":[]})
    assert _seed_raw_peak_width(_ProfiledModel(UnresolvedPhotometry(doc)))["reason"]=="MULTIPLE_SUPPORTED_NATIVE_BRIGHTENING_REGIONS"
    doc["rows"]=[r for r in doc["rows"] if r["native_time"]<25]
    assert _seed_raw_peak_width(_ProfiledModel(UnresolvedPhotometry(doc)))["reason"]=="NATIVE_HALF_EXCESS_NOT_BRACKETED"


def test_34_raw_summary_invariance_uses_peak_sigma_and_preserves_all_rows():
    data=sparse_invented_data();before=data.to_dict();raw=_seed_raw_peak_width(_ProfiledModel(data))
    doc=data.to_dict();doc["rows"].reverse();doc["common_numeric_origin_jd"]=2400000.
    for row in doc["rows"]:row["magnitude"]+=4.
    other=_seed_raw_peak_width(_ProfiledModel(UnresolvedPhotometry(doc)))
    assert abs(other["peak_time"]-raw["peak_time"]-50000)<1e-9
    assert abs(other["half_excess_width_days"]-raw["half_excess_width_days"])<1e-8
    assert abs(other["relative_peak_excess"]-raw["relative_peak_excess"])<2e-14
    assert other["peak_magnitude_error"]==raw["peak_magnitude_error"]==.02
    assert data.to_dict()==before


def test_35_sparse_noiseless_native_objective_resolves_without_truth_seeds():
    data=sparse_invented_data();before=data.to_dict()
    out=profile_ordinate(data,"tE_days",25.,starts=12,max_nfev=800,search_method="NULL12_FREE1",seed_policy="NULL_RAW_PEAK_WIDTH12_V1")
    assert out["statistic"] is not None and out["statistic"]<1e-10
    assert len(out["null_constrained"]["starts"])==12
    assert out["seed_initialization"]["summary"]["summary_policy"]=="RAW_PEAK_V1"
    assert data.to_dict()==before and all(v is None for v in out["physical_identification"].values())


def test_36_raw_policy_is_symmetric_for_observation_and_every_MC_child():
    data=invented_data();policies=[]
    def fitting(*args,**kwargs):
        policies.append(kwargs["seed_policy"])
        return observed_stub(data,.4 if len(policies)==1 else .8)
    with patch("bhtracker.photometry_inference.profile_ordinate",side_effect=fitting),patch("bhtracker.photometry_inference._synthetic_document",return_value=data):
        out=monte_carlo_ordinate(data,"tE_days",25.,entropy=[26],slots=1,search_method="NULL12_FREE1",seed_policy="NULL_RAW_PEAK_WIDTH12_V1")
    assert policies==["NULL_RAW_PEAK_WIDTH12_V1"]*2 and out["seed_policy"]=="NULL_RAW_PEAK_WIDTH12_V1"


def test_37_inadmissible_raw_width_tries_existing_median_before_generic():
    model=_ProfiledModel(invented_data());raw=exact_invented_peak_summary();raw["half_excess_width_days"]=1e10
    median=exact_invented_peak_summary()
    with patch("bhtracker.photometry_inference._seed_raw_peak_width",return_value=raw),patch("bhtracker.photometry_inference._seed_peak_width",return_value=median):
        seeds,info=_null_peak_width_seeds(model,1,math.log(25.),12,summary_policy="RAW_FIRST_V1")
    assert len(seeds)==12 and info["status"]=="MATCHED8_PLUS_GENERIC4"
    assert info["raw_geometry_failure"]=="NO_SUPPORTED_PHYSICAL_RAW_PEAK_WIDTH_INVERSE"


def test_38_observed_profile_commits_before_any_simulation_or_simulated_fit():
    data=invented_data();stages=[];events=[]
    def fitting(*a,**kw):
        events.append("FIT")
        return observed_stub(data,.4 if len(events)==1 else .8)
    def audit(stage,slot,payload):stages.append((stage,slot));events.append(stage)
    with patch("bhtracker.photometry_inference.profile_ordinate",side_effect=fitting),patch("bhtracker.photometry_inference._synthetic_document",return_value=data):
        out=monte_carlo_ordinate(data,"tE_days",25.,entropy=[27],slots=1,audit_callback=audit)
    assert stages==[("OBSERVED_PROFILE",-1),("GENERATED",0),("FITTED",0)]
    assert events==["FIT","OBSERVED_PROFILE","GENERATED","FIT","FITTED"]
    assert out["audit_failure"] is None


def test_39_failed_simulated_stage_stops_every_later_fit_and_draw():
    data=invented_data()
    def audit(stage,slot,payload):
        if stage=="FITTED":raise OSError("invented committed-stage acknowledgement failure")
    with patch("bhtracker.photometry_inference.profile_ordinate",return_value=observed_stub(data)) as fitting,patch("bhtracker.photometry_inference._synthetic_document",return_value=data) as generation:
        out=monte_carlo_ordinate(data,"tE_days",25.,entropy=[28],slots=199,audit_callback=audit)
    assert fitting.call_count==2 and generation.call_count==1
    assert out["rank_bounds"]["decision"]=="UNRESOLVED" and out["rank_bounds"]["unknown"]==199
    assert out["attempted_slots"]==1 and out["slots"][0]["status"]=="AUDIT_FAILURE_UNKNOWN"
