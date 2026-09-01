"""Generate deterministic, claim-safe BHSM museum simulation displays.

The seven primary exhibits use normalized explanatory data. They visualize the
kind of calculation performed by the documented machinery; they are not
measurements and do not supply physical predictions. The CMS gallery has its
own generator and is intentionally excluded here.
"""

from __future__ import annotations

import base64
import io
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
W, H = 1280, 720
FRAMES = 36
BG = "#06111c"
PANEL = "#0c1d2c"
GRID = "#17364c"
INK = "#eef6f8"
MUTED = "#9bb0bf"
CYAN = "#43d7e8"
GOLD = "#e5bc63"
GREEN = "#63d6a3"
RED = "#e37d7d"
VIOLET = "#a9a0ff"

FONT = Path("C:/Windows/Fonts/segoeui.ttf")
BOLD = Path("C:/Windows/Fonts/segoeuib.ttf")


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(BOLD if bold else FONT), size)


def text(draw: ImageDraw.ImageDraw, xy: tuple[float, float], value: str, size: int,
         fill: str = INK, *, bold: bool = False, anchor: str = "la") -> None:
    draw.text(xy, value, font=font(size, bold), fill=fill, anchor=anchor)


def chrome(draw: ImageDraw.ImageDraw, title: str, label: str) -> None:
    draw.rectangle((0, 0, W, H), fill=BG)
    draw.rectangle((0, 0, W, 92), fill="#091827")
    draw.line((36, 82, W - 36, 82), fill=CYAN, width=2)
    text(draw, (40, 38), title, 31, bold=True)
    text(draw, (W - 40, 40), label, 16, MUTED, bold=True, anchor="ra")
    text(draw, (40, 688), "EXPLANATORY SIMULATION • NORMALIZED VALUES • NOT A PHYSICAL PREDICTION", 16, GOLD, bold=True)
    text(draw, (W - 40, 688), "BHSM MUSEUM", 15, MUTED, bold=True, anchor="ra")


def panel(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    draw.rounded_rectangle(box, radius=12, fill=PANEL, outline=GRID, width=2)


def axes(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], xlabel: str, ylabel: str) -> None:
    x0, y0, x1, y1 = box
    for i in range(1, 5):
        x = x0 + i * (x1 - x0) / 5
        y = y0 + i * (y1 - y0) / 5
        draw.line((x, y0, x, y1), fill=GRID, width=1)
        draw.line((x0, y, x1, y), fill=GRID, width=1)
    draw.line((x0, y1, x1, y1), fill=MUTED, width=2)
    draw.line((x0, y0, x0, y1), fill=MUTED, width=2)
    text(draw, ((x0 + x1) / 2, y1 + 28), xlabel, 17, MUTED, anchor="ma")
    if ylabel:
        text(draw, (x0 + 10, (y0 + y1) / 2), ylabel, 17, MUTED, anchor="lm")


def line_plot(draw: ImageDraw.ImageDraw, points: list[tuple[float, float]], color: str, width: int = 3) -> None:
    draw.line(points, fill=color, width=width, joint="curve")


