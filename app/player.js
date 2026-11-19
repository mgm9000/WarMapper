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
bases.forEach(function(b){b.m=b.map?B.maps[b.map]:null;b.own=!!(b.m&&b.m.own);b.sat=!!(b.imagery&&b.imagery.tiles)});
var SKK=1e-5; function ownLL(p){return [p[0]*SKK,-p[1]*SKK]}   // a not-to-scale map: its pixels laid out as a small patch of pretend ground
var bm=P.bounds&&B.maps[P.bounds],EXT=bm?bm.box:B.ext;
var WORLDS={ground:{toLL:B.toLL,ext:EXT,mPerUnit:1,maxScale:Z.max||2,minFactor:Z.min_factor||0.9}};
bases.forEach(function(b){if(b.own)WORLDS['own:'+b.map]={toLL:ownLL,ext:[0,0,b.m.size[0],b.m.size[1]],mPerUnit:SKK*EARTH/360,maxScale:3,minFactor:0.9}});
/* The modern map: today's topographic map from a tile service. It is the current map, it shows through a period map that is turned down,
   and it lies around a period map where that ends, so the reader can zoom out past the sheet. The battle's own drawing of today's roads
   and water (the base data) is the fall-back, shown only if the service cannot be reached. */
var MOD=(function(){var m=P.modern||P.surround;return m&&m.tiles?m:null})(),modOn=null,modFail=0,modOff=false;
function topo(){return !!MOD&&!modOff}
/* Terrain shading: shadows drawn from elevation tiles, laid over today's map and under the period maps, kept out of the muting so the
   lie of the land stays plain. Every battle gets it unless its file says hillshade:false; hillshade:{exaggeration, tiles, ...} tunes it. */
var HS=(function(){if(P.hillshade===false)return null;var h={tiles:'https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png',encoding:'terrarium',max_zoom:15,exaggeration:0.8,
  credit:'Terrain Tiles (Mapzen, AWS Open Data)',link:'https://github.com/tilezen/joerd/blob/master/docs/attribution.md'},o=P.hillshade||{};for(var k in o)h[k]=o[k];return h})(),hsOn=true,hsVis=null,hsFail=0;
function paintHill(){ if(!HS) return; var on=hsOn&&hsFail<4&&!base.sat&&!!(modOn||base.current); if(on!==hsVis){hsVis=on;mv.show('hill',on);lastCredit=''} }
if(MOD){(function(){var f=(+MOD.reach||(bm?4:2))/2,cx=(EXT[0]+EXT[2])/2,cy=(EXT[1]+EXT[3])/2,hw=Math.abs(EXT[2]-EXT[0])*f,hh=Math.abs(EXT[3]-EXT[1])*f;var r=[cx-hw,cy-hh,cx+hw,cy+hh];
  B.mapList.forEach(function(m){if(m.own)return;m.images.forEach(function(im){var b=im.box;if(!b)return;b=[Math.min(b[0],b[2]),Math.min(b[1],b[3]),Math.max(b[0],b[2]),Math.max(b[1],b[3])];var mx=(b[2]-b[0])*0.3,my=(b[3]-b[1])*0.3;   // room to zoom out past every period map, so the modern map is seen around it
    r=[Math.min(r[0],b[0]-mx),Math.min(r[1],b[1]-my),Math.max(r[2],b[2]+mx),Math.max(r[3],b[3]+my)]})});
  WORLDS.ground.reach=r})()}
function inQuad(p,Q){var s=0,i,a,b,c;for(i=0;i<4;i++){a=Q[i];b=Q[(i+1)%4];c=(b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0]);if(c){if(s&&(c>0)!==(s>0))return false;s=c}}return true}
/* Under a period map at full strength the modern map is asked for only while some of the screen lies beyond the picture, so nothing is fetched until the reader zooms or pans out past it. */
function paintModern(H){ if(!MOD) return; var on=false;
  if(!modOff&&!base.own&&!base.sat){var m=base.series?H:base.m,Q=m&&!m.own?m.ll:null,z=mv.size();
    on=!!(base.current||base.backdrop==='current'||through()||!Q||[[0,0],[z.w,0],[z.w,z.h],[0,z.h]].some(function(q){var l=mv.map.unproject(q);return !inQuad([l.lng,l.lat],Q)}))}
  if(on!==modOn){modOn=on;mv.show('sur',on);panelKey=''} }
/* The map a battle opens on: a period map if it covers all of the opening view, otherwise the current map. `start_base` overrides. */
function startBase(){ var byId=P.start_base&&bases.filter(function(b){return b.id===P.start_base})[0]; if(byId) return byId;
  var V=raw.view,bx=(P.views&&V.presets&&V.presets[P.views[0].preset])||V.extent,dx=(bx[2]-bx[0])*0.04,dy=(bx[3]-bx[1])*0.04,C=[[bx[0]+dx,bx[1]+dy],[bx[2]-dx,bx[1]+dy],[bx[2]-dx,bx[3]-dy],[bx[0]+dx,bx[3]-dy]];
  var per=bases.filter(function(b){return b.m&&!b.own&&!b.series&&C.every(function(c){return inQuad(c,b.m.ll)})})[0];
  return per||bases.filter(function(b){return b.current})[0]||bases[0]}
