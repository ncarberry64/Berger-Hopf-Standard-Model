"""Versioned nonregular native-magnitude PSPL inference.

This adds a finite-search profile/Monte Carlo route. It leaves the v1 optical
mean, native Gaussian law, bounds and local-error result unchanged. A fitted
photometric imprint is interpreted through the same single BHSM exterior; it
does not identify mass, distance, angular motion, core or horizon.
"""
from copy import deepcopy
from fractions import Fraction
import hashlib
import json
import math

import numpy as np
from scipy.optimize import least_squares, brentq

from .observations import UnresolvedPhotometry
from .photometry import FIT_PROTOCOL, _Model, _dataset, predict_photometry

SCHEMA = "bhsm_native_photometry_inference/2"
PROTOCOL = {
    "id": "BHSM-native-magnitude-nonregular-inference-v2-development",
    "observation_law": "unchanged independent Gaussian native apparent magnitudes",
    "optical_model": "unchanged rectilinear image-summed PSPL; one BHSM exterior",
    "baseline_profile": "exact weighted linear minimum within unchanged baseline bounds",
    "nonlinear_search": "v1 deterministic seeds; analytic profiled Jacobian; every outcome retained",
    "projected_score_tolerance": 1e-4,
    "reference_objective_tolerance": 1e-5,
    "reference_relative_tolerance": 1e-10,
    "confidence_level": .95,
    "rank_test": "p=(1+number[simulated statistic>=observed statistic])/(B+1); reject p<=alpha",
    "default_bootstrap_slots": 199,
    "lazy_bounds": "fixed denominator/seed roster; failed and unattempted comparisons remain unknown",
    "known_null": "exact rank validity only for completely specified same-law null and fixed algorithm",
    "estimated_nuisance": "null-constrained plug-in bootstrap is approximate; independent coverage required",
    "confidence_claim": False,
}


def _positive_integer(value, name):
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(name + " must be a positive integer")


def _finite_number(value, name):
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, float, np.integer, np.floating)) or not math.isfinite(float(value)):
        raise ValueError(name + " must be a finite number")
    return float(value)


def rank_p_bounds(exceedances, unknown, slots=199, *, confidence_level=.95):
    """Fixed-roster conservative bounds, using exact integer/rational decisions.

Unknown includes failed and unattempted slots. The caller must justify every
counted exceedance/nonexceedance; unknowns are never silently counted as zero.
"""
    _positive_integer(slots, "slots")
    for value, name in ((exceedances, "exceedances"), (unknown, "unknown")):
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(name + " must be a nonnegative integer")
    if exceedances + unknown > slots:
        raise ValueError("exceedance/unknown counts exceed the fixed roster")
    level = Fraction(str(_finite_number(confidence_level, "confidence_level")))
    if not 0 < level < 1:
        raise ValueError("confidence level must lie strictly between zero and one")
    alpha = 1-level
    lower = Fraction(1+exceedances, slots+1)
    upper = Fraction(1+exceedances+unknown, slots+1)
    decision = "INCLUDED" if lower > alpha else "EXCLUDED" if upper <= alpha else "UNRESOLVED"
    return {"p_lower": float(lower), "p_upper": float(upper), "p_lower_fraction": [lower.numerator, lower.denominator],
            "p_upper_fraction": [upper.numerator, upper.denominator], "decision": decision,
            "exceedances": exceedances, "unknown": unknown, "slots": slots,
            "rejection_convention": "p<=1-confidence_level"}


