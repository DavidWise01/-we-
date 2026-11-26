use crate::{mesh::{Silo,SiloId,SILOS},temporal::{Clock,Inbox},provenance::{self,Verdict},evidence_gate::{Packet,Outcome},integrity::{observation_id,Hash},coupling::Coupling,cortex::{regulate,Decision,observe},witness::{geometry,conservation}};
#[derive(Clone,Copy,Debug,PartialEq,Eq)]
pub enum Fault{Owner,Clock,Capacity,Replay,Equivocation,Evidence,Admission,Quarantined}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Gate{owner:SiloId,latest:[Option<(u64,Hash,Clock)>;SILOS],quarantine:[bool;SILOS],last_clock:Option<Clock>}
impl Gate{
 pub fn new(owner:SiloId)->Self{Self{owner,latest:[None;SILOS],quarantine:[false;SILOS],last_clock:None}}
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
