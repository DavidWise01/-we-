use std::path::Path;
use crate::{mesh::SiloId,integrity::Hash,filesystem,publication::{self,Publication},roster_binding::{Binding,ROSTER_BYTES},signed_evidence::{Evidence,EVIDENCE_BYTES},custody::{Custody,MAX_EVIDENCE}};
/// Each published payload is exactly one QR1 or QE1 record. Each QC1 attests
/// to the complete corresponding prefix. Roster remains fixed for this profile.
pub fn verify(dir:&Path,owner:SiloId,genesis:Hash,chain:&[Custody],expected:Hash)->bool{
 if chain.is_empty()||chain.len()>filesystem::MAX_RECORDS{return false;}
 let Some(last)=chain.last()else{return false;};
 if last.digest()!=expected{return false;}
 let Ok(p)=publication::recover(dir,chain.len()as u64,last.claim.publication)else{return false;};
 let Ok(records)=filesystem::read_prefix(dir,chain.len(),p.head)else{return false;};
 let Some(binding)=Binding::decode(owner,&records[0].payload,genesis)else{return false;};
 if binding.encode()[5..13]!=[0;8]{return false;}
 let mut evidence=Vec::new();let mut prev_pub=[0;32];let mut prev_custody=[0;32];
 for (i,(record,c)) in records.iter().zip(chain).enumerate(){
 if i==0{if record.payload.len()!=ROSTER_BYTES{return false;}}
 else{
 if record.payload.len()!=EVIDENCE_BYTES||evidence.len()>=MAX_EVIDENCE{return false;}
 let Some(e)=Evidence::decode(&record.payload)else{return false;};evidence.push(e);
 }
 let count=(i+1)as u64;let pub_head=Publication{count,head:record.link.digest,previous:prev_pub}.digest();
 let digest=c.digest();
 if !c.verify(&binding,&evidence,count,pub_head,prev_custody,digest){return false;}
 prev_pub=pub_head;prev_custody=digest;
 }
 prev_pub==p.digest()&&prev_custody==expected
}
#[cfg(test)]mod tests{
 use super::*;use crate::{authentication::Witness,mesh::mesh,journal::Policy,temporal::{Clock,TimedObservation},signed_evidence,custody::{Claim,evidence_head}};use ed25519_dalek::{SigningKey,Signer};use std::{fs,time::{SystemTime,UNIX_EPOCH}};
 #[test]fn actual_published_bytes(){
 let keys:[SigningKey;3]=std::array::from_fn(|i|SigningKey::from_bytes(&[(i+1)as u8;32]));
 let members=std::array::from_fn(|i|Witness{key:keys[i].verifying_key().to_bytes(),root:[(i+1)as u8;32]});
 let a=mesh([100;3],Policy::FixedV1);let owner=a[0].observation().source;let binding=Binding::genesis(owner,members).unwrap();
 let sign=|i:usize,b:&[u8]|keys.iter().find(|k|k.verifying_key().to_bytes()==binding.members()[i].key).unwrap().sign(b).to_bytes();
 let make=|tick:u64|{let message=TimedObservation{observed:Clock::new(tick),observation:a[4].observation()};let signatures=std::array::from_fn(|i|sign(i,&signed_evidence::signing_bytes(&binding,&message,binding.members()[i].root)));Evidence{recipient:owner,roster:binding.digest(),message,signatures}};
 let e=make(359);let other=make(360);
 let dir=std::env::temp_dir().join(format!("quartz-g54-{}-{}",std::process::id(),SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_nanos()));fs::create_dir(&dir).unwrap();
 let h=filesystem::append(&dir,0,[0;32],&binding.encode()).unwrap();let p=publication::publish(&dir,1,h,[0;32]).unwrap();
 let h2=filesystem::append(&dir,1,h,&e.encode()).unwrap();let p2=publication::publish(&dir,2,h2,p.digest()).unwrap();
 let attest=|p:Publication,previous:Hash,ev:&[Evidence]|{let claim=Claim{owner,publication_count:p.count,publication:p.digest(),roster:binding.digest(),evidence:evidence_head(&binding,ev).unwrap(),previous};let signatures=std::array::from_fn(|i|sign(i,&claim.signing_bytes(binding.members()[i].root)));Custody{claim,signatures}};
 let c=attest(p,[0;32],&[]);let d=attest(p2,c.digest(),&[e]);let head=d.digest();
 assert!(verify(&dir,owner,binding.digest(),&[c.clone(),d.clone()],head));
 let wrong=attest(p2,c.digest(),&[other]);assert!(!verify(&dir,owner,binding.digest(),&[c.clone(),wrong.clone()],wrong.digest()));
 assert!(!verify(&dir,owner,[9;32],&[c.clone(),d],head));assert!(!verify(&dir,owner,binding.digest(),&[c],head));
 fs::remove_dir_all(dir).unwrap();
 }
}
