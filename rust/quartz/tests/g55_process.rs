#![cfg(unix)]
use quartz_kernel::{filesystem,publication::{self,Publication}};
use std::{fs::{self,OpenOptions},io::Write,path::PathBuf,process::{Command,Stdio},time::{Duration,Instant,SystemTime,UNIX_EPOCH},thread};
#[test]
fn child_writer(){
 let Ok(dir)=std::env::var("QUARTZ_G55_DIR")else{return;};
 let dir=PathBuf::from(dir);let mode=std::env::var("QUARTZ_G55_MODE").unwrap();
 // Test fixture recreates deterministic first record in a separate directory.
 let base=dir.join("reference");fs::create_dir(&base).unwrap();
 let h=filesystem::append(&base,0,[0;32],b"sealed").unwrap();let p=Publication{count:1,head:h,previous:[0;32]};
 if mode=="torn-record"{let mut f=OpenOptions::new().write(true).create_new(true).open(dir.join("0000000000000001.qf1")).unwrap();f.write_all(b"QF1").unwrap();f.sync_all().unwrap();}
 else if mode!="before-write"{
 let h2=filesystem::append(&dir,1,h,b"successor").unwrap();
 if mode=="torn-marker"{let mut f=OpenOptions::new().write(true).create_new(true).open(dir.join("0000000000000002.qp1")).unwrap();f.write_all(b"QP1").unwrap();f.sync_all().unwrap();}
 else if mode=="published"{publication::publish(&dir,2,h2,p.digest()).unwrap();}
 else{assert_eq!(mode,"record-synced");}
 }
 // Ready marker confirms the specific test boundary has been reached before kill.
 fs::write(dir.join("ready"),b"ready").unwrap();
 loop{thread::sleep(Duration::from_secs(1));}
}
#[test]
fn process_interruption(){
 for mode in ["before-write","torn-record","record-synced","torn-marker","published"]{
 let dir=std::env::temp_dir().join(format!("quartz-g55-{}-{}-{mode}",std::process::id(),SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_nanos()));
 fs::create_dir(&dir).unwrap();let h=filesystem::append(&dir,0,[0;32],b"sealed").unwrap();let p=publication::publish(&dir,1,h,[0;32]).unwrap();
 let original=fs::read(dir.join("0000000000000000.qf1")).unwrap();
 let mut child=Command::new(std::env::current_exe().unwrap()).args(["--exact","child_writer","--nocapture"]).env("QUARTZ_G55_DIR",&dir).env("QUARTZ_G55_MODE",mode).stdout(Stdio::null()).stderr(Stdio::inherit()).spawn().unwrap();
 let start=Instant::now();while !dir.join("ready").exists(){
 if let Some(s)=child.try_wait().unwrap(){panic!("child exited before boundary: {s}");}
 if start.elapsed()>Duration::from_secs(15){let _=child.kill();let _=child.wait();panic!("boundary timeout: {mode}");}
 thread::sleep(Duration::from_millis(10));
 }
 child.kill().unwrap();assert!(!child.wait().unwrap().success());
 assert_eq!(publication::recover(&dir,1,p.digest()).unwrap(),p);assert_eq!(fs::read(dir.join("0000000000000000.qf1")).unwrap(),original);
 assert!(publication::recover(&dir,2,p.digest()).is_err());
 if mode=="torn-record"||mode=="record-synced"||mode=="torn-marker"||mode=="published"{assert!(filesystem::append(&dir,1,h,b"overwrite").is_err());}
 if mode=="published"{let h2=filesystem::append(&dir.join("reference"),1,h,b"successor").unwrap();let p2=Publication{count:2,head:h2,previous:p.digest()};assert_eq!(publication::recover(&dir,2,p2.digest()).unwrap(),p2);}
 println!("G55 boundary {mode}: retained prefix verified");fs::remove_dir_all(dir).unwrap();
 }
}
