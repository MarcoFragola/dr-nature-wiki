"""Import complete official hydrography for a declared regional bbox.

Sources are cached in web/tmp/geography. Geometry is never clipped or topologically
simplified: longitude/latitude are rounded to six decimals for transport (nine for tiny lines that would collapse), and source
Z is retained only in the original download (map heights use the separate DEM).
"""
from __future__ import annotations
import argparse, concurrent.futures, datetime, gzip, hashlib, json, math, time
import urllib.parse, urllib.request, zipfile
from collections import Counter, defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CACHE=ROOT/'tmp/geography'
OUT=ROOT/'dist/data/geography'
BBOX=[-5.2,39.5,-2.5,41.6]
LIMIT=1000
BASE='https://api-features.idee.es/collections'
ENP_PAGE='https://www.miteco.gob.es/es/biodiversidad/servicios/banco-datos-naturaleza/informacion-disponible/enp_descargas.html'
ENP_ZIP='https://www.miteco.gob.es/content/dam/miteco/es/biodiversidad/servicios/banco-datos-naturaleza/enp/Enp2025_geojson.zip'
HEADERS={'User-Agent':'DrNatureWiki/1.0 (official public geographic data import)','Accept-Encoding':'gzip'}

def write(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_name(path.name+'.writing')
    temporary.write_text(json.dumps(obj,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
    temporary.replace(path)

def fetch(url,path,offline=False):
    if path.exists():return path.read_bytes()
    if offline:raise FileNotFoundError(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers=HEADERS),timeout=120) as r:
                raw=r.read()
                if r.headers.get('Content-Encoding')=='gzip':raw=gzip.decompress(raw)
            path.write_bytes(raw);return raw
        except Exception:
            if attempt==2:raise
            time.sleep(1+attempt*2)

def source_url(collection,offset=0):
    return BASE+'/'+collection+'/items?'+urllib.parse.urlencode({'f':'json','bbox':','.join(map(str,BBOX)),'limit':LIMIT,'offset':offset})

def load_collection(collection,offline=False):
    first_path=CACHE/'hydro'/f'{collection}-000000.json'
    first=json.loads(fetch(source_url(collection),first_path,offline))
    matched=int(first['numberMatched'])
    print(f'{collection}: source declares {matched:,} rows',flush=True)
    offsets=range(LIMIT,matched,LIMIT)
    def page(offset):
        url=source_url(collection,offset);path=CACHE/'hydro'/f'{collection}-{offset:06}.json'
        raw=fetch(url,path,offline);data=json.loads(raw)
        if int(data['numberMatched'])!=matched:raise ValueError('Source changed during snapshot')
        return data['features'],{'url':url,'file':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(raw).hexdigest(),'returned':len(data['features'])}
    features=list(first['features'])
    manifest=[{'url':source_url(collection),'file':first_path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(first_path.read_bytes()).hexdigest(),'returned':len(first['features'])}]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for i,(rows,entry) in enumerate(pool.map(page,offsets),1):
            features.extend(rows);manifest.append(entry)
            if i%10==0:print(f'  {collection}: {len(features):,}/{matched:,}',flush=True)
    if len(features)!=matched:raise ValueError(f'{collection}: only {len(features)} of {matched} source rows')
    unique={};duplicates=[]
    for f in features:
        if f['id'] in unique:duplicates.append(f['id'])
        unique[f['id']]=f
    return list(unique.values()),manifest,{'source_rows':matched,'unique_features':len(unique),'duplicate_ids':duplicates}

def points(coordinates):
    if coordinates and isinstance(coordinates[0],(int,float)):
        yield coordinates
    else:
        for child in coordinates:yield from points(child)

def normalize_geometry(g):
    decimals=6
    def coords(c):
        if c and isinstance(c[0],(int,float)):return [round(float(c[0]),decimals),round(float(c[1]),decimals)]
        return [coords(x) for x in c]
    geometry={'type':g['type'],'coordinates':coords(g['coordinates'])}
    if g['type']=='LineString' and len(set(map(tuple,geometry['coordinates'])))<2:
        decimals=9;geometry={'type':g['type'],'coordinates':coords(g['coordinates'])}
    return geometry

def bbox(g):
    ps=list(points(g['coordinates']))
    return [min(p[0] for p in ps),min(p[1] for p in ps),max(p[0] for p in ps),max(p[1] for p in ps)]

def intersects(a,b):return a[0]<=b[2] and a[2]>=b[0] and a[1]<=b[3] and a[3]>=b[1]

def normalize_hydro(collection,f):
    p=f['properties'];g=normalize_geometry(f['geometry']);bb=bbox(g)
    kind='watercourse' if collection=='watercourse' else 'wetland' if collection=='wetland' else 'reservoir' if p.get('tipo_aestd')=='Embalse' else 'lake'
    size=max((bb[2]-bb[0])*85,(bb[3]-bb[1])*111)
    area=p.get('area');length=p.get('longitud')
    mz=8 if (length or 0)>15000 or (area or 0)>3000000 else 10 if (length or 0)>5000 or (area or 0)>200000 else 11 if size>1 else 13
    if not p.get('nombre'):mz=max(mz,12)
    properties={
        'id':f"ign:{collection}:{f['id']}", 'name':p.get('nombre') or None, 'type':kind,
        'source_id':f['id'], 'hydro_id':p.get('hydroid_localid'), 'source':'ign-igr-hydrography', 'collection':collection,
        'source_url':BASE+'/'+collection+'/items/'+urllib.parse.quote(str(f['id']))+'?f=json',
        'bbox':bb,'minZoom':mz,'geographic_precision_m':None,'source_resolution':p.get('resolucion'),'precision_note':'Source resolution value retained without claiming a survey or positional accuracy.',
        'source_feature_date':p.get('fecha_alta'),'verified_at':'2026-10-27',
        'subtype':p.get('tipo_aestd') or p.get('tipo_cursod') or p.get('tipo'),
        'water_persistence':p.get('persistd'),'origin':p.get('origend'),
        'basin':p.get('id_demarcd'),'length_m':length,'area_m2':area,
        'photograph':None,'verification':'official_source_geometry_not_live_conditions',
    }
    return {'type':'Feature','id':properties['id'],'properties':properties,'geometry':g}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--offline',action='store_true');parser.add_argument('--hydro-only',action='store_true');args=parser.parse_args()
    CACHE.mkdir(parents=True,exist_ok=True);OUT.mkdir(parents=True,exist_ok=True)
    features=[];manifest=[];counts={}
    for collection in ['watercourse','standingwater','wetland']:
        fs,entries,count=load_collection(collection,args.offline);counts[collection]=count;manifest.extend(entries)
        features.extend(normalize_hydro(collection,f) for f in fs)
    # ENP is handled as a separate complete official download, not via a failing legacy WMS.
    enp_status={'status':'not_imported','reason':'Optional official ENP import not yet prepared'}
    extra=CACHE/'enp-normalized.json'
    if extra.exists():
        enp=json.loads(extra.read_text(encoding='utf-8'));features.extend(enp['features']);enp_status=enp['metadata']
    cells=defaultdict(list)
    for f in features:
        b=f['properties']['bbox'];key=(math.floor((b[0]+b[2])/2/.25),math.floor((b[1]+b[3])/2/.25))
        cells[key].append(f)
    chunks=[];search=[]
    for (x,y),items in sorted(cells.items()):
        batch=[];byte_count=0;part=0
        def emit(batch,part):
            path=f'data/geography/chunks/cell-{x}-{y}-{part}.geojson';file=ROOT/'dist'/path
            write(file,{'type':'FeatureCollection','features':batch})
            boxes=[f['properties']['bbox'] for f in batch];bounds=[min(b[0] for b in boxes),min(b[1] for b in boxes),max(b[2] for b in boxes),max(b[3] for b in boxes)]
            chunk_id=len(chunks);chunks.append({'file':path,'bbox':bounds,'count':len(batch),'bytes':file.stat().st_size})
            for f in batch:
                p=f['properties'];search.append([p['id'],p['name'],p['type'],p['bbox'],chunk_id,p['minZoom']])
        for f in items:
            n=len(json.dumps(f,separators=(',',':'),ensure_ascii=False).encode())
            if batch and (byte_count+n>1500000 or len(batch)>=500):emit(batch,part);part+=1;batch=[];byte_count=0
            batch.append(f);byte_count+=n
        if batch:emit(batch,part)
    # Separate broad-view assets keep the full detailed catalogue independent of rendering.
    overview_cells=defaultdict(list)
    for f in features:
        p=f['properties']
        if p['minZoom']>9:continue
        b=p['bbox'];family='protected-areas' if p['type']=='protected-area' else 'hydrography'
        key=(family,math.floor((b[0]+b[2])/2),math.floor((b[1]+b[3])/2))
        overview_cells[key].append(f)
    overview=[]
    for (family,x,y),items in sorted(overview_cells.items()):
        batches=[];batch=[];nbytes=0
        for feature in items:
            n=len(json.dumps(feature,separators=(',',':'),ensure_ascii=False).encode())
            if batch and nbytes+n>1900000:batches.append(batch);batch=[];nbytes=0
            batch.append(feature);nbytes+=n
        if batch:batches.append(batch)
        for part,batch in enumerate(batches):
            path=f'data/geography/overview/{family}-{x}-{y}-{part}.geojson';file=ROOT/'dist'/path
            write(file,{'type':'FeatureCollection','features':batch})
            boxes=[f['properties']['bbox'] for f in batch]
            bounds=[min(b[0] for b in boxes),min(b[1] for b in boxes),max(b[2] for b in boxes),max(b[3] for b in boxes)]
            overview.append({'file':path,'bbox':bounds,'count':len(batch),'bytes':file.stat().st_size,'family':family})
    types=Counter(f['properties']['type'] for f in features)
    metadata={
        'schema':'dr-nature-geographic-reference-v1','snapshot_date':'2026-10-27',
        'coverage':{'hydrography_bbox':BBOX,'bbox_order':'west,south,east,north','crs':'OGC:CRS84','definition':'All official source records intersecting this bbox, not complete autonomous communities. Geometry crossing the bbox is preserved unclipped.'},
        'sources':{
            'ign-igr-hydrography':{'title':'IGN IGR-Hidrografía v0 / INSPIRE aguas físicas','publisher':'Instituto Geográfico Nacional / CNIG','page_url':'https://www.ign.es/web/ign/portal/seccion-hidrografia','api':BASE,'license':'CC BY 4.0 scne.es','license_url':'https://www.ign.es/resources/licencia/Condiciones_licenciaUso_IGN.pdf','collection_source_update':'IGR v0 latest update2019 according to IGN product page; individual feature dates retained','geometry_scale_note':'Source resolucion is retained as source_resolution. No source positional accuracy is asserted; geographic_precision_m remains null.'},
        },
        'counts':dict(types),'source_counts':counts,'enp':enp_status,
        'geometry_processing':'No clipping, smoothing or topological simplification. XY rounded to six decimal degrees (submetre encoding), with nine decimals retained for tiny line segments that would otherwise collapse; source Z omitted from display geometry and preserved in cached official downloads. Separate official DEM provides map relief.',
        'chunking':'0.25 degree cell by feature bbox centre, then batches <=1.5MB or500features; chunk bbox is union of actual complete feature bounds, not the cell extent. Large individual features are never cut to meet byte target.',
        'limitations':['Counts are source features/segments and water bodies, not counts of unique rivers.','No walking paths, access permissions, water levels, bathing suitability, species observations or photographs are inferred.','Nameless source objects retain null names; display fallback labels must not be presented as official names.','Source date is not a statement of live environmental conditions.'],
        'source_manifest':'data/geography/import-report.json',
    }
    if enp_status.get('source'):metadata['sources']['miteco-enp']=enp_status['source']
    write(OUT/'metadata.json',metadata)
    write(OUT/'index.json',{'schema':'dr-nature-geographic-index-v1','generated_at':'2026-10-27','coverage':metadata['coverage'],'total_features':len(features),'counts':dict(types),'search_columns':['id','name','type','bbox','chunk','minZoom'],'chunks':chunks,'overview_chunks':overview,'overview_feature_count':sum(c['count'] for c in overview),'minZoom_histogram':dict(Counter(f['properties']['minZoom'] for f in features)),'search':search})
    write(OUT/'import-report.json',{'source_counts':counts,'requests':manifest,'feature_count':len(features),'enp':enp_status})
    (OUT/'README.txt').write_text('Official geographic reference for Dr Nature wiki. Read metadata.json for exact coverage, source dates, licences and limitations.\nIndex rows: [id,name,type,bbox,chunk,minZoom]; chunk is a numeric index into chunks[]. Geometry files are FeatureCollections and can be loaded by intersecting their actual bbox with the viewport. IDs are stable source identifiers prefixed by publisher/collection. No points of observation or photos have been invented.\nRebuild: python scripts/prepare_geography.py --offline after downloading the documented source snapshot. Omit --offline to fetch missing public source pages.\n',encoding='utf-8')
    print(f'COMPLETE: {len(features):,} geographic source features; {len(chunks)} chunks; index {(OUT/"index.json").stat().st_size:,} bytes',flush=True)

if __name__=='__main__':main()
