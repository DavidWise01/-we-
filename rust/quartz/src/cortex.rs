use crate::{CELLS,CENTER,recovery::Recovery,bit_geometry,adaptive,pump_memory::derive,journal::Journal};
#[derive(Clone,Copy,Debug,PartialEq,Eq)]
pub enum Layer{Shell,Cortex,Constant}
pub fn layer(i:usize)->Option<Layer>{
 if i>=CELLS{None}else if i==CENTER{Some(Layer::Constant)}else if Recovery::outer(i){Some(Layer::Shell)}else{Some(Layer::Cortex)}
}
#[derive(Clone,Copy,Debug,PartialEq,Eq)]
pub enum Decision{HoldHealthy,HoldExhausted,HoldUnreachable,HoldInvariant,Trial([usize;3])}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Observation{pub shell_deficit:u16,pub cortex_deficit:u16,pub center_health:u8,pub reachable:u32,pub energy:u64}
pub fn observe(s:&Recovery)->Observation{
 let mut o=Observation{shell_deficit:0,cortex_deficit:0,center_health:s.health()[CENTER],reachable:bit_geometry::reachable(s.health()).count_ones(),energy:s.energy().iter().map(|&e|u64::from(e)).sum()};
 for (i,&h) in s.health().iter().enumerate(){match layer(i){Some(Layer::Shell)=>o.shell_deficit+=100-u16::from(h),Some(Layer::Cortex)=>o.cortex_deficit+=100-u16::from(h),_=>{}}}o
}
pub fn regulate(j:&Journal)->Option<Decision>{
 let o=observe(j.state());
 if o.center_health!=100||o.cortex_deficit!=0{return Some(Decision::HoldInvariant);}
 if o.shell_deficit==0{return Some(Decision::HoldHealthy);}
 if o.energy==0{return Some(Decision::HoldExhausted);}
 if o.reachable==0{return Some(Decision::HoldUnreachable);}
 Some(Decision::Trial(adaptive::recommend(j.state(),&derive(j)?).order))
}
#[cfg(test)]mod tests{
 use super::*;use crate::journal::Event;
 #[test]fn partition(){let counts=[Layer::Shell,Layer::Cortex,Layer::Constant].map(|l|(0..CELLS).filter(|&i|layer(i)==Some(l)).count());assert_eq!(counts,[98,26,1]);assert_eq!(layer(125),None);}
 #[test]fn decisions(){let a=Journal::new([100;3]);assert_eq!(regulate(&a),Some(Decision::HoldHealthy));let b=a.append(Event::Shock(vec![(0,40)])).unwrap();let o=observe(b.state());assert_eq!(o.shell_deficit,40);assert_eq!(o.cortex_deficit,0);assert_eq!(o.center_health,100);assert_eq!(o.reachable,1);assert!(matches!(regulate(&b),Some(Decision::Trial(_))));assert_eq!(a.events().len(),0);let c=Journal::new([0;3]).append(Event::Shock(vec![(0,1)])).unwrap();assert_eq!(regulate(&c),Some(Decision::HoldExhausted));}
}
