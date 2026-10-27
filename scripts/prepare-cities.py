"""Prepare a small official IGN NGBE settlement point dataset for orientation labels."""
import json,sys,math,urllib.request,urllib.parse,hashlib
import unicodedata
from pathlib import Path
from xml.etree import ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT/'tmp/ciudades';WORK.mkdir(parents=True,exist_ok=True)
BASE='https://www.ign.es/wfs-inspire/ngbe'
UA='DrNatureWiki/1.0 (official settlement orientation points)'
CAPITALS=['Madrid','Toledo','Segovia','Ávila','Guadalajara','Cuenca']
TOWNS=['Cercedilla','Rascafría','Manzanares el Real','Navacerrada','Guadarrama','San Lorenzo de El Escorial','El Escorial','Buitrago del Lozoya','Lozoya','Montejo de la Sierra','San Ildefonso','Torrelaguna','Alcalá de Henares','Aranjuez','Chinchón','El Tiemblo','Hoyo de Manzanares','Miraflores de la Sierra','Soto del Real','Colmenar Viejo','Becerril de la Sierra','Los Molinos','Pinilla del Valle','Prádena del Rincón','Puebla de la Sierra','Patones','Guadalix de la Sierra','San Agustín del Guadalix','Torrelodones','Boadilla del Monte','Rivas-Vaciamadrid','Lozoyuela']
ALIASES=['La Granja de San Ildefonso','Real Sitio de San Ildefonso','Granja de San Ildefonso (La)','Ildefonso (San)','San Lorenzo del Escorial','Manzanares El Real','Rivas Vaciamadrid','Escorial (El)','Tiemblo (El)']
def fetch(params,name):
    url=BASE+'?'+urllib.parse.urlencode(params)
    req=urllib.request.Request(url,headers={'User-Agent':UA})
    with urllib.request.urlopen(req,timeout=100) as r:data=r.read()
    (WORK/name).write_bytes(data)
    return url,data
def name_filter(names):
    ors=''.join('<fes:PropertyIsEqualTo><fes:ValueReference>gn:name/gn:GeographicalName/gn:spelling/gn:SpellingOfName/gn:text</fes:ValueReference><fes:Literal>'+name+'</fes:Literal></fes:PropertyIsEqualTo>' for name in names)
    return '<fes:Filter xmlns:fes="http://www.opengis.net/fes/2.0" xmlns:gn="http://inspire.ec.europa.eu/schemas/gn/4.0"><fes:Or>'+ors+'</fes:Or></fes:Filter>'
def geographical_names(f):
    value=f['properties']['name']
    return [item['GeographicalName'] for item in (value if isinstance(value,list) else [value])]
mode=sys.argv[1] if len(sys.argv)>1 else 'inspect'
if mode=='inspect':
    url,data=fetch({'service':'WFS','request':'GetCapabilities','version':'2.0.0'},'capabilities.xml')
    root=ET.fromstring(data);print('CAPABILITIES',url)
    for e in root.iter():
        if e.tag.rsplit('}',1)[-1] in ['Title','Abstract','AccessConstraints','Name','DefaultCRS','Value'] and e.text:print(e.tag.rsplit('}',1)[-1],e.text.strip()[:2500])
    url,data=fetch({'service':'WFS','request':'GetFeature','version':'2.0.0','typeNames':'gn:NamedPlace','count':'15','outputFormat':'application/geo+json','srsName':'EPSG:4326','filter':name_filter(['Madrid','Segovia'])},'sample.geojson')
    try:d=json.loads(data);print('SAMPLE',json.dumps(d,ensure_ascii=False)[:14000])
    except Exception:print(data.decode()[:5000]);raise