function worldOf(b){return b.own?'own:'+b.map:'ground'}

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
  var V=key==='g'?b.via:(b.vo&&b.vo[key]),G=geo(b,key);   // a picture not to scale may carry the route in its own pixels (vo)
  if(V&&V.length>1&&G){ if(f>0.92&&G.length>1){return lerpG([alongP(V,0.92)],G,(f-0.92)/0.08)} return [alongP(V,Math.min(f/0.92,1))]; }
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
   of its last, and the move to the next takes the day before it. A unit the sources stop following stays, faded, for two days, then leaves the map. */
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
      var ms=Math.max(e,nx.t0-1-LEAD_IN),me=nx.t0-LEAD_IN;   // the move takes a whole day, ending as the next record comes in
      if(tt<ms) return (g&&tt<=e+LINGER)?{k:k,g:g,kind:'after'}:{k:k,g:null,kind:g?'lost':noPlace(k,key)};
      if(g&&gn) return {k:nx,from:k,g:morph(g,gn,ease((tt-ms)/Math.max(0.01,me-ms))),kind:'moving'};
      if(g) return {k:k,g:g,kind:'after'};
      return {k:nx,g:null,kind:noPlace(nx,key)};
    }
  }
  var last=ks[n-1],gl=geo(last,key); if(!gl) return {k:last,g:null,kind:noPlace(last,key)};
  return tt<=last.t1+LINGER?{k:last,g:gl,kind:'after'}:{k:last,g:null,kind:'lost'};
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
function home(){return preset?cameraOf(preset):((follow&&!landing)?target():mv.cameraFor(base.own?WORLDS[worldOf(base)].ext:EXT,{t:48,b:22,l:14,r:14}))}
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
   stood over BRK_MS, and the clock waits for them. Two or more new units from the same parent make a breakout; a seek does not. */
var BRK_MS=2500,brk={},lastW=null,lastT=null,holdUntil=0;
function parentsOf(uid){var out=[],d=stamp(t),seen=0;while(uid&&seen++<6){var u=B.units[uid];if(!u)break;var as=u.assignments||[],a=null;
    as.forEach(function(x){var f=x.from?B.time(x.from):-1e9,e=x.to?B.time(x.to)+((!byDay&&x.to.length===10)?1439:0):1e9;if(d>=f&&d<=e)a=x});
    a=a||as[as.length-1];if(!a||!a.parent)break;out.push(a.parent);uid=a.parent}return out}
