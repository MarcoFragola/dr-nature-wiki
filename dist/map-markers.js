// Screen-space level of detail: only nearby, visible features receive DOM nodes.
// A small pool is reconciled after camera movement instead of rebuilding every pin.
const paths={
  mountain:'<path d="m3 20 6-14 4 8 3-6 5 12Z"/><path d="m7 11 2 3 2-3"/>',
  trees:'<path d="m8 3-5 8h3l-4 6h5v4h2v-4h5l-4-6h3Z"/><path d="m15 4 5 8h-3l4 6h-6"/>',
  leaf:'<path d="M20 3c-9-1-17 3-15 10 2 7 14 6 15-10Z"/><path d="M3 21 15 9"/>',
  bird:'<path d="m16 7 2-3 3 4-3 2c0 6-5 10-12 9l3-5-6-4 5-1 5 3 1-4Z"/>',
  footprints:'<ellipse cx="7" cy="7" rx="3" ry="5" transform="rotate(-20 7 7)"/><ellipse cx="17" cy="15" rx="3" ry="5" transform="rotate(20 17 15)"/><path d="m5 15 2 3m9-15 2 2"/>',
  waves:'<path d="M2 6q2-3 5 0t5 0 5 0 5 0M2 12q2-3 5 0t5 0 5 0 5 0M2 18q2-3 5 0t5 0 5 0 5 0"/>'
};
const svg=name=>`<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${paths[name]||paths.mountain}</svg>`;
const distance=(a,b)=>{const r=Math.PI/180,dlat=(b[1]-a[1])*r,dlng=(b[0]-a[0])*r;const t=Math.sin(dlat/2)**2+Math.cos(a[1]*r)*Math.cos(b[1]*r)*Math.sin(dlng/2)**2;return 12742*Math.atan2(Math.sqrt(t),Math.sqrt(1-t));};
const intersects=(a,b)=>a.x<b.x+b.w&&a.x+a.w>b.x&&a.y<b.y+b.h&&a.y+a.h>b.y;