class _ProfiledModel:
    """Eliminate only linear magnitude baselines; preserve the native model."""
    def __init__(self, data, noise_scale=1., allow_negative_blend=False):
        self.base = _Model(data, noise_scale, False, allow_negative_blend)
        self.keep = [i for i in range(len(self.base.lower)) if i < 3 or i % 2 == 0]
        self.lower = self.base.lower[self.keep]
        self.upper = self.base.upper[self.keep]
        self.names = [self.base.parameter_names[i] for i in self.keep]
        for name in ("t","y","sigma","weights","index","lower","upper"):
            getattr(self.base,name).flags.writeable=False
        self.lower.flags.writeable=False
        self.upper.flags.writeable=False
        self._cache_z=None
        self._cache_x=None
        self._cache_contacts=None
        self._cache_residual=None
        self._cache_jacobian=None
        self.evaluation_counts={"state_misses":0,"residual_misses":0,"jacobian_misses":0,"cache_hits":0}

    def full_state(self, z):
        z = np.asarray(z, dtype=float)
        if self._cache_z is not None and np.array_equal(z,self._cache_z):
            self.evaluation_counts["cache_hits"]+=1
            return self._cache_x.copy(),self._cache_contacts.copy()
        self.evaluation_counts["state_misses"]+=1
        x = np.zeros(len(self.base.lower))
        x[self.keep] = z
        # With baseline zero, residual is w*(d-y); exact b is -sum(w*r)/sum(wÃƒâ€šÃ‚Â²).
        residual_zero = self.base.evaluate(x)
        contacts = []
        for k, name in enumerate(self.base.names):
            select = self.base.index == k
            weights = self.base.weights[select]
            optimum = -float(weights @ residual_zero[select]) / float(weights @ weights)
            bi = 3+2*k
            x[bi] = np.clip(optimum, self.base.lower[bi], self.base.upper[bi])
            if not self.base.lower[bi] < optimum < self.base.upper[bi]:
                contacts.append(name+".baseline_magnitude")
        self._cache_z=z.copy()
        self._cache_x=x.copy()
        self._cache_contacts=contacts.copy()
        self._cache_residual=None
        self._cache_jacobian=None
        return x.copy(),contacts.copy()

    def evaluate(self, z, jac=False):
        x, contacts = self.full_state(z)
        if not jac:
            if self._cache_residual is None:
                self.evaluation_counts["residual_misses"]+=1
                self._cache_residual=self.base.evaluate(x)
            else:self.evaluation_counts["cache_hits"]+=1
            return self._cache_residual.copy()
        if self._cache_jacobian is not None:
            self.evaluation_counts["cache_hits"]+=1
            return self._cache_jacobian.copy()
        self.evaluation_counts["jacobian_misses"]+=1
        j = self.base.evaluate(x, jac=True)[:, self.keep].copy()
        for k, name in enumerate(self.base.names):
            if name+".baseline_magnitude" in contacts:
                continue
            select = self.base.index == k
            w = self.base.weights[select]
            j[select] -= w[:, None] * ((w @ j[select]) / (w @ w))[None, :]
        self._cache_jacobian=j.copy()
        return j.copy()

    def seeds(self, starts):
        return [x[self.keep] for x in self.base.seeds(None, starts)]



def _magnification_excess(u):
    """Stable positive A(u)-1, only for deterministic seed geometry."""
    u=_finite_number(u,"seed separation")
    if u<=0:raise ValueError("positive seed separation required")
    root=math.hypot(u,2.)
    value=4./(u*root*(u*u+2.+u*root))
    if not math.isfinite(value) or value<=0:raise ValueError("seed excess outside floating range")
    return value


def _inverse_magnification_excess(excess):
    """Invert A-1>0 without subtracting nearly equal quantities.

This is initializer algebra. It neither transforms Gaussian magnitude errors
nor supplies another likelihood. Passing A-1 directly retains tiny excesses.
"""
    d=_finite_number(excess,"magnification excess")
    if d<=0:raise ValueError("positive magnification excess required")
    if d<=1.:
        root=math.sqrt(d)*math.sqrt(d+2.)
        return math.sqrt(2./root/(1.+d+root))
    reciprocal=1./(1.+d)
    root=math.sqrt((1.-reciprocal)*(1.+reciprocal))
    return reciprocal*math.sqrt(2./root/(1.+root))


