/* WAG-316 · Phase VII 5/8 · independently signed anchor fixtures · .dlw
 * Two distinct Ed25519 fixture keys sign status-Q and clock-T records.
 * 8 signed records per authority, private keys intentionally omitted.
 * Source identities and ancestry are synthetic assertions, NOT independent
 * attestation by a real external trust authority. No trusted hardware clock.
 * Shared roots are rejected externally. Signed false evidence still fails truth.
 * Three interpreters remain unaware of their peers / reference.
 */
const WAG316=Object.freeze({phase:'VII',turn:5,of:8,epoch:316,
 cases:Object.freeze(["clean","status-missing","clock-missing","status-tamper","clock-tamper","swapped-key","shared-root","replayed-counter","counter-ahead","reported-revocation","unreported-compromise","correlated-false-reference"]),physicalActions:0});
const WAG316_FIXTURES=Object.freeze({"status":{"key":"TBkp2ZZ07o78z7qpwro2yOqkylhFYXhG9UuN5E4tszc=","signatures":["BF1R7eE10R5z7s61ClUMxzYSj/ukqd3bTMZXYiepSaQgvbyv4kBCu+JYv9NdfpxQJ3e2Vob5UnKaxKfkyoTtCg==","u0oHHaZxFSRE/OOXD0snq7OBtHkHsLDW8EpLEs+LEKuE58YHA3+hklsLwddT2vAWqJDielJwd+F2/facVL8fAg==","9Cps/s71xsoA6xwXSPxj2EjU1nyMf3U2pXmQIrkI9G1F//4XqY/tcIU3qSnDicyxBiB/rI6KKR464lBqoW3qBQ==","xnHSGP1aIAY+d2NZZQHVHpZBqc+Cp/oBzaB+1FFMy6A/SheHg+ygKZSQPxWhz8b0/WU/0wble/dRfCgZMMz1AA==","qEPmxIW3jxJTER2KloFNEYLAYeenlxFlCXISUf78GSefXIGVc/UrwveNfJfXS+lAXe3MQFjQdt3Er4xJBL2dBA==","wtEytBsuoIJXydy/hxF6YNiKKQxhP+zYcqGoW9JEDTFJVcOJmXRlUTIGPBX0JMrsdK9qgCwOUSR4O4KbwvLADw==","Rz8RceskEV/ymRE6cNnT32XwoZ22OzrwC5XVKc+CBb1jMbGcZb4BUswa4irAomApPjWwweptq5Ma5WVC1DStAQ==","lD0HTtzCkx+WtV/9uPrL3LrMauLnnddIBzxlEcdopsz97VfAQh4KO8b5bcTHszXGo9SAFUJu+3YVHcDqGdEWCw=="]},"clock":{"key":"Tlxfp8TsoAuzye/sO4CoF/m17BR+uyDuD+gdZ8eMguo=","signatures":["8Sf1Nt4NAtiqK6L89CSmtrsLNlq6/2r1F+n2s/jwBSs/gH44WlKvDvQTvY3WrrV8pB1OdoAVGoSE/nBHPV1zAw==","GNUpL8lAMOFi+ItLarv5836YKPcdDJw78V/dzaFO4cg1J19XcCeHTtrrmN9yjp1WRZXaw9WN8E/BF7SautT6Dw==","rv0TPQbeKtw0jwCzJJaH244PmLfn1RAGSRVTsh36/zI+ymUssa81i2hmr4QbpW6hUnBCKD2urzjmy+N8s0oaBw==","LzPCdDjlMHRU5QDknRHxjT3WfGU3iIcybsFZuW+rs5a5wHNAmQjmz9DBnfo2VKB/GEbdeZ2pUlvhuuUF992tBw==","k0mvLUOgOsr+qwEZr0C2aQOWvs0IH30DHY/AYkgQVx3Nc8ZDj0nyU/dE+GdO6lVH8wYvylk5Rg/iP+iHEQ0TCw==","sUdx7o47w1JgT73y06RoWInNr9BI9SqQXu2cCsl+e/bO23C1I9MTXwfIyoOMTU+rFff+exwLpNrpp4yWWDvnBg==","9S7iNPA8aMahmlYFi7SO7oUVlIIWX9bEHi58WrdMFjiNFYr2ohl6xoiNwcGw/wgTdjZNA8VekWzbHUqxDV8+Cg==","F7OV4xZoFczikDCpSldUxdDvxsVdyayC7w4R/iYyoM87Fqq3h3Ia/lor4pU9vYO7vr4AcRJrlpC20jfrFWEPBA=="]}});
function wag316Packet(kind,seq){
 const authority=kind==='status'?'status-Q':'clock-T';
 const body=kind==='status'?
  {v:316,authority,epoch:316,seq,key:'fixture-D',state:'ACTIVE'}:
  {v:316,authority,epoch:316,seq,counter:120+seq,tick:1000+seq*10};
 return {body,publicKey:WAG316_FIXTURES[kind].key,
  signature:WAG316_FIXTURES[kind].signatures[seq],
  roots:kind==='status'?['fixture-Q']:['fixture-T']};
}
function wag316Fixture(scenario,seq){
 const status=wag316Packet('status',seq),clock=wag316Packet('clock',seq);
 if(scenario==='status-missing')status.signature='';
 if(scenario==='clock-missing')clock.signature='';
 if(scenario==='status-tamper')status.body.state='REVOKED';
 if(scenario==='clock-tamper')clock.body.counter+=1;
 if(scenario==='swapped-key')clock.publicKey=status.publicKey;
 if(scenario==='shared-root')clock.roots=['fixture-Q'];
 if(scenario==='replayed-counter'){
  clock.body=wag316Packet('clock',(seq+7)%8).body;clock.signature=wag316Packet('clock',(seq+7)%8).signature;
 }
 if(scenario==='counter-ahead')clock.body.counter+=4;
 if(scenario==='reported-revocation')status.body.state='REVOKED';
 return {status,clock};
}
function wag316Bytes(s){return Uint8Array.from(atob(s),c=>c.charCodeAt(0))}
async function wag316Verify(packet,kind,seq){
 const pin=WAG316_FIXTURES[kind].key;
 const authority=kind==='status'?'status-Q':'clock-T';
 const context=packet.body.v===316&&packet.body.authority===authority&&
  packet.body.epoch===316&&packet.body.seq===seq&&
  (kind==='status'?(packet.body.key==='fixture-D'&&packet.body.state==='ACTIVE'):
    packet.body.counter===120+seq&&packet.body.tick===1000+seq*10);
 const pinMatches=packet.publicKey===pin;
 let signatureValid=false;
 try{
  const key=await crypto.subtle.importKey('raw',wag316Bytes(pin),{name:'Ed25519'},false,['verify']);
  signatureValid=await crypto.subtle.verify('Ed25519',key,wag316Bytes(packet.signature),
   new TextEncoder().encode(JSON.stringify(packet.body)));
 }catch(e){signatureValid=false}
 return Object.freeze({kind,context,pinMatches,signatureValid,
  valid:context&&pinMatches&&signatureValid});
}
async function wag316Trial(scenario,seq){
 const fixture=wag316Fixture(scenario,seq),[status,clock]=await Promise.all([
  wag316Verify(fixture.status,'status',seq),wag316Verify(fixture.clock,'clock',seq)]);
 const roots=fixture.status.roots.concat(fixture.clock.roots);
 const distinct=fixture.status.roots.every(r=>!fixture.clock.roots.includes(r))&&
  !roots.some(r=>['fixture-A','fixture-B','fixture-C','fixture-D'].includes(r));
 const correlated=['unreported-compromise','correlated-false-reference'].includes(scenario);
 const reference=await wag313Trial(correlated?'correlated-signed-false':'clean',seq);
 const valid=status.valid&&clock.valid&&distinct&&reference.reference.valid&&reference.observedSigned;
 const candidate=valid&&reference.candidate!==null?reference.candidate:null;
 return Object.freeze({scenario,seq,status,clock,distinct,
  referenceSignatureOK:reference.reference.signatureOK,
  candidate,target:correlated?4:3,
  verdict:!status.valid?'STATUS_ATTESTATION_REJECTED':
   !clock.valid?'CLOCK_ATTESTATION_REJECTED':
   !distinct?'SHARED_ATTESTATION_ANCESTRY':
   !reference.reference.valid?'REFERENCE_REJECTED':
   candidate===null?'ABSTAIN':'SYNTHETIC_ATTESTATIONS_ACCEPTED',
  trueExternalIdentityVerified:false,trueClockAttested:false,
  promotionAuthorized:false});
}
async function wag316Evaluate(state){
 const baseline=JSON.stringify(state),rows=[];
 for(const scenario of WAG316.cases){
  let correct=0,wrong=0,abstain=0,attestationRejected=0;
  for(let seq=0;seq<8;seq++){
   const x=await wag316Trial(scenario,seq);
   if(!x.status.valid||!x.clock.valid||!x.distinct)attestationRejected++;
   if(x.candidate===null)abstain++;
   else if(x.candidate===x.target)correct++;else wrong++;
  }
  rows.push({scenario,correct,wrong,abstain,attestationRejected,total:8});
 }
 if(JSON.stringify(state)!==baseline)throw Error('authoritative state changed');
 return wag291DeepFreeze({bound:'WAG-316',phase:'VII',turn:5,rows,total:96,
  signedAuthorityRecords:16,externalRootAttestation:false,
  clockHardwareAttestation:false,controllerPromoted:false,physicalActions:0,
  limitation:'Valid Ed25519 signatures authenticate only test-fixture public keys. Independently named fixtures and coherent false assertions can still deceive.'});
}
async function wag316Audit(){
 const s=wag288Initial(),snapshot=JSON.stringify(s),
 a=await wag316Evaluate(s),b=await wag316Evaluate(s),get=k=>a.rows.find(x=>x.scenario===k);
 const checks={
  deterministic:JSON.stringify(a)===JSON.stringify(b),
  unchanged:JSON.stringify(s)===snapshot,
  twelveScenarios:a.rows.length===12&&a.total===96,
  accounting:a.rows.every(x=>x.correct+x.wrong+x.abstain===8),
  distinctKeys:WAG316_FIXTURES.status.key!==WAG316_FIXTURES.clock.key,
  sixteenSignedRecords:WAG316_FIXTURES.status.signatures.length===8&&WAG316_FIXTURES.clock.signatures.length===8,
  cleanCorrect:get('clean').correct===8,
  missingStatusRejected:get('status-missing').abstain===8,
  missingClockRejected:get('clock-missing').abstain===8,
  tamperedStatusRejected:get('status-tamper').abstain===8,
  tamperedClockRejected:get('clock-tamper').abstain===8,
  substitutedKeyRejected:get('swapped-key').abstain===8,
  sharedRootRejected:get('shared-root').abstain===8,
  replayRejected:get('replayed-counter').abstain===8,
  futureCounterRejected:get('counter-ahead').abstain===8,
  reportedRevocationRejected:get('reported-revocation').abstain===8,
  undisclosedCompromiseRetained:get('unreported-compromise').wrong===8,
  correlatedFalseRetained:get('correlated-false-reference').wrong===8,
  validSignatureBaseline:(await wag316Trial('clean',0)).status.signatureValid&&(await wag316Trial('clean',0)).clock.signatureValid,
  noPrivateKeys:!WAG316_FIXTURES.status.privateKey&&!WAG316_FIXTURES.clock.privateKey,
  sourceNotAuthenticated:!a.externalRootAttestation&&!a.clockHardwareAttestation,
  noPromotion:!a.controllerPromoted&&a.physicalActions===0,
  frozen:Object.isFrozen(a)&&Object.isFrozen(a.rows[0]),
  privateFormsPreserved:WAG304.forms.join('|')==='[1]|{1}|(1)'
 };
 return {bound:'WAG-316',pass:Object.values(checks).every(Boolean),checks,rows:a.rows,progress:5/8};
}
if(typeof module!=='undefined')module.exports={WAG316,WAG316_FIXTURES,wag316Packet,wag316Fixture,wag316Verify,wag316Trial,wag316Evaluate,wag316Audit};
