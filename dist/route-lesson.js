import {lessonRoute,lessonCamera} from './route-lesson-model.js';

const labels={
 es:{loading:'Cargando el terreno de Cotos…',terrain:'01 · Entiende el relieve',route:'02 · Sigue el recorrido',prepare:'03 · Prepara la salida',
  terrainNote:'El valle, las laderas y el circo glaciar, en su posición real.',routeNote:'Cotos → zona del Zabala → Cotos. La línea conserva el GPX del parque.',prepareNote:'Ida y vuelta · consulta cupos y condiciones de nieve antes de salir.',
  fallback:'La vista 3D no está disponible. Puedes abrir la ficha y el trazado en el mapa.',cotos:'Cotos · inicio y regreso',zabala:'Zona del Zabala',
  credit:'Ortofoto: PNOA 2023 / IGN · Relieve: IGN / SCNE · CC BY 4.0 · GPX: PNSG',scale:'Relieve local ~13 m · alturas sin realce'},
 en:{loading:'Loading the terrain around Cotos…',terrain:'01 · Understand the terrain',route:'02 · Follow the trail',prepare:'03 · Prepare your visit',
  terrainNote:'The valley, slopes and glacial cirque in their real positions.',routeNote:'Cotos → Zabala area → Cotos. The line retains the park’s original GPX.',prepareNote:'Out and back · check access quotas and snow conditions before setting out.',
  fallback:'The 3D preview is unavailable. You can open the entry and its track on the map.',cotos:'Cotos · start and return',zabala:'Zabala area',
  credit:'Aerial imagery: PNOA 2023 / IGN · Elevation: IGN / SCNE · CC BY 4.0 · GPX: PNSG',scale:'Local terrain ~13 m · natural elevation scale'}
};

export function mountRouteLesson({host,lang='es',reduced=false}){
  const frame=host.closest('.method-map-frame'),status=document.querySelector('#method-scene-status'),description=document.querySelector('#method-scene-description');
  const credit=document.querySelector('.method-map-credit'),scale=document.querySelector('.method-map-scale');
  let map=null,route=null,base=null,started=false,ready=false,visible=false,language=lang,progress=0,stage=0,lastCamera='',markers=[],resizer=null,destroyed=false;
  const t=()=>labels[language];
  function copy(){
    status.textContent=ready?[t().terrain,t().route,t().prepare][stage]:started?t().loading:t().terrain;
    description.textContent=[t().terrainNote,t().routeNote,t().prepareNote][stage];
    credit.textContent=t().credit;scale.textContent=t().scale;
    markers.forEach((m,i)=>m.getElement().querySelector('span').textContent=i?t().zabala:t().cotos);
    if(frame.dataset.state==='unavailable')status.textContent=t().fallback;
  }
  function camera(smooth=false){
    if(!ready||!visible||!base)return;
    const pose=lessonCamera(base,progress,reduced),key=JSON.stringify(pose);
    if(key===lastCamera)return;lastCamera=key;
    if(smooth&&!reduced)map.easeTo({...pose,duration:650});else map.jumpTo(pose);
  }
  function fit(){
    if(!map||!route)return;
    map.resize();
    const small=host.clientWidth<430;
    base=map.cameraForBounds(route.bounds,{padding:{top:small?78:82,bottom:small?78:82,left:small?42:62,right:small?42:62},bearing:0,maxZoom:14.6});
    base.center=[base.center.lng+(small?.0005:.004),base.center.lat];base.zoom+=.2;lastCamera='';camera();
  }
  function unavailable(){
    ready=false;frame.dataset.state='unavailable';frame.setAttribute('aria-busy','false');
    resizer?.disconnect();map?.remove();map=null;markers=[];host.replaceChildren();copy();
  }
  async function start(){
    if(started||destroyed)return;started=true;frame.dataset.state='loading';frame.setAttribute('aria-busy','true');copy();
    try{
      const [trackResponse,demResponse]=await Promise.all([fetch('data/tracks/penalara-zabala.geojson'),fetch('data/route-lesson/metadata.json')]);
      if(!trackResponse.ok||!demResponse.ok)throw Error('Lesson data unavailable');
      const [feature,dem]=await Promise.all([trackResponse.json(),demResponse.json()]);
      route=lessonRoute(feature);if(destroyed)return;

      map=new maplibregl.Map({container:host,interactive:false,attributionControl:false,renderWorldCopies:false,
        center:[(route.bounds[0][0]+route.bounds[1][0])/2,(route.bounds[0][1]+route.bounds[1][1])/2],zoom:13.6,pitch:34,bearing:-16,
        maxPitch:50,terrainSkirtLength:'auto',canvasContextAttributes:{antialias:true},
        style:{version:8,sources:{aerial:{type:'image',url:'data/route-lesson/'+dem.imagery.path,coordinates:[[dem.imagery.bbox[0],dem.imagery.bbox[3]],[dem.imagery.bbox[2],dem.imagery.bbox[3]],[dem.imagery.bbox[2],dem.imagery.bbox[1]],[dem.imagery.bbox[0],dem.imagery.bbox[1]]]},
          elevation:{type:'raster-dem',tiles:[dem.tiles.template],tileSize:dem.tiles.size,encoding:dem.tiles.encoding,minzoom:dem.tiles.minzoom,maxzoom:dem.tiles.maxzoom,bounds:dem.tiles.bounds}},
          layers:[{id:'lesson-background',type:'background',paint:{'background-color':'#10211c'}},
            {id:'lesson-aerial',type:'raster',source:'aerial',paint:{'raster-saturation':-.12,'raster-brightness-max':.92,'raster-contrast':.04}}],
          terrain:{source:'elevation',exaggeration:1}}});
      map.on('load',()=>{
        if(destroyed)return;
        map.addSource('lesson-track',{type:'geojson',data:feature});
        map.addLayer({id:'lesson-track-halo',type:'line',source:'lesson-track',layout:{'line-cap':'round','line-join':'round'},paint:{'line-color':'#10251d','line-width':7,'line-opacity':.8}});
        map.addLayer({id:'lesson-track-line',type:'line',source:'lesson-track',layout:{'line-cap':'round','line-join':'round'},paint:{'line-color':'#e4f1b4','line-width':3.3}});
        for(const [i,coordinate] of [route.start,route.turn].entries()){
          const el=document.createElement('div');el.className='lesson-pin '+(i?'lesson-turn':'lesson-start');
          const dot=document.createElement('b');dot.textContent=i?'2':'1';const label=document.createElement('span');el.append(dot,label);
          markers.push(new maplibregl.Marker({element:el,anchor:'center'}).setLngLat(coordinate).addTo(map));
        }
        // 'idle' means the visible DEM and imagery have completed, not merely the style JSON.
        map.once('idle',()=>{if(destroyed)return;ready=true;frame.dataset.state='ready';frame.setAttribute('aria-busy','false');fit();copy();});
        resizer=new ResizeObserver(()=>fit());resizer.observe(host);
      });
      map.on('error',e=>{
        if(!ready&&e.sourceId==='elevation')unavailable();
      });
    }catch(error){if(!destroyed){console.warn('Route lesson:',error.message);unavailable();}}
  }
  copy();
  return {
    setVisible(value){visible=value;if(value){void start();camera();}else map?.stop();},
    setProgress(value,nextStage,smooth=false){progress=value;if(stage!==nextStage){stage=nextStage;copy();}camera(smooth);},
    setLanguage(value){language=value==='en'?'en':'es';copy();},
    destroy(){destroyed=true;resizer?.disconnect();map?.remove();}
  };
}