function zoomSig(){return [FM&&(fmForced()||(fmOn&&!base.own&&sNow<FM.below)),sNow<(Z.fold||0)].concat((P.groups||[]).map(function(G){return sNow<G.below})).join()}
function breakouts(L){var now=Date.now(),W={},inv=function(q){return mv.map.unproject(q)},sig=zoomSig(),ok=clk&&clk.playing&&lastW&&lastT!=null&&t>=lastT&&t-lastT<(byDay?2:30)&&lastW.sig===sig,born={};
  L.forEach(function(u){var tr=u.o.tr;if(!tr.id||u.noSym)return;var ll=inv([u.c[0],u.c[1]]);W[tr.unit]=W[tr.unit]||[ll.lng,ll.lat];
    if(ok&&!lastW.ids[tr.id]&&!brk[tr.id]){var ps=parentsOf(tr.unit);for(var i=0;i<ps.length;i++){if(lastW.pos[ps[i]]){(born[ps[i]]=born[ps[i]]||[]).push(tr.id);break}}}});
  Object.keys(born).forEach(function(p){if(born[p].length<2)return;born[p].forEach(function(id){brk[id]={from:lastW.pos[p],t0:now}});holdUntil=now+BRK_MS});
  L.forEach(function(u){var tr=u.o.tr,b=tr.id&&brk[tr.id];if(!b)return;var f=(now-b.t0)/BRK_MS;if(f>=1){delete brk[tr.id];return}
    var e=1-Math.pow(1-f,3),q=mv.map.project(b.from),dx=(q.x-u.c[0])*(1-e),dy=(q.y-u.c[1])*(1-e);u.x+=dx;u.y+=dy;u.pts=u.pts.map(function(p){return [p[0]+dx,p[1]+dy]});mv.kick()});
  var ids={};L.forEach(function(u){if(u.o.tr.id&&!u.noSym)ids[u.o.tr.id]=1});lastW={pos:W,ids:ids,sig:sig};lastT=t}
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
  for(var i=0;i<L.length;i++)for(var pass=0;pass<4;pass++){var moved=false;for(var j=0;j<i;j++){var a=L[i],b=L[j];if(a.noSym||b.noSym)continue;if(Math.abs(a.x-b.x)<27&&Math.abs(a.y-b.y)<21){var sx=a.x>=b.x?1:-1,sy=a.y>=b.y?1:-1;if(Math.abs(a.x-b.x)>Math.abs(a.y-b.y))a.x=b.x+sx*28;else a.y=b.y+sy*22;a.nudged=true;moved=true}}if(!moved)break}
  var R=[]; function hit(r){for(var i=0;i<R.length;i++){var q=R[i];if(r[0]<q[2]&&r[2]>q[0]&&r[1]<q[3]&&r[3]>q[1])return true}return false}
  L.forEach(function(u){if(!u.noSym)R.push([u.x-14,u.y-19,u.x+14,u.y+10]);
    if(!compact) for(var i=1;i<u.pts.length&&u.line;i++){var a=u.pts[i-1],b=u.pts[i],d=Math.hypot(b[0]-a[0],b[1]-a[1]),n=Math.max(1,Math.round(d/11));
      for(var j=0;j<=n;j++){var qx=a[0]+(b[0]-a[0])*j/n,qy=a[1]+(b[1]-a[1])*j/n;R.push([qx-4,qy-4,qx+4,qy+4])}}});
  // names, most important units first; a crowded name is dropped (the unit stays tappable)
  var phoneW=wrap.clientWidth<=560,force=!phoneW&&!compact&&sNow>=(Z.force_names_from||0);
  var fewer=phoneW&&sNow<(Z.phone_names||(compact?(Z.full_names||1e9):0.6));   // phones, zoomed out: no names for small parts (artillery, detachments, sub-units) until zoomed in
  L.forEach(function(u){
    u.lab=null; if(u.noSym||(!names&&!(sel&&u.o.tr.id===sel))) return; if(fewer&&u.pr>=3) return;
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
function unitSvg(u,part){   // the last position on record stays plain to see: dashed, barely faded
  var o=u.o,tr=o.tr,s=o.s,pts=u.pts,lk=look(tr),col=lk.col,k=s.kind;
  var soft=(k==='moving'||k==='early'||k==='after'||k==='unplaced'),low=u.low,op=k==='unplaced'?0.5:k==='after'?0.8:1,isSel=!!tr.id&&sel===tr.id,h='',x=u.x,y=u.y,c=u.c;
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
      h+='<rect x="'+f1(c[0]-9)+'" y="'+f1(c[1]-4)+'" width="18" height="8" fill="'+col+'" stroke="var(--u-halo)" stroke-width="1.5"'+((soft||low)?' fill-opacity=".55"':'')+'/>'}
    if(u.lab){h+='<text class="ulab" text-anchor="'+u.lab[4]+'" x="'+f1(u.lab[5])+'" y="'+f1(u.lab[6])+'">'+esc(u.txt)+'</text>';mv.hits.push({id:tr.id,r:[u.lab[0],u.lab[1],u.lab[0]+u.w,u.lab[1]+16]})}
    return h+'</g>'}
  var foe=!!seenFrom&&tr.side!==seenFrom,D=W+1;   // seen from one side, the other side's units take the diamond frame of the standard symbols
  h+='<g opacity="'+op+'">'; mv.hits.push({id:tr.id,r:[x-W-4,y-H-11,x+W+4,y+H+4]});
  if((compact&&u.line)||u.nudged) h+='<line x1="'+f1(c[0])+'" y1="'+f1(c[1])+'" x2="'+f1(x)+'" y2="'+f1(y)+'" stroke="'+(compact?col:'var(--u-ink)')+'" stroke-width="'+(compact?1.2:1)+'"/>';
  if(u.nudged&&!(compact&&u.line)) h+='<circle cx="'+f1(c[0])+'" cy="'+f1(c[1])+'" r="2.5" fill="'+col+'"/>';
  h+='<g transform="translate('+f1(x)+' '+f1(y)+')">';
  if(isSel) h+='<rect x="'+(-W-5)+'" y="'+(foe?-D-4:-H-5)+'" width="'+(2*W+10)+'" height="'+(foe?2*D+8:2*H+10)+'" rx="4" fill="none" stroke="var(--m-sel)" stroke-width="4"/>';
  var dsh=((soft||low)?' stroke-dasharray="3 2.5"':''),q=D/2;
  if(foe){h+='<path d="M0 '+(-D)+'L'+D+' 0L0 '+D+'L'+(-D)+' 0Z" fill="none" stroke="var(--u-halo)" stroke-width="5" stroke-linejoin="round"/>'+'<path d="M0 '+(-D)+'L'+D+' 0L0 '+D+'L'+(-D)+' 0Z" fill="'+lk.fill+'" stroke="'+col+'" stroke-width="1.8"'+dsh+'/>';
    if(tr.ech==='headquarters') h+='<text class="ech in" text-anchor="middle" y="3.5" style="stroke:none">HQ</text>';
    else if(tr.branch==='inf') h+='<path d="M'+(-q)+' '+(-q)+'L'+q+' '+q+'M'+(-q)+' '+q+'L'+q+' '+(-q)+'" stroke="'+col+'" stroke-width="1.4"/>';
    else if(tr.branch==='cav') h+='<path d="M'+(-q)+' '+q+'L'+q+' '+(-q)+'" stroke="'+col+'" stroke-width="1.4"/>';
    else h+='<circle r="3.2" fill="'+col+'"/>';
    h+='<text class="ech" text-anchor="middle" y="'+(-D-3)+'">'+(ECH[tr.ech]||'')+'</text></g>';}
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
function mapNames(L,cover){
  var z=mv.size(),lvl=sNow>=(Z.labels||0)?1:0,h='',cur=!!(base.current||base.sat||base.backdrop==='current'||through()),tp=cur&&!base.sat&&topo();
  var TER={ridge:1,hill:1},LB=B.labels.filter(function(l){return TER[l.k]}).concat(B.labels.filter(function(l){return !TER[l.k]}));   // the lie of the land is named first, so roads and woods give way to it
  LB.forEach(function(l){
    var show=l.show||'current'; if(cur?show==='period':show==='current') return;
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
      if(l.k==='town'&&Z.towns_until&&sNow>Z.towns_until) return; if(l.k==='wood'&&sNow<(Z.woods_from||0)) return;
      var aw=l.t.length*(l.k==='town'?8.6:l.k==='wood'?5.9:8.2)/2,ar=[q[0]-aw,q[1]-9,q[0]+aw,q[1]+7]; if(L.hit(ar)) return; L.keep(ar);
      h+='<text class="'+(l.k==='wood'?'wl':'al'+(l.k==='town'?' town':''))+'" text-anchor="middle" x="'+f1(q[0])+'" y="'+f1(q[1]+4)+'">'+esc(l.t)+'</text>'; return}
    // a place or a landmark: a dot, and its name if there is room
    if(l.k==='landmark'&&sNow<(Z.landmarks_from||0)) return;
    var big=l.k==='place'&&l.l===0,full=l.s&&sNow>=(Z.full_names||1e9),txt=l.t+(full?' ('+l.s+')':''),w=txt.length*(big?6.6:5.9)+4,pr=[q[0]+5,q[1]-15,q[0]+8+w,q[1]-1],hid=L.hit(pr);
    h+='<circle cx="'+f1(q[0])+'" cy="'+f1(q[1])+'" r="'+(big?3:2.2)+'" fill="var(--u-ink)" opacity="'+(big?1:.7)+'"/>'; if(hid) return; L.keep(pr);
    h+='<text class="'+(l.k==='place'?'pl'+(big?' big':''):'lm')+'" x="'+f1(q[0]+7)+'" y="'+f1(q[1]-4)+'">'+esc(l.t)+(full?' <tspan class="old">('+esc(l.s)+')</tspan>':'')+'</text>'});
  return h}
