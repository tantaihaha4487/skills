// MediaCard cover edges from shaders/rounded_image.frag, with the caller values
// of the reference cover-artwork component.
// A square cover's hovered edge is scalloped; a round cover's edge is a
// squiggle. These outlines feed a CSS clip-path or a canvas path. They sample
// the shader's analytic boundary; antialiasing and the drawn squiggle line are
// host rendering, not shader pixels (use SourceRenderer for pixel parity).

export const CARD_EDGE=Object.freeze({
  // MediaArtwork: waviness root.wavy ? 3.5 : 0, springing on Bounce
  // (disabled in performance mode); ArtworkImage.wavelength 22
  hoverWaviness:3.5,wavelength:22,
  wavinessSpring:Object.freeze({stiffness:7,damping:.24,epsilon:.002}),
  // ArtworkImage waveDrift: 2*PI/2.4 rad/s; Drift eases its rate 650ms InOutSine
  driftSpeed:2*Math.PI/2.4,driftEaseMs:650,
  // round covers: squiggle speed eases 700ms InOutSine, spin += dt*speed*waves*0.075
  squiggleEaseMs:700,squiggleTurnRate:.075,squiggleMinSize:40,
});

const TAU=2*Math.PI;

// scallops round the outline, counted on the item's own edge (not the cut-in
// one) so the count does not jump while the waviness springs
export function scallopCount(width,height,radius,wavelength=CARD_EDGE.wavelength){
  const hx=width/2,hy=height/2,corner=Math.min(radius,hx,hy);
  const perimeter=4*((hx-corner)+(hy-corner))+TAU*corner;
  return Math.max(1,Math.floor(perimeter/Math.max(wavelength,1)+.5));
}

// The shader's signed distance (negative inside), for tests and hit checks.
export function scallopDistance(x,y,width,height,{radius=12,waviness=0,wavelength=CARD_EDGE.wavelength,phase=0}={}){
  const hx=width/2-Math.abs(waviness),hy=height/2-Math.abs(waviness);
  const corner=Math.min(radius,hx,hy),sx=hx-corner,sy=hy-corner;
  const px=x-width/2,py=y-height/2,qx=Math.abs(px)-sx,qy=Math.abs(py)-sy;
  const box=Math.hypot(Math.max(qx,0),Math.max(qy,0))+Math.min(Math.max(qx,qy),0)-corner;
  if(Math.abs(waviness)<.001)return box;
  const quarter=.5*Math.PI*corner,perimeter=4*(sx+sy)+4*quarter;
  let along;
  if(qx>0&&qy>0){
    const turn=Math.atan2(Math.abs(px)-sx,Math.abs(py)-sy);
    if(py<0&&px>=0)along=sx+corner*turn;
    else if(py>=0&&px>=0)along=sx+quarter+2*sy+corner*(.5*Math.PI-turn);
    else if(py>=0)along=3*sx+2*quarter+2*sy+corner*turn;
    else along=3*sx+3*quarter+4*sy+corner*(.5*Math.PI-turn);
  }else if(qy>qx){
    along=py<0?px:sx+2*quarter+2*sy+(sx-px);
  }else{
    along=px>=0?sx+quarter+(py+sy):3*sx+3*quarter+2*sy+(sy-py);
  }
  const n=scallopCount(width,height,radius,wavelength);
  return box-waviness*(.5+.5*Math.cos(TAU*n*along/perimeter-phase));
}

