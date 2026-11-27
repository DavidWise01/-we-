use crate::{sovereign_checkpoint::{Checkpoint,Inputs},integrity::Hash,mesh::{SiloId,Silo},state_commitment,epochs};
pub const MAX_CHECKPOINTS:usize=epochs::MAX_EPOCHS;
pub struct Entry<'a>{pub checkpoint:&'a Checkpoint,pub inputs:Inputs<'a>}
fn state_continues(old:&Silo,new:&Silo)->bool{old==new||state_commitment::extends(old,new)}
fn strict_prefix<T:PartialEq>(old:&[T],new:&[T])->bool{new.len()>old.len()&&new.starts_with(old)}
/// Verify every signed QU1 from genesis to an externally pinned head.
/// All slices are full historical prefixes, not merely caller-declared digests.
/// Local shocks may occur between checkpoints; inherited journal ancestry must remain exact.
pub fn verify(owner:SiloId,genesis:Hash,entries:&[Entry<'_>],expected:Hash)->bool{
 if entries.is_empty()||entries.len()>MAX_CHECKPOINTS{return false;}
 let mut previous=[0;32];let mut advisory=[0;32];
 for (n,entry) in entries.iter().enumerate(){
 let c=entry.checkpoint;let i=&entry.inputs;
 if c.claim.owner!=owner||i.binding.owner()!=owner||c.claim.index!=n as u64||i.epochs.len()!=n+1{return false;}
 if n>0{
 let prior=&entries[n-1];let p=&prior.inputs;
 if !state_continues(p.next,i.prior)||!state_commitment::extends(p.next,i.next)||!strict_prefix(p.containment,i.containment)||!strict_prefix(p.epochs,i.epochs)||!strict_prefix(p.custody,i.custody)||i.transition.claim.at<p.transition.claim.at{return false;}
 }
 let digest=c.digest();if !c.verify(i,genesis,previous,advisory,digest){return false;}
 previous=digest;advisory=i.advisory.digest();
 }
 previous==expected
}
#[cfg(test)]mod tests{
 use super::*;use crate::{mesh::mesh,journal::{Policy,Event}};
 #[test]fn prefix_and_state_boundaries(){
 assert!(strict_prefix(&[1,2],&[1,2,3]));assert!(!strict_prefix(&[1,2],&[1,2]));assert!(!strict_prefix(&[1,2],&[1,3,4]));assert!(!strict_prefix(&[1,2],&[1]));
 for policy in [Policy::FixedV1,Policy::RotatingV2]{let a=mesh([100;3],policy);for s in &a{
 let p=s.successor(Event::Shock(vec![(0,40)])).unwrap();let n=p.successor(Event::Recover).unwrap();let fork=s.successor(Event::Shock(vec![(0,41)])).unwrap();
 assert!(state_continues(&p,&p));assert!(state_continues(&p,&n));assert!(!state_continues(&n,&p));assert!(!state_continues(&p,&fork));assert!(!state_continues(&p,&a[(s.observation().source.index()+1)%5]));
 }}
 assert!(!verify(SiloId::new(0).unwrap(),[0;32],&[],[0;32]));
 }
}
