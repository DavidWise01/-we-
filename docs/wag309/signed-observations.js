/* WAG-309 · Phase VI 6/8 · Ed25519-signed observation binding · .dlw
 * 24 pre-signed synthetic packets = 3 signer keys x 8 sequences.
 * No private keys in repo. This is test evidence, not external identity.
 * Signatures bind version, origin, leaf, epoch, sequence, channel and vector.
 * Observers [1], {1}, (1) see only their private vector-based view.
 * Expected sequence and epoch are supplied by an external read-only gate.
 * A valid signature does not establish underlying observation truth.
 */
const WAG309=Object.freeze({phase:'VI',turn:6,of:8,epoch:309,steps:8,
 scenarios:Object.freeze(['clean','vector-tamper','sequence-replay','epoch-replay',
 'signature-swap','key-substitution','root-relabel','missing-signature','signed-false-observation']),
 physicalActions:0});
const WAG309_PUBLIC_KEYS=Object.freeze(["vVHJ9b/If7WLmqA3lMhWhBeFnC+ryPB7lYvWheb9ikw=","YwyIbbszPsIoyJhtOMAtbeuKyfOj5/uS7j/1rzT1paE=","XaS6E3YVFSu598eq+SAWwEQBJ7BVcyHbe4QREvgEPgo="]);
const WAG309_SIGNATURES=Object.freeze([["4M4HozxIwNVkfudQP1668JdTarv2iGDZzpDZ8/3e9GKRPlK+qvSJ5hcm2d3lztrAmksP/uvUuqNFsxJy1cAWBQ==","UUDyRvjVXWOJ8JXf4oNtQTiEeCGAkOKP99eI3PzympN+5uXI1fA2yqRlsqkC4fgISmatpr5qGrVBKn0CHJhyBQ==","NpwJj+U5G+mLHBH0ev7v7mNa60XjsgkkwXj+nM7ohkAw4JGjCdhhl/r+ZNpJ5dJ9C7B8i66H6NxgkvlNvXFHDw=="],["JtL+2cOfdO07Kkvls8HM6/eNRo2+l48X8htJxZrLjBWuJal6Mj3KAQrbsbjw2EaLDyuffiZ5K/btK1xClUKXBw==","HDZ+jdvsySRPcVpkAf7JYEeJ5L+6Ux9iruKOvZWSqkqSOlHXrf8I/Sw/e60HA8Oq5HWIzzSFCOPZKNNOpSPSCA==","5Nn55foZQKv9eGpAQ98AtQR7B88W+IcwcUScDHfmzC4fOul2/dQW86cIeNBcvf/4Bm4s9aiZa3uzH84xWfpHBw=="],["Zoc/kV28EGsRDn/7nl2CQ0XAFiIog1ML1QNV4a2ZlUjP/e1n5OEuDbFyIsjjqBThia3SNNPEeVjx2H39q9E8Bw==","7d41mlPzMQqGiFNoZsQKvovh5lJk3ob9B6xTbk6JJkvpUGR07Fgtd4Nl5Ou0fYsLsQnQkarmXTnsiOJQhOjHDQ==","W4mqa1904Tai7lawv/25XQ7cjMtE3zaT0zsoiPKlUclH7WftakYQQH1Hdow4+17j9Vm76Wc68z/hfP1PEqtEBA=="],["CZrHweU/gqP2pkMarjCCpbPzddF7Bg9S49ywEmHMcT8a2Yod92Trq/D9TMgqk2RaGovp7HMs2wZJPLyPcgYoCg==","9+w5e7gp4Uh+wEftr6Nh4jlfbJQBGsW4hbawkJuOaRAinQhi+gwext6TBuTRAmPCe/EI25linrq26qqSkFvgAg==","zoOk072UkHT7GmLeYKLpZatLJPFpRvohpDSNCMOzClNAqfEpRRF3wVriMv/Cwq1Yxt07Hr6SC2wCrkfozHh2Cw=="],["NI87ePiqfy08taHur4QXYAgw1cF11fZItoMscM1xFn8UTgVRvlgJUpca+YCNA3+Hh+EoOeUVFFH0c7IU+ynLAw==","MG19HuOA2mniSQTre8ghkXjlyJTV6DYA7i9IS2ZoBtq2yVsJvTAhV3VTelCYOMnkRRytSrh2/xBijutFzmt7DQ==","gzc6k3mnlGkf1M/nefylFC+BcjpqAWNAa20PvQ5L+vvdAkFeJYsvxPGwbG2BQ9DVYC1WeoVjS1MHJnFJOXflDw=="],["BwkwUSGXHNzd7rc4iWTAgzU0YYdnAVJ7HiN9I3RWuVBBgSlqiMmSfxV0WYJoHXLpVqPlM8zHWCVqEVHQY5/2BQ==","3PVn0VhHtA6pZDc3RCbf5jJzT6BNI/tbaoxMe4dDBY/JEZUkcS1j3tjY5BssfgRD/A7jzRmJrQGfJ9Ck4u9CDQ==","uAdajEGTb4HKLfsgFPF/oTntD4lOC6qGYyXHQEv40U5y/heQHl1QctET23wKIUBKVWCblp4WfIw5mccjwnEvDA=="],["+SiQ9xwcZNHFx3oXGz2l/rRrIHOtzEV5VVQVN97qGxSUgIUiyJWDFFh4q00ma8MZnfixC0BB7GfeLM19q7RUCA==","2qe+BPt8IquG5CoZUJitgEyERA5JF+r6WqktbnsafW0iemHX6YkM74+yO6FBOzeLwEWO+bFXJOO8XYlNfCtIAw==","5C/DDyRfInU3drVTBu7H3i/pL6RlvJkgM8wnGu5RYMTUscmLkN+WryO4fwndB2LQ3+YH0c1paLYok8/zTPKjDQ=="],["+DO1XC13E1/7bgrSrZcKW2A0xZDXOUSTETSk6c6ApygUr+8Myz9JnxwDioWWfEuS1fHiWWH+cS/rPHUHLoT4CQ==","4vIvA+dHO6EGoK7F+EfGSueiHDKoNo3wVMDGSkTTqazEJt5mmKroM7CZqOSeLyqrew2lCLFJEMejThPN0GvyAw==","elm2jASLtevhqFQH0M7ToMWLav5keYXLfyVZv1UQpCxn/saXPJLVzoUFx2YTE7TMp2jERoe6JpL6W7y3+ZZjBQ=="]]);

