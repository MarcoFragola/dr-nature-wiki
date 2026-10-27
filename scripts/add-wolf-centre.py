"""Add the documented Robledo wolf centre, its guided visit and a scoped wolf card."""
import json,hashlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'dist/data/catalogue.json'
before=PATH.read_bytes();data=json.loads(before)
DATE='2026-10-27'
SOURCES={
 'centro-lobo-centro':{'title':'Centro del Lobo Ibérico — El centro y su entorno','url':'https://centrodellobo.es/el-centro-del-lobo-iberico','type':'official'},
 'centro-lobo-visitas':{'title':'Centro del Lobo Ibérico — Visitas y horario','url':'https://centrodellobo.es/visitas-y-horario','type':'official'},
 'centro-lobo-situacion':{'title':'Centro del Lobo Ibérico — Situación y acceso recomendado','url':'https://centrodellobo.es/situacion','type':'official'},
 'centro-lobo-reservas':{'title':'Centro del Lobo Ibérico — Reservas y normas de acceso','url':'https://centrodellobo.es/reserva','type':'official'},
 'centro-lobo-contacto':{'title':'Centro del Lobo Ibérico — Contacto','url':'https://centrodellobo.es/contacto','type':'official'},
 'centro-lobo-turismo':{'title':'Turismo Castilla y León — Centro del Lobo Ibérico, visita guiada de dos horas','url':'https://www.turismocastillayleon.com/es/naturaleza/centro-lobo-iberico-castilla-leon','type':'official'},
 'taxon-lobo-secem':{'title':'SECEM — Atlas de mamíferos, Canis lupus','url':'https://secem.es/mamiferos/atlas/canis-lupus','type':'taxon_reference','publisher':'Sociedad Española para la Conservación y Estudio de los Mamíferos'},
 'taxon-lobo-miteco':{'title':'MITECO — Lobo (Canis lupus) en España','url':'https://www.miteco.gob.es/es/biodiversidad/temas/conservacion-de-especies-amenazadas/vertebrados/lobo_espana.html','type':'official'}
}
for value in SOURCES.values():value['checked_at']=DATE
MAP_URL='https://www.google.com/maps/embed?pb=!1m14!1m8!1m3!1d11861.316930819046!2d-6.5739317!3d41.9932093!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x0%3A0xc9b8907f631099cd!2sCentro%20del%20Lobo%20Ib%C3%A9rico%20F%C3%A9lix%20Rodr%C3%ADguez%20de%20la%20Fuente!5e0!3m2!1ses!2ses!4v1674897291338!5m2!1ses!2ses'
PLACE={
 'id':'centro-lobo-iberico',
 'name':'Centro del Lobo Ibérico · Félix Rodríguez de la Fuente',
 'name_en':'Iberian Wolf Centre · Félix Rodríguez de la Fuente',
 'regions':['Castilla y León'],
 'coordinates':[-6.5739317,41.9932093],
 'coordinate_order':'longitude,latitude',
 'coordinate_status':'official_website_embedded_map_centre_not_verified_access_point',
 'coordinate_evidence':{'source_id':'centro-lobo-situacion','official_page_url':'https://centrodellobo.es/situacion','embedded_map_url':MAP_URL,'method':'Longitude and latitude are the map-centre parameters !2d/!3d in the Google map embedded by the official centre website, explicitly labelled with the centre name. Not interpreted as a surveyed building entrance or parking coordinate.','checked_at':DATE},
 'place_kind':'wildlife_education_centre',
 'managed_facility':True,
 'observation_context':'managed_fenced_enclosures_semifreedom_not_free_ranging_sighting',
 'habitats':['pine-forest','oak-forest','riparian-forest','scrub'],
 'summary':{
   'es':'Centro educativo en Robledo, Puebla de Sanabria, con exposición sobre el lobo y observación guiada de ejemplares en semilibertad dentro de grandes recintos vallados. El entorno combina pinar, pequeños robledales y vegetación de ribera.',
   'en':'An educational centre in Robledo, Puebla de Sanabria, with wolf interpretation and guided observation of animals in semi-free conditions inside large fenced enclosures. Pine woodland, small oak stands and riverside vegetation surround the site.'
 },
 'species_ids':['lobo-iberico','roble-melojo'],
 'species_scope':'Wolf presence refers exclusively to managed animals in the public centre enclosures. Woodland vegetation is documented by the centre. This is not a free-ranging wildlife sighting record.',
 'water':[],
 'route_ids':['visita-centro-lobo'],
 'sources':['centro-lobo-centro','centro-lobo-visitas','centro-lobo-situacion','centro-lobo-reservas','centro-lobo-turismo','centro-lobo-contacto'],
 'notes':[
   'Las visitas son guiadas y requieren reserva previa en la web del centro. Los turnos y condiciones se consultan allí.',
   'La observación se realiza en recintos con lobos en semilibertad; este marcador no señala un lugar de avistamiento de lobos libres.',
   'Acceso oficial por la ZA-921 desde Puebla de Sanabria, pasando por Ungilde y Robledo. El centro advierte evitar las pistas alternativas y el acceso desde Pedroso.',
   'El acceso peatonal desde el aparcamiento a la entrada es de unos 400 m. No equivale a la distancia total de la visita.',
   'La normativa de reservas indica que no se admite la entrada con perros.'
 ],
 'notes_en':[
   'Visits are guided and require advance booking on the centre website. Check time slots and current conditions there.',
   'Observation takes place in enclosures with wolves in semi-free conditions; this marker is not a free-ranging wolf sighting location.',
   'Official road access follows the ZA-921 from Puebla de Sanabria via Ungilde and Robledo. The centre advises avoiding alternative forest tracks and the route from Pedroso.',
   'The pedestrian approach from the car park to the entrance is about 400 m. It is not the total distance of the visit.',
   'The booking rules state that dogs are not admitted.'
 ],
 'directions_url':'https://centrodellobo.es/situacion',
 'directions_policy':'use_official_access_instructions_before_automatic_road_routing',
 'reservation_url':'https://centrodellobo.es/reserva',
 'guided_only':True,
 'reservation_required':True,
 'verified_at':DATE
}
ROUTE={
 'id':'visita-centro-lobo',
 'name':'Visita guiada al Centro del Lobo Ibérico',
 'name_en':'Guided visit to the Iberian Wolf Centre',
 'place_id':'centro-lobo-iberico',
 'activity_type':'guided_facility_visit',
 'distance_km':None,
 'duration_minutes':120,
 'duration_scope':'guided_visit_museum_and_managed_wolf_observation_not_walking_time',
 'duration_source_id':'centro-lobo-turismo',
 'duration_label':{'es':'Visita guiada · 2 h','en':'Guided visit · 2 h'},
 'ascent_m':None,
 'distance_scope':'guided_facility_visit_total_distance_not_published',
 'difficulty_official':'No publicada',
 'shape':'not_specified',
 'family_official':None,
 'wheelchair_verified':None,
 'dogs':{'status':'prohibited','source':'centro-lobo-reservas'},
 'cycling_verified':None,
 'route_status':'published_official_visit_not_live_availability',
 'source_ids':['centro-lobo-visitas','centro-lobo-turismo','centro-lobo-reservas','centro-lobo-situacion'],
 'gpx_path':None,
 'geojson_path':None,
 'geometry_status':'not_imported',
 'track_url':None,
 'start_coordinates':None,
 'start_name':'Centro del Lobo Ibérico, Robledo (Puebla de Sanabria)',
 'source_elevations_present':False,
 'metric_note':'Las 2 horas son la duración publicada de la visita guiada al museo y a los observatorios, no un tiempo de senderismo. Los 400 m de acceso peatonal al centro no son la longitud total de esta visita. Distancia completa y desnivel no publicados.',
 'metric_note_en':'The published two hours cover the guided museum and observation visit, not hiking time. The 400 m pedestrian approach is not the total length of the visit. Total distance and ascent are not published.',
 'reservation_required':True,
 'guided_only':True,
 'reservation_url':'https://centrodellobo.es/reserva',
 'directions_url':'https://centrodellobo.es/situacion',
 'observation_context':'managed_wolves_in_semifreedom_not_free_ranging_sightings',
 'verified_at':DATE
}
WOLF={
 'id':'lobo-iberico',
 'name':{'es':'Lobo ibérico','en':'Iberian wolf'},
 'scientific_name':'Canis lupus',
 'group':'mammal',
 'summary':{
   'es':'Este registro conecta el lobo ibérico con los ejemplares mantenidos en semilibertad en el centro de Robledo. No documenta observaciones de lobos libres en sus alrededores.',
   'en':'This record links the Iberian wolf to animals kept in semi-free conditions at the Robledo centre. It does not document free-ranging wolf sightings nearby.'
 },
 'documented_area':'Centro del Lobo Ibérico, Robledo (Puebla de Sanabria): ejemplares gestionados en recintos de semilibertad.',
 'documented_area_en':'Iberian Wolf Centre, Robledo (Puebla de Sanabria): managed animals in semi-free enclosures.',
 'sources':['centro-lobo-centro','centro-lobo-visitas','taxon-lobo-secem','taxon-lobo-miteco'],
 'observation_status':'documented_managed_centre_animals_not_wild_sighting',
 'location_policy':'Solo se enlaza el equipamiento público. No se publican localizaciones de manadas, madrigueras ni puntos de avistamiento libre.',
 'location_policy_en':'Only the public visitor facility is linked. No pack, den or free-ranging sighting locations are published.',
 'model_3d':None,
 'details':{
   'identify':{'es':'Cánido de orejas triangulares relativamente cortas, pelaje pardo grisáceo y marcas oscuras en la parte anterior de las patas. Rasgos orientativos; esta ficha no identifica ejemplares a distancia.','en':'A canid with relatively short triangular ears, grey-brown fur and dark markings on the front of the legs. These are indicative traits, not a remote identification diagnosis.'},
   'ecology':{'es':'En libertad es un carnívoro social que consume ungulados, otras presas y carroña. En esta ficha la presencia local corresponde a animales atendidos por el centro.','en':'In the wild it is a social carnivore feeding on ungulates, other prey and carrion. Local presence in this entry refers to animals cared for by the centre.'},
   'look':{'es':'Sigue las indicaciones del guía y los cuidadores, mantén silencio y utiliza prismáticos. La actividad se desarrolla en un recinto gestionado.','en':'Follow the guide and keepers, stay quiet and use binoculars. This activity takes place within a managed facility.'},
   'source':{'url':'https://secem.es/mamiferos/atlas/canis-lupus','publisher':'SECEM','checked_at':DATE},
   'identification_scope':'orientative_not_diagnostic',
   'look_is_editorial_guidance':True
 }
}

