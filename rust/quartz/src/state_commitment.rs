use sha2::{Digest,Sha256};
use crate::{mesh::{Silo,SiloId},journal::{Journal,Policy},integrity::Hash,CENTER,CONSTANT};
pub const MAX_EVENTS:usize=4096;
pub const MAX_JOURNAL:usize=1_048_576;
pub const HEADER:usize=167;
pub const MAX_FRAME:usize=HEADER+MAX_JOURNAL;
/// QS1 encodes owner, policy, sequence, tick, pump energies, protected
/// constant, all cell health values, and the complete canonical journal.
pub fn encode(s:&Silo)->Option<Vec<u8>>{
 let j=s.journal();let state=j.state();let o=s.observation();
 if j.events().len()>MAX_EVENTS||state.health()[CENTER]!=100{return None;}
 let text=j.encode();if text.len()>MAX_JOURNAL{return None;}
 let mut b=b"QS1\0".to_vec();b.push(o.source.index()as u8);
 b.push(match j.policy(){Policy::FixedV1=>0,Policy::RotatingV2=>1});
 b.extend_from_slice(&o.sequence.to_be_bytes());b.extend_from_slice(&state.tick().to_be_bytes());
 for e in state.energy(){b.extend_from_slice(&e.to_be_bytes());}
 b.extend_from_slice(&CONSTANT.to_be_bytes());b.extend_from_slice(state.health());
 b.extend_from_slice(&(text.len()as u32).to_be_bytes());b.extend_from_slice(text.as_bytes());Some(b)
}
pub fn digest(bytes:&[u8])->Hash{let mut h=Sha256::new();h.update(b"quartz/QS1/v1\0");h.update(bytes);h.finalize().into()}
pub fn commitment(s:&Silo)->Option<Hash>{Some(digest(&encode(s)?))}
/// Reconstruct from journal replay; compare every canonical state byte.
pub fn restore(owner:SiloId,b:&[u8],expected:Hash)->Option<Silo>{
 if b.len()<HEADER||b.len()>MAX_FRAME||&b[..4]!=b"QS1\0"||b[4]as usize!=owner.index()||digest(b)!=expected{return None;}
 let n=u32::from_be_bytes(b[163..167].try_into().ok()?)as usize;if n>MAX_JOURNAL||b.len()!=HEADER+n{return None;}
 let text=std::str::from_utf8(&b[HEADER..]).ok()?;
 if text.bytes().filter(|&x|x==b'\n').count()>MAX_EVENTS+1{return None;}
 let j=Journal::decode(text)?;if j.events().len()>MAX_EVENTS{return None;}
 let seq=u64::from_be_bytes(b[6..14].try_into().ok()?);let s=Silo::from_journal(owner,j,seq)?;
 if encode(&s)?.as_slice()!=b{return None;}Some(s)
}
/// Verify that a successor retains the exact prior journal and owner.
pub fn extends(prior:&Silo,next:&Silo)->bool{
 if prior.observation().source!=next.observation().source{return false;}
 if encode(prior).is_none()||encode(next).is_none(){return false;}
 next.journal().encode().starts_with(&prior.journal().encode())&&next.journal().events().len()>prior.journal().events().len()
}
#[cfg(test)]mod tests{
 use super::*;use crate::{mesh::mesh,journal::Event};
 #[test]fn state_replay_binding(){
 for policy in [Policy::FixedV1,Policy::RotatingV2]{
 let a=mesh([100;3],policy);
 for s in &a{
 let owner=s.observation().source;let n=s.successor(Event::Shock(vec![(0,40)])).unwrap().successor(Event::Recover).unwrap();
 let b=encode(&n).unwrap();let h=digest(&b);assert_eq!(restore(owner,&b,h),Some(n.clone()));assert!(extends(s,&n));assert!(!extends(&n,s));
 for i in [5,6,14,22,34,38+CENTER,38+crate::CELLS-1]{let mut bad=b.clone();bad[i]^=1;assert!(restore(owner,&bad,digest(&bad)).is_none());}
 for i in 0..b.len(){assert!(restore(owner,&b[..i],h).is_none());}
 assert!(restore(SiloId::new(((owner.index()+1)%5)as u8).unwrap(),&b,h).is_none());
 assert_ne!(commitment(s),commitment(&n));
 }
 }
 }
}
