use sha2::{Digest,Sha256};
use ed25519_dalek::{Signature,VerifyingKey};
use crate::{mesh::{Silo,SiloId},journal::Event,temporal::Clock,roster_binding::Binding,signed_evidence::Evidence,integrity::Hash,state_commitment,witness::{geometry,conservation},cortex::observe};
pub const CLAIM_BYTES:usize=173;
pub const TRANSITION_BYTES:usize=365;
fn evidence_digest(e:&Evidence)->Hash{let mut h=Sha256::new();h.update(b"quartz/QT1/evidence/v1\0");h.update(e.encode());h.finalize().into()}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Claim{pub owner:SiloId,pub at:u64,pub roster:Hash,pub prior:Hash,pub successor:Hash,pub source:Hash,pub evidence:Hash}
impl Claim{
 /// One inherited-policy Recover event, not an adaptive or remote mutation.
 pub fn prepare(binding:&Binding,now:Clock,prior:&Silo,next:&Silo,source:&Silo,e:&Evidence)->Option<Self>{
 let owner=binding.owner();if prior.observation().source!=owner||next.observation().source!=owner{return None;}
 e.verify_fresh(binding,now)?;
 if source.observation()!=e.message.observation||prior.successor(Event::Recover).as_ref()!=Some(next){return None;}
 let a=prior.journal().state();let b=next.journal().state();
 if !geometry(a,b)||!conservation(a,b)||observe(b).shell_deficit>=observe(a).shell_deficit{return None;}
 Some(Self{owner,at:now.cycle()*360+now.phase(),roster:binding.digest(),prior:state_commitment::commitment(prior)?,successor:state_commitment::commitment(next)?,source:state_commitment::commitment(source)?,evidence:evidence_digest(e)})
 }
 pub fn encode(&self)->[u8;CLAIM_BYTES]{let mut b=[0;CLAIM_BYTES];b[..4].copy_from_slice(b"QT1\0");b[4]=self.owner.index()as u8;b[5..13].copy_from_slice(&self.at.to_be_bytes());for(i,h)in [self.roster,self.prior,self.successor,self.source,self.evidence].iter().enumerate(){let p=13+i*32;b[p..p+32].copy_from_slice(h);}b}
 pub fn signing_bytes(&self,root:Hash)->Vec<u8>{let mut b=b"quartz/QT1/witness/v1\0".to_vec();b.extend_from_slice(&self.encode());b.extend_from_slice(&root);b}
}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Transition{pub claim:Claim,pub signatures:[[u8;64];3]}
impl Transition{
 pub fn encode(&self)->[u8;TRANSITION_BYTES]{let mut b=[0;TRANSITION_BYTES];b[..CLAIM_BYTES].copy_from_slice(&self.claim.encode());for(i,s)in self.signatures.iter().enumerate(){let p=CLAIM_BYTES+i*64;b[p..p+64].copy_from_slice(s);}b}
 pub fn digest(&self)->Hash{let mut h=Sha256::new();h.update(b"quartz/QT1/v1\0");h.update(self.encode());h.finalize().into()}
 pub fn decode(b:&[u8])->Option<Self>{if b.len()!=TRANSITION_BYTES||&b[..4]!=b"QT1\0"{return None;}let claim=Claim{owner:SiloId::new(b[4])?,at:u64::from_be_bytes(b[5..13].try_into().ok()?),roster:b[13..45].try_into().ok()?,prior:b[45..77].try_into().ok()?,successor:b[77..109].try_into().ok()?,source:b[109..141].try_into().ok()?,evidence:b[141..173].try_into().ok()?};let mut signatures=[[0;64];3];for(i,s)in signatures.iter_mut().enumerate(){let p=CLAIM_BYTES+i*64;*s=b[p..p+64].try_into().ok()?;}Some(Self{claim,signatures})}
 /// Historical replay at the attested logical clock; no present admission authority.
 pub fn verify(&self,binding:&Binding,prior:&Silo,next:&Silo,source:&Silo,e:&Evidence,expected:Hash)->bool{
 if self.digest()!=expected||Claim::prepare(binding,Clock::new(self.claim.at),prior,next,source,e).as_ref()!=Some(&self.claim){return false;}
 for(i,w)in binding.members().iter().enumerate(){let Ok(k)=VerifyingKey::from_bytes(&w.key)else{return false;};if k.verify_strict(&self.claim.signing_bytes(w.root),&Signature::from_bytes(&self.signatures[i])).is_err(){return false;}}
 true
 }
}
#[cfg(test)]mod tests{
 use super::*;use crate::{authentication::Witness,mesh::mesh,journal::Policy,temporal::TimedObservation,signed_evidence};use ed25519_dalek::{SigningKey,Signer};
 #[test]fn signed_state_transition(){
 let keys:[SigningKey;3]=std::array::from_fn(|i|SigningKey::from_bytes(&[(i+1)as u8;32]));let members=std::array::from_fn(|i|Witness{key:keys[i].verifying_key().to_bytes(),root:[(i+1)as u8;32]});
 for policy in [Policy::FixedV1,Policy::RotatingV2]{let a=mesh([100;3],policy);for i in 0..5{
 let prior=a[i].successor(Event::Shock(vec![(0,40)])).unwrap();let next=prior.successor(Event::Recover).unwrap();let source=a[if i==4{0}else{4}].successor(Event::Shock(vec![(124,20)])).unwrap();
 let binding=Binding::genesis(prior.observation().source,members).unwrap();
 let sign=|j:usize,b:&[u8]|keys.iter().find(|k|k.verifying_key().to_bytes()==binding.members()[j].key).unwrap().sign(b).to_bytes();
 let message=TimedObservation{observed:Clock::new(359),observation:source.observation()};let signatures=std::array::from_fn(|j|sign(j,&signed_evidence::signing_bytes(&binding,&message,binding.members()[j].root)));
 let e=Evidence{recipient:binding.owner(),roster:binding.digest(),message,signatures};
 let claim=Claim::prepare(&binding,Clock::new(391),&prior,&next,&source,&e).unwrap();
 let signatures=std::array::from_fn(|j|sign(j,&claim.signing_bytes(binding.members()[j].root)));let t=Transition{claim,signatures};let head=t.digest();
 assert_eq!(Transition::decode(&t.encode()),Some(t.clone()));assert!(t.verify(&binding,&prior,&next,&source,&e,head));
 assert!(!t.verify(&binding,&prior,&prior,&source,&e,head));assert!(!t.verify(&binding,&prior,&next,&a[if i==4{0}else{4}],&e,head));
 assert!(Claim::prepare(&binding,Clock::new(392),&prior,&next,&source,&e).is_none());
 let mut bad=t.clone();bad.signatures[0][0]^=1;assert!(!bad.verify(&binding,&prior,&next,&source,&e,bad.digest()));
 for n in 0..TRANSITION_BYTES{assert!(Transition::decode(&t.encode()[..n]).is_none());}
 }}
 }
}
