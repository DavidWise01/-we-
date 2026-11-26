use ed25519_dalek::{Signature,VerifyingKey};
use crate::{mesh::{SiloId,Silo,SILOS},temporal::{Clock,TimedObservation,MAX_AGE},integrity::{Hash,observation_id},provenance::Report,evidence_gate::{Packet,Outcome},containment::{Gate,Fault},coupling::Coupling};
#[derive(Clone,Copy,Debug,PartialEq,Eq)]
pub struct Witness{pub key:[u8;32],pub root:Hash}
pub struct Roster{members:[Witness;3]}
impl Roster{
 pub fn new(members:[Witness;3])->Option<Self>{
 for (i,m) in members.iter().enumerate(){
 if m.root==[0;32]||VerifyingKey::from_bytes(&m.key).ok()?.is_weak()||members[..i].iter().any(|p|p.key==m.key||p.root==m.root){return None;}
 }Some(Self{members})
 }
}
#[derive(Clone,Copy,Debug,PartialEq,Eq)]
pub struct Attestation{pub key:[u8;32],pub signature:[u8;64]}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct SignedPacket{pub message:TimedObservation,pub attestations:[Attestation;3]}
pub fn signing_bytes(recipient:SiloId,m:&TimedObservation,root:Hash)->Vec<u8>{
 let mut b=b"quartz/witness/v1\0".to_vec();b.push(recipient.index() as u8);b.extend_from_slice(&observation_id(m));b.extend_from_slice(&root);b
}
/// Three registered signatures required. Roots are roster assertions, not proof of independence.
pub fn verify(roster:&Roster,recipient:SiloId,now:Clock,p:&SignedPacket)->Option<Packet>{
 let m=&p.message;let o=&m.observation;
 if !crate::mesh::route(o.source,recipient)||!now.age(m.observed).is_some_and(|a|a<=MAX_AGE)||o.recovery_tick>o.sequence||o.deficit>9800||o.energy>3*u64::from(u32::MAX){return None;}
 let mut seen=[false;3];let mut reports=Vec::with_capacity(3);
 for a in &p.attestations{
 let i=roster.members.iter().position(|w|w.key==a.key)?;if seen[i]{return None;}seen[i]=true;
 let w=roster.members[i];let k=VerifyingKey::from_bytes(&w.key).ok()?;
 k.verify_strict(&signing_bytes(recipient,m,w.root),&Signature::from_bytes(&a.signature)).ok()?;
 reports.push(Report{root:w.root,relay:i as u8,observed:m.observed,subject:observation_id(m),value:o.deficit});
 }Some(Packet{message:m.clone(),reports})
}
#[derive(Clone,Copy,Debug,PartialEq,Eq)]
pub enum AuthFault{Authentication,Containment(Fault)}
/// Verify entire batch before allowing any mutation of containment state.
pub fn trial(gate:&mut Gate,roster:&Roster,s:&Silo,now:Clock,c:Coupling,packets:&[SignedPacket])->Result<Outcome,AuthFault>{
 if packets.len()>SILOS{return Err(AuthFault::Authentication);}
 let recipient=s.observation().source;
 let verified:Vec<Packet>=packets.iter().map(|p|verify(roster,recipient,now,p)).collect::<Option<_>>().ok_or(AuthFault::Authentication)?;
 gate.trial(s,now,c,&verified).map_err(AuthFault::Containment)
}
#[cfg(test)]mod tests{
 use super::*;use ed25519_dalek::{SigningKey,Signer};use crate::{mesh::mesh,journal::{Event,Policy}};
 #[test]fn exact_roster_and_no_false_quarantine(){
 let keys:[SigningKey;3]=std::array::from_fn(|i|SigningKey::from_bytes(&[(i+1)as u8;32]));
 let members=std::array::from_fn(|i|Witness{key:keys[i].verifying_key().to_bytes(),root:[(i+1)as u8;32]});
 let roster=Roster::new(members).unwrap();assert!(Roster::new([members[0],members[0],members[2]]).is_none());
 let a=mesh([100;3],Policy::FixedV1);let s=a[0].successor(Event::Shock(vec![(0,20)])).unwrap();let h=a[4].successor(Event::Shock(vec![(0,100)])).unwrap();
 let now=Clock::new(359);let owner=s.observation().source;let message=TimedObservation{observed:now,observation:h.observation()};
 let attestations=std::array::from_fn(|i|Attestation{key:members[i].key,signature:keys[i].sign(&signing_bytes(owner,&message,members[i].root)).to_bytes()});
 let p=SignedPacket{message,attestations};let mut gate=Gate::new(owner);let c=Coupling::new(1000).unwrap();
 assert!(matches!(trial(&mut gate,&roster,&s,now,c,&[p.clone()]),Ok(Outcome::Trial{..})));
 let before=gate.clone();let mut bad=p.clone();bad.message.observation.energy-=1;
 assert_eq!(trial(&mut gate,&roster,&s,now,c,&[bad]),Err(AuthFault::Authentication));assert_eq!(gate,before);
 let mut bad=p.clone();bad.attestations[2]=bad.attestations[0];assert!(verify(&roster,owner,now,&bad).is_none());
 assert!(verify(&roster,SiloId::new(1).unwrap(),now,&p).is_none());
 assert!(verify(&roster,owner,Clock::new(392),&p).is_none());
 assert_eq!(trial(&mut gate,&roster,&s,now,c,&[p]),Err(AuthFault::Containment(Fault::Replay)));
 }
}