function seriesAt(){var d=Math.max(T0,stamp(t));for(var i=0;i<series.length;i++)if(d>=series[i].t0&&d<=series[i].t1)return series[i];return series[series.length-1]}
var seriesShown=null,lastCredit='';
function showSeries(H){ if(H===seriesShown) return; if(H){mv.moveImage('pic-series',WM.asset(H.images[0].file),H.images[0].ll);if(!seriesShown)mv.show('pic-series',true)} else mv.show('pic-series',false); seriesShown=H }
function paintCredit(H){var c,mc=MOD?(MOD.link?'<a href="'+esc(MOD.link)+'" target="_blank" rel="noopener">'+esc(MOD.credit)+'</a>':esc(MOD.credit)):'',now=topo()?mc:WM.OSM_CREDIT;
  if(base.current) c=now;
  else if(base.sat){var im=base.imagery;c=(im.link?'<a href="'+esc(im.link)+'" target="_blank" rel="noopener">'+esc(im.credit)+'</a>':esc(im.credit))+' &middot; Names: '+WM.OSM_CREDIT}
  else{var m=H||base.m,und=base.backdrop==='current'||through(); c=(H?esc(m.short)+', '+esc(m.label)+(stamp(t)>m.t1?' (the last one)':'')+' &middot; ':'')+esc(m.credit)+(und?' &middot; '+now:(modOn?' &middot; Around it: '+mc:''))}
  if(hsVis) c+=' &middot; Terrain shading: <a href="'+esc(HS.link)+'" target="_blank" rel="noopener">'+esc(HS.credit)+'</a>';
  if(c!==lastCredit){lastCredit=c;$('credit').innerHTML=c}}
function draw(){
  sNow=mv.scale(); mv.hits.length=0;
  var H=base.series?seriesAt():null; if(series.length) showSeries(H); paintModern(H); paintHill(); paintCredit(H);
  var cover=base.backdrop==='current'?(H||base.m).box:null;
  var sc=scene(),L=layout(unitsOn&&!landing?sc:[]),h=mapNames(L,cover);   // on landing the map is shown alone; the units come on when the battle is started
  L.sort(function(a,b){return (a.o.tr.id===sel)-(b.o.tr.id===sel)});   // the selected unit last, so it sits on top
  h+=trailsSvg(); L.forEach(function(u){h+=unitSvg(u,'line')}); L.forEach(function(u){h+=unitSvg(u,'sym')}); ov.innerHTML=h;
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
}
/* The period map can be turned down to let today's map show through it. Turned down, only a map's whole-sheet picture shows, so two pictures of one map do not add up. */
function through(){return opac<1&&!base.current&&!base.own&&!base.sat}
function paintFade(){(PICS[base.id]||[]).forEach(function(p){mv.opacity(p.id,opac>=1?1:p.detail?0:opac)});if(series.length)mv.opacity('pic-series',opac);
  bases.forEach(function(b){if(b.sat)mv.map.setLayoutProperty('sat-'+b.id,'visibility',b===base?'visible':'none')});
  var cur=!!(base.current||base.backdrop==='current'||through()),own=cur&&!topo();   // the battle's own drawing of today's ground shows only when the modern map cannot
  CUR.forEach(function(id){mv.show(id,own)});mv.show('b-mask',!topo()&&(cur||base.sat)&&!!(base.clip||(base.m&&P.bounds===base.map)));
  mv.bg((base.own||(base.m&&base.backdrop!=='current'&&!through()))?'--m-paper':'--land')}
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
  if(e&&e.sourceId==='dem'){ if(++hsFail>=4){hsVis=null;mv.show('hill',false);lastCredit='';mv.kick()} return }
  if(e&&e.sourceId==='sur'){ if(++modFail>=4&&!modOff){modOff=true;modOn=null;mv.show('sur',false);paintFade();lastCredit='';panelKey='';mv.kick()} return }   // the modern map cannot be reached: fall back to the drawing
  var er=e&&e.error,txt=String((er&&(er.url||er.message))||''),mine=(e&&/^iiif-/.test(String(e.sourceId||'')))||/iiif/i.test(txt)||(Object.keys(TILES).length&&/fetch|network|load/i.test(txt));
  if(mine&&++tileFail>=3&&!tilesOff){tilesOff=true;updateTiles();panelKey='';mv.kick()}}
