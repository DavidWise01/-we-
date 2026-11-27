use std::{fs::{self,File,OpenOptions},io::{self,Read,Write},path::{Path,PathBuf}};
use sha2::{Digest,Sha256};
use crate::{checkpoint_frame::{self,Frame,MAX_FRAME},integrity::Hash,mesh::SiloId,temporal_chain::{self,Entry,MAX_CHECKPOINTS}};
pub const MARKER_BYTES:usize=117;
#[derive(Clone,Copy,Debug,PartialEq,Eq)]
pub struct Marker{pub owner:SiloId,pub index:u64,pub length:u64,pub frame:Hash,pub checkpoint:Hash,pub previous:Hash}
fn invalid()->io::Error{io::Error::new(io::ErrorKind::InvalidData,"invalid QX1 publication boundary")}
impl Marker{
 pub fn encode(self)->[u8;MARKER_BYTES]{let mut b=[0;MARKER_BYTES];b[..4].copy_from_slice(b"QY1\0");b[4]=self.owner.index()as u8;b[5..13].copy_from_slice(&self.index.to_be_bytes());b[13..21].copy_from_slice(&self.length.to_be_bytes());b[21..53].copy_from_slice(&self.frame);b[53..85].copy_from_slice(&self.checkpoint);b[85..117].copy_from_slice(&self.previous);b}
 pub fn digest(self)->Hash{let mut h=Sha256::new();h.update(b"quartz/QY1/v1\0");h.update(self.encode());h.finalize().into()}
 pub fn decode(b:&[u8])->Option<Self>{if b.len()!=MARKER_BYTES||&b[..4]!=b"QY1\0"{return None;}let m=Self{owner:SiloId::new(b[4])?,index:u64::from_be_bytes(b[5..13].try_into().ok()?),length:u64::from_be_bytes(b[13..21].try_into().ok()?),frame:b[21..53].try_into().ok()?,checkpoint:b[53..85].try_into().ok()?,previous:b[85..117].try_into().ok()?};if m.index>=MAX_CHECKPOINTS as u64||m.length==0||m.length>MAX_FRAME as u64||(m.index==0)!=(m.previous==[0;32]){return None;}Some(m)}
}
fn path(dir:&Path,index:u64,ext:&str)->PathBuf{dir.join(format!("{index:016x}.{ext}"))}
fn read(path:&Path,max:usize)->io::Result<Vec<u8>>{if !fs::symlink_metadata(path)?.file_type().is_file(){return Err(invalid());}let mut b=Vec::new();File::open(path)?.take((max+1)as u64).read_to_end(&mut b)?;if b.len()>max{return Err(invalid());}Ok(b)}
/// Same private filesystem, single trusted writer. The staging file is retained,
/// including on failure; occupied slots are never silently reused.
fn expose(dir:&Path,index:u64,ext:&str,b:&[u8])->io::Result<()>{
 let stage=path(dir,index,&format!("{ext}.stage"));let final_path=path(dir,index,ext);
 let mut f=OpenOptions::new().write(true).create_new(true).open(&stage)?;
 f.write_all(b)?;f.sync_all()?;drop(f);
 fs::hard_link(&stage,&final_path)?;File::open(dir)?.sync_all()?;Ok(())
}
/// Reconstruct only the explicitly pinned prefix; never discover/promote a suffix.
pub fn recover(dir:&Path,archive:&Path,owner:SiloId,genesis:Hash,count:usize,expected:Hash)->io::Result<Vec<Frame>>{
 if count==0||count>MAX_CHECKPOINTS{return Err(invalid());}
 // Bound cumulative encoded input to 128 MiB, not a heap or execution-time guarantee.
 let mut remaining=128usize*1024*1024;let mut frames=Vec::new();let mut previous=[0;32];
 for n in 0..count{
 let m=Marker::decode(&read(&path(dir,n as u64,"qy1"),MARKER_BYTES)?).ok_or_else(invalid)?;
 if m.owner!=owner||m.index!=n as u64||m.previous!=previous{return Err(invalid());}
 remaining=remaining.checked_sub(m.length as usize).ok_or_else(invalid)?;
 let b=read(&path(dir,n as u64,"qx1"),m.length as usize)?;
 if b.len()!=m.length as usize{return Err(invalid());}
 let f=Frame::decode(&b,m.frame).ok_or_else(invalid)?;
 if f.checkpoint.digest()!=m.checkpoint{return Err(invalid());}previous=m.digest();frames.push(f);
 }
 if previous!=expected{return Err(invalid());}
 let entries:Vec<_>=frames.iter().map(|f|Entry{checkpoint:&f.checkpoint,inputs:f.inputs(archive)}).collect();
 if !temporal_chain::verify(owner,genesis,&entries,frames.last().ok_or_else(invalid)?.checkpoint.digest()){return Err(invalid());}
 // Check the serialized published payloads as well as the QU1 reconstruction.
 let mut prev=[0;32];let mut adv=[0;32];for f in &frames{if !f.verify(archive,genesis,prev,adv,f.checkpoint.digest()){return Err(invalid());}prev=f.checkpoint.digest();adv=f.advisory.digest();}
 Ok(frames)
}
/// Verify full ancestry before creating the frame, then atomically expose its marker.
/// A directory sync failure is ambiguous: caller must retain the old external pin.
pub fn publish(dir:&Path,archive:&Path,owner:SiloId,genesis:Hash,frame:&Frame,previous:Hash,expected_checkpoint:Hash)->io::Result<Marker>{
 let index=frame.checkpoint.claim.index;if index>=MAX_CHECKPOINTS as u64||frame.checkpoint.digest()!=expected_checkpoint{return Err(invalid());}
 let mut prior=if index==0{if previous!=[0;32]{return Err(invalid());}Vec::new()}else{recover(dir,archive,owner,genesis,index as usize,previous)?};
 let b=frame.encode().ok_or_else(invalid)?;let hash=checkpoint_frame::digest(&b);
 let reconstructed=Frame::decode(&b,hash).ok_or_else(invalid)?;
 let mut total=b.len();for f in &prior{total=total.checked_add(f.encode().ok_or_else(invalid)?.len()).ok_or_else(invalid)?;}if total>128*1024*1024{return Err(invalid());}
 let prev=prior.last().map(|f|f.checkpoint.digest()).unwrap_or([0;32]);let adv=prior.last().map(|f|f.advisory.digest()).unwrap_or([0;32]);
 if !reconstructed.verify(archive,genesis,prev,adv,expected_checkpoint){return Err(invalid());}
 prior.push(reconstructed);let entries:Vec<_>=prior.iter().map(|f|Entry{checkpoint:&f.checkpoint,inputs:f.inputs(archive)}).collect();
 if !temporal_chain::verify(owner,genesis,&entries,expected_checkpoint){return Err(invalid());}
 let m=Marker{owner,index,length:b.len()as u64,frame:hash,checkpoint:expected_checkpoint,previous};
 expose(dir,index,"qx1",&b)?;expose(dir,index,"qy1",&m.encode())?;Ok(m)
}
#[cfg(test)]mod tests{use super::*;use std::time::{SystemTime,UNIX_EPOCH};
 #[test]fn marker_and_exclusive_visibility(){
 let m=Marker{owner:SiloId::new(0).unwrap(),index:0,length:4,frame:[1;32],checkpoint:[2;32],previous:[0;32]};assert_eq!(Marker::decode(&m.encode()),Some(m));for n in 0..MARKER_BYTES{assert!(Marker::decode(&m.encode()[..n]).is_none());}
 let d=std::env::temp_dir().join(format!("quartz-g67-{}-{}",std::process::id(),SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_nanos()));fs::create_dir(&d).unwrap();
 expose(&d,0,"qx1",b"complete").unwrap();assert!(expose(&d,0,"qx1",b"overwrite").is_err());assert_eq!(read(&path(&d,0,"qx1"),8).unwrap(),b"complete");
 fs::write(path(&d,1,"qx1.stage"),b"torn").unwrap();assert!(!path(&d,1,"qx1").exists());assert!(expose(&d,1,"qx1",b"replacement").is_err());
 fs::write(path(&d,2,"qy1"),b"occupied").unwrap();assert!(expose(&d,2,"qy1",&m.encode()).is_err());assert_eq!(fs::read(path(&d,2,"qy1")).unwrap(),b"occupied");fs::remove_dir_all(d).unwrap();
 }}
