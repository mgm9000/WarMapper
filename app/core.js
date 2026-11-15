/* WarMapper playback core: the parts every battle shares.
   - mapView: the map itself (MapLibre GL JS), base layers, period-map images, camera, and picking a unit.
   - clock:   time, the play button, the slider, scrolling over the timeline, arrow keys.
   - helpers: geometry, text, the date box, the scale bar, the source list.
   Each battle's own script supplies its data, where its units are at a given time, and how they are drawn. */
(function(global){
"use strict";
var WM={};
var EARTH=40075016.686, TILE=512;

/* ---------- small helpers ---------- */
WM.$=function(id){return document.getElementById(id)};
WM.esc=function(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})};
WM.fmtClock=function(m){m=Math.round(m);var h=Math.floor(m/60),mm=m%60;return ((h+11)%12+1)+':'+(mm<10?'0':'')+mm+(h<12?' a.m.':' p.m.')};
WM.pad=function(g,n){g=g.slice();while(g.length<n)g.push(g[g.length-1]);return g};
WM.lerpG=function(a,b,f){var n=Math.max(a.length,b.length);a=WM.pad(a,n);b=WM.pad(b,n);var o=[];for(var i=0;i<n;i++)o.push([a[i][0]+(b[i][0]-a[i][0])*f,a[i][1]+(b[i][1]-a[i][1])*f]);return o};
WM.cen=function(g){var x=0,y=0;g.forEach(function(p){x+=p[0];y+=p[1]});return [x/g.length,y/g.length]};
WM.plen=function(g){var L=0;for(var i=1;i<g.length;i++)L+=Math.hypot(g[i][0]-g[i-1][0],g[i][1]-g[i-1][1]);return L};
/* the point a fraction f of the way along a line, and the direction of the line there */
WM.along=function(pts,f){var L=0,i,seg=[];for(i=1;i<pts.length;i++){var d=Math.hypot(pts[i][0]-pts[i-1][0],pts[i][1]-pts[i-1][1]);seg.push(d);L+=d}
  if(L<0.5) return {p:pts[0],v:[1,0]}; var h=L*f;
  for(i=0;i<seg.length;i++){if(h<=seg[i]){var q=seg[i]?h/seg[i]:0;return {p:[pts[i][0]+(pts[i+1][0]-pts[i][0])*q,pts[i][1]+(pts[i+1][1]-pts[i][1])*q],v:seg[i]?[(pts[i+1][0]-pts[i][0])/seg[i],(pts[i+1][1]-pts[i][1])/seg[i]]:[1,0]}}h-=seg[i]}
  return {p:pts[pts.length-1],v:[1,0]}};
WM.chip=function(v){var c=(v==='high'||v==='medium'||v==='low')?v:'na';return '<span class="chip '+c+'">'+WM.esc(v||'n/a')+'</span>'};
WM.srcList=function(sources,ids){var out='';String(ids||'').split(';').forEach(function(id){id=id.trim();var s=sources[id];if(!s)return;
  out+='<li><code>'+id+'</code> '+(s.url?'<a href="'+WM.esc(s.url)+'" target="_blank" rel="noopener">'+WM.esc(s.title)+'</a>':WM.esc(s.title))+'</li>'});return out};
/* an image or other file of the page: a single-file copy of the page carries them inside itself */
WM.asset=function(name){var a=global.WM_ASSETS;return (a&&a[name])?a[name]:name};
/* "M1 2L3 4L5 6Z" (the form the data files use for map lines) to a list of points */
WM.pathPoints=function(d){var out=[];String(d).split(/[MLZ]/).forEach(function(s){s=s.trim();if(!s)return;var a=s.split(/[ ,]+/);out.push([+a[0],+a[1]])});return out};
WM.OSM_CREDIT='Map data &copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> contributors';

/* ---------- date and time box ---------- */
var WDN=['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'],MON12=['January','February','March','April','May','June','July','August','September','October','November','December'];
WM.WEEKDAYS=WDN; WM.MONTHS=MON12;
/* cal = {first:'YYYY-MM-DD', numbered:true|false, count:n}; m = minutes from midnight of that first day.
   The day number is given only for battles whose data says their days are numbered. */
WM.calOf=function(cal,m){var i=Math.floor(m/1440),b=cal.first.split('-'),dt=new Date(Date.UTC(+b[0],+b[1]-1,+b[2]+i));
  return {n:(cal.numbered&&i>=0&&i<cal.count)?i+1:0,date:WDN[dt.getUTCDay()]+' '+dt.getUTCDate()+' '+MON12[dt.getUTCMonth()]+' '+dt.getUTCFullYear(),clock:WM.fmtClock(((m%1440)+1440)%1440)}};
