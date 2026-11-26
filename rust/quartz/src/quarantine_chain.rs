use crate::{containment::Gate,mesh::{SiloId,SILOS},integrity::{Hash,Link}};
pub const MAX_CHECKPOINTS:usize=4096;
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Record{pub bytes:Vec<u8>,pub link:Link}
/// Compare canonical QH1 snapshots after structural validation.
fn monotonic(a:&[u8],b:&[u8])->bool{
 if a[4]!=b[4]||a[5]>b[5]||a[6..14]>b[6..14]{return false;}
 for i in 0..SILOS{
 let p=14+i*50;
 if a[p]>b[p]||a[p+1]>b[p+1]{return false;}
 if a[p+1]==1{
 if a[p+2..p+10]>b[p+2..p+10]||a[p+42..p+50]>b[p+42..p+50]{return false;}
 if a[p+2..p+10]==b[p+2..p+10]&&a[p+10..p+50]!=b[p+10..p+50]{return false;}
 if a[p]==1&&a[p+1..p+50]!=b[p+1..p+50]{return false;}
 }
 if a[p]==1&&a[p+1]!=b[p+1]{return false;}
 }true
}
/// Caller supplies separately retained head. Empty history is not a restart checkpoint.
pub fn restore(owner:SiloId,records:&[Record],expected:Hash)->Option<Gate>{
 if records.is_empty()||records.len()>MAX_CHECKPOINTS{return None;}
 let mut prior:Option<&[u8]>=None;let mut head=[0;32];let mut last=None;
 for (i,r) in records.iter().enumerate(){
 let payload=Gate::snapshot_digest(&r.bytes);
 let gate=Gate::restore(owner,&r.bytes,payload)?;
 if r.link!=Link::new(i as u64,head,payload){return None;}
 if i==0&&gate!=Gate::new(owner){return None;}
 if prior.is_some_and(|a|!monotonic(a,&r.bytes)){return None;}
 prior=Some(&r.bytes);head=r.link.digest;last=Some(gate);
 }
 if head!=expected{return None;}last
}
/// Return a new record without rewriting prior records.
pub fn append(owner:SiloId,records:&[Record],expected:Hash,gate:&Gate)->Option<Record>{
 if records.len()>=MAX_CHECKPOINTS{return None;}
 if records.is_empty(){if expected!=[0;32]||gate!=&Gate::new(owner){return None;}}
 else{restore(owner,records,expected)?;}
 let bytes=gate.snapshot();let payload=Gate::snapshot_digest(&bytes);Gate::restore(owner,&bytes,payload)?;
 if records.last().is_some_and(|r|!monotonic(&r.bytes,&bytes)){return None;}
 Some(Record{bytes,link:Link::new(records.len() as u64,expected,payload)})
}
#[cfg(test)]mod tests{
 use super::*;use crate::{mesh::mesh,journal::{Policy,Event},temporal::{Clock,TimedObservation},provenance::Report,evidence_gate::Packet,integrity::observation_id,coupling::Coupling,containment::Fault};
 #[test]fn quarantine_restart(){
 let a=mesh([100;3],Policy::FixedV1);let s=a[0].successor(Event::Shock(vec![(0,20)])).unwrap();let h=a[4].successor(Event::Shock(vec![(0,100)])).unwrap();
 let owner=s.observation().source;let mut g=Gate::new(owner);let mut records=vec![append(owner,&[],[0;32],&g).unwrap()];
 let now=Clock::new(359);let message=TimedObservation{observed:now,observation:h.observation()};let reports=(1..=3).map(|n|Report{root:[n;32],relay:n,observed:now,subject:observation_id(&message),value:100}).collect();let p=Packet{message,reports};let c=Coupling::new(1000).unwrap();
 assert!(g.trial(&s,now,c,&[p.clone()]).is_ok());
 records.push(append(owner,&records,records.last().unwrap().link.digest,&g).unwrap());let accepted=g.clone();
 let mut bad=p.clone();bad.message.observation.energy-=1;assert_eq!(g.trial(&s,now,c,&[bad]),Err(Fault::Equivocation));
 records.push(append(owner,&records,records.last().unwrap().link.digest,&g).unwrap());let head=records.last().unwrap().link.digest;
 let mut restarted=restore(owner,&records,head).unwrap();assert!(restarted.quarantined(h.observation().source));assert_eq!(restarted.trial(&s,now,c,&[p]),Err(Fault::Quarantined));
 assert!(restore(owner,&records[..2],head).is_none());assert!(append(owner,&records,head,&accepted).is_none());
 let mut fork=records.clone();let bytes=accepted.snapshot();fork.push(Record{link:Link::new(3,head,Gate::snapshot_digest(&bytes)),bytes});assert!(restore(owner,&fork,fork[3].link.digest).is_none());
 }
}
