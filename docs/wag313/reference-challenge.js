/* WAG-313 · Phase VII 2/8 · Ed25519 reference challenge-response · .dlw
 * Offline-generated test signatures. NO private keys shipped.
 * An external reference signer authenticates a nonce/sequence/epoch/channel.
 * Challenge response is not a truth oracle and keys are synthetic fixtures.
 * Three frontal forms remain blind and read only.
 */
const WAG313=Object.freeze({phase:'VII',turn:2,of:8,epoch:313,
 cases:Object.freeze(['clean','nonce-replay','epoch-mismatch','response-tamper',
 'signature-swap','key-substitution','shared-root','missing-response',
 'signed-false-correct-reference','correlated-signed-false','wrong-signed-reference']),
 referenceKey:'3vOs6xeVzKH5tOpWl8hcQij+Kp6QKfx82xED1MjLfA8=',physicalActions:0});
const WAG313_SIGNATURES=Object.freeze([["Q2riJ5yyOr+Cz9nChV4IQfkpLqWbZqiy4LBiswNslrGqBrNmlrpETvGSxrZnbSkwcjvLQQiv3J0Smw3Uo+ruDA==","uDhvqtKYO6emVmyoOLx7ktYEQ9Zsu1tkhT6H+/TrIGmQLQyzV2qeueNMbwU7oPDd5IXH7oVW32yMjJZyNNsLAg=="],["CidJT5XBZKzH7d2tjP+zoKSTiZoswF/un/Vroi263Lu/4Nb4J4uH59CGimyWOP+2lnM2LBqSTG69bfJdb7hZAg==","vOyXwMRQowItDM2PJZnXWwotXzkHaaRpi+8/r7SDg4mPF+UOGdBtkH1CJC5Aa0VROmFLBc3PQx5Nb/L1ns8SDA=="],["k8bXf3Ny8GbInJLTp2ijCIWBPpMrj9OogSxJjZ9iOrmB8BVr8gkPcppHksixuT0tu4Rpf4n5nYlB/MfMxJ/VBQ==","deKk0/Wgwq8PJZsmall3i3kYy16YAlGa8/mZHWxGvHn9t1x4udwl4Ce9PZpXLOmRFbEh5KWCkHsy3zytzDvrCg=="],["UVqT11dbpLaTCFcOijpJRV7iPC28KgLwqHlWIJtRIF2OVfXlKn+tVnF1rKTsOUOL8Ft91i21gY6pFxU2Jq5lBg==","SS8wmbj3LL9cSIgkHjDDSqzeDp3XqgIFgzLojbT4X0Ik3wPUVQnSA5oubB74HbBlX3pUGluRfYJwxUUPYq9XAg=="],["eDOp449UHFKxedwNcTfvNUWk9j1xo+hBQCkRmVYMDQRHvc34g0HlKSbfVBO2Y1h03h4zGusDx1q+wyK/TbFCAw==","mTG5ftVGg0zQh95QqPjuKhN9Q5XLClrDwlZ+lROYebfcuYBUWyMXayVAzczuXpql+2Ja+cO3sM4P2esIT66XBA=="],["7YNl/u8FM7rZHDAiF8vnz6gLNTAol2nj+s3vJ7pccttzRMfQhxElErJcbt6yntu5Va/uchMaQ3air2VyKVn1Aw==","8zzqngcsak0rIdUdqrWPjUs9SlLcEvq++YYOpeRcNUSTZl6iTJQxCIYrwZS5X+YIkJUGjd1/t6cHA8p/GiQkAA=="],["yOKtNaxJura1ggjb3ec9gqFc6CjlOTISFw1BFiRMhuabOklZr+PUc1mUvo9wWL4iFcXUbKGPaDpANqMJA6f7DA==","CsNIiVysmMUgicFFGysx/10RdRThUJjZaBMJX05fnxf77bo4C2XFoNd2t2ybT2yyHN3PbwGp3OcEINcABkKiBw=="],["Lp2ncAlSDE4j+RIK9ySNmq1Fozdat0gMro5RrNZyJevT90YKGhATLdFwlESpUJ+OZy2S8eDAZu0vCQBO7au+CA==","zPYmHp0grtcFxtYN2StQtRqNZCmlltNA563zotC/Pe8BsX8Sjis/XvYYXXnT4WquGD1BdIG6qh/q4rhzLSGiAg=="]]);
function wag313Message(seq,channel){
 return {version:313,reference:'fixture-D',leaf:'ref-leaf',
 challenge:'wag313-nonce-'+String(seq).padStart(2,'0'),epoch:313,sequence:seq,channel};
}
function wag313Challenge(kind,seq){
 const falseObserved=kind==='signed-false-correct-reference'||kind==='correlated-signed-false';
 const replyChannel=kind==='signed-false-correct-reference'||kind==='wrong-signed-reference'?4:3;
 const s=kind==='nonce-replay'?(seq+7)%8:seq;
 const packet={body:wag313Message(s,replyChannel),key:WAG313.referenceKey,
 signature:WAG313_SIGNATURES[s][replyChannel===4?1:0],
 ancestry:Object.freeze(['fixture-D'])};
 if(kind==='epoch-mismatch')packet.body.epoch=312;
 if(kind==='response-tamper')packet.body.channel=4;
 if(kind==='signature-swap')packet.signature=WAG313_SIGNATURES[s][replyChannel===4?0:1];
 if(kind==='key-substitution')packet.key=WAG309_PUBLIC_KEYS[0];
 if(kind==='shared-root')packet.ancestry=Object.freeze(['fixture-D','fixture-A']);
 if(kind==='missing-response')packet.signature='';
 return {packet,falseObserved,expectedChallenge:wag313Message(seq,3).challenge};
}
function wag313Decode(s){return Uint8Array.from(atob(s),c=>c.charCodeAt(0))}
async function wag313Check(packet,seq){
 const body=packet.body;
 const context=body.version===313&&body.reference==='fixture-D'&&body.leaf==='ref-leaf'
  &&body.epoch===313&&body.sequence===seq&&body.challenge===wag313Message(seq,3).challenge
  &&(body.channel===3||body.channel===4);
 const keyPinned=packet.key===WAG313.referenceKey;
 const noSharedRoot=Array.isArray(packet.ancestry)&&packet.ancestry.length===1&&packet.ancestry[0]==='fixture-D';
 let signatureOK=false;
 try{
  const key=await crypto.subtle.importKey('raw',wag313Decode(WAG313.referenceKey),{name:'Ed25519'},false,['verify']);
  signatureOK=await crypto.subtle.verify('Ed25519',key,wag313Decode(packet.signature),
    new TextEncoder().encode(JSON.stringify(body)));
 }catch(e){signatureOK=false}
 return Object.freeze({context,keyPinned,noSharedRoot,signatureOK,
  valid:context&&keyPinned&&noSharedRoot&&signatureOK});
}
async function wag313Trial(kind,seq){
 const fixture=wag313Challenge(kind,seq);
 const signed=await wag309Trial(fixture.falseObserved?'signed-false-observation':'clean',seq);
 const reference=await wag313Check(fixture.packet,seq);
 const available=signed.trusted&&signed.unanimous&&signed.candidate!==null;
 const agrees=available&&signed.candidate===fixture.packet.body.channel;
 const candidate=reference.valid&&agrees?signed.candidate:null;
 const target=fixture.falseObserved?4:3;
 return Object.freeze({kind,seq,reference,observedSigned:signed.trusted,
  localClaims:signed.claims,reply:fixture.packet.body,agrees,candidate,target,
  verdict:!reference.valid?'REFERENCE_CHALLENGE_REJECTED':
   !available?'SOURCE_REJECTED':!agrees?'REFERENCE_CONFLICT':'SIGNED_REFERENCE_AGREEMENT',
  truthAuthenticated:false,realIdentityVerified:false,promotionAuthorized:false});
}
async function wag313Evaluate(source){
 const before=JSON.stringify(source),rows=[];
 for(const kind of WAG313.cases){
  let correct=0,wrong=0,abstain=0,referenceRejected=0;
  for(let seq=0;seq<8;seq++){
   const x=await wag313Trial(kind,seq);
   if(!x.reference.valid)referenceRejected++;
   if(x.candidate===null)abstain++;
   else if(x.candidate===x.target)correct++;else wrong++;
  }
  rows.push({kind,correct,wrong,abstain,referenceRejected,total:8});
 }
 if(JSON.stringify(source)!==before)throw Error('authority mutated');
 return wag291DeepFreeze({bound:'WAG-313',phase:'VII',turn:2,rows,testCases:88,
  referenceSignatures:16,publicKeyPinned:true,realWorldIdentityAuthenticated:false,
  truthAuthenticated:false,controllerPromoted:false,physicalActions:0,
  caveat:'Valid signatures can corroborate the same false information; independence and physical truth are unverified.'});
}
async function wag313Audit(){
 const s=wag288Initial(),snap=JSON.stringify(s),a=await wag313Evaluate(s),
 b=await wag313Evaluate(s),get=k=>a.rows.find(x=>x.kind===k);
 const checks={
  deterministic:JSON.stringify(a)===JSON.stringify(b),
  readOnly:JSON.stringify(s)===snap,
  elevenScenarios:a.rows.length===11&&a.testCases===88,
  sixteenSignedResponses:WAG313_SIGNATURES.length===8&&WAG313_SIGNATURES.every(x=>x.length===2),
  accounting:a.rows.every(x=>x.correct+x.wrong+x.abstain===8),
  cleanAccepted:get('clean').correct===8,
  nonceReplayRejected:get('nonce-replay').abstain===8,
  epochRejected:get('epoch-mismatch').abstain===8,
  tamperingRejected:get('response-tamper').abstain===8,
  swappedSignatureRejected:get('signature-swap').abstain===8,
  changedKeyRejected:get('key-substitution').abstain===8,
  commonRootRejected:get('shared-root').abstain===8,
  absentResponseRejected:get('missing-response').abstain===8,
  signedFalseCorrectReferenceRejected:get('signed-false-correct-reference').abstain===8,
  signedFalseConsensusRetained:get('correlated-signed-false').wrong===8,
  wrongReferenceWithheld:get('wrong-signed-reference').abstain===8,
  signaturesVerified:(await wag313Check(wag313Challenge('clean',0).packet,0)).signatureOK,
  noPrivateKey:!('privateKey' in WAG313),
  noTruthPromotion:!a.truthAuthenticated&&!a.controllerPromoted,
  immutable:Object.isFrozen(a)&&Object.isFrozen(a.rows[0]),
  noActions:a.physicalActions===0,
  noPeerInputs:WAG304.forms.join('|')==='[1]|{1}|(1)'
 };
 return {bound:'WAG-313',pass:Object.values(checks).every(Boolean),checks,rows:a.rows,progress:2/8};
}
if(typeof module!=='undefined')module.exports={WAG313,WAG313_SIGNATURES,wag313Message,wag313Challenge,wag313Check,wag313Trial,wag313Evaluate,wag313Audit};
