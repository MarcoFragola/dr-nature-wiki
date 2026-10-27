import {normalize,matchesText} from './search.js';
export const geographicLabels={watercourse:['Tramo de curso de agua','Watercourse segment'],reservoir:['Embalse','Reservoir'],lake:['Agua estancada','Standing water'],wetland:['Humedal','Wetland'],'protected-area':['Espacio protegido','Protected area']};
const regionBits={'Madrid':1,'Castilla y León':2,'Castilla-La Mancha':4};
const intersects=(a,b)=>a[0]<=b[2]&&a[2]>=b[0]&&a[1]<=b[3]&&a[3]>=b[1];
const empty=()=>({type:'FeatureCollection',features:[]});

// Static hosts count the expanded deployment files, so geometry is delivered
// as losslessly compressed assets and decoded only for the visible chunks.
// Sniff the bytes because some hosts transparently decode Content-Encoding.
export async function readGeographicResponse(response,file=''){
  if(!response.ok)throw Error('Geographic geometry unavailable');
  if(!file.endsWith('.gz'))return response.json();
  const body=await response.blob(),magic=new Uint8Array(await body.slice(0,2).arrayBuffer());
  if(magic[0]!==0x1f||magic[1]!==0x8b)return JSON.parse(await body.text());
  if(typeof DecompressionStream!=='function')throw Error('This browser cannot decompress geographic data');
  return new Response(body.stream().pipeThrough(new DecompressionStream('gzip'))).json();
}

export class GeographicIndex{
  constructor(){this.cache=new Map();this.byId=new Map();this.queries=new Map();this.pending=new Map();}
  async load(){
    if(!this.loading)this.loading=fetch('data/geography/index.json').then(r=>{if(!r.ok)throw Error('Geographic catalogue unavailable');return r.json();}).then(data=>{this.data=data;this.texts=data.search.map(r=>normalize(r[1]));data.search.forEach(row=>this.byId.set(row[0],row));return data;}).catch(error=>{this.loading=null;throw error;});
    return this.loading;
  }
  query({query='',type='all',bounds=null,region=''}={}){
    if(!this.data)return [];const q=normalize(query),key=JSON.stringify([q,type,bounds,region]);if(this.queries.has(key))return this.queries.get(key);
    let rows=this.data.search.filter((r,i)=>(type==='all'||r[2]===type)&&(!region||Boolean((r[6]||0)&(regionBits[region]||0)))&&(!bounds||intersects(r[3],bounds))&&(!q||this.texts[i].includes(q)));
    if(q&&!rows.length&&q.length>=4)rows=this.data.search.filter((r,i)=>(type==='all'||r[2]===type)&&(!region||Boolean((r[6]||0)&(regionBits[region]||0)))&&(!bounds||intersects(r[3],bounds))&&(this.texts[i].includes(q.slice(0,2))||this.texts[i].includes(q.slice(1,3))||this.texts[i].includes(q.slice(-3)))&&matchesText(r[1],q));
    this.queries.set(key,rows);while(this.queries.size>6)this.queries.delete(this.queries.keys().next().value);return rows;
  }
  async chunk(file){
    if(this.cache.has(file)){const value=this.cache.get(file);this.cache.delete(file);this.cache.set(file,value);return value;}
    if(this.pending.has(file))return this.pending.get(file);const request=fetch(file).then(r=>readGeographicResponse(r,file)).then(data=>{this.cache.set(file,data);while(this.cache.size>24)this.cache.delete(this.cache.keys().next().value);return data;}).finally(()=>this.pending.delete(file));this.pending.set(file,request);return request;
  }
  async feature(id){await this.load();const row=this.byId.get(id);if(!row)return null;const chunk=this.data.chunks[row[4]];return (await this.chunk(chunk.file)).features.find(f=>String(f.id||f.properties.id)===id)||null;}
}

