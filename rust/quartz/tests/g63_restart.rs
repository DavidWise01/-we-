#![cfg(unix)]
use quartz_kernel::{authentication::Witness,mesh::{mesh,SiloId},journal::{Policy,Event},temporal::{Clock,TimedObservation},roster_binding::{Binding,ROSTER_BYTES},signed_evidence::{self,Evidence},custody::{self,Claim,Custody,CUSTODY_BYTES},filesystem,publication,cross_ledger,incremental::VerifiedPrefix,integrity::Hash};
use ed25519_dalek::{SigningKey,Signer};
use std::{fs,path::Path,process::Command,time::{SystemTime,UNIX_EPOCH}};
fn hex(h:Hash)->String{h.iter().map(|b|format!("{b:02x}")).collect()}
fn unhex(s:&str)->Option<Hash>{if s.len()!=64||!s.is_ascii(){return None;}let mut h=[0;32];for(i,b)in h.iter_mut().enumerate(){*b=u8::from_str_radix(&s[2*i..2*i+2],16).ok()?;}Some(h)}
fn rebuild(dir:&Path,owner:SiloId,roster:Hash,head:Hash)->Option<VerifiedPrefix>{
 let bytes=fs::read(dir.join("roster")).ok()?;if bytes.len()!=ROSTER_BYTES{return None;}
 let binding=Binding::decode(owner,&bytes,roster)?;
 let raw=fs::read(dir.join("custody")).ok()?;if raw.len()!=3*CUSTODY_BYTES{return None;}
 let chain:Vec<Custody>=raw.chunks_exact(CUSTODY_BYTES).map(Custody::decode).collect::<Option<_>>()?;
 if !cross_ledger::verify(dir,owner,roster,&chain,head){return None;}
 let mut cache=VerifiedPrefix::genesis(&binding)?;
 for c in &chain{cache=cache.advance(dir,c,c.digest())?;}
 if cache.head()!=head||cache.count()!=3{return None;}Some(cache)
}
#[test]fn restart_child(){
 let Ok(dir)=std::env::var("QUARTZ_G63_DIR")else{return;};
 let owner=SiloId::new(std::env::var("QUARTZ_G63_OWNER").unwrap().parse().unwrap()).unwrap();
 let roster=unhex(&std::env::var("QUARTZ_G63_ROSTER").unwrap()).unwrap();
 let head=unhex(&std::env::var("QUARTZ_G63_HEAD").unwrap()).unwrap();
 assert_eq!(rebuild(Path::new(&dir),owner,roster,head).is_some(),std::env::var("QUARTZ_G63_EXPECT").unwrap()=="accept");
}
fn child(dir:&Path,owner:usize,roster:Hash,head:Hash,accept:bool){
 let status=Command::new(std::env::current_exe().unwrap()).args(["--exact","restart_child","--nocapture"]).env("QUARTZ_G63_DIR",dir).env("QUARTZ_G63_OWNER",owner.to_string()).env("QUARTZ_G63_ROSTER",hex(roster)).env("QUARTZ_G63_HEAD",hex(head)).env("QUARTZ_G63_EXPECT",if accept{"accept"}else{"reject"}).status().unwrap();assert!(status.success());
}
#[test]fn five_silo_isolation(){
 let root=std::env::temp_dir().join(format!("quartz-g63-{}-{}",std::process::id(),SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_nanos()));fs::create_dir(&root).unwrap();
 let a=mesh([100;3],Policy::FixedV1);let mut pins=Vec::new();
 for i in 0..5{
 let dir=root.join(i.to_string());fs::create_dir(&dir).unwrap();
 let keys:[SigningKey;3]=std::array::from_fn(|j|SigningKey::from_bytes(&[(i*3+j+1)as u8;32]));
 let members=std::array::from_fn(|j|Witness{key:keys[j].verifying_key().to_bytes(),root:[(i*3+j+1)as u8;32]});
 let owner=a[i].observation().source;let binding=Binding::genesis(owner,members).unwrap();
 let sign=|j:usize,b:&[u8]|keys.iter().find(|k|k.verifying_key().to_bytes()==binding.members()[j].key).unwrap().sign(b).to_bytes();
 let mut source=a[if i==4{0}else{4}].clone();let mut ev=Vec::new();let mut chain=Vec::new();let mut q=[0;32];let mut p=[0;32];let mut h=[0;32];
 for n in 0..3{
 let payload=if n==0{binding.encode().to_vec()}else{source=source.successor(Event::Shock(vec![(0,1)])).unwrap();let message=TimedObservation{observed:Clock::new(n as u64),observation:source.observation()};let signatures=std::array::from_fn(|j|sign(j,&signed_evidence::signing_bytes(&binding,&message,binding.members()[j].root)));let e=Evidence{recipient:owner,roster:binding.digest(),message,signatures};let b=e.encode().to_vec();ev.push(e);b};
 q=filesystem::append(&dir,n,q,&payload).unwrap();p=publication::publish(&dir,(n+1)as u64,q,p).unwrap().digest();
 let claim=Claim{owner,publication_count:(n+1)as u64,publication:p,roster:binding.digest(),evidence:custody::evidence_head(&binding,&ev).unwrap(),previous:h};let signatures=std::array::from_fn(|j|sign(j,&claim.signing_bytes(binding.members()[j].root)));let c=Custody{claim,signatures};h=c.digest();chain.extend_from_slice(&c.encode());
 }
 fs::write(dir.join("roster"),binding.encode()).unwrap();fs::write(dir.join("custody"),chain).unwrap();pins.push((binding.digest(),h));
 }
 for i in 0..5{let dir=root.join(i.to_string());child(&dir,i,pins[i].0,pins[i].1,true);fs::write(dir.join("0000000000000003.qf1"),b"QF1").unwrap();child(&dir,i,pins[i].0,pins[i].1,true);}
 for i in 0..5{for j in 0..5{if i!=j{child(&root.join(i.to_string()),j,pins[j].0,pins[j].1,false);}}}
 for fault in 0..5{let dir=root.join(fault.to_string());let path=dir.join("0000000000000001.qf1");let original=fs::read(&path).unwrap();fs::write(&path,b"corrupt").unwrap();
 for i in 0..5{child(&root.join(i.to_string()),i,pins[i].0,pins[i].1,i!=fault);}
 fs::write(path,original).unwrap();child(&dir,fault,pins[fault].0,pins[fault].1,true);
 }
 fs::remove_dir_all(root).unwrap();
}