WM.paintDayNumber=function(n){var el=WM.$('dayn');el.hidden=!n;if(n)el.textContent='Day '+n};

/* ---------- scale bar ---------- */
/* mPerPx: metres on the ground per screen pixel; units: 'yards' or 'km' */
WM.scaleBar=function(el,mPerPx,units){var pick,txt;
  if(units==='yards'){var oy=[100,250,500,1000,1760,3520,8800];pick=oy[0];oy.forEach(function(y){if(y*0.9144/mPerPx<=150)pick=y});
    txt=pick>=1760?(pick/1760)+(pick===1760?' mile':' miles'):pick+' yards'; el.innerHTML=txt+'<i style="width:'+(pick*0.9144/mPerPx).toFixed(0)+'px"></i>'}
  else{var om=[500,1000,2000,5000,10000,20000];pick=om[0];om.forEach(function(m){if(m/mPerPx<=150)pick=m});
    el.innerHTML=(pick>=1000?(pick/1000)+' km':pick+' m')+' <span style="opacity:.7">('+(pick/1609.34).toFixed(pick<2000?1:0)+' mi)</span><i style="width:'+(pick/mPerPx).toFixed(0)+'px"></i>'}};

/* ---------- the map ---------- */
function merc(ll){var s=Math.sin(ll[1]*Math.PI/180);return [(ll[0]+180)/360,0.5-Math.log((1+s)/(1-s))/(4*Math.PI)]}
function unmerc(m){return [m[0]*360-180,Math.atan(Math.sinh(Math.PI*(1-2*m[1])))*180/Math.PI]}
/* A "world" is one flat frame the battle's data is drawn in, with the way to turn its points into longitude and latitude:
   {toLL:function(p)->[lng,lat], ext:[x0,y0,x1,y1], mPerUnit:metres per unit of the frame, maxScale:most screen pixels per unit, minFactor:how far out past "the whole frame fits"}
   opt = {container, wrap, worlds:{name:world}, world:name, onDraw(), onStep(ts)->still moving?, onPick(id), onUserMove(), onResize()} */