def action_frame(k: int) -> Image.Image:
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    chrome(d, "ACTION LANDSCAPE + DERIVATIVE SCOPE", "ENGINE VIEW 01")
    panel(d, (36, 116, 600, 638)); panel(d, (628, 116, 1244, 638))
    text(d, (58, 142), "Normalized action landscape", 22, bold=True)
    text(d, (650, 142), "Live derivative traces from the same sampled action", 20, bold=True)
    cx, cy = 318, 376
    for j in range(8):
        rx, ry = 55 + j * 28, 30 + j * 22
        color = CYAN if j % 2 else GRID
        d.ellipse((cx-rx, cy-ry, cx+rx, cy+ry), outline=color, width=2)
    phase = 2 * math.pi * k / FRAMES
    px = cx + 205 * math.cos(phase)
    py = cy + 150 * math.sin(phase) * 0.68
    d.line((cx, cy, px, py), fill=GOLD, width=2)
    d.ellipse((px-10, py-10, px+10, py+10), fill=GOLD, outline=INK, width=3)
    text(d, (58, 600), "The gold sample moves across one action surface.", 18, MUTED)
    labels = (("S²  propagation", CYAN, 0.0), ("S³  cubic interaction", GOLD, 1.1), ("S⁴  quartic interaction", VIOLET, 2.2))
    for row, (lab, color, shift) in enumerate(labels):
        top = 185 + row * 135
        box = (670, top, 1205, top + 88)
        axes(d, box, "sample position", "")
        pts = []
        for i in range(100):
            x = box[0] + i / 99 * (box[2]-box[0])
            value = math.sin(i / 99 * math.pi * 2 + shift) * (0.22 + row * .08)
            y = (box[1]+box[3])/2 - value * 90
            pts.append((x, y))
        line_plot(d, pts, color)
        cursor = box[0] + (k / (FRAMES-1)) * (box[2]-box[0])
        d.line((cursor, box[1], cursor, box[3]), fill=INK, width=2)
        text(d, (680, top - 18), lab, 18, color, bold=True)
    return im


def spectrum_frame(k: int) -> Image.Image:
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    chrome(d, "SPECTRUM + AMPLITUDE MONITOR", "ENGINE VIEW 02")
    panel(d, (36, 116, 1244, 420)); panel(d, (36, 444, 1244, 638))
    text(d, (58, 142), "Quadratic response — pole locations and residue strength", 22, bold=True)
    box = (76, 180, 1200, 380); axes(d, box, "normalized spectral coordinate", "response")
    poles = [(0.18, .65, CYAN), (.39, .92, GOLD), (.64, .72, VIOLET), (.83, .52, GREEN)]
    pts=[]
    for i in range(360):
        u=i/359
        val=sum(a/(1+((u-p)/.018)**2) for p,a,_ in poles)
        pts.append((box[0]+u*(box[2]-box[0]), box[3]-min(val,1.08)*165))
    line_plot(d, pts, CYAN, 3)
    revealed = int((k / (FRAMES-1))*len(poles)) + 1
    for idx,(p,a,c) in enumerate(poles):
        x=box[0]+p*(box[2]-box[0]); y=box[3]-a*150
        if idx < revealed:
            d.line((x, box[3], x, y), fill=c, width=4)
            d.ellipse((x-7,y-7,x+7,y+7), fill=c)
            text(d,(x,y-18),f"p{idx+1}",16,c,bold=True,anchor="ms")
    text(d, (58, 470), "Amplitude monitor after inverse-free LSZ normalization", 20, bold=True)
    wave=(76,505,1200,600); axes(d,wave,"phase sample","")
    pts=[]
    phase=2*math.pi*k/FRAMES
    for i in range(300):
        u=i/299; y=(wave[1]+wave[3])/2-math.sin(u*math.pi*8-phase)*29*(.4+.6*u)
        pts.append((wave[0]+u*(wave[2]-wave[0]),y))
    line_plot(d,pts,GOLD,3)
    cursor=wave[0]+(k/(FRAMES-1))*(wave[2]-wave[0])
    d.line((cursor,wave[1],cursor,wave[3]),fill=INK,width=3)
    text(d,(1110,470),"LSZ PULSE",16,GOLD,bold=True,anchor="ra")
    return im


