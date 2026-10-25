"""Plot the frozen metadata inventory without a fit or a physical inference.

Usage: python plot_candidate_inventory.py --inventory inventory_v3.json --outdir figures
Requires Matplotlib. Outputs use exclusive writes and contain no PDF date fields.
Printed catalog directions are source/event directions, not current lens positions.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

EXPECTED_SHA256 = "4a76300f0e0e3883a0c9c343e1e0c5fbead595c9b4f333aaa01ec05c9ec9debc"
FORMAL_REPOSITORY = "https://github.com/ncarberry64/Berger-Hopf-Standard-Model"

def load_inventory(path):
    raw=Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=EXPECTED_SHA256:
        raise ValueError("The figure requires the exact frozen v3 inventory bytes")
    data=json.loads(raw)
    if data["schema_version"]!="bhsm.blackhole_tracker.candidate_inventory.v1":
        raise ValueError("Unsupported inventory schema")
    if len(data["events"])!=155 or len(data["benchmarks"])!=1:
        raise ValueError("Expected separate155-event cohort and one benchmark")
    if data["metadata"]["formal_BHSM_repository"]!=FORMAL_REPOSITORY:
        raise ValueError("Formal reviewer repository differs")
    for event in data["events"]+data["benchmarks"]:
        direction=event["source_direction"]
        if direction["role"]!="SOURCE_EVENT_DIRECTION" or direction["epoch"] is not None:
            raise ValueError("Figure is restricted to the frozen source/event directions")
        if not event["map_eligibility"]["sky_marker"] or event["map_eligibility"]["three_dimensional"] or event["map_eligibility"]["propagate_position"]:
            raise ValueError("Unsupported localization claim")
        if any(value is not None for value in event["lens"].values()):
            raise ValueError("The frozen figure supplies no inferred lens quantities")
    return data

def make_figure(data):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import MaxNLocator
    plt.rcParams.update({"font.family":"DejaVu Sans","font.size":8.5,
        "axes.labelsize":9,"axes.titlesize":11,"xtick.labelsize":8,"ytick.labelsize":8,
        "pdf.fonttype":42,"ps.fonttype":42,"axes.unicode_minus":False,
        "savefig.dpi":250,"figure.dpi":150,"path.simplify":False})
    fig,ax=plt.subplots(figsize=(7.2,4.9))
    fig.subplots_adjust(left=.105,right=.975,top=.86,bottom=.24)
    fig.suptitle("Historical source/event directions",y=.97,fontsize=11,fontweight="bold")
    fig.text(.54,.905,"155 distinct cohort events; one separate literature benchmark",ha="center",fontsize=8)
    groups=[("REVIEW_REQUIRED","Review required (94)","#8d949c","x",19,1.0),
            ("SUPPORTED_LENSING_EVENT","Literature parallax lens (58)","#2166ac","o",19,.65),
            ("BLACK_HOLE_SEARCH_TARGET","Qualified investigation target (3)","#b45d00","*",98,1.0)]
    for tier,label,color,marker,size,alpha in groups:
        rows=[e for e in data["events"] if e["tier"]==tier]
        ax.scatter([e["source_direction"]["ra_deg"] for e in rows],
            [e["source_direction"]["dec_deg"] for e in rows],s=size,c=color,marker=marker,
            alpha=alpha,label=label,linewidths=.8 if marker=="x" else .5,
            edgecolors=None if marker=="x" else "white",zorder=2 if tier=="REVIEW_REQUIRED" else 3)
    benchmark=data["benchmarks"][0]
    bd=benchmark["source_direction"]
    ax.scatter([bd["ra_deg"]],[bd["dec_deg"]],s=58,marker="D",color="#8b2c7b",
        edgecolors="white",linewidths=.7,zorder=5,label="Published BH benchmark (1); engine unresolved")
    labels={"OGLE3-ULENS-0585":("0585",(-48,-23)),
        "OGLE3-ULENS-3092":("3092",(-56,22)),
        "OGLE3-ULENS-PAR-13":("PAR-13",(-50,22))}
    for e in data["events"]:
        if e["event_id"] not in labels:continue
        label,offset=labels[e["event_id"]];d=e["source_direction"]
        ax.annotate(label,(d["ra_deg"],d["dec_deg"]),xytext=offset,textcoords="offset points",
            color="#7b4000",fontweight="bold",fontsize=8.5,zorder=6,
            arrowprops={"arrowstyle":"-","color":"#7b4000","lw":.7},
            bbox={"boxstyle":"round,pad=.15","facecolor":"white","edgecolor":"none","alpha":.9})
    ax.annotate("OB110462",(bd["ra_deg"],bd["dec_deg"]),xytext=(18,-27),textcoords="offset points",
        color="#752166",fontweight="bold",fontsize=8,zorder=6,
        arrowprops={"arrowstyle":"-","color":"#752166","lw":.7},
        bbox={"boxstyle":"round,pad=.15","facecolor":"white","edgecolor":"none","alpha":.9})
    all_rows=data["events"]+data["benchmarks"]
    ra=[e["source_direction"]["ra_deg"] for e in all_rows];dec=[e["source_direction"]["dec_deg"] for e in all_rows]
    ax.set_xlim(max(ra)+.7,min(ra)-.7)
    ax.set_ylim(min(dec)-1,max(dec)+1)
    ax.set_xlabel("Source/event right ascension (degrees; catalog directions)")
    ax.set_ylabel("Source/event declination (degrees)")
    ax.xaxis.set_major_locator(MaxNLocator(8));ax.yaxis.set_major_locator(MaxNLocator(7))
    ax.grid(color="#d6dce1",lw=.45,alpha=.75,zorder=0)
    for side in ["top","right"]:ax.spines[side].set_visible(False)
    ax.legend(loc="upper center",bbox_to_anchor=(.5,-.18),ncol=2,fontsize=7.2,
        frameon=False,columnspacing=1.4,handletextpad=.4)
    fig.text(.5,.025,"Markers are source/event directions, not current lens positions. No depth, motion or error regions are inferred.",
        ha="center",fontsize=7,color="#343b43")
    return fig

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--inventory",type=Path,required=True)
    ap.add_argument("--outdir",type=Path,required=True)
    args=ap.parse_args();data=load_inventory(args.inventory)
    args.outdir.mkdir(parents=True,exist_ok=True)
    outputs=[args.outdir/"candidate_inventory_sky.png",args.outdir/"candidate_inventory_sky.pdf"]
    if any(p.exists() for p in outputs):raise FileExistsError("Figure outputs already exist; use a fresh output directory")
    fig=make_figure(data)
    with outputs[0].open("xb") as stream:
        fig.savefig(stream,format="png",metadata={"Software":"BHSM Blackhole Tracker candidate-inventory figure"})
    with outputs[1].open("xb") as stream:
        fig.savefig(stream,format="pdf",metadata={"Title":"Historical source/event directions",
            "Author":"Norman P. Carberry","Subject":"Catalog metadata visualization; no inferred lens positions or new black-hole identification",
            "Keywords":"BHSM, Blackhole Tracker, source-event directions, "+FORMAL_REPOSITORY,
            "Creator":"BHSM Blackhole Tracker candidate-inventory figure","CreationDate":None,"ModDate":None})
    print(json.dumps({"inventory_sha256":EXPECTED_SHA256,"events":155,"separate_literature_benchmarks":1,
        "new_fits":0,"outputs":[{"name":p.name,"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()} for p in outputs]},indent=2))

if __name__=="__main__":main()
