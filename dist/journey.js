import {TerrainIntro} from './terrain-intro.js';
import {installBoundaries} from './boundaries.js';
import {mountCinematicCover} from './cinematic-cover.js';

const text={
  es:{atlasLabel:'ATLAS DE NATURALEZA',introLine:'Relieve. Caminos. Vida natural.',scrollEnter:'Desliza para entrar',independent:'Un atlas independiente',aboutKicker:'EL TERRITORIO, CON CONTEXTO',aboutTitle:'Un atlas de naturaleza.',aboutCopy:'Elige un lugar y entiende lo que lo rodea: sus caminos, el relieve, el agua y la vida que alberga.',aboutMore:'Madrid y sus comunidades vecinas, con escapadas invitadas como el Valle del Jerte. Lugares y visitas documentados, con acceso directo al mapa y a sus fuentes.',naturalPlaces:'espacios naturales',documentedTrails:'rutas documentadas',species:'fichas de vida',seeTerritory:'Ver el territorio',methodKicker:'CÓMO RECORRER EL ATLAS',methodTitle:'Del mapa<br>al sendero.',step1Title:'Mira el terreno',step1Copy:'Gira, inclina y acércate al relieve real. Los límites se dibujan con datos oficiales del IGN.',step2Title:'Lee la ruta',step2Copy:'Consulta distancia, desnivel y dificultad publicada. Las rutas con GPX conservan el trazado original.',step3Title:'Prepara tu salida',step3Copy:'Guarda lugares en tu cuaderno. Revisa accesos, restricciones y fuentes antes de ir.',openThisTrail:'Abrir esta ruta en el mapa',lifeKicker:'MÁS ALLÁ DEL PAISAJE',lifeTitle:'Fauna, flora<br>y ecosistemas.',lifeCopy:'Rasgos, hábitats y el papel de cada especie. Un inventario documentado, sin promesas de avistamiento.',wildlife:'FAUNA',eagle:'Águila imperial ibérica',plants:'FLORA',oak:'Cerezos en flor',meetSpecies:'Abrir el atlas natural',endKicker:'TU SIGUIENTE LUGAR',endTitle:'Elige por dónde empezar.',enterMap:'Entrar en el mapa',endCopy:'Puedes explorar sin cuenta. Tu cuaderno se guarda en este navegador.',sourcesCredits:'Fuentes y créditos',backTop:'Volver arriba ↑',mapLoading:'Cargando relieve real…',mapPhoto:'Vista fotográfica · abre el mapa para explorar'},
  en:{atlasLabel:'AN ATLAS OF NATURE',introLine:'Terrain. Trails. Natural life.',scrollEnter:'Scroll to enter',independent:'An independent atlas',aboutKicker:'THE LANDSCAPE, IN CONTEXT',aboutTitle:'An atlas of nature.',aboutCopy:'A mountain range, a forest, a lake. Dr Nature connects the landscape with its trails, water and the species that belong to it.',aboutMore:'Madrid and its two neighbouring regions, through a documented selection. Every entry retains its sources.',naturalPlaces:'natural places',documentedTrails:'documented trails',species:'life entries',seeTerritory:'Explore the territory',methodKicker:'HOW TO EXPLORE THE ATLAS',methodTitle:'From the map<br>to the trail.',step1Title:'Look at the terrain',step1Copy:'Rotate, tilt and get closer to real terrain. Boundaries use official IGN vector data.',step2Title:'Read the trail',step2Copy:'Check published distance, ascent and difficulty. Trails with a GPX retain the original geometry.',step3Title:'Prepare your visit',step3Copy:'Save places in your notebook. Review access, restrictions and sources before setting out.',openThisTrail:'Open this trail on the map',lifeKicker:'BEYOND THE LANDSCAPE',lifeTitle:'Wildlife, plants<br>and ecosystems.',lifeCopy:'Traits, habitats and the role of each species. A documented inventory, with no promise of sightings.',wildlife:'WILDLIFE',eagle:'Spanish imperial eagle',plants:'PLANTS',oak:'Cherry blossom',meetSpecies:'Open the nature atlas',endKicker:'YOUR NEXT PLACE',endTitle:'Choose where to begin.',enterMap:'Enter the map',endCopy:'Explore without an account. Your notebook stays in this browser.',sourcesCredits:'Sources and credits',backTop:'Back to top ↑',mapLoading:'Loading real terrain…',mapPhoto:'Photographic view · open the map to explore'}
};
const clamp=(v,a=0,b=1)=>Math.max(a,Math.min(b,v));

