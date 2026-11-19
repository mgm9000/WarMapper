/* WarMapper playback core: the parts every battle shares.
   - battle:  reads a battle file (the one format every battle's data comes in; docs/battle-file.md) and lays it out for drawing.
   - mapView: the map itself (MapLibre GL JS), base layers, period-map images, camera, and picking a unit.
   - clock:   time, the play button, the slider, scrolling over the timeline, arrow keys.
   - helpers: geometry, text, the date box, the scale bar, the source list.
   player.js is the playback itself: the rules for where units are at a given time, how they are drawn, the controls and the side panel. */
(function(global){
"use strict";
var WM={};
var EARTH=40075016.686, TILE=512;

/* ---------- small helpers ---------- */
WM.$=function(id){return document.getElementById(id)};
WM.esc=function(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})};
WM.fmtClock=function(m){m=Math.round(m);var h=Math.floor(m/60)%24,mm=((m%60)+60)%60;if(h<0)h+=24;return (h<10?'0':'')+h+':'+(mm<10?'0':'')+mm};   // 24-hour clock everywhere (Morgan, 18 Nov)
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
/* a map feature (a line or an area) from a list of [longitude, latitude] points */
WM.feat=function(type,ll,props){var area=type==='area',r=ll;
  if(area&&r.length&&(r[0][0]!==r[r.length-1][0]||r[0][1]!==r[r.length-1][1]))r=r.concat([r[0]]);
  return {type:'Feature',properties:props||{},geometry:area?{type:'Polygon',coordinates:[r]}:{type:'LineString',coordinates:r}}};
WM.OSM_CREDIT='Map data &copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> contributors';

/* ---------- date and time box ---------- */
var WDN=['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'],MON12=['January','February','March','April','May','June','July','August','September','October','November','December'];
WM.WEEKDAYS=WDN; WM.MONTHS=MON12;
/* cal = {first:'YYYY-MM-DD', numbered:true|false, count:n}; m = minutes from midnight of that first day.
   The day number is given only for battles whose data says their days are numbered. */
WM.calOf=function(cal,m){var i=Math.floor(m/1440),b=cal.first.split('-'),dt=new Date(Date.UTC(+b[0],+b[1]-1,+b[2]+i));
  return {n:(cal.numbered&&i>=0&&i<cal.count)?i+1:0,date:WDN[dt.getUTCDay()]+' '+dt.getUTCDate()+' '+MON12[dt.getUTCMonth()]+' '+dt.getUTCFullYear(),clock:WM.fmtClock(((m%1440)+1440)%1440)}};
WM.paintDayNumber=function(n){var el=WM.$('dayn');el.hidden=!n;if(n)el.textContent='Day '+n};

/* ---------- the battle file ---------- */
/* Every battle's data arrives as one battle file (format "warmapper-battle/1": docs/battle-file.md). The file holds places as
   longitude and latitude and times as dates and clock times. WM.battle turns it into what the drawing code works with:
   - a flat frame in metres, east and south of the file's origin (B.toLL and B.fromLL go between the frame and longitude, latitude);
   - time as a number: minutes or days (the file says which) from the file's zero;
   - B.tracks: one per symbol, each with its steps k[] in time order. A step has t0, t1 (when it is shown), g (its points in the frame),
     and the record behind it: act, place, say (the source's words), method, oc (confidence), src, notes, ts and te (its times as text). */
