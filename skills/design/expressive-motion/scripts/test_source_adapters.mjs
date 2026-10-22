// Offline cross-language source oracle checks. Browser/GPU/DOM proof is separate.
import fs from 'node:fs';
import assert from 'node:assert/strict';
import {sourceLayout} from '../assets/web-adapter/source-layout.mjs';
import {spectrumStyle,spectrumTargets} from '../assets/web-adapter/spectrum.mjs';
const native=JSON.parse(fs.readFileSync(new URL('../assets/adapters-oracle.json',import.meta.url)));
let checks=0;
for(const row of native.zoom_cases){
 const actual=sourceLayout(row.width,780,{zoom:row.zoom});
 for(const[key,source]of [['layoutWidth','layout_width'],['sidebar','sidebar'],['rightPanelFits','fits'],['minimumWidth','minimum_width'],['minimumHeight','minimum_height']]){
  assert.equal(actual[key],row[source]);checks++;
 }
}
for(const row of native.spectrum.cases){
 const actual=spectrumTargets(native.spectrum.raw_levels,spectrumStyle(row.kind,row.height,row.wave));
 assert.deepEqual(actual,row.targets,row.name);checks+=actual.length;
}
console.log(JSON.stringify({status:'pass',checks,spectrum_cases:native.spectrum.cases.length,zoom_cases:native.zoom_cases.length,scope:'Offline numeric source oracles; not GPU, DOM or live audio proof'}));
// right-panel state: tst_views aNarrowWindowClosesItsRightPanels plus PlaybackController defaults
{
 const {SourcePanels}=await import('../assets/web-adapter/source-layout.mjs');
 const fits=w=>sourceLayout(w,780).rightPanelFits;
 const p=new SourcePanels(fits(1280));assert.equal(p.lyrics,true);assert.equal(p.queue,false);assert.equal(p.shown(),true);
 assert.equal(new SourcePanels(fits(988)).shown(),true);assert.equal(new SourcePanels(fits(987)).lyrics,false);
 p.setFits(fits(1000));p.setLyrics(true);p.setFits(fits(980));assert.equal(p.lyrics,false);assert.equal(p.queue,false);
 p.setFits(fits(526));p.setQueue(true);assert.equal(p.queue,false);
 p.setFits(fits(1000));assert.equal(p.lyrics,false);assert.equal(p.queue,false);
 p.toggleQueue();assert.equal(p.queue,true);p.toggleLyrics();assert.equal(p.lyrics,true);assert.equal(p.queue,false);
 assert.equal(p.shown({immersiveOpen:true}),false);
 console.log(JSON.stringify({status:'pass',panel_checks:16,scope:'Panel state semantics; not QML runtime'}));
}