if mode=='download':
    allnames=CAPITALS+TOWNS+ALIASES;allfeatures={};requests=[]
    for i in range(0,len(allnames),7):
        filt=name_filter(allnames[i:i+7])
        part=filt[filt.index('<fes:Or>'):filt.index('</fes:Or>')+len('</fes:Or>')]
        bbox='<fes:BBOX><fes:ValueReference>gn:geometry</fes:ValueReference><gml:Envelope srsName="http://www.opengis.net/def/crs/EPSG/0/4326"><gml:lowerCorner>39.4 -5.1</gml:lowerCorner><gml:upperCorner>41.4 -1.9</gml:upperCorner></gml:Envelope></fes:BBOX>'
        filt='<fes:Filter xmlns:fes="http://www.opengis.net/fes/2.0" xmlns:gn="http://inspire.ec.europa.eu/schemas/gn/4.0" xmlns:gml="http://www.opengis.net/gml/3.2" xmlns:xlink="http://www.w3.org/1999/xlink"><fes:And><fes:PropertyIsEqualTo><fes:ValueReference>gn:type/@xlink:href</fes:ValueReference><fes:Literal>https://inspire.ec.europa.eu/codelist/NamedPlaceTypeValue/populatedPlace</fes:Literal></fes:PropertyIsEqualTo>'+bbox+part+'</fes:And></fes:Filter>'
        params={'service':'WFS','request':'GetFeature','version':'2.0.0','typeNames':'gn:NamedPlace','count':'200','outputFormat':'application/geo+json','srsName':'EPSG:4326','filter':filt}
        name=f'settlements-{i//7:02}.geojson';cached=WORK/name
        if cached.exists():url=BASE+'?'+urllib.parse.urlencode(params);data=cached.read_bytes()
        else:url,data=fetch(params,name)
        batch=json.loads(data);assert batch['type']=='FeatureCollection';batch.setdefault('features',[]);assert len(batch['features'])<200
        allfeatures.update({f['id']:f for f in batch['features']})
        print('Batch',i//7,'features',len(batch['features']),flush=True)
        requests.append({'url':url,'names':allnames[i:i+7],'bytes':len(data),'feature_count':len(batch['features']),'sha256':hashlib.sha256(data).hexdigest()})
    d={'type':'FeatureCollection','features':list(allfeatures.values())}
    (WORK/'settlements.geojson').write_text(json.dumps(d,ensure_ascii=False),encoding='utf8')
    (WORK/'request.json').write_text(json.dumps({'requests':requests},indent=2),encoding='utf8')
    for f in d['features']:
        p=f['properties'];name=' / '.join(n['spelling']['SpellingOfName']['text'] for n in geographical_names(f));local=p['localType']['LocalisedCharacterString'];local=local.get('value',local) if isinstance(local,dict) else local
        print(json.dumps({'id':f['id'],'name':name,'localType':local,'coordinates':f['geometry']['coordinates'],'type':p['type']},ensure_ascii=False))
    print('TOTAL',len(d['features']))
if mode=='package':
    data=json.loads((WORK/'settlements.geojson').read_text(encoding='utf8'))
    request=json.loads((WORK/'request.json').read_text(encoding='utf8'))
    def normalize(s):return ''.join(c for c in unicodedata.normalize('NFD',s.lower()) if not unicodedata.combining(c)).replace('-',' ').strip()
    def getnames(f):return [n['spelling']['SpellingOfName']['text'] for n in geographical_names(f)]
    def getname(f,label=None):
        names=getnames(f)
        return next((n for n in names if label and normalize(n)==normalize(label)),names[0])
    def getlocal(f):
        value=f['properties']['localType']['LocalisedCharacterString']
        return value.get('value',value) if isinstance(value,dict) else value
    grouped={}
    for f in data['features']:
        g=f['geometry'];p=f['properties']
        assert p['type']['href'].endswith('/populatedPlace') and g['type']=='Point'
        lon,lat=g['coordinates'][:2]
        if not(-5.1<lon<-1.9 and 39.4<lat<41.4):continue
        for name in getnames(f):
            key=normalize(name)
            if key in ['la granja de san ildefonso','real sitio de san ildefonso','granja de san ildefonso (la)','ildefonso (san)']:key='san ildefonso'
            if key=='san lorenzo del escorial':key='san lorenzo de el escorial'
            if key=='escorial (el)':key='el escorial'
            if key=='tiemblo (el)':key='el tiemblo'
            grouped.setdefault(key,[]).append(f)
    expected_boxes={'Madrid':[-3.8,40.3,-3.5,40.55],'Toledo':[-4.1,39.8,-3.9,39.95],'Segovia':[-4.2,40.9,-4.0,41.0],'Ávila':[-4.8,40.6,-4.6,40.75],'Guadalajara':[-3.25,40.55,-3.1,40.72],'Cuenca':[-2.25,40.0,-2.0,40.15]}
    features=[];missing=[];verification=[]
    for label in CAPITALS+TOWNS:
        candidates=grouped.get(normalize(label),[])
        if not candidates:missing.append(label);continue
        capital=label in CAPITALS
        def preference(f):
            local=normalize(getlocal(f))
            preferred=(0 if local=='capital de provincia' else 1 if local.startswith('capital de comunidad') else 2) if capital else (0 if 'capital de municipio' in local else 1 if 'nucleo' in local else 2)
            return preferred,f['id']
        candidates.sort(key=preference);f=candidates[0];p=f['properties'];coords=f['geometry']['coordinates'];local=getlocal(f)
        if capital:
            assert normalize(local).startswith('capital de provincia'),(label,local)
            west,south,east,north=expected_boxes[label];assert west<coords[0]<east and south<coords[1]<north,(label,coords)
        gn=next((n for n in geographical_names(f) if n['spelling']['SpellingOfName']['text']==getname(f,label)),geographical_names(f)[0])
        item={'type':'Feature','id':f['id'],'geometry':{'type':'Point','coordinates':coords},'properties':{'id':f['id'],'name':label,'sourceName':getname(f,label),'sourceNames':getnames(f),'rank':'capital' if capital else 'town','minZoom':7 if capital else 10.5,'coordinatesWGS84':coords,'kind':'urban-orientation','source':'IGN NGBE','sourceType':p['type']['href'],'sourceLocalType':local,'sourceIdentifier':p['inspireId']['Identifier'],'sourceOfName':gn.get('sourceOfName'),'sourceVersion':p.get('beginLifespanVersion'),'checked_at':'2026-10-27'}}
        features.append(item);verification.append({'name':label,'source_name':getname(f,label),'source_feature_id':f['id'],'source_local_type':local,'coordinates':coords,'capital_point_verified':capital})
    assert len([f for f in features if f['properties']['rank']=='capital'])==6
    assert len(features)>=26
    assert len({f['id'] for f in features})==len(features)
    assert all(all(isinstance(c,(int,float)) and math.isfinite(c) for c in f['geometry']['coordinates']) for f in features)
    out=ROOT/'dist/data';out.mkdir(parents=True,exist_ok=True)
    content=(json.dumps({'type':'FeatureCollection','features':features},ensure_ascii=False,separators=(',',':'))+'\n').encode('utf8')
    (out/'cities.geojson').write_bytes(content)
    meta={'title':'Puntos urbanos de orientación — Madrid y entorno','provider':'Instituto Geográfico Nacional','dataset':'Nomenclátor Geográfico Básico de España (NGBE)','checked_at':'2026-10-27','source_service':BASE,'capabilities_url':BASE+'?service=WFS&request=GetCapabilities&version=2.0.0','official_product_url':'https://centrodedescargas.cnig.es/CentroDescargas/nomenclator-geografico-basico-espana','official_catalogue_url':'https://datos.gob.es/es/catalogo/e0dat0002-nomenclator-geografico-basico-de-espana1','license':{'name':'CC BY 4.0','url':'https://creativecommons.org/licenses/by/4.0/','attribution':'NGBE CC-BY 4.0 ign.es','confirmed_by':'WFS AccessConstraints'},'crs':{'source_service_default':'ETRS89 / EPSG:4258','requested_output':'EPSG:4326 / WGS84','coordinate_order':'longitude,latitude','local_reprojection':False},'selection':{'feature_type':'gn:NamedPlace','required_named_place_type':'https://inspire.ec.europa.eu/codelist/NamedPlaceTypeValue/populatedPlace','urban_point_policy':'Only official populatedPlace POINT records selected. administrativeUnit records, polygon centroids, landforms, buildings and other homonyms excluded. Province-capital population records were required for all six capitals.','regional_selection_bbox':[-5.1,39.4,-1.9,41.4],'download_scope':'Small exact-name batches; no nationwide dataset downloaded.','rank_policy':'Editorial display priority only: capital for six province capitals, town for remaining selected settlements. These ranks do not alter official legal city status.','minZoom_policy':{'capital':7,'town':10.5},'unmatched_requested_names':missing},'counts':{'total':len(features),'capital':6,'town':len(features)-6},'limitations':['Named place points locate the settlement for map orientation; they are not entrance, parking, postal address or surveyed monument coordinates.','Point positions are copied from IGN without geometry derivation or centroid calculation. No independent positional survey accuracy is asserted.','Source version dates are recorded per feature where supplied. The extraction is a dated local snapshot, not a live synchronisation.'],'validation':{'all_six_capitals_verified_as_province_capital_population_points':True,'all_geometries_points':True,'all_selected_records_populated_place':True,'all_coordinates_finite_and_regional':True,'ids_unique':True,'coordinates_unchanged_from_ign':True},'file':{'name':'cities.geojson','bytes':len(content),'sha256':hashlib.sha256(content).hexdigest()},'features':verification,'requests':request['requests']}
    meta['official_product_url']='https://centrodedescargas.cnig.es/CentroDescargas/buscadorCatalogo.do?codFamilia=NGBES'
    meta['service_response_caveat']='The service emits a FeatureCollection without a features member for an empty result. The empty final alias batch was recorded as zero features; no entity was inferred from it.'
    for entry in meta['features']:entry['settlement_point_verified']=True
    (out/'metadata-city.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'counts':meta['counts'],'missing':missing,'bytes':len(content),'features':verification},ensure_ascii=False))