export function mountJourney({catalogue,lang='es'}){
  const introSection=document.querySelector('.story-intro');
  const atlas=document.querySelector('#atlas');
  const method=document.querySelector('.story-method');
  const steps=[...document.querySelectorAll('[data-step]')];
  const canvas=document.querySelector('#intro-terrain');
  const terrain=new TerrainIntro(canvas);
  const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
  let currentLang=lang,mapOpen=false,frame=0,methodMap=null,methodMapReady=false,methodVisible=false;
  let methodProgress=0,routeCoordinates=[],mapRequested=false,cinematic=null,coverRequested=false,coverVisible=false;

  document.body.classList.add('js-story');
  const reveal=new IntersectionObserver(entries=>entries.forEach(e=>{
    if(e.isIntersecting){e.target.classList.add('is-visible');reveal.unobserve(e.target);}
  }),{threshold:.12,rootMargin:'0px 0px -4% 0px'});
  document.querySelectorAll('[data-reveal]').forEach(el=>reveal.observe(el));

  for(const step of steps){
    const go=()=>{const i=Number(step.dataset.step),top=method.getBoundingClientRect().top+scrollY;window.scrollTo({top:top+(method.offsetHeight-innerHeight)*(i+.3)/3,behavior:reduced?'instant':'smooth'});};
    step.addEventListener('click',go);step.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();go();}});
  }

  async function initCinematicCover(){
    if(coverRequested)return;coverRequested=true;
    cinematic=await mountCinematicCover(document.querySelector('#cinematic-cover'),{lang:currentLang,visible:coverVisible&&!mapOpen,onStatus:status=>{
      document.querySelector('#main').classList.toggle('cover-ready',status.ready);
      document.querySelector('#main').dataset.coverState=status.status;
      if(status.ready&&!mapOpen)document.querySelector('#map-status').textContent=currentLang==='es'?'MDT IGN · PNOA · realce visual ×4,8':'IGN elevation · PNOA · visual emphasis ×4.8';
    }});
    await cinematic.ready;
  }

  function setLanguage(next){
    currentLang=next==='en'?'en':'es';
    document.querySelectorAll('[data-story-key]').forEach(el=>{
      const value=text[currentLang][el.dataset.storyKey];if(value)el.innerHTML=value;
    });
    const images=document.querySelectorAll('.story-content img');
    const alts=currentLang==='es'?['Lobos en semilibertad en el Centro del Lobo Ibérico. Fotografía de Marco.','Águila imperial ibérica','Cerezos en flor en el Valle del Jerte, fotografía aportada por Marco']:['Wolves in a managed enclosure at the Iberian Wolf Centre. Photograph by Marco.','Spanish imperial eagle','Cherry blossom in Valle del Jerte, photograph supplied by Marco'];
    images.forEach((img,i)=>{if(alts[i])img.alt=alts[i];});
    document.querySelector('#story-real-map').setAttribute('aria-label',currentLang==='es'?'Relieve real y trazado oficial Cotos–Zabala':'Real terrain and official Cotos–Zabala trail');
  }

  function updateMethodCamera(){
    if(!methodMapReady||!methodVisible||mapOpen||!routeCoordinates.length)return;
    const p=reduced?.3:methodProgress;
    const index=clamp(p*.8+.08)*(routeCoordinates.length-1),i=Math.floor(index),t=index-i;
    const a=routeCoordinates[i],b=routeCoordinates[Math.min(i+1,routeCoordinates.length-1)];
    const center=[a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t];
    methodMap.jumpTo({center,zoom:13.05+p*.35,pitch:45+p*7,bearing:-25+p*33});
  }

  async function initMethodMap(){
    if(mapRequested)return;mapRequested=true;
    const host=document.querySelector('#story-real-map'),credit=document.querySelector('.method-map-credit');
    credit.textContent=text[currentLang].mapLoading;
    try{
      const response=await fetch('data/tracks/penalara-zabala.geojson');if(!response.ok)throw Error('Track unavailable');
      const feature=await response.json();
      const getCoords=f=>f.type==='Feature'?getCoords(f.geometry):f.type==='FeatureCollection'?f.features.flatMap(getCoords):f.type==='LineString'?f.coordinates:f.type==='MultiLineString'?f.coordinates.flat():[];
      routeCoordinates=getCoords(feature);
      const tiles='https://www.ign.es/wmts/pnoa-ma?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=OI.OrthoimageCoverage&STYLE=default&FORMAT=image/jpeg&TILEMATRIXSET=GoogleMapsCompatible&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}';
      methodMap=new maplibregl.Map({container:host,interactive:false,terrainSkirtLength:'none',attributionControl:false,center:routeCoordinates[0],zoom:12.5,pitch:59,bearing:-22,maxPitch:70,canvasContextAttributes:{antialias:true},style:{version:8,sources:{aerial:{type:'raster',tiles:[tiles],tileSize:256,maxzoom:19},elevation:{type:'raster-dem',tiles:['data/terrain/tiles/{z}/{x}/{y}.png'],tileSize:256,encoding:'terrarium',minzoom:6,maxzoom:10,bounds:[-4.9,39.65,-2.75,41.45]}},layers:[{id:'background',type:'background',paint:{'background-color':'#132a23'}},{id:'imagery',type:'raster',source:'aerial',paint:{'raster-saturation':-.35,'raster-brightness-max':.75,'raster-contrast':.12}}],terrain:{source:'elevation',exaggeration:1.5}}});
      methodMap.on('load',()=>{
        methodMapReady=true;
        methodMap.addSource('story-official-trail',{type:'geojson',data:feature});
        methodMap.addLayer({id:'story-trail-shadow',type:'line',source:'story-official-trail',paint:{'line-color':'#06150e','line-width':7,'line-opacity':.8}});
        methodMap.addLayer({id:'story-trail',type:'line',source:'story-official-trail',layout:{'line-cap':'round','line-join':'round'},paint:{'line-color':'#e6efcb','line-width':3,'line-opacity':1}});
        void installBoundaries(methodMap);updateMethodCamera();
      });
      methodMap.on('sourcedata',e=>{if(e.sourceId==='aerial'&&e.sourceDataType==='content')credit.textContent='PNOA / IGN · MDT IGN ~180 m · ×1,5 · GPX PNSG';});
      new ResizeObserver(()=>methodMap?.resize()).observe(host);
    }catch(error){
      credit.textContent=text[currentLang].mapPhoto;
      if(!methodMapReady){methodMap?.remove();methodMap=null;host.replaceChildren();}
      console.warn('Story terrain:',error.message);
    }
  }

  const visibility=new IntersectionObserver(entries=>entries.forEach(e=>{
    if(e.target===introSection)terrain.setVisible(e.isIntersecting&&!mapOpen);
    if(e.target===atlas){coverVisible=e.isIntersecting;if(coverVisible)void initCinematicCover();cinematic?.setVisible(coverVisible&&!mapOpen);}
    if(e.target===method){methodVisible=e.isIntersecting;if(methodVisible){void initMethodMap();updateMethodCamera();}}
  }),{rootMargin:'180px 0px'});
  visibility.observe(introSection);visibility.observe(atlas);visibility.observe(method);

  function draw(){
    frame=0;if(mapOpen)return;
    const vh=innerHeight,introRect=introSection.getBoundingClientRect();
    const introProgress=reduced?0:clamp(-introRect.top/Math.max(1,introSection.offsetHeight-vh));
    introSection.style.setProperty('--intro-progress',introProgress);
    terrain.setProgress(introProgress);
    const a=atlas.getBoundingClientRect(),hud=reduced?1:clamp((vh-a.top)/(vh*.75));
    atlas.style.setProperty('--hud-opacity',hud);
    const m=method.getBoundingClientRect();
    methodProgress=clamp(-m.top/Math.max(1,method.offsetHeight-vh));
    method.style.setProperty('--method-progress',reduced?1:methodProgress);
    const active=Math.min(2,Math.floor(methodProgress*3));steps.forEach((s,i)=>s.classList.toggle('active',i===active||reduced));
    if(!reduced)document.querySelectorAll('[data-parallax]').forEach(el=>{
      const r=el.getBoundingClientRect();
      if(r.top<vh&&r.bottom>0)el.style.setProperty('--photo-offset',`${(clamp((vh-r.top)/(vh+r.height))-.5)*60}px`);
    });
    updateMethodCamera();
  }
  function schedule(){if(!frame)frame=requestAnimationFrame(draw);}
  window.addEventListener('scroll',schedule,{passive:true});window.addEventListener('resize',schedule);
  const numbers=document.querySelectorAll('.story-numbers strong');
  [catalogue.places.length,catalogue.routes.length,catalogue.species.length].forEach((value,i)=>numbers[i].textContent=value);
  setLanguage(lang);
  if(!location.hash){history.scrollRestoration='manual';window.scrollTo({top:0,behavior:'instant'});}
  schedule();
  return {
    setLanguage,
    openMap(){mapOpen=true;document.body.classList.add('map-active');terrain.setVisible(false);cinematic?.setVisible(false);methodMap?.stop();},
    closeMap(){mapOpen=false;document.body.classList.remove('map-active');atlas.scrollIntoView({behavior:'instant',block:'start'});cinematic?.setVisible(true);cinematic?.resize();schedule();},
    destroy(){terrain.destroy();cinematic?.destroy();methodMap?.remove();visibility.disconnect();reveal.disconnect();window.removeEventListener('scroll',schedule);window.removeEventListener('resize',schedule);if(frame)cancelAnimationFrame(frame);}
  };
}
