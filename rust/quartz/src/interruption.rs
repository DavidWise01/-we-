use sha2::{Digest,Sha256};
use crate::{mesh::SiloId,containment::Gate,integrity::Hash,quarantine_chain::{self,Record,MAX_CHECKPOINTS},epochs::{self,Epoch,MAX_EPOCHS}};
pub const COMMIT_BYTES:usize=77;
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Boundary{owner:SiloId,quarantine_count:u32,epoch_count:u32,quarantine_head:Hash,epoch_head:Hash}
pub struct Recovered{pub gate:Gate,pub quarantine:Vec<Record>,pub epochs:Vec<Epoch>}
impl Boundary{
 pub fn prepare(owner:SiloId,q:&[Record],e:&[Epoch])->Option<Self>{
 if q.is_empty()||q.len()>MAX_CHECKPOINTS||e.len()>MAX_EPOCHS{return None;}
 let quarantine_head=q.last()?.link.digest;let epoch_head=e.last().map(|x|x.link.digest).unwrap_or([0;32]);
 quarantine_chain::restore(owner,q,quarantine_head)?;if !epochs::verify(owner,e,epoch_head){return None;}
 Some(Self{owner,quarantine_count:q.len()as u32,epoch_count:e.len()as u32,quarantine_head,epoch_head})
 }
 pub fn encode(&self)->[u8;COMMIT_BYTES]{
 let mut b=[0;COMMIT_BYTES];b[..4].copy_from_slice(b"QB1\0");b[4]=self.owner.index()as u8;b[5..9].copy_from_slice(&self.quarantine_count.to_be_bytes());b[9..13].copy_from_slice(&self.epoch_count.to_be_bytes());b[13..45].copy_from_slice(&self.quarantine_head);b[45..77].copy_from_slice(&self.epoch_head);b
 }
 pub fn digest(b:&[u8])->Hash{let mut h=Sha256::new();h.update(b"quartz/QB1/v1\0");h.update(b);h.finalize().into()}
}
/// Restore committed prefixes only. Expected digest is independently supplied.
/// Uncommitted suffixes are ignored, not validated or promoted.
pub fn recover(owner:SiloId,bytes:&[u8],expected:Hash,q:&[Record],e:&[Epoch])->Option<Recovered>{
 if bytes.len()!=COMMIT_BYTES||&bytes[..4]!=b"QB1\0"||bytes[4]as usize!=owner.index()||Boundary::digest(bytes)!=expected{return None;}
 let nq=u32::from_be_bytes(bytes[5..9].try_into().ok()?)as usize;let ne=u32::from_be_bytes(bytes[9..13].try_into().ok()?)as usize;
 if nq==0||nq>MAX_CHECKPOINTS||ne>MAX_EPOCHS{return None;}
 let q=q.get(..nq)?;let e=e.get(..ne)?;
 let boundary=Boundary::prepare(owner,q,e)?;if boundary.encode().as_slice()!=bytes{return None;}
 Some(Recovered{gate:quarantine_chain::restore(owner,q,boundary.quarantine_head)?,quarantine:q.to_vec(),epochs:e.to_vec()})
}
#[cfg(test)]mod tests{
 use super::*;use crate::{mesh::mesh,journal::{Policy,Event},temporal::{Clock,TimedObservation},integrity::observation_id,provenance::Report,evidence_gate::Packet,coupling::Coupling,containment::Fault};
 #[test]fn interrupted_commit(){
 let a=mesh([100;3],Policy::FixedV1);let s=a[0].successor(Event::Shock(vec![(0,20)])).unwrap();let h=a[4].successor(Event::Shock(vec![(0,100)])).unwrap();let owner=s.observation().source;
 let mut g=Gate::new(owner);let mut q=vec![quarantine_chain::append(owner,&[],[0;32],&g).unwrap()];
 let now=Clock::new(359);let message=TimedObservation{observed:now,observation:h.observation()};let reports=(1..=3).map(|n|Report{root:[n;32],relay:n,observed:now,subject:observation_id(&message),value:100}).collect();let p=Packet{message,reports};let c=Coupling::new(1000).unwrap();
 assert!(g.trial(&s,now,c,&[p.clone()]).is_ok());q.push(quarantine_chain::append(owner,&q,q.last().unwrap().link.digest,&g).unwrap());
 let mut bad=p.clone();bad.message.observation.energy-=1;assert_eq!(g.trial(&s,now,c,&[bad]),Err(Fault::Equivocation));q.push(quarantine_chain::append(owner,&q,q.last().unwrap().link.digest,&g).unwrap());
 let t=vec![vec![vec![(0,1)];9]];let ch=vec![vec![vec![(124,1)];12]];let mut e=vec![epochs::append(&s,&[],[0;32],&t,&ch).unwrap()];
 let b=Boundary::prepare(owner,&q,&e).unwrap().encode();let head=Boundary::digest(&b);
 for n in 0..COMMIT_BYTES{assert!(recover(owner,&b[..n],head,&q,&e).is_none());}
 let mut torn=b; torn[40]^=1;assert!(recover(owner,&torn,head,&q,&e).is_none());
 assert!(recover(owner,&b,head,&q[..2],&e).is_none());assert!(recover(owner,&b,head,&q,&[]).is_none());
 let next=s.successor(Event::Shock(vec![(124,1)])).unwrap();e.push(epochs::append(&next,&e,e.last().unwrap().link.digest,&t,&ch).unwrap());
 q.push(quarantine_chain::append(owner,&q,q.last().unwrap().link.digest,&g).unwrap());
 let mut restored=recover(owner,&b,head,&q,&e).unwrap();assert_eq!(restored.quarantine.len(),3);assert_eq!(restored.epochs.len(),1);assert!(restored.gate.quarantined(h.observation().source));assert_eq!(restored.gate.trial(&s,now,c,&[p]),Err(Fault::Quarantined));
 let b2=Boundary::prepare(owner,&q,&e).unwrap().encode();assert!(recover(owner,&b,Boundary::digest(&b2),&q,&e).is_none());
 }
}
