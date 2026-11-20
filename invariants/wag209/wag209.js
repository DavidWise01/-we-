// WAG-208, extended WAG-209 — cross-window harmonic ancestry, .dlw
const PERIODS=[9,13,17,23], MODES=['spacing','confirmed','dual'];
function events(g){const e=[];for(let i=1;i<g.length;i++)if(g[i]!==g[i-1]&&(e.length===0||i!==e[e.length-1]+1))e.push(i);return e}
function intervals(e){const a=[];for(let i=1;i<e.length;i++){const d=e[i]-e[i-1];if(d>=4&&d<=32)a.push(d)}return a}
function median(a){if(!a.length)return null;const b=a.slice().sort((x,y)=>x-y);return b[Math.floor(b.length/2)]}
function support(a,p,t){return a.length?a.filter(d=>Math.abs(d-p)<=t).length/a.length:0}
function propose(e,t){const a=intervals(e),p=median(a);return p!==null&&a.length>=5&&support(a,p,t)>=.8?p:null}
function recurrence(e,p,t){let hits=0;for(let i=0;i<e.length-1;i++){for(let j=i+1;j<e.length;j++){const d=e[j]-e[i];if(d>p+t)break;if(Math.abs(d-p)<=t){hits++;break}}}return e.length>1?hits/(e.length-1):0}
function infer(g,t,mode){
 const e=events(g);
 if(mode==='spacing'||mode==='confirmed'){const p=propose(e,t),v=p===null?0:mode==='spacing'?support(intervals(e),p,t):recurrence(e,p,t);return {period:v>=(mode==='spacing'?.8:.55)?p:null,score:v}}
 const early=e.filter(x=>x<192),later=e.filter(x=>x>=192),p=propose(early,t);
 if(p===null)return {period:null,score:0,reason:'insufficient'};
 const a=intervals(later),score=support(a,p,t);
 if(a.length<5||score<.8)return {period:null,score,reason:'holdout'};
 const aliases=Array.from({length:p-4},(_,i)=>i+4).filter(q=>p%q===0&&q<p&&support(a,q,t)>=score-.05);
 if(aliases.length)return {period:null,score,reason:'harmonic'};
 return {period:p,score,reason:'confirmed'};
}
function fixture(p,kind,seed){let x=seed>>>0;const rand=()=>{x=(Math.imul(x,1664525)+1013904223)>>>0;return x};const g=Array.from({length:384},(_,i)=>i%p===3?1:0);
 if(kind==='shuffled')for(let i=g.length-1;i>0;i--){const j=rand()%(i+1);[g[i],g[j]]=[g[j],g[i]]}
 if(kind==='jittered')for(let i=3;i<383;i+=p){const j=i+((rand()>>>16)%3)-1;g[i]=0;g[j]=1}
 return g}
function experiment(){let checks=0;const rows=[];
 for(const tolerance of [0,1,2])for(const kind of ['periodic','jittered','shuffled'])for(const mode of MODES){
 let locked=0,correct=0,wrong=0,abstain=0,harmonic=0;
 for(const p of PERIODS)for(let seed=208;seed<272;seed++){const g=fixture(p,kind,seed),r=infer(g,tolerance,mode),m=infer(g.map(x=>1-x),tolerance,mode);
 if(r.period!==m.period||r.score!==m.score||r.reason!==m.reason)throw Error('polarity asymmetry');checks+=384;
 if(r.period===null){abstain++;harmonic+=Number(r.reason==='harmonic')}else{locked++;correct+=Number(r.period===p);wrong+=Number(r.period!==p)}}
 rows.push({tolerance,kind,mode,runs:256,locked,correct,wrong,abstain,harmonic});
 }
 return {observationChecks:checks,mirroredChecks:checks,rows};
}
if(typeof module!=='undefined')module.exports={events,intervals,median,support,propose,recurrence,infer,fixture,experiment};
if(typeof require!=='undefined'&&typeof module!=='undefined'&&require.main===module)console.log(JSON.stringify(experiment(),null,2));


function infer209(g,t,policy='cross'){
 const base=infer(g,t,'dual');
 const pooled=propose(events(g),t);
 if(policy==='prior')return base;
 if(policy==='pooled')return {period:pooled,score:pooled===null?0:support(intervals(events(g)),pooled,t),reason:'pooled'};
 if(base.period===null)return base;
 return base.period===pooled?base:{period:null,score:base.score,reason:'conflicting_periods',provisional:base.period,pooled};
}
function counterexamples(){
 const items=[];
 for(const p of [9,13,17,23])for(let seed=208;seed<272;seed++){
 const g=fixture(p,'jittered',seed),r=infer209(g,2,'prior');
 if(r.period===null||r.period===p)continue;
 let minPrefix=g.length;
 for(let n=193;n<=g.length;n++)if(infer209(g.slice(0,n),2,'prior').period===r.period){minPrefix=n;break}
 const shrunk=g.slice(0,minPrefix);
 if(infer209(shrunk,2,'prior').period!==r.period)throw Error('bad reproducer');
 items.push({truePeriod:p,seed,wrongPeriod:r.period,minimalByPrefixOnly:minPrefix,observedBinaryPrefix:shrunk.join(''),observedEventPositions:events(shrunk),fullEventPositions:events(g),correctedEstimate:infer209(g,2,'cross')});
 }
 return items;
}
function experiment209(){
 let checks=0;
 const rows=[],kinds=['periodic','jittered','shuffled'];
 for(const tol of [0,1,2])for(const kind of kinds)for(const mode of ['prior','pooled','cross']){
 let correct=0,wrong=0,unknown=0,conflicted=0;
 for(const p of [9,13,17,23])for(let seed=208;seed<272;seed++){
 const g=fixture(p,kind,seed),r=infer209(g,tol,mode),m=infer209(g.map(v=>1-v),tol,mode);
 if(r.period!==m.period||r.reason!==m.reason||r.score!==m.score)throw Error('mirror failed');
 checks+=g.length;
 if(r.period===null){unknown++;conflicted+=Number(r.reason==='conflicting_periods')}
 else if(r.period===p)correct++;else wrong++;
 }
 rows.push({tol,kind,mode,correct,wrong,unknown,conflicted});
 }
 const errors=counterexamples();
 if(errors.length!==4)throw Error('expected exactly four preserved failures');
 const t=rows.filter(r=>r.tol===2&&r.kind==='jittered'&&r.mode==='cross')[0];
 if(t.correct!==248||t.wrong!==0||t.unknown!==8)throw Error('regression mismatch');
 return {mirroredSlotChecks:checks,cases:errors.length,rows};
}
if(typeof module!=='undefined')module.exports={infer209,counterexamples,experiment209,fixture};