WM.battle=function(raw){
  if(!raw||String(raw.format)!=='warmapper-battle/1') throw new Error('This page reads battle files of format warmapper-battle/1; this file says '+(raw&&raw.format));
  var B={raw:raw,id:raw.id,title:raw.title,subtitle:raw.subtitle||'',sources:raw.sources||{},opening:raw.opening||{label:'',text:''}};
  /* the frame: metres per degree of longitude and of latitude at the origin (the standard series for the WGS 84 ellipsoid) */
  var o=raw.view.origin,ph=o[1]*Math.PI/180,KY=111132.92-559.82*Math.cos(2*ph)+1.175*Math.cos(4*ph),KX=111412.84*Math.cos(ph)-93.5*Math.cos(3*ph);
  B.toLL=function(p){return [o[0]+p[0]/KX,o[1]-p[1]/KY]};
  B.fromLL=function(q){return [(q[0]-o[0])*KX,(o[1]-q[1])*KY]};
  B.box=function(b){var a=B.fromLL([b[0],b[3]]),c=B.fromLL([b[2],b[1]]);return [a[0],a[1],c[0],c[1]]};   // [west, south, east, north] -> a box in the frame
  B.ext=B.box(raw.view.extent); B.presets={}; B.points={}; var k;
  for(k in (raw.view.presets||{})) B.presets[k]=B.box(raw.view.presets[k]);
  for(k in (raw.view.points||{})) B.points[k]=B.fromLL(raw.view.points[k]);
  /* time */
  var T=raw.time,byDay=T.unit==='day';
  function stamp(s){var m=/^(\d{4})-(\d\d)-(\d\d)(?:T(\d\d):(\d\d)(?::(\d\d))?)?$/.exec(s);if(!m)throw new Error('not a date or time: '+s);
    var d=new Date(0);d.setUTCFullYear(+m[1],+m[2]-1,+m[3]);d.setUTCHours(+(m[4]||0),+(m[5]||0),+(m[6]||0),0);return d.getTime()}
  var zero=stamp(byDay?T.zero.slice(0,10):T.zero);
  B.unit=T.unit;
  B.time=function(s){return s==null?null:byDay?Math.round((stamp(s.slice(0,10))-zero)/864e5):(stamp(s)-zero)/6e4};
  B.isoOf=function(n){var d=new Date(zero+n*(byDay?864e5:6e4)),p=function(v){return (v<10?'0':'')+v},s=d.getUTCFullYear()+'-'+p(d.getUTCMonth()+1)+'-'+p(d.getUTCDate());return byDay?s:s+'T'+p(d.getUTCHours())+':'+p(d.getUTCMinutes())};   // the other way: a number back to a date or time
  B.T0=B.time(T.start); B.T1=B.time(T.end); B.focus=T.focus?[B.time(T.focus[0]),B.time(T.focus[1])]:null;
  B.cal={first:T.calendar.first,numbered:!!T.calendar.numbered,count:T.calendar.days||0};
  B.dateOf=function(n){var d=new Date(zero+n*864e5);return {day:d.getUTCDate(),mon:MON12[d.getUTCMonth()],wd:WDN[d.getUTCDay()],year:d.getUTCFullYear()}};   // the date n days after zero
  function dayText(s){return (+s.slice(8,10))+' '+MON12[+s.slice(5,7)-1]}
  function momentText(s){if(byDay||s.length===10)return dayText(s);var c=WM.fmtClock((+s.slice(11,13))*60+(+s.slice(14,16)));return s.slice(0,10)===T.calendar.first?c:dayText(s)+', '+c}
  /* a time the record gives as [earliest, latest]; either may be unknown */
  B.rangeText=function(r){var a=r[0],b=r[1];if(a==null&&b==null)return 'unknown';if(a==null)return 'by '+momentText(b);if(b==null)return momentText(a)+' or later';return a===b?momentText(a):momentText(a)+' to '+momentText(b)};
  /* sides, units, tracks */
  B.sides={}; raw.sides.forEach(function(s){B.sides[s.id]=s});
  B.units={}; raw.units.forEach(function(u){B.units[u.id]=u});
  var BR={infantry:'inf',cavalry:'cav',artillery:'art'};
  function step(s){var loc=s.location||{},g=s.at?s.at.map(B.fromLL):null,mid=null;
    if(s.at){var n=s.at.length,i=n>>1;mid=(n%2)?s.at[i]:[(s.at[i-1][0]+s.at[i][0])/2,(s.at[i-1][1]+s.at[i][1])/2]}
    return {id:s.id,t0:B.time(s.show[0]),t1:B.time(s.show[1]),ts:B.rangeText(s.start),te:B.rangeText(s.end),open:s.end[1]==null?1:0,
      g:g,via:s.via?s.via.map(B.fromLL):null,on:s.on||null,vo:s.via_on||null,leaving:!!s.leaving,
      act:s.activity||'',place:s.place||'',say:s.quote||'',method:s.method,oc:s.confidence,tb:s.time_basis||'',
      basis:loc.basis||'',cb:loc.basis||(g?'':'No position on record'),cs:loc.source||'none',cc:loc.confidence||'',prec:loc.precision_m||null,
      pl:(loc.places||[]).map(function(p){return [p.name||'',p.today||'',p.source,p.precision_m]}),
      src:(s.sources||[]).join('; '),notes:s.notes||'',status:s.review||'',bat:s.battle||'',virtual:!!s.virtual,shared:!!s.shared,along:!!s.along,march:!!s.march,
      lat:mid?+mid[1].toFixed(5):null,lon:mid?+mid[0].toFixed(5):null}}
  B.tracks=raw.tracks.map(function(tr){var u=B.units[tr.unit],as=u.assignments||[],a0=as[0]||{};
    return {id:tr.id,unit:tr.unit,name:u.name,label:tr.label||u.label,side:B.sides[u.side].code,nation:u.nation||'',ech:tr.echelon||u.echelon,branch:BR[u.branch]||'inf',
      cmd:a0.commander||'',str:a0.strength||'',notes:u.notes||'',
      par:as.map(function(a){return [a.from?B.time(a.from):-1e9,a.to?B.time(a.to)+((!byDay&&a.to.length===10)?1439:0):1e9,a.parent||'',a.commander||'',a.strength||'']}),   // a date alone runs to the end of that day   // who it answered to, and when
      parent:tr.parent||'',hideAfter:!!tr.hide_after,hold:tr.hold_until?B.time(tr.hold_until):0,nudge:tr.nudge||null,loose:!!tr.loose,offmap:tr.off_map||'',
      k:tr.steps.map(step)}});
  B.track=function(id){for(var i=0;i<B.tracks.length;i++)if(B.tracks[i].id===id)return B.tracks[i]};
  /* events: t is the moment the timeline marks the event at */
  B.events=(raw.events||[]).map(function(e){return {id:e.id,t:B.time(e.at),t0:B.time(e.start),t1:B.time(e.end),name:e.label||e.name,full:e.name,text:e.text,quiet:!!e.quiet}});
  B.eventAt=function(t){var p=null;B.events.forEach(function(e){if(t>=e.t)p=e});return p};   // the latest event to have begun
  /* names on the map: t text, s the other name (the period's, or today's), p place, a angle, l level (0 shows first), k kind, e placed only roughly */
  B.labels=(raw.labels||[]).map(function(l){return {t:l.text,s:l.alt||'',p:B.fromLL(l.at),a:l.angle||0,l:l.level||0,k:l.kind,e:l.approximate?1:0,show:l.show||'current'}});
  /* period maps. One laid on the ground has, for each picture, its four corners (ll) and the box they span in the frame;
     one that is not to scale (own) is a picture with its own pixel grid, and steps carry positions on it (k.on[map id]). */
  B.maps={}; B.mapList=(raw.maps||[]).map(function(m){
    var v={raw:m,id:m.id,title:m.title,short:m.short||'',label:m.label||'',credit:m.credit,own:m.georeferenced===false,size:m.size||null,t0:m.from!=null?B.time(m.from):null,t1:m.to!=null?B.time(m.to):null,
      images:m.images.map(function(im){var c=im.corners||null,box=null;
        if(c){var f=c.map(B.fromLL);box=[Math.min(f[0][0],f[3][0]),Math.min(f[0][1],f[1][1]),Math.max(f[1][0],f[2][0]),Math.max(f[2][1],f[3][1])]}
        return {file:im.file,ll:c,box:box,detail:!!im.detail,reduced:im.reduced||0}})};
    var I=v.images,cut=I.length>1&&I.every(function(im){return im.box&&!im.detail});   // a map cut into pieces side by side (no piece is wider than a phone can show)
    if(cut){var b=[1e18,1e18,-1e18,-1e18];I.forEach(function(im){b=[Math.min(b[0],im.box[0]),Math.min(b[1],im.box[1]),Math.max(b[2],im.box[2]),Math.max(b[3],im.box[3])]});
      v.box=b;v.ll=[[b[0],b[1]],[b[2],b[1]],[b[2],b[3]],[b[0],b[3]]].map(B.toLL);var t=v.ll[0][1]>v.ll[3][1];if(!t)v.ll=[v.ll[3],v.ll[2],v.ll[1],v.ll[0]]}
    else if(I.length){v.box=I[0].box;v.ll=I[0].ll}
    B.maps[m.id]=v; return v});
  /* the current map's lines and areas, as lists of [longitude, latitude] */
  function unpack(s){var out=[],x=0,y=0;s.split(';').forEach(function(t,i){var a=t.split(',');x=i?x+(+a[0]):+a[0];y=i?y+(+a[1]):+a[1];out.push([x/1e5,y/1e5])});return out}
  var bs=raw.base||{};
  B.base={credit:bs.credit||'',lines:(bs.lines||[]).map(function(l){return {kind:l[0],cls:l[1],name:l[2],ll:unpack(l[3])}}),areas:(bs.areas||[]).map(function(a){return {kind:a[0],name:a[1],ll:unpack(a[2])}})};
  return B;
};