export class MapMarkers{
  constructor(map,{Marker,onSelect,onGroup,onCount,padding}){
    Object.assign(this,{map,Marker,onSelect,onGroup,onCount,padding});
    this.pool=new Map();this.records=[];this.cities=[];this.lang='es';this.enabled=true;
    this.host=document.querySelector('#map');
    this.legend=document.createElement('div');this.legend.className='map-key';
    document.querySelector('#main').append(this.legend);
    this.schedule=()=>{clearTimeout(this.timer);this.timer=setTimeout(()=>this.render(),100);};
    map.on('movestart',()=>this.host.classList.add('markers-moving'));
    map.on('moveend',()=>{this.host.classList.remove('markers-moving');this.schedule();});
    map.on('zoomend',this.schedule);map.on('resize',this.schedule);
    // The compatibility renderer emits move rather than moveend.
    if(map.isSoftware)map.on('move',this.schedule);
    map.on('sourcedata',e=>{if(e.sourceId==='terrain')this.schedule();});
    fetch('data/cities.geojson').then(r=>r.ok?r.json():null).then(data=>{
      this.cities=data?.features||[];this.schedule();
    }).catch(()=>{});
  }
  set({records,selected,lang,enabled,citiesEnabled=true}){
    Object.assign(this,{records,selected,lang,enabled,citiesEnabled});this.render();
  }
  render(){
    const map=this.map,canvas=map.getCanvas(),w=canvas.clientWidth,h=canvas.clientHeight;
    const es=this.lang==='es';this.legend.hidden=!this.enabled&&!this.citiesEnabled;
    if(!w||!h)return;
    const center=map.getCenter(),origin=[center.lng,center.lat],zoom=map.getZoom();
    // Exclude remote terrain behind the horizon, even if projection returns a screen point.
    const radius=Math.min(1000,155*2**(9-zoom));
    const padding=this.padding(),screen={x:Math.min(padding.left,w*.6),y:Math.max(135,padding.top),w:0,h:0};
    screen.w=Math.max(60,w-screen.x-padding.right);screen.h=Math.max(60,h-screen.y-padding.bottom);
    const project=coordinates=>{
      if(distance(origin,coordinates)>radius)return null;
      const p=map.project(coordinates);
      if(p.depth!==undefined&&p.depth<=0)return null;
      if(!Number.isFinite(p.x)||!Number.isFinite(p.y)||p.x<screen.x+20||p.x>screen.x+screen.w-20||p.y<screen.y+20||p.y>screen.y+screen.h-20)return null;
      return p;
    };
    let points=this.enabled?this.records.map(r=>({...r,point:project(r.coordinates)})).filter(r=>r.point):[];
    const selected=points.find(r=>r.key===this.selected);points=points.filter(r=>r!==selected);
    // A cluster splits continuously with scale; at close range only overlapping starts group.
    const gap=zoom<9?106:zoom<11?86:zoom<13?68:48;
    const groups=[];
    for(const r of points){
      let g=groups.find(g=>Math.hypot(g.x-r.point.x,g.y-r.point.y)<gap);
      if(!g){g={x:r.point.x,y:r.point.y,members:[]};groups.push(g);}
      g.members.push(r);g.x=g.members.reduce((s,p)=>s+p.point.x,0)/g.members.length;g.y=g.members.reduce((s,p)=>s+p.point.y,0)/g.members.length;
    }
    const desired=[];
    if(selected)desired.push({...selected,kind:'poi',selected:true});
    for(const g of groups){
      const anchor=g.members.reduce((a,b)=>Math.hypot(a.point.x-g.x,a.point.y-g.y)<Math.hypot(b.point.x-g.x,b.point.y-g.y)?a:b);
      desired.push(g.members.length===1?{...anchor,kind:'poi'}:{key:'cluster:'+g.members.map(r=>r.key).sort().join('|'),kind:'cluster',coordinates:anchor.coordinates,point:anchor.point,members:g.members,count:g.members.length});
    }
    const occupied=desired.map(r=>({x:r.point.x-26,y:r.point.y-26,w:52,h:52}));
    if(this.citiesEnabled)for(const f of this.cities){
      if(zoom<f.properties.minZoom)continue;
      const point=project(f.geometry.coordinates);if(!point)continue;
      const width=Math.min(180,f.properties.name.length*7+24),box={x:point.x-8,y:point.y-16,w:width,h:32};
      if(occupied.some(b=>intersects(box,b)))continue;
      occupied.push(box);desired.push({key:'city:'+f.properties.id,kind:'city',coordinates:f.geometry.coordinates,point,name:f.properties.name,capital:f.properties.rank==='capital'});
    }
    // Labels are collision checked once, and can always be read with focus or hover.
    for(const r of desired.filter(r=>r.kind==='poi')){
      const width=Math.min(225,r.label.length*6+20),box={x:r.point.x+25,y:r.point.y-15,w:width,h:30};
      r.labelVisible=(r.selected||zoom>=11.2)&&box.x+width<w-padding.right&&!occupied.some(b=>intersects(box,b));
      if(r.labelVisible)occupied.push(box);
    }
    this.onCount?.({symbols:desired.filter(r=>r.kind!=='city').length,records:desired.filter(r=>r.kind!=='city').reduce((sum,r)=>sum+(r.count||1),0)});
    const active=new Set();
    for(const record of desired){
      active.add(record.key);let node=this.pool.get(record.key);
      if(!node){
        const button=document.createElement('button');button.type='button';
        button.className='map-feature';
        const marker=new this.Marker({element:button,anchor:'center'}).setLngLat(record.coordinates).addTo(map);
        node={button,marker};this.pool.set(record.key,node);
        button.addEventListener('click',e=>{e.stopPropagation();this.activate(node.record);});
      }
      node.record=record;node.marker.setLngLat(record.coordinates);
      const signature=[record.kind,record.label,record.name,record.count,record.icon,this.lang].join('|');
      if(node.signature!==signature){
        node.signature=signature;node.button.replaceChildren();
        const symbol=document.createElement('span');symbol.className='map-feature-symbol';
        if(record.kind==='city')symbol.innerHTML='<svg viewBox="0 0 12 12" aria-hidden="true"><rect x="3" y="3" width="6" height="6" fill="currentColor"/></svg>';
        else if(record.kind==='cluster')symbol.innerHTML=`${svg('mountain')}<b>+${record.count}</b>`;
        else symbol.innerHTML=svg(record.icon);
        node.button.append(symbol);
        const label=document.createElement('span');label.className='map-feature-label';label.textContent=record.name||record.label||'';node.button.append(label);
        node.button.setAttribute('aria-label',record.kind==='cluster'?(es?`Acercar a ${record.count} elementos del mapa`:`Zoom to ${record.count} map items`):record.kind==='city'?(es?'Población: ':'Settlement: ')+record.name:record.label);
      }
      node.button.className=`maplibregl-marker maplibregl-marker-anchor-center map-feature map-${record.kind} ${record.color||''} ${record.capital?'is-capital':''} ${record.selected?'is-selected':''} ${record.labelVisible?'show-label':''}`;
    }
    for(const[key,node]of this.pool)if(!active.has(key)){node.marker.remove();this.pool.delete(key);}
    this.legend.innerHTML=`<span class="key-city">▪</span> ${es?'Población':'Settlement'} <span class="key-nature">○</span> ${es?'Naturaleza':'Nature'} <span class="key-cluster">+N</span> ${es?'Acerca para desplegar':'Zoom to expand'}`;
  }
  activate(r){
    if(r.kind==='poi')return this.onSelect(r.type,r.id);
    if(r.kind==='city')return this.map.flyTo({center:r.coordinates,zoom:Math.max(11.5,this.map.getZoom()+.8),padding:this.padding(),duration:matchMedia('(prefers-reduced-motion: reduce)').matches?0:900});
    if(this.map.getZoom()>=15)return this.onGroup(r.members);
    const box=r.members.reduce((b,p)=>[Math.min(b[0],p.coordinates[0]),Math.min(b[1],p.coordinates[1]),Math.max(b[2],p.coordinates[0]),Math.max(b[3],p.coordinates[1])],[180,90,-180,-90]);
    this.map.fitBounds([[box[0],box[1]],[box[2],box[3]]],{padding:this.padding(),maxZoom:Math.min(16,this.map.getZoom()+2),duration:matchMedia('(prefers-reduced-motion: reduce)').matches?0:900});
  }
}