def forecast_frame(k: int) -> Image.Image:
    im=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(im)
    chrome(d,"STRUCTURAL SPECTRAL SCAN","ENGINE VIEW 03")
    panel(d,(36,116,1244,638)); text(d,(58,142),"Classifier response across a normalized structural spectrum",22,bold=True)
    box=(92,190,1198,548); axes(d,box,"normalized scan coordinate","classification")
    rows=[("ADMISSIBLE BAND",GREEN,0.18,0.44), ("NULL WINDOW",RED,0.48,0.62), ("CLOSED REGION",GOLD,0.66,0.78), ("UNRESOLVED",VIOLET,0.82,0.97)]
    reveal=box[0]+(k/(FRAMES-1))*(box[2]-box[0])
    for idx,(label,color,a,b) in enumerate(rows):
        y=225+idx*76
        d.line((box[0],y+24,box[2],y+24),fill=GRID,width=18)
        xa=box[0]+a*(box[2]-box[0]); xb=box[0]+b*(box[2]-box[0])
        if reveal>xa:
            d.line((xa,y+24,min(reveal,xb),y+24),fill=color,width=24)
        text(d,(box[0],y-8),label,17,color,bold=True)
    d.line((reveal,box[1],reveal,box[3]),fill=INK,width=4)
    d.polygon([(reveal-8,box[1]),(reveal+8,box[1]),(reveal,box[1]+14)],fill=INK)
    text(d,(58,598),"The moving scan distinguishes allowed, absent, closed, and unresolved regions.",18,MUTED)
    return im


def form_factor_frame(k:int)->Image.Image:
    im=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(im)
    chrome(d,"ELECTROMAGNETIC FORM-FACTOR PROJECTION","ENGINE VIEW 04")
    panel(d,(36,116,1244,638)); text(d,(58,142),"Normalized F₁(q²) and F₂(q²) projection monitor",22,bold=True)
    box=(92,190,1198,560); axes(d,box,"q² → 0 (normalized)","projected form factor")
    curves=[]
    for color,fun in [(CYAN,lambda u:.72-.27*u+.05*math.sin(u*5)),(GOLD,lambda u:.18+.22*(1-u)**2)]:
        pts=[]
        for i in range(240):
            u=i/239; pts.append((box[0]+u*(box[2]-box[0]),box[3]-fun(u)*390))
        line_plot(d,pts,color,4); curves.append(pts)
    text(d,(1060,235),"F₁(q²)",18,CYAN,bold=True); text(d,(1060,405),"F₂(q²)",18,GOLD,bold=True)
    u=1-k/(FRAMES-1); x=box[0]+u*(box[2]-box[0])
    d.line((x,box[1],x,box[3]),fill=INK,width=3)
    for pts,color in zip(curves,(CYAN,GOLD)):
        p=pts[round(u*(len(pts)-1))]; d.ellipse((p[0]-8,p[1]-8,p[0]+8,p[1]+8),fill=color,outline=INK,width=2)
    d.ellipse((box[0]-11,box[3]-.40*390-11,box[0]+11,box[3]-.40*390+11),outline=GOLD,width=4)
    text(d,(box[0]+18,box[3]-.40*390-22),"F₂(0) READOUT GATED",17,GOLD,bold=True)
    text(d,(58,605),"The cursor approaches zero momentum; no numerical muon g−2 value is asserted.",18,MUTED)
    return im


