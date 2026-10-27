"""Integrity checks for the official geometry and local terrain deployment."""
import json
import struct
from pathlib import Path

root=Path(__file__).resolve().parents[1]/'dist/data'
for name,count,level in [('madrid',1,'2ndOrder'),('comunidades',3,'2ndOrder'),('provincias',6,'3rdOrder')]:
    data=json.loads((root/f'boundaries/{name}.geojson').read_text(encoding='utf-8'))
    assert len(data['features'])==count,(name,'feature count')
    for feature in data['features']:
        assert feature['properties']['nationalLevel']==level,(name,'level')
        geometry=feature['geometry']
        polygons=geometry['coordinates'] if geometry['type']=='MultiPolygon' else [geometry['coordinates']]
        for polygon in polygons:
            for ring in polygon:
                assert len(ring)>=4 and ring[0]==ring[-1],(name,'closed ring')
                assert all(-10<p[0]<5 and 35<p[1]<45 for p in ring),(name,'longitude/latitude')

tiles=list((root/'terrain/tiles').rglob('*.png'))
assert len(tiles)==80,'terrain pyramid incomplete'
for file in tiles:
    header=file.read_bytes()[:24]
    assert header[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',header[16:24])==(256,256),file
metadata=json.loads((root/'terrain/metadata.json').read_text(encoding='utf-8'))
assert metadata['source']['coverage_id']=='Elevacion4258_5'
assert metadata['grid']['width']==1024 and metadata['grid']['height']==1024
assert (root/'terrain/madrid-1024.f32').stat().st_size==1024*1024*4
poster=root.parent/'assets/landscape/guadarrama-official-poster.jpg'
assert poster.is_file() and poster.read_bytes()[:2]==b'\xff\xd8'
print('OK: official IGN geometry (3 regions, 6 provinces), 80 terrain tiles, source grid and rendered poster.')