function setBase(b,first){
  if(typeof b==='string') b=bases.filter(function(x){return x.id===b})[0]; if(!b) return;
  var moved=first||worldOf(b)!==worldOf(base); base=b;
  bases.forEach(function(x){if(!x.of)press('b-'+x.id,x===b||b.of===x.id);(PICS[x.id]||[]).forEach(function(p){mv.show(p.id,x===b)})});
  if(moved) mv.setWorld(worldOf(b));
  if(!b.series&&series.length){mv.show('pic-series',false);seriesShown=null}
  if(b.series) series.forEach(function(m){if(!m.pre){m.pre=new Image();m.pre.src=WM.asset(m.images[0].file)}});
  wrap.classList.toggle('paper',!b.current&&!b.sat); wrap.classList.toggle('sat',b.sat); var go=$('gOpac'); if(go) go.hidden=!!(b.current||b.own||b.sat); paintFade();
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
  if(info&&!sel){var ik='info|'+base.id+'|'+(seriesShown?seriesShown.id:'');if(ik!==panelKey){panelKey=ik;panel.innerHTML=mapDetails()+aroundNote();panel.scrollTop=0}return}
  var key=base.id+'|'+(sel?sel+'|'+(me?me.s.k.id+me.s.kind+(byDay?stamp(t):''):'x'):'now|'+(landing?'L':'')+(ev?ev.id:0)+'|'+sc.map(function(o){return o.tr.id+(o.drawn?1:0)+o.s.kind+o.s.k.id}).join(','));
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
  } else {
    h+='<div class="eyebrow">'+esc(ev?'Now: '+ev.name:B.opening.label)+'</div><p class="phase">'+esc(ev?ev.text:B.opening.text)+'</p>';
    if(landing) h+='<p class="meta start">Press play to begin. The units come onto the map as the battle starts.</p>';
    if(B.events.length){h+='<details class="evs"'+(evOpen?' open':'')+'><summary>Key events: jump to one</summary><ul class="evl">';
      B.events.forEach(function(e){h+='<li><button data-ev="'+esc(e.id)+'"'+(ev&&ev.id===e.id?' class="cur"':'')+'><span class="tm">'+esc(whenText(e.t))+'</span><span>'+esc(e.full)+'</span></button></li>'});h+='</ul></details>'}
    var groups=[],seen={}; (byNation?(raw.nations||[]).map(function(n){return [n.name,n.short]}):raw.sides.map(function(s){return [s.code,s.short]})).forEach(function(g){groups.push(g);seen[g[0]]=1});
    groups.forEach(function(g){var Ls=sc.filter(function(o){return (o.drawn||o.folded)&&look(o.tr).group===g[0]});if(!Ls.length)return;
      h+='<h3>'+esc(g[1])+' on the map</h3><ul class="ulist">';Ls.forEach(function(o){h+=item(o,status(o))});h+='</ul>'});
    var nd=sc.filter(function(o){return !o.hidden&&!o.folded&&o.s.kind!=='lost'&&(!o.drawn||o.s.kind==='unplaced')});
    if(nd.length){h+='<h3>'+(base.own?'Not on this map or not placed':'Not placed right now')+'</h3><ul class="nd">';
      nd.forEach(function(o){var kd=o.s.kind;h+='<li><b>'+esc(o.tr.label)+'</b>: '+esc(kd==='offmap'?o.tr.offmap:o.s.k.act+(kd==='offthis'?' (not on this map)':'. No position on record.'))+'</li>'});h+='</ul>'}
    var lo=sc.filter(function(o){return o.s.kind==='lost'});
    if(lo.length){h+='<h3>No longer followed by the sources</h3><ul class="ulist">';lo.forEach(function(o){h+=item(o,'last placed '+o.s.k.te.split(' or later')[0].split(' to ').pop())});h+='</ul>'}
    h+='<p class="meta" style="margin-top:14px">Tap a unit for its source and how sure the position is.</p>'+about();
  }
  panel.innerHTML=h; if(sel) panel.scrollTop=0;
}
function select(id){
  if(id&&String(id).indexOf('F:')===0){ // a formation drawn zoomed out: zoom in on it until it breaks out into its units
    var hit=null;mv.hits.forEach(function(h){if(h.id===id&&h.r)hit=h}); if(hit){setFollow(false);setPreset(null);var W=WORLDS[worldOf(base)],c=mv.map.unproject([(hit.r[0]+hit.r[2])/2,(hit.r[1]+hit.r[3])/2]);
      mv.map.easeTo({center:c,zoom:mv.zoomFor(FM.below*1.15),duration:700})} return }
  sel=id||null;info=false;panelKey='';if(sel&&sheet)sheet.open();if(sel&&pane)pane.show();mv.kick()}
var evOpen=false;
/* what lies around the map on screen, where the battle has a surround */
function aroundNote(){ if(!topo()||base.own||base.sat||base.current) return '';
  return '<div class="eyebrow" style="margin-top:18px">Around this map</div><p>Zoom out past the edge of this map and today\'s topographic map is drawn around it.</p><dl><dt>Source</dt><dd>'+esc(MOD.name?MOD.name+' ('+MOD.credit+')':MOD.credit)+'</dd>'+(MOD.rights?'<dt>Rights</dt><dd>'+esc(MOD.rights)+'</dd>':'')+'</dl>'}
/* the map on screen: what it is, who made it, where it is held, how it was placed */
function mapDetails(){var h='<button class="back" id="back">&larr; All units</button><div class="eyebrow">The map on screen</div>',row=function(k,v){return v?'<dt>'+k+'</dt><dd>'+esc(v)+'</dd>':''};
  h+='<p class="meta credits">Credits for what is on screen: '+lastCredit+'</p>';
  if(base.sat){var im=base.imagery;h+='<h2>'+esc(im.name||base.label)+'</h2><p>'+esc(im.about||'Aerial or satellite imagery of the ground today, streamed from the provider\'s tile service. The names on it come from OpenStreetMap.')+'</p><dl>'+row('Source',im.credit)+row('Rights',im.rights||'')+row('Taken',im.date||'')+'</dl>'+(im.link?'<p style="margin-top:10px"><a href="'+esc(im.link)+'" target="_blank" rel="noopener">About this imagery</a></p>':'')+'<p class="meta" style="margin-top:12px">If the tile service cannot be reached, the map shows plain ground under the units.</p>';return h}
  if(base.current&&topo()){h+='<h2>'+esc(MOD.name||'Current map')+'</h2><p>'+esc(MOD.about||'Today\'s topographic map, streamed from the provider\'s tile service.')+'</p><dl>'+row('Source',MOD.credit)+row('Rights',MOD.rights||'')+'</dl>'+(MOD.link?'<p style="margin-top:10px"><a href="'+esc(MOD.link)+'" target="_blank" rel="noopener">About this map</a></p>':'')+'<p class="meta" style="margin-top:12px">If the map service cannot be reached, a plain drawing of today\'s roads and water, made from OpenStreetMap, is shown in its place.</p>'+hillAbout();return h}
  if(base.current){h+='<h2>Current map</h2>'+(MOD?'<p class="meta">The topographic map service could not be reached from here, so this plain drawing is shown in its place.</p>':'')+'<p>Today\'s roads, water, railways, woods and names, cut down from OpenStreetMap to what this battle needs. It is a drawing of that data, not a live map service.</p><dl>'+row('Source','OpenStreetMap contributors')+row('Rights','Open Database License')+'</dl><p style="margin-top:10px"><a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap copyright and licence</a></p>';return h}
  var m=(base.series&&seriesShown)||base.m||series[0],s=B.sources[m.raw.source]||{},f=m.raw.fit||{},fit='';
  if(m.own) fit='No. It is not to scale, so it is shown as a picture of its own and units have separate positions on it.';
  else{fit='Yes';if(f.method)fit+=': '+f.method;if(f.metres_per_pixel)fit+='; '+f.metres_per_pixel+' m per scan pixel';if(f.turn_degrees)fit+='; turned '+f.turn_degrees+'\u00b0 from north';if(f.points)fit+=': fitted on '+f.points+' points'+(f.misfit_m?', typical misfit '+f.misfit_m+' m':'');fit+='.'}
  h+='<h2>'+esc(m.title)+'</h2><dl>'+row('Battle',B.title)+row('Shows',m.label)+row('Made by',s.author)+row('Date',s.date)+row('Kind',s.type)+row('Published or held',s.citation)+row('Scale',m.raw.scale_note||(m.own?'Not to scale':''))+row('Rights',s.rights||'Not checked')+row('Placed on the ground',fit)+'</dl>';
  if(m.raw.note) h+='<p style="margin-top:10px">'+esc(m.raw.note)+'</p>';
  if(s.url) h+='<p style="margin-top:10px"><a href="'+esc(s.url)+'" target="_blank" rel="noopener">Open the original record</a></p>';
  var I=m.raw.iiif,host=I?I.service.split('/')[2]:'';
  h+='<p class="meta" style="margin-top:12px">'+(I&&!tilesOff?'The picture that comes with this page is a reduced copy. When you zoom in, the full scan is streamed in pieces from '+esc(host)+'; the 1:1 button shows it at full size.':I?'The picture shown is a reduced copy. The full scan could not be reached at '+esc(host)+' from here.':'The picture shown here is a reduced copy of the scan.')+'</p>';return h}

