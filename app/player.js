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
var BLEND=RU.blend||4,NEAR=RU.near||15,LEAD_IN=RU.lead||0.35,LINGER=RU.linger||2;
var wrap=$('mapwrap'),ov=$('ov'),panel=$('panel');
var kinds={},found={},k0; for(k0 in KIND)kinds[k0]=[KIND[k0][0],(P.texts&&P.texts[k0])||KIND[k0][1]]; for(k0 in FOUND)found[k0]=(P.found&&P.found[k0])||FOUND[k0];

/* ---------- bases: the maps the reader can put under the units ---------- */
/* a base is the current map ({current:true}), one period map ({map:id}) or the period map for the date on the timeline ({series:true}).
   A period map lies on plain paper (backdrop "paper") or over the current map (backdrop "current"). A map that is not to scale has a frame of its own. */
var bases=(P.bases&&P.bases.length)?P.bases:[{id:'now',label:'Current map',short:'Today',current:true}];
var series=B.mapList.filter(function(m){return m.t0!=null});
bases.forEach(function(b){b.m=b.map?B.maps[b.map]:null;b.own=!!(b.m&&b.m.own)});
var SKK=1e-5; function ownLL(p){return [p[0]*SKK,-p[1]*SKK]}   // a not-to-scale map: its pixels laid out as a small patch of pretend ground
var bm=P.bounds&&B.maps[P.bounds],EXT=bm?bm.images[0].box:B.ext;
var WORLDS={ground:{toLL:B.toLL,ext:EXT,mPerUnit:1,maxScale:Z.max||2,minFactor:Z.min_factor||0.9}};
bases.forEach(function(b){if(b.own)WORLDS['own:'+b.map]={toLL:ownLL,ext:[0,0,b.m.size[0],b.m.size[1]],mPerUnit:SKK*EARTH/360,maxScale:3,minFactor:0.9}});
function worldOf(b){return b.own?'own:'+b.map:'ground'}

