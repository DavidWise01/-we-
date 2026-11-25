use crate::{mesh::{Silo,SiloId,Observation,route,SILOS},pump_memory::{self,PumpMemory}};
pub const EXTERNAL_WINDOW:usize=32;
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct MemoryBank{owner:SiloId,local:[PumpMemory;3],external:[Vec<Observation>;SILOS],latest:[Option<u64>;SILOS]}
impl MemoryBank{
 pub fn new(owner:SiloId)->Self{Self{owner,local:std::array::from_fn(|_|PumpMemory::default()),external:std::array::from_fn(|_|Vec::new()),latest:[None;SILOS]}}
 pub fn owner(&self)->SiloId{self.owner}
 pub fn local(&self)->&[PumpMemory;3]{&self.local}
 pub fn external(&self,source:SiloId)->&[Observation]{&self.external[source.index()]}
 pub fn refresh(&mut self,silo:&Silo)->Option<()>{
  if silo.observation().source!=self.owner{return None;}
  self.local=pump_memory::derive(silo.journal())?;Some(())
 }
 /// Received observations remain untrusted; never modify local recovery history.
 pub fn receive(&mut self,msg:Observation)->bool{
  if !route(msg.source,self.owner){return false;}
  let i=msg.source.index();
  if self.latest[i].is_some_and(|n|msg.sequence<=n){return false;}
  if msg.recovery_tick>msg.sequence||msg.deficit>9800||msg.energy>3*u64::from(u32::MAX){return false;}
  self.latest[i]=Some(msg.sequence);
  let v=&mut self.external[i];if v.len()==EXTERNAL_WINDOW{v.remove(0);}v.push(msg);true
 }
}
#[cfg(test)]mod tests{
 use super::*;use crate::{mesh::mesh,journal::{Policy,Event}};
 #[test]fn isolation_and_rollover(){
 let a=mesh([100;3],Policy::RotatingV2);let mut s=a[0].clone();let mut b=MemoryBank::new(SiloId::new(4).unwrap());b.refresh(&a[4]).unwrap();let local=b.local().clone();
 for _ in 0..40{ s=s.successor(Event::Shock(vec![(0,1)])).unwrap();assert!(b.receive(s.observation()));}
 assert_eq!(b.external(SiloId::new(0).unwrap()).len(),32);assert_eq!(b.external(SiloId::new(0).unwrap())[0].sequence,9);
 assert!(!b.receive(s.observation()));assert!(b.refresh(&s).is_none());assert_eq!(b.local(),&local);assert_eq!(a[4].observation().deficit,0);
 }
 #[test]fn route_and_local(){
 let a=mesh([100;3],Policy::FixedV1);let id=SiloId::new(0).unwrap();let mut b=MemoryBank::new(id);
 assert!(!b.receive(a[1].observation()));assert!(!b.receive(a[0].observation()));assert!(b.receive(a[4].observation()));
 let s=a[0].successor(Event::Shock(vec![(0,1)])).unwrap().successor(Event::Recover).unwrap();
 b.refresh(&s).unwrap();assert_eq!(b.local()[0].spent(),1);assert_eq!(b.local()[1].spent(),0);assert_eq!(b.external(SiloId::new(4).unwrap()).len(),1);
 }
}
