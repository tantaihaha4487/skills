// Offline checks of card-edge.mjs against rounded_image.frag's equations.
import assert from 'node:assert/strict';
import {CARD_EDGE,scallopCount,scallopDistance,scallopOutline,scallopClipPath,squiggleGeometry,squiggleOutline,advanceSquiggle} from '../assets/web-adapter/card-edge.mjs';
let checks=0;const near=(a,b,eps,msg)=>{assert.ok(Math.abs(a-b)<=eps,`${msg}: ${a} vs ${b}`);checks++};

// MediaArtwork/ArtworkImage caller values
assert.equal(CARD_EDGE.hoverWaviness,3.5);assert.equal(CARD_EDGE.wavelength,22);checks+=2;
// 176px square card, radius 12: perimeter 4*(76+76)+2*PI*12 = 683.40 -> 31 scallops
assert.equal(scallopCount(176,176,12),31);checks++;
assert.equal(scallopCount(10,10,99,22),1);checks++;

let worst=0,points=0;
for(const [w,h,radius] of [[176,176,12],[144,144,12],[60,40,30],[176,176,0]])
  for(const waviness of [0,1.7,3.5])
    for(const phase of [0,1.3,5.9]){
      const pts=scallopOutline(w,h,{radius,waviness,phase,samples:600});
      let maxX=0;
      for(const [x,y] of pts){
        const d=Math.abs(scallopDistance(x,y,w,h,{radius,waviness,phase}));
        worst=Math.max(worst,d);points++;maxX=Math.max(maxX,Math.abs(x-w/2));
      }
      // peaks reach the item's edge; nothing leaves it
      assert.ok(maxX<=w/2+1e-9,`outline leaves item ${w}x${h}`);checks++;
      if(waviness===0)near(maxX,w/2,1e-9,'plain edge reaches item');
    }
assert.ok(worst<1e-9,`outline off the shader contour by ${worst}`);checks++;
assert.match(scallopClipPath(176,176,{radius:12,waviness:3.5,samples:8}),/^polygon\((-?[\d.]+px -?[\d.]+px,){7}-?[\d.]+px -?[\d.]+px\)$/);checks++;

// ArtworkImage squiggle proportions at 176px
const g=squiggleGeometry(176);
near(g.thickness,3.52,1e-12,'thickness');near(g.amplitude,2.464,1e-12,'amplitude');
near(g.middle,83.026,1e-9,'middle');assert.equal(g.waves,19);assert.equal(squiggleGeometry(39).shows,false);checks+=2;
for(const [x,y] of squiggleOutline(176,176,{phase:.7,samples:90})){
  const px=x-88,py=y-88,angle=g.waves*Math.atan2(px,-py)-.7;
  near(Math.hypot(px,py),g.middle+g.amplitude*Math.sin(angle),1e-9,'squiggle on its sine');
}
near(advanceSquiggle(0,1,1,19),19*.075,1e-12,'squiggle turn rate');

console.log(JSON.stringify({status:'pass',checks,outline_points:points,max_contour_error:worst,
  scope:'Analytic boundary of rounded_image.frag; not antialiased pixels or GPU output'}));
