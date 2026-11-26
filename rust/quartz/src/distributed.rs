use crate::{recovery::Recovery,mesh::{route,SiloId,SILOS},pump_memory::{PumpMemory,Sample},adaptive, coupling::Coupling, witness::{geometry,conservation},cortex::observe,temporal::Clock};
pub const MAX_ROUNDS:usize=256;
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Round{pub clock:Clock,pub before:[u16;SILOS],pub after:[u16;SILOS],pub orders:[[usize;3];SILOS],pub shifts:[u16;SILOS]}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct ResultMesh{pub states:[Recovery;SILOS],pub rounds:Vec<Round>}
/// Synchronous synthetic snapshots, never remote execution. lambda in thousandths.
pub fn simulate(initial:&[Recovery;SILOS],lambda:u16,limit:usize)->Option<ResultMesh>{
 Coupling::new(lambda)?;
 let mut states=initial.clone();let mut memories:[[PumpMemory;3];SILOS]=std::array::from_fn(|_|std::array::from_fn(|_|PumpMemory::default()));
 let mut rounds=Vec::new();
 for t in 0..limit.min(MAX_ROUNDS){
  let before=std::array::from_fn(|i|observe(&states[i]).shell_deficit);
  if before.iter().all(|&p|p==0){break;}
  let mut orders=[[0,1,2];SILOS];let mut shifts=[0;SILOS];let mut next=states.clone();
  for i in 0..SILOS{
   let s=&states[i];let o=observe(s);if o.center_health!=100||o.cortex_deficit!=0{return None;}
   let local=adaptive::recommend(s,&memories[i]);let mut order=local.order;
   let mut sum=0u32;let mut n=0u32;
   for j in 0..SILOS{if route(SiloId::new(j as u8)?,SiloId::new(i as u8)?){sum+=u32::from(before[j]);n+=1;}}
   let mean=if n==0{before[i]}else{(sum/n)as u16};
   let shift=(u32::from(mean.saturating_sub(before[i]).min(8))*u32::from(lambda)/1000)as u16;
   if before[i]>0&&before[i]+shift>=adaptive::PRESSURE_THRESHOLD&&!local.high_pressure{
    let e=s.energy();let start=(s.tick()%3)as usize;order.sort_by_key(|&p|(e[p]==0,u32::MAX-e[p],memories[i][p].spent(),(p+3-start)%3));
   }
   orders[i]=order;shifts[i]=shift;
   if before[i]==0||o.energy==0||o.reachable==0{continue;}
   let b=s.ordered_step(order)?;if !geometry(s,&b)||!conservation(s,&b){return None;}
   for p in 0..3{let spent=u8::try_from(s.energy()[p].checked_sub(b.energy()[p])?).ok()?;memories[i][p].record(Sample{spent,unused:8u8.checked_sub(spent)?,pressure:before[i]});}
   next[i]=b;
  }
  let after=std::array::from_fn(|i|observe(&next[i]).shell_deficit);
  if after==before{break;}
  rounds.push(Round{clock:Clock::new(t as u64),before,after,orders,shifts});states=next;
 }
 Some(ResultMesh{states,rounds})
}
#[cfg(test)]mod tests{
 use super::*;
 #[test]fn isolation_and_replay(){
 let mut a=std::array::from_fn(|_|Recovery::new([10,40,90]));a[0]=a[0].shock(&[(0,20)]).unwrap();a[4]=a[4].shock(&[(0,100)]).unwrap();
 let before=a.clone();let z=simulate(&a,0,1).unwrap();let c=simulate(&a,1000,1).unwrap();
 assert_eq!(z.rounds[0].shifts,[0;5]);assert_eq!(c.rounds[0].shifts[0],8);assert_eq!(c.rounds[0].orders[0],[2,1,0]);assert_eq!(a,before);
 assert_eq!(simulate(&a,1000,1),Some(c));assert!(simulate(&a,1001,1).is_none());
 let mut isolated=a.clone();isolated[4]=Recovery::new([10,40,90]);assert_eq!(simulate(&isolated,0,1).unwrap().states[0],z.states[0]);
 }
}
