/* WAG-307 · Phase VI 4/8 · SHA-256 pinned record integrity · .dlw
 * The trust anchor is a hard-coded independent baseline SHA-256 digest.
 * It is detached from mutable fixture manifests, but is public, unsigned
 * and unauthenticated. SHA-256 provides collision-resistant integrity
 * comparison; no digital signature, identity, or truthful origin proof.
 * Three blind interpreters never see ancestry or other claims.
 */
const WAG307=Object.freeze({phase:'VI',turn:4,of:8,
 pinnedSha256:'b7b673a5e44828c057e766be3fc0cfa809c046a11b9edfda529dde261971b3a3',
 cases:Object.freeze(['clean','alias-only','parent-tamper','forged-rehash',
   'mutable-pin-replaced','missing-leaf','all-corrupt','coordinated-forgery']),
 physicalActions:0});
function wag307Sha256(input){
 const bytes=[];
 for(let i=0;i<input.length;i++){
  const cp=input.codePointAt(i);if(cp>65535)i++;
  if(cp<128)bytes.push(cp);
  else if(cp<2048)bytes.push(192|(cp>>6),128|(cp&63));
  else if(cp<65536)bytes.push(224|(cp>>12),128|((cp>>6)&63),128|(cp&63));
  else bytes.push(240|(cp>>18),128|((cp>>12)&63),128|((cp>>6)&63),128|(cp&63));
 }
 const bitLen=bytes.length*8;bytes.push(128);while(bytes.length%64!==56)bytes.push(0);
 const high=Math.floor(bitLen/4294967296),low=bitLen>>>0;
 for(const n of [high,low])for(let j=3;j>=0;j--)bytes.push((n>>>(8*j))&255);
 const K=[0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
 0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
 0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
 0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
 0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
 0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
 0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
 0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2];
 const H=[0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19];
 const ro=(x,n)=>(x>>>n)|(x<<(32-n));
 for(let offset=0;offset<bytes.length;offset+=64){
  const w=new Array(64);
  for(let i=0;i<16;i++){const j=offset+i*4;w[i]=((bytes[j]<<24)|(bytes[j+1]<<16)|(bytes[j+2]<<8)|bytes[j+3])>>>0;}
  for(let i=16;i<64;i++){const x=w[i-15],y=w[i-2];w[i]=(w[i-16]+(ro(x,7)^ro(x,18)^(x>>>3))+w[i-7]+(ro(y,17)^ro(y,19)^(y>>>10)))>>>0;}
  let [a,b,c,d,e,f,g,h]=H;
  for(let i=0;i<64;i++){
   const t1=(h+(ro(e,6)^ro(e,11)^ro(e,25))+((e&f)^(~e&g))+K[i]+w[i])>>>0;
   const t2=((ro(a,2)^ro(a,13)^ro(a,22))+((a&b)^(a&c)^(b&c)))>>>0;
   h=g;g=f;f=e;e=(d+t1)>>>0;d=c;c=b;b=a;a=(t1+t2)>>>0;
  }
  [a,b,c,d,e,f,g,h].forEach((v,i)=>H[i]=(H[i]+v)>>>0);
 }
 return H.map(n=>n.toString(16).padStart(8,'0')).join('');
}
function wag307Fixture(kind){
 const basic=wag306Fixture('clean'),graph=JSON.parse(JSON.stringify(basic.graph));
 const aliases=basic.aliases.slice(),leaves=basic.leaves.slice();
 if(kind==='alias-only')aliases.splice(0,3,'renamed-X','renamed-Y','renamed-Z');
 if(['parent-tamper','forged-rehash','mutable-pin-replaced','coordinated-forgery'].includes(kind))graph['leaf-B'].parents=['root-A'];
 if(kind==='missing-leaf')delete graph['leaf-C'];
 const actual=wag307Sha256(wag306Canonical(graph));
 let claimed=kind==='parent-tamper'?WAG307.pinnedSha256:actual;
 if(kind==='forged-rehash'||kind==='coordinated-forgery')claimed=actual;
 const mutablePin=kind==='mutable-pin-replaced'?actual:WAG307.pinnedSha256;
 return {graph,aliases,leaves,claimed,mutablePin,actual};
}
function wag307External(records,fixture){
 const digest=wag307Sha256(wag306Canonical(fixture.graph));
 const selfConsistent=digest===fixture.claimed;
 const anchored=digest===WAG307.pinnedSha256;
 const mutableRegistryMatch=digest===fixture.mutablePin;
 const ancestry=wag305External(records,fixture.graph);
 const allowed=selfConsistent&&anchored&&ancestry.candidate!==null;
 return Object.freeze({
  candidate:allowed?ancestry.candidate:null,
  verdict:!selfConsistent?'CLAIM_DIGEST_MISMATCH':!anchored?'DETACHED_PIN_MISMATCH':
   ancestry.verdict,
  selfConsistent,anchored,mutableRegistryMatch,traceError:ancestry.traceError,
  collision:ancestry.sharedRootCollision,declaredOriginsDistinct:ancestry.distinctRoots,
  sha256:digest,detachedPin:WAG307.pinnedSha256,claimedDigest:fixture.claimed,
  cryptographicDigest:true,digitalSignatureVerified:false,
  originAuthenticated:false,truthVerified:false,promotionAuthorized:false
 });
}
function wag307Trial(label,trial,kind){
 const fixture=wag307Fixture(kind),records=fixture.leaves.map((leaf,i)=>Object.freeze({
  form:WAG304.forms[i],leaf,displayName:fixture.aliases[i],
  claim:wag304Isolated(WAG304.forms[i],wag304SourceView(label,trial,kind==='all-corrupt'||kind==='coordinated-forgery'))
 }));
 return {fixture,records,result:wag307External(records,fixture)};
}
function wag307Evaluate(source){
 const original=JSON.stringify(source),rows=[];
 for(const kind of WAG307.cases){
  let correct=0,wrong=0,abstain=0,pinReject=0,mutablePinFalsePass=0;
  for(let label=0;label<8;label++)for(let trial=0;trial<8;trial++){
   const t=wag307Trial(label,trial,kind),r=t.result;
   if(!r.anchored)pinReject++;
   if(!r.anchored&&r.mutableRegistryMatch)mutablePinFalsePass++;
   if(r.candidate===null)abstain++;else if(r.candidate===label)correct++;else wrong++;
  }
  rows.push({kind,correct,wrong,abstain,pinReject,mutablePinFalsePass,total:64});
 }
 if(JSON.stringify(source)!==original)throw Error('authoritative silos modified');
 return wag291DeepFreeze({bound:'WAG-307',phase:'VI',turn:4,rows,samples:512,
  detachedPin:WAG307.pinnedSha256,actualAuthentication:false,
  authority:'READ_ONLY',physicalActions:0,
  caveat:'SHA-256 does not authenticate identity/truth; a replaced application anchor or altered verifier can pass'});
}
function wag307Audit(){
 const source=wag288Initial(),before=JSON.stringify(source),a=wag307Evaluate(source),b=wag307Evaluate(source);
 const get=x=>a.rows.find(v=>v.kind===x),comp=wag307Trial(3,0,'mutable-pin-replaced');
 const checks={
  sha256Empty:wag307Sha256('')==='e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
  sha256Abc:wag307Sha256('abc')==='ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad',
  pinnedClean:wag307Sha256(wag306Canonical(wag306Fixture('clean').graph))===WAG307.pinnedSha256,
  deterministic:JSON.stringify(a)===JSON.stringify(b),
  stateUnchanged:JSON.stringify(source)===before,
  eightScenarios:a.rows.length===8&&a.samples===512,
  accounts:a.rows.every(r=>r.correct+r.wrong+r.abstain===64),
  cleanCorrect:get('clean').correct===64,
  aliasUnchanged:get('alias-only').correct===64,
  parentTamperRejected:get('parent-tamper').abstain===64,
  forgedDigestRejected:get('forged-rehash').pinReject===64,
  mutableRegistryBypassed:comp.result.mutableRegistryMatch&&!comp.result.anchored,
  missingLeafRejected:get('missing-leaf').abstain===64,
  coordinatedFalseObserved:get('all-corrupt').wrong===64,
  noFalseOriginAuth:comp.result.originAuthenticated===false,
  noSignature:comp.result.digitalSignatureVerified===false,
  readOnlyForms:comp.records.every(r=>!('leaf' in r.claim)),
  priorStage:wag306Audit().pass,
  noActions:a.physicalActions===0
 };
 return {bound:'WAG-307',pass:Object.values(checks).every(Boolean),checks,
  results:a.rows,phaseProgress:.5};
}
if(typeof module!=='undefined')module.exports={WAG307,wag307Sha256,wag307Fixture,wag307External,wag307Trial,wag307Evaluate,wag307Audit};
