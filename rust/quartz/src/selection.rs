use crate::{adaptive::recommend,pump_memory::{PumpMemory,Sample},recovery::Recovery,CENTER};
#[derive(Clone,Copy,Debug,PartialEq,Eq)]
pub enum Candidate{Fixed,Rotating,Adaptive}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Outcome{pub deficit_sum:u64,pub final_deficit:u16,pub spent:[u32;3],pub peak_gap:u32}
fn deficit(s:&Recovery)->u16{s.health().iter().map(|&h|100-u16::from(h)).sum()}
pub fn evaluate(initial:[u32;3],history:&[Vec<(usize,u8)>],policy:Candidate)->Option<Outcome>{
 let mut s=Recovery::new(initial);let mut m:[PumpMemory;3]=std::array::from_fn(|_|PumpMemory::default());
 let mut area=0u64;let mut peak=0u32;
 for damage in history{
  let prior=s.shock(damage)?;let pressure=deficit(&prior);
  s=match policy{Candidate::Fixed=>prior.step(),Candidate::Rotating=>prior.rotating_step(),Candidate::Adaptive=>prior.ordered_step(recommend(&prior,&m).order)}?;
  let a=prior.energy();let b=s.energy();let mut total=0u16;
  for p in 0..3{let spent=u8::try_from(a[p].checked_sub(b[p])?).ok()?;let unused=8u8.checked_sub(spent)?;total+=u16::from(spent);m[p].record(Sample{spent,unused,pressure});}
  if pressure.checked_sub(deficit(&s))?!=total||s.health()[CENTER]!=100{return None;}
  area=area.checked_add(u64::from(deficit(&s)))?;
  let spent=std::array::from_fn::<_,3,_>(|p|initial[p]-b[p]);
  peak=peak.max(spent.iter().max()? - spent.iter().min()?);
 }
 Some(Outcome{deficit_sum:area,final_deficit:deficit(&s),spent:std::array::from_fn(|p|initial[p]-s.energy()[p]),peak_gap:peak})
}
/// Strict improvement in at least one metric against each baseline, no regression in any.
pub fn eligible(candidate:&Outcome,baselines:&[Outcome;2])->bool{
 let metrics=|o:&Outcome|[o.deficit_sum,u64::from(o.final_deficit),o.spent.iter().map(|&x|u64::from(x)).sum(),u64::from(o.peak_gap)];
 let c=metrics(candidate);baselines.iter().all(|b|{let b=metrics(b);c.iter().zip(b).all(|(&x,y)|x<=y)&&c.iter().zip(b).any(|(&x,y)|x<y)})
}
#[cfg(test)]mod tests{
 use super::*;
 #[test]fn equal_damage(){let h=vec![vec![(0,1)];9];let a=evaluate([10;3],&h,Candidate::Fixed).unwrap();let b=evaluate([10;3],&h,Candidate::Rotating).unwrap();let c=evaluate([10;3],&h,Candidate::Adaptive).unwrap();assert_eq!(a.spent,[9,0,0]);assert_eq!(b.spent,[3;3]);assert_eq!(b,c);assert!(!eligible(&c,&[a,b]));}
 #[test]fn deterministic(){for seed in 0..32usize{let h:Vec<_>=(0..48).map(|t|vec![(if (t+seed)%2==0{0}else{124},((t*7+seed)%80) as u8)]).collect();for p in [Candidate::Fixed,Candidate::Rotating,Candidate::Adaptive]{let a=evaluate([100,80,60],&h,p).unwrap();assert_eq!(Some(a),evaluate([100,80,60],&h,p));}}}
}
