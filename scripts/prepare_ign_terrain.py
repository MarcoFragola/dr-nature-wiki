import urllib.request,urllib.parse,json,sys,hashlib,math
from pathlib import Path
from xml.etree import ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT/'tmp/terrain-research';WORK.mkdir(parents=True,exist_ok=True)
BASE='https://servicios.idee.es/wcs-inspire/mdt'
def fetch(params,name):
    url=BASE+'?'+urllib.parse.urlencode(params,doseq=True)
    req=urllib.request.Request(url,headers={'User-Agent':'DrNatureWiki/1.0 (official regional terrain integration)'})
    with urllib.request.urlopen(req,timeout=120) as r:data=r.read()
    (WORK/name).write_bytes(data)
    return url,data
mode=sys.argv[1] if len(sys.argv)>1 else 'capabilities'
if mode=='capabilities':
    url,data=fetch({'service':'WCS','request':'GetCapabilities','version':'2.0.1'},'capabilities.xml')
    root=ET.fromstring(data)
    print(url)
    for e in root.iter():
        tag=e.tag.rsplit('}',1)[-1]
        if tag in ['Title','Abstract','Fees','AccessConstraints','CoverageId','formatSupported','Profile','crsSupported','Value'] and e.text:print(tag,e.text.strip()[:6000])
if mode=='describe':
    url,data=fetch({'service':'WCS','request':'DescribeCoverage','version':'2.0.1','coverageId':'Elevacion4258_5'},'coverage.xml')
    print(url);print(data.decode()[:16000])
if mode=='download':
    params={'service':'WCS','request':'GetCoverage','version':'2.0.1','coverageId':'Elevacion4258_5','subset':['long(-4.9,-2.75)','lat(39.65,41.45)'],'scaleSize':'long(1024),lat(1024)','format':'image/tiff','outputCRS':'http://www.opengis.net/def/crs/EPSG/0/4326'}
    url,data=fetch(params,'madrid-regional.tif')
    if data.lstrip().startswith(b'<'):print(data.decode()[:6000]);raise ValueError('WCS returned XML instead of terrain')
    from PIL import Image
    im=Image.open(WORK/'madrid-regional.tif')
    print('IMAGE',im.mode,im.size,'BYTES',len(data))
    print('TAGS',json.dumps({str(k):list(v) if isinstance(v,tuple) else v for k,v in im.tag_v2.items()},ensure_ascii=False,default=str))
    (WORK/'request.json').write_text(json.dumps({'url':url,'request_parameters':params,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()},indent=2),encoding='utf8')
    print('REQUEST',url)
