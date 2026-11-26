use crate::{mesh::{Silo,SiloId,SILOS},temporal::{Clock,Inbox},provenance::{self,Verdict},evidence_gate::{Packet,Outcome},integrity::{observation_id,Hash},coupling::Coupling,cortex::{regulate,Decision,observe},witness::{geometry,conservation}};
#[derive(Clone,Copy,Debug,PartialEq,Eq)]
pub enum Fault{Owner,Clock,Capacity,Replay,Equivocation,Evidence,Admission,Quarantined}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Gate{owner:SiloId,latest:[Option<(u64,Hash,Clock)>;SILOS],quarantine:[bool;SILOS],last_clock:Option<Clock>}
impl Gate{
 pub fn new(owner:SiloId)->Self{Self{owner,latest:[None;SILOS],quarantine:[false;SILOS],last_clock:None}}

 /// QH1 snapshot retains sequence, digest, clock and quarantine flags.
 pub fn snapshot(&self)->Vec<u8>{
  let mut b=b"QH1\0".to_vec();b.push(self.owner.index() as u8);
  fn time(t:Clock)->[u8;8]{(t.cycle()*360+t.phase()).to_be_bytes()}
  match self.last_clock{Some(t)=>{b.push(1);b.extend_from_slice(&time(t));},None=>{b.push(0);b.extend_from_slice(&[0;8]);}}
  for i in 0..SILOS{
   b.push(u8::from(self.quarantine[i]));
   match self.latest[i]{Some((n,h,t))=>{b.push(1);b.extend_from_slice(&n.to_be_bytes());b.extend_from_slice(&h);b.extend_from_slice(&time(t));},None=>{b.push(0);b.extend_from_slice(&[0;48]);}}
  }b
 }
 pub fn snapshot_digest(bytes:&[u8])->Hash{
  use sha2::{Digest,Sha256};let mut h=Sha256::new();h.update(b"quartz/QH1/v1\0");h.update(bytes);h.finalize().into()
 }
 /// Expected digest must come from a separately retained trusted checkpoint.
 pub fn restore(owner:SiloId,bytes:&[u8],expected:Hash)->Option<Self>{
  if bytes.len()!=264||Self::snapshot_digest(bytes)!=expected||&bytes[..4]!=b"QH1\0"||usize::from(bytes[4])!=owner.index(){return None;}
  let read=|b:&[u8]|u64::from_be_bytes(b.try_into().expect("fixed width"));
  let mut g=Self::new(owner);
  g.last_clock=match bytes[5]{0 if bytes[6..14]==[0;8]=>None,1=>Some(Clock::new(read(&bytes[6..14]))),_=>return None};
  for i in 0..SILOS{
   let p=14+i*50;let id=SiloId::new(i as u8)?;
   g.quarantine[i]=match bytes[p]{0=>false,1=>true,_=>return None};
   g.latest[i]=match bytes[p+1]{
    0 if bytes[p+2..p+50]==[0;48]=>None,
    1=>{let t=Clock::new(read(&bytes[p+42..p+50]));if g.last_clock.is_none_or(|now|t>now){return None;}Some((read(&bytes[p+2..p+10]),bytes[p+10..p+42].try_into().ok()?,t))},
    _=>return None
   };
   if (g.quarantine[i]||g.latest[i].is_some())&&(!crate::mesh::route(id,owner)||g.last_clock.is_none()){return None;}
  }
  if g.snapshot()!=bytes{return None;}Some(g)
 }
 pub fn quarantined(&self,id:SiloId)->bool{self.quarantine[id.index()]}
 /// In-memory containment only; declared roots are not authenticated.
 pub fn trial(&mut self,s:&Silo,now:Clock,c:Coupling,packets:&[Packet])->Result<Outcome,Fault>{
 if s.observation().source!=self.owner{return Err(Fault::Owner);}
 if self.last_clock.is_some_and(|t|now<t){return Err(Fault::Clock);}
 self.last_clock=Some(now);
 if packets.len()>SILOS{return Err(Fault::Capacity);}
 let mut staged=self.latest;let mut inbox=Inbox::new(self.owner);
 for p in packets{
  let m=&p.message;let o=&m.observation;let i=o.source.index();let digest=observation_id(m);
  if !crate::mesh::route(o.source,self.owner){return Err(Fault::Admission);}
  if self.quarantine[i]{return Err(Fault::Quarantined);}
  if let Some((seq,old,t))=staged[i]{
   if o.sequence==seq&&digest!=old{self.quarantine[i]=true;return Err(Fault::Equivocation);}
   if o.sequence<=seq||m.observed<t{return Err(Fault::Replay);}
  }
  let verdict=provenance::reconcile(now,digest,&p.reports);
  if verdict==Verdict::Contradiction{self.quarantine[i]=true;return Err(Fault::Evidence);}
  if verdict!=Verdict::ConsistentDeclared||p.reports.iter().any(|r|r.value!=o.deficit||r.observed!=m.observed){return Err(Fault::Evidence);}
  if !inbox.receive(now,m.clone()){return Err(Fault::Admission);}
  staged[i]=Some((o.sequence,digest,m.observed));
 }
 self.latest=staged;
 if !matches!(regulate(s.journal()),Some(Decision::Trial(_))){return Ok(Outcome::Hold);}
 let Some(advice)=inbox.advise(s,now,c)else{return Ok(Outcome::Hold);};
 let prior=s.journal().state();let Some(state)=prior.ordered_step(advice.order)else{return Ok(Outcome::Hold);};
 if !geometry(prior,&state)||!conservation(prior,&state)||observe(&state).shell_deficit>=observe(prior).shell_deficit{return Ok(Outcome::Hold);}
 Ok(Outcome::Trial{advice,state})
 }
}
#[cfg(test)]mod tests{
 use super::*;use crate::{mesh::mesh,journal::{Event,Policy},temporal::TimedObservation,provenance::Report};
 fn packet(s:&Silo,t:Clock)->Packet{
 let message=TimedObservation{observed:t,observation:s.observation()};
 let reports=(1..=3).map(|n|Report{root:[n;32],relay:0,observed:t,subject:observation_id(&message),value:message.observation.deficit}).collect();
 Packet{message,reports}
 }
 #[test]fn containment(){
 let a=mesh([10,40,90],Policy::FixedV1);let s=a[0].successor(Event::Shock(vec![(0,20)])).unwrap();let h=a[4].successor(Event::Shock(vec![(0,100)])).unwrap();
 let now=Clock::new(359);let c=Coupling::new(1000).unwrap();let p=packet(&h,now);let mut g=Gate::new(s.observation().source);
 assert!(matches!(g.trial(&s,now,c,&[p.clone()]),Ok(Outcome::Trial{..})));
 assert_eq!(g.trial(&s,now,c,&[p.clone()]),Err(Fault::Replay));
 let mut altered=p.clone();altered.message.observation.energy-=1;
 assert_eq!(g.trial(&s,now,c,&[altered]),Err(Fault::Equivocation));
 assert!(g.quarantined(h.observation().source));
 assert_eq!(g.trial(&s,now,c,&[p.clone()]),Err(Fault::Quarantined));
 let mut fresh=Gate::new(s.observation().source);let mut bad=p;bad.reports[2].value=99;
 assert_eq!(fresh.trial(&s,now,c,&[bad]),Err(Fault::Evidence));assert!(fresh.quarantined(h.observation().source));
 }
}

