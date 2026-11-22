/* WAG-277 lattice-chain preview · ---@---@---@---@---{} · .dlw
   Each @ is an eight-vertex crystalline lattice junction.
   Each --- is a reciprocal SIGNAL coupling; {} is terminal two-cubit collector.
   No physical material, energy, or authorized action is transferred here.
   Experimental topology is kept SEPARATE from frozen WAG-276 candidate.
*/
const WAG277_CHAIN=Object.freeze({
 glyph:'---@---@---@---@---{}',
 junction:'@',link:'---',terminal:'{}',
 defaultJunctions:4,railWeight:.125,passes:3
});
function wag277ChainTopology(n=WAG277_CHAIN.defaultJunctions){
 if(!Number.isInteger(n)||n<2||n>64)throw Error('junction count must be 2..64');
 const nodes=Array.from({length:n},(_,i)=>({
  id:'J'+i,type:'crystalline-lattice',
  orientation:i%2?'/' :'\\',neurons:8,
  neighbors:[...(i?[i-1]:[]),...(i<n-1?[i+1]:[])]
 }));
 const links=Array.from({length:n-1},(_,i)=>({from:i,to:i+1,
  type:'reciprocal-signal',rails:8,weight:WAG277_CHAIN.railWeight}));
 const terminal={id:'T',type:'terminal-two-cubit',glyph:'{}',connectedTo:n-1,
  primitive:'{\\a{b/}}',neurons:16};
 return {glyph:'---@'.repeat(n).replace(/---@$/,'---@---{}'),nodes,links,terminal};
}
function wag277Initial(n=4,kind='pulse'){
 const t=wag277ChainTopology(n);
 const state=Array.from({length:n},()=>Array(8).fill(0));
 if(kind==='pulse'){state[0][0]=1;state[0][7]=.75}
 else if(kind==='alternating')for(let i=0;i<n;i++)for(let j=0;j<8;j++)
  state[i][j]=(i+j)%2?.8:.1;
 else if(kind==='uniform')for(const row of state)row.fill(.5);
 else throw Error('unknown test signal');
 return {topology:t,junctionSignals:state,terminalSignals:Array(16).fill(0),
  pulse:0};
}
function wag277Mass(state){return state.junctionSignals.flat()
 .concat(state.terminalSignals).reduce((a,b)=>a+b,0)}
function wag277Step(state,weight=WAG277_CHAIN.railWeight){
 if(!Number.isFinite(weight)||weight<0||weight>.25)throw Error('invalid coupling');
 const n=state.topology.nodes.length;
 if(state.junctionSignals.length!==n||state.terminalSignals.length!==16)
  throw Error('state topology mismatch');
 // Frozen synchronous pulse: all flux derives from pre-pulse state.
 const before=wag277Mass(state);
 const next=state.junctionSignals.map(z=>z.slice()),terminal=state.terminalSignals.slice();
 const move=(a,i,b,j)=>{const delta=weight*(a[i]-b[j]);return delta};
 // Each edge is processed exactly once, and its flux has equal opposite entries.
 for(const edge of state.topology.links)for(let k=0;k<8;k++){
  const source=state.junctionSignals[edge.from],target=state.junctionSignals[edge.to];
  const j=k^7,delta=move(source,k,target,j);
  next[edge.from][k]-=delta;next[edge.to][j]+=delta;
 }
 // Terminal {} carries a nested a{b} orientation. Its 16 signal nodes are
 // a reservoir for flux, not additional physical mass/energy.
 for(let k=0;k<8;k++){
  const src=state.junctionSignals[n-1],delta=weight*(src[k]-state.terminalSignals[k]);
  next[n-1][k]-=delta;terminal[k]+=delta;
 }
 for(let k=0;k<8;k++){
  const delta=weight*(state.terminalSignals[k]-state.terminalSignals[8+(k^7)]);
  terminal[k]-=delta;terminal[8+(k^7)]+=delta;
 }
 const afterState={topology:state.topology,junctionSignals:next,
  terminalSignals:terminal,pulse:state.pulse+1},after=wag277Mass(afterState);
 const error=Math.abs(after-before);
 if(error>1e-9)throw Error('signal sum drift: '+error);
 if(!next.flat().concat(terminal).every(v=>v>=-1e-12&&v<=1+1e-12))
  throw Error('activation range failure');
 return {...afterState,signalResidual:error};
}
function wag277Simulate(junctions=4,steps=64,kind='pulse'){
 if(!Number.isInteger(steps)||steps<0||steps>4096)throw Error('bad pulse count');
 let s=wag277Initial(junctions,kind);const initialMass=wag277Mass(s),timeline=[];
 const snap=()=>timeline.push({pulse:s.pulse,meanByJunction:s.junctionSignals.map(z=>
   z.reduce((a,b)=>a+b,0)/8),
  terminalA:s.terminalSignals.slice(0,8).reduce((a,b)=>a+b,0)/8,
  terminalB:s.terminalSignals.slice(8).reduce((a,b)=>a+b,0)/8,
  signalMass:wag277Mass(s)});
 snap();
 for(let i=0;i<steps;i++){s=wag277Step(s);snap()}
 return {junctions,steps,kind,initialMass,finalMass:wag277Mass(s),
  maxResidual:Math.max(...timeline.map(z=>Math.abs(z.signalMass-initialMass))),
  timeline,state:s};
}
function wag277Verify(){
 const checks=[];
 for(const n of [2,4,8,16]){
  const a=wag277Simulate(n,80,'pulse'),b=wag277Simulate(n,80,'pulse');
  if(JSON.stringify(a.timeline)!==JSON.stringify(b.timeline))throw Error('nondeterministic '+n);
  if(a.maxResidual>1e-9)throw Error('conservation '+n);
  const u=wag277Simulate(n,30,'uniform');
  if(u.timeline.some(z=>Math.abs(z.signalMass-u.initialMass)>1e-9))throw Error('uniform '+n);
  checks.push({junctions:n,signals:n*8+16,
   massResidual:a.maxResidual,deterministic:true,
   terminalReached:a.state.terminalSignals.some(v=>v>0)});
 }
 return {primitive:WAG277_CHAIN.glyph,checks,
  policyStatus:'topology-only preview',authoritativeController:'WAG-276 unchanged'};
}
if(typeof module!=='undefined')module.exports={WAG277_CHAIN,wag277ChainTopology,
 wag277Initial,wag277Step,wag277Mass,wag277Simulate,wag277Verify};
