use sha2::{Digest,Sha256};
use crate::{integrity::Hash,roster_binding::Binding,signed_evidence::Evidence,mesh::SiloId};
pub const MAX_RECORDS:u64=4095;
pub const HEAD_BYTES:usize=77;
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Rolling{owner:SiloId,roster:Hash,count:u64,head:Hash}
impl Rolling{
 pub fn genesis(b:&Binding)->Option<Self>{if b.encode()[5..13]!=[0;8]{return None;}let roster=b.digest();let mut h=Sha256::new();h.update(b"quartz/QZ1/genesis/v1\0");h.update(roster);Some(Self{owner:b.owner(),roster,count:0,head:h.finalize().into()})}
 pub fn advance(&self,b:&Binding,e:&Evidence)->Option<Self>{
 if self.owner!=b.owner()||self.roster!=b.digest()||self.count>=MAX_RECORDS{return None;}
 e.verify_history(b)?;
 let count=self.count.checked_add(1)?;let mut h=Sha256::new();h.update(b"quartz/QZ1/step/v1\0");h.update(self.roster);h.update(count.to_be_bytes());h.update(self.head);h.update(e.encode());
 Some(Self{owner:self.owner,roster:self.roster,count,head:h.finalize().into()})
 }
 pub fn count(&self)->u64{self.count}
 pub fn head(&self)->Hash{self.head}
 pub fn encode(&self)->[u8;HEAD_BYTES]{let mut b=[0;HEAD_BYTES];b[..4].copy_from_slice(b"QZ1\0");b[4]=self.owner.index()as u8;b[5..13].copy_from_slice(&self.count.to_be_bytes());b[13..45].copy_from_slice(&self.roster);b[45..77].copy_from_slice(&self.head);b}
 /// No unchecked restoration: rebuild from original authenticated records.
 pub fn restore(b:&Binding,evidence:&[Evidence],expected:&[u8])->Option<Self>{if evidence.len()>MAX_RECORDS as usize||expected.len()!=HEAD_BYTES{return None;}let mut s=Self::genesis(b)?;for e in evidence{s=s.advance(b,e)?;}if s.encode().as_slice()!=expected{return None;}Some(s)}
}
#[cfg(test)]mod tests{
 use super::*;use crate::{authentication::Witness,mesh::mesh,journal::Policy,temporal::{Clock,TimedObservation},signed_evidence};use ed25519_dalek::{SigningKey,Signer};
 #[test]fn rolling_ancestry(){
 let keys:[SigningKey;3]=std::array::from_fn(|j|SigningKey::from_bytes(&[(j+1)as u8;32]));
 let members=std::array::from_fn(|j|Witness{key:keys[j].verifying_key().to_bytes(),root:[(j+1)as u8;32]});
 let a=mesh([100;3],Policy::FixedV1);
 for i in 0..5{let owner=a[i].observation().source;let b=Binding::genesis(owner,members).unwrap();
 let make=|tick:u64|{let message=TimedObservation{observed:Clock::new(tick),observation:a[if i==4{0}else{4}].observation()};let signatures=std::array::from_fn(|j|{let w=b.members()[j];keys.iter().find(|k|k.verifying_key().to_bytes()==w.key).unwrap().sign(&signed_evidence::signing_bytes(&b,&message,w.root)).to_bytes()});Evidence{recipient:owner,roster:b.digest(),message,signatures}};
 let ev=[make(1),make(2),make(3)];let g=Rolling::genesis(&b).unwrap();let x=g.advance(&b,&ev[0]).unwrap();let y=x.advance(&b,&ev[1]).unwrap();let z=y.advance(&b,&ev[2]).unwrap();let pin=z.encode();
 assert_eq!(Rolling::restore(&b,&ev,&pin),Some(z));assert!(Rolling::restore(&b,&ev[..2],&pin).is_none());
 let mut swapped=ev.clone();swapped.swap(0,1);assert!(Rolling::restore(&b,&swapped,&pin).is_none());
 let mut changed=ev.clone();changed[1]=make(4);assert!(Rolling::restore(&b,&changed,&pin).is_none());
 let mut bad=ev[0].clone();bad.signatures[0][0]^=1;assert!(g.advance(&b,&bad).is_none());
 let other=Binding::genesis(a[(i+1)%5].observation().source,members).unwrap();assert!(g.advance(&other,&ev[0]).is_none());
 for n in 0..HEAD_BYTES{assert!(Rolling::restore(&b,&ev,&pin[..n]).is_none());}
 assert_eq!(g.count(),0);assert_eq!(x.count(),1);
 }}
}