def _seed_peak_width(model):
    """Deterministic, data-only initializer summary; never a fitted result.

Five-row median smoothing is in native magnitude. Time interpolation and
relative-flux algebra below initialize optimizer coordinates only. Every row
still enters the original native-magnitude objective with its supplied sigma.
"""
    base=model.base
    def unavailable(reason):return {"status":"GENERIC_FALLBACK","reason":reason}
    if len(base.names)!=1:return unavailable("MULTI_INSTRUMENT_SUMMARY_UNSUPPORTED")
    if len(base.t)<15:return unavailable("INSUFFICIENT_ROWS_FOR_INITIALIZER")
    order=np.lexsort((base.sigma,base.y,base.t))
    t=base.t[order];y=base.y[order];sigma=base.sigma[order]
    if np.any(np.diff(t)<=0):return unavailable("REPEATED_TIME_SUMMARY_UNSUPPORTED")
    smooth=np.median(np.lib.stride_tricks.sliding_window_view(y,5),axis=1)
    st=t[2:-2]
    k=int(np.argmin(smooth));peak_time=float(st[k])
    # Exactly the farthest half; deterministic value tie-breaks avoid row-order effects.
    distance=np.abs(t-peak_time)
    far=np.lexsort((sigma,y,t,-distance))[:max(5,len(t)//2)]
    baseline=float(np.median(y[far]));peak=float(smooth[k])
    amplitude=baseline-peak
    if not math.isfinite(amplitude) or amplitude<=5.*float(np.median(sigma)):
        return unavailable("WEAK_OR_NONBRIGHTENING_SUMMARY")
    try:excess=math.expm1(.4*math.log(10.)*amplitude)
    except OverflowError:return unavailable("RELATIVE_FLUX_OVERFLOW")
    if not math.isfinite(excess) or excess<=0:return unavailable("NONPHYSICAL_RELATIVE_FLUX")
    half_magnitude=baseline-2.5/math.log(10.)*math.log1p(.5*excess)
    below=smooth<half_magnitude
    edges=np.diff(np.r_[False,below,False].astype(int))
    runs=list(zip(np.flatnonzero(edges==1),np.flatnonzero(edges==-1)))
    substantial=[(a,b) for a,b in runs if b-a>=5]
    if len(substantial)>1:return unavailable("MULTIPLE_SUBSTANTIAL_BRIGHTENING_REGIONS")
    left=k
    while left>0 and below[left-1]:left-=1
    right=k
    while right+1<len(st) and below[right+1]:right+=1
    if left==0 or right==len(st)-1:return unavailable("HALF_EXCESS_NOT_BRACKETED")
    def crossing(i,j):
        denominator=float(smooth[j]-smooth[i])
        if denominator==0:raise ValueError("flat crossing")
        return float(st[i]+(st[j]-st[i])*(half_magnitude-smooth[i])/denominator)
    try:
        l=crossing(left-1,left);r=crossing(right,right+1)
    except (ValueError,OverflowError):return unavailable("DEGENERATE_HALF_EXCESS_CROSSING")
    halfwidth=.5*(r-l)
    if not math.isfinite(halfwidth) or halfwidth<=0:return unavailable("INVALID_HALF_EXCESS_WIDTH")
    return {"status":"DATA_ONLY_PEAK_WIDTH_SUMMARY","peak_time":peak_time,
        "baseline_magnitude":baseline,"peak_magnitude":peak,"relative_peak_excess":excess,
        "half_excess_width_days":halfwidth,"left_crossing":l,"right_crossing":r,
        "role":"INITIALIZER_ONLY; not a measurement, likelihood, detection or physical identification"}



def _seed_raw_peak_width(model):
    """Sparse-sampling summary; raw values only initialize, never replace data.

Require a significant native peak, at least one independently significant
adjacent-time neighbor, and both native half-excess crossings. A five-row
median can erase a short peak whose neighbors span weeks; no such smoothing
is used here. Unsupported raw summaries retain the predeclared median policy.
"""
    base=model.base
    def unavailable(reason):return {"status":"GENERIC_FALLBACK","reason":reason,"summary_policy":"RAW_PEAK_V1"}
    if len(base.names)!=1:return unavailable("MULTI_INSTRUMENT_SUMMARY_UNSUPPORTED")
    if len(base.t)<15:return unavailable("INSUFFICIENT_ROWS_FOR_INITIALIZER")
    order=np.lexsort((base.sigma,base.y,base.t))
    t=base.t[order];y=base.y[order];sigma=base.sigma[order]
    if np.any(np.diff(t)<=0):return unavailable("REPEATED_TIME_SUMMARY_UNSUPPORTED")
    k=int(np.argmin(y));peak_time=float(t[k]);peak=float(y[k])
    far=np.lexsort((sigma,y,t,-np.abs(t-peak_time)))[:max(5,len(t)//2)]
    baseline=float(np.median(y[far]));amplitude=baseline-peak
    if not math.isfinite(amplitude) or amplitude<=5.*float(sigma[k]):
        return unavailable("WEAK_OR_NONBRIGHTENING_NATIVE_PEAK")
    neighbors=[j for j in (k-1,k+1) if 0<=j<len(t)]
    supported=[j for j in neighbors if baseline-y[j]>3.*math.hypot(float(sigma[k]),float(sigma[j]))]
    if not supported:return unavailable("ISOLATED_NATIVE_PEAK_UNSUPPORTED")
    try:excess=math.expm1(.4*math.log(10.)*amplitude)
    except OverflowError:return unavailable("RELATIVE_FLUX_OVERFLOW")
    if not math.isfinite(excess) or excess<=0:return unavailable("NONPHYSICAL_RELATIVE_FLUX")
    half_magnitude=baseline-2.5/math.log(10.)*math.log1p(.5*excess)
    below=y<half_magnitude
    edges=np.diff(np.r_[False,below,False].astype(int))
    runs=list(zip(np.flatnonzero(edges==1),np.flatnonzero(edges==-1)))
    if sum(b-a>=2 for a,b in runs)>1:return unavailable("MULTIPLE_SUPPORTED_NATIVE_BRIGHTENING_REGIONS")
    left=k
    while left>0 and below[left-1]:left-=1
    right=k
    while right+1<len(t) and below[right+1]:right+=1
    if left==0 or right==len(t)-1:return unavailable("NATIVE_HALF_EXCESS_NOT_BRACKETED")
    def crossing(i,j):return float(t[i]+(t[j]-t[i])*(half_magnitude-y[i])/(y[j]-y[i]))
    l=crossing(left-1,left);r=crossing(right,right+1);width=.5*(r-l)
    if not math.isfinite(width) or width<=0:return unavailable("INVALID_NATIVE_HALF_EXCESS_WIDTH")
    return {"status":"DATA_ONLY_PEAK_WIDTH_SUMMARY","summary_policy":"RAW_PEAK_V1",
        "peak_time":peak_time,"baseline_magnitude":baseline,"peak_magnitude":peak,
        "peak_magnitude_error":float(sigma[k]),"supported_neighbor_count":len(supported),
        "relative_peak_excess":excess,"half_excess_width_days":width,"left_crossing":l,"right_crossing":r,
        "role":"INITIALIZER_ONLY; no transformed errors, replacement rows, likelihood or physical identification"}


def _null_peak_width_seeds(model,fixed_index,coordinate,starts,summary_policy="MEDIAN5_V1"):
    """Eight matched physical seeds plus four broad v1 seeds; otherwise v1 roster.

Only null tE/u0, single-instrument, 12-start use is supported. No supplied truth,
catalog value, fitted nuisance or random state enters this initialization.
"""
    if starts!=12:raise ValueError("NULL_PEAK_WIDTH12_V1 requires exactly 12 starts")
    generic=model.seeds(starts)
    if summary_policy=="MEDIAN5_V1":summary=_seed_peak_width(model)
    elif summary_policy=="RAW_FIRST_V1":
        raw_summary=_seed_raw_peak_width(model)
        summary=raw_summary if raw_summary["status"]=="DATA_ONLY_PEAK_WIDTH_SUMMARY" else _seed_peak_width(model)
    else:raise ValueError("unknown peak summary policy")
    info={"policy":"NULL_PEAK_WIDTH12_V1","summary":summary,"seed_count":12,
        "generic_fallback_indices":[0,2,5,10],"all_original_generic_seeds_used":False}
    if summary_policy=="RAW_FIRST_V1":
        info["policy"]="NULL_RAW_PEAK_WIDTH12_V1";info["raw_summary"]=raw_summary
    if summary["status"]!="DATA_ONLY_PEAK_WIDTH_SUMMARY":
        info["all_original_generic_seeds_used"]=True
        return generic,info
    peak=summary["peak_time"];e=summary["relative_peak_excess"];width=summary["half_excess_width_days"]
    def half_shape(u):
        other=_inverse_magnification_excess(.5*_magnification_excess(u))
        return math.sqrt((other-u)*(other+u))
    try:
        if fixed_index==1:
            te=math.exp(coordinate);ratio=width/te
            def equation(u):return half_shape(u)-ratio
            lo=max(math.exp(model.lower[2]),_inverse_magnification_excess(e/model.lower[3]))
            hi=min(math.exp(model.upper[2]),_inverse_magnification_excess(e/model.upper[3]))
            if lo>=hi:raise ValueError("physical fraction/impact intersection empty")
            if equation(lo)*equation(hi)>0:raise ValueError("shape root unbracketed")
            impact=brentq(equation,lo,hi,xtol=1e-13,rtol=1e-13,maxiter=100)
            fraction=e/_magnification_excess(impact)
            if not model.lower[3]<=fraction<=model.upper[3]:raise ValueError("physical width root unsupported")
            fractions=[fraction,.5*fraction,2*fraction,.05,.15,.3,.6,.95]
            physical=[(peak,te,_inverse_magnification_excess(e/float(np.clip(f,model.lower[3],model.upper[3]))),float(np.clip(f,model.lower[3],model.upper[3]))) for f in fractions]
        elif fixed_index==2:
            impact=math.exp(coordinate);te=width/half_shape(impact)
            fraction=float(np.clip(e/_magnification_excess(impact),model.lower[3],model.upper[3]))
            physical=[(peak,te,impact,fraction),(peak,te,impact,.5*fraction),
                (peak,te,impact,2*fraction),(peak,.5*te,impact,fraction),
                (peak,2*te,impact,fraction),(peak-.25*width,te,impact,fraction),
                (peak+.25*width,te,impact,fraction),(peak,te,impact,.1)]
        else:raise ValueError("unsupported null coordinate")
        matched=[]
        for time,timescale,impact,fraction in physical:
            z=np.array([(time-model.base.center)/model.base.scale,math.log(timescale),math.log(impact),fraction])
            z=np.clip(z,model.lower+1e-9,model.upper-1e-9);z[fixed_index]=coordinate
            if not np.all(np.isfinite(z)):raise ValueError("nonfinite seed")
            matched.append(z)
        seeds=matched+[generic[k].copy() for k in info["generic_fallback_indices"]]
        for z in seeds:z[fixed_index]=coordinate
        info["status"]="MATCHED8_PLUS_GENERIC4"
        info["encoded_seeds"]=[z.tolist() for z in seeds]
        return seeds,info
    except (ValueError,OverflowError,ZeroDivisionError):
        if summary_policy=="RAW_FIRST_V1":
            fallback,fallback_info=_null_peak_width_seeds(model,fixed_index,coordinate,starts,summary_policy="MEDIAN5_V1")
            fallback_info["policy"]="NULL_RAW_PEAK_WIDTH12_V1"
            fallback_info["raw_summary"]=raw_summary
            fallback_info["raw_geometry_failure"]="NO_SUPPORTED_PHYSICAL_RAW_PEAK_WIDTH_INVERSE"
            return fallback,fallback_info
        info["status"]="GENERIC_FALLBACK";info["reason"]="NO_SUPPORTED_PHYSICAL_PEAK_WIDTH_INVERSE"
        info["all_original_generic_seeds_used"]=True
        return generic,info


def _search(model, *, fixed=None, starts=12, max_nfev=1500, extra_seeds=(), only_extra_seeds=False):
    _positive_integer(starts, "starts")
    _positive_integer(max_nfev, "max_nfev")
    fixed = {} if fixed is None else fixed
    free = [k for k in range(len(model.lower)) if k not in fixed]
    seeds = ([] if only_extra_seeds else model.seeds(starts)) + [np.asarray(x, dtype=float).copy() for x in extra_seeds]
    if not seeds:
        raise ValueError("search requires a nonempty deterministic seed roster")
    reports, candidates = [], []
    for index, seed in enumerate(seeds):
        for k, value in fixed.items():
            seed[k] = value
        def state(z):
            x = seed.copy()
            x[free] = z
            return x
        try:
            solution = least_squares(lambda z: model.evaluate(state(z)), seed[free],
                jac=lambda z: model.evaluate(state(z), jac=True)[:, free],
                bounds=(model.lower[free], model.upper[free]), x_scale="jac",
                max_nfev=max_nfev, **FIT_PROTOCOL["tolerances"])
            x = state(solution.x)
            residual = model.evaluate(x)
            objective = float(residual @ residual)
            j = model.evaluate(x, jac=True)[:, free]
            gradient = j.T @ residual
            norms = np.maximum(np.linalg.norm(j, axis=0), 1e-300)
            distance = 1e-7*np.maximum(1., model.upper[free]-model.lower[free])
            projected = gradient.copy()
            projected[(solution.x-model.lower[free] <= distance) & (gradient >= 0)] = 0
            projected[(model.upper[free]-solution.x <= distance) & (gradient <= 0)] = 0
            score = float(np.max(np.abs(projected)/norms)) if free else 0.
            full, baseline_contacts = model.full_state(x)
            resolved = bool(solution.success and math.isfinite(objective) and math.isfinite(score) and score <= PROTOCOL["projected_score_tolerance"])
            report = {"start": index, "optimizer_success": bool(solution.success), "resolved": resolved,
                "status": int(solution.status), "message": str(solution.message), "nfev": int(solution.nfev),
                "objective_chi_square": objective, "scaled_projected_score": score,
                "parameters": model.base.decode(full), "baseline_box_contacts": baseline_contacts}
            reports.append(report)
            if resolved:
                candidates.append((objective, x, report))
        except (ValueError, OverflowError, FloatingPointError, np.linalg.LinAlgError) as exc:
            reports.append({"start": index, "resolved": False, "error": type(exc).__name__+": "+str(exc)})
    if not candidates:
        return {"status": "SEARCH_UNRESOLVED", "objective_chi_square": None, "starts": reports,
                "global_optimality_certified": False}, None
    candidates.sort(key=lambda c: c[0])
    objective, x, best = candidates[0]
    feasible = [r for r in reports if r.get("objective_chi_square") is not None and math.isfinite(r["objective_chi_square"])]
    lowest = min(feasible,key=lambda r:r["objective_chi_square"])
    tolerance = PROTOCOL["reference_objective_tolerance"]+PROTOCOL["reference_relative_tolerance"]*abs(objective)
    if lowest["objective_chi_square"] < objective-tolerance:
        return {"status":"LOWER_FEASIBLE_UNRESOLVED_TRIAL","objective_chi_square":None,
            "best_resolved_candidate":best,"lower_feasible_trial":lowest,"starts":reports,
            "global_optimality_certified":False},None
    contacts = [model.names[k] for k in range(len(x)) if
        min(x[k]-model.lower[k], model.upper[k]-x[k]) <= 1e-7*max(1., model.upper[k]-model.lower[k]) and k not in fixed]
    return {"status": "LOCALLY_RESOLVED_FINITE_SEARCH", "objective_chi_square": objective,
        "parameters": best["parameters"], "scaled_projected_score": best["scaled_projected_score"],
        "active_bounds": contacts, "baseline_box_contacts": best["baseline_box_contacts"],
        "starts": reports, "global_optimality_certified": False}, x


def profile_ordinate(dataset, parameter, value, *, starts=12, max_nfev=1500, noise_scale=1., search_method="FULL12_NULL12_POLISH1",seed_policy="V1_GENERIC"):
    """Profile all nuisance states at one tE/u0 value; finite search, not proof.

The null-constrained state seeds one additional unrestricted refinement. Any
still-better constrained objective invalidates the reference instead of being
silently clipped to a zero statistic. Boundary states are retained.
"""
    data = _dataset(dataset)
    if parameter not in ("tE_days", "u0"):
        raise ValueError("parameter must be tE_days or u0")
    value = _finite_number(value, parameter)
    if value <= 0:
        raise ValueError("positive parameter value required")
    if search_method not in ("FULL12_NULL12_POLISH1","NULL12_FREE1"):
        raise ValueError("unknown finite-search statistic method")
    if seed_policy not in ("V1_GENERIC","NULL_PEAK_WIDTH12_V1","NULL_RAW_PEAK_WIDTH12_V1"):raise ValueError("unknown seed policy")
    model = _ProfiledModel(data, noise_scale)
    fixed_index = 1 if parameter == "tE_days" else 2
    coordinate = math.log(value)
    if not model.lower[fixed_index] <= coordinate <= model.upper[fixed_index]:
        raise ValueError("ordinate outside unchanged numerical search domain")
    if search_method=="FULL12_NULL12_POLISH1":
        free, _ = _search(model, starts=starts, max_nfev=max_nfev)
        unrestricted_searches=[free]
    else:
        free={"status":"SEARCH_UNRESOLVED","objective_chi_square":None,"starts":[],"global_optimality_certified":False}
        unrestricted_searches=[]
    seed_info={"policy":"V1_GENERIC","seed_count":starts}
    if seed_policy in ("NULL_PEAK_WIDTH12_V1","NULL_RAW_PEAK_WIDTH12_V1"):
        seeds,seed_info=_null_peak_width_seeds(model,fixed_index,coordinate,starts,summary_policy="RAW_FIRST_V1" if seed_policy=="NULL_RAW_PEAK_WIDTH12_V1" else "MEDIAN5_V1")
        null,nx=_search(model,fixed={fixed_index:coordinate},starts=starts,max_nfev=max_nfev,extra_seeds=seeds,only_extra_seeds=True)
    else:
        null, nx = _search(model, fixed={fixed_index: coordinate}, starts=starts, max_nfev=max_nfev)
    refinement = None
    if nx is not None:
        refinement, _ = _search(model, starts=1, max_nfev=max_nfev, extra_seeds=(nx,), only_extra_seeds=True)
        unrestricted_searches.append(refinement)
        if refinement["objective_chi_square"] is not None and (free["objective_chi_square"] is None or refinement["objective_chi_square"] < free["objective_chi_square"]):
            free = refinement
    # A polish must not erase a lower unresolved feasible trial from an earlier search.
    reference_trials = [r for search in unrestricted_searches for r in search["starts"] if r.get("objective_chi_square") is not None and math.isfinite(r["objective_chi_square"])]
    if free["objective_chi_square"] is not None and reference_trials:
        lowest = min(reference_trials,key=lambda r:r["objective_chi_square"])
        tolerance = PROTOCOL["reference_objective_tolerance"]+PROTOCOL["reference_relative_tolerance"]*abs(free["objective_chi_square"])
        if lowest["objective_chi_square"] < free["objective_chi_square"]-tolerance:
            free = {"status":"LOWER_FEASIBLE_UNRESOLVED_REFERENCE_HISTORY","objective_chi_square":None,
                    "lower_feasible_trial":lowest,"starts":reference_trials,"global_optimality_certified":False}
    status, statistic, delta, tol = "NUMERICALLY_UNRESOLVED", None, None, None
    if free["objective_chi_square"] is not None and null["objective_chi_square"] is not None:
        delta = null["objective_chi_square"]-free["objective_chi_square"]
        tol = PROTOCOL["reference_objective_tolerance"] + PROTOCOL["reference_relative_tolerance"]*max(abs(null["objective_chi_square"]),abs(free["objective_chi_square"]))
        if delta >= -tol:
            statistic = max(delta, 0.)
            status = "PROFILE_ORDINATE_RESOLVED_FINITE_SEARCH"
    return {"schema": SCHEMA, "kind": "FINITE_SEARCH_PROFILE_ORDINATE", "input_sha256": data.sha256,
        "parameter": parameter, "value": value, "status": status, "statistic": statistic,
        "raw_profile_delta_chi_square":delta,"reference_roundoff_tolerance":tol,
        "tiny_negative_delta_clamped":bool(delta is not None and statistic is not None and delta<0),
        "unrestricted": free, "null_constrained": null, "null_seeded_unrestricted_refinement": refinement,
        "all_unrestricted_searches":unrestricted_searches,
        "run_options": {"starts": starts, "max_nfev": max_nfev, "noise_scale": float(noise_scale),"search_method":search_method,"seed_policy":seed_policy},
        "search_method":search_method,"seed_policy":seed_policy,"seed_initialization":seed_info,"evaluation_counts":model.evaluation_counts.copy(),
        "statistic_definition":"Fixed finite-search LR-like algorithm; no global likelihood optimum claim",
        "coverage_claim": False, "global_optimality_certified": False,
        "default_Wald_kind": "LOCAL_INVERSE_INFORMATION_DIAGNOSTIC_ONLY",
        "physical_identification": {"mass_msun": None, "lens_distance_pc": None, "theta_E_mas": None, "pi_E": None}}


def _seed_slots(entropy, parameter, value, slots):
    if not isinstance(entropy, (list, tuple)) or not entropy or any(isinstance(x,bool) or not isinstance(x,int) or x<0 for x in entropy):
        raise ValueError("entropy must be an explicit nonempty list of nonnegative integers")
    key = hashlib.sha256((parameter+":"+float(value).hex()).encode("ascii")).digest()
    words = [int.from_bytes(key[k:k+4], "big") for k in range(0, 32, 4)]
    return [[*entropy, *words, index] for index in range(slots)]


def _synthetic_document(data, mean_prediction, seed, noise_scale):
    rng = np.random.Generator(np.random.PCG64(np.random.SeedSequence(seed)))
    observed = mean_prediction + data.errors*noise_scale*rng.standard_normal(len(data.rows))
    token = hashlib.sha256(json.dumps(seed,separators=(",",":")).encode()).hexdigest()[:24]
    doc = data.to_dict()
    doc["sources"] = []
    doc["metadata"] = {"synthetic": True, "kind": "PARAMETRIC_BOOTSTRAP_MAGNITUDES", "parent_input_sha256": data.sha256}
    if "relative_time_combination_assumption" in data.document.get("metadata",{}):
        doc["metadata"]["relative_time_combination_assumption"] = deepcopy(data.document["metadata"]["relative_time_combination_assumption"])
    doc["metadata"]["inherited_instrument_metadata_role"] = "Parent time/error/calibration context only; every child brightness is synthetic and original source files remain with the immutable parent."
    doc["transformations"] = [{"operation":"SYNTHETIC_MAGNITUDE_REPLACEMENT","parent_input_sha256":data.sha256,"all_rows_replaced":True,"original_source_files_embedded":False}]
    for index,(row,y) in enumerate(zip(doc["rows"],observed)):
        row["bootstrap_parent_source_row_id"] = row["source_row_id"]
        row["source_row_id"] = f"SYNTHETIC:BOOTSTRAP:{token}:{index}"
        for key in ("native_fields","source_file","source_line","source_sha256"):
            row.pop(key,None)
        row["magnitude"] = float(y)
        row["quality_flags"] = [*row.get("quality_flags",[]),"SYNTHETIC_MAGNITUDE"]
    return UnresolvedPhotometry(doc)


class _AuditFailure(Exception):
    pass


def monte_carlo_ordinate(dataset, parameter, value, *, entropy, slots=199, confidence_level=.95,
                         starts=12, max_nfev=1500, noise_scale=1., generating_parameters=None,
                         lazy=True, audit_callback=None,search_method="FULL12_NULL12_POLISH1",seed_policy="V1_GENERIC"):
    """Fixed-slot rank test, with explicit estimated-nuisance qualification.

Default generation is at the NULL-CONSTRAINED fitted nuisance. Explicit fully
specified generating_parameters instead describe a simple null; they must not
be silently supplied by a validation truth to the fitting code. No source
observations are changed and synthetic values are never marked as native.
"""
    _positive_integer(slots,"slots")
    rank_p_bounds(0,slots,slots,confidence_level=confidence_level)
    data = _dataset(dataset)
    seeds = _seed_slots(entropy,parameter,value,slots)
    observed = profile_ordinate(data,parameter,value,starts=starts,max_nfev=max_nfev,noise_scale=noise_scale,search_method=search_method,seed_policy=seed_policy)
    rows = [{"slot":i,"seed":seed,"status":"NOT_ATTEMPTED_UNKNOWN"} for i,seed in enumerate(seeds)]
    kind = "NULL_CONSTRAINED_NUISANCE_PLUGIN_BOOTSTRAP_APPROXIMATE" if generating_parameters is None else "FULLY_SPECIFIED_SIMPLE_NULL_MONTE_CARLO"
    bounds = rank_p_bounds(0,slots,slots,confidence_level=confidence_level)
    null_parameters = None
    roundtrip_value = None
    audit_failure = None
    def emit(stage, slot, payload):
        if audit_callback is not None:
            try:
                audit_callback(stage,slot,payload)
            except Exception as exc:
                raise _AuditFailure(type(exc).__name__+": "+str(exc)) from exc
    try:emit("OBSERVED_PROFILE",-1,observed)
    except _AuditFailure as exc:audit_failure=str(exc)
    if observed["statistic"] is not None and audit_failure is None:
        null_parameters = deepcopy(observed["null_constrained"]["parameters"] if generating_parameters is None else generating_parameters)
        if not math.isclose(_finite_number(null_parameters[parameter],parameter),float(value),rel_tol=2e-15,abs_tol=0.):
            raise ValueError("generating state must satisfy the tested null value exactly")
        # Explicit physical ordinate is retained; log/exp round-trip is reported.
        roundtrip_value = null_parameters[parameter]
        null_parameters[parameter] = float(value)
        for name,lower,upper in (("tE_days",.1,10000.),("u0",.0001,10.)):
            if not lower <= _finite_number(null_parameters[name],name) <= upper:
                raise ValueError("generating geometry outside unchanged search domain")
        if null_parameters.get("allow_negative_blend",False):
            raise ValueError("signed blend is not the unchanged physical calibration model")
        for instrument in data.instruments:
            _finite_number(null_parameters["instruments"][instrument]["baseline_magnitude"],"baseline_magnitude")
            f = _finite_number(null_parameters["instruments"][instrument]["source_fraction"],"source_fraction")
            if not .000001 <= f <= 1.:
                raise ValueError("generating source fraction outside unchanged search domain")
        mean_prediction = predict_photometry(data,null_parameters)
        exceedances, unknown = 0, slots
        for row in rows:
            try:
                synthetic = _synthetic_document(data,mean_prediction,row["seed"],noise_scale)
                emit("GENERATED",row["slot"],synthetic.to_dict())
                result = profile_ordinate(synthetic,parameter,value,starts=starts,max_nfev=max_nfev,noise_scale=noise_scale,search_method=search_method,seed_policy=seed_policy)
                emit("FITTED",row["slot"],result)
                row.update({"input_sha256":synthetic.sha256,"statistic":result["statistic"],"numerical_status":result["status"]})
                if result["statistic"] is None:
                    row["status"] = "NUMERICALLY_UNRESOLVED_UNKNOWN"
                else:
                    # Near floating ties remain unknown; they cannot certify an exclusion.
                    tolerance = 1e-8*(1+abs(observed["statistic"])+abs(result["statistic"]))
                    difference = result["statistic"]-observed["statistic"]
                    if abs(difference) <= tolerance:
                        row["status"] = "ORDERING_UNRESOLVED_UNKNOWN"
                    else:
                        unknown -= 1
                        counted = difference > 0
                        exceedances += int(counted)
                        row["status"] = "EXCEEDANCE" if counted else "NONEXCEEDANCE"
            except _AuditFailure as exc:
                audit_failure = str(exc)
                row.update({"status":"AUDIT_FAILURE_UNKNOWN","error":audit_failure})
                break
            except (ValueError,RuntimeError,FloatingPointError,OverflowError,np.linalg.LinAlgError) as exc:
                row.update({"status":"FAILED_UNKNOWN","error":type(exc).__name__+": "+str(exc)})
            bounds = rank_p_bounds(exceedances,unknown,slots,confidence_level=confidence_level)
            if lazy and bounds["decision"] != "UNRESOLVED":
                break
    if audit_failure is not None:
        bounds["decision"] = "UNRESOLVED"
    return {"schema":SCHEMA,"kind":kind,"input_sha256":data.sha256,"parameter":parameter,"value":float(value),
        "confidence_level":float(confidence_level),"rank_bounds":bounds,"observed_profile":observed,
        "search_method":search_method,"seed_policy":seed_policy,
        "null_generating_parameters":null_parameters,"slots":rows,"fixed_roster_slots":slots,
        "attempted_slots":sum(r["status"]!="NOT_ATTEMPTED_UNKNOWN" for r in rows),"lazy":bool(lazy),
        "audit_failure":audit_failure,"null_coordinate_roundtrip_value":roundtrip_value if null_parameters is not None else None,
        "coverage_claim":False,"independent_holdout_validated":False,
        "qualification":"Rank validity is simple-null/same-law; fitted-nuisance generation is approximate. Finite search and uncertain comparisons remain explicit.",
        "BHSM_interpretation":"One PSPL optical exterior interpreted as BHSM surface topography; no gravitational-origin/BH identity validation.",
        "physical_identification":observed["physical_identification"]}


def confidence_set_from_ordinates(ordinates):
    """Inspect a supplied grid without inventing smooth/stochastic endpoints.

Unknown decisions stay in the outer set. Disconnected components and endpoint
brackets are retained. This does not prove that an unevaluated gap is excluded
or that a grid edge is a finite confidence endpoint.
"""
    if not ordinates:
        raise ValueError("at least one calibrated ordinate required")
    first = ordinates[0]
    ordered = sorted(ordinates,key=lambda r:r["value"])
    if len({r["value"] for r in ordered}) != len(ordered):
        raise ValueError("duplicate ordinates")
    for r in ordered:
        if any(r[k]!=first[k] for k in ("input_sha256","parameter","confidence_level","kind")):
            raise ValueError("incompatible inference ordinate grids")
    components = []
    begin = None
    for index,row in enumerate(ordered):
        retained = row["rank_bounds"]["decision"] != "EXCLUDED"
        if retained and begin is None:
            begin = index
        if begin is not None and (not retained or index==len(ordered)-1):
            end = index if retained else index-1
            components.append({"retained_grid_values":[r["value"] for r in ordered[begin:end+1]],
                "lower_endpoint":None,"upper_endpoint":None,
                "lower_endpoint_bracket":None if begin==0 else [ordered[begin-1]["value"],ordered[begin]["value"]],
                "upper_endpoint_bracket":None if end==len(ordered)-1 else [ordered[end]["value"],ordered[end+1]["value"]],
                "lower_status":"GRID_EDGE_OUTSIDE_UNASSESSED" if begin==0 else "BRACKET_ONLY",
                "upper_status":"GRID_EDGE_OUTSIDE_UNASSESSED" if end==len(ordered)-1 else "BRACKET_ONLY"})
            begin=None
    return {"schema":SCHEMA,"kind":"GRID_DECISION_SUMMARY_WITH_UNRESOLVED_ENDPOINTS",
        "parameter":first["parameter"],"confidence_level":first["confidence_level"],"components":components,
        "ordinates":ordered,"finite_endpoints_available":False,"coverage_claim":False,
        "interpolation_or_unobserved_gap_exclusion_claimed":False,
        "unevaluated_domain":"UNASSESSED; not excluded and not assigned a continuous set topology",
        "qualification":"Sampled-grid decisions/brackets only, not a continuous confidence set or certified endpoints; numerical-domain caps never become physical confidence bounds."}
