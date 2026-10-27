"""Check the complete static geographic reference without contacting providers."""
import json, math, hashlib, gzip
from collections import Counter
from pathlib import Path
root=Path(__file__).resolve().parents[1]/'dist'
data=root/'data/geography'
index=json.loads((data/'index.json').read_text(encoding='utf-8'))
metadata=json.loads((data/'metadata.json').read_text(encoding='utf-8'))
base_columns=['id','name','type','bbox','chunk','minZoom']
assert index['search_columns'] in [base_columns,base_columns+['regionMask']]
regional=len(index['search_columns'])==7
region_bits={1:'Madrid',2:'Castilla y León',4:'Castilla-La Mancha'}
geometry_hash=hashlib.sha256()
assert len(index['search'])==index['total_features']
seen={};types=Counter();invalid=[]

def positions(c):
    if c and isinstance(c[0],(int,float)):
        assert len(c)==2 and all(math.isfinite(n) for n in c)
        assert -180<=c[0]<=180 and -90<=c[1]<=90
        yield c
    else:
        for child in c:yield from positions(child)

def valid_geometry(g):
    if g['type']=='LineString':return len(g['coordinates'])>=2 and len(set(map(tuple,g['coordinates'])))>=2
    if g['type']=='MultiLineString':return all(valid_geometry({'type':'LineString','coordinates':c}) for c in g['coordinates'])
    polygons=[g['coordinates']] if g['type']=='Polygon' else g['coordinates']
    return all(len(ring)>=4 and ring[0]==ring[-1] for polygon in polygons for ring in polygon)

def read_chunk(path,chunk):
    payload=path.read_bytes()
    if 'sha256' in chunk:assert hashlib.sha256(payload).hexdigest()==chunk['sha256']
    raw=gzip.decompress(payload) if path.suffix=='.gz' else payload
    if 'uncompressed_sha256' in chunk:assert hashlib.sha256(raw).hexdigest()==chunk['uncompressed_sha256']
    if 'uncompressed_bytes' in chunk:assert len(raw)==chunk['uncompressed_bytes']
    return json.loads(raw)

for i,chunk in enumerate(index['chunks']):
    path=(root/chunk['file']).resolve();assert path.is_relative_to(root.resolve())
    assert path.stat().st_size==chunk['bytes']
    if 'sha256' in chunk:assert hashlib.sha256(path.read_bytes()).hexdigest()==chunk['sha256']
    fc=read_chunk(path,chunk);assert fc['type']=='FeatureCollection' and len(fc['features'])==chunk['count']
    for f in fc['features']:
        p=f['properties'];assert f['id']==p['id'] and f['id'] not in seen
        assert p['source_id'] and p['source'] in metadata['sources'] and p['source_url'].startswith('https://')
        assert p['verified_at']=='2026-10-27' and p['geographic_precision_m'] is None
        ps=list(positions(f['geometry']['coordinates']));assert ps
        b=[min(p[0] for p in ps),min(p[1] for p in ps),max(p[0] for p in ps),max(p[1] for p in ps)]
        assert b==p['bbox']
        if not valid_geometry(f['geometry']):invalid.append(f['id'])
        seen[f['id']]=(p['name'],p['type'],p['bbox'],i,p['minZoom'])
        if regional:
            assert isinstance(p['regionMask'],int) and 0<=p['regionMask']<=7
            assert p['regions']==[name for bit,name in region_bits.items() if p['regionMask']&bit]
            seen[f['id']]+=(p['regionMask'],)
            canonical=hashlib.sha256(json.dumps(f['geometry'],sort_keys=True,separators=(',',':')).encode()).hexdigest()
            geometry_hash.update((f['id']+':'+canonical+'\n').encode())
        types[p['type']]+=1
for row in index['search']:assert seen[row[0]]==tuple(row[1:])
assert len(seen)==index['total_features'] and dict(types)==index['counts']
overview_ids=set()
for chunk in index['overview_chunks']:
    path=root/chunk['file'];assert path.stat().st_size==chunk['bytes']
    fs=read_chunk(path,chunk)['features'];assert len(fs)==chunk['count']
    for f in fs:
        assert f['id'] in seen and f['id'] not in overview_ids
        assert f['properties']['minZoom']<=9
        if regional:assert f['properties']['regionMask']==seen[f['id']][-1]
        overview_ids.add(f['id'])
assert len(overview_ids)==index['overview_feature_count']
if regional:
    report=metadata['regional_intersection']
    boundary=root/report['boundary_file']
    assert hashlib.sha256(boundary.read_bytes()).hexdigest()==report['boundary_sha256']
    assert report['geometry_preservation']['canonical_geometry_sha256_before']==report['geometry_preservation']['canonical_geometry_sha256_after']==geometry_hash.hexdigest()
    assert dict(Counter(str(row[6]) for row in index['search']))==report['counts_by_mask']
assert not invalid, f'Degenerate source/encoding geometry: {invalid[:10]} ({len(invalid)} total)'
print(f"OK: {len(seen):,} geographic source features, {len(index['chunks'])} detailed chunks and {len(overview_ids):,} broad-view features; unique IDs, complete index, provenance and valid geometry.")
