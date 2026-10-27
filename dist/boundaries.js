/* IGN/CNIG official administrative units. Vertices are retained without
 * simplification; polygon rings become ground-clamped cartographic lines. */
let dataPromise;
export function loadBoundaries(){
  if(!dataPromise)dataPromise=Promise.all(['comunidades','provincias'].map(name=>fetch(`data/boundaries/${name}.geojson`).then(r=>{
    if(!r.ok)throw new Error('Official boundaries unavailable');return r.json();
  }))).then(collections=>({type:'FeatureCollection',features:collections.flatMap((fc,index)=>fc.features.filter(f=>index===0||f.properties.nationalCode!=='34132800000').flatMap(f=>{
    const polygons=f.geometry.type==='MultiPolygon'?f.geometry.coordinates:[f.geometry.coordinates];
    return polygons.map(rings=>({type:'Feature',properties:{...f.properties,boundary_level:index===0?'autonomous':'province'},geometry:{type:'MultiLineString',coordinates:rings}}));
  }))})).catch(error=>{dataPromise=null;throw error;});
  return dataPromise;
}
export async function installBoundaries(map){
  try{
    if(map.getSource('official-boundaries'))return true;
    const data=await loadBoundaries();
    if(map.getSource('official-boundaries'))return true;
    map.addSource('official-boundaries',{type:'geojson',data,tolerance:0,attribution:'Límites administrativos: IGN · BDLJE · CC BY 4.0 ign.es'});
    map.addLayer({id:'boundary-shadow',type:'line',source:'official-boundaries',paint:{'line-color':'#071314','line-width':3.1,'line-opacity':.55}});
    map.addLayer({id:'boundary-line',type:'line',source:'official-boundaries',paint:{'line-color':'#e9eee4','line-width':1.2,'line-opacity':.88}});
    return true;
  }catch(error){console.warn(error.message);return false;}
}
export async function setBoundariesVisible(map,visible){
  if(!map.getSource('official-boundaries'))await installBoundaries(map);
  const source=map.getSource('official-boundaries');
  if(source)source.setData(visible?await loadBoundaries():{type:'FeatureCollection',features:[]});
}
