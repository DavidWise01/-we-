// WAG-223: packet integrity, signer authorization, acquisition lineage (.dlw)
// Demo keys are PUBLIC. HMAC in this fixture does not authenticate real sensors.
function sha256(s){
 const ro=(x,n)=>(x>>>n)|(x<<(32-n)),K=[0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2];
 const b=Array.from(s,c=>c.charCodeAt(0));if(b.some(x=>x>255))throw Error('binary chars only');
 const bits=b.length*8;b.push(128);while(b.length%64!==56)b.push(0);
 for(const word of [Math.floor(bits/4294967296),bits>>>0])for(let j=3;j>=0;j--)b.push((word>>>(8*j))&255);
 let H=[0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19];
 for(let offset=0;offset<b.length;offset+=64){let W=Array(64);
  for(let i=0;i<16;i++)W[i]=(b[offset+4*i]<<24)|(b[offset+4*i+1]<<16)|(b[offset+4*i+2]<<8)|b[offset+4*i+3];
  for(let i=16;i<64;i++){let a=W[i-15],z=W[i-2];W[i]=(W[i-16]+(ro(a,7)^ro(a,18)^(a>>>3))+W[i-7]+(ro(z,17)^ro(z,19)^(z>>>10)))|0}
  let [a,z,c,d,e,f,g,h]=H;
  for(let i=0;i<64;i++){const x=(h+(ro(e,6)^ro(e,11)^ro(e,25))+((e&f)^(~e&g))+K[i]+W[i])|0,y=((ro(a,2)^ro(a,13)^ro(a,22))+((a&z)^(a&c)^(z&c)))|0;h=g;g=f;f=e;e=(d+x)|0;d=c;c=z;z=a;a=(x+y)|0}
  H=H.map((v,i)=>(v+[a,z,c,d,e,f,g,h][i])|0);
 }
 return H.map(x=>(x>>>0).toString(16).padStart(8,'0')).join('');
}
function hmac256(key,msg){const bytes=s=>Array.from(s,c=>c.charCodeAt(0)),str=a=>String.fromCharCode(...a);let k=bytes(key);
 if(k.length>64){let z=sha256(key);k=Array.from({length:32},(_,i)=>parseInt(z.slice(i*2,i*2+2),16))}
 while(k.length<64)k.push(0);
 const inner=sha256(str(k.map(x=>x^54))+msg),raw=Array.from({length:32},(_,i)=>parseInt(inner.slice(i*2,i*2+2),16));
 return sha256(str(k.map(x=>x^92))+str(raw));
}
const TRUST223={a:'fixture-key-a',b:'fixture-key-b'},CASES223=['independent','shared','payload_tamper','ancestry_tamper','unknown_signer','bad_mac','old_epoch','missing_packet','unknown_root','authorized_collusion'];
function packet223(signer,channel,root,p,epoch=5){const payload={channel,root,epoch,events:Array.from({length:64},(_,i)=>Number(i%p===3))},digest=sha256(JSON.stringify(payload));return {signer,payload,digest,mac:hmac256(TRUST223[signer]||'rogue',digest)}}
function fixture223(kind,p,seed){
 const A=packet223('a','A','rootA',p);let B=packet223('b','B','rootB',p);
 let trueRoots=['rootA','rootB'];
 if(kind==='shared'){B=packet223('b','B','rootA',p);trueRoots[1]='rootA'}
 if(kind==='payload_tamper')B.payload.events[8]^=1;
 if(kind==='ancestry_tamper')B.payload.root='rootA';
 if(kind==='unknown_signer')B=packet223('rogue','B','rootB',p);
 if(kind==='bad_mac')B.mac='0'.repeat(64);
 if(kind==='old_epoch')B=packet223('b','B','rootB',p,4);
 if(kind==='missing_packet')B=null;
 if(kind==='unknown_root')B=packet223('b','B','UNKNOWN',p);
 if(kind==='authorized_collusion')trueRoots[1]='rootA';
 return {kind,p,seed,A,B,trueRoots};
}
function check223(packet){if(!packet)return {ok:false,errors:['MISSING_PACKET']};
 const e=[],key=TRUST223[packet.signer];if(!key)e.push('UNAUTHORIZED_SIGNER');
 if(sha256(JSON.stringify(packet.payload))!==packet.digest)e.push('DIGEST_CHANGED');
 if(key&&hmac256(key,packet.digest)!==packet.mac)e.push('MAC_INVALID');
 if(packet.payload.epoch!==5)e.push('STALE_EPOCH');
 if(!packet.payload.root||packet.payload.root==='UNKNOWN')e.push('ROOT_UNKNOWN');
 return {ok:e.length===0,errors:e};
}
function assess223(f){const a=check223(f.A),b=check223(f.B);if(!a.ok||!b.ok)return {status:'QUARANTINE',A:a,B:b};
 if(f.A.payload.root===f.B.payload.root)return {status:'SHARED_ROOT',A:a,B:b};
 return {status:f.A.payload.events.every((v,i)=>v===f.B.payload.events[i])?'INDEPENDENT_AGREEMENT':'DISAGREEMENT',A:a,B:b};
}
function experiment223(){
 if(sha256('abc')!=='ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad')throw Error('SHA-256 test vector failed');
 if(hmac256('key','The quick brown fox jumps over the lazy dog')!=='f7bc83f430538424b13298e6aa6fb143ef4d59a14946175997479dbc2d1a3cd8')throw Error('HMAC test vector failed');
 let cases=0,collusionAccepted=0;const rows=[],samples=[];
 for(const kind of CASES223){let pass=0,incorrect=0,quarantine=0,shared=0,independent=0;
  for(const p of [9,13,17,23])for(let seed=223;seed<231;seed++){
   const f=fixture223(kind,p,seed),r=assess223(f),expected=kind==='shared'?'SHARED_ROOT':kind==='independent'||kind==='authorized_collusion'?'INDEPENDENT_AGREEMENT':'QUARANTINE';
   cases++;pass+=Number(r.status===expected);incorrect+=Number(r.status!==expected);quarantine+=Number(r.status==='QUARANTINE');shared+=Number(r.status==='SHARED_ROOT');independent+=Number(r.status==='INDEPENDENT_AGREEMENT');
   if(kind==='authorized_collusion'&&r.status==='INDEPENDENT_AGREEMENT'&&f.trueRoots[0]===f.trueRoots[1])collusionAccepted++;
   if(p===9&&seed===223)samples.push({kind,expected,assessment:r,fixture:f});
  }
  rows.push({kind,runs:32,pass,incorrect,quarantine,shared,independent});
 }
 return {cases,collusionAccepted,knownAnswerTests:2,rows,samples};
}
if(typeof module!=='undefined')module.exports={sha256,hmac256,packet223,fixture223,check223,assess223,experiment223};
if(typeof require!=='undefined'&&require.main===module)console.log(JSON.stringify(experiment223(),null,2));
