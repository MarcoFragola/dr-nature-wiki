"""Add a broadly located Jerte cherry-blossom destination without locating a private photo."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'dist/data/catalogue.json'
before=PATH.read_bytes();data=json.loads(before)
DATE='2026-10-27'
SOURCES={
 'jerte-geografia':{'title':'Mancomunidad Valle del Jerte — Situación geográfica y naturaleza','url':'https://turismovalledeljerte.com/valle-del-jerte/situacion-geografica','type':'official','checked_at':DATE},
 'jerte-floracion':{'title':'Mancomunidad Valle del Jerte — Cerezo en flor y seguimiento estacional','url':'https://www.turismovalledeljerte.com/cerezo-en-flor','type':'official','checked_at':DATE},
 'jerte-caozo':{'title':'Mancomunidad Valle del Jerte — Ruta Cascada del Caozo SL-CC32','url':'https://turismovalledeljerte.com/que-ver-en-el-valle-del-jerte/naturaleza-activa/rutas-de-senderismo/ruta-cascada-del-caozo-sl-cc-32','type':'official','checked_at':DATE},
 'jerte-cabezuela-ancla':{'title':'Mancomunidad Valle del Jerte — Punto publicado en Cabezuela del Valle, Ruta de las Juderías','url':'https://turismovalledeljerte.com/que-ver-en-el-valle-del-jerte/naturaleza-activa/rutas-de-senderismo/ruta-de-las-juderias-pr-cc-10','type':'official','checked_at':DATE}
}
PLACE={
 'id':'valle-jerte',
 'name':'Cerezos en flor · Valle del Jerte',
 'name_en':'Cherry blossom · Jerte Valley',
 'area_name':'Valle del Jerte',
 'regions':['Extremadura'],
 'coordinates':[-5.81,40.20],
 'coordinate_order':'longitude,latitude',
 'coordinate_status':'approximate_valley_overview_anchor_not_photo_location_or_viewpoint',
 'coordinate_evidence':{'source_id':'jerte-cabezuela-ancla','published_coordinates':[-5.806568,40.196793],'method':'The official tourist page publishes a point in Cabezuela del Valle. It is rounded to two decimal places solely as an overview anchor for the wider valley; it is not the position of the personal photograph, a viewpoint, parking area or trailhead.','checked_at':DATE},
 'place_kind':'cultivated_landscape',
 'is_guest_destination':True,
 'editorial_scope':'Invited destination in Extremadura, explicitly included by the user; this is not a comprehensive regional catalogue or a region bordering Madrid.',
 'categories':['flora','landscape'],
 'habitats':['orchard','river','oak-forest'],
 'summary':{
   'es':'Bancales de cerezos cultivados acompañan al río Jerte y a las laderas del norte de Cáceres. La floración transforma este paisaje agrario a distintas cotas; las gargantas y los robledales completan el entorno del valle.',
   'en':'Terraced cherry orchards follow the River Jerte and the hillsides of northern Cáceres. Blossom transforms this cultivated landscape at different elevations; gorges and oak woodland complete the valley setting.'
 },
 'species_ids':[],
 'species_scope':'Cultivated cherry landscape documented by the local tourism authority. No cultivar or exact botanical specimen is identified from the personal photograph.',
 'water':['Río Jerte'],
 'route_ids':['jerte-caozo'],
 'sources':['jerte-geografia','jerte-floracion','jerte-caozo','jerte-cabezuela-ancla'],
 'notes':[
   'Destino invitado en Extremadura, fuera del núcleo editorial inicial de Madrid y sus comunidades vecinas.',
   'La fotografía personal se vincula únicamente al Valle del Jerte. No se atribuye a un mirador oficial ni se fija una ubicación exacta de la toma.',
   'La floración no sucede simultáneamente en todas las cotas. Consulta el seguimiento oficial de cada primavera; las fechas de una edición no son una previsión para otros años.',
   'La ruta del Caozo es una propuesta documentada para conocer el valle entre cerezales. No se afirma que pase por el lugar de la fotografía.'
 ],
 'notes_en':[
   'An invited destination in Extremadura, outside the initial editorial focus on Madrid and neighbouring regions.',
   'The personal photograph is linked only to the Jerte Valley. It is not assigned to an official viewpoint or an exact camera location.',
   'Blossom does not occur simultaneously at all elevations. Check each spring’s official updates; one year’s dates are not a forecast for another year.',
   'The Caozo trail is a documented suggestion for exploring the valley among cherry orchards. It is not claimed to pass the photograph’s location.'
 ],
 'photo_context':{'caption':{'es':'Cerezos en flor · Valle del Jerte','en':'Cherry blossom · Jerte Valley'},'location_scope':'Valle del Jerte, Cáceres, Extremadura, confirmed by the user','specific_viewpoint':None,'exact_photo_coordinates':None,'cultivar_identification':None,'image_taxon_diagnosis_performed':False},
 'seasonality':{'context':'seasonal_cherry_blossom_not_live_status','official_updates_url':'https://www.turismovalledeljerte.com/cerezo-en-flor','simultaneous_bloom_across_valley':False,'future_bloom_dates':None},
 'verified_at':DATE
}
ROUTE={
 'id':'jerte-caozo',
 'name':'Cascada del Caozo · SL-CC32',
 'name_en':'Caozo Waterfall · SL-CC32',
 'place_id':'valle-jerte',
 'distance_km':7,
 'duration_minutes':135,
 'ascent_m':265,
 'descent_m':265,
 'distance_scope':'entire_described_route',
 'difficulty_official':'Baja',
 'shape':'circular',
 'family_official':None,
 'wheelchair_verified':None,
 'dogs':{'status':'unknown','source':None},
 'cycling_verified':None,
 'route_status':'published_official_not_live_conditions',
 'source_ids':['jerte-caozo'],
 'gpx_path':None,
 'geojson_path':None,
 'geometry_status':'not_imported',
 'track_url':None,
 'start_coordinates':[-5.873492,40.134644],
 'start_coordinates_status':'point_published_by_official_route_page_not_verified_parking',
 'start_name':'Valdastillas, salida y llegada de la ficha SL-CC32',
 'source_elevations_present':False,
 'metric_note':'Métricas publicadas por la Mancomunidad: 7 km, 2 h 15 min y 265 m de subida y de bajada. El itinerario recorre cerezales y robledales; no se identifica como el lugar de la fotografía personal. La página enlaza un GPX, aún no incorporado al catálogo.',
 'metric_note_en':'The Mancomunidad publishes 7 km, 2 h 15 min and 265 m of ascent and descent. The trail crosses cherry orchards and oak woods; it is not identified as the personal photograph’s location. A GPX is linked by the source but has not been added to this catalogue.',
 'photo_location_relationship':'nearby_regional_suggestion_only_not_the_photo_site',
 'verified_at':DATE
}
assert not any(p['id']==PLACE['id'] for p in data['places']),'Jerte already exists; review rather than overwrite.'
assert not any(r['id']==ROUTE['id'] for r in data['routes']),'Caozo already exists; review rather than overwrite.'
assert not(set(SOURCES)&set(data['sources'])),'Source IDs already exist; review before updating.'
assert any(p['id']=='centro-lobo-iberico' for p in data['places']),'Current wolf-centre changes must be preserved.'
if 'Extremadura' not in data['regions']:data['regions'].append('Extremadura')
data['sources'].update(SOURCES);data['places'].append(PLACE);data['routes'].append(ROUTE)
assert all(s in data['sources'] for s in PLACE['sources']+ROUTE['source_ids'])
assert PLACE['route_ids']==[ROUTE['id']] and ROUTE['place_id']==PLACE['id']
assert PATH.read_bytes()==before,'Catalogue changed; rerun from the current content.'
temp=PATH.with_suffix('.jerte.tmp');temp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
assert PATH.read_bytes()==before,'Concurrent catalogue change detected before save.'
temp.replace(PATH)
print(json.dumps({'added_place':PLACE['id'],'title':PLACE['name'],'added_region':'Extremadura','added_route':ROUTE['id'],'new_species':0,'sources_added':len(SOURCES),'exact_photo_location':None,'wolf_centre_preserved':True,'counts':{k:len(data[k]) for k in ['places','routes','species']}},ensure_ascii=False))
