use crate::{mesh::Silo,selection::{self,Candidate,Outcome},journal::Policy};
pub const MAX_CASES:usize=64;
pub const MAX_STEPS:usize=256;
pub type History=Vec<Vec<(usize,u8)>>;
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Specialization{pub baseline:Candidate,pub eligible:Vec<Candidate>,pub recommendation:Option<Candidate>}
fn metrics(o:&Outcome)->[u64;4]{[o.deficit_sum,u64::from(o.final_deficit),o.spent.iter().map(|&x|u64::from(x)).sum(),u64::from(o.peak_gap)]}
fn valid(h:&[History])->bool{!h.is_empty()&&h.len()<=MAX_CASES&&h.iter().all(|x|!x.is_empty()&&x.len()<=MAX_STEPS&&x.iter().all(|d|d.len()<=98))}
fn improves(energy:[u32;3],cases:&[History],candidate:Candidate,baseline:Candidate)->Option<bool>{
 let mut strict=false;
 for h in cases{let a=metrics(&selection::evaluate(energy,h,candidate)?);let b=metrics(&selection::evaluate(energy,h,baseline)?);
 if a.iter().zip(b).any(|(&x,y)|x>y){return Some(false);}
 strict|=a.iter().zip(b).any(|(&x,y)|x<y);
 }Some(strict)
}
/// Advisory only. Separate exact histories do not establish independent statistical evidence.
pub fn specialize(s:&Silo,training:&[History],challenge:&[History])->Option<Specialization>{
 if !valid(training)||!valid(challenge)||training.iter().any(|x|challenge.contains(x)){return None;}
 let baseline=match s.journal().policy(){Policy::FixedV1=>Candidate::Fixed,Policy::RotatingV2=>Candidate::Rotating};
 let energy=s.journal().state().energy();let mut eligible=Vec::new();
 for candidate in [Candidate::Fixed,Candidate::Rotating,Candidate::Adaptive]{
 if candidate!=baseline&&improves(energy,training,candidate,baseline)?&&improves(energy,challenge,candidate,baseline)?{eligible.push(candidate);}
 }
 // Ambiguous winners hold rather than imposing a global tie-break.
 let recommendation=if eligible.len()==1{Some(eligible[0])}else{None};
 Some(Specialization{baseline,eligible,recommendation})
}
#[cfg(test)]mod tests{
 use super::*;use crate::mesh::mesh;
 #[test]fn separate_challenges_and_ambiguity(){
 let a=mesh([100;3],Policy::FixedV1);let before=a.clone();
 let training=vec![vec![vec![(0,1)];9]];let challenge=vec![vec![vec![(124,1)];12]];
 let x=specialize(&a[0],&training,&challenge).unwrap();
 assert!(x.eligible.contains(&Candidate::Rotating));assert!(x.eligible.contains(&Candidate::Adaptive));assert_eq!(x.recommendation,None);
 assert!(specialize(&a[0],&training,&training).is_none());
 let b=mesh([100;3],Policy::RotatingV2);assert_eq!(specialize(&b[0],&training,&challenge).unwrap().recommendation,None);
 assert_eq!(a,before);
 }
 #[test]fn exhausted(){let a=mesh([0;3],Policy::FixedV1);let t=vec![vec![vec![(0,1)]]];let c=vec![vec![vec![(124,2)]]];assert!(specialize(&a[0],&t,&c).unwrap().eligible.is_empty());}
}
