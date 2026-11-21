// WAG-221 — independent acquisition and shared-root auditing .dlw
const PERIODS221=[9,13,17,23],KINDS221=['independent_clean','shared_copy','shared_corruption','independent_disagree','shared_upstream','forged_distinct'];
function random221(seed){let x=seed>>>0;return ()=>{x=(Math.imul(x,1664525)+1013904223)>>>0;return x}}
function source221(p){const a=Array(192).fill(0);for(let i=3;i<192;i+=p)a[i]=1;return a}
function fixture221(p,kind,seed){
 const original=source221(p),A=original.slice(),B=original.slice(),randA=random221(seed+401),randB=random221(seed+809);
 // The latent stimulus is shared; independence concerns acquisition roots, not the observed target.
 const rootA=['sensor-A:'+seed],rootB=['independent_clean','independent_disagree'].includes(kind)?['sensor-B:'+seed]:['sensor-A:'+seed,'relay-B:'+seed];
 if(kind==='shared_corruption'||kind==='shared_upstream')for(let i=0;i<192;i++)if(i%19===0){A[i]=1-A[i];B[i]=A[i]}
 if(kind==='independent_disagree')for(let i=0;i<192;i++)if(i%3===0)B[i]=1-B[i];
 if(kind==='independent_clean')for(let i=0;i<192;i++){if(randA()%97===0)A[i]=1-A[i];if(randB()%97===0)B[i]=1-B[i]}
 const claimedB=kind==='forged_distinct'?['sensor-B:'+seed]:rootB.slice();
 return {A,B,rootA,rootB,claimedB,kind,p,seed};
}
function agree221(A,B){let equal=0;for(let i=0;i<A.length;i++)equal+=Number(A[i]===B[i]);return equal/A.length}
function assess221(f,policy='anchored'){
 const checkedB=policy==='self_reported'?f.claimedB:f.rootB;
 const shared=f.rootA.some(x=>checkedB.includes(x)),agreement=agree221(f.A,f.B);
 const outcome=shared?'SHARED_ROOT':agreement>=.96?'INDEPENDENT_AGREEMENT':'DISAGREEMENT';
 return {outcome,agreement,shared,qualified:outcome==='INDEPENDENT_AGREEMENT',
  rootsChecked:policy==='anchored'?'fixture-root-registry':'self-reported',
  note:'Synthetic acquisition lineage. A fixture registry is NOT real authenticated sensor provenance.'};
}
function experiment221(){
 const rows=[],examples=[],counterexamples=[];let comparisons=0,independentAgreements=0,sharedRejected=0,disagreements=0,forgeriesExposed=0;
 for(const kind of KINDS221){let independent=0,shared=0,disagree=0,wrong=0,selfReportedQualified=0;
  for(const p of PERIODS221)for(let seed=221;seed<229;seed++){
   const f=fixture221(p,kind,seed),r=assess221(f),self=assess221(f,'self_reported');comparisons+=192;
   if(r.outcome==='INDEPENDENT_AGREEMENT'){independent++;independentAgreements++}
   if(r.outcome==='SHARED_ROOT'){shared++;sharedRejected++}
   if(r.outcome==='DISAGREEMENT'){disagree++;disagreements++}
   if(self.qualified)selfReportedQualified++;
   const expected=kind==='independent_clean'?'INDEPENDENT_AGREEMENT':kind==='independent_disagree'?'DISAGREEMENT':'SHARED_ROOT';
   if(r.outcome!==expected){wrong++;if(counterexamples.length<16)counterexamples.push({kind,p,seed,expected,result:r,A:f.A,B:f.B})}
   if(kind==='forged_distinct'&&self.qualified&&!r.qualified)forgeriesExposed++;
   if(seed===221&&p===9)examples.push({kind,p,seed,rootA:f.rootA,rootB:f.rootB,claimedB:f.claimedB,assessment:r,selfReported:self,A:f.A,B:f.B});
  }
  rows.push({kind,runs:32,independent,shared,disagree,wrong,selfReportedQualified});
 }
 return {comparisons,independentAgreements,sharedRejected,disagreements,forgeriesExposed,rows,examples,counterexamples};
}
if(typeof module!=='undefined')module.exports={fixture221,assess221,experiment221};
if(typeof require!=='undefined'&&require.main===module)console.log(JSON.stringify(experiment221(),null,2));
