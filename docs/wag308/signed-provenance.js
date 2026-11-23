/* WAG-308 · Phase VI 5/8 · Signed provenance and pinned keys · .dlw
 * Real Ed25519 verification via WebCrypto; browsers must support Ed25519.
 * Three independent test-fixture signer keys, public keys pinned in source.
 * Only fixed producer/ancestry declarations are signed: observation vectors
 * are NOT signed and NOT authenticated. A false observation can still pass.
 * Source identity is authenticated ONLY as possession of fixture key.
 * Public keys/signatures are public; private signing keys are NOT shipped.
 * The three [1], {1}, (1) agents get private inputs, never peer records.
*/
const WAG308=Object.freeze({phase:'VI',turn:5,of:8,physicalActions:0,
 cases:Object.freeze(['clean','alias-only','record-tamper','swapped-signature',
 'substituted-key','mutable-key-replaced','signed-false-data','all-corrupt']),
 fixtures:Object.freeze([
  Object.freeze({message:'{"v":308,"source":"root-A","leaf":"leaf-A","parent":"root-A"}',publicKey:'PUpIFwpOY7rQ7zpY4Vdan14n8Y8M2mMsvuyY/YExW3s=',signature:'GaMaOGEe+R8i9MyZe8OykZG69oVFMtNPPFEx2pP0c2gZXjC4EIrrB/LJtWfXu5QvU8wdiuwow91udwa9BGZ9Bw=='}),
  Object.freeze({message:'{"v":308,"source":"root-B","leaf":"leaf-B","parent":"root-B"}',publicKey:'tY0lmoZZPKmaO8oiM4huC4cWLEGe2OBF5JoFXtRqMbE=',signature:'NgE/24AnPz89Od9mP4bIMQOhHM0ZIuVmSD1j8ZEll4STMgxA1u4cuSiEfsNmFnpwP2UiN4RLVVxnvsMDMFQIDg=='}),
  Object.freeze({message:'{"v":308,"source":"root-C","leaf":"leaf-C","parent":"root-C"}',publicKey:'gPmAG4WLF/LJZCc9qo1v3Uz5YRWy0PXtA2D72U+iE3Y=',signature:'2lfCI6WydR6EBlgL5cwQ+1xndlW+2Gs74Xhc6rn5qel9LWDHvtqSnfJlSVtfZGVsxNA7usKPYE4fpwLyAIodDw=='})
 ])});
