use std::{fs::{self,File,OpenOptions},io::{self,Read,Write},path::{Path,PathBuf}};
use sha2::{Digest,Sha256};
use crate::integrity::{Hash,Link};
pub const MAX_RECORDS:usize=4096;
pub const MAX_PAYLOAD:usize=1_048_576;
pub const HEADER:usize=112;
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Record{pub link:Link,pub payload:Vec<u8>}
fn invalid()->io::Error{io::Error::new(io::ErrorKind::InvalidData,"invalid QF1 journal record")}
fn payload_hash(b:&[u8])->Hash{let mut h=Sha256::new();h.update(b"quartz/QF1/payload/v1\0");h.update(b);h.finalize().into()}
fn path(dir:&Path,index:usize)->PathBuf{dir.join(format!("{index:016x}.qf1"))}
fn encode(r:&Record)->Vec<u8>{
 let mut b=b"QF1\0".to_vec();b.extend_from_slice(&r.link.index.to_be_bytes());b.extend_from_slice(&r.link.previous);b.extend_from_slice(&r.link.payload);b.extend_from_slice(&r.link.digest);b.extend_from_slice(&(r.payload.len()as u32).to_be_bytes());b.extend_from_slice(&r.payload);b
}
fn decode(b:&[u8],index:usize,previous:Hash)->io::Result<Record>{
 if b.len()<HEADER||&b[..4]!=b"QF1\0"{return Err(invalid());}
 let n=u32::from_be_bytes(b[108..112].try_into().map_err(|_|invalid())?)as usize;
 if n>MAX_PAYLOAD||b.len()!=HEADER+n{return Err(invalid());}
 let payload=b[HEADER..].to_vec();let link=Link::new(index as u64,previous,payload_hash(&payload));
 let r=Record{link,payload};if encode(&r)!=b{return Err(invalid());}Ok(r)
}
/// Load only the externally specified committed prefix; no automatic promotion.
pub fn read_prefix(dir:&Path,count:usize,expected:Hash)->io::Result<Vec<Record>>{
 if count>MAX_RECORDS{return Err(invalid());}
 let mut head=[0;32];let mut out=Vec::with_capacity(count);
 for i in 0..count{
 let p=path(dir,i);if !fs::symlink_metadata(&p)?.file_type().is_file(){return Err(invalid());}
 let f=File::open(p)?;let mut b=Vec::new();f.take((HEADER+MAX_PAYLOAD+1)as u64).read_to_end(&mut b)?;
 let r=decode(&b,i,head)?;head=r.link.digest;out.push(r);
 }
 if head!=expected{return Err(invalid());}Ok(out)
}
/// Trusted private directory, single writer. Failed writes leave occupied slots.
/// A successful return means file sync completed, not directory or external head durability.
pub fn append(dir:&Path,count:usize,expected:Hash,payload:&[u8])->io::Result<Hash>{
 if count>=MAX_RECORDS||payload.len()>MAX_PAYLOAD{return Err(invalid());}
 read_prefix(dir,count,expected)?;
 let r=Record{link:Link::new(count as u64,expected,payload_hash(payload)),payload:payload.to_vec()};
 let mut f=OpenOptions::new().write(true).create_new(true).open(path(dir,count))?;
 f.write_all(&encode(&r))?;f.sync_all()?;Ok(r.link.digest)
}
#[cfg(test)]mod tests{
 use super::*;use std::time::{SystemTime,UNIX_EPOCH};
 #[test]fn exclusive_records_and_torn_suffix(){
 let dir=std::env::temp_dir().join(format!("quartz-g49-{}-{}",std::process::id(),SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_nanos()));
 fs::create_dir(&dir).unwrap();
 let h=append(&dir,0,[0;32],b"first").unwrap();let a=fs::read(path(&dir,0)).unwrap();
 assert!(append(&dir,0,[0;32],b"overwrite").is_err());assert_eq!(fs::read(path(&dir,0)).unwrap(),a);
 let h2=append(&dir,1,h,b"second").unwrap();assert_eq!(read_prefix(&dir,2,h2).unwrap()[1].payload,b"second");
 assert!(read_prefix(&dir,1,h2).is_err());
 fs::write(path(&dir,2),b"QF1").unwrap();
 assert_eq!(read_prefix(&dir,2,h2).unwrap().len(),2);assert!(read_prefix(&dir,3,h2).is_err());assert!(append(&dir,2,h2,b"replacement").is_err());
 let mut bad=a;bad[HEADER]^=1;fs::write(path(&dir,0),bad).unwrap();assert!(read_prefix(&dir,2,h2).is_err());fs::remove_dir_all(dir).unwrap();
 }
}

 /// Read only the next record relative to a previously verified prefix.
 pub(crate) fn read_successor(dir:&Path,index:usize,previous:Hash,expected:Hash)->io::Result<Record>{
 if index>=MAX_RECORDS{return Err(invalid());}
 let p=path(dir,index);if !fs::symlink_metadata(&p)?.file_type().is_file(){return Err(invalid());}
 let f=File::open(p)?;let mut b=Vec::new();f.take((HEADER+MAX_PAYLOAD+1)as u64).read_to_end(&mut b)?;
 let r=decode(&b,index,previous)?;if r.link.digest!=expected{return Err(invalid());}Ok(r)
 }
