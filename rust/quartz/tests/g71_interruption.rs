#![cfg(unix)]
use quartz_kernel::{authentication::Witness,mesh::mesh,journal::{Policy,Event},temporal::{Clock,TimedObservation},roster_binding::Binding,signed_evidence::{self,Evidence},transition_binding::{self,Transition},transition_containment::{self,Decision},containment::Gate,quarantine_chain,epochs,specialization_binding::{self,Advisory},sovereign_checkpoint::{self,Inputs,Checkpoint},custody::{self,Custody},filesystem,publication,checkpoint_frame::{self,Frame},checkpoint_publication::{self,Marker},external_pin::{self,Pin},rollback_gate::{self,Reference}};
use ed25519_dalek::{SigningKey,Signer};
use std::{fs::{self,File,OpenOptions},io::Write,path::Path,process::{Command,Stdio},thread,time::{Duration,Instant,SystemTime,UNIX_EPOCH}};
fn sync_write(p:&Path,b:&[u8]){let mut f=OpenOptions::new().write(true).create_new(true).open(p).unwrap();f.write_all(b).unwrap();f.sync_all().unwrap();}
fn fixture(root:&Path){
 let archive=root.join("archive");let dir=root.join("published");fs::create_dir(&archive).unwrap();fs::create_dir(&dir).unwrap();
 let keys:[SigningKey;6]=std::array::from_fn(|j|SigningKey::from_bytes(&[(j+1)as u8;32]));
 let a=mesh([100;3],Policy::FixedV1);let owner=a[0].observation().source;
 let roster=|offset:usize|Binding::genesis(owner,std::array::from_fn(|j|Witness{key:keys[offset+j].verifying_key().to_bytes(),root:[(offset+j+1)as u8;32]})).unwrap();
 let binding=roster(0);let external=roster(3);let genesis=binding.digest();
 let sign=|b:&Binding,j:usize,msg:&[u8]|keys.iter().find(|k|k.verifying_key().to_bytes()==b.members()[j].key).unwrap().sign(msg).to_bytes();
 let mut records=vec![quarantine_chain::append(owner,&[],[0;32],&Gate::new(owner)).unwrap()];let mut history=Vec::new();let mut chain=Vec::new();let mut ev=Vec::new();let mut payloads=vec![binding.encode().to_vec()];
 let mut q=filesystem::append(&archive,0,[0;32],&payloads[0]).unwrap();let mut p=publication::publish(&archive,1,q,[0;32]).unwrap().digest();
 let claim=custody::Claim{owner,publication_count:1,publication:p,roster:genesis,evidence:custody::evidence_head(&binding,&[]).unwrap(),previous:[0;32]};let signatures=std::array::from_fn(|j|sign(&binding,j,&claim.signing_bytes(binding.members()[j].root)));chain.push(Custody{claim,signatures});
 let mut state=a[0].clone();let mut source=a[4].clone();let mut previous=[0;32];let mut adv=[0;32];let mut marker=[0;32];let mut pin=[0;32];let mut pins=Vec::new();
 for n in 0..3{
 let prior=state.successor(Event::Shock(vec![(0,40)])).unwrap();let next=prior.successor(Event::Recover).unwrap();source=source.successor(Event::Shock(vec![(0,10)])).unwrap();let now=Clock::new(359+n as u64);
 let message=TimedObservation{observed:now,observation:source.observation()};let signatures=std::array::from_fn(|j|sign(&binding,j,&signed_evidence::signing_bytes(&binding,&message,binding.members()[j].root)));let e=Evidence{recipient:owner,roster:genesis,message,signatures};
 let claim=transition_binding::Claim::prepare(&binding,now,&prior,&next,&source,&e).unwrap();let signatures=std::array::from_fn(|j|sign(&binding,j,&claim.signing_bytes(binding.members()[j].root)));let t=Transition{claim,signatures};
 let staged=transition_containment::stage_transition(&binding,&prior,&next,&source,&e,&t,t.digest(),now,&records,records.last().unwrap().link.digest).unwrap();assert_eq!(staged.decision,Decision::Accepted);records.push(staged.record);let qh=records.last().unwrap().link.digest;
 let training=vec![vec![vec![(0,1)];3]];let challenge=vec![vec![vec![(124,2)];4]];let epoch=epochs::append(&next,&history,history.last().map(|x:&epochs::Epoch|x.link.digest).unwrap_or([0;32]),&training,&challenge).unwrap();let eh=epoch.link.digest;history.push(epoch);
 let claim=specialization_binding::Claim::prepare(&binding,&prior,&next,&source,&e,&t,&records,qh,&history,eh,adv).unwrap();let signatures=std::array::from_fn(|j|sign(&binding,j,&claim.signing_bytes(binding.members()[j].root)));let advisory=Advisory{claim,signatures};
 ev.push(e.clone());payloads.push(e.encode().to_vec());q=filesystem::append(&archive,n+1,q,payloads.last().unwrap()).unwrap();p=publication::publish(&archive,(n+2)as u64,q,p).unwrap().digest();
 let claim=custody::Claim{owner,publication_count:(n+2)as u64,publication:p,roster:genesis,evidence:custody::evidence_head(&binding,&ev).unwrap(),previous:chain.last().unwrap().digest()};let signatures=std::array::from_fn(|j|sign(&binding,j,&claim.signing_bytes(binding.members()[j].root)));chain.push(Custody{claim,signatures});
 let inputs=Inputs{binding:&binding,prior:&prior,next:&next,source:&source,evidence:&e,transition:&t,containment:&records,epochs:&history,advisory:&advisory,custody:&chain,directory:&archive};
 let claim=sovereign_checkpoint::Claim::prepare(&inputs,genesis,previous,adv).unwrap();let signatures=std::array::from_fn(|j|sign(&binding,j,&claim.signing_bytes(binding.members()[j].root)));let checkpoint=Checkpoint{claim,signatures};let head=checkpoint.digest();adv=advisory.digest();
 let frame=Frame{checkpoint,binding:binding.clone(),prior,next:next.clone(),source:source.clone(),evidence:e,transition:t,containment:records.clone(),epochs:history.clone(),advisory,custody:chain.clone(),published:payloads.clone()};
 let bytes=frame.encode().unwrap();let fh=checkpoint_frame::digest(&bytes);assert_eq!(Frame::decode(&bytes,fh).unwrap().encode().unwrap(),bytes);
 if n==2{let m=Marker{owner,index:2,length:bytes.len()as u64,frame:fh,checkpoint:head,previous:marker};sync_write(&root.join("candidate"),&bytes);sync_write(&root.join("candidate.marker"),&m.encode());break;}
 let m=checkpoint_publication::publish(&dir,&archive,owner,genesis,&frame,marker,head).unwrap();marker=m.digest();
 let claim=external_pin::Claim::prepare(&dir,&archive,&binding,&external,external.digest(),n+1,marker,pin).unwrap();let signatures=std::array::from_fn(|j|sign(&external,j,&claim.signing_bytes(external.members()[j].root)));let signed=Pin{claim,signatures};pin=signed.digest();pins.extend_from_slice(&signed.encode());previous=head;state=next;
 }
 sync_write(&root.join("local"),&binding.encode());sync_write(&root.join("external"),&external.encode());sync_write(&root.join("pins"),&pins);sync_write(&root.join("reference"),&Reference{owner,count:2,genesis,external:external.digest(),head:pin}.encode());
}
#[test]fn writer_child(){
 let Ok(root)=std::env::var("QUARTZ_G71_ROOT")else{return;};let root=Path::new(&root);let dir=root.join("published");let mode:usize=std::env::var("QUARTZ_G71_MODE").unwrap().parse().unwrap();let b=fs::read(root.join("candidate")).unwrap();let m=fs::read(root.join("candidate.marker")).unwrap();let stage=dir.join("0000000000000002.qx1.stage");let final_frame=dir.join("0000000000000002.qx1");let ms=dir.join("0000000000000002.qy1.stage");let mf=dir.join("0000000000000002.qy1");
 if mode==0{sync_write(&stage,&b[..b.len()/2]);}else{sync_write(&stage,&b);if mode>=2{fs::hard_link(&stage,&final_frame).unwrap();File::open(&dir).unwrap().sync_all().unwrap();if mode==3{sync_write(&ms,&m[..m.len()/2]);}if mode>=4{sync_write(&ms,&m);fs::hard_link(&ms,&mf).unwrap();if mode>=5{File::open(&dir).unwrap().sync_all().unwrap();}}}}
 fs::write(root.join("ready"),b"ready").unwrap();loop{thread::sleep(Duration::from_secs(1));}
}
#[test]fn recovery_child(){
 let Ok(root)=std::env::var("QUARTZ_G71_RECOVER")else{return;};let root=Path::new(&root);let reference=Reference::decode(&fs::read(root.join("reference")).unwrap()).unwrap();let local=Binding::decode(reference.owner,&fs::read(root.join("local")).unwrap(),reference.genesis).unwrap();let external=Binding::decode(reference.owner,&fs::read(root.join("external")).unwrap(),reference.external).unwrap();let raw=fs::read(root.join("pins")).unwrap();assert_eq!(raw.len(),2*external_pin::PIN_BYTES);let pins:Vec<_>=raw.chunks_exact(external_pin::PIN_BYTES).map(|b|Pin::decode(b).unwrap()).collect();let frames=rollback_gate::verify_current(&root.join("published"),&root.join("archive"),&local,&external,&reference,&pins).unwrap();assert_eq!(frames.len(),2);
}
#[test]fn interruption_matrix(){
 for mode in 0..6{let root=std::env::temp_dir().join(format!("quartz-g71-{}-{}-{mode}",std::process::id(),SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_nanos()));fs::create_dir(&root).unwrap();fixture(&root);let original=fs::read(root.join("reference")).unwrap();
 let mut child=Command::new(std::env::current_exe().unwrap()).args(["--exact","writer_child"]).env("QUARTZ_G71_ROOT",&root).env("QUARTZ_G71_MODE",mode.to_string()).stdout(Stdio::null()).spawn().unwrap();let start=Instant::now();while !root.join("ready").exists(){if child.try_wait().unwrap().is_some(){panic!("writer exited");}if start.elapsed()>Duration::from_secs(15){let _=child.kill();let _=child.wait();panic!("writer timeout");}thread::sleep(Duration::from_millis(10));}child.kill().unwrap();assert!(!child.wait().unwrap().success());
 assert!(Command::new(std::env::current_exe().unwrap()).args(["--exact","recovery_child","--nocapture"]).env("QUARTZ_G71_RECOVER",&root).status().unwrap().success());assert_eq!(fs::read(root.join("reference")).unwrap(),original);fs::remove_dir_all(root).unwrap();
 }
}
