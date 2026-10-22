import {advanceSpring, CARD_SPRING} from './spring.mjs';
// Source-backed lyrics layout and motion values extracted from
// the reference lyrics panels.  The controller owns no provider,
// clock, or media service; callers supply lines and active state.
export const SOURCE_LYRICS_MOTION = Object.freeze({
  reducedScrollMs: 420,
  lineSettleMs: 560,
  staggerMsPerDistance: 16,
  staggerDistanceCap: 8,
  panelSpacing: 22,
  panelTopMargin: 18,
  panelBottomMargin: 18,
  panelHorizontalMargin: 24,
  immersiveSpacing: 26,
  immersiveTopMargin: 30,
  immersiveBottomMargin: 30,
  immersiveHorizontalMargin: 8,
  panelInactiveScale: 19 / 22,
  immersiveInactiveScale: 0.96,
  panelInactiveOpacity: 0.34,
  immersiveInactiveOpacity: 0.28,
  panelOpacityMs: 280,
  immersiveOpacityMs: 320,
});

export function lineIsActive({synchronized, activeIndex}, index) {
  return !synchronized || activeIndex === index;
}

export function lineStaggerDelay(index, activeIndex) {
  return Math.min(Math.abs(index - activeIndex), SOURCE_LYRICS_MOTION.staggerDistanceCap)
    * SOURCE_LYRICS_MOTION.staggerMsPerDistance;
}

export function followTarget({itemY, itemHeight, listHeight, contentHeight, originY = 0,
  topMargin, bottomMargin}) {
  return Math.max(originY - topMargin,
    Math.min(itemY + itemHeight / 2 - listHeight / 2,
      contentHeight + originY - listHeight + bottomMargin));
}

export function easingOutCubic(progress) {
  const t = Math.max(0, Math.min(1, progress));
  return 1 - (1 - t) ** 3;
}

export function lineVisualState(variant, {synchronized, activeIndex}, index) {
  const active = lineIsActive({synchronized, activeIndex}, index);
  const immersive = variant === 'immersive';
  return {
    active,
    glow: immersive && synchronized && active ? 1 : 0,
    scale: active ? 1 : (immersive ? SOURCE_LYRICS_MOTION.immersiveInactiveScale
      : SOURCE_LYRICS_MOTION.panelInactiveScale),
    opacity: active ? 1 : (immersive ? SOURCE_LYRICS_MOTION.immersiveInactiveOpacity
      : SOURCE_LYRICS_MOTION.panelInactiveOpacity),
    staggerDelay: lineStaggerDelay(index, activeIndex),
  };
}

export function seekTimeForLine(lines, synchronized, index) {
  if (!synchronized || index < 0 || index >= lines.length) return null;
  return Number.isFinite(lines[index]?.startTimeMs) ? lines[index].startTimeMs : null;
}

export class LyricsMotionController {
  constructor({variant = 'panel', root = null, list = null, onSeek = () => {}} = {}) {
    this.disposed = false;
    this.variant = variant;
    this.root = root;
    this.list = list;
    this.onSeek = onSeek;
    this.lines = [];
    this.loading = false;
    this.synchronized = false;
    this.activeIndex = -1;
    this.reducedMotion = false;
    this.performanceMode = false;
    this.noShapes = false;
    this.suspended = false;
    this.scrollAnimation = null;
    this.renderedScrollTop = 0;
    this.visuals = [];
    this.lineAnimations = [];
    this.lagAnimations = [];
    this.flashAnimations = [];
  }

  setState(patch = {}) {
    if(this.disposed)return;
    const wasSuspended=this.suspended,previousIndex=this.activeIndex,previousSync=this.synchronized;
    Object.assign(this, patch);
    if (Object.prototype.hasOwnProperty.call(patch, 'loading') && this.root) {
      this.root.dataset.loading = String(this.loading);
    }
    if(previousIndex!==this.activeIndex||previousSync!==this.synchronized)
      this.setActive(this.activeIndex,{follow:previousIndex!==this.activeIndex});
    this.render();
    if(wasSuspended&&!this.suspended&&this.variant==='panel')this.follow(false);
  }

  setLines(lines, {synchronized = false, activeIndex = -1} = {}) {
    if(this.disposed)return;
    this.lines = lines.map(line => ({...line}));
    this.synchronized = synchronized;
    this.activeIndex = activeIndex;
    this.scrollAnimation = null;
    this.lineAnimations = []; this.lagAnimations = []; this.flashAnimations = [];
    this.visuals = this.lineStates().map(state=>({...state,lag:0,springing:state.scale,eased:state.scale}));
    this.list?.replaceChildren();
    this.render();
  }

