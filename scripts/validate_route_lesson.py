"""Verify the separate route-scene assets, source hashes and real coverage."""
import hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image

root=Path(__file__).resolve().parents[1]/'dist'
directory=root/'data/route-lesson'
meta=json.loads((directory/'metadata.json').read_text(encoding='utf-8'))
assert meta['coverage_id']=='Elevacion4258_5'
assert meta['display']['exaggeration']==1
assert all(12<v<14 for v in meta['grid']['effective_spacing_m'])
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
source=directory/meta['source_file']['path']
assert sha(source)==meta['source_file']['sha256']
grid=np.asarray(Image.open(source),dtype=float)
assert grid.shape==(1024,1024) and np.isfinite(grid).all() and grid.min()>500 and grid.max()<2600
assert meta['imagery']['layer']=='PNOA2023'
assert sha(directory/meta['imagery']['path'])==meta['imagery']['sha256']
assert Image.open(directory/meta['imagery']['path']).size==tuple(meta['imagery']['size'])
max_delta=0
for tile in meta['tiles']['files']:
    p=directory/tile['path'];assert sha(p)==tile['sha256']
    rgba=np.asarray(Image.open(p));assert rgba.shape==(256,256,4) and (rgba[:,:,3]==255).all()
    h=rgba[:,:,0].astype(float)*256+rgba[:,:,1]+rgba[:,:,2]/256-32768
    assert h.min()>500 and h.max()<2600
    max_delta=max(max_delta,float(np.abs(np.diff(h,axis=0)).max()),float(np.abs(np.diff(h,axis=1)).max()))
assert max_delta<100, 'Unexpected vertical discontinuity / invalid elevation pixel'
track=json.loads((root/'data/tracks/penalara-zabala.geojson').read_text(encoding='utf-8'))
west,south,east,north=meta['imagery']['bbox']
for point in track['geometry']['coordinates']:
    assert west<point[0]<east and south<point[1]<north
    assert len(point)==2 # the original official file does not contain elevations
print(f'OK: route lesson uses {len(meta["tiles"]["files"])} verified local IGN tiles (~13 m), PNOA2023 and the unmodified GPX. No invalid elevation cliffs; maximum neighbouring-pixel difference {max_delta:.2f} m.')