WM.mapView=function(opt){
  if(!global.maplibregl) throw new Error('The map library did not load.');
  var wrap=opt.wrap,cur=opt.worlds[opt.world],curName=opt.world,tracked=[],bgToken='--land',hits=[];
  var c0=cur.toLL([(cur.ext[0]+cur.ext[2])/2,(cur.ext[1]+cur.ext[3])/2]);
  var map=new global.maplibregl.Map({container:opt.container,attributionControl:false,dragRotate:false,pitchWithRotate:false,touchPitch:false,keyboard:false,
    renderWorldCopies:false,maxPitch:0,fadeDuration:0,center:c0,zoom:12,
    style:{version:8,sources:{},layers:[{id:'bg',type:'background',paint:{'background-color':'#e6e9e0'}}]}});
  map.touchZoomRotate.disableRotation();
  function css(name){return getComputedStyle(wrap).getPropertyValue(name).trim()}
  function size(){var c=map.getContainer();return {w:c.clientWidth,h:c.clientHeight}}
  function pxPerMeter(zoom,lat){return TILE*Math.pow(2,zoom)/(EARTH*Math.cos(lat*Math.PI/180))}
  function scale(){var c=map.getCenter();return pxPerMeter(map.getZoom(),c.lat)*cur.mPerUnit}                 // screen pixels per unit of the current frame
  function zoomFor(s,lat,w){w=w||cur;return Math.log2(s/w.mPerUnit*EARTH*Math.cos(lat*Math.PI/180)/TILE)}
  function S(p){var q=map.project(cur.toLL(p));return [q.x,q.y]}
  function corners(b,w){w=w||cur;return [w.toLL([b[0],b[1]]),w.toLL([b[2],b[1]]),w.toLL([b[2],b[3]]),w.toLL([b[0],b[3]])]}
  /* the camera that shows box b (in the current frame) inside the padding; never closer than maxS screen pixels per unit */
  function cameraFor(b,pad,maxS){var z=size(),c=corners(b).map(merc),x0=1e9,y0=1e9,x1=-1e9,y1=-1e9;
    c.forEach(function(m){x0=Math.min(x0,m[0]);x1=Math.max(x1,m[0]);y0=Math.min(y0,m[1]);y1=Math.max(y1,m[1])});
    pad=pad||{t:0,b:0,l:0,r:0}; var aw=Math.max(40,z.w-pad.l-pad.r),ah=Math.max(40,z.h-pad.t-pad.b);
    var zoom=Math.log2(Math.min(aw/Math.max(x1-x0,1e-12),ah/Math.max(y1-y0,1e-12))/TILE),cm=[(x0+x1)/2,(y0+y1)/2],lat=unmerc(cm)[1];
    if(maxS) zoom=Math.min(zoom,zoomFor(maxS,lat));
    zoom=Math.max(map.getMinZoom(),Math.min(map.getMaxZoom(),zoom)); var ws=TILE*Math.pow(2,zoom);
    return {center:unmerc([cm[0]-((pad.l-pad.r)/2)/ws,cm[1]-((pad.t-pad.b)/2)/ws]),zoom:zoom}}
  function jump(cam){map.jumpTo(cam)}
  /* move part of the way to a camera; false once it has arrived */
  function chase(tg,rate){var c=map.getCenter(),z=map.getZoom(),dz=tg.zoom-z,a=merc([c.lng,c.lat]),b=merc(tg.center),ws=TILE*Math.pow(2,z),dx=(b[0]-a[0])*ws,dy=(b[1]-a[1])*ws;
    if(Math.abs(dz)<0.004&&Math.abs(dx)<0.6&&Math.abs(dy)<0.6){map.jumpTo(tg);return false}
    map.jumpTo({center:unmerc([a[0]+(b[0]-a[0])*rate,a[1]+(b[1]-a[1])*rate]),zoom:z+dz*rate});return true}
  function limits(){var e=cur.ext,z=size(),c=corners(e).map(merc),x0=1e9,y0=1e9,x1=-1e9,y1=-1e9;
    c.forEach(function(m){x0=Math.min(x0,m[0]);x1=Math.max(x1,m[0]);y0=Math.min(y0,m[1]);y1=Math.max(y1,m[1])});
    var lat=unmerc([(x0+x1)/2,(y0+y1)/2])[1],fit=Math.log2(Math.min(z.w/(x1-x0),z.h/(y1-y0))/TILE)+Math.log2(cur.minFactor||1);
    map.setMaxBounds(null); map.setMinZoom(0); map.setMaxZoom(24); map.setMinZoom(Math.max(0,Math.min(23,fit))); map.setMaxZoom(Math.min(24,Math.max(fit+0.5,zoomFor(cur.maxScale,lat))));
    var mx=(x1-x0)*2.5,my=(y1-y0)*2.5,sw=unmerc([x0-mx,y1+my]),ne=unmerc([x1+mx,y0-my]); map.setMaxBounds([sw,ne])}
  function setWorld(name){curName=name;cur=opt.worlds[name];limits()}
  function zoomBy(f){map.easeTo({zoom:map.getZoom()+Math.log2(f),duration:180})}

  /* layers: a colour written as 'var(--name)' follows the page's light and dark themes */
  function resolve(v){ if(typeof v==='function') return v(css); if(typeof v==='string'&&v.indexOf('var(')===0) return css(v.slice(4,-1)); return v }
  function layer(spec,before){var paint={},k;tracked=tracked.filter(function(t){return t[0]!==spec.id});for(k in (spec.paint||{})){var v=spec.paint[k];if(typeof v==='function'||(typeof v==='string'&&v.indexOf('var(')===0))tracked.push([spec.id,k,v]);paint[k]=resolve(v)}
    var s={};for(k in spec)s[k]=spec[k];s.paint=paint;map.addLayer(s,before)}
  function retheme(){map.setPaintProperty('bg','background-color',css(bgToken));tracked.forEach(function(t){if(map.getLayer(t[0]))map.setPaintProperty(t[0],t[1],resolve(t[2]))});map.triggerRepaint()}
  function bg(token){bgToken=token;map.setPaintProperty('bg','background-color',css(token))}
  function geo(id,features){map.addSource(id,{type:'geojson',data:{type:'FeatureCollection',features:features},tolerance:0.2})}
  function line(d,props,w){w=w||cur;return {type:'Feature',properties:props||{},geometry:{type:'LineString',coordinates:WM.pathPoints(d).map(w.toLL)}}}
  function poly(d,props,w){w=w||cur;var r=WM.pathPoints(d).map(w.toLL);if(r.length&&(r[0][0]!==r[r.length-1][0]||r[0][1]!==r[r.length-1][1]))r.push(r[0]);return {type:'Feature',properties:props||{},geometry:{type:'Polygon',coordinates:[r]}}}
  /* A period-map picture laid on the ground: box is where its corners sit in the frame. The picture is loaded as an ordinary image
     and handed to the map as a canvas, so it needs no web request of the map library's own and also works from a single-file page. */
  var pics={};
  function image(id,url,box,w){pics[id]={vis:true,op:1,want:null};map.addLayer({id:id+'-slot',type:'background',layout:{visibility:'none'}});moveImage(id,url,box,w)}   // the slot keeps the picture's place among the layers
  function moveImage(id,url,box,w){var rec=pics[id],cs=corners(box,w),im=new Image();rec.want=url;
    im.onload=function(){if(rec.want!==url)return;   // a later request overtook this one
      var cv=document.createElement('canvas');cv.width=im.naturalWidth;cv.height=im.naturalHeight;cv.getContext('2d').drawImage(im,0,0);
      if(map.getLayer(id))map.removeLayer(id);if(map.getSource(id))map.removeSource(id);
      map.addSource(id,{type:'canvas',canvas:cv,coordinates:cs,animate:false});
      layer({id:id,type:'raster',source:id,layout:{visibility:rec.vis?'visible':'none'},
        paint:{'raster-fade-duration':0,'raster-resampling':'linear','raster-opacity':rec.op,'raster-brightness-max':function(c){return +c('--raster-max')||1}}},id+'-slot');  // a little dimmer in the dark theme
      map.triggerRepaint()};
    im.onerror=function(){if(global.console)console.warn('WarMapper: could not load the picture '+String(url).slice(0,80))};
    im.src=url}
  function show(id,on){if(pics[id])pics[id].vis=on;if(map.getLayer(id))map.setLayoutProperty(id,'visibility',on?'visible':'none')}
  function opacity(id,v){if(pics[id])pics[id].op=v;if(map.getLayer(id))map.setPaintProperty(id,'raster-opacity',v)}

  /* picking: the battle's drawing code lists what can be tapped, last drawn on top */
  function pick(pt){for(var i=hits.length-1;i>=0;i--){var h=hits[i];
      if(h.r){if(pt.x>=h.r[0]&&pt.x<=h.r[2]&&pt.y>=h.r[1]&&pt.y<=h.r[3])return h}
      else if(h.pts){for(var j=1;j<h.pts.length;j++){var a=h.pts[j-1],b=h.pts[j],vx=b[0]-a[0],vy=b[1]-a[1],L=vx*vx+vy*vy,u=L?Math.max(0,Math.min(1,((pt.x-a[0])*vx+(pt.y-a[1])*vy)/L)):0;
        if(Math.hypot(pt.x-(a[0]+vx*u),pt.y-(a[1]+vy*u))<=h.tol)return h}}}
    return null}
  map.on('click',function(e){var h=pick(e.point);opt.onPick(h?h.id:null)});
  map.on('mousemove',function(e){map.getCanvas().style.cursor=pick(e.point)?'pointer':''});
  function userMove(){if(opt.onUserMove)opt.onUserMove()}   // the reader moved the map: stop following the action
  map.on('movestart',function(e){if(e.originalEvent)userMove()});map.on('wheel',userMove);map.on('dblclick',userMove);
  map.on('resize',function(){limits();if(opt.onResize)opt.onResize();kick()});
  /* drawing happens when the map draws, so units never lag behind the ground; stepping (playing, following) runs between frames */
  var stepRaf=0,ready=false;
  map.on('render',function(){if(ready)opt.onDraw()});
  function tick(ts){stepRaf=0;var more=opt.onStep?opt.onStep(ts):false;map.triggerRepaint();if(more)stepRaf=requestAnimationFrame(tick)}
  function kick(){map.triggerRepaint();if(ready&&!stepRaf)stepRaf=requestAnimationFrame(tick)}
  if(global.matchMedia){var mq=global.matchMedia('(prefers-color-scheme: dark)');if(mq.addEventListener)mq.addEventListener('change',function(){setTimeout(retheme,0)})}
  if(global.MutationObserver) new MutationObserver(function(){setTimeout(retheme,0)}).observe(document.documentElement,{attributes:true,attributeFilter:['data-theme','class','style']});

  var mv={map:map,css:css,size:size,scale:scale,S:S,cameraFor:cameraFor,jump:jump,chase:chase,setWorld:setWorld,zoomBy:zoomBy,zoomFor:function(s){var e=cur.ext;return zoomFor(s,cur.toLL([(e[0]+e[2])/2,(e[1]+e[3])/2])[1])},
    layer:layer,geo:geo,line:line,poly:poly,image:image,moveImage:moveImage,show:show,opacity:opacity,bg:bg,retheme:retheme,kick:kick,hits:hits,
    get world(){return curName}, mPerPx:function(){return cur.mPerUnit/scale()},
    /* run fn once the map is ready for layers */
    start:function(fn){map.on('load',function(){limits();fn();ready=true;retheme();kick()})}};
  return mv;
};

