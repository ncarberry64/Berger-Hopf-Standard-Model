from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import letter
from pathlib import Path
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
font=Path('/usr/share/fonts/truetype/dejavu')
pdfmetrics.registerFont(TTFont('DejaVuSans',str(font/'DejaVuSans.ttf')))
pdfmetrics.registerFont(TTFont('DejaVuSans-Bold',str(font/'DejaVuSans-Bold.ttf')))
pdfmetrics.registerFontFamily('DejaVuSans',normal='DejaVuSans',bold='DejaVuSans-Bold',italic='DejaVuSans',boldItalic='DejaVuSans-Bold')
R=Path(__file__).parent
blue=HexColor('#183854'); ink=HexColor('#1c2833'); muted=HexColor('#536879'); pale=HexColor('#ecf3f7'); line=HexColor('#cbd8e0')
styles={
 'title':ParagraphStyle('Title',fontName='DejaVuSans-Bold',fontSize=29,leading=33,textColor=blue,spaceAfter=11),
 'sub':ParagraphStyle('Sub',fontName='DejaVuSans',fontSize=12,leading=16,textColor=muted,spaceAfter=12),
 'h':ParagraphStyle('Head',fontName='DejaVuSans-Bold',fontSize=14,leading=17,textColor=blue,spaceBefore=9,spaceAfter=5,keepWithNext=True),
 'p':ParagraphStyle('P',fontName='DejaVuSans',fontSize=10.1,leading=13.4,textColor=ink,spaceAfter=7),
 'table':ParagraphStyle('Cell',fontName='DejaVuSans',fontSize=9,leading=11.4,textColor=ink),
 'white':ParagraphStyle('Colname',fontName='DejaVuSans-Bold',fontSize=9,leading=11.4,textColor=white),
 'small':ParagraphStyle('Small',fontName='DejaVuSans',fontSize=9.3,leading=12.9,textColor=muted,spaceAfter=7),
 'lead':ParagraphStyle('Lead',fontName='DejaVuSans-Bold',fontSize=11.4,leading=15,textColor=blue),
}
story=[]
def p(s,k='p'):story.append(Paragraph(s,styles[k]))
def h(s):p(s,'h')
def callout(s):
 t=Table([[Paragraph(s,styles['lead'])]],[492])
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),pale),('LEFTPADDING',(0,0),(-1,-1),13),('RIGHTPADDING',(0,0),(-1,-1),13),('TOPPADDING',(0,0),(-1,-1),11),('BOTTOMPADDING',(0,0),(-1,-1),11)]))
 story.extend([t,Spacer(1,8)])
def table(rows,widths):
 t=Table([[Paragraph(c,styles['white' if i==0 else 'table']) for c in row] for i,row in enumerate(rows)],widths,repeatRows=1,hAlign='LEFT')
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),blue),('ROWBACKGROUNDS',(0,1),(-1,-1),[white,pale]),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,-1),(-1,-1),.5,line),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
 story.append(t)