/* ---------- scale bar ---------- */
/* mPerPx: metres on the ground per screen pixel. units: 'yards' or 'km', the measure written first; the other follows under it.
   about: the map is only roughly to scale, so the lengths are marked as rough. note: a line under the bars. */
WM.scaleBar=function(el,mPerPx,units,about,note){
  var IMP=[10,25,50,100,250,500,1000,1760,3520,8800,17600,35200,88000,176000],MET=[10,20,50,100,200,500,1000,2000,5000,10000,20000,50000,100000,200000];
  function best(list,m){var pick=list[0];list.forEach(function(v){if(v*m/mPerPx<=130)pick=v});return pick}
  var y=best(IMP,0.9144),k=best(MET,1),pre=about?'about ':'';
  var imp='<div class="sb"><span>'+pre+(y>=1760?(y/1760)+(y===1760?' mile':' miles'):y+' yards')+'</span><i style="width:'+(y*0.9144/mPerPx).toFixed(0)+'px"></i></div>',
      met='<div class="sb"><span>'+pre+(k>=1000?(k/1000)+' km':k+' m')+'</span><i style="width:'+(k/mPerPx).toFixed(0)+'px"></i></div>';
  var h=(units==='km'?met+imp:imp+met)+(note?'<div class="sn">'+WM.esc(note)+'</div>':''); if(el._h!==h){el._h=h;el.innerHTML=h}};

