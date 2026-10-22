import assert from 'node:assert/strict';
import fs from 'node:fs';
import {simulateSpring,CardScaleAnimation} from '../assets/card-spring.mjs';
const oracle=JSON.parse(fs.readFileSync(new URL('../assets/card-scale-oracle.json',import.meta.url)));
let count=0,maxError=0;
for(const phase of ['press','release']){
 const actual=oracle.samples.filter(s=>s.phase===phase);
 const model=simulateSpring({from:phase==='press'?1:.95,target:phase==='press'?.95:1,steps:40});
 for(const s of actual){const error=Math.abs(model[s.t_ms/16].position-s.scale);assert.ok(error<1e-12);maxError=Math.max(maxError,error);count++;}
}
// Lifecycle tests exercise the scheduler rather than just endpoints.
let next=0;const callbacks=new Map();
globalThis.requestAnimationFrame=cb=>{callbacks.set(++next,cb);return next;};
globalThis.cancelAnimationFrame=id=>callbacks.delete(id);
const a=new CardScaleAnimation({onUpdate:()=>{}});a.setTarget(.95);assert.equal(callbacks.size,1);
a.advance(80);const velocity=a.velocity;a.setTarget(1);assert.equal(a.velocity,velocity);assert.equal(callbacks.size,1);
a.setPerformance(true);assert.equal(a.position,1);assert.equal(a.velocity,0);assert.equal(callbacks.size,0);
a.setPerformance(false);a.setTarget(.95);a.dispose();assert.equal(callbacks.size,0);a.setTarget(1);assert.equal(callbacks.size,0);
const isolated=JSON.parse(fs.readFileSync(new URL('../assets/normalized-spring-oracle.json',import.meta.url)));
const forward=simulateSpring({from:0,target:1,steps:96});
const origin=forward[8];
const reversal=simulateSpring({from:origin.position,initialVelocity:origin.velocity,target:0,steps:96});
let reversalMax=0;
for(const [i,t] of isolated.reversal.timesMs.entries()){
 const error=Math.abs(reversal[t/16].position-isolated.reversal.reversal[i]);assert.ok(error<1e-12);reversalMax=Math.max(reversalMax,error);
}
assert.equal(isolated.forward.forward[1],0);assert.equal(forward[1].position,.112);
console.log(JSON.stringify({isolated_reversal_samples:isolated.reversal.timesMs.length,isolated_reversal_max_error:reversalMax,startup_boundary:'first callback registration differs; test_motion_engine.mjs verifies explicit Qt lifecycle without shifting oracle',oracle_samples:count,max_error:maxError,lifecycle_checks:9,status:'pass',boundary:'fixed16ms recurrence; reversal velocity retention is a lifecycle check, not a Qt trajectory comparison'}));
