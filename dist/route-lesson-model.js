// Read the original GPX geometry without rounding, simplifying or inventing return legs.
const radians=n=>n*Math.PI/180;
export function distanceMetres(a,b){
  const dlat=radians(b[1]-a[1]),dlon=radians(b[0]-a[0]);
  const h=Math.sin(dlat/2)**2+Math.cos(radians(a[1]))*Math.cos(radians(b[1]))*Math.sin(dlon/2)**2;
  return 6371008.8*2*Math.atan2(Math.sqrt(h),Math.sqrt(1-h));
}
export function lessonRoute(feature){
  const g=feature.type==='Feature'?feature.geometry:feature;
  const segments=g.type==='LineString'?[g.coordinates]:g.type==='MultiLineString'?g.coordinates:[];
  if(!segments.length||segments.some(s=>s.length<2))throw Error('No valid route segments');
  const points=segments.flat();
  if(points.some(c=>!Number.isFinite(c[0])||!Number.isFinite(c[1])))throw Error('Invalid route coordinates');
  const start=points[0],turn=points.reduce((best,c)=>distanceMetres(start,c)>distanceMetres(start,best)?c:best,start);
  const bounds=[[Math.min(...points.map(c=>c[0])),Math.min(...points.map(c=>c[1]))],[Math.max(...points.map(c=>c[0])),Math.max(...points.map(c=>c[1]))]];
  return {segments,start,turn,bounds,length:segments.reduce((sum,s)=>sum+s.slice(1).reduce((n,c,i)=>n+distanceMetres(s[i],c),0),0)};
}
export function lessonCamera(base,progress,reduced=false){
  const p=reduced?.15:Math.max(0,Math.min(1,progress));
  const anchors=[{zoom:base.zoom-.12,pitch:34,bearing:-16},{zoom:base.zoom+.02,pitch:43,bearing:-6},{zoom:base.zoom-.12,pitch:34,bearing:2}];
  const index=Math.min(1,Math.floor(p*2)),t=p*2-index,u=t*t*(3-2*t),a=anchors[index],b=anchors[index+1];
  return {center:base.center,zoom:a.zoom+(b.zoom-a.zoom)*u,pitch:a.pitch+(b.pitch-a.pitch)*u,bearing:a.bearing+(b.bearing-a.bearing)*u};
}
