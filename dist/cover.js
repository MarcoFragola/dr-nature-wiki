/* The cover preserves the reference's full camera framing. Exploration lives in
 * the geographic map, so this artwork has no simulated camera or false pins. */
export class CoverFrame {
  constructor(container){
    this.container=container;
    this.world=container.querySelector('.landscape-world');
    this.observer=new ResizeObserver(()=>this.layout());
    this.observer.observe(container);
    this.layout();
  }
  layout(){
    const r=this.container.getBoundingClientRect();
    if(!r.width||!r.height)return;
    const aspect=1672/941;
    let width=Math.min(r.width,r.height*aspect);
    if(r.width<600)width=r.width*1.65;
    const height=width/aspect;
    this.world.style.width=`${width}px`;
    this.world.style.height=`${height}px`;
    this.world.style.left=r.width<600?'63%':'50%';
    this.world.style.transform=r.width<600?'translate(-62%,-50%)':'translate(-50%,-50%)';
  }
}
