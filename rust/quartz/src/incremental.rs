use sha2::{Digest,Sha256};
use ed25519_dalek::{Signature,VerifyingKey};
use crate::{roster_binding::Binding,signed_evidence::Evidence,custody::{Custody,MAX_EVIDENCE},integrity::Hash,filesystem,publication::Publication};
use std::path::Path;
/// Process-local verified evidence prefix. No serialization or unchecked constructor.
/// Historical disk integrity must still be audited separately.
#[derive(Clone)]
pub struct VerifiedPrefix{binding:Binding,bytes:Vec<u8>,count:u64,publication:Hash,custody:Hash,journal:Hash}
impl VerifiedPrefix{
 pub fn genesis(binding:&Binding)->Option<Self>{
 if binding.encode()[5..13]!=[0;8]{return None;}
 Some(Self{binding:binding.clone(),bytes:Vec::new(),count:0,publication:[0;32],custody:[0;32],journal:[0;32]})
 }
 pub fn count(&self)->u64{self.count}
 pub fn head(&self)->Hash{self.custody}
 /// Verify a single successor against the in-memory authenticated prefix.
 /// The supplied journal record is reconstructed from disk by the caller-facing method.
 pub fn advance(&self,dir:&Path,c:&Custody,expected:Hash)->Option<Self>{
 let count=self.count.checked_add(1)?;if count>filesystem::MAX_RECORDS as u64{return None;}
 let p=crate::publication::read_successor(dir,count,self.publication,c.claim.publication).ok()?;
 let record=filesystem::read_successor(dir,(count-1)as usize,self.journal,p.head).ok()?;
 self.advance_record(&p,&record,c,expected)
 }
 fn advance_record(&self,p:&Publication,r:&filesystem::Record,c:&Custody,expected:Hash)->Option<Self>{
 let count=self.count.checked_add(1)?;if count>filesystem::MAX_RECORDS as u64||p.count!=count||p.previous!=self.publication||r.link.previous!=self.journal||r.link.index!=count-1||r.link.digest!=p.head{return None;}
 let mut next=self.clone();
 if self.count==0{if r.payload.as_slice()!=self.binding.encode().as_slice(){return None;}}
 else{if self.bytes.len()/crate::signed_evidence::EVIDENCE_BYTES>=MAX_EVIDENCE{return None;}let e=Evidence::decode(&r.payload)?;e.verify_history(&self.binding)?;next.bytes.extend_from_slice(&e.encode());}
 let mut h=Sha256::new();h.update(b"quartz/QC1/evidence/v1\0");h.update((count-1).to_be_bytes());h.update(&next.bytes);let evidence:Hash=h.finalize().into();
 let claim=&c.claim;let publication=p.digest();
 if c.digest()!=expected||claim.owner!=self.binding.owner()||claim.roster!=self.binding.digest()||claim.publication_count!=count||claim.publication!=publication||claim.previous!=self.custody||claim.evidence!=evidence{return None;}
 for(i,w)in self.binding.members().iter().enumerate(){let k=VerifyingKey::from_bytes(&w.key).ok()?;k.verify_strict(&claim.signing_bytes(w.root),&Signature::from_bytes(&c.signatures[i])).ok()?;}
 next.count=count;next.publication=publication;next.custody=expected;next.journal=p.head;Some(next)
 }
}