#[cfg(test)]mod persistence_tests{
 use super::*;use crate::{mesh::mesh,journal::{Event,Policy},temporal::TimedObservation,provenance::Report};
 #[test]fn restart_high_water(){
 let a=mesh([100;3],Policy::FixedV1);let s=a[0].successor(Event::Shock(vec![(0,20)])).unwrap();let h=a[4].successor(Event::Shock(vec![(0,100)])).unwrap();
 let now=Clock::new(359);let message=TimedObservation{observed:now,observation:h.observation()};
 let reports=(1..=3).map(|n|Report{root:[n;32],relay:n,observed:now,subject:observation_id(&message),value:100}).collect();
 let p=Packet{message,reports};let c=Coupling::new(1000).unwrap();let owner=s.observation().source;let mut g=Gate::new(owner);
 let old=g.snapshot();assert!(g.trial(&s,now,c,&[p.clone()]).is_ok());
 let b=g.snapshot();assert_eq!(b.len(),264);let head=Gate::snapshot_digest(&b);
 let mut restored=Gate::restore(owner,&b,head).unwrap();assert_eq!(g,restored);
 assert_eq!(restored.trial(&s,now,c,&[p]),Err(Fault::Replay));
 assert_eq!(restored.trial(&s,Clock::new(358),c,&[]),Err(Fault::Clock));
 assert!(Gate::restore(owner,&old,head).is_none());assert!(Gate::restore(h.observation().source,&b,head).is_none());
 for n in 0..b.len(){assert!(Gate::restore(owner,&b[..n],head).is_none());}
 let mut bad=b.clone();bad[20]^=1;assert!(Gate::restore(owner,&bad,head).is_none());
 }
}