def collision_frame(k:int)->Image.Image:
    im=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(im)
    chrome(d,"2 → 2 COLLISION EVENT DISPLAY","ENGINE VIEW 05")
    panel(d,(36,116,850,638)); panel(d,(874,116,1244,638))
    text(d,(58,142),"Simulated topology in normalized event coordinates",21,bold=True)
    cx,cy=445,382
    for r in (70,140,210): d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=GRID,width=2)
    d.line((cx-340,cy,cx+340,cy),fill=GRID,width=1); d.line((cx,cy-230,cx,cy+230),fill=GRID,width=1)
    incoming=[(cx-320,cy-90,cx,cy),(cx+320,cy+90,cx,cy)]
    outgoing=[(cx,cy,cx+300,cy-185),(cx,cy,cx-280,cy+200)]
    for line in incoming: d.line(line,fill=CYAN,width=4)
    for line in outgoing: d.line(line,fill=GOLD,width=4)
    u=min(1,k/(FRAMES*.48)) if k<FRAMES/2 else min(1,(k-FRAMES/2)/(FRAMES*.48))
    lines=incoming if k<FRAMES/2 else outgoing
    for x0,y0,x1,y1 in lines:
        px=x0+(x1-x0)*u; py=y0+(y1-y0)*u; d.ellipse((px-10,py-10,px+10,py+10),fill=INK,outline=CYAN if k<FRAMES/2 else GOLD,width=3)
    d.ellipse((cx-15,cy-15,cx+15,cy+15),fill=RED,outline=INK,width=3)
    text(d,(cx,cy+42),"shared amplitude vertex",17,INK,anchor="ma")
    text(d,(896,142),"Kinematic monitor",21,bold=True)
    labels=[("incoming balance",.94,GREEN),("threshold check",.77,GOLD),("angular average",.61,CYAN),("symmetry factor",.84,VIOLET)]
    for i,(lab,val,color) in enumerate(labels):
        y=205+i*88; text(d,(896,y),lab,17,MUTED)
        d.line((896,y+32,1208,y+32),fill=GRID,width=12)
        d.line((896,y+32,896+val*312,y+32),fill=color,width=12)
        text(d,(1208,y),f"{val:.2f}",17,color,bold=True,anchor="ra")
    text(d,(896,570),"Topology only",19,RED,bold=True); text(d,(896,600),"No cross-section value",17,MUTED)
    return im


def decay_frame(k:int)->Image.Image:
    im=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(im)
    chrome(d,"DECAY CHANNEL + STABILITY LEDGER","ENGINE VIEW 06")
    panel(d,(36,116,780,638)); panel(d,(804,116,1244,638))
    text(d,(58,142),"Channel state monitor",22,bold=True); cx,cy=405,380
    d.ellipse((cx-54,cy-54,cx+54,cy+54),fill="#143047",outline=INK,width=3); text(d,(cx,cy),"STATE",20,INK,bold=True,anchor="mm")
    channels=[(-2.55,"allowed",GREEN),(-1.55,"forbidden",RED),(-.45,"closed",GOLD),(.55,"unresolved",VIOLET),(1.55,"allowed",GREEN),(2.55,"forbidden",RED)]
    pulse=(k%FRAMES)/FRAMES
    for idx,(a,status,color) in enumerate(channels):
        ex=cx+260*math.cos(a); ey=cy+205*math.sin(a)
        d.line((cx+58*math.cos(a),cy+58*math.sin(a),ex,ey),fill=color,width=4 if status=="allowed" else 2)
        d.ellipse((ex-24,ey-24,ex+24,ey+24),outline=color,width=4)
        if status=="allowed":
            px=cx+(58+(260-58)*pulse)*math.cos(a); py=cy+(58+(205-58)*pulse)*math.sin(a)
            d.ellipse((px-8,py-8,px+8,py+8),fill=INK,outline=color,width=2)
        if status=="forbidden":
            d.line((ex-17,ey-17,ex+17,ey+17),fill=RED,width=5); d.line((ex-17,ey+17,ex+17,ey-17),fill=RED,width=5)
    text(d,(826,142),"Complete ledger",22,bold=True)
    ledger=[("CHANNEL A","ALLOWED",GREEN),("CHANNEL B","EXACTLY FORBIDDEN",RED),("CHANNEL C","KINEMATICALLY CLOSED",GOLD),("CHANNEL D","UNRESOLVED",VIOLET)]
    for i,(name,status,color) in enumerate(ledger):
        y=210+i*90; text(d,(828,y),name,16,MUTED,bold=True); text(d,(1212,y),status,15,color,bold=True,anchor="ra")
        d.line((828,y+34,1212,y+34),fill=GRID,width=2)
    text(d,(828,570),"STABILITY STATUS",17,MUTED,bold=True); text(d,(1212,570),"NOT ESTABLISHED",17,RED,bold=True,anchor="ra")
    text(d,(58,605),"A stable label requires every possible channel to be closed or exactly forbidden.",18,MUTED)
    return im


