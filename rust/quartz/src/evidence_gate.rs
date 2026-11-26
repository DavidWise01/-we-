use crate::{mesh::{Silo,SiloId,SILOS},temporal::{Clock,Inbox,TimedObservation},provenance::{self,Report,Verdict},coupling::{Coupling,Advisory},recovery::Recovery,witness::{geometry,conservation},cortex::{observe,regulate,Decision}};
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Packet{pub message:TimedObservation,pub reports:Vec<Report>}
/// Canonical subject fields, not a cryptographic digest.
pub fn subject(m:&TimedObservation)->[u8;32]{
 let o=&m.observation;let mut b=[0;32];b[0]=o.source.index() as u8;b[1..9].copy_from_slice(&o.sequence.to_be_bytes());b[9..17].copy_from_slice(&o.recovery_tick.to_be_bytes());b[17..19].copy_from_slice(&o.deficit.to_be_bytes());b[19..27].copy_from_slice(&o.energy.to_be_bytes());b[27..].copy_from_slice(&[71,51,51,0,1]);b
}
#[derive(Clone,Debug,PartialEq,Eq)]
pub enum Outcome{Hold,Trial{advice:Advisory,state:Recovery}}
/// One synchronous shadow round; original journals remain unchanged.
/// Each packet must have fresh, consistent declared evidence for its exact observation.
pub fn trial(s:&Silo,now:Clock,c:Coupling,packets:&[Packet])->Outcome{
 if packets.len()>SILOS{return Outcome::Hold;}
 if !matches!(regulate(s.journal()),Some(Decision::Trial(_))){return Outcome::Hold;}
 let mut inbox=Inbox::new(s.observation().source);
 for p in packets{
  let m=&p.message;
  if provenance::reconcile(now,subject(m),&p.reports)!=Verdict::ConsistentDeclared{return Outcome::Hold;}
  if p.reports.iter().any(|r|r.value!=m.observation.deficit||r.observed!=m.observed){return Outcome::Hold;}
  if !inbox.receive(now,m.clone()){return Outcome::Hold;}
 }
 let Some(advice)=inbox.advise(s,now,c)else{return Outcome::Hold;};
 let prior=s.journal().state();let Some(state)=prior.ordered_step(advice.order)else{return Outcome::Hold;};
 if !geometry(prior,&state)||!conservation(prior,&state)||observe(&state).shell_deficit>=observe(prior).shell_deficit{return Outcome::Hold;}
 Outcome::Trial{advice,state}
}
pub fn round(silos:&[Silo;SILOS],now:Clock,c:Coupling,packets:&[Vec<Packet>;SILOS])->[Outcome;SILOS]{
 std::array::from_fn(|i|if silos[i].observation().source==SiloId::new(i as u8).unwrap(){trial(&silos[i],now,c,&packets[i])}else{Outcome::Hold})
}
#[cfg(test)]mod tests{
 use super::*;use crate::{mesh::mesh,journal::{Event,Policy}};
 #[test]fn gates(){
 let a=mesh([10,40,90],Policy::FixedV1);let s=a[0].successor(Event::Shock(vec![(0,20)])).unwrap();let h=a[4].successor(Event::Shock(vec![(0,100)])).unwrap();
 let now=Clock::new(359);let m=TimedObservation{observed:now,observation:h.observation()};
 let reports=(1..=3).map(|n|Report{root:[n;32],relay:0,observed:now,subject:subject(&m),value:100}).collect();
 let p=Packet{message:m,reports};let c=Coupling::new(1000).unwrap();let before=s.clone();
 let Outcome::Trial{advice,..}=trial(&s,now,c,&[p.clone()])else{panic!("expected shadow trial")};assert_eq!(advice.shift,8);assert_eq!(s,before);
 let mut bad=p.clone();bad.reports[2].value=99;assert_eq!(trial(&s,now,c,&[bad]),Outcome::Hold);
 let mut bad=p.clone();bad.reports[2].root=bad.reports[0].root;assert_eq!(trial(&s,now,c,&[bad]),Outcome::Hold);
 assert_eq!(trial(&s,Clock::new(392),c,&[p]),Outcome::Hold);
 }
}
