use sha2::{Digest,Sha256};
use crate::{mesh::{Silo,SiloId},journal::Journal,integrity::{Hash,Link},specialization::{self,History,Specialization},selection::Candidate};
pub const MAX_EPOCHS:usize=256;
pub const MAX_EVENTS:usize=4096;
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Epoch{pub owner:SiloId,pub journal:String,pub training:Vec<History>,pub challenge:Vec<History>,pub decision:Specialization,pub link:Link}
fn tag(c:Candidate)->u8{match c{Candidate::Fixed=>0,Candidate::Rotating=>1,Candidate::Adaptive=>2}}
fn history(h:&mut Sha256,cases:&[History])->Option<()>{
 if cases.is_empty()||cases.len()>64{return None;}h.update((cases.len() as u16).to_be_bytes());
 for c in cases{if c.is_empty()||c.len()>256{return None;}h.update((c.len()as u16).to_be_bytes());for d in c{if d.len()>98{return None;}h.update((d.len()as u16).to_be_bytes());for &(i,v) in d{if i>=125||v>100{return None;}h.update([i as u8,v]);}}}Some(())
}
fn payload(e:&Epoch)->Option<Hash>{
 if e.journal.len()>1_048_576||e.decision.eligible.len()>3{return None;}
 let mut h=Sha256::new();h.update(b"quartz/specialization-epoch/v1\0");h.update([e.owner.index()as u8]);h.update((e.journal.len()as u32).to_be_bytes());h.update(e.journal.as_bytes());
 history(&mut h,&e.training)?;history(&mut h,&e.challenge)?;
 h.update([tag(e.decision.baseline),e.decision.eligible.len()as u8]);for &c in &e.decision.eligible{h.update([tag(c)]);}
 h.update([e.decision.recommendation.map(tag).unwrap_or(255)]);Some(h.finalize().into())
}
fn reconstruct(e:&Epoch)->Option<Silo>{
 if e.journal.len()>1_048_576||e.journal.bytes().filter(|&b|b==b'\n').count()>MAX_EVENTS+1{return None;}
 let j=Journal::decode(&e.journal)?;let n=j.events().len()as u64;Silo::from_journal(e.owner,j,n)
}
/// Verify every decision by re-executing local evaluation, not trusting recorded recommendation.
pub fn verify(owner:SiloId,epochs:&[Epoch],expected:Hash)->bool{
 if epochs.len()>MAX_EPOCHS{return false;}let mut head=[0;32];let mut prior:Option<&str>=None;
 for (i,e) in epochs.iter().enumerate(){
 if e.owner!=owner||prior.is_some_and(|p|!e.journal.starts_with(p)){return false;}
 let Some(s)=reconstruct(e)else{return false;};let Some(d)=payload(e)else{return false;};
 if specialization::specialize(&s,&e.training,&e.challenge).as_ref()!=Some(&e.decision)||e.link!=Link::new(i as u64,head,d){return false;}
 head=e.link.digest;prior=Some(&e.journal);
 }head==expected
}
/// Return an advisory successor; never modify the source journal or earlier epochs.
pub fn append(s:&Silo,epochs:&[Epoch],expected:Hash,training:&[History],challenge:&[History])->Option<Epoch>{
 let owner=s.observation().source;
 if epochs.len()>=MAX_EPOCHS||!verify(owner,epochs,expected)||s.journal().events().len()>MAX_EVENTS{return None;}
 let journal=s.journal().encode();if journal.len()>1_048_576||epochs.last().is_some_and(|e|!journal.starts_with(&e.journal)){return None;}
 let decision=specialization::specialize(s,training,challenge)?;
 let mut e=Epoch{owner,journal,training:training.to_vec(),challenge:challenge.to_vec(),decision,link:Link::new(0,[0;32],[0;32])};
 e.link=Link::new(epochs.len()as u64,expected,payload(&e)?);Some(e)
}
#[cfg(test)]mod tests{
 use super::*;use crate::{mesh::mesh,journal::{Policy,Event}};
 #[test]fn sealed_history(){
 let a=mesh([100;3],Policy::FixedV1);let s=&a[0];let before=s.clone();let owner=s.observation().source;
 let t=vec![vec![vec![(0,1)];9]];let c=vec![vec![vec![(124,1)];12]];
 let e=append(s,&[],[0;32],&t,&c).unwrap();let next=s.successor(Event::Shock(vec![(0,20)])).unwrap();
 let f=append(&next,&[e.clone()],e.link.digest,&t,&c).unwrap();let head=f.link.digest;let chain=vec![e,f];assert!(verify(owner,&chain,head));assert!(!verify(owner,&chain[..1],head));
 let mut bad=chain.clone();bad[1].decision.recommendation=Some(Candidate::Fixed);let digest=payload(&bad[1]).unwrap();bad[1].link=Link::new(1,bad[0].link.digest,digest);assert!(!verify(owner,&bad,bad[1].link.digest));
 assert!(append(s,&chain,head,&t,&c).is_none());assert!(append(&a[1],&chain,head,&t,&c).is_none());assert_eq!(*s,before);
 }
}