export class GeographicLayers{
  constructor(map,{index,onSelect,onReady,onStatus,isDrawing,padding}){
    Object.assign(this,{map,index,onSelect,onReady,onStatus,isDrawing,padding});this.water=true;this.protected=true;this.token=0;this.query='';this.type='all';this.region='';this.selected=null;
    this.schedule=()=>{clearTimeout(this.timer);this.timer=setTimeout(()=>void this.update(),160);};
  }
  async init(){
    const map=this.map;
    if(map.isSoftware)return false;
    map.addSource('natural-features',{type:'geojson',data:empty(),maxzoom:15,tolerance:.35,attribution:'<a href="https://www.ign.es/" target="_blank">Hidrografía IGN</a> · <a href="https://www.miteco.gob.es/" target="_blank">ENP MITECO</a>'});
    map.addLayer({id:'natural-water-area',type:'fill',source:'natural-features',filter:['all',['==',['geometry-type'],'Polygon'],['!=',['get','type'],'protected-area']],paint:{'fill-color':'#7cb5be','fill-opacity':.23}});
    map.addLayer({id:'natural-protected-area',type:'fill',source:'natural-features',filter:['==',['get','type'],'protected-area'],paint:{'fill-color':'#bdd8a5','fill-opacity':.055}});
    map.addLayer({id:'natural-area-border',type:'line',source:'natural-features',filter:['==',['geometry-type'],'Polygon'],paint:{'line-color':['case',['==',['get','type'],'protected-area'],'#bfd3a4','#a8d6db'],'line-width':['interpolate',['linear'],['zoom'],7,.7,13,1.5],'line-opacity':.65}});
    map.addLayer({id:'natural-water-line',type:'line',source:'natural-features',filter:['==',['geometry-type'],'LineString'],layout:{'line-join':'round','line-cap':'round'},paint:{'line-color':'#a9d5da','line-width':['interpolate',['linear'],['zoom'],8,.7,12,1.4,16,2.5],'line-opacity':.75}});
    map.addSource('selected-natural',{type:'geojson',data:empty()});
    map.addLayer({id:'selected-natural-fill',type:'fill',source:'selected-natural',filter:['==',['geometry-type'],'Polygon'],paint:{'fill-color':'#e1e8c5','fill-opacity':.18}});
    map.addLayer({id:'selected-natural-line',type:'line',source:'selected-natural',paint:{'line-color':'#edf2d4','line-width':3,'line-opacity':1}});
    map.on('moveend',this.schedule);
    map.on('click',e=>{
      if(this.isDrawing()||e.originalEvent?.defaultPrevented)return;
      const features=map.queryRenderedFeatures([[e.point.x-5,e.point.y-5],[e.point.x+5,e.point.y+5]],{layers:['natural-water-line','natural-area-border','natural-water-area','natural-protected-area']});
      const feature=features.find(f=>f.properties?.id);if(feature)this.onSelect(feature.properties.id);
    });
    try{await this.index.load();this.onReady?.(this.index.data);await this.update();return true;}
    catch(error){console.warn('Geographic layers:',error.message);this.onStatus?.({error:true,count:0});return false;}
  }
  viewBounds(){
    const map=this.map,canvas=map.getCanvas(),p=this.padding(),points=[[p.left,p.top],[canvas.clientWidth-p.right,p.top],[p.left,canvas.clientHeight-p.bottom],[canvas.clientWidth-p.right,canvas.clientHeight-p.bottom]].map(point=>map.unproject(point));
    return [Math.min(...points.map(p=>p.lng)),Math.min(...points.map(p=>p.lat)),Math.max(...points.map(p=>p.lng)),Math.max(...points.map(p=>p.lat))];
  }
  enabled(type){return type==='protected-area'?this.protected:this.water;}
  async update(){
    if(!this.index.data)return;const token=++this.token,map=this.map,zoom=map.getZoom(),bounds=this.viewBounds(),center=map.getCenter();
    const detailed=zoom>=10.5;
    const available=(detailed?this.index.data.chunks:this.index.data.overview_chunks).filter(c=>intersects(c.bbox,bounds));
    available.sort((a,b)=>Math.hypot((a.bbox[0]+a.bbox[2])/2-center.lng,(a.bbox[1]+a.bbox[3])/2-center.lat)-Math.hypot((b.bbox[0]+b.bbox[2])/2-center.lng,(b.bbox[1]+b.bbox[3])/2-center.lat));
    // Bound live geometry work, never the catalogue: every feature remains searchable.
    const chunks=available.slice(0,detailed?12:8),loaded=[];
    for(let i=0;i<chunks.length;i+=3){
      const results=await Promise.allSettled(chunks.slice(i,i+3).map(c=>this.index.chunk(c.file)));
      if(token!==this.token)return;
      for(const result of results)if(result.status==='fulfilled')loaded.push(...result.value.features);
    }
    const unique=new Map();
    for(const feature of loaded){const p=feature.properties;if((this.region&&!((p.regionMask||0)&(regionBits[this.region]||0)))||(this.type!=='all'&&p.type!==this.type)||!this.enabled(p.type)||p.minZoom>zoom||(!intersects(p.bbox,bounds)))continue;if(this.query&&!matchesText(p.name,this.query))continue;unique.set(String(feature.id||p.id),feature);}
    if(this.selected&&this.enabled(this.selected.properties.type))unique.set(String(this.selected.id||this.selected.properties.id),this.selected);
    map.getSource('natural-features')?.setData({type:'FeatureCollection',features:[...unique.values()]});
    this.onStatus?.({count:unique.size,detailed,total:this.index.data.total_features,partial:available.length>chunks.length});
  }
  setVisible({water=this.water,protectedAreas=this.protected}={}){this.water=water;this.protected=protectedAreas;void this.update();}
  configure({query=this.query,type=this.type,region=this.region}={}){if(query===this.query&&type===this.type&&region===this.region)return;Object.assign(this,{query,type,region});this.schedule();}
  setType(type){this.type=type||'all';void this.update();}
  setQuery(query){this.query=query||'';void this.update();}
  select(feature){this.selected=feature;this.map.getSource('selected-natural')?.setData(feature||empty());this.schedule();}
  clearSelection(){this.selected=null;this.map.getSource('selected-natural')?.setData(empty());}
}