if mode=='package':
    import numpy as np
    from PIL import Image
    im=Image.open(WORK/'madrid-regional.tif');a=np.asarray(im,dtype='<f4')
    assert a.shape==(1024,1024) and np.isfinite(a).all()
    assert float(a.min())>0 and float(a.max())<3000
    assert np.array_equal(a,np.asarray(im))
    scale=im.tag_v2[33550];tie=im.tag_v2[33922]
    width,height=im.size;west,north=tie[3],tie[4];dx,dy=scale[:2];east=west+width*dx;south=north-height*dy
    assert abs(west+4.9)<1e-8 and abs(east+2.75)<1e-8 and abs(south-39.65)<1e-8 and abs(north-41.45)<1e-8
    assert 4326 in im.tag_v2[34735]
    out=ROOT/'dist/data/terrain';out.mkdir(parents=True,exist_ok=True)
    grid=a.tobytes(order='C');(out/'madrid-1024.f32').write_bytes(grid)
    tif=(WORK/'madrid-regional.tif').read_bytes();(out/'madrid-mdt05-regional.tif').write_bytes(tif)
    request=json.loads((WORK/'request.json').read_text(encoding='utf8'))
    metadata={
      'title':'Relieve regional real de Madrid y entorno — IGN MDT05 remuestreado para portada',
      'provider':'Instituto Geográfico Nacional / Sistema Cartográfico Nacional',
      'downloaded_at':'2026-10-27',
      'source':{
        'service_url':BASE,'coverage_id':'Elevacion4258_5','get_capabilities_url':BASE+'?service=WCS&request=GetCapabilities&version=2.0.1',
        'describe_coverage_url':BASE+'?service=WCS&request=DescribeCoverage&version=2.0.1&coverageId=Elevacion4258_5',
        'get_coverage_url':request['url'],'request_parameters':request['request_parameters'],
        'service_metadata_url':'https://www.idee.es/csw-inspire-idee/srv/spa/csw?Service=CSW&Request=GetRecordById&Version=2.0.2&outputSchema=http://www.isotc211.org/2005/gmd&elementSetName=full&id=spaignwcs_mdt',
        'official_catalogue_url':'https://datos.gob.es/es/catalogo/e0dat0002-wcs-de-modelos-digitales-del-terreno-de-espana1',
        'official_mdt05_product_url':'https://centrodedescargas.cnig.es/CentroDescargas/modelo-digital-terreno-mdt05-primera-cobertura',
        'original_source_grid_spacing_m':5,
        'original_sampling_note':'Coverage identifier names the MDT05 source. This regional output is substantially downsampled and must not be described as a 5 m delivered mesh.',
        'acquisition_dates':'Not determined for each contributing LiDAR flight; no single acquisition year asserted.'
      },
      'license':{'name':'CC BY 4.0','url':'https://creativecommons.org/licenses/by/4.0/','attribution':'CC BY 4.0 scne.es','service_access_constraints':'CC BY 4.0 scne.es','required_visible_credit':'Relieve: IGN / SCNE · MDT05 remuestreado · CC BY 4.0 scne.es'},
      'crs':{'source_coverage':'ETRS89 geographic / EPSG:4258 (coverage identifier)','delivered_geotiff':'WGS 84 geographic / EPSG:4326, confirmed by GeoTIFF key 2048','axis_order':'longitude, latitude','local_reprojection':'None; output EPSG:4326 requested from WCS. No local datum shift applied.','height_type':'Orthometric terrain elevations in metres, according to the official MDT05 product description.','vertical_datum_detail':'No more specific vertical CRS/epoch is asserted from this WCS response; the response does not encode a vertical GeoTIFF key.'},
      'grid':{'file':'madrid-1024.f32','format':'IEEE754 Float32 little-endian, headerless, row-major','width':width,'height':height,'bbox':[west,south,east,north],'bbox_order':'west,south,east,north','pixel_is_area':True,'origin':'north-west outer pixel corner','west':west,'north':north,'pixel_size_longitude_degrees':dx,'pixel_size_latitude_degrees':dy,'row_direction':'north to south','column_direction':'west to east','pixel_center_formula':{'longitude':'west + (column + 0.5) * pixel_size_longitude_degrees','latitude':'north - (row + 0.5) * pixel_size_latitude_degrees'},'sample_index_formula':{'column':'(longitude - west) / pixel_size_longitude_degrees - 0.5','row':'(north - latitude) / pixel_size_latitude_degrees - 0.5','byte_offset':'4 * (rowInteger * width + columnInteger)'},'approximate_spacing_m_at_centre':[dx*111320*math.cos(math.radians((north+south)/2)),dy*111320],'no_data_value':None,'outside_bbox_policy':'Return null / no sample. Do not extrapolate or wrap to fill areas outside this rectangle.','min_height_m':float(a.min()),'max_height_m':float(a.max()),'all_cells_valid_in_this_crop':True},
      'processing':{'server_scaling':'WCS scaleSize=long(1024),lat(1024)','interpolation':'No interpolationMethod override sent; WCS server default. Exact server resampling kernel not asserted.','server_geotiff_sample_type':'Signed Int16 (GeoTIFF BitsPerSample=16, SampleFormat=2)','value_quantisation_in_response_m':1,'float32_conversion':'Exact cast of the received integer elevation values; no value modification, smoothing, gap filling, clipping or added relief.','visual_exaggeration_applied_to_data':False,'vertical_scale_factor':1,'describe_coverage_unit_caveat':'The DescribeCoverage range uom is a generic radiation unit inconsistent with MDT terrain metadata. Heights are interpreted using the official MDT05 product definition, not that malformed unit field.'},
      'validation':{'dimensions':[width,height],'geo_keys_verified':True,'bbox_from_geotiff_tags_verified':True,'all_values_finite':True,'zero_cells':int((a==0).sum()),'minus9999_cells':int((a==-9999).sum()),'value_range_plausible_for_region':True,'float32_values_equal_to_wcs_geotiff':True,'independent_survey_validation':False},
      'files':[{'file':'madrid-1024.f32','bytes':len(grid),'sha256':hashlib.sha256(grid).hexdigest()},{'file':'madrid-mdt05-regional.tif','bytes':len(tif),'sha256':hashlib.sha256(tif).hexdigest()}]
    }
    (out/'metadata.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    (out/'README.txt').write_text('IGN regional terrain crop for the cover\n\nFetch metadata.json and madrid-1024.f32. The binary has exactly 1024*1024 Float32 little-endian samples, row-major, north to south. Heights are metres with no visual exaggeration applied.\n\nUse the pixel-centre and sample-index formulae in metadata.json. Return null outside bbox. Bilinear interpolation for display can use the four surrounding valid samples; it must not extend coverage outside the rectangle.\n\nThe original WCS GeoTIFF is retained as madrid-mdt05-regional.tif. Its sample values are signed Int16; Float32 conversion preserves them exactly. Effective spacing is about 177 by 196 metres, despite MDT05 source naming. Do not advertise a delivered 5 m terrain mesh.\n\nVisible attribution: Relieve: IGN / SCNE · MDT05 remuestreado · CC BY 4.0 scne.es.\n',encoding='utf8')
    print(json.dumps({'output':str(out),'grid':metadata['grid'],'files':metadata['files']},ensure_ascii=False))
if mode=='tiles':
    import numpy as np
    from PIL import Image
    out=ROOT/'dist/data/terrain'
    meta=json.loads((out/'metadata.json').read_text(encoding='utf8'))
    g=meta['grid'];width,height=g['width'],g['height'];west,south,east,north=g['bbox'];dx=g['pixel_size_longitude_degrees'];dy=g['pixel_size_latitude_degrees']
    grid=np.fromfile(out/g['file'],dtype='<f4').reshape(height,width)
    def xtile(lon,z):return int(math.floor((lon+180)/360*(2**z)))
    def ytile(lat,z):return int(math.floor((1-math.asinh(math.tan(math.radians(lat)))/math.pi)/2*(2**z)))
    tile_records=[];total=0;outside=0;max_error=0.
    for z in range(6,11):
        n=2**z;count=0
        for x in range(xtile(west,z),xtile(east,z)+1):
            lon=((x*256+np.arange(256,dtype=np.float64)+.5)/(n*256)*360-180)[None,:]
            u=np.clip((lon-west)/dx-.5,0,width-1);x0=np.floor(u).astype(np.int32);x1=np.minimum(x0+1,width-1);tx=u-x0
            for y in range(ytile(north,z),ytile(south,z)+1):
                lat=np.degrees(np.arctan(np.sinh(math.pi*(1-2*(y*256+np.arange(256,dtype=np.float64)+.5)/(n*256)))))[:,None]
                v=np.clip((north-lat)/dy-.5,0,height-1);y0=np.floor(v).astype(np.int32);y1=np.minimum(y0+1,height-1);ty=v-y0
                h=(grid[y0,x0]*(1-tx)+grid[y0,x1]*tx)*(1-ty)+(grid[y1,x0]*(1-tx)+grid[y1,x1]*tx)*ty
                valid=(lon>=west)&(lon<=east)&(lat>=south)&(lat<=north)
                q=np.rint((h+32768)*256).astype(np.uint32)
                rgba=np.empty((256,256,4),dtype=np.uint8)
                rgba[:,:,0]=(q>>16)&255;rgba[:,:,1]=(q>>8)&255;rgba[:,:,2]=q&255;rgba[:,:,3]=255
                decoded=rgba[:,:,0].astype(float)*256+rgba[:,:,1]+rgba[:,:,2]/256-32768
                max_error=max(max_error,float(np.max(np.abs(decoded-h))))
                dest=out/'tiles'/str(z)/str(x)/(str(y)+'.png');dest.parent.mkdir(parents=True,exist_ok=True)
                Image.fromarray(rgba).save(dest,compress_level=9)
                assert Image.open(dest).size==(256,256)
                tile_records.append({'z':z,'x':x,'y':y,'bytes':dest.stat().st_size,'inside_bbox_pixels':int(valid.sum()),'outside_bbox_pixels':int((~valid).sum())})
                count+=1;total+=dest.stat().st_size;outside+=int((~valid).sum())
        print('ZOOM',z,'TILES',count,flush=True)
    meta['terrarium_tiles']={
      'url_template':'data/terrain/tiles/{z}/{x}/{y}.png','tile_scheme':'XYZ Web Mercator / Slippy map','tile_size':256,'encoding':'terrarium','minzoom':6,'maxzoom':10,'bounds':g['bbox'],
      'height_decode':'height_m = red*256 + green + blue/256 - 32768',
      'resampling':'For each XYZ pixel centre, invert spherical Mercator to longitude/latitude, then bilinearly sample the original 1024x1024 WCS grid using its geographic pixel-centre coordinates.',
      'outside_bounds_alpha':255,
      'partial_tile_edge_padding':'For pixels outside the exact crop bbox, RGB contains the nearest edge height extruded only as technical padding; alpha stays 255 so browser premultiplication cannot erase RGB and create false -32768 m cliffs. These padded values are NOT real terrain coverage. Nodata is declared externally by the exact bounds, not by transparent pixels. Source bounds and camera must remain within the actual crop; sampling outside the bbox must return null.',
      'inside_half_pixel_border':'The narrow strip between the source pixel edge and its centre uses the nearest source sample, without extending declared coverage.',
      'tile_count':len(tile_records),'total_png_bytes':total,'outside_bbox_pixels_with_technical_edge_padding':outside,'maximum_terrarium_encode_error_m':max_error,
      'effective_source_sampling':'Approximately 178 x 196 m at regional centre. Tile encoding and zoom levels do not add source resolution.',
      'visual_exaggeration_applied_to_heights':False,
      'tiles':tile_records
    }
    meta['validation']['all_terrarium_tiles_decode_as_256px_rgba']=True
    meta['validation']['terrarium_roundtrip_max_error_m']=max_error
    (out/'metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    readme=(out/'README.txt').read_text(encoding='utf8').split('\nMapLibre source:')[0]
    (out/'README.txt').write_text(readme+'\nMapLibre source: type raster-dem, tiles [data/terrain/tiles/{z}/{x}/{y}.png], tileSize256, encoding terrarium, minzoom6, maxzoom10, bounds equal to metadata bbox. Tiles are XYZ/Web Mercator. Partial tiles have opaque alpha255 and edge-extruded RGB solely as technical padding; outside values are NOT geographic coverage. Transparency is avoided because canvas premultiplication can erase hidden RGB and produce -32768 m cliffs. Nodata outside the exact bbox is defined by bounds and metadata. Camera and source bounds must respect the crop; samples outside must return null.\n',encoding='utf8')
    print(json.dumps({'tile_count':len(tile_records),'total_bytes':total,'max_roundtrip_error_m':max_error},ensure_ascii=False))
