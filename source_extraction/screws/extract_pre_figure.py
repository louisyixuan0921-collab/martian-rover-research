from pathlib import Path
from PIL import Image
import numpy as np,json
root=Path(__file__).resolve().parent
im=np.array(Image.open(root/'PRE_page5_image0_Im5.jpg').convert('RGB'))
r,g,b=im[:,:,0].astype(int),im[:,:,1].astype(int),im[:,:,2].astype(int)
for color,mask in [('red',(r>100)&(r>g*1.5)&(r>b*1.3)),('blue',(b>90)&(b>r*1.5)&(g>r*1.3))]:
 seen=np.zeros(mask.shape,bool); groups=[]
 for y,x in zip(*np.where(mask)):
  if seen[y,x]: continue
  stack=[(y,x)];seen[y,x]=True;coords=[]
  while stack:
   yy,xx=stack.pop();coords.append((yy,xx))
   for y2,x2 in [(yy-1,xx),(yy+1,xx),(yy,xx-1),(yy,xx+1)]:
    if y2>=0 and y2<mask.shape[0] and x2>=0 and x2<mask.shape[1] and mask[y2,x2] and not seen[y2,x2]: seen[y2,x2]=True;stack.append((y2,x2))
  if len(coords)>20:
   a=np.array(coords);lo=a.min(0);hi=a.max(0);groups.append({'n':len(coords),'bbox':[*lo.tolist(),*hi.tolist()],'center':((lo+hi)/2).tolist()})
 print(color,json.dumps(groups))
seeds={'power':{'HGSL2':[(264,727),(358,635),(466,534),(588,411),(708,311)],'HGSL3':[(307,698),(427,559),(566,406),(723,219),(876,70)]},'velocity':{'HGSL2':[(295,1776),(400,1666),(539,1541),(657,1391),(748,1270)],'HGSL3':[(295,1797),(400,1690),(538,1570),(656,1425),(748,1309)]}}
centers={}
for panel,groups in seeds.items():
 centers[panel]={}
 for label,coords in groups.items():
  mask=(b>90)&(b>r*1.5)&(g>r*1.3) if label=='HGSL2' else (r>100)&(r>g*1.5)&(r>b*1.3)
  centers[panel][label]=[]
  for x,y in coords:
   crop=mask[y-16:y+17,x-15:x+16]; counts=crop.sum(1)
   hit=np.where(counts>=6)[0]; runs=np.split(hit,np.where(np.diff(hit)!=1)[0]+1);run=max(runs,key=len)
   ymin,ymax=int(run[0]),int(run[-1]);ys,xs=np.where(crop[ymin:ymax+1])
   center=[float((xs.min()+xs.max())/2+x-15),float((ymin+ymax)/2+y-16)]
   centers[panel][label].append(center)
print('CENTERS',json.dumps(centers,indent=2))
(root/'PRE_marker_centers.json').write_text(json.dumps(centers,indent=2))