/* ---------- the map ---------- */
function merc(ll){var s=Math.sin(ll[1]*Math.PI/180);return [(ll[0]+180)/360,0.5-Math.log((1+s)/(1-s))/(4*Math.PI)]}
function unmerc(m){return [m[0]*360-180,Math.atan(Math.sinh(Math.PI*(1-2*m[1])))*180/Math.PI]}
/* A "world" is one flat frame the battle's data is drawn in, with the way to turn its points into longitude and latitude:
   {toLL:function(p)->[lng,lat], ext:[x0,y0,x1,y1], mPerUnit:metres per unit of the frame, maxScale:most screen pixels per unit, minFactor:how far out past "the whole frame fits",
    reach:[x0,y0,x1,y1] a larger box the reader may zoom out to, where another map lies around the frame (optional)}
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
  function corners(b,w){if(Array.isArray(b[0]))return b;w=w||cur;return [w.toLL([b[0],b[1]]),w.toLL([b[2],b[1]]),w.toLL([b[2],b[3]]),w.toLL([b[0],b[3]])]}
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
  var lastChase=0;   // the chase eases by time, not by frame, so a slow machine (or a heavy period map) does not leave the units behind
  /* zrate, if given, eases the zoom at its own pace (Follow zooms more gently than it pans) */
  function chase(tg,rate,zrate){var now=performance.now(),dt=lastChase?Math.max(8,Math.min(250,now-lastChase)):16.7;lastChase=now;var k=function(r){return 1-Math.pow(1-r,dt/16.7)},pr=k(rate),zr=k(zrate||rate);
    var c=map.getCenter(),z=map.getZoom(),dz=tg.zoom-z,a=merc([c.lng,c.lat]),b=merc(tg.center),ws=TILE*Math.pow(2,z),dx=(b[0]-a[0])*ws,dy=(b[1]-a[1])*ws;
    if(Math.abs(dz)<0.004&&Math.abs(dx)<0.6&&Math.abs(dy)<0.6){map.jumpTo(tg);return false}
    map.jumpTo({center:unmerc([a[0]+(b[0]-a[0])*pr,a[1]+(b[1]-a[1])*pr]),zoom:z+dz*zr});return true}
  function limits(){var e=cur.reach||cur.ext,z=size(),c=corners(e).map(merc),x0=1e9,y0=1e9,x1=-1e9,y1=-1e9;
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
  /* A period-map picture laid on the ground: box is where it sits, either a box in the frame or its four corners as longitude and latitude. The picture is loaded as an ordinary image
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
    layer:layer,geo:geo,image:image,moveImage:moveImage,show:show,opacity:opacity,bg:bg,retheme:retheme,kick:kick,hits:hits,
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
  function icon(){document.documentElement.classList.toggle('wm-playing',playing);$('play').setAttribute('aria-label',playing?'Pause':'Play');$('playico').innerHTML=playing?'<path d="M3 1.5h3.5v13H3zM9.5 1.5H13v13H9.5z"/>':'<path d="M3 1.5v13l11-6.5z"/>'}
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
