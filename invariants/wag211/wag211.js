// WAG-211 — multi-frequency decomposition, .dlw
// Source ancestry: all components are hypotheses about ONE observed stream.
const PERIODS=[9,13,17,23];
function fixture(p,kind,seed){let x=seed>>>0;const rand=()=>{x=(Math.imul(x,1664525)+1013904223)>>>0;return x};const g=Array(384).fill(0);
 if(kind==='mixed'){for(let i=3;i<384;i+=p)g[i]=1;for(let i=7;i<384;i+=p+4)g[i]=1}
 else if(kind==='jittered'){for(let i=3;i<384;i+=p){const j=i+((rand()>>>16)%3)-1;g[j]=1}}
 else if(kind==='periodic'){for(let i=3;i<384;i+=p)g[i]=1}
 else if(kind==='skipped'){let n=0;for(let i=3;i<384;i+=p)if(n++%5!==4)g[i]=1}
 else if(kind==='drift'){for(let i=3;i<190;i+=p)g[i]=1;for(let i=195;i<384;i+=p+4)g[i]=1}
 else if(kind==='shuffled'){for(let i=3;i<384;i+=p)g[i]=1;for(let i=g.length-1;i>0;i--){let j=rand()%(i+1);[g[i],g[j]]=[g[j],g[i]]}}
 return g;
}
function observed(g,start,end){const a=[];for(let i=start;i<end;i++)if(g[i])a.push(i);return a}
function predicted(p,phase,start,end){const a=[];for(let i=start;i<end;i++)if(i%p===phase)a.push(i);return a}
function match(obs,pred,tol=1){let m=0;const used=Array(obs.length).fill(false);
 for(const x of pred){let best=-1,d=tol+1;for(let i=0;i<obs.length;i++)if(!used[i]&&Math.abs(obs[i]-x)<d){d=Math.abs(obs[i]-x);best=i}
 if(best>=0&&d<=tol){m++;used[best]=true}}
 const precision=pred.length?m/pred.length:0,recall=obs.length?m/obs.length:0;
 return {f1:precision+recall?2*precision*recall/(precision+recall):0,precision,recall,matched:m};
}
function evaluate(obs,components,start,end){const union=[...new Set(components.flatMap(c=>predicted(c.p,c.phase,start,end)))].sort((a,b)=>a-b);return match(obs,union)}
function infer(g){
 const train=observed(g,0,192),hold=observed(g,192,384),cs=[];
 for(let p=7;p<=30;p++){let top=null;for(let phase=0;phase<p;phase++){let score=evaluate(train,[{p,phase}],0,192);if(!top||score.f1>top.train.f1)top={p,phase,train:score}}cs.push(top)}
 cs.sort((a,b)=>b.train.f1-a.train.f1);
 const single={...cs[0],hold:evaluate(hold,[cs[0]],192,384)};
 let pair=null;
 for(let i=0;i<cs.length;i++)for(let j=i+1;j<cs.length;j++){const a=cs[i],b=cs[j],tr=evaluate(train,[a,b],0,192);if(!pair||tr.f1>pair.train.f1)pair={a,b,train:tr,hold:evaluate(hold,[a,b],192,384)}}
 if(pair&&pair.train.f1>=single.train.f1+.1&&pair.hold.f1>=single.hold.f1+.1&&pair.hold.precision>=.8&&pair.hold.recall>=.8)return {kind:'pair',periods:[pair.a.p,pair.b.p].sort((a,b)=>a-b),train:pair.train.f1,hold:pair.hold.f1};
 if(single.train.f1>=.85&&single.hold.f1>=.85)return {kind:'single',periods:[single.p],train:single.train.f1,hold:single.hold.f1};
 return {kind:'unknown',periods:[],train:single.train.f1,hold:single.hold.f1};
}
function experiment(){
 const rows=[],examples=[];let mirroredSamples=0;
 for(const kind of ['periodic','jittered','skipped','mixed','shuffled','drift']){let correct=0,wrong=0,unknown=0,pair=0;
 for(const p of PERIODS)for(let seed=211;seed<227;seed++){const g=fixture(p,kind,seed),r=infer(g);
 // Inverting observation polarity must not alter event-position inference.
 const mirrored=infer(g.map(x=>Number(x!==0)));if(r.kind!==mirrored.kind||JSON.stringify(r.periods)!==JSON.stringify(mirrored.periods))throw Error('symmetry');
 mirroredSamples+=g.length;
 const target=kind==='mixed'?[p,p+4].sort((a,b)=>a-b):['periodic','jittered','skipped'].includes(kind)?[p]:[];
 if(r.kind==='unknown')unknown++;else if(JSON.stringify(r.periods)===JSON.stringify(target))correct++;else{wrong++;if(examples.length<20)examples.push({kind,p,seed,r,target})}
 if(r.kind==='pair')pair++;
 }
 rows.push({kind,runs:64,correct,wrong,unknown,pair});
 }
 return {mirroredSamples,rows,examples};
}
if(typeof module!=='undefined')module.exports={fixture,infer,experiment};
if(typeof require!=='undefined'&&typeof module!=='undefined'&&require.main===module)console.log(JSON.stringify(experiment(),null,2));