/* ---------- controls ---------- */
(function(){var h='',seg=function(label,items){return '<div class="seg" role="group" aria-label="'+label+'">'+items.join('')+'</div>'},
    btn=function(id,x){return '<button id="'+id+'" aria-pressed="false"'+(x.title?' title="'+esc(x.title)+'"':'')+'><span class="lg">'+esc(x.label)+'</span><span class="sm">'+esc(x.short||x.label)+'</span></button>'},
    chipb=function(id,label,title,on){return '<button class="chipbtn" id="'+id+'" aria-pressed="'+(on?'true':'false')+'" title="'+esc(title)+'"><span class="dot"></span><span>'+label+'</span></button>'};
  if(bases.length>1) h+=seg('Base map',bases.filter(function(b){return !b.of}).map(function(b){return btn('b-'+b.id,b)}));
  if(P.views) h+=seg('Map view',P.views.map(function(v){return btn('v-'+v.preset,v)}));
  if(P.follow) h+=chipb('bFollow','Follow<span class="long"> the action</span>','Keep the units in view as time moves (F)',true);
  h+='<button class="chipbtn" id="bLayers" aria-expanded="false" aria-controls="layers" title="What is drawn on the map, and how"><span>Layers</span><span class="car">&#9662;</span></button>';
  $('ctl').innerHTML=h;
  // the Layers menu: what is drawn, how units are drawn, and how much of the period map shows
  var ck=function(id,label,on,key){return '<label class="ck"><input type="checkbox" id="'+id+'"'+(on?' checked':'')+'><span>'+label+(key?'<kbd>'+key+'</kbd>':'')+'</span></label>'},
      sb=function(id,label,on){return '<button id="'+id+'" aria-pressed="'+(on?'true':'false')+'">'+esc(label)+'</button>'},L='';
  L+='<div class="grp"><div class="gh">Show</div>'+ck('cUnits','Units',true,'U')+ck('cNames','Unit names',true,'N')+((P.fold&&P.fold.label)?ck('cFold',esc(P.fold.label)+' when zoomed in',true):'')+(FM?ck('cForm',esc(FM.label||'Divisions')+' when zoomed out',fmOn):'')+(TRL?ck('cTrail','Routes taken',trlOn):'')
    +((MOD||bases.some(function(b){return b.sat}))?ck('cMute','Today\'s map in muted colours',muteOn):'')+(HS?ck('cHill','Terrain shading on today\'s map',hsOn):'')+ck('cPlaces','Place names',true)+ck('cLines','Road and stream names',true)+ck('cNarr','The current event, in words, on the map',false)+'</div>';
  L+='<div class="grp"><div class="gh">Unit symbols</div>'+seg('Symbol style',[sb('sy-standard','Standard',true),sb('sy-period','Period style',false)])+'<p class="gn">Period style drops the frames: a line is a bar, as on maps of the time.</p></div>';
  L+='<div class="grp"><div class="gh">Seen from</div>'+seg('Seen from',[sb('fr-none','Neither side',true)].concat(raw.sides.map(function(sd){return sb('fr-'+sd.code,sd.short,false)})))+'<p class="gn">Seen from one side, the other side takes the diamond frame of the standard military symbols.</p></div>';
  if(bases.some(function(b){return !b.current&&!b.own&&!b.sat})) L+='<div class="grp" id="gOpac"><div class="gh"><span>Period map</span><span id="opv">100%</span></div><input type="range" id="opac" min="0" max="100" step="5" value="100" aria-label="How strongly the period map is drawn"><p class="gn">Turn it down to see today&rsquo;s map through the period map.</p></div>';
  L+='<div class="grp"><button class="lnk" id="bLink">Copy a link to this view</button><span class="ok" id="linkok" hidden>Copied</span></div>';
  $('layers').innerHTML=L;
  var cb=$('clockbattle'); if(cb){cb.textContent=P.clock_title||B.title;cb.hidden=P.clock_title===''}   // the battle's name in the date box
  wrap.classList.toggle('compact',compact); $('when').classList.toggle('date',byDay); $('tl').classList.toggle('days',byDay);
  if(byDay){$('hint').innerHTML=$('hint').innerHTML.replace('to move time','to move through the days')}
})();