function wag308DecodeB64(s){return Uint8Array.from(atob(s),c=>c.charCodeAt(0))}
function wag308Fixture(kind){
 const items=WAG308.fixtures.map(x=>({...x})),names=['alice','bob','carol'];
 if(kind==='alias-only')names.splice(0,3,'renamed-A','renamed-B','renamed-C');
 if(kind==='record-tamper')items[1].message=items[1].message.replace('"root-B"','"root-A"');
 if(kind==='swapped-signature')items[1].signature=items[0].signature;
 if(kind==='substituted-key')items[1].publicKey=items[0].publicKey;
 if(kind==='mutable-key-replaced')items[1].publicKey=items[0].publicKey;
 return {items,names};
}
async function wag308VerifyFixture(kind){
 const fx=wag308Fixture(kind),cryptoApi=typeof crypto!=='undefined'?crypto.subtle:null;
 if(!cryptoApi)return {kind,status:'CRYPTO_UNAVAILABLE',valid:false,checks:[],identityVerified:false};
 const checks=[];
 for(let i=0;i<fx.items.length;i++){
  const item=fx.items[i],pin=WAG308.fixtures[i],mutablePin=item.publicKey;
  try{
   // Always use source-pinned public key, not mutable record key.
   const key=await cryptoApi.importKey('raw',wag308DecodeB64(pin.publicKey),{name:'Ed25519'},false,['verify']);
   const signatureOK=await cryptoApi.verify('Ed25519',key,wag308DecodeB64(item.signature),new TextEncoder().encode(item.message));
   const pinMatch=mutablePin===pin.publicKey;
   const body=JSON.parse(item.message);
   const correctIdentity=body.v===308&&body.source==='root-'+String.fromCharCode(65+i)&&
    body.leaf==='leaf-'+String.fromCharCode(65+i)&&body.parent===body.source;
   checks.push({signer:i,signatureOK,pinMatch,correctIdentity});
  }catch(e){checks.push({signer:i,signatureOK:false,pinMatch:false,correctIdentity:false,error:String(e)});}
 }
 const valid=checks.length===3&&checks.every(x=>x.signatureOK&&x.pinMatch&&x.correctIdentity);
 return {kind,valid,checks,status:valid?'SIGNED_FIXTURE_ACCEPTED':'SIGNATURE_OR_PIN_REJECTED',
  identityVerified:valid,realWorldOriginVerified:false,
  observationAuthenticated:false,promotionAuthorized:false};
}
async function wag308Evaluate(authority){
 const snapshot=JSON.stringify(authority),rows=[];
 for(const kind of WAG308.cases){
  const verified=await wag308VerifyFixture(kind);
  let correct=0,wrong=0,abstain=0;
  // 64 observational trials, but only 3 fixed SIGNED PROVENANCE fixtures per scenario.
  for(let label=0;label<8;label++)for(let trial=0;trial<8;trial++){
   const bad=kind==='signed-false-data'||kind==='all-corrupt';
   const claims=WAG304.forms.map((form,i)=>wag304Isolated(form,wag304SourceView(label,trial,bad)));
   const agree=claims.every(x=>!x.uncertain&&x.channel===claims[0].channel);
   const answer=verified.valid&&agree?claims[0].channel:null;
   if(answer===null)abstain++;else if(answer===label)correct++;else wrong++;
  }
  rows.push({kind,correct,wrong,abstain,signatureAccepted:verified.valid,
   status:verified.status,checks:verified.checks,total:64});
 }
 if(JSON.stringify(authority)!==snapshot)throw Error('source mutated');
 return wag291DeepFreeze({bound:'WAG-308',phase:'VI',turn:5,rows,
  trials:512,signedFixtureRecords:3,realWorldOriginAuthenticated:false,
  observationVectorsSigned:false,accepted:false,authority:'READ_ONLY',physicalActions:0,
  limitation:'Three test keys authenticate only fixed ancestry declarations; compromised signer or independently false data can still pass.'});
}
async function wag308Audit(){
 const s=wag288Initial(),prior=JSON.stringify(s),a=await wag308Evaluate(s),
 b=await wag308Evaluate(s),get=k=>a.rows.find(x=>x.kind===k);
 const known=await wag308VerifyFixture('clean');
 const checks={
  cryptoAvailable:known.status!=='CRYPTO_UNAVAILABLE',
  actualEd25519:known.valid&&known.checks.every(x=>x.signatureOK),
  deterministic:JSON.stringify(a)===JSON.stringify(b),
  sourceUnchanged:JSON.stringify(s)===prior,
  count:a.rows.length===8&&a.trials===512,
  accounting:a.rows.every(x=>x.correct+x.wrong+x.abstain===64),
  cleanCorrect:get('clean').correct===64,
  aliasesPreserved:get('alias-only').correct===64,
  tamperDetected:get('record-tamper').abstain===64,
  swappedSignatureRejected:get('swapped-signature').abstain===64,
  differentKeyRejected:get('substituted-key').abstain===64,
  mutablePinRejected:get('mutable-key-replaced').abstain===64,
  signedFalseDataExposed:get('signed-false-data').wrong===64,
  coordinatedWrongExposed:get('all-corrupt').wrong===64,
  keyMaterialNotEmbedded:WAG308.fixtures.every(x=>!('privateKey' in x)),
  noTruthClaim:a.realWorldOriginAuthenticated===false&&!a.observationVectorsSigned,
  frozen:Object.isFrozen(a)&&Object.isFrozen(a.rows[0]),
  previousPass:wag307Audit().pass,
  noActuation:a.physicalActions===0
 };
 return {bound:'WAG-308',checks,pass:Object.values(checks).every(Boolean),
  rows:a.rows,phaseProgress:5/8};
}
if(typeof module!=='undefined')module.exports={WAG308,wag308DecodeB64,wag308Fixture,wag308VerifyFixture,wag308Evaluate,wag308Audit};