  metrics() {
    const immersive = this.variant === 'immersive';
    return immersive ? {
      spacing: SOURCE_LYRICS_MOTION.immersiveSpacing,
      topMargin: SOURCE_LYRICS_MOTION.immersiveTopMargin,
      bottomMargin: SOURCE_LYRICS_MOTION.immersiveBottomMargin,
      horizontalMargin: SOURCE_LYRICS_MOTION.immersiveHorizontalMargin,
    } : {
      spacing: SOURCE_LYRICS_MOTION.panelSpacing,
      topMargin: SOURCE_LYRICS_MOTION.panelTopMargin,
      bottomMargin: SOURCE_LYRICS_MOTION.panelBottomMargin,
      horizontalMargin: SOURCE_LYRICS_MOTION.panelHorizontalMargin,
    };
  }

  lineStates() {
    return this.lines.map((_line, index) => lineVisualState(this.variant,
      {synchronized: this.synchronized, activeIndex: this.activeIndex}, index));
  }

  targetFor(index) {
    const metrics=this.metrics();
    if (!this.list || index < 0 || index >= this.lines.length) return (this.list?.scrollTop||0)-metrics.topMargin;
    const item=this.list.children[index],last=this.list.children[this.lines.length-1];
    if(!item||!last)return this.list.scrollTop-metrics.topMargin;
    // Qt contentHeight includes the provider footer, but excludes ListView
    // margins. scrollHeight is viewport-clamped, so derive the real extent.
    const footerHeight=this.variant==='immersive'?61:33;
    const contentHeight=last.offsetTop-metrics.topMargin+last.offsetHeight+footerHeight;
    return followTarget({itemY:item.offsetTop-metrics.topMargin,itemHeight:item.offsetHeight,
      listHeight:this.list.clientHeight,contentHeight,topMargin:metrics.topMargin,bottomMargin:metrics.bottomMargin});
  }

  follow(animated = true) {
    if(this.disposed)return;
    if (!this.list || this.activeIndex < 0 || (this.variant==='panel'&&this.suspended)) return;
    const target = this.targetFor(this.activeIndex);
    const current = this.list.scrollTop-this.metrics().topMargin;
    this.scrollAnimation = null;
    // The source uses a plain 420ms OutCubic scroll only for reduced motion.
    if (animated && this.reducedMotion && !this.performanceMode) {
      this.scrollAnimation = {from: current, to: target, elapsed: 0,
        duration: SOURCE_LYRICS_MOTION.reducedScrollMs};
    } else {
      this.list.scrollTop = target+this.metrics().topMargin;
      this.renderedScrollTop = target;
      if (animated && !this.reducedMotion && !this.performanceMode) {
        this.lagAnimations = this.lines.map((_line,index)=>({
          from:(this.visuals[index]?.lag||0)+(target-current),elapsed:0,
          delay:lineStaggerDelay(index,this.activeIndex)}));
        this.lagAnimations.forEach((animation,index)=>{this.visuals[index].lag=animation.from;});
      }
    }
    this.render();
  }

  advance(milliseconds) {
    if(this.disposed)return false;
    const dt=Math.max(0,milliseconds); let moving=false;
    if (this.scrollAnimation && this.list) {
      const animation=this.scrollAnimation;
      animation.elapsed=Math.min(animation.duration,animation.elapsed+dt);
      this.list.scrollTop=animation.from+(animation.to-animation.from)*easingOutCubic(animation.elapsed/animation.duration)+this.metrics().topMargin;
      this.renderedScrollTop=this.list.scrollTop;
      if(animation.elapsed>=animation.duration)this.scrollAnimation=null;else moving=true;
    }
    this.lineAnimations.forEach((animation,index)=>{
      if(!animation)return;
      animation.elapsed+=dt;
      const state=this.visuals[index];
      // Qt keeps both properties alive: changing the settings switches the
      // selected binding, while an already-running hidden spring keeps going.
      if(animation.spring){
        animation.spring=advanceSpring(animation.spring,animation.toScale,dt,CARD_SPRING,{maxFrameMs:Number.MAX_VALUE});
        state.springing=animation.spring.position;
      }
      if(animation.ease){
        const t=Math.min(1,animation.elapsed/420);
        state.eased=animation.ease.from+(animation.toScale-animation.ease.from)*easingOutCubic(t);
      }
      state.scale=(this.reducedMotion||this.performanceMode)?state.eased:state.springing;
      const duration=this.variant==='immersive'?320:280;
      const t=Math.min(1,animation.elapsed/duration),eased=t<.5?2*t*t:1-2*(1-t)**2;
      state.opacity=animation.fromOpacity+(animation.toOpacity-animation.fromOpacity)*eased;
      const glowT=Math.min(1,animation.elapsed/320),glowEased=glowT<.5?2*glowT*glowT:1-2*(1-glowT)**2;
      state.glow=animation.fromGlow+(animation.toGlow-animation.fromGlow)*glowEased;
      const scaleDone=(!animation.spring||animation.spring.settled)&&(!animation.ease||animation.elapsed>=420);
      if(scaleDone&&t>=1)this.lineAnimations[index]=null;else moving=true;
    });
    this.lagAnimations.forEach((animation,index)=>{
      if(!animation)return;
      animation.elapsed+=dt;
      const t=Math.max(0,Math.min(1,(animation.elapsed-animation.delay)/560));
      // Qt Easing.OutBack, overshoot .6, exact scalar equation.
      const eased=1+1.6*(t-1)**3+.6*(t-1)**2;
      this.visuals[index].lag=animation.from*(1-eased);
      if(t>=1)this.lagAnimations[index]=null;else moving=true;
    });
    this.flashAnimations.forEach((animation,index)=>{
      if(!animation)return;
      animation.elapsed+=dt;
      if(animation.elapsed>=260)this.flashAnimations[index]=null;else moving=true;
    });
    this.render();return moving;
  }

