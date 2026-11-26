use sha2::{Digest,Sha256};
use crate::{canonical,mesh::{Silo,SILOS},temporal::{Clock,TimedObservation},evidence_gate::Packet};
pub type Hash=[u8;32];
fn hash(domain:&[u8],data:&[u8])->Hash{
 let mut h=Sha256::new();h.update((domain.len() as u64).to_be_bytes());h.update(domain);h.update(data);h.finalize().into()
}
pub fn observation_id(m:&TimedObservation)->Hash{
 let o=&m.observation;let mut b=Vec::new();
 b.extend_from_slice(&(m.observed.cycle()*360+m.observed.phase()).to_be_bytes());
 b.push(o.source.index() as u8);b.extend_from_slice(&o.sequence.to_be_bytes());b.extend_from_slice(&o.recovery_tick.to_be_bytes());b.extend_from_slice(&o.deficit.to_be_bytes());b.extend_from_slice(&o.energy.to_be_bytes());
 hash(b"quartz/observation/v1",&b)
}
pub fn checkpoint(s:&[Silo;SILOS],now:Clock,lambda:u16,p:&[Vec<Packet>;SILOS])->Option<Hash>{Some(hash(b"quartz/QD1/v1",&canonical::encode(s,now,lambda,p)?))}
#[derive(Clone,Copy,Debug,PartialEq,Eq)]
pub struct Link{pub index:u64,pub previous:Hash,pub payload:Hash,pub digest:Hash}
impl Link{
 pub fn new(index:u64,previous:Hash,payload:Hash)->Self{
 let mut b=[0u8;72];b[..8].copy_from_slice(&index.to_be_bytes());b[8..40].copy_from_slice(&previous);b[40..].copy_from_slice(&payload);
 Self{index,previous,payload,digest:hash(b"quartz/link/v1",&b)}
 }
}
/// Verify against a separately retained expected head; no identity authentication.
pub fn verify(links:&[Link],expected_head:Hash)->bool{
 let mut previous=[0;32];
 for (i,l) in links.iter().enumerate(){
 let Ok(index)=u64::try_from(i)else{return false;};
 if *l!=Link::new(index,previous,l.payload){return false;}previous=l.digest;
 }previous==expected_head
}
#[cfg(test)]mod tests{
 use super::*;use crate::{mesh::mesh,journal::Policy};
 #[test]fn binding(){
 let a=mesh([100;3],Policy::FixedV1);let p=std::array::from_fn(|_|Vec::new());
 let x=checkpoint(&a,Clock::new(359),500,&p).unwrap();let y=checkpoint(&a,Clock::new(360),500,&p).unwrap();assert_ne!(x,y);
 let a0=Link::new(0,[0;32],x);let a1=Link::new(1,a0.digest,y);let chain=[a0,a1];assert!(verify(&chain,a1.digest));assert!(!verify(&chain[..1],a1.digest));
 let mut bad=chain;bad[0].payload=y;assert!(!verify(&bad,a1.digest));assert!(!verify(&[a1,a0],a1.digest));
 let mut m=TimedObservation{observed:Clock::new(359),observation:a[0].observation()};let x=observation_id(&m);m.observed=Clock::new(360);assert_ne!(x,observation_id(&m));
 }
}
