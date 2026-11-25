use crate::{mesh::{Silo,SiloId,Observation,route,SILOS},coupling::{self,Coupling,Advisory}};
pub const CYCLE:u64=360;
pub const MAX_AGE:u64=32;
#[derive(Clone,Copy,Debug,PartialEq,Eq,PartialOrd,Ord)]
pub struct Clock(u64);
impl Clock{
 pub fn new(tick:u64)->Self{Self(tick)}
 pub fn cycle(self)->u64{self.0/CYCLE}
 pub fn phase(self)->u64{self.0%CYCLE}
 pub fn advance(self)->Option<Self>{Some(Self(self.0.checked_add(1)?))}
 pub fn age(self,earlier:Self)->Option<u64>{self.0.checked_sub(earlier.0)}
}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct TimedObservation{pub observed:Clock,pub observation:Observation}
pub struct Inbox{owner:SiloId,latest:[Option<TimedObservation>;SILOS]}
impl Inbox{
 pub fn new(owner:SiloId)->Self{Self{owner,latest:std::array::from_fn(|_|None)}}
 pub fn receive(&mut self,now:Clock,msg:TimedObservation)->bool{
  let o=&msg.observation;
  if !route(o.source,self.owner)||o.recovery_tick>o.sequence||o.deficit>9800||o.energy>3*u64::from(u32::MAX)||!now.age(msg.observed).is_some_and(|age|age<=MAX_AGE){return false;}
  let slot=&mut self.latest[o.source.index()];
  if slot.as_ref().is_some_and(|p|o.sequence<=p.observation.sequence||msg.observed<p.observed){return false;}
  *slot=Some(msg);true
 }
 pub fn advise(&self,s:&Silo,now:Clock,c:Coupling)->Option<Advisory>{
  if s.observation().source!=self.owner{return None;}
  let mut sum=0u32;let mut n=0;
  for o in self.latest.iter().flatten(){if now.age(o.observed).is_some_and(|age|age<=MAX_AGE){sum+=u32::from(o.observation.deficit);n+=1;}}
  coupling::advise_mean(s,c,if n==0{None}else{Some((sum/n)as u16)})
 }
}
#[cfg(test)]mod tests{
 use super::*;use crate::{mesh::mesh,journal::{Event,Policy}};
 #[test]fn wrap_and_freshness(){
 let a=mesh([10,40,90],Policy::FixedV1);let s=a[0].successor(Event::Shock(vec![(0,20)])).unwrap();let h=a[4].successor(Event::Shock(vec![(0,100)])).unwrap();let mut b=Inbox::new(s.observation().source);
 let t=Clock::new(359);let next=t.advance().unwrap();assert_eq!((next.cycle(),next.phase()),(1,0));
 let m=TimedObservation{observed:t,observation:h.observation()};assert!(!b.receive(Clock::new(358),m.clone()));assert!(b.receive(next,m.clone()));assert!(!b.receive(next,m));
 let c=Coupling::new(1000).unwrap();assert_eq!(b.advise(&s,Clock::new(391),c).unwrap().shift,8);assert_eq!(b.advise(&s,Clock::new(392),c).unwrap().shift,0);assert_eq!(s.observation().sequence,1);assert!(Clock::new(u64::MAX).advance().is_none());
 }
}
