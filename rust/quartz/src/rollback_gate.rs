use std::path::Path;
use crate::{mesh::SiloId,integrity::Hash,roster_binding::Binding,external_pin::{self,Pin},checkpoint_frame::Frame};
pub const REFERENCE_BYTES:usize=109;
/// A trusted reference must originate outside the candidate archive.
/// This type does not authenticate the reference's acquisition or establish freshness.
#[derive(Clone,Copy,Debug,PartialEq,Eq)]
pub struct Reference{pub owner:SiloId,pub count:u64,pub genesis:Hash,pub external:Hash,pub head:Hash}
impl Reference{
 pub fn encode(self)->[u8;REFERENCE_BYTES]{let mut b=[0;REFERENCE_BYTES];b[..4].copy_from_slice(b"QK1\0");b[4]=self.owner.index()as u8;b[5..13].copy_from_slice(&self.count.to_be_bytes());b[13..45].copy_from_slice(&self.genesis);b[45..77].copy_from_slice(&self.external);b[77..109].copy_from_slice(&self.head);b}
 pub fn decode(b:&[u8])->Option<Self>{if b.len()!=REFERENCE_BYTES||&b[..4]!=b"QK1\0"{return None;}let r=Self{owner:SiloId::new(b[4])?,count:u64::from_be_bytes(b[5..13].try_into().ok()?),genesis:b[13..45].try_into().ok()?,external:b[45..77].try_into().ok()?,head:b[77..109].try_into().ok()?};if r.count==0||r.count>256||r.genesis==[0;32]||r.external==[0;32]||r.head==[0;32]||r.genesis==r.external{return None;}Some(r)}
}
#[derive(Clone,Copy,Debug,PartialEq,Eq)]
pub enum Fault{InvalidReference,Identity,Stale,UnpinnedFuture,Fork,MalformedChain,Verification}
/// Read-only preflight. Success is not authentication.
pub fn preflight(reference:&Reference,local:&Binding,external:&Binding,pins:&[Pin])->Result<(),Fault>{
 if Reference::decode(&reference.encode()).as_ref()!=Some(reference){return Err(Fault::InvalidReference);}
 if local.owner()!=reference.owner||external.owner()!=reference.owner||local.digest()!=reference.genesis||external.digest()!=reference.external{return Err(Fault::Identity);}
 let n=pins.len()as u64;if n<reference.count{return Err(Fault::Stale);}if n>reference.count{return Err(Fault::UnpinnedFuture);}
 if pins.last().map(Pin::digest)!=Some(reference.head){return Err(Fault::Fork);}
 let mut previous=[0;32];let mut count=0;
 for(i,p)in pins.iter().enumerate(){let c=&p.claim;if Pin::decode(&p.encode()).as_ref()!=Some(p)||c.owner!=reference.owner||c.genesis!=reference.genesis||c.external!=reference.external||c.index!=i as u64||c.previous!=previous||c.count<=count{return Err(Fault::MalformedChain);}previous=p.digest();count=c.count;}
 Ok(())
}
/// Never promote a newer candidate or accept an older authentic history.
/// Full signatures, archive and temporal ancestry remain mandatory.
pub fn verify_current(dir:&Path,archive:&Path,local:&Binding,external:&Binding,reference:&Reference,pins:&[Pin])->Result<Vec<Frame>,Fault>{
 preflight(reference,local,external,pins)?;
 external_pin::verify(dir,archive,local,external,reference.external,pins,reference.head).ok_or(Fault::Verification)
}
#[cfg(test)]mod tests{
 use super::*;use crate::{authentication::Witness,external_pin::Claim};use ed25519_dalek::{SigningKey,Signer};
 #[test]fn signed_history_challenges(){
 for i in 0..5{let owner=SiloId::new(i).unwrap();let keys:[SigningKey;6]=std::array::from_fn(|j|SigningKey::from_bytes(&[(j+1)as u8;32]));let roster=|offset:usize|Binding::genesis(owner,std::array::from_fn(|j|Witness{key:keys[offset+j].verifying_key().to_bytes(),root:[(offset+j+1)as u8;32]})).unwrap();let local=roster(0);let external=roster(3);
 let sign=|claim:Claim|{let signatures=std::array::from_fn(|j|{let w=external.members()[j];keys.iter().find(|k|k.verifying_key().to_bytes()==w.key).unwrap().sign(&claim.signing_bytes(w.root)).to_bytes()});Pin{claim,signatures}};
 let make=|index:u64,previous:Hash|sign(Claim{owner,index,count:index+1,genesis:local.digest(),external:external.digest(),checkpoint:[index as u8+1;32],publication:[index as u8+2;32],rolling:[index as u8+3;32],previous});
 let a=make(0,[0;32]);let b=make(1,a.digest());let c=make(2,b.digest());let pins=[a.clone(),b.clone(),c.clone()];
 let reference=Reference{owner,count:2,genesis:local.digest(),external:external.digest(),head:b.digest()};
 assert_eq!(Reference::decode(&reference.encode()),Some(reference));assert_eq!(preflight(&reference,&local,&external,&pins[..2]),Ok(()));
 assert_eq!(preflight(&reference,&local,&external,&pins[..1]),Err(Fault::Stale));assert_eq!(preflight(&reference,&local,&external,&pins),Err(Fault::UnpinnedFuture));
 let mut alternate=b.claim.clone();alternate.checkpoint=[99;32];let fork=sign(alternate);assert_eq!(preflight(&reference,&local,&external,&[a.clone(),fork]),Err(Fault::Fork));
 assert_eq!(preflight(&reference,&local,&local,&pins[..2]),Err(Fault::Identity));
 assert_eq!(preflight(&reference,&local,&external,&[c.clone(),b.clone()]),Err(Fault::MalformedChain));
 let mut altered=b.clone();altered.signatures[0][0]^=1;assert_eq!(preflight(&reference,&local,&external,&[a.clone(),altered]),Err(Fault::Fork));
 for n in 0..REFERENCE_BYTES{assert!(Reference::decode(&reference.encode()[..n]).is_none());}
 let mut invalid=reference;invalid.count=0;assert_eq!(preflight(&invalid,&local,&external,&pins[..2]),Err(Fault::InvalidReference));
 // Synthetic signed pins cannot pass full archive verification without actual frames.
 let missing=std::env::temp_dir().join(format!("quartz-g70-missing-{}-{i}",std::process::id()));assert!(!missing.exists());
 assert!(matches!(verify_current(&missing,&missing,&local,&external,&reference,&pins[..2]),Err(Fault::Verification)));
 }}
}