def page():story.append(PageBreak())
p('Jackpot: the BHSM pin model','title')
p('Author review checkpoint  |  Norman Carberry  |  November 26, 2026','sub')
callout('Each singularity event couples the surface to the core. It acts as a pin that holds the envelope in a wider, lower settled configuration and contributes to the extra pull. The pins shape one collective well.')
h('The picture you have been describing')
p('We live <b>in</b> the membrane. The hypersphere is the background; the local, finite-depth shape is what changes around the galaxy and its surroundings. Your floating-ducks analogy describes bodies deforming the same surface. Your magnets-under-a-trampoline analogy describes how a pin connects the surface to the core and changes where the surrounding surface settles. These are guides to the model, not measured properties of space.')
p('The singularity is the coupling event, not a second copy of the black hole’s ordinary mass. The system settles to a lower state under the combined influence of the pins and surrounding matter. We are not assuming stored strain, a permanent pumping rate, equal strengths for all pins, or a strength proportional to black-hole mass. The background, local mass profiles, depth, and relative motion remain distinct inputs. Motion and history may affect which configuration is reached; they are not adjustment knobs for the held-out image.')
h('What the model has to account for')
p('<b>Envelope target = total pull inferred from the observations minus the pull of accounted-for ordinary matter.</b> In lensing, do the subtraction in the lensing field or its equivalent projected mass, with a common distance convention. “Galactic weight” remains the accounted-for matter: stars, gas where measured, and ordinary compact contributions counted once. A conventional halo estimate is a comparison for the residual, not a second term to add or an independent validation.')
p('Use the local bends at each lens plane together with the larger well of genuinely coupled bodies. A foreground or background galaxy can bend light without being part of that well. The three redshifts in Jackpot are three source planes, not three singularities. A nearer source may also deflect a farther source, which is distinct from pinning the main galaxy’s envelope.')
h('What a prediction means here')
p('Use the first two rings to calibrate the allowed response. Freeze the pin inputs and lens geometry before the third-source test. Start with the observed image A of source 3 and predict where B should be; B cannot choose pin sites, strengths, depth, or the winning geometry. The same field should also predict stellar motion through its own metric readout.')
page()
p('What we have actually tested','title')
p('Keep the successful control separate from the mechanisms it was used to test.','sub')
h('Calibration and held-out data')
p('At 5.15 and 7.63 kpc, the main-lens projected mass summaries are 3.08 and 4.44 × 10<super>11</super> solar masses. After subtracting stars and the fixed compact proxy once, the two residuals are <b>1.34 and 2.34 × 10<super>11</super></b> for the nominal Salpeter inventory, or <b>2.13 and 3.29 × 10<super>11</super></b> for Chabrier. These are correlated model summaries, not two direct force measurements. The MUSE-based lensing-equivalent inner slope is about 0.96; use the published stellar kinematics as a separate comparison, with care over overlap in the calibrations.')
table([
 ['What we tested','Nominal result','What it tells us'],
 ['Conventional composite, fixed stellar input','66 mas source-plane gap in the shared R1 Salpeter comparison. 0.097″ image-plane error when predicting B from A.','Working comparator. Nominal fit, not an exact historical replay or a statistical detection.'],
 ['Frozen two-ring envelope with inner curvature matched','174 mas source-plane gap vs 66 mas. The ordering was unclear in the paired position-jitter exercise.','A calibrated radial shape does not by itself predict the exterior.'],
 ['Light-tracing, collective-field and directional controls','Light-tracing shapes underbent the second ring. The archived normalized stellar-overlap contribution was much smaller than the need.','Do not multiply an unvalidated field or splice small effects together to declare closure.'],
 ['Static screened and equal-charge redistribution tests','Adding positive modes of the tested form could not reproduce the baseline curvature. The tested equal-charge alternatives did not close S3.','These restrict particular profiles, not the pin mechanism. Equal visible-only exterior charge is not your premise.'],
 ['Archived distributed radial law, fit to the excess at both rings','0.294″ image-plane error for B vs 0.097″ conventional in the nominal Salpeter comparison.','A real forward prediction, but it misses. The calculation did not solve a joint field driven by singularity pins.'],
],[134,180,178])
story.append(Spacer(1,8))
p('A separate null test preserved both ring mass summaries and the exterior charge while changing the far-ray bend. Matching those summaries does not uniquely fix the outer field. No comparison above establishes a physical BHSM pin solution or warrants transfer to HE 0435.','small')
p('Primary sources: <link href="https://arxiv.org/abs/2401.08771" color="#183854">Turner et al.: MUSE and mass-model constraints</link>; <link href="https://arxiv.org/abs/0801.1555" color="#183854">Gavazzi et al.: early-ring features</link>; <link href="https://arxiv.org/abs/2004.00649" color="#183854">Collett &amp; Smith: third-source image pair</link>; <link href="https://arxiv.org/abs/2104.12790" color="#183854">Smith &amp; Collett: spectroscopic source planes</link>.','small')
page()
p('The next calculation','title')
p('Build the well from the pins before tracing the light.','sub')
h('1. Separate the pins, the ordinary lens and the environment')
p('Use the main lens center as a first pin <b>hypothesis</b>, not as proof of a singularity census. Record which sites are measured, which are inferred, and which lack evidence; a galaxy center or mass peak alone is not an identified pin. Keep the existing compact proxy and stellar masses in the ordinary field. Test a central pin first and add a coupled candidate only with independent evidence or as an explicitly labeled sensitivity. Do not use a different-redshift source or a convenient residual direction as evidence for a pin.')
h('2. Solve one settled configuration')
p('Compare a regular reference and a pin-admitted state on the same local frame and ordinary inputs. Represent each pin by its admissible finite interface or trace condition on the same field, then solve all interfaces and the bulk together. In a linearized trial, a matrix of responses between pin traces makes their mutual influence explicit. That matrix and the boundary values must come from the model, not from a separate fitted halo for every pin. Where the junction selects a nonlinear branch, test stationarity and stability in that branch.')
p('The archived fourth-order equation supplies a possible static bulk response. It separates the flux controlling distant pull from the screened trace controlling part of the local shape. Its global zero-source identity does not set the galaxy’s local excess to zero. The archive still lacks the actual pin coupling, its effect on the stable branch, and the optical map. Do not assume that a lower internal energy supplies a particular gravitational charge or makes photons and stars respond to the same potential.')
h('3. Convert the resulting geometry to two predictions')
p('Compute the light-bending field from the settled metric and propagate the rays through their physical planes. Independently compute stellar motions from the same metric with the measured light weighting and instrumental resolution. Use the ring residuals to calibrate only declared shared inputs. Compare the third-source counterimage and signed displacement against the same conventional control, with uncertainty. If the data do not independently pin down the geometry, report sensitivity rather than tuning B.')
h('4. Keep the paper decision separate')
p('Jackpot is the calibration and validation example. HE 0435 stays an independent transfer test: carry over the law and boundary rules, not the Jackpot coefficients. Keep the paper in private author review until the pin calculation gives a testable result that adds something beyond the conventional fit.')
callout('Current checkpoint: the premise and test are defined. The next unknown is the pin-to-metric response, not the amount of extra pull to aim for.')
def footer(c,d):
 w,h=letter
 c.setStrokeColor(line);c.line(60,44,w-60,44)
 c.setFillColor(muted);c.setFont('DejaVuSans',9);c.drawString(60,29,'BHSM  /  Jackpot  /  Private author review');c.drawRightString(w-60,29,str(d.page))
doc=SimpleDocTemplate(str(R/'BHSM Jackpot - Pin Model Checkpoint.pdf'),pagesize=letter,leftMargin=60,rightMargin=60,topMargin=43,bottomMargin=54,title='Jackpot: the BHSM pin model',author='BHSM author review')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
