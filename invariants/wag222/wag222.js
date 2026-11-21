// WAG-222 inherits WAG-221 — independent acquisition and shared-root auditing .dlw
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


const KINDS222=['distinct_verified','shared_direct','shared_deep','alias_shared','unverified_root','broken_link','cycle','independent_disagree','forged_alias','unverified_distinct'];
function fixture222(p,kind,seed){
 const base=fixture221(p,kind==='independent_disagree'?'independent_disagree':'independent_clean',seed);
 const graph={
  A:{parents:['a0'],verified:true},a0:{parents:['a1'],verified:true},a1:{parents:[],verified:true,root:true},
  B:{parents:['b0'],verified:true},b0:{parents:['b1'],verified:true},b1:{parents:[],verified:true,root:true}
 };
 if(kind==='shared_direct')graph.b0.parents=['a1'];
 if(['shared_deep','alias_shared','forged_alias'].includes(kind)){
  graph.b1.parents=['common'];graph.b1.root=false;graph.a1.parents=['common'];graph.a1.root=false;
  graph.common={parents:[],verified:true,root:true};
 }
 if(['alias_shared','forged_alias'].includes(kind)){graph.b1.parents=['aliasOfCommon'];graph.aliasOfCommon={parents:[],verified:true,aliasOf:'common'}}
 if(kind==='unverified_root')graph.b1.verified=false;
 if(kind==='unverified_distinct')graph.b0.verified=false;
 if(kind==='broken_link')graph.b1.parents=['not_found'];
 if(kind==='cycle')graph.b1.parents=['b0'];
 if(kind==='forged_alias')graph.aliasOfCommon.claimedRoot='fake-distinct';
 return {A:base.A,B:base.B,graph,kind,p,seed};
}
function ancestry222(graph,id){
 const visiting=new Set(),visited=new Set(),roots=new Set(),issues=[];
 function walk(node){
  if(visiting.has(node)){issues.push('CYCLE:'+node);return}
  if(visited.has(node))return;
  const entry=graph[node];if(!entry){issues.push('MISSING:'+node);return}
  visiting.add(node);
  if(entry.verified!==true)issues.push('UNVERIFIED:'+node);
  if(entry.aliasOf)walk(entry.aliasOf);
  else if(entry.parents?.length)for(const p of entry.parents)walk(p);
  else if(entry.root===true)roots.add(node);
  else issues.push('NO_ROOT:'+node);
  visiting.delete(node);visited.add(node);
 }
 walk(id);return {roots:[...roots].sort(),issues:[...new Set(issues)].sort(),visited:[...visited].sort()};
}
function assess222(f,mode='graph'){
 const a=ancestry222(f.graph,'A'),b=ancestry222(f.graph,'B'),agreement=agree221(f.A,f.B),shared=a.roots.some(root=>b.roots.includes(root));
 let status;
 if(mode==='labels')status=agreement>=.96?'INDEPENDENT_AGREEMENT':'DISAGREEMENT';
 else if(a.issues.length||b.issues.length||!a.roots.length||!b.roots.length)status='UNKNOWN_PROVENANCE';
 else if(shared)status='SHARED_ROOT';
 else if(agreement<.96)status='DISAGREEMENT';
 else status='INDEPENDENT_AGREEMENT';
 return {status,agreement,rootsA:a.roots,rootsB:b.roots,issuesA:a.issues,issuesB:b.issues,shared,independentWitnesses:status==='INDEPENDENT_AGREEMENT'?2:status==='SHARED_ROOT'?1:0};
}
function experiment222(){
 const rows=[],examples=[],counterexamples=[];let cases=0,pairedSlots=0,unsafeNaiveAgreements=0;
 for(const kind of KINDS222){
  let passed=0,failed=0,unknown=0,shared=0,independent=0,disagree=0,naiveFalse=0;
  for(const p of [9,13,17,23])for(let seed=222;seed<230;seed++){
   const f=fixture222(p,kind,seed),r=assess222(f),naive=assess222(f,'labels');
   const expected=kind==='distinct_verified'?'INDEPENDENT_AGREEMENT':kind==='independent_disagree'?'DISAGREEMENT':
    ['shared_direct','shared_deep','alias_shared','forged_alias'].includes(kind)?'SHARED_ROOT':'UNKNOWN_PROVENANCE';
   cases++;pairedSlots+=f.A.length;
   if(r.status===expected)passed++;else{failed++;if(counterexamples.length<16)counterexamples.push({kind,p,seed,expected,assessment:r,graph:f.graph,A:f.A,B:f.B})}
   unknown+=Number(r.status==='UNKNOWN_PROVENANCE');shared+=Number(r.status==='SHARED_ROOT');
   independent+=Number(r.status==='INDEPENDENT_AGREEMENT');disagree+=Number(r.status==='DISAGREEMENT');
   if(naive.status==='INDEPENDENT_AGREEMENT'&&r.status!=='INDEPENDENT_AGREEMENT'){naiveFalse++;unsafeNaiveAgreements++}
   if(seed===222&&p===9)examples.push({kind,p,seed,expected,assessment:r,naive:naive.status,graph:f.graph,observationsA:f.A,observationsB:f.B});
  }
  rows.push({kind,runs:32,passed,failed,unknown,shared,independent,disagree,naiveFalse});
 }
 return {cases,pairedSlots,unsafeNaiveAgreements,rows,examples,counterexamples};
}
if(typeof module!=='undefined')module.exports={fixture222,ancestry222,assess222,experiment222};
if(typeof require!=='undefined'&&require.main===module)console.log(JSON.stringify(experiment222(),null,2));