/* ---------- time ---------- */
/* o = {T0,T1, mv, toRange(t), fromRange(v), rate(t) (time units per second while playing), onTime(t), arrow(dir,t)->t, wheel(dd,t)->t,
        snap(t)->t (optional: where time settles when it stops), onKey(e) (optional: other keys)} */
WM.clock=function(o){
  var $=WM.$,range=$('time'),t=o.T0,playing=false,last=0,wheelT=0;
  function icon(){$('play').setAttribute('aria-label',playing?'Pause':'Play');$('playico').innerHTML=playing?'<path d="M3 1.5h3.5v13H3zM9.5 1.5H13v13H9.5z"/>':'<path d="M3 1.5v13l11-6.5z"/>'}
  function setTime(v,fromRange){t=Math.max(o.T0,Math.min(o.T1,v));if(!fromRange)range.value=o.toRange(t);o.onTime(t);o.mv.kick()}
  function settle(){if(o.snap&&t<o.T1){var s=o.snap(t);if(Math.abs(s-t)>0.001)setTime(s)}}
  function setPlaying(v){if(v===playing)return;playing=v;last=0;icon();if(v){if(t>=o.T1-0.01)setTime(o.T0);o.mv.kick()}else settle()}
  function step(ts){if(!playing)return false;var dt=last?Math.min(0.1,(ts-last)/1000):0;last=ts;var nt=t+dt*o.rate(t);
    if(nt>=o.T1){nt=o.T1;playing=false;icon()} t=nt;range.value=o.toRange(t);o.onTime(t);return playing}
  range.addEventListener('input',function(){setPlaying(false);setTime(o.fromRange(+range.value),true)});
  range.addEventListener('change',settle);
  $('play').addEventListener('click',function(){setPlaying(!playing)});
  /* over the timeline bar, scrolling moves time (over the map it zooms) */
  document.querySelector('.tlbar').addEventListener('wheel',function(e){e.preventDefault();var dy=e.deltaY*(e.deltaMode===1?16:e.deltaMode===2?400:1),dd=Math.abs(e.deltaX)>Math.abs(dy)?e.deltaX:dy;
    setPlaying(false);setTime(o.wheel(dd,t));if(o.snap){clearTimeout(wheelT);wheelT=setTimeout(settle,350)}},{passive:false});
  document.addEventListener('keydown',function(e){var tag=e.target.tagName;if(tag==='BUTTON'||tag==='SUMMARY')return;
    if(e.key==='ArrowRight'||e.key==='ArrowLeft'){if(tag==='INPUT'&&!o.snap)return;setPlaying(false);setTime(o.arrow(e.key==='ArrowRight'?1:-1,t));e.preventDefault();return}
    if(tag==='INPUT')return;
    if(e.key===' '){setPlaying(!playing);e.preventDefault()} else if(o.onKey)o.onKey(e)});
  return {setTime:setTime,setPlaying:setPlaying,step:step,get t(){return t},get playing(){return playing}};
};

/* clicks in the side panel: a unit in a list, or the "All units" link */
WM.panelClicks=function(panel,onPick){panel.addEventListener('click',function(e){var b=e.target.closest('[data-pick]');if(b){onPick(b.getAttribute('data-pick'));return} if(e.target.id==='back')onPick(null)})};
/* the gesture hint goes away once the map has been used, and is never shown on touch screens */
WM.hint=function(mv){var h=WM.$('hint');if(!h)return;if(global.matchMedia&&global.matchMedia('(pointer:coarse)').matches){h.hidden=true;return}
  var off=function(){h.hidden=true};mv.map.once('movestart',off);mv.map.once('click',off)};
/* shown in place of the map when the browser cannot draw it */
WM.noMap=function(wrap,err){var d=document.createElement('div');d.className='nogl';d.textContent='This map needs WebGL, which this browser has switched off or does not support. ('+(err&&err.message?err.message:err)+')';wrap.appendChild(d)};

global.WM=WM;
})(window);
