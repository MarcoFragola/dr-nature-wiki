"""Prepare a separate official local DEM for the Cotos route lesson.

The approved regional cover is never modified. Uses numpy and Pillow.
Download: python scripts/prepare_route_terrain.py download
Package cached source: python scripts/prepare_route_terrain.py package
Add orthoimagery: python scripts/prepare_route_terrain.py imagery
"""
import hashlib
import json
import math
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / 'tmp/route-lesson-terrain'
OUT = ROOT / 'dist/data/route-lesson'
BASE = 'https://servicios.idee.es/wcs-inspire/mdt'
BBOX = [-4.035, 40.775, -3.875, 40.895]
PARAMS = {'service':'WCS','request':'GetCoverage','version':'2.0.1',
          'coverageId':'Elevacion4258_5',
          'subset':[f'long({BBOX[0]},{BBOX[2]})',f'lat({BBOX[1]},{BBOX[3]})'],
          'scaleSize':'long(1024),lat(1024)','format':'image/tiff',
          'outputCRS':'http://www.opengis.net/def/crs/EPSG/0/4326'}
URL = BASE + '?' + urllib.parse.urlencode(PARAMS, doseq=True)

def digest(data):
    return hashlib.sha256(data).hexdigest()

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'package'
    WORK.mkdir(parents=True, exist_ok=True)
    if mode == 'download':
        request = urllib.request.Request(URL, headers={'User-Agent':'DrNatureWiki/1.0 (Cotos local terrain lesson)'})
        with urllib.request.urlopen(request, timeout=60) as response:
            raw = response.read()
        assert raw[:2] in (b'II', b'MM'), 'WCS did not return a GeoTIFF'
        (WORK/'cotos-wcs.tif').write_bytes(raw)
        print(json.dumps({'downloaded_bytes':len(raw),'sha256':digest(raw)}))
    elif mode == 'imagery':
        # The current mosaic has a photographic seam across this close-up.
        # The official 2023 layer covers the lesson's route in one consistent area.
        image_bbox=[-3.995,40.798,-3.910,40.870]
        params={'SERVICE':'WMS','VERSION':'1.3.0','REQUEST':'GetMap','LAYERS':'PNOA2023',
                'STYLES':'','CRS':'EPSG:4326',
                'BBOX':','.join(map(str,[image_bbox[1],image_bbox[0],image_bbox[3],image_bbox[2]])),
                'WIDTH':2048,'HEIGHT':2048,'FORMAT':'image/jpeg'}
        url='https://www.ign.es/wms/pnoa-historico?'+urllib.parse.urlencode(params)
        with urllib.request.urlopen(url,timeout=60) as response:raw=response.read()
        assert raw[:2]==b'\xff\xd8', 'WMS did not return JPEG imagery'
        from PIL import Image
        from io import BytesIO
        image=Image.open(BytesIO(raw));assert image.size==(2048,2048)
        OUT.mkdir(parents=True,exist_ok=True);(OUT/'cotos-pnoa.jpg').write_bytes(raw)
        path=OUT/'metadata.json';metadata=json.loads(path.read_text(encoding='utf-8'))
        metadata['imagery']={'path':'cotos-pnoa.jpg','source_url':url,'layer':'PNOA2023',
            'provider':'PNOA / IGN / SCNE','license':'CC BY 4.0 scne.es','bbox':image_bbox,
            'crs':'EPSG:4326','size':[2048,2048],'sha256':digest(raw),'bytes':len(raw),
            'note':'Official historical 2023 layer, retained without pixel edits. Geographic positions are unchanged; the lesson camera keeps unrelated mosaic seams outside its close-up.'}
        path.write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({'imagery_layer':'PNOA2023','bytes':len(raw)}))
    elif mode == 'package':
        import numpy as np
        from PIL import Image
        image = Image.open(WORK/'cotos-wcs.tif')
        grid = np.asarray(image, dtype=np.float64)
        assert grid.shape == (1024,1024) and np.isfinite(grid).all()
        assert 500 < grid.min() < grid.max() < 2600
        dx,dy = image.tag_v2[33550][:2]
        west,north = image.tag_v2[33922][3:5]
        south,east = north-1024*dy,west+1024*dx
        assert 4326 in image.tag_v2[34735]
        assert all(abs(a-b)<1e-8 for a,b in zip([west,south,east,north], BBOX))
        OUT.mkdir(parents=True, exist_ok=True)
        raw = (WORK/'cotos-wcs.tif').read_bytes()
        (OUT/'cotos-wcs.tif').write_bytes(raw)
        records = []
        def tile_x(lon,z):return math.floor((lon+180)/360*2**z)
        def tile_y(lat,z):return math.floor((1-math.asinh(math.tan(math.radians(lat)))/math.pi)/2*2**z)
        for z in range(11,15):
            n = 2**z
            for x in range(tile_x(west,z),tile_x(east,z)+1):
                lon = ((x*256+np.arange(256)+.5)/(n*256)*360-180)[None,:]
                u = np.clip((lon-west)/dx-.5,0,1023)
                x0 = np.floor(u).astype(int);x1 = np.minimum(x0+1,1023);tx = u-x0
                for y in range(tile_y(north,z),tile_y(south,z)+1):
                    lat = np.degrees(np.arctan(np.sinh(math.pi*(1-2*(y*256+np.arange(256)+.5)/(n*256)))))[:,None]
                    v = np.clip((north-lat)/dy-.5,0,1023)
                    y0 = np.floor(v).astype(int);y1 = np.minimum(y0+1,1023);ty = v-y0
                    h = (grid[y0,x0]*(1-tx)+grid[y0,x1]*tx)*(1-ty)+(grid[y1,x0]*(1-tx)+grid[y1,x1]*tx)*ty
                    encoded = np.rint((h+32768)*256).astype(np.uint32)
                    rgba = np.empty((256,256,4),dtype=np.uint8)
                    rgba[:,:,0]=(encoded>>16)&255;rgba[:,:,1]=(encoded>>8)&255;rgba[:,:,2]=encoded&255;rgba[:,:,3]=255
                    path=OUT/f'tiles/{z}/{x}/{y}.png';path.parent.mkdir(parents=True,exist_ok=True)
                    Image.fromarray(rgba).save(path,compress_level=9)
                    decoded=rgba[:,:,0].astype(float)*256+rgba[:,:,1]+rgba[:,:,2]/256-32768
                    error=float(np.abs(decoded-h).max());assert error <= 1/512+1e-8
                    records.append({'path':path.relative_to(OUT).as_posix(),'sha256':digest(path.read_bytes()),'bytes':path.stat().st_size,'encoding_error_m':error})
        spacing=[dx*111320*math.cos(math.radians((north+south)/2)),dy*111320]
        metadata={'title':'Cotos - Zona del Zabala: local official elevation for the route lesson',
          'checked_at':'2026-10-28','provider':'IGN / SCNE','source_url':URL,'coverage_id':'Elevacion4258_5',
          'license':{'name':'CC BY 4.0','url':'https://creativecommons.org/licenses/by/4.0/','attribution':'CC BY 4.0 scne.es'},
          'grid':{'width':1024,'height':1024,'bbox':BBOX,'crs':'EPSG:4326','pixel_is_area':True,
                  'effective_spacing_m':spacing,'minimum_height_m':float(grid.min()),'maximum_height_m':float(grid.max())},
          'source_file':{'path':'cotos-wcs.tif','bytes':len(raw),'sha256':digest(raw)},
          'tiles':{'template':'data/route-lesson/tiles/{z}/{x}/{y}.png','minzoom':11,'maxzoom':14,'encoding':'terrarium','size':256,'bounds':BBOX,'files':records},
          'processing':'WCS server resampling to 1024 squared; local bilinear sampling at XYZ pixel centres. No added mountains or height scaling. Opaque edge padding is technical only and never extends the declared coverage.',
          'display':{'exaggeration':1,'note':'Natural elevation scale; separate from the approved regional cover.'},
          'limitations':['Effective spacing is approximately 13 m, not a delivered 5 m mesh.','No acquisition year or independent field survey is asserted.','GPX source has no elevation samples; this DEM is not a measured GPX altitude profile.']}
        (OUT/'metadata.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({'tiles':len(records),'effective_spacing_m':spacing,'tile_bytes':sum(r['bytes'] for r in records)}))
    else:
        raise SystemExit('Use download, package or imagery')
