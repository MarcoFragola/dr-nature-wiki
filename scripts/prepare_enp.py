"""Import official ENP2025 polygons for Madrid, Castilla y León and Castilla-La Mancha.

Requires pyproj>=3.7 for the official CRS conversion. The website has no Python
dependency; this is an offline/source-preparation tool only.
"""
import argparse, hashlib, io, json, re, sys, zipfile
from pathlib import Path
from prepare_geography import CACHE, OUT, ROOT, ENP_PAGE, ENP_ZIP, fetch, write, bbox, points

try:
    from pyproj import Transformer
except ImportError:
    # Isolated preparation dependency used on this desktop; never shipped to dist.
    sys.path.insert(0,str(CACHE/'python-packages'))
    from pyproj import Transformer

def stream_features(binary):
    stream=io.TextIOWrapper(binary,encoding='utf-8-sig')
    buffer='';decoder=json.JSONDecoder()
    while True:
        chunk=stream.read(65536)
        if not chunk:raise ValueError('Feature collection header missing')
        buffer+=chunk;match=re.search(r'"features"\s*:\s*\[',buffer)
        if match:buffer=buffer[match.end():];break
    while True:
        buffer=buffer.lstrip(' \r\n\t,')
        if buffer.startswith(']'):return
        try:
            feature,end=decoder.raw_decode(buffer)
        except json.JSONDecodeError:
            more=stream.read(65536)
            if not more:raise ValueError('Truncated source FeatureCollection')
            buffer+=more;continue
        yield feature;buffer=buffer[end:]

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--offline',action='store_true');args=parser.parse_args()
    raw=fetch(ENP_ZIP,CACHE/'enp2025.zip',args.offline)
    transformer=Transformer.from_crs('EPSG:25830','EPSG:4326',always_xy=True)
    groups={};source_total=0;selected_parts=0;authority_counts={}
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        with archive.open('Enp2025_p.json') as binary:
            for feature in stream_features(binary):
                source_total+=1;p=feature['properties'];authority=str(p.get('NUT2',''))
                if not re.search(r'\b(?:30|41|42)\b',authority) and p.get('SITE_CODE_') not in ['ES801001','ES802001']:continue
                selected_parts+=1;authority_counts[authority]=authority_counts.get(authority,0)+1
                geometry=feature['geometry'];xy=list(points(geometry['coordinates']));xs,ys=transformer.transform([p[0] for p in xy],[p[1] for p in xy]);it=iter(zip(xs,ys))
                def transform(c):
                    if c and isinstance(c[0],(float,int)):
                        x,y=next(it);return [round(x,6),round(y,6)]
                    return [transform(child) for child in c]
                coordinates=transform(geometry['coordinates'])
                polygons=[coordinates] if geometry['type']=='Polygon' else coordinates
                code=str(p.get('SITE_CODE_') or p.get('SITE_CDDA'))
                key=code+':'+str(p.get('DESIG_ABBR',''))
                group=groups.setdefault(key,{'source_code':code,'name':p.get('SITE_NAME'),'designation':p.get('ODESIGNATE'),'designation_code':p.get('DESIG_ABBR'),'cdda':p.get('SITE_CDDA'),'authorities':set(),'source_rows':[],'polygons':[]})
                group['authorities'].add(authority);group['source_rows'].append(p.get('FID',feature.get('id')));group['polygons'].extend(polygons)
    features=[]
    for key,item in groups.items():
        polygons=item.pop('polygons');geometry={'type':'Polygon','coordinates':polygons[0]} if len(polygons)==1 else {'type':'MultiPolygon','coordinates':polygons}
        bb=bbox(geometry);assert -8<bb[0]<bb[2]<1 and 37<bb[1]<bb[3]<44
        props={'id':'miteco:enp:'+key,'name':item['name'],'type':'protected-area','source_id':item['source_code'],'source':'miteco-enp','source_url':ENP_PAGE,'bbox':bb,'minZoom':7,'geographic_precision_m':None,'source_scale':'1:50,000','source_feature_date':'2025-12-31','verified_at':'2026-10-27','designation':item['designation'],'designation_code':item['designation_code'],'cdda_id':item['cdda'],'authorities':sorted(item['authorities']),'source_rows':item['source_rows'],'photograph':None,'verification':'official_source_geometry_not_live_access_rules'}
        features.append({'type':'Feature','id':props['id'],'properties':props,'geometry':geometry})
    source={'title':'Espacios Naturales Protegidos, diciembre2025','publisher':'MITECO / Subdirección General del Sistema Integrado de Información de la Biodiversidad; cartography from competent administrations','page_url':ENP_PAGE,'download_url':ENP_ZIP,'license':'Reutilización con cita de fuente y fecha conforme al aviso legal MITECO; no se presume una licencia Creative Commons específica','license_url':'https://www.miteco.gob.es/es/atencion-al-ciudadano/aviso-legal.html','attribution':'Origen de los datos: Ministerio para la Transición Ecológica y el Reto Demográfico. ENP, diciembre2025. Reproyección y preparación para Dr Nature wiki. Sin patrocinio ni aval ministerial.','source_update_date':'2025-12-31','source_crs':'EPSG:25830','output_crs':'EPSG:4326 longitude,latitude','coordinate_operation':'PROJ/pyproj Transformer.from_crs(25830,4326,always_xy=True); source ETRS89/UTM30N to WGS84. Source scale1:50,000; no metre-level boundary accuracy claim.','sha256':hashlib.sha256(raw).hexdigest()}
    metadata={'status':'imported','source':source,'source_peninsular_rows':source_total,'selected_source_rows':selected_parts,'unique_site_designations':len(features),'authority_counts':authority_counts,'scope':'All source features whose NUT2 competent-authority field includes30(Madrid),41(Castilla y León),42(Castilla-La Mancha), plus official inter-autonomous national parks ES801001(Picos de Europa) and ES802001(Sierra de Guadarrama), coded80 by the source and explicitly documented by MITECO as extending into these regions. Complete official site geometries retained, including the park parts in Asturias/Cantabria and outside the hydrography bbox. This is not all Spanish ENP.','part_deduplication':'Source parts sharing SITE_CODE_ and DESIG_ABBR merged as Polygon/MultiPolygon; original source row IDs retained. No polygon union, clipping or smoothing.'}
    write(CACHE/'enp-normalized.json',{'metadata':metadata,'features':features})
    print(json.dumps({'features':len(features),'selected_rows':selected_parts,'source_rows':source_total,'authorities':authority_counts,'output_bytes':(CACHE/'enp-normalized.json').stat().st_size},ensure_ascii=False))

if __name__=='__main__':main()
