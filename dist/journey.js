import {TerrainIntro} from './terrain-intro.js';
import {mountRouteLesson} from './route-lesson.js';
import {mountCinematicCover} from './cinematic-cover.js';

const text={
  es:{atlasLabel:'ATLAS DE NATURALEZA',introLine:'Relieve. Caminos. Vida natural.',scrollEnter:'Desliza para entrar',independent:'Un atlas independiente',aboutKicker:'EL TERRITORIO, CON CONTEXTO',aboutTitle:'Un atlas de naturaleza.',aboutCopy:'Elige un lugar y entiende lo que lo rodea: sus caminos, el relieve, el agua y la vida que alberga.',aboutMore:'Madrid y sus comunidades vecinas, con escapadas invitadas como el Valle del Jerte. Lugares y visitas documentados, con acceso directo al mapa y a sus fuentes.',naturalPlaces:'espacios naturales',documentedTrails:'rutas documentadas',species:'fichas de vida',seeTerritory:'Ver el territorio',methodKicker:'CÓMO RECORRER EL ATLAS',methodTitle:'Del mapa<br>al sendero.',step1Title:'Mira el terreno',step1Copy:'Observa las laderas y el circo de Peñalara. Este relieve conserva las alturas reales del IGN.',step2Title:'Lee la ruta',step2Copy:'Sigue el GPX de Cotos a la zona del Zabala y de vuelta al inicio. Comprueba distancia, tiempo y dificultad.',step3Title:'Prepara tu salida',step3Copy:'Abre la ficha, revisa cupos y meteorología y guarda la ruta en tu cuaderno antes de ir.',methodIntro:'Del relieve a los datos de la ruta, y de ahí a los preparativos de tu visita.',methodRouteName:'Cotos — Zona del Zabala',methodScope:'Ida y vuelta · Sierra de Guadarrama',methodTime:'Tiempo',methodAscent:'Desnivel',methodDistance:'Distancia total',methodSource:'Ficha del Parque Nacional',openThisTrail:'Abrir la ruta y sus detalles',lifeKicker:'MÁS ALLÁ DEL PAISAJE',lifeTitle:'Fauna, flora<br>y ecosistemas.',lifeCopy:'Rasgos, hábitats y el papel de cada especie. Un inventario documentado, sin promesas de avistamiento.',wildlife:'FAUNA',eagle:'Águila imperial ibérica',plants:'FLORA',oak:'Cerezos en flor',meetSpecies:'Abrir el atlas natural',endKicker:'TU SIGUIENTE LUGAR',endTitle:'Elige por dónde empezar.',enterMap:'Entrar en el mapa',endCopy:'Puedes explorar sin cuenta. Tu cuaderno se guarda en este navegador.',sourcesCredits:'Fuentes y créditos',backTop:'Volver arriba ↑',mapLoading:'Cargando relieve real…',mapPhoto:'Vista fotográfica · abre el mapa para explorar'},
  en:{atlasLabel:'AN ATLAS OF NATURE',introLine:'Terrain. Trails. Natural life.',scrollEnter:'Scroll to enter',independent:'An independent atlas',aboutKicker:'THE LANDSCAPE, IN CONTEXT',aboutTitle:'An atlas of nature.',aboutCopy:'A mountain range, a forest, a lake. Dr Nature connects the landscape with its trails, water and the species that belong to it.',aboutMore:'Madrid and its two neighbouring regions, through a documented selection. Every entry retains its sources.',naturalPlaces:'natural places',documentedTrails:'documented trails',species:'life entries',seeTerritory:'Explore the territory',methodKicker:'HOW TO EXPLORE THE ATLAS',methodTitle:'From the map<br>to the trail.',step1Title:'Look at the terrain',step1Copy:'Read Peñalara’s slopes and glacial cirque. This terrain retains the official IGN elevations.',step2Title:'Read the trail',step2Copy:'Follow the GPX from Cotos to the Zabala area and back. Check distance, time and difficulty.',step3Title:'Prepare your visit',step3Copy:'Open the entry, check access quotas and weather, and save the trail in your notebook before setting out.',methodIntro:'From the terrain to trail information, then to the preparations for your visit.',methodRouteName:'Cotos — Zabala area',methodScope:'Out and back · Sierra de Guadarrama',methodTime:'Time',methodAscent:'Ascent',methodDistance:'Total distance',methodSource:'National Park description',openThisTrail:'Open the trail and its details',lifeKicker:'BEYOND THE LANDSCAPE',lifeTitle:'Wildlife, plants<br>and ecosystems.',lifeCopy:'Traits, habitats and the role of each species. A documented inventory, with no promise of sightings.',wildlife:'WILDLIFE',eagle:'Spanish imperial eagle',plants:'PLANTS',oak:'Cherry blossom',meetSpecies:'Open the nature atlas',endKicker:'YOUR NEXT PLACE',endTitle:'Choose where to begin.',enterMap:'Enter the map',endCopy:'Explore without an account. Your notebook stays in this browser.',sourcesCredits:'Sources and credits',backTop:'Back to top ↑',mapLoading:'Loading real terrain…',mapPhoto:'Photographic view · open the map to explore'}
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
  let currentLang=lang,mapOpen=false,frame=0,methodVisible=false;
  let methodProgress=0,cinematic=null,coverRequested=false,coverVisible=false;
  const lesson=mountRouteLesson({host:document.querySelector('#story-real-map'),lang,reduced});

  document.body.classList.add('js-story');
  const reveal=new IntersectionObserver(entries=>entries.forEach(e=>{
    if(e.isIntersecting){e.target.classList.add('is-visible');reveal.unobserve(e.target);}
  }),{threshold:.12,rootMargin:'0px 0px -4% 0px'});
  document.querySelectorAll('[data-reveal]').forEach(el=>reveal.observe(el));

  for(const step of steps){
    step.addEventListener('click',()=>{
      const i=Number(step.dataset.step),progress=(i+.5)/3;
      if(!reduced&&innerWidth>900&&innerHeight>650){
        const top=method.getBoundingClientRect().top+scrollY;
        window.scrollTo({top:top+Math.max(0,method.offsetHeight-innerHeight)*progress,behavior:'smooth'});
      }else{
        methodProgress=progress;
        steps.forEach((button,index)=>{button.classList.toggle('active',index===i);button.setAttribute('aria-pressed',String(index===i));});
        lesson.setProgress(progress,i,true);
      }
    });
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
    document.querySelector('#story-real-map').setAttribute('aria-label',currentLang==='es'?'Relieve local IGN y GPX oficial de Cotos a la zona del Zabala, ida y vuelta':'Local IGN terrain and official out-and-back GPX from Cotos to the Zabala area');
    lesson.setLanguage(currentLang);
    document.querySelector('.method-steps').setAttribute('aria-label',currentLang==='es'?'Pasos para explorar':'Steps for exploring');
    const example=catalogue.routes.find(route=>route.id==='penalara-zabala'),number=new Intl.NumberFormat(currentLang,{maximumFractionDigits:1});
    if(example){
      document.querySelector('[data-method-fact=distance]').innerHTML=`${number.format(example.distance_km)} <span>km</span>`;
      document.querySelector('[data-method-fact=duration]').innerHTML=`${Math.floor(example.duration_minutes/60)} h ${example.duration_minutes%60} <span>min</span>`;
      document.querySelector('[data-method-fact=ascent]').innerHTML=example.ascent_m===null?'—':`+${number.format(example.ascent_m)} <span>m</span>`;
    }
  }

  const visibility=new IntersectionObserver(entries=>entries.forEach(e=>{
    if(e.target===introSection)terrain.setVisible(e.isIntersecting&&!mapOpen);
    if(e.target===atlas){coverVisible=e.isIntersecting;if(coverVisible)void initCinematicCover();cinematic?.setVisible(coverVisible&&!mapOpen);}
    if(e.target===method){methodVisible=e.isIntersecting;lesson.setVisible(methodVisible&&!mapOpen);}
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
    if(!reduced&&innerWidth>900&&innerHeight>650)methodProgress=clamp(-m.top/Math.max(1,method.offsetHeight-vh));
    method.style.setProperty('--method-progress',reduced?1:methodProgress);
    const active=Math.min(2,Math.floor(methodProgress*3));steps.forEach((s,i)=>{s.classList.toggle('active',i===active);s.setAttribute('aria-pressed',String(i===active));});
    if(!reduced)document.querySelectorAll('[data-parallax]').forEach(el=>{
      const r=el.getBoundingClientRect();
      if(r.top<vh&&r.bottom>0)el.style.setProperty('--photo-offset',`${(clamp((vh-r.top)/(vh+r.height))-.5)*60}px`);
    });
    lesson.setProgress(methodProgress,active);
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
    openMap(){mapOpen=true;document.body.classList.add('map-active');terrain.setVisible(false);cinematic?.setVisible(false);lesson.setVisible(false);},
    closeMap(){mapOpen=false;document.body.classList.remove('map-active');atlas.scrollIntoView({behavior:'instant',block:'start'});cinematic?.setVisible(true);cinematic?.resize();lesson.setVisible(methodVisible);schedule();},
    destroy(){terrain.destroy();cinematic?.destroy();lesson.destroy();visibility.disconnect();reveal.disconnect();window.removeEventListener('scroll',schedule);window.removeEventListener('resize',schedule);if(frame)cancelAnimationFrame(frame);}
  };
}
