"""Read-only, source-pinned candidate localization inventory; no fit imports.

Catalog directions locate a background source/event, not a present lens.
All supplied results and failed assessments survive in source_records.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
from html.parser import HTMLParser
import json
import math
from pathlib import Path
import re

SCHEMA = "bhsm.blackhole_tracker.candidate_inventory.v1"
FORMAL = "https://github.com/ncarberry64/Berger-Hopf-Standard-Model"
COMMIT = "2af2d37d75786d923cfe780517125450ad1f49a3"
PAPER = "papers/bhsm_blackhole_tracker_20261021/real_data_pilot_20261022"
PAR_BASE = "complementary_parallax_cohort_inventory/"
W2016 = "https://arxiv.org/html/1509.04899v2"
M2021 = "https://arxiv.org/html/2107.13701v1"
CDS = "https://cdsarc.cds.unistra.fr/ftp/J/MNRAS/458/3012/"
BHSM = ("One ordinary compact-lens Einstein/GHY exterior optical response is counted once. "
        "No additional core/envelope lensing potential is introduced. These data do not "
        "uniquely identify a core state, membrane deformation or horizon.")

def digest(data):
    return hashlib.sha256(data).hexdigest()

def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")

def angle(ra, dec):
    h,m,s = map(float, ra.split(":"))
    if not (0 <= h < 24 and 0 <= m < 60 and 0 <= s < 60):
        raise ValueError("Invalid catalog right ascension")
    sign = -1 if dec.startswith("-") else 1
    d,dm,ds = map(float, dec.lstrip("+-").split(":"))
    if not (0 <= d <= 90 and 0 <= dm < 60 and 0 <= ds < 60 and (d < 90 or dm == ds == 0)):
        raise ValueError("Invalid catalog declination")
    return (15*(h+m/60+s/3600), sign*(d+dm/60+ds/3600))

def separation(a,b):
    ra,dec = map(math.radians,a)
    rb,deb = map(math.radians,b)
    v = (math.cos(dec)*math.cos(ra),math.cos(dec)*math.sin(ra),math.sin(dec))
    w = (math.cos(deb)*math.cos(rb),math.cos(deb)*math.sin(rb),math.sin(deb))
    cross = (v[1]*w[2]-v[2]*w[1],v[2]*w[0]-v[0]*w[2],v[0]*w[1]-v[1]*w[0])
    return math.degrees(math.atan2(math.sqrt(sum(x*x for x in cross)),sum(x*y for x,y in zip(v,w))))*3600

def ews_alias(value):
    if value is None or value in {"", "-", "---"}:
        return None
    return value if value.startswith("OGLE-") else "OGLE-" + value

class TableParser(HTMLParser):
    """Save printed cells from one primary HTML table without interpreting math."""
    def __init__(self, identity):
        super().__init__(convert_charrefs=True)
        self.identity=identity; self.depth=0; self.rows=[]; self.row=None; self.cell=None
    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        if tag == "table":
            if self.depth: self.depth += 1
            elif attrs.get("id") == self.identity: self.depth=1
        if not self.depth: return
        if tag == "tr": self.row=[]
        if tag in {"td","th"}: self.cell=[]
    def handle_data(self, data):
        if self.depth and self.cell is not None: self.cell.append(data)
    def handle_endtag(self, tag):
        if not self.depth: return
        if tag in {"td","th"} and self.cell is not None:
            self.row.append(" ".join("".join(self.cell).split())); self.cell=None
        if tag == "tr" and self.row:
            self.rows.append(self.row); self.row=None
        if tag == "table": self.depth-=1

def source_spec(formal_root, evidence_root):
    p = Path(formal_root)/PAPER
    r = Path(evidence_root)
    specs = {
        "pilot_results": (p/"literature_annotations_v1/all_100_results.json", FORMAL+f"/blob/{COMMIT}/{PAPER}/literature_annotations_v1/all_100_results.json"),
        "pilot_ranking": (p/"literature_annotations_v1/followup_ranking.json", FORMAL+f"/blob/{COMMIT}/{PAPER}/literature_annotations_v1/followup_ranking.json"),
        "prior_crossmatch": (p/"literature_annotations_v1/prior_cohort_crossmatch.json", FORMAL+f"/blob/{COMMIT}/{PAPER}/literature_annotations_v1/prior_cohort_crossmatch.json"),
        "pilot_protocol": (p/"protocol_v1.json", FORMAL+f"/blob/{COMMIT}/{PAPER}/protocol_v1.json"),
        "alias_addendum": (r/"complementary_parallax_alias_addendum/PILOT_ALIAS_AND_PARALLAX59_ADDENDUM.json", None),
        "cohort59": (r/PAR_BASE/"COHORT59_PREACQUISITION_DECLARATION.json", CDS+"table2.dat"),
        "older_acquisition": (r/PAR_BASE/"OLDER2015_NATIVE_ACQUISITION.json", "https://ftp.astrouw.edu.pl/ogle/ogle3/blg_tau/README.txt"),
        "catalog2015": (r/PAR_BASE/"primary_sources/OGLE2015_catalogA-full.table", "https://ftp.astrouw.edu.pl/ogle/ogle3/blg_tau/catalogA-full.table"),
        "catalog2016": (r/PAR_BASE/"primary_sources/CDS2016_table2.dat", CDS+"table2.dat"),
        "modes2016": (r/PAR_BASE/"primary_sources/CDS2016_table3.dat", CDS+"table3.dat"),
        "readme2016": (r/PAR_BASE/"primary_sources/CDS2016_ReadMe", CDS+"ReadMe"),
        "tables2016": (r/PAR_BASE/"Wyrzykowski2016_arxiv150904899v2.html.tables.json", W2016),
        "reanalysis2021": (r/"metadata_research/MrozWyrzykowski2021_arxiv210713701v1.html", M2021),
        "cohort_inventory": (r/PAR_BASE/"COMPLEMENTARY_COHORT_INVENTORY.json", W2016),
        "benchmark_input": (r/"joint_2025_exposure_research_v1/JOINT_2025_NATIVE_INPUT_v1.review_pending.json", "https://doi.org/10.3847/1538-4357/adbe6e"),
        "benchmark_recovery_outcome": (r/"joint_2025_exposure_research_v1/native_checkpoint_recovery_review_pending/authentic_M0_nu6_checkpoint_replay_v1/RECOVERY_OUTCOME.json", None),
    }
    acq=json.loads(specs["older_acquisition"][0].read_text(encoding="utf-8"))
    for row in acq["records"]:
        specs["older_native:"+row["event_id"]] = (r/PAR_BASE/Path(row["relative_path"]), row["requested_url"])
    return specs

def freeze_inputs(formal_root, evidence_root, script_path):
    specs=source_spec(formal_root,evidence_root)
    sources={}
    for role,(path,url) in specs.items():
        raw=path.read_bytes()
        sources[role]={"path":str(path.resolve()),"bytes":len(raw),"sha256":digest(raw),"url":url}
    return {"schema":"bhsm.blackhole_tracker.candidate_inventory_input_freeze.v1",
            "status":"SOURCE_METADATA_ONLY_NO_MODEL_OR_FIT_CALLS",
            "scientific_as_of":"2026-10-23", "formal_BHSM_repository":FORMAL,
            "formal_source_commit":COMMIT, "builder_sha256":digest(Path(script_path).read_bytes()),
            "sources":sources}

def load_frozen(freeze, snapshot_root=None, original_source_map=None):
    raw={}
    snapshot_root=Path(snapshot_root) if snapshot_root is not None else Path(__file__).resolve().parent
    if original_source_map:
        for role,path in original_source_map.items():
            source=freeze["sources"][role]
            content=Path(path).read_bytes()
            if len(content)!=source["bytes"] or digest(content)!=source["sha256"]:
                raise ValueError("Original source integrity mismatch: "+role)
    for role, row in freeze["sources"].items():
        if row.get("snapshot_path") is None:
            continue
        path=(snapshot_root/row["snapshot_path"]).resolve()
        if not path.is_relative_to(snapshot_root.resolve()):
            raise ValueError("Snapshot path escapes metadata root")
        content=path.read_bytes()
        if len(content)!=row["snapshot_bytes"] or digest(content)!=row["snapshot_sha256"]:
            raise ValueError("Source integrity mismatch: "+role)
        raw[role]=content
    return raw

def cells_for(rows, event):
    short=event.removeprefix("OGLE3-ULENS-")
    return [{"printed_row":i,"cells":row} for i,row in enumerate(rows,1)
            if row and (row[0]==short or row[0].startswith(short+" ") or row[0].startswith(short+"\u2020"))]

def validate_inventory(doc):
    events=doc["events"]
    if doc["schema_version"]!=SCHEMA or len(events)!=155: raise ValueError("Inventory schema/count")
    if len({e["event_id"] for e in events})!=155: raise ValueError("Duplicate identity")
    for e in events+doc.get("benchmarks",[]):
        s=e["source_direction"]
        if not (0<=s["ra_deg"]<360 and -90<=s["dec_deg"]<=90): raise ValueError("Direction range")
        if s["epoch"] is not None: raise ValueError("J2000 is not an observation epoch")
        if any(v is not None for v in e["lens"].values()): raise ValueError("Unidentified lens quantity promoted")
        if e["map_eligibility"]!={"sky_marker":True,"three_dimensional":False,"propagate_position":False}:
            raise ValueError("Unsupported localization promotion")
        if e["new_black_hole_interpretation"] or e["accepted_engine_black_hole"]:
            raise ValueError("Unsupported discovery/acceptance")
    return True

def build(freeze, snapshot_root=None):
    if freeze.get("verification_scope")!="OFFLINE_METADATA_REBUILD_FROM_FACTUAL_SNAPSHOTS":
        raise ValueError("This version requires the declared metadata snapshot route")
    raw=load_frozen(freeze,snapshot_root)
    read=lambda name: json.loads(raw[name])
    pilot=read("pilot_results"); declaration=read("cohort59"); prior=declaration["events"]
    alias=read("alias_addendum"); old=read("older_acquisition"); tables=read("tables2016")
    get_table=lambda identity: next(t["rows"] for t in tables if t["id"]==identity)
    if len(pilot)!=100 or len(prior)!=59: raise ValueError("Whole cohorts required")
    if len({x["event_id"] for x in pilot})!=100 or len({x["event_id"] for x in prior})!=59: raise ValueError("Source duplicates")
    if len({x["ogle_database_id"] for x in prior})!=59: raise ValueError("Duplicate PAR DB ID")
    # Independently verify the 59 printed source rows and the complete pilot
    # against original catalog coordinates; no coordinate propagation is used.
    native_par=raw["catalog2016"].decode().splitlines()
    if len(native_par)!=59: raise ValueError("59-row primary catalog required")
    for x,line in zip(prior,native_par):
        if x["native_catalog_line"]!=line: raise ValueError("PAR native row changed")
    catalog={line.split()[0]:line for line in raw["catalog2015"].decode().splitlines() if line.strip() and not line.startswith("#")}
    pilot_db={}; pilot_alias={}; native_pilot={}
    for p in pilot:
        short=p["event_id"].rsplit("-",1)[1]; line=catalog[short]; fields=line.split()
        if fields[1:3]!=[p["ra_j2000"],p["dec_j2000"]]: raise ValueError("Pilot direction changed")
        db=fields[3]+"."+fields[4]
        if db!=p["catalog_database_id"]: raise ValueError("Pilot DB identity changed")
        pilot_db[p["event_id"]]={db}
        if fields[-1]!="-": pilot_db[p["event_id"]].add(fields[-1])
        pilot_alias[p["event_id"]]={ews_alias(p["ews_alias"])}-{None}
        native_pilot[p["event_id"]]=line
    pairs=[]; to_pilot={}
    for x in prior:
        matches=[]
        for p in pilot:
            methods=[]
            if x["ogle_database_id"] in pilot_db[p["event_id"]]: methods.append("EXACT_OGLE_DATABASE_ID_OR_DECLARED_OVERLAP")
            if set(x["aliases"]) & pilot_alias[p["event_id"]]: methods.append("EXACT_PUBLISHED_EWS_ALIAS")
            sep=separation(angle(p["ra_j2000"],p["dec_j2000"]),angle(x["ra_j2000_hms"],x["dec_j2000_dms"]))
            if methods:
                if sep>2.0: raise ValueError("Identity/direction contradiction")
                methods.append("J2000_GREAT_CIRCLE_WITHIN_2_ARCSEC")
                matches.append(p["event_id"])
                pairs.append({"pilot_event_id":p["event_id"],"parallax_event_id":x["event_id"],"methods":methods,"separation_arcsec":sep})
            elif sep<=2.0: raise ValueError("Unresolved coordinate-only association requires review")
        if len(matches)>1: raise ValueError("Ambiguous duplicate association")
        if matches: to_pilot[x["event_id"]]=matches[0]
    saved={(p["event_id"],x["prior_event_id"]) for p in alias["matched_pilot_events"] for x in p["matched_prior_events"]}
    found={(p["pilot_event_id"],p["parallax_event_id"]) for p in pairs}
    if found!=saved or len(pairs)!=4 or len(set(to_pilot.values()))!=4:
        raise ValueError("Four independently verified historical associations required")
    # The manuscript table, unlike CDS table3's entire 142 modes, identifies
    # the 13 highlighted remnant-consistent events. Preserve every mode.
    remnant={"OGLE3-ULENS-"+r[0] for r in get_table("S3.T3.1.1") if r and re.fullmatch(r"PAR-\d{2}",r[0])}
    if len(remnant)!=13: raise ValueError("Historical13 remnant selection changed")
    modes={x["event_id"]:[] for x in prior}
    for line_no,line in enumerate(raw["modes2016"].decode().splitlines(),1):
        identity="OGLE3-ULENS-"+line[:6].strip()
        modes[identity].append({"source_row_id":f"CDS:J/MNRAS/458/3012/table3.dat:line:{line_no}","native_catalog_line":line})
    if sum(map(len,modes.values()))!=142 or any(not m for m in modes.values()): raise ValueError("All142 parallax modes required")
    revision_snapshot=read("reanalysis2021")
    if revision_snapshot["table_id"]!="S2.T1.2": raise ValueError("2021 table snapshot identity")
    revision_rows=revision_snapshot["rows"]
    revised={"OGLE3-ULENS-"+re.match(r"PAR-\d{2}",r[0])[0] for r in revision_rows if r and re.match(r"PAR-\d{2}",r[0])}
    if len(revised)!=8: raise ValueError("Eight2021 revised events required")
    old_by={r["event_id"]:r for r in old["records"]}
    if len(old_by)!=26 or sum(r["numeric_rows"] for r in old_by.values())!=19068: raise ValueError("26 native tables required")
    for identity,r in old_by.items():
        audit=read("native_availability_audit")["records"][identity]
        source=freeze["sources"]["older_native:"+identity]
        if not audit["original_bytes_verified_at_snapshot_preparation"]:
            raise ValueError("Missing prior raw observation integrity audit")
        if (audit["sha256"]!=r["sha256"] or source["sha256"]!=r["sha256"]
                or audit["bytes"]!=r["bytes"] or audit["numeric_rows"]!=r["numeric_rows"]):
            raise ValueError("Native availability metadata contradiction")
    eligible={p["event_id"] for p in pilot if p["followup_eligible"]}
    if eligible!={"OGLE3-ULENS-0585","OGLE3-ULENS-3092"}: raise ValueError("Frozen pilot followup changed")
    records={}
    def source_ref(role,row=None):
        s=freeze["sources"][role]
        return {"source_role":role,"sha256":s["sha256"],"url":s["url"],"source_row_id":row}
    for p in pilot:
        identity=p["event_id"]; ra,dec=angle(p["ra_j2000"],p["dec_j2000"])
        aliases={ews_alias(p["ews_alias"]), p["catalog_database_id"]}-{None}
        aliases.update(p.get("additional_confirmed_aliases",[]))
        records[identity]={
            "event_id":identity,"known_aliases":sorted(aliases),"cohorts":["FROZEN_100_EVENT_PILOT_V1"],
            "source_direction":{"ra_deg":ra,"dec_deg":dec,"ra_hms":p["ra_j2000"],"dec_dms":p["dec_j2000"],
                "frame":"catalog_equatorial","equinox":"J2000","epoch":None,"role":"SOURCE_EVENT_DIRECTION",
                "uncertainty":None,"provenance":[source_ref("catalog2015", "OGLE2015:catalogA-full.table:line:"+identity.rsplit("-",1)[1])]},
            "lens":{key:None for key in ["position","position_epoch","position_covariance","distance_pc","mass_msun","proper_motion_mas_yr","radial_velocity_km_s"]},
            "tier":"BLACK_HOLE_SEARCH_TARGET" if identity in eligible else "REVIEW_REQUIRED",
            "classification_basis":"FROZEN_PHOTOMETRIC_FOLLOWUP_SCREEN_ONLY_NO_BH_DISCRIMINATION" if identity in eligible else "PUBLISHED_CATALOG_EVENT_REQUIRES_FURTHER_MODEL_OR_ALTERNATIVE_ASSESSMENT",
            "classification_evidence":["Historical published microlensing catalog designation; this is not independently established by a scalar nonrejection."]+(["Passed all frozen pilot followup screens; lens mass/type remains unresolved."] if identity in eligible else []),
            "quality_flags":copy.deepcopy(p["flags"]),
            "photometric_assessment":{"tracker_status":p["status"],"scalar_fit_nonrejected":p["status"]!="PHOTOMETRIC_MODEL_INADEQUATE", "followup_eligible":p["followup_eligible"],
                "fit_statistics_are_not_lens_versus_variable_model_evidence":True,
                "fitted_tE_days":p["fitted_tE_days"],"timescale_profile_lower_days":p["profile_lower_days"],"timescale_profile_upper_days":p["profile_upper_days"],
                "timescale_profile_status":p["profile_status"],"timescale_is_not_mass":True,"conditions":copy.deepcopy(p["followup_conditions"])},
            "literature_assessment":{"published_lensing_designation":True,"lensing_designation_source":"Wyrzykowski2015 standard-event catalog", "published_dark_remnant_consistent":False,
                "current_BH_evidence_status":"UNRESOLVED_NO_DISCRIMINATING_BH_EVIDENCE", "interpretations":[],"alternatives":["luminous stellar lens","white dwarf","neutron star","multiple-object lens","source variability or calibration inadequacy pending model checks"]},
            "map_eligibility":{"sky_marker":True,"three_dimensional":False,"propagate_position":False},
            "missing_observations":["independent angular lensing scale or relative lens-source motion","validated microlensing parallax for this route","lens-light constraints with crowded-field calibration","source-distance information","absolute lens position and reference epoch"],
            "next_actions":(["Search archival event photometry for parallax and validate alternatives; obtain angular/lens-light evidence before physical classification."] if identity in eligible else ["Review failed/flagged simple-model adequacy and compare variability, parallax, blending and multiple-lens explanations."]),
            "provenance":[source_ref("pilot_results",identity),source_ref("catalog2015",identity)],
            "source_records":{"pilot_result":copy.deepcopy(p),"native2015_catalog_line":native_pilot[identity]},
            "new_black_hole_interpretation":False,"accepted_engine_black_hole":False,
            "ranking":{"new_rank":None,"basis":"No new ranking; preserve frozen pilot qualification separately from literature evidence."},
        }
    for p in prior:
        par=p["event_id"]; identity=to_pilot.get(par,par)
        if identity not in records:
            ra,dec=angle(p["ra_j2000_hms"],p["dec_j2000_dms"])
            records[identity]={"event_id":identity,"known_aliases":[],"cohorts":[],
                "source_direction":{"ra_deg":ra,"dec_deg":dec,"ra_hms":p["ra_j2000_hms"],"dec_dms":p["dec_j2000_dms"],"frame":"catalog_equatorial","equinox":"J2000","epoch":None,"role":"SOURCE_EVENT_DIRECTION","uncertainty":None,"provenance":[source_ref("catalog2016",p["catalog_source_row_id"])]},
                "lens":{key:None for key in ["position","position_epoch","position_covariance","distance_pc","mass_msun","proper_motion_mas_yr","radial_velocity_km_s"]},
                "quality_flags":[],"photometric_assessment":{"tracker_status":"NOT_FIT_WITH_VALIDATED_PARALLAX_ROUTE","scalar_fit_nonrejected":None,"followup_eligible":None,"timescale_is_not_mass":True},
                "literature_assessment":{"interpretations":[],"alternatives":["ordinary luminous star","white dwarf","neutron star","black hole","multiple-object lens or model/systematic alternatives"]},
                "map_eligibility":{"sky_marker":True,"three_dimensional":False,"propagate_position":False},
                "missing_observations":["measured angular lensing scale or relative lens-source motion","independent lens position at stated date","validated source-distance and lens-light information"],
                "next_actions":[],"provenance":[],"source_records":{},"new_black_hole_interpretation":False,"accepted_engine_black_hole":False,
                "ranking":{"new_rank":None,"basis":"Published cohort is not newly ranked; mode probabilities depend on specified population assumptions."}}
        e=records[identity]
        e["cohorts"].append("WYRZYKOWSKI_2016_PARALLAX_59")
        e["known_aliases"]=sorted(set(e["known_aliases"]+p["aliases"]+[p["ogle_database_id"]]+([par] if par!=identity else [])))
        e["tier"]="BLACK_HOLE_SEARCH_TARGET" if par=="OGLE3-ULENS-PAR-13" else "SUPPORTED_LENSING_EVENT"
        e["classification_basis"]="PUBLISHED_CONDITIONAL_BH_POSSIBILITY_WITH_UNRELIABLE_GAIA_AND_LOWER_MASS_ALTERNATIVE" if par.endswith("PAR-13") else "LITERATURE_PARALLAX_LENS_DESIGNATION_NOT_TRACKER_CONFIRMATION"
        e["classification_evidence"]=["Primary2016 paper selected this event as part of its59 parallax-lensing golden sample; no new parallax fit was performed."]
        e["literature_assessment"].update({"published_lensing_designation":True,"lensing_designation_source":"Wyrzykowski2016 Table2",
            "published_dark_remnant_consistent":par in remnant,
            "current_BH_evidence_status":"DISPUTED_PRIOR_CONDITIONAL_BH_POSSIBILITY" if par.endswith("PAR-13") else "NO_CURRENT_DISCRIMINATING_BH_IDENTIFICATION_IN_THIS_INVENTORY",
            "historical_remnant_probability_mode_cells":cells_for(get_table("S4.T4.3"),par),
            "historical_mass_distance_mode_cells":cells_for(get_table("S4.T5.3"),par),
            "conditional_values_are_not_independent_observations":True,
            "population_prior_assumptions":"2016 Galactic/relative-proper-motion and source-distance assumptions; probability pertains to dark remnants collectively, not black holes alone."})
        e["literature_assessment"]["interpretations"].append({"publication":"Wyrzykowski et al.2016","url":W2016,"role":"HISTORICAL_PRIOR_CONDITIONAL_INTERPRETATION","dark_remnant_candidate":par in remnant,"accepted_by_engine":False})
        if par in revised:
            caution=("2021 reanalysis lowers several historical mass estimates using revised Galactic/source-motion priors and frame treatment; do not reuse historical BH labels as current truth.")
            if par.endswith("PAR-02"):
                caution="2021 reanalysis favors a roughly0.9 solar-mass bulge star under its fiducial Galactic/source-motion assumptions, superseding the historical strongest-BH-candidate interpretation; not a direct mass measurement."
            if par.endswith("PAR-13"):
                caution="2021 BH-scale conditional mass depends on unreliable Gaia DR2 source astrometry (RUWE1.67; absent in EDR3); an alternative OGLE source-motion estimate gives a lower conditional mass. Both remain population-dependent, not measured lens motion or mass."
            e["literature_assessment"]["interpretations"].append({"publication":"Mroz & Wyrzykowski2021","url":M2021,"role":"LATER_PRIOR_CONDITIONAL_REANALYSIS","printed_table1_rows":cells_for(revision_rows,par),"caution":caution,"accepted_by_engine":False})
            e["quality_flags"].append("LATER_PRIOR_CONDITIONAL_REANALYSIS_REVISES_HISTORICAL_MASS")
        if par.endswith("PAR-13"):
            e["quality_flags"].extend(["GAIA_SOURCE_ASTROMETRIC_SOLUTION_UNRELIABLE","ALTERNATIVE_SOURCE_MOTION_SUPPORTS_LOWER_MASS","NO_BLACK_HOLE_IDENTIFICATION"])
            e["classification_evidence"].append("Later literature retains a BH-scale prior-conditional possibility but explicitly flags unreliable source astrometry and a lower-mass alternative. This justifies investigation, not candidate confirmation.")
            e["next_actions"].append("Resolve Gaia/OGLE source-motion discrepancy and crowded-field association before adopting any BH-scale interpretation.")
        if par in remnant: e["quality_flags"].append("HISTORICAL_DARK_REMNANT_IS_NOT_A_BH_LABEL")
        e["quality_flags"].extend(["EXACT_2016_NATIVE_REDUCTION_UNAVAILABLE","LENS_MASS_DISTANCE_MOTION_UNRESOLVED"])
        native=old_by.get(par)
        e["source_records"]["parallax2016_catalog"]=copy.deepcopy(p)
        e["source_records"]["parallax2016_all_degenerate_fit_modes"]=modes[par]
        e["source_records"]["older2015_acquisition"]=copy.deepcopy(native)
        e["native_data_availability"]={"exact2016_version":"UNAVAILABLE_IN_BOUNDED_SOURCE_AUDIT","older2015_version":native["native_version"] if native else None,
            "older2015_rows":native["numeric_rows"] if native else None,"older2015_sha256":native["sha256"] if native else None,
            "older2015_status":"RAW_HASH_VERIFIED_AT_SNAPSHOT_PREPARATION_NOT_REFETCHED_BY_OFFLINE_METADATA_BUILD" if native else "UNAVAILABLE_EXACT_ID_MATCH_NOT_LOCATED",
            "raw_time_convention":"HJD-2450000","raw_clock_scale":None,"covariance":None,"extra_error_rescaling_applied":False}
        if not native: e["quality_flags"].append("OLDER_NATIVE_TABLE_UNAVAILABLE")
        e["next_actions"].append("Recover and version exact native parallax observations, calibration, masks and clocks; validate and process all59 including unavailable or failed cases.")
        e["provenance"].extend([source_ref("catalog2016",p["catalog_source_row_id"]),source_ref("tables2016",par),source_ref("reanalysis2021",par)] if par in revised else [source_ref("catalog2016",p["catalog_source_row_id"]),source_ref("tables2016",par)])
    events=sorted(records.values(),key=lambda e:e["event_id"])
    for e in events:
        e["quality_flags"]=sorted(set(e["quality_flags"]))
        e["BHSM_interpretation"]=BHSM
    counts={"unique_events":len(events),"pilot_events":100,"published_parallax_events":59,"verified_overlap_pairs":len(pairs),"sky_markers":len(events),
        "pilot_inadequate_simple_model":sum(p["status"]=="PHOTOMETRIC_MODEL_INADEQUATE" for p in pilot),
        "pilot_scalar_nonrejected":sum(p["status"]!="PHOTOMETRIC_MODEL_INADEQUATE" for p in pilot),"pilot_frozen_followup_targets":len(eligible),
        "historical_dark_remnant_consistent":len(remnant),"published_parallax_model_modes":sum(map(len,modes.values())),"older_native_tables":len(old_by),
        "older_native_rows":sum(r["numeric_rows"] for r in old_by.values()),"older_native_unavailable":59-len(old_by),"older_classA":sum(r["native_version"]=="CLASSA-OPTIMIZED" for r in old_by.values()),
        "older_classB":sum(r["native_version"]=="CLASSB" for r in old_by.values()),"independently_measured_lens_mass_in_atlas":0,"new_BH_interpretations":0,
        "tier_counts":{tier:sum(e["tier"]==tier for e in events) for tier in ["REVIEW_REQUIRED","SUPPORTED_LENSING_EVENT","BLACK_HOLE_SEARCH_TARGET","BLACK_HOLE_CANDIDATE","STRONGLY_SUPPORTED_BLACK_HOLE_IDENTIFICATION"]}}
    benchmark_input=read("benchmark_input")
    benchmark_outcome=read("benchmark_recovery_outcome")
    sky=benchmark_input["sky_position_icrs_deg"]
    if sky!={"ra":267.9174583333,"dec":-29.89063888889}: raise ValueError("Benchmark source direction changed")
    if (benchmark_outcome.get("schema")!="bhsm.native_checkpoint_recovery_outcome.v1"
            or benchmark_outcome.get("status")!="CHECKPOINT_RECOVERY_NUMERICAL_STAGE_UNRESOLVED"
            or "accepted_mass_interval" not in benchmark_outcome
            or benchmark_outcome["accepted_mass_interval"] is not None
            or benchmark_outcome.get("accepted_black_hole_interpretation") is not False):
        raise ValueError("Re-review benchmark outcome before changing physical classification")
    benchmark={"event_id":"OGLE-2011-BLG-0462","known_aliases":["MOA-2011-BLG-191","OB110462","OGLE-11-462"],"cohorts":["SEPARATE_KNOWN_SYSTEM_BENCHMARK"],
        "source_direction":{"ra_deg":sky["ra"],"dec_deg":sky["dec"],"ra_hms":None,"dec_dms":None,"frame":"ICRS","equinox":None,"epoch":None,"role":"SOURCE_EVENT_DIRECTION","uncertainty":None,
            "provenance":[source_ref("benchmark_input","sky_position_icrs_deg")]},
        "lens":{key:None for key in ["position","position_epoch","position_covariance","distance_pc","mass_msun","proper_motion_mas_yr","radial_velocity_km_s"]},
        "tier":"STRONGLY_SUPPORTED_BLACK_HOLE_IDENTIFICATION","classification_source":"LITERATURE","benchmark_status":"KNOWN_PUBLISHED_ISOLATED_BLACK_HOLE",
        "tracker_recovery_status":"NOT_ESTABLISHED_NUMERICAL_STAGE_UNRESOLVED",
        "classification_basis":"PUBLISHED_HST_ASTROMETRY_PLUS_PHOTOMETRIC_PARALLAX_AND_LENS_LIGHT_LIMITS_NOT_A_TRACKER_RECOVERY",
        "classification_evidence":["Sahu et al.2025 reports an isolated BH using angular deflections, microlensing parallax and restrictive lens-light measurements; the published full analysis uses16 telescopes.","Current engine recovery remains unresolved; a published positive label is a benchmark label, not its own fitted result."],
        "quality_flags":["TRACKER_RECOVERY_NOT_ESTABLISHED","PUBLISHED_ANALYSIS_NOT_FULLY_REPLICATED","CROWDED_FIELD_PSF_SUBTRACTION_CRITICAL","NATIVE_ASTROMETRIC_ERRORS_NOT_SUPPLIED"],
        "photometric_assessment":{"tracker_status":"NUMERICAL_STAGE_UNRESOLVED","followup_eligible":None},
        "literature_assessment":{"published_lensing_designation":True,"published_BH_identification":True,"classification_source":"LITERATURE","current_BH_evidence_status":"STRONG_PUBLISHED_BH_SUPPORT_ENGINE_RECOVERY_OPEN",
            "interpretations":[{"publication":"Sahu et al.2025 ApJ983104","url":"https://doi.org/10.3847/1538-4357/adbe6e","author_version":"https://arxiv.org/html/2503.07820v2","role":"KNOWN_POSITIVE_LITERATURE_LABEL_NOT_ENGINE_MEASUREMENT","accepted_by_engine":False}],
            "published_mass_used_as_optimizer_target":False},
        "map_eligibility":{"sky_marker":True,"three_dimensional":False,"propagate_position":False},
        "missing_observations":["engine-accepted adequate joint fit and validated uncertainty coverage","supplied native per-exposure astrometric covariance or validated noise route","complete16-telescope native photometry for exact published-analysis replication","absolute lens position uncertainty and epoch for a lens marker"],
        "next_actions":["Complete independent numerical and noise-model validation, then uncertainty calibration without tuning to a published mass."],
        "provenance":[source_ref("benchmark_input","sky_position_icrs_deg"),source_ref("benchmark_recovery_outcome"),{"url":"https://doi.org/10.3847/1538-4357/adbe6e","role":"KNOWN_BH_PRIMARY_PUBLICATION"}],
        "source_records":{"native_input_metadata":{"schema":benchmark_input["schema"],"data_version":benchmark_input["data_version"],"target":benchmark_input["target"],"sky_position_icrs_deg":sky},"recovery_outcome":benchmark_outcome},
        "new_black_hole_interpretation":False,"accepted_engine_black_hole":False,"ranking":{"new_rank":None,"basis":"Calibration benchmark, outside candidate ranking."},"BHSM_interpretation":BHSM}
    result={"schema_version":SCHEMA,"metadata":{"scientific_as_of":freeze["scientific_as_of"],"formal_BHSM_repository":FORMAL,"formal_source_commit":COMMIT,
        "status":"CANDIDATE_LOCALIZATION_METADATA_ONLY_NO_NEW_FIT_OR_BH_IDENTIFICATION","input_freeze_sha256":digest(json_bytes(freeze)),"counts":counts,
        "BHSM_interpretation":BHSM,"map_warning":"Markers locate printed catalog source/event directions. J2000 is the equinox, not a supplied observation epoch; no present-day lens position, distance or exclusion zone is inferred. Unmarked sky is not evidence of black-hole absence.",
        "classification_policy":"Separate literature lens designation, tracker fit adequacy, frozen photometric followup qualification and BH-discriminating evidence. Scalar nonrejection alone establishes none of the latter physical classifications.",
        "mass_policy":"Lens physical values remain null. Historical mass/distance/probability summaries are retained only as attributed prior-conditional literature cells; duration and optimizer bounds are not mass bounds.",
        "known_system_benchmark_scope":"The separate benchmarks array contains OGLE-2011-BLG-0462, a literature-positive benchmark outside the155 pilot/parallax sources. It is not newly measured or accepted by this inventory.",
        "new_followup_ranking_produced":False,"fits_or_new_likelihood_calls":0,"all_source_outcomes_retained":True,
        "known_published_benchmarks_outside_cohort":1,"sky_markers_including_optional_benchmark":156,
        "rebuild_scope":"OFFLINE_METADATA_ONLY_CLASSIFICATION_AND_IDENTITY_RULES_RERUN; ORIGINAL_OBSERVATION_HASHES_AUDITED_AT_PREPARATION; NO_RAW_OBSERVATIONS_BUNDLED_OR_REFITTED",
        "source_snapshot_derivations":freeze["source_snapshot_derivations"],
        "sources":freeze["sources"]},"identity_crossmatch":{"policy":"Merge only exact DB/declared-alias identities with compatible printed directions; nearest neighbor alone does not merge crowded-field sources.","pairs":pairs},"events":events,"benchmarks":[benchmark]}
    validate_inventory(result)
    return result

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--freeze",required=True); ap.add_argument("--out",required=True)
    ap.add_argument("--source-map",help="Optional JSON role-to-original-source paths for independent original-byte hash verification")
    args=ap.parse_args(); fpath=Path(args.freeze); opath=Path(args.out)
    freeze=json.loads(fpath.read_bytes())
    if freeze["builder_sha256"]!=digest(Path(__file__).read_bytes()): raise ValueError("Builder source mismatch")
    original_map=None
    if args.source_map:
        map_path=Path(args.source_map)
        original_map={role:str((map_path.parent/Path(path)).resolve()) for role,path in json.loads(map_path.read_bytes()).items()}
        load_frozen(freeze,fpath.parent,original_map)
    result=build(freeze,fpath.parent)
    # Verify source bytes a second time before the exclusive new write.
    load_frozen(freeze,fpath.parent,original_map)
    with opath.open("xb") as output: output.write(json_bytes(result))
    print(json.dumps({"status":"BUILT_NO_NEW_FIT","sha256":digest(opath.read_bytes()),"counts":result["metadata"]["counts"]},indent=2))

if __name__ == "__main__": main()
