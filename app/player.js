/* WarMapper player: the playback itself, the same for every battle.
   WM.play(battleFile) reads the battle file (core.js: WM.battle) and runs the whole page from it:
   - where each unit is at a given time (the rules are below, one set for battles followed by the clock and one for battles followed by the day);
   - which units fold into their parent when zoomed out; how symbols, lines and names are laid out and drawn;
   - the base maps and the switch between them; the controls; the timeline; the date box; the side panel.
   What differs from battle to battle is data: the battle file's "playback" section (docs/battle-file.md). No battle has code of its own. */
(function(global){
"use strict";
var WM=global.WM,EARTH=40075016.686;

/* how a recorded place was found, in words */
var FOUND={map_read:'read from a period map',sketch_read:'read from a period sketch',modern_map:'a named place on the current map',marker:'a marker at the spot',derived:'worked out from other points',estimate:'estimated from a description'};
/* what the state of a unit means: [title, explanation] */
var KIND={stated:['Placed by a source','A source puts the unit here.'],
  inferred:['Inferred position','Worked out from the sequence of events or from other units; no source states it.'],
  moving:['Moving: interpolated','No source records this stretch. The unit is drawn between two recorded positions.'],
  early:['Arrived: time inferred','No source says when the unit got here. It is shown leaving when its last record ends, moving at a march pace, and waiting here for its next record.'],
  after:['Last recorded position','The data has nothing later for this unit.'],
  unplaced:['No position recorded','The sources read so far do not say where the unit was at this time.'],
  offmap:['Off this map',''],
  offthis:['Not on this map','This position lies outside what this map shows. Switch to the current map to see it.'],
  lost:['Not followed','The sources read stop following this unit after the record below. It is taken off the map two days later.']};
var ECH={army:'XXXX',corps:'XXX',division:'XX',brigade:'X',regiment:'III',battalion:'II',battery:'I',company:'I',section:'••',squadrons:'••',detachment:'•',headquarters:''};
/* base-map line widths in screen pixels, [casing, fill], by road class: for a battlefield (tactical) and for a front (operational) */
var ROADS={tactical:{m:[5,3.6],p:[4.4,3],s:[3.8,2.5],t:[3.2,2],u:[2.8,1.7],r:[2.3,1.3],v:[1.5,0.8],_:'r'},operational:{m:[3.4,2.2],r:[2.9,1.7],s:[2.2,1.1],_:'s'}};

WM.play=function(raw){
var B=WM.battle(raw),P=raw.playback||{},Z=P.zoom||{},RU=P.rules||{};
var $=WM.$,esc=WM.esc,chip=WM.chip,lerpG=WM.lerpG,cen=WM.cen,plen=WM.plen;
var byDay=B.unit==='day',style=P.style||(byDay?'operational':'tactical'),compact=style==='operational';
var T0=B.T0,T1=B.T1;
/* BP-34: a campaign and the battles inside it link to each other (raw.links: written by the exporter from the Links sheet; a battle file
   with no links has none, and nothing below shows). A campaign lists its battles and marks their dates on the timeline; while the clock is
   on a battle's dates the pane offers to open it there. A battle offers the way back to its campaign at the date on its clock. */
var LINKS=(raw.links||[]).map(function(x){return {kind:x.kind,id:x.playback,name:x.label||x.title,from:x.from,to:x.to,at:x.at||x.from,t0:B.time(x.from),t1:B.time(x.to)}});
var LMON=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
function lday(s){return (+s.slice(8,10))+' '+LMON[+s.slice(5,7)-1]}
function lspan(x){var a=x.from.slice(0,10),b=x.to.slice(0,10),y=' '+b.slice(0,4);if(a===b)return lday(a)+y;return (a.slice(5,7)===b.slice(5,7)?(+a.slice(8,10)):lday(a))+' to '+lday(b)+y}
function linkNow(x){return x.kind==='battle'&&t>=x.t0-1e-6&&t<=x.t1+(byDay?0.999:0)}
function linkAt(x){   // where the other playback opens: the battle at its start, or at the campaign's day if later; the campaign at the battle's day
  if(x.kind==='battle'){var d=B.isoOf(Math.floor(t+1e-6)).slice(0,10)+'T00:00';return d>x.at?(d<x.to?d:x.to):x.at}
  var e=B.isoOf(t).slice(0,10);return e<x.from.slice(0,10)?x.from.slice(0,10):e>x.to.slice(0,10)?x.to.slice(0,10):e}
function openLink(id){var x=LINKS.filter(function(l){return l.id===id})[0];if(!x)return;var h=document.querySelector('a.home'),home=h?h.getAttribute('href'):'../../',
  url=home+'playbacks/'+encodeURIComponent(x.id)+'/#at='+encodeURIComponent(linkAt(x));clk.setPlaying(false);
  if(/^https?:/.test(home))window.open(url,'_blank','noopener');else location.href=url}   // from an offline copy the site opens in a new tab
function linksHtml(){if(!LINKS.length)return '';var h='',now=LINKS.filter(linkNow),bt=LINKS.filter(function(x){return x.kind==='battle'});
  LINKS.forEach(function(x){if(x.kind==='campaign')h+='<div class="cbl"><span class="eyebrow">Part of a campaign</span><button data-lnk="'+esc(x.id)+'">'+esc(x.name)+' <span class="cbs">'+esc(lspan(x))+'</span><span class="cbg">Open the campaign at this date &rarr;</span></button></div>'});
  now.forEach(function(x){h+='<div class="cbl on"><span class="eyebrow">A battle on this date</span><button data-lnk="'+esc(x.id)+'">'+esc(x.name)+' <span class="cbs">'+esc(lspan(x))+'</span><span class="cbg">Open the battle &rarr;</span></button></div>'});
  if(bt.length){h+='<details class="evs cbls"'+(lnkOpen?' open':'')+'><summary>Battles in this campaign ('+bt.length+')</summary><ul class="evl">';
    bt.forEach(function(x){h+='<li><button data-lnk="'+esc(x.id)+'"><span class="tm">'+esc(lspan(x))+'</span><span>'+esc(x.name)+'</span></button></li>'});h+='</ul></details>'}
  return h}
var lnkOpen=false;
/* BP-32: events tied to the map. An event lists the position rows it rests on (steps); the units are the tracks that carry them (and the
   formations above those, so a regiment folded into its brigade still counts). While an event is current, and for a while after its mark
   (the record's end, or 45 minutes / 2 days at least), its units and their arrows stand out and the other symbols are dimmed. Picking an
   event in the pane moves the clock to it and frames its units; a unit's details list the events that name it. Nothing new in the file. */
var EVT={},EVOF={},EVDIM=(P.event_dim!=null?P.event_dim:0.32),EVHOLD=byDay?2:45,EVEASE=600,evCur={};   // EVDIM: how faint the units not in the current event are; EVEASE: ms over which a unit fades or comes back
B.events.forEach(function(e){var m={};
  B.tracks.forEach(function(tr){if(tr.k.some(function(k){return !k.virtual&&e.steps.indexOf(k.id)>=0})){m[tr.id]=1;(EVOF[tr.id]=EVOF[tr.id]||[]).push(e.id)}});
  var own=Object.keys(m);
  own.forEach(function(id){var tr=B.track(id),n=0;while(tr&&tr.parent&&n++<6){m[tr.parent]=1;tr=B.track(tr.parent)}});   // the formations above count too
  B.tracks.forEach(function(tr){var p=tr,n=0;while(p&&p.parent&&n++<6){if(own.indexOf(p.parent)>=0){m[tr.id]=1;break}p=B.track(p.parent)}});   // and the parts below (a brigade's regiments, zoomed in)
  EVT[e.id]=m});
var EVH_OK=B.events.some(function(e){return e.steps.length}),evhOn=EVH_OK,evf=null;
function evFocus(){if(!evhOn||landing||sel)return null;var e=curEvent();if(!e||!e.steps.length||!Object.keys(EVT[e.id]).length)return null;
  return t>Math.max(e.t1==null?e.t:e.t1,e.t)+EVHOLD?null:EVT[e.id]}
function frameEvent(e){   // frame the event's own rows, wherever they are on the map now
  if(base.own||!e)return;var x0=1e18,y0=1e18,x1=-1e18,y1=-1e18;
  B.tracks.forEach(function(tr){tr.k.forEach(function(k){if(k.g&&!k.virtual&&e.steps.indexOf(k.id)>=0)k.g.forEach(function(p){x0=Math.min(x0,p[0]);y0=Math.min(y0,p[1]);x1=Math.max(x1,p[0]);y1=Math.max(y1,p[1])})})});
  if(x0>x1)return;var mn=((P.follow||{}).min)||(byDay?[30000,22000]:[900,650]),cx=(x0+x1)/2,cy=(y0+y1)/2,w=Math.max(x1-x0,mn[0]),hh=Math.max(y1-y0,mn[1]);
  setFollow(false);setPreset(null);mv.jump(mv.cameraFor([cx-w/2,cy-hh/2,cx+w/2,cy+hh/2],{t:60,b:40,l:30,r:30}))}
function setEvh(v){evhOn=v;tick('cEvh',v);remember('evh',v);mv.kick()}
var BLEND=RU.blend||4,NEAR=RU.near||15,LEAD_IN=RU.lead||0.35,LINGER=RU.linger||2,PACE=RU.pace||null;
/* march pace in metres a minute (rules.pace: one number, or one per branch). A unit moving to a step marked "march", with nothing on record
   between, leaves when the earlier record ends and moves at that pace, rather than drifting across the whole gap; it then waits there. */
function paceOf(tr){if(!PACE)return 0;if(typeof PACE==='number')return PACE;return PACE[{inf:'infantry',cav:'cavalry',art:'artillery'}[tr.branch]]||PACE.infantry||0}
var wrap=$('mapwrap'),ov=$('ov'),panel=$('panel');
var kinds={},found={},k0; for(k0 in KIND)kinds[k0]=[KIND[k0][0],(P.texts&&P.texts[k0])||KIND[k0][1]]; for(k0 in FOUND)found[k0]=(P.found&&P.found[k0])||FOUND[k0];

/* ---------- bases: the maps the reader can put under the units ---------- */
/* a base is the current map ({current:true}), one period map ({map:id}), the period map for the date on the timeline ({series:true})
   or aerial or satellite imagery from a tile service ({imagery:{tiles, credit, ...}}).
   A period map lies on plain paper (backdrop "paper") or over the current map (backdrop "current"). A map that is not to scale has a frame of its own. */
var bases=(P.bases&&P.bases.length)?P.bases:[{id:'now',label:'Current map',short:'Today',current:true}];
var series=B.mapList.filter(function(m){return m.t0!=null});
/* A reconstructed base ({recon:id}) is not a picture: the page draws it from the traced lines of one of the battle file's `reconstructions`,
   in the manner of a map of the time. It is always labelled a reconstruction: the map details (the i button) open by saying so, and every line can be
   tapped for its source, how it was read and how sure it is. It carries no banner on the map (Morgan, 22 Nov 2026). */
var RECON={};(raw.reconstructions||[]).forEach(function(r){RECON[r.id]=r});
bases.forEach(function(b){b.m=b.map?B.maps[b.map]:null;b.own=!!(b.m&&b.m.own);b.sat=!!(b.imagery&&b.imagery.tiles);b.rc=(b.recon&&RECON[b.recon])||null});
var SKK=1e-5; function ownLL(p){return [p[0]*SKK,-p[1]*SKK]}   // a not-to-scale map: its pixels laid out as a small patch of pretend ground
var bm=P.bounds&&B.maps[P.bounds],EXT=bm?bm.box:B.ext;
var WORLDS={ground:{toLL:B.toLL,ext:EXT,mPerUnit:1,maxScale:Z.max||2,minFactor:Z.min_factor||0.9}};
bases.forEach(function(b){if(b.own)WORLDS['own:'+b.map]={toLL:ownLL,ext:[0,0,b.m.size[0],b.m.size[1]],mPerUnit:SKK*EARTH/360,maxScale:3,minFactor:0.9}});
bases.forEach(function(b){ if(!(b.terrain&&b.terrain.extent&&b.rc)) return; var e=b.terrain.extent,p=B.fromLL([e[0],e[1]]),q=B.fromLL([e[2],e[3]]);   // a terrain base that runs past its sheet: the reader stays inside its extent, so the screen is always full
  WORLDS['terrain:'+b.id]={toLL:B.toLL,ext:[Math.min(p[0],q[0]),Math.min(p[1],q[1]),Math.max(p[0],q[0]),Math.max(p[1],q[1])],mPerUnit:1,maxScale:Z.max||2,cover:true}});
/* The modern map: today's topographic map from a tile service. It is the current map, it shows through a period map that is turned down,
   and it lies around a period map where that ends, so the reader can zoom out past the sheet. The battle's own drawing of today's roads
   and water (the base data) is the fall-back, shown only if the service cannot be reached. */
var MOD=(function(){var m=P.modern||P.surround;return m&&m.tiles?m:null})(),modOn=null,modFail=0,modOff=false;
function topo(){return !!MOD&&!modOff}
/* Terrain shading: shadows drawn from elevation tiles, laid over today's map and under the period maps, kept out of the muting so the
   lie of the land stays plain. Every battle gets it unless its file says hillshade:false; hillshade:{exaggeration, tiles, ...} tunes it. */
var HS=(function(){if(P.hillshade===false)return null;var h={tiles:'https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png',encoding:'terrarium',max_zoom:15,exaggeration:0.8,
  credit:'Terrain Tiles (Mapzen, AWS Open Data)',link:'https://github.com/tilezen/joerd/blob/master/docs/attribution.md'},o=P.hillshade||{};for(var k in o)h[k]=o[k];return h})(),hsOn=true,hsVis=null,hsRc=null,hsFail=0;
function paintHill(){ if(!HS) return; var ok=hsOn&&hsFail<4,on=ok&&!base.rc&&!base.sat&&!!(modOn||base.current),onr=ok&&!!base.rc&&!trnOf();   // on a reconstructed map the relief is drawn in the map's own ink
  if(on!==hsVis||onr!==hsRc){hsVis=on;hsRc=onr;mv.show('hill',on);if(mv.map.getLayer('rc-hill'))mv.show('rc-hill',onr);lastCredit=''} }
if(MOD){(function(){var f=(+MOD.reach||(bm?4:2))/2,cx=(EXT[0]+EXT[2])/2,cy=(EXT[1]+EXT[3])/2,hw=Math.abs(EXT[2]-EXT[0])*f,hh=Math.abs(EXT[3]-EXT[1])*f;var r=[cx-hw,cy-hh,cx+hw,cy+hh];
  B.mapList.forEach(function(m){if(m.own)return;m.images.forEach(function(im){var b=im.box;if(!b)return;b=[Math.min(b[0],b[2]),Math.min(b[1],b[3]),Math.max(b[0],b[2]),Math.max(b[1],b[3])];var mx=(b[2]-b[0])*0.3,my=(b[3]-b[1])*0.3;   // room to zoom out past every period map, so the modern map is seen around it
    r=[Math.min(r[0],b[0]-mx),Math.min(r[1],b[1]-my),Math.max(r[2],b[2]+mx),Math.max(r[3],b[3]+my)]})});
  WORLDS.ground.reach=r})()}
function inQuad(p,Q){var s=0,i,a,b,c;for(i=0;i<4;i++){a=Q[i];b=Q[(i+1)%4];c=(b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0]);if(c){if(s&&(c>0)!==(s>0))return false;s=c}}return true}
/* Under a period map at full strength the modern map is asked for only while some of the screen lies beyond the picture, so nothing is fetched until the reader zooms or pans out past it. */
function paintModern(H){ if(!MOD) return; var on=false;
  if(!modOff&&!base.own&&!base.sat&&!base.rc){var m=base.series?H:base.m,Q=m&&!m.own?m.ll:null,z=mv.size();
    on=!!(base.current||base.backdrop==='current'||through()||!Q||[[0,0],[z.w,0],[z.w,z.h],[0,z.h]].some(function(q){var l=mv.map.unproject(q);return !inQuad([l.lng,l.lat],Q)}))}
  if(on!==modOn){modOn=on;mv.show('sur',on);panelKey=''} }
/* The map a battle opens on: a period map if it covers all of the opening view, otherwise the current map. `start_base` overrides. */
function startBase(){ var byId=P.start_base&&bases.filter(function(b){return b.id===P.start_base})[0]; if(byId) return byId;
  var V=raw.view,bx=(P.views&&V.presets&&V.presets[P.views[0].preset])||V.extent,dx=(bx[2]-bx[0])*0.04,dy=(bx[3]-bx[1])*0.04,C=[[bx[0]+dx,bx[1]+dy],[bx[2]-dx,bx[1]+dy],[bx[2]-dx,bx[3]-dy],[bx[0]+dx,bx[3]-dy]];
  var per=bases.filter(function(b){return b.m&&!b.own&&!b.series&&C.every(function(c){return inQuad(c,b.m.ll)})})[0];
  return per||bases.filter(function(b){return b.current})[0]||bases[0]}
function worldOf(b){return b.own?'own:'+b.map:(WORLDS['terrain:'+b.id]?'terrain:'+b.id:'ground')}

/* ---------- state ---------- */
var base=bases[0],landing=true,t=T0,sel=null,follow=!!P.follow,names=true,unitsOn=true,foldOn=true,sNow=0.1,preset=null,goal=null,S,mv,clk;
var placeNames=true,lineNames=true,narrOn=false,symbols='standard',seenFrom='',opac=1,info=false,stepI=0,wheelAcc=0;   // the Layers menu's choices, the map-details view, the time step
function gkey(){return base.own?base.map:'g'}
function geo(k,key){return key==='g'?k.g:((k.on&&k.on[key])||null)}

/* ---------- sides and nations ---------- */
var NAT={},byNation=false; (raw.nations||[]).forEach(function(n){NAT[n.name]=n;if(n.colour)byNation=true});
var SIDES={}; raw.sides.forEach(function(s){SIDES[s.code]=s});
(function(){ // a nation with a colour of its own (First Ypres has four) gets style variables made from the battle file
  var l='',d='',p=''; (raw.nations||[]).forEach(function(n){if(!n.colour)return;l+='--n-'+n.code+':'+n.colour+';';if(n.dark)d+='--n-'+n.code+':'+n.dark+';';p+='--n-'+n.code+':'+(n.paper||n.colour)+';'});
  if(!l)return; var st=document.createElement('style');
  st.textContent=':root{'+l+'}@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){'+d+'}}:root[data-theme="dark"]{'+d+'}.mapwrap.paper{'+p+'}';document.head.appendChild(st)})();
function look(tr){var s=SIDES[tr.side]||{colour:'blue',short:''},n=NAT[tr.nation],c=s.colour==='red'?'red':'blue';
  return {col:(n&&n.colour)?'var(--n-'+n.code+')':'var(--m-'+c+')',fill:'var(--m-'+c+'-fill)',ui:(n&&n.colour)?'var(--n-'+n.code+')':'var(--ui-'+c+')',
          name:(n&&n.short)||s.short,group:byNation?(n?n.name:tr.side):tr.side}}

/* ---------- where is a unit at time t ---------- */
function alongP(path,f){return WM.along(path,f).p}
function prevGeo(ks,i,key){for(var j=i-1;j>=0;j--){var g=geo(ks[j],key);if(g)return g}return null}
function noPlace(k,key){return (key!=='g'&&k.g)?'offthis':'unplaced'}   // on a map of its own, a unit placed on the ground but not on that map
function placed(k){return k.method==='inferred'?'inferred':'stated'}
function move(a,b,f,key){ // from step a to step b: along the route the record gives (via) if it has one, else straight
  var V=key==='g'?b.via:(b.vo&&b.vo[key]),G=geo(b,key),ga=geo(a,key);   // a picture not to scale may carry the route in its own pixels (vo)
  if(V&&V.length>1&&G){
    if(ga){var c0=cen(ga);if(Math.hypot(c0[0]-V[0][0],c0[1]-V[0][1])>1)V=[c0].concat(V)}   // the route may begin a little way off: the unit walks to it, it does not jump
    if(f>0.92&&G.length>1){return lerpG([alongP(V,1)],G,(f-0.92)/0.08)}   // at the route's end it opens out into its line (from the end, not back along the route)
    return [alongP(V,Math.min(f/0.92,1))]; }
  return lerpG(geo(a,key),geo(b,key),f)}
/* A battle followed by the clock. A unit stands at a step's place for the step's time; between two steps it moves; where one step
   ends as the next begins it shifts over the last few minutes; after its last step it stays, faded, unless the record says it left. */
function stateClock(tr,tt,key){
  var ks=tr.k,n=ks.length; if(tt<ks[0].t0) return null;
  if(tr.offmap) return (tt<=ks[n-1].t1)?{k:ks[0],g:null,kind:'offmap'}:null;
  for(var i=0;i<n;i++){
    var k=ks[i],nx=ks[i+1],end=k.t1,g=geo(k,key),gn=nx?geo(nx,key):null; if(i===n-1&&tr.hold) end=Math.max(end,tr.hold);
    if(tt>=k.t0&&tt<=end){
      if(k.virtual) return nx?{k:k,g:g,kind:'moving',from:k,hid:true}:null;   // a stand-in start: nothing is drawn until the unit sets off
      if(!g){var u=noPlace(k,key);return {k:k,g:u==='unplaced'?prevGeo(ks,i,key):null,kind:u}}
      if(k.along) return {k:k,g:[alongP(g,(tt-k.t0)/Math.max(1,k.t1-k.t0))],kind:'stated'};   // the step's line is the path the unit takes during it
      if(nx&&gn&&nx.t0-end<0.01&&!nx.via){var M=Math.min(BLEND,(end-k.t0)/2); if(M>0&&tt>end-M) return {k:nx,from:k,g:lerpG(g,gn,(tt-(end-M))/M),kind:'moving'}}
      return {k:k,g:g,kind:placed(k)};
    }
    if(nx&&tt>end&&tt<nx.t0){
      if(g&&gn){ var ca=cen(g),cb=cen(gn),dd=Math.hypot(ca[0]-cb[0],ca[1]-cb[1]),arr=nx.t0,pc=(key==='g'&&!nx.via&&nx.march)?paceOf(tr):0;
        if(!nx.via&&dd<(key==='g'?NEAR:8)) return {k:nx,g:gn,kind:placed(nx)};   // hardly any distance: no march is drawn
        if(pc&&end+Math.max(3,dd/pc)<arr){arr=end+Math.max(3,dd/pc);if(tt>=arr)return {k:nx,from:k,g:gn,kind:'early'}}   // there at march pace, then waits
        return {k:nx,from:k,g:move(k,nx,(tt-end)/(arr-end),key),kind:'moving'}; }
      if(g) return {k:nx,g:noPlace(nx,key)==='unplaced'?g:null,kind:noPlace(nx,key)};
      return {k:k,g:null,kind:noPlace(k,key)};
    }
  }
  if(tr.hideAfter) return null;
  var last=ks[n-1],gl=geo(last,key); if(gl) return {k:last,g:gl,kind:'after'};
  var un=noPlace(last,key); return {k:last,g:un==='unplaced'?prevGeo(ks,n-1,key):null,kind:un};
}
/* A battle followed by the day. The sources give a position at nightfall, so a step runs from the evening of its first date to the evening
   of its last, and the move to the next takes the day before it. Where the record gives the route between two steps (a march of several
   days, a voyage), the move takes the whole time between them and follows the route. A unit the sources stop following stays, faded, for two days, then leaves the map. */
function ease(f){return f<0?0:f>1?1:f*f*(3-2*f)}
function resample(g,n){if(g.length===1){var o=[];for(var i=0;i<n;i++)o.push(g[0]);return o}
  var L=plen(g),out=[g[0]],seg=1,acc=0;if(L<1){for(var j=1;j<n;j++)out.push(g[0]);return out}
  for(var k=1;k<n-1;k++){var want=L*k/(n-1);
    while(seg<g.length){var d=Math.hypot(g[seg][0]-g[seg-1][0],g[seg][1]-g[seg-1][1]);if(acc+d>=want){var f=d?(want-acc)/d:0;out.push([g[seg-1][0]+(g[seg][0]-g[seg-1][0])*f,g[seg-1][1]+(g[seg][1]-g[seg-1][1])*f]);break}acc+=d;seg++}}
  out.push(g[g.length-1]);return out}
function morph(a,b,f){ if(a.length===1&&b.length===1) return [[a[0][0]+(b[0][0]-a[0][0])*f,a[0][1]+(b[0][1]-a[0][1])*f]];
  var n=9,A=resample(a,n),C=resample(b,n);
  var d1=Math.hypot(A[0][0]-C[0][0],A[0][1]-C[0][1])+Math.hypot(A[n-1][0]-C[n-1][0],A[n-1][1]-C[n-1][1]),d2=Math.hypot(A[0][0]-C[n-1][0],A[0][1]-C[n-1][1])+Math.hypot(A[n-1][0]-C[0][0],A[n-1][1]-C[0][1]);
  if(d2<d1) C.reverse(); var o=[];for(var i=0;i<n;i++)o.push([A[i][0]+(C[i][0]-A[i][0])*f,A[i][1]+(C[i][1]-A[i][1])*f]);return o}
function stateDaily(tr,tt,key){
  var ks=tr.k,n=ks.length; if(tt<ks[0].t0-LEAD_IN) return null;
  for(var i=0;i<n;i++){
    var k=ks[i],nx=ks[i+1],s=k.t0-LEAD_IN,e=k.t1,g=geo(k,key),gn=nx?geo(nx,key):null;
    if(tt>=s&&tt<=e) return {k:k,g:g,kind:!g?noPlace(k,key):k.virtual?'moving':placed(k)};   // a stand-in start (an approach not recorded) is drawn dashed
    if(nx&&tt>e&&tt<nx.t0-LEAD_IN){
      var V=key==='g'?nx.via:(nx.vo&&nx.vo[key]);
      if(V&&V.length>1&&g&&gn){var fr=(tt-e)/Math.max(0.01,nx.t0-LEAD_IN-e);   // the record gives the route (a march of days, a voyage): the move takes the whole gap, along it
        return {k:nx,from:k,g:(g.length===1&&gn.length===1)?[alongP(V,fr)]:morph(g,gn,fr),kind:'moving'}}
      var ms=Math.max(e,nx.t0-1-LEAD_IN),me=nx.t0-LEAD_IN;   // no route: the move takes a whole day, ending as the next record comes in
      if(tt<ms) return (g&&tt<=e+LINGER)?{k:k,g:g,kind:'after'}:{k:k,g:null,kind:g?'lost':noPlace(k,key)};
      if(g&&gn) return {k:nx,from:k,g:morph(g,gn,ease((tt-ms)/Math.max(0.01,me-ms))),kind:'moving'};
      if(g) return {k:k,g:g,kind:'after'};
      return {k:nx,g:null,kind:noPlace(nx,key)};
    }
  }
  var last=ks[n-1],gl=geo(last,key); if(!gl) return {k:last,g:null,kind:noPlace(last,key)};
  return tt<=last.t1+LINGER?{k:last,g:gl,kind:'after',fade:1-0.85*(tt-last.t1)/LINGER}:{k:last,g:null,kind:'lost'};   // it fades over the hold, then leaves the map
}
var stateAt=byDay?stateDaily:stateClock;
function stamp(tt){return byDay?Math.ceil(tt-1e-6):tt}   // the day a moment belongs to
function parentAt(tr,tt){var p=null,d=stamp(tt);tr.par.forEach(function(a){if(d>=a[0]&&d<=a[1])p=a});return p||tr.par[tr.par.length-1]||null}   // who the unit answered to then: [from, to, parent, commander, strength]
/* Everything on the map at this moment. Two ways a unit folds into its parent when the reader zooms out:
   a track that is part of another (a regiment's stretch of its brigade's line) is drawn in its place when zoomed in, and not at all otherwise;
   where the battle asks for it (playback.fold.formation), a unit whose parent formation has a line of its own on the map is hidden while zoomed out. */
function scene(){
  var key=gkey(),out=[],by={},kids=foldOn&&Z.fold&&sNow>=Z.fold,F=P.fold||{};
  B.tracks.forEach(function(tr){var s=stateAt(tr,t,key);if(s&&!s.hid){var o={tr:tr,s:s,drawn:!!s.g,hidden:false};out.push(o);by[tr.id]=o}});
  out.forEach(function(o){var tr=o.tr; if(!tr.parent) return;
    if(!kids||!o.s.g){o.drawn=false;o.hidden=true} else if(by[tr.parent]){by[tr.parent].drawn=false;by[tr.parent].hidden=true}});
  if(F.formation&&Z.fold&&sNow<Z.fold) out.forEach(function(o){var tr=o.tr; if(!o.drawn||tr.parent||tr.id===sel||(F.sides&&F.sides.indexOf(tr.side)<0)) return;
    var p=parentAt(tr,t),q=p&&by[p[2]]; if(q&&q.s.g&&!q.hidden){o.drawn=false;o.folded=p[2]}});
  return out;
}

/* ---------- view ---------- */
/* What the Follow camera frames: every unit on the map now, and every unit that will be on it within the look-ahead
   (playback.follow.lookahead, minutes), so a column still far off is in view before it arrives and the camera closes in as the forces meet. */
function actionBox(){var key=gkey(),F=P.follow||{},ex=F.exclude||[],b=[1e9,1e9,-1e9,-1e9],any=false,la=byDay?0:(F.lookahead!=null?F.lookahead:30),when=la?[0,0.2,0.4,0.6,0.8,1].map(function(f){return Math.min(T1,t+la*f)}):[t];
  var su=F.side_from||{};   // a side left out of the frame until a time (Trenton: the garrison sits still all night while the army crosses)
  B.tracks.forEach(function(tr){if(tr.parent||tr.loose||ex.indexOf(tr.id)>=0)return;if(su[tr.side]&&t<B.time(su[tr.side]))return;when.forEach(function(tt){if(tt>=leaveAt(tr))return;var s=stateAt(tr,tt,key);if(!s||!s.g||s.hid)return;any=true;
    s.g.forEach(function(p){b[0]=Math.min(b[0],p[0]);b[1]=Math.min(b[1],p[1]);b[2]=Math.max(b[2],p[0]);b[3]=Math.max(b[3],p[1])})})});
  if(!any) return base.own?[0,0,base.m.size[0]*0.75,base.m.size[1]]:((F.empty&&B.presets[F.empty])||EXT);
  var mn=base.own?[520,400]:(F.min||[1400,900]),mg=base.own?70:(F.margin||140);
  var mx=Math.max(mg,(mn[0]-(b[2]-b[0]))/2),my=Math.max(mg,(mn[1]-(b[3]-b[1]))/2);
  return [b[0]-mx,b[1]-my,b[2]+mx,b[3]+my]}
/* A unit that gets away (a route of kind escape) leaves the Follow frame when it sets off, so the camera stays on the fight
   and lets it go off the screen. */
function leaveAt(tr){if(tr._leave===undefined){tr._leave=1e12;for(var i=1;i<tr.k.length;i++)if(tr.k[i].leaving){tr._leave=tr.k[i-1].t1;break}}return tr._leave}
/* Where the action is. If two opposing units are close enough to be in contact, it is where they meet (the closest pairs, averaged);
   otherwise it is where units are on the move; otherwise the middle of everything on the map. */
function focusPoint(){var key=gkey(),F=P.follow||{},ex=F.exclude||[],U=[],mov=[];
  B.tracks.forEach(function(tr){if(tr.parent||ex.indexOf(tr.id)>=0||t>=leaveAt(tr))return;var s=stateAt(tr,t,key);if(!s||!s.g||s.hid)return;
    var c=cen(s.g);U.push({side:tr.side,c:c,pts:s.g.length>1?s.g.concat([c]):[c]});if(s.kind==='moving')mov.push(c)});
  if(!U.length) return null;
  var lim=base.own?260:(F.contact||(compact?5000:800)),best=1e18,pairs=[];   // how close counts as contact: metres on the ground
  for(var i=0;i<U.length;i++)for(var j=i+1;j<U.length;j++){if(U[i].side===U[j].side)continue;var d=1e18,m=null;
    U[i].pts.forEach(function(a){U[j].pts.forEach(function(b){var q=Math.hypot(a[0]-b[0],a[1]-b[1]);if(q<d){d=q;m=[(a[0]+b[0])/2,(a[1]+b[1])/2]}})});
    pairs.push([d,m]);if(d<best)best=d}
  if(best<=lim) return cen(pairs.filter(function(q){return q[0]<=Math.max(best*1.5,best+lim*0.2)}).map(function(q){return q[1]}));
  return cen(mov.length?mov:U.map(function(u){return u.c}))}
/* The Follow camera. At its widest it frames every unit. Zoomed in from there with + (followK above 1) it cannot show them all,
   so it centres on where the action is and keeps doing so as time moves. */
var FOL={rate:(P.follow&&P.follow.ease)||0.035,zoom_rate:0.02,pause_ms:((P.follow&&P.follow.pause_seconds!=null)?P.follow.pause_seconds:4)*1000,glide_rate:0.03,glide_ms:(P.follow&&P.follow.glide_seconds!=null?P.follow.glide_seconds:6)*1000};
var followK=1,glide=0;   // glide: until when (ms) the camera eases in slowly, after play is first pressed
/* The Follow camera must not pulse. It zooms out as soon as the units need more room, but zooms in only when a view at least
   ZIN_MIN closer has been wanted for ZIN_WAIT ms; small wishes to come closer are ignored. Pans and zooms ease over about a second. */
var ZIN_MIN=0.3,ZIN_WAIT=1500,zinSince=0;
function calmTarget(){var tg=target(),z=mv.map.getZoom(),now=Date.now();
  if(tg.zoom>z){if(tg.zoom-z<ZIN_MIN){zinSince=0;tg.zoom=z}else{if(!zinSince)zinSince=now;if(now-zinSince<ZIN_WAIT)tg.zoom=z}}else zinSince=0;
  return tg}
function target(){var n=mv.size().w<520?36:56,W=WORLDS[worldOf(base)],cam=mv.cameraFor(actionBox(),{t:n+34,b:n+26,l:n,r:n},followMax());
  if(followK!==1){cam.zoom=Math.min(cam.zoom+Math.log2(followK),mv.zoomFor(W.maxScale));
    if(followK>1){var f=focusPoint();if(f)cam.center=W.toLL(f)}}
  return cam}
/* Dragging or zooming the map by hand no longer switches Follow off for good: Follow waits while the reader moves the map
   (FOL.pause_ms after the last touch), then carries on from there, keeping the reader's zoom as a tighter or wider Follow view.
   Only the Follow button, Fit, 1:1 or a link to a view switch it off. */
var fpause=0;
/* Skips (playback.skip): a long stretch where little happens is shown for a moment, then the clock jumps to its end
   (Trenton: the crossing begins at 18:00; two seconds later the army is over the river). Moving the clock by hand is not affected. */
var SKIP=(function(x){x=x?(Array.isArray(x)?x:Object.keys(x).sort().map(function(k){return x[k]})):[];return x.map(function(s){return {a:B.time(s.from),b:B.time(s.to),ms:(s.after_seconds!=null?s.after_seconds:2)*1000,note:s.note||''}})})(P.skip),skipAcc=0,skipTs=0;
function doSkip(ts){if(!clk.playing||!SKIP.length){skipTs=0;return}var dt=skipTs?Math.min(100,ts-skipTs):0;skipTs=ts;
  var s=SKIP.filter(function(x){return t>=x.a&&t<x.b})[0];if(!s){skipAcc=0;return}skipAcc+=dt;if(skipAcc>=s.ms){skipAcc=0;lastW=null;clk.setTime(s.b);if(s.note)toast(s.note)}}
function toast(msg){var e=document.createElement('div');e.className='toast';e.textContent=msg;wrap.appendChild(e);setTimeout(function(){e.classList.add('off')},3200);setTimeout(function(){e.remove()},3800)}
/* How close Follow may come: on a fitted period map with no detail to stream, no closer than about 2.5 screen pixels to a pixel of the picture,
   so the 1777 map is not blown up into a blur. */
function followMax(){if(base.own)return 1.3;var mx=Z.follow_max||Z.max||2,m=base.m&&!base.current&&!base.sat?base.m:null,f=m&&m.raw&&m.raw.fit,mpp=f&&(f.m_per_px||f.metres_per_pixel);
  if(mpp&&!(m.raw.iiif))mx=Math.min(mx,2.5/mpp);return mx}
function pauseFollow(){fpause=Date.now()+FOL.pause_ms;mv.kick()}
function resumeFollow(){var W=WORLDS[worldOf(base)],n=mv.size().w<520?36:56,fit=mv.cameraFor(actionBox(),{t:n+34,b:n+26,l:n,r:n},followMax());
  followK=Math.max(0.35,Math.min(Math.pow(2,mv.map.getZoom()-fit.zoom),Math.pow(2,mv.zoomFor(W.maxScale)-fit.zoom)));if(Math.abs(followK-1)<0.15)followK=1}
function zoomStep(f){ // the + and - buttons: while Follow is on they tighten or widen the Follow camera, which stays on the action
  if(follow&&P.follow){var W=WORLDS[worldOf(base)],n=mv.size().w<520?36:56,fit=mv.cameraFor(actionBox(),{t:n+34,b:n+26,l:n,r:n},followMax());
    followK=Math.max(0.35,Math.min(followK*f,Math.pow(2,mv.zoomFor(W.maxScale)-fit.zoom)));if(Math.abs(followK-1)<0.05)followK=1;mv.kick();return}
  setPreset(null);mv.zoomBy(f)}
function cameraOf(p){return mv.cameraFor(B.presets[p],{t:48,b:22,l:14,r:14})}
/* The opening view (Morgan, 24 Nov 2026: every battle opens zoomed out, so the reader sees the ground around it): before play, the
   page stands playback.opening_zoom_out zoom levels wider than the battle's first view (1 by default: twice as wide), then eases in. */
var OPEN_OUT=P.opening_zoom_out!=null?+P.opening_zoom_out:1,goalK=0.2;
function wide(c){return (landing&&OPEN_OUT&&!base.own)?{center:c.center,zoom:Math.max(mv.map.getMinZoom(),c.zoom-OPEN_OUT)}:c}   // not on a picture not drawn to scale: there is no ground around it
function home(){return wide(preset?cameraOf(preset):((follow&&!landing)?target():mv.cameraFor(base.own?WORLDS[worldOf(base)].ext:EXT,{t:48,b:22,l:14,r:14})))}
function press(id,v){var e=$(id);if(e)e.setAttribute('aria-pressed',v?'true':'false')}
function setFollow(v){if(v&&!follow)followK=1;fpause=0;follow=v;press('bFollow',v);if(v)mv.kick()}   // switched on again, Follow starts from its widest view
function setPreset(p,jump){preset=p;(P.views||[]).forEach(function(v){press('v-'+v.preset,p===v.preset)});
  if(!p){goal=null;return} goal=cameraOf(p); if(jump){mv.jump(goal);goal=null} mv.kick()}
function remember(k,v){try{localStorage.setItem('wm.'+B.id+'.'+k,v?'1':'0')}catch(_){ }}
function tick(id,v){var e=$(id);if(e)e.checked=v}
function setNames(v){names=v;tick('cNames',v);remember('names',v);mv.kick()}
function setUnits(v){unitsOn=v;tick('cUnits',v);mv.kick()}
function setFold(v){foldOn=v;tick('cFold',v);mv.kick()}
function setNarr(v){narrOn=v;tick('cNarr',v);remember('narr',v);wrap.classList.toggle('narr-on',v);paintNarr()}
function setSymbols(v){symbols=v;press('sy-standard',v==='standard');press('sy-period',v==='period');mv.kick()}
function setSeenFrom(c){seenFrom=c||'';press('fr-none',!seenFrom);raw.sides.forEach(function(sd){press('fr-'+sd.code,seenFrom===sd.code)});mv.kick()}

/* ---------- drawing ---------- */
function rank(tr){ // which names are kept when the map is crowded: 1 first
  if(tr.id===sel) return 0;
  if(tr.loose||tr.ech==='detachment'||tr.ech==='section') return 4;
  if(tr.parent||tr.branch==='art') return 3;
  if(compact) return (tr.ech==='corps'||tr.ech==='army')?1:tr.ech==='division'?2:3;
  return (tr.ech==='regiment'||tr.ech==='brigade')?1:2}
/* Breakouts: when, during play, a higher unit divides into the units under it (the army into its divisions, a division into its
   brigades at the end of formations.until, a corps unfolding when zoomed in), the new symbols spread out from where the higher unit
   stood over BRK_MS, and the clock waits for them. Two or more new units from the same parent make a breakout; a seek does not.
   Merges are the reverse: when, during play, units come to the end of their records while a higher unit of theirs is on the map
   (regiments whose positions stop, their brigade going on), they slide into that unit's symbol over BRK_MS instead of vanishing. */
var BRK_MS=2500,brk={},mrg={},lastW=null,lastT=null,holdUntil=0;
function parentsOf(uid){var out=[],d=stamp(t),seen=0;while(uid&&seen++<6){var u=B.units[uid];if(!u)break;var as=u.assignments||[],a=null;
    as.forEach(function(x){var f=x.from?B.time(x.from):-1e9,e=x.to?B.time(x.to)+((!byDay&&x.to.length===10)?1439:0):1e9;if(d>=f&&d<=e)a=x});
    a=a||as[as.length-1];if(!a||!a.parent)break;out.push(a.parent);uid=a.parent}return out}
/* where a higher unit stands now even while its own symbol is not drawn (its other regiments are still shown in its place) */
function hiddenAt(uid){var tr=null;B.tracks.forEach(function(x){if(x.unit===uid&&!tr)tr=x});if(!tr)return null;var st=stateAt(tr,t,gkey());if(!st||!st.g||!st.g.length)return null;
  var x=0,y=0;st.g.forEach(function(p){var q=S(p);x+=q[0];y+=q[1]});var ll=mv.map.unproject([x/st.g.length,y/st.g.length]);return [ll.lng,ll.lat]}
function zoomSig(){return [FM&&(fmForced()||(fmOn&&!base.own&&sNow<FM.below)),sNow<(Z.fold||0)].concat((P.groups||[]).map(function(G){return sNow<G.below})).join()}
function breakouts(L){var now=Date.now(),W={},inv=function(q){return mv.map.unproject(q)},sig=zoomSig(),ok=clk&&clk.playing&&lastW&&lastT!=null&&t>=lastT&&t-lastT<(byDay?2:30)&&lastW.sig===sig,born={};
  L.forEach(function(u){var tr=u.o.tr;if(!tr.id||u.noSym)return;var ll=inv([u.c[0],u.c[1]]);W[tr.unit]=W[tr.unit]||[ll.lng,ll.lat];
    if(ok&&!lastW.ids[tr.id]&&!brk[tr.id]){var ps=parentsOf(tr.unit);for(var i=0;i<ps.length;i++){if(lastW.pos[ps[i]]){(born[ps[i]]=born[ps[i]]||[]).push(tr.id);break}}}});
  Object.keys(born).forEach(function(p){if(born[p].length<2)return;born[p].forEach(function(id){brk[id]={from:lastW.pos[p],t0:now}});holdUntil=now+BRK_MS});
  L.forEach(function(u){var tr=u.o.tr,b=tr.id&&brk[tr.id];if(!b)return;var f=(now-b.t0)/BRK_MS;if(f>=1){delete brk[tr.id];return}
    var e=1-Math.pow(1-f,3),q=mv.map.project(b.from),dx=(q.x-u.c[0])*(1-e),dy=(q.y-u.c[1])*(1-e);u.x+=dx;u.y+=dy;u.pts=u.pts.map(function(p){return [p[0]+dx,p[1]+dy]});mv.kick()});
  var ids={},items={};L.forEach(function(u){if(u.o.tr.id&&!u.noSym&&!u.ghost){ids[u.o.tr.id]=1;items[u.o.tr.id]={u:u,c:inv([u.c[0],u.c[1]]),pts:u.pts.map(function(q){return inv(q)})}}});
  if(ok)Object.keys(lastW.ids).forEach(function(id){if(ids[id]||mrg[id]||!lastW.items[id])return;var it=lastW.items[id],ps=parentsOf(it.u.o.tr.unit);
    for(var i=0;i<ps.length;i++){var at=W[ps[i]]||hiddenAt(ps[i]);if(at){mrg[id]={it:it,to:ps[i],at:at,t0:now};holdUntil=now+BRK_MS;break}}});
  Object.keys(mrg).forEach(function(id){var m=mrg[id],f=(now-m.t0)/BRK_MS;if(f>=1||ids[id]){delete mrg[id];return}
    var e=f*f*(3-2*f),to=mv.map.project(W[m.to]||m.at||m.it.c),a=mv.map.project(m.it.c),cx=a.x+(to.x-a.x)*e,cy=a.y+(to.y-a.y)*e,u=m.it.u,g={};
    for(var k in u)g[k]=u[k];g.ghost=true;g.fade=1-0.7*e;g.lab=null;g.c=[cx,cy];g.x=cx+(u.x-u.c[0]);g.y=cy+(u.y-u.c[1]);
    g.pts=m.it.pts.map(function(q){var p=mv.map.project(q);return [p.x+cx-a.x,p.y+cy-a.y]});L.push(g);mv.kick()});
  lastW={pos:W,ids:ids,items:items,sig:sig};lastT=t}
function layout(sc){
  var L=[],Zs=mv.size(),rear=(P.rear&&!base.own)?S(B.fromLL(P.rear.at)):null,ag={},FOES=[],reach=(compact?8000:2500)*(base.own?0.5:sNow);   // how far off an enemy still decides which way a line faces (screen px)
  sc.forEach(function(o){if(o.s.g&&!o.hidden)o.s.g.forEach(function(p){FOES.push([o.tr.side,S(p)])})});
  function nearFoe(side,c){var b=null,bd=reach;FOES.forEach(function(f){if(f[0]===side)return;var d=Math.hypot(f[1][0]-c[0],f[1][1]-c[1]);if(d<bd){bd=d;b=f[1]}});return b}
  sc.forEach(function(o){ if(!o.drawn) return; var tr=o.tr;
    for(var gi=0;gi<(P.groups||[]).length;gi++){var G=P.groups[gi]; // zoomed right out, a group of units is one symbol
      if(!base.own&&sNow<G.below&&tr.side===G.side&&(G.except||[]).indexOf(tr.id)<0){(ag[gi]=ag[gi]||[]).push(S(cen(o.s.g)));return}}
    var pts=o.s.g.map(S),len=plen(pts),m=WM.along(pts,0.5),c=m.p,nx=tr.nudge?tr.nudge[0]:0,ny=tr.nudge?tr.nudge[1]:0,x=c[0]+nx,y=c[1]+ny;
    if(len>7){var px=-m.v[1],py=m.v[0],foe=nearFoe(tr.side,c); // the symbol sits behind its line: on the side away from the nearest enemy,
      if(foe){if(px*(foe[0]-c[0])+py*(foe[1]-c[1])>0){px=-px;py=-py}x+=px*21;y+=py*17}   // else where the battle says the rear lies, else to the east
      else if(rear){var dot=px*(rear[0]-c[0])+py*(rear[1]-c[1]);if((dot<0)===(tr.side===P.rear.side)){px=-px;py=-py}x+=px*21;y+=py*17}
      else{if(px<0){px=-px;py=-py}x+=px*20;y+=py*13}}
    var conf=(P.question_mark==='location'&&o.s.k.cc)||o.s.k.oc,low=(conf==='low'&&o.s.kind!=='moving'),txt=tr.label+((low&&!compact)?' ?':'');
    L.push({o:o,pts:pts,len:len,c:c,x:x,y:y,low:low,txt:txt,w:txt.length*(compact?6.7:7.1)+6,pr:rank(tr),nudged:!!(nx||ny),line:len>7})});
  if(FM&&(fmForced()||(fmOn&&!base.own&&sNow<FM.below))){ var F={};
    L.forEach(function(u){var tr=u.o.tr;if(!tr.id||tr.parent||tr.id===sel)return;var me=B.units[tr.unit],f=isFormation(me)?me:formationOf(tr.unit);if(!f||f.side==null)return;(F[f.id]=F[f.id]||{f:f,u:[]}).u.push(u)});
    Object.keys(F).forEach(function(id){var g=F[id],n=g.u.length,x=0,y=0,cx=0,cy=0,mov=0,tr0=g.u[0].o.tr; if(n<(FM.min_units||1)) return;
      var own=null;g.u.forEach(function(u){u.noSym=true;x+=u.x;y+=u.y;cx+=u.c[0];cy+=u.c[1];if(u.o.s.kind==='moving')mov++;if(u.o.tr.unit===id)own=u});
      if(own){x=own.x*n;y=own.y*n;cx=own.c[0]*n;cy=own.c[1]*n;tr0=own.o.tr}   // the formation's own symbol, where it has a track, places the group
      var lab=g.f.label||g.f.name,tr={id:'F:'+id,unit:id,label:lab,side:tr0.side,nation:tr0.nation,ech:String(g.f.echelon||FM.echelon||'division').toLowerCase(),branch:tr0.branch,parent:'',formation:true};
      L.push({o:{tr:tr,s:{kind:mov===n?'moving':'stated',k:{oc:'high'}}},pts:[[cx/n,cy/n]],len:0,c:[cx/n,cy/n],x:x/n,y:y/n,low:false,txt:lab,w:lab.length*7.1+6,pr:0,nudged:false,line:false,kids:g.u.map(function(u){return u.o.tr.id})})});
    L=L.filter(function(u){return !u.noSym||u.line}); }   // a gathered unit keeps only its line
  breakouts(L);
  Object.keys(ag).forEach(function(gi){var G=P.groups[gi],gc=cen(ag[gi]);
    L.push({o:{tr:{id:'',label:G.label,side:G.side,nation:'',ech:G.echelon||'brigade',branch:G.branch||'inf'},s:{kind:'stated',k:{oc:'high'}}},pts:[gc],len:0,c:gc,x:gc[0],y:gc[1],low:false,txt:G.label,w:G.label.length*7.1+6,pr:1,nudged:false,line:false})});
  L.sort(function(a,b){return a.pr-b.pr});
  // spread symbols that land on the same spot
  for(var i=0;i<L.length;i++)for(var pass=0;pass<4;pass++){var moved=false;for(var j=0;j<i;j++){var a=L[i],b=L[j];if(a.noSym||b.noSym||a.ghost||b.ghost)continue;if(Math.abs(a.x-b.x)<27&&Math.abs(a.y-b.y)<21){var sx=a.x>=b.x?1:-1,sy=a.y>=b.y?1:-1;if(Math.abs(a.x-b.x)>Math.abs(a.y-b.y))a.x=b.x+sx*28;else a.y=b.y+sy*22;a.nudged=true;moved=true}}if(!moved)break}
  var R=[]; function hit(r){for(var i=0;i<R.length;i++){var q=R[i];if(r[0]<q[2]&&r[2]>q[0]&&r[1]<q[3]&&r[3]>q[1])return true}return false}
  L.forEach(function(u){if(!u.noSym)R.push([u.x-14,u.y-19,u.x+14,u.y+10]);
    if(!compact) for(var i=1;i<u.pts.length&&u.line;i++){var a=u.pts[i-1],b=u.pts[i],d=Math.hypot(b[0]-a[0],b[1]-a[1]),n=Math.max(1,Math.round(d/11));
      for(var j=0;j<=n;j++){var qx=a[0]+(b[0]-a[0])*j/n,qy=a[1]+(b[1]-a[1])*j/n;R.push([qx-4,qy-4,qx+4,qy+4])}}});
  // names, most important units first; a crowded name is dropped (the unit stays tappable)
  var phoneW=wrap.clientWidth<=560,force=!phoneW&&!compact&&sNow>=(Z.force_names_from||0);
  var fewer=phoneW&&sNow<(Z.phone_names||(compact?(Z.full_names||1e9):0.6));   // phones, zoomed out: no names for small parts (artillery, detachments, sub-units) until zoomed in
  L.forEach(function(u){
    u.lab=null; if(u.ghost||u.noSym||(!names&&!(sel&&u.o.tr.id===sel))) return; if(fewer&&u.pr>=3) return;
    var x=u.x,y=u.y,w=u.w,C=[[x+16,y-8,x+16+w,y+8,'start',x+17,y+4.5],[x-16-w,y-8,x-16,y+8,'end',x-17,y+4.5],[x-w/2,y+11,x+w/2,y+26,'middle',x,y+23],[x-w/2,y-35,x+w/2,y-20,'middle',x,y-23]];
    for(var i=0;i<C.length;i++){ if(C[i][0]>=3&&C[i][2]<=Zs.w-3&&!hit(C[i])){u.lab=C[i];break} }
    if(!u.lab&&(u.pr===0||(force&&u.pr===1))) u.lab=C[0];
    if(u.lab) R.push(u.lab) });
  L.hit=hit; L.keep=function(r){R.push(r)};
  return L;
}
/* Formations (playback.formations, and the Layers menu): zoomed out below `below`, the units under one formation of the given
   echelon (a division, say) are drawn as that formation: one symbol where their symbols would sit, with their lines kept as its front.
   Zooming in past `below` breaks it out into its units again. A unit is gathered by walking up who it answered to at the moment. */
var FM=P.formations||null,fmOn=!!(FM&&FM.on);
function formationOf(uid){ var seen=0,d=stamp(t);
  while(uid&&seen++<5){var u=B.units[uid];if(!u)return null;var as=u.assignments||[],a=null;
    as.forEach(function(x){var f=x.from?B.time(x.from):-1e9,e=x.to?B.time(x.to)+((!byDay&&x.to.length===10)?1439:0):1e9;if(d>=f&&d<=e)a=x});
    a=a||as[as.length-1]; if(!a||!a.parent) return null; var p=B.units[a.parent]; if(!p) return null;
    if(isFormation(p)) return p; uid=a.parent}
  return null}
/* A unit counts as a formation if it is of the echelon, or named in formations.also (Trenton: Knox's artillery).
   Before formations.until the formations are drawn whatever the zoom: Trenton keeps Greene, Sullivan and Knox whole until the first shots. */
function isFormation(u){return !!u&&(String(u.echelon||'').toLowerCase()===(FM.echelon||'division')||[].concat(FM.also||[]).indexOf(u.id)>=0)}
function fmForced(){return !!(FM&&FM.until&&t<B.time(FM.until))}
function setFormations(v){fmOn=v;tick('cForm',v);remember('form',v);mv.kick()}
function f1(v){return v.toFixed(1)}
/* Routes taken: the road each unit has marched so far (the routes the record gives), drawn under the units and growing with the clock.
   Each side's lines are one group at reduced strength, so roads that several units took are not drawn darker. */
var TRL=P.trails||null,trlOn=!!(TRL&&TRL.on!==false);
var muteOn=true;
function hillAbout(){return HS?'<h2 style="margin-top:18px">Terrain shading</h2><p>Shadows worked out from the height of the ground, so ridges and valleys show even where today\'s map is muted. They are drawn over today\'s map only, not over the period maps, which show the ground in their own way. Heights in the United States come from the USGS; elsewhere mostly from satellite radar. Layers turns them off.</p><dl><dt>Source</dt><dd>'+esc(HS.credit)+'</dd></dl><p style="margin-top:10px"><a href="'+esc(HS.link)+'" target="_blank" rel="noopener">Where the heights come from</a></p>':''}
function setHill(v){hsOn=v;tick('cHill',v);remember('hill',v);hsVis=null;mv.kick()}
function setMute(v){muteOn=v;tick('cMute',v);remember('mute',v);wrap.classList.toggle('vivid',!v);mv.retheme();mv.kick()}
function setTrails(v){trlOn=v;tick('cTrail',v);remember('trail',v);mv.kick()}
function subPath(V,f){if(f>=1)return V;var L=0,i,seg=[];for(i=1;i<V.length;i++)L+=Math.hypot(V[i][0]-V[i-1][0],V[i][1]-V[i-1][1]);var want=L*f,out=[V[0]];
  for(i=1;i<V.length;i++){var d=Math.hypot(V[i][0]-V[i-1][0],V[i][1]-V[i-1][1]);if(d>=want){var u=d?want/d:0;out.push([V[i-1][0]+(V[i][0]-V[i-1][0])*u,V[i-1][1]+(V[i][1]-V[i-1][1])*u]);return out}want-=d;out.push(V[i])}return out}
/* Arrows ahead (playback.arrows): shortly before a unit sets off on a long move, and while it is on it, an arrow runs from the unit to
   where the record next puts it, along the route the record gives (straight where it gives none). On in every battle for moves of
   20 km or more; a battle can set min_km (how long a move earns an arrow), lead (how long before the unit sets off the arrow
   appears, in the battle's time unit: 3 days or 45 minutes unless set) or on: false. */
function evOp(id){   // a unit's opacity under the event focus, easing towards its target so it never flicks on and off
  var want=(evf&&!evf[id])?EVDIM:1,now=Date.now(),c=evCur[id];if(!c){evCur[id]={v:want,ts:now};return want}
  var dt=Math.min(200,now-c.ts),k=Math.min(1,dt/EVEASE)*(1-EVDIM+0.0001);c.ts=now;
  if(Math.abs(want-c.v)<=k)c.v=want;else{c.v+=want>c.v?k:-k;mv.kick()}return c.v}
var ARW=P.arrows||{},arwOn=ARW.on!==false,ARW_MIN=(ARW.min_km!=null?ARW.min_km:20)*1000,ARW_ANY=null;
function arrowsAny(){ // does any unit of this battle make a move long enough for an arrow? If none, the menu does not offer them
  if(ARW_ANY==null){ARW_ANY=false;B.tracks.forEach(function(tr){var ks=tr.k,i;for(i=1;i<ks.length&&!ARW_ANY;i++){var a=ks[i-1].g,b=ks[i].g;if(a&&b&&plen((ks[i].via&&ks[i].via.length>1)?ks[i].via:[cen(a),cen(b)])>=ARW_MIN)ARW_ANY=true}})}
  return ARW_ANY}
function setArrows(v){arwOn=v;tick('cArrow',v);remember('arrow',v);mv.kick()}
function ahead(V,c){ // the route from the point on it nearest c to its end
  var best=1e18,bi=0,bq=V[0],i; for(i=1;i<V.length;i++){var ax=V[i-1][0],ay=V[i-1][1],dx=V[i][0]-ax,dy=V[i][1]-ay,L2=dx*dx+dy*dy,u=L2?Math.max(0,Math.min(1,((c[0]-ax)*dx+(c[1]-ay)*dy)/L2)):0,
      q=[ax+dx*u,ay+dy*u],d=Math.hypot(q[0]-c[0],q[1]-c[1]); if(d<best){best=d;bi=i;bq=q}}
  return [bq].concat(V.slice(bi))}
function arrowsSvg(sc){ if(!arwOn||landing||!unitsOn||base.own||!arrowsAny()) return '';
  var minU=ARW_MIN,lead=ARW.lead!=null?ARW.lead:(byDay?3:45),h='';
  sc.forEach(function(o){ if(!o.drawn||o.hidden||o.folded||!o.s.g) return; var tr=o.tr,ks=tr.k,st=o.s,a,b,moving=st.kind==='moving'&&st.from;
    if(moving){a=st.from;b=st.k} else {a=st.k;b=ks[ks.indexOf(a)+1]; if(!b||st.kind==='lost'||t<a.t1-lead) return}
    var ga=geo(a,'g'),gb=geo(b,'g'); if(!ga||!gb) return;
    var V=(b.via&&b.via.length>1)?b.via:[cen(ga),cen(gb)]; if(plen(V)<minU) return;
    var Vg=moving?ahead(V,cen(st.g)):V;
    if(ARW.reach_minutes){var cap=plen(V)*ARW.reach_minutes/Math.max(1,b.t0-a.t1),lv=plen(Vg); if(lv>cap) Vg=subPath(Vg,cap/lv)}   // the arrow runs a few minutes' march ahead of the unit, not to the end of a long road
    var pts=Vg.map(S),n=pts.length,L=plen(pts); if(L<46) return;   // too short on screen to read as an arrow
    var e=WM.along(pts,1-9/L),s0=WM.along(pts,Math.min(0.4,18/L)),d='M'+f1(s0.p[0])+' '+f1(s0.p[1]),acc=0,i;   // clear of the symbol at one end, room for the head at the other
    for(i=1;i<n;i++){acc+=Math.hypot(pts[i][0]-pts[i-1][0],pts[i][1]-pts[i-1][1]); if(acc>18&&acc<L-9) d+='L'+f1(pts[i][0])+' '+f1(pts[i][1])}
    d+='L'+f1(e.p[0])+' '+f1(e.p[1]);
    var tip=pts[n-1],vx=tip[0]-e.p[0],vy=tip[1]-e.p[1],vl=Math.hypot(vx,vy)||1; vx/=vl; vy/=vl;
    var hd='M'+f1(tip[0])+' '+f1(tip[1])+'L'+f1(e.p[0]-vx*4-vy*6)+' '+f1(e.p[1]-vy*4+vx*6)+'L'+f1(e.p[0]-vx*4+vy*6)+' '+f1(e.p[1]-vy*4-vx*6)+'Z',col=look(tr).col,w=compact?2.4:3;
    h+='<g class="ahead" style="pointer-events:none" fill="none" stroke-linecap="round" stroke-linejoin="round" opacity="'+((moving?0.9:0.75)*evOp(tr.id))+'"><path d="'+d+'" stroke="var(--u-halo)" stroke-width="'+(w+3)+'"/><path d="'+hd+'" fill="var(--u-halo)" stroke="var(--u-halo)" stroke-width="4"/>'
      +'<path d="'+d+'" style="stroke:'+col+'" stroke-width="'+w+'" stroke-dasharray="'+(moving?'':'7 6')+'"/><path d="'+hd+'" style="fill:'+col+';stroke:'+col+'" stroke-width="1"/></g>'});
  return h}
function trailsSvg(){ if(!TRL||!trlOn||landing||!unitsOn) return ''; var key=base.own?base.map:'g',by={};
  /* fade_after (time units): once a unit has stopped this long, the roads it took to get there fade out over fade_over */
  var FA=TRL.fade_after,FO=Math.max(0.01,TRL.fade_over||FA||1),base0=TRL.opacity||0.55;
  B.tracks.forEach(function(tr){var ks=tr.k;for(var i=1;i<ks.length;i++){var a=ks[i-1],b=ks[i],V=key==='g'?b.via:(b.vo&&b.vo[key]);if(!V||V.length<2)continue;
    var end=a.t1;if(t<=end)break;var op=1;
    if(FA!=null){ // when does the unit next stand still for FA or more after this leg?
      var j=i;while(j<ks.length-1&&(ks[j].t1-ks[j].t0)<FA)j++;var gone=ks[j].t0+FA;
      if(t>gone){op=1-(t-gone)/FO;if(op<=0)continue}}
    var f=Math.min(1,(t-end)/Math.max(0.01,b.t0-end)),pts=subPath(V,Math.min(f/0.92,1)).map(S);
    var g=(by[tr.side]=by[tr.side]||{}),k=op.toFixed(2);(g[k]=g[k]||[]).push(pts.map(function(p,j){return (j?'L':'M')+f1(p[0])+' '+f1(p[1])}).join(''))}});
  var h='',w=compact?3:4;Object.keys(by).forEach(function(sd){var c=look({side:sd}).col;Object.keys(by[sd]).forEach(function(k){
    var dd=by[sd][k].join('');h+='<g class="trail" opacity="'+(base0*k).toFixed(3)+'" style="pointer-events:none" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="'+dd+'" stroke="var(--u-halo)" stroke-width="'+(w+3)+'"/><path d="'+dd+'" style="stroke:'+c+'" stroke-width="'+w+'"/></g>'})});
  return h}
/* ---------- days: pauses with a summary, and where units began and ended each day ----------
   A battle longer than two days can stop at the end of each day (or week) while it plays: the map stays as it is, and the
   text pane gives a summary; Continue goes on. Up to a week long it stops each day unless the reader turns it off; longer, it asks first.
   playback.day_pause: false (never), or "day", "week", "off" or "ask" to set the starting choice. Days end at midnight (time_zero is a
   midnight); a battle followed by the day ends each day at nightfall, when its positions are given. */
var DAYLEN=byDay?1:1440,NDAYS=(T1-T0)/DAYLEN,DAY0=byDay?T0-1:Math.floor(T0/1440)*1440;   // DAY0: when the first day began
var DE_OK=NDAYS>1.5,deOn=false;
var PZ_OK=P.day_pause!==false&&NDAYS>2,PZ_DEF=(typeof P.day_pause==='string')?P.day_pause:(NDAYS<=7?'day':'ask'),pzMode=PZ_DEF==='ask'?null:PZ_DEF;
try{var pzs=localStorage.getItem('wm.'+B.id+'.pause');if(pzs&&/^(off|day|week)$/.test(pzs))pzMode=pzs}catch(e){}
var SUMS=raw.summaries||[],sumAt=null,sumMode=null;
function dayEnds(){var out=[];for(var b=DAY0+DAYLEN;b<T1-1e-6;b+=DAYLEN)if(b>T0+1e-6)out.push(b);return out}
function weekEnds(){var d=dayEnds().filter(function(b){return Math.round((b-DAY0)/DAYLEN)%7===0});if(d.length&&(T1-d[d.length-1])/DAYLEN<=2)d.pop();return d}
function stopsFor(m){return m==='day'?dayEnds():m==='week'?weekEnds():[]}
function stopAt(a,b){if(!PZ_OK||!pzMode||pzMode==='off')return null;var st=stopsFor(pzMode);for(var i=0;i<st.length;i++)if(st[i]>a+1e-6&&st[i]<=b+1e-9)return st[i];
  if(b>=T1&&a<T1-1e-6)return T1;return null}   // and at the very end, for the last summary
function isoDay(b){return byDay?B.isoOf(Math.round(b)):B.isoOf(b-1).slice(0,10)}   // the day that has just ended at b
function dayNo(b){return Math.round((b-DAY0)/DAYLEN)}
function sumFor(b,m){var d=isoDay(b),hit=null;SUMS.forEach(function(x){if(x.kind===m&&x.from<=d&&x.to>=d&&(m==='day'||x.to===d||b>=T1-1e-6))hit=x});
  if(!hit&&m==='week')SUMS.forEach(function(x){if(x.kind==='week'&&x.from<=d&&x.to>=d)hit=x});return hit}
function longDate(iso){var p=iso.split('-'),d=new Date(Date.UTC(+p[0],+p[1]-1,+p[2]));return ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'][d.getUTCDay()]+' '+(+p[2])+' '+['January','February','March','April','May','June','July','August','September','October','November','December'][+p[1]-1]+' '+p[0]}
function setPause(m,keep){pzMode=m;['off','day','week'].forEach(function(k){press('pz-'+k,m===k)});if(!keep)try{localStorage.setItem('wm.'+B.id+'.pause',m)}catch(e){}}
/* units whose record changes during the day that ends at b (a new step begins), for the summary's list and for the day's map view */
function dayMoves(b){var a=b-DAYLEN,out=[];B.tracks.forEach(function(tr){tr.k.forEach(function(k){if(!k.virtual&&k.t0>a+1e-6&&k.t0<=b+1e-6&&geo(k,gkey()))out.push({tr:tr,k:k})})});return out}
function openSummary(b,m){sumAt=b;sumMode=m;sel=null;info=false;panelKey='';
  var c=$('cont');if(b<T1-1e-6){var nx=stopsFor(m).filter(function(x){return x>b+1e-6})[0];$('contTx').textContent='Continue'+(m==='week'?' to the next week':' to '+(byDay?(function(){var d=B.dateOf(Math.round(b)+1);return d.day+' '+d.mon}):function(){return 'the next day'})());c.hidden=false}else c.hidden=true;
  if(sheet)sheet.open();if(pane)pane.show();mv.kick()}
function closeSummary(){if(sumAt==null)return;sumAt=null;sumMode=null;panelKey='';$('cont').hidden=true;mv.kick()}
function summaryHtml(){var b=sumAt,m=sumMode,x=sumFor(b,m),d=isoDay(b),h='',n=dayNo(b);
  if(m==='week'){var st=stopsFor('week'),i=st.indexOf(b);h+='<div class="eyebrow">'+(b>=T1-1e-6?'End of the battle':'End of week '+(i+1))+(x?' &middot; '+esc(shortRange(x.from,x.to)):'')+'</div>'}
  else h+='<div class="eyebrow">'+(b>=T1-1e-6?'End of the battle &middot; ':'End of day '+n+' &middot; ')+esc(longDate(d))+'</div>';
  h+='<h2 class="sumh">'+esc(x?x.title:(m==='week'?'This week':'This day'))+'</h2>';
  if(x)h+='<p class="sumtx">'+esc(x.text)+'</p>';else{var ev=B.events.filter(function(e){return e.t>b-DAYLEN*(m==='week'?7:1)+1e-6&&e.t<=b+1e-6});h+=ev.length?ev.map(function(e){return '<p class="sumtx">'+esc(e.text||e.full)+'</p>'}).join(''):'<p class="sumtx meta">No summary written for this '+(m==='week'?'week':'day')+' yet.</p>'}
  if(m==='week'&&x){var days=SUMS.filter(function(y){return y.kind==='day'&&y.from>=x.from&&y.from<=x.to});if(days.length){h+='<h3>Day by day</h3><ul class="evl">';days.forEach(function(y){var bb=dayEndOf(y.from);h+='<li><button data-day="'+bb+'"><span class="tm">'+esc(shortDay(y.from))+'</span><span>'+esc(y.title)+'</span></button></li>'});h+='</ul>'}}
  else{var mv0=dayMoves(b),seen={};if(mv0.length){h+='<h3>On record this day</h3><ul class="ulist">';mv0.forEach(function(o){if(seen[o.tr.id])return;seen[o.tr.id]=1;h+='<li><button data-pick="'+o.tr.id+'"><span class="sd" style="background:'+look(o.tr).ui+'"></span><span class="nm">'+esc(o.tr.name)+'</span><span class="st">'+esc(o.k.act||o.k.place||'')+'</span></button></li>'});h+='</ul>'}}
  if(x&&x.sources&&x.sources.length)h+='<p class="meta" style="margin-top:12px">Drawn from: '+x.sources.map(function(id){var s=B.sources[id];return esc(s?(s.author?s.author.split(',')[0]+', ':'')+s.title:id)}).join('; ')+'.</p>';
  h+=(b<T1-1e-6?'<p style="margin-top:14px"><button class="lnk" id="sumgo">&#9654; '+esc($('contTx').textContent)+'</button></p>':'');
  return h}
function shortDay(iso){var p=iso.split('-');return (+p[2])+' '+['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][+p[1]-1]}
function shortRange(a,b){return a===b?shortDay(a):shortDay(a)+' – '+shortDay(b)}
function dayEndOf(iso){for(var b=DAY0+DAYLEN;b<=T1+1e-6;b+=DAYLEN)if(isoDay(b)===iso)return b;return T1}
function jumpToDay(b,m){clk.setPlaying(false);clk.setTime(b);openSummary(b,m||'day')}
/* where units began and ended the day now on screen: the day's first position dashed, its last thin and solid, joined by a line */
function dayEndsSvg(sc){ if(!DE_OK||!deOn||landing||!unitsOn) return ''; var key=gkey(),e=byDay?Math.max(T0,stamp(t)):Math.min(T1,DAY0+(Math.floor((t-DAY0)/DAYLEN)+1)*DAYLEN),a=Math.max(T0,e-DAYLEN),h='';
  var cen=function(P){var x=0,y=0;P.forEach(function(p){x+=p[0];y+=p[1]});return [x/P.length,y/P.length]},pth=function(P){return P.map(function(p,j){return (j?'L':'M')+f1(p[0])+' '+f1(p[1])}).join('')};
  sc.forEach(function(o){if(!o.drawn)return;var s0=stateAt(o.tr,a+1e-4,key),s1=stateAt(o.tr,e,key);if(!s0||!s1||!s0.g||!s1.g)return;
    var P0=s0.g.map(S),P1=s1.g.map(S),c0=cen(P0),c1=cen(P1);if(Math.hypot(c1[0]-c0[0],c1[1]-c0[1])<4)return;var c=look(o.tr).col;
    h+='<g class="dayend" style="pointer-events:none" fill="none" stroke-linecap="round">';
    if(P0.length>1)h+='<path d="'+pth(P0)+'" style="stroke:'+c+'" stroke-width="2" stroke-dasharray="5 4" opacity=".6"/>';else h+='<circle cx="'+f1(c0[0])+'" cy="'+f1(c0[1])+'" r="5" style="stroke:'+c+'" stroke-width="1.6" stroke-dasharray="3 2" opacity=".7"/>';
    if(P1.length>1)h+='<path d="'+pth(P1)+'" style="stroke:'+c+'" stroke-width="1.4" opacity=".85"/>';else h+='<rect x="'+f1(c1[0]-5)+'" y="'+f1(c1[1]-5)+'" width="10" height="10" style="stroke:'+c+'" stroke-width="1.6" opacity=".85"/>';
    h+='<path d="M'+f1(c0[0])+' '+f1(c0[1])+'L'+f1(c1[0])+' '+f1(c1[1])+'" style="stroke:'+c+'" stroke-width="1" stroke-dasharray="2 3" opacity=".6"/></g>'});
  return h}
function setDayEnds(v){deOn=v;tick('cDayEnds',v);remember('dayends',v);mv.kick()}
function unitSvg(u,part){   // the last position on record stays plain to see: dashed, barely faded
  var o=u.o,tr=o.tr,s=o.s,pts=u.pts,lk=look(tr),col=lk.col,k=s.kind;
  var soft=(k==='moving'||k==='early'||k==='after'||k==='unplaced'),low=u.low,op=(k==='unplaced'?0.5:k==='after'?0.8:1)*(u.fade==null?1:u.fade)*(u.o.s.fade==null?1:u.o.s.fade),isSel=!!tr.id&&sel===tr.id,h='',x=u.x,y=u.y,c=u.c;
  op*=tr.id?evOp(tr.id):1;   // BP-32: not one of the current event's units
  if(part==='line'){ if(!u.line) return '';
    var d=pts.map(function(p,i){return (i?'L':'M')+f1(p[0])+' '+f1(p[1])}).join('');
    var w=compact?((tr.ech==='corps'||tr.ech==='army')?5:tr.ech==='division'?4:3):((!tr.parent&&(tr.ech==='brigade'||tr.ech==='division'))?6:4.5);
    if(symbols==='period') w+=1.5;
    var dash=tr.loose?' stroke-dasharray="2 5"':((soft||(compact&&k==='inferred'))?' stroke-dasharray="'+(compact?'8 6':'7 5')+'"':'');
    h+='<g opacity="'+op+'" stroke-linecap="round" stroke-linejoin="round" fill="none">'; mv.hits.push({id:tr.id,pts:pts,tol:Math.max(7,w/2+4)});
    if(isSel) h+='<path d="'+d+'" stroke="var(--m-sel)" stroke-width="'+(w+9)+'" opacity=".8"/>';
    h+='<path d="'+d+'" stroke="var(--u-halo)" stroke-width="'+(w+(compact?3:4))+'"'+(compact?'':' stroke-linecap="butt"')+'/><path d="'+d+'" stroke="'+col+'" stroke-width="'+w+'"'+((compact||tr.loose)?'':' stroke-linecap="butt"')+dash+'/>';
    return h+'</g>'; }
  if(u.noSym) return '';
  var W=compact?12:13,H=compact?8:9;
  if(symbols==='period'){ // period style: no frame. A line is its own mark, as on the maps of the time; a unit at a point is a small block
    h+='<g opacity="'+op+'">';
    if(!u.line){mv.hits.push({id:tr.id,r:[c[0]-12,c[1]-9,c[0]+12,c[1]+9]});
      if(isSel) h+='<rect x="'+f1(c[0]-13)+'" y="'+f1(c[1]-8)+'" width="26" height="16" rx="3" fill="none" stroke="var(--m-sel)" stroke-width="4"/>';
      if(tr.branch==='nav') h+='<path transform="translate('+f1(c[0])+' '+f1(c[1])+')" d="M-10 0H10L7 5H-7ZM-4 0V-3H4V0ZM-1 -3V-6H2V-3Z" fill="'+col+'" stroke="var(--u-halo)" stroke-width="1.2"'+((soft||low)?' fill-opacity=".55"':'')+'/>';
      else h+='<rect x="'+f1(c[0]-9)+'" y="'+f1(c[1]-4)+'" width="18" height="8" fill="'+col+'" stroke="var(--u-halo)" stroke-width="1.5"'+((soft||low)?' fill-opacity=".55"':'')+'/>'}
    if(u.lab){h+='<text class="ulab" text-anchor="'+u.lab[4]+'" x="'+f1(u.lab[5])+'" y="'+f1(u.lab[6])+'">'+esc(u.txt)+'</text>';mv.hits.push({id:tr.id,r:[u.lab[0],u.lab[1],u.lab[0]+u.w,u.lab[1]+16]})}
    return h+'</g>'}
  var foe=!!seenFrom&&tr.side!==seenFrom,D=W+1;   // seen from one side, the other side's units take the diamond frame of the standard symbols
  h+='<g opacity="'+op+'">'; mv.hits.push({id:tr.id,r:[x-W-4,y-H-11,x+W+4,y+H+4]});
  if((compact&&u.line)||u.nudged) h+='<line x1="'+f1(c[0])+'" y1="'+f1(c[1])+'" x2="'+f1(x)+'" y2="'+f1(y)+'" stroke="'+(compact?col:'var(--u-ink)')+'" stroke-width="'+(compact?1.2:1)+'"/>';
  if(u.nudged&&!(compact&&u.line)) h+='<circle cx="'+f1(c[0])+'" cy="'+f1(c[1])+'" r="2.5" fill="'+col+'"/>';
  h+='<g transform="translate('+f1(x)+' '+f1(y)+')">';
  if(isSel) h+='<rect x="'+(-W-5)+'" y="'+(foe?-D-4:-H-5)+'" width="'+(2*W+10)+'" height="'+(foe?2*D+8:2*H+10)+'" rx="4" fill="none" stroke="var(--m-sel)" stroke-width="4"/>';
  var dsh=((soft||low)?' stroke-dasharray="3 2.5"':''),q=D/2;
  if(foe&&tr.branch!=='nav'){h+='<path d="M0 '+(-D)+'L'+D+' 0L0 '+D+'L'+(-D)+' 0Z" fill="none" stroke="var(--u-halo)" stroke-width="5" stroke-linejoin="round"/>'+'<path d="M0 '+(-D)+'L'+D+' 0L0 '+D+'L'+(-D)+' 0Z" fill="'+lk.fill+'" stroke="'+col+'" stroke-width="1.8"'+dsh+'/>';
    if(tr.ech==='headquarters') h+='<text class="ech in" text-anchor="middle" y="3.5" style="stroke:none">HQ</text>';
    else if(tr.branch==='inf') h+='<path d="M'+(-q)+' '+(-q)+'L'+q+' '+q+'M'+(-q)+' '+q+'L'+q+' '+(-q)+'" stroke="'+col+'" stroke-width="1.4"/>';
    else if(tr.branch==='cav') h+='<path d="M'+(-q)+' '+q+'L'+q+' '+(-q)+'" stroke="'+col+'" stroke-width="1.4"/>';
    else h+='<circle r="3.2" fill="'+col+'"/>';
    h+='<text class="ech" text-anchor="middle" y="'+(-D-3)+'">'+(ECH[tr.ech]||'')+'</text></g>';}
  else if(tr.branch==='nav'){   // ships: a hull, deckhouse and funnel in the side's colour, no frame and no echelon mark
    var sp='M'+(-W-2)+' 1H'+(W+2)+'L'+(W-2)+' '+(H+1)+'H'+(-W+2)+'ZM-6 1V-3H5V1ZM-2 -3V'+(-H-1)+'H2V-3Z';
    h+='<path d="'+sp+'" fill="none" stroke="var(--u-halo)" stroke-width="5" stroke-linejoin="round"/><path d="'+sp+'" fill="'+col+'"'+((soft||low)?' fill-opacity=".6"':'')+' stroke="'+col+'" stroke-width="1.2" stroke-linejoin="round"'+dsh+'/></g>';}
  else{
  h+='<rect x="'+(-W)+'" y="'+(-H)+'" width="'+2*W+'" height="'+2*H+'" fill="none" stroke="var(--u-halo)" stroke-width="5"/>'+'<rect x="'+(-W)+'" y="'+(-H)+'" width="'+2*W+'" height="'+2*H+'" fill="'+lk.fill+'" stroke="'+col+'" stroke-width="1.8"'+dsh+'/>';
  if(tr.ech==='headquarters') h+='<path d="M'+(-W)+' '+(-H)+'V'+(H+7)+'" stroke="'+col+'" stroke-width="1.8"/><text class="ech in" text-anchor="middle" y="4" style="stroke:none">HQ</text>';
  else if(tr.branch==='inf') h+='<path d="M'+(-W)+' '+(-H)+'L'+W+' '+H+'M'+(-W)+' '+H+'L'+W+' '+(-H)+'" stroke="'+col+'" stroke-width="1.4"/>';
  else if(tr.branch==='cav') h+='<path d="M'+(-W)+' '+H+'L'+W+' '+(-H)+'" stroke="'+col+'" stroke-width="1.4"/>';
  else h+='<circle r="3.4" fill="'+col+'"/>';
  h+='<text class="ech" text-anchor="middle" y="'+(-H-3)+'">'+(ECH[tr.ech]||'')+'</text></g>';}
  if(u.lab){h+='<text class="ulab" text-anchor="'+u.lab[4]+'" x="'+f1(u.lab[5])+'" y="'+f1(u.lab[6])+'">'+esc(u.txt)+'</text>';mv.hits.push({id:tr.id,r:[u.lab[0],u.lab[1],u.lab[0]+u.w,u.lab[1]+16]})}
  return h+'</g>';
}
/* Names on the map. Names from today's map are drawn where today's map shows: not on a period map, which carries its own.
   A name marked for period maps (show "period" or "both") is drawn there too. */
/* Places far off the map (show "far"): a town the reader knows the battle by, too far away to zoom out to. While it is off screen it is
   named at the edge of the map, on the line from the middle of the screen towards it, with an arrow and how far it is from the middle of
   the screen in a straight line; on screen it is a town like any other. They are named on every map, a reconstruction too. The edge is
   kept clear of the buttons over the map. */
var farKey='',farLater=0;
function farFrame(z){
  var R=wrap.getBoundingClientRect(),f={w:z.w,h:z.h,l:12,t:12,r:z.w-12,b:z.h-12};
  function rc(e){if(!e||e.classList.contains('gone'))return null;var r=e.getBoundingClientRect();return r.width&&r.height?[r.left-R.left,r.top-R.top,r.right-R.left,r.bottom-R.top]:null}
  [].forEach.call(wrap.querySelectorAll('.ctl'),function(e){var r=rc(e);if(!r)return;if(r[0]>z.w*0.6&&r[3]>z.h*0.2)f.r=Math.min(f.r,r[0]-10);else if(r[1]<z.h*0.3)f.t=Math.max(f.t,r[3]+10)});
  var bl=rc(wrap.querySelector('.bl'));if(bl)f.b=Math.min(f.b,bl[1]-8);
  var key=[f.l,f.t,f.r,f.b].map(Math.round).join();   // the buttons can settle after the map is first drawn: draw again once they have
  if(key!==farKey){farKey=key;clearTimeout(farLater);farLater=setTimeout(function(){mv.kick()},400)}
  return f}
function farName(l,L,z){
  var q=S(l.p),f=farFrame(z),cx=(f.l+f.r)/2,cy=(f.t+f.b)/2;
  if(q[0]>f.l&&q[0]<f.r&&q[1]>f.t&&q[1]<f.b){ var w=l.t.length*6.6+4,pr=[q[0]+5,q[1]-15,q[0]+8+w,q[1]-1]; L.keep(pr);   // on screen: a town like any other
    return '<circle cx="'+f1(q[0])+'" cy="'+f1(q[1])+'" r="3.4" fill="var(--u-ink)"/><text class="pl big far" x="'+f1(q[0]+7)+'" y="'+f1(q[1]-4)+'">'+esc(l.t)+'</text>'}
  var dx=q[0]-cx,dy=q[1]-cy,k=Math.min(dx?((dx>0?f.r:f.l)-cx)/dx:1e9,dy?((dy>0?f.b:f.t)-cy)/dy:1e9),px=cx+dx*k,py=cy+dy*k,a=Math.atan2(dy,dx);
  var mi=Math.hypot(dx,dy)/sNow/1609.344,d=(mi<10?mi.toFixed(1):String(Math.round(mi)))+' mi',txt=l.t,tw=Math.max(txt.length*6.9,d.length*6)+6;
  var side=Math.abs(px-f.r)<1?'r':Math.abs(px-f.l)<1?'l':Math.abs(py-f.t)<1?'t':'b',ax,ay,an;   // the name sits inside the arrow, on the map side of it
  if(side==='r'){ax=px-14;ay=py;an='end'} else if(side==='l'){ax=px+14;ay=py;an='start'} else if(side==='t'){ax=px;ay=py+22;an='middle'} else {ax=px;ay=py-26;an='middle'}
  var x0=an==='end'?ax-tw:an==='start'?ax:ax-tw/2,r=[x0,ay-12,x0+tw,ay+16],n=0;
  while(L.hit(r)&&n++<6){var s=side==='r'||side==='l'?[0,18]:[tw+6,0];r=[r[0]+s[0],r[1]+s[1],r[2]+s[0],r[3]+s[1]];ax+=s[0];ay+=s[1];px+=s[0];py+=s[1]}   // two places the same way: the second steps along the edge
  L.keep(r);
  var arrow='<path class="farr" transform="translate('+f1(px)+' '+f1(py)+') rotate('+f1(a*180/Math.PI)+')" d="M0 0L-11 -6L-8 0L-11 6Z"/>';
  return arrow+'<text class="pl big far" text-anchor="'+an+'" x="'+f1(ax)+'" y="'+f1(ay)+'">'+esc(txt)+'</text><text class="pl far d" text-anchor="'+an+'" x="'+f1(ax)+'" y="'+f1(ay+13)+'">'+esc(d)+'</text>'}
function mapNames(L,cover){
  var z=mv.size(),lvl=sNow>=(Z.labels||0)?1:0,h='',cur=!!(base.current||base.sat||base.backdrop==='current'||through()),tp=cur&&!base.sat&&topo();
  var TER={ridge:1,hill:1},LB=B.labels.filter(function(l){return TER[l.k]}).concat(B.labels.filter(function(l){return !TER[l.k]}));   // the lie of the land is named first, so roads and woods give way to it
  if(base.rc&&base.rc.sheet&&placeNames){var sh=base.rc.sheet,tq=S(B.fromLL([sh[0]+(sh[2]-sh[0])*0.03,sh[1]+(sh[3]-sh[1])*0.1])),tt=String(base.rc.title).split(': ');   // the sheet's title, where a map of the time carried it; it says what the sheet is
    if(sNow>0.04&&sNow<0.3&&tq[0]>-200&&tq[1]>20&&tq[0]<z.w&&tq[1]<z.h+40){var tr=[tq[0]-6,tq[1]-44,tq[0]+215,tq[1]+24];L.keep(tr);
      h+='<g class="rct" transform="translate('+f1(tq[0])+' '+f1(tq[1])+')"><text class="t1" y="-24">'+esc(tt[0].split(', ')[0])+'</text><text class="t2" y="-4">'+esc(tt[0].split(', ').slice(1).join(', '))+'</text><text class="t3" y="16">'+esc(cap(tt[1]||'A reconstruction'))+'</text></g>'}}
  LB.forEach(function(l){
    if(l.show==='far'){ if(placeNames) h+=farName(l,L,z); return }
    var show=l.show||'current'; if(base.rc?show!=='recon':(show==='recon'||(cur?show==='period':show==='current'))) return;   // a reconstructed map carries the names read for it, and only those
    if(tp&&(l.k==='road'||l.k==='water'||l.k==='town')) return;   // the modern map names its own roads, streams and towns; the battle's landmarks and high ground are still named
    if((l.k==='road'||l.k==='water')?!lineNames:!placeNames) return;
    if(TER[l.k]){ if(l.l>lvl) return; var q0=S(l.p); if(q0[0]<-200||q0[1]<-200||q0[0]>z.w+200||q0[1]>z.h+200) return;
      if(l.k==='ridge'){ // a ridge: its name spaced out along the crest, slid along it to find room clear of the units; a key ridge is named even under them
        var tw=l.t.length*9.1,ra=l.a*Math.PI/180,ux=Math.cos(ra),uy=Math.sin(ra),ca=Math.abs(ux),sa=Math.abs(uy),bw=(tw*ca+14*sa)/2,bh=(tw*sa+14*ca)/2,pick=null,rr;
        [0,45,-45,90,-90,140,-140].some(function(o){var cx=q0[0]+ux*o,cy=q0[1]+uy*o;rr=[cx-bw,cy-bh,cx+bw,cy+bh];if(rr[0]<2||rr[1]<2||rr[2]>z.w-2||rr[3]>z.h-2||L.hit(rr))return false;pick=[cx,cy,rr];return true});
        if(!pick){if(l.l>0)return;pick=[q0[0],q0[1],null]} else L.keep(pick[2]);
        h+='<text class="rl'+(pick[2]?'':' under')+'" text-anchor="middle" transform="translate('+f1(pick[0])+' '+f1(pick[1])+') rotate('+l.a+')" y="4">'+esc(l.t)+'</text>'; return}
      // a hill: a summit mark, and its name beside it
      var hw=l.t.length*7.3+4,hr=[q0[0]+7,q0[1]-16,q0[0]+9+hw,q0[1]],hl=[q0[0]-9-hw,q0[1]-16,q0[0]-7,q0[1]],side=!L.hit(hr)?hr:!L.hit(hl)?hl:null;
      h+='<path class="hm" d="M'+f1(q0[0])+' '+f1(q0[1]-5)+'l4.5 7.5h-9z"/>';
      if(!side&&l.l>0) return; if(side) L.keep(side);
      h+='<text class="hl'+(side?'':' under')+'"'+(side===hl?' text-anchor="end" x="'+f1(q0[0]-8)+'"':' x="'+f1(q0[0]+8)+'"')+' y="'+f1(q0[1]-4)+'">'+esc(l.t)+(l.s&&sNow>=(Z.full_names||1e9)?' <tspan class="old">('+esc(l.s)+')</tspan>':'')+'</text>'; return}
    if(l.l>lvl&&l.k!=='wood') return;
    if(cover&&l.p[0]>cover[0]&&l.p[0]<cover[2]&&l.p[1]>cover[1]&&l.p[1]<cover[3]) return;
    var q=S(l.p); if(q[0]<-60||q[1]<-20||q[0]>z.w+60||q[1]>z.h+20) return;
    if(l.k==='road'||l.k==='water'){ // laid along the road or stream; skipped where it would sit on a unit or another name
      var tw=(l.t.length+(l.s?l.s.length+3:0))*5.7,ca=Math.abs(Math.cos(l.a*Math.PI/180)),sa=Math.abs(Math.sin(l.a*Math.PI/180)),bw=(tw*ca+13*sa)/2,bh=(tw*sa+13*ca)/2,r=[q[0]-bw,q[1]-bh,q[0]+bw,q[1]+bh];
      if(r[0]<2||r[1]<2||r[2]>z.w-2||r[3]>z.h-2||L.hit(r)) return; L.keep(r);
      h+='<text class="sl'+(l.k==='water'?' w':'')+'" text-anchor="middle" transform="translate('+f1(q[0])+' '+f1(q[1])+') rotate('+l.a+')" y="3.5">'+esc(l.t)+(l.s?' <tspan class="old">('+esc(l.s)+')</tspan>':'')+'</text>'; return}
    if(l.k==='area'||l.k==='town'||l.k==='wood'){
      if(l.k==='area'&&inkNames(l.p)) return;   // close in, the period map's own lettering names the district
      if(l.k==='town'&&Z.towns_until&&sNow>Z.towns_until) return; if(l.k==='wood'&&sNow<(Z.woods_from||0)) return;
      var aw=l.t.length*(l.k==='town'?8.6:l.k==='wood'?5.9:base.rc?12.8:8.2)/2,ar=[q[0]-aw,q[1]-9,q[0]+aw,q[1]+7]; if(L.hit(ar)) return; L.keep(ar);
      h+='<text class="'+(l.k==='wood'?'wl':'al'+(l.k==='town'?' town':''))+'" text-anchor="middle" x="'+f1(q[0])+'" y="'+f1(q[1]+4)+'">'+esc(l.t)+'</text>'; return}
    // a place or a landmark: a dot, and its name if there is room
    if(l.k==='landmark'&&sNow<(Z.landmarks_from||0)) return;
    var big=l.k==='place'&&l.l===0,full=l.s&&sNow>=(Z.full_names||1e9),txt=l.t+(full?' ('+l.s+')':''),w=txt.length*(big?6.6:5.9)+4,pr=[q[0]+5,q[1]-15,q[0]+8+w,q[1]-1],hid=L.hit(pr);
    h+='<circle cx="'+f1(q[0])+'" cy="'+f1(q[1])+'" r="'+(big?3:2.2)+'" fill="var(--u-ink)" opacity="'+(big?1:.7)+'"/>'; if(hid) return; L.keep(pr);
    h+='<text class="'+(l.k==='place'?'pl'+(big?' big':''):'lm')+'" x="'+f1(q[0]+7)+'" y="'+f1(q[1]-4)+'">'+esc(l.t)+(full?' <tspan class="old">('+esc(l.s)+')</tspan>':'')+'</text>'});
  if(placeNames) h+=contourNames(L);   // last, so the names of places come first
  return h}
function seriesAt(){var d=Math.max(T0,stamp(t));for(var i=0;i<series.length;i++)if(d>=series[i].t0&&d<=series[i].t1)return series[i];return series[series.length-1]}
var seriesShown=null,lastCredit='';
function showSeries(H){ if(H===seriesShown) return; if(H){mv.moveImage('pic-series',WM.asset(H.images[0].file),H.images[0].ll);if(!seriesShown)mv.show('pic-series',true)} else mv.show('pic-series',false); seriesShown=H }
function paintCredit(H){var c,mc=MOD?(MOD.link?'<a href="'+esc(MOD.link)+'" target="_blank" rel="noopener">'+esc(MOD.credit)+'</a>':esc(MOD.credit)):'',now=topo()?mc:(raw.base&&raw.base.credit&&!/OpenStreetMap/.test(raw.base.credit)?'Map data: '+esc(raw.base.credit):WM.OSM_CREDIT);
  if(base.current) c=now;
  else if(base.sat){var im=base.imagery;c=(im.link?'<a href="'+esc(im.link)+'" target="_blank" rel="noopener">'+esc(im.credit)+'</a>':esc(im.credit))+' &middot; Names: '+WM.OSM_CREDIT}
  else if(base.rc) c=esc(base.rc.credit||'A WarMapper reconstruction');
  else{var m=H||base.m,und=base.backdrop==='current'||through(); c=(H?esc(m.short)+', '+esc(m.label)+(stamp(t)>m.t1?' (the last one)':'')+' &middot; ':'')+esc(m.credit)+(und?' &middot; '+now:(modOn?' &middot; Around it: '+mc:''))}
  if(hsVis||hsRc||trnOf()) c+=' &middot; '+(trnOf()?'Relief and contours':hsRc?'Relief':'Terrain shading')+': <a href="'+esc(HS.link)+'" target="_blank" rel="noopener">'+esc(HS.credit)+'</a>';
  if(c!==lastCredit){lastCredit=c;$('credit').innerHTML=c;if(info)panelKey=''}}   // the i panel lists the credits: redraw it if it is open
/* The credits are under the i button. They also show on the map for five seconds when the page opens and when the reader changes the
   map, then fade (OpenStreetMap's attribution guideline: show the credit first; after five seconds it may collapse behind an "i"). */
var creditTimer=0;
function flashCredit(){var e=$('credit');e.classList.remove('gone');clearTimeout(creditTimer);creditTimer=setTimeout(function(){e.classList.add('gone')},5000)}
function draw(){
  sNow=mv.scale(); mv.hits.length=0;
  var H=base.series?seriesAt():null; if(series.length) showSeries(H); paintModern(H); paintHill(); paintCredit(H); trnTick(); inkTick();
  var cover=base.backdrop==='current'?(H||base.m).box:null;
  evf=evFocus();
  var sc=scene(),L=layout(unitsOn&&!landing?sc:[]),h=mapNames(L,cover);   // on landing the map is shown alone; the units come on when the battle is started
  L.sort(function(a,b){return (a.o.tr.id===sel)-(b.o.tr.id===sel)});   // the selected unit last, so it sits on top
  h+=trailsSvg()+dayEndsSvg(sc)+arrowsSvg(sc); L.forEach(function(u){h+=unitSvg(u,'line')}); L.forEach(function(u){h+=unitSvg(u,'sym')}); ov.innerHTML=h;
  var su=P.scale_bar||(byDay?'km':'yards'),sk=$('scale');
  if(!base.own) WM.scaleBar(sk,mv.mPerPx(),su);
  else if(base.m.raw.approx_m_per_px) WM.scaleBar(sk,base.m.raw.approx_m_per_px/sNow,su,true,base.m.raw.scale_note||'Roughly: this map is not to scale');   // a sketch: a rough scale where it is nearest to true
  else{var nt='<span class="nts">'+esc(base.m.raw.scale_note||'Not to scale')+'</span>';if(sk._h!==nt){sk._h=nt;sk.innerHTML=nt}}
  var off=$('offnote'),on=base.own&&base.m.raw.off_note; if(on&&t<B.time(on.until)){off.hidden=false;off.textContent=on.text} else off.hidden=true;
  renderPanel(landing?[]:sc); noteView();
}

/* ---------- the base maps ---------- */
var CUR=[],PICS={};
var cssNum=function(n,d){return function(c){var v=parseFloat(c(n));return isNaN(v)?d:v}};   // a paint value read from the page's settings, so it follows the theme and the Muted switch
function buildBase(){
  var W=ROADS[style],f=[],lat=raw.view.origin[1],minor=!!Z.minor_roads_from,wide=(raw.base&&raw.base.widths)||{},mask=bases.filter(function(b){return b.clip})[0];
  if(MOD){ // the modern map, under the pictures and over the battle's own drawing of today's ground (which it replaces)
    mv.map.addSource('sur',{type:'raster',tiles:[MOD.tiles],tileSize:MOD.tile_size||256,minzoom:MOD.min_zoom||0,maxzoom:MOD.max_zoom||16});
    mv.map.on('sourcedata',function(e){if(e.sourceId==='sur'&&e.tile&&!modOff)modFail=0})}
  if(HS) mv.map.addSource('dem',{type:'raster-dem',tiles:[HS.tiles],encoding:HS.encoding,tileSize:HS.tile_size||256,maxzoom:HS.max_zoom});
  // imagery bases: tiles from the provider's own service, under everything else. MapLibre fetches tiles only while the layer is shown.
  bases.forEach(function(b){if(!b.sat)return;var im=b.imagery,id='sat-'+b.id;
    mv.map.addSource(id,{type:'raster',tiles:[im.tiles],tileSize:im.tile_size||256,minzoom:im.min_zoom||0,maxzoom:im.max_zoom||18});
    mv.layer({id:id,type:'raster',source:id,layout:{visibility:'none'},paint:{'raster-fade-duration':0,'raster-saturation':cssNum('--img-sat',0),'raster-brightness-min':cssNum('--img-lo',0),'raster-brightness-max':function(c){return +c('--raster-max')||1}}})});
  B.base.areas.forEach(function(a){f.push(WM.feat('area',a.ll,{k:a.kind==='wood'?'wood':'lake'}))});
  B.base.lines.forEach(function(l){
    if(l.kind==='water'){f.push(WM.feat('line',l.ll,wide[l.name]?{k:'river',gw:wide[l.name]}:{k:'water',w:compact?(l.cls==='river'?3.6:2.6):(l.cls==='river'?3.2:1.6)}));return}
    if(l.kind==='former-water'){f.push(WM.feat('line',l.ll,{k:'former'}));return}
    if(l.kind==='rail'){f.push(WM.feat('line',l.ll,{k:'rail'}));return}
    var w=W[l.cls]||W[W._];f.push(WM.feat('line',l.ll,{k:'road',major:(!compact&&(l.cls==='m'||l.cls==='p'))?1:0,e:w[0],w:w[1],minor:(minor&&(l.cls==='r'||l.cls==='v'))?1:0}))});
  if(mask){ // everything outside the period map is covered, so the current map ends where the period map does
    var c=B.maps[mask.clip].ll,far=[[-9,-9],[10,-9],[10,10],[-9,10],[-9,-9]].map(function(q){return B.toLL([EXT[0]+(EXT[2]-EXT[0])*q[0],EXT[1]+(EXT[3]-EXT[1])*q[1]])});
    f.push({type:'Feature',properties:{k:'mask'},geometry:{type:'Polygon',coordinates:[far,[c[0],c[3],c[2],c[1],c[0]]]}})}
  mv.geo('base',f);
  var is=function(k){return ['==',['get','k'],k]},round={'line-cap':'round','line-join':'round'},mz=minor?mv.zoomFor(Z.minor_roads_from):0;
  var px=function(zm){return 512*Math.pow(2,zm)/(EARTH*Math.cos(lat*Math.PI/180))};   // screen pixels per metre at a zoom level
  function add(spec){CUR.push(spec.id);spec.source='base';mv.layer(spec)}
  add({id:'b-wood',type:'fill',filter:is('wood'),paint:{'fill-color':'var(--wood)'}});
  add({id:'b-lake',type:'fill',filter:is('lake'),paint:{'fill-color':'var(--water)'}});
  // a river given a width on the ground is drawn that wide, so its width in pixels doubles with each zoom level
  add({id:'b-river',type:'line',filter:is('river'),layout:round,paint:{'line-color':'var(--water)','line-width':['interpolate',['exponential',2],['zoom'],6,['*',['get','gw'],px(6)],22,['*',['get','gw'],px(22)]]}});
  add({id:'b-water',type:'line',filter:is('water'),layout:round,paint:{'line-color':'var(--water)','line-width':['get','w']}});
  add({id:'b-former',type:'line',filter:is('former'),paint:{'line-color':'var(--water)','line-width':2,'line-dasharray':[2.5,2]}});
  add({id:'b-rail',type:'line',filter:is('rail'),paint:{'line-color':'var(--rail)','line-width':1.6,'line-dasharray':[4.4,2.5]}});
  // side streets and tracks are left out when zoomed right out
  var mn=function(v){return ['all',is('road'),['==',['get','minor'],v]]},col=function(c){return ['match',['get','major'],1,c('--road-major'),c('--road')]};
  add({id:'b-edge-minor',type:'line',minzoom:mz,filter:mn(1),layout:round,paint:{'line-color':'var(--road-edge)','line-width':['get','e']}});
  add({id:'b-edge',type:'line',filter:mn(0),layout:round,paint:{'line-color':'var(--road-edge)','line-width':['get','e']}});
  add({id:'b-road-minor',type:'line',minzoom:mz,filter:mn(1),layout:round,paint:{'line-color':'var(--road)','line-width':['get','w']}});
  add({id:'b-road',type:'line',filter:mn(0),layout:round,paint:{'line-color':col,'line-width':['get','w']}});
  mv.layer({id:'b-mask',type:'fill',source:'base',filter:is('mask'),paint:{'fill-color':'var(--bg)'}});
  if(MOD) mv.layer({id:'sur',type:'raster',source:'sur',layout:{visibility:'none'},paint:{'raster-fade-duration':0,'raster-saturation':cssNum('--mod-sat',-0.2),'raster-brightness-min':cssNum('--mod-lo',0),'raster-contrast':cssNum('--mod-con',0),'raster-brightness-max':function(c){return +c('--raster-max')||1}}});
  if(HS) mv.layer({id:'hill',type:'hillshade',source:'dem',layout:{visibility:'none'},paint:{'hillshade-exaggeration':HS.exaggeration,'hillshade-illumination-direction':315,
    'hillshade-shadow-color':'var(--hs-shadow)','hillshade-highlight-color':'var(--hs-light)','hillshade-accent-color':'var(--hs-shadow)'}});
  // the period maps: each base's pictures; the map of the day is one picture, re-pointed when the date calls for another
  bases.forEach(function(b){PICS[b.id]=[];
    if(b.series){ if(series.length){mv.image('pic-series',WM.asset(series[0].images[0].file),series[0].images[0].ll);mv.show('pic-series',false)} return }
    if(!b.m) return;
    b.m.images.forEach(function(im,i){var id='pic-'+b.id+'-'+i;PICS[b.id].push({id:id,detail:im.detail});
      mv.image(id,WM.asset(im.file),b.own?[0,0,b.m.size[0],b.m.size[1]]:im.ll,b.own?WORLDS[worldOf(b)]:undefined);mv.show(id,false)})});
  mv.map.addLayer({id:'iiif-slot',type:'background',layout:{visibility:'none'}});   // full-detail tiles go in here, over the pictures
  for(var rk in RECON) buildRecon(RECON[rk],px);
}
/* ---------- a reconstructed base map: drawn from data, in period dress ---------- */
/* The look is that of an Army engineer's map of about 1900: toned paper, water in a pale wash with lines drawn along the shore, roads as
   double lines, the railway with its ties, walls in a heavy line, relief shaded in the ink's own brown. All of it is drawn by the map
   library from the battle file's lines, so it stays sharp at any zoom and sits on the same ground as the units. The colours are the
   paper's, the same in the light and dark themes. */
var RCL={},rcSel=null,RCF={};
function unpackLL(s){var out=[],x=0,y=0;s.split(';').forEach(function(t,i){var a=t.split(',');x=i?x+(+a[0]):+a[0];y=i?y+(+a[1]):+a[1];out.push([x/1e5,y/1e5])});return out}
function paperGrain(){ // a small tile of toned paper (soft mottle and a little speckle), made here so the page carries no picture for it
  var n=256,d=new Uint8Array(n*n*4),s=7,r=function(){s=(s*16807)%2147483647;return s/2147483647},i,j;
  var field=function(c){var g=[],k;for(k=0;k<c*c;k++)g.push(r());var w=n/c;return function(x,y){var fx=x/w,fy=y/w,x0=Math.floor(fx)%c,y0=Math.floor(fy)%c,x1=(x0+1)%c,y1=(y0+1)%c,u=fx-Math.floor(fx),v=fy-Math.floor(fy);u=u*u*(3-2*u);v=v*v*(3-2*v);
    return g[y0*c+x0]*(1-u)*(1-v)+g[y0*c+x1]*u*(1-v)+g[y1*c+x0]*(1-u)*v+g[y1*c+x1]*u*v}},A=field(4),Bf=field(16);
  for(j=0;j<n;j++)for(i=0;i<n;i++){var k=(j*n+i)*4,v=A(i,j)*0.6+Bf(i,j)*0.28+r()*0.12-0.5,dark=v<0;d[k]=dark?104:255;d[k+1]=dark?80:249;d[k+2]=dark?46:228;d[k+3]=Math.round(Math.min(1,Math.abs(v)*2.2)*(dark?58:66))}
  return {width:n,height:n,data:d}}
function blockhouseIcon(){var n=28,cv=document.createElement('canvas');cv.width=cv.height=n;var c=cv.getContext('2d');c.fillStyle='#efe4c8';c.strokeStyle='#33291f';c.lineWidth=2.4;c.fillRect(5,5,18,18);c.strokeRect(5,5,18,18);c.lineWidth=1.6;c.strokeRect(10.5,10.5,7,7);
  return {width:n,height:n,data:new Uint8Array(c.getImageData(0,0,n,n).data.buffer)}}
function buildRecon(R,px){
  var src='rc-'+R.id,f=[],ids=[],sh=R.sheet,is=function(k){return ['==',['get','k'],k]},round={'line-cap':'round','line-join':'round'};
  var inks=R.features.filter(function(x){return x.kind==='ink'&&x.file}),iz=inks.length?Math.min.apply(null,inks.map(function(x){return x.from_zoom||13.5})):99;   // the zoom from which a period map's own ink comes in
  INKS[R.id]=inks.map(function(x,n){var c=unpackLL(x.at[0]).slice(0,4),z0=x.from_zoom||13.5,fl=x.files&&x.files.length?x.files:[[z0,x.file]];return {n:n,id:x.id,corners:c,lv:fl.map(function(q){return {z:q[0],file:q[1]}})}});
  R.features.forEach(function(x){RCF[x.id]=x;var pr={k:x.kind,id:x.id,cls:x['class']||'',gw:x.width_m||0,lo:x.confidence==='low'?1:0,un:x.under?1:0},g;
    if(x.shape==='point') g={type:'Point',coordinates:x.at};
    else if(x.shape==='areas') g={type:'MultiPolygon',coordinates:x.at.map(function(a){return a.map(unpackLL)})};   // several areas under one record (the esteros of a district)
    else{var rings=x.at.map(unpackLL);g=x.shape==='line'?{type:'LineString',coordinates:rings[0]}:x.shape==='lines'?{type:'MultiLineString',coordinates:rings}:{type:'Polygon',coordinates:rings}}
    f.push({type:'Feature',properties:pr,geometry:g})});
  if(sh){var o=[[sh[0]-3,sh[1]-3],[sh[2]+3,sh[1]-3],[sh[2]+3,sh[3]+3],[sh[0]-3,sh[3]+3],[sh[0]-3,sh[1]-3]],e=[[sh[0],sh[1]],[sh[0],sh[3]],[sh[2],sh[3]],[sh[2],sh[1]],[sh[0],sh[1]]];
    f.push({type:'Feature',properties:{k:'off'},geometry:{type:'Polygon',coordinates:[o,e]}});f.push({type:'Feature',properties:{k:'frame'},geometry:{type:'LineString',coordinates:e}})}
  mv.geo(src,f);
  if(!mv.map.hasImage('rc-grain')) mv.map.addImage('rc-grain',paperGrain(),{pixelRatio:1});
  if(!mv.map.hasImage('rc-bh')) mv.map.addImage('rc-bh',blockhouseIcon(),{pixelRatio:2});
  function add(spec,keep){if(!keep)ids.push(spec.id);spec.source=spec.source||src;spec.layout=spec.layout||{};spec.layout.visibility='none';mv.layer(spec)}
  var zw=function(w){return ['interpolate',['linear'],['zoom'],10,w*0.45,13,w,16,w*2,19,w*4.5]},   // line widths grow with the zoom, as a map drawn at a larger scale would have them
      gw=['interpolate',['exponential',2],['zoom'],6,['*',['get','gw'],px(6)],22,['*',['get','gw'],px(22)]];   // a width on the ground, in metres
  add({id:src+'-paper',type:'background',paint:{'background-pattern':'rc-grain','background-opacity':0.5}});
  /* Relief on a reconstructed map comes from coarser elevation tiles than today's map uses (zoom 11, about 75 m a pixel, enlarged smoothly), so the
     shading shows the lie of the land and not today's buildings, which the fine tiles pick up as bumps on flat ground. */
  if(HS&&!mv.map.getSource('dem-rc')) mv.map.addSource('dem-rc',{type:'raster-dem',tiles:[HS.tiles],encoding:HS.encoding,tileSize:HS.tile_size||256,maxzoom:Math.min(HS.max_zoom||11,R.relief_zoom||11)});
  if(HS&&!mv.map.getLayer('rc-hill')) add({id:'rc-hill',type:'hillshade',source:'dem-rc',paint:{'hillshade-exaggeration':1,'hillshade-illumination-direction':315,'hillshade-shadow-color':'var(--rc-shade)','hillshade-highlight-color':'var(--rc-light)','hillshade-accent-color':'var(--rc-shade)'}},true);
  addTerrainLayers(R);   // a terrain version of this map: its contours go here, under the water and the lines
  add({id:src+'-sea',type:'fill',filter:is('sea'),paint:{'fill-color':'var(--rc-water)','fill-antialias':false}});
  [[2.6,0.9,0.5],[6,0.75,0.36],[10.5,0.6,0.24],[16,0.5,0.14]].forEach(function(q,i){   // lines drawn along the shore, fainter as they go out
    add({id:src+'-lining'+i,type:'line',filter:is('shore'),layout:{'line-join':'round'},paint:{'line-color':'var(--rc-water-ink)','line-width':zw(q[1]),'line-offset':zw(q[0]),'line-opacity':q[2]}})});
  add({id:src+'-water',type:'fill',filter:['any',is('river'),is('water')],paint:{'fill-color':'var(--rc-water)'}});
  add({id:src+'-stream',type:'line',filter:is('stream'),layout:round,paint:{'line-color':'var(--rc-water)','line-width':gw}});
  add({id:src+'-streambank',type:'line',filter:is('stream'),layout:{'line-join':'round'},paint:{'line-color':'var(--rc-water-ink)','line-width':zw(0.9),'line-gap-width':gw}});
  add({id:src+'-bank',type:'line',filter:['any',is('river'),is('water')],layout:{'line-join':'round'},paint:{'line-color':'var(--rc-water-ink)','line-width':zw(1)}});
  /* the period map's own fine lines (street and block edges, dykes, field lines, hachures): thin ink, coming in as the reader zooms in */
  var un=['==',['get','un'],1],giveWay=function(v){return ['case',un,0,v]};   // a traced line that a period map's own ink also draws gives way to it as the ink comes in
  add({id:src+'-detail',type:'line',filter:is('detail'),minzoom:11.4,layout:round,paint:{'line-color':'var(--rc-ink)','line-width':['interpolate',['linear'],['zoom'],11.4,0.3,13,0.55,15,1,17,1.7,19,3],
    'line-opacity':iz<99?['interpolate',['linear'],['zoom'],11.4,0.3,12.5,0.6,iz+0.1,0.72,iz+0.9,giveWay(0.8)]:['interpolate',['linear'],['zoom'],11.4,0.3,12.5,0.6,14,0.8]}});
  add({id:src+'-shore',type:'line',filter:is('shore'),layout:round,paint:{'line-color':'var(--rc-ink)','line-width':zw(1.5),'line-dasharray':['case',['==',['get','lo'],1],['literal',[6,2.2]],['literal',[1,0]]]}});
  add({id:src+'-break',type:'line',filter:is('breakwater'),paint:{'line-color':'var(--rc-ink)','line-width':zw(0.9),'line-gap-width':zw(1.3)}});
  var rw=function(m,o){var by=function(i){return ['match',['get','cls'],'main',m[i],o[i]]};return ['interpolate',['linear'],['zoom'],10,by(0),12,by(1),14,by(2),17,by(3)]};   // zoomed out a road is one ink line; closer in it opens into the double line of the engineer's map
  add({id:src+'-roadedge',type:'line',filter:is('road'),layout:round,paint:{'line-color':'var(--rc-ink)','line-width':rw([1,1.5,3.6,8],[0.6,1,2.6,6])}});
  add({id:src+'-road',type:'line',filter:is('road'),layout:round,paint:{'line-color':'var(--rc-road)','line-width':rw([0,0,1.9,5.2],[0,0,1.1,3.6])}});
  add({id:src+'-rail',type:'line',filter:is('rail'),paint:{'line-color':'var(--rc-ink)','line-width':zw(1.3)}});
  add({id:src+'-ties',type:'line',filter:is('rail'),paint:{'line-color':'var(--rc-ink)','line-width':zw(5.5),'line-dasharray':[0.22,1.9]}});
  add({id:src+'-wallfill',type:'fill',filter:is('wall'),paint:{'fill-color':'var(--rc-town)'}});
  var wop=iz<99?{'line-opacity':['interpolate',['linear'],['zoom'],iz+0.1,1,iz+0.9,giveWay(1)]}:{},wp=function(o){for(var k in wop)o[k]=wop[k];return o};
  add({id:src+'-wall',type:'line',filter:is('wall'),layout:{'line-join':'miter'},paint:wp({'line-color':'var(--rc-wall)','line-width':zw(3.4)})});
  add({id:src+'-wallin',type:'line',filter:is('wall'),layout:{'line-join':'miter'},paint:wp({'line-color':'var(--rc-paper)','line-width':zw(0.9)})});
  if(inks.length){ add({id:src+'-inkslot',type:'background'},true);   // the ink pictures go in here when the reader comes close enough: over the traced roads and walls, under the field works and blockhouses
    add({id:src+'-inkhit',type:'fill',filter:is('ink'),minzoom:iz,paint:{'fill-color':'#000','fill-opacity':0.001}}) }   // nothing to see: it lets a tap on the ink find its record
  add({id:src+'-works',type:'line',filter:is('entrenchment'),paint:{'line-color':'#8c2f25','line-width':zw(3),'line-dasharray':[0.9,0.7]}});   // field works, in the colour of the side that dug them
  add({id:src+'-bh',type:'symbol',filter:is('blockhouse'),layout:{'icon-image':'rc-bh','icon-allow-overlap':true,'icon-size':['interpolate',['linear'],['zoom'],10,0.6,13,0.9,16,1.4]}});
  add({id:src+'-off',type:'fill',filter:is('off'),paint:{'fill-color':'var(--bg)'}});
  add({id:src+'-frame',type:'line',filter:is('frame'),paint:{'line-color':'var(--rc-ink)','line-width':2.4,'line-offset':-5}});
  add({id:src+'-frame2',type:'line',filter:is('frame'),paint:{'line-color':'var(--rc-ink)','line-width':0.9}});
  addTerrainTop(R);
  RCL[R.id]=ids;
}
/* ---------- the terrain version of a reconstructed map ----------
   A base with `terrain` ({recon:id, terrain:{...}}) adds the lie of the land, and adds more of it the closer the reader looks.
   The page reads elevation tiles (the same service as the shading) once, over `extent` (the reconstruction's sheet if none is given), and
   hands them to a background worker. The tiles are a radar surface (SRTM, 2000) that carries the buildings of its day, so the worker
   cleans them first: every bump narrower than about `open_m` (a block, a tower, a dump) is taken off, and what is left is smoothed over
   about `smooth_m`. That leaves the broad lie of the land. It is today's ground, not 1899's, and the map details say so.
   From that surface the worker makes
     - one relief picture for the whole extent: shadow and light in the map's own inks, a faint tint that deepens with height, and,
       beyond the reconstruction's sheet, today's sea;
     - contour lines for what is on screen, afresh whenever the reader moves or zooms: the interval closes in with the zoom (`steps`:
       [zoom, interval in metres, interval of the heavier lines]) and the surface is sampled a few screen pixels apart whatever the zoom,
       so the lines stay smooth curves however close the reader comes; half-metre lines are drawn dashed, as form lines;
     - spot heights: the summits on screen, more of them the closer the reader looks.
   Where `extent` is wider than the sheet the terrain runs on past the sheet's edge and fills the screen at any shape of window; a thin
   dotted line marks where the traced maps stop, and the reader cannot move past the extent. */
var TRN={};
function trnOf(b){b=b||base;var X=b&&b.terrain&&b.rc&&TRN[b.rc.id];return X&&X.state==='ready'?X:null}
function trnWide(b){b=b||base;return !!(b&&b.terrain&&b.terrain.extent&&b.rc)}
var TRN_STEPS=[[0,20,100],[11.2,10,50],[12.4,5,25],[13.4,2,10],[14.4,1,5],[15.6,0.5,5]];
function addTerrainLayers(R){ var T=bases.filter(function(b){return b.terrain&&b.recon===R.id})[0]; if(!T||TRN[R.id]) return;
  var tc=T.terrain,src='rt-'+R.id,X=TRN[R.id]={state:'idle',src:src,T:tc,layers:[],top:[],z:tc.zoom||12,ext:tc.extent||R.sheet,sheet:R.sheet,req:0,busy:false,dirty:false,cur:null,
    steps:(tc.steps||TRN_STEPS).map(function(s){return [s[0],s[1],s[2]||s[1]*5]})};
  mv.geo(src,[]);
  var cls=function(c){return ['==',['get','c'],c]},add=function(spec){spec.source=src;spec.layout={visibility:'none','line-join':'round'};mv.layer(spec);X.layers.push(spec.id)};
  add({id:src+'-c3',type:'line',filter:cls(3),paint:{'line-color':'var(--rc-contour)','line-width':0.8,'line-dasharray':[0.4,2.6],'line-opacity':0.5}});                                 // doubtful: low ground where the radar most likely saw a mass of buildings
  add({id:src+'-c0',type:'line',filter:cls(0),paint:{'line-color':'var(--rc-contour)','line-width':0.6,'line-dasharray':[5,4],'line-opacity':0.6}});                                  // half-metre form lines
  add({id:src+'-c1',type:'line',filter:cls(1),paint:{'line-color':'var(--rc-contour)','line-width':['interpolate',['linear'],['zoom'],10,0.35,13,0.6,16,0.85],'line-opacity':0.8}});
  add({id:src+'-c2',type:'line',filter:cls(2),paint:{'line-color':'var(--rc-contour)','line-width':['interpolate',['linear'],['zoom'],10,0.8,13,1.2,16,1.7]}});                       // the heavier lines
  add({id:src+'-coast',type:'line',filter:cls(9),paint:{'line-color':'var(--rc-water-ink)','line-width':1.1,'line-opacity':0.85}});                                                  // today's shore, beyond the sheet
}
function addTerrainTop(R){ var X=TRN[R.id]; if(!X||!X.T.extent||!R.sheet) return; var sh=R.sheet;   // where the traced maps stop
  mv.geo(X.src+'-lim',[{type:'Feature',properties:{},geometry:{type:'LineString',coordinates:[[sh[0],sh[1]],[sh[0],sh[3]],[sh[2],sh[3]],[sh[2],sh[1]],[sh[0],sh[1]]]}}]);
  mv.layer({id:X.src+'-limit',type:'line',source:X.src+'-lim',layout:{visibility:'none'},paint:{'line-color':'var(--rc-ink)','line-width':1,'line-dasharray':[0.6,3.2],'line-opacity':0.55}}); X.top.push(X.src+'-limit')}
function loadTerrain(R){ var X=TRN[R.id]; if(!X||X.state!=='idle'||!HS) return; X.state='loading';
  var tc=X.T,z=X.z,e=X.ext,n=256*Math.pow(2,z),wx=function(l){return (l+180)/360*n},wy=function(a){var r=a*Math.PI/180;return (1-Math.log(Math.tan(r)+1/Math.cos(r))/Math.PI)/2*n};
  var lat0=(e[1]+e[3])/2,px=EARTH*Math.cos(lat0*Math.PI/180)/n,ro=Math.max(1,Math.round(((tc.open_m||230)/px-1)/2)),rs=Math.max(1,Math.round((tc.smooth_m||60)/px/1.1)),pad=ro+3*rs+3;
  var X0=Math.floor(wx(e[0]))-pad,X1=Math.ceil(wx(e[2]))+pad,Y0=Math.floor(wy(e[3]))-pad,Y1=Math.ceil(wy(e[1]))+pad,W=X1-X0,H=Y1-Y0,g=new Float32Array(W*H),jobs=[];
  var cv=document.createElement('canvas');cv.width=cv.height=256;var cx=cv.getContext('2d',{willReadFrequently:true}),terr=HS.encoding!=='mapbox';
  for(var ty=Math.floor(Y0/256);ty<=Math.floor((Y1-1)/256);ty++)for(var tx=Math.floor(X0/256);tx<=Math.floor((X1-1)/256);tx++)(function(tx,ty){
    var u=HS.tiles.replace('{z}',z).replace('{x}',tx).replace('{y}',ty);
    jobs.push(fetch(u).catch(function(){return fetch(u,{cache:'reload'})}).then(function(r){if(!r.ok)throw new Error(r.status);return r.blob()}).then(createImageBitmap).then(function(im){
      cx.clearRect(0,0,256,256);cx.drawImage(im,0,0);var d=cx.getImageData(0,0,256,256).data;
      for(var j=0;j<256;j++){var y=ty*256+j-Y0;if(y<0||y>=H)continue;for(var i=0;i<256;i++){var x=tx*256+i-X0;if(x<0||x>=W)continue;var k=(j*256+i)*4;
        g[y*W+x]=terr?d[k]*256+d[k+1]+d[k+2]/256-32768:-10000+(d[k]*65536+d[k+1]*256+d[k+2])*0.1}}}))})(tx,ty);
  var ll=function(x,y){return [(X0+x)/n*360-180,Math.atan(Math.sinh(Math.PI*(1-2*(Y0+y)/n)))*180/Math.PI]},fail=function(){X.state='failed';panelKey='';paintFade();mv.kick()};
  function got(m){
    if(m.t==='fail'){ if(X.state!=='ready') fail(); X.busy=false; return }
    if(m.t==='ready'){ var done=function(url){
        mv.map.addSource(X.src+'-img',{type:'image',url:url,coordinates:[ll(0,0),ll(W,0),ll(W,H),ll(0,H)]});
        mv.layer({id:X.src+'-relief',type:'raster',source:X.src+'-img',layout:{visibility:'none'},paint:{'raster-fade-duration':0,'raster-resampling':'linear'}},X.src+'-c3');
        X.layers.unshift(X.src+'-relief'); X.range=[m.lo,m.hi]; X.state='ready'; paintHill(); paintFade(); lastCredit=''; panelKey=''; mv.kick()};
      if(m.blob) done(URL.createObjectURL(m.blob));
      else{var c2=document.createElement('canvas');c2.width=m.w;c2.height=m.h;c2.getContext('2d').putImageData(new ImageData(m.rgba,m.w,m.h),0,0);done(c2.toDataURL('image/png'))}
      return }
    if(m.t==='view'){ X.busy=false; if(m.id!==X.req) return;
      X.cur={key:m.key,box:m.box,labs:m.labs,spots:m.spots,minor:m.st<=1}; mv.map.getSource(X.src).setData({type:'FeatureCollection',features:m.lines}); mv.kick() } }
  Promise.all(jobs).then(function(){ X.eng=terrainEngine(got);
    X.eng({t:'init',g:g,W:W,H:H,X0:X0,Y0:Y0,n:n,px:px,ro:ro,rs:rs,ex:tc.relief||4,sheet:X.sheet,ext:X.ext,wide:!!tc.extent,tint:tc.tint!==false,
      doubt:tc.doubt===false?null:{below:(tc.doubt&&tc.doubt.below_m)||9,rise:(tc.doubt&&tc.doubt.rise_m)||2.5,r:Math.max(1,Math.round((((tc.doubt&&tc.doubt.across_m)||600)/px-1)/2))}},[g.buffer]) }).catch(fail);
}
/* asked on every drawing of the map: contours and spot heights for what is on screen, if what the worker last sent no longer covers it */
function trnTick(){ var X=trnOf(); if(!X) return; var zm=mv.map.getZoom(),b=mv.map.getBounds(),w=b.getWest(),s=b.getSouth(),e=b.getEast(),n=b.getNorth(),st=X.steps[0];
  X.steps.forEach(function(q){if(zm>=q[0])st=q});
  var c=Math.pow(2,zm+1-X.z),cell=Math.max(1/16,Math.min(2,Math.pow(2,Math.round(Math.log2(3.5/c))))),key=st[1]+'|'+st[2]+'|'+cell,cur=X.cur;   // c: screen pixels to a cell of the heights; samples are taken 2.5 to 5 pixels apart
  if(cur&&cur.key===key&&w>=cur.box[0]&&e<=cur.box[2]&&s>=cur.box[1]&&n<=cur.box[3]) return;
  if(X.busy){X.dirty=true;return}
  var mx=(e-w)*0.3,my=(n-s)*0.3,E=X.ext,box=[Math.max(E[0],w-mx),Math.max(E[1],s-my),Math.min(E[2],e+mx),Math.min(E[3],n+my)];
  if(cur&&cur.key===key&&cur.box.join()===box.join()) return;   // already all there is (the screen reaches past the extent)
  X.busy=true; X.dirty=false; X.eng({t:'view',id:++X.req,key:key,box:box,st:st[1],ix:st[2],cell:cell,spots:zm>=(X.T.spots_from||12.6)?Math.max(2,Math.round(22*cell)):0});
}
function terrainEngine(recv){
  try{ var src='var core=('+terrainCore+')(function(m,tr){postMessage(m,tr||[])});onmessage=function(e){try{core(e.data)}catch(x){postMessage({t:"fail",why:String(x)})}}';
    var w=new Worker(URL.createObjectURL(new Blob([src],{type:'text/javascript'}))); w.onmessage=function(e){recv(e.data)}; w.onerror=function(){recv({t:'fail'})};
    return function(m,tr){w.postMessage(m,tr||[])} }
  catch(e){ var core=terrainCore(function(m){setTimeout(function(){recv(m)},0)}); return function(m){setTimeout(function(){try{core(m)}catch(x){recv({t:'fail'})}},0)} }   // no worker to be had: on the page's own thread
}
/* The worker. It stands alone (it is sent to the worker as text), so it uses nothing from the page around it. */
function terrainCore(post){
  var G=null;
  /* take off what is narrower than the opening (the lowest ground near each point, then the highest of those), then smooth (three passes of a box filter, close to a Gaussian) */
  function run(a,W,H,r,f,init){var t=new Float32Array(W*H),o=new Float32Array(W*H),x,y,i,v;
    for(y=0;y<H;y++)for(x=0;x<W;x++){v=init;for(i=-r;i<=r;i++){var xx=x+i;if(xx>=0&&xx<W)v=f(v,a[y*W+xx])}t[y*W+x]=v}
    for(y=0;y<H;y++)for(x=0;x<W;x++){v=init;for(i=-r;i<=r;i++){var yy=y+i;if(yy>=0&&yy<H)v=f(v,t[yy*W+x])}o[y*W+x]=v}return o}
  function box(a,W,H,r){var t=new Float32Array(W*H),o=new Float32Array(W*H),x,y;
    for(y=0;y<H;y++){var s=0,c=0;for(x=0;x<=r&&x<W;x++){s+=a[y*W+x];c++}for(x=0;x<W;x++){t[y*W+x]=s/c;var ad=x+r+1,rm=x-r;if(ad<W){s+=a[y*W+ad];c++}if(rm>=0){s-=a[y*W+rm];c--}}}
    for(x=0;x<W;x++){var s2=0,c2=0;for(y=0;y<=r&&y<H;y++){s2+=t[y*W+x];c2++}for(y=0;y<H;y++){o[y*W+x]=s2/c2;var ad2=y+r+1,rm2=y-r;if(ad2<H){s2+=t[ad2*W+x];c2++}if(rm2>=0){s2-=t[rm2*W+x];c2--}}}return o}
  /* the surface between the cells: a smooth (cubic B-spline) reading of the grid at cw x ch points, the first at (x0, y0) and `cell` cells apart.
     Every picture and every contour is read through this, at whatever spacing the zoom calls for, so they agree with each other. */
  function bw(f){var f2=f*f,f3=f2*f;return [(1-3*f+3*f2-f3)/6,(4-6*f2+3*f3)/6,(1+3*f+3*f2-3*f3)/6,f3/6]}
  function sample(A,x0,y0,cw,ch,cell){var W=G.W,H=G.H,out=new Float32Array(cw*ch),r0=Math.floor(y0)-1,r1=Math.floor(y0+(ch-1)*cell)+2,nr=r1-r0+1,tmp=new Float32Array(nr*cw),i,j,r,k;
    for(i=0;i<cw;i++){var gx=x0+i*cell,ix=Math.floor(gx),w=bw(gx-ix),xs=[0,0,0,0];for(k=0;k<4;k++)xs[k]=Math.max(0,Math.min(W-1,ix-1+k));
      for(r=0;r<nr;r++){var row=Math.max(0,Math.min(H-1,r0+r))*W;tmp[r*cw+i]=w[0]*A[row+xs[0]]+w[1]*A[row+xs[1]]+w[2]*A[row+xs[2]]+w[3]*A[row+xs[3]]}}
    for(j=0;j<ch;j++){var gy=y0+j*cell,iy=Math.floor(gy),v=bw(gy-iy),b=(iy-1-r0)*cw;
      for(i=0;i<cw;i++)out[j*cw+i]=v[0]*tmp[b+i]+v[1]*tmp[b+cw+i]+v[2]*tmp[b+2*cw+i]+v[3]*tmp[b+3*cw+i]}
    return out}
  function lonOf(gx){return (G.X0+gx+0.5)/G.n*360-180} function latOf(gy){return Math.atan(Math.sinh(Math.PI*(1-2*(G.Y0+gy+0.5)/G.n)))*180/Math.PI}
  function gxOf(l){return (l+180)/360*G.n-G.X0-0.5} function gyOf(a){var r=a*Math.PI/180;return (1-Math.log(Math.tan(r)+1/Math.cos(r))/Math.PI)/2*G.n-G.Y0-0.5}
  /* lines of equal value through a grid (marching squares), joined end to end. levels(mn,mx) lists the values to draw through a cell
     whose corners run from mn to mx; skip(i,j) leaves a cell out. Returns [{L:value, p:[[x,y],...]}] in grid steps. */
  function iso(F,cw,ch,levels,skip){ var lv={},order=[],x,y;
    for(y=0;y<ch-1;y++)for(x=0;x<cw-1;x++){ var o=y*cw+x,a=F[o],b=F[o+1],c=F[o+cw+1],d=F[o+cw],mn=Math.min(a,b,c,d),mx=Math.max(a,b,c,d); if(mn===mx||(skip&&skip(o))) continue;
      var Ls=levels(mn,mx); for(var q=0;q<Ls.length;q++){ var L=Ls[q],idx=(a>=L?8:0)|(b>=L?4:0)|(c>=L?2:0)|(d>=L?1:0); if(idx===0||idx===15) continue;
        var T=o*2,Bm=(o+cw)*2,Le=o*2+1,Ri=(o+1)*2+1,segs;   // the cell's edges: top, bottom, left, right
        switch(idx){case 1:case 14:segs=[[Le,Bm]];break;case 2:case 13:segs=[[Bm,Ri]];break;case 3:case 12:segs=[[Le,Ri]];break;case 4:case 11:segs=[[T,Ri]];break;
          case 6:case 9:segs=[[T,Bm]];break;case 7:case 8:segs=[[Le,T]];break;
          case 5:segs=(a+b+c+d)/4>=L?[[Le,T],[Bm,Ri]]:[[Le,Bm],[T,Ri]];break;default:segs=(a+b+c+d)/4>=L?[[Le,Bm],[T,Ri]]:[[Le,T],[Bm,Ri]]}
        var g=lv[L]; if(!g){g=lv[L]={L:L,s:[],p:{}};order.push(g)}
        for(var s=0;s<segs.length;s++){ for(var e=0;e<2;e++){var k=segs[s][e]; if(g.p[k]===undefined){var cell=k>>1,ex=cell%cw,ey=(cell/cw)|0,v0=F[cell],v1=(k&1)?F[cell+cw]:F[cell+1],f=(L-v0)/(v1-v0);g.p[k]=(k&1)?[ex,ey+f]:[ex+f,ey]}} g.s.push(segs[s]) } } }
    var out=[];
    order.forEach(function(g){var by={},used=new Uint8Array(g.s.length),i;
      for(i=0;i<g.s.length;i++){var s=g.s[i];(by[s[0]]||(by[s[0]]=[])).push(i);(by[s[1]]||(by[s[1]]=[])).push(i)}
      for(i=0;i<g.s.length;i++){ if(used[i]) continue; used[i]=1; var line=[g.s[i][0],g.s[i][1]];
        for(var end=1;end>=0;end--){ for(;;){var k=end?line[line.length-1]:line[0],c2=by[k],nx=-1;for(var j=0;j<c2.length;j++)if(!used[c2[j]]){nx=c2[j];break} if(nx<0)break; used[nx]=1;
          var o2=g.s[nx][0]===k?g.s[nx][1]:g.s[nx][0]; if(end)line.push(o2);else line.unshift(o2)} }
        if(line.length>=4) out.push({L:g.L,p:line.map(function(k){return g.p[k]})}) } });
    return out}
  function init(m){ var W=m.W,H=m.H,g=m.g,i,j,N=W*H,wet=new Float32Array(N);
    for(i=0;i<N;i++) wet[i]=g[i]<=0.01?1:0;                                                   // the radar survey sets the sea to nothing at all
    wet=run(run(wet,W,H,1,Math.min,1),W,H,1,Math.max,0);                                        // less the specks: water narrower than three cells
    var op=run(run(g,W,H,m.ro,Math.min,1e9),W,H,m.ro,Math.max,-1e9),S=box(box(box(op,W,H,m.rs),W,H,m.rs),W,H,m.rs),off=new Float32Array(N); for(i=0;i<N;i++) off[i]=g[i]-op[i];   // what the cleaning took off: much of it means buildings
    /* Doubtful ground. A rise that stands well clear of low, flat ground and is narrower than `across` is, on a delta under a modern city, almost
       always a mass of buildings the cleaning could not take off. It is marked, so its contours can be drawn as doubtful and no height given. */
    var dbt=new Float32Array(N); if(m.doubt){ var fl=run(run(g,W,H,m.doubt.r,Math.min,1e9),W,H,m.doubt.r,Math.max,-1e9); fl=box(box(box(fl,W,H,m.rs),W,H,m.rs),W,H,m.rs);
      for(i=0;i<N;i++) dbt[i]=(g[i]>0.01&&fl[i]<m.doubt.below&&S[i]-fl[i]>m.doubt.rise)?1:0; dbt=box(dbt,W,H,1) }
    G={S:S,M:wet,D:dbt,B:box(box(off,W,H,4),W,H,4),W:W,H:H,X0:m.X0,Y0:m.Y0,n:m.n,px:m.px,sheet:m.sheet,wide:m.wide};
    /* the relief picture, two points to a cell */
    var cw=W*2,ch=H*2,F=sample(S,-0.25,-0.25,cw,ch,0.5),K=sample(wet,-0.25,-0.25,cw,ch,0.5),d=new Uint8ClampedArray(cw*ch*4),p2=m.px/2,az=315*Math.PI/180,zen=45*Math.PI/180,flat=Math.cos(zen),lo=1e9,hi=-1e9;
    var sh=m.sheet,sx0=sh?(gxOf(sh[0])+0.5)*2:0,sx1=sh?(gxOf(sh[2])+0.5)*2:0,sy0=sh?(gyOf(sh[3])+0.5)*2:0,sy1=sh?(gyOf(sh[1])+0.5)*2:0;
    for(j=1;j<ch-1;j++)for(i=1;i<cw-1;i++){ var o=j*cw+i,h=F[o],k=o*4,dzx=(F[o+1]-F[o-1])/(2*p2)*m.ex,dzy=(F[o+cw]-F[o-cw])/(2*p2)*m.ex,gm=Math.sqrt(dzx*dzx+dzy*dzy),sq=1/(1+gm/1.6);   // steep ground is eased, so hills do not go black
      dzx*=sq;dzy*=sq; var sl=Math.atan(Math.sqrt(dzx*dzx+dzy*dzy)),asp=Math.atan2(dzy,-dzx),v=Math.cos(zen)*Math.cos(sl)+Math.sin(zen)*Math.sin(sl)*Math.cos(az-Math.PI/2-asp)-flat;
      if(h<lo)lo=h; if(h>hi)hi=h;
      var at=m.tint&&h>0?0.30*(1-Math.exp(-h/45)):0,as=v<0?Math.min(0.72,-v*2.2):Math.min(0.46,v*1.65),sr=v<0?84:255,sg=v<0?58:250,sb=v<0?30:232,oa=as+at*(1-as);   // tint (176,128,70), deeper with height; the shade over it
      var r=oa?(sr*as+176*at*(1-as))/oa:0,gg=oa?(sg*as+128*at*(1-as))/oa:0,bb=oa?(sb*as+70*at*(1-as))/oa:0;
      if(m.wide&&K[o]>0.35&&!(i>=sx0&&i<sx1&&j>=sy0&&j<sy1)){ var aw=Math.min(1,(K[o]-0.35)/0.3),na=aw+oa*(1-aw);   // today's sea, beyond the sheet only: inside it the 1899 water is traced
        r=(191*aw+r*oa*(1-aw))/na;gg=(208*aw+gg*oa*(1-aw))/na;bb=(204*aw+bb*oa*(1-aw))/na;oa=na }
      d[k]=r;d[k+1]=gg;d[k+2]=bb;d[k+3]=oa*255 }
    var msg={t:'ready',w:cw,h:ch,lo:lo,hi:hi};
    if(typeof OffscreenCanvas!=='undefined'&&typeof ImageData!=='undefined'){ try{ var cv=new OffscreenCanvas(cw,ch);cv.getContext('2d').putImageData(new ImageData(d,cw,ch),0,0);
        cv.convertToBlob({type:'image/png'}).then(function(b){msg.blob=b;post(msg)},function(){msg.rgba=d;post(msg,[d.buffer])}); return }catch(e){} }
    msg.rgba=d; post(msg,[d.buffer]) }
  function view(m){ var cell=m.cell,W=G.W,H=G.H,x0=Math.max(0,Math.floor(gxOf(m.box[0])/cell)*cell),x1=Math.min(W-1,Math.ceil(gxOf(m.box[2])/cell)*cell),y0=Math.max(0,Math.floor(gyOf(m.box[3])/cell)*cell),y1=Math.min(H-1,Math.ceil(gyOf(m.box[1])/cell)*cell);
    var cw=Math.round((x1-x0)/cell)+1,ch=Math.round((y1-y0)/cell)+1,out={t:'view',id:m.id,key:m.key,box:m.box,st:m.st,lines:[],labs:[],spots:[]}; if(cw<2||ch<2){post(out);return}
    var F=sample(G.S,x0,y0,cw,ch,cell),K=sample(G.M,x0,y0,cw,ch,cell),Dk=sample(G.D,x0,y0,cw,ch,cell),st=m.st,ix2=Math.round(m.ix*2),Q=96,sh=G.sheet,r6=function(v){return Math.round(v*1e6)/1e6};
    var LL=function(p){return [r6(lonOf(x0+p[0]*cell)),r6(latOf(y0+p[1]*cell))]};
    /* the grid of the labels: a height is written where a line crosses every 96th row or column of points, counted from the corner of the heights, so it stays put as the reader moves */
    var gx0=Math.round(x0/cell),gy0=Math.round(y0/cell);
    var lev=function(mn,mx){var o=[],L=Math.ceil(mn/st)*st;if(L<=0)L=st;for(;L<=mx;L+=st)o.push(L);return o},wetAt=function(o){return (K[o]+K[o+1]+K[o+cw]+K[o+cw+1])>2},dbtAt=function(o){return (Dk[o]+Dk[o+1]+Dk[o+cw]+Dk[o+cw+1])>2};
    iso(F,cw,ch,lev,function(o){return wetAt(o)||!dbtAt(o)}).forEach(function(c){ if(Math.round(c.L*2)%2===0) out.lines.push({type:'Feature',properties:{e:c.L,c:3},geometry:{type:'LineString',coordinates:c.p.map(LL)}}) });   // doubtful ground: whole metres only, drawn dotted, no heights
    iso(F,cw,ch,lev,function(o){return wetAt(o)||dbtAt(o)}).forEach(function(c){
      var L2=Math.round(c.L*2),cl=L2%ix2===0?2:(L2%2?0:1),pts=c.p.map(LL); out.lines.push({type:'Feature',properties:{e:c.L,c:cl},geometry:{type:'LineString',coordinates:pts}});
      if(cl===0) return;
      for(var i=1;i<c.p.length;i++){var a=c.p[i-1],b=c.p[i],ka=Math.floor((gx0+a[0])/Q),kb=Math.floor((gx0+b[0])/Q),hit=ka!==kb; if(!hit){ka=Math.floor((gy0+a[1])/Q);kb=Math.floor((gy0+b[1])/Q);hit=ka!==kb}
        if(hit) out.labs.push([pts[i][0],pts[i][1],pts[i-1][0],pts[i-1][1],c.L,cl])} });
    if(G.wide) iso(K,cw,ch,function(mn,mx){return mn<0.5&&mx>=0.5?[0.5]:[]}).forEach(function(c){ var runs=[[]];   // today's shore, kept only beyond the sheet
      c.p.map(LL).forEach(function(q){ if(sh&&q[0]>sh[0]&&q[0]<sh[2]&&q[1]>sh[1]&&q[1]<sh[3]){if(runs[runs.length-1].length)runs.push([])} else runs[runs.length-1].push(q) });
      runs.forEach(function(r){if(r.length>1)out.lines.push({type:'Feature',properties:{e:0,c:9},geometry:{type:'LineString',coordinates:r}})}) });
    if(m.spots){ var R=m.spots,S=G.S,M=G.M,ax=Math.max(1,Math.ceil(x0)),bx=Math.min(W-2,Math.floor(x1)),ay=Math.max(1,Math.ceil(y0)),by=Math.min(H-2,Math.floor(y1)),x,y;   // summits: the highest point for R cells around, standing well clear of the ground about it
      for(y=ay;y<=by;y++)for(x=ax;x<=bx;x++){ var o=y*W+x,v=S[o]; if(v<3||M[o]>0.5||G.D[o]>0.3||G.B[o]>(m.rough||3)) continue;   // no height is given where the radar saw mostly buildings
        if(v<S[o-1]||v<=S[o+1]||v<S[o-W]||v<=S[o+W]||v<S[o-W-1]||v<S[o-W+1]||v<=S[o+W-1]||v<=S[o+W+1]) continue;
        var top=true,low=v,yy,xx; for(yy=Math.max(0,y-R);top&&yy<=Math.min(H-1,y+R);yy++)for(xx=Math.max(0,x-R);xx<=Math.min(W-1,x+R);xx++){var u=S[yy*W+xx]; if(u>v||(u===v&&yy*W+xx<o)){top=false;break} if(u<low)low=u}
        if(top&&v-low>=Math.max(1.5,v*0.06)) out.spots.push([r6(lonOf(x)),r6(latOf(y)),Math.round(v)]) } }
    post(out) }
  return function(m){ if(m.t==='init') init(m); else if(m.t==='view'&&G) view(m) }
}
/* the heights written along the contour lines, and the spot heights: drawn with the names, where there is room */
function contourNames(L){ var X=trnOf(); if(!X||!X.cur) return ''; var z=mv.size(),h='',n=0,C=X.cur;
  C.spots.forEach(function(sp){ var p=S(B.fromLL(sp)); if(p[0]<8||p[1]<8||p[0]>z.w-8||p[1]>z.h-8) return; var tw=String(sp[2]).length*6+4,r=[p[0]-3,p[1]-12,p[0]+5+tw,p[1]+3]; if(L.hit(r)) return; L.keep(r);
    h+='<circle class="sh" cx="'+f1(p[0])+'" cy="'+f1(p[1])+'" r="1.6"/><text class="st" x="'+f1(p[0]+4.5)+'" y="'+f1(p[1]-2.5)+'">'+sp[2]+'</text>' });
  C.labs.forEach(function(a){ if(n>=44||(a[5]<2&&!C.minor)) return; var p=S(B.fromLL(a)); if(p[0]<22||p[1]<22||p[0]>z.w-22||p[1]>z.h-22) return;
    var p2=S(B.fromLL([a[2],a[3]])),g=Math.atan2(p2[1]-p[1],p2[0]-p[0])*180/Math.PI; if(g>90)g-=180; if(g<-90)g+=180;
    var tw=String(a[4]).length*6.2+8,r=[p[0]-tw/2,p[1]-8,p[0]+tw/2,p[1]+8]; if(L.hit(r)) return; L.keep(r); n++;
    h+='<text class="cl'+(a[5]<2?' m':'')+'" text-anchor="middle" transform="translate('+f1(p[0])+' '+f1(p[1])+') rotate('+f1(g)+')" y="3.5">'+a[4]+'</text>' });
  return h}
/* ---------- a period map's own ink, laid over a reconstruction for the closest zooms ----------
   A feature of kind `ink` is a picture, not a line: every dark mark of a period map with the paper made clear, laid on the ground by its
   four corners. It comes in from its `from_zoom`, where the reconstruction's own traced lines run out of detail, so that zooming in keeps
   showing more: blocks, public buildings, street names. `files` lists the picture at several sizes ([zoom, file], smallest first), each
   fetched only when the reader comes that close. Traced features marked `under` (the same lines, drawn more coarsely) give way to it. */
var INKS={};
/* is this place under an ink picture that is showing its own lettering (from its second size up)? */
function inkNames(p){ var R=base.rc,K=R&&INKS[R.id]; if(!K||!K.length) return false; var zm=mv.map.getZoom(),q=B.toLL(p);
  return K.some(function(k){ if(!k.lv[1]||zm<k.lv[1].z+0.3) return false; var c=k.corners,s=0;
    for(var i=0;i<4;i++){var a=c[i],b=c[(i+1)%4];s+=((b[0]-a[0])*(q[1]-a[1])-(b[1]-a[1])*(q[0]-a[0]))<0?1:-1} return Math.abs(s)===4 }) }
function inkTick(){ var R=base.rc; if(!R||!INKS[R.id]) return; var zm=mv.map.getZoom(),src='rc-'+R.id;
  INKS[R.id].forEach(function(K){ K.lv.forEach(function(v,i){ if(v.asked||zm<v.z-0.5) return; v.asked=true; var im=new Image(),id=src+'-ink-'+K.n+'-'+i,nx=K.lv[i+1];
    im.onload=function(){ var cv=document.createElement('canvas');cv.width=im.naturalWidth;cv.height=im.naturalHeight;var c2=cv.getContext('2d');c2.drawImage(im,0,0);
      try{c2.getImageData(0,0,1,1)}catch(e){return}   // a picture the browser will not let the map read (served from elsewhere without leave): left out
      mv.map.addSource(id,{type:'canvas',canvas:cv,coordinates:K.corners,animate:false});
      var full=nx?(i?0.8:0.7):0.86,op=['interpolate',['linear'],['zoom'],v.z,0,v.z+(i?0.35:0.6),full]; if(nx) op=op.concat([nx.z+0.15,full,nx.z+0.5,0]);   // the smaller pictures a little paler, as the lines crowd
      mv.layer({id:id,type:'raster',source:id,layout:{visibility:base.rc===R?'visible':'none'},paint:{'raster-fade-duration':0,'raster-resampling':'linear','raster-opacity':op}},src+'-inkslot');
      RCL[R.id].push(id); mv.kick() };
    im.onerror=function(){if(window.console)console.warn('WarMapper: could not load the picture '+v.file)};
    var u=WM.asset(v.file); if(!/^data:/.test(u)) im.crossOrigin='anonymous'; im.src=u }) });
}
/* tapping a line of a reconstructed map: its details go in the text pane */
var RC_PICK=['-bh','-works','-wall','-wallfill','-roadedge','-rail','-ties','-shore','-break','-stream','-water','-detail','-inkhit','-sea'];
function pickRecon(pt){ if(!base.rc) return null; var src='rc-'+base.rc.id,ls=RC_PICK.map(function(x){return src+x}).filter(function(id){return mv.map.getLayer(id)}),r=coarse?9:5;
  var hit=mv.map.queryRenderedFeatures([[pt.x-r,pt.y-r],[pt.x+r,pt.y+r]],{layers:ls}),best=null,rank=function(f){var i=RC_PICK.indexOf(f.layer.id.slice(src.length));return i<0?99:i};
  hit.forEach(function(f){if(RCF[f.properties.id]&&(!best||rank(f)<rank(best)))best=f});return best?best.properties.id:null}
var coarse=window.matchMedia&&matchMedia('(pointer:coarse)').matches;
function featureHtml(){var x=RCF[rcSel],R=base.rc,L=R.layers.filter(function(l){return l.id===x.layer})[0]||{},s=B.sources[x.source]||{},row=function(k,v){return v?'<dt>'+k+'</dt><dd>'+v+'</dd>':''};
  var M={traced:'Traced: read point by point from the map',  'AI-extracted':'AI-extracted: separated from the scan by a program, then checked by eye',interpolated:'Interpolated: not on any map'};
  var h='<button class="back" id="back">&larr; All units</button><div class="eyebrow">On the reconstructed map</div><h2>'+esc(x.name||x.desc||L.title||x.kind)+'</h2>';
  if(x.name&&x.desc) h+='<p>'+esc(x.desc)+'</p>';
  h+='<div class="state inferred"><b>A reconstruction</b>Drawn by WarMapper from the source below. It is not a line on a period map.</div>';
  h+='<h3>How sure</h3><dl>'+row('Layer',esc(L.title||x.layer))+row('How read',esc(M[x.method]||x.method))+row('Confidence',chip(x.confidence)+(x.precision_m?' good to about '+x.precision_m+' m':''))+row('As of',esc(spanText(x.from,x.to)))+row('Review',esc(x.review||''))+'</dl>';
  if(x.basis) h+='<h3>How it was read</h3><p>'+esc(x.basis)+'</p>';
  var sl=WM.srcList(B.sources,[x.source]); if(sl) h+='<h3>Source</h3><ul class="srcs">'+sl+'</ul>';
  if(L.link) h+='<p style="margin-top:10px"><a href="'+esc(L.link)+'" target="_blank" rel="noopener">Open the original map: '+esc(L.link_label||s.title||'the scan')+'</a></p>';
  return h+'<p class="meta" style="margin-top:12px">Record '+esc(x.id)+' of '+esc(R.file||R.id)+'.</p>'}
function spanText(a,b){var d=function(s){return s?(+s.slice(8,10))+' '+['January','February','March','April','May','June','July','August','September','October','November','December'][+s.slice(5,7)-1]+' '+s.slice(0,4):''};return a&&b&&a!==b?d(a).replace(/ [A-Z][a-z]+ \d{4}$/,a.slice(0,7)===b.slice(0,7)?'':'$&')+' to '+d(b):d(a||b)}
function terrainText(){var X=base.rc&&TRN[base.rc.id],T=base.terrain,st=(X&&X.steps)||[];
  if(!X||X.state==='failed') return 'The elevation service could not be reached, so this version shows no relief or contours.';
  if(X.state!=='ready') return 'Loading the heights.';
  var iv=[],half=false; st.forEach(function(q){if(q[1]<1)half=true;else if(iv.indexOf(q[1])<0)iv.push(q[1])});
  return 'Relief, contour lines and spot heights worked out by this page from today\'s elevation data ('+esc(HS.credit)+')'+(T.about?'. '+esc(T.about)+' ':   // a battle's own words on what its heights are (Cowpens); else Manila's
     ', a radar survey of 2000 that measured the tops of buildings as well as the ground. Bumps narrower than about '+(T.open_m||230)+' m (blocks, towers, the Tondo dump) are taken off and the rest smoothed over about '+(T.smooth_m||60)+' m, which leaves the broad lie of the land: today\'s ground, little changed since 1899 away from the shore. '
    +'Heights are in metres, good to a few metres at best. Where buildings stand thick the ground may read some metres too high. Dotted contours mark low ground where the radar most likely saw a mass of buildings, not a rise: old Manila stands on low, nearly flat ground, so do not read those as hills. No height is written there. ')
    +'The closer you look, the more is drawn: contours every '+iv.join(', then ')+' m'+(half?', and closest in dashed form lines every half metre':'')+'; every fifth line is heavier and carries its height; summits are marked with theirs. Read the ridges where the contours bend downhill, the valleys where they bend uphill.'
    +(trnWide()?' '+(T.beyond?esc(T.beyond):'Beyond the dotted line the traced maps of 1899 stop. Only relief, contours and today\'s shore are drawn there, so the map fills the window; the reclaimed land south and north of the sheet is today\'s, not 1899\'s.'):'')}
function reconDetails(){var R=base.rc,row=function(k,v){return v?'<dt>'+k+'</dt><dd>'+v+'</dd>':''},used=[],h='<h2>'+esc(R.title)+'</h2>';
  h+='<div class="state inferred"><b>A reconstruction, not a period map</b>'+esc(R.about||'Drawn by WarMapper from traced lines.')+'</div>';
  if(R.note) h+='<p>'+esc(R.note)+'</p>';
  h+='<dl>'+row('Battle',esc(B.title))+row('Made',esc(spanText(R.made,R.made)))+row('Review',esc(R.review||''))+row('Relief',base.terrain?terrainText():hsRc?'Shaded from today\'s elevation data ('+esc(HS.credit)+'), which also picks up today\'s buildings. The ground itself has changed little.':(HS?'Off, or the elevation service could not be reached.':'None.'))+'</dl>';
  h+='<h3>What is drawn, and where each layer came from</h3><ul class="rcl">';
  R.layers.forEach(function(l){var s=B.sources[l.source]||{};if(used.indexOf(l.source)<0)used.push(l.source);
    h+='<li><b>'+esc(l.title)+'</b><span class="meta">'+esc(l.method)+' &middot; '+chip(l.confidence)+(l.features?' &middot; '+l.features+(l.features===1?' feature':' features'):'')+'</span><span>'+esc(l.how||'')+'</span>'
      +(l.link?'<a href="'+esc(l.link)+'" target="_blank" rel="noopener">'+esc(l.link_label||'Open the original map')+'</a>':'')+'</li>'});
  h+='</ul><h3>Sources</h3><ul class="srcs">'+WM.srcList(B.sources,used)+'</ul>';
  return h+'<p class="meta" style="margin-top:12px">Tap any line on the map for its own source, how it was read and how sure it is.'+(R.features.some(function(x){return x.kind==='shore'})?' Dashed shore lines are low confidence.':'')+' The lines are in '+esc(R.file||'the battle file')+'.</p>'}
/* The period map can be turned down to let today's map show through it. Turned down, only a map's whole-sheet picture shows, so two pictures of one map do not add up. */
function through(){return opac<1&&!base.current&&!base.own&&!base.sat&&!base.rc}
function paintFade(){(PICS[base.id]||[]).forEach(function(p){mv.opacity(p.id,opac>=1?1:p.detail?0:opac)});if(series.length)mv.opacity('pic-series',opac);
  bases.forEach(function(b){if(b.sat)mv.map.setLayoutProperty('sat-'+b.id,'visibility',b===base?'visible':'none')});
  var cur=!!(base.current||base.backdrop==='current'||through()),own=cur&&!topo();   // the battle's own drawing of today's ground shows only when the modern map cannot
  for(var rk in RCL) RCL[rk].forEach(function(id){mv.show(id,!!base.rc&&base.rc.id===rk)});
  for(var tk in TRN){ var tx=TRN[tk],ton=!!base.terrain&&!!base.rc&&base.rc.id===tk,wide=ton&&tx.state==='ready'&&trnWide();   // the terrain version's relief and contours
    tx.layers.forEach(function(id){mv.show(id,ton)}); tx.top.forEach(function(id){mv.show(id,wide)});
    if(wide)['-off','-frame','-frame2'].forEach(function(x){mv.show('rc-'+tk+x,false)}) }   // past the sheet's edge the terrain runs on: no frame, and nothing blanked
  CUR.forEach(function(id){mv.show(id,own)});mv.show('b-mask',!topo()&&(cur||base.sat)&&!!(base.clip||(base.m&&P.bounds===base.map)));
  mv.bg(base.rc?'--rc-paper':(base.own||(base.m&&base.backdrop!=='current'&&!through()))?'--m-paper':'--land')}
function setOpacity(v){opac=Math.max(0,Math.min(1,v));var e=$('opac');if(e)e.value=Math.round(opac*100);var o=$('opv');if(o)o.textContent=Math.round(opac*100)+'%';paintFade();updateTiles();mv.retheme();mv.kick()}
/* ---------- full detail: the scan itself, streamed from the library that holds it ---------- */
/* The pictures that come with a playback are reduced copies. Where the holding library serves the full scan as tiles (the IIIF image
   service named in the battle file), the tiles for the part on screen are laid over the picture once the reader zooms in past what the
   picture can show. If the library cannot be reached, nothing changes: the reduced picture stays. */
var TILES={},tileSeq=0,tileFail=0,tilesOff=false,tileTimer=0;
function scanOf(){var m=base.m;return (m&&m.raw.iiif&&!tilesOff)?m:null}
function scanFrame(m){ // how the scan's pixels sit in the frame: the region lies on the map's first picture
  var I=m.raw.iiif,r=I.region,c;
  if(m.own) c=[[0,0],[m.size[0],0],[0,m.size[1]]]; else{var q=m.images[0].ll.map(B.fromLL);c=[q[0],q[1],q[3]]}   // top-left, top-right, bottom-left
  var ux=[(c[1][0]-c[0][0])/(r[2]-r[0]),(c[1][1]-c[0][1])/(r[2]-r[0])],uy=[(c[2][0]-c[0][0])/(r[3]-r[1]),(c[2][1]-c[0][1])/(r[3]-r[1])],det=ux[0]*uy[1]-ux[1]*uy[0];
  return {r:r,per:Math.hypot(ux[0],ux[1]),   // frame units per scan pixel
    toF:function(X,Y){X-=r[0];Y-=r[1];return [c[0][0]+ux[0]*X+uy[0]*Y,c[0][1]+ux[1]*X+uy[1]*Y]},
    fromF:function(p){var dx=p[0]-c[0][0],dy=p[1]-c[0][1];return [r[0]+(dx*uy[1]-dy*uy[0])/det,r[1]+(dy*ux[0]-dx*ux[1])/det]}}}
function scanScale(m){return mv.scale()*scanFrame(m).per}   // screen pixels per scan pixel
function updateTiles(){
  var m=scanOf(),want={},k;
  if(m&&opac>=1){var I=m.raw.iiif,F=scanFrame(m),toLL=WORLDS[worldOf(base)].toLL,s=mv.scale()*F.per,
      inv=m.own?function(q){return [q.lng/SKK,-q.lat/SKK]}:function(q){return B.fromLL([q.lng,q.lat])};
    var have=I.reduced,ctr=inv(mv.map.getCenter());   // how much of the scan's detail the pictures already give at the middle of the screen
    m.images.forEach(function(im){if(im.reduced>have&&im.box&&ctr[0]>im.box[0]&&ctr[0]<im.box[2]&&ctr[1]>im.box[1]&&ctr[1]<im.box[3])have=im.reduced});
    if(s>have*1.08){
      var sf=1; I.scale_factors.forEach(function(f){if(f<=1/s&&f>sf)sf=f});   // the coarsest level that still has a scan pixel for every screen pixel
      var z=mv.size(),x0=1e9,y0=1e9,x1=-1e9,y1=-1e9,r=F.r,T=I.tile*sf;
      [[0,0],[z.w,0],[z.w,z.h],[0,z.h]].forEach(function(c){var p=F.fromF(inv(mv.map.unproject(c)));x0=Math.min(x0,p[0]);y0=Math.min(y0,p[1]);x1=Math.max(x1,p[0]);y1=Math.max(y1,p[1])});
      x0=Math.max(x0,r[0]);y0=Math.max(y0,r[1]);x1=Math.min(x1,r[2])-0.01;y1=Math.min(y1,r[3])-0.01;
      if(x1>x0&&y1>y0&&(Math.floor(x1/T)-Math.floor(x0/T)+1)*(Math.floor(y1/T)-Math.floor(y0/T)+1)<=48)
        for(var i=Math.floor(x0/T);i<=Math.floor(x1/T);i++)for(var j=Math.floor(y0/T);j<=Math.floor(y1/T);j++){
          var ax=Math.max(i*T,r[0]),ay=Math.max(j*T,r[1]),bx=Math.min((i+1)*T,r[2]),by=Math.min((j+1)*T,r[3]); if(bx-ax<2||by-ay<2) continue;
          want[m.id+'/'+sf+'/'+i+'/'+j]={url:I.service+'/'+ax+','+ay+','+(bx-ax)+','+(by-ay)+'/'+Math.ceil((bx-ax)/sf)+',/0/default.jpg',q:[F.toF(ax,ay),F.toF(bx,ay),F.toF(bx,by),F.toF(ax,by)].map(toLL)}}
    }}
  for(k in TILES) if(!want[k]){if(mv.map.getLayer(TILES[k]))mv.map.removeLayer(TILES[k]);if(mv.map.getSource(TILES[k]))mv.map.removeSource(TILES[k]);delete TILES[k]}
  for(k in want) if(!TILES[k]){var id='iiif-'+(tileSeq++);TILES[k]=id;
    mv.map.addSource(id,{type:'image',url:want[k].url,coordinates:want[k].q});
    mv.layer({id:id,type:'raster',source:id,paint:{'raster-fade-duration':0,'raster-resampling':'linear','raster-brightness-max':function(c){return +c('--raster-max')||1}}},'iiif-slot')}
  var b11=$('z11'); if(b11){b11.hidden=!m&&!sheetOf(base);b11.title=sheetOf(base)?'The engraving as printed, unstretched, at full detail':'Full detail: one pixel of the scan to one pixel of the screen'}
}
function queueTiles(){clearTimeout(tileTimer);tileTimer=setTimeout(updateTiles,160)}
function tileError(e){ // three failures and the library is left alone for the rest of the visit
  if(e&&(e.sourceId==='dem'||e.sourceId==='dem-rc')){ if(++hsFail>=4){hsVis=null;hsRc=null;mv.show('hill',false);if(mv.map.getLayer('rc-hill'))mv.show('rc-hill',false);lastCredit='';panelKey='';mv.kick()} return }
  if(e&&e.sourceId==='sur'){ if(++modFail>=4&&!modOff){modOff=true;modOn=null;mv.show('sur',false);paintFade();lastCredit='';panelKey='';flashCredit();mv.kick()} return }   // the modern map cannot be reached: fall back to the drawing
  var er=e&&e.error,txt=String((er&&(er.url||er.message))||''),mine=(e&&/^iiif-/.test(String(e.sourceId||'')))||/iiif/i.test(txt)||(Object.keys(TILES).length&&/fetch|network|load/i.test(txt));
  if(mine&&++tileFail>=3&&!tilesOff){tilesOff=true;updateTiles();panelKey='';mv.kick()}}
function setBase(b,first){
  if(typeof b==='string') b=bases.filter(function(x){return x.id===b})[0]; if(!b) return;
  var moved=first||worldOf(b)!==worldOf(base); base=b; flashCredit(); if(b.terrain&&b.rc) loadTerrain(b.rc);
  var tc=$('typeCur');if(tc){var tb=b.of?bases.filter(function(x){return x.id===b.of})[0]||b:b;tc.textContent=tb.label}
  bases.forEach(function(x){if(!x.of)press('b-'+x.id,x===b||b.of===x.id);(PICS[x.id]||[]).forEach(function(p){mv.show(p.id,x===b)})});
  if(moved) mv.setWorld(worldOf(b));
  if(!b.series&&series.length){mv.show('pic-series',false);seriesShown=null}
  if(b.series) series.forEach(function(m){if(!m.pre){m.pre=new Image();m.pre.src=WM.asset(m.images[0].file)}});
  wrap.classList.toggle('paper',!b.current&&!b.sat); wrap.classList.toggle('sat',b.sat); wrap.classList.toggle('recon',!!b.rc); var go=$('gOpac'); if(go) go.hidden=!!(b.current||b.own||b.sat||b.rc); paintFade();
  rcSel=null;
  if(moved) mv.jump(home());
  updateTiles(); panelKey=''; mv.retheme(); mv.kick()}

/* ---------- panel ---------- */
function curEvent(){return B.eventAt(stamp(t))}
function paintNarr(){var n=$('narr'),ev=curEvent(),tx=ev?ev.text:B.opening.text; n.hidden=!narrOn||!tx; if(narrOn&&tx) n.innerHTML=(ev?'<b>'+esc(ev.name)+'.</b> ':'')+esc(tx)}
function whenText(v){if(byDay){var d=B.dateOf(v);return d.day+' '+d.mon.slice(0,3)}return WM.fmtClock(v)}
function toEvent(dir){var eps=byDay?0.01:0.5,hit=null;B.events.forEach(function(e){if(dir>0?(e.t>t+eps&&!hit):(e.t<t-eps))hit=e});if(hit){clk.setPlaying(false);clk.setTime(hit.t)}}
function nowText(){if(byDay){var d=B.dateOf(stamp(t));return d.day+' '+d.mon}return WM.fmtClock(t)}
function cap(s){return s.charAt(0).toUpperCase()+s.slice(1)}
function rowHtml(k,head){
  var h='<h3>'+esc(head)+' <span class="rid">row '+esc(k.id)+'</span></h3><p><b>'+esc(k.act)+'.</b> '+esc(k.place)+'</p>';
  if(k.say) h+='<blockquote>'+esc(k.say)+'</blockquote>';
  h+='<h3>How sure</h3><dl><dt>Start</dt><dd>'+esc(k.ts)+'</dd><dt>End</dt><dd>'+esc(k.te)+(k.open&&byDay?'; not followed after this':'')+(k.tb?' <span class="meta">('+esc(k.tb)+')</span>':'')+'</dd>';
  var loc='';
  if(k.pl.length&&!k.basis){var n={},parts=[],order=[];k.pl.forEach(function(p){if(!n[p[2]])order.push(p[2]);n[p[2]]=(n[p[2]]||0)+1});
    order.forEach(function(c){parts.push((k.pl.length>1?n[c]+' ':'')+(found[c]||c))});loc=(k.pl.length>1?'A line through '+k.pl.length+' places: ':'A point ')+parts.join(', ')}
  else if(k.cs!=='none'&&!k.basis) loc=cap(found[k.cs]||k.cs);   // the record's own account of the place (basis) is shown where there is one
  var good=k.prec?'good to about '+(k.prec>=1000?(k.prec/1000)+' km':k.prec+' m'):'';
  if(good&&/good to about/i.test(k.cb)) good='';
  if(loc) loc+=(good?', '+good:'')+'.'; else if(good&&k.cb) loc=cap(good)+'.';
  h+='<dt>Location</dt><dd>'+(k.cc&&k.cc!=='n/a'?chip(k.cc)+' ':'')+(k.cb?esc(k.cb)+(/[.!?]$/.test(k.cb)?' ':'. '):'')+esc(loc)+'</dd><dt>Overall</dt><dd>'+chip(k.oc)+'</dd>';
  if(k.status) h+='<dt>Review</dt><dd>'+esc(k.status)+'</dd>';
  h+='</dl>';
  if(k.notes) h+='<h3>Notes</h3><p>'+esc(k.notes)+'</p>';
  var sl=WM.srcList(B.sources,k.src); if(sl) h+='<h3>Sources</h3><ul class="srcs">'+sl+'</ul>';
  if(k.lat!=null){var zz=compact?14:16;h+='<p style="margin-top:10px"><a href="https://www.openstreetmap.org/?mlat='+k.lat+'&mlon='+k.lon+'#map='+zz+'/'+k.lat+'/'+k.lon+'" target="_blank" rel="noopener">Open this spot on OpenStreetMap</a></p>'}
  return h;
}
function about(){return '<details><summary>About this prototype</summary>'+(P.about||[]).map(function(p){return '<p>'+esc(p)+'</p>'}).join('')+'<p>The map is drawn with MapLibre GL JS.</p></details>'}
function status(o){return o.s.kind==='moving'?'Moving (interpolated)':o.s.kind==='early'?'Arrived (time inferred)':o.s.kind==='after'?'Last recorded position':o.s.k.act}
function item(o,text){return '<li><button data-pick="'+o.tr.id+'"><span class="sd" style="background:'+look(o.tr).ui+'"></span><span class="nm">'+esc(o.tr.label)+'</span><span class="ac">'+esc(text)+'</span></button></li>'}
var panelKey='';
function renderPanel(sc){
  var me=sel?sc.filter(function(o){return o.tr.id===sel})[0]:null,ev=curEvent();
  if(sumAt!=null){var sk='sum|'+sumAt+'|'+sumMode;if(sk!==panelKey){panelKey=sk;panel.innerHTML=summaryHtml();panel.scrollTop=0}return}
  if(rcSel&&!sel&&base.rc&&RCF[rcSel]){var rk2='rc|'+rcSel;if(rk2!==panelKey){panelKey=rk2;panel.innerHTML=featureHtml();panel.scrollTop=0}return}
  if(info&&!sel){var ik='info|'+base.id+'|'+(seriesShown?seriesShown.id:'')+(hsRc?'r':'');if(ik!==panelKey){panelKey=ik;panel.innerHTML=mapDetails()+aroundNote();panel.scrollTop=0}return}
  var key=base.id+'|'+(sel?sel+'|'+(me?me.s.k.id+me.s.kind+(byDay?stamp(t):''):'x'):'now|'+(landing?'L':'')+(ev?ev.id:0)+'|'+LINKS.filter(linkNow).map(function(x){return x.id}).join(',')+'|'+sc.map(function(o){return o.tr.id+(o.drawn?1:0)+o.s.kind+o.s.k.id}).join(','));
  if(key===panelKey) return; panelKey=key; var h='';
  if(sel){
    var tr=B.track(sel),lk=look(tr),p=parentAt(tr,t),pu=p&&p[2]&&B.units[p[2]];
    h+='<button class="back" id="back">&larr; All units</button><div class="who"><div><div class="side" style="color:'+lk.ui+'">'+esc(lk.name)+'</div><h2>'+esc(tr.name)+'</h2>';
    h+='<div class="meta">'+[p?p[3]:tr.cmd,pu?'under '+pu.name:'',p?p[4]:tr.str].filter(Boolean).map(esc).join(' &middot; ')+'</div></div></div>';
    if(!me){h+='<div class="state unplaced"><b>Not in the data at '+esc(nowText())+'</b>Move the time to see this unit.</div>'}
    else{var kd=me.s.kind,K=kinds[kd];
      h+='<div class="state '+((kd==='offthis'||kd==='lost'||kd==='offmap')?'unplaced':kd)+'"><b>'+K[0]+'</b>'+esc(kd==='offmap'?tr.offmap:K[1])+'</div>';
      if(kd==='moving'){h+=rowHtml(me.s.k,'Heading to');if(me.s.from)h+=rowHtml(me.s.from,'Coming from')}
      else if(kd==='early'){h+=rowHtml(me.s.k,'Next record');if(me.s.from)h+=rowHtml(me.s.from,'Came from')}
      else h+=rowHtml(me.s.k,(kd==='after'||kd==='lost')?'Last record':'Current record');}
    if(tr.notes) h+='<p class="meta" style="margin-top:12px">'+esc(tr.notes)+'</p>';
    var evs=(EVOF[sel]||[]).map(function(id){return B.events.filter(function(x){return x.id===id})[0]});
    if(evs.length){h+='<h3>Events that name this unit</h3><ul class="evl">';evs.forEach(function(x){h+='<li><button data-ev="'+esc(x.id)+'" data-evu="1"><span class="tm">'+esc(whenText(x.t))+'</span><span>'+esc(x.full)+'</span></button></li>'});h+='</ul>'}
  } else {
    /* the Now text and the lists of units share the pane: opening a list folds the Now text away, and closing every list opens it again */
    h+=linksHtml();
    h+='<details class="nowd"'+(nowOpen?' open':'')+'><summary class="eyebrow">'+esc(ev?'Now: '+ev.name:B.opening.label)+'</summary><p class="phase">'+esc(ev?ev.text:B.opening.text)+'</p></details>';
    if(landing) h+='<p class="meta start">Press play to begin. The units come onto the map as the battle starts.</p>';
    if(B.events.length){h+='<details class="evs"'+(evOpen?' open':'')+'><summary>Key events: jump to one</summary><ul class="evl">';
      B.events.forEach(function(e){h+='<li><button data-ev="'+esc(e.id)+'"'+(ev&&ev.id===e.id?' class="cur"':'')+'><span class="tm">'+esc(whenText(e.t))+'</span><span>'+esc(e.full)+'</span></button></li>'});h+='</ul></details>'}
    if(SUMS.length){h+='<details class="evs sums"'+(sumsOpen?' open':'')+'><summary>Day by day: summaries</summary><ul class="evl">';
      SUMS.forEach(function(x){if(x.kind!=='day')return;var bb=dayEndOf(x.from);h+='<li><button data-day="'+bb+'"><span class="tm">'+esc(shortDay(x.from))+'</span><span>'+esc(x.title)+'</span></button></li>'});h+='</ul></details>'}
    /* Unit movement details: one drop-down holding a drop-down for each side (or nation), then the units not placed and those no longer followed */
    var groups=[],seen={},U=''; (byNation?(raw.nations||[]).map(function(n){return [n.name,n.short]}):raw.sides.map(function(s){return [s.code,s.short]})).forEach(function(g){groups.push(g);seen[g[0]]=1});
    groups.forEach(function(g){var Ls=sc.filter(function(o){return (o.drawn||o.folded)&&look(o.tr).group===g[0]});if(!Ls.length)return;
      U+='<details class="evs onmap" data-g="'+esc(g[0])+'"'+(grpOpen[g[0]]?' open':'')+'><summary>'+esc(g[1])+' <span class="cnt">('+Ls.length+')</span></summary><ul class="ulist">';Ls.forEach(function(o){U+=item(o,status(o))});U+='</ul></details>'});
    var nd=sc.filter(function(o){return !o.hidden&&!o.folded&&o.s.kind!=='lost'&&(!o.drawn||o.s.kind==='unplaced')});
    if(nd.length){U+='<details class="evs onmap" data-g="_nd"'+(grpOpen._nd?' open':'')+'><summary>'+(base.own?'Not on this map or not placed':'Not placed right now')+' <span class="cnt">('+nd.length+')</span></summary><ul class="nd">';
      nd.forEach(function(o){var kd=o.s.kind;U+='<li><b>'+esc(o.tr.label)+'</b>: '+esc(kd==='offmap'?o.tr.offmap:o.s.k.act+(kd==='offthis'?' (not on this map)':'. No position on record.'))+'</li>'});U+='</ul></details>'}
    var lo=sc.filter(function(o){return o.s.kind==='lost'});
    if(lo.length){U+='<details class="evs onmap" data-g="_lo"'+(grpOpen._lo?' open':'')+'><summary>No longer followed by the sources <span class="cnt">('+lo.length+')</span></summary><ul class="ulist">';lo.forEach(function(o){U+=item(o,'last placed '+o.s.k.te.split(' or later')[0].split(' to ').pop())});U+='</ul></details>'}
    if(U) h+='<details class="evs umd"'+(umdOpen?' open':'')+'><summary>Unit movement details</summary><div class="umdb">'+U+'</div></details>';
    h+='<p class="meta" style="margin-top:14px">Tap a unit for its source and how sure the position is.</p>'+about();
  }
  panel.innerHTML=h; if(sel) panel.scrollTop=0;
}
function select(id){
  if(id&&String(id).indexOf('F:')===0){ // a formation drawn zoomed out: zoom in on it until it breaks out into its units
    var hit=null;mv.hits.forEach(function(h){if(h.id===id&&h.r)hit=h}); if(hit){setFollow(false);setPreset(null);var W=WORLDS[worldOf(base)],c=mv.map.unproject([(hit.r[0]+hit.r[2])/2,(hit.r[1]+hit.r[3])/2]);
      mv.map.easeTo({center:c,zoom:mv.zoomFor(FM.below*1.15),duration:700})} return }
  if(id)closeSummary();sel=id||null;info=false;rcSel=null;panelKey='';if(sel&&sheet)sheet.open();if(sel&&pane)pane.show();mv.kick()}
var evOpen=false,sumsOpen=false,nowOpen=true,grpOpen={},umdOpen=false;
/* what lies around the map on screen, where the battle has a surround */
function aroundNote(){ if(!topo()||base.own||base.sat||base.current) return '';
  return '<div class="eyebrow" style="margin-top:18px">Around this map</div><p>Zoom out past the edge of this map and today\'s topographic map is drawn around it.</p><dl><dt>Source</dt><dd>'+esc(MOD.name?MOD.name+' ('+MOD.credit+')':MOD.credit)+'</dd>'+(MOD.rights?'<dt>Rights</dt><dd>'+esc(MOD.rights)+'</dd>':'')+'</dl>'}
/* the map on screen: what it is, who made it, where it is held, how it was placed */
/* Maps of this ground that are not on the Type of map menu (`hidden`), offered in the map details instead: each opens in the playback,
   with a link to the original where there is one. On a hidden map the panel offers the way back to the main one. */
function otherMaps(){ var hid=bases.filter(function(b){return b.hidden&&!b.of}); if(!hid.length) return '';
  var main=bases.filter(function(b){return !b.hidden&&!b.of&&b.id===P.start_base})[0]||bases.filter(function(b){return !b.hidden&&!b.of})[0],h='';
  var item=function(b){var url='';if(b.m){var s=B.sources[b.m.raw.source]||{};url=s.url||''}
    return '<li><button class="linkish" data-base="'+esc(b.id)+'">'+esc(b.label)+'</button>'+(b.note?'<span>'+esc(b.note)+'</span>':'')+(url?' <a href="'+esc(url)+'" target="_blank" rel="noopener">The original</a>':'')+'</li>'};
  if(base.hidden){ h+='<div class="othermaps"><p>This map is not on the Type of map menu.'+(main?' <button class="linkish" data-base="'+esc(main.id)+'">Back to '+esc(main.label)+'</button>':'')+'</p>';
    var rest=hid.filter(function(b){return b!==base}); if(rest.length) h+='<p class="meta">Also: </p><ul class="rcl">'+rest.map(item).join('')+'</ul>'; return h+'</div>' }
  return '<div class="othermaps"><h3>Other maps of this ground</h3><ul class="rcl">'+hid.map(item).join('')+'</ul></div>'}
function mapDetails(){var h='<button class="back" id="back">&larr; All units</button><div class="eyebrow">The map on screen</div>',row=function(k,v){return v?'<dt>'+k+'</dt><dd>'+esc(v)+'</dd>':''};
  var cr='<p class="meta credits">Credits for what is on screen: '+lastCredit+'</p>';
  h+=otherMaps();
  if(base.rc) return h+reconDetails()+cr;   // a reconstruction says first that it is one (it carries no banner on the map: Morgan, 22 Nov 2026)
  h+=cr;
  if(base.sat){var im=base.imagery;h+='<h2>'+esc(im.name||base.label)+'</h2><p>'+esc(im.about||'Aerial or satellite imagery of the ground today, streamed from the provider\'s tile service. The names on it come from OpenStreetMap.')+'</p><dl>'+row('Source',im.credit)+row('Rights',im.rights||'')+row('Taken',im.date||'')+'</dl>'+(im.link?'<p style="margin-top:10px"><a href="'+esc(im.link)+'" target="_blank" rel="noopener">About this imagery</a></p>':'')+'<p class="meta" style="margin-top:12px">If the tile service cannot be reached, the map shows plain ground under the units.</p>';return h}
  if(base.current&&topo()){h+='<h2>'+esc(MOD.name||'Current map')+'</h2><p>'+esc(MOD.about||'Today\'s topographic map, streamed from the provider\'s tile service.')+'</p><dl>'+row('Source',MOD.credit)+row('Rights',MOD.rights||'')+'</dl>'+(MOD.link?'<p style="margin-top:10px"><a href="'+esc(MOD.link)+'" target="_blank" rel="noopener">About this map</a></p>':'')+'<p class="meta" style="margin-top:12px">If the map service cannot be reached, a plain drawing of today\'s roads and water, made from OpenStreetMap, is shown in its place.</p>'+hillAbout();return h}
  if(base.current){h+='<h2>Current map</h2>'+(MOD?'<p class="meta">The topographic map service could not be reached from here, so this plain drawing is shown in its place.</p>':'')+(function(){var bc=raw.base&&raw.base.credit,bs=raw.base&&raw.base.source&&B.sources[raw.base.source];
      if(bc&&!/OpenStreetMap/.test(bc))   // a drawing from other data (Luzon 1899: Natural Earth): say whose, from the source the base names
        return '<p>Today\'s coast, main roads, railways and rivers, drawn from '+esc(bs?bs.title:bc)+'. It is a drawing of that data, not a live map service, and much coarser than a street map.</p><dl>'+row('Source',bc)+row('Rights',bs?bs.rights||'':'')+'</dl>'+(bs&&bs.url?'<p style="margin-top:10px"><a href="'+esc(bs.url)+'" target="_blank" rel="noopener">'+esc(bs.author||bs.title)+'</a></p>':'');
      return '<p>Today\'s roads, water, railways, woods and names, cut down from OpenStreetMap to what this battle needs. It is a drawing of that data, not a live map service.</p><dl>'+row('Source','OpenStreetMap contributors')+row('Rights','Open Database License')+'</dl><p style="margin-top:10px"><a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap copyright and licence</a></p>'})();return h}
  var m=(base.series&&seriesShown)||base.m||series[0],s=B.sources[m.raw.source]||{},f=m.raw.fit||{},fit='';
  if(m.own) fit='No. It is not to scale, so it is shown as a picture of its own and units have separate positions on it.';
  else{fit='Yes';if(f.method)fit+=': '+f.method;if(f.metres_per_pixel)fit+='; '+f.metres_per_pixel+' m per scan pixel';if(f.turn_degrees)fit+='; turned '+f.turn_degrees+'\u00b0 from north';if(f.points)fit+=': fitted on '+f.points+' points'+(f.misfit_m?', typical misfit '+f.misfit_m+' m':'');fit+='.'}
  h+='<h2>'+esc(m.title)+'</h2><dl>'+row('Battle',B.title)+row('Shows',m.label)+row('Made by',s.author)+row('Date',s.date)+row('Kind',s.type)+row('Published or held',s.citation)+row('Scale',m.raw.scale_note||(m.own?'Not to scale':''))+row('Rights',s.rights||'Not checked')+row('Placed on the ground',fit)+'</dl>';
  if(m.raw.note) h+='<p style="margin-top:10px">'+esc(m.raw.note)+'</p>';
  if(s.url) h+='<p style="margin-top:10px"><a href="'+esc(s.url)+'" target="_blank" rel="noopener">Open the original record</a></p>';
  var I=m.raw.iiif,host=I?I.service.split('/')[2]:'';
  h+='<p class="meta" style="margin-top:12px">'+(I&&!tilesOff?'The picture that comes with this page is a reduced copy. When you zoom in, the full scan is streamed in pieces from '+esc(host)+'; the 1:1 button shows it at full size.':I?'The picture shown is a reduced copy. The full scan could not be reached at '+esc(host)+' from here.':'The picture shown here is a reduced copy of the scan.')+'</p>';return h}

/* ---------- controls ---------- */
/* Three menus over the map, plus Follow: Type of map (which map is under the units), Map options (how today's map and the names look),
   Battle options (how units are drawn, what else is shown, and the pauses with day or week summaries). */
(function(){var h='',seg=function(label,items){return '<div class="seg" role="group" aria-label="'+label+'">'+items.join('')+'</div>'},
    opt=function(id,x){return '<button class="opt" id="'+id+'" aria-pressed="false"'+(x.title?' title="'+esc(x.title)+'"':'')+'>'+esc(x.label)+'</button>'},
    chipb=function(id,label,title,on){return '<button class="chipbtn" id="'+id+'" aria-pressed="'+(on?'true':'false')+'" title="'+esc(title)+'"><span class="dot"></span><span>'+label+'</span></button>'},
    dd=function(id,pop,label,title,extra){return '<button class="chipbtn dd" id="'+id+'" aria-expanded="false" aria-controls="'+pop+'" title="'+esc(title)+'"><span>'+label+'</span>'+(extra||'')+'<span class="car">&#9662;</span></button>'};
  var many=bases.filter(function(b){return !b.of&&!b.hidden}).length>1||P.views;
  if(many) h+=dd('bType','pType','Type of map','Which map the battle is drawn on','<span class="cur" id="typeCur"></span>');
  if(P.follow) h+=chipb('bFollow','Follow<span class="long"> the action</span>','Keep the units in view as time moves (F)',true);
  h+=dd('bLayers','layers','Map options','How the map and its names are drawn');
  h+=dd('bBattle','pBattle','Battle options','How the units are drawn, and pauses with summaries');
  $('ctl').innerHTML=h;
  var ck=function(id,label,on,key){return '<label class="ck"><input type="checkbox" id="'+id+'"'+(on?' checked':'')+'><span>'+label+(key?'<kbd>'+key+'</kbd>':'')+'</span></label>'},
      sb=function(id,label,on){return '<button id="'+id+'" aria-pressed="'+(on?'true':'false')+'">'+esc(label)+'</button>'},T='',L='',G='';
  // Type of map
  if(many){T+='<div class="grp"><div class="gh">Map</div>'+bases.filter(function(b){return !b.of&&!b.hidden}).map(function(b){return opt('b-'+b.id,b)}).join('')+'</div>';
    if(P.views) T+='<div class="grp"><div class="gh">View</div>'+P.views.map(function(v){return opt('v-'+v.preset,v)}).join('')+'</div>';
    $('pType').innerHTML=T}
  // Map options
  if(MOD||bases.some(function(b){return b.sat})||HS) L+='<div class="grp"><div class="gh">Today\'s map</div>'+((MOD||bases.some(function(b){return b.sat}))?ck('cMute','Muted colours',muteOn):'')+(HS?ck('cHill','Terrain shading',hsOn):'')+'</div>';
  L+='<div class="grp"><div class="gh">Names on the map</div>'+ck('cPlaces','Place names',true)+ck('cLines','Road and stream names',true)+'</div>';
  if(bases.some(function(b){return !b.current&&!b.own&&!b.sat})) L+='<div class="grp" id="gOpac"><div class="gh"><span>Period map</span><span id="opv">100%</span></div><input type="range" id="opac" min="0" max="100" step="5" value="100" aria-label="How strongly the period map is drawn"><p class="gn">Turn it down to see today&rsquo;s map through the period map.</p></div>';
  L+='<div class="grp"><button class="lnk" id="bLink">Copy a link to this view</button><span class="ok" id="linkok" hidden>Copied</span></div>';
  $('layers').innerHTML=L;
  // Battle options
  G+='<div class="grp"><div class="gh">Show</div>'+ck('cUnits','Units',true,'U')+ck('cNames','Unit names',true,'N')+((P.fold&&P.fold.label)?ck('cFold',esc(P.fold.label)+' when zoomed in',true):'')+(FM?ck('cForm',esc(FM.label||'Divisions')+' when zoomed out',fmOn):'')+(TRL?ck('cTrail','Routes taken',trlOn):'')+(arrowsAny()?ck('cArrow','Arrows to where units go next',arwOn):'')
    +(DE_OK?ck('cDayEnds','Where units began and ended each day',deOn):'')+ck('cNarr','The current event, in words, on the map',false)+(EVH_OK?ck('cEvh','Highlight the units in the current event',evhOn):'')+(DE_OK?'<p class="gn">Dashed: where a unit began the day. Thin solid: where it ended it.</p>':'')+'</div>';
  G+='<div class="grp"><div class="gh">Unit symbols</div>'+seg('Unit symbols',[sb('fr-none','Neutral',true)].concat(raw.sides.map(function(sd){return sb('fr-'+sd.code,sd.short,false)})))+'<p class="gn">Choose a side to see the battle from its point of view: the other side&rsquo;s units take the diamond frame of the standard military symbols.</p></div>';
  if(PZ_OK) G+='<div class="grp"><div class="gh">Pause and summary</div>'+seg('Pause and summary',[sb('pz-off','Off',pzMode==='off'),sb('pz-day','Each day',pzMode==='day'),sb('pz-week','Each week',pzMode==='week')])+'<p class="gn">While it plays, the battle stops at the end of each day or week and shows a summary. Press Continue to go on.</p></div>';
  $('pBattle').innerHTML=G;
  var cb=$('clockbattle'); if(cb){cb.textContent=P.clock_title||B.title;cb.hidden=P.clock_title===''}   // the battle's name in the date box
  wrap.classList.toggle('compact',compact); $('when').classList.toggle('date',byDay); $('tl').classList.toggle('days',byDay);
  if(byDay){$('hint').innerHTML=$('hint').innerHTML.replace('to move time','to move through the days')}
})();

/* ---------- map and time ---------- */
try{ mv=WM.mapView({container:'map',wrap:wrap,world:worldOf(base),worlds:WORLDS,
  onDraw:draw,onPick:select,
  onUserMove:function(){if(follow)pauseFollow();if(preset||goal)setPreset(null)},
  onResize:function(){if(preset){mv.jump(landing?home():cameraOf(preset));goal=null}else if(follow&&!landing)mv.jump(target());else if(landing)mv.jump(home())},
  onStep:function(ts){var more=(clk.playing&&Date.now()<holdUntil)?true:clk.step(ts);if(more)doSkip(ts);if(goal){if(mv.chase(goal,goalK))more=true;else{goal=null;goalK=0.2}}else if(follow&&!landing){if(Date.now()<fpause)more=true;else{if(fpause){resumeFollow();fpause=0}if(glide>Date.now()?mv.chase(target(),FOL.glide_rate):mv.chase(calmTarget(),FOL.rate,FOL.zoom_rate))more=true}}return more}});
}catch(err){WM.noMap(wrap,err);return null}
S=mv.S;
mv.map.on('moveend',queueTiles); mv.map.on('error',tileError);
/* on a reconstructed map a tap that finds no unit may find one of its lines: show where that line came from */
mv.map.on('click',function(e){ if(sel||!base.rc) return; var id=pickRecon(e.point); if(!id) return; closeSummary(); rcSel=id; info=false; panelKey=''; sheet.open(); pane.show(); mv.kick() });
mv.map.on('mousemove',function(e){ if(base.rc&&!mv.map.getCanvas().style.cursor&&pickRecon(e.point)) mv.map.getCanvas().style.cursor='help' });
/* the stretch before the part the data covers best (a night march before a fight) can be squeezed into a share of the bar and played faster */
var LD=(P.lead&&B.focus&&B.focus[0]>T0)?P.lead:null,TM=LD?B.focus[0]:T0,UM=LD?LD.share:0,RNG=4000;
function u2t(u){return (LD&&u<=UM)?T0+(TM-T0)*u/UM:TM+(T1-TM)*(u-UM)/(1-UM)}
function t2u(v){return (LD&&v<=TM)?UM*(v-T0)/(TM-T0):UM+(1-UM)*(v-TM)/(T1-TM)}
function paintTime(v){if(sumAt!=null&&Math.abs(v-sumAt)>1e-6)closeSummary();t=v; if(landing&&(v!==T0||(clk&&clk.playing))){landing=false;panelKey='';glide=Date.now()+FOL.glide_ms;if(!follow&&OPEN_OUT&&!base.own&&mv){goal=home();goalK=0.03}}   // without Follow, the camera eases in from the wide opening to the battle's own first view   // the battle has been started: the units come on, and Follow takes the camera

  if(byDay){var n=stamp(t),d=B.dateOf(n),night=Math.abs(t-Math.round(t))<0.02;
    $('clock').textContent=d.day+' '+d.mon+' '+d.year;$('clockdate').textContent=d.wd+' · '+(night?'at nightfall':'during the day');WM.paintDayNumber(B.cal.numbered?n+1:0)}
  else{var c=WM.calOf(B.cal,t);$('clock').textContent=c.clock;$('clockdate').textContent=c.date;WM.paintDayNumber(c.n)}
  var tn=P.time_note,ne=$('clocknote'); if(tn){ne.textContent=tn.text;ne.hidden=t<B.time(tn.from)} else ne.hidden=true;
  $('done').style.width=(t2u(t)*100)+'%'; var ev=curEvent(); paintNarr();
  Array.prototype.forEach.call(document.querySelectorAll('.tl .ev'),function(e){e.classList.toggle('on',!!ev&&e.dataset.id===ev.id)});
  var cur=ev?ev.id:''; if(cur!==namedFor){namedFor=cur;fitNames()}}
/* Event names on the timeline: where two would overlap, only one is written (the tick stays). The current event's name always is. */
var namedFor=null;
function fitNames(){
  var els=Array.prototype.slice.call(document.querySelectorAll('.tl .ev')),kept=[],i;
  els.forEach(function(e){e.classList.remove('crowd')});
  var box=els.map(function(e){var r=e.getBoundingClientRect();return [r.left-4,r.right+4,r.width]});
  function clash(b){for(var j=0;j<kept.length;j++)if(b[0]<kept[j][1]&&b[1]>kept[j][0])return true;return false}
  for(i=0;i<els.length;i++)if(els[i].classList.contains('on')&&box[i][2]>20)kept.push(box[i]);
  for(i=0;i<els.length;i++){var e=els[i]; if(e.classList.contains('on')||e.classList.contains('mute')||box[i][2]<=20)continue;   // a name already hidden (a quiet event, or a narrow screen) takes no room
    if(clash(box[i]))e.classList.add('crowd');else kept.push(box[i])}
}
window.addEventListener('resize',fitNames);
/* the time step: how far one arrow key or one notch of the scroll wheel moves time. Only steps the battle's span can use are offered. */
/* The same step sets how fast the playback runs: one step of battle time for each second played. */
var STEPS=(byDay?[[1,'1 day'],[7,'1 week'],[30,'1 month']]:[[1,'1 min'],[5,'5 min'],[15,'15 min'],[60,'1 hour'],[1440,'1 day']]).filter(function(x,i){return i===0||x[0]*3<=T1-T0});
function setStep(i){stepI=(i+STEPS.length)%STEPS.length;wheelAcc=0;var e=$('step'),w=STEPS[stepI][1];e.textContent=w;e.hidden=STEPS.length<2;
  e.title='Step: '+w+'. The back and forward buttons and the arrow keys move '+w+'; playing runs '+w+' a second. Click to change.';
  var b=$('evprev'),f=$('evnext');if(b){b.title='Back '+w;b.setAttribute('aria-label','Back '+w)}if(f){f.title='Forward '+w;f.setAttribute('aria-label','Forward '+w)}}
function stepNear(r){var best=0;STEPS.forEach(function(x,i){if(Math.abs(Math.log(x[0]/r))<Math.abs(Math.log(STEPS[best][0]/r)))best=i});return best}   // the step nearest a play rate
function stepBy(dir,v){var n=STEPS[stepI][0];
  if(byDay) return (dir>0?Math.floor(v+1e-6):Math.ceil(v-1e-6))+dir*n;
  if(stepI===0) return v+dir*((LD&&(dir>0?v<TM:v<=TM))?(LD.step||5):1);
  return Math.round(v)+dir*n}   // always exactly one step, so every press moves time the same amount
var rng=$('time'); rng.min=0; rng.max=RNG; rng.step=1; rng.value=0; rng.setAttribute('aria-label',byDay?'Day of the battle':'Time of day');
clk=WM.clock({T0:T0,T1:T1,mv:mv,stopAt:stopAt,onStop:function(b){openSummary(b,b>=T1-1e-6&&pzMode==='week'?'week':pzMode)},
  beforePlay:function(){if(PZ_OK&&pzMode==null&&t<T1-1e-6){ask();return false}},toRange:function(v){return Math.round(t2u(v)*RNG)},fromRange:function(v){return u2t(v/RNG)},
  rate:function(v){var n=STEPS[stepI][0];if(byDay&&stepI===0&&P.rate>0&&P.rate<1)return P.rate;   /* a day battle can play slower than a day a second (Ypres: half a day) */
    return (LD&&v<TM)?Math.max(LD.rate,n):n},onTime:paintTime,
  snap:byDay?function(v){return Math.round(v)}:null,   // the sources give one position a day, so time settles on nightfall
  arrow:stepBy,
  wheel:function(dd,v){if(stepI===0)return u2t(Math.max(0,Math.min(1,t2u(v)+dd*0.0002)));   // at the finest step scrolling is smooth; at a coarser one each notch is one step
    wheelAcc+=dd;if(Math.abs(wheelAcc)<50)return v;var dir=wheelAcc>0?1:-1;wheelAcc=0;return stepBy(dir,v)},
  onKey:function(e){var k=e.key.toLowerCase();
    if(e.key==='['||e.key==='PageUp'){toEvent(-1);e.preventDefault()}else if(e.key===']'||e.key==='PageDown'){toEvent(1);e.preventDefault()}
    else if(e.key==='Escape')select(null);else if(k==='n')setNames(!names);else if(k==='u')setUnits(!unitsOn);else if(k==='f'&&P.follow)setFollow(!follow);
    else if(k==='m'&&bases.length>1){var vis=bases.filter(function(x){return !x.of}),cb=base.of?bases.filter(function(x){return x.id===base.of})[0]:base;setBase(vis[(vis.indexOf(cb)+1)%vis.length])}}});

/* timeline furniture: ticks, the part the data covers best, and the events */
(function(){var tl=$('tl'),pc=function(m){return (t2u(m)*100)+'%'},h='',m,lg=!byDay&&(T1-TM)>360,fmt=function(v){return WM.fmtClock(v)};
  var win=$('win'); if(B.focus){win.style.left=pc(B.focus[0]);win.style.width=((t2u(B.focus[1])-t2u(B.focus[0]))*100)+'%';if(B.focus[1]>=T1)win.style.borderRadius='0 5px 5px 0'} else win.hidden=true;
  if(byDay&&(T1-T0)>120){for(m=T0;m<=T1;m++){var dl=B.dateOf(m);   // a campaign of months: a tick at each month's start and middle, the month named at its start
      if(dl.day===1){h+='<span class="tick maj" style="left:'+pc(m)+'"></span><span class="tk" style="left:'+pc(m)+'">'+dl.mon.slice(0,3)+'</span>'}
      else if(dl.day===15)h+='<span class="tick" style="left:'+pc(m)+'"></span>'}}
  else if(byDay){var nth=0;for(m=T0;m<=T1;m++){var d=B.dateOf(m),maj=d.day%5===0;h+='<span class="tick'+(maj?' maj':'')+'" style="left:'+pc(m)+'"></span>';
      if(maj){h+='<span class="tk'+(nth%2?' minor':'')+'" style="left:'+pc(m)+'">'+d.day+' '+d.mon.slice(0,3)+'</span>';nth++}}}
  else{for(m=Math.ceil(T0/60)*60;m<TM;m+=60){h+='<span class="tick" style="left:'+pc(m)+'"></span>';if(m%120===0)h+='<span class="tk minor" style="left:'+pc(m)+'">'+fmt(m)+'</span>'}
    var st=lg?30:15,lb=lg?60:30;   // a long day: a tick each half hour and a time each hour
    for(m=Math.ceil(TM/30)*30;m<=T1;m+=st){h+='<span class="tick" style="left:'+pc(m)+'"></span>';if(m%lb===0)h+='<span class="tk'+(m%(lb*2)?' minor':'')+'" style="left:'+pc(m)+'">'+fmt(m)+'</span>'}}
  LINKS.forEach(function(x){if(x.kind!=='battle')return;var a0=Math.max(T0,x.t0),a1=Math.min(T1,x.t1+(byDay?1:0));if(a1<a0)return;
    h+='<button class="cblb" data-t="'+a0+'" style="left:'+pc(a0)+';width:'+((t2u(a1)-t2u(a0))*100)+'%" title="'+esc(x.name+', '+lspan(x))+'" aria-label="'+esc('Go to '+x.name)+'"></button>'});
  B.events.forEach(function(e){h+='<button class="ev'+(e.quiet?' mute':'')+'" data-id="'+esc(e.id)+'" data-t="'+e.t+'" style="left:'+pc(e.t)+'" title="'+esc(e.name)+'" aria-label="'+esc(e.name)+'">'+esc(e.name)+'</button>'});
  tl.insertAdjacentHTML('afterbegin',h);
  tl.addEventListener('click',function(ev){var b=ev.target.closest('.ev,.cblb');if(b){clk.setPlaying(false);clk.setTime(+b.dataset.t)}});
})();
function on(id,fn){var e=$(id);if(e)e.addEventListener('click',fn)}
bases.forEach(function(b){if(!b.of)on('b-'+b.id,function(){if(base.of===b.id){var p=sheetToGround(base,mv.map.getCenter());setBase(b);if(p)mv.map.jumpTo({center:p,zoom:mv.zoomFor(0.2)})}else setBase(b)})});
(P.views||[]).forEach(function(v){on('v-'+v.preset,function(){setPreset(v.preset)})});
on('bFollow',function(){setFollow(!follow)});
document.addEventListener('keydown',function(e){var tg=(e.target&&e.target.tagName)||''; if(tg==='INPUT'||tg==='TEXTAREA'||e.metaKey||e.ctrlKey||e.altKey) return;
  var d={ArrowLeft:[-1,0],ArrowRight:[1,0],ArrowUp:[0,-1],ArrowDown:[0,1]}[e.key];
  if(d&&e.shiftKey){setFollow(false);setPreset(null);mv.map.panBy([d[0]*120,d[1]*120],{duration:160});e.preventDefault();e.stopPropagation();return}   // shift + arrows move the map; plain arrows move time
  if(e.key==='+'||e.key==='='){zoomStep(1.45);e.preventDefault()} else if(e.key==='-'||e.key==='_'){zoomStep(1/1.45);e.preventDefault()}},true);
/* the three menus over the map: one open at a time, each under its own button */
var POPS=[['bType','pType'],['bLayers','layers'],['bBattle','pBattle']].filter(function(x){return $(x[0])&&$(x[1])});
function openPop(id,v){POPS.forEach(function(x){var on=x[1]===id&&v,p=$(x[1]);p.hidden=!on;$(x[0]).setAttribute('aria-expanded',on?'true':'false');
  if(on){var bt=$(x[0]),wl=wrap.getBoundingClientRect().left,l=bt.getBoundingClientRect().left-wl;p.style.left=Math.max(10,Math.min(l,wrap.clientWidth-p.offsetWidth-10))+'px'}})}
function openLayers(v){openPop('layers',v)}
POPS.forEach(function(x){on(x[0],function(){openPop(x[1],$(x[1]).hidden)})});
document.addEventListener('pointerdown',function(e){POPS.forEach(function(x){if(!$(x[1]).hidden&&!e.target.closest('#'+x[1])&&!e.target.closest('#'+x[0]))openPop(x[1],false)})});
document.addEventListener('keydown',function(e){if(e.key!=='Escape')return;POPS.forEach(function(x){if(!$(x[1]).hidden){openPop(x[1],false);$(x[0]).focus();e.stopPropagation()}})},true);
/* a choice of map closes its menu */
bases.forEach(function(b){var e=$('b-'+b.id);if(e)e.addEventListener('click',function(){openPop('pType',false)})});
(P.views||[]).forEach(function(v){var e=$('v-'+v.preset);if(e)e.addEventListener('click',function(){openPop('pType',false)})});
function onCheck(id,fn){var e=$(id);if(e)e.addEventListener('change',function(){fn(e.checked)})}
onCheck('cUnits',setUnits); onCheck('cNames',setNames); onCheck('cFold',setFold); onCheck('cNarr',setNarr); onCheck('cForm',setFormations); onCheck('cTrail',setTrails); onCheck('cArrow',setArrows); onCheck('cMute',setMute); onCheck('cHill',setHill);
onCheck('cEvh',setEvh); onCheck('cPlaces',function(v){placeNames=v;mv.kick()}); onCheck('cLines',function(v){lineNames=v;mv.kick()});
on('sy-standard',function(){setSymbols('standard')}); on('sy-period',function(){setSymbols('period')});
on('fr-none',function(){setSeenFrom('')}); raw.sides.forEach(function(sd){on('fr-'+sd.code,function(){setSeenFrom(sd.code)})});
var opr=$('opac'); if(opr) opr.addEventListener('input',function(){setOpacity(+opr.value/100)});
on('zin',function(){zoomStep(1.45)}); on('zout',function(){zoomStep(1/1.45)});
on('z11',function(){var sb=sheetOf(base);
  if(sb){var c=mv.map.getCenter(),xy=groundToSheet(sb,[c.lng,c.lat]);setFollow(false);setPreset(null);setBase(sb);if(xy)mv.map.jumpTo({center:ownLL(xy)});var m2=scanOf();if(m2)mv.zoomBy(1/scanScale(m2));return}
  var m=scanOf();if(!m)return;setFollow(false);setPreset(null);mv.zoomBy(1/scanScale(m))});
/* A fitted map that is stretched to lie on the ground can have its engraving shown as printed (a base with `of` naming the fitted one):
   1:1 opens it at full detail where the reader is looking, and its own button brings the fitted map back. A table laid over the ground
   (lookup) gives the engraving's pixel for each place; units carry their own positions on it. */
function sheetOf(b){return bases.filter(function(x){return x.of===b.id})[0]||null}
function groundToSheet(sb,ll){var L=sb.m.raw.lookup;if(!L)return null;var e=L.ext,n=L.n,fx=(ll[0]-e[0])/(e[2]-e[0])*(n[0]-1),fy=(e[3]-ll[1])/(e[3]-e[1])*(n[1]-1);
  if(fx<0||fy<0||fx>n[0]-1||fy>n[1]-1)return null;var i=Math.min(n[0]-2,Math.floor(fx)),j=Math.min(n[1]-2,Math.floor(fy)),u=fx-i,v=fy-j,P=function(a,b){return L.xy[b*n[0]+a]};
  var a=P(i,j),b=P(i+1,j),c=P(i,j+1),d=P(i+1,j+1);return [0,1].map(function(k){return a[k]*(1-u)*(1-v)+b[k]*u*(1-v)+c[k]*(1-u)*v+d[k]*u*v})}
function sheetToGround(sb,c){var L=sb.m.raw.lookup;if(!L)return null;var x=c.lng/SKK,y=-c.lat/SKK,best=1e18,bi=0;L.xy.forEach(function(p,i){var d=(p[0]-x)*(p[0]-x)+(p[1]-y)*(p[1]-y);if(d<best){best=d;bi=i}});
  var e=L.ext,n=L.n,i=bi%n[0],j=Math.floor(bi/n[0]);return [e[0]+(e[2]-e[0])*i/(n[0]-1),e[3]-(e[3]-e[1])*j/(n[1]-1)]}
on('zfit',function(){setFollow(false);setPreset(null);mv.jump(mv.cameraFor(base.own?WORLDS[worldOf(base)].ext:EXT,{t:48,b:22,l:14,r:14}))});
(function(){var app=document.querySelector('.app'),b=$('zfull'); if(!b) return;   // full screen is not offered where the browser does not allow it (inside some embedded views)
  if(!document.fullscreenEnabled||!app.requestFullscreen){b.hidden=true;return}
  b.addEventListener('click',function(){if(document.fullscreenElement)document.exitFullscreen();else app.requestFullscreen()})})();
on('binfo',function(){closeSummary();sel=null;rcSel=null;info=!info;panelKey='';if(info){sheet.open();pane.show()}mv.kick()});
/* phones: the text sheet under the map. It starts as a strip; a tap on the handle opens it to about half the screen and closes it
   again, and dragging the handle sets any height in between. Dragged right down, or with the map's hide-text button, it goes away
   and only the handle is left; a tap or a drag on the handle brings it back. Tapping a unit opens it so the unit's details can be read. */
var sheet=(function(){var st=document.querySelector('.stage'),bar=$('sheetbar'),MIN=72,DEF=96,GONE=44,h=DEF,drag=null;
  function phone(){return getComputedStyle(bar).display!=='none'}
  function hidden(){return st.classList.contains('nopane')}
  function maxH(){return Math.round(st.getBoundingClientRect().height*0.72)}
  function set(v,anim,free){h=Math.max(free?0:MIN,Math.min(maxH(),v));st.classList.toggle('sheet-anim',!!anim);st.style.setProperty('--sheet-h',h+'px');$('grab').setAttribute('aria-expanded',!hidden()&&h>DEF+20?'true':'false')}
  function open(){if(phone()&&h<DEF+40)set(st.getBoundingClientRect().height*0.5,true)}
  function toggle(){if(hidden()){set(DEF,false);pane.show();return}if(h>DEF+20)set(DEF,true);else open()}
  bar.addEventListener('pointerdown',function(e){if(!phone())return;drag={y:e.clientY,h:hidden()?0:h,moved:false};bar.setPointerCapture(e.pointerId);e.preventDefault()});
  bar.addEventListener('pointermove',function(e){if(!drag)return;var dy=drag.y-e.clientY;if(Math.abs(dy)>4)drag.moved=true;if(!drag.moved)return;
    set(drag.h+dy,false,true);if(hidden()&&h>0)pane.show(true)});
  bar.addEventListener('pointerup',function(){if(!drag)return;var m=drag.moved;drag=null;if(!m)toggle();else if(h<GONE){set(DEF,false);pane.hide()}else if(h<MIN)set(MIN,true)});
  bar.addEventListener('pointercancel',function(){drag=null;if(h<MIN&&!hidden())set(MIN,true)});
  $('grab').addEventListener('keydown',function(e){if(e.key==='Enter'||e.key===' '){e.preventDefault();toggle()}});
  return {open:open,phone:phone,sync:function(){$('grab').setAttribute('aria-label',hidden()?'Show the text':'Show more of the text')}}})();
/* the text pane beside the map (under it on a phone) folds away and comes back; choosing a unit or the i panel brings it back */
var pane=(function(){var st=document.querySelector('.stage'),b=$('bpane');
  function set(hide){st.classList.remove('sheet-anim');st.classList.toggle('nopane',hide);b.setAttribute('aria-pressed',hide?'true':'false');var t=hide?'Show the text':'Hide the text';b.setAttribute('aria-label',t);b.title=t;remember('pane',!hide);sheet.sync();mv.kick()}
  b.addEventListener('click',function(){set(!st.classList.contains('nopane'))});
  try{if(localStorage.getItem('wm.'+B.id+'.pane')==='0')set(true)}catch(e){}
  return {show:function(){if(st.classList.contains('nopane'))set(false)},hide:function(){if(!st.classList.contains('nopane'))set(true)}}})();
/* the edge between the map and the text pane beside it: drag it to make the text wider or narrower; double-click, or Home, puts it
   back to the usual width. The width chosen is kept for every battle on this browser. */
(function(){var st=document.querySelector('.stage'),s=$('split'),KEY='wm.panew',w=null,drag=null,raf=0;
  function lim(v){var W=st.getBoundingClientRect().width;return Math.round(Math.max(240,Math.min(W*0.7,W-320,v)))}
  function now(){return Math.round(panel.getBoundingClientRect().width)}
  function apply(){raf=0;if(w==null)st.style.removeProperty('--pane-w');else st.style.setProperty('--pane-w',lim(w)+'px');s.setAttribute('aria-valuenow',now())}
  function set(v,save){w=v==null?null:lim(v);if(!raf)raf=requestAnimationFrame(apply);
    if(save)try{if(w==null)localStorage.removeItem(KEY);else localStorage.setItem(KEY,String(w))}catch(e){}}
  s.addEventListener('pointerdown',function(e){if(e.button)return;drag={x:e.clientX,w:now()};s.setPointerCapture(e.pointerId);st.classList.add('resizing');e.preventDefault()});
  s.addEventListener('pointermove',function(e){if(drag)set(drag.w+(drag.x-e.clientX))});
  function end(){if(!drag)return;drag=null;st.classList.remove('resizing');set(w,true)}
  s.addEventListener('pointerup',end);s.addEventListener('pointercancel',end);
  s.addEventListener('dblclick',function(){set(null,true)});
  s.addEventListener('keydown',function(e){var k=e.key;if(k==='ArrowLeft'||k==='ArrowRight'){e.preventDefault();set(now()+(k==='ArrowLeft'?40:-40),true)}else if(k==='Home'){e.preventDefault();set(null,true)}});
  s.setAttribute('aria-valuemin','240');
  window.addEventListener('resize',function(){if(w!=null&&!raf)raf=requestAnimationFrame(apply)});   // the wish is kept; it is fitted to the window as it now is
  try{var v=+localStorage.getItem(KEY);if(v>0){w=v;apply();requestAnimationFrame(function(){mv.map.resize()})}}catch(e){}})();   // MapLibre does not notice a change made before its first look at the page
/* phones: while playing, a tap on the map brings the hidden buttons back for a few seconds */
(function(){var tmo=0;wrap.addEventListener('touchstart',function(){if(!document.documentElement.classList.contains('wm-playing'))return;wrap.classList.add('peek');clearTimeout(tmo);tmo=setTimeout(function(){wrap.classList.remove('peek')},4000)},{passive:true})})();
// back and forward one step; [ and ] jump between key events
on('restart',restart);   // start over: the first moment, the opening map and view, no unit picked
function restart(){closeSummary();$('ask').hidden=true;clk.setPlaying(false);select(null);setPreset(null);fpause=0;followK=1;glide=0;skipAcc=0;brk={};mrg={};lastW=null;holdUntil=0;
  if(P.follow){follow=true;press('bFollow',true)} landing=true;panelKey='';clk.setTime(T0);setBase(startBase(),true);mv.jump(home());mv.kick()}
on('evprev',function(){clk.setPlaying(false);clk.setTime(stepBy(-1,t))}); on('evnext',function(){clk.setPlaying(false);clk.setTime(stepBy(1,t))}); on('step',function(){setStep(stepI+1)});
WM.panelClicks(panel,select);
panel.addEventListener('click',function(e){var b=e.target.closest('[data-ev]');if(!b)return;var ev=B.events.filter(function(x){return x.id===b.getAttribute('data-ev')})[0];if(ev){clk.setPlaying(false);if(b.hasAttribute('data-evu')){sel=null;panelKey=''}clk.setTime(ev.t);frameEvent(ev)}});
panel.addEventListener('click',function(e){var b=e.target.closest('[data-lnk]');if(b)openLink(b.getAttribute('data-lnk'))});
panel.addEventListener('toggle',function(e){if(e.target.classList&&e.target.classList.contains('cbls'))lnkOpen=e.target.open},true);
panel.addEventListener('click',function(e){var b=e.target.closest('[data-base]');if(!b)return;setBase(b.getAttribute('data-base'));info=true;rcSel=null;panelKey='';mv.kick()});   // a map offered in the map details
panel.addEventListener('toggle',function(e){if(!e.target.classList)return;
  if(e.target.classList.contains('nowd')){nowOpen=e.target.open;return}
  if(e.target.classList.contains('onmap')){grpOpen[e.target.getAttribute('data-g')]=e.target.open;return}
  /* the Now text changes only when the reader opens or closes it, except that folding the unit details away opens it again */
  if(e.target.classList.contains('umd')){umdOpen=e.target.open;if(!umdOpen&&!nowOpen){var nd=panel.querySelector('details.nowd');nowOpen=true;if(nd)nd.open=true}return}
  if(e.target.classList.contains('sums'))sumsOpen=e.target.open;else if(e.target.classList.contains('evs'))evOpen=e.target.open},true);
panel.addEventListener('click',function(e){var b=e.target.closest('[data-day]');if(b){jumpToDay(+b.getAttribute('data-day'),'day');return} if(e.target.closest('#sumgo'))goOn()});
function goOn(){closeSummary();glide=Date.now()+FOL.glide_ms;clk.setPlaying(true)}
on('cont',goOn);
['off','day','week'].forEach(function(k){on('pz-'+k,function(){setPause(k)})});
onCheck('cDayEnds',setDayEnds);
/* a long battle asks, the first time it is played, whether to stop at the end of each day */
function ask(){var a=$('ask'),n=Math.round(NDAYS+(byDay?1:0)),long=n>60;   // a campaign of months is not offered a stop every day: there would be hundreds
  $('askq').textContent=(long?'This campaign runs '+n+' days. Stop at the end of each week':'This battle runs '+n+' days. Stop at the end of each day')+' for a summary of what happened?';
  $('ask-day').hidden=long;a.hidden=false;$(long?'ask-week':'ask-day').focus()}
['day','week','off'].forEach(function(k){on('ask-'+k,function(){$('ask').hidden=true;setPause(k);glide=Date.now()+FOL.glide_ms;clk.setPlaying(true)})});

/* ---------- a link to this view ---------- */
/* The page address carries the moment, the map, the place and zoom, and the unit picked, so a copied link opens the same view. */
function linkHash(){var c=mv.map.getCenter(),p=['at='+B.isoOf(byDay?Math.round(t):Math.round(t)),'map='+base.id,'view='+c.lng.toFixed(5)+','+c.lat.toFixed(5)+','+mv.map.getZoom().toFixed(2)];if(sel)p.push('unit='+encodeURIComponent(sel));return '#'+p.join('&')}
var hashT=0; function noteView(){clearTimeout(hashT);hashT=setTimeout(function(){try{history.replaceState(null,'',linkHash())}catch(_){ }},500)}
function readLink(){var q={};String(location.hash||'').replace(/^#/,'').split('&').forEach(function(kv){var i=kv.indexOf('=');if(i>0)q[kv.slice(0,i)]=decodeURIComponent(kv.slice(i+1))});
  if(q.at||q.unit||q.view) landing=false;   // a link to a moment opens on that moment, units and all
  try{ if(q.map&&bases.some(function(b){return b.id===q.map})) setBase(q.map);
    if(q.at){var v=B.time(q.at);if(isFinite(v))clk.setTime(v)}
    if(q.view){var a=q.view.split(',').map(Number);if(a.length===3&&a.every(isFinite)){setFollow(false);setPreset(null);mv.jump({center:[a[0],a[1]],zoom:a[2]})}}
    if(q.unit&&B.track(q.unit)) select(q.unit);
  }catch(_){ }}
on('bLink',function(){var url=location.href.split('#')[0]+linkHash(),ok=$('linkok'),done=function(){ok.hidden=false;setTimeout(function(){ok.hidden=true},1600)};
  try{history.replaceState(null,'',linkHash())}catch(_){ }
  if(navigator.clipboard&&navigator.clipboard.writeText)navigator.clipboard.writeText(url).then(done,function(){ok.textContent='Copy it from the address bar';done()});else{ok.textContent='Copy it from the address bar';done()}});

/* ---------- start ---------- */
try{if(DE_OK&&localStorage.getItem('wm.'+B.id+'.dayends')==='1'){deOn=true;tick('cDayEnds',true)}}catch(e){}
try{if(localStorage.getItem('wm.'+B.id+'.arrow')==='0'){arwOn=false;tick('cArrow',false)}}catch(e){}
try{if(EVH_OK&&localStorage.getItem('wm.'+B.id+'.evh')==='0'){evhOn=false;tick('cEvh',false)}}catch(e){}
try{if(localStorage.getItem('wm.'+B.id+'.hill')==='0'){hsOn=false;tick('cHill',false)} if(localStorage.getItem('wm.'+B.id+'.mute')==='0'){muteOn=false;tick('cMute',false);wrap.classList.add('vivid')} if(localStorage.getItem('wm.'+B.id+'.names')==='0'){names=false;tick('cNames',false)} if(localStorage.getItem('wm.'+B.id+'.narr')==='1'){narrOn=true;tick('cNarr',true);wrap.classList.add('narr-on')} var fs=localStorage.getItem('wm.'+B.id+'.form'); if(FM&&fs!=null){fmOn=fs==='1';tick('cForm',fmOn)} var ts=localStorage.getItem('wm.'+B.id+'.trail'); if(TRL&&ts!=null){trlOn=ts==='1';tick('cTrail',trlOn)}}catch(_){ }
setStep(stepNear(P.rate||(byDay?1:5)));
if(P.views) preset=P.views[0].preset;
base=startBase();
mv.start(function(){buildBase();paintTime(T0);(P.views||[]).forEach(function(v){press('v-'+v.preset,preset===v.preset)});setBase(base,true);clk.setTime(T0);readLink();WM.hint(mv)});
var api={battle:B,setTime:clk.setTime,select:select,setFollow:setFollow,setBase:setBase,setNames:setNames,setUnits:setUnits,setFold:setFold,setPreset:setPreset,mv:mv,
  focus:function(){var f=focusPoint();return f?WORLDS[worldOf(base)].toLL(f):null},setNarrative:setNarr,setSymbols:setSymbols,setSeenFrom:setSeenFrom,setOpacity:setOpacity,setStep:setStep,link:linkHash,
  begin:function(){landing=false;panelKey='';mv.kick()},setFormations:setFormations,setMute:setMute,setHill:setHill,
  scene:function(){var f=evFocus();return scene().map(function(o){return {id:o.tr.id,kind:o.s.kind,row:o.s.k.id,drawn:o.drawn,c:o.s.g?cen(o.s.g):null,dim:!!(f&&!f[o.tr.id])}})}};   // c: where it stands, in the frame's metres; dim: faded by the event focus (BP-32)
Object.defineProperty(api,'view',{get:function(){return {s:mv.scale()}}}); Object.defineProperty(api,'base',{get:function(){return base.id}}); Object.defineProperty(api,'landing',{get:function(){return landing}}); Object.defineProperty(api,'summary',{get:function(){return sumAt==null?null:{at:sumAt,mode:sumMode}}});
api.stops=function(m){return stopsFor(m)};api.merging=function(){return Object.keys(mrg)};api.stopAt=stopAt;
Object.defineProperty(api,'modern',{get:function(){return {on:!!modOn,off:modOff,hill:!!hsVis}}});
global.__wm=api; return api;
};
})(window);