def firewall_frame(k:int)->Image.Image:
    im=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(im)
    chrome(d,"NO-FIT PROVENANCE + RESIDUAL MONITOR","ENGINE VIEW 07")
    panel(d,(36,116,1244,410)); panel(d,(36,434,1244,638))
    text(d,(58,142),"Comparison residuals — measurement enters only here",22,bold=True)
    box=(80,182,1200,360); axes(d,box,"comparison index","prediction − measurement")
    pts=[]
    for i in range(180):
        u=i/179; val=.18*math.sin(u*math.pi*10)+.08*math.cos(u*math.pi*23)
        pts.append((box[0]+u*(box[2]-box[0]),(box[1]+box[3])/2-val*240))
    line_plot(d,pts,CYAN,3); d.line((box[0],(box[1]+box[3])/2,box[2],(box[1]+box[3])/2),fill=GOLD,width=2)
    cursor=box[0]+k/(FRAMES-1)*(box[2]-box[0]); d.line((cursor,box[1],cursor,box[3]),fill=INK,width=3)
    text(d,(58,460),"Immutable upstream provenance",21,bold=True)
    rows=[("branch", "24", GREEN),("action coefficients", "LOCKED", GREEN),("normalization", "LOCKED", GREEN),("scale", "ACTION-OWNED", GREEN)]
    for i,(name,value,color) in enumerate(rows):
        y=502+i*30; text(d,(80,y),name,16,MUTED); text(d,(420,y),value,16,color,bold=True); d.line((560,y,1180,y),fill=GRID,width=8)
        d.line((560,y,560+(500 if i!=k//9 else 500),y),fill=color,width=8)
    text(d,(1184,476),"AUDIT PASS",18,GREEN,bold=True,anchor="ra")
    text(d,(800,604),"Measured values cannot retune upstream choices.",18,GOLD,bold=True,anchor="ma")
    return im


RENDERERS = {
    "bhsm_geometry_to_prediction": action_frame,
    "bhsm_universal_predictive_engine": spectrum_frame,
    "bhsm_spectral_forecast": forecast_frame,
    "bhsm_muon_g2_pipeline": form_factor_frame,
    "bhsm_collision_predictor": collision_frame,
    "bhsm_decay_stability_engine": decay_frame,
    "bhsm_no_fit_firewall": firewall_frame,
}


def svg_document(name: str, still: Image.Image) -> str:
    data = io.BytesIO(); still.save(data, format="PNG", optimize=True)
    encoded = base64.b64encode(data.getvalue()).decode("ascii")
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" viewBox="0 0 1280 720" data-visual-kind="simulation-engine">
<title>BHSM explanatory simulation engine display</title>
<desc>Normalized animated scientific visualization. This is not measured data and not a physical prediction.</desc>
<metadata>Generator: docs/assets/generate_bhsm_museum_engines.py; scope: explanatory simulation; claim boundary: physical promotion gated.</metadata>
<image width="1280" height="720" href="data:image/png;base64,{encoded}"/>
<line x1="80" y1="100" x2="80" y2="640" stroke="#eef6f8" stroke-width="3" opacity="0.72">
  <animate attributeName="x1" values="80;1200;80" dur="5s" repeatCount="indefinite"/>
  <animate attributeName="x2" values="80;1200;80" dur="5s" repeatCount="indefinite"/>
  <animate attributeName="opacity" values="0;0.72;0" dur="5s" repeatCount="indefinite"/>
</line>
</svg>'''


def main() -> None:
    for name, renderer in RENDERERS.items():
        frames = [renderer(k) for k in range(FRAMES)]
        frames[-1].save(ROOT / f"{name}.png", optimize=True)
        frames[0].save(
            ROOT / f"{name}_animated.gif",
            save_all=True,
            append_images=frames[1:],
            duration=90,
            loop=0,
            optimize=True,
        )
        (ROOT / f"{name}.svg").write_text(svg_document(name, frames[-1]), encoding="utf-8")
        print(f"generated {name}")


if __name__ == "__main__":
    main()
