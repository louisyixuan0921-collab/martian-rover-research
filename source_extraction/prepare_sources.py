"""Fetch the publicly hosted primary PDFs and extract native source figures.
This optional step is not needed to rerun MATLAB from the supplied CSVs.
Requires pypdf. Files are stored beside the corresponding extraction scripts.
"""
from pathlib import Path
from urllib.request import urlretrieve
import hashlib,json
from pypdf import PdfReader
root=Path(__file__).resolve().parent
sources=[
 ('wheels','moreland2011.pdf','https://publications.ri.cmu.edu/storage/publications/pub_files/2011/3/inching_ieeeAERO2011.pdf'),
 ('wheels','creager2012.pdf','https://ntrs.nasa.gov/api/citations/20140008625/downloads/20140008625.pdf'),
 ('wheels','creager2014_nasa.pdf','https://ntrs.nasa.gov/api/citations/20150000897/downloads/20150000897.pdf'),
 ('screws','Thoesen_2020_PRE.pdf','https://labs.engineering.asu.edu/birth/wp-content/uploads/sites/190/2021/02/PhysRevE.102.032902.pdf')]
for folder,name,url in sources:
 p=root/folder/name
 if not p.exists():urlretrieve(url,p)
 if not p.read_bytes().startswith(b'%PDF'):raise ValueError(f'{name}: the server did not return a PDF')
 print(name,hashlib.sha256(p.read_bytes()).hexdigest())
# Preserve original native image bytes. Dimensions identify the correct plot.
for folder,pdf,page,size,name in [
 ('wheels','moreland2011.pdf',2,(772,614),'moreland2011_p3_image1_Im4.png'),
 ('screws','Thoesen_2020_PRE.pdf',4,(1020,2090),'PRE_page5_image0_Im5.jpg')]:
 images=PdfReader(root/folder/pdf).pages[page].images
 matches=[x for x in images if x.image.size==size]
 if len(matches)!=1:raise ValueError(f'{pdf}: expected one native figure of size {size}, found {len(matches)}')
 (root/folder/name).write_bytes(matches[0].data)
 print('Extracted',name)
print('Now run wheels/extract_wheel_data.py and screws/extract_pre_figure.py, then screws/build_screw_csv.py.')
