// Logical geometry from the reference shell. Physical window minimum enforcement is
// provided by the host (a web document cannot resize its containing browser).
export function sourceLayout(width,height,{zoom=1,sidebarWidth=232}={}){
  zoom=Math.max(.5,Math.min(2,zoom));
  const layoutWidth=width/zoom,layoutHeight=height/zoom;
  const sidebar=Math.max(132,Math.min(sidebarWidth,layoutWidth*.28));
  return{zoom,layoutWidth,layoutHeight,sidebar,rightPanelFits:layoutWidth-sidebar-320-32>=404,
    minimumWidth:Math.ceil(526*zoom),minimumHeight:Math.ceil(410*zoom)};
}
export function sourceZoomCommand(value){return Math.round(Math.min(2,Math.max(.5,value))*10)/10;}

// Source Shortcut sequences on a Control-key host. The caller owns dispatch
// and preventDefault; null leaves unrelated input untouched.
export function sourceZoomForKey(event,zoom=1){
  if(!event.ctrlKey||event.altKey||!['+','=','-','0'].includes(event.key))return null;
  return sourceZoomCommand(event.key==='0'?1:zoom+(event.key==='-'?-.1:.1));
}

// Explicit DOM adapter: layers are positioned at the host origin by its CSS.
// Logical geometry is scaled once; hero overlays using physical DOM rects
// remain outside these layers. This does not resize the external browser.
export function applySourceZoom({content,overlay,width,height,zoom=1,sidebarWidth=232,minimumTarget=null}){
  const geometry=sourceLayout(width,height,{zoom,sidebarWidth});
  for(const element of [content,overlay]){
    if(!element)continue;
    element.style.width=`${geometry.layoutWidth}px`;element.style.height=`${geometry.layoutHeight}px`;
    element.style.transform=`scale(${geometry.zoom})`;element.style.transformOrigin='0 0';
  }
  if(minimumTarget){minimumTarget.style.minWidth=`${geometry.minimumWidth}px`;minimumTarget.style.minHeight=`${geometry.minimumHeight}px`;}
  content?.ownerDocument.documentElement.style.setProperty('--layout-height',`${geometry.layoutHeight}px`);
  return geometry;
}

// Right-panel state from the player state and the reference shell. Lyrics start shown
// (m_showingLyrics = true) and the queue hidden; lyrics and queue exclude each
// other. Whenever the panel does not fit, both are cleared (closeCrowdedPanels,
// on fit changes and on every panel change), so a toggle pressed while it does
// not fit opens nothing and widening again does not reopen it. the reference shell's
// window opens at 1280 wide, so a host that loads already narrow starts as if
// it had shrunk from there: lyrics cleared. Record that as the start adaptation.
export class SourcePanels{
  constructor(rightPanelFits){this.lyrics=true;this.queue=false;this.fits=rightPanelFits;this.closeCrowded();}
  closeCrowded(){if(!this.fits){this.lyrics=false;this.queue=false}return this}
  setFits(fits){if(fits!==this.fits){this.fits=fits;this.closeCrowded()}return this}
  setLyrics(on){this.lyrics=on;if(on)this.queue=false;return this.closeCrowded()}
  setQueue(on){this.queue=on;if(on)this.lyrics=false;return this.closeCrowded()}
  toggleLyrics(){return this.setLyrics(!this.lyrics)}
  toggleQueue(){return this.setQueue(!this.queue)}
  // the inspector also needs setup complete and the immersive view closed
  shown({immersiveOpen=false,needsSetup=false}={}){return(this.lyrics||this.queue)&&!immersiveOpen&&!needsSetup&&this.fits}
}
