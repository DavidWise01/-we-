#![cfg(unix)]
use quartz_kernel::{authentication::Witness,mesh::mesh,journal::Policy,temporal::{Clock,TimedObservation},roster_binding::Binding,signed_evidence::{self,Evidence},custody::{self,Claim,Custody},filesystem,publication,cross_ledger,incremental::VerifiedPrefix};
use ed25519_dalek::{SigningKey,Signer};
use std::{fs,time::{SystemTime,UNIX_EPOCH}};
#[test]fn incremental_parity(){
 let keys:[SigningKey;3]=std::array::from_fn(|i|SigningKey::from_bytes(&[(i+1)as u8;32]));
 let members=std::array::from_fn(|i|Witness{key:keys[i].verifying_key().to_bytes(),root:[(i+1)as u8;32]});
 let a=mesh([100;3],Policy::FixedV1);let owner=a[0].observation().source;let binding=Binding::genesis(owner,members).unwrap();
 let sign=|i:usize,b:&[u8]|keys.iter().find(|k|k.verifying_key().to_bytes()==binding.members()[i].key).unwrap().sign(b).to_bytes();
 let dir=std::env::temp_dir().join(format!("quartz-g62-{}-{}",std::process::id(),SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_nanos()));fs::create_dir(&dir).unwrap();
 let mut cache=VerifiedPrefix::genesis(&binding).unwrap();let mut ev=Vec::new();let mut chain=Vec::new();let mut q=[0;32];let mut p=[0;32];
 for i in 0..8{
 let payload=if i==0{binding.encode().to_vec()}else{let message=TimedObservation{observed:Clock::new(i as u64),observation:a[4].observation()};let signatures=std::array::from_fn(|j|sign(j,&signed_evidence::signing_bytes(&binding,&message,binding.members()[j].root)));let e=Evidence{recipient:owner,roster:binding.digest(),message,signatures};let b=e.encode().to_vec();ev.push(e);b};
 q=filesystem::append(&dir,i,q,&payload).unwrap();p=publication::publish(&dir,(i+1)as u64,q,p).unwrap().digest();
 let claim=Claim{owner,publication_count:(i+1)as u64,publication:p,roster:binding.digest(),evidence:custody::evidence_head(&binding,&ev).unwrap(),previous:cache.head()};
 let signatures=std::array::from_fn(|j|sign(j,&claim.signing_bytes(binding.members()[j].root)));let c=Custody{claim,signatures};let h=c.digest();
 assert!(cache.advance(&dir,&c,[0;32]).is_none());let mut bad=c.clone();bad.signatures[0][0]^=1;assert!(cache.advance(&dir,&bad,bad.digest()).is_none());
 let next=cache.advance(&dir,&c,h).unwrap();assert_eq!(next.count(),(i+1)as u64);assert_eq!(next.head(),h);assert!(next.advance(&dir,&c,h).is_none());
 chain.push(c);assert!(cross_ledger::verify(&dir,owner,binding.digest(),&chain,h));cache=next;
 }
 // Cached validation does not certify the continued existence or integrity of old disk bytes.
 fs::write(dir.join("0000000000000000.qf1"),b"damaged").unwrap();assert!(!cross_ledger::verify(&dir,owner,binding.digest(),&chain,cache.head()));
 fs::remove_dir_all(dir).unwrap();
}
