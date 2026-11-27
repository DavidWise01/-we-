use crate::{integrity::Hash,roster_binding::Binding};
use ed25519_dalek::{Signature,VerifyingKey};
use sha2::{Digest,Sha256};
use std::collections::{BTreeMap,BTreeSet};
pub const MAX_NODES:usize=128;
pub const MAX_PARENTS:usize=8;
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Node{pub id:Hash,pub parents:Vec<Hash>}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Declaration{pub root:Hash,pub subject:Hash,pub observation:Hash,pub source:Hash,pub signature:[u8;64]}
#[derive(Clone,Copy,Debug,PartialEq,Eq)]
pub enum Fault{Graph,Missing,Cycle,SharedAncestry,DuplicateObservation,Subject,Identity,Signature}
pub fn graph_digest(nodes:&[Node])->Option<Hash>{
 if nodes.is_empty()||nodes.len()>MAX_NODES{return None;}
 let mut h=Sha256::new();h.update(b"quartz/G78/graph/v1\0");h.update((nodes.len()as u16).to_be_bytes());
 let mut previous=None;
 for n in nodes{if n.id==[0;32]||previous.is_some_and(|p|p>=n.id)||n.parents.len()>MAX_PARENTS||n.parents.windows(2).any(|w|w[0]>=w[1]){return None;}previous=Some(n.id);h.update(n.id);h.update([n.parents.len()as u8]);for p in &n.parents{h.update(p);}}
 Some(h.finalize().into())
}
impl Declaration{
 pub fn signing_bytes(&self,roster:Hash,graph:Hash)->Vec<u8>{let mut b=b"quartz/G78/declaration/v1\0".to_vec();for h in [roster,graph,self.root,self.subject,self.observation,self.source]{b.extend_from_slice(&h);}b}
}
fn visit(id:Hash,map:&BTreeMap<Hash,&Node>,active:&mut BTreeSet<Hash>,done:&mut BTreeSet<Hash>)->Result<(),Fault>{
 if active.contains(&id){return Err(Fault::Cycle);}if done.contains(&id){return Ok(());}
 let n=map.get(&id).ok_or(Fault::Missing)?;active.insert(id);for p in &n.parents{visit(*p,map,active,done)?;}active.remove(&id);done.insert(id);Ok(())
}
/// Authenticate a bounded, explicitly declared ancestry graph against externally supplied pins.
/// Disjoint declarations do not prove real-world independence or authorize action.
pub fn verify(binding:&Binding,expected_roster:Hash,subject:Hash,nodes:&[Node],expected_graph:Hash,reports:&[Declaration;3])->Result<(),Fault>{
 if binding.digest()!=expected_roster{return Err(Fault::Identity);}
 if subject==[0;32]{return Err(Fault::Subject);}
 if graph_digest(nodes)!=Some(expected_graph){return Err(Fault::Graph);}
 let map:BTreeMap<_,_>=nodes.iter().map(|n|(n.id,n)).collect();
 let mut all=BTreeSet::new();for n in nodes{visit(n.id,&map,&mut BTreeSet::new(),&mut all)?;}
 let mut used=BTreeSet::new();let mut observations=BTreeSet::new();
 for (i,r) in reports.iter().enumerate(){
 let w=&binding.members()[i];if r.root!=w.root{return Err(Fault::Identity);}if r.subject!=subject{return Err(Fault::Subject);}
 if r.observation==[0;32]||!observations.insert(r.observation){return Err(Fault::DuplicateObservation);}
 let k=VerifyingKey::from_bytes(&w.key).map_err(|_|Fault::Signature)?;
 k.verify_strict(&r.signing_bytes(expected_roster,expected_graph),&Signature::from_bytes(&r.signature)).map_err(|_|Fault::Signature)?;
 let mut closure=BTreeSet::new();visit(r.source,&map,&mut BTreeSet::new(),&mut closure)?;
 if !closure.is_disjoint(&used){return Err(Fault::SharedAncestry);}used.extend(closure);
 }Ok(())
}
#[cfg(test)]mod tests{
 use super::*;use crate::{authentication::Witness,mesh::SiloId};use ed25519_dalek::{SigningKey,Signer};
 #[test]fn declared_ancestry_challenges(){
 let keys:[SigningKey;3]=std::array::from_fn(|i|SigningKey::from_bytes(&[(i+1)as u8;32]));
 let b=Binding::genesis(SiloId::new(0).unwrap(),std::array::from_fn(|i|Witness{key:keys[i].verifying_key().to_bytes(),root:[(i+1)as u8;32]})).unwrap();
 let roster=b.digest();let subject=[99;32];
 let clean:Vec<_>=(1..=6u8).map(|i|Node{id:[i;32],parents:if i>3{vec![[i-3;32]]}else{vec![]}}).collect();
 let sign=|nodes:&[Node],sources:[u8;3],obs:[u8;3]|{let g=graph_digest(nodes).unwrap();std::array::from_fn(|i|{let w=b.members()[i];let mut d=Declaration{root:w.root,subject,observation:[obs[i];32],source:[sources[i];32],signature:[0;64]};d.signature=keys.iter().find(|k|k.verifying_key().to_bytes()==w.key).unwrap().sign(&d.signing_bytes(roster,g)).to_bytes();d})};
 let check=|nodes:&[Node],d:&[Declaration;3]|verify(&b,roster,subject,nodes,graph_digest(nodes).unwrap(),d);
 let d=sign(&clean,[4,5,6],[10,11,12]);assert_eq!(check(&clean,&d),Ok(()));
 let mut shared=clean.clone();shared[4].parents=vec![[1;32]];assert_eq!(check(&shared,&sign(&shared,[4,5,6],[10,11,12])),Err(Fault::SharedAncestry));
 assert_eq!(check(&clean,&sign(&clean,[4,5,6],[10,10,12])),Err(Fault::DuplicateObservation));
 let mut cycle=clean.clone();cycle[0].parents=vec![[4;32]];assert_eq!(check(&cycle,&sign(&cycle,[4,5,6],[10,11,12])),Err(Fault::Cycle));
 let mut missing=clean.clone();missing[0].parents=vec![[77;32]];assert_eq!(check(&missing,&sign(&missing,[4,5,6],[10,11,12])),Err(Fault::Missing));
 let mut forged=d.clone();forged[1].signature[0]^=1;assert_eq!(check(&clean,&forged),Err(Fault::Signature));
 let mut wrong=d.clone();wrong[0].subject=[88;32];assert_eq!(check(&clean,&wrong),Err(Fault::Subject));
 assert_eq!(verify(&b,roster,subject,&clean,[0;32],&d),Err(Fault::Graph));
 }
}
