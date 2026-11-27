use std::path::Path;
use sha2::{Digest,Sha256};
use crate::{mesh::{Silo,SiloId},integrity::{Hash,Link},roster_binding::Binding,signed_evidence::Evidence,transition_binding::Transition,specialization_binding::Advisory,sovereign_checkpoint::{Checkpoint,Inputs},quarantine_chain::{self,Record},epochs::{self,Epoch},specialization::History,state_commitment,journal::Journal,custody::Custody};
pub const MAX_FRAME:usize=32*1024*1024;
#[derive(Clone)]
pub struct Frame{pub checkpoint:Checkpoint,pub binding:Binding,pub prior:Silo,pub next:Silo,pub source:Silo,pub evidence:Evidence,pub transition:Transition,pub containment:Vec<Record>,pub epochs:Vec<Epoch>,pub advisory:Advisory,pub custody:Vec<Custody>,pub published:Vec<Vec<u8>>}
struct Writer(Vec<u8>);
impl Writer{
 fn put(&mut self,b:&[u8])->Option<()>{if self.0.len().checked_add(b.len())?>MAX_FRAME{return None;}self.0.extend_from_slice(b);Some(())}
 fn num(&mut self,n:usize)->Option<()>{self.put(&u32::try_from(n).ok()?.to_be_bytes())}
 fn blob(&mut self,b:&[u8])->Option<()>{self.num(b.len())?;self.put(b)}
 fn link(&mut self,l:&Link)->Option<()>{self.put(&l.index.to_be_bytes())?;self.put(&l.previous)?;self.put(&l.payload)?;self.put(&l.digest)}
 fn histories(&mut self,h:&[History])->Option<()>{if h.is_empty()||h.len()>64{return None;}self.num(h.len())?;for c in h{if c.is_empty()||c.len()>256{return None;}self.num(c.len())?;for d in c{if d.len()>98{return None;}self.num(d.len())?;for &(i,v) in d{if i>=125||v>100{return None;}self.put(&[i as u8,v])?;}}}Some(())}
}
struct Reader<'a>{b:&'a[u8],p:usize}
impl<'a> Reader<'a>{
 fn take(&mut self,n:usize)->Option<&'a[u8]>{let end=self.p.checked_add(n)?;let b=self.b.get(self.p..end)?;self.p=end;Some(b)}
 fn hash(&mut self)->Option<Hash>{self.take(32)?.try_into().ok()}
 fn num(&mut self,max:usize)->Option<usize>{let n=u32::from_be_bytes(self.take(4)?.try_into().ok()?)as usize;if n>max{return None;}Some(n)}
 fn blob(&mut self,max:usize)->Option<&'a[u8]>{let n=self.num(max)?;self.take(n)}
 fn link(&mut self)->Option<Link>{Some(Link{index:u64::from_be_bytes(self.take(8)?.try_into().ok()?),previous:self.hash()?,payload:self.hash()?,digest:self.hash()?})}
 fn histories(&mut self)->Option<Vec<History>>{let n=self.num(64)?;if n==0{return None;}let mut out=Vec::new();for _ in 0..n{let m=self.num(256)?;if m==0{return None;}let mut c=Vec::new();for _ in 0..m{let k=self.num(98)?;let mut d=Vec::new();for _ in 0..k{let b=self.take(2)?;if b[0]>=125||b[1]>100{return None;}d.push((b[0]as usize,b[1]));}c.push(d);}out.push(c);}Some(out)}
}
pub fn digest(b:&[u8])->Hash{let mut h=Sha256::new();h.update(b"quartz/QX1/v1\0");h.update(b);h.finalize().into()}
impl Frame{
 pub fn inputs<'a>(&'a self,directory:&'a Path)->Inputs<'a>{Inputs{binding:&self.binding,prior:&self.prior,next:&self.next,source:&self.source,evidence:&self.evidence,transition:&self.transition,containment:&self.containment,epochs:&self.epochs,advisory:&self.advisory,custody:&self.custody,directory}}
 pub fn encode(&self)->Option<Vec<u8>>{
 let mut w=Writer(b"QX1\0".to_vec());w.put(&self.checkpoint.encode())?;w.put(&self.binding.encode())?;
 for s in [&self.prior,&self.next,&self.source]{w.blob(&state_commitment::encode(s)?)?;}
 w.put(&self.evidence.encode())?;w.put(&self.transition.encode())?;w.put(&self.advisory.encode())?;
 if self.containment.len()>4096||self.epochs.len()>256||self.custody.len()>4096||self.published.len()!=self.custody.len(){return None;}
 w.num(self.containment.len())?;for r in &self.containment{if r.bytes.len()!=264{return None;}w.put(&r.bytes)?;w.link(&r.link)?;}
 w.num(self.epochs.len())?;for e in &self.epochs{if e.owner!=self.binding.owner()||e.journal.len()>1_048_576{return None;}w.blob(e.journal.as_bytes())?;w.histories(&e.training)?;w.histories(&e.challenge)?;w.link(&e.link)?;}
 w.num(self.custody.len())?;for c in &self.custody{w.put(&c.encode())?;}
 for (i,b) in self.published.iter().enumerate(){if b.len()!=if i==0{237}else{264}{return None;}w.put(b)?;}
 Some(w.0)
 }
 /// A pinned frame digest protects serialized bytes; this is not publication authority.
 pub fn decode(b:&[u8],expected:Hash)->Option<Self>{
 if b.len()>MAX_FRAME||digest(b)!=expected{return None;}let mut r=Reader{b,p:0};if r.take(4)?!=b"QX1\0"{return None;}
 let checkpoint=Checkpoint::decode(r.take(493)?)?;let owner=checkpoint.claim.owner;let binding=Binding::decode(owner,r.take(237)?,checkpoint.claim.roster)?;
 // Prior/source commitments come from the signed transition, so read their bytes first.
 let prior_bytes=r.blob(state_commitment::MAX_FRAME)?;let next_bytes=r.blob(state_commitment::MAX_FRAME)?;let source_bytes=r.blob(state_commitment::MAX_FRAME)?;
 let evidence=Evidence::decode(r.take(264)?)?;let transition=Transition::decode(r.take(365)?)?;let advisory=Advisory::decode(r.take(397)?)?;
 let prior=state_commitment::restore(owner,prior_bytes,transition.claim.prior)?;let next=state_commitment::restore(owner,next_bytes,checkpoint.claim.state)?;let source=state_commitment::restore(evidence.message.observation.source,source_bytes,transition.claim.source)?;
 let mut containment=Vec::new();for _ in 0..r.num(4096)?{containment.push(Record{bytes:r.take(264)?.to_vec(),link:r.link()?});}quarantine_chain::restore(owner,&containment,checkpoint.claim.containment)?;
 let mut history=Vec::new();let mut head=[0;32];for _ in 0..r.num(256)?{let text=std::str::from_utf8(r.blob(1_048_576)?).ok()?;if text.bytes().filter(|&x|x==b'\n').count()>4097{return None;}let j=Journal::decode(text)?;let seq=j.events().len()as u64;let s=Silo::from_journal(owner,j,seq)?;let training=r.histories()?;let challenge=r.histories()?;let link=r.link()?;let e=epochs::append(&s,&history,head,&training,&challenge)?;if e.link!=link{return None;}head=link.digest;history.push(e);}
 if head!=checkpoint.claim.epoch{return None;}
 let mut custody=Vec::new();let count=r.num(4096)?;for _ in 0..count{custody.push(Custody::decode(r.take(333)?)?);}
 let mut published=Vec::new();for i in 0..count{published.push(r.take(if i==0{237}else{264})?.to_vec());}
 let f=Self{checkpoint,binding,prior,next,source,evidence,transition,containment,epochs:history,advisory,custody,published};
 if r.p!=b.len()||f.encode()?.as_slice()!=b{return None;}Some(f)
 }
 /// Full verification against the retained filesystem and independent expected QU1 head.
 pub fn verify(&self,dir:&Path,genesis:Hash,previous:Hash,previous_advisory:Hash,expected:Hash)->bool{
 let Some(c)=self.custody.last()else{return false;};let Ok(p)=crate::publication::recover(dir,c.claim.publication_count,c.claim.publication)else{return false;};let Ok(records)=crate::filesystem::read_prefix(dir,self.custody.len(),p.head)else{return false;};
 records.len()==self.published.len()&&records.iter().zip(&self.published).all(|(r,b)|&r.payload==b)&&self.checkpoint.verify(&self.inputs(dir),genesis,previous,previous_advisory,expected)
 }
}
#[cfg(test)]mod tests{use super::*;#[test]fn framing_limits(){let mut w=Writer(Vec::new());assert!(w.blob(b"abc").is_some());let mut r=Reader{b:&w.0,p:0};assert_eq!(r.blob(3),Some(b"abc".as_slice()));assert!(r.take(1).is_none());let mut r=Reader{b:&w.0,p:0};assert!(r.blob(2).is_none());assert!(Frame::decode(b"QX1\0",digest(b"QX1\0")).is_none());}}
