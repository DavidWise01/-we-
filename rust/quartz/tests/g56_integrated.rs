#![cfg(unix)]
use quartz_kernel::{authentication::Witness,mesh::mesh,journal::{Policy,Event},temporal::{Clock,TimedObservation},roster_binding::Binding,signed_evidence::{self,Evidence},custody::{self,Claim,Custody},filesystem,publication,cross_ledger,integrity::Hash};
use ed25519_dalek::{SigningKey,Signer};
use std::{fs,time::{SystemTime,UNIX_EPOCH}};
#[test]fn phase_vii_five_silos(){
 let keys:[SigningKey;3]=std::array::from_fn(|i|SigningKey::from_bytes(&[(i+1)as u8;32]));
 let members=std::array::from_fn(|i|Witness{key:keys[i].verifying_key().to_bytes(),root:[(i+1)as u8;32]});
 for policy in [Policy::FixedV1,Policy::RotatingV2]{
 for recipient in 0..5{
 for count in [1usize,2,3]{
 let a=mesh([100;3],policy);let owner=a[recipient].observation().source;let source=if recipient==4{0}else{4};
 let binding=Binding::genesis(owner,members).unwrap();
 let sign=|i:usize,b:&[u8]|keys.iter().find(|k|k.verifying_key().to_bytes()==binding.members()[i].key).unwrap().sign(b).to_bytes();
 let dir=std::env::temp_dir().join(format!("quartz-g56-{}-{}-{recipient}-{count}",std::process::id(),SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_nanos()));fs::create_dir(&dir).unwrap();
 let mut qhead:Hash=[0;32];let mut phead:Hash=[0;32];let mut chead:Hash=[0;32];let mut evidence=Vec::new();let mut chain=Vec::new();
 let mut silo=a[source].clone();
 for i in 0..count{
 let payload=if i==0{binding.encode().to_vec()}else{
 silo=silo.successor(Event::Shock(vec![(0,1)])).unwrap();
 let message=TimedObservation{observed:Clock::new(359+i as u64),observation:silo.observation()};
 let signatures=std::array::from_fn(|j|sign(j,&signed_evidence::signing_bytes(&binding,&message,binding.members()[j].root)));
 let e=Evidence{recipient:owner,roster:binding.digest(),message,signatures};let bytes=e.encode().to_vec();evidence.push(e);bytes};
 qhead=filesystem::append(&dir,i,qhead,&payload).unwrap();
 let p=publication::publish(&dir,(i+1)as u64,qhead,phead).unwrap();phead=p.digest();
 let claim=Claim{owner,publication_count:(i+1)as u64,publication:phead,roster:binding.digest(),evidence:custody::evidence_head(&binding,&evidence).unwrap(),previous:chead};
 let signatures=std::array::from_fn(|j|sign(j,&claim.signing_bytes(binding.members()[j].root)));let c=Custody{claim,signatures};chead=c.digest();chain.push(Custody::decode(&c.encode()).unwrap());
 assert!(cross_ledger::verify(&dir,owner,binding.digest(),&chain,chead));
 }
 let original=fs::read(dir.join("0000000000000000.qf1")).unwrap();
 fs::write(dir.join(format!("{count:016x}.qf1")),b"QF1").unwrap();
 assert!(cross_ledger::verify(&dir,owner,binding.digest(),&chain,chead));
 assert!(filesystem::append(&dir,count,qhead,b"replace").is_err());
 assert_eq!(fs::read(dir.join("0000000000000000.qf1")).unwrap(),original);
 assert!(!cross_ledger::verify(&dir,owner,binding.digest(),&chain[..count-1],chead));
 let mut bad=chain.clone();bad[count-1].signatures[0][0]^=1;let altered=bad[count-1].digest();assert!(!cross_ledger::verify(&dir,owner,binding.digest(),&bad,altered));
 fs::remove_dir_all(dir).unwrap();
 }
 }
 }
}