assert not any(p['id']==PLACE['id'] for p in data['places']),'Centre already exists; review before updating.'
assert not any(r['id']==ROUTE['id'] for r in data['routes']),'Visit already exists; review before updating.'
assert not any(s['scientific_name']=='Canis lupus' for s in data['species']),'Wolf taxon already exists; link it instead.'
assert not (set(SOURCES)&set(data['sources'])),'Source IDs already exist; review before updating.'
data['sources'].update(SOURCES)
data['places'].append(PLACE);data['routes'].append(ROUTE);data['species'].append(WOLF)
all_sources=data['sources'];all_routes={r['id'] for r in data['routes']};all_species={s['id'] for s in data['species']}
assert all(x in all_sources for x in PLACE['sources']+ROUTE['source_ids']+WOLF['sources'])
assert all(x in all_routes for x in PLACE['route_ids']) and all(x in all_species for x in PLACE['species_ids'])
assert PATH.read_bytes()==before,'Catalogue changed during preparation; rerun from current content.'
content=(json.dumps(data,ensure_ascii=False,indent=2)+'\n').encode('utf8')
temporary=PATH.with_suffix('.wolf.tmp');temporary.write_bytes(content)
assert PATH.read_bytes()==before,'Catalogue changed before atomic save; preserve concurrent edits.'
temporary.replace(PATH)
print(json.dumps({'added_place':PLACE['id'],'added_route':ROUTE['id'],'added_species':WOLF['id'],'sources_added':len(SOURCES),'coordinates':PLACE['coordinates'],'coordinate_status':PLACE['coordinate_status'],'duration_minutes':120,'duration_scope':ROUTE['duration_scope'],'distance_km':None,'ascent_m':None,'gpx':None,'counts':{k:len(data[k]) for k in ['places','routes','species']}},ensure_ascii=False))