function wag309Packet(seq,signer){
 return {version:309,origin:'root-'+String.fromCharCode(65+signer),
  leaf:'leaf-'+String.fromCharCode(65+signer),epoch:309,seq,channel:3,
  vector:Array.from({length:8},(_,i)=>i===3?.9:.1)};
}
function wag309TestCase(scenario,seq){
 const packets=Array.from({length:3},(_,i)=>({body:wag309Packet(seq,i),signature:WAG309_SIGNATURES[seq][i],key:WAG309_PUBLIC_KEYS[i]}));
 if(scenario==='vector-tamper')packets[1].body.vector[3]=.01;
 if(scenario==='sequence-replay')for(let i=0;i<3;i++){packets[i].body=wag309Packet(0,i);packets[i].signature=WAG309_SIGNATURES[0][i];}
 if(scenario==='signature-swap')packets[1].signature=WAG309_SIGNATURES[seq][0];
 if(scenario==='key-substitution')packets[1].key=WAG309_PUBLIC_KEYS[0];
 if(scenario==='root-relabel')packets[1].body.origin='root-A';
 if(scenario==='missing-signature')packets[2].signature='';
 return packets;
}
function wag309DecodeBase64(s){return Uint8Array.from(atob(s),c=>c.charCodeAt(0))}
async function wag309VerifyPacket(packet,signer,expectedSeq,expectedEpoch=309){
 const body=packet.body;
 const expectedOrigin='root-'+String.fromCharCode(65+signer);
 const pinnedKey=WAG309_PUBLIC_KEYS[signer];
 const context=body.version===309&&body.origin===expectedOrigin&&body.leaf==='leaf-'+String.fromCharCode(65+signer)&&
  body.epoch===expectedEpoch&&body.seq===expectedSeq&&body.channel>=0&&body.channel<8&&
  Array.isArray(body.vector)&&body.vector.length===8&&body.vector.every(x=>Number.isFinite(x)&&x>=0&&x<=1);
 const pinMatch=packet.key===pinnedKey;
 let signatureOK=false;
 try{
  if(typeof crypto==='undefined'||!crypto.subtle)throw Error('WebCrypto unavailable');
  const key=await crypto.subtle.importKey('raw',wag309DecodeBase64(pinnedKey),{name:'Ed25519'},false,['verify']);
  signatureOK=await crypto.subtle.verify('Ed25519',key,wag309DecodeBase64(packet.signature),
   new TextEncoder().encode(JSON.stringify(body)));
 }catch(e){signatureOK=false}
 return {context,pinMatch,signatureOK,accepted:context&&pinMatch&&signatureOK};
}
function wag309PrivateClaim(form,vector){
 // Neither the signature nor provenance metadata is passed to the interpreter.
 const center=vector.slice(),cortex=Array.from({length:26},()=>vector.slice());
 return wag304Isolated(form,{center,cortex});
}
async function wag309Trial(scenario,seq){
 const packets=wag309TestCase(scenario,seq);
 const expectedEpoch=scenario==='epoch-replay'?310:309;
 const checks=await Promise.all(packets.map((p,i)=>wag309VerifyPacket(p,i,
   scenario==='sequence-replay'?seq+8:seq,expectedEpoch)));
 const trusted=checks.every(x=>x.accepted);
 const claims=packets.map((p,i)=>wag309PrivateClaim(WAG304.forms[i],p.body.vector));
 const unanimous=claims.every(c=>!c.uncertain&&c.channel===claims[0].channel);
 const candidate=trusted&&unanimous?claims[0].channel:null;
 const syntheticGroundTruth=scenario==='signed-false-observation'?4:3;
 return {scenario,seq,checks,claims,unanimous,trusted,candidate,syntheticGroundTruth,
  verdict:!trusted?'SIGNED_CONTEXT_REJECTED':!unanimous?'PRIVATE_CONFLICT':'SIGNED_PACKET_CANDIDATE',
  promotionAuthorized:false};
}
async function wag309Evaluate(source){
 const before=JSON.stringify(source),rows=[];
 for(const scenario of WAG309.scenarios){
  let correct=0,wrong=0,abstain=0,signatureFailures=0,contextFailures=0;
  for(let seq=0;seq<8;seq++){
   const r=await wag309Trial(scenario,seq);
   if(r.checks.some(c=>!c.signatureOK))signatureFailures++;
   if(r.checks.some(c=>!c.context||!c.pinMatch))contextFailures++;
   if(r.candidate===null)abstain++;else if(r.candidate===r.syntheticGroundTruth)correct++;else wrong++;
  }
  rows.push({scenario,correct,wrong,abstain,signatureFailures,contextFailures,total:8});
 }
 if(JSON.stringify(source)!==before)throw Error('authoritative state mutated');
 return wag291DeepFreeze({bound:'WAG-309',turn:6,phase:'VI',rows,
  signedPackets:24,scenarios:WAG309.scenarios.length,tests:72,
  actualCryptographicVerification:true,realWorldOriginAuthenticated:false,
  observationsTruthVerified:false,promotionAuthorized:false,physicalActions:0,
  caveat:'Fixture public keys verify real Ed25519 signatures, but no external identity or truth attestation. Signed false observations remain possible.'});
}
async function wag309Audit(){
 const s=wag288Initial(),before=JSON.stringify(s),a=await wag309Evaluate(s),b=await wag309Evaluate(s);
 const by=k=>a.rows.find(r=>r.scenario===k);
 const checks={
  cryptoApiAvailable:typeof crypto!=='undefined'&&!!crypto.subtle,
  deterministic:JSON.stringify(a)===JSON.stringify(b),
  authoritativeStateUnchanged:JSON.stringify(s)===before,
  threeDistinctPins:new Set(WAG309_PUBLIC_KEYS).size===3,
  twentyFourSignatures:WAG309_SIGNATURES.length===8&&WAG309_SIGNATURES.every(v=>v.length===3),
  noPrivateKeysEmbedded:WAG309_PUBLIC_KEYS.every(k=>k.length===44),
  allCleanValid:by('clean').correct===8,
  vectorTamperRejected:by('vector-tamper').abstain===8&&by('vector-tamper').signatureFailures===8,
  replayRejected:by('sequence-replay').abstain===8&&by('sequence-replay').contextFailures===8,
  wrongEpochRejected:by('epoch-replay').abstain===8&&by('epoch-replay').contextFailures===8,
  swappedSignatureRejected:by('signature-swap').abstain===8,
  substitutedKeyRejected:by('key-substitution').abstain===8,
  rootRelabelRejected:by('root-relabel').abstain===8,
  missingSignatureRejected:by('missing-signature').abstain===8,
  signedFalseTruthExposed:by('signed-false-observation').wrong===8,
  recordsAccounted:a.rows.every(r=>r.correct+r.wrong+r.abstain===8),
  immutable:Object.isFrozen(a)&&Object.isFrozen(a.rows[0]),
  noTruthClaims:!a.realWorldOriginAuthenticated&&!a.observationsTruthVerified,
  noPromotion:a.promotionAuthorized===false&&a.physicalActions===0
 };
 return {bound:'WAG-309',pass:Object.values(checks).every(Boolean),checks,rows:a.rows,phaseProgress:.75};
}
if(typeof module!=='undefined')module.exports={WAG309,WAG309_PUBLIC_KEYS,WAG309_SIGNATURES,wag309Packet,wag309Trial,wag309Evaluate,wag309Audit};
