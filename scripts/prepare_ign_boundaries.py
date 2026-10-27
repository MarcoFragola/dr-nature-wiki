import urllib.request,urllib.parse,json,sys,math,hashlib,datetime
from pathlib import Path
from xml.etree import ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT/'tmp/boundary-research'
BASE='https://www.ign.es/wfs-inspire/unidades-administrativas'
WORK.mkdir(parents=True,exist_ok=True)
def fetch(params,name):
    url=BASE+'?'+urllib.parse.urlencode(params)
    req=urllib.request.Request(url,headers={'User-Agent':'DrNatureWiki/1.0 (official boundary data integration)'})
    with urllib.request.urlopen(req,timeout=120) as r:data=r.read()
    (WORK/name).write_bytes(data)
    return url,data
if len(sys.argv)>1 and sys.argv[1]=='inspect':
    url,data=fetch({'service':'WFS','request':'DescribeFeatureType','version':'2.0.0','typeNames':'au:AdministrativeUnit'},'schema.xml')
    root=ET.fromstring(data)
    print('SCHEMA',url)
    for x in root.iter():
        if x.tag.rsplit('}',1)[-1]=='element':print(x.attrib)
    url,data=fetch({'service':'WFS','request':'GetFeature','version':'2.0.0','typeNames':'au:AdministrativeUnit','count':'1','outputFormat':'application/geo+json','srsName':'EPSG:4326'},'sample.geojson')
    try:
        sample=json.loads(data)
        for f in sample.get('features',[]):print(json.dumps({k:v for k,v in f.items() if k!='geometry'},ensure_ascii=False))
        print('SAMPLE TOP KEYS',list(sample))
        print('GEOMETRY TYPE',sample.get('features',[{}])[0].get('geometry',{}).get('type'))
    except Exception:print(data.decode()[:3000])
    sys.exit()
if len(sys.argv)>1 and sys.argv[1]=='download':
    ids=['34130000000','34070000000','34080000000']
    filter_xml='<fes:Filter xmlns:fes="http://www.opengis.net/fes/2.0" xmlns:au="http://inspire.ec.europa.eu/schemas/au/4.0"><fes:Or>'+''.join('<fes:PropertyIsEqualTo><fes:ValueReference>au:nationalCode</fes:ValueReference><fes:Literal>'+ident+'</fes:Literal></fes:PropertyIsEqualTo>' for ident in ids)+'</fes:Or></fes:Filter>'
    url,data=fetch({'service':'WFS','request':'GetFeature','version':'2.0.0','typeNames':'au:AdministrativeUnit','count':'3','outputFormat':'application/geo+json','srsName':'EPSG:4326','filter':filter_xml},'communities-original.geojson')
    try:collection=json.loads(data)
    except Exception:print(data.decode()[:5000]);raise
    assert len(collection.get('features',[]))==3,collection
    output=ROOT/'dist/data/boundaries';output.mkdir(parents=True,exist_ok=True)
    results=[];features=[]
    def rings_of(g):
        if g['type']=='Polygon':return g['coordinates']
        if g['type']=='MultiPolygon':return [r for p in g['coordinates'] for r in p]
        raise ValueError('Not polygonal geometry')
    for f in collection['features']:
        props=f['properties'];code=props['nationalCode'];name=props['name']['GeographicalName']['spelling']['SpellingOfName']['text'];level=props['nationalLevel']['href']
        assert code in ids and level.endswith('/2ndOrder'),(code,name,level)
        geometry=f['geometry'];rings=rings_of(geometry);points=[]
        for ring in rings:
            assert len(ring)>=4 and ring[0]==ring[-1]
            assert all(len(p)>=2 and all(isinstance(v,(float,int)) and math.isfinite(v) for v in p) and -180<=p[0]<=180 and -90<=p[1]<=90 for p in ring)
            area=sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(ring,ring[1:]))/2
            assert abs(area)>1e-15
            points.extend(ring)
        bbox=[min(p[0] for p in points),min(p[1] for p in points),max(p[0] for p in points),max(p[1] for p in points)]
        assert -8<bbox[0]<bbox[2]<2 and 37<bbox[1]<bbox[3]<44.5,(name,bbox)
        if code=='34130000000':assert -4.8<bbox[0]<-4 and -3.5<bbox[2]<-2.8 and 39.7<bbox[1]<40.1 and 41.0<bbox[3]<41.3,(name,bbox)
        item={'type':'Feature','id':f['id'],'bbox':bbox,'properties':{'name':name,'nationalCode':code,'nationalLevel':'2ndOrder','nationalLevelName':props['nationalLevelName']['LocalisedCharacterString'],'source_identifier':props['inspireId']['Identifier'],'source':'Instituto Geográfico Nacional (IGN)','license':'CC BY 4.0 ign.es'},'geometry':geometry}
        features.append(item)
        results.append(dict(name=name,nationalCode=code,feature_id=f['id'],geometry_type=geometry['type'],polygon_count=1 if geometry['type']=='Polygon' else len(geometry['coordinates']),ring_count=len(rings),vertex_count=len(points),bbox=bbox))
        print(json.dumps(results[-1],ensure_ascii=False))
    assert {f['properties']['nationalCode'] for f in features}==set(ids)
    cleaned={'type':'FeatureCollection','features':features}
    madrid={'type':'FeatureCollection','features':[f for f in features if f['properties']['nationalCode']=='34130000000']}
    for name,obj in [('comunidades.geojson',cleaned),('madrid.geojson',madrid)]:
        content=(json.dumps(obj,ensure_ascii=False,separators=(',',':'))+'\n').encode('utf8');(output/name).write_bytes(content);print(name,len(content),'bytes')
    (WORK/'request.json').write_text(json.dumps({'request_url':url,'original_sha256':hashlib.sha256(data).hexdigest(),'features':results},ensure_ascii=False,indent=2),encoding='utf8')
    print('REQUEST',url)
    sys.exit()