/* ---------- map and time ---------- */
try{ mv=WM.mapView({container:'map',wrap:wrap,world:worldOf(base),worlds:WORLDS,
  onDraw:draw,onPick:select,
  onUserMove:function(){if(follow)pauseFollow();if(preset||goal)setPreset(null)},
  onResize:function(){if(preset){mv.jump(cameraOf(preset));goal=null}else if(follow&&!landing)mv.jump(target());else if(landing)mv.jump(home())},
  onStep:function(ts){var more=(clk.playing&&Date.now()<holdUntil)?true:clk.step(ts);if(more)doSkip(ts);if(goal){if(mv.chase(goal,0.2))more=true;else goal=null}else if(follow&&!landing){if(Date.now()<fpause)more=true;else{if(fpause){resumeFollow();fpause=0}if(glide>Date.now()?mv.chase(target(),FOL.glide_rate):mv.chase(calmTarget(),FOL.rate,FOL.zoom_rate))more=true}}return more}});
}catch(err){WM.noMap(wrap,err);return null}
S=mv.S;
mv.map.on('moveend',queueTiles); mv.map.on('error',tileError);
/* the stretch before the part the data covers best (a night march before a fight) can be squeezed into a share of the bar and played faster */
var LD=(P.lead&&B.focus&&B.focus[0]>T0)?P.lead:null,TM=LD?B.focus[0]:T0,UM=LD?LD.share:0,RNG=4000;
function u2t(u){return (LD&&u<=UM)?T0+(TM-T0)*u/UM:TM+(T1-TM)*(u-UM)/(1-UM)}
function t2u(v){return (LD&&v<=TM)?UM*(v-T0)/(TM-T0):UM+(1-UM)*(v-TM)/(T1-TM)}
function paintTime(v){t=v; if(landing&&(v!==T0||(clk&&clk.playing))){landing=false;panelKey='';glide=Date.now()+FOL.glide_ms}   // the battle has been started: the units come on, and Follow takes the camera

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
clk=WM.clock({T0:T0,T1:T1,mv:mv,toRange:function(v){return Math.round(t2u(v)*RNG)},fromRange:function(v){return u2t(v/RNG)},
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
  if(byDay){var nth=0;for(m=T0;m<=T1;m++){var d=B.dateOf(m),maj=d.day%5===0;h+='<span class="tick'+(maj?' maj':'')+'" style="left:'+pc(m)+'"></span>';
      if(maj){h+='<span class="tk'+(nth%2?' minor':'')+'" style="left:'+pc(m)+'">'+d.day+' '+d.mon.slice(0,3)+'</span>';nth++}}}
  else{for(m=Math.ceil(T0/60)*60;m<TM;m+=60){h+='<span class="tick" style="left:'+pc(m)+'"></span>';if(m%120===0)h+='<span class="tk minor" style="left:'+pc(m)+'">'+fmt(m)+'</span>'}
    var st=lg?30:15,lb=lg?60:30;   // a long day: a tick each half hour and a time each hour
    for(m=Math.ceil(TM/30)*30;m<=T1;m+=st){h+='<span class="tick" style="left:'+pc(m)+'"></span>';if(m%lb===0)h+='<span class="tk'+(m%(lb*2)?' minor':'')+'" style="left:'+pc(m)+'">'+fmt(m)+'</span>'}}
  B.events.forEach(function(e){h+='<button class="ev'+(e.quiet?' mute':'')+'" data-id="'+esc(e.id)+'" data-t="'+e.t+'" style="left:'+pc(e.t)+'" title="'+esc(e.name)+'" aria-label="'+esc(e.name)+'">'+esc(e.name)+'</button>'});
  tl.insertAdjacentHTML('afterbegin',h);
  tl.addEventListener('click',function(ev){var b=ev.target.closest('.ev');if(b){clk.setPlaying(false);clk.setTime(+b.dataset.t)}});
})();
function on(id,fn){var e=$(id);if(e)e.addEventListener('click',fn)}
bases.forEach(function(b){if(!b.of)on('b-'+b.id,function(){if(base.of===b.id){var p=sheetToGround(base,mv.map.getCenter());setBase(b);if(p)mv.map.jumpTo({center:p,zoom:mv.zoomFor(0.2)})}else setBase(b)})});
(P.views||[]).forEach(function(v){on('v-'+v.preset,function(){setPreset(v.preset)})});
on('bFollow',function(){setFollow(!follow)});
document.addEventListener('keydown',function(e){var tg=(e.target&&e.target.tagName)||''; if(tg==='INPUT'||tg==='TEXTAREA'||e.metaKey||e.ctrlKey||e.altKey) return;
  var d={ArrowLeft:[-1,0],ArrowRight:[1,0],ArrowUp:[0,-1],ArrowDown:[0,1]}[e.key];
  if(d&&e.shiftKey){setFollow(false);setPreset(null);mv.map.panBy([d[0]*120,d[1]*120],{duration:160});e.preventDefault();e.stopPropagation();return}   // shift + arrows move the map; plain arrows move time
  if(e.key==='+'||e.key==='='){zoomStep(1.45);e.preventDefault()} else if(e.key==='-'||e.key==='_'){zoomStep(1/1.45);e.preventDefault()}},true);
function openLayers(v){$('layers').hidden=!v;$('bLayers').setAttribute('aria-expanded',v?'true':'false')}
on('bLayers',function(){openLayers($('layers').hidden)});
document.addEventListener('pointerdown',function(e){if(!$('layers').hidden&&!e.target.closest('#layers')&&!e.target.closest('#bLayers'))openLayers(false)});
document.addEventListener('keydown',function(e){if(e.key==='Escape'&&!$('layers').hidden){openLayers(false);$('bLayers').focus();e.stopPropagation()}},true);
function onCheck(id,fn){var e=$(id);if(e)e.addEventListener('change',function(){fn(e.checked)})}
onCheck('cUnits',setUnits); onCheck('cNames',setNames); onCheck('cFold',setFold); onCheck('cNarr',setNarr); onCheck('cForm',setFormations); onCheck('cTrail',setTrails); onCheck('cMute',setMute); onCheck('cHill',setHill);
onCheck('cPlaces',function(v){placeNames=v;mv.kick()}); onCheck('cLines',function(v){lineNames=v;mv.kick()});
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
on('binfo',function(){sel=null;info=!info;panelKey='';if(info){sheet.open();pane.show()}mv.kick()});
/* phones: the text sheet under the map. It starts as a strip; a tap on the handle opens it to about half the screen and closes it
   again, and dragging the handle sets any height in between. Tapping a unit opens it so the unit's details can be read. */
var sheet=(function(){var st=document.querySelector('.stage'),bar=$('sheetbar'),MIN=72,DEF=96,h=DEF,drag=null;
  function phone(){return getComputedStyle(bar).display!=='none'}
  function maxH(){return Math.round(st.getBoundingClientRect().height*0.72)}
  function set(v,anim){h=Math.max(MIN,Math.min(maxH(),v));st.classList.toggle('sheet-anim',!!anim);st.style.setProperty('--sheet-h',h+'px');$('grab').setAttribute('aria-expanded',h>DEF+20?'true':'false')}
  function open(){if(phone()&&h<DEF+40)set(st.getBoundingClientRect().height*0.5,true)}
  function toggle(){if(h>DEF+20)set(DEF,true);else open()}
  bar.addEventListener('pointerdown',function(e){if(!phone())return;drag={y:e.clientY,h:h,moved:false};bar.setPointerCapture(e.pointerId);e.preventDefault()});
  bar.addEventListener('pointermove',function(e){if(!drag)return;var dy=drag.y-e.clientY;if(Math.abs(dy)>4)drag.moved=true;if(drag.moved)set(drag.h+dy,false)});
  bar.addEventListener('pointerup',function(){if(!drag)return;var m=drag.moved;drag=null;if(!m)toggle()});
  bar.addEventListener('pointercancel',function(){drag=null});
  $('grab').addEventListener('keydown',function(e){if(e.key==='Enter'||e.key===' '){e.preventDefault();toggle()}});
  return {open:open,phone:phone}})();
/* the text pane beside the map folds away and comes back; choosing a unit or the i panel brings it back */
var pane=(function(){var st=document.querySelector('.stage'),b=$('bpane');
  function set(hide){st.classList.toggle('nopane',hide);b.setAttribute('aria-pressed',hide?'true':'false');var t=hide?'Show the text':'Hide the text';b.setAttribute('aria-label',t);b.title=t;remember('pane',!hide);mv.kick()}
  b.addEventListener('click',function(){set(!st.classList.contains('nopane'))});
  try{if(localStorage.getItem('wm.'+B.id+'.pane')==='0')set(true)}catch(e){}
  return {show:function(){if(st.classList.contains('nopane'))set(false)}}})();
/* phones: while playing, a tap on the map brings the hidden buttons back for a few seconds */
(function(){var tmo=0;wrap.addEventListener('touchstart',function(){if(!document.documentElement.classList.contains('wm-playing'))return;wrap.classList.add('peek');clearTimeout(tmo);tmo=setTimeout(function(){wrap.classList.remove('peek')},4000)},{passive:true})})();
// back and forward one step; [ and ] jump between key events
on('restart',restart);   // start over: the first moment, the opening map and view, no unit picked
function restart(){clk.setPlaying(false);select(null);setPreset(null);fpause=0;followK=1;glide=0;skipAcc=0;brk={};lastW=null;holdUntil=0;
  if(P.follow){follow=true;press('bFollow',true)} landing=true;panelKey='';clk.setTime(T0);setBase(startBase(),true);mv.jump(home());mv.kick()}
on('evprev',function(){clk.setPlaying(false);clk.setTime(stepBy(-1,t))}); on('evnext',function(){clk.setPlaying(false);clk.setTime(stepBy(1,t))}); on('step',function(){setStep(stepI+1)});
WM.panelClicks(panel,select);
panel.addEventListener('click',function(e){var b=e.target.closest('[data-ev]');if(!b)return;var ev=B.events.filter(function(x){return x.id===b.getAttribute('data-ev')})[0];if(ev){clk.setPlaying(false);clk.setTime(ev.t)}});
panel.addEventListener('toggle',function(e){if(e.target.classList&&e.target.classList.contains('evs'))evOpen=e.target.open},true);

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
try{if(localStorage.getItem('wm.'+B.id+'.hill')==='0'){hsOn=false;tick('cHill',false)} if(localStorage.getItem('wm.'+B.id+'.mute')==='0'){muteOn=false;tick('cMute',false);wrap.classList.add('vivid')} if(localStorage.getItem('wm.'+B.id+'.names')==='0'){names=false;tick('cNames',false)} if(localStorage.getItem('wm.'+B.id+'.narr')==='1'){narrOn=true;tick('cNarr',true);wrap.classList.add('narr-on')} var fs=localStorage.getItem('wm.'+B.id+'.form'); if(FM&&fs!=null){fmOn=fs==='1';tick('cForm',fmOn)} var ts=localStorage.getItem('wm.'+B.id+'.trail'); if(TRL&&ts!=null){trlOn=ts==='1';tick('cTrail',trlOn)}}catch(_){ }
setStep(stepNear(P.rate||(byDay?1:5)));
if(P.views) preset=P.views[0].preset;
base=startBase();
mv.start(function(){buildBase();paintTime(T0);(P.views||[]).forEach(function(v){press('v-'+v.preset,preset===v.preset)});setBase(base,true);clk.setTime(T0);readLink();WM.hint(mv)});
var api={battle:B,setTime:clk.setTime,select:select,setFollow:setFollow,setBase:setBase,setNames:setNames,setUnits:setUnits,setFold:setFold,setPreset:setPreset,mv:mv,
  focus:function(){var f=focusPoint();return f?WORLDS[worldOf(base)].toLL(f):null},setNarrative:setNarr,setSymbols:setSymbols,setSeenFrom:setSeenFrom,setOpacity:setOpacity,setStep:setStep,link:linkHash,
  begin:function(){landing=false;panelKey='';mv.kick()},setFormations:setFormations,setMute:setMute,setHill:setHill,
  scene:function(){return scene().map(function(o){return {id:o.tr.id,kind:o.s.kind,row:o.s.k.id,drawn:o.drawn}})}};
Object.defineProperty(api,'view',{get:function(){return {s:mv.scale()}}}); Object.defineProperty(api,'base',{get:function(){return base.id}}); Object.defineProperty(api,'landing',{get:function(){return landing}}); Object.defineProperty(api,'modern',{get:function(){return {on:!!modOn,off:modOff,hill:!!hsVis}}});
global.__wm=api; return api;
};
})(window);
