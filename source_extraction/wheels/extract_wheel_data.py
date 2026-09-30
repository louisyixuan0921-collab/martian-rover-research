"""Source-figure digitization. No numbers below are newly measured rover data.
Run with bundled Python (pdfplumber, numpy, Pillow). See PROVENANCE.md.
"""
from pathlib import Path
import csv,json,hashlib
import numpy as np
import pdfplumber
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent

def csvwrite(name, rows):
 with (ROOT/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

# Moreland 2011 Fig4: manually located centers on native embedded image 772x614 px.
# Axes: TR0 x67; TR1 x748; DP0% y551; DP40% y13. Centers checked visually.
pts={'rolling':[(74,505),(92,461),(279,398),(331,384),(428,345),(523,332),(630,302)],
     'inching':[(74,470),(74,436),(279,264),(553,118)]}
rows=[]
im=Image.open(ROOT/'moreland2011_p3_image1_Im4.png').convert('RGB');draw=ImageDraw.Draw(im)
for mode,coords in pts.items():
 for j,(x,y) in enumerate(coords,1):
  rows.append(dict(source='Moreland2011',figure=4,pdf_page=3,mode=mode,point_id=j,
   travel_reduction=round((x-67)/681,6),drawbar_ratio=round((551-y)/538*.4,6),
   source_x_px=x,source_y_px=y,extraction_bound_tr=round(2/681,6),extraction_bound_dp=round(2/538*.4,6),
   medium='GRC-1',mass_kg=400,wheel_diameter_m=.71,wheel_width_m=.25,
   data_type='digitized marker center',uncertainty_type='assumed 2px extraction bound; not experimental CI'))
  draw.ellipse((x-9,y-9,x+9,y+9),outline='black',width=1);draw.text((x+11,y-11),f'{mode[0]}{j}',fill='black')
csvwrite('moreland2011_fig4_traction.csv',rows)
im.save(ROOT/'moreland2011_fig4_digitization_overlay.png')

# Creager NASA TM2014-218431. All numbers are PDF-figure reconstructions.
# Figure 11 TR uses hard-ground rolling baseline for BOTH modes.
# Figure 12 PN includes vehicle actuation AND hotel loads; PN uses 6-s smoothing.
with pdfplumber.open(ROOT/'creager2014_nasa.pdf') as doc:
 p16=doc.pages[15];p17=doc.pages[16]
 curves={16:p16.curves,17:p17.curves}
 # Axis x anchors = printed tick centers at 0,50,100,150; extrapolated 200.
 specs={
 'tr':dict(page=16,fig=11,x0=146.52,x200=488.941,y0=665.341,ymax=419.101,vmax=1.,
  indices={'pneumatic_rolling':[106],'pneumatic_inching':list(range(107,232)),
           'rigid_rolling':[247],'rigid_inching':list(range(248,386))},
  means={'pneumatic_inching':(470.101+472.861)/2,'rigid_inching':(466.681+469.201)/2}),
 'pn':dict(page=17,fig=12,x0=136.08,x200=506.881,y0=342.601,ymax=80.52,vmax=50.,
  indices={'pneumatic_rolling':[4],'pneumatic_inching':list(range(5,141)),
           'rigid_rolling':[160],'rigid_inching':list(range(161,342))},
  means={'pneumatic_inching':(292.021+294.541)/2,'rigid_inching':(285.661+288.181)/2})}
 def section(poly,x):
  ys=[];points=poly['pts']
  for a,b in zip(points,points[1:]+points[:1]):
   xa,ya=a;xb,yb=b
   if xa!=xb and min(xa,xb)<=x<max(xa,xb):ys.append(ya+(yb-ya)*(x-xa)/(xb-xa))
  if len(ys)<2:return None
  return (min(ys)+max(ys))/2,(max(ys)-min(ys))/2
 def line_samples(spec,key):
  polys=[curves[spec['page']][i] for i in spec['indices'][key]]
  a=min(c['x0'] for c in polys);b=max(c['x1'] for c in polys)
  xs=np.arange(a+.05,b,.05);out=[]
  for x in xs:
   se=[section(c,x) for c in polys if c['x0']<=x<c['x1']];se=[z for z in se if z is not None]
   if len(se)==1:out.append((x,*se[0]))
   elif len(se)>1:out.append((x,float(np.mean([z[0] for z in se])),max(z[1] for z in se)))
  return np.array(out)
 def data_at(spec,samples,t):
  x=spec['x0']+t/200*(spec['x200']-spec['x0'])
  if x<samples[0,0] or x>samples[-1,0]:return None
  y=np.interp(x,samples[:,0],samples[:,1]);half=np.interp(x,samples[:,0],samples[:,2])
  value=(spec['y0']-y)/(spec['y0']-spec['ymax'])*spec['vmax']
  bound=(half+.4)/(spec['y0']-spec['ymax'])*spec['vmax']
  return value,bound
 arrays={metric:{k:line_samples(spec,k) for k in spec['indices']} for metric,spec in specs.items()}
 for metric,spec in specs.items():
  rr=[]
  for key,sam in arrays[metric].items():
   for t in range(5,191,5):
    v=data_at(spec,sam,t)
    if v is None:continue
    rr.append(dict(source='Creager2014_NASA_TM_2014_218431',figure=spec['fig'],pdf_page=spec['page'],
      series=key,time_s=t,value=round(v[0],6),metric='travel_reduction_fraction' if metric=='tr' else 'total_system_power_number',
      extraction_bound=round(max(v[1],.005 if metric=='tr' else .25),6),
      bound_type='geometric line half-thickness plus axis allowance; floor .005 TR or .25 PN; not CI',
      data_type='interpolated published curve; correlated time samples',medium='Fillite',mass_kg=400,external_drawbar_ratio=0))
  csvwrite(f'creager2014_fig{spec["fig"]}_{metric}_curves.csv',rr)
 # Pair readouts at common time coordinates; no assumption of independent experimental repeats.
 paired=[]
 for tire in ['pneumatic','rigid']:
  key=tire+'_rolling'
  for t in [10,20,30,40,50,60,70,80]:
   tr,trb=data_at(specs['tr'],arrays['tr'][key],t)
   pn,pnb=data_at(specs['pn'],arrays['pn'][key],t)
   paired.append(dict(tire=tire,mode='rolling',time_s=t,travel_reduction=round(tr,6),total_power_number=round(pn,6),
    extraction_bound_tr=round(max(trb,.005),6),extraction_bound_pn=round(max(pnb,.25),6),
    energy_boundary='all actuation plus hotel loads',source='Creager2014_NASA_TM_2014_218431',figures='11 and 12',
    role='chronological conditional model test; not independent replicate',medium='Fillite',external_drawbar_ratio=0))
 csvwrite('creager2014_matched_rolling_times.csv',paired)
 means=[]
 for tire in ['pneumatic','rigid']:
  key=tire+'_inching';vals={}
  for metric,spec in specs.items():
   vals[metric]=(spec['y0']-spec['means'][key])/(spec['y0']-spec['ymax'])*spec['vmax']
  means.append(dict(tire=tire,mode='inching',mean_tr=round(vals['tr'],6),mean_total_power_number=round(vals['pn'],6),
   extraction_bound_tr=.005,extraction_bound_pn=.25,source='Creager2014_NASA_TM_2014_218431',figures='11 and 12',
   definition='separately published mean lines; mean(PN) times one minus mean(TR) is not mean normalized power',medium='Fillite',external_drawbar_ratio=0))
 csvwrite('creager2014_inching_published_mean_lines.csv',means)
 # Audit overlay at matched times on source page, visual verification only.
 for metric,spec in specs.items():
  p=doc.pages[spec['page']-1];im=p.to_image(resolution=150)
  for key,sam in arrays[metric].items():
   for t in ([10,20,30,40,50,60,70,80] if 'rolling' in key else [20,40,60,80,100,120,140,160]):
    v=data_at(spec,sam,t)
    if v is None:continue
    x=spec['x0']+t/200*(spec['x200']-spec['x0']);y=spec['y0']-v[0]/spec['vmax']*(spec['y0']-spec['ymax'])
    im.draw_circle((x,y),radius=2.8,fill=None,stroke='red')
  im.save(ROOT/f'creager2014_fig{spec["fig"]}_digitization_overlay.png')
(ROOT/'source_hashes.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.glob('*.pdf')},indent=2))
print('Source CSVs and overlays generated.')

# Optional external traction test, Creager 2012 Fig5; different wheel width and soil preparation.
# The plotted series' marker shapes (star=rolling, circle=inching) identify modes.
with pdfplumber.open(ROOT/'creager2012.pdf') as doc:
 p=doc.pages[5];out=[];centers=[]
 for idx,c in enumerate(p.curves):
  if idx>=29:continue # two circles in legend
  color=c['stroking_color'];tire='rigid' if color[0]<.3 else 'pneumatic'
  centers.append((tire,'inching',(c['x0']+c['x1'])/2,(c['top']+c['bottom'])/2,'circle',idx))
 for idx,c in enumerate(p.lines):
  color=c['stroking_color']
  if not isinstance(color,(tuple,list)) or len(color)!=3:continue
  if c['x1']-c['x0']<3.5 or abs(c['bottom']-c['top'])>.05:continue
  x=(c['x0']+c['x1'])/2;y=(c['top']+c['bottom'])/2
  if x<280 and y<185:continue # star legend
  tire='rigid' if color[0]<.3 else 'pneumatic'
  centers.append((tire,'rolling',x,y,'star-horizontal-stroke',idx))
 im=p.to_image(resolution=180)
 for tire,mode,x,y,kind,idx in centers:
  out.append(dict(source='Creager2012',figure=5,pdf_page=6,tire=tire,mode=mode,
    travel_reduction=round((361.7539167-y)/(361.7539167-132.8692387)*1.2-.2,6),
    drawbar_ratio=round((x-150.0597525)/(470.0129635-150.0597525)*.4,6),
    source_x_pt=round(x,6),source_y_pt=round(y,6),pdf_object_type=kind,pdf_object_index=idx,
    extraction_bound_tr=.005,extraction_bound_dp=.001,medium='GRC-1',wheel_diameter_in=28,wheel_width_in=7,
    data_type='vector marker center; source condition average',
    role='external traction comparison; different wheel width and soil preparation from Moreland2011'))
  im.draw_circle((x,y),radius=3,fill=None,stroke='red')
 out.sort(key=lambda a:(a['tire'],a['mode'],a['drawbar_ratio']))
 csvwrite('creager2012_fig5_traction.csv',out)
 im.save(ROOT/'creager2012_fig5_digitization_overlay.png')
print('Creager2012 external traction markers:',len(out))