// Outline points (item px, clockwise from the top middle) of the scalloped
// edge: the cut-in rounded rect pushed out along its normal by
// waviness*wave(along), so peaks reach the item edge and valleys cut in.
export function scallopOutline(width,height,{radius=12,waviness=0,wavelength=CARD_EDGE.wavelength,phase=0,samples=480}={}){
  const w=Math.abs(waviness),hx=width/2-w,hy=height/2-w;
  const corner=Math.min(radius,hx,hy),sx=hx-corner,sy=hy-corner;
  const quarter=.5*Math.PI*corner,perimeter=4*(sx+sy)+4*quarter;
  const n=scallopCount(width,height,radius,wavelength),cx=width/2,cy=height/2;
  // [length, start point, normal or arc centre] for the eight pieces, in the shader's order
  const pieces=[
    ['line',sx,[0,-hy],[1,0],[0,-1]],
    ['arc',quarter,[sx,-sy],-Math.PI/2],
    ['line',2*sy,[hx,-sy],[0,1],[1,0]],
    ['arc',quarter,[sx,sy],0],
    ['line',2*sx,[sx,hy],[-1,0],[0,1]],
    ['arc',quarter,[-sx,sy],Math.PI/2],
    ['line',2*sy,[-hx,sy],[0,-1],[-1,0]],
    ['arc',quarter,[-sx,-sy],Math.PI],
    ['line',sx,[-sx,-hy],[1,0],[0,-1]],
  ];
  const pts=[];
  for(let i=0;i<samples;i++){
    let s=perimeter*i/samples,along=s;
    let x,y,nx,ny;
    for(let k=0;k<pieces.length;k++){
      const [kind,len,a,b,c]=pieces[k];
      if(s>len&&k<pieces.length-1){s-=len;continue}
      if(kind==='line'){x=a[0]+b[0]*s;y=a[1]+b[1]*s;[nx,ny]=c}
      else{const t=b+(corner>0?s/corner:0);nx=Math.cos(t);ny=Math.sin(t);x=a[0]+corner*nx;y=a[1]+corner*ny}
      break;
    }
    const off=waviness*(.5+.5*Math.cos(TAU*n*along/perimeter-phase));
    pts.push([cx+x+nx*off,cy+y+ny*off]);
  }
  return pts;
}

export function scallopClipPath(width,height,options){
  return 'polygon('+scallopOutline(width,height,options).map(([x,y])=>`${x.toFixed(2)}px ${y.toFixed(2)}px`).join(',')+')';
}

// ArtworkImage squiggle proportions: a wave eight line-widths long and 0.7 of
// a line high either side, at every size.
export function squiggleGeometry(width,height=width){
  const size=Math.min(width,height),thickness=Math.max(2,size*.02);
  const amplitude=Math.max(1.4,thickness*.7);
  const middle=size/2-amplitude-thickness/2-.75;
  const waves=Math.max(8,Math.round(TAU*middle/(8*thickness)));
  return{shows:size>=CARD_EDGE.squiggleMinSize,thickness,amplitude,middle,waves};
}

// The sine the line follows (offset 0) and the cover cut (offset -2*thickness),
// angle measured clockwise from the top like the shader's atan(p.x,-p.y).
export function squiggleOutline(width,height=width,{phase=0,offset=0,samples=720}={}){
  const g=squiggleGeometry(width,height),cx=width/2,cy=height/2,pts=[];
  for(let i=0;i<samples;i++){
    const a=TAU*i/samples,r=g.middle+offset+g.amplitude*Math.sin(g.waves*a-phase);
    pts.push([cx+r*Math.sin(a),cy-r*Math.cos(a)]);
  }
  return pts;
}

export function squiggleCoverClipPath(width,height=width,{phase=0,samples}={}){
  const g=squiggleGeometry(width,height);
  return 'polygon('+squiggleOutline(width,height,{phase,offset:-2*g.thickness,samples}).map(([x,y])=>`${x.toFixed(2)}px ${y.toFixed(2)}px`).join(',')+')';
}

// One shared-clock step of a round cover's hovered squiggle (FrameAnimation in
// ArtworkImage). speed is the caller's eased 0..1 rate (700ms InOutSine), and
// is 0 under reduceMotion or a resting pointer.
export function advanceSquiggle(phase,seconds,speed,waves){
  return (phase+seconds*speed*waves*CARD_EDGE.squiggleTurnRate)%TAU;
}
