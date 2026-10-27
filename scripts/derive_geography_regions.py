"""Optional exact regional intersection pass for the official geographic reference.

Preparation-only dependency: Shapely2.1.2 (Python>=3.10, NumPy>=1.21).
It may be installed in tmp/geography/python-packages; nothing is installed into the
website. No source geometry, coordinate, source ID or catalogue row is removed.
"""
import hashlib, json, sys
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'dist/data/geography'
BOUNDARIES=ROOT/'dist/data/boundaries/comunidades.geojson'
try:
    import shapely
except ImportError:
    sys.path.insert(0,str(ROOT/'tmp/geography/python-packages'))
    import shapely
from shapely.geometry import shape
from shapely.prepared import prep
from shapely.validation import make_valid, explain_validity
from prepare_geography import write

REGIONS={
    '34130000000':('Madrid',1),
    '34070000000':('Castilla y León',2),
    '34080000000':('Castilla-La Mancha',4),
}

def digest(geometry):
    return hashlib.sha256(json.dumps(geometry,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def intersects_bbox(a,b):
    return a[0]<=b[2] and a[2]>=b[0] and a[1]<=b[3] and a[3]>=b[1]

def update_readme():
    readme=DATA/'README.txt'
    text=readme.read_text(encoding='utf-8')
    text=text.replace('search=[id,name,type,bbox,chunk,minZoom]', 'search=[id,name,type,bbox,chunk,minZoom,regionMask]')
    text=text.replace('No hay intersecciones de región calculadas: los códigos administrativos de ENP son los de la fuente, no máscaras espaciales de todo el catálogo.', 'regionMask y regions se derivan de intersecciones geométricas con los límites oficiales del IGN; no de centroides ni de códigos administrativos. Los códigos de administración del ENP siguen siendo un atributo distinto de la fuente.')
    marker='FILTRO REGIONAL DERIVADO'
    if marker in text:text=text[:text.index(marker)].rstrip()+'\n'
    text+='\n'+marker+'''
regionMask es la séptima columna del índice y una propiedad de cada feature: 1 Madrid, 2 Castilla y León, 4 Castilla-La Mancha. Los bits se combinan si el elemento toca o cruza varias regiones; 0 significa que no intersecta ninguna de estas tres, sin asignarlo a otra comunidad. regions enumera los nombres correspondientes.
El cálculo usa la geometría completa y los polígonos oficiales de data/boundaries/comunidades.geojson, sin buffers ni aproximación por centroides. No implica pertenencia exclusiva ni precisión superior a la de las fuentes.
Se reparan copias topológicas solo para el cálculo si GEOS detecta invalidez; geometrías publicadas y archivo de límites permanecen intactos. Detalles, versiones, máscaras, reparaciones y hashes de conservación en regional-intersection-report.json.
Reproducción opcional tras la importación: python scripts/derive_geography_regions.py. Requiere Shapely2.1.2 y NumPy>=1.21 únicamente durante la preparación; no añade dependencias de ejecución a la web.
'''
    readme.write_text(text,encoding='utf-8')

def main():
    index=json.loads((DATA/'index.json').read_text(encoding='utf-8'))
    metadata=json.loads((DATA/'metadata.json').read_text(encoding='utf-8'))
    source_boundaries=BOUNDARIES.read_bytes()
    collection=json.loads(source_boundaries)
    boundaries=[];boundary_repairs=[]
    for feature in collection['features']:
        code=str(feature['properties']['nationalCode'])
        if code not in REGIONS:continue
        name,bit=REGIONS[code];geometry=shape(feature['geometry'])
        if not geometry.is_valid:
            reason=explain_validity(geometry);geometry=make_valid(geometry)
            if geometry.geom_type=='GeometryCollection':
                geometry=shapely.union_all([g for g in geometry.geoms if g.geom_type in ['Polygon','MultiPolygon']])
            boundary_repairs.append({'nationalCode':code,'name':name,'reason':reason,'repair':'GEOS make_valid, polygonal parts only, for intersection computations; original boundary file unchanged'})
        assert geometry.is_valid and not geometry.is_empty
        boundaries.append((name,bit,geometry.bounds,prep(geometry)))
    boundaries.sort(key=lambda r:r[1]);assert len(boundaries)==3
    masks={};mask_counts=Counter();region_counts=Counter();feature_repairs=[]
    geometry_before=hashlib.sha256();geometry_after=hashlib.sha256()
    for ci,chunk in enumerate(index['chunks']):
        path=(ROOT/'dist'/chunk['file']).resolve()
        assert path.is_relative_to(DATA.resolve())
        fc=json.loads(path.read_text(encoding='utf-8'))
        originals={f['id']:digest(f['geometry']) for f in fc['features']}
        for feature in fc['features']:
            properties=feature['properties'];geometry=shape(feature['geometry']);test_geometry=geometry
            if not geometry.is_valid:
                reason=explain_validity(geometry);test_geometry=make_valid(geometry)
                feature_repairs.append({'id':feature['id'],'reason':reason,'repair':'GEOS make_valid for intersection computations only; published geometry unchanged'})
            assert not test_geometry.is_empty
            mask=0
            for name,bit,bounds,prepared in boundaries:
                if intersects_bbox(test_geometry.bounds,bounds) and prepared.intersects(test_geometry):mask|=bit
            properties['regionMask']=mask
            properties['regions']=[name for name,bit,_,_ in boundaries if mask&bit]
            masks[feature['id']]=mask;mask_counts[mask]+=1
            region_counts.update(properties['regions'])
            geometry_before.update((feature['id']+':'+originals[feature['id']]+'\n').encode())
        write(path,fc)
        reloaded=json.loads(path.read_text(encoding='utf-8'))
        for feature in reloaded['features']:
            current=digest(feature['geometry']);assert current==originals[feature['id']]
            geometry_after.update((feature['id']+':'+current+'\n').encode())
        chunk['bytes']=path.stat().st_size;chunk['sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
        if (ci+1)%50==0:print(f'Regional intersection: {len(masks):,}/{index["total_features"]:,}',flush=True)
    assert len(masks)==index['total_features'] and geometry_before.digest()==geometry_after.digest()
    for row in index['search']:
        row[:]=row[:6]+[masks[row[0]]]
    index['search_columns']=['id','name','type','bbox','chunk','minZoom','regionMask']
    for chunk in index['overview_chunks']:
        path=ROOT/'dist'/chunk['file'];fc=json.loads(path.read_text(encoding='utf-8'))
        for feature in fc['features']:
            mask=masks[feature['id']];feature['properties']['regionMask']=mask
            feature['properties']['regions']=[name for name,bit,_,_ in boundaries if mask&bit]
        write(path,fc);chunk['bytes']=path.stat().st_size;chunk['sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
    regional={
        'method':'Derived intersection with official IGN autonomous-community polygons, using GEOS/Shapely intersects on complete feature geometry. Not centroid assignment, containment, source administrative-authority code or bbox-only membership.',
        'semantics':'A bit is set when any part of the feature intersects or touches that region. Multiple bits may be set.0 means no intersection with the three tested regions; it does not identify another region.',
        'bits':{'1':'Madrid','2':'Castilla y León','4':'Castilla-La Mancha'},
        'boundary_file':'data/boundaries/comunidades.geojson',
        'boundary_sha256':hashlib.sha256(source_boundaries).hexdigest(),
        'boundary_source':'Instituto Geográfico Nacional / CNIG, official administrative boundaries; CC BY4.0 ign.es',
        'boundary_metadata':'data/boundaries/metadata.json',
        'coordinate_model':'GEOS planar topological intersection of longitude/latitude geometries in the same CRS84 axis order; no buffer, centroid approximation or added tolerance. Underlying source scale, coordinate encoding and boundary accuracy still apply.',
        'prepared_with':{'shapely':shapely.__version__,'geos':shapely.geos_version_string,'preparation_only':True},
        'derived_at':'2026-10-27','counts_by_mask':dict(sorted(mask_counts.items())),
        'feature_counts_by_intersected_region':dict(region_counts),
        'boundary_repairs_for_intersection_only':boundary_repairs,
        'feature_repairs_for_intersection_only':feature_repairs,
        'geometry_preservation':{'feature_count':len(masks),'canonical_geometry_sha256_before':geometry_before.hexdigest(),'canonical_geometry_sha256_after':geometry_after.hexdigest(),'unchanged':True},
        'rebuild':'python scripts/derive_geography_regions.py, after prepare_geography.py; requires Shapely2.1.2 as a preparation dependency only.',
    }
    metadata['regional_intersection']=regional
    index['region_bits']=regional['bits'];index['counts_by_region_mask']=regional['counts_by_mask']
    write(DATA/'regional-intersection-report.json',regional)
    write(DATA/'metadata.json',metadata)
    write(DATA/'index.json',index)
    update_readme()
    print(json.dumps({'features':len(masks),'counts_by_mask':dict(mask_counts),'region_counts':dict(region_counts),'boundary_repairs':len(boundary_repairs),'feature_repairs':len(feature_repairs),'geometry_unchanged':True,'index_bytes':(DATA/'index.json').stat().st_size},ensure_ascii=False),flush=True)

if __name__=='__main__':main()
