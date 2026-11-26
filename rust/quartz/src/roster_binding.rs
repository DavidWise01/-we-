use sha2::{Digest,Sha256};
use crate::{authentication::{self,Roster,Witness,SignedPacket},mesh::SiloId,integrity::Hash,temporal::Clock,evidence_gate::Packet};
pub const ROSTER_BYTES:usize=237;
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Binding{owner:SiloId,epoch:u64,previous:Hash,members:[Witness;3]}
impl Binding{
 pub fn genesis(owner:SiloId,mut members:[Witness;3])->Option<Self>{
 Roster::new(members)?;members.sort_by_key(|m|m.key);
 Some(Self{owner,epoch:0,previous:[0;32],members})
 }
 /// Identity roster stays frozen. Successors explicitly reaffirm the same membership.
 pub fn successor(&self)->Option<Self>{Some(Self{owner:self.owner,epoch:self.epoch.checked_add(1)?,previous:self.digest(),members:self.members})}
 pub fn encode(&self)->[u8;ROSTER_BYTES]{
 let mut b=[0;ROSTER_BYTES];b[..4].copy_from_slice(b"QR1\0");b[4]=self.owner.index()as u8;b[5..13].copy_from_slice(&self.epoch.to_be_bytes());b[13..45].copy_from_slice(&self.previous);
 for (i,m) in self.members.iter().enumerate(){let p=45+i*64;b[p..p+32].copy_from_slice(&m.key);b[p+32..p+64].copy_from_slice(&m.root);}b
 }
 pub fn digest(&self)->Hash{let mut h=Sha256::new();h.update(b"quartz/QR1/v1\0");h.update(self.encode());h.finalize().into()}
 pub fn decode(owner:SiloId,b:&[u8],expected:Hash)->Option<Self>{
 if b.len()!=ROSTER_BYTES||&b[..4]!=b"QR1\0"||b[4]as usize!=owner.index(){return None;}
 let epoch=u64::from_be_bytes(b[5..13].try_into().ok()?);let previous:Hash=b[13..45].try_into().ok()?;
 if (epoch==0)!=(previous==[0;32]){return None;}
 let mut members=[Witness{key:[0;32],root:[0;32]};3];
 for (i,m) in members.iter_mut().enumerate(){let p=45+i*64;m.key=b[p..p+32].try_into().ok()?;m.root=b[p+32..p+64].try_into().ok()?;}
 let mut canonical=Self::genesis(owner,members)?;canonical.epoch=epoch;canonical.previous=previous;
 if canonical.encode().as_slice()!=b||canonical.digest()!=expected{return None;}Some(canonical)
 }
 pub fn owner(&self)->SiloId{self.owner}
 pub fn members(&self)->&[Witness;3]{&self.members}
 pub fn verify(&self,now:Clock,p:&SignedPacket)->Option<Packet>{authentication::verify(&Roster::new(self.members)?,self.owner,now,p)}
}
pub const MAX_BINDINGS:usize=4096;
/// Validate the complete pinned chain; a standalone digest does not prove ancestry.
pub fn restore(owner:SiloId,records:&[[u8;ROSTER_BYTES]],expected:Hash)->Option<Binding>{
 if records.is_empty()||records.len()>MAX_BINDINGS{return None;}
 let mut prior:Option<Binding>=None;
 for (i,b) in records.iter().enumerate(){let mut h=Sha256::new();h.update(b"quartz/QR1/v1\0");h.update(b);let next=Binding::decode(owner,b,h.finalize().into())?;
 if next.epoch!=i as u64{return None;}
 if let Some(p)=prior.as_ref(){if p.successor().as_ref()!=Some(&next){return None;}}
 prior=Some(next);
 }let last=prior?;if last.digest()!=expected{return None;}Some(last)
}
#[cfg(test)]mod tests{
 use super::*;use ed25519_dalek::SigningKey;
 #[test]fn pinned_identity(){
 let owner=SiloId::new(0).unwrap();let members=std::array::from_fn(|i|Witness{key:SigningKey::from_bytes(&[(i+1)as u8;32]).verifying_key().to_bytes(),root:[(i+1)as u8;32]});
 let a=Binding::genesis(owner,members).unwrap();let mut reversed=members;reversed.reverse();assert_eq!(Binding::genesis(owner,reversed),Some(a.clone()));
 let b=a.successor().unwrap();let chain=[a.encode(),b.encode()];assert_eq!(restore(owner,&chain,b.digest()),Some(b.clone()));assert!(restore(owner,&chain[..1],b.digest()).is_none());
 assert!(restore(SiloId::new(1).unwrap(),&chain,b.digest()).is_none());
 let mut changed=b.clone();changed.members[0].root=[9;32];assert!(restore(owner,&[a.encode(),changed.encode()],changed.digest()).is_none());
 for n in 0..ROSTER_BYTES{assert!(Binding::decode(owner,&chain[1][..n],b.digest()).is_none());}
 assert!(Binding::genesis(owner,[members[0],members[0],members[2]]).is_none());
 }
}
