use crate::temporal::{Clock,MAX_AGE};
use std::collections::BTreeMap;
pub const MAX_REPORTS:usize=32;
#[derive(Clone,Copy,Debug,PartialEq,Eq)]
pub struct Report{pub root:[u8;32],pub relay:u8,pub observed:Clock,pub subject:[u8;32],pub value:u16}
#[derive(Clone,Copy,Debug,PartialEq,Eq)]
pub enum Verdict{Insufficient,Contradiction,ConsistentDeclared,Invalid}
/// Declared roots only. No authentication or execution authority.
pub fn reconcile(now:Clock,subject:[u8;32],reports:&[Report])->Verdict{
 if reports.len()>MAX_REPORTS{return Verdict::Invalid;}
 let mut roots=BTreeMap::new();
 for r in reports{
  if r.subject!=subject||r.root==[0;32]||r.value>9800{return Verdict::Invalid;}
  if !now.age(r.observed).is_some_and(|a|a<=MAX_AGE){continue;}
  if let Some(prior)=roots.insert(r.root,r.value){if prior!=r.value{return Verdict::Contradiction;}}
 }
 let mut values=roots.values();
 if let Some(first)=values.next(){if values.any(|v|v!=first){return Verdict::Contradiction;}}
 if roots.len()<3{Verdict::Insufficient}else{Verdict::ConsistentDeclared}
}
#[cfg(test)]mod tests{
 use super::*;
 fn report(root:u8,relay:u8,value:u16,t:u64)->Report{Report{root:[root;32],relay,observed:Clock::new(t),subject:[9;32],value}}
 #[test]fn ancestry(){
 let now=Clock::new(360);let a=report(1,0,20,359);let mirror=report(1,1,20,359);let b=report(2,2,20,359);let c=report(3,3,20,359);
 assert_eq!(reconcile(now,[9;32],&[a,mirror,b]),Verdict::Insufficient);
 assert_eq!(reconcile(now,[9;32],&[a,mirror,b,c]),Verdict::ConsistentDeclared);
 assert_eq!(reconcile(now,[9;32],&[a,b,report(3,3,21,359)]),Verdict::Contradiction);
 assert_eq!(reconcile(now,[9;32],&[a,report(1,1,21,359)]),Verdict::Contradiction);
 assert_eq!(reconcile(Clock::new(392),[9;32],&[a,b,c]),Verdict::Insufficient);
 assert_eq!(reconcile(now,[8;32],&[a,b,c]),Verdict::Invalid);
 }
}
