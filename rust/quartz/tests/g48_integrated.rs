use ed25519_dalek::{SigningKey,Signer};
use quartz_kernel::{mesh::mesh,journal::{Policy,Event},temporal::{Clock,TimedObservation},authentication::{self,Roster,Witness,Attestation,SignedPacket,AuthFault},containment::{Gate,Fault},coupling::Coupling,quarantine_chain,epochs,interruption::{self,Boundary},canonical,decoding,evidence_gate::Outcome,CENTER};
#[test]fn phase_vi_authenticated_recovery(){
 let keys:[SigningKey;3]=std::array::from_fn(|i|SigningKey::from_bytes(&[(i+1)as u8;32]));
 let members=std::array::from_fn(|i|Witness{key:keys[i].verifying_key().to_bytes(),root:[(i+1)as u8;32]});
 let roster=Roster::new(members).unwrap();
 for policy in [Policy::FixedV1,Policy::RotatingV2]{
 for lambda in [0,500,1000]{
 for delay in [0,32,33]{
 let mut a=mesh([100;3],policy);a[0]=a[0].successor(Event::Shock(vec![(0,20)])).unwrap();a[4]=a[4].successor(Event::Shock(vec![(124,100)])).unwrap();
 let s=&a[0];let owner=s.observation().source;let source=a[4].observation().source;let observed=Clock::new(359);let now=Clock::new(359+delay);let c=Coupling::new(lambda).unwrap();
 let sign=|message:TimedObservation|{let attestations=std::array::from_fn(|i|Attestation{key:members[i].key,signature:keys[i].sign(&authentication::signing_bytes(owner,&message,members[i].root)).to_bytes()});SignedPacket{message,attestations}};
 let p=sign(TimedObservation{observed,observation:a[4].observation()});
 let mut g=Gate::new(owner);let mut q=vec![quarantine_chain::append(owner,&[],[0;32],&g).unwrap()];
 let mut packets=std::array::from_fn(|_|Vec::new());if let Some(v)=authentication::verify(&roster,owner,now,&p){packets[0].push(v);}
 let bytes=canonical::encode(&a,now,lambda,&packets).unwrap();let d=decoding::decode(&bytes).unwrap();assert_eq!(d.silos,a);
 assert_eq!(canonical::encode(&d.silos,d.now,d.lambda,&d.packets),Some(bytes));
 let result=authentication::trial(&mut g,&roster,s,now,c,&[p.clone()]);
 if delay<=32{
 let Ok(Outcome::Trial{state,..})=result else{panic!("expected trial")};assert_eq!(state.health()[CENTER],100);
 q.push(quarantine_chain::append(owner,&q,q.last().unwrap().link.digest,&g).unwrap());
 let mut altered=p.clone();altered.message.observation.energy-=1;let before=g.clone();
 assert_eq!(authentication::trial(&mut g,&roster,s,now,c,&[altered.clone()]),Err(AuthFault::Authentication));assert_eq!(g,before);
 let conflict=sign(altered.message);assert_eq!(authentication::trial(&mut g,&roster,s,now,c,&[conflict]),Err(AuthFault::Containment(Fault::Equivocation)));
 q.push(quarantine_chain::append(owner,&q,q.last().unwrap().link.digest,&g).unwrap());
 }else{assert_eq!(result,Err(AuthFault::Authentication));assert_eq!(g,Gate::new(owner));}
 let t=vec![vec![vec![(0,1)];9]];let ch=vec![vec![(124,1)];12]];let e=vec![epochs::append(s,&[],[0;32],&t,&ch).unwrap()];
 let b=Boundary::prepare(owner,&q,&e).unwrap().encode();let head=Boundary::digest(&b);
 let mut recovered=interruption::recover(owner,&b,head,&q,&e).unwrap();assert_eq!(recovered.gate,g);assert_eq!(recovered.epochs,e);
 assert!(interruption::recover(owner,&b[..76],head,&q,&e).is_none());
 if delay<=32{assert!(recovered.gate.quarantined(source));assert_eq!(authentication::trial(&mut recovered.gate,&roster,s,now,c,&[p]),Err(AuthFault::Containment(Fault::Quarantined)));}
 }
 }
 }
}
