use crate::{integrity::Hash,roster_binding::Binding,witness_ancestry::{self,Node,Declaration}};
use sha2::{Digest,Sha256};
pub const MAX_LOG:usize=8*1024*1024;
pub const MAX_OUTPUT:usize=32*1024*1024;
pub const MAX_META:usize=4096;
#[derive(Clone,Copy,Debug,PartialEq,Eq)]
pub struct Target{pub revision:Hash,pub procedure:Hash,pub result:Hash}
impl Target{
 pub fn subject(self)->Hash{let mut h=Sha256::new();h.update(b"quartz/G79/subject/v1\0");for x in [self.revision,self.procedure,self.result]{h.update(x);}h.finalize().into()}
}
pub fn digest(bytes:&[u8])->Hash{Sha256::digest(bytes).into()}
pub struct Observation<'a>{pub revision:Hash,pub procedure:Hash,pub run:Hash,pub source:Hash,pub toolchain:&'a[u8],pub log:&'a[u8],pub output:&'a[u8],pub exit:i32}
#[derive(Clone,Copy,Debug,PartialEq,Eq)]
pub enum Fault{Bounds,Target,Failed,DuplicateRun,DuplicateLog,Binding,Ancestry(witness_ancestry::Fault)}
impl Observation<'_>{
 pub fn commitment(&self)->Result<Hash,Fault>{
 if self.log.is_empty()||self.log.len()>MAX_LOG||self.output.is_empty()||self.output.len()>MAX_OUTPUT||self.toolchain.is_empty()||self.toolchain.len()>MAX_META||self.run==[0;32]||self.source==[0;32]{return Err(Fault::Bounds);}
 let mut h=Sha256::new();h.update(b"quartz/G79/observation/v1\0");for x in [self.revision,self.procedure,self.run,self.source,digest(self.toolchain),digest(self.log),digest(self.output)]{h.update(x);}h.update(self.exit.to_be_bytes());Ok(h.finalize().into())
 }
}
/// Successful return means bytes and signed declarations agree, not independent origin.
/// Target, roster and graph pins must be retained separately from submitted evidence.
pub fn reconcile(target:Target,binding:&Binding,roster:Hash,nodes:&[Node],graph:Hash,observations:&[Observation<'_>;3],declarations:&[Declaration;3])->Result<(),Fault>{
 if [target.revision,target.procedure,target.result].contains(&[0;32]){return Err(Fault::Target);}
 let mut runs=Vec::new();let mut logs=Vec::new();
 for (i,o) in observations.iter().enumerate(){let commitment=o.commitment()?;if o.revision!=target.revision||o.procedure!=target.procedure||digest(o.output)!=target.result{return Err(Fault::Target);}if o.exit!=0{return Err(Fault::Failed);}
 if runs.contains(&o.run){return Err(Fault::DuplicateRun);}runs.push(o.run);
 let log=digest(o.log);if logs.contains(&log){return Err(Fault::DuplicateLog);}logs.push(log);
 if declarations[i].observation!=commitment||declarations[i].source!=o.source{return Err(Fault::Binding);}
 }
 witness_ancestry::verify(binding,roster,target.subject(),nodes,graph,declarations).map_err(Fault::Ancestry)
}
#[cfg(test)]mod tests{
 use super::*;use crate::{authentication::Witness,mesh::SiloId};use ed25519_dalek::{SigningKey,Signer};
 #[test]fn reconciliation(){
 let keys:[SigningKey;3]=std::array::from_fn(|i|SigningKey::from_bytes(&[(i+1)as u8;32]));let b=Binding::genesis(SiloId::new(0).unwrap(),std::array::from_fn(|i|Witness{key:keys[i].verifying_key().to_bytes(),root:[(i+1)as u8;32]})).unwrap();
 let nodes:Vec<_>=(1..=3u8).map(|i|Node{id:[i;32],parents:vec![]}).collect();let graph=witness_ancestry::graph_digest(&nodes).unwrap();
 let target=Target{revision:digest(b"fixture revision"),procedure:digest(b"fixture procedure"),result:digest(b"same result")};
 let logs:[&[u8];3]=[b"fixture log A",b"fixture log B",b"fixture log C"];
 let mut obs=std::array::from_fn(|i|Observation{revision:target.revision,procedure:target.procedure,run:[(i+10)as u8;32],source:[(i+1)as u8;32],toolchain:b"fixture compiler",log:logs[i],output:b"same result",exit:0});
 let ds=std::array::from_fn(|i|{let w=b.members()[i];let mut d=Declaration{root:w.root,subject:target.subject(),source:obs[i].source,observation:obs[i].commitment().unwrap(),signature:[0;64]};d.signature=keys.iter().find(|k|k.verifying_key().to_bytes()==w.key).unwrap().sign(&d.signing_bytes(b.digest(),graph)).to_bytes();d});
 let check=|o:&[Observation<'_>;3]|reconcile(target,&b,b.digest(),&nodes,graph,o,&ds);
 assert_eq!(check(&obs),Ok(()));obs[2].output=b"different";assert_eq!(check(&obs),Err(Fault::Target));obs[2].output=b"same result";obs[2].exit=1;assert_eq!(check(&obs),Err(Fault::Failed));obs[2].exit=0;
 obs[2].run=obs[0].run;assert_eq!(check(&obs),Err(Fault::DuplicateRun));obs[2].run=[12;32];obs[2].log=logs[0];assert_eq!(check(&obs),Err(Fault::DuplicateLog));obs[2].log=b"edited";assert_eq!(check(&obs),Err(Fault::Binding));obs[2].log=logs[2];assert_eq!(check(&obs),Ok(()));
 }
}
