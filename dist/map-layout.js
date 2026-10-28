// Context around the official IGN Madrid extent, including the neighbouring sierra.
export const REGIONAL_BOUNDS=[[-4.74,39.78],[-2.90,41.25]];

export function terrainPitch(zoom,enabled=true){
  if(!enabled)return 0;
  return zoom<9?28:zoom<11?36:zoom<13?44:50;
}

export function boundsPitch(bounds,enabled=true){
  if(!enabled)return 0;
  const [[west,south],[east,north]]=bounds;
  const span=Math.max(Math.abs(east-west)*Math.cos((south+north)*Math.PI/360),Math.abs(north-south));
  return span>2?22:span>.7?30:span>.12?38:46;
}

export function mapInsets({width,height,top=140,panel=null,side='left'}){
  const compact=width<=700;
  const inset={top:Math.max(24,top),left:compact?16:24,right:compact?64:88,bottom:compact?88:96};
  if(panel){
    if(compact)inset.bottom=Math.max(inset.bottom,height-panel.top+12);
    else if(side==='right')inset.right=Math.max(inset.right,width-panel.left+16);
    else inset.left=Math.max(inset.left,panel.right+16);
  }
  // Native camera padding must leave a usable rectangle, including short screens.
  for(const [a,b,size,min]of [['left','right',width,150],['top','bottom',height,140]]){
    const budget=Math.max(0,size-min),sum=inset[a]+inset[b];
    if(sum>budget&&sum){inset[a]*=budget/sum;inset[b]*=budget/sum;}
  }
  return inset;
}
