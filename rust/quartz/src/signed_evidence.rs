use ed25519_dalek::{Signature,VerifyingKey};
use crate::{mesh::{SiloId,Observation,route},temporal::{Clock,TimedObservation,MAX_AGE},roster_binding::Binding,integrity::{Hash,observation_id},provenance::Report,evidence_gate::Packet};
pub const EVIDENCE_BYTES:usize=264;
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Evidence{pub recipient:SiloId,pub roster:Hash,pub message:TimedObservation,pub signatures:[[u8;64];3]}
fn tick(t:Clock)->[u8;8]{(t.cycle()*360+t.phase()).to_be_bytes()}
pub fn signing_bytes(binding:&Binding,m:&TimedObservation,root:Hash)->Vec<u8>{
 let mut b=b"quartz/QE1/witness/v1\0".to_vec();b.push(binding.owner().index()as u8);b.extend_from_slice(&binding.digest());b.extend_from_slice(&observation_id(m));b.extend_from_slice(&root);b
}
impl Evidence{
 pub fn encode(&self)->[u8;EVIDENCE_BYTES]{
 let mut b=[0;EVIDENCE_BYTES];b[..4].copy_from_slice(b"QE1\0");b[4]=self.recipient.index()as u8;b[5..37].copy_from_slice(&self.roster);
 let m=&self.message;let o=&m.observation;b[37..45].copy_from_slice(&tick(m.observed));b[45]=o.source.index()as u8;b[46..54].copy_from_slice(&o.sequence.to_be_bytes());b[54..62].copy_from_slice(&o.recovery_tick.to_be_bytes());b[62..64].copy_from_slice(&o.deficit.to_be_bytes());b[64..72].copy_from_slice(&o.energy.to_be_bytes());
 for (i,s) in self.signatures.iter().enumerate(){let p=72+i*64;b[p..p+64].copy_from_slice(s);}b
 }
 pub fn decode(b:&[u8])->Option<Self>{
 if b.len()!=EVIDENCE_BYTES||&b[..4]!=b"QE1\0"{return None;}
 let recipient=SiloId::new(b[4])?;let roster=b[5..37].try_into().ok()?;let observed=Clock::new(u64::from_be_bytes(b[37..45].try_into().ok()?));
 let observation=Observation{source:SiloId::new(b[45])?,sequence:u64::from_be_bytes(b[46..54].try_into().ok()?),recovery_tick:u64::from_be_bytes(b[54..62].try_into().ok()?),deficit:u16::from_be_bytes(b[62..64].try_into().ok()?),energy:u64::from_be_bytes(b[64..72].try_into().ok()?)};
 let mut signatures=[[0;64];3];for (i,s) in signatures.iter_mut().enumerate(){let p=72+i*64;*s=b[p..p+64].try_into().ok()?;}
 let e=Self{recipient,roster,message:TimedObservation{observed,observation},signatures};if e.encode().as_slice()!=b{return None;}Some(e)
 }
 /// Historical verification does not confer freshness or admission authority.
 pub fn verify_history(&self,binding:&Binding)->Option<Packet>{
 let m=&self.message;let o=&m.observation;
 if self.recipient!=binding.owner()||self.roster!=binding.digest()||!route(o.source,self.recipient)||o.recovery_tick>o.sequence||o.deficit>9800||o.energy>3*u64::from(u32::MAX){return None;}
 let mut reports=Vec::with_capacity(3);
 for (i,w) in binding.members().iter().enumerate(){let k=VerifyingKey::from_bytes(&w.key).ok()?;k.verify_strict(&signing_bytes(binding,m,w.root),&Signature::from_bytes(&self.signatures[i])).ok()?;reports.push(Report{root:w.root,relay:i as u8,observed:m.observed,subject:observation_id(m),value:o.deficit});}
 Some(Packet{message:m.clone(),reports})
 }
 pub fn verify_fresh(&self,binding:&Binding,now:Clock)->Option<Packet>{if !now.age(self.message.observed).is_some_and(|a|a<=MAX_AGE){return None;}self.verify_history(binding)}
}
#[cfg(test)]mod tests{
 use super::*;use ed25519_dalek::{SigningKey,Signer};use crate::{authentication::Witness,mesh::mesh,journal::Policy};
 #[test]fn historical_signatures(){
 let keys:[SigningKey;3]=std::array::from_fn(|i|SigningKey::from_bytes(&[(i+1)as u8;32]));let members=std::array::from_fn(|i|Witness{key:keys[i].verifying_key().to_bytes(),root:[(i+1)as u8;32]});
 let a=mesh([100;3],Policy::FixedV1);let owner=a[0].observation().source;let binding=Binding::genesis(owner,members).unwrap();
 let message=TimedObservation{observed:Clock::new(359),observation:a[4].observation()};
 let signatures=std::array::from_fn(|i|{let w=binding.members()[i];keys.iter().find(|k|k.verifying_key().to_bytes()==w.key).unwrap().sign(&signing_bytes(&binding,&message,w.root)).to_bytes()});
 let e=Evidence{recipient:owner,roster:binding.digest(),message,signatures};let b=e.encode();assert_eq!(Evidence::decode(&b),Some(e.clone()));assert!(e.verify_history(&binding).is_some());
 assert!(e.verify_fresh(&binding,Clock::new(391)).is_some());assert!(e.verify_fresh(&binding,Clock::new(392)).is_none());assert!(e.verify_fresh(&binding,Clock::new(358)).is_none());
 let next=binding.successor().unwrap();assert!(e.verify_history(&next).is_none());let mut altered=e.clone();altered.roster=next.digest();assert!(altered.verify_history(&next).is_none());
 for i in [46,64,72,136,200]{let mut bad=b;bad[i]^=1;assert!(Evidence::decode(&bad).and_then(|x|x.verify_history(&binding)).is_none());}
 for n in 0..EVIDENCE_BYTES{assert!(Evidence::decode(&b[..n]).is_none());}
 }
}
