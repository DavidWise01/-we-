use crate::{mesh::{Silo,SiloId,route},selection::{self,Candidate,Outcome}};
pub const MAX_CASES:usize=64;
pub const MAX_STEPS:usize=256;
#[derive(Clone,Copy,Debug,PartialEq,Eq)]
pub struct Proposal{pub donor:SiloId,pub strategy:Candidate}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Evaluation{pub proposal:Proposal,pub cases:usize,pub improved:usize,pub eligible:bool}
/// Recipient-owned synthetic challenges. No donor memory, journal or energy is imported.
/// Eligibility is advisory; neither policy nor journal is mutated.
pub fn evaluate(recipient:&Silo,proposal:Proposal,cases:&[Vec<Vec<(usize,u8)>>])->Option<Evaluation>{
 if !route(proposal.donor,recipient.observation().source)||cases.is_empty()||cases.len()>MAX_CASES{return None;}
 let initial=recipient.journal().state().energy();
 let baseline=match recipient.journal().policy(){crate::journal::Policy::FixedV1=>Candidate::Fixed,crate::journal::Policy::RotatingV2=>Candidate::Rotating};
 let mut improved=0;let mut eligible=true;
 for h in cases{
  if h.is_empty()||h.len()>MAX_STEPS||h.iter().any(|d|d.len()>98){return None;}
  let b=selection::evaluate(initial,h,baseline)?;
  let c=selection::evaluate(initial,h,proposal.strategy)?;
  let metrics=|o:&Outcome|[o.deficit_sum,u64::from(o.final_deficit),o.spent.iter().map(|&x|u64::from(x)).sum(),u64::from(o.peak_gap)];
  let b=metrics(&b);let c=metrics(&c);
  if c.iter().zip(b).any(|(&x,y)|x>y){eligible=false;}
  else if c.iter().zip(b).any(|(&x,y)|x<y){improved+=1;}
 }
 Some(Evaluation{proposal,cases:cases.len(),improved,eligible:eligible&&improved>0})
}
#[cfg(test)]mod tests{
 use super::*;use crate::{mesh::mesh,journal::{Policy,Event}};
 #[test]fn local_selection(){
 let a=mesh([100;3],Policy::FixedV1);let s=a[0].successor(Event::Shock(vec![(124,5)])).unwrap();let before=s.clone();
 let h=vec![vec![vec![(0,1)];9]];
 let p=Proposal{donor:SiloId::new(4).unwrap(),strategy:Candidate::Rotating};
 let v=evaluate(&s,p,&h).unwrap();assert!(v.eligible);assert_eq!(v.improved,1);assert_eq!(s,before);
 assert!(!evaluate(&s,Proposal{strategy:Candidate::Fixed,..p},&h).unwrap().eligible);
 assert!(evaluate(&s,Proposal{donor:SiloId::new(1).unwrap(),..p},&h).is_none());
 assert!(evaluate(&s,p,&[]).is_none());
 let b=mesh([100;3],Policy::RotatingV2);
 assert!(!evaluate(&b[0],Proposal{strategy:Candidate::Fixed,..p},&h).unwrap().eligible);
 }
}
