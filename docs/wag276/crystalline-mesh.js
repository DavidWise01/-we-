/* WAG-276 crystalline topology preview · {\a{b/}} · .dlw
 Outer "\" is ingress/inward; inner "/" is return/outward.
 Geometry is versioned; no policy promoted or previous receipt changed.
*/
const WAG276_CRYSTAL=Object.freeze({
 primitive:'{\\a{b/}}',
 orientation:{a:'\\',b:'/'},
 names:{a:'outer-survival-resource',b:'inner-repair-recovery'},
 vertices:8,edgesPerCube:12,railPairs:8,passes:3,railWeight:.125
});
function wag276CrystalVertices(scale=1){
 return Array.from({length:8},(_,i)=>({
  id:i,x:(i&1)?scale:-scale,
  y:(i&2)?scale:-scale,z:(i&4)?scale:-scale
 }));
}
function wag276CrystalEdges(){
 const edges=[];
 for(let i=0;i<8;i++)for(const bit of [1,2,4]){
  const j=i^bit;if(i<j)edges.push({from:i,to:j,axis:bit});
 }
 return edges;
}
function wag276CrystalRails(){
 const rails=[];
 for(let i=0;i<8;i++){
  const j=i^7;
  rails.push({from:'a',fromVertex:i,to:'b',toVertex:j,
   orientation:'\\',weight:WAG276_CRYSTAL.railWeight});
  rails.push({from:'b',fromVertex:j,to:'a',toVertex:i,
   orientation:'/',weight:WAG276_CRYSTAL.railWeight});
 }
 return rails;
}
function wag276CrystalPropagate(a,b,passes=WAG276_CRYSTAL.passes){
 if(!Array.isArray(a)||!Array.isArray(b)||a.length!==8||b.length!==8)
  throw Error('crystal requires two cubits of eight neurons');
 if(![...a,...b].every(x=>Number.isFinite(x)&&x>=0&&x<=1))
  throw Error('activations must be finite in [0,1]');
 const clamp=x=>Math.max(0,Math.min(1,x));
 let outer=a.slice(),inner=b.slice(),trace=[];
 for(let pulse=0;pulse<passes;pulse++){
  const aNext=outer.slice(),bNext=inner.slice();
  for(let i=0;i<8;i++){
   const j=i^7,w=WAG276_CRYSTAL.railWeight;
   bNext[j]=clamp((1-w)*inner[j]+w*outer[i]);
   aNext[i]=clamp((1-w)*outer[i]+w*inner[j]);
  }
  outer=aNext;inner=bNext;
  trace.push({pulse:pulse+1,a:outer.slice(),b:inner.slice()});
 }
 return {a:outer,b:inner,trace,primitive:WAG276_CRYSTAL.primitive};
}
function wag276CrystalVerify(){
 const v=wag276CrystalVertices(),e=wag276CrystalEdges(),
  rails=wag276CrystalRails();
 if(v.length!==8||e.length!==12||rails.length!==16)throw Error('topology cardinality');
 for(const r of rails){
  if(r.from==='a'&&!rails.some(s=>s.from==='b'&&s.fromVertex===r.toVertex&&
   s.toVertex===r.fromVertex&&s.weight===r.weight))
   throw Error('unpaired crystalline rail');
 }
 const a=[0,1,0,1,0,1,0,1],b=[1,0,1,0,1,0,1,0];
 const initial=[...a,...b].reduce((s,v)=>s+v,0);
 const x=wag276CrystalPropagate(a,b);
 const final=[...x.a,...x.b].reduce((s,v)=>s+v,0);
 if(Math.abs(initial-final)>1e-12)throw Error('signal balance drift');
 if(JSON.stringify(wag276CrystalPropagate(a,b))!==JSON.stringify(x))
  throw Error('nondeterministic propagator');
 return {primitive:WAG276_CRYSTAL.primitive,verticesPerCubit:8,
  edgesPerCubit:12,opposedRailLinks:16,balancedSignalResidual:final-initial,
  deterministic:true,resourceAuthority:'WAG-244 only',policyStatus:'preview'};
}
if(typeof module!=='undefined')module.exports={
 WAG276_CRYSTAL,wag276CrystalVertices,wag276CrystalEdges,
 wag276CrystalRails,wag276CrystalPropagate,wag276CrystalVerify
};