/* ---------- state ---------- */
var base=bases[0],t=T0,sel=null,follow=!!P.follow,names=true,unitsOn=true,foldOn=true,faded=false,sNow=0.1,preset=null,goal=null,S,mv,clk;
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
  if(key==='g'&&b.via&&b.via.length>1){ if(f>0.92&&b.g.length>1){return lerpG([alongP(b.via,0.92)],b.g,(f-0.92)/0.08)} return [alongP(b.via,Math.min(f/0.92,1))]; }
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
      if(g&&gn){ var ca=cen(g),cb=cen(gn);
        if(!nx.via&&Math.hypot(ca[0]-cb[0],ca[1]-cb[1])<(key==='g'?NEAR:8)) return {k:nx,g:gn,kind:placed(nx)};   // hardly any distance: no march is drawn
        return {k:nx,from:k,g:move(k,nx,(tt-end)/(nx.t0-end),key),kind:'moving'}; }
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
    if(tt>=s&&tt<=e) return {k:k,g:g,kind:!g?noPlace(k,key):placed(k)};
    if(nx&&tt>e&&tt<nx.t0-LEAD_IN){
      var ms=Math.max(e,nx.t0-1),me=nx.t0-LEAD_IN;            // the move takes the last day before the next record
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
function actionBox(){var key=gkey(),F=P.follow||{},ex=F.exclude||[],b=[1e9,1e9,-1e9,-1e9],any=false;
  B.tracks.forEach(function(tr){if(tr.parent||tr.loose||ex.indexOf(tr.id)>=0)return;var s=stateAt(tr,t,key);if(!s||!s.g||s.hid)return;any=true;
    s.g.forEach(function(p){b[0]=Math.min(b[0],p[0]);b[1]=Math.min(b[1],p[1]);b[2]=Math.max(b[2],p[0]);b[3]=Math.max(b[3],p[1])})});
  if(!any) return base.own?[0,0,base.m.size[0]*0.75,base.m.size[1]]:((F.empty&&B.presets[F.empty])||EXT);
  var mn=base.own?[520,400]:(F.min||[1400,900]),mg=base.own?70:(F.margin||140);
  var mx=Math.max(mg,(mn[0]-(b[2]-b[0]))/2),my=Math.max(mg,(mn[1]-(b[3]-b[1]))/2);
  return [b[0]-mx,b[1]-my,b[2]+mx,b[3]+my]}
function target(){var n=mv.size().w<520?36:56;return mv.cameraFor(actionBox(),{t:n+34,b:n+26,l:n,r:n},base.own?1.3:(Z.follow_max||Z.max||2))}
function cameraOf(p){return mv.cameraFor(B.presets[p],{t:48,b:22,l:14,r:14})}
function home(){return preset?cameraOf(preset):(follow?target():mv.cameraFor(base.own?WORLDS[worldOf(base)].ext:EXT,{t:48,b:22,l:14,r:14}))}
function press(id,v){var e=$(id);if(e)e.setAttribute('aria-pressed',v?'true':'false')}
function setFollow(v){follow=v;press('bFollow',v);if(v)mv.kick()}
function setPreset(p,jump){preset=p;(P.views||[]).forEach(function(v){press('v-'+v.preset,p===v.preset)});
  if(!p){goal=null;return} goal=cameraOf(p); if(jump){mv.jump(goal);goal=null} mv.kick()}
function remember(k,v){try{localStorage.setItem('wm.'+B.id+'.'+k,v?'1':'0')}catch(_){ }}
function setNames(v){names=v;press('bNames',v);remember('names',v);mv.kick()}
function setUnits(v){unitsOn=v;press('bUnits',v);mv.kick()}
function setFold(v){foldOn=v;press('bFold',v);mv.kick()}

/* ---------- drawing ---------- */
function rank(tr){ // which names are kept when the map is crowded: 1 first
  if(tr.id===sel) return 0;
  if(tr.loose||tr.ech==='detachment'||tr.ech==='section') return 4;
  if(tr.parent||tr.branch==='art') return 3;
  if(compact) return (tr.ech==='corps'||tr.ech==='army')?1:tr.ech==='division'?2:3;
  return (tr.ech==='regiment'||tr.ech==='brigade')?1:2}
function layout(sc){
  var L=[],Zs=mv.size(),rear=(P.rear&&!base.own)?S(B.fromLL(P.rear.at)):null,ag={};
  sc.forEach(function(o){ if(!o.drawn) return; var tr=o.tr;
    for(var gi=0;gi<(P.groups||[]).length;gi++){var G=P.groups[gi]; // zoomed right out, a group of units is one symbol
      if(!base.own&&sNow<G.below&&tr.side===G.side&&(G.except||[]).indexOf(tr.id)<0){(ag[gi]=ag[gi]||[]).push(S(cen(o.s.g)));return}}
    var pts=o.s.g.map(S),len=plen(pts),m=WM.along(pts,0.5),c=m.p,nx=tr.nudge?tr.nudge[0]:0,ny=tr.nudge?tr.nudge[1]:0,x=c[0]+nx,y=c[1]+ny;
    if(len>7){var px=-m.v[1],py=m.v[0]; // the symbol sits beside its line: behind it, where the battle says which way the rear lies; otherwise to the east
      if(rear){var dot=px*(rear[0]-c[0])+py*(rear[1]-c[1]);if((dot<0)===(tr.side===P.rear.side)){px=-px;py=-py}x+=px*21;y+=py*17}
      else{if(px<0){px=-px;py=-py}x+=px*20;y+=py*13}}
    var conf=(P.question_mark==='location'&&o.s.k.cc)||o.s.k.oc,low=(conf==='low'&&o.s.kind!=='moving'),txt=tr.label+((low&&!compact)?' ?':'');
    L.push({o:o,pts:pts,len:len,c:c,x:x,y:y,low:low,txt:txt,w:txt.length*(compact?6.7:7.1)+6,pr:rank(tr),nudged:!!(nx||ny),line:len>7})});
  Object.keys(ag).forEach(function(gi){var G=P.groups[gi],gc=cen(ag[gi]);
    L.push({o:{tr:{id:'',label:G.label,side:G.side,nation:'',ech:G.echelon||'brigade',branch:G.branch||'inf'},s:{kind:'stated',k:{oc:'high'}}},pts:[gc],len:0,c:gc,x:gc[0],y:gc[1],low:false,txt:G.label,w:G.label.length*7.1+6,pr:1,nudged:false,line:false})});
  L.sort(function(a,b){return a.pr-b.pr});
  // spread symbols that land on the same spot
  for(var i=0;i<L.length;i++)for(var pass=0;pass<4;pass++){var moved=false;for(var j=0;j<i;j++){var a=L[i],b=L[j];if(Math.abs(a.x-b.x)<27&&Math.abs(a.y-b.y)<21){var sx=a.x>=b.x?1:-1,sy=a.y>=b.y?1:-1;if(Math.abs(a.x-b.x)>Math.abs(a.y-b.y))a.x=b.x+sx*28;else a.y=b.y+sy*22;a.nudged=true;moved=true}}if(!moved)break}
  var R=[]; function hit(r){for(var i=0;i<R.length;i++){var q=R[i];if(r[0]<q[2]&&r[2]>q[0]&&r[1]<q[3]&&r[3]>q[1])return true}return false}
  L.forEach(function(u){R.push([u.x-14,u.y-19,u.x+14,u.y+10]);
    if(!compact) for(var i=1;i<u.pts.length&&u.line;i++){var a=u.pts[i-1],b=u.pts[i],d=Math.hypot(b[0]-a[0],b[1]-a[1]),n=Math.max(1,Math.round(d/11));
      for(var j=0;j<=n;j++){var qx=a[0]+(b[0]-a[0])*j/n,qy=a[1]+(b[1]-a[1])*j/n;R.push([qx-4,qy-4,qx+4,qy+4])}}});
  // names, most important units first; a crowded name is dropped (the unit stays tappable)
  var force=!compact&&sNow>=(Z.force_names_from||0);
  L.forEach(function(u){
    u.lab=null; if(!names&&!(sel&&u.o.tr.id===sel)) return;
    var x=u.x,y=u.y,w=u.w,C=[[x+16,y-8,x+16+w,y+8,'start',x+17,y+4.5],[x-16-w,y-8,x-16,y+8,'end',x-17,y+4.5],[x-w/2,y+11,x+w/2,y+26,'middle',x,y+23],[x-w/2,y-35,x+w/2,y-20,'middle',x,y-23]];
    for(var i=0;i<C.length;i++){ if(C[i][0]>=3&&C[i][2]<=Zs.w-3&&!hit(C[i])){u.lab=C[i];break} }
    if(!u.lab&&(u.pr===0||(force&&u.pr===1))) u.lab=C[0];
    if(u.lab) R.push(u.lab) });
  L.hit=hit; L.keep=function(r){R.push(r)};
  return L;
}
function f1(v){return v.toFixed(1)}
function unitSvg(u,part){
  var o=u.o,tr=o.tr,s=o.s,pts=u.pts,lk=look(tr),col=lk.col,k=s.kind;
  var soft=(k==='moving'||k==='after'||k==='unplaced'),low=u.low,op=(k==='after'||k==='unplaced')?0.5:1,isSel=!!tr.id&&sel===tr.id,h='',x=u.x,y=u.y,c=u.c;
  if(part==='line'){ if(!u.line) return '';
    var d=pts.map(function(p,i){return (i?'L':'M')+f1(p[0])+' '+f1(p[1])}).join('');
    var w=compact?((tr.ech==='corps'||tr.ech==='army')?5:tr.ech==='division'?4:3):((!tr.parent&&(tr.ech==='brigade'||tr.ech==='division'))?6:4.5);
    var dash=tr.loose?' stroke-dasharray="2 5"':((soft||(compact&&k==='inferred'))?' stroke-dasharray="'+(compact?'8 6':'7 5')+'"':'');
    h+='<g opacity="'+op+'" stroke-linecap="round" stroke-linejoin="round" fill="none">'; mv.hits.push({id:tr.id,pts:pts,tol:Math.max(7,w/2+4)});
    if(isSel) h+='<path d="'+d+'" stroke="var(--m-sel)" stroke-width="'+(w+9)+'" opacity=".8"/>';
    h+='<path d="'+d+'" stroke="var(--u-halo)" stroke-width="'+(w+(compact?3:4))+'"'+(compact?'':' stroke-linecap="butt"')+'/><path d="'+d+'" stroke="'+col+'" stroke-width="'+w+'"'+((compact||tr.loose)?'':' stroke-linecap="butt"')+dash+'/>';
    return h+'</g>'; }
  var W=compact?12:13,H=compact?8:9;
  h+='<g opacity="'+op+'">'; mv.hits.push({id:tr.id,r:[x-W-4,y-H-11,x+W+4,y+H+4]});
  if((compact&&u.line)||u.nudged) h+='<line x1="'+f1(c[0])+'" y1="'+f1(c[1])+'" x2="'+f1(x)+'" y2="'+f1(y)+'" stroke="'+(compact?col:'var(--u-ink)')+'" stroke-width="'+(compact?1.2:1)+'"/>';
  if(u.nudged&&!(compact&&u.line)) h+='<circle cx="'+f1(c[0])+'" cy="'+f1(c[1])+'" r="2.5" fill="'+col+'"/>';
  h+='<g transform="translate('+f1(x)+' '+f1(y)+')">';
  if(isSel) h+='<rect x="'+(-W-5)+'" y="'+(-H-5)+'" width="'+(2*W+10)+'" height="'+(2*H+10)+'" rx="4" fill="none" stroke="var(--m-sel)" stroke-width="4"/>';
  h+='<rect x="'+(-W)+'" y="'+(-H)+'" width="'+2*W+'" height="'+2*H+'" fill="'+lk.fill+'" stroke="'+col+'" stroke-width="1.8"'+((soft||low)?' stroke-dasharray="3 2.5"':'')+'/>';
  if(tr.ech==='headquarters') h+='<path d="M'+(-W)+' '+(-H)+'V'+(H+7)+'" stroke="'+col+'" stroke-width="1.8"/><text class="ech in" text-anchor="middle" y="4" style="stroke:none">HQ</text>';
  else if(tr.branch==='inf') h+='<path d="M'+(-W)+' '+(-H)+'L'+W+' '+H+'M'+(-W)+' '+H+'L'+W+' '+(-H)+'" stroke="'+col+'" stroke-width="1.4"/>';
  else if(tr.branch==='cav') h+='<path d="M'+(-W)+' '+H+'L'+W+' '+(-H)+'" stroke="'+col+'" stroke-width="1.4"/>';
  else h+='<circle r="3.4" fill="'+col+'"/>';
  h+='<text class="ech" text-anchor="middle" y="'+(-H-3)+'">'+(ECH[tr.ech]||'')+'</text></g>';
  if(u.lab){h+='<text class="ulab" text-anchor="'+u.lab[4]+'" x="'+f1(u.lab[5])+'" y="'+f1(u.lab[6])+'">'+esc(u.txt)+'</text>';mv.hits.push({id:tr.id,r:[u.lab[0],u.lab[1],u.lab[0]+u.w,u.lab[1]+16]})}
  return h+'</g>';
}
/* Names on the map. Names from today's map are drawn where today's map shows: not on a period map, which carries its own.
   A name marked for period maps (show "period" or "both") is drawn there too. */
function mapNames(L,cover){
  var z=mv.size(),lvl=sNow>=(Z.labels||0)?1:0,h='',cur=!!(base.current||base.backdrop==='current');
  B.labels.forEach(function(l){
    var show=l.show||'current'; if(cur?show==='period':show==='current') return;
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
function paintCredit(H){var c;
  if(base.current) c=WM.OSM_CREDIT;
  else{var m=H||base.m; c=(H?esc(m.short)+', '+esc(m.label)+(stamp(t)>m.t1?' (the last one)':'')+' &middot; ':'')+esc(m.credit)+(base.backdrop==='current'?' &middot; '+WM.OSM_CREDIT:'')}
  if(c!==lastCredit){lastCredit=c;$('credit').innerHTML=c}}
function draw(){
  sNow=mv.scale(); mv.hits.length=0;
  var H=base.series?seriesAt():null; if(series.length) showSeries(H); paintCredit(H);
  var cover=base.backdrop==='current'?(H||base.m).images[0].box:null;
  var sc=scene(),L=layout(unitsOn?sc:[]),h=mapNames(L,cover);
  L.sort(function(a,b){return (a.o.tr.id===sel)-(b.o.tr.id===sel)});   // the selected unit last, so it sits on top
  L.forEach(function(u){h+=unitSvg(u,'line')}); L.forEach(function(u){h+=unitSvg(u,'sym')}); ov.innerHTML=h;
  if(base.own) $('scale').innerHTML='<span class="nts">'+esc(base.m.raw.scale_note||'Not to scale')+'</span>';
  else WM.scaleBar($('scale'),mv.mPerPx(),P.scale_bar||(byDay?'km':'yards'));
  var off=$('offnote'),on=base.own&&base.m.raw.off_note; if(on&&t<B.time(on.until)){off.hidden=false;off.textContent=on.text} else off.hidden=true;
  renderPanel(sc);
}

/* ---------- the base maps ---------- */
var CUR=[],PICS={};
function buildBase(){
  var W=ROADS[style],f=[],lat=raw.view.origin[1],minor=!!Z.minor_roads_from,wide=(raw.base&&raw.base.widths)||{},mask=bases.filter(function(b){return b.clip})[0];
  B.base.areas.forEach(function(a){f.push(WM.feat('area',a.ll,{k:a.kind==='wood'?'wood':'lake'}))});
  B.base.lines.forEach(function(l){
    if(l.kind==='water'){f.push(WM.feat('line',l.ll,wide[l.name]?{k:'river',gw:wide[l.name]}:{k:'water',w:compact?(l.cls==='river'?3.6:2.6):(l.cls==='river'?3.2:1.6)}));return}
    if(l.kind==='former-water'){f.push(WM.feat('line',l.ll,{k:'former'}));return}
    if(l.kind==='rail'){f.push(WM.feat('line',l.ll,{k:'rail'}));return}
    var w=W[l.cls]||W[W._];f.push(WM.feat('line',l.ll,{k:'road',major:(!compact&&(l.cls==='m'||l.cls==='p'))?1:0,e:w[0],w:w[1],minor:(minor&&(l.cls==='r'||l.cls==='v'))?1:0}))});
  if(mask){ // everything outside the period map is covered, so the current map ends where the period map does
    var c=B.maps[mask.clip].images[0].ll,far=[[-9,-9],[10,-9],[10,10],[-9,10],[-9,-9]].map(function(q){return B.toLL([EXT[0]+(EXT[2]-EXT[0])*q[0],EXT[1]+(EXT[3]-EXT[1])*q[1]])});
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
  // the period maps: each base's pictures; the map of the day is one picture, re-pointed when the date calls for another
  bases.forEach(function(b){PICS[b.id]=[];
    if(b.series){ if(series.length){mv.image('pic-series',WM.asset(series[0].images[0].file),series[0].images[0].ll);mv.show('pic-series',false)} return }
    if(!b.m) return;
    b.m.images.forEach(function(im,i){var id='pic-'+b.id+'-'+i;PICS[b.id].push({id:id,detail:im.detail});
      mv.image(id,WM.asset(im.file),b.own?[0,0,b.m.size[0],b.m.size[1]]:im.ll,b.own?WORLDS[worldOf(b)]:undefined);mv.show(id,false)})});
}
function paintFade(){(PICS[base.id]||[]).forEach(function(p){mv.opacity(p.id,!(faded&&base.fade)?1:p.detail?0:0.5)})}   // faded, only the whole-map picture shows, so the two do not add up
function setBase(b,first){
  if(typeof b==='string') b=bases.filter(function(x){return x.id===b})[0]; if(!b) return;
  var moved=first||worldOf(b)!==worldOf(base); base=b;
  bases.forEach(function(x){press('b-'+x.id,x===b);(PICS[x.id]||[]).forEach(function(p){mv.show(p.id,x===b)})});
  if(moved) mv.setWorld(worldOf(b));
  var cur=!!(b.current||b.backdrop==='current'); CUR.forEach(function(id){mv.show(id,cur)}); mv.show('b-mask',cur&&!!b.clip);
  if(!b.series&&series.length){mv.show('pic-series',false);seriesShown=null}
  if(b.series) series.forEach(function(m){if(!m.pre){m.pre=new Image();m.pre.src=WM.asset(m.images[0].file)}});
  wrap.classList.toggle('paper',!b.current); mv.bg((b.own||(b.m&&b.backdrop!=='current'))?'--m-paper':'--land');
  var fd=$('bFade'); if(fd) fd.hidden=!b.fade; paintFade();
  if(moved) mv.jump(home());
  panelKey=''; mv.retheme(); mv.kick()}

/* ---------- panel ---------- */
function curEvent(){return B.eventAt(stamp(t))}
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
function status(o){return o.s.kind==='moving'?'Moving (interpolated)':o.s.kind==='after'?'Last recorded position':o.s.k.act}
function item(o,text){return '<li><button data-pick="'+o.tr.id+'"><span class="sd" style="background:'+look(o.tr).ui+'"></span><span class="nm">'+esc(o.tr.label)+'</span><span class="ac">'+esc(text)+'</span></button></li>'}
var panelKey='';
function renderPanel(sc){
  var me=sel?sc.filter(function(o){return o.tr.id===sel})[0]:null,ev=curEvent();
  var key=base.id+'|'+(sel?sel+'|'+(me?me.s.k.id+me.s.kind+(byDay?stamp(t):''):'x'):'now|'+(ev?ev.id:0)+'|'+sc.map(function(o){return o.tr.id+(o.drawn?1:0)+o.s.kind+o.s.k.id}).join(','));
  if(key===panelKey) return; panelKey=key; var h='';
  if(sel){
    var tr=B.track(sel),lk=look(tr),p=parentAt(tr,t),pu=p&&p[2]&&B.units[p[2]];
    h+='<button class="back" id="back">&larr; All units</button><div class="who"><div><div class="side" style="color:'+lk.ui+'">'+esc(lk.name)+'</div><h2>'+esc(tr.name)+'</h2>';
    h+='<div class="meta">'+[p?p[3]:tr.cmd,pu?'under '+pu.name:'',p?p[4]:tr.str].filter(Boolean).map(esc).join(' &middot; ')+'</div></div></div>';
    if(!me){h+='<div class="state unplaced"><b>Not in the data at '+esc(nowText())+'</b>Move the time to see this unit.</div>'}
    else{var kd=me.s.kind,K=kinds[kd];
      h+='<div class="state '+((kd==='offthis'||kd==='lost'||kd==='offmap')?'unplaced':kd)+'"><b>'+K[0]+'</b>'+esc(kd==='offmap'?tr.offmap:K[1])+'</div>';
      if(kd==='moving'){h+=rowHtml(me.s.k,'Heading to');if(me.s.from)h+=rowHtml(me.s.from,'Coming from')}
      else h+=rowHtml(me.s.k,(kd==='after'||kd==='lost')?'Last record':'Current record');}
    if(tr.notes) h+='<p class="meta" style="margin-top:12px">'+esc(tr.notes)+'</p>';
  } else {
    h+='<div class="eyebrow">'+esc(ev?'Now: '+ev.name:B.opening.label)+'</div><p class="phase">'+esc(ev?ev.text:B.opening.text)+'</p>';
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
function select(id){sel=id||null;panelKey='';mv.kick()}

/* ---------- controls ---------- */
(function(){var h='',seg=function(label,items){return '<div class="seg" role="group" aria-label="'+label+'">'+items.join('')+'</div>'},
    btn=function(id,x){return '<button id="'+id+'" aria-pressed="false"'+(x.title?' title="'+esc(x.title)+'"':'')+'><span class="lg">'+esc(x.label)+'</span><span class="sm">'+esc(x.short||x.label)+'</span></button>'},
    chipb=function(id,label,title,on){return '<button class="chipbtn" id="'+id+'" aria-pressed="'+(on?'true':'false')+'" title="'+esc(title)+'"><span class="dot"></span><span>'+label+'</span></button>'};
  if(bases.length>1) h+=seg('Base map',bases.map(function(b){return btn('b-'+b.id,b)}));
  if(P.views) h+=seg('Map view',P.views.map(function(v){return btn('v-'+v.preset,v)}));
  if(P.follow) h+=chipb('bFollow','Follow<span class="long"> the action</span>','Keep the units in view as time moves (F)',true);
  if(P.fold&&P.fold.label) h+=chipb('bFold',esc(P.fold.label),'Show the smaller units when zoomed in',true);
  if(bases.some(function(b){return b.fade})) h+=chipb('bFade','Fade map','Dim the period map so the units stand out',false);
  h+=chipb('bNames','Names','Show or hide the names beside the unit symbols (N)',true)+chipb('bUnits','Units','Show or hide the units, to read the map underneath (U)',true);
  $('ctl').innerHTML=h;
  wrap.classList.toggle('compact',compact); $('when').classList.toggle('date',byDay); $('tl').classList.toggle('days',byDay);
  if(byDay){$('hint').innerHTML=$('hint').innerHTML.replace('to move time','to move through the days')}
})();

/* ---------- map and time ---------- */
try{ mv=WM.mapView({container:'map',wrap:wrap,world:worldOf(base),worlds:WORLDS,
  onDraw:draw,onPick:select,
  onUserMove:function(){if(follow)setFollow(false);if(preset||goal)setPreset(null)},
  onResize:function(){if(preset){mv.jump(cameraOf(preset));goal=null}else if(follow)mv.jump(target())},
  onStep:function(ts){var more=clk.step(ts);if(goal){if(mv.chase(goal,0.2))more=true;else goal=null}else if(follow&&mv.chase(target(),0.16))more=true;return more}});
}catch(err){WM.noMap(wrap,err);return null}
S=mv.S;
/* the stretch before the part the data covers best (a night march before a fight) can be squeezed into a share of the bar and played faster */
var LD=(P.lead&&B.focus&&B.focus[0]>T0)?P.lead:null,TM=LD?B.focus[0]:T0,UM=LD?LD.share:0,RNG=4000;
function u2t(u){return (LD&&u<=UM)?T0+(TM-T0)*u/UM:TM+(T1-TM)*(u-UM)/(1-UM)}
function t2u(v){return (LD&&v<=TM)?UM*(v-T0)/(TM-T0):UM+(1-UM)*(v-TM)/(T1-TM)}
function paintTime(v){t=v;
  if(byDay){var n=stamp(t),d=B.dateOf(n),night=Math.abs(t-Math.round(t))<0.02;
    $('clock').textContent=d.day+' '+d.mon+' '+d.year;$('clockdate').textContent=d.wd+' · '+(night?'at nightfall':'during the day');WM.paintDayNumber(B.cal.numbered?n+1:0)}
  else{var c=WM.calOf(B.cal,t);$('clock').textContent=c.clock;$('clockdate').textContent=c.date;WM.paintDayNumber(c.n)}
  var tn=P.time_note,ne=$('clocknote'); if(tn){ne.textContent=tn.text;ne.hidden=t<B.time(tn.from)} else ne.hidden=true;
  $('done').style.width=(t2u(t)*100)+'%'; var ev=curEvent();
  Array.prototype.forEach.call(document.querySelectorAll('.tl .ev'),function(e){e.classList.toggle('on',!!ev&&e.dataset.id===ev.id)})}
var rng=$('time'); rng.min=0; rng.max=RNG; rng.step=1; rng.value=0; rng.setAttribute('aria-label',byDay?'Day of the battle':'Time of day');
clk=WM.clock({T0:T0,T1:T1,mv:mv,toRange:function(v){return Math.round(t2u(v)*RNG)},fromRange:function(v){return u2t(v/RNG)},
  rate:function(v){return (LD&&v<TM)?LD.rate:(P.rate||(byDay?0.85:3))},onTime:paintTime,
  snap:byDay?function(v){return Math.round(v)}:null,   // the sources give one position a day, so time settles on nightfall
  arrow:function(dir,v){if(byDay)return dir>0?Math.floor(v+1e-6)+1:Math.ceil(v-1e-6)-1;return v+dir*((LD&&(dir>0?v<TM:v<=TM))?(LD.step||5):1)},
  wheel:function(dd,v){return u2t(Math.max(0,Math.min(1,t2u(v)+dd*0.0002)))},
  onKey:function(e){var k=e.key.toLowerCase();
    if(e.key==='Escape')select(null);else if(k==='n')setNames(!names);else if(k==='u')setUnits(!unitsOn);else if(k==='f'&&P.follow)setFollow(!follow);
    else if(k==='m'&&bases.length>1)setBase(bases[(bases.indexOf(base)+1)%bases.length])}});

/* timeline furniture: ticks, the part the data covers best, and the events */
(function(){var tl=$('tl'),pc=function(m){return (t2u(m)*100)+'%'},h='',m,fmt=function(v){return WM.fmtClock(v).replace(' a.m.','')};
  var win=$('win'); if(B.focus){win.style.left=pc(B.focus[0]);win.style.width=((t2u(B.focus[1])-t2u(B.focus[0]))*100)+'%';if(B.focus[1]>=T1)win.style.borderRadius='0 5px 5px 0'} else win.hidden=true;
  if(byDay){var nth=0;for(m=T0;m<=T1;m++){var d=B.dateOf(m),maj=d.day%5===0;h+='<span class="tick'+(maj?' maj':'')+'" style="left:'+pc(m)+'"></span>';
      if(maj){h+='<span class="tk'+(nth%2?' minor':'')+'" style="left:'+pc(m)+'">'+d.day+' '+d.mon.slice(0,3)+'</span>';nth++}}}
  else{for(m=Math.ceil(T0/60)*60;m<TM;m+=60){h+='<span class="tick" style="left:'+pc(m)+'"></span>';if(m%120===0)h+='<span class="tk minor" style="left:'+pc(m)+'">'+fmt(m)+'</span>'}
    for(m=Math.ceil(TM/30)*30;m<=T1;m+=15){h+='<span class="tick" style="left:'+pc(m)+'"></span>';if(m%30===0)h+='<span class="tk'+(m%60?' minor':'')+'" style="left:'+pc(m)+'">'+fmt(m)+'</span>'}}
  B.events.forEach(function(e){h+='<button class="ev'+(e.quiet?' mute':'')+'" data-id="'+esc(e.id)+'" data-t="'+e.t+'" style="left:'+pc(e.t)+'" title="'+esc(e.name)+'" aria-label="'+esc(e.name)+'">'+esc(e.name)+'</button>'});
  tl.insertAdjacentHTML('afterbegin',h);
  tl.addEventListener('click',function(ev){var b=ev.target.closest('.ev');if(b){clk.setPlaying(false);clk.setTime(+b.dataset.t)}});
})();
function on(id,fn){var e=$(id);if(e)e.addEventListener('click',fn)}
bases.forEach(function(b){on('b-'+b.id,function(){setBase(b)})});
(P.views||[]).forEach(function(v){on('v-'+v.preset,function(){setPreset(v.preset)})});
on('bFollow',function(){setFollow(!follow)}); on('bFold',function(){setFold(!foldOn)}); on('bNames',function(){setNames(!names)}); on('bUnits',function(){setUnits(!unitsOn)});
on('bFade',function(){faded=!faded;press('bFade',faded);paintFade()});
on('zin',function(){setFollow(false);setPreset(null);mv.zoomBy(1.45)}); on('zout',function(){setFollow(false);setPreset(null);mv.zoomBy(1/1.45)});
WM.panelClicks(panel,select);

/* ---------- start ---------- */
try{if(localStorage.getItem('wm.'+B.id+'.names')==='0'){names=false;press('bNames',false)}}catch(_){ }
if(P.views) preset=P.views[0].preset;
mv.start(function(){buildBase();paintTime(T0);(P.views||[]).forEach(function(v){press('v-'+v.preset,preset===v.preset)});setBase(base,true);clk.setTime(T0);WM.hint(mv)});
var api={battle:B,setTime:clk.setTime,select:select,setFollow:setFollow,setBase:setBase,setNames:setNames,setUnits:setUnits,setFold:setFold,setPreset:setPreset,mv:mv,
  scene:function(){return scene().map(function(o){return {id:o.tr.id,kind:o.s.kind,row:o.s.k.id,drawn:o.drawn}})}};
Object.defineProperty(api,'view',{get:function(){return {s:mv.scale()}}}); Object.defineProperty(api,'base',{get:function(){return base.id}});
global.__wm=api; return api;
};
})(window);
