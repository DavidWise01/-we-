//! Native single-directory checkpoint store. QJ1 retains its original recovery policy.
use quartz_kernel::journal::Journal;
use std::{fs::{self,File,OpenOptions},io::{self,Read,Write},path::Path};
const LIMIT:u64=65536;
fn invalid()->io::Error{io::Error::new(io::ErrorKind::InvalidData,"invalid checkpoint or ancestry")}
pub fn load(path:&Path)->io::Result<Journal>{
 let mut data=String::new();File::open(path)?.take(LIMIT+1).read_to_string(&mut data)?;
 if data.len() as u64>LIMIT{return Err(invalid());}
 Journal::decode(&data).ok_or_else(invalid)
}
/// Linux/Unix local filesystem: publish without overwriting via hard link.
/// Caller supplies an existing trusted directory and sequence number.
pub fn publish(dir:&Path,seq:u64,j:&Journal)->io::Result<()>{
 let data=j.encode();if data.len() as u64>LIMIT{return Err(invalid());}
 if seq==0 {if !j.events().is_empty(){return Err(invalid());}}
 else{
  let prior=load(&dir.join(format!("{:020}.qj1",seq-1)))?;
  if j.events().len()!=prior.events().len()+1 || !j.events().starts_with(prior.events()) ||
   j.encode().lines().next()!=prior.encode().lines().next(){return Err(invalid());}
 }
 let dest=dir.join(format!("{seq:020}.qj1"));
 let stage=dir.join(format!(".{seq:020}.pending"));
 let mut file=OpenOptions::new().write(true).create_new(true).open(&stage)?;
 let result=(||{file.write_all(data.as_bytes())?;file.sync_all()?;fs::hard_link(&stage,&dest)?;File::open(dir)?.sync_all()?;Ok(())})();
 drop(file);
 let cleanup=fs::remove_file(&stage);
 result?;cleanup?;File::open(dir)?.sync_all()
}
fn main(){}
#[cfg(test)]
mod tests{
 use super::*;use quartz_kernel::journal::Event;
 #[test]fn persistence(){
 let dir=std::env::temp_dir().join(format!("quartz-g15-{}",std::process::id()));fs::create_dir(&dir).unwrap();
 let a=Journal::new([100;3]);let b=a.append(Event::Shock(vec![(0,40)])).unwrap();let c=b.append(Event::Recover).unwrap();
 publish(&dir,0,&a).unwrap();publish(&dir,1,&b).unwrap();assert!(publish(&dir,1,&b).is_err());assert!(publish(&dir,3,&c).is_err());
 assert!(publish(&dir,2,&a).is_err());publish(&dir,2,&c).unwrap();assert_eq!(load(&dir.join("00000000000000000002.qj1")).unwrap(),c);
 assert_eq!(load(&dir.join("00000000000000000000.qj1")).unwrap(),a);
 fs::write(dir.join("bad"),"QJ1 1 2 3\nR").unwrap();assert!(load(&dir.join("bad")).is_err());fs::remove_dir_all(dir).unwrap();
 }
}
