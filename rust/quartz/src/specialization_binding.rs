use sha2::{Digest,Sha256};
use ed25519_dalek::{Signature,VerifyingKey};
use crate::{mesh::{Silo,SiloId},integrity::Hash,roster_binding::Binding,signed_evidence::Evidence,transition_binding::Transition,transition_containment::{self,Decision},quarantine_chain::{self,Record},epochs::{self,Epoch},state_commitment,temporal::Clock};
pub const CLAIM_BYTES:usize=205;
pub const ADVISORY_BYTES:usize=397;
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Claim{pub owner:SiloId,pub index:u64,pub roster:Hash,pub state:Hash,pub transition:Hash,pub containment:Hash,pub epoch:Hash,pub previous:Hash}
impl Claim{
 /// Recompute the accepted containment successor and the complete specialization history.
 /// The resulting advice cannot change policy or authorize an action.
 pub fn prepare(binding:&Binding,prior:&Silo,next:&Silo,source:&Silo,e:&Evidence,t:&Transition,records:&[Record],head:Hash,history:&[Epoch],epoch_head:Hash,previous:Hash)->Option<Self>{
 let owner=binding.owner();if records.len()<2||history.is_empty(){return None;}
 let before=&records[..records.len()-1];let before_head=before.last()?.link.digest;
 let staged=transition_containment::stage_transition(binding,prior,next,source,e,t,t.digest(),Clock::new(t.claim.at),before,before_head)?;
 if staged.decision!=Decision::Accepted||&staged.record!=records.last()?{return None;}
 let gate=quarantine_chain::restore(owner,records,head)?;
 if gate.quarantined(source.observation().source)||!epochs::verify(owner,history,epoch_head){return None;}
 let last=history.last()?;if last.journal!=next.journal().encode(){return None;}
 let index=(history.len()-1)as u64;
 if (index==0)!=(previous==[0;32]){return None;}
 Some(Self{owner,index,roster:binding.digest(),state:state_commitment::commitment(next)?,transition:t.digest(),containment:head,epoch:epoch_head,previous})
 }
 pub fn encode(&self)->[u8;CLAIM_BYTES]{let mut b=[0;CLAIM_BYTES];b[..4].copy_from_slice(b"QL1\0");b[4]=self.owner.index()as u8;b[5..13].copy_from_slice(&self.index.to_be_bytes());for(i,h)in [self.roster,self.state,self.transition,self.containment,self.epoch,self.previous].iter().enumerate(){let p=13+i*32;b[p..p+32].copy_from_slice(h);}b}
 pub fn signing_bytes(&self,root:Hash)->Vec<u8>{let mut b=b"quartz/QL1/witness/v1\0".to_vec();b.extend_from_slice(&self.encode());b.extend_from_slice(&root);b}
}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Advisory{pub claim:Claim,pub signatures:[[u8;64];3]}
impl Advisory{
 pub fn encode(&self)->[u8;ADVISORY_BYTES]{let mut b=[0;ADVISORY_BYTES];b[..CLAIM_BYTES].copy_from_slice(&self.claim.encode());for(i,s)in self.signatures.iter().enumerate(){let p=CLAIM_BYTES+i*64;b[p..p+64].copy_from_slice(s);}b}
 pub fn digest(&self)->Hash{let mut h=Sha256::new();h.update(b"quartz/QL1/v1\0");h.update(self.encode());h.finalize().into()}
 pub fn decode(b:&[u8])->Option<Self>{if b.len()!=ADVISORY_BYTES||&b[..4]!=b"QL1\0"{return None;}let claim=Claim{owner:SiloId::new(b[4])?,index:u64::from_be_bytes(b[5..13].try_into().ok()?),roster:b[13..45].try_into().ok()?,state:b[45..77].try_into().ok()?,transition:b[77..109].try_into().ok()?,containment:b[109..141].try_into().ok()?,epoch:b[141..173].try_into().ok()?,previous:b[173..205].try_into().ok()?};let mut signatures=[[0;64];3];for(i,s)in signatures.iter_mut().enumerate(){let p=CLAIM_BYTES+i*64;*s=b[p..p+64].try_into().ok()?;}Some(Self{claim,signatures})}
 pub fn verify(&self,binding:&Binding,prior:&Silo,next:&Silo,source:&Silo,e:&Evidence,t:&Transition,records:&[Record],head:Hash,history:&[Epoch],epoch_head:Hash,previous:Hash,expected:Hash)->bool{
 if self.digest()!=expected||Claim::prepare(binding,prior,next,source,e,t,records,head,history,epoch_head,previous).as_ref()!=Some(&self.claim){return false;}
 for(i,w)in binding.members().iter().enumerate(){let Ok(k)=VerifyingKey::from_bytes(&w.key)else{return false;};if k.verify_strict(&self.claim.signing_bytes(w.root),&Signature::from_bytes(&self.signatures[i])).is_err(){return false;}}true
 }
}
#[cfg(test)]mod tests{
 use super::*;use crate::{authentication::Witness,mesh::mesh,journal::{Policy,Event},temporal::TimedObservation,signed_evidence,transition_binding,containment::Gate};use ed25519_dalek::{SigningKey,Signer};
 #[test]fn bound_advisory(){
 let keys:[SigningKey;3]=std::array::from_fn(|i|SigningKey::from_bytes(&[(i+1)as u8;32]));
 let members=std::array::from_fn(|i|Witness{key:keys[i].verifying_key().to_bytes(),root:[(i+1)as u8;32]});
 for policy in [Policy::FixedV1,Policy::RotatingV2]{let a=mesh([100;3],policy);for i in 0..5{
 let prior=a[i].successor(Event::Shock(vec![(0,40)])).unwrap();let next=prior.successor(Event::Recover).unwrap();let source=a[if i==4{0}else{4}].successor(Event::Shock(vec![(0,20)])).unwrap();let owner=prior.observation().source;let binding=Binding::genesis(owner,members).unwrap();let now=Clock::new(359);
 let sign=|j:usize,b:&[u8]|keys.iter().find(|k|k.verifying_key().to_bytes()==binding.members()[j].key).unwrap().sign(b).to_bytes();
 let message=TimedObservation{observed:now,observation:source.observation()};let signatures=std::array::from_fn(|j|sign(j,&signed_evidence::signing_bytes(&binding,&message,binding.members()[j].root)));let e=Evidence{recipient:owner,roster:binding.digest(),message,signatures};
 let claim=transition_binding::Claim::prepare(&binding,now,&prior,&next,&source,&e).unwrap();let signatures=std::array::from_fn(|j|sign(j,&claim.signing_bytes(binding.members()[j].root)));let t=Transition{claim,signatures};
 let mut records=vec![quarantine_chain::append(owner,&[],[0;32],&Gate::new(owner)).unwrap()];let staged=transition_containment::stage_transition(&binding,&prior,&next,&source,&e,&t,t.digest(),now,&records,records[0].link.digest).unwrap();assert_eq!(staged.decision,Decision::Accepted);records.push(staged.record);let head=records[1].link.digest;
 let training=vec![vec![vec![(0,1)];3]];let challenge=vec![vec![vec![(124,2)];4]];let epoch=epochs::append(&next,&[],[0;32],&training,&challenge).unwrap();let eh=epoch.link.digest;let history=[epoch];
 let claim=Claim::prepare(&binding,&prior,&next,&source,&e,&t,&records,head,&history,eh,[0;32]).unwrap();let signatures=std::array::from_fn(|j|sign(j,&claim.signing_bytes(binding.members()[j].root)));let advice=Advisory{claim,signatures};let digest=advice.digest();
 assert_eq!(Advisory::decode(&advice.encode()),Some(advice.clone()));assert!(advice.verify(&binding,&prior,&next,&source,&e,&t,&records,head,&history,eh,[0;32],digest));
 assert!(!advice.verify(&binding,&prior,&next,&source,&e,&t,&records[..1],head,&history,eh,[0;32],digest));
 assert!(!advice.verify(&binding,&prior,&next,&source,&e,&t,&records,head,&history,[9;32],[0;32],digest));
 let mut bad=advice.clone();bad.signatures[0][0]^=1;assert!(!bad.verify(&binding,&prior,&next,&source,&e,&t,&records,head,&history,eh,[0;32],bad.digest()));
 assert_eq!(next.journal().policy(),policy);
 for n in 0..ADVISORY_BYTES{assert!(Advisory::decode(&advice.encode()[..n]).is_none());}
 }}
 }
}
