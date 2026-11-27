use std::{path::Path,fs::File,io::Read};
use sha2::{Digest,Sha256};
use ed25519_dalek::{Signature,VerifyingKey};
use crate::{mesh::SiloId,integrity::Hash,roster_binding::Binding,checkpoint_publication::{self,Marker},rolling_evidence::Rolling,signed_evidence::Evidence,checkpoint_frame::Frame};
pub const CLAIM_BYTES:usize=213;
pub const PIN_BYTES:usize=405;
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Claim{pub owner:SiloId,pub index:u64,pub count:u64,pub genesis:Hash,pub external:Hash,pub checkpoint:Hash,pub publication:Hash,pub rolling:Hash,pub previous:Hash}
fn distinct(local:&Binding,external:&Binding)->bool{
 local.owner()==external.owner()&&external.encode()[5..13]==[0;8]&&local.members().iter().all(|a|external.members().iter().all(|b|a.key!=b.key&&a.root!=b.root))
}
impl Claim{
 pub fn encode(&self)->[u8;CLAIM_BYTES]{let mut b=[0;CLAIM_BYTES];b[..4].copy_from_slice(b"QN1\0");b[4]=self.owner.index()as u8;b[5..13].copy_from_slice(&self.index.to_be_bytes());b[13..21].copy_from_slice(&self.count.to_be_bytes());for(i,h)in [self.genesis,self.external,self.checkpoint,self.publication,self.rolling,self.previous].iter().enumerate(){let p=21+i*32;b[p..p+32].copy_from_slice(h);}b}
 pub fn signing_bytes(&self,root:Hash)->Vec<u8>{let mut b=b"quartz/QN1/witness/v1\0".to_vec();b.extend_from_slice(&self.encode());b.extend_from_slice(&root);b}
 /// Read the actual published marker and reconstruct the complete pinned prefix.
 pub fn prepare(dir:&Path,archive:&Path,local:&Binding,external:&Binding,external_pin:Hash,count:usize,publication:Hash,previous:Hash)->Option<Self>{
 if !distinct(local,external)||external.digest()!=external_pin||count==0||count>256||(count==1)!=(previous==[0;32]){return None;}
 let frames=checkpoint_publication::recover(dir,archive,local.owner(),local.digest(),count,publication).ok()?;
 let f=frames.last()?;if &f.binding!=local{return None;}
 let mut bytes=Vec::new();File::open(dir.join(format!("{:016x}.qy1",count-1))).ok()?.take(118).read_to_end(&mut bytes).ok()?;
 let m=Marker::decode(&bytes)?;if m.digest()!=publication||m.checkpoint!=f.checkpoint.digest(){return None;}
 let mut rolling=Rolling::genesis(local)?;for b in f.published.iter().skip(1){rolling=rolling.advance(local,&Evidence::decode(b)?)?;}
 let mut h=Sha256::new();h.update(b"quartz/QN1/rolling/v1\0");h.update(rolling.encode());
 Some(Self{owner:local.owner(),index:(count-1)as u64,count:rolling.count(),genesis:local.digest(),external:external_pin,checkpoint:m.checkpoint,publication,rolling:h.finalize().into(),previous})
 }
}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Pin{pub claim:Claim,pub signatures:[[u8;64];3]}
impl Pin{
 pub fn encode(&self)->[u8;PIN_BYTES]{let mut b=[0;PIN_BYTES];b[..CLAIM_BYTES].copy_from_slice(&self.claim.encode());for(i,s)in self.signatures.iter().enumerate(){let p=CLAIM_BYTES+i*64;b[p..p+64].copy_from_slice(s);}b}
 pub fn digest(&self)->Hash{let mut h=Sha256::new();h.update(b"quartz/QN1/v1\0");h.update(self.encode());h.finalize().into()}
 pub fn decode(b:&[u8])->Option<Self>{if b.len()!=PIN_BYTES||&b[..4]!=b"QN1\0"{return None;}let hash=|n:usize|->Option<Hash>{b[21+n*32..53+n*32].try_into().ok()};let claim=Claim{owner:SiloId::new(b[4])?,index:u64::from_be_bytes(b[5..13].try_into().ok()?),count:u64::from_be_bytes(b[13..21].try_into().ok()?),genesis:hash(0)?,external:hash(1)?,checkpoint:hash(2)?,publication:hash(3)?,rolling:hash(4)?,previous:hash(5)?};if claim.index>=256||claim.count>4095||(claim.index==0)!=(claim.previous==[0;32]){return None;}let mut signatures=[[0;64];3];for(i,s)in signatures.iter_mut().enumerate(){let p=CLAIM_BYTES+i*64;*s=b[p..p+64].try_into().ok()?;}Some(Self{claim,signatures})}
 fn signed(&self,external:&Binding)->bool{if self.claim.external!=external.digest()||self.claim.owner!=external.owner(){return false;}for(i,w)in external.members().iter().enumerate(){let Ok(k)=VerifyingKey::from_bytes(&w.key)else{return false;};if k.verify_strict(&self.claim.signing_bytes(w.root),&Signature::from_bytes(&self.signatures[i])).is_err(){return false;}}true}
}
/// Independently retained expected digest is an input, never inferred from disk.
/// Distinct registered keys and roots do not prove actual independent custody.
pub fn verify(dir:&Path,archive:&Path,local:&Binding,external:&Binding,external_pin:Hash,pins:&[Pin],expected:Hash)->Option<Vec<Frame>>{
 if pins.is_empty()||pins.len()>256{return None;}let mut prev=[0;32];let mut count=0;
 for(i,p)in pins.iter().enumerate(){if p.claim.index!=i as u64||p.claim.count<=count||!p.signed(external)||Claim::prepare(dir,archive,local,external,external_pin,i+1,p.claim.publication,prev).as_ref()!=Some(&p.claim){return None;}prev=p.digest();count=p.claim.count;}
 if prev!=expected{return None;}checkpoint_publication::recover(dir,archive,local.owner(),local.digest(),pins.len(),pins.last()?.claim.publication).ok()
}
#[cfg(test)]mod tests{use super::*;use crate::authentication::Witness;use ed25519_dalek::{SigningKey,Signer};
 #[test]fn external_identity_and_framing(){
 let owner=SiloId::new(0).unwrap();let keys:[SigningKey;6]=std::array::from_fn(|i|SigningKey::from_bytes(&[(i+1)as u8;32]));
 let roster=|offset:usize|Binding::genesis(owner,std::array::from_fn(|i|Witness{key:keys[offset+i].verifying_key().to_bytes(),root:[(offset+i+1)as u8;32]})).unwrap();
 let local=roster(0);let external=roster(3);assert!(distinct(&local,&external));assert!(!distinct(&local,&local));
 let claim=Claim{owner,index:0,count:1,genesis:local.digest(),external:external.digest(),checkpoint:[1;32],publication:[2;32],rolling:[3;32],previous:[0;32]};
 let signatures=std::array::from_fn(|i|{let w=external.members()[i];keys.iter().find(|k|k.verifying_key().to_bytes()==w.key).unwrap().sign(&claim.signing_bytes(w.root)).to_bytes()});
 let p=Pin{claim,signatures};assert!(p.signed(&external));assert!(!p.signed(&local));assert_eq!(Pin::decode(&p.encode()),Some(p.clone()));for n in 0..PIN_BYTES{assert!(Pin::decode(&p.encode()[..n]).is_none());}let mut bad=p.clone();bad.signatures[0][0]^=1;assert!(!bad.signed(&external));bad=p.clone();bad.claim.rolling=[9;32];assert!(!bad.signed(&external));
 }}
