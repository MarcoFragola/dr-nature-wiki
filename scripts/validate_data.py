"""Comprobaciones de integridad, licencias y geometría del catálogo publicado."""
import json
import math
from pathlib import Path
root=Path(__file__).resolve().parents[1]
dist=root/'dist'
catalogue=json.loads((dist/'data/catalogue.json').read_text(encoding='utf-8'))
assets=json.loads((dist/'data/asset-map.json').read_text(encoding='utf-8'))
credits=json.loads((dist/'data/attribution.json').read_text(encoding='utf-8'))
sources=catalogue['sources']
places={p['id']:p for p in catalogue['places']}
species={p['id']:p for p in catalogue['species']}
routes={p['id']:p for p in catalogue['routes']}
assert len(places)==len(catalogue['places'])
assert len(routes)==len(catalogue['routes'])
assert len(species)==len(catalogue['species'])
allowed={'Madrid','Castilla y León','Castilla-La Mancha','Extremadura'}
assert set(catalogue['regions'])==allowed
def coord(c):
    assert len(c)>=2 and all(isinstance(v,(int,float)) and math.isfinite(v) for v in c)
    assert -180<=c[0]<=180 and -90<=c[1]<=90
def geometry(g):
    if g['type']=='Feature':return geometry(g['geometry'])
    if g['type']=='FeatureCollection':return sum(geometry(f) for f in g['features'])
    if g['type']=='LineString':
        assert len(g['coordinates'])>=2
        for c in g['coordinates']:coord(c)
        return len(g['coordinates'])
    if g['type']=='MultiLineString':return sum(geometry({'type':'LineString','coordinates':x}) for x in g['coordinates'])
    raise AssertionError('Unexpected geometry')
for p in places.values():
    coord(p['coordinates']);assert set(p['regions'])<=allowed
    assert all(x in species for x in p['species_ids'])
    assert all(x in routes for x in p['route_ids'])
    assert all(x in sources for x in p['sources'])
for s in species.values():assert all(x in sources for x in s['sources'])
points=0;track_count=0
for r in routes.values():
    assert r['place_id'] in places
    assert all(x in sources for x in r['source_ids'])
    if r['geometry_status']=='official_track':
        track_count+=1
        path=dist/f"data/tracks/{r['id']}.geojson"
        assert path.is_file() and (dist/f"data/tracks/{r['id']}.gpx").is_file()
        track=json.loads(path.read_text(encoding='utf-8'));points+=geometry(track)
        assert track['properties']['source']==r['track_url']
        assert r['start_coordinates'] is not None
    else:assert r['geojson_path'] is None
for group,items in assets.items():
    if group not in ['species','places']:continue
    for ident,item in items.items():
        if item is None:continue
        file=item['file'];assert (dist/'assets/photos'/file).is_file(),file
        credit=next((c for c in credits if c['file']==file),None)
        assert credit and credit['author'] and credit['source_url'] and credit['license'],file
assert track_count==8
assert len(places)>=53 and len(routes)>=55 and len(species)>=65
for item in [*places.values(), *species.values()]:
    assert item['summary']['es'] and item['summary']['en']
for item in routes.values():
    assert item['distance_km'] is None or item['distance_km'] > 0
print(f'OK: {len(places)} places, {len(routes)} routes, {len(species)} species, {track_count} official tracks, {points} coordinates. References and media licences present.')

# Official vector and elevation assets deployed with the atlas.
import runpy
runpy.run_path(str(root/'scripts/validate_geography.py'),run_name='__main__')

runpy.run_path(str(root/'scripts/validate_atlas.py'),run_name='__main__')

relations=json.loads((dist/'data/species-relations.json').read_text(encoding='utf-8'))
assert relations['observations']==[]
for r in relations['records']:
    assert r['place_id'] in places and r['species_id'] in species
    assert r['observation_id'] is None and not r['local_presence_confirmed']
    assert r['relation_type'] in ['managed_collection','regional_distribution','habitat_context']
    assert all(k in sources for k in r['source_ids'])

runpy.run_path(str(root/'scripts/validate_geographic_reference.py'),run_name='__main__')