if len(sys.argv)>1 and sys.argv[1]=='metadata':
    cap=ET.fromstring((WORK/'capabilities.xml').read_bytes())
    urls=[e.attrib['{http://www.w3.org/1999/xlink}href'] for e in cap.iter() if e.tag.rsplit('}',1)[-1]=='MetadataURL']
    url=urls[0]
    req=urllib.request.Request(url,headers={'User-Agent':'DrNatureWiki/1.0 (official metadata integration)'})
    with urllib.request.urlopen(req,timeout=120) as r:data=r.read()
    (WORK/'dataset-metadata.xml').write_bytes(data)
    root=ET.fromstring(data)
    print('METADATA',url)
    for e in root.iter():
        if e.tag.rsplit('}',1)[-1] in ['title','abstract','lineage','spatialResolution','referenceSystemInfo','resourceConstraints','dateStamp','extent']:
            text=' '.join(s.strip() for s in e.itertext() if s.strip())
            print(e.tag.rsplit('}',1)[-1],text[:6500])
    sys.exit()
if len(sys.argv)>1 and sys.argv[1]=='package':
    output=ROOT/'dist/data/boundaries'
    req=json.loads((WORK/'request.json').read_text(encoding='utf8'))
    original=json.loads((WORK/'communities-original.geojson').read_text(encoding='utf8'))
    cleaned=json.loads((output/'comunidades.geojson').read_text(encoding='utf8'))
    byid={f['id']:f for f in original['features']}
    assert all(f['geometry']==byid[f['id']]['geometry'] for f in cleaned['features'])
    files=[]
    for name in ['madrid.geojson','comunidades.geojson']:
        content=(output/name).read_bytes();data=json.loads(content)
        files.append({'file':name,'bytes':len(content),'sha256':hashlib.sha256(content).hexdigest(),'feature_count':len(data['features'])})
    metadata={
      'title':'Límites autonómicos oficiales: Comunidad de Madrid, Castilla y León y Castilla-La Mancha',
      'provider':'Instituto Geográfico Nacional (IGN)',
      'dataset':'Divisiones Administrativas de España / Base de Datos de Límites Jurisdiccionales de España (BDLJE)',
      'downloaded_at':'2026-10-27',
      'metadata_revision_date':'2026-02-23',
      'individual_feature_revision_date':None,
      'source':{
        'reference_product_url':'https://centrodedescargas.cnig.es/CentroDescargas/limites-municipales-provinciales-autonomicos',
        'service_url':BASE,
        'get_capabilities_url':BASE+'?service=WFS&request=GetCapabilities&version=2.0.0',
        'get_feature_url':req['request_url'],
        'dataset_metadata_url':'https://www.idee.es/csw-inspire-idee/srv/spa/csw?SERVICE=CSW&VERSION=2.0.2&REQUEST=GetRecordById&outputSchema=http://www.isotc211.org/2005/gmd&ElementSetName=full&ID=spaignLLM',
        'original_response_sha256':req['original_sha256'],
        'original_response_format':'application/geo+json',
        'feature_type':'au:AdministrativeUnit',
        'administrative_level':'2ndOrder / Comunidad autónoma',
        'selection':'Exact nationalCode values 34130000000, 34070000000, 34080000000, then verified against returned official names and hierarchy.'
      },
      'license':{'name':'CC BY 4.0','url':'https://creativecommons.org/licenses/by/4.0/','attribution':'BDLJE CC-BY 4.0 ign.es','service_access_constraints':'CC BY 4.0 ign.es','required_visible_credit':'Límites administrativos: IGN · BDLJE · CC BY 4.0 ign.es'},
      'coordinate_reference_system':{
        'dataset_original':'ETRS89, EPSG:4258, geographic coordinates for the Spanish mainland; confirmed in the official dataset metadata and WFS default CRS.',
        'requested_output':'EPSG:4326 / WGS 84',
        'geojson_coordinate_order':'longitude, latitude, decimal degrees',
        'local_transformation':'None. GeoJSON in EPSG:4326 was requested directly from the IGN WFS. The service performs its CRS handling; its transformation parameters are not exposed here.',
        'vertical_coordinates':'None; these are 2D administrative polygons to be draped by the map engine over a separate terrain source.'
      },
      'geometry_processing':{'simplification':False,'coordinate_rounding':False,'ring_or_polygon_removal':False,'geometry_preserved_exactly_from_ign_response':True,'properties':'Official INSPIRE identifier, national code, name and hierarchy retained; unused nested relational properties omitted.'},
      'resolution_and_limitations':{
        'reference_scale_denominator':25000,
        'source_precision':'Official metadata describes heterogeneous origins, from decimetric to decametric precision; most historic limits are decametric and the general explanatory text cites uncertainty around 40 m.',
        'display_limit':'A zoomed screen display does not improve the source accuracy. The metadata advises against treating the general geometry as jurisdictional mapping at scales larger than 1:25,000.',
        'provisional_segments':'The official dataset warns that some source limit sections can be provisional to close administrative polygons. This extraction does not independently classify those sections.',
        'not_cadastral':'No cadastral parcel, surveyed access point, trail or elevation information is included.'
      },
      'validation':{'json_parse':True,'feature_count':3,'administrative_level_and_ids_verified':True,'coordinate_axis_and_regional_bboxes_verified':True,'all_coordinates_finite_and_in_geographic_ranges':True,'polygon_and_multipolygon_structure_verified':True,'all_linear_rings_closed_with_at_least_four_positions':True,'no_zero_signed_area_rings':True,'coordinate_arrays_equal_to_ign_response':True,'independent_full_topology_validation':False,'topology_note':'No geometry repair or simplification was performed. Full self-intersection/overlay validation with an external geometry engine has not been run.'},
      'features':req['features'],'files':files
    }
    (output/'metadata.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'directory':str(output),'files':files,'metadata_bytes':(output/'metadata.json').stat().st_size},ensure_ascii=False))
    sys.exit()
if len(sys.argv)>1 and sys.argv[1]=='provinces':
    names=['Madrid','Segovia','Ávila','Guadalajara','Cuenca','Toledo']
    head='<fes:Filter xmlns:fes="http://www.opengis.net/fes/2.0" xmlns:au="http://inspire.ec.europa.eu/schemas/au/4.0" xmlns:gn="http://inspire.ec.europa.eu/schemas/gn/4.0" xmlns:xlink="http://www.w3.org/1999/xlink"><fes:And>'
    level='<fes:PropertyIsEqualTo><fes:ValueReference>au:nationalLevel/@xlink:href</fes:ValueReference><fes:Literal>https://inspire.ec.europa.eu/codelist/AdministrativeHierarchyLevel/3rdOrder</fes:Literal></fes:PropertyIsEqualTo>'
    options='<fes:Or>'+''.join('<fes:PropertyIsEqualTo><fes:ValueReference>au:name/gn:GeographicalName/gn:spelling/gn:SpellingOfName/gn:text</fes:ValueReference><fes:Literal>'+name+'</fes:Literal></fes:PropertyIsEqualTo>' for name in names)+'</fes:Or>'
    filter_xml=head+level+options+'</fes:And></fes:Filter>'
    url,data=fetch({'service':'WFS','request':'GetFeature','version':'2.0.0','typeNames':'au:AdministrativeUnit','count':'6','outputFormat':'application/geo+json','srsName':'EPSG:4326','filter':filter_xml},'provinces-original.geojson')
    try:collection=json.loads(data)
    except Exception:print(data.decode()[:6000]);raise
    print('RESPONSE',collection.get('type'),'FEATURES',len(collection.get('features',[])))
    if not collection.get('features'):print(json.dumps(collection)[:1000]);raise ValueError('No provinces')
    features=[];records=[]
    for f in collection['features']:
        p=f['properties'];name=p['name']['GeographicalName']['spelling']['SpellingOfName']['text'];level=p['nationalLevel']['href'];code=p['nationalCode'];g=f['geometry']
        assert name in names and level.endswith('/3rdOrder'),(name,level)
        polys=g['coordinates'] if g['type']=='MultiPolygon' else [g['coordinates']]
        rings=[r for poly in polys for r in poly];pts=[point for ring in rings for point in ring]
        assert all(len(r)>=4 and r[0]==r[-1] for r in rings)
        assert all(len(point)>=2 and all(isinstance(v,(float,int)) and math.isfinite(v) for v in point) and -8<point[0]<1 and 37<point[1]<44 for point in pts)
        bbox=[min(pt[0] for pt in pts),min(pt[1] for pt in pts),max(pt[0] for pt in pts),max(pt[1] for pt in pts)]
        item={'type':'Feature','id':f['id'],'bbox':bbox,'properties':{'name':name,'nationalCode':code,'nationalLevel':'3rdOrder','nationalLevelName':p['nationalLevelName']['LocalisedCharacterString'],'source_identifier':p['inspireId']['Identifier'],'source':'Instituto Geográfico Nacional (IGN)','license':'CC BY 4.0 ign.es'},'geometry':g}
        features.append(item);records.append(dict(name=name,nationalCode=code,feature_id=f['id'],geometry_type=g['type'],polygon_count=len(polys),ring_count=len(rings),vertex_count=len(pts),bbox=bbox));print(json.dumps(records[-1],ensure_ascii=False))
    assert {f['properties']['name'] for f in features}==set(names)
    output=ROOT/'dist/data/boundaries';path=output/'provincias.geojson';content=(json.dumps({'type':'FeatureCollection','features':features},ensure_ascii=False,separators=(',',':'))+'\n').encode('utf8');path.write_bytes(content)
    meta=json.loads((output/'metadata.json').read_text(encoding='utf8'))
    meta['provinces']={'file':'provincias.geojson','source_request_url':url,'selection':'Official name spellings and nationalLevel 3rdOrder were used in the WFS filter. National codes below were read from returned feature attributes, not generated.','features':records,'original_response_sha256':hashlib.sha256(data).hexdigest(),'geometry_processing':'Complete coordinate arrays, holes and polygon parts copied without simplification or rounding.','license':'CC BY 4.0 ign.es','crs':'EPSG:4326, longitude/latitude requested directly from WFS','reference_scale_denominator':25000}
    meta['files']=[x for x in meta['files'] if x['file']!='provincias.geojson']+[{'file':'provincias.geojson','bytes':len(content),'sha256':hashlib.sha256(content).hexdigest(),'feature_count':len(features)}]
    (output/'metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('PROVINCES BYTES',len(content))
    sys.exit()
url,data=fetch({'service':'WFS','request':'GetCapabilities','version':'2.0.0'},'capabilities.xml')
root=ET.fromstring(data)
print('CAPABILITIES',url)
for x in root.iter():
    tag=x.tag.rsplit('}',1)[-1]
    if tag in ['Title','Abstract','Name','DefaultCRS','OtherCRS','Value'] and x.text:print(tag,x.text[:2000])
