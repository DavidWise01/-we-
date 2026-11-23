/* WAG-288 · 5 variable × 5 variable × 5 constant lattice · .dlw
   125 independent eight-channel silos; exactly one nested {[(Ss#Ss)]}.
   Simultaneous conservative diffusion; no mutable memory sharing.
   The third axis indexes fixed locations, not fixed signal values.
*/
const WAG288=Object.freeze({side:5,count:125,channels:8,
 center:62,centerGlyph:'{[(Ss#Ss)]}',regularGlyph:'{Ss@sS}',
 geometry:'{{5 variable x 5 variable}}^{{5 constant}}',
 depthCoordinates:Object.freeze([-2,-1,0,1,2]),routesPerEdge:2});
function wag288Index(x,y,z){return x+5*y+25*z}
function wag288Coords(i){return [i%5,Math.floor(i/5)%5,Math.floor(i/25)]}
const WAG288_EDGES=Object.freeze((()=>{
 const out=[];for(let z=0;z<5;z++)for(let y=0;y<5;y++)for(let x=0;x<5;x++){
 const a=wag288Index(x,y,z);
 if(x<4)out.push([a,wag288Index(x+1,y,z)]);
 if(y<4)out.push([a,wag288Index(x,y+1,z)]);
 if(z<4)out.push([a,wag288Index(x,y,z+1)]);
 }return out.map(e=>Object.freeze(e));
})());
function wag288Initial(){
 const nodes=Array.from({length:125},(_,i)=>Array.from({length:8},(_,j)=>
  i===62?(j===0?1:.125):((i*13+j*7)%31)/124));
 return {nodes,tick:0,maxResidual:0,transferred:0};
}
function wag288Mass(s){let v=0;for(const n of s.nodes)for(const x of n)v+=x;return v}
function wag288Tick(s,weight=.125){
 if(!Number.isFinite(weight)||weight<0||weight>.25)throw Error('invalid coupling');
 const before=wag288Mass(s);
 const nodes=s.nodes.map(n=>n.slice());
 let transferred=0;
 // Maximum degree six; normalize by six for positivity at weight <=.25.
 for(const [a,b] of WAG288_EDGES)for(let j=0;j<8;j++)for(let d=0;d<2;d++){
  const k=d===0?(j^7):((j+3)&7);
  const flux=(weight/12)*(s.nodes[a][j]-s.nodes[b][k]);
  nodes[a][j]-=flux;nodes[b][k]+=flux;transferred+=Math.abs(flux);
 }
 const next={nodes,tick:s.tick+1,maxResidual:s.maxResidual,transferred:s.transferred+transferred};
 const residual=Math.abs(wag288Mass(next)-before);
 next.maxResidual=Math.max(residual,s.maxResidual);
 if(residual>1e-8||nodes.some(n=>n.length!==8||n.some(v=>!Number.isFinite(v)||v< -1e-10||v>1+1e-10)))throw Error('conservation or domain failure');
 return next;
}
function wag288Audit(){
 const tests=[];
 for(const w of [0,.0625,.125,.2,.25]){
  const initial=wag288Initial(),snap=JSON.stringify(initial.nodes),mass=wag288Mass(initial);
  let s=initial;for(let t=0;t<100;t++)s=wag288Tick(s,w);
  tests.push({weight:w,pass:Math.abs(wag288Mass(s)-mass)<1e-8&&s.maxResidual<1e-8&&
    (w!==0||snap===JSON.stringify(s.nodes))&&
    (w===0?s.transferred===0:s.transferred>0)&&
    new Set(s.nodes).size===125,
    maxResidual:s.maxResidual,totalTransfer:s.transferred});
 }
 return {bound:'WAG-288',nodes:125,edges:WAG288_EDGES.length,routes:WAG288_EDGES.length*2,
  nestedCenters:1,tests,pass:tests.every(t=>t.pass),frozenPreviousFiles:true,physicalActions:0};
}
if(typeof module!=='undefined')module.exports={WAG288,WAG288_EDGES,wag288Index,wag288Coords,wag288Initial,wag288Mass,wag288Tick,wag288Audit};
