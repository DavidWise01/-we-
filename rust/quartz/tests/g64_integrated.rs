#![cfg(unix)]
use quartz_kernel::{authentication::Witness,mesh::mesh,journal::{Policy,Event},temporal::{Clock,TimedObservation},roster_binding::Binding,signed_evidence::{self,Evidence},transition_binding::{self,Transition},transition_containment::{self,Decision},containment::Gate,quarantine_chain,epochs,specialization_binding::{self,Advisory},sovereign_checkpoint::{self,Inputs,Checkpoint},custody::{self,Custody},filesystem,publication,incremental::VerifiedPrefix,state_commitment};
use ed25519_dalek::{SigningKey,Signer};
use std::{fs,time::{SystemTime,UNIX_EPOCH}};
#[test]fn integrated_sovereign_checkpoint(){
 for policy in [Policy::FixedV1,Policy::RotatingV2]{let a=mesh([100;3],policy);for i in 0..5{
 let keys:[SigningKey;3]=std::array::from_fn(|j|SigningKey::from_bytes(&[(i*3+j+1)as u8;32]));
 let members=std::array::from_fn(|j|Witness{key:keys[j].verifying_key().to_bytes(),root:[(i*3+j+1)as u8;32]});
 let prior=a[i].successor(Event::Shock(vec![(0,40)])).unwrap();let next=prior.successor(Event::Recover).unwrap();let source=a[if i==4{0}else{4}].successor(Event::Shock(vec![(0,20)])).unwrap();
 let owner=prior.observation().source;let binding=Binding::genesis(owner,members).unwrap();let genesis=binding.digest();let now=Clock::new(359);
 let sign=|j:usize,b:&[u8]|keys.iter().find(|k|k.verifying_key().to_bytes()==binding.members()[j].key).unwrap().sign(b).to_bytes();
 let message=TimedObservation{observed:now,observation:source.observation()};let signatures=std::array::from_fn(|j|sign(j,&signed_evidence::signing_bytes(&binding,&message,binding.members()[j].root)));let e=Evidence{recipient:owner,roster:genesis,message,signatures};
 let claim=transition_binding::Claim::prepare(&binding,now,&prior,&next,&source,&e).unwrap();let signatures=std::array::from_fn(|j|sign(j,&claim.signing_bytes(binding.members()[j].root)));let t=Transition{claim,signatures};
 let mut records=vec![quarantine_chain::append(owner,&[],[0;32],&Gate::new(owner)).unwrap()];let staged=transition_containment::stage_transition(&binding,&prior,&next,&source,&e,&t,t.digest(),now,&records,records[0].link.digest).unwrap();assert_eq!(staged.decision,Decision::Accepted);records.push(staged.record);let qh=records[1].link.digest;
 let training=vec![vec![vec![(0,1)];3]];let challenge=vec![vec![vec![(124,2)];4]];let epoch=epochs::append(&next,&[],[0;32],&training,&challenge).unwrap();let eh=epoch.link.digest;let history=[epoch];
 let claim=specialization_binding::Claim::prepare(&binding,&prior,&next,&source,&e,&t,&records,qh,&history,eh,[0;32]).unwrap();let signatures=std::array::from_fn(|j|sign(j,&claim.signing_bytes(binding.members()[j].root)));let advisory=Advisory{claim,signatures};
 let dir=std::env::temp_dir().join(format!("quartz-g64-{}-{}-{i}",std::process::id(),SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_nanos()));fs::create_dir(&dir).unwrap();
 let mut chain=Vec::new();let mut q=[0;32];let mut p=[0;32];let mut h=[0;32];let ev=[e.clone()];let mut cache=VerifiedPrefix::genesis(&binding).unwrap();
 for n in 0..2{let payload=if n==0{binding.encode().to_vec()}else{e.encode().to_vec()};q=filesystem::append(&dir,n,q,&payload).unwrap();p=publication::publish(&dir,(n+1)as u64,q,p).unwrap().digest();
 let claim=custody::Claim{owner,publication_count:(n+1)as u64,publication:p,roster:genesis,evidence:custody::evidence_head(&binding,&ev[..n]).unwrap(),previous:h};let signatures=std::array::from_fn(|j|sign(j,&claim.signing_bytes(binding.members()[j].root)));let c=Custody{claim,signatures};h=c.digest();cache=cache.advance(&dir,&c,h).unwrap();chain.push(c);}
 assert_eq!(cache.head(),h);
 let inputs=Inputs{binding:&binding,prior:&prior,next:&next,source:&source,evidence:&e,transition:&t,containment:&records,epochs:&history,advisory:&advisory,custody:&chain,directory:&dir};
 let claim=sovereign_checkpoint::Claim::prepare(&inputs,genesis,[0;32],[0;32]).unwrap();let signatures=std::array::from_fn(|j|sign(j,&claim.signing_bytes(binding.members()[j].root)));let c=Checkpoint{claim,signatures};let head=c.digest();let decoded=Checkpoint::decode(&c.encode()).unwrap();assert!(decoded.verify(&inputs,genesis,[0;32],[0;32],head));
 let state=state_commitment::encode(&next).unwrap();assert_eq!(state_commitment::restore(owner,&state,c.claim.state),Some(next.clone()));
 assert!(!c.verify(&inputs,[9;32],[0;32],[0;32],head));assert!(!c.verify(&inputs,genesis,[1;32],[0;32],head));assert!(!c.verify(&inputs,genesis,[0;32],[0;32],[9;32]));
 let mut bad=c.clone();bad.signatures[0][0]^=1;assert!(!bad.verify(&inputs,genesis,[0;32],[0;32],bad.digest()));
 fs::write(dir.join("0000000000000002.qf1"),b"QF1").unwrap();assert!(c.verify(&inputs,genesis,[0;32],[0;32],head));
 fs::write(dir.join("0000000000000001.qf1"),b"corrupt").unwrap();assert!(!c.verify(&inputs,genesis,[0;32],[0;32],head));
 assert_eq!(next.journal().policy(),policy);fs::remove_dir_all(dir).unwrap();
 }}
}
