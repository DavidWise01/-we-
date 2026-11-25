use crate::{recovery::Recovery,pump_memory::{PumpMemory,Sample},adaptive::recommend,witness::{geometry,conservation},cortex::observe};
pub const MAX_TICKS:usize=256;
#[derive(Clone,Copy,Debug,PartialEq,Eq)]
pub enum Stop{Healthy,Exhausted,Unreachable,Invariant,NoProgress,Limit}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Record{pub order:[usize;3],pub before:u16,pub after:u16,pub spent:[u8;3]}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Simulation{pub state:Recovery,pub records:Vec<Record>,pub stop:Stop}
/// Shadow trajectory only. No journal mutation or operational authorization.
pub fn run(initial:&Recovery,limit:usize)->Option<Simulation>{
 let mut state=initial.clone();let mut memory:[PumpMemory;3]=std::array::from_fn(|_|PumpMemory::default());let mut records=Vec::new();
 let stop=loop{
  let o=observe(&state);
  if o.center_health!=100||o.cortex_deficit!=0{break Stop::Invariant;}
  if o.shell_deficit==0{break Stop::Healthy;}
  if o.energy==0{break Stop::Exhausted;}
  if o.reachable==0{break Stop::Unreachable;}
  if records.len()>=limit.min(MAX_TICKS){break Stop::Limit;}
  let plan=recommend(&state,&memory);
  let next=state.ordered_step(plan.order)?;
  if !geometry(&state,&next)||!conservation(&state,&next){break Stop::Invariant;}
  let after=observe(&next).shell_deficit;
  if after>=o.shell_deficit{break Stop::NoProgress;}
  let mut spent=[0u8;3];
  for p in 0..3{spent[p]=u8::try_from(state.energy()[p].checked_sub(next.energy()[p])?).ok()?;memory[p].record(Sample{spent:spent[p],unused:8u8.checked_sub(spent[p])?,pressure:o.shell_deficit});}
  records.push(Record{order:plan.order,before:o.shell_deficit,after,spent});state=next;
 };
 Some(Simulation{state,records,stop})
}
/// Replay every deterministic shadow decision; not an independent witness.
pub fn reconcile(initial:&Recovery,limit:usize,claim:&Simulation)->bool{run(initial,limit).as_ref()==Some(claim)}
#[cfg(test)]mod tests{
 use super::*;
 #[test]fn recovery(){let a=Recovery::new([100;3]).shock(&[(0,40)]).unwrap();let b=run(&a,256).unwrap();assert_eq!(b.stop,Stop::Healthy);assert_eq!(b.records.len(),2);assert_eq!(b.state.health()[0],100);assert_eq!(a.health()[0],60);assert!(reconcile(&a,256,&b));let mut bad=b.clone();bad.records[0].after+=1;assert!(!reconcile(&a,256,&bad));}
 #[test]fn bounds(){let a=Recovery::new([0;3]).shock(&[(0,40)]).unwrap();assert_eq!(run(&a,256).unwrap().stop,Stop::Exhausted);let b=Recovery::new([100;3]).shock(&[(0,40)]).unwrap();assert_eq!(run(&b,0).unwrap().stop,Stop::Limit);assert_eq!(run(&b,1).unwrap().stop,Stop::Limit);}
}
