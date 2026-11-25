use crate::{journal::Journal,pump_memory::{derive,PumpMemory},recovery::Recovery};
pub const PRESSURE_THRESHOLD:u16=24;
#[derive(Clone,Copy,Debug,PartialEq,Eq)]
pub struct Recommendation{pub pressure:u16,pub order:[usize;3],pub high_pressure:bool}
pub fn recommend(state:&Recovery,memory:&[PumpMemory;3])->Recommendation{
 let pressure=state.health().iter().map(|&h|100u16-u16::from(h)).sum::<u16>();
 let high=pressure>=PRESSURE_THRESHOLD;let energy=state.energy();
 let start=(state.tick()%3) as usize;let mut order=[0,1,2];
 order.sort_by_key(|&p|(! (energy[p]>0),if high{u32::MAX-energy[p]}else{memory[p].spent()},memory[p].spent(),(p+3-start)%3));
 Recommendation{pressure,order,high_pressure:high}
}
pub fn trial(j:&Journal)->Option<(Recommendation,Recovery)>{
 let memory=derive(j)?;let plan=recommend(j.state(),&memory);
 Some((plan,j.state().ordered_step(plan.order)?))
}
#[cfg(test)]
mod tests{
 use super::*;use crate::{journal::{Event,Policy},CENTER};
 #[test]fn pressure_and_isolation(){
 let a=Journal::new([10,40,90]).append(Event::Shock(vec![(0,40)])).unwrap();
 let before=a.clone();let (p,b)=trial(&a).unwrap();assert_eq!(p.order,[2,1,0]);assert!(p.high_pressure);assert_eq!(p.pressure,40);assert_eq!(a,before);assert_eq!(b.health()[0],84);assert_eq!(b.health()[CENTER],100);
 assert_eq!(a.state().energy().iter().sum::<u32>()-b.energy().iter().sum::<u32>(),24);
 }
 #[test]fn low_pressure_memory(){
 let mut j=Journal::with_policy([100;3],Policy::FixedV1);
 j=j.append(Event::Shock(vec![(0,1)])).unwrap().append(Event::Recover).unwrap().append(Event::Shock(vec![(0,1)])).unwrap();
 let (p,b)=trial(&j).unwrap();assert_eq!(p.order,[1,2,0]);assert!(!p.high_pressure);assert_eq!(b.energy(),[99,99,100]);assert_eq!(trial(&j),trial(&Journal::decode(&j.encode()).unwrap()));
 assert!(j.state().ordered_step([0,0,2]).is_none());
 }
}
