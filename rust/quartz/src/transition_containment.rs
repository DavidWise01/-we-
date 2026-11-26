use crate::{mesh::Silo,roster_binding::Binding,signed_evidence::Evidence,transition_binding::Transition,containment::{Gate,Fault},quarantine_chain::{self,Record},integrity::Hash,temporal::Clock,coupling::Coupling};
#[derive(Clone,Debug,PartialEq,Eq)]
pub enum Decision{Accepted,Rejected(Fault)}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Staged{pub decision:Decision,pub record:Record}
/// A staged result is not a durable commit or permission to mutate state.
pub fn stage(binding:&Binding,prior:&Silo,now:Clock,e:&Evidence,records:&[Record],head:Hash)->Option<Staged>{
 let owner=binding.owner();if prior.observation().source!=owner{return None;}
 let mut gate=quarantine_chain::restore(owner,records,head)?;
 let packet=e.verify_fresh(binding,now)?;
 let decision=match gate.trial(prior,now,Coupling::new(0)?,&[packet]){
 Ok(_)=>Decision::Accepted,Err(f)=>Decision::Rejected(f)};
 let record=quarantine_chain::append(owner,records,head,&gate)?;
 Some(Staged{decision,record})
}
/// Require a verified QT1 and a fresh admission decision against the pinned gate history.
pub fn stage_transition(binding:&Binding,prior:&Silo,next:&Silo,source:&Silo,e:&Evidence,t:&Transition,expected:Hash,now:Clock,records:&[Record],head:Hash)->Option<Staged>{
 if t.claim.at!=now.cycle()*360+now.phase()||!t.verify(binding,prior,next,source,e,expected){return None;}
 stage(binding,prior,now,e,records,head)
}
/// Recompute the exact staged result instead of trusting a caller-declared decision.
pub fn verify_staged(binding:&Binding,prior:&Silo,now:Clock,e:&Evidence,records:&[Record],head:Hash,claimed:&Staged)->bool{
 stage(binding,prior,now,e,records,head).as_ref()==Some(claimed)
}
#[cfg(test)]mod tests{
 use super::*;use crate::{authentication::Witness,mesh::mesh,journal::{Policy,Event},temporal::TimedObservation,signed_evidence,transition_binding::Claim};use ed25519_dalek::{SigningKey,Signer};
 #[test]fn authenticated_quarantine_restart(){
 let keys:[SigningKey;3]=std::array::from_fn(|i|SigningKey::from_bytes(&[(i+1)as u8;32]));
 let members=std::array::from_fn(|i|Witness{key:keys[i].verifying_key().to_bytes(),root:[(i+1)as u8;32]});
 for policy in [Policy::FixedV1,Policy::RotatingV2]{let a=mesh([100;3],policy);for i in 0..5{
 let prior=a[i].successor(Event::Shock(vec![(0,40)])).unwrap();let next=prior.successor(Event::Recover).unwrap();let remote=&a[if i==4{0}else{4}];
 let source=remote.successor(Event::Shock(vec![(0,20)])).unwrap();let conflict=remote.successor(Event::Shock(vec![(0,21)])).unwrap();
 let owner=prior.observation().source;let binding=Binding::genesis(owner,members).unwrap();let now=Clock::new(359);
 let sign=|j:usize,b:&[u8]|keys.iter().find(|k|k.verifying_key().to_bytes()==binding.members()[j].key).unwrap().sign(b).to_bytes();
 let make=|s:&Silo|{let message=TimedObservation{observed:now,observation:s.observation()};let signatures=std::array::from_fn(|j|sign(j,&signed_evidence::signing_bytes(&binding,&message,binding.members()[j].root)));Evidence{recipient:owner,roster:binding.digest(),message,signatures}};
 let e=make(&source);let bad=make(&conflict);
 let claim=Claim::prepare(&binding,now,&prior,&next,&source,&e).unwrap();let signatures=std::array::from_fn(|j|sign(j,&claim.signing_bytes(binding.members()[j].root)));let t=Transition{claim,signatures};
 let mut records=vec![quarantine_chain::append(owner,&[],[0;32],&Gate::new(owner)).unwrap()];let head=records[0].link.digest;
 let accepted=stage_transition(&binding,&prior,&next,&source,&e,&t,t.digest(),now,&records,head).unwrap();assert_eq!(accepted.decision,Decision::Accepted);assert!(verify_staged(&binding,&prior,now,&e,&records,head,&accepted));
 records.push(accepted.record);let head=records.last().unwrap().link.digest;
 assert_eq!(stage(&binding,&prior,now,&e,&records,head).unwrap().decision,Decision::Rejected(Fault::Replay));
 let mut forged=bad.clone();forged.signatures[0][0]^=1;assert!(stage(&binding,&prior,now,&forged,&records,head).is_none());
 let rejected=stage(&binding,&prior,now,&bad,&records,head).unwrap();assert_eq!(rejected.decision,Decision::Rejected(Fault::Equivocation));records.push(rejected.record);
 let head=records.last().unwrap().link.digest;assert!(quarantine_chain::restore(owner,&records,head).unwrap().quarantined(source.observation().source));
 assert_eq!(stage_transition(&binding,&prior,&next,&source,&e,&t,t.digest(),now,&records,head).unwrap().decision,Decision::Rejected(Fault::Quarantined));
 assert!(stage(&binding,&prior,now,&e,&records[..2],head).is_none());
 }}
 }
}
