use std::path::Path;
use sha2::{Digest,Sha256};
use ed25519_dalek::{Signature,VerifyingKey};
use crate::{mesh::{Silo,SiloId},integrity::Hash,roster_binding::Binding,signed_evidence::Evidence,transition_binding::Transition,specialization_binding::Advisory,quarantine_chain::Record,epochs::Epoch,custody::Custody,state_commitment,cross_ledger,publication,filesystem};
pub const CLAIM_BYTES:usize=301;
pub const CHECKPOINT_BYTES:usize=493;
pub struct Inputs<'a>{
 pub binding:&'a Binding,pub prior:&'a Silo,pub next:&'a Silo,pub source:&'a Silo,pub evidence:&'a Evidence,pub transition:&'a Transition,pub containment:&'a [Record],pub epochs:&'a [Epoch],pub advisory:&'a Advisory,pub custody:&'a [Custody],pub directory:&'a Path
}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Claim{pub owner:SiloId,pub index:u64,pub roster:Hash,pub state:Hash,pub transition:Hash,pub containment:Hash,pub epoch:Hash,pub advisory:Hash,pub custody:Hash,pub publication:Hash,pub previous:Hash}
impl Claim{
 /// Single genesis roster; each checkpoint binds the last published QE1.
 /// Predecessor verification is required separately for subsequent checkpoints.
 pub fn prepare(i:&Inputs<'_>,genesis:Hash,previous:Hash,previous_advisory:Hash)->Option<Self>{
 let owner=i.binding.owner();if i.binding.digest()!=genesis{return None;}
 let q=i.containment.last()?.link.digest;let e=i.epochs.last()?.link.digest;let c=i.custody.last()?;let ch=c.digest();let p=c.claim.publication;
 if !cross_ledger::verify(i.directory,owner,genesis,i.custody,ch){return None;}
 let published=publication::recover(i.directory,c.claim.publication_count,p).ok()?;
 let records=filesystem::read_prefix(i.directory,i.custody.len(),published.head).ok()?;
 if records.len()<2||records.last()?.payload.as_slice()!=i.evidence.encode().as_slice(){return None;}
 if !i.advisory.verify(i.binding,i.prior,i.next,i.source,i.evidence,i.transition,i.containment,q,i.epochs,e,previous_advisory,i.advisory.digest()){return None;}
 let index=i.advisory.claim.index;if (index==0)!=(previous==[0;32]){return None;}
 Some(Self{owner,index,roster:genesis,state:state_commitment::commitment(i.next)?,transition:i.transition.digest(),containment:q,epoch:e,advisory:i.advisory.digest(),custody:ch,publication:p,previous})
 }
 pub fn encode(&self)->[u8;CLAIM_BYTES]{let mut b=[0;CLAIM_BYTES];b[..4].copy_from_slice(b"QU1\0");b[4]=self.owner.index()as u8;b[5..13].copy_from_slice(&self.index.to_be_bytes());for(i,h)in [self.roster,self.state,self.transition,self.containment,self.epoch,self.advisory,self.custody,self.publication,self.previous].iter().enumerate(){let p=13+i*32;b[p..p+32].copy_from_slice(h);}b}
 pub fn signing_bytes(&self,root:Hash)->Vec<u8>{let mut b=b"quartz/QU1/witness/v1\0".to_vec();b.extend_from_slice(&self.encode());b.extend_from_slice(&root);b}
}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Checkpoint{pub claim:Claim,pub signatures:[[u8;64];3]}
impl Checkpoint{
 pub fn encode(&self)->[u8;CHECKPOINT_BYTES]{let mut b=[0;CHECKPOINT_BYTES];b[..CLAIM_BYTES].copy_from_slice(&self.claim.encode());for(i,s)in self.signatures.iter().enumerate(){let p=CLAIM_BYTES+i*64;b[p..p+64].copy_from_slice(s);}b}
 pub fn digest(&self)->Hash{let mut h=Sha256::new();h.update(b"quartz/QU1/v1\0");h.update(self.encode());h.finalize().into()}
 pub fn decode(b:&[u8])->Option<Self>{if b.len()!=CHECKPOINT_BYTES||&b[..4]!=b"QU1\0"{return None;}let hash=|n:usize|->Option<Hash>{b[13+n*32..45+n*32].try_into().ok()};let claim=Claim{owner:SiloId::new(b[4])?,index:u64::from_be_bytes(b[5..13].try_into().ok()?),roster:hash(0)?,state:hash(1)?,transition:hash(2)?,containment:hash(3)?,epoch:hash(4)?,advisory:hash(5)?,custody:hash(6)?,publication:hash(7)?,previous:hash(8)?};let mut signatures=[[0;64];3];for(i,s)in signatures.iter_mut().enumerate(){let p=CLAIM_BYTES+i*64;*s=b[p..p+64].try_into().ok()?;}Some(Self{claim,signatures})}
 pub fn verify(&self,i:&Inputs<'_>,genesis:Hash,previous:Hash,previous_advisory:Hash,expected:Hash)->bool{
 if self.digest()!=expected||Claim::prepare(i,genesis,previous,previous_advisory).as_ref()!=Some(&self.claim){return false;}
 for(j,w)in i.binding.members().iter().enumerate(){let Ok(k)=VerifyingKey::from_bytes(&w.key)else{return false;};if k.verify_strict(&self.claim.signing_bytes(w.root),&Signature::from_bytes(&self.signatures[j])).is_err(){return false;}}true
 }
}
#[cfg(test)]mod tests{
 use super::*;
 #[test]fn canonical_boundary(){let c=Checkpoint{claim:Claim{owner:SiloId::new(0).unwrap(),index:0,roster:[1;32],state:[2;32],transition:[3;32],containment:[4;32],epoch:[5;32],advisory:[6;32],custody:[7;32],publication:[8;32],previous:[0;32]},signatures:[[0;64];3]};let b=c.encode();assert_eq!(Checkpoint::decode(&b),Some(c.clone()));for n in 0..CHECKPOINT_BYTES{assert!(Checkpoint::decode(&b[..n]).is_none());}for n in [13,45,77,109,141,173,205,237,269,301]{let mut changed=b;changed[n]^=1;assert_ne!(Checkpoint::decode(&changed).unwrap().digest(),c.digest());}}
}
