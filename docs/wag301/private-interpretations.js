/* WAG-301 · private interpretations · .dlw
 * Exactly one frontal ADDRESS with three mutually unaware interpretive forms.
 * [1] sees ONLY an 8-vector at address 62 and uses peak selection.
 * {1} sees ONLY 27 anonymous cortex 8-vectors and uses per-channel medians.
 * (1) sees ONLY 26 anonymous shell vectors and uses cyclic neighbor contrast.
 * No form receives its peers, the target, full state, or the adjudicator.
 * Distinct algorithms are not proof of independent evidence ancestry.
 */
const WAG301=Object.freeze({forms:Object.freeze(['[1]','{1}','(1)']),
 thresholds:Object.freeze([.25,.5,.75]),routines:Object.freeze(['peak','median','cyclic-contrast']),
 center:62,physicalActions:0});
function wag301Choose(scores){let channel=0;for(let i=1;i<8;i++)if(scores[i]>scores[channel])channel=i;
 const rank=scores.slice().sort((a,b)=>b-a);return {channel,margin:rank[0]-rank[1],strength:rank[0]};}
function wag301Box(local){
 if(!Array.isArray(local)||local.length!==8)throw Error('box input dimension');
 const p=wag301Choose(local);
 return Object.freeze({form:'[1]',method:'peak',...p,claim:'MY_LOCAL_TRUTH'});
}
function wag301Brace(siteVectors){
 if(!Array.isArray(siteVectors)||siteVectors.length!==27||siteVectors.some(x=>!Array.isArray(x)||x.length!==8))throw Error('brace input dimension');
 const medians=Array.from({length:8},(_,ch)=>{
  const v=siteVectors.map(x=>x[ch]).sort((a,b)=>a-b);return v[13];
 });
 return Object.freeze({form:'{1}',method:'median',...wag301Choose(medians),claim:'MY_LOCAL_TRUTH'});
}
function wag301Toroid(shellVectors){
 if(!Array.isArray(shellVectors)||shellVectors.length!==26||shellVectors.some(x=>!Array.isArray(x)||x.length!==8))throw Error('toroid input dimension');
 const means=Array.from({length:8},(_,ch)=>shellVectors.reduce((s,x)=>s+x[ch],0)/26);
 const contrast=means.map((v,i)=>v-.25*(means[(i+7)%8]+means[(i+1)%8]));
 return Object.freeze({form:'(1)',method:'cyclic-contrast',...wag301Choose(contrast),claim:'MY_LOCAL_TRUTH'});
}
function wag301Observe(source,light){
 if(!Number.isFinite(light)||light<0||light>1)throw Error('illumination domain');
 const group=wag289Groups(),claims=[];
 if(light>=.25)claims.push(wag301Box(source.nodes[62].slice()));
 if(light>=.5)claims.push(wag301Brace(group.cortex.concat(group.frontal).map(i=>source.nodes[i].slice())));
 if(light>=.75)claims.push(wag301Toroid(group.cortex.map(i=>source.nodes[i].slice())));
 return wag291DeepFreeze({light,claims,decision:wag300Adjudicate(claims),
   note:'observers have different private algorithms but share source lineage'});
}
function wag301Scenario(source,target,kind,trial){
 const nodes=source.nodes.map(x=>x.slice()),groups=wag289Groups();
 const wrong=(target+1+trial%3)%8;
 for(const i of groups.cortex){
  for(let c=0;c<8;c++)nodes[i][c]=c===target?.88:.08;
  if(kind==='cortex-corrupt'&&((i+trial)%26)<18){nodes[i][target]=.03;nodes[i][wrong]=.98;}
 }
 for(let c=0;c<8;c++)nodes[62][c]=c===target?.95:.05;
 if(kind==='frontal-corrupt'||kind==='both-corrupt'){nodes[62][target]=.02;nodes[62][wrong]=.99;}
 if(kind==='both-corrupt')for(const i of groups.cortex)for(let c=0;c<8;c++)nodes[i][c]=c===wrong?.96:.04;
 return {nodes,tick:source.tick};
}
function wag301Evaluate(source){
 const before=JSON.stringify(source),rows=[];
 for(const kind of ['clear','frontal-corrupt','cortex-corrupt','both-corrupt']){
  let correct=0,wrong=0,abstain=0,unanimous=0;
  for(let target=0;target<8;target++)for(let trial=0;trial<8;trial++){
   const receipt=wag301Observe(wag301Scenario(source,target,kind,trial),1);
   if(receipt.decision.unanimous)unanimous++;
   if(receipt.decision.candidate===null)abstain++;
   else if(receipt.decision.candidate===target)correct++;else wrong++;
  }
  rows.push({kind,correct,wrong,abstain,unanimous,total:64});
 }
 if(JSON.stringify(source)!==before)throw Error('source changed');
 return wag291DeepFreeze({bound:'WAG-301',tick:source.tick,
   rows,phase:'V',turn:6,sharedRootCount:1,authority:'READ_ONLY',
   limitations:'private JavaScript function inputs, not security sandbox or independent source origins',
   physicalActions:0});
}
function wag301Audit(){
 const s=wag288Initial(),snap=JSON.stringify(s),
  initial=wag301Observe(s,1),dark=wag301Observe(s,0),
  receipts=wag301Evaluate(s),repeat=wag301Evaluate(s);
 const checks={
  distinctProcedures:new Set(WAG301.routines).size===3,
  exactForms:WAG301.forms.join('|')==='[1]|{1}|(1)',
  oneCenter:wag289Groups().frontal.length===1&&WAG301.center===62,
  darkNoClaims:dark.claims.length===0,
  partialOnlyOne:wag301Observe(s,.25).claims.length===1,
  middleOnlyTwo:wag301Observe(s,.5).claims.length===2,
  fullThree:initial.claims.length===3,
  methodsMapped:initial.claims.map(c=>c.method).join('|')==='peak|median|cyclic-contrast',
  privateOutputShape:initial.claims.every(c=>!('peer' in c)&&!('other' in c)&&!('target' in c)),
  conflictVeto:wag300Adjudicate([{channel:0},{channel:1},{channel:0}]).candidate===null,
  sharedAncestry:initial.decision.independentRoots===1,
  expectedDimensions:(()=>{try{wag301Brace([[0]]);return false}catch(e){return true}})(),
  fourCases:receipts.rows.length===4&&receipts.rows.every(r=>r.total===64&&r.correct+r.wrong+r.abstain===64),
  deterministic:JSON.stringify(receipts)===JSON.stringify(repeat),
  readOnly:JSON.stringify(s)===snap,
  immutable:Object.isFrozen(receipts)&&Object.isFrozen(receipts.rows[0]),
  previousGate:wag300Audit().pass,
  noActuation:receipts.physicalActions===0
 };
 return {bound:'WAG-301',checks,pass:Object.values(checks).every(Boolean),results:receipts.rows,phaseProgress:.75};
}
if(typeof module!=='undefined')module.exports={WAG301,wag301Box,wag301Brace,wag301Toroid,wag301Observe,wag301Scenario,wag301Evaluate,wag301Audit};
