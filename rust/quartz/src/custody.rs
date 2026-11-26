use sha2::{Digest,Sha256};
use ed25519_dalek::{Signature,VerifyingKey};
use crate::{mesh::SiloId,integrity::Hash,roster_binding::Binding,signed_evidence::Evidence};
pub const CUSTODY_BYTES:usize=333;
pub const MAX_EVIDENCE:usize=4096;
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Claim{pub owner:SiloId,pub publication_count:u64,pub publication:Hash,pub roster:Hash,pub evidence:Hash,pub previous:Hash}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Custody{pub claim:Claim,pub signatures:[[u8;64];3]}
/// Ordered, length-framed commitment; all retained observations must verify under the exact roster.
pub fn evidence_head(binding:&Binding,evidence:&[Evidence])->Option<Hash>{
 if evidence.len()>MAX_EVIDENCE{return None;}
 let mut h=Sha256::new();h.update(b"quartz/QC1/evidence/v1\0");h.update((evidence.len()as u64).to_be_bytes());
 for e in evidence{e.verify_history(binding)?;h.update(e.encode());}Some(h.finalize().into())
}
impl Claim{
 pub fn encode(&self)->[u8;141]{let mut b=[0;141];b[..4].copy_from_slice(b"QC1\0");b[4]=self.owner.index()as u8;b[5..13].copy_from_slice(&self.publication_count.to_be_bytes());b[13..45].copy_from_slice(&self.publication);b[45..77].copy_from_slice(&self.roster);b[77..109].copy_from_slice(&self.evidence);b[109..141].copy_from_slice(&self.previous);b}
 pub fn signing_bytes(&self,root:Hash)->Vec<u8>{let mut b=b"quartz/QC1/witness/v1\0".to_vec();b.extend_from_slice(&self.encode());b.extend_from_slice(&root);b}
}
impl Custody{
 pub fn encode(&self)->[u8;CUSTODY_BYTES]{let mut b=[0;CUSTODY_BYTES];b[..141].copy_from_slice(&self.claim.encode());for (i,s) in self.signatures.iter().enumerate(){let p=141+i*64;b[p..p+64].copy_from_slice(s);}b}
 pub fn digest(&self)->Hash{let mut h=Sha256::new();h.update(b"quartz/QC1/v1\0");h.update(self.encode());h.finalize().into()}
 pub fn decode(b:&[u8])->Option<Self>{
 if b.len()!=CUSTODY_BYTES||&b[..4]!=b"QC1\0"{return None;}
 let claim=Claim{owner:SiloId::new(b[4])?,publication_count:u64::from_be_bytes(b[5..13].try_into().ok()?),publication:b[13..45].try_into().ok()?,roster:b[45..77].try_into().ok()?,evidence:b[77..109].try_into().ok()?,previous:b[109..141].try_into().ok()?};
 let mut signatures=[[0;64];3];for(i,s)in signatures.iter_mut().enumerate(){let p=141+i*64;*s=b[p..p+64].try_into().ok()?;}Some(Self{claim,signatures})
 }
 /// Verify attestation against caller-pinned publication and predecessor. No authority is granted.
 pub fn verify(&self,binding:&Binding,evidence:&[Evidence],count:u64,publication:Hash,previous:Hash,expected:Hash)->bool{
 let c=&self.claim;
 if count==0||count>4096||publication==[0;32]||c.owner!=binding.owner()||c.roster!=binding.digest()||c.publication_count!=count||c.publication!=publication||c.previous!=previous||self.digest()!=expected||evidence_head(binding,evidence)!=Some(c.evidence){return false;}
 for(i,w)in binding.members().iter().enumerate(){let Ok(k)=VerifyingKey::from_bytes(&w.key)else{return false;};if k.verify_strict(&c.signing_bytes(w.root),&Signature::from_bytes(&self.signatures[i])).is_err(){return false;}}
 true
 }
 #[cfg(unix)]
 pub fn verify_disk(&self,dir:&std::path::Path,binding:&Binding,evidence:&[Evidence],count:u64,publication:Hash,previous:Hash,expected:Hash)->bool{
 if !self.verify(binding,evidence,count,publication,previous,expected){return false;}
 crate::publication::recover(dir,count,publication).is_ok()
 }
}
#[cfg(test)]mod tests{
 use super::*;use ed25519_dalek::{SigningKey,Signer};use crate::{authentication::Witness,mesh::mesh,journal::Policy,temporal::{Clock,TimedObservation},signed_evidence};
 #[test]fn custody_binding(){
 let keys:[SigningKey;3]=std::array::from_fn(|i|SigningKey::from_bytes(&[(i+1)as u8;32]));let members=std::array::from_fn(|i|Witness{key:keys[i].verifying_key().to_bytes(),root:[(i+1)as u8;32]});
 let a=mesh([100;3],Policy::FixedV1);let owner=a[0].observation().source;let binding=Binding::genesis(owner,members).unwrap();
 let sign=|i:usize,b:&[u8]|{let w=binding.members()[i];keys.iter().find(|k|k.verifying_key().to_bytes()==w.key).unwrap().sign(b).to_bytes()};
 let message=TimedObservation{observed:Clock::new(359),observation:a[4].observation()};
 let signatures=std::array::from_fn(|i|sign(i,&signed_evidence::signing_bytes(&binding,&message,binding.members()[i].root)));
 let e=Evidence{recipient:owner,roster:binding.digest(),message,signatures};let evidence=[e];
 let claim=Claim{owner,publication_count:1,publication:[7;32],roster:binding.digest(),evidence:evidence_head(&binding,&evidence).unwrap(),previous:[0;32]};
 let signatures=std::array::from_fn(|i|sign(i,&claim.signing_bytes(binding.members()[i].root)));let c=Custody{claim,signatures};let head=c.digest();
 assert_eq!(Custody::decode(&c.encode()),Some(c.clone()));assert!(c.verify(&binding,&evidence,1,[7;32],[0;32],head));
 assert!(!c.verify(&binding,&[],1,[7;32],[0;32],head));assert!(!c.verify(&binding,&evidence,1,[8;32],[0;32],head));assert!(!c.verify(&binding,&evidence,1,[7;32],[1;32],head));assert!(!c.verify(&binding,&evidence,1,[7;32],[0;32],[9;32]));
 let mut altered=c.clone();altered.signatures[1][0]^=1;assert!(!altered.verify(&binding,&evidence,1,[7;32],[0;32],altered.digest()));
 for n in 0..CUSTODY_BYTES{assert!(Custody::decode(&c.encode()[..n]).is_none());}
 }
}
