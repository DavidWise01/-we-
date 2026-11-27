use quartz_kernel::{authentication::Witness,mesh::mesh,journal::Policy,roster_binding::Binding,signed_evidence::{self,Evidence},temporal::{Clock,TimedObservation},custody,rolling_evidence::Rolling};
use ed25519_dalek::{SigningKey,Signer};
use sha2::{Digest,Sha256};
use std::{hint::black_box,time::{Instant,SystemTime,UNIX_EPOCH},io::Write,fs::{self,OpenOptions,File}};
fn timed<F:FnOnce()>(f:F)->u128{let t=Instant::now();f();t.elapsed().as_nanos()}
fn main(){
 let keys:[SigningKey;3]=std::array::from_fn(|j|SigningKey::from_bytes(&[(j+1)as u8;32]));
 let a=mesh([100;3],Policy::FixedV1);let b=Binding::genesis(a[0].observation().source,std::array::from_fn(|j|Witness{key:keys[j].verifying_key().to_bytes(),root:[(j+1)as u8;32]})).unwrap();
 let ev:Vec<_>=(0..256).map(|i|{let message=TimedObservation{observed:Clock::new(i),observation:a[4].observation()};let signatures=std::array::from_fn(|j|{let w=b.members()[j];keys.iter().find(|k|k.verifying_key().to_bytes()==w.key).unwrap().sign(&signed_evidence::signing_bytes(&b,&message,w.root)).to_bytes()});Evidence{recipient:b.owner(),roster:b.digest(),message,signatures}}).collect();
 let raw:Vec<_>=ev.iter().map(Evidence::encode).collect();
 let dir=std::env::temp_dir().join(format!("quartz-g76-{}-{}",std::process::id(),SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_nanos()));fs::create_dir(&dir).unwrap();
 println!("n,trial,qc1_prefix_ns,qz1_advance_ns,history_verify_ns,full_payload_hash_ns,rolling_payload_hash_ns,allocation_copy_ns,write_ns,sync_ns,read_ns,payload_bytes,full_signature_count,rolling_signature_count");
 for n in [8usize,32,128,256]{for trial in 0..3{
 let qc=||{for k in 1..=n{black_box(custody::evidence_head(&b,&ev[..k]).unwrap());}};
 let qz=||{let mut s=Rolling::genesis(&b).unwrap();for e in &ev[..n]{s=s.advance(&b,e).unwrap();}assert_eq!(s.count(),n as u64);black_box(s);};
 let (full,rolling)=if trial%2==0{(timed(qc),timed(qz))}else{let y=timed(qz);(timed(qc),y)};
 let auth=timed(||{for e in &ev[..n]{black_box(e.verify_history(&b).unwrap());}});
 let hash_full=timed(||{for k in 1..=n{let mut h=Sha256::new();for p in &raw[..k]{h.update(p);}black_box(h.finalize());}});
 let hash_roll=timed(||{let mut head=[0u8;32];for p in &raw[..n]{let mut h=Sha256::new();h.update(head);h.update(p);head=h.finalize().into();}black_box(head);});
 let alloc=timed(||{for k in 1..=n{let mut v=Vec::with_capacity(k*264);for p in &raw[..k]{v.extend_from_slice(p);}black_box(v);}});
 let path=dir.join(format!("{n}-{trial}"));let mut f=OpenOptions::new().write(true).create_new(true).open(&path).unwrap();
 let write=timed(||{for p in &raw[..n]{f.write_all(p).unwrap();}});
 let sync=timed(||{f.sync_all().unwrap();File::open(&dir).unwrap().sync_all().unwrap();});drop(f);
 let mut readback=Vec::new();let read=timed(||{readback=fs::read(&path).unwrap();});
 assert_eq!(readback.len(),264*n);assert!(readback.chunks_exact(264).zip(&raw[..n]).all(|(x,y)|x==y.as_slice()));
 println!("{n},{trial},{full},{rolling},{auth},{hash_full},{hash_roll},{alloc},{write},{sync},{read},{},{},{}",264*n,3*n*(n+1)/2,3*n);
 }}
 fs::remove_dir_all(dir).unwrap();
}
