use std::{fs::{self,File,OpenOptions},io::{self,Read,Write},path::{Path,PathBuf}};
use sha2::{Digest,Sha256};
use crate::{filesystem,integrity::Hash};
pub const MARKER_BYTES:usize=76;
#[derive(Clone,Copy,Debug,PartialEq,Eq)]
pub struct Publication{pub count:u64,pub head:Hash,pub previous:Hash}
fn invalid()->io::Error{io::Error::new(io::ErrorKind::InvalidData,"invalid QP1 publication")}
fn marker(dir:&Path,count:u64)->PathBuf{dir.join(format!("{count:016x}.qp1"))}
impl Publication{
 pub fn encode(self)->[u8;MARKER_BYTES]{let mut b=[0;MARKER_BYTES];b[..4].copy_from_slice(b"QP1\0");b[4..12].copy_from_slice(&self.count.to_be_bytes());b[12..44].copy_from_slice(&self.head);b[44..76].copy_from_slice(&self.previous);b}
 pub fn digest(self)->Hash{let mut h=Sha256::new();h.update(b"quartz/QP1/v1\0");h.update(self.encode());h.finalize().into()}
}
fn read_marker(dir:&Path,count:u64)->io::Result<Publication>{
 let p=marker(dir,count);if !fs::symlink_metadata(&p)?.file_type().is_file(){return Err(invalid());}
 let mut b=Vec::new();File::open(p)?.take((MARKER_BYTES+1)as u64).read_to_end(&mut b)?;
 if b.len()!=MARKER_BYTES||&b[..4]!=b"QP1\0"||b[4..12]!=count.to_be_bytes(){return Err(invalid());}
 Ok(Publication{count,head:b[12..44].try_into().map_err(|_|invalid())?,previous:b[44..76].try_into().map_err(|_|invalid())?})
}
/// Validate only a caller-pinned publication prefix and its underlying QF1 records.
pub fn recover(dir:&Path,count:u64,expected:Hash)->io::Result<Publication>{
 if count==0||count>filesystem::MAX_RECORDS as u64{return Err(invalid());}
 let mut prev=[0;32];let mut markers=Vec::new();
 for n in 1..=count{let p=read_marker(dir,n)?;if p.previous!=prev{return Err(invalid());}prev=p.digest();markers.push(p);}
 if prev!=expected{return Err(invalid());}
 let last=*markers.last().ok_or_else(invalid)?;
 let records=filesystem::read_prefix(dir,count as usize,last.head)?;
 if markers.iter().zip(&records).any(|(p,r)|p.head!=r.link.digest){return Err(invalid());}
 Ok(last)
}
/// Linux/Unix trusted private directory, single writer. A failed sync is ambiguous; never retry by overwriting.
pub fn publish(dir:&Path,count:u64,head:Hash,previous:Hash)->io::Result<Publication>{
 if count==0||count>filesystem::MAX_RECORDS as u64{return Err(invalid());}
 let prior=if count==1{if previous!=[0;32]{return Err(invalid());}[0;32]}else{recover(dir,count-1,previous)?.head};
 let records=filesystem::read_prefix(dir,count as usize,head)?;
 if records.last().ok_or_else(invalid)?.link.previous!=prior{return Err(invalid());}
 // Sync underlying records and their directory before exposing the marker.
 for n in 0..count{File::open(dir.join(format!("{n:016x}.qf1")))?.sync_all()?;}
 File::open(dir)?.sync_all()?;
 let p=Publication{count,head,previous};
 let mut f=OpenOptions::new().write(true).create_new(true).open(marker(dir,count))?;
 f.write_all(&p.encode())?;f.sync_all()?;File::open(dir)?.sync_all()?;Ok(p)
}
#[cfg(test)]mod tests{
 use super::*;use std::time::{SystemTime,UNIX_EPOCH};
 #[test]fn publication_prefix(){
 let dir=std::env::temp_dir().join(format!("quartz-g50-{}-{}",std::process::id(),SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_nanos()));
 fs::create_dir(&dir).unwrap();let h=filesystem::append(&dir,0,[0;32],b"first").unwrap();
 assert!(recover(&dir,1,[0;32]).is_err());let p=publish(&dir,1,h,[0;32]).unwrap();assert_eq!(recover(&dir,1,p.digest()).unwrap(),p);
 assert!(publish(&dir,1,h,[0;32]).is_err());
 let h2=filesystem::append(&dir,1,h,b"second").unwrap();assert!(recover(&dir,2,p.digest()).is_err());
 let p2=publish(&dir,2,h2,p.digest()).unwrap();assert_eq!(recover(&dir,2,p2.digest()).unwrap(),p2);assert!(recover(&dir,1,p2.digest()).is_err());
 let h3=filesystem::append(&dir,2,h2,b"third").unwrap();fs::write(marker(&dir,3),b"QP1").unwrap();
 assert_eq!(recover(&dir,2,p2.digest()).unwrap(),p2);assert!(recover(&dir,3,p2.digest()).is_err());assert!(publish(&dir,3,h3,p2.digest()).is_err());
 fs::remove_dir_all(dir).unwrap();
 }
}
