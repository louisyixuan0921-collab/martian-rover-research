"""Reconstruct Fig.4 coordinates; these are digitized means, never raw trials."""
from pathlib import Path
import json,csv,hashlib,statistics,math
r=Path(__file__).resolve().parent
c=json.loads((r/'PRE_marker_centers.json').read_text())
# Pixel coordinate zero is upper-left in the unmodified native 1020x2090 JPEG.
axes={'power':{'x0':114.,'x1':995.,'y0':878.5,'y1':13.,'xmax':15.,'ymax':15.},'velocity':{'x0':115.5,'x1':996.5,'y0':1966.5,'y1':1101.,'xmax':0.1,'ymax':0.1}}
# ±3 pixels encompasses center selection/JPEG/raster and approximate axis line centers.
# This is an analyst-selected extraction tolerance, not a sampling confidence interval.
bounds={'power':3*max(15/(995-114),15/(878.5-13)), 'velocity':3*max(.1/(996.5-115.5),.1/(1966.5-1101))}
rows=[]
for label,mass,length,beta in [('HGSL2',2.075,.14,1.44),('HGSL3',2.666,.18,1.85)]:
 for i,rpm in enumerate([13.7,27.4,41.,54.8,68.5]):
  vals={}
  for panel in axes:
   x,y=c[panel][label][i];a=axes[panel]
   vals[panel+'_predicted']=(x-a['x0'])/(a['x1']-a['x0'])*a['xmax']
   vals[panel+'_measured']=(a['y0']-y)/(a['y0']-a['y1'])*a['ymax']
  pp,pm,vp,vm=[vals[k] for k in ['power_predicted','power_measured','velocity_predicted','velocity_measured']]
  cp,cm=pp/(mass*9.81*vp),pm/(mass*9.81*vm)
  dp,dv=bounds['power'],bounds['velocity']
  row=dict(prototype=label,target_rpm=rpm,mass_kg=mass,pitch_m=.09,length_m=length,inner_radius_m=.045,outer_radius_m=.06,power_predicted_W=pp,power_measured_W=pm,velocity_predicted_m_s=vp,velocity_measured_m_s=vm,cot_predicted=cp,cot_measured=cm,power_digitization_bound_W=dp,velocity_digitization_bound_m_s=dv,power_sem_W='',velocity_sem_m_s='',source_page=5,source_figure='4a_4b',measurement_origin='published_experimental_mean_digitized',g_assumed_m_s2=9.81,source_base_target_rpm=[15,30,45,60,75][i],scale_a=1.2,scale_b=beta,power_source_relative_residual_pct=100*(pm/pp-1),velocity_source_relative_residual_pct=100*(vm/vp-1),cot_prediction_error_pct=100*(cp/cm-1),cot_measured_digitization_low=(pm-dp)/(mass*9.81*(vm+dv)),cot_measured_digitization_high=(pm+dp)/(mass*9.81*(vm-dv)),cot_predicted_digitization_low=(pp-dp)/(mass*9.81*(vp+dv)),cot_predicted_digitization_high=(pp+dp)/(mass*9.81*(vp-dv)),mass_unit_status='kg_inferred_source_table_omits_units',rpm_status='nominal_target_not_measured',pairing_status='ascending_speed_order_across_panels')
  rows.append(row)
with (r/'thoesen2020_screw_validation.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
summary={}
for label in ['HGSL2','HGSL3','pooled']:
 sub=rows if label=='pooled' else [z for z in rows if z['prototype']==label]
 out={'n_digitized_means':len(sub),'cot_measured_median':statistics.median(z['cot_measured'] for z in sub),'cot_measured_min':min(z['cot_measured'] for z in sub),'cot_measured_max':max(z['cot_measured'] for z in sub)}
 for var in ['power','velocity']:
  unit='W' if var=='power' else 'm_s'
  err=[(z[f'{var}_predicted_{unit}']-z[f'{var}_measured_{unit}'])/z[f'{var}_measured_{unit}'] for z in sub]
  out[var+'_mape_pct']=100*statistics.mean(abs(x) for x in err)
 out['cot_mape_pct']=statistics.mean(abs(z['cot_prediction_error_pct']) for z in sub)
 summary[label]=out
(r/'digitization_metadata.json').write_text(json.dumps({'image':'PRE_page5_image0_Im5.jpg','image_sha256':hashlib.sha256((r/'PRE_page5_image0_Im5.jpg').read_bytes()).hexdigest(),'pixel_coordinates':'native JPEG, x rightwards and y downwards','axes':axes,'marker_centers':c,'selection_bound_pixels':3,'bound_interpretation':'coordinate perturbation bound; not statistical CI','scalar_uncertainties_excluded':['mass unit interpretation','motor torque calibration','power/velocity covariance','actual rpm matching','mass measurement','sampling uncertainty'],'csv':'thoesen2020_screw_validation.csv','summaries':summary},indent=2))
print(json.dumps(summary,indent=2))
