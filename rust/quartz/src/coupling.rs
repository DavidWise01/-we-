use crate::{mesh::{Silo,SiloId,SILOS},silo_memory::MemoryBank,adaptive::{self,Recommendation},pump_memory::derive};
/// Fixed-point coupling in thousandths. No floating-point replay drift.
#[derive(Clone,Copy,Debug,PartialEq,Eq)]
pub struct Coupling(u16);
impl Coupling{pub fn new(v:u16)->Option<Self>{(v<=1000).then_some(Self(v))}}
pub const MAX_SHIFT:u16=8;
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Advisory{pub local:Recommendation,pub external_mean:Option<u16>,pub shift:u16,pub effective_pressure:u16,pub order:[usize;3]}
pub fn advise(s:&Silo,b:&MemoryBank,c:Coupling)->Option<Advisory>{
 if b.owner()!=s.observation().source{return None;}
 let state=s.journal().state();let memory=derive(s.journal())?;
 let local=adaptive::recommend(state,&memory);
 let mut sum=0u32;let mut count=0u32;
 for i in 0..SILOS{if let Some(o)=b.external(SiloId::new(i as u8)?).last(){sum+=u32::from(o.deficit);count+=1;}}
 let mean=if count==0{None}else{Some((sum/count)as u16)};
 let excess=mean.unwrap_or(local.pressure).saturating_sub(local.pressure).min(MAX_SHIFT);
 let shift=(u32::from(excess)*u32::from(c.0)/1000)as u16;
 let effective=local.pressure+shift;let mut order=local.order;
 if local.pressure>0&&effective>=adaptive::PRESSURE_THRESHOLD&&!local.high_pressure{
  let energy=state.energy();let start=(state.tick()%3)as usize;
  order.sort_by_key(|&p|(energy[p]==0,u32::MAX-energy[p],memory[p].spent(),(p+3-start)%3));
 }
 Some(Advisory{local,external_mean:mean,shift,effective_pressure:effective,order})
}
#[cfg(test)]mod tests{
 use super::*;use crate::{mesh::mesh,journal::{Event,Policy}};
 #[test]fn isolation_and_bound(){
 let a=mesh([10,40,90],Policy::FixedV1);let s=a[0].successor(Event::Shock(vec![(0,20)])).unwrap();let hub=a[4].successor(Event::Shock(vec![(0,100)])).unwrap();
 let mut b=MemoryBank::new(s.observation().source);let empty=b.clone();assert!(b.receive(hub.observation()));let before=s.clone();
 let zero=advise(&s,&b,Coupling::new(0).unwrap()).unwrap();let independent=advise(&s,&empty,Coupling::new(0).unwrap()).unwrap();assert_eq!(zero.order,independent.order);assert_eq!(zero.shift,0);
 let full=advise(&s,&b,Coupling::new(1000).unwrap()).unwrap();assert_eq!(full.shift,8);assert_eq!(full.order,[2,1,0]);assert_eq!(s,before);
 assert!(Coupling::new(1001).is_none());assert!(advise(&hub,&b,Coupling::new(1000).unwrap()).is_none());
 }
}