  setActive(index, {animated = true, follow = true} = {}) {
    if(this.disposed)return;
    this.activeIndex = index;
    const targets=this.lineStates();
    this.lineAnimations=targets.map((target,i)=>{
      const current=this.visuals[i]||{...target,lag:0,springing:target.scale,eased:target.scale};this.visuals[i]=current;
      if(!animated||this.performanceMode||(this.variant==='panel'&&this.suspended)){
        Object.assign(current,target,{springing:target.scale,eased:target.scale});return null;
      }
      let spring=null,ease=null;
      if(this.reducedMotion){
        ease={from:current.eased};current.springing=target.scale;
      }else{
        spring={position:current.springing,velocity:this.lineAnimations[i]?.spring?.velocity||0,accumulator:this.lineAnimations[i]?.spring?.accumulator||0};
        current.eased=target.scale;
      }
      return {fromScale:current.scale,toScale:target.scale,fromOpacity:current.opacity,toOpacity:target.opacity,fromGlow:current.glow||0,toGlow:target.glow,
        elapsed:0,spring,ease};
    });
    this.render();if(follow)this.follow(animated);
  }

  seekLine(index) {
    if(this.disposed)return null;
    const time = seekTimeForLine(this.lines, this.synchronized, index);
    if (time !== null) {
      if(this.variant==='immersive')this.flashAnimations[index]={elapsed:0};
      this.render();this.onSeek(time, index);
    }
    return time;
  }

  render() {
    if(this.disposed)return;
    if (!this.root || !this.list) return;
    this.root.dataset.state = this.loading ? 'loading' : this.lines.length===0 ? 'empty' : 'ready';
    this.list.dataset.footer=`Lyrics provided by ${this.provider||''}`;
    this.root.dataset.noShapes = this.noShapes ? 'true' : 'false';
    this.root.dataset.reducedMotion = this.reducedMotion ? 'true' : 'false';
    this.root.dataset.performanceMode = this.performanceMode ? 'true' : 'false';
    const states = this.lineStates();
    this.lines.forEach((line, index) => {
      let item=this.list.children[index],text;
      if(!item){
        item=document.createElement('article');item.className='lyrics-closure__line';item.dataset.index=String(index);
        if(this.variant==='immersive'){
          const highlight=document.createElement('div');highlight.className='lyrics-closure__highlight';
          const flash=document.createElement('div');flash.className='lyrics-closure__flash';item.append(highlight,flash);
        }
        text=document.createElement('button');text.type='button';text.className='lyrics-closure__text';
        text.addEventListener('click',()=>this.seekLine(index));item.append(text);this.list.append(item);
      }else text=item.querySelector('button');
      const visual=this.visuals[index]||states[index];
      if(visual.springing!==undefined)visual.scale=(this.reducedMotion||this.performanceMode)?visual.eased:visual.springing;
      item.dataset.active=String(states[index].active);
      const highlight=item.querySelector('.lyrics-closure__highlight');
      if(highlight)highlight.style.backgroundColor=`rgb(255 255 255 / ${(visual.glow||0)*7}%)`;
      const flash=item.querySelector('.lyrics-closure__flash'),time=this.flashAnimations[index]?.elapsed;
      if(flash){
        const peak=.13*(1-(1-80/180)**2);
        const alpha=time===undefined?0:this.performanceMode?(time<80?.13:0):time<=80?.13*(1-(1-time/180)**2):peak*(1-Math.min(1,(time-80)/180))**2;
        flash.style.backgroundColor=`rgb(255 255 255 / ${alpha*100}%)`;
      }
      item.style.setProperty('--line-scale',String(visual.scale));
      item.style.setProperty('--line-opacity',String(visual.opacity));
      item.style.setProperty('--line-delay',`${states[index].staggerDelay}ms`);
      item.style.transform=`translateY(${visual.lag||0}px)${this.variant==='immersive'?` scale(${visual.scale})`:''}`;
      const words=line.words?.length?line.words:'♪';if(text.textContent!==words)text.textContent=words;text.disabled=!this.synchronized;
    });
  }
  dispose(){this.disposed=true;this.scrollAnimation=null;this.lineAnimations=[];this.lagAnimations=[];this.flashAnimations=[];this.lines=[];this.visuals=[];this.root=null;this.list=null;this.onSeek=()=>{};}
}